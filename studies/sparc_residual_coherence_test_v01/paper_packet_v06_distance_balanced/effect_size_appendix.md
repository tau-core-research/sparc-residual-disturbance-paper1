# Effect-Size Appendix

The primary paper statistic is a median C-minus-A residual-scatter difference. This appendix translates the same A/C separation into scale-free effect-size and classification-sanity quantities. These are descriptive checks, not new primary endpoints.

Definitions:

```text
Cohen-like d      = median(C)-median(A) divided by pooled standard deviation
robust median d   = median(C)-median(A) divided by 1.4826 * pooled MAD
common-language AUC = P(rms_C > rms_A) + 0.5 P(tie)
Cliff's delta     = 2*AUC - 1
```

| score | n A | n C | C-A median diff | Cohen-like d | robust median d | AUC | AUC 95% CI | Cliff delta |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | ---: |
| Fixed low-acceleration residual score | 17 | 28 | 0.0842686 | 0.447033 | 0.93756 | 0.771008 | [0.621849, 0.915966] | 0.542017 |
| Newtonian baryonic | 17 | 28 | 0.0455866 | 0.174072 | 0.136256 | 0.506303 | [0.342437, 0.672269] | 0.012605 |
| MOND simple-mu | 17 | 28 | 0.118723 | 0.565345 | 1.23381 | 0.720588 | [0.556723, 0.867647] | 0.441176 |
| Empirical RAR | 17 | 28 | 0.110816 | 0.528266 | 1.22378 | 0.731092 | [0.565126, 0.871849] | 0.462185 |

Interpretation: the fixed low-acceleration residual score, MOND-like, and empirical RAR scores show moderate A/C separation by common-language AUC, while the Newtonian baryonic baseline is close to weak/non-informative in this sample. This supports the paper's restrained reading: the signal is tied to low-acceleration residual regularity, not uniquely to the projection formula.
