# Run-to-run spread: core120, rank mode, success

Trials split into blocks of 40 per object (3 blocks); each block is the size of one original run. Gains are paired differences to the baseline; the pooled column uses all trials with a 95% bootstrap CI. 'block SD' is the standard deviation of the per-block gains: what to expect between two independent 40-trial runs.

## all objects

| arm | block 0 | block 1 | block 2 | pooled [95% CI] | n | block SD |
|---|---|---|---|---|---|---|
| squeeze | +0.091 | +0.045 | +0.072 | +0.070 [+0.051, +0.089] | 992 | 0.023 |
| select | -0.015 | -0.009 | +0.009 | -0.005 [-0.022, +0.013] | 992 | 0.013 |
| oracle | +0.061 | +0.027 | +0.054 | +0.047 [+0.024, +0.071] | 992 | 0.018 |
| table_mean | +0.064 | +0.018 | +0.048 | +0.043 [+0.023, +0.065] | 992 | 0.023 |
| table_q | +0.067 | +0.030 | +0.036 | +0.044 [+0.020, +0.069] | 992 | 0.020 |
| table_squeeze | +0.085 | +0.039 | +0.072 | +0.066 [+0.046, +0.085] | 992 | 0.024 |

## low-mu objects

| arm | block 0 | block 1 | block 2 | pooled [95% CI] | n | block SD |
|---|---|---|---|---|---|---|
| squeeze | +0.134 | +0.070 | +0.113 | +0.106 [+0.079, +0.134] | 606 | 0.033 |
| select | -0.015 | -0.015 | -0.010 | -0.013 [-0.036, +0.008] | 606 | 0.003 |
| oracle | +0.099 | +0.045 | +0.069 | +0.071 [+0.040, +0.104] | 606 | 0.027 |
| table_mean | +0.084 | +0.025 | +0.074 | +0.061 [+0.031, +0.091] | 606 | 0.032 |
| table_q | +0.104 | +0.045 | +0.064 | +0.071 [+0.036, +0.104] | 606 | 0.030 |
| table_squeeze | +0.119 | +0.070 | +0.123 | +0.104 [+0.078, +0.132] | 606 | 0.030 |
