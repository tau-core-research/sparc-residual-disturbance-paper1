# Continuous / Held-Out S_tau Protocol Draft

## Goal

Define a more serious Tau Core extension than the naive A/B/C switch:

```text
F_tau(a_N, S_tau) = 1 + S_tau alpha ln(1 + a0/a_N)
```

The purpose is to compare the old high-coherence TPG limit (`S_tau=1`) against an externally defined continuous coherence parameter.

## Non-Negotiable Rule

`S_tau` must be defined without using residuals, score values, p-values, class medians, or any Tau Core/MOND/RAR comparison output.

## Current Candidate

The current manifest uses source-backed external evidence:

```text
Reynolds Amap/Avel low-asymmetry proxies
Yu+2022 ALFALFA Af/Ac global HI profile asymmetry
WHISP resolved HI morphology asymmetry A
evidence-type fallback for rows without quantitative proxies
```

The manifest carries two versions:

```text
S_tau_continuous      = direct monotone mapping, useful as a stress test
S_tau_soft_calibrated = conservative mapping constrained to [0.55, 0.95]
```

The numeric mapping is intentionally monotone:

```text
lower asymmetry -> higher S_tau
higher disturbance -> lower S_tau, but the soft-calibrated version does not switch off the response
ambiguous/no-data -> S_tau near 0.5
```

## Held-Out Source-Family Test

For the next paper-grade pass, use source families instead of tuning on the same evidence:

```text
train/freeze mapping family A: Reynolds + Yu global asymmetry
test family B: WHISP resolved HI morphology

or

train/freeze mapping family A: WHISP morphology
test family B: Reynolds/Yu global asymmetry
```

The statistic should be computed only after choosing the family split and mapping constants.

## Why This Is Better Than A/B/C Switching

The naive rule `A=1, B=0.5, C=0` reuses the endpoint grouping as the model input and pushes disturbed galaxies toward the Newtonian baseline. It increases A/C separation but worsens global residual scatter. A continuous source-backed score can be tested as a physical covariate rather than as a hard label switch.

## Held-Out Rule

For a paper-grade test, one of the following must be used:

```text
1. Train/freeze the S_tau mapping on one source family and test on another.
2. Freeze the mapping on current SPARC labels and evaluate on an independent validation sample.
3. Use numeric proxies only for S_tau and reserve A/C labels only for evaluation.
```

The current manifest is a scaffold. It should not be treated as proof until one of these held-out rules is applied.

## Preferred Next Endpoint

```text
primary_model = F_tau(a_N, S_tau_continuous_external)
primary_comparator = old fixed projection plus MOND/RAR
primary_statistic = galaxy-level paired residual improvement and residual-shape interaction
primary_validation = held-out evidence family or independent sample
```
