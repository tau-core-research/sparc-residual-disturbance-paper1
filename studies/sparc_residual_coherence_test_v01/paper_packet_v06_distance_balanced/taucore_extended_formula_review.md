# Tau Core Extended Formula Review

## Verdict

This note is an exploratory bridge document. It is included to document how the
fixed residual score relates to later coherence-gated variants, but it is not
part of the manuscript's primary endpoint and is not evidence for the main Paper
1 claim.

The current SPARC paper and the baseline/specificity maps still use the old high-coherence fixed projection score:

```text
F_proj(R) = 1 + alpha ln(1 + a0 / a_N(R))
V_model(R) = F_proj(R) V_bar(R)
```

In the manuscript implementation this is written as the `S_tau = 1` limit:

```text
F_tau(R) = 1 + S_tau alpha ln(1 + a0 / a_N(R))
S_tau = 1
```

The docs do not yet contain a closed, first-principles, fully extended Tau Core field equation that can replace the SPARC residual model without extra assumptions. What they do contain is a more general, operationally testable coherence-gated form:

```text
F_tau(a_N, S_tau) = 1 + S_tau alpha ln(1 + a0/a_N)
```

with `S_tau` interpreted as a collective tau-coherence order parameter rather than a fitted rescue parameter.

## Internal Source Trail

The broader Tau Core working notes that motivated this review are not part of
this public reproducibility repository. This file therefore records only the
operational statements needed to understand the packet-level comparison. The
relevant local packet files are:

```text
taucore_extended_formula_comparison.md
continuous_s_tau_protocol.md
continuous_s_tau_manifest.md
soft_s_tau_frozen_mapping.md
soft_s_tau_heldout_source_family_test.md
```

The key repeated statements are:

```text
S_tau = |sum_i w_i exp(i theta_i)| / sum_i w_i
F_tau(a_N,S_tau)=1+S_tau alpha ln(1+a0/a_N)
```

and the warning:

```text
S_tau is not a switch and not a free per-galaxy fit parameter.
```

## What Is Immediately Testable

The only extended formula that is currently clean enough to code is the coherence-gated operational candidate:

```text
V_tau(R) = [1 + S_tau(R) alpha ln(1 + a0/a_N(R))] V_bar(R)
```

The hard part is not the formula. The hard part is predefining `S_tau(R)` without looking at residuals.

Acceptable `S_tau` sources for a paper-grade test:

```text
external structural labels mapped to fixed S_tau values
published HI asymmetry / lopsidedness mapped by a frozen rule
regular-kinematic evidence mapped by a frozen rule
radial source evidence only if it is external and residual-blind
```

Not acceptable:

```text
choosing S_tau per galaxy to minimize residuals
tuning S_tau after seeing MOND/RAR comparisons
using TPG/Tau Core residuals to define the coherence score
```

## Candidate Frozen Variants

Variant A: class-gated constant `S_tau`.

```text
A -> S_tau = 1.0
B -> S_tau = 0.5
C -> S_tau = 0.0
```

This is easy to implement but scientifically dangerous for the current paper, because the same labels are also the endpoint grouping. It is best used as a sensitivity or illustration, not as primary proof.

Variant B: evidence-type-gated constant `S_tau`.

```text
regular_kinematics / low_asymmetry -> high S_tau
mixed / no_data / other -> intermediate or missing
disturbed_hi / tidal / interaction / warp -> low S_tau
```

This is closer to the protocol but still label-derived. It can test whether the broader Tau Core interpretation sharpens the residual score, but it must be secondary.

Variant C: radial external-coherence profile `S_tau(R)`.

```text
S_tau(R) = externally defined radial regularity/coherence profile
```

This is the most genuinely Tau Core-like SPARC discriminator, because the extended docs explicitly say different radial `S_tau(R)` profiles alter rotation-curve predictions. It is not currently ready because the packet does not yet contain residual-blind radial coherence profiles.

## Best Next Paper-Grade Path

Do not retrofit the full Tau Core claim into Paper 1. Instead:

1. Keep Paper 1 on the fixed `S_tau = 1` projection endpoint and external residual-coherence audit.
2. Use the current specificity map to motivate Paper 2.
3. For Paper 2, freeze a coherence-gated endpoint before looking at new residual outputs:

```text
primary_model = F_tau(a_N, S_tau_external)
primary_contrast = residual_shape_vs_MOND_RAR
primary_bins = low acceleration + outer radius
primary_statistic = projection-vs-comparator absolute-residual interaction by A/C class
```

4. Prefer an independent or held-out validation sample for the first real `S_tau(R)` test.

## Old TPG vs Naive Extended Formula Result

The packet now includes a first operational comparison:

```text
taucore_extended_formula_comparison.md
taucore_extended_formula_comparison.csv
```

The naive class/evidence-gated variants are not better global residual models in the current SPARC packet. They increase A/C separation because C rows are pushed toward the Newtonian baseline, but their median rms-log residual is worse than the old high-coherence projection score:

```text
old fixed projection, all classes median rms-log = 0.165637
class-gated S_tau, all classes median rms-log = 0.342143
evidence-gated S_tau, all classes median rms-log = 0.342143
continuous external S_tau, all classes median rms-log = 0.308866
soft-calibrated S_tau, all classes median rms-log = 0.193527
```

This is useful rather than disappointing. It says the simple rule `disturbed -> S_tau = 0` is too blunt, and that the first direct continuous external proxy is still too suppressive even after direct VizieR catalog matches are used. The soft-calibrated version is much closer to the old high-coherence TPG limit but still does not beat it. If the extended Tau Core formula is to outperform the old high-coherence TPG limit, `S_tau` probably cannot be only a galaxy-level A/B/C switch. It needs either:

```text
radial S_tau(R),
better-calibrated continuous source-backed coherence values,
or a held-out/independent rule that does not reuse the same A/C labels as the proof target.
```

The most promising immediate variant is therefore the soft-calibrated mapping, not the hard or direct mapping. It should be frozen and then tested with a held-out source-family rule before being treated as evidence.

## Held-Out Source-Family Result

The soft mapping is now frozen in:

```text
soft_s_tau_frozen_mapping.md
```

and tested in:

```text
soft_s_tau_heldout_source_family_test.md
```

The source-family split is WHISP versus global Reynolds/Yu. Current overlap is small:

```text
overlap galaxies = 7
Pearson correlation = -0.365438
Spearman correlation = -0.180187
```

This is not a validation of the soft mapping. It is a useful blocker-clearing result: the current WHISP and global-source `S_tau` estimates do not yet agree well enough to call the continuous mapping paper-grade. The global-family subset gives a small C-class residual improvement relative to old TPG, but the support is only four C galaxies, so it should be treated as hypothesis-generating.

Next requirement:

```text
increase source-family overlap,
or define a radial WHISP-only S_tau(R) endpoint,
or validate on an independent sample with frozen mapping constants.
```

## Plain-Language Meaning

The present work is not yet using a full extended Tau Core model. It is using the high-coherence limit. The next upgrade is not to invent a larger equation inside the paper, but to make `S_tau` operational: define it from external, residual-blind coherence evidence and test whether that changes the residual shape relative to MOND/RAR.
