# Run-to-run spread: core120, filter mode, success

Trials split into blocks of 40 per object (3 blocks); each block is the size of one original run. Gains are paired differences to the baseline; the pooled column uses all trials with a 95% bootstrap CI. 'block SD' is the standard deviation of the per-block gains: what to expect between two independent 40-trial runs.

## all objects

| arm | block 0 | block 1 | block 2 | pooled [95% CI] | n | block SD |
|---|---|---|---|---|---|---|
| squeeze | +0.095 | +0.054 | +0.048 | +0.066 [+0.045, +0.087] | 992 | 0.025 |
| select | -0.027 | -0.018 | -0.021 | -0.022 [-0.041, -0.004] | 992 | 0.005 |
| oracle | +0.058 | +0.036 | +0.033 | +0.042 [+0.017, +0.067] | 992 | 0.014 |
| table_mean | +0.055 | +0.024 | +0.033 | +0.037 [+0.015, +0.059] | 992 | 0.016 |
| table_q | +0.061 | +0.051 | +0.012 | +0.041 [+0.015, +0.067] | 992 | 0.026 |
| table_squeeze | +0.076 | +0.036 | +0.036 | +0.049 [+0.028, +0.072] | 992 | 0.023 |

## low-mu objects

| arm | block 0 | block 1 | block 2 | pooled [95% CI] | n | block SD |
|---|---|---|---|---|---|---|
| squeeze | +0.139 | +0.085 | +0.079 | +0.101 [+0.071, +0.130] | 606 | 0.033 |
| select | -0.020 | -0.035 | -0.039 | -0.031 [-0.056, -0.007] | 606 | 0.010 |
| oracle | +0.109 | +0.065 | +0.044 | +0.073 [+0.040, +0.106] | 606 | 0.033 |
| table_mean | +0.069 | +0.040 | +0.049 | +0.053 [+0.020, +0.086] | 606 | 0.015 |
| table_q | +0.094 | +0.080 | +0.030 | +0.068 [+0.033, +0.104] | 606 | 0.034 |
| table_squeeze | +0.109 | +0.070 | +0.064 | +0.081 [+0.050, +0.114] | 606 | 0.024 |
