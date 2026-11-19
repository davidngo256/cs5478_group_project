# Simulation study: torsion_k2.0


## Coverage

992 usable trials, 208 skipped (too few feasible grasps), 0 errors.

| object | material | usable trials | skipped | mean feasible cands | mean FC at mu* |
|---|---|---|---|---|---|
| 028_skillet_lid | glass | 120 | 0 | 40 | 13 |
| 038_padlock | metal | 120 | 0 | 40 | 25 |
| 010_potted_meat_can | metal | 84 | 36 | 40 | 23 |
| 029_plate | ceramic | 93 | 27 | 40 | 13 |
| 006_mustard_bottle | plastic | 112 | 8 | 28 | 15 |
| 021_bleach_cleanser | plastic | 77 | 43 | 38 | 22 |
| 003_cracker_box | paper | 76 | 44 | 40 | 38 |
| 004_sugar_box | paper | 70 | 50 | 40 | 33 |
| 061_foam_brick | foam | 120 | 0 | 40 | 39 |
| 057_racquetball | rubber | 120 | 0 | 40 | 39 |


## 2x2 on lift success under the force cap, rank mode

| grasp chosen with \ force set with | mu = 0.5 | mu* |
|---|---|---|
| mu = 0.5 | 0.537 (baseline) | 0.624 (squeeze only) |
| mu* | 0.523 (selection only) | 0.600 (oracle) |

selection-only gain -0.014 [-0.028, +0.001]; squeeze-only gain +0.087 [+0.067, +0.110]; oracle gain +0.062 [+0.039, +0.088] (n = 992 paired trials)

**low-mu objects (glass, metal, ceramic, plastic)**

| grasp chosen with \ force set with | mu = 0.5 | mu* |
|---|---|---|
| mu = 0.5 | 0.322 (baseline) | 0.460 (squeeze only) |
| mu* | 0.312 (selection only) | 0.432 (oracle) |

selection-only gain -0.010 [-0.031, +0.012]; squeeze-only gain +0.139 [+0.109, +0.172]; oracle gain +0.111 [+0.076, +0.144] (n = 606 paired trials)

**high-mu objects (paper, foam, rubber)**

| grasp chosen with \ force set with | mu = 0.5 | mu* |
|---|---|---|
| mu = 0.5 | 0.876 (baseline) | 0.881 (squeeze only) |
| mu* | 0.855 (selection only) | 0.863 (oracle) |

selection-only gain -0.021 [-0.041, -0.003]; squeeze-only gain +0.005 [-0.018, +0.028]; oracle gain -0.013 [-0.044, +0.016] (n = 386 paired trials)


## 2x2 on lift success under the force cap, filter mode

| grasp chosen with \ force set with | mu = 0.5 | mu* |
|---|---|---|
| mu = 0.5 | 0.558 (baseline) | 0.637 (squeeze only) |
| mu* | 0.535 (selection only) | 0.613 (oracle) |

selection-only gain -0.023 [-0.039, -0.008]; squeeze-only gain +0.079 [+0.057, +0.103]; oracle gain +0.054 [+0.031, +0.080] (n = 992 paired trials)

**low-mu objects (glass, metal, ceramic, plastic)**

| grasp chosen with \ force set with | mu = 0.5 | mu* |
|---|---|---|
| mu = 0.5 | 0.340 (baseline) | 0.482 (squeeze only) |
| mu* | 0.325 (selection only) | 0.455 (oracle) |

selection-only gain -0.015 [-0.036, +0.007]; squeeze-only gain +0.142 [+0.111, +0.175]; oracle gain +0.116 [+0.084, +0.149] (n = 606 paired trials)

**high-mu objects (paper, foam, rubber)**

| grasp chosen with \ force set with | mu = 0.5 | mu* |
|---|---|---|
| mu = 0.5 | 0.902 (baseline) | 0.881 (squeeze only) |
| mu* | 0.865 (selection only) | 0.860 (oracle) |

selection-only gain -0.036 [-0.062, -0.013]; squeeze-only gain -0.021 [-0.049, +0.005]; oracle gain -0.041 [-0.075, -0.008] (n = 386 paired trials)


## 2x2 on wrench at slip [N], 0 if the grasp failed, rank mode

| grasp chosen with \ force set with | mu = 0.5 | mu* |
|---|---|---|
| mu = 0.5 | 1.137 (baseline) | 1.411 (squeeze only) |
| mu* | 1.108 (selection only) | 1.353 (oracle) |

selection-only gain -0.028 [-0.075, +0.020]; squeeze-only gain +0.275 [+0.215, +0.341]; oracle gain +0.216 [+0.146, +0.293] (n = 992 paired trials)

**low-mu objects (glass, metal, ceramic, plastic)**

| grasp chosen with \ force set with | mu = 0.5 | mu* |
|---|---|---|
| mu = 0.5 | 0.842 (baseline) | 1.291 (squeeze only) |
| mu* | 0.822 (selection only) | 1.209 (oracle) |

selection-only gain -0.020 [-0.088, +0.043]; squeeze-only gain +0.449 [+0.366, +0.539]; oracle gain +0.366 [+0.264, +0.470] (n = 606 paired trials)

**high-mu objects (paper, foam, rubber)**

| grasp chosen with \ force set with | mu = 0.5 | mu* |
|---|---|---|
| mu = 0.5 | 1.599 (baseline) | 1.600 (squeeze only) |
| mu* | 1.558 (selection only) | 1.579 (oracle) |

selection-only gain -0.041 [-0.112, +0.023]; squeeze-only gain +0.001 [-0.071, +0.070]; oracle gain -0.020 [-0.114, +0.073] (n = 386 paired trials)


## 2x2 on wrench at slip [N], 0 if the grasp failed, filter mode

| grasp chosen with \ force set with | mu = 0.5 | mu* |
|---|---|---|
| mu = 0.5 | 1.197 (baseline) | 1.536 (squeeze only) |
| mu* | 1.132 (selection only) | 1.406 (oracle) |

selection-only gain -0.065 [-0.115, -0.019]; squeeze-only gain +0.339 [+0.270, +0.414]; oracle gain +0.209 [+0.137, +0.289] (n = 992 paired trials)

**low-mu objects (glass, metal, ceramic, plastic)**

| grasp chosen with \ force set with | mu = 0.5 | mu* |
|---|---|---|
| mu = 0.5 | 0.905 (baseline) | 1.508 (squeeze only) |
| mu* | 0.858 (selection only) | 1.321 (oracle) |

selection-only gain -0.046 [-0.114, +0.024]; squeeze-only gain +0.603 [+0.504, +0.710]; oracle gain +0.416 [+0.318, +0.520] (n = 606 paired trials)

**high-mu objects (paper, foam, rubber)**

| grasp chosen with \ force set with | mu = 0.5 | mu* |
|---|---|---|
| mu = 0.5 | 1.655 (baseline) | 1.580 (squeeze only) |
| mu* | 1.561 (selection only) | 1.539 (oracle) |

selection-only gain -0.094 [-0.165, -0.028]; squeeze-only gain -0.075 [-0.162, +0.003]; oracle gain -0.116 [-0.221, -0.024] (n = 386 paired trials)


## Arms vs baseline: success, rank mode

| cell | n | mean success | Δ vs baseline | 95% CI |
|---|---|---|---|---|
| baseline | 992 | 0.537 | +0.000 | [+0.000, +0.000] |
| squeeze | 992 | 0.624 | +0.087 | [+0.067, +0.110] |
| oracle | 992 | 0.600 | +0.062 | [+0.039, +0.088] |
| table_q | 992 | 0.619 | +0.082 | [+0.058, +0.106] |
| table_mean | 992 | 0.609 | +0.072 | [+0.051, +0.093] |
| table_squeeze | 992 | 0.633 | +0.096 | [+0.076, +0.118] |

Per material (mean over trials):

| material (bin) | baseline | squeeze | oracle | table_q | table_mean | table_squeeze |
|---|---|---|---|---|---|---|
| glass (very low) | 0.35 | 0.52 | 0.51 | 0.47 | 0.50 | 0.52 |
| ceramic (low) | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| metal (low) | 0.52 | 0.80 | 0.76 | 0.85 | 0.76 | 0.83 |
| plastic (mid) | 0.24 | 0.29 | 0.24 | 0.24 | 0.23 | 0.29 |
| paper (mid-high) | 0.67 | 0.68 | 0.64 | 0.66 | 0.72 | 0.71 |
| foam (high) | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| rubber (high) | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |


## Arms vs baseline: success, filter mode

| cell | n | mean success | Δ vs baseline | 95% CI |
|---|---|---|---|---|
| baseline | 992 | 0.558 | +0.000 | [+0.000, +0.000] |
| squeeze | 992 | 0.637 | +0.079 | [+0.057, +0.103] |
| oracle | 992 | 0.613 | +0.054 | [+0.031, +0.080] |
| table_q | 992 | 0.618 | +0.059 | [+0.034, +0.086] |
| table_mean | 992 | 0.614 | +0.055 | [+0.033, +0.080] |
| table_squeeze | 992 | 0.638 | +0.080 | [+0.058, +0.103] |

Per material (mean over trials):

| material (bin) | baseline | squeeze | oracle | table_q | table_mean | table_squeeze |
|---|---|---|---|---|---|---|
| glass (very low) | 0.38 | 0.52 | 0.48 | 0.48 | 0.51 | 0.53 |
| ceramic (low) | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| metal (low) | 0.60 | 0.86 | 0.83 | 0.83 | 0.77 | 0.85 |
| plastic (mid) | 0.21 | 0.29 | 0.25 | 0.23 | 0.25 | 0.29 |
| paper (mid-high) | 0.74 | 0.68 | 0.63 | 0.69 | 0.71 | 0.70 |
| foam (high) | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| rubber (high) | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |


## Arms vs baseline: wrench at slip [N], rank mode

| cell | n | mean wrench at slip [N] | Δ vs baseline | 95% CI |
|---|---|---|---|---|
| baseline | 992 | 1.137 | +0.000 | [+0.000, +0.000] |
| squeeze | 992 | 1.411 | +0.275 | [+0.215, +0.341] |
| oracle | 992 | 1.353 | +0.216 | [+0.146, +0.293] |
| table_q | 992 | 1.565 | +0.429 | [+0.348, +0.507] |
| table_mean | 992 | 1.419 | +0.283 | [+0.223, +0.345] |
| table_squeeze | 992 | 1.595 | +0.458 | [+0.390, +0.532] |

Per material (mean over trials):

| material (bin) | baseline | squeeze | oracle | table_q | table_mean | table_squeeze |
|---|---|---|---|---|---|---|
| glass (very low) | 1.02 | 1.63 | 1.64 | 1.63 | 1.70 | 1.69 |
| ceramic (low) | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| metal (low) | 1.16 | 2.02 | 1.91 | 2.74 | 2.05 | 2.63 |
| plastic (mid) | 0.80 | 0.93 | 0.77 | 0.84 | 0.79 | 1.04 |
| paper (mid-high) | 1.85 | 1.86 | 1.81 | 2.01 | 1.99 | 2.06 |
| foam (high) | 1.28 | 1.28 | 1.27 | 1.27 | 1.27 | 1.28 |
| rubber (high) | 1.61 | 1.61 | 1.61 | 1.61 | 1.61 | 1.61 |


## Arms vs baseline: wrench at slip [N], filter mode

| cell | n | mean wrench at slip [N] | Δ vs baseline | 95% CI |
|---|---|---|---|---|
| baseline | 992 | 1.197 | +0.000 | [+0.000, +0.000] |
| squeeze | 992 | 1.536 | +0.339 | [+0.270, +0.414] |
| oracle | 992 | 1.406 | +0.209 | [+0.137, +0.289] |
| table_q | 992 | 1.588 | +0.391 | [+0.303, +0.485] |
| table_mean | 992 | 1.461 | +0.264 | [+0.193, +0.341] |
| table_squeeze | 992 | 1.779 | +0.582 | [+0.493, +0.677] |

Per material (mean over trials):

| material (bin) | baseline | squeeze | oracle | table_q | table_mean | table_squeeze |
|---|---|---|---|---|---|---|
| glass (very low) | 1.08 | 1.65 | 1.57 | 1.63 | 1.72 | 1.75 |
| ceramic (low) | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| metal (low) | 1.41 | 2.62 | 2.25 | 2.87 | 2.20 | 3.49 |
| plastic (mid) | 0.70 | 0.96 | 0.81 | 0.82 | 0.91 | 1.09 |
| paper (mid-high) | 2.06 | 1.87 | 1.76 | 2.07 | 1.95 | 2.05 |
| foam (high) | 1.22 | 1.22 | 1.22 | 1.22 | 1.22 | 1.22 |
| rubber (high) | 1.59 | 1.59 | 1.59 | 1.59 | 1.59 | 1.59 |


## Arms vs baseline: commanded grip force [N], rank mode

| cell | n | mean commanded grip force [N] | Δ vs baseline | 95% CI |
|---|---|---|---|---|
| baseline | 992 | 16.782 | +0.000 | [+0.000, +0.000] |
| squeeze | 992 | 20.465 | +3.683 | [+3.254, +4.120] |
| oracle | 992 | 17.193 | +0.411 | [-0.324, +1.179] |
| table_q | 992 | 18.528 | +1.746 | [+0.958, +2.585] |
| table_mean | 992 | 19.011 | +2.230 | [+1.797, +2.692] |
| table_squeeze | 992 | 22.308 | +5.526 | [+5.111, +5.993] |

Per material (mean over trials):

| material (bin) | baseline | squeeze | oracle | table_q | table_mean | table_squeeze |
|---|---|---|---|---|---|---|
| glass (very low) | 28.92 | 37.56 | 27.63 | 34.33 | 35.24 | 39.65 |
| ceramic (low) | 27.37 | 27.37 | 14.42 | 1.77 | 22.07 | 27.37 |
| metal (low) | 8.74 | 17.05 | 16.78 | 20.77 | 15.99 | 20.23 |
| plastic (mid) | 30.32 | 34.64 | 30.50 | 34.70 | 33.03 | 38.07 |
| paper (mid-high) | 16.43 | 17.14 | 17.06 | 17.68 | 16.12 | 19.07 |
| foam (high) | 3.00 | 3.00 | 3.00 | 3.00 | 3.00 | 3.00 |
| rubber (high) | 3.00 | 3.00 | 3.00 | 3.00 | 3.00 | 3.00 |


## Arms vs baseline: commanded grip force [N], filter mode

| cell | n | mean commanded grip force [N] | Δ vs baseline | 95% CI |
|---|---|---|---|---|
| baseline | 992 | 16.998 | +0.000 | [+0.000, +0.000] |
| squeeze | 992 | 21.396 | +4.398 | [+3.906, +4.916] |
| oracle | 992 | 17.422 | +0.424 | [-0.272, +1.167] |
| table_q | 992 | 18.996 | +1.998 | [+1.212, +2.848] |
| table_mean | 992 | 19.505 | +2.507 | [+2.058, +2.966] |
| table_squeeze | 992 | 24.010 | +7.013 | [+6.453, +7.606] |

Per material (mean over trials):

| material (bin) | baseline | squeeze | oracle | table_q | table_mean | table_squeeze |
|---|---|---|---|---|---|---|
| glass (very low) | 27.85 | 37.97 | 27.75 | 34.48 | 35.44 | 40.00 |
| ceramic (low) | 27.37 | 27.37 | 14.42 | 1.77 | 22.07 | 27.37 |
| metal (low) | 8.99 | 20.38 | 16.76 | 21.24 | 16.02 | 27.04 |
| plastic (mid) | 31.98 | 35.90 | 31.87 | 36.42 | 35.42 | 39.52 |
| paper (mid-high) | 16.27 | 16.84 | 16.77 | 17.85 | 16.17 | 18.96 |
| foam (high) | 3.00 | 3.00 | 3.00 | 3.00 | 3.00 | 3.00 |
| rubber (high) | 3.00 | 3.00 | 3.00 | 3.00 | 3.00 | 3.00 |


## How often does knowing mu change the grasp?

- rank: baseline and oracle choose the same grasp in 78% of 907 trials
- rank: baseline and table_q choose the same grasp in 70% of 893 trials
- rank: oracle and table_q choose the same grasp in 76% of 853 trials
- rank, low-mu: baseline and oracle choose the same grasp in 72% of 521 trials
- rank, high-mu: baseline and oracle choose the same grasp in 85% of 386 trials
- filter: baseline and oracle choose the same grasp in 68% of 907 trials
- filter: baseline and table_q choose the same grasp in 60% of 893 trials
- filter: oracle and table_q choose the same grasp in 69% of 853 trials
- filter, low-mu: baseline and oracle choose the same grasp in 53% of 521 trials
- filter, high-mu: baseline and oracle choose the same grasp in 88% of 386 trials


## Analytical epsilon vs measured wrench at slip

Spearman(eps(mu*) x 2F, wrench at slip) pooled = +0.17 over 3032 grasps; per object: 028_skillet_lid: +0.27 (n=319); 038_padlock: +0.38 (n=778); 010_potted_meat_can: +0.53 (n=511); 006_mustard_bottle: +0.71 (n=269); 021_bleach_cleanser: -0.03 (n=76); 003_cracker_box: +0.07 (n=404); 004_sugar_box: +0.48 (n=227); 061_foam_brick: +0.70 (n=216); 057_racquetball: +0.97 (n=232)


## Planner fallbacks and force capping

| cell | mode | executed | fallback (nothing holdable under cap) | force capped |
|---|---|---|---|---|
| baseline | filter | 992 | 19% | 19% |
| baseline | rank | 992 | 19% | 19% |
| oracle | filter | 907 | 25% | 25% |
| oracle | rank | 907 | 25% | 25% |
| table_q | filter | 893 | 26% | 26% |
| table_q | rank | 893 | 26% | 26% |
