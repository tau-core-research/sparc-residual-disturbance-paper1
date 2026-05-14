# SPARC Residual-Coherence External Proxy v0.6 Distance-Balanced Summary

## Status

This is an exploratory pilot summary generated from local outputs. It is not a final paper result.
The pilot-level observation is that low-coherence / disturbed candidates tend to show larger fixed-score residual scatter than non-C galaxies. The paper-level claim is based on the later residual-blind A/C quality-selected packet, not on this pilot summary.

## Class Medians

| Class | n | median RMS | median weighted RMS | median outer residual |
|---|---:|---:|---:|---:|
| A | 19 | 0.1244 | 0.09799 | 0.00928 |
| B | 103 | 0.1705 | 0.1608 | -0.0005278 |
| C | 53 | 0.1945 | 0.1981 | -0.02873 |

## Primary C-vs-nonC Result

| Metric | Difference | one-sided p | 95% bootstrap CI |
|---|---:|---:|---:|
| RMS log TPG | 0.04333 | 0.08929 | [-0.009469, 0.08359] |

## Quality-Control Subset

Quality-passed galaxies: 73 / 175.

| Comparison | Difference | one-sided p | 95% bootstrap CI |
|---|---:|---:|---:|
| C minus non-C | 0.06998 | 0.0173 | [0.02276, 0.1417] |

## Robustness Checks

- Threshold sensitivity: 12 / 12 valid cells kept C-minus-nonC positive.
- Leave-one-out sign flips in quality-pass C-minus-nonC: 0.
- Metric robustness summary:

| Metric | Direction | C-minus-nonC diff | p | CI |
|---|---|---:|---:|---:|
| rms_log_tpg | greater | 0.04333 | 0.08929 | [-0.009469, 0.08359] |
| weighted_rms_log_tpg | greater | 0.05962 | 0.0234 | [0.0004935, 0.09688] |
| outer_mean_log_residual_tpg | less | -0.03091 | 0.08989 | [-0.09224, 0.03447] |

## Claim Ladder

1. Pilot-level observation: C / low-coherence candidates tend to have larger fixed-score residual scatter than non-C.
2. Moderate claim: A / high-coherence candidates tend to have lower scatter than non-A.
3. Weakest claim: strict A < B < C ordering. Do not promote this yet.

## Limits

- Labels use v0.5 preregistered labels with residual-blind v0.6 distance-balanced review overlays frozen before this residual audit.
- The quality-pass C sample is small, so quality-cut results are suggestive rather than decisive.
- A paper-level claim needs reviewed labels and an external or held-out proxy pass.

## Figures

- [class rms scatter](figures/class_rms_scatter.svg)
- [class weighted rms scatter](figures/class_weighted_rms_scatter.svg)
- [threshold sensitivity](figures/threshold_sensitivity.svg)
