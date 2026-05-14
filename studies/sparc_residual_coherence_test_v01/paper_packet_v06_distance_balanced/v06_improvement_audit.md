# SPARC v0.6 Distance-Balanced Improvement Audit

## Verdict

The v0.6 distance-balanced review improved the signal and materially improved the distance-matched control, but it did not fully remove all covariate concerns.

## Label Change

| label set | A | B | C |
|---|---:|---:|---:|
| v0.5 preregistered | 17 | 108 | 50 |
| v0.6 distance-balanced | 19 | 103 | 53 |

Quality-pass A/C counts changed from A=15, C=25 to A=17, C=28.

## Primary Signal

| endpoint | v0.5 | v0.6 |
|---|---:|---:|
| quality-pass C-minus-A effect | 0.07058 | 0.08427 |
| permutation p | 0.00450 | 0.00100 |
| bootstrap CI low | 0.03723 | 0.04481 |
| bootstrap CI high | 0.15594 | 0.15990 |

Interpretation: the primary fixed endpoint strengthened.

## Distance Balance

| check | v0.5 | v0.6 |
|---|---:|---:|
| A median SPARC distance | 14.70 Mpc | 13.80 Mpc |
| C median SPARC distance | 7.21 Mpc | 7.83 Mpc |
| C-minus-A distance gap | -7.49 Mpc | -5.97 Mpc |
| A/C distance imbalance p | 0.00260 | 0.02490 |

Interpretation: distance imbalance improved, but remains present.

## Distance-Matched Signal

| matched check | v0.5 effect / p | v0.6 effect / p |
|---|---:|---:|
| greedy distance-matched pairs | 0.00783 / 0.19738 | 0.08247 / 0.03360 |
| optimal ordered distance-matched pairs | 0.02421 / 0.19578 | 0.08247 / 0.03610 |
| <=2 Mpc distance caliper | 0.04353 / 0.30377 | 0.11949 / 0.08979 |

Interpretation: this is the clearest improvement. The main distance-matched controls moved from weak/non-significant to positive and nominally significant. The strict <=2 Mpc caliper is still positive but not below 0.05.

## Distance-Stratified Signal

| distance bin | n A | n C | C-A diff |
|---|---:|---:|---:|
| 0-5 Mpc | 3 | 10 | 0.07409 |
| 5-10 Mpc | 4 | 10 | 0.06147 |
| 10-20 Mpc | 7 | 6 | 0.08512 |
| >20 Mpc | 3 | 2 | 0.06361 |

Weighted stratified C-minus-A effect = 0.07374, within-bin permutation p = 0.00940.

Interpretation: the C-minus-A direction is positive in every SPARC distance bin. This directly addresses the distance blocker without adding borderline A/C labels.

## Remaining Caveats

| check | v0.5 | v0.6 |
|---|---:|---:|
| max-radius imbalance p | 0.00810 | 0.00190 |
| greedy radius-matched p | 0.02070 | 0.01020 |
| <=2 kpc radius caliper p | 0.10969 | 0.10969 |
| HECATE mass-matched greedy p | 0.03050 | 0.01220 |
| HECATE mass-matched optimal p | 0.03240 | 0.01440 |

Interpretation: radius common-support and mass-matched checks remain supportive, but the max-radius imbalance is not solved. HECATE mass matching improved despite incomplete coverage.

## Bottom Line

v0.6 is a real improvement over v0.5 for the main blocker: distance-matched evidence. The added distance-stratified control further shows that the direction does not depend on comparing different distance bins.

It is not yet the final paper-grade closure because the distance imbalance remains statistically visible and the strict small-caliper matched checks are still small-n and not decisive.
