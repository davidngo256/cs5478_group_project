"""MINC-2500 (split 1) subset for the MobileNet head, fetched from the Hugging Face mirror
`mcimpoi/minc-2500_split_1` (CC BY 4.0) by reading only the parquet row groups that hold
the ten classes in friction.MINC_TO_TABLE. The mirror stores each split sorted by class in
1000-row row groups, so this downloads roughly 10/23 of the data rather than all 2.3 GB.
"""
from __future__ import annotations

import json
import random
import time
from pathlib import Path

from ..friction import MINC_TO_TABLE
from ..ycb import DATA_DIR

MINC_DIR = DATA_DIR / "minc"
HF_REPO = "datasets/mcimpoi/minc-2500_split_1"
SPLITS = ("train", "validation", "test")
MINC_CLASSES = sorted(MINC_TO_TABLE)          # the 10 kept classes, index = training label


def index_path(split: str) -> Path:
    return MINC_DIR / f"{split}.json"


def load_index(split: str) -> list[dict]:
    """[{"file": <path>, "label": <minc class name>}] for one split (kept classes only)."""
    return json.loads(index_path(split).read_text())


def choose_rows(labels: list[int], keep: set[int], per_class: int | None) -> list[int]:
    """Row indices to keep: for each kept label, the first `per_class` rows (all if None)."""
    count: dict[int, int] = {}
    rows = []
    for i, lab in enumerate(labels):
        if lab not in keep:
            continue
        c = count.get(lab, 0)
        if per_class is None or c < per_class:
            rows.append(i)
            count[lab] = c + 1
    return rows


def row_groups_for(rows: list[int], rg_sizes: list[int]) -> list[tuple[int, int, int]]:
    """[(row_group, start_row, end_row)] for the row groups that contain any wanted row."""
    out, start = [], 0
    wanted = set(rows)
    for g, n in enumerate(rg_sizes):
        if any(r in wanted for r in range(start, start + n)):
            out.append((g, start, start + n))
        start += n
    return out


def fetch_minc(per_class_train: int = 700, verbose: bool = True) -> None:
    import pyarrow.parquet as pq
    from huggingface_hub import HfFileSystem

    fs = HfFileSystem()
    files = sorted(fs.ls(HF_REPO + "/data", detail=False))
    for split in SPLITS:
        if index_path(split).exists():
            continue
        shards = [f for f in files if Path(f).name.startswith(split + "-")]
        per_class = per_class_train if split == "train" else None
        entries: list[dict] = []
        names = None
        t0 = time.time()
        # the split is sorted by class across shards, so count rows per class across shards
        seen: dict[int, int] = {}
        for shard in shards:
            with fs.open(shard, "rb") as fh:
                pf = pq.ParquetFile(fh)
                if names is None:
                    names = json.loads(pf.schema_arrow.metadata[b"huggingface"])["info"]["features"]["label"]["names"]
                    keep = {names.index(c) for c in MINC_CLASSES}
                md = pf.metadata
                rg_sizes = [md.row_group(i).num_rows for i in range(md.num_row_groups)]
                labels = pf.read(columns=["label"]).column("label").to_pylist()
                # continue per-class counts from previous shards
                rows = []
                for i, lab in enumerate(labels):
                    if lab in keep and (per_class is None or seen.get(lab, 0) < per_class):
                        rows.append(i)
                        seen[lab] = seen.get(lab, 0) + 1
                wanted = set(rows)
                groups = row_groups_for(rows, rg_sizes)
                if verbose:
                    print(f"[{split}] {Path(shard).name}: {len(rows)} rows in {len(groups)} row groups", flush=True)
                for g, start, end in groups:
                    tbl = pf.read_row_group(g, columns=["image", "label"])
                    imgs = tbl.column("image").to_pylist()
                    labs = tbl.column("label").to_pylist()
                    for j in range(end - start):
                        r = start + j
                        if r not in wanted:
                            continue
                        cname = names[labs[j]]
                        d = MINC_DIR / split / cname
                        d.mkdir(parents=True, exist_ok=True)
                        p = d / f"{Path(shard).name.split('-')[1]}_{r:06d}.jpg"
                        p.write_bytes(imgs[j]["bytes"])
                        entries.append({"file": str(p.relative_to(MINC_DIR)), "label": cname})
        index_path(split).write_text(json.dumps(entries))
        if verbose:
            print(f"[{split}] wrote {len(entries)} images in {time.time() - t0:.0f}s", flush=True)


def subsample(entries: list[dict], per_class: int, seed: int = 0) -> list[dict]:
    rng = random.Random(seed)
    by: dict[str, list[dict]] = {}
    for e in entries:
        by.setdefault(e["label"], []).append(e)
    out = []
    for c in sorted(by):
        xs = by[c][:]
        rng.shuffle(xs)
        out.extend(xs[:per_class])
    return out


if __name__ == "__main__":
    fetch_minc()
