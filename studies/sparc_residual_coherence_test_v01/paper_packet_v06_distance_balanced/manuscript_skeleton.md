# Manuscript Skeleton: SPARC Residual-Coherence v0.6

## Title

External structural disturbance predicts larger residual scatter in a fixed SPARC rotation-curve residual score

## Abstract Draft

We test whether externally reviewed structural-disturbance labels separate scatter under a fixed SPARC rotation-curve residual score. Labels were assigned from source-backed external evidence under residual blinding, frozen before residual audit, and documented in a separate labeling protocol plus row-level external evidence table. The fixed primary endpoint compares quality-pass C galaxies against quality-pass A galaxies using the median rms-log residual scatter. In v0.6, the primary C-minus-A difference is 0.08427, with one-sided permutation p = 0.00100 and bootstrap 95% CI [0.04481, 0.15990]. Distance-matched controls improve materially relative to v0.5, and a distance-stratified within-bin permutation test remains positive (effect = 0.07374, p = 0.00940). Alternative baseline-score comparisons show that the Newtonian baryonic score is not a sharp separator, while MOND-like/RAR scores show compatible disturbance sensitivity; the claim is therefore not uniqueness of the projection formula.

## Claim Discipline

Allowed primary claim:

```text
In a residual-blind, externally reviewed SPARC quality-pass audit, externally disturbed galaxies show larger fixed-score residual scatter than externally regular disks, and the direction persists under distance-matched and distance-stratified controls.
```

Not allowed:

```text
A complete physical theory is proven.
The fixed residual model is generally confirmed.
Distance and radius confounding are fully eliminated.
The v0.4 exploratory result is primary evidence.
The result is a physical proof of the projection model.
```

## Sections

1. Motivation and falsifiable endpoint
2. SPARC data and fixed quality gate
3. Labeling protocol and external evidence table
4. Frozen primary test and v0.6 distance-balanced review
5. Primary result: quality-pass C minus A
6. Distance, radius, and mass stress controls
7. Alternative baseline-score comparisons
8. Interpretation
9. Limitations and independent replication plan

## Relation To The Broader Program

The tested prescription may be described as motivated by a broader projection-based theoretical program, but the manuscript should evaluate it only as a fixed, reproducible residual model. The SPARC paper is therefore the empirical first step, not the full theory paper.

## Key Reviewer Risks To Address

The result is publishable only as a statistical/methodological audit unless these risks are made explicit:

```text
the logarithmic formula and alpha = 0.360 may have theoretical motivation, but this audit should not depend on reviewers accepting that derivation
external labeling may be partly subjective, so the separate reviewer/adjudication protocol and evidence table must stay visible
the A/C distance imbalance is physically dangerous because nearer galaxies reveal more disturbance and substructure
C-class non-equilibrium or non-circular systems may make any smooth axisymmetric score worse
baseline comparisons show compatible MOND/RAR-like sensitivity, so do not claim projection-score uniqueness
```

Alpha-origin note:

```text
The alpha-origin audit is not part of this public Paper 1 reproducibility repository. The manuscript should treat alpha = 0.360 as a pre-frozen operational constant, not as a fitted parameter and not as a completed first-principles derivation. Keep any deeper alpha-origin discussion for a separate model note or Paper 2.
```

## Results Spine

Primary result:

```text
quality-pass C-minus-A
nA = 17
nC = 28
median A = 0.12436
median C = 0.20862
median difference = 0.08427
one-sided permutation p = 0.00100
bootstrap 95% CI = [0.04481, 0.15990]
```

Supportive checks:

```text
quality-pass C-minus-nonC remains positive: p = 0.0173
quality-pass A-to-B-to-C trend: rho = 0.3620, p = 0.00110
A/C leave-one-out sign flips = 0
common radius-support C-minus-A: p = 0.00090
greedy radius-matched pairs: p = 0.01020
```

Baseline-score checks:

```text
fixed projection C-minus-A = 0.08427, p = 0.00210
Newtonian baryonic C-minus-A = 0.04559, p = 0.39546
MOND simple-mu C-minus-A = 0.11872, p = 0.00190
empirical RAR C-minus-A = 0.11082, p = 0.00210
```

Distance controls:

```text
SPARC distance imbalance improved but remains visible: p = 0.02490
greedy distance-matched C-minus-A: effect = 0.08247, p = 0.03360
optimal ordered distance-matched C-minus-A: effect = 0.08247, p = 0.03610
strict <=2 Mpc distance caliper remains positive but not decisive: effect = 0.11949, p = 0.08979
distance-stratified within-bin control: effect = 0.07374, p = 0.00940
```

Distance-bin directionality:

```text
0-5 Mpc: C-A = 0.07409
5-10 Mpc: C-A = 0.06147
10-20 Mpc: C-A = 0.08512
>20 Mpc: C-A = 0.06361
```

Scale and radius sensitivity:

```text
max-radius imbalance remains visible: p = 0.00190
radius common-support and greedy radius-matched controls preserve the signal
strict <=2 kpc radius caliper remains positive but not significant: p = 0.10969
HECATE mass-matched paired C-minus-A is positive in available coverage: p = 0.01220
optimal ordered HECATE mass-matched paired C-minus-A is also positive: p = 0.01440
HECATE mass coverage is incomplete and must not be promoted as a primary control
```

## Limitation Paragraph Draft

The main v0.5 limitation was scale sensitivity: quality-pass C galaxies were closer and smaller in radius than quality-pass A galaxies. The v0.6 distance-balanced review mitigates this concern but does not erase it. The primary C-minus-A signal strengthens, distance-matched paired controls become positive and nominally significant, and the direction is positive within every SPARC distance bin. However, the raw A/C distance imbalance remains statistically visible, and strict small-caliper controls have limited support. We therefore treat v0.6 as a paper-grade candidate result with a substantially mitigated distance blocker, while reserving a final broad discovery claim for independent external replication or a larger distance-balanced sample.

## Submission Readiness

```text
result readiness = paper-grade candidate
methods/audit readiness = strong
reproducibility readiness = strong
figure readiness = draft
manuscript readiness = full-draft-ready skeleton
main reviewer risk = residual distance/radius imbalance and strict-caliper small-n support
recommended submission status = close to submit-ready, but polish limitations and figures first
```

## Minimum Figure Set

- `figures/primary_c_minus_a.svg`
- `figures/review_gate_flow.svg`
- `outputs/external_proxy_v06_distance_balanced/figures/class_rms_scatter.svg`
- `outputs/external_proxy_v06_distance_balanced/figures/threshold_sensitivity.svg`
