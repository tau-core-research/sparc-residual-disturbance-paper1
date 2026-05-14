# Old TPG vs Operational Extended Tau Core Formulae

This table separates two questions:

```text
1. Does a score separate A and C labels?
2. Does a score improve residual scatter relative to the old fixed projection score?
```

The old fixed projection score is the `S_tau=1` high-coherence TPG limit. The operational extended candidates use externally assigned `S_tau` mappings. Negative `delta vs old` means the candidate has lower median rms-log residual than the old fixed projection score for that class.

| Score | Class | n | median rms-log | old fixed-projection median | delta vs old |
| --- | --- | ---: | ---: | ---: | ---: |
| Fixed projection score | A | 17 | 0.124355 | 0.124355 | 0 |
| Fixed projection score | B | 28 | 0.16468 | 0.16468 | 0 |
| Fixed projection score | C | 28 | 0.208624 | 0.208624 | 0 |
| Fixed projection score | all | 73 | 0.165637 | 0.165637 | 0 |
| Tau Core S_tau class-gated | A | 17 | 0.124355 | 0.124355 | 0 |
| Tau Core S_tau class-gated | B | 28 | 0.313989 | 0.16468 | 0.185949 |
| Tau Core S_tau class-gated | C | 28 | 0.616147 | 0.208624 | 0.451798 |
| Tau Core S_tau class-gated | all | 73 | 0.342143 | 0.165637 | 0.144252 |
| Tau Core S_tau evidence-gated | A | 17 | 0.124355 | 0.124355 | 0 |
| Tau Core S_tau evidence-gated | B | 28 | 0.313989 | 0.16468 | 0.185949 |
| Tau Core S_tau evidence-gated | C | 28 | 0.616147 | 0.208624 | 0.451798 |
| Tau Core S_tau evidence-gated | all | 73 | 0.342143 | 0.165637 | 0.144252 |
| Tau Core S_tau continuous external | A | 17 | 0.132534 | 0.124355 | 0.00817801 |
| Tau Core S_tau continuous external | B | 28 | 0.314271 | 0.16468 | 0.185949 |
| Tau Core S_tau continuous external | C | 28 | 0.473177 | 0.208624 | 0.21675 |
| Tau Core S_tau continuous external | all | 73 | 0.308866 | 0.165637 | 0.0970724 |
| Tau Core S_tau soft-calibrated | A | 17 | 0.142446 | 0.124355 | 0.0128113 |
| Tau Core S_tau soft-calibrated | B | 28 | 0.18889 | 0.16468 | 0.0488307 |
| Tau Core S_tau soft-calibrated | C | 28 | 0.322959 | 0.208624 | 0.0225848 |
| Tau Core S_tau soft-calibrated | all | 73 | 0.193527 | 0.165637 | 0.0182482 |
| Newtonian baryonic | A | 17 | 0.57056 | 0.124355 | 0.485633 |
| Newtonian baryonic | B | 28 | 0.713113 | 0.16468 | 0.5265 |
| Newtonian baryonic | C | 28 | 0.616147 | 0.208624 | 0.451798 |
| Newtonian baryonic | all | 73 | 0.648932 | 0.165637 | 0.484299 |
| MOND simple-mu | A | 17 | 0.113658 | 0.124355 | -0.00311853 |
| MOND simple-mu | B | 28 | 0.169065 | 0.16468 | 0.0067043 |
| MOND simple-mu | C | 28 | 0.232381 | 0.208624 | 0.00563278 |
| MOND simple-mu | all | 73 | 0.166589 | 0.165637 | 0.00236175 |
| Empirical RAR | A | 17 | 0.113603 | 0.124355 | -0.00317352 |
| Empirical RAR | B | 28 | 0.168588 | 0.16468 | 0.00478483 |
| Empirical RAR | C | 28 | 0.22442 | 0.208624 | -0.000727908 |
| Empirical RAR | all | 73 | 0.165313 | 0.165637 | 0.000325352 |

Current reading: the class/evidence-gated `S_tau` variants strongly increase A/C separation because C rows are pushed toward the Newtonian baseline. That is not automatically better physics. A paper-grade extended Tau Core test should use held-out labels or independent radial `S_tau(R)` evidence before treating improved separation as validation.
