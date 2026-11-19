# Does vision-estimated friction improve analytical grasp selection?

CS5478 Intelligent Robots: Algorithms and Systems (NUS, AY2026/27 Semester 1) group project.

A material-aware grasp planner estimates the friction coefficient from an image before contact. A PyBullet
study measures what that estimate is worth for grasp selection and grip force, against an oracle that knows
the true coefficient.

This repository holds the code and the results behind the final report.

## Layout

- `matgrasp/`: scorer, friction model, antipodal sampler, planner, simulator, trial runner and analysis.
  `matgrasp/heads/`: the three material heads and their YCB-photo evaluation.
- `scripts/`: study drivers (`run_study.py`, `headroom_ycb.py`), the timing chain (`run_chain.sh`), the
  derived-file builders (`build_reports.sh`, `analyse_*.py`, `compare_runs.py`, `plot_sim.py`,
  `draw_diagrams.py`) and the simulation clips (`record_clips.py`).
- `tests/`: pytest.
- `results/`: raw simulation rows, per-run tables, figures, the demo clips, head posteriors and summaries,
  timing logs (`timing_idle/` this machine, `timing_idle_l4/` the earlier 4-vCPU / NVIDIA L4 box).
  `results/REPORT.md` is the results write-up.
- `data/` (not in git, about 1.8GB in full): YCB meshes and photographs, the MINC-2500 subset and model
  weights. See "Data".

## Setup

- [uv](https://docs.astral.sh/uv/) manages the environment.
- `uv sync` creates `.venv` with Python 3.12 and every dependency. PyBullet compiles from source and takes
  several minutes.
- torch comes from the CUDA 13.0 index on aarch64 Linux, the CUDA 12.6 index on x86_64 Linux and the CPU index
  elsewhere.
- `uv run pytest` runs the 62 tests in about 10s. They need no GPU and no data.

## Quick check

Neither step needs a GPU or the model weights.

- A short simulation run:
  `uv run python scripts/run_study.py smoke --trials 4 --objects 038_padlock 061_foam_brick`
  - It downloads the two YCB meshes (16MB), runs four trials per object and writes
    `results/sim/smoke/rows.jsonl`.
  - About 20s on a 20-core machine.
  - `uv run python scripts/analyse_sim.py smoke` prints its tables.
- `scripts/build_reports.sh` rebuilds every table and figure under `results/` from the tracked raw rows, in
  about 30s.
  - The rebuild is deterministic: `git status` stays clean.
  - The figures use IBM Plex Sans and IBM Plex Mono. Without the two faces matplotlib falls back to its default
    and the figures differ.

## Data

- Meshes: downloaded on demand from the YCB server by `matgrasp.ycb.ensure_mesh`. The simulation runs need
  nothing else.
- Photographs for the material heads: `uv run python -m matgrasp.heads.ycb_photos`.
- Skillet-lid renders (the YCB server has no photographs of it): `uv run python -m matgrasp.heads.render_views`.
- MINC-2500 subset for the MobileNet fine-tune: `uv run python -m matgrasp.heads.minc`.
- CLIP weights: downloaded into `data/models/open_clip` on first use.
- DMS46 weights: placed by hand. Download `dms46_v1.zip` from Apple's release at
  https://github.com/apple/ml-dms-dataset and put `DMS46_v1.pt` in `data/models/`. Save that repository's
  `taxonomy.json` as `data/models/dms_taxonomy.json`.

## Reproducing the study

- The four simulation runs alone, from the tracked head posteriors in `results/heads/*_ycb.json`:
  - `uv run python scripts/run_study.py core --trials 120 --name core120`
  - `uv run python scripts/run_study.py heads --trials 120 --name heads120`
  - `uv run python scripts/run_study.py lean --trials 120 --gamma-scale 2.0 --name torsion_k2.0`
  - `uv run python scripts/run_study.py lean --trials 120 --gamma-scale 3.2 --name torsion_k3.2`
  - About 6 minutes each for the first two and 1 minute each for the torsion runs on a 20-core machine.
- Everything, with the data in place: `scripts/run_chain.sh` re-runs every stage one at a time (fine-tune, head
  evaluation and latency, headroom study, the four simulation runs) and records the timings in
  `results/timing_idle/`. About 25 minutes on a 20-core machine with nothing else running.
- `scripts/build_reports.sh` then rebuilds the tables, figures and the heads README from the raw results.
- Trials are seeded by object and trial index, so every run uses the same trials. Outcomes are bit-identical
  on one machine and about 98% identical across x86-64 and aarch64.
