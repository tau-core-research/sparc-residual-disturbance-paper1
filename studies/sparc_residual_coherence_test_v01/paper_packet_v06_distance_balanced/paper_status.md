# SPARC v0.6 Paper Status

## Current Status

Paper 1 is closed as a statistical/methodological short paper candidate. The frozen claim is a reproducible residual-disturbance audit in SPARC, not a physical-theory proof and not a unique validation of the projection formula. The exploratory `S_tau` extensions remain packet material for follow-up work only.

## What Is Strong

- Fixed quality-pass C-minus-A primary endpoint strengthened relative to v0.5.
- Primary v0.6 effect = 0.08427, p = 0.00100, bootstrap 95% CI [0.04481, 0.15990].
- Greedy distance-matched control improved to effect = 0.08247, p = 0.03360.
- Optimal ordered distance-matched control improved to effect = 0.08247, p = 0.03610.
- Distance-stratified within-bin control is positive in every bin and combined p = 0.00940.
- A/C leave-one-out sign flips remain zero.
- Radius common-support and greedy radius-matched controls preserve the signal.
- Separate `labeling_protocol.md` and row-level `external_evidence_table.csv` are now in the packet.
- Alternative baseline-score checks are now in the packet: Newtonian baryonic is not significant, while MOND simple-mu and empirical RAR show compatible positive disturbance sensitivity.
- A Tau Core specificity-map scaffold is now in the packet. It compares projection-vs-MOND/RAR absolute residual differences by acceleration bin, radius bin, and A/C class, both pointwise and galaxy-aggregated.
- `taucore_extended_formula_review.md` now separates the current high-coherence TPG/projection score from the only currently code-ready extended Tau Core candidate, the externally defined `S_tau`-gated formula.
- `taucore_extended_formula_comparison.md` now compares old high-coherence TPG against naive class/evidence-gated `S_tau` variants. The naive variants increase A/C separation but worsen global residual scatter, so they are not a paper-grade improvement.
- `download_s_tau_sources.py` downloads WHISP, Reynolds+2020, Yu+2022/ALFALFA, and WHISP merger morphology tables from VizieR. Current coverage is 33/73 quality-pass galaxies with direct source matches.
- `continuous_s_tau_manifest.md` and `continuous_s_tau_protocol.md` now define direct and soft-calibrated residual-blind continuous `S_tau` candidates from downloaded external asymmetry/evidence fields. The soft-calibrated version is much closer to old TPG performance but still does not beat it in global residual scatter.
- `soft_s_tau_frozen_mapping.md` freezes the current soft mapping. `soft_s_tau_heldout_source_family_test.md` runs a WHISP-vs-Reynolds/Yu held-out source-family sanity check.
- `selection_observability_appendix.md` and `controlled_regression_appendix.md` explicitly document the main selection-function/observability risk.
- `effect_size_appendix.md` translates the primary separation into AUC / Cliff's delta / robust median effect-size language.
- `inclination_systematics_appendix.md` documents inclination-bin behavior and remaining beam-smearing, asymmetric-drift, pressure-support, and non-circular-motion vulnerabilities.
- `referee_concerns_checklist.md` maps likely referee objections to packet files and restrained answers.
- `venue_fit_notes.md` records the recommended submission framing and plausible venue shapes.

## Remaining Reviewer Risks

- Raw A/C distance imbalance remains visible: p = 0.02490.
- Strict <=2 Mpc distance caliper is positive but still not decisive: p = 0.08979.
- Max-radius imbalance remains visible: p = 0.00190.
- Strict <=2 kpc radius caliper is positive but not significant: p = 0.10969.
- HECATE mass controls are supportive but coverage is incomplete.
- Robust nested regression is positive in class-only and distance-only specifications, but weakens when distance, radius, and observability proxies are included jointly. This is a limitation, not a blocker, because Paper 1 is scoped as an audit rather than a physical detection.
- Homogeneous beam-size / physical HI-resolution metadata are still missing, so beam smearing and velocity-field systematics are discussed but not fully controlled.
- Independent validation is not claimed. Phase II should freeze the endpoint and labeling/proxy rule before testing WHISP, LITTLE THINGS, THINGS, or LVHIS.
- MOND/RAR-like baselines also separate A/C, so the paper should not claim the projection formula is uniquely selected by this audit.
- The specificity map is exploratory until frozen as a separate endpoint with galaxy-level uncertainty and an explicit independent validation rule.
- The held-out source-family test is not yet validating: WHISP/global overlap is only seven galaxies and cross-family `S_tau` agreement is weak.

## Recommended Claim

Externally disturbed SPARC galaxies show larger fixed-score residual scatter than externally regular disks under residual-blind labeling, and the direction persists under distance-matched and distance-stratified controls. Baseline comparisons should be reported transparently: the result is a residual-disturbance association, not a uniqueness proof for the projection formula.

## Claim To Avoid

Do not claim that the projection model is physically proven or uniquely correct. Do not claim that distance and radius confounding are fully eliminated. The right wording is mitigated, stress-tested, direction-preserving, and statistically/methodologically positive.

## Tau Core Specificity Lead

The strongest next discriminator is not another raw A/C residual test. It is a residual-shape test:

```text
delta_abs = abs(residual_projection_fixed) - abs(residual_MOND_or_RAR)
interaction = median(delta_abs | C, bin) - median(delta_abs | A, bin)
```

The current exploratory map points to low-acceleration and outer-radius bins as promising places to freeze a Tau Core-vs-MOND/RAR comparison. Negative C-class deltas mean the projection score has smaller absolute residuals than the comparator in disturbed rows. This should be handled as Paper 2 / preregistered validation material, not as a new primary claim in Paper 1.

## Extended Formula Status

The docs do not yet contain a closed full Tau Core field equation for SPARC rotation curves. The code-ready extension is:

```text
F_tau(a_N, S_tau) = 1 + S_tau alpha ln(1 + a0/a_N)
```

The current paper uses the high-coherence limit `S_tau = 1`. A true extended Tau Core SPARC test requires `S_tau` or `S_tau(R)` to be defined externally and residual-blind, then frozen before comparison to MOND/RAR.

The first naive operational test is informative: class/evidence-gated `S_tau` pushes C galaxies toward Newtonian behavior, making A/C separation much larger but also increasing global rms-log residuals. The direct continuous external `S_tau` is less blunt but still too suppressive. The soft-calibrated mapping is the current best candidate, with all-class median rms-log 0.193527 versus 0.165637 for old TPG. This argues against using galaxy-level A/B/C as the extended formula itself. The next serious version should freeze the soft mapping and test it with held-out source families or true radial external coherence evidence.

Held-out source-family status: current overlap is too small and agreement is weak (`n=7`, Spearman = -0.180187). This blocks any claim that the continuous `S_tau` mapping is paper-grade. The next pass should expand source overlap or switch to a WHISP-only radial endpoint.

## Alpha-Origin Reference

The broader alpha-origin audit is not included in this public Paper 1 repository because it is not needed to reproduce the SPARC residual-disturbance result. The useful packet-level statement is narrower: `alpha = 0.360` is a pre-frozen operational constant in this audit. A suggestive Planck-ratio route exists outside this reproducibility package, but the factor of two and a clean first-principles derivation remain open. The SPARC paper should therefore treat `alpha` as fixed before the residual-blind audit, not as a fitted parameter and not as a completed theoretical derivation.

## Closeout Decision

Paper 1 should freeze on the high-coherence fixed projection endpoint:

```text
F_proj(a_N) = 1 + alpha ln(1 + a0/a_N)
```

The supported Paper 1 claim is residual-coherence, not Tau Core uniqueness:

```text
externally disturbed SPARC galaxies show larger fixed-score residual scatter than externally regular disks under residual-blind labeling, with distance/radius controls and transparent alternative baselines.
```

The `S_tau` material stays in the packet as an exploratory bridge to Paper 2. It should not be promoted into the Paper 1 abstract, primary result, or conclusion as evidence for the extended formula.

## Final Closeout State

Paper 1 is ready to freeze for handoff/review in its current scope. Do not add new Paper 1 endpoints. Further work should move to the Paper 1 companion model note or to the separate SPARC follow-up pilot for radial `S_tau(R)`.

The Phase II validation plan is now part of the paper framing: reproduce the residual-disturbance separation in independent resolved-HI samples or treat the present result as SPARC-specific / observability-driven.
