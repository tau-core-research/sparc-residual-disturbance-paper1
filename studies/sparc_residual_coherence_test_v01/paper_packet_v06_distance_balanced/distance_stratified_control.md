# Distance-Stratified A/C Control

Fixed sample: quality-pass A/C rows. Labels are compared only within SPARC distance bins, then combined with `min(n_A, n_C)` stratum weights.

| distance bin | n A | n C | median A | median C | C-A diff | weight |
|---|---:|---:|---:|---:|---:|---:|
| 0-5 | 3 | 10 | 0.138812 | 0.212901 | 0.0740889 | 3 |
| 5-10 | 4 | 10 | 0.153896 | 0.215364 | 0.0614677 | 4 |
| 10-20 | 7 | 6 | 0.118484 | 0.203605 | 0.0851207 | 6 |
| >20 | 3 | 2 | 0.116777 | 0.180391 | 0.0636143 | 2 |

## Combined Statistic

- weighted stratified C-minus-A effect = 0.0737394
- within-bin label permutation p = 0.00939906
- permutations = 10000

Interpretation: this control asks whether C remains higher than A after the comparison is constrained within distance bins.
