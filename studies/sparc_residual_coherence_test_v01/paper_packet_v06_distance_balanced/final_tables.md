# SPARC v0.6 Paper Tables

Primary endpoint: fixed quality-pass C-minus-A, `rms_log_tpg`, one-sided greater alternative.

## Primary Result

| comparison | n A | n C | median A | median C | C-A diff | p | CI low | CI high |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| C_minus_A | 17 | 28 | 0.1244 | 0.2086 | 0.08427 | 0.0009999 | 0.04481 | 0.1599 |

## Class Medians

| view | class | n | median RMS | median weighted RMS | median outer residual |
| --- | --- | --- | --- | --- | --- |
| full_sample | A | 19 | 0.1244 | 0.09799 | 0.00928 |
| full_sample | B | 103 | 0.1705 | 0.1608 | -0.0005278 |
| full_sample | C | 53 | 0.1945 | 0.1981 | -0.02873 |
| quality_pass | A | 17 | 0.1244 | 0.09799 | 0.03928 |
| quality_pass | B | 28 | 0.1647 | 0.1557 | -0.004726 |
| quality_pass | C | 28 | 0.2086 | 0.2119 | -0.0285 |

## Comparisons

| view | comparison | n left | n right | diff | p | CI low | CI high |
| --- | --- | --- | --- | --- | --- | --- | --- |
| full_sample | nonA_minus_A | 19 | 156 | 0.05783 | 0.0143 | 0.01851 | 0.09098 |
| full_sample | C_minus_nonC | 122 | 53 | 0.04333 | 0.08929 | -0.009469 | 0.08359 |
| full_sample | C_minus_A | 19 | 53 | 0.07012 | 0.0022 | 0.0217 | 0.1151 |
| quality_pass | nonA_minus_A | 17 | 56 | 0.06612 | 0.005799 | 0.02559 | 0.109 |
| quality_pass | C_minus_nonC | 45 | 28 | 0.06998 | 0.0173 | 0.02276 | 0.1417 |
| quality_pass | C_minus_A | 17 | 28 | 0.08427 | 0.0009999 | 0.04481 | 0.1599 |

## Trend

| view | metric | n | rho | p |
| --- | --- | --- | --- | --- |
| full_sample | rms_log_tpg | 175 | 0.1673 | 0.0144 |
| quality_pass | rms_log_tpg | 73 | 0.362 | 0.0011 |
