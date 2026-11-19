#!/usr/bin/env bash
# Re-run every stage of the project, one at a time, on an otherwise idle machine and time each
# stage: the protocol behind results/timing_idle/ (this machine), results/timing_idle_l4/ (the same
# chain on the 4-vCPU / NVIDIA L4 box) and REPORT.md section 8.
#
# Usage, from the repo root, with nothing else running on the box:
#   scripts/run_chain.sh [out_dir]          # default results/timing_idle
#
# Writes to out_dir:
#   chain.log     one START/END line per stage with the 1/5/15-minute load averages
#   stages.csv    stage, start/end epoch, seconds, exit code, 1-minute load at start/end
#   <stage>.out   each stage's stdout and stderr
#   load.csv      load averages and GPU utilisation/memory sampled once a minute
#
# Stages, in order: the MobileNet fine-tune; the three head evaluations (the stored *_ycb.json are
# removed first so every posterior is recomputed rather than reused; git keeps the previous ones);
# three latency passes per head; the scorer-only headroom study; core120, heads120 and the two
# torsion runs. Pauses let the load average settle before the latency timings. The chain stops at
# the first stage that fails.
set -u
ROOT=$(cd "$(dirname "$0")/.." && pwd)
cd "$ROOT"
OUT=${1:-results/timing_idle}
PY=${PY:-.venv/bin/python}
mkdir -p "$OUT"
LOG="$OUT/chain.log"
CSV="$OUT/stages.csv"
LOADCSV="$OUT/load.csv"

now() { date -u +%Y-%m-%dT%H:%M:%SZ; }
load() { cut -d' ' -f1-3 /proc/loadavg; }
load1() { cut -d' ' -f1 /proc/loadavg; }
say() { echo "$(now) $*" | tee -a "$LOG"; }

cpu=$(lscpu | sed -n 's/^Model name: *//p' | sort -u | paste -sd'+' -)
gpu=$(nvidia-smi --query-gpu=name --format=csv,noheader 2>/dev/null | paste -sd',' -)
say "machine: $(nproc) CPUs ($cpu), GPU ${gpu:-none}, uptime $(uptime -p), $($PY --version 2>&1)"
say "other GPU processes: $(nvidia-smi --query-compute-apps=pid,process_name --format=csv,noheader 2>/dev/null | paste -sd';' -)"

# once-a-minute load / GPU sampler for the whole chain
echo "utc,load1,load5,gpu_util_pct,gpu_mem_mib" > "$LOADCSV"
(
  while true; do
    g=$(nvidia-smi --query-gpu=utilization.gpu,memory.used --format=csv,noheader,nounits 2>/dev/null | head -1 | tr -d ' ')
    echo "$(now),$(cut -d' ' -f1,2 /proc/loadavg | tr ' ' ','),${g:-,}" >> "$LOADCSV"
    sleep 60
  done
) &
SAMPLER=$!
trap 'kill $SAMPLER 2>/dev/null' EXIT

echo "stage,start_epoch,end_epoch,seconds,exit_code,load1_start,load1_end" > "$CSV"

stage() {   # stage <name> <command...>
  local name=$1; shift
  local l0 t0 t1 rc l1
  l0=$(load1); t0=$(date +%s)
  say "START $name | load $(load) | $*"
  "$@" > "$OUT/$name.out" 2>&1
  rc=$?
  t1=$(date +%s); l1=$(load1)
  say "END   $name | rc=$rc | $((t1 - t0)) s | load $(load)"
  echo "$name,$t0,$t1,$((t1 - t0)),$rc,$l0,$l1" >> "$CSV"
  if [ "$rc" -ne 0 ]; then say "CHAIN_FAILED at $name"; exit "$rc"; fi
}

pause() { say "settling $1 s"; sleep "$1"; }

pause 90
stage mobilenet_train "$PY" -m matgrasp.heads.mobilenet train
pause 60
rm -f results/heads/dms46_ycb.json results/heads/clip_ycb.json results/heads/mobilenet_ycb.json
stage eval_dms46 "$PY" -m matgrasp.heads.dms46
stage eval_clip "$PY" -m matgrasp.heads.clip_head
stage eval_mobilenet "$PY" -m matgrasp.heads.mobilenet
for head in dms46 clip_head mobilenet; do
  pause 45
  for i in 1 2 3; do stage "latency_${head}_$i" "$PY" -m "matgrasp.heads.$head" latency; done
done
pause 45
stage headroom "$PY" scripts/headroom_ycb.py --trials 30 --cands 40
stage core120 "$PY" scripts/run_study.py core --trials 120 --name core120
stage heads120 "$PY" scripts/run_study.py heads --trials 120 --name heads120
stage torsion_k2.0 "$PY" scripts/run_study.py lean --trials 120 --gamma-scale 2.0 --name torsion_k2.0
stage torsion_k3.2 "$PY" scripts/run_study.py lean --trials 120 --gamma-scale 3.2 --name torsion_k3.2
say CHAIN_DONE
