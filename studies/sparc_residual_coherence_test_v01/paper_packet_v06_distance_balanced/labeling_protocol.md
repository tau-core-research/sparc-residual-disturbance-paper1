# Labeling Protocol

## Scope

This protocol documents the residual-blind external evidence labels used by the v0.6 distance-balanced SPARC paper packet. It is a paper-facing extraction of the locked v0.5 review protocol plus the v0.6 blocker-resolution pass.

## Eligible Sample

Only SPARC rows passing the fixed quality gate enter the primary paper tables:

```text
n_points >= 8
mean_err_vobs_kms <= 6
30 <= inclination_deg <= 85
inclination_error_deg <= 10
```

The quality variables define sample eligibility and were allowed in reviewer workbooks. TPG/projection residual summaries, class medians, p-values, and prior exploratory labels were not allowed as labeling evidence.

## Label Definitions

```text
A = externally supported regular/calm disk
B = ambiguous, incomplete, mixed, weak, or only indirectly supported
C = externally supported disturbed/low-coherence system
```

Ambiguous rows default to B. A/C rows require direct source-backed evidence rather than environment-only or rotation-curve-quality-only arguments.

## Accepted Evidence

A evidence includes explicit regular or symmetric HI/Halpha velocity fields, well-defined symmetric rotation curves, low HI asymmetry, negligible non-circular motion, or isolated/undisturbed context used only as supporting evidence.

C evidence includes tidal streams, mergers/interactions, accretion evidence, disturbed HI morphology, warp tied to gas morphology or kinematics, lopsided HI or velocity fields, resolved HI asymmetry, or companion/flyby evidence tied to morphology or kinematics.

## Reviewer and Blinding Controls

Two residual-blind workbook passes were reconciled into accepted decisions. Agreement rows were accepted directly; weak A/C calls without direct evidence were downgraded to B. The v0.5 blinding audit found no residual metric or prior-label leakage in reviewer-facing artifacts. The v0.6 pass was then used to resolve the distance/radius blocker while preserving the same residual-blind evidence standard.

## Paper Packet Artifacts

The row-level evidence table is `external_evidence_table.csv`; a compact Markdown rendering is `external_evidence_table.md`. The source protocol lineage is preserved in `external_proxy_paper_grade_protocol_v05.md`, `external_proxy_review_v05_blinding_audit.md`, and `external_proxy_review_v05_agreement_report.json`.
