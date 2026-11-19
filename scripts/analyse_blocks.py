"""Run-to-run spread of the paired gains: split a run's trials into blocks (default 40 trials per
object, i.e. the size of one original run) and report each arm's gain per block next to the pooled
gain and its bootstrap CI. Usage: python scripts/analyse_blocks.py <run> [--block 40] [--mode rank]"""
import argparse
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from matgrasp.analysis import load_rows, paired_diff, table_by_trial
from matgrasp.experiment import RESULTS
from matgrasp.friction import MATERIAL_TABLE
from matgrasp.ycb import OBJECTS

LOW = {o for o, s in OBJECTS.items() if MATERIAL_TABLE[s.material].nominal <= 0.35}


def gains(rows, mode, metric, cell, subset=None, block=None, size=40):
    t = table_by_trial(rows, mode, metric)
    keep = lambda k: (subset is None or k[0] in subset) and (block is None or k[1] // size == block)
    return paired_diff({k: v for k, v in t[cell].items() if keep(k)}, {k: v for k, v in t["baseline"].items() if keep(k)})


def build(run: str, size: int, mode: str, metric: str = "success") -> str:
    rows = load_rows(RESULTS / "sim" / run / "rows.jsonl")
    n_blocks = max(r["trial"] for r in rows) // size + 1
    present = {r["cell"] for r in rows}
    cells = [c for c in ["squeeze", "select", "oracle", "table_mean", "table_q", "table_squeeze"] if c in present]
    cells += sorted(c for c in present if c.startswith("head:"))
    out = [f"# Run-to-run spread: {run}, {mode} mode, {metric}", "",
           f"Trials split into blocks of {size} per object ({n_blocks} blocks); each block is the size of one original run. "
           "Gains are paired differences to the baseline; the pooled column uses all trials with a 95% bootstrap CI. "
           "'block SD' is the standard deviation of the per-block gains: what to expect between two independent 40-trial runs.", ""]
    for name, subset in (("all objects", None), ("low-mu objects", LOW)):
        hdr = "| arm | " + " | ".join(f"block {b}" for b in range(n_blocks)) + " | pooled [95% CI] | n | block SD |"
        out += [f"## {name}", "", hdr, "|---|" + "---|" * (n_blocks + 3)]
        for c in cells:
            per = [gains(rows, mode, metric, c, subset, b, size)[0] for b in range(n_blocks)]
            d, (lo, hi), n = gains(rows, mode, metric, c, subset)
            out.append(f"| {c} | " + " | ".join(f"{x:+.3f}" for x in per) + f" | {d:+.3f} [{lo:+.3f}, {hi:+.3f}] | {n} | {np.std(per, ddof=1) if len(per) > 1 else float('nan'):.3f} |")
        out.append("")
    return "\n".join(out)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("run"); ap.add_argument("--block", type=int, default=40); ap.add_argument("--mode", default="rank")
    a = ap.parse_args()
    md = build(a.run, a.block, a.mode)
    (RESULTS / "sim" / a.run / f"blocks_{a.mode}.md").write_text(md, encoding="utf-8")
    print(md)
