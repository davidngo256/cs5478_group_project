# Simulation study: heads120


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
| mu = 0.5 | 0.573 (baseline) | 0.642 (squeeze only) |
| mu* | 0.569 (selection only) | 0.621 (oracle) |

selection-only gain -0.004 [-0.021, +0.014]; squeeze-only gain +0.070 [+0.051, +0.089]; oracle gain +0.048 [+0.025, +0.072] (n = 992 paired trials)

**low-mu objects (glass, metal, ceramic, plastic)**

| grasp chosen with \ force set with | mu = 0.5 | mu* |
|---|---|---|
| mu = 0.5 | 0.391 (baseline) | 0.497 (squeeze only) |
| mu* | 0.380 (selection only) | 0.462 (oracle) |

selection-only gain -0.012 [-0.033, +0.012]; squeeze-only gain +0.106 [+0.079, +0.134]; oracle gain +0.071 [+0.040, +0.104] (n = 606 paired trials)

**high-mu objects (paper, foam, rubber)**

| grasp chosen with \ force set with | mu = 0.5 | mu* |
|---|---|---|
| mu = 0.5 | 0.858 (baseline) | 0.870 (squeeze only) |
| mu* | 0.865 (selection only) | 0.870 (oracle) |

selection-only gain +0.008 [-0.018, +0.034]; squeeze-only gain +0.013 [-0.005, +0.031]; oracle gain +0.013 [-0.018, +0.044] (n = 386 paired trials)


## 2x2 on lift success under the force cap, filter mode

| grasp chosen with \ force set with | mu = 0.5 | mu* |
|---|---|---|
| mu = 0.5 | 0.569 (baseline) | 0.633 (squeeze only) |
| mu* | 0.543 (selection only) | 0.609 (oracle) |

selection-only gain -0.025 [-0.043, -0.005]; squeeze-only gain +0.065 [+0.043, +0.086]; oracle gain +0.040 [+0.016, +0.065] (n = 992 paired trials)

**low-mu objects (glass, metal, ceramic, plastic)**

| grasp chosen with \ force set with | mu = 0.5 | mu* |
|---|---|---|
| mu = 0.5 | 0.380 (baseline) | 0.482 (squeeze only) |
| mu* | 0.348 (selection only) | 0.457 (oracle) |

selection-only gain -0.031 [-0.058, -0.005]; squeeze-only gain +0.102 [+0.073, +0.132]; oracle gain +0.078 [+0.045, +0.111] (n = 606 paired trials)

**high-mu objects (paper, foam, rubber)**

| grasp chosen with \ force set with | mu = 0.5 | mu* |
|---|---|---|
| mu = 0.5 | 0.865 (baseline) | 0.870 (squeeze only) |
| mu* | 0.850 (selection only) | 0.847 (oracle) |

selection-only gain -0.016 [-0.041, +0.010]; squeeze-only gain +0.005 [-0.013, +0.023]; oracle gain -0.018 [-0.047, +0.013] (n = 386 paired trials)


## 2x2 on wrench at slip [N], 0 if the grasp failed, rank mode

| grasp chosen with \ force set with | mu = 0.5 | mu* |
|---|---|---|
| mu = 0.5 | 1.317 (baseline) | 1.589 (squeeze only) |
| mu* | 1.296 (selection only) | 1.514 (oracle) |

selection-only gain -0.021 [-0.075, +0.036]; squeeze-only gain +0.272 [+0.215, +0.336]; oracle gain +0.197 [+0.123, +0.275] (n = 992 paired trials)

**low-mu objects (glass, metal, ceramic, plastic)**

| grasp chosen with \ force set with | mu = 0.5 | mu* |
|---|---|---|
| mu = 0.5 | 1.109 (baseline) | 1.542 (squeeze only) |
| mu* | 1.070 (selection only) | 1.432 (oracle) |

selection-only gain -0.039 [-0.112, +0.031]; squeeze-only gain +0.433 [+0.351, +0.521]; oracle gain +0.323 [+0.220, +0.429] (n = 606 paired trials)

**high-mu objects (paper, foam, rubber)**

| grasp chosen with \ force set with | mu = 0.5 | mu* |
|---|---|---|
| mu = 0.5 | 1.644 (baseline) | 1.663 (squeeze only) |
| mu* | 1.651 (selection only) | 1.644 (oracle) |

selection-only gain +0.007 [-0.074, +0.090]; squeeze-only gain +0.019 [-0.043, +0.084]; oracle gain -0.000 [-0.099, +0.100] (n = 386 paired trials)


## 2x2 on wrench at slip [N], 0 if the grasp failed, filter mode

| grasp chosen with \ force set with | mu = 0.5 | mu* |
|---|---|---|
| mu = 0.5 | 1.315 (baseline) | 1.618 (squeeze only) |
| mu* | 1.219 (selection only) | 1.477 (oracle) |

selection-only gain -0.096 [-0.155, -0.035]; squeeze-only gain +0.303 [+0.230, +0.383]; oracle gain +0.162 [+0.079, +0.245] (n = 992 paired trials)

**low-mu objects (glass, metal, ceramic, plastic)**

| grasp chosen with \ force set with | mu = 0.5 | mu* |
|---|---|---|
| mu = 0.5 | 1.105 (baseline) | 1.608 (squeeze only) |
| mu* | 0.982 (selection only) | 1.430 (oracle) |

selection-only gain -0.122 [-0.205, -0.042]; squeeze-only gain +0.504 [+0.399, +0.609]; oracle gain +0.325 [+0.216, +0.436] (n = 606 paired trials)

**high-mu objects (paper, foam, rubber)**

| grasp chosen with \ force set with | mu = 0.5 | mu* |
|---|---|---|
| mu = 0.5 | 1.646 (baseline) | 1.634 (squeeze only) |
| mu* | 1.591 (selection only) | 1.552 (oracle) |

selection-only gain -0.054 [-0.145, +0.031]; squeeze-only gain -0.011 [-0.078, +0.054]; oracle gain -0.094 [-0.197, +0.010] (n = 386 paired trials)


## Arms vs baseline: success, rank mode

| cell | n | mean success | Δ vs baseline | 95% CI |
|---|---|---|---|---|
| baseline | 992 | 0.573 | +0.000 | [+0.000, +0.000] |
| squeeze | 992 | 0.642 | +0.070 | [+0.051, +0.089] |
| oracle | 992 | 0.621 | +0.048 | [+0.025, +0.072] |
| table_q | 992 | 0.618 | +0.045 | [+0.022, +0.070] |
| table_mean | 992 | 0.614 | +0.041 | [+0.021, +0.061] |
| table_squeeze | 992 | 0.635 | +0.062 | [+0.043, +0.082] |
| head:clip | 992 | 0.594 | +0.021 | [-0.006, +0.047] |
| head:clip:mean | 992 | 0.602 | +0.029 | [+0.012, +0.045] |
| head:clip:squeeze | 992 | 0.631 | +0.058 | [+0.040, +0.078] |
| head:dms46 | 992 | 0.611 | +0.038 | [+0.015, +0.061] |
| head:dms46:mean | 992 | 0.603 | +0.030 | [+0.014, +0.046] |
| head:dms46:squeeze | 992 | 0.625 | +0.052 | [+0.035, +0.072] |
| head:mobilenet | 992 | 0.573 | +0.000 | [-0.026, +0.027] |
| head:mobilenet:mean | 992 | 0.624 | +0.051 | [+0.030, +0.073] |
| head:mobilenet:squeeze | 992 | 0.638 | +0.066 | [+0.045, +0.087] |

Per material (mean over trials):

| material (bin) | baseline | squeeze | oracle | table_q | table_mean | table_squeeze | head:clip | head:clip:mean |
|---|---|---|---|---|---|---|---|---|
| glass (very low) | 0.46 | 0.57 | 0.49 | 0.47 | 0.48 | 0.56 | 0.57 | 0.42 |
| ceramic (low) | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| metal (low) | 0.66 | 0.87 | 0.87 | 0.87 | 0.84 | 0.88 | 0.86 | 0.72 |
| plastic (mid) | 0.25 | 0.29 | 0.23 | 0.24 | 0.23 | 0.27 | 0.23 | 0.31 |
| paper (mid-high) | 0.62 | 0.66 | 0.66 | 0.64 | 0.66 | 0.64 | 0.42 | 0.71 |
| foam (high) | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| rubber (high) | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |


## Arms vs baseline: success, filter mode

| cell | n | mean success | Δ vs baseline | 95% CI |
|---|---|---|---|---|
| baseline | 992 | 0.569 | +0.000 | [+0.000, +0.000] |
| squeeze | 992 | 0.633 | +0.065 | [+0.043, +0.086] |
| oracle | 992 | 0.609 | +0.040 | [+0.016, +0.065] |
| table_q | 992 | 0.618 | +0.049 | [+0.024, +0.075] |
| table_mean | 992 | 0.610 | +0.041 | [+0.019, +0.065] |
| table_squeeze | 992 | 0.627 | +0.058 | [+0.038, +0.080] |
| head:clip | 992 | 0.585 | +0.016 | [-0.012, +0.044] |
| head:clip:mean | 992 | 0.595 | +0.026 | [+0.005, +0.046] |
| head:clip:squeeze | 992 | 0.624 | +0.055 | [+0.035, +0.077] |
| head:dms46 | 992 | 0.614 | +0.045 | [+0.021, +0.071] |
| head:dms46:mean | 992 | 0.592 | +0.023 | [+0.004, +0.043] |
| head:dms46:squeeze | 992 | 0.623 | +0.054 | [+0.034, +0.076] |
| head:mobilenet | 992 | 0.570 | +0.001 | [-0.027, +0.029] |
| head:mobilenet:mean | 992 | 0.609 | +0.040 | [+0.017, +0.064] |
| head:mobilenet:squeeze | 992 | 0.629 | +0.060 | [+0.039, +0.083] |

Per material (mean over trials):

| material (bin) | baseline | squeeze | oracle | table_q | table_mean | table_squeeze | head:clip | head:clip:mean |
|---|---|---|---|---|---|---|---|---|
| glass (very low) | 0.38 | 0.50 | 0.47 | 0.47 | 0.51 | 0.50 | 0.57 | 0.32 |
| ceramic (low) | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| metal (low) | 0.64 | 0.85 | 0.83 | 0.86 | 0.80 | 0.85 | 0.82 | 0.72 |
| plastic (mid) | 0.28 | 0.31 | 0.27 | 0.25 | 0.23 | 0.30 | 0.24 | 0.34 |
| paper (mid-high) | 0.64 | 0.66 | 0.60 | 0.64 | 0.66 | 0.63 | 0.41 | 0.70 |
| foam (high) | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| rubber (high) | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |


## Arms vs baseline: wrench at slip [N], rank mode

| cell | n | mean wrench at slip [N] | Δ vs baseline | 95% CI |
|---|---|---|---|---|
| baseline | 992 | 1.317 | +0.000 | [+0.000, +0.000] |
| squeeze | 992 | 1.589 | +0.272 | [+0.215, +0.336] |
| oracle | 992 | 1.514 | +0.197 | [+0.123, +0.275] |
| table_q | 992 | 1.633 | +0.316 | [+0.234, +0.396] |
| table_mean | 992 | 1.577 | +0.260 | [+0.187, +0.327] |
| table_squeeze | 992 | 1.753 | +0.436 | [+0.367, +0.509] |
| head:clip | 992 | 1.548 | +0.231 | [+0.140, +0.322] |
| head:clip:mean | 992 | 1.435 | +0.117 | [+0.061, +0.169] |
| head:clip:squeeze | 992 | 1.704 | +0.387 | [+0.322, +0.456] |
| head:dms46 | 992 | 1.581 | +0.264 | [+0.184, +0.339] |
| head:dms46:mean | 992 | 1.439 | +0.122 | [+0.066, +0.176] |
| head:dms46:squeeze | 992 | 1.653 | +0.335 | [+0.273, +0.402] |
| head:mobilenet | 992 | 1.581 | +0.263 | [+0.165, +0.360] |
| head:mobilenet:mean | 992 | 1.558 | +0.240 | [+0.172, +0.309] |
| head:mobilenet:squeeze | 992 | 1.859 | +0.542 | [+0.461, +0.625] |

Per material (mean over trials):

| material (bin) | baseline | squeeze | oracle | table_q | table_mean | table_squeeze | head:clip | head:clip:mean |
|---|---|---|---|---|---|---|---|---|
| glass (very low) | 1.43 | 1.91 | 1.66 | 1.64 | 1.66 | 1.91 | 1.89 | 1.28 |
| ceramic (low) | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| metal (low) | 1.66 | 2.52 | 2.55 | 3.04 | 2.76 | 3.23 | 2.95 | 1.94 |
| plastic (mid) | 0.86 | 1.01 | 0.79 | 0.83 | 0.81 | 1.05 | 0.81 | 1.06 |
| paper (mid-high) | 1.97 | 2.03 | 1.98 | 2.06 | 2.08 | 2.09 | 1.43 | 2.24 |
| foam (high) | 1.28 | 1.28 | 1.27 | 1.27 | 1.28 | 1.28 | 1.27 | 1.28 |
| rubber (high) | 1.61 | 1.61 | 1.61 | 1.61 | 1.61 | 1.61 | 1.61 | 1.61 |


## Arms vs baseline: wrench at slip [N], filter mode

| cell | n | mean wrench at slip [N] | Δ vs baseline | 95% CI |
|---|---|---|---|---|
| baseline | 992 | 1.315 | +0.000 | [+0.000, +0.000] |
| squeeze | 992 | 1.618 | +0.303 | [+0.230, +0.383] |
| oracle | 992 | 1.477 | +0.162 | [+0.079, +0.245] |
| table_q | 992 | 1.651 | +0.336 | [+0.236, +0.434] |
| table_mean | 992 | 1.535 | +0.220 | [+0.141, +0.298] |
| table_squeeze | 992 | 1.825 | +0.510 | [+0.421, +0.598] |
| head:clip | 992 | 1.505 | +0.190 | [+0.097, +0.286] |
| head:clip:mean | 992 | 1.414 | +0.099 | [+0.026, +0.169] |
| head:clip:squeeze | 992 | 1.763 | +0.448 | [+0.365, +0.532] |
| head:dms46 | 992 | 1.582 | +0.267 | [+0.180, +0.355] |
| head:dms46:mean | 992 | 1.387 | +0.072 | [+0.006, +0.137] |
| head:dms46:squeeze | 992 | 1.738 | +0.423 | [+0.346, +0.500] |
| head:mobilenet | 992 | 1.547 | +0.232 | [+0.123, +0.338] |
| head:mobilenet:mean | 992 | 1.511 | +0.195 | [+0.115, +0.273] |
| head:mobilenet:squeeze | 992 | 1.932 | +0.617 | [+0.522, +0.713] |

Per material (mean over trials):

| material (bin) | baseline | squeeze | oracle | table_q | table_mean | table_squeeze | head:clip | head:clip:mean |
|---|---|---|---|---|---|---|---|---|
| glass (very low) | 1.15 | 1.64 | 1.51 | 1.62 | 1.71 | 1.67 | 1.89 | 0.93 |
| ceramic (low) | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| metal (low) | 1.67 | 2.77 | 2.46 | 3.13 | 2.57 | 3.63 | 2.77 | 1.97 |
| plastic (mid) | 1.01 | 1.13 | 0.97 | 0.87 | 0.81 | 1.22 | 0.86 | 1.21 |
| paper (mid-high) | 2.04 | 2.01 | 1.79 | 2.08 | 2.07 | 2.07 | 1.38 | 2.21 |
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
| head:clip | 992 | 20.648 | +2.568 | [+2.037, +3.088] |
| head:clip:mean | 992 | 18.202 | +0.122 | [-0.165, +0.403] |
| head:clip:squeeze | 992 | 22.802 | +4.722 | [+4.374, +5.115] |
| head:dms46 | 992 | 18.336 | +0.256 | [-0.426, +0.965] |
| head:dms46:mean | 992 | 18.944 | +0.864 | [+0.567, +1.151] |
| head:dms46:squeeze | 992 | 22.400 | +4.320 | [+3.976, +4.705] |
| head:mobilenet | 992 | 20.237 | +2.157 | [+1.353, +2.958] |
| head:mobilenet:mean | 992 | 19.705 | +1.625 | [+1.281, +1.986] |
| head:mobilenet:squeeze | 992 | 24.416 | +6.336 | [+5.865, +6.832] |

Per material (mean over trials):

| material (bin) | baseline | squeeze | oracle | table_q | table_mean | table_squeeze | head:clip | head:clip:mean |
|---|---|---|---|---|---|---|---|---|
| glass (very low) | 28.68 | 37.20 | 27.20 | 34.43 | 35.33 | 39.29 | 32.19 | 27.89 |
| ceramic (low) | 27.37 | 27.37 | 14.42 | 1.77 | 21.78 | 27.37 | 20.01 | 27.37 |
| metal (low) | 12.70 | 21.47 | 20.22 | 22.55 | 20.16 | 25.10 | 21.66 | 14.96 |
| plastic (mid) | 31.84 | 35.39 | 31.28 | 34.43 | 33.56 | 38.18 | 34.62 | 30.99 |
| paper (mid-high) | 17.94 | 18.29 | 18.09 | 18.39 | 17.96 | 19.89 | 21.08 | 17.38 |
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
| head:clip | 992 | 20.505 | +2.124 | [+1.604, +2.618] |
| head:clip:mean | 992 | 18.415 | +0.034 | [-0.262, +0.315] |
| head:clip:squeeze | 992 | 24.049 | +5.668 | [+5.225, +6.164] |
| head:dms46 | 992 | 18.332 | -0.049 | [-0.735, +0.642] |
| head:dms46:mean | 992 | 19.221 | +0.840 | [+0.540, +1.143] |
| head:dms46:squeeze | 992 | 23.622 | +5.241 | [+4.791, +5.707] |
| head:mobilenet | 992 | 20.342 | +1.961 | [+1.170, +2.744] |
| head:mobilenet:mean | 992 | 19.905 | +1.524 | [+1.200, +1.845] |
| head:mobilenet:squeeze | 992 | 25.523 | +7.142 | [+6.603, +7.721] |

Per material (mean over trials):

| material (bin) | baseline | squeeze | oracle | table_q | table_mean | table_squeeze | head:clip | head:clip:mean |
|---|---|---|---|---|---|---|---|---|
| glass (very low) | 30.29 | 38.99 | 28.08 | 34.58 | 35.53 | 40.00 | 32.38 | 27.26 |
| ceramic (low) | 27.37 | 27.37 | 14.42 | 1.77 | 21.78 | 27.37 | 20.01 | 27.37 |
| metal (low) | 11.36 | 22.70 | 19.34 | 22.50 | 18.29 | 28.81 | 19.95 | 13.69 |
| plastic (mid) | 33.96 | 36.90 | 32.61 | 35.58 | 35.86 | 39.95 | 35.57 | 33.80 |
| paper (mid-high) | 17.78 | 18.09 | 18.07 | 18.37 | 17.76 | 19.87 | 21.11 | 17.47 |
| foam (high) | 3.02 | 3.00 | 3.00 | 3.00 | 3.00 | 3.00 | 3.00 | 3.00 |
| rubber (high) | 3.00 | 3.00 | 3.00 | 3.00 | 3.00 | 3.00 | 3.00 | 3.00 |


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

Spearman(eps(mu*) x 2F, wrench at slip) pooled = +0.36 over 6437 grasps; per object: 028_skillet_lid: +0.42 (n=775); 038_padlock: +0.61 (n=1955); 010_potted_meat_can: +0.70 (n=1145); 006_mustard_bottle: +0.76 (n=646); 021_bleach_cleanser: +0.13 (n=120); 003_cracker_box: +0.71 (n=574); 004_sugar_box: +0.57 (n=513); 061_foam_brick: +0.79 (n=451); 057_racquetball: +0.97 (n=258)


## Planner fallbacks and force capping

| cell | mode | executed | fallback (nothing holdable under cap) | force capped |
|---|---|---|---|---|
| baseline | filter | 992 | 22% | 22% |
| baseline | rank | 992 | 22% | 22% |
| head:clip | filter | 967 | 35% | 35% |
| head:clip | rank | 967 | 35% | 35% |
| head:clip:mean | filter | 992 | 22% | 22% |
| head:clip:mean | rank | 992 | 22% | 22% |
| head:clip:squeeze | filter | 992 | 22% | 60% |
| head:clip:squeeze | rank | 992 | 22% | 51% |
| head:dms46 | filter | 901 | 27% | 27% |
| head:dms46 | rank | 901 | 27% | 27% |
| head:dms46:mean | filter | 989 | 25% | 25% |
| head:dms46:mean | rank | 989 | 25% | 25% |
| head:dms46:squeeze | filter | 992 | 22% | 58% |
| head:dms46:squeeze | rank | 992 | 22% | 47% |
| head:mobilenet | filter | 903 | 42% | 42% |
| head:mobilenet | rank | 903 | 42% | 42% |
| head:mobilenet:mean | filter | 991 | 25% | 25% |
| head:mobilenet:mean | rank | 991 | 25% | 25% |
| head:mobilenet:squeeze | filter | 992 | 22% | 75% |
| head:mobilenet:squeeze | rank | 992 | 22% | 63% |
| oracle | filter | 907 | 29% | 29% |
| oracle | rank | 907 | 29% | 29% |
| table_q | filter | 893 | 32% | 32% |
| table_q | rank | 893 | 32% | 32% |
