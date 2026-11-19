"""Run the simulation study. Usage:
  python scripts/run_study.py core  --trials 40            # 2x2, table arms, quantile ablation, mu sweep
  python scripts/run_study.py heads --trials 40            # baseline/oracle + classifier-head cells (needs results/heads/*_ycb.json)
  python scripts/run_study.py lean  --trials 40 --gamma-scale 2.2 --name torsion_k2.2
                                                           # 2x2 + table arms only, planner's torsional term scaled
"""
import os
# One simulation process per core (experiment.default_workers), so each worker's BLAS pool must not
# also spawn a thread per core: 20 workers x 20 OpenBLAS threads put the load average above 70 on a
# 20-core box and cost about a quarter of the wall time, with identical outcomes. Set before numpy loads.
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")
import argparse, json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from matgrasp.experiment import Config, default_workers, run_study, RESULTS
from matgrasp.ycb import OBJECTS


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("run", choices=["core", "heads", "final", "lean", "smoke"])
    ap.add_argument("--trials", type=int, default=40)
    ap.add_argument("--workers", type=int, default=default_workers(), help="simulation processes (default: CPU count)")
    ap.add_argument("--objects", nargs="*", default=list(OBJECTS))
    ap.add_argument("--name", default=None)
    ap.add_argument("--gamma-scale", type=float, default=1.0, help="planner's torsional coefficient multiplier (physics unchanged)")
    a = ap.parse_args()
    if a.run == "core":
        cfg = Config(n_cands=40, sweep=True)
    elif a.run in ("heads", "final"):
        heads = {}
        for f in sorted((RESULTS / "heads").glob("*_ycb.json")):
            name = f.name.replace("_ycb.json", "")
            d = json.loads(f.read_text())
            heads[name] = {o: d[o]["mean_probs"] for o in d if "mean_probs" in d[o]}
        if not heads:
            sys.exit("no head posteriors found in results/heads")
        print("heads:", {k: sorted(v) for k, v in heads.items()})
        cfg = Config(n_cands=40, sweep=(a.run == "final"), quantiles=(0.05, 0.25) if a.run == "final" else (), heads=heads)
    elif a.run == "lean":
        cfg = Config(n_cands=40, sweep=False, quantiles=())
    else:
        cfg = Config(n_cands=20, sweep=False, quantiles=())
    cfg.gamma_scale = a.gamma_scale
    run_study(a.name or a.run, a.objects, a.trials, cfg, workers=a.workers)


# The workers are processes. Where they are spawned (macOS, Windows) each one imports this file again,
# so the study must start only when the file is run as a script.
if __name__ == "__main__":
    main()
