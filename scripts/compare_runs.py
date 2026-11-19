"""Compare the 2x2 across runs (e.g. the planner's torsional-coefficient sensitivity). For each run:
the paired gains of squeeze-only, selection-only and oracle over the baseline, pooled and on low-mu
objects, in rank and filter mode, plus how often baseline and oracle choose the same grasp.
Usage: python scripts/compare_runs.py run1 run2 ... [--trials 40] [--out results/sim/<file>.md]
--trials N restricts every run to trials < N so runs of different length compare on identical trials
(trials are reproducible across runs and workers)."""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from matgrasp.analysis import load_rows, paired_diff, same_grasp_rate, table_by_trial
from matgrasp.experiment import RESULTS
from matgrasp.friction import MATERIAL_TABLE
from matgrasp.ycb import OBJECTS

LOW = {o for o, s in OBJECTS.items() if MATERIAL_TABLE[s.material].nominal <= 0.35}


def gain(rows, mode, metric, cell, subset=None):
    t = table_by_trial(rows, mode, metric)
    f = lambda d: {k: v for k, v in d.items() if subset is None or k[0] in subset}
    return paired_diff(f(t[cell]), f(t["baseline"]))


def build(runs, max_trials=None):
    out = ["# 2x2 across runs", ""]
    if max_trials:
        out += [f"Restricted to trials < {max_trials} per object (identical trials in every run).", ""]
    out += ["| run | gamma x | n | mode | oracle | squeeze only | selection only | oracle, low-mu | selection only, low-mu | oracle wrench [N] | same grasp as baseline |",
            "|---|---|---|---|---|---|---|---|---|---|---|"]
    for run in runs:
        rows = load_rows(RESULTS / "sim" / run / "rows.jsonl")
        if max_trials:
            rows = [r for r in rows if r["trial"] < max_trials]
        cfg = json.loads((RESULTS / "sim" / run / "config.json").read_text())
        n = len({(r["obj"], r["trial"]) for r in rows})
        for mode in ("rank", "filter"):
            f = lambda c, s=None, m="success": "{:+.3f} [{:+.3f}, {:+.3f}]".format(*(lambda r: (r[0], r[1][0], r[1][1]))(gain(rows, mode, m, c, s)))
            same, ns = same_grasp_rate(rows, mode, "baseline", "oracle")
            out.append(f"| {run} | {cfg.get('gamma_scale', 1.0)} | {n} | {mode} | {f('oracle')} | {f('squeeze')} | {f('select')} | "
                       f"{f('oracle', LOW)} | {f('select', LOW)} | {gain(rows, mode, 'wrench', 'oracle')[0]:+.3f} | {same:.0%} of {ns} |")
    return "\n".join(out) + "\n"


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("runs", nargs="+"); ap.add_argument("--trials", type=int, default=None); ap.add_argument("--out", default=None)
    a = ap.parse_args()
    md = build(a.runs, a.trials)
    if a.out:
        Path(a.out).write_text(md, encoding="utf-8")
    print(md)
