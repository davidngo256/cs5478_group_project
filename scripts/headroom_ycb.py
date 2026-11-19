"""Scorer-only headroom study on YCB meshes (no simulator).

For each object and trial: sample N candidates, then compare the grasp chosen with the
default mu = 0.5 against the grasp an oracle chooses with the true mu, in rank mode and in
filter mode. Reports how often they agree, how much epsilon the default loses, and how often
the default's choice is not force closure at the true mu.

Usage: python scripts/headroom_ycb.py [--trials 30] [--cands 40]
"""
from __future__ import annotations

import os
# One simulation process per core (experiment.default_workers), so each worker's BLAS pool must not
# also spawn a thread per core: 20 workers x 20 OpenBLAS threads put the load average above 70 on a
# 20-core box and cost about a quarter of the wall time, with identical outcomes. Set before numpy loads.
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse
import json
from multiprocessing import Pool
from pathlib import Path

import numpy as np

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from matgrasp.experiment import default_workers
from matgrasp.planner import choose, score_candidates
from matgrasp.sampler import sample_candidates
from matgrasp.ycb import OBJECTS, characteristic_radius, load_mesh

MU_GRID = [0.15, 0.2, 0.3, 0.5, 0.8]
RESULTS = Path(__file__).resolve().parents[1] / "results"


def run_object(args):
    obj_id, trials, n_cands = args
    mesh = load_mesh(obj_id)
    rho = characteristic_radius(mesh)
    com = np.zeros(3)
    rows = []
    for t in range(trials):
        rng = np.random.default_rng(1000 * t + 17)
        cands = sample_candidates(mesh, n_cands, rng)
        q_def = score_candidates(cands, 0.5, com, rho)
        picks_def = {m: choose(cands, q_def, m) for m in ("rank", "filter")}
        for mu in MU_GRID:
            q_true = score_candidates(cands, mu, com, rho)
            n_fc = sum(q.force_closure for q in q_true)
            for mode in ("rank", "filter"):
                i_or = choose(cands, q_true, mode)
                i_def = picks_def[mode]
                row = dict(obj=obj_id, trial=t, mu=mu, mode=mode, any_fc=n_fc > 0, frac_fc=n_fc / n_cands,
                           def_none=i_def is None, oracle_none=i_or is None)
                if i_or is not None and i_def is not None:
                    row.update(same=i_def == i_or, eps_ratio=q_true[i_def].epsilon / q_true[i_or].epsilon,
                               def_not_fc=not q_true[i_def].force_closure)
                rows.append(row)
        # accept/reject view: candidates accepted at 0.5 that fail at the true mu
        acc = [k for k, q in enumerate(q_def) if q.force_closure]
        for mu in MU_GRID:
            q_true = score_candidates(cands, mu, com, rho)
            if acc:
                rows.append(dict(obj=obj_id, trial=t, mu=mu, mode="accept", n_acc=len(acc),
                                 acc_fail=float(np.mean([not q_true[k].force_closure for k in acc]))))
    return rows


def summarise(rows):
    import collections
    out = collections.defaultdict(list)
    for r in rows:
        out[(r["mode"], r["mu"])].append(r)
    lines = ["| mode | true mu | trials w/ oracle pick | default same as oracle | mean eps ratio | default pick not FC | accepted@0.5 that fail |",
             "|---|---|---|---|---|---|---|"]
    for mode in ("rank", "filter"):
        for mu in MU_GRID:
            rs = out[(mode, mu)]
            ok = [r for r in rs if "same" in r]
            acc = out[("accept", mu)]
            lines.append(f"| {mode} | {mu} | {np.mean([not r['oracle_none'] for r in rs]):.0%} | "
                         f"{np.mean([r['same'] for r in ok]) if ok else float('nan'):.0%} | "
                         f"{np.mean([r['eps_ratio'] for r in ok]) if ok else float('nan'):.2f} | "
                         f"{np.mean([r['def_not_fc'] for r in ok]) if ok else float('nan'):.0%} | "
                         f"{np.mean([r['acc_fail'] for r in acc]) if acc else float('nan'):.0%} |")
    return "\n".join(lines)


def per_object(rows):
    import collections
    lines = ["| object | material | mode | mu=0.2: same / eps ratio / def not FC | mu=0.3: same / eps ratio / def not FC | mu=0.8: same / eps ratio |", "|---|---|---|---|---|---|"]
    for obj_id, o in OBJECTS.items():
        for mode in ("rank", "filter"):
            cells = []
            for mu in (0.2, 0.3, 0.8):
                rs = [r for r in rows if r["obj"] == obj_id and r["mode"] == mode and r["mu"] == mu and "same" in r]
                if not rs:
                    cells.append("no FC candidates")
                    continue
                s = f"{np.mean([r['same'] for r in rs]):.0%} / {np.mean([r['eps_ratio'] for r in rs]):.2f}"
                if mu < 0.5:
                    s += f" / {np.mean([r['def_not_fc'] for r in rs]):.0%}"
                cells.append(s)
            lines.append(f"| {obj_id} | {o.material} | {mode} | " + " | ".join(cells) + " |")
    return "\n".join(lines)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--trials", type=int, default=30)
    ap.add_argument("--cands", type=int, default=40)
    a = ap.parse_args()
    with Pool(min(default_workers(), len(OBJECTS))) as pool:
        rows = [r for rs in pool.map(run_object, [(o, a.trials, a.cands) for o in OBJECTS]) for r in rs]
    RESULTS.mkdir(exist_ok=True)
    (RESULTS / "headroom_ycb.json").write_text(json.dumps(rows))
    md = f"# Scorer-only headroom on YCB meshes\n\n{a.trials} trials x {a.cands} candidates per object, {len(OBJECTS)} objects.\n\n## Pooled\n\n{summarise(rows)}\n\n## Per object\n\n{per_object(rows)}\n"
    (RESULTS / "headroom_ycb.md").write_text(md, encoding="utf-8")
    print(md)
