# SPARC v0.5 Scale / Mass / Distance Controls

These checks test whether the quality-pass A/C split is obviously confounded by distance, HECATE stellar mass, or coarse morphology. P-values are two-sided A-vs-C median permutation tests.

| covariate | n A | n C | median A | median C | C-A diff | p | coverage |
| --- | --- | --- | --- | --- | --- | --- | --- |
| sparc_distance_mpc | 17 | 28 | 13.8 | 7.83 | -5.97 | 0.0249 | A=17/17; C=28/28 |
| sparc_distance_error_mpc | 17 | 28 | 2.5 | 2.19 | -0.31 | 0.6154 | A=17/17; C=28/28 |
| hecate_distance_mpc | 14 | 20 | 15.46 | 7.14 | -8.315 | 0.0345 | A=14/17; C=20/28 |
| hecate_stellar_mass_log | 10 | 11 | 9.956 | 8.771 | -1.185 | 0.0048 | A=10/17; C=11/28 |
| hecate_morph_t | 14 | 20 | 6 | 8.85 | 2.85 | 0.0115 | A=14/17; C=20/28 |

Interpretation guardrail: HECATE mass coverage is incomplete for SPARC dwarfs, so mass controls are reviewer-risk diagnostics, not alternate primary endpoints.
