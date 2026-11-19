# Simulation study: torsion_k3.2


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
| mu = 0.5 | 0.469 (baseline) | 0.583 (squeeze only) |
| mu* | 0.481 (selection only) | 0.581 (oracle) |

selection-only gain +0.012 [-0.004, +0.030]; squeeze-only gain +0.114 [+0.093, +0.137]; oracle gain +0.112 [+0.088, +0.139] (n = 992 paired trials)

**low-mu objects (glass, metal, ceramic, plastic)**

| grasp chosen with \ force set with | mu = 0.5 | mu* |
|---|---|---|
| mu = 0.5 | 0.218 (baseline) | 0.401 (squeeze only) |
| mu* | 0.262 (selection only) | 0.421 (oracle) |

selection-only gain +0.045 [+0.023, +0.066]; squeeze-only gain +0.183 [+0.150, +0.215]; oracle gain +0.203 [+0.167, +0.236] (n = 606 paired trials)

**high-mu objects (paper, foam, rubber)**

| grasp chosen with \ force set with | mu = 0.5 | mu* |
|---|---|---|
| mu = 0.5 | 0.863 (baseline) | 0.868 (squeeze only) |
| mu* | 0.824 (selection only) | 0.832 (oracle) |

selection-only gain -0.039 [-0.065, -0.013]; squeeze-only gain +0.005 [-0.018, +0.028]; oracle gain -0.031 [-0.065, +0.003] (n = 386 paired trials)


## 2x2 on lift success under the force cap, filter mode

| grasp chosen with \ force set with | mu = 0.5 | mu* |
|---|---|---|
| mu = 0.5 | 0.516 (baseline) | 0.612 (squeeze only) |
| mu* | 0.514 (selection only) | 0.602 (oracle) |

selection-only gain -0.002 [-0.019, +0.015]; squeeze-only gain +0.096 [+0.074, +0.119]; oracle gain +0.086 [+0.059, +0.111] (n = 992 paired trials)

**low-mu objects (glass, metal, ceramic, plastic)**

| grasp chosen with \ force set with | mu = 0.5 | mu* |
|---|---|---|
| mu = 0.5 | 0.295 (baseline) | 0.447 (squeeze only) |
| mu* | 0.304 (selection only) | 0.452 (oracle) |

selection-only gain +0.008 [-0.013, +0.030]; squeeze-only gain +0.152 [+0.119, +0.185]; oracle gain +0.157 [+0.122, +0.190] (n = 606 paired trials)

**high-mu objects (paper, foam, rubber)**

| grasp chosen with \ force set with | mu = 0.5 | mu* |
|---|---|---|
| mu = 0.5 | 0.863 (baseline) | 0.870 (squeeze only) |
| mu* | 0.845 (selection only) | 0.837 (oracle) |

selection-only gain -0.018 [-0.049, +0.013]; squeeze-only gain +0.008 [-0.018, +0.034]; oracle gain -0.026 [-0.060, +0.010] (n = 386 paired trials)


## 2x2 on wrench at slip [N], 0 if the grasp failed, rank mode

| grasp chosen with \ force set with | mu = 0.5 | mu* |
|---|---|---|
| mu = 0.5 | 0.916 (baseline) | 1.227 (squeeze only) |
| mu* | 0.978 (selection only) | 1.258 (oracle) |

selection-only gain +0.062 [+0.014, +0.118]; squeeze-only gain +0.310 [+0.253, +0.371]; oracle gain +0.342 [+0.272, +0.420] (n = 992 paired trials)

**low-mu objects (glass, metal, ceramic, plastic)**

| grasp chosen with \ force set with | mu = 0.5 | mu* |
|---|---|---|
| mu = 0.5 | 0.523 (baseline) | 1.030 (squeeze only) |
| mu* | 0.674 (selection only) | 1.122 (oracle) |

selection-only gain +0.151 [+0.088, +0.219]; squeeze-only gain +0.507 [+0.424, +0.588]; oracle gain +0.599 [+0.502, +0.696] (n = 606 paired trials)

**high-mu objects (paper, foam, rubber)**

| grasp chosen with \ force set with | mu = 0.5 | mu* |
|---|---|---|
| mu = 0.5 | 1.533 (baseline) | 1.536 (squeeze only) |
| mu* | 1.456 (selection only) | 1.471 (oracle) |

selection-only gain -0.078 [-0.154, +0.001]; squeeze-only gain +0.002 [-0.062, +0.065]; oracle gain -0.063 [-0.160, +0.032] (n = 386 paired trials)


## 2x2 on wrench at slip [N], 0 if the grasp failed, filter mode

| grasp chosen with \ force set with | mu = 0.5 | mu* |
|---|---|---|
| mu = 0.5 | 1.043 (baseline) | 1.417 (squeeze only) |
| mu* | 1.046 (selection only) | 1.338 (oracle) |

selection-only gain +0.003 [-0.049, +0.054]; squeeze-only gain +0.375 [+0.308, +0.445]; oracle gain +0.296 [+0.222, +0.370] (n = 992 paired trials)

**low-mu objects (glass, metal, ceramic, plastic)**

| grasp chosen with \ force set with | mu = 0.5 | mu* |
|---|---|---|
| mu = 0.5 | 0.743 (baseline) | 1.338 (squeeze only) |
| mu* | 0.769 (selection only) | 1.262 (oracle) |

selection-only gain +0.026 [-0.043, +0.094]; squeeze-only gain +0.595 [+0.496, +0.698]; oracle gain +0.519 [+0.419, +0.622] (n = 606 paired trials)

**high-mu objects (paper, foam, rubber)**

| grasp chosen with \ force set with | mu = 0.5 | mu* |
|---|---|---|
| mu = 0.5 | 1.512 (baseline) | 1.541 (squeeze only) |
| mu* | 1.480 (selection only) | 1.458 (oracle) |

selection-only gain -0.032 [-0.113, +0.051]; squeeze-only gain +0.029 [-0.036, +0.095]; oracle gain -0.055 [-0.151, +0.043] (n = 386 paired trials)


## Arms vs baseline: success, rank mode

| cell | n | mean success | Δ vs baseline | 95% CI |
|---|---|---|---|---|
| baseline | 992 | 0.469 | +0.000 | [+0.000, +0.000] |
| squeeze | 992 | 0.583 | +0.114 | [+0.093, +0.137] |
| oracle | 992 | 0.581 | +0.112 | [+0.088, +0.139] |
| table_q | 992 | 0.610 | +0.141 | [+0.117, +0.166] |
| table_mean | 992 | 0.586 | +0.117 | [+0.094, +0.140] |
| table_squeeze | 992 | 0.588 | +0.119 | [+0.097, +0.142] |

Per material (mean over trials):

| material (bin) | baseline | squeeze | oracle | table_q | table_mean | table_squeeze |
|---|---|---|---|---|---|---|
| glass (very low) | 0.18 | 0.38 | 0.51 | 0.45 | 0.48 | 0.38 |
| ceramic (low) | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| metal (low) | 0.40 | 0.78 | 0.74 | 0.82 | 0.73 | 0.82 |
| plastic (mid) | 0.15 | 0.20 | 0.23 | 0.27 | 0.23 | 0.21 |
| paper (mid-high) | 0.64 | 0.65 | 0.55 | 0.64 | 0.63 | 0.62 |
| foam (high) | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| rubber (high) | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |


## Arms vs baseline: success, filter mode

| cell | n | mean success | Δ vs baseline | 95% CI |
|---|---|---|---|---|
| baseline | 992 | 0.516 | +0.000 | [+0.000, +0.000] |
| squeeze | 992 | 0.612 | +0.096 | [+0.074, +0.119] |
| oracle | 992 | 0.602 | +0.086 | [+0.059, +0.111] |
| table_q | 992 | 0.615 | +0.099 | [+0.076, +0.122] |
| table_mean | 992 | 0.598 | +0.082 | [+0.059, +0.106] |
| table_squeeze | 992 | 0.614 | +0.098 | [+0.076, +0.121] |

Per material (mean over trials):

| material (bin) | baseline | squeeze | oracle | table_q | table_mean | table_squeeze |
|---|---|---|---|---|---|---|
| glass (very low) | 0.28 | 0.46 | 0.50 | 0.44 | 0.50 | 0.45 |
| ceramic (low) | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| metal (low) | 0.55 | 0.87 | 0.82 | 0.83 | 0.76 | 0.85 |
| plastic (mid) | 0.17 | 0.21 | 0.24 | 0.26 | 0.24 | 0.24 |
| paper (mid-high) | 0.64 | 0.66 | 0.57 | 0.68 | 0.63 | 0.66 |
| foam (high) | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| rubber (high) | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |


## Arms vs baseline: wrench at slip [N], rank mode

| cell | n | mean wrench at slip [N] | Δ vs baseline | 95% CI |
|---|---|---|---|---|
| baseline | 992 | 0.916 | +0.000 | [+0.000, +0.000] |
| squeeze | 992 | 1.227 | +0.310 | [+0.253, +0.371] |
| oracle | 992 | 1.258 | +0.342 | [+0.272, +0.420] |
| table_q | 992 | 1.465 | +0.548 | [+0.475, +0.625] |
| table_mean | 992 | 1.289 | +0.373 | [+0.308, +0.438] |
| table_squeeze | 992 | 1.372 | +0.456 | [+0.392, +0.522] |

Per material (mean over trials):

| material (bin) | baseline | squeeze | oracle | table_q | table_mean | table_squeeze |
|---|---|---|---|---|---|---|
| glass (very low) | 0.52 | 1.18 | 1.59 | 1.56 | 1.62 | 1.24 |
| ceramic (low) | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| metal (low) | 0.84 | 1.83 | 1.72 | 2.39 | 1.74 | 2.37 |
| plastic (mid) | 0.44 | 0.58 | 0.73 | 0.94 | 0.75 | 0.72 |
| paper (mid-high) | 1.71 | 1.71 | 1.54 | 1.76 | 1.67 | 1.71 |
| foam (high) | 1.25 | 1.25 | 1.25 | 1.26 | 1.25 | 1.25 |
| rubber (high) | 1.61 | 1.61 | 1.61 | 1.61 | 1.61 | 1.61 |


## Arms vs baseline: wrench at slip [N], filter mode

| cell | n | mean wrench at slip [N] | Δ vs baseline | 95% CI |
|---|---|---|---|---|
| baseline | 992 | 1.043 | +0.000 | [+0.000, +0.000] |
| squeeze | 992 | 1.417 | +0.375 | [+0.308, +0.445] |
| oracle | 992 | 1.338 | +0.296 | [+0.222, +0.370] |
| table_q | 992 | 1.540 | +0.497 | [+0.421, +0.575] |
| table_mean | 992 | 1.379 | +0.337 | [+0.270, +0.409] |
| table_squeeze | 992 | 1.648 | +0.605 | [+0.525, +0.696] |

Per material (mean over trials):

| material (bin) | baseline | squeeze | oracle | table_q | table_mean | table_squeeze |
|---|---|---|---|---|---|---|
| glass (very low) | 0.79 | 1.42 | 1.57 | 1.50 | 1.68 | 1.47 |
| ceramic (low) | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| metal (low) | 1.28 | 2.57 | 2.11 | 2.75 | 2.12 | 3.36 |
| plastic (mid) | 0.50 | 0.61 | 0.78 | 0.91 | 0.80 | 0.89 |
| paper (mid-high) | 1.69 | 1.76 | 1.54 | 1.88 | 1.67 | 1.82 |
| foam (high) | 1.22 | 1.22 | 1.22 | 1.22 | 1.22 | 1.22 |
| rubber (high) | 1.59 | 1.59 | 1.59 | 1.59 | 1.59 | 1.59 |


## Arms vs baseline: commanded grip force [N], rank mode

| cell | n | mean commanded grip force [N] | Δ vs baseline | 95% CI |
|---|---|---|---|---|
| baseline | 992 | 15.881 | +0.000 | [+0.000, +0.000] |
| squeeze | 992 | 19.716 | +3.835 | [+3.400, +4.297] |
| oracle | 992 | 16.460 | +0.579 | [-0.114, +1.300] |
| table_q | 992 | 17.905 | +2.024 | [+1.213, +2.814] |
| table_mean | 992 | 17.899 | +2.018 | [+1.590, +2.455] |
| table_squeeze | 992 | 21.302 | +5.421 | [+5.000, +5.852] |

Per material (mean over trials):

| material (bin) | baseline | squeeze | oracle | table_q | table_mean | table_squeeze |
|---|---|---|---|---|---|---|
| glass (very low) | 27.45 | 37.34 | 27.24 | 34.32 | 35.32 | 40.00 |
| ceramic (low) | 27.37 | 27.37 | 14.42 | 1.77 | 22.07 | 27.37 |
| metal (low) | 7.45 | 15.24 | 14.78 | 18.87 | 13.10 | 17.70 |
| plastic (mid) | 29.79 | 34.27 | 29.72 | 34.62 | 31.93 | 37.19 |
| paper (mid-high) | 14.00 | 15.24 | 16.21 | 16.20 | 13.95 | 16.62 |
| foam (high) | 3.00 | 3.00 | 3.00 | 3.00 | 3.00 | 3.00 |
| rubber (high) | 3.00 | 3.00 | 3.00 | 3.00 | 3.00 | 3.00 |


## Arms vs baseline: commanded grip force [N], filter mode

| cell | n | mean commanded grip force [N] | Δ vs baseline | 95% CI |
|---|---|---|---|---|
| baseline | 992 | 16.280 | +0.000 | [+0.000, +0.000] |
| squeeze | 992 | 20.909 | +4.629 | [+4.109, +5.157] |
| oracle | 992 | 16.748 | +0.468 | [-0.196, +1.220] |
| table_q | 992 | 18.461 | +2.180 | [+1.364, +3.030] |
| table_mean | 992 | 18.749 | +2.468 | [+1.997, +2.941] |
| table_squeeze | 992 | 23.444 | +7.164 | [+6.599, +7.774] |

Per material (mean over trials):

| material (bin) | baseline | squeeze | oracle | table_q | table_mean | table_squeeze |
|---|---|---|---|---|---|---|
| glass (very low) | 26.61 | 37.41 | 27.21 | 34.48 | 35.53 | 40.00 |
| ceramic (low) | 27.37 | 27.37 | 14.42 | 1.77 | 22.07 | 27.37 |
| metal (low) | 8.27 | 19.72 | 15.52 | 19.93 | 14.61 | 25.86 |
| plastic (mid) | 30.88 | 35.10 | 30.53 | 35.90 | 34.01 | 38.86 |
| paper (mid-high) | 14.85 | 15.98 | 16.10 | 16.72 | 14.77 | 17.62 |
| foam (high) | 3.00 | 3.00 | 3.00 | 3.00 | 3.00 | 3.00 |
| rubber (high) | 3.00 | 3.00 | 3.00 | 3.00 | 3.00 | 3.00 |


## How often does knowing mu change the grasp?

- rank: baseline and oracle choose the same grasp in 78% of 907 trials
- rank: baseline and table_q choose the same grasp in 75% of 893 trials
- rank: oracle and table_q choose the same grasp in 78% of 853 trials
- rank, low-mu: baseline and oracle choose the same grasp in 74% of 521 trials
- rank, high-mu: baseline and oracle choose the same grasp in 84% of 386 trials
- filter: baseline and oracle choose the same grasp in 68% of 907 trials
- filter: baseline and table_q choose the same grasp in 65% of 893 trials
- filter: oracle and table_q choose the same grasp in 71% of 853 trials
- filter, low-mu: baseline and oracle choose the same grasp in 55% of 521 trials
- filter, high-mu: baseline and oracle choose the same grasp in 86% of 386 trials


## Analytical epsilon vs measured wrench at slip

Spearman(eps(mu*) x 2F, wrench at slip) pooled = +0.03 over 2918 grasps; per object: 028_skillet_lid: +0.19 (n=288); 038_padlock: +0.28 (n=746); 010_potted_meat_can: +0.39 (n=485); 006_mustard_bottle: +0.63 (n=253); 021_bleach_cleanser: -0.23 (n=64); 003_cracker_box: +0.04 (n=447); 004_sugar_box: +0.31 (n=186); 061_foam_brick: +0.69 (n=217); 057_racquetball: +0.97 (n=232)


## Planner fallbacks and force capping

| cell | mode | executed | fallback (nothing holdable under cap) | force capped |
|---|---|---|---|---|
| baseline | filter | 992 | 19% | 19% |
| baseline | rank | 992 | 19% | 19% |
| oracle | filter | 907 | 23% | 23% |
| oracle | rank | 907 | 23% | 23% |
| table_q | filter | 893 | 24% | 24% |
| table_q | rank | 893 | 24% | 24% |
