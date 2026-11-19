#!/usr/bin/env bash
# Rebuild every file derived from the raw results after scripts/run_chain.sh: the per-run tables
# (results/sim/<run>/report.md), the heads table merged with the core run, the block analyses, the
# torsion comparison, the figures in results/figures and results/heads/README.md.
# Usage, from the repo root: scripts/build_reports.sh
set -eu
ROOT=$(cd "$(dirname "$0")/.." && pwd)
cd "$ROOT"
PY=${PY:-.venv/bin/python}
"$PY" scripts/analyse_sim.py heads120 core120 > /dev/null        # writes results/sim/heads120/report.md ...
mv results/sim/heads120/report.md results/sim/heads120/report_merged_with_core.md
for run in core120 heads120 torsion_k2.0 torsion_k3.2; do
  "$PY" scripts/analyse_sim.py "$run" > /dev/null
done
for run in core120 heads120; do
  for mode in rank filter; do "$PY" scripts/analyse_blocks.py "$run" --mode "$mode" > /dev/null; done
done
"$PY" scripts/compare_runs.py core120 torsion_k2.0 torsion_k3.2 --out results/sim/torsion_comparison.md > /dev/null
"$PY" scripts/plot_sim.py core120 heads120
"$PY" scripts/draw_diagrams.py
"$PY" -m matgrasp.heads.report
