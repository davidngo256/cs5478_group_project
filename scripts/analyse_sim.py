"""Build results/sim/<run>/report.md from rows.jsonl.
Usage: python scripts/analyse_sim.py core [heads ...]   (later runs are merged for the head cells)
"""
import sys
from collections import Counter
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from matgrasp.analysis import (by_material, eps_vs_wrench, fmt_table, load_rows, paired_diff, same_grasp_rate,
                               summarise_cells, table_by_trial, two_by_two)
from matgrasp.experiment import RESULTS
from matgrasp.friction import MATERIAL_TABLE
from matgrasp.ycb import OBJECTS

LOW = {o for o, s in OBJECTS.items() if MATERIAL_TABLE[s.material].nominal <= 0.35}
HIGH = {o for o, s in OBJECTS.items() if MATERIAL_TABLE[s.material].nominal >= 0.5}


def section(title, body):
    return f"\n## {title}\n\n{body}\n"


def coverage(rows, all_rows):
    trials = {(r["obj"], r["trial"]) for r in rows}
    skipped = [r for r in all_rows if r.get("skipped")]
    errs = [r for r in all_rows if "error" in r]
    per_obj = Counter(o for o, _ in trials)
    lines = [f"{len(trials)} usable trials, {len(skipped)} skipped (too few feasible grasps), {len(errs)} errors.", "",
             "| object | material | usable trials | skipped | mean feasible cands | mean FC at mu* |", "|---|---|---|---|---|---|"]
    for o, s in OBJECTS.items():
        rs = [r for r in rows if r["obj"] == o and r["cell"] == "baseline" and r["mode"] == "rank"]
        sk = sum(1 for r in skipped if r["obj"] == o)
        lines.append(f"| {o} | {s.material} | {per_obj.get(o, 0)} | {sk} | {np.mean([r['n_cands'] for r in rs]) if rs else 0:.0f} | {np.mean([r['n_fc_true'] for r in rs]) if rs else 0:.0f} |")
    return "\n".join(lines)


def main(runs):
    all_rows, rows = [], []
    for run in runs:
        path = RESULTS / "sim" / run / "rows.jsonl"
        all_rows += [__import__("json").loads(l) for l in open(path)]
        rows += load_rows(path)
    out = [f"# Simulation study: {', '.join(runs)}\n"]
    out.append(section("Coverage", coverage(rows, all_rows)))

    for metric, label in (("success", "lift success under the force cap"), ("wrench", "wrench at slip [N], 0 if the grasp failed")):
        for mode in ("rank", "filter"):
            body = two_by_two(rows, mode, metric)
            for name, subset in (("low-mu objects (glass, metal, ceramic, plastic)", LOW), ("high-mu objects (paper, foam, rubber)", HIGH)):
                sub = [r for r in rows if r["obj"] in subset]
                if sub:
                    body += f"\n\n**{name}**\n\n" + two_by_two(sub, mode, metric)
            out.append(section(f"2x2 on {label}, {mode} mode", body))

    cells = ["baseline", "squeeze", "oracle", "table_q", "table_mean", "table_squeeze", "table_q0.05", "table_q0.25"]
    heads = sorted({r["cell"] for r in rows if r["cell"].startswith("head:")})
    cells += heads
    for metric, label in (("success", "success"), ("wrench", "wrench at slip [N]"), ("force", "commanded grip force [N]")):
        for mode in ("rank", "filter"):
            ent = summarise_cells(rows, mode, metric, [c for c in cells if c in {r["cell"] for r in rows}])
            body = fmt_table(ent, label)
            body += "\n\nPer material (mean over trials):\n\n" + by_material(rows, mode, metric, [c for c in cells if c in {r['cell'] for r in rows}][:8])
            out.append(section(f"Arms vs baseline: {label}, {mode} mode", body))

    sweep = sorted({r["cell"] for r in rows if r["cell"].startswith("sweep:")}, key=lambda c: float(c.split(":")[1]))
    if sweep:
        for mode in ("rank", "filter"):
            ent = summarise_cells(rows, mode, "success", ["baseline"] + sweep + ["oracle"])
            ent_w = summarise_cells(rows, mode, "wrench", ["baseline"] + sweep + ["oracle"])
            body = "Constant-mu planner at other assumed values (ablation d), success and wrench:\n\n" + fmt_table(ent, "success") + "\n\n" + fmt_table(ent_w, "wrench [N]")
            out.append(section(f"Assumed-mu sweep, {mode} mode", body))

    lines = []
    for mode in ("rank", "filter"):
        for a, b in (("baseline", "oracle"), ("baseline", "table_q"), ("oracle", "table_q")):
            rate, n = same_grasp_rate(rows, mode, a, b)
            lines.append(f"- {mode}: {a} and {b} choose the same grasp in {rate:.0%} of {n} trials")
        for subset_name, subset in (("low-mu", LOW), ("high-mu", HIGH)):
            rate, n = same_grasp_rate([r for r in rows if r["obj"] in subset], mode, "baseline", "oracle")
            lines.append(f"- {mode}, {subset_name}: baseline and oracle choose the same grasp in {rate:.0%} of {n} trials")
    out.append(section("How often does knowing mu change the grasp?", "\n".join(lines)))
    out.append(section("Analytical epsilon vs measured wrench at slip", eps_vs_wrench(rows)))

    # fallback / capped statistics
    ex = [r for r in rows if r.get("executed")]
    fb = Counter((r["cell"], r["mode"]) for r in ex if r.get("fallback"))
    cp = Counter((r["cell"], r["mode"]) for r in ex if r.get("capped"))
    tot = Counter((r["cell"], r["mode"]) for r in ex)
    lines = ["| cell | mode | executed | fallback (nothing holdable under cap) | force capped |", "|---|---|---|---|---|"]
    for k in sorted(tot):
        if k[0] in ("baseline", "oracle", "table_q") or k[0].startswith("head:"):
            lines.append(f"| {k[0]} | {k[1]} | {tot[k]} | {fb[k] / tot[k]:.0%} | {cp[k] / tot[k]:.0%} |")
    out.append(section("Planner fallbacks and force capping", "\n".join(lines)))

    report = "\n".join(out)
    (RESULTS / "sim" / runs[0] / "report.md").write_text(report, encoding="utf-8")
    print(report)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")   # the tables carry Greek letters, whatever the system encoding
    main(sys.argv[1:] or ["core"])
