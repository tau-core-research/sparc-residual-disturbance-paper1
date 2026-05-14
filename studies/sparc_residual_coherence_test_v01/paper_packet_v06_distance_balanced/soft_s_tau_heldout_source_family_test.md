# Soft S_tau Held-Out Source-Family Test

Frozen mapping: `soft_s_tau_frozen_mapping.md`.

This is a source-family sanity check, not a final independent validation. It keeps WHISP-derived and Reynolds/Yu-derived `S_tau` mappings separate.

## Residual Performance

| mapping family | evaluation subset | class | n | soft rms | old TPG rms | delta vs old |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| whisp | family_covered | B | 6 | 0.142835 | 0.165778 | 0.0570998 |
| whisp | family_covered | C | 17 | 0.342964 | 0.194478 | 0.14444 |
| whisp | family_covered | all | 23 | 0.331756 | 0.194478 | 0.0765774 |
| whisp | other_family_overlap | B | 4 | 0.211084 | 0.109616 | 0.0971462 |
| whisp | other_family_overlap | C | 3 | 0.342964 | 0.180773 | 0.162191 |
| whisp | other_family_overlap | all | 7 | 0.323458 | 0.138512 | 0.117715 |
| global | family_covered | A | 7 | 0.155 | 0.138645 | 0.0180908 |
| global | family_covered | B | 5 | 0.173623 | 0.124036 | 0.0451488 |
| global | family_covered | C | 4 | 0.18262 | 0.159642 | -0.0125562 |
| global | family_covered | all | 16 | 0.155175 | 0.136223 | 0.0200895 |
| global | other_family_overlap | B | 4 | 0.157684 | 0.109616 | 0.0450096 |
| global | other_family_overlap | C | 3 | 0.211671 | 0.180773 | 0.0150566 |
| global | other_family_overlap | all | 7 | 0.200492 | 0.138512 | 0.0204994 |

## Source-Family Agreement

Overlap galaxies: 7
Pearson correlation: -0.365438
Spearman correlation: -0.180187
Median WHISP S_tau: 0.739333
Median global S_tau: 0.842

```text
UGC02455;UGC05721;UGC05829;UGC07524;UGC07603;UGC09133;UGC12732
```

Reading: if the soft mapping only works in the family used to build it, it is not yet paper-grade. A stronger version needs either better cross-family agreement or a genuinely independent validation sample.
