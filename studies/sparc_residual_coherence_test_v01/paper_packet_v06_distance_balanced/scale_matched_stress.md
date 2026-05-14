# SPARC v0.6 Scale-Matched Stress Tests

These paired checks ask whether the C-minus-A direction survives greedy unique matching by SPARC distance or HECATE stellar mass.

| control | n pairs | median A | median C | median abs delta | caliper | effect | p | CI low | CI high |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| greedy_unique_sparc_distance_mpc_matched_pairs | 17 | 13.8 | 9.9 | 0.36 |  | 0.08247 | 0.0336 | -0.03018 | 0.1647 |
| optimal_ordered_sparc_distance_mpc_matched_pairs | 17 | 13.8 | 9.9 | 0.53 |  | 0.08247 | 0.0361 | -0.01323 | 0.1635 |
| sparc_distance_mpc_matched_pairs_caliper | 13 | 9 | 8.64 | 0.14 | 2 Mpc | 0.1195 | 0.08979 | -0.01878 | 0.1671 |
| greedy_unique_hecate_stellar_mass_log_matched_pairs | 10 | 9.956 | 9.042 | 0.695 |  | 0.1393 | 0.0122 | 0.05342 | 0.212 |
| optimal_ordered_hecate_stellar_mass_log_matched_pairs | 10 | 9.956 | 9.042 | 0.967 |  | 0.1282 | 0.0144 | 0.06092 | 0.2115 |
| hecate_stellar_mass_log_matched_pairs_caliper | 5 | 9.728 | 9.357 | 0.25 | 0.5 dex | 0.08603 | 0.3048 | -0.1024 | 0.2078 |

The distance-matched result is a stress diagnostic, not a replacement for the fixed primary endpoint. HECATE stellar-mass matching has incomplete coverage.
