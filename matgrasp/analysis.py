"""Paired analysis of the simulation study: per-cell means with bootstrap CIs on the
paired difference against the baseline, per-material breakdown, 2x2 decomposition."""
from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

import numpy as np

from .friction import friction_bin
from .ycb import OBJECTS


def load_rows(path: Path) -> list[dict]:
    rows = [json.loads(l) for l in open(path)]
    return [r for r in rows if "error" not in r and not r.get("skipped") and r["obj"] in OBJECTS]


def _val(r: dict, metric: str):
    """Trial outcome for one cell. A cell that chose nothing is a failure: success 0, wrench 0."""
    if not r.get("executed"):
        return 0.0
    if metric == "success":
        return float(r["success"])
    if metric == "wrench":
        w = r.get("min_wrench")
        return float(w) if r.get("success") and w is not None and np.isfinite(w) else 0.0
    if metric == "fc_true":
        return float(r["fc_true"])
    if metric == "force":
        return float(r["force"])
    raise KeyError(metric)


def table_by_trial(rows: list[dict], mode: str, metric: str) -> dict[str, dict[tuple, float]]:
    """cell -> {(obj, trial): value}"""
    out: dict[str, dict] = defaultdict(dict)
    for r in rows:
        if r["mode"] == mode:
            out[r["cell"]][(r["obj"], r["trial"])] = _val(r, metric)
    return out


def paired_diff(a: dict, b: dict, n_boot: int = 2000, seed: int = 0):
    """mean(a - b) over shared trials with a 95% bootstrap CI."""
    keys = sorted(set(a) & set(b))
    if not keys:
        return float("nan"), (float("nan"), float("nan")), 0
    d = np.array([a[k] - b[k] for k in keys])
    rng = np.random.default_rng(seed)
    boots = np.array([d[rng.integers(0, len(d), len(d))].mean() for _ in range(n_boot)])
    return float(d.mean()), (float(np.percentile(boots, 2.5)), float(np.percentile(boots, 97.5))), len(keys)


def summarise_cells(rows, mode, metric, cells=None, keys_filter=None):
    """Rows of (cell, n, mean, diff vs baseline, CI)."""
    t = table_by_trial(rows, mode, metric)
    base = t["baseline"]
    if keys_filter is not None:
        base = {k: v for k, v in base.items() if keys_filter(k)}
    out = []
    for cell in (cells or sorted(t)):
        vals = t[cell]
        if keys_filter is not None:
            vals = {k: v for k, v in vals.items() if keys_filter(k)}
        shared = sorted(set(vals) & set(base))
        if not shared:
            continue
        m = float(np.mean([vals[k] for k in shared]))
        d, ci, n = paired_diff(vals, base)
        out.append((cell, n, m, d, ci))
    return out


def fmt_table(entries, metric_label: str, baseline_note=True) -> str:
    lines = [f"| cell | n | mean {metric_label} | Δ vs baseline | 95% CI |", "|---|---|---|---|---|"]
    for cell, n, m, d, ci in entries:
        lines.append(f"| {cell} | {n} | {m:.3f} | {d:+.3f} | [{ci[0]:+.3f}, {ci[1]:+.3f}] |")
    return "\n".join(lines)


def by_material(rows, mode, metric, cells):
    # tie-break by name: metal and ceramic share a nominal mu, and a set's order varies with the hash seed
    mats = sorted({r["material"] for r in rows}, key=lambda m: (__import__("matgrasp.friction", fromlist=["MATERIAL_TABLE"]).MATERIAL_TABLE[m].nominal, m))
    lines = ["| material (bin) | " + " | ".join(cells) + " |", "|---|" + "---|" * len(cells)]
    for mat in mats:
        objs = {o for o, s in OBJECTS.items() if s.material == mat}
        t = table_by_trial([r for r in rows if r["obj"] in objs], mode, metric)
        from .friction import MATERIAL_TABLE
        cells_txt = []
        for c in cells:
            vals = list(t[c].values())
            cells_txt.append(f"{np.mean(vals):.2f}" if vals else "-")
        lines.append(f"| {mat} ({friction_bin(MATERIAL_TABLE[mat].nominal)}) | " + " | ".join(cells_txt) + " |")
    return "\n".join(lines)


def two_by_two(rows, mode, metric):
    t = table_by_trial(rows, mode, metric)
    b, s, se, o = t["baseline"], t["squeeze"], t["select"], t["oracle"]
    keys = sorted(set(b) & set(s) & set(se) & set(o))
    def mean(d): return float(np.mean([d[k] for k in keys]))
    lines = [f"| grasp chosen with \\ force set with | mu = 0.5 | mu* |", "|---|---|---|",
             f"| mu = 0.5 | {mean(b):.3f} (baseline) | {mean(s):.3f} (squeeze only) |",
             f"| mu* | {mean(se):.3f} (selection only) | {mean(o):.3f} (oracle) |"]
    d_sel, ci_sel, _ = paired_diff(se, b); d_sq, ci_sq, _ = paired_diff(s, b); d_or, ci_or, _ = paired_diff(o, b)
    lines.append(f"\nselection-only gain {d_sel:+.3f} [{ci_sel[0]:+.3f}, {ci_sel[1]:+.3f}]; squeeze-only gain {d_sq:+.3f} [{ci_sq[0]:+.3f}, {ci_sq[1]:+.3f}]; oracle gain {d_or:+.3f} [{ci_or[0]:+.3f}, {ci_or[1]:+.3f}] (n = {len(keys)} paired trials)")
    return "\n".join(lines)


def same_grasp_rate(rows, mode, cell_a, cell_b):
    pa = {(r["obj"], r["trial"]): r.get("chosen") for r in rows if r["mode"] == mode and r["cell"] == cell_a}
    pb = {(r["obj"], r["trial"]): r.get("chosen") for r in rows if r["mode"] == mode and r["cell"] == cell_b}
    keys = [k for k in pa if k in pb and pa[k] is not None and pb[k] is not None]
    return float(np.mean([pa[k] == pb[k] for k in keys])) if keys else float("nan"), len(keys)


def eps_vs_wrench(rows):
    """Spearman rank correlation between eps at the true mu and the measured wrench-at-slip,
    over executed, successful grasps (pooled, and within object)."""
    from scipy.stats import spearmanr
    ex = [r for r in rows if r.get("executed") and r.get("success") and np.isfinite(r.get("min_wrench", np.nan))]
    seen, pts = set(), []
    for r in ex:
        key = (r["obj"], r["trial"], r["chosen"], r["force"])
        if key in seen:
            continue
        seen.add(key)
        pts.append((r["obj"], r["eps_true"] * 2 * r["force"], r["min_wrench"], r["eps_true"], r["force"]))
    if len(pts) < 5:
        return "not enough successful grasps"
    e = np.array([p[1] for p in pts]); w = np.array([p[2] for p in pts])
    pooled = spearmanr(e, w).statistic
    per_obj = []
    for o in OBJECTS:
        sub = [p for p in pts if p[0] == o]
        if len(sub) >= 8:
            per_obj.append(f"{o}: {spearmanr([p[1] for p in sub], [p[2] for p in sub]).statistic:+.2f} (n={len(sub)})")
    return f"Spearman(eps(mu*) x 2F, wrench at slip) pooled = {pooled:+.2f} over {len(pts)} grasps; per object: " + "; ".join(per_obj)
