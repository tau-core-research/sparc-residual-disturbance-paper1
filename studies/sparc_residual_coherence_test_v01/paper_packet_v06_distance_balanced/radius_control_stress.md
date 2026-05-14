# SPARC v0.6 Radius-Control Stress Tests

These checks address the max-radius imbalance flagged by the covariate stress test. They do not redefine the fixed primary endpoint.

| control | n A | n C | median radius A | median radius C | effect | p | CI low | CI high | radius detail |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| radius_overlap_window | 17 | 26 | 14.86 | 6.945 | 0.08427 | 0.0008999 | 0.04684 | 0.1559 | common radius window [1.79, 53.75] kpc |
| greedy_unique_radius_matched_pairs | 17 | 17 | 14.86 | 10.22 | 0.0788 | 0.0102 | -0.03834 | 0.1658 | median_abs_delta=1.13 kpc; max_abs_delta=29.33 kpc |
| radius_matched_pairs_delta_le_2kpc | 9 | 9 | 9.86 | 10.15 | 0.07599 | 0.1097 | -0.05816 | 0.2156 | subset of greedy unique pairs with abs(radius_delta) <= 2 kpc |

## Matched Pairs

| pair | A | C | A radius | C radius | radius delta | A RMS | C RMS | C-A RMS |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | NGC5585 | UGC00731 | 10.96 | 10.91 | -0.05 | 0.1739 | 0.3397 | 0.1658 |
| 2 | DDO154 | NGC1705 | 5.92 | 6 | 0.08 | 0.1388 | 0.3544 | 0.2156 |
| 3 | CamB | UGC07577 | 1.79 | 1.69 | -0.1 | 0.9636 | 0.6545 | -0.3091 |
| 4 | UGC00191 | UGC08490 | 9.98 | 10.15 | 0.17 | 0.1244 | 0.1865 | 0.06213 |
| 5 | ESO116-G012 | UGC06446 | 9.86 | 10.22 | 0.36 | 0.1185 | 0.1945 | 0.07599 |
| 6 | UGC05764 | UGC02455 | 3.62 | 4.03 | 0.41 | 0.3295 | 0.7931 | 0.4636 |
| 7 | UGC00128 | UGC05253 | 53.75 | 53.29 | -0.46 | 0.1386 | 0.08049 | -0.05816 |
| 8 | NGC3972 | UGC04499 | 8.72 | 8.18 | -0.54 | 0.1017 | 0.1374 | 0.03578 |
| 9 | UGC05716 | NGC0055 | 12.37 | 13.5 | 1.13 | 0.1132 | 0.2045 | 0.09128 |
| 10 | NGC6503 | UGC03580 | 23.5 | 27.06 | 3.56 | 0.0725 | 0.2803 | 0.2078 |
| 11 | NGC3917 | UGC12632 | 14.86 | 10.66 | -4.2 | 0.1436 | 0.1053 | -0.03834 |
| 12 | ESO079-G014 | UGC06917 | 16.67 | 10.47 | -6.2 | 0.1168 | 0.07149 | -0.04529 |
| 13 | NGC3198 | NGC5055 | 44.08 | 54.59 | 10.51 | 0.1562 | 0.1175 | -0.03869 |
| 14 | NGC2403 | IC2574 | 20.87 | 10.23 | -10.64 | 0.08493 | 0.2213 | 0.1364 |
| 15 | NGC4559 | UGC06973 | 20.97 | 7.85 | -13.12 | 0.1339 | 0.2127 | 0.0788 |
| 16 | NGC4183 | NGC3741 | 21.02 | 7 | -14.02 | 0.06779 | 0.2044 | 0.1366 |
| 17 | NGC7331 | UGC06818 | 36.31 | 6.98 | -29.33 | 0.09804 | 0.3083 | 0.2103 |
