# Tau Core Specificity Map

This is a pre-specification scaffold for a Tau Core-vs-MOND/RAR discriminator. It compares pointwise absolute log residuals on the same quality-pass A/C galaxies.

Definition:

```text
delta_abs = abs(residual_projection_fixed) - abs(residual_comparator)
interaction = median(delta_abs | C, bin) - median(delta_abs | A, bin)
```

Negative `delta_abs` means the fixed low-acceleration residual score has smaller absolute residuals than the comparator in that bin. Positive `interaction` means the fixed score loses more ground in disturbed C rows than in regular A rows.

| Bin type | Bin | Comparator | n A pts | n C pts | median delta A | median delta C | interaction C-A | median delta all |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| acceleration | aN/a0<0.1 | MOND simple-mu | 157 | 303 | 0.0238476 | -0.0416805 | -0.0655281 | -0.0333922 |
| acceleration | aN/a0<0.1 | Empirical RAR | 157 | 303 | 0.0248166 | -0.0402755 | -0.0650921 | -0.0318476 |
| acceleration | 0.1<=aN/a0<0.3 | MOND simple-mu | 126 | 85 | 0.0124534 | -0.0134135 | -0.0258669 | 0.0016773 |
| acceleration | 0.1<=aN/a0<0.3 | Empirical RAR | 126 | 85 | 0.00830936 | -0.00955068 | -0.01786 | 0.00430625 |
| acceleration | 0.3<=aN/a0<1 | MOND simple-mu | 93 | 53 | -0.0122968 | -0.0127821 | -0.000485278 | -0.0124131 |
| acceleration | 0.3<=aN/a0<1 | Empirical RAR | 93 | 53 | -0.00645424 | -0.00654285 | -8.86078e-05 | -0.00648245 |
| acceleration | aN/a0>=1 | MOND simple-mu | 17 | 92 | -0.0185596 | -0.0164417 | 0.00211792 | -0.0171694 |
| acceleration | aN/a0>=1 | Empirical RAR | 17 | 92 | -0.00156962 | 0.00198203 | 0.00355165 | 0.00172143 |
| radius | inner_R<0.33Rmax | MOND simple-mu | 172 | 225 | -0.0122363 | -0.0159375 | -0.00370117 | -0.0129087 |
| radius | inner_R<0.33Rmax | Empirical RAR | 172 | 225 | 0.00319626 | -0.00203714 | -0.0052334 | -0.00143064 |
| radius | middle_0.33-0.67Rmax | MOND simple-mu | 105 | 149 | 0.0130667 | -0.0131298 | -0.0261965 | -0.0122109 |
| radius | middle_0.33-0.67Rmax | Empirical RAR | 105 | 149 | 0.00937641 | -0.00653777 | -0.0159142 | -0.0064438 |
| radius | outer_R>=0.67Rmax | MOND simple-mu | 116 | 159 | -0.0124207 | -0.0303973 | -0.0179766 | -0.0174546 |
| radius | outer_R>=0.67Rmax | Empirical RAR | 116 | 159 | -0.00785969 | -0.028563 | -0.0207033 | -0.0143205 |

Galaxy-aggregated companion summary, using each galaxy-bin median as one statistical unit:

| Bin type | Bin | Comparator | n A gal | n C gal | median delta A | median delta C | interaction C-A | median delta all |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| acceleration | 0.1<=aN/a0<0.3 | MOND simple-mu | 12 | 17 | 0.0131243 | -0.0133753 | -0.0264996 | 0.012676 |
| acceleration | 0.1<=aN/a0<0.3 | Empirical RAR | 12 | 17 | 0.00959513 | -0.00949116 | -0.0190863 | 0.0094143 |
| acceleration | 0.3<=aN/a0<1 | MOND simple-mu | 8 | 8 | -0.0122784 | -0.0128456 | -0.00056726 | -0.0124064 |
| acceleration | 0.3<=aN/a0<1 | Empirical RAR | 8 | 8 | -0.00656752 | -0.00651588 | 5.16438e-05 | -0.00652746 |
| acceleration | aN/a0<0.1 | MOND simple-mu | 14 | 24 | 0.022915 | -0.0100673 | -0.0329823 | 0.00944025 |
| acceleration | aN/a0<0.1 | Empirical RAR | 14 | 24 | 0.0233688 | -0.00934466 | -0.0327135 | 0.0104825 |
| acceleration | aN/a0>=1 | MOND simple-mu | 3 | 4 | -0.0190465 | -0.0186864 | 0.000360183 | -0.018802 |
| acceleration | aN/a0>=1 | Empirical RAR | 3 | 4 | -0.00532924 | -0.000621577 | 0.00470766 | -0.00226673 |
| radius | inner_R<0.33Rmax | MOND simple-mu | 17 | 28 | 0.011442 | -0.0155998 | -0.0270418 | -0.0126712 |
| radius | inner_R<0.33Rmax | Empirical RAR | 17 | 28 | 0.00664167 | -0.0064168 | -0.0130585 | -0.00389583 |
| radius | middle_0.33-0.67Rmax | MOND simple-mu | 17 | 28 | 0.012676 | -0.0126819 | -0.0253579 | 0.00277759 |
| radius | middle_0.33-0.67Rmax | Empirical RAR | 17 | 28 | 0.00839363 | -0.00388839 | -0.012282 | 0.00334565 |
| radius | outer_R>=0.67Rmax | MOND simple-mu | 17 | 28 | 0.00253498 | -0.0194991 | -0.0220341 | -0.0155949 |
| radius | outer_R>=0.67Rmax | Empirical RAR | 17 | 28 | 0.0027581 | -0.0149712 | -0.0177293 | -0.00967448 |

Reading guide: this table does not yet prove Tau Core specificity. It identifies where a future preregistered test should look for a different residual shape than MOND/RAR: acceleration bins, radius bins, and the A/C interaction of projection-vs-comparator residual differences.
