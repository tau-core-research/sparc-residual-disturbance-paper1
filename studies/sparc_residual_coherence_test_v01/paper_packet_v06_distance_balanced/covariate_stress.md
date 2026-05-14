# SPARC v0.5 Covariate Stress Tests

Fixed sample: v0.5 quality-pass subset. P-values are two-sided permutation tests for A-vs-C median imbalance.

| covariate | n A | n C | median A | median C | C-A diff | p |
| --- | --- | --- | --- | --- | --- | --- |
| n_points | 17 | 28 | 17 | 13 | -4 | 0.5225 |
| mean_err_vobs_kms | 17 | 28 | 2.635 | 3.56 | 0.9249 | 0.037 |
| max_radius_kpc | 17 | 28 | 14.86 | 6.945 | -7.915 | 0.0019 |
| inclination_deg | 17 | 28 | 67 | 56.5 | -10.5 | 0.1394 |
| inclination_error_deg | 17 | 28 | 3 | 3.5 | 0.5 | 0.5355 |
| hubble_type | 17 | 28 | 6 | 9 | 3 | 0.0187 |
| distance_quality | 17 | 28 | 2 | 2 | 0 | 1 |

Interpretation guardrail: these checks do not redefine the primary endpoint. They flag obvious quality or scale imbalances a reviewer may ask about.
