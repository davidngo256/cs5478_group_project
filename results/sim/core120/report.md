# Simulation study: core120


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
| mu = 0.5 | 0.574 (baseline) | 0.643 (squeeze only) |
| mu* | 0.569 (selection only) | 0.621 (oracle) |

selection-only gain -0.005 [-0.022, +0.013]; squeeze-only gain +0.070 [+0.051, +0.089]; oracle gain +0.047 [+0.024, +0.071] (n = 992 paired trials)

**low-mu objects (glass, metal, ceramic, plastic)**

| grasp chosen with \ force set with | mu = 0.5 | mu* |
|---|---|---|
| mu = 0.5 | 0.391 (baseline) | 0.497 (squeeze only) |
| mu* | 0.378 (selection only) | 0.462 (oracle) |

selection-only gain -0.013 [-0.036, +0.008]; squeeze-only gain +0.106 [+0.079, +0.134]; oracle gain +0.071 [+0.040, +0.104] (n = 606 paired trials)

**high-mu objects (paper, foam, rubber)**

| grasp chosen with \ force set with | mu = 0.5 | mu* |
|---|---|---|
| mu = 0.5 | 0.860 (baseline) | 0.873 (squeeze only) |
| mu* | 0.868 (selection only) | 0.870 (oracle) |

selection-only gain +0.008 [-0.018, +0.034]; squeeze-only gain +0.013 [-0.005, +0.031]; oracle gain +0.010 [-0.021, +0.041] (n = 386 paired trials)


## 2x2 on lift success under the force cap, filter mode

| grasp chosen with \ force set with | mu = 0.5 | mu* |
|---|---|---|
| mu = 0.5 | 0.574 (baseline) | 0.639 (squeeze only) |
| mu* | 0.551 (selection only) | 0.616 (oracle) |

selection-only gain -0.022 [-0.041, -0.004]; squeeze-only gain +0.066 [+0.045, +0.087]; oracle gain +0.042 [+0.017, +0.067] (n = 992 paired trials)

**low-mu objects (glass, metal, ceramic, plastic)**

| grasp chosen with \ force set with | mu = 0.5 | mu* |
|---|---|---|
| mu = 0.5 | 0.391 (baseline) | 0.492 (squeeze only) |
| mu* | 0.360 (selection only) | 0.464 (oracle) |

selection-only gain -0.031 [-0.056, -0.007]; squeeze-only gain +0.101 [+0.071, +0.130]; oracle gain +0.073 [+0.040, +0.106] (n = 606 paired trials)

**high-mu objects (paper, foam, rubber)**

| grasp chosen with \ force set with | mu = 0.5 | mu* |
|---|---|---|
| mu = 0.5 | 0.860 (baseline) | 0.870 (squeeze only) |
| mu* | 0.852 (selection only) | 0.855 (oracle) |

selection-only gain -0.008 [-0.036, +0.018]; squeeze-only gain +0.010 [-0.005, +0.028]; oracle gain -0.005 [-0.036, +0.026] (n = 386 paired trials)


## 2x2 on wrench at slip [N], 0 if the grasp failed, rank mode

| grasp chosen with \ force set with | mu = 0.5 | mu* |
|---|---|---|
| mu = 0.5 | 1.325 (baseline) | 1.593 (squeeze only) |
| mu* | 1.299 (selection only) | 1.516 (oracle) |

selection-only gain -0.026 [-0.082, +0.030]; squeeze-only gain +0.268 [+0.210, +0.330]; oracle gain +0.190 [+0.118, +0.268] (n = 992 paired trials)

**low-mu objects (glass, metal, ceramic, plastic)**

| grasp chosen with \ force set with | mu = 0.5 | mu* |
|---|---|---|
| mu = 0.5 | 1.118 (baseline) | 1.543 (squeeze only) |
| mu* | 1.068 (selection only) | 1.432 (oracle) |

selection-only gain -0.050 [-0.124, +0.024]; squeeze-only gain +0.425 [+0.342, +0.514]; oracle gain +0.315 [+0.211, +0.422] (n = 606 paired trials)

**high-mu objects (paper, foam, rubber)**

| grasp chosen with \ force set with | mu = 0.5 | mu* |
|---|---|---|
| mu = 0.5 | 1.651 (baseline) | 1.671 (squeeze only) |
| mu* | 1.662 (selection only) | 1.646 (oracle) |

selection-only gain +0.011 [-0.075, +0.100]; squeeze-only gain +0.020 [-0.043, +0.085]; oracle gain -0.005 [-0.104, +0.096] (n = 386 paired trials)


## 2x2 on wrench at slip [N], 0 if the grasp failed, filter mode

| grasp chosen with \ force set with | mu = 0.5 | mu* |
|---|---|---|
| mu = 0.5 | 1.335 (baseline) | 1.639 (squeeze only) |
| mu* | 1.244 (selection only) | 1.499 (oracle) |

selection-only gain -0.092 [-0.152, -0.033]; squeeze-only gain +0.304 [+0.231, +0.379]; oracle gain +0.164 [+0.080, +0.243] (n = 992 paired trials)

**low-mu objects (glass, metal, ceramic, plastic)**

| grasp chosen with \ force set with | mu = 0.5 | mu* |
|---|---|---|
| mu = 0.5 | 1.150 (baseline) | 1.642 (squeeze only) |
| mu* | 1.019 (selection only) | 1.450 (oracle) |

selection-only gain -0.131 [-0.210, -0.051]; squeeze-only gain +0.492 [+0.386, +0.596]; oracle gain +0.300 [+0.188, +0.412] (n = 606 paired trials)

**high-mu objects (paper, foam, rubber)**

| grasp chosen with \ force set with | mu = 0.5 | mu* |
|---|---|---|
| mu = 0.5 | 1.626 (baseline) | 1.634 (squeeze only) |
| mu* | 1.595 (selection only) | 1.575 (oracle) |

selection-only gain -0.030 [-0.123, +0.055]; squeeze-only gain +0.009 [-0.051, +0.070]; oracle gain -0.051 [-0.156, +0.052] (n = 386 paired trials)


## Arms vs baseline: success, rank mode

| cell | n | mean success | Δ vs baseline | 95% CI |
|---|---|---|---|---|
| baseline | 992 | 0.574 | +0.000 | [+0.000, +0.000] |
| squeeze | 992 | 0.643 | +0.070 | [+0.051, +0.089] |
| oracle | 992 | 0.621 | +0.047 | [+0.024, +0.071] |
| table_q | 992 | 0.618 | +0.044 | [+0.020, +0.069] |
| table_mean | 992 | 0.617 | +0.043 | [+0.023, +0.065] |
| table_squeeze | 992 | 0.639 | +0.066 | [+0.046, +0.085] |
| table_q0.05 | 992 | 0.610 | +0.036 | [+0.012, +0.061] |
| table_q0.25 | 992 | 0.627 | +0.053 | [+0.030, +0.076] |

Per material (mean over trials):

| material (bin) | baseline | squeeze | oracle | table_q | table_mean | table_squeeze | table_q0.05 | table_q0.25 |
|---|---|---|---|---|---|---|---|---|
| glass (very low) | 0.46 | 0.57 | 0.49 | 0.47 | 0.49 | 0.57 | 0.46 | 0.49 |
| ceramic (low) | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| metal (low) | 0.66 | 0.87 | 0.87 | 0.87 | 0.84 | 0.88 | 0.88 | 0.86 |
| plastic (mid) | 0.25 | 0.29 | 0.23 | 0.24 | 0.23 | 0.28 | 0.22 | 0.23 |
| paper (mid-high) | 0.63 | 0.66 | 0.66 | 0.64 | 0.67 | 0.64 | 0.61 | 0.71 |
| foam (high) | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| rubber (high) | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |


## Arms vs baseline: success, filter mode

| cell | n | mean success | Δ vs baseline | 95% CI |
|---|---|---|---|---|
| baseline | 992 | 0.574 | +0.000 | [+0.000, +0.000] |
| squeeze | 992 | 0.639 | +0.066 | [+0.045, +0.087] |
| oracle | 992 | 0.616 | +0.042 | [+0.017, +0.067] |
| table_q | 992 | 0.615 | +0.041 | [+0.015, +0.067] |
| table_mean | 992 | 0.611 | +0.037 | [+0.015, +0.059] |
| table_squeeze | 992 | 0.623 | +0.049 | [+0.028, +0.072] |
| table_q0.05 | 992 | 0.608 | +0.034 | [+0.009, +0.060] |
| table_q0.25 | 992 | 0.621 | +0.047 | [+0.023, +0.073] |

Per material (mean over trials):

| material (bin) | baseline | squeeze | oracle | table_q | table_mean | table_squeeze | table_q0.05 | table_q0.25 |
|---|---|---|---|---|---|---|---|---|
| glass (very low) | 0.41 | 0.50 | 0.47 | 0.47 | 0.51 | 0.50 | 0.43 | 0.51 |
| ceramic (low) | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| metal (low) | 0.65 | 0.87 | 0.84 | 0.85 | 0.80 | 0.82 | 0.87 | 0.84 |
| plastic (mid) | 0.30 | 0.32 | 0.28 | 0.25 | 0.24 | 0.31 | 0.24 | 0.23 |
| paper (mid-high) | 0.63 | 0.66 | 0.62 | 0.63 | 0.66 | 0.63 | 0.60 | 0.68 |
| foam (high) | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| rubber (high) | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |


## Arms vs baseline: wrench at slip [N], rank mode

| cell | n | mean wrench at slip [N] | Δ vs baseline | 95% CI |
|---|---|---|---|---|
| baseline | 992 | 1.325 | +0.000 | [+0.000, +0.000] |
| squeeze | 992 | 1.593 | +0.268 | [+0.210, +0.330] |
| oracle | 992 | 1.516 | +0.190 | [+0.118, +0.268] |
| table_q | 992 | 1.632 | +0.307 | [+0.224, +0.390] |
| table_mean | 992 | 1.587 | +0.262 | [+0.188, +0.334] |
| table_squeeze | 992 | 1.766 | +0.440 | [+0.370, +0.513] |
| table_q0.05 | 992 | 1.615 | +0.289 | [+0.202, +0.375] |
| table_q0.25 | 992 | 1.657 | +0.331 | [+0.252, +0.414] |

Per material (mean over trials):

| material (bin) | baseline | squeeze | oracle | table_q | table_mean | table_squeeze | table_q0.05 | table_q0.25 |
|---|---|---|---|---|---|---|---|---|
| glass (very low) | 1.43 | 1.90 | 1.66 | 1.63 | 1.68 | 1.97 | 1.59 | 1.71 |
| ceramic (low) | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| metal (low) | 1.66 | 2.52 | 2.55 | 3.03 | 2.76 | 3.23 | 3.11 | 2.95 |
| plastic (mid) | 0.89 | 1.02 | 0.79 | 0.84 | 0.81 | 1.08 | 0.77 | 0.79 |
| paper (mid-high) | 1.99 | 2.05 | 1.99 | 2.06 | 2.13 | 2.11 | 1.95 | 2.34 |
| foam (high) | 1.28 | 1.28 | 1.27 | 1.28 | 1.28 | 1.28 | 1.27 | 1.28 |
| rubber (high) | 1.61 | 1.61 | 1.61 | 1.61 | 1.61 | 1.61 | 1.61 | 1.61 |


## Arms vs baseline: wrench at slip [N], filter mode

| cell | n | mean wrench at slip [N] | Δ vs baseline | 95% CI |
|---|---|---|---|---|
| baseline | 992 | 1.335 | +0.000 | [+0.000, +0.000] |
| squeeze | 992 | 1.639 | +0.304 | [+0.231, +0.379] |
| oracle | 992 | 1.499 | +0.164 | [+0.080, +0.243] |
| table_q | 992 | 1.642 | +0.307 | [+0.210, +0.403] |
| table_mean | 992 | 1.541 | +0.206 | [+0.126, +0.282] |
| table_squeeze | 992 | 1.799 | +0.464 | [+0.375, +0.552] |
| table_q0.05 | 992 | 1.606 | +0.270 | [+0.174, +0.364] |
| table_q0.25 | 992 | 1.615 | +0.280 | [+0.194, +0.363] |

Per material (mean over trials):

| material (bin) | baseline | squeeze | oracle | table_q | table_mean | table_squeeze | table_q0.05 | table_q0.25 |
|---|---|---|---|---|---|---|---|---|
| glass (very low) | 1.24 | 1.62 | 1.51 | 1.58 | 1.71 | 1.66 | 1.47 | 1.71 |
| ceramic (low) | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| metal (low) | 1.67 | 2.81 | 2.48 | 3.10 | 2.56 | 3.49 | 3.11 | 2.86 |
| plastic (mid) | 1.10 | 1.20 | 1.01 | 0.91 | 0.84 | 1.24 | 0.87 | 0.80 |
| paper (mid-high) | 1.99 | 2.01 | 1.86 | 2.04 | 2.10 | 2.07 | 1.92 | 2.22 |
| foam (high) | 1.22 | 1.22 | 1.22 | 1.22 | 1.22 | 1.22 | 1.22 | 1.22 |
| rubber (high) | 1.59 | 1.59 | 1.59 | 1.59 | 1.59 | 1.59 | 1.59 | 1.59 |


## Arms vs baseline: commanded grip force [N], rank mode

| cell | n | mean commanded grip force [N] | Δ vs baseline | 95% CI |
|---|---|---|---|---|
| baseline | 992 | 18.080 | +0.000 | [+0.000, +0.000] |
| squeeze | 992 | 21.641 | +3.561 | [+3.134, +4.008] |
| oracle | 992 | 18.150 | +0.070 | [-0.616, +0.853] |
| table_q | 992 | 18.961 | +0.881 | [+0.093, +1.696] |
| table_mean | 992 | 20.224 | +2.144 | [+1.674, +2.665] |
| table_squeeze | 992 | 23.408 | +5.328 | [+4.903, +5.802] |
| table_q0.05 | 992 | 18.798 | +0.718 | [-0.075, +1.599] |
| table_q0.25 | 992 | 19.096 | +1.016 | [+0.323, +1.763] |

Per material (mean over trials):

| material (bin) | baseline | squeeze | oracle | table_q | table_mean | table_squeeze | table_q0.05 | table_q0.25 |
|---|---|---|---|---|---|---|---|---|
| glass (very low) | 28.68 | 37.20 | 27.20 | 34.43 | 35.33 | 39.29 | 31.44 | 34.97 |
| ceramic (low) | 27.37 | 27.37 | 14.42 | 1.77 | 21.78 | 27.37 | 1.18 | 6.77 |
| metal (low) | 12.70 | 21.47 | 20.22 | 22.55 | 20.16 | 25.10 | 23.26 | 21.61 |
| plastic (mid) | 31.84 | 35.39 | 31.28 | 34.43 | 33.56 | 38.18 | 34.76 | 33.85 |
| paper (mid-high) | 17.94 | 18.29 | 18.09 | 18.39 | 17.96 | 19.89 | 18.72 | 17.75 |
| foam (high) | 3.00 | 3.00 | 3.02 | 3.00 | 3.00 | 3.00 | 3.00 | 3.00 |
| rubber (high) | 3.00 | 3.00 | 3.00 | 3.00 | 3.00 | 3.00 | 3.00 | 3.00 |


## Arms vs baseline: commanded grip force [N], filter mode

| cell | n | mean commanded grip force [N] | Δ vs baseline | 95% CI |
|---|---|---|---|---|
| baseline | 992 | 18.381 | +0.000 | [+0.000, +0.000] |
| squeeze | 992 | 22.370 | +3.989 | [+3.507, +4.487] |
| oracle | 992 | 18.323 | -0.058 | [-0.757, +0.713] |
| table_q | 992 | 19.183 | +0.803 | [+0.005, +1.608] |
| table_mean | 992 | 20.272 | +1.892 | [+1.417, +2.384] |
| table_squeeze | 992 | 24.593 | +6.212 | [+5.688, +6.788] |
| table_q0.05 | 992 | 18.898 | +0.517 | [-0.294, +1.383] |
| table_q0.25 | 992 | 19.224 | +0.843 | [+0.157, +1.555] |

Per material (mean over trials):

| material (bin) | baseline | squeeze | oracle | table_q | table_mean | table_squeeze | table_q0.05 | table_q0.25 |
|---|---|---|---|---|---|---|---|---|
| glass (very low) | 30.29 | 38.99 | 28.08 | 34.58 | 35.53 | 40.00 | 31.44 | 35.10 |
| ceramic (low) | 27.37 | 27.37 | 14.42 | 1.77 | 21.78 | 27.37 | 1.18 | 6.77 |
| metal (low) | 11.36 | 22.70 | 19.34 | 22.50 | 18.29 | 28.81 | 23.00 | 20.77 |
| plastic (mid) | 33.96 | 36.90 | 32.61 | 35.58 | 35.86 | 39.95 | 35.51 | 35.38 |
| paper (mid-high) | 17.78 | 18.09 | 18.07 | 18.37 | 17.76 | 19.87 | 18.78 | 17.70 |
| foam (high) | 3.02 | 3.00 | 3.00 | 3.00 | 3.00 | 3.00 | 3.00 | 3.00 |
| rubber (high) | 3.00 | 3.00 | 3.00 | 3.00 | 3.00 | 3.00 | 3.00 | 3.00 |


## Assumed-mu sweep, rank mode

Constant-mu planner at other assumed values (ablation d), success and wrench:

| cell | n | mean success | Δ vs baseline | 95% CI |
|---|---|---|---|---|
| baseline | 992 | 0.574 | +0.000 | [+0.000, +0.000] |
| sweep:0.1 | 992 | 0.527 | -0.046 | [-0.075, -0.019] |
| sweep:0.2 | 992 | 0.585 | +0.011 | [-0.016, +0.037] |
| sweep:0.3 | 992 | 0.593 | +0.019 | [-0.007, +0.044] |
| sweep:0.4 | 992 | 0.595 | +0.021 | [+0.001, +0.041] |
| sweep:0.6 | 992 | 0.557 | -0.016 | [-0.036, +0.004] |
| sweep:0.7 | 992 | 0.526 | -0.047 | [-0.071, -0.024] |
| sweep:0.9 | 992 | 0.471 | -0.103 | [-0.131, -0.077] |
| oracle | 992 | 0.621 | +0.047 | [+0.024, +0.071] |

| cell | n | mean wrench [N] | Δ vs baseline | 95% CI |
|---|---|---|---|---|
| baseline | 992 | 1.325 | +0.000 | [+0.000, +0.000] |
| sweep:0.1 | 992 | 1.598 | +0.273 | [+0.159, +0.382] |
| sweep:0.2 | 992 | 1.593 | +0.268 | [+0.175, +0.360] |
| sweep:0.3 | 992 | 1.520 | +0.195 | [+0.105, +0.281] |
| sweep:0.4 | 992 | 1.434 | +0.109 | [+0.041, +0.174] |
| sweep:0.6 | 992 | 1.251 | -0.075 | [-0.133, -0.015] |
| sweep:0.7 | 992 | 1.141 | -0.184 | [-0.255, -0.115] |
| sweep:0.9 | 992 | 0.940 | -0.385 | [-0.465, -0.307] |
| oracle | 992 | 1.516 | +0.190 | [+0.118, +0.268] |


## Assumed-mu sweep, filter mode

Constant-mu planner at other assumed values (ablation d), success and wrench:

| cell | n | mean success | Δ vs baseline | 95% CI |
|---|---|---|---|---|
| baseline | 992 | 0.574 | +0.000 | [+0.000, +0.000] |
| sweep:0.1 | 992 | 0.534 | -0.039 | [-0.068, -0.011] |
| sweep:0.2 | 992 | 0.576 | +0.002 | [-0.027, +0.029] |
| sweep:0.3 | 992 | 0.580 | +0.006 | [-0.022, +0.034] |
| sweep:0.4 | 992 | 0.592 | +0.018 | [-0.004, +0.039] |
| sweep:0.6 | 992 | 0.553 | -0.020 | [-0.040, -0.001] |
| sweep:0.7 | 992 | 0.510 | -0.064 | [-0.087, -0.040] |
| sweep:0.9 | 992 | 0.449 | -0.125 | [-0.154, -0.099] |
| oracle | 992 | 0.616 | +0.042 | [+0.017, +0.067] |

| cell | n | mean wrench [N] | Δ vs baseline | 95% CI |
|---|---|---|---|---|
| baseline | 992 | 1.335 | +0.000 | [+0.000, +0.000] |
| sweep:0.1 | 992 | 1.671 | +0.336 | [+0.218, +0.452] |
| sweep:0.2 | 992 | 1.562 | +0.226 | [+0.121, +0.331] |
| sweep:0.3 | 992 | 1.453 | +0.118 | [+0.022, +0.208] |
| sweep:0.4 | 992 | 1.420 | +0.085 | [+0.007, +0.159] |
| sweep:0.6 | 992 | 1.236 | -0.099 | [-0.161, -0.038] |
| sweep:0.7 | 992 | 1.081 | -0.255 | [-0.327, -0.184] |
| sweep:0.9 | 992 | 0.879 | -0.456 | [-0.539, -0.378] |
| oracle | 992 | 1.499 | +0.164 | [+0.080, +0.243] |


## How often does knowing mu change the grasp?

- rank: baseline and oracle choose the same grasp in 74% of 907 trials
- rank: baseline and table_q choose the same grasp in 65% of 893 trials
- rank: oracle and table_q choose the same grasp in 71% of 853 trials
- rank, low-mu: baseline and oracle choose the same grasp in 68% of 521 trials
- rank, high-mu: baseline and oracle choose the same grasp in 82% of 386 trials
- filter: baseline and oracle choose the same grasp in 65% of 907 trials
- filter: baseline and table_q choose the same grasp in 53% of 893 trials
- filter: oracle and table_q choose the same grasp in 64% of 853 trials
- filter, low-mu: baseline and oracle choose the same grasp in 50% of 521 trials
- filter, high-mu: baseline and oracle choose the same grasp in 86% of 386 trials


## Analytical epsilon vs measured wrench at slip

Spearman(eps(mu*) x 2F, wrench at slip) pooled = +0.33 over 7029 grasps; per object: 028_skillet_lid: +0.35 (n=821); 038_padlock: +0.66 (n=1896); 010_potted_meat_can: +0.72 (n=1170); 006_mustard_bottle: +0.77 (n=716); 021_bleach_cleanser: +0.05 (n=158); 003_cracker_box: +0.59 (n=713); 004_sugar_box: +0.53 (n=603); 061_foam_brick: +0.86 (n=509); 057_racquetball: +0.98 (n=443)


## Planner fallbacks and force capping

| cell | mode | executed | fallback (nothing holdable under cap) | force capped |
|---|---|---|---|---|
| baseline | filter | 992 | 22% | 22% |
| baseline | rank | 992 | 22% | 22% |
| oracle | filter | 907 | 29% | 29% |
| oracle | rank | 907 | 29% | 29% |
| table_q | filter | 893 | 32% | 32% |
| table_q | rank | 893 | 32% | 32% |
