# Referee Concerns Checklist

## Core Claim

Supported claim:

```text
External structural disturbance is associated with increased low-acceleration rotation-curve residual scatter in the quality-selected SPARC audit sample.
```

Claims not made:

```text
The projection model is physically proven.
The projection score is uniquely selected over MOND/RAR-like baselines.
Distance, radius, and observability confounding are fully eliminated.
Dark matter, MOND, or RAR phenomenology is falsified.
Tau Core is proven.
```

## Likely Referee Concern: Label Cherry-Picking

Answer:

```text
Labels are residual-blind, source-backed, and documented row by row.
```

Relevant files:

```text
labeling_protocol.md
external_evidence_table.csv
external_evidence_table.md
```

## Likely Referee Concern: No Baselines

Answer:

```text
The same A/C labels are compared against Newtonian baryonic, MOND simple-mu, and empirical RAR residual scores.
```

Relevant files:

```text
baseline_score_comparisons.md
baseline_score_by_galaxy.csv
effect_size_appendix.md
```

Main interpretation:

```text
Newtonian baryonic is near non-informative by AUC, while projection and MOND/RAR-like low-acceleration scores separate A/C. This supports low-acceleration residual-disturbance phenomenology, not projection uniqueness.
```

## Likely Referee Concern: Distance / Radius / Observability Bias

Answer:

```text
Distance and radius imbalance are explicit limitations. Matched, stratified, regression, and observability summaries are reported transparently.
```

Relevant files:

```text
distance_stratified_control.md
scale_matched_stress.md
radius_control_stress.md
selection_observability_appendix.md
controlled_regression_appendix.md
```

Main interpretation:

```text
The signal remains directionally positive in several controls, but full observability control is not decisive. This is a limitation, not hidden.
```

## Likely Referee Concern: Effect Size

Answer:

```text
The fixed projection score has common-language AUC = 0.771. MOND/RAR-like scores have AUC about 0.72-0.73. Newtonian baryonic has AUC = 0.506.
```

Relevant files:

```text
effect_size_appendix.md
effect_size_summary.csv
```

## Likely Referee Concern: Inclination / Beam / Kinematic Systematics

Answer:

```text
The paper does not claim these are fully solved. The systematics appendix lists remaining risks and gives descriptive inclination-bin checks.
```

Relevant files:

```text
inclination_systematics_appendix.md
inclination_systematics_summary.csv
systematics_risk_counts.csv
```

## Likely Referee Concern: Reproducibility

Answer:

```text
The packet includes generation scripts, tables, figures, labels, and test commands. Raw SPARC rotmod inputs are not redistributed; `studies/sparc_residual_coherence_test_v01/download_sparc_data.py` fetches the public SPARC Zenodo archive into the local paths expected by the regeneration scripts.
```

Key commands:

```text
python studies/sparc_residual_coherence_test_v01/make_labeling_protocol_and_baselines.py
python studies/sparc_residual_coherence_test_v01/make_selection_and_regression_appendix.py
python studies/sparc_residual_coherence_test_v01/make_effect_size_and_systematics_appendix.py
python studies/sparc_residual_coherence_test_v01/make_manuscript_pdf.py
PYTHONPATH=src python -m pytest -q
```

## Likely Referee Concern: Independent Validation

Answer:

```text
Independent validation is not claimed in Paper 1. It is the explicit Phase II requirement.
```

Best next samples:

```text
WHISP
LITTLE THINGS
THINGS
LVHIS
```

Validation rule:

```text
freeze endpoint + freeze labels/proxies + freeze effect-size summaries before evaluating the external sample
```

## Submission Readiness

Remaining before submission:

```text
choose venue format
convert references to target style
decide main-text vs supplement table allocation
write cover-letter framing as phenomenological audit
freeze final commit hash
```
