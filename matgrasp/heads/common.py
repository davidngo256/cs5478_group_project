"""Shared pieces for the material heads: the head interface, calibration metrics (ECE,
temperature scaling), latency measurement, and the YCB-photo evaluation loop that
writes results/heads/<head>_ycb.json.
"""
from __future__ import annotations

import json
import time
from collections import Counter
from pathlib import Path
from typing import Protocol

import numpy as np

from ..friction import MATERIAL_TABLE
from ..ycb import DATA_DIR, OBJECTS
from . import ycb_photos

TABLE_CLASSES: list[str] = list(MATERIAL_TABLE)
MODELS_DIR = DATA_DIR / "models"
RESULTS_DIR = Path(__file__).resolve().parents[2] / "results" / "heads"
IMAGENET_MEAN = np.array([0.485, 0.456, 0.406], np.float32)
IMAGENET_STD = np.array([0.229, 0.224, 0.225], np.float32)


class MaterialHead(Protocol):
    name: str

    def predict(self, img: np.ndarray, mask: np.ndarray) -> dict[str, float]:
        """Posterior over TABLE_CLASSES (all keys present, sums to 1) for one RGB uint8
        image and its boolean object mask."""
        ...


def full_table_probs(probs: dict[str, float]) -> dict[str, float]:
    """Every table class present (zeros for absent ones), table order, renormalised."""
    tot = sum(float(probs.get(c, 0.0)) for c in TABLE_CLASSES)
    if tot <= 0:
        raise ValueError("no mass on table classes")
    return {c: float(probs.get(c, 0.0)) / tot for c in TABLE_CLASSES}


def top1(probs: dict[str, float]) -> str:
    return max(probs, key=probs.get)


def mask_average(post: np.ndarray, mask: np.ndarray) -> np.ndarray:
    """Mean of a per-pixel posterior [C, H, W] over the pixels where mask [H, W] is True.
    Falls back to the whole frame if the mask is empty. Returns [C], summing to 1 if the
    input rows do."""
    post = np.asarray(post, float)
    mask = np.asarray(mask, bool)
    assert post.shape[1:] == mask.shape, (post.shape, mask.shape)
    if not mask.any():
        mask = np.ones_like(mask)
    return post[:, mask].mean(axis=1)


def resize_mask(mask: np.ndarray, h: int, w: int) -> np.ndarray:
    from PIL import Image

    return np.asarray(Image.fromarray(mask.astype(np.uint8) * 255).resize((w, h), Image.NEAREST)) > 127


# --- calibration --------------------------------------------------------------------------

def ece_score(probs: np.ndarray, labels: np.ndarray, n_bins: int = 15) -> float:
    """Expected calibration error of the top-1 confidence with equal-width bins on (0, 1]."""
    probs = np.asarray(probs, float)
    labels = np.asarray(labels)
    conf = probs.max(axis=1)
    correct = (probs.argmax(axis=1) == labels).astype(float)
    edges = np.linspace(0.0, 1.0, n_bins + 1)
    ece = 0.0
    for lo, hi in zip(edges[:-1], edges[1:]):
        sel = (conf > lo) & (conf <= hi)
        if sel.any():
            ece += sel.mean() * abs(correct[sel].mean() - conf[sel].mean())
    return float(ece)


def softmax(logits: np.ndarray, T: float = 1.0) -> np.ndarray:
    z = np.asarray(logits, float) / T
    z = z - z.max(axis=1, keepdims=True)
    e = np.exp(z)
    return e / e.sum(axis=1, keepdims=True)


def fit_temperature(logits: np.ndarray, labels: np.ndarray, max_iter: int = 200) -> float:
    """Temperature T > 0 minimising NLL of softmax(logits / T) on held-out data (LBFGS
    on log T, as in Guo et al. 2017)."""
    import torch

    z = torch.as_tensor(np.asarray(logits, np.float64))
    y = torch.as_tensor(np.asarray(labels), dtype=torch.long)
    log_t = torch.zeros((), dtype=torch.float64, requires_grad=True)
    opt = torch.optim.LBFGS([log_t], lr=0.1, max_iter=max_iter, line_search_fn="strong_wolfe")

    def closure():
        opt.zero_grad()
        loss = torch.nn.functional.cross_entropy(z / log_t.exp(), y)
        loss.backward()
        return loss

    opt.step(closure)
    return float(log_t.exp().item())


def confusion_matrix(true: list[str], pred: list[str], classes: list[str]) -> dict[str, dict[str, int]]:
    cm = {t: {p: 0 for p in classes} for t in classes}
    for t, p in zip(true, pred):
        cm[t][p] += 1
    return cm


# --- latency / size ----------------------------------------------------------------------

def count_params(model) -> int:
    return int(sum(p.numel() for p in model.parameters()))


def device() -> str:
    """Torch device for the heads: MATGRASP_DEVICE if set (e.g. "cpu" to reproduce CPU-only numbers),
    else CUDA when available, else CPU."""
    import os

    import torch

    return os.environ.get("MATGRASP_DEVICE") or ("cuda" if torch.cuda.is_available() else "cpu")


def device_name(dev: str) -> str:
    """GPU model for a CUDA device, "cpu" otherwise."""
    import torch

    return torch.cuda.get_device_name(dev) if str(dev).startswith("cuda") else "cpu"


def machine_info(dev: str) -> dict:
    """What a set of numbers was measured on: CPU count, torch build, device and its name."""
    import os

    import torch

    return {"cpu_count": os.cpu_count(), "torch_threads": torch.get_num_threads(), "torch": torch.__version__,
            "device": str(dev), "device_name": device_name(dev)}


def measure_latency_ms(fn, inputs: list, warmup: int = 5, n: int = 20, device: str | None = None) -> dict[str, float]:
    """Wall-clock ms per call of `fn(x)` for one input at a time (batch size 1) under
    torch.no_grad, after `warmup` calls. Returns mean/std/min over `n` timed calls, plus
    the device, the torch thread count and the 1-minute load average when the timing started
    (other processes on the box inflate these numbers). On CUDA every call is bracketed by
    `torch.cuda.synchronize()` so queued kernels are counted, not just their launch."""
    import os

    import torch

    assert len(inputs) >= 1
    dev = str(device or "cpu")
    sync = torch.cuda.synchronize if dev.startswith("cuda") else (lambda: None)
    load1 = os.getloadavg()[0]
    with torch.no_grad():
        for i in range(warmup):
            fn(inputs[i % len(inputs)])
            sync()
        times = []
        for i in range(n):
            sync()
            t0 = time.perf_counter()
            fn(inputs[i % len(inputs)])
            sync()
            times.append((time.perf_counter() - t0) * 1000.0)
    return {"mean": float(np.mean(times)), "std": float(np.std(times)), "min": float(np.min(times)), "n": n,
            "device": dev, "torch_threads": torch.get_num_threads(), "loadavg_1min_at_start": float(load1)}


# --- YCB evaluation -----------------------------------------------------------------------

def evaluate_ycb(head: MaterialHead, obj_ids=None, verbose: bool = True, previous: dict | None = None) -> dict:
    """Run a head over every stored view of every object. Output matches the spec:
    {obj: {"images": [{"file", "mask", "probs"}], "mean_probs", "true_material", "top1_correct_rate"}}
    An object's entry in `previous` (an earlier results file) is reused when its view list and
    true material are unchanged, so adding objects does not re-run the others."""
    out: dict[str, dict] = {}
    for oid in (obj_ids or list(OBJECTS)):
        views = ycb_photos.list_views(oid)
        if not views:
            print(f"[{head.name}] no photos for {oid}, skipping", flush=True)
            continue
        truth = OBJECTS[oid].material
        files = [str(p.relative_to(DATA_DIR)) for p, _ in views]
        prev = (previous or {}).get(oid)
        if prev and [im["file"] for im in prev["images"]] == files and prev.get("true_material") == truth:
            out[oid] = {k: v for k, v in prev.items() if k != "retired"}
            if verbose:
                print(f"[{head.name}] {oid}: reused {len(files)} views from previous run", flush=True)
            continue
        imgs = []
        t0 = time.time()
        for img_p, mask_p in views:
            img, mask, src = ycb_photos.load_view(img_p, mask_p)
            probs = full_table_probs(head.predict(img, mask))
            imgs.append({"file": str(img_p.relative_to(DATA_DIR)), "mask": src, "probs": probs})
        mean = {c: float(np.mean([im["probs"][c] for im in imgs])) for c in TABLE_CLASSES}
        rate = float(np.mean([top1(im["probs"]) == truth for im in imgs]))
        source = "render" if all(im["mask"] == "render" for im in imgs) else "photo"
        out[oid] = {"images": imgs, "mean_probs": mean, "true_material": truth, "top1_correct_rate": rate,
                    "source": source}
        if source == "render":
            out[oid]["note"] = ("no photographs of this object exist on the YCB server; views are PyBullet "
                                "renders of the Google textured scan and are excluded from photo accuracy")
        if verbose:
            print(f"[{head.name}] {oid}: {len(imgs)} views, top1 rate {rate:.2f}, mean top1 {top1(mean)} "
                  f"(true {truth}) in {time.time() - t0:.0f}s", flush=True)
    return out


def ycb_accuracy(results: dict) -> dict:
    """Image-level top-1 accuracy over all views, object-level accuracy with the majority
    top-1 over an object's views (ties broken by the mean posterior), per-object predictions."""
    n_img = n_ok = 0
    per_obj, excluded = {}, {}
    for oid, r in results.items():
        votes = Counter(top1(im["probs"]) for im in r["images"])
        source = r.get("source", "photo")
        if oid not in OBJECTS or r.get("retired"):
            excluded[oid] = "retired: no longer in matgrasp.ycb.OBJECTS"
        elif source != "photo":
            excluded[oid] = source
        if oid not in excluded:
            n_img += len(r["images"])
            n_ok += sum(top1(im["probs"]) == r["true_material"] for im in r["images"])
        best = max(votes.values())
        tied = [c for c, v in votes.items() if v == best]
        pred = max(tied, key=lambda c: r["mean_probs"][c])
        per_obj[oid] = {"pred": pred, "true": r["true_material"], "votes": dict(votes),
                        "mean_top1": top1(r["mean_probs"]), "n_images": len(r["images"]),
                        "source": "retired" if oid in excluded and excluded[oid].startswith("retired") else source}
    photo_objs = [v for k, v in per_obj.items() if k not in excluded]
    obj_acc = float(np.mean([v["pred"] == v["true"] for v in photo_objs])) if photo_objs else float("nan")
    return {"image_level": n_ok / max(n_img, 1), "object_level": obj_acc, "n_images": n_img,
            "n_objects": len(photo_objs), "excluded": excluded,
            "excluded_render_objects": [k for k, v in excluded.items() if v == "render"],
            "per_object": per_obj}


def write_json(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=1))


def remeasure_latency(head: MaterialHead, n: int = 20) -> dict:
    """Re-time an already evaluated head on an idle machine and update its summary file."""
    path = RESULTS_DIR / f"{head.name}_summary.json"
    summary = json.loads(path.read_text())
    summary["latency_ms_per_image"] = measure_latency_ms(head.forward_one, first_views(n), n=n,
                                                         device=getattr(head, "device", None))
    summary["machine"] = machine_info(getattr(head, "device", "cpu"))
    write_json(path, summary)
    return summary["latency_ms_per_image"]


def run_head(head: MaterialHead, extra_summary: dict | None = None, latency_inputs=None) -> dict:
    """Evaluate on YCB, write <head>_ycb.json and <head>_summary.json, return the summary.
    Objects already in the results file are reused if unchanged; entries for objects that
    have since left OBJECTS are kept, flagged `retired`, and excluded from the accuracies."""
    path = RESULTS_DIR / f"{head.name}_ycb.json"
    previous = json.loads(path.read_text()) if path.exists() else {}
    results = evaluate_ycb(head, previous=previous)
    for oid, r in previous.items():
        if oid not in results:
            results[oid] = {**r, "retired": True,
                            "note": "object no longer in matgrasp.ycb.OBJECTS; kept for reference, excluded from accuracies"}
    write_json(path, results)
    summary = {"head": head.name, "params": count_params(head.model), "objects": list(OBJECTS),
               "machine": machine_info(getattr(head, "device", "cpu")), "ycb": ycb_accuracy(results)}
    if latency_inputs is not None:
        summary["latency_ms_per_image"] = measure_latency_ms(head.forward_one, latency_inputs,
                                                             device=getattr(head, "device", None))
    if extra_summary:
        summary.update(extra_summary)
    write_json(RESULTS_DIR / f"{head.name}_summary.json", summary)
    return summary


def first_views(n: int = 20) -> list[tuple[np.ndarray, np.ndarray]]:
    """(image, mask) pairs from stored YCB photos, round-robin over objects, for latency."""
    pairs = []
    per = {oid: ycb_photos.list_views(oid) for oid in OBJECTS}
    i = 0
    while len(pairs) < n and any(per.values()):
        for oid, vs in per.items():
            if i < len(vs):
                img, mask, _ = ycb_photos.load_view(*vs[i])
                pairs.append((img, mask))
                if len(pairs) >= n:
                    break
        i += 1
        if i > 50:
            break
    return pairs
