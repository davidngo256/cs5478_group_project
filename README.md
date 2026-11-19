# Does vision-estimated friction improve analytical grasp selection?

CS5478 Intelligent Robots: Algorithms and Systems (NUS, AY2026/27 Semester 1) group project.

A material-aware grasp planner estimates the friction coefficient from an image before contact. A PyBullet
study measures what that estimate is worth for grasp selection and grip force, against an oracle that knows
the true coefficient.

This repository holds the code and the results behind the final report.

## Layout

- `matgrasp/`: scorer, friction model, antipodal sampler, planner, simulator, trial runner and analysis.
  `matgrasp/heads/`: the three material heads and their YCB-photo evaluation. `matgrasp/hulls/`: the collision
  hulls of the ten objects, as the study ran on them.
- `scripts/`: study drivers (`run_study.py`, `headroom_ycb.py`), the timing chain (`run_chain.sh`), the
  derived-file builders (`build_reports.sh`, `analyse_*.py`, `compare_runs.py`, `plot_sim.py`,
  `draw_diagrams.py`) and the simulation clips (`record_clips.py`).
- `tests/`: pytest.
- `fonts/`: the three IBM Plex faces the figures use, under the SIL Open Font License (`fonts/LICENSE.txt`).
- `results/`: raw simulation rows, per-run tables, figures, the demo clips, head posteriors and summaries,
  timing logs (`timing_idle/` this machine, `timing_idle_l4/` the earlier 4-vCPU / NVIDIA L4 box).
  `results/REPORT.md` is the results write-up.
- `data/` (not in git, about 1.6GB in full): YCB meshes and photographs, the MINC-2500 subset and model
  weights. See "Data".

## Setup

- [uv](https://docs.astral.sh/uv/) manages the environment (checked with uv 0.6.0, 0.13.1 and 0.13.9).
- `uv sync` creates `.venv` with Python 3.12 and every dependency.
  - PyBullet has no wheel for Python 3.12 and compiles from source, so a C++ compiler must be installed
    (`sudo apt install build-essential` on Debian or Ubuntu; nothing else was needed on a bare Ubuntu 24.04).
  - The install took 35s on a 20-core machine; expect a few minutes on a laptop. The environment fills about
    6GB on Linux, most of it torch and its CUDA libraries.
- torch comes from the CUDA 13.0 index on aarch64 Linux, the CUDA 12.6 index on x86_64 Linux and the CPU index
  elsewhere. No GPU is needed: the simulation is CPU-only, and the material heads fall back to the CPU.
- Platforms: developed and run on Linux, x86-64 and aarch64. The lock file also resolves for Windows and for
  Apple Silicon under macOS 14 or later, but the code was not run there. Intel Macs have no torch wheel.
  - macOS: PyBullet's bundled zlib redefines `fdopen`, which Xcode 16.3 and later reject, so its build is
    expected to stop there. `CFLAGS="-Dfdopen=fdopen" uv sync` avoids the redefinition. This was checked by
    forcing the header's macOS branch on Linux, not on a Mac.
  - Windows: use WSL. The two shell scripts need bash.
  - The Docker image below is the checked route on both.
- `uv run pytest` runs the 62 tests in about 10s. They need no GPU and no data.

## Docker

A Linux environment for macOS and Windows, where the native install was not run.

- `docker build -t matgrasp .` builds it: Ubuntu 24.04, a C++ compiler, uv and the locked packages. The build
  took 3 minutes on a 20-core machine and the image fills 10GB.
- `docker run --rm matgrasp` runs the tests.
- `docker run --rm -it --shm-size=2g matgrasp bash` opens a shell in the repository for every command below.
  - `--shm-size=2g`: the MobileNet fine-tune needs more shared memory than Docker's 64MB default.
  - `-v "$PWD/data:/repo/data" -v "$PWD/results:/repo/results"` keeps the data and the results on the host.
  - `--gpus all` passes an NVIDIA GPU through on a Linux host with the NVIDIA container toolkit (not checked).
    Without it everything runs on the CPU.
- Checked on linux/arm64, the platform Docker uses on Apple Silicon, with no GPU: the tests, the quick check
  and the whole chain, which takes 36 minutes on the CPU.

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
  - The figures load their type from `fonts/`, so no font needs installing.
  - On the machine that produced the results the rebuild leaves `git status` clean. On another platform the
    PNGs can differ in a few bytes.

## Data

- Meshes: downloaded on demand from the YCB server by `matgrasp.ycb.ensure_mesh`. The simulation runs need
  nothing else.
- Photographs for the material heads: `uv run python -m matgrasp.heads.ycb_photos`.
  - It streams nine archives and keeps 48 files of each, in about 6 minutes.
  - The skillet lid has no archive on the YCB server: the command reports a 404 for it and moves on.
- Skillet-lid renders, in place of its photographs: `uv run python -m matgrasp.heads.render_views`.
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
  - About 6 minutes each for the first two and 3 minutes each for the torsion runs on a 20-core machine.
  - On a fresh clone the first run also downloads the ten meshes (about 170MB).
- Everything, with the data in place: `scripts/run_chain.sh` re-runs every stage one at a time (fine-tune, head
  evaluation and latency, headroom study, the four simulation runs) and records the timings in
  `results/timing_idle/`. About 25 minutes on a 20-core machine with nothing else running.
  - The script needs Linux: it reads `/proc/loadavg` and calls `lscpu` and `nproc`. On another system run its
    stage commands by hand; they are the `stage` lines at the end of the script.
  - The chain retrains MobileNet, and GPU training is not bit-reproducible, so that head's numbers move a
    little. The four commands above use the tracked posteriors instead.
- `scripts/build_reports.sh` then rebuilds the tables, figures and the heads README from the raw results.
- Repeatability: trials are seeded by object and trial index, so every run draws the same poses and candidates
  and the planner makes the same choices.
  - The executed outcome also depends slightly on what a worker process simulated before the trial. A re-run of
    `torsion_k2.0` on the same machine changed slip or wrench in 3.5% of its rows and lift success in 0.12%.
  - Across x86-64 and aarch64 about 98% of outcomes agree.
  - The collision hulls are part of the inputs and ship in `matgrasp/hulls/`. With hulls recomputed on another
    machine, 4.5% of lift outcomes changed.
  - `results/REPORT.md` covers this under "Reproducibility".
