# Does vision-estimated friction improve analytical grasp selection?

`261015 · CS5478 RESULTS WRITE-UP · V1.0`

Results of the simulation study.

- Code: `matgrasp/`.
- Raw rows: `results/sim/core120/` and `results/sim/heads120/`.
- Per-run tables: the `report.md` files there.
- Figures: `fig_*.png` (drawn for the report; `slides/` holds the same figures at deck size; `fig_demo.png` is
  report-only, the decks play the clips).
- Demo clips: `results/clips/`, one trial of the core run replayed as four looping GIFs (§3.8).

Run facts:

- Date: 15-Oct-2026, nothing else running on the box.
- Machine: a 20-core aarch64 NVIDIA GB10 box (10 Cortex-X925 + 10 Cortex-A725 cores, 121GB unified memory).
- Software: PyBullet 3.2.7 built from source, 20 workers; heads on the GPU, torch 2.14.1+cu130.
- Scope: the whole project re-run end to end (MobileNet fine-tune, head evaluation and latency, headroom
  study, all four simulation runs).
- Driver: `scripts/run_chain.sh`, one stage at a time --> every timing is uncontended (§8).
- Previous machine: the same chain ran on 1-Oct-2026 on a 4-vCPU Google Cloud VM with an NVIDIA L4 (logs in
  `results/timing_idle_l4/`).
- Trials: 120 per object, simulator reset to a saved pristine state before every trial.
- Seed: `zlib.crc32(obj_id)`, fixed on 1-Oct.
  - It replaced the per-interpreter salted `hash()` that had made every earlier invocation draw different
    trials.
  - --> Every run below, and the 1-Oct runs, draw the same true μ and poses and, up to floating-point
    differences between the two machines (§8), the same candidates.
- Removed runs: the 23-Sep runs and the earlier 40-trial runs were drawn with the salted seed --> removed
  from `results/sim` (they remain in the git history).
- What moved between the 1-Oct and 15-Oct numbers: §8.

## 1. What was built

- **Scorer** (`wrench.py`):
  - Soft-finger contact model: Coulomb cone linearised to 8 edges plus a torsional limit γ = (2/3)·a·μ with
    a = 8mm.
  - 6-D wrench hull about the CoM, torques scaled by ρ = half the largest extent.
  - Ferrari–Canny ε, the hull volume ν, and the minimum total normal force that resists a given wrench.
- **Friction model** (`friction.py`):
  - Material → μ table, assumed values against a rubber pad: e.g. glass 0.20 [0.12, 0.30], metal 0.30,
    plastic 0.35, paper 0.50, foam 0.75, rubber 0.80.
  - A mixture distribution p(μ) induced by class probabilities, and its quantiles.
  - True μ* of each trial: drawn from a normal centred on the nominal value with s.d. 1.5× the table
    half-range. --> The oracle knows something the table does not.
- **Candidate generator** (`sampler.py`):
  - Seeded antipodal sampling on the YCB mesh (Dex-Net style).
  - Closing direction within 25° of the normal at both contacts, width ≤ 8cm (Panda).
  - A μ-independent generator score prefers horizontal closing axes near the centroid.
- **Planner** (`planner.py`):
  - Rank mode: argmax ε. Filter mode: first candidate in generator order that passes.
  - A candidate is acceptable if it is force closure at the planning μ and the planner believes it can hold
    the gravity wrench within a per-object grip-force cap.
  - Grip force = 1.5 × analytical minimum, floored at 3N per finger and clipped at the cap.
- **Simulator** (`sim.py`):
  - PyBullet, floating parallel-jaw gripper with force-limited finger motors, 2cm tip pads.
  - Per-trial object friction μ* (lateral) and γ(μ*) (torsional).
  - A trial: settle the object (even trials upright with random yaw, odd trials a random drop), then sample
    up to 40 feasible candidates (collision-free open gripper at one of 11 approach angles; 40 in every trial
    but 43% of the mustard bottle's and 6% of the bleach bottle's).
  - Each experimental cell: place, close, lift 20cm, hold 2s. Then ramp an external wrench along each of 6
    friction-mediated directions in the gripper frame (tangential ±x, ±z, torsion ±y) until the object moves
    1cm or 10°.
  - Calibration on a box: tangential slip at 7.3/15.6/23.6N vs the 2μF prediction 8/16/24N; torsion at
    0.14/0.27/0.40N·m for μ = 0.2/0.4/0.6, linear in μ.
- **Objects**:
  - 028_skillet_lid (glass), 038_padlock and 010_potted_meat_can (metal), 029_plate (ceramic),
    006_mustard_bottle and 021_bleach_cleanser (plastic), 003_cracker_box and 004_sugar_box (paper),
    061_foam_brick (foam), 057_racquetball (rubber).
  - Dropped: 036_wood_block, 007_tuna_fish_can and 025_mug. A Panda pinch cannot grasp them on a table (all
    dimensions > 8cm, an 8.6cm disc, a body at the gripper limit).
- **Cells** (all planned on the same candidates and executed from the same saved state --> trials are paired):
  - baseline (μ = 0.5 for grasp and force), squeeze-only (baseline grasp, oracle force), selection-only
    (oracle grasp, baseline force), oracle (μ* for both).
  - Table arms: perfect classifier + table, planned at the mean or at quantiles 0.05/0.10/0.25 of p(μ).
  - Constant-μ sweep {0.1 … 0.7, 0.9}; the baseline is its 0.5.
  - Second run: the three real material heads at quantile 0.1, at the mean, and force-only (baseline grasp,
    force from the quantile; §7.2).

- Trials: 120 per object; 992 of 1200 usable (208 skipped for having fewer than 8 feasible candidates, mostly
  random-drop poses of the boxes and bottles).
- Metrics: lift success under the force cap (held after the lift, < 15° pivot) and wrench at slip (0 for a
  failed grasp). Paired bootstrap 95% CIs on the difference to baseline.

## 2. Scorer-only headroom on YCB meshes (no simulator)

`results/headroom_ycb.md`, 10 objects × 30 trials × 40 candidates, argmax-ε at μ = 0.5 vs at the true μ:

| true μ | rank: same pick / ε ratio / default pick not FC | filter: same pick / ε ratio / default pick not FC | accepted at 0.5 that fail |
|---|---|---|---|
| 0.15 | 65% / 0.86 / 8% | 45% / 0.46 / 53% | 84% |
| 0.2 | 71% / 0.93 / 3% | 54% / 0.55 / 44% | 74% |
| 0.3 | 85% / 0.98 / 0% | 69% / 0.70 / 27% | 51% |
| 0.8 | 90% / 0.99 / 0% | 93% / 1.03 / 0% | 0% |

- Ranking by ε is almost μ-invariant.
- Used as an accept/reject test, the constant-μ assumption waves through grasps that are not force closure on
  slippery objects.
- This is what the analytical model predicts. --> The simulation below tests whether it translates into
  outcomes.

## 3. Simulation: does knowing μ help, and how?

### 3.1 The 2×2 (rank mode, 992 paired trials)

Lift success:

| grasp chosen with \ force set with | μ = 0.5 | μ* |
|---|---|---|
| μ = 0.5 | **0.574** (baseline) | 0.643 (squeeze only) |
| μ* | 0.569 (selection only) | **0.621** (oracle) |

- oracle gain **+0.047 [+0.024, +0.071]**; squeeze-only **+0.070 [+0.051, +0.089]**; selection-only −0.005 [−0.022, +0.013]
- low-μ objects (n = 606): oracle **+0.071 [+0.040, +0.104]**, squeeze-only **+0.106 [+0.079, +0.134]**, selection-only −0.013 [−0.036, +0.008]
- high-μ objects (n = 386): oracle +0.010 [−0.021, +0.041], squeeze-only +0.013 [−0.005, +0.031], selection-only +0.008 [−0.018, +0.034]

Wrench at slip:

- oracle +0.190N [+0.118, +0.268] (baseline 1.33N); squeeze-only +0.268 [+0.210, +0.330]; selection-only
  −0.026 [−0.082, +0.030]
- low-μ objects: oracle +0.31N [+0.21, +0.42]; high-μ objects: −0.005N (n.s.)

Filter mode gives the same picture:

- oracle +0.042 [+0.017, +0.067], squeeze-only +0.066 [+0.045, +0.087], selection-only −0.022 [−0.041, −0.004]
  in success
- selection-only −0.092N [−0.152, −0.033] in wrench at slip --> the one mode in which the selection-only cell
  is distinguishable from the baseline, and slightly worse than it

Excluding the plate (never lifted by any arm, see §3.7) changes nothing qualitatively: oracle +0.052
[+0.029, +0.076] pooled, +0.084 [+0.047, +0.121] on low-μ objects, selection-only −0.016 on low-μ objects.

Reading:

- Knowing the true friction coefficient improves grasp outcomes by 5 points pooled and 7 points on low-μ
  objects. It does nothing on high-μ objects.
- The gain is entirely a grip-force effect.
  - The baseline's grasp with the oracle's force reproduces all of it (+0.070 pooled, +0.106 on low-μ objects).
  - The oracle's grasp with the baseline's force is indistinguishable from the baseline (−0.005 pooled, −0.013
    on low-μ objects; slightly negative in filter mode).
- Choosing a different grasp with the true μ adds nothing at the default torsional model (§7.3 looks at a
  calibrated one).
- H1 holds in its "where" (low μ, not high μ) but not in its "how" (selection, filter mode).

### 3.2 Per material (rank mode, success; baseline → oracle)

| material | baseline | oracle | note |
|---|---|---|---|
| glass (lid) | 0.46 | 0.49 | rim/knob grasps, torsion-limited; force alone gives 0.57 |
| metal (padlock, can) | 0.66 | **0.87** | the clearest win, +21 pts |
| ceramic (plate) | 0.00 | 0.00 | 4 mm rim pinch cannot hold 279 g at 13 cm |
| plastic (bottles) | 0.25 | 0.23 | heavy, tall; most grasps pivot |
| paper (boxes) | 0.63 | 0.66 | assuming 0.5 is right |
| foam, rubber | 1.00 | 1.00 | assuming 0.5 is merely conservative |

### 3.3 How often does μ change the grasp?

- Baseline and oracle choose the same candidate in 74% of trials in rank mode (68% on low-μ objects) and 65%
  in filter mode (50% on low-μ objects).
- --> μ does change the choice in a quarter to a half of the trials. The changed choice is not better in
  simulation.

Why:

- At low μ the ε ranking is dominated by the torsional term. That is the part of the point-contact model that
  the physics reproduces least faithfully (finite 2cm pads give ~3× the model's torsional capacity on flat
  faces and ~1× on curved ones).
- The ordering that the model produces at μ = 0.5, driven by cone geometry, is as good a predictor of success
  as the ordering at μ*.
- The analytical requirement is also very conservative for off-centre grasps (3–6× the ideal mg/2μ at 1–3cm
  off the centre of mass; the grasps the planner chose need a median 2.5×). --> At
  low μ the planner more often finds nothing it believes holdable under the cap (29% fallbacks for the oracle
  vs 22% for the baseline) and falls back to a force-closure-only choice.
- §7.3 tests this explanation directly by scaling the torsional term.

### 3.4 Perfect classifier + table (H2 ceiling) and the quantile (ablation b)

| arm (rank mode) | Δ success vs baseline | Δ wrench [N] |
|---|---|---|
| oracle (true μ*) | +0.047 [+0.024, +0.071] | +0.190 [+0.118, +0.268] |
| table, mean of p(μ) | +0.043 [+0.023, +0.065] | +0.262 [+0.188, +0.334] |
| table, quantile 0.25 | +0.053 [+0.030, +0.076] | +0.331 |
| table, quantile 0.10 | +0.044 [+0.020, +0.069] | +0.307 |
| table, quantile 0.05 | +0.036 [+0.012, +0.061] | +0.289 |
| table, quantile 0.10, force only (baseline grasp) | **+0.066 [+0.046, +0.085]** | +0.440 |

- A perfect material classifier feeding the lookup table at the mean of p(μ) recovers nearly all of the
  oracle's success gain (+0.043 vs +0.047; paired difference −0.004 [−0.021, +0.013]).
  - The within-class spread of μ* is not what limits outcomes.
  - The table's mean for paper is 0.51, next to the baseline's 0.5 --> this arm rarely changes the grasp on
    the boxes (11 of 146 trials in rank mode).
- Planning at a pessimistic quantile is neutral for success down to q = 0.10 (+0.053 at q = 0.25, +0.044 at
  q = 0.10, against +0.043 at the mean).
  - It starts to cost at q = 0.05 (+0.036). The more pessimistic the planner, the more often it finds nothing
    holdable under the cap (32% fallbacks at q = 0.10 vs 22% for the baseline).
  - It buys extra wrench-at-slip through higher force (+0.31N against +0.26N at the mean).
- Using the quantile for the force only, with the baseline's grasp, is the best table arm on both metrics
  (+0.066, +0.44N).
- --> With a perfect classifier the pessimistic-quantile design of the proposal is free in success. Whether it
  is robust to misclassification is H3 (§4).

### 3.5 Constant-μ sweep (ablation d)

- Success of a constant-μ planner peaks at an assumed μ of 0.4 (+0.021 [+0.001, +0.041]) and falls off on
  both sides (0.1: −0.046; 0.9: −0.103).
- The oracle (+0.047) is above every constant; its margin over μ = 0.4 is +0.026 [+0.006, +0.046].
- Wrench at slip: constants of 0.1–0.2 (+0.27, +0.27) exceed the oracle (+0.19) and 0.3 matches it (+0.20).
  - Assuming low friction everywhere squeezes harder and is as robust as knowing μ, until the cap makes the
    planner reject everything (μ = 0.1 loses 5 points of success).
- See `fig_sweep.png`.

### 3.6 Does ε predict the measured wrench at slip?

- Spearman correlation between ε(μ*) × total grip force and the measured wrench at slip over 7029 successful
  grasps: **+0.33 pooled**.
- Per object: +0.98 (racquetball), +0.86 (foam brick), +0.77 (mustard bottle), +0.72 (potted meat can),
  +0.66 (padlock), +0.59 (cracker box), +0.53 (sugar box), +0.35 (skillet lid), +0.05 (bleach).
- ε is a good predictor for compact, convex objects. It is a poor one for thin rims and tall heavy bottles,
  where the binding constraint is torsion and finite-pad effects.
- This agrees with Rubert et al. (2017): classical metrics predict success only moderately.

### 3.7 Objects where nothing works

- The plate is never lifted by any arm (415 distinct executions, all at its 27N force cap). A 4mm rim between
  2cm pads cannot resist the gravity torque of a 279g plate whose CoM is 13cm away.
- The bleach cleanser (1.13kg) succeeds in 19% of executions, the skillet lid in 57% (median pivot 6°).
- These are the torsion-limited cases the proposal singled out. --> They are where the analytical model's
  torsional term matters most and where it is least accurate.

### 3.8 One trial in detail: the demo clips

- Trial: 118 of the padlock, rank mode, from `core120`; upright pose with a random yaw, true μ* = 0.181 (metal,
  table 0.30), cap 29.8N, 40 candidates, 16 of them force closure at μ*.
- Clips: `results/clips/038_padlock_t118_<cell>.gif`, recorded 20-Oct-2026 by `scripts/record_clips.py` (the
  close, the 20cm lift and the 2s hold at 20 fps; the camera rides with the gripper). The script replays the
  trial from the saved state through the study's own `Runner.prepare` and `planner.decide` and stops if a
  cell's candidate, force or outcome differs from `rows.jsonl`; all four matched, slip within 0.3mm of the run.
- Where: the demo slide of the final deck plays the four clips; `fig_demo.png` puts one still per cell, 0.3s into
  the lift, in the report.
- Why this trial: of the 992 rank-mode trials, 10 have baseline and selection-only failing while squeeze-only
  and the oracle succeed, with different candidates and both contacts made. Trial 118 is the upright padlock
  among them, the object with the largest oracle gain (§3.2).

| cell | planner μ (grasp / force) | candidate | force per finger | outcome | slip | wrench at slip |
|---|---|---|---|---|---|---|
| baseline | 0.5 / 0.5 | 32 | 6.0N | dropped during the lift | 200mm | 0 |
| squeeze only | 0.5 / μ* | 32 | 17.3N | held | 14.6mm | 1.92N |
| selection only | μ* / 0.5 | 19 | 7.5N | dropped during the lift | 200mm | 0 |
| oracle | μ* / μ* | 19 | 20.2N | held | 15.6mm | 2.08N |
| table, mean (μ = 0.30) | 0.30 / 0.30 | 32 | 10.1N | held | 15.0mm | 1.67N |
| table, q = 0.10 (μ = 0.22) | 0.22 / 0.22 | 19 | 16.7N | held | 13.3mm | 1.83N |
| table, force only | 0.5 / 0.22 | 32 | 14.1N | held | 14.2mm | 2.17N |

- No cell is capped --> every force is 1.5× the analytical minimum at the planner's μ (8.1N total for
  candidate 32 at μ = 0.5, 23.1N at μ*).
- Both grasps drop the padlock at the force set with μ = 0.5 and hold it at the force set with μ*. --> The
  grasp choice does not decide this trial; the force does. This is the pooled 2×2 result (§3.1) on one trial.
- The table's metal entry (0.30) sits above μ* = 0.18, and its 10.1N still holds. --> The 1.5× margin and the
  conservative analytical requirement absorb the within-class spread here, as §3.4 found over all trials.

## 4. Real material heads (H2 with a real classifier, H3)

- Three heads, evaluated on 24 real YCB photographs per object (archive masks).
- The skillet lid has no photographs on the YCB server --> its rendered views are excluded from accuracy.
- Details: `results/heads/README.md`.

| head | params | latency (bs 1, NVIDIA GB10, incl. CPU preprocessing) | YCB object-level top-1 | MINC test acc (10 cls) | ECE before → after temperature |
|---|---|---|---|---|---|
| DMS46 (Apple, per-pixel, released) | 46.7M | 21 ± 6 ms (min 10) | 2/9 | – | – |
| CLIP ViT-B/32 zero-shot (OpenCLIP, LAION-2B weights) | 151M | 11 ± 1 ms (min 7) | 3/9 | – | – |
| MobileNetV3-Small, MINC fine-tune | **1.53M** | 8 ± 1 ms (min 6) | 2/9 | 71.4% | 0.071 → 0.029 (T = 1.40) |

All three are weak on product photographs:

- Cardboard is recognised.
- Printed cans and bottles read as "painted"/"paper".
- The foam brick is never recognised; the ball only by CLIP.
- MobileNet cannot output foam or rubber at all (not MINC classes).
- This is the domain shift the proposal flagged. --> H2/H3 is a genuine test.

Second simulation run:

- `heads120`, the same 992 trials as `core120`.
- Same cells plus each head at quantile 0.1, at the mean of its p(μ), and force-only (the baseline's grasp
  with the force set from the head's quantile).
- Rank mode, lift success.
- The cells shared with `core120` choose the same grasps and forces in every trial. Their executed outcomes
  differ slightly (109 of 13 888 shared rows flip success, §6). --> The oracle reads +0.048 here and +0.047
  in §3.

| arm | Δ success vs baseline | Δ success, low-μ objects (n = 606) | Δ success, high-μ objects (n = 386) | Δ wrench [N] |
|---|---|---|---|---|
| oracle (true μ*) | +0.048 [+0.025, +0.072] | +0.071 [+0.040, +0.104] | +0.013 | +0.197 |
| perfect classifier + table, mean | +0.041 [+0.021, +0.061] | +0.059 [+0.030, +0.089] | +0.013 | +0.260 |
| perfect classifier + table, q = 0.1 | +0.045 [+0.022, +0.070] | +0.071 [+0.038, +0.104] | +0.005 | +0.316 |
| perfect classifier, force only | **+0.062 [+0.043, +0.082]** | **+0.099 [+0.071, +0.127]** | +0.005 | +0.436 |
| DMS46, q = 0.1 | +0.038 [+0.015, +0.061] | +0.063 [+0.033, +0.092] | +0.000 | +0.264 |
| DMS46, mean | +0.030 [+0.014, +0.046] | +0.036 [+0.013, +0.058] | +0.021 | +0.122 |
| DMS46, force only | **+0.052 [+0.035, +0.072]** | **+0.081 [+0.056, +0.107]** | +0.008 | +0.335 |
| CLIP, q = 0.1 | +0.021 [−0.006, +0.047] | +0.084 [+0.051, +0.117] | **−0.078 [−0.122, −0.039]** | +0.231 |
| CLIP, mean | +0.029 [+0.012, +0.045] | +0.028 [+0.005, +0.051] | +0.031 | +0.117 |
| CLIP, force only | **+0.058 [+0.040, +0.078]** | **+0.092 [+0.068, +0.119]** | +0.005 | +0.387 |
| MobileNet, q = 0.1 | +0.000 [−0.026, +0.027] | +0.068 [+0.033, +0.102] | **−0.106 [−0.148, −0.065]** | +0.263 |
| MobileNet, mean | +0.051 [+0.030, +0.073] | +0.078 [+0.050, +0.104] | +0.010 | +0.240 |
| MobileNet, force only | **+0.066 [+0.045, +0.087]** | **+0.102 [+0.074, +0.132]** | +0.008 | +0.542 |

- Low-μ objects (n = 606, plate included): the heads at the quantile recover the oracle's gain.
  - baseline 0.391, oracle 0.462 (+0.071), DMS46 +0.063, CLIP +0.084, MobileNet +0.068 (all CIs exclude 0);
    at the mean +0.03 to +0.08.
- Per material:
  - metal 0.66 → 0.84–0.87 (oracle 0.87)
  - glass 0.46 → 0.48–0.57 (oracle 0.49)
  - plastic unchanged within noise
  - paper 0.62 → 0.34–0.62 (oracle 0.66). The pessimistic quantile of a wrong posterior makes the planner
    reject or over-squeeze the cardboard boxes, worst for MobileNet.
  - foam and rubber 1.00 throughout

**H2.**

- With real, mostly wrong classifiers, planning everything at the pessimistic quantile recovers the oracle's
  gain on slippery objects (+0.06 to +0.08 vs +0.07).
- CLIP and MobileNet give it back on the cardboard boxes (−0.08 and −0.11 on high-μ objects). --> Pooled,
  only DMS46 (+0.038) is significantly above the baseline.
- Using the estimate for the grip force only (§7.2) removes the cardboard loss: the three force-only arms are
  +0.052, +0.058 and +0.066 pooled, all significant, and match or beat the oracle (+0.048).
- The mechanism is robustness rather than recognition. A posterior spread over several materials has a low
  10% quantile --> the planner squeezes harder on everything that looks ambiguous, which is what slippery
  objects needed.
- It is only partly a "pessimistic constant" in disguise. A constant μ = 0.2 gives +0.011 success (§3.5,
  n.s.); the force-only heads give +0.052 to +0.066. --> The heads' object-to-object ordering of μ carries
  information even when the top-1 label is wrong.

**H3.**

- Quantile minus mean, same head, paired: DMS46 +0.008 [−0.013, +0.029], CLIP −0.008 [−0.034, +0.018],
  MobileNet **−0.051 [−0.076, −0.029]**; for the perfect classifier +0.004 [−0.014, +0.023].
- H3 is not supported. At 120 trials per object the quantile is neutral for DMS46, CLIP and the perfect
  classifier and significantly worse than the mean for MobileNet.
- CLIP's and MobileNet's posteriors on the cardboard boxes are spread over paper, plastic and glass --> their
  10% quantiles are low there. The planner rejects or over-squeezes the boxes (35% and 42% fallbacks vs 22%
  for the baseline; paper 0.62 → 0.42 and 0.34).
- For CLIP a larger gain on the slippery objects (+0.084 against +0.028 at the mean) offsets that loss. For
  MobileNet it does not.
- The quantile helps only where the object is actually slippery. Where the posterior is diffuse on a
  high-friction object it costs.

## 5. Conclusions

1. **Friction knowledge helps on slippery objects only, and through grip force.**
   - With the true μ, lift success rises by 5 points overall and 7 points on glass/metal/plastic objects
     (21 points on metal), and wrench at slip by 0.2–0.3N.
   - On paper, foam and rubber nothing changes.
   - All of this gain is reproduced by giving the baseline's grasp the oracle's force (+0.070 pooled); none of
     it by giving the oracle's grasp the baseline's force (−0.005).
2. **Material-aware grasp selection, the proposal's contribution, adds nothing at the default contact model.**
   - Knowing μ changes which candidate is chosen in 26–50% of trials. The new choice is no better.
   - Selection-only is −0.005 pooled and −0.013 on low-μ objects in rank mode (n.s.) and −0.022 in filter
     mode, where it is just significantly worse than the baseline.
   - §7.3 shows where selection could matter. With the planner's torsional term scaled to the flat-face
     calibration (3.2×) the oracle's gain more than doubles on identical trials (+0.047 → +0.112) and
     selection-only turns positive on low-μ objects (+0.045 [+0.023, +0.066]) though not pooled (+0.012, n.s.).
     Force still carries the gain (squeeze-only +0.114).
   - The ε ranking at low μ is decided by the torsional term, which the default model under-estimates
     threefold on flat faces.
3. **A perfect classifier with a lookup table recovers nearly the whole oracle gain. Real classifiers recover
   it on slippery objects despite being wrong on most objects** (H2), provided the estimate is used for the
   grip force only.
   - Force-only arms with DMS46, CLIP and MobileNet at the 10% quantile give +0.052 to +0.066 pooled and
     +0.08 to +0.10 on slippery objects, all significant. No loss on cardboard, and +0.34 to +0.54N of wrench
     at slip.
   - CLIP and MobileNet used for grasp selection as well lose 8–11 points on the high-μ objects.
   - The mechanism is robustness rather than recognition: an ambiguous posterior has a low quantile, and a low
     planning μ means more force, which is what slippery objects needed.
3b. **Quantile vs mean (H3) is not supported:** neutral for DMS46, CLIP and the perfect classifier, −0.05 for
   MobileNet at n = 992.
   - Pessimism pays only where the object is slippery. A diffuse posterior on a high-friction object turns it
     into a cost.
4. **A single pessimistic constant is nearly as good for robustness.**
   - Assuming μ = 0.1–0.2 everywhere exceeds the oracle's wrench at slip, and μ = 0.4 gives half of the
     oracle's success gain (+0.021 against +0.047).
   - The remaining value of per-object friction knowledge is in NOT over-squeezing fragile objects while
     still holding slippery ones, which a constant cannot do.
5. **ε predicts measured robustness well for compact objects (ρ ≈ 0.66–0.98), moderately for the boxes
   (0.5–0.6) and poorly for the lid's rim and the bleach bottle (0.05–0.35).**

Implications for the project's framing:

- The honest title of the result: "vision-estimated friction is worth having for setting grip force before
  contact, even from a weak classifier if it is used pessimistically. It is not worth having for choosing
  among antipodal grasp candidates with the ε metric at the default contact model. With a wrong posterior,
  letting it choose the grasp costs what the force gains".
- The pre-contact, vision-only estimate remains the differentiator from tactile methods. Its consumer should
  be the force controller, not the grasp ranker.
- The inference-budget question is moot for now. The 1.5M-parameter head (8ms on the GB10) is as useful as the
  47M and 151M ones when used for force. None of them is accurate on this domain and the value comes from the
  uncertainty handling.

## 6. Limitations

- Floating gripper, no arm: motion planning and reachability are replaced by a collision check over 11
  approach angles. 17% of trials were skipped as ungraspable in the settled pose.
- The soft-finger torsional coefficient γ = (2/3)aμ is one modelling choice. PyBullet's torsional friction
  plus finite-pad corner effects give 1–3× that capacity --> the model is conservative in a geometry-dependent
  way (§7.3 quantifies what a 2–3.2× scale does to the 2×2).
- The material → μ table is assumed, not measured; the true μ* is drawn around it. --> Results are about the
  value of knowing μ, not about the table's accuracy.
- Ten objects, one gripper geometry, one per-object force cap rule (4× the ideal force at the material's
  lowest friction, within [8, 40]N). The cap rule sets the regime in which force matters. A looser cap would
  saturate success and shift all the value to wrench at slip.
- 120 trials per object with paired bootstrap CIs. Per-material numbers rest on 93–204 trials and are
  indicative. Between 40-trial blocks the gains vary with a standard deviation of 0.003–0.04 (§7.1), the size
  of the differences a 40-trial run showed from one invocation to the next.
- Reproducibility:
  - The simulator is restored to a saved pristine state before every trial. Since 1-Oct-2026 the trial seed
    is a fixed function of the object and the trial index. --> Every run draws the same true μ, pose and
    candidates for a given trial and the planner makes the same choices.
  - Across the 13 888 rows that `core120` and `heads120` share (seven cells, two modes), the chosen grasp and
    the commanded force are identical in every row.
  - The executed outcome of the same grasp is not bit-identical between the two runs. Wrench at slip, slip or
    pivot differ in about half of the trials, and lift success flips in 109 rows (0.8%).
  - The two runs execute a trial's cells in different orders. --> PyBullet's restored state evidently does not
    fix everything a grasp execution depends on.
  - The effect on a cell's mean is well under one point. It is why the shared cells read +0.047 / +0.048
    (oracle) and +0.070 / +0.070 (squeeze-only) in the two runs.
  - Two invocations of the same command do reproduce each other exactly. A 20-trial lean run of four objects
    with 20 workers, run twice, agreed on every one of its 1003 rows in choice, force, lift success, slip,
    pivot and the wrench probe. --> The differences above come from the cell order, not from the simulator.
  - Across machines the trials are the same up to floating point (§8). The 15-Oct and 1-Oct `core120` agree
    on the chosen grasp in 97.5% and on lift success in 98.1% of their shared executed rows.
- The material heads were evaluated on turntable product photographs, not on the fixed-camera tabletop images
  a deployment would see. Their accuracy here is a lower bound in some respects (clean masks) and an upper
  bound in others (uniform lighting).

## 7. Follow-up experiments (first run 23-Sep-2026, numbers from the 15-Oct-2026 re-run; §7.3 from the 120-trial torsion runs of 6-Nov-2026)

### 7.1 Run-to-run spread

- `results/sim/core120/blocks_rank.md` and `results/sim/heads120/blocks_rank.md` split each 120-trial run into
  three blocks of 40 trials per object, the size of one original run. They report every arm's gain per block
  next to the pooled gain.
- Pooled over all objects the per-block standard deviation is 0.013 (selection-only) to 0.024 (force-only
  table arm); on low-μ objects 0.003–0.036.
- Squeeze-only, for example, is +0.091 / +0.045 / +0.072 in the three blocks against +0.070 [+0.051, +0.089]
  pooled.
- --> A single 40-trial run resolves gains to about ±0.03. That is why the pooled oracle gain was significant
  in one 40-trial run and not in another (each drew its own trials, see the note at the top). At 120 trials
  it is +0.047 [+0.024, +0.071].
- Two 120-trial runs on different trials still differ by about as much as their CIs suggest.
  - 23-Sep run: +0.032 [+0.009, +0.055] for the oracle and −0.028 [−0.046, −0.010] for selection-only.
  - 1-Oct run: +0.050 and −0.006.
  - This run, on the same trials as 1-Oct up to floating point (§8): +0.047 and −0.005.

### 7.2 Using the estimate for grip force only

- Every classifier arm in §4 used the predicted μ for both the grasp choice and the grip force.
- The new `table_squeeze` and `head:<h>:squeeze` cells keep the baseline's grasp (chosen at μ = 0.5) and set
  only the force from the 10% quantile of the predicted p(μ).
- Rank mode, `heads120`:

| force from | full arm (grasp + force) | force only | force only, low-μ | force only, high-μ | Δ wrench, force only [N] |
|---|---|---|---|---|---|
| perfect classifier, q = 0.1 | +0.045 | **+0.062 [+0.043, +0.082]** | +0.099 | +0.005 | +0.436 |
| DMS46, q = 0.1 | +0.038 | **+0.052 [+0.035, +0.072]** | +0.081 | +0.008 | +0.335 |
| CLIP, q = 0.1 | +0.021 | **+0.058 [+0.040, +0.078]** | +0.092 | +0.005 | +0.387 |
| MobileNet, q = 0.1 | +0.000 | **+0.066 [+0.045, +0.087]** | +0.102 | +0.008 | +0.542 |
| oracle (true μ*), for comparison | +0.048 | squeeze-only +0.070 | +0.106 | +0.013 | +0.272 |

- The force-only arms are the best real-classifier arms in the study: all three beat the baseline
  significantly, none loses on the cardboard boxes, and they match or exceed the oracle's full arm pooled.
- What the full arms lose (−0.08 and −0.11 on high-μ objects for CLIP and MobileNet) is entirely the grasp
  choice. The same posteriors used for force alone change nothing there (+0.005 to +0.008).
- MobileNet, the weakest classifier, gives the largest wrench-at-slip gain (+0.54N): its diffuse posteriors
  command the most force.
- Per-block spread of these cells is 0.023–0.028 pooled.
- Design rule: feed the material estimate to the force controller and leave grasp ranking at a constant μ.

### 7.3 Does a calibrated torsional term make selection useful?

- We scaled the planner's torsional coefficient by 2.0 and by 3.2 and left the physics unchanged.
  - The larger scale is the flat-face calibration: measured torsion at slip 0.14/0.27/0.40N·m at
    μ = 0.2/0.4/0.6 against the model's 0.043/0.085/0.128N·m.
- 120 trials per object, the same trials in all three runs (`results/sim/torsion_comparison.md`; scale 1.0 is
  `core120`). Run 6-Nov-2026; the 40-trial runs of 15-Oct-2026 are the first 40 trials of these, row for row.
- Rank mode, n = 992:

| planner torsional scale | oracle | squeeze only | selection only | oracle, low-μ | selection only, low-μ | oracle Δ wrench [N] |
|---|---|---|---|---|---|---|
| 1.0 (model) | +0.047 [+0.024, +0.071] | +0.070 | −0.005 [−0.022, +0.013] | +0.071 | −0.013 [−0.036, +0.008] | +0.19 |
| 2.0 | +0.062 [+0.039, +0.088] | +0.087 | −0.014 [−0.028, +0.001] | +0.111 | −0.010 [−0.031, +0.012] | +0.22 |
| 3.2 (flat-face fit) | **+0.112 [+0.088, +0.139]** | +0.114 | +0.012 [−0.004, +0.030] | **+0.203** | **+0.045 [+0.023, +0.066]** | +0.34 |

- Doubling the torsional term is a small step: the oracle's gain rises from +0.047 to +0.062 and selection-only
  stays at zero.
- At the flat-face calibration (3.2×) the oracle's advantage over the constant-μ baseline more than doubles
  (+0.047 → +0.112 pooled, +0.071 → +0.203 on low-μ objects, +0.19 → +0.34N of wrench).
- The grasp choice contributes on low-μ objects: selection-only +0.045 [+0.023, +0.066] in rank mode
  (squeeze-only +0.183 and the oracle +0.203 there). Pooled it is +0.012 [−0.004, +0.030], within noise, and on
  high-μ objects it costs −0.039 [−0.065, −0.013].
- Filter mode shows the same step in the oracle (+0.042 / +0.054 / +0.086) and nothing in selection-only
  (−0.022 / −0.023 / −0.002 pooled; +0.008 [−0.013, +0.030] on low-μ objects at 3.2×).
- Squeeze-only (+0.114) still matches the oracle (+0.112). --> The torsional term does matter: once the model
  stops under-rating torsion-heavy grasps, knowing μ is worth more than twice as much, nearly all of it through
  the force, with a modest part from the grasp choice on slippery objects.
- The 40-trial block of 15-Oct-2026 had read selection-only at +0.037 [+0.003, +0.070] pooled and +0.079 on
  low-μ objects, with the oracle above squeeze-only; at 120 trials both effects shrink to the numbers above.
  --> The block spread of §7.1 (SD up to 0.04 on low-μ gains) explains the difference; the 120-trial numbers
  are the result.

## 8. Timing on an idle machine and what the 15-Oct-2026 re-run changed

- Date: 15-Oct-2026. Every stage of the project re-run by `scripts/run_chain.sh`, one stage at a time, with
  nothing else on the machine.
- Machine: a 20-core aarch64 NVIDIA GB10 box (10 Cortex-X925 + 10 Cortex-A725 cores, 121GB unified memory,
  torch 2.14.1+cu130).
- Logs: `results/timing_idle/` has the stage log (`chain.log`, `stages.csv`), each stage's output and a
  once-a-minute load and GPU sample (`load.csv`).
- Load: during the simulation runs the 1-minute load averaged 18.7 (20 workers), i.e. no other consumer.
- 1-Oct-2026 figures: the same chain on the previous machine, a 4-vCPU Google Cloud VM (two physical cores of
  a 2.2GHz Xeon) with an NVIDIA L4, torch 2.14.0+cu126 and four workers (`results/timing_idle_l4/`).

| stage | 1-Oct (L4 VM, 4 workers) | 15-Oct (GB10, 20 workers) |
|---|---|---|
| MobileNet fine-tune, 8 epochs on 6000 images | 136 s, 16–18 s per epoch | **39 s**, 5 s per epoch (41 s for the stage) |
| head latency, DMS46 / CLIP / MobileNet (ms per image, bs 1) | 74 ± 25 / 13 ± 1 / 13 ± 2 | **21 ± 6 / 11 ± 1 / 8 ± 1** |
| head evaluation on 240 views (incl. model load and latency), DMS46 / CLIP / MobileNet | 40 / 31 / 24 s | **14 / 12 / 10 s** |
| scorer-only headroom, 10 × 30 × 40 | 217 s | **33 s** |
| `core120` | 2 h 01 min (7289 s) | **5.7 min** (342 s) |
| `heads120` | 1 h 52 min (6726 s) | **5.5 min** (330 s) |
| `torsion_k2.0` / `torsion_k3.2`, 40 trials | 19.6 / 19.2 min | **68 / 68 s** |

- Per-trial wall time (`wall_s`, cell planning and execution only):
  - `core120`: mean 5.7s, median 3.6s (27 / 17s on the VM).
  - `heads120`: 5.4 / 3.5s (25 / 15s).
  - 40-trial lean runs: 2.6 / 1.7s and 2.4 / 1.9s (12 / 8s).
- 6-Nov-2026: the two torsion runs were re-run at 120 trials per object outside the chain
  (`run_study.py lean --trials 120`), 180 / 184s for scale 3.2 / 2.0 with 20 workers; `run_chain.sh` now runs
  them at 120 trials. Their first 40 trials reproduce the 15-Oct rows bit for bit (`fig_torsion.png`, cut to
  those trials, is unchanged).
- One worker here gets through a trial about five times faster than one of the VM's hyperthreads, and five
  times as many workers run at once.
- The three latency passes per head agree within 0.5ms (DMS46 21.2 / 21.2 / 21.2, CLIP 11.4 / 10.9 / 11.0,
  MobileNet 8.2 / 8.8 / 8.4ms).

Two things in the code were wrong for this machine. Both were fixed before the chain above. A first pass of
the chain with the original code had read 972 / 956s for `core120` / `heads120` and 120–150 ± 100ms for DMS46.

- BLAS threads: with one simulation worker per core, every worker also opened a 20-thread OpenBLAS pool.
  - Load average 50–78; cost about a quarter of the wall time (A/B on a 20-trial lean run of four objects with
    20 workers: 42s against 31s with one thread per worker, identical rows and outcomes).
  - `scripts/run_study.py` and `scripts/headroom_ycb.py` now pin the BLAS pool to one thread.
- DMS46 copy: the head copied its 46 × H × W per-pixel posterior (11–44MB) to the host and averaged it there.
  - On this unified-memory GPU that copy took 0.2–380ms per image (mean 96ms, s.d. 108ms) against a 7–25ms
    forward. The L4 had done the same copy in a few ms inside its 74ms.
  - The average is now taken on the device and only the 46 class means are copied. The posteriors are
    unchanged (maximum difference 1e-16 against the old path); the latency is 21 ± 6ms (min 10).
  - Torch's CPU thread count (20 here by default) made no difference to it (20 / 10 / 4 / 1 threads were
    tried).

What moved in the results between the 1-Oct (L4 VM, x86-64) and 15-Oct (GB10, aarch64) runs:

- The two machines draw the same true μ in every trial (the seed is a function of the object and the trial
  index).
- The candidate sampler and PyBullet are not bit-identical in floating point across the two architectures.
  embreex has no aarch64 wheel --> trimesh's own ray–triangle intersector casts the sampler's rays here.
- Against the 1-Oct `core120`: 98.4% of the shared executed rows carry the same candidate, 97.5% the same
  chosen grasp, 98.3% the same force and 98.1% the same lift success.
- One mustard-bottle trial moved from skipped to usable (992 usable trials, 208 skipped).
- Every gain moved within its confidence interval and no conclusion changes:
  - 2×2 (rank): oracle +0.047 (was +0.050), squeeze-only +0.070 (was +0.062), selection-only −0.005 (was
    −0.006); on low-μ objects +0.071 / +0.106 / −0.013 (were +0.083 / +0.098 / −0.008). In filter mode
    selection-only is now −0.022 [−0.041, −0.004], just significant where it was −0.016 (n.s.).
  - Table arms: unchanged to within 0.002 (q = 0.10 +0.044, mean +0.043, force only +0.066).
  - Sweep: the best constant is still 0.4 (+0.021, was +0.024); 0.3 now matches the oracle on wrench at slip.
  - MobileNet was retrained (GPU training is not bit-reproducible): MINC test accuracy 71.4% (was 71.2%), ECE
    0.071 → 0.029 (was 0.079 → 0.027), T = 1.40. On the YCB photographs it now predicts plastic for the plate
    where the 1-Oct checkpoint predicted ceramic --> its object-level top-1 is 2/9 (was 3/9). DMS46 and CLIP
    were re-evaluated on this GPU and give the same per-object votes and accuracies.
  - Heads (rank): force-only arms +0.052 / +0.058 / +0.066 (were +0.051 / +0.060 / +0.072); at the quantile
    +0.038 / +0.021 / +0.000 (were +0.036 / +0.020 / +0.007).
  - Heads, H3 (quantile minus mean): +0.008 / −0.008 / −0.051 (were +0.010 / −0.002 / −0.042), MobileNet's
    still the only significant one.
  - Torsion (identical first-40 trials): at 3.2× the oracle gain is +0.137 (was +0.131) and selection-only is
    now +0.037 [+0.003, +0.070] pooled, significant where it was +0.027 (n.s.); on low-μ objects +0.079 (was
    +0.069).
  - Headroom table: identical to the 1-Oct one at the printed precision.
  - What the 1-Oct run had changed against the 23-Sep numbers is in this file's git history.
