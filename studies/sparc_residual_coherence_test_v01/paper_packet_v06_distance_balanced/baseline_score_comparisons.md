# Alternative Baseline-Score Comparisons

Same quality-pass A/C sample and same median C-minus-A statistic. Positive values mean disturbed C galaxies have larger residual scatter.

`Fixed projection score` is the old high-coherence TPG limit (`S_tau=1`). The two Tau Core rows are operational extended candidates with external, residual-blind `S_tau` mappings; they are sensitivity tests, not primary Paper 1 endpoints.

| Score | n_A | n_C | median A | median C | C-A | one-sided p | 95% bootstrap CI |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| Fixed projection score | 17 | 28 | 0.124355 | 0.208624 | 0.0842686 | 0.00209979 | [0.0443983, 0.157918] |
| Tau Core S_tau class-gated | 17 | 28 | 0.124355 | 0.616147 | 0.491792 | 9.999e-05 | [0.325978, 0.73573] |
| Tau Core S_tau evidence-gated | 17 | 28 | 0.124355 | 0.616147 | 0.491792 | 9.999e-05 | [0.325307, 0.73573] |
| Tau Core S_tau continuous external | 17 | 28 | 0.132534 | 0.473177 | 0.340643 | 9.999e-05 | [0.186878, 0.544119] |
| Tau Core S_tau soft-calibrated | 17 | 28 | 0.142446 | 0.322959 | 0.180513 | 0.00289971 | [0.076575, 0.246527] |
| Newtonian baryonic | 17 | 28 | 0.57056 | 0.616147 | 0.0455866 | 0.384762 | [-0.196053, 0.313757] |
| MOND simple-mu | 17 | 28 | 0.113658 | 0.232381 | 0.118723 | 0.00179982 | [0.00303851, 0.174148] |
| Empirical RAR | 17 | 28 | 0.113603 | 0.22442 | 0.110816 | 0.00119988 | [0.00305295, 0.174704] |

Interpretation: these are baseline-score stress tests, not replacement primary endpoints. If several smooth residual scores show the same direction, the paper should phrase the result as a residual-disturbance association rather than uniqueness of the fixed projection prescription. If the `S_tau`-gated variants mechanically increase A/C separation, that is expected: the same external labels are being used to gate the response and should not be reused as independent proof.
