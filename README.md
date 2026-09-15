# SPARC Residual-Disturbance Paper 1

This repository is the public reproducibility package for:

**External structural disturbance is associated with increased low-acceleration residual scatter in SPARC galaxies: a residual-blind audit**

The package preserves the relative paths cited by the manuscript. The main paper packet is:

```text
studies/sparc_residual_coherence_test_v01/paper_packet_v06_distance_balanced
```

Archived reproducibility package DOI: [10.5281/zenodo.20285859](https://doi.org/10.5281/zenodo.20285859)

## Author And Research Workflow

I am an independent researcher using an AI-assisted workflow to develop reproducible diagnostic tests around projection-sensitive residual hypotheses. I am not claiming expert-level validation. I would value criticism on whether the proposed gate/falsification structure is scientifically meaningful.

AI systems are used for drafting, mathematical organization, code generation, literature triage, and internal consistency checks. Numerical and symbolic audits can support reproducibility and error-finding, but they do not replace independent expert review or physical validation.

## Theory Context

The broader Tau Core / projection-theory background is maintained separately at:

```text
https://github.com/tau-core-research/tau-core-theory
```

This Paper 1 repository is a standalone reproducibility package. It does not require accepting the Tau Core theory hub; the manuscript should be read as a residual-blind SPARC residual-disturbance audit.

The later observer-specific full-4D Tau descent changes neither the frozen
endpoint nor any reported statistic. It expands only the list of possible
upstream explanations of a terminal residual. No nonzero radial Tau coframe is
derived here, so the existing packet is not retrospectively reinterpreted or
rescored as a 4D-distortion detection.

Later negative routes constrain the finite morphology representations that
were actually frozen; they do not directly test a source-complete parent body.
This does not permit same-packet repair. Any refined representation must be
source-only, frozen before endpoint access, and tested on a new untouched
packet.

## Downstream Claim-Boundary Update

The original Paper 1 numbers remain a marginal or unconditional within-SPARC
association. A later Paper 3 repeated-cross-fitting audit found no stable
projection-specific predictive increment after endpoint-residual-free
observability/baryonic covariates and MOND/RAR-common residual structure were
supplied. This is a conditional predictive-increment result, not a literal
conditional-mutual-information estimate.

A separate source-frozen seven-galaxy EDGE-CALIFA rotation-morphology proxy
stress test also failed its directional gate: mean
`D=-0.058679293503004035`, exact one-sided `p=0.6015625`, median
`D=+0.11020194395988532`, and `4/7` positive values. It is an external
morphology-proxy stress test, not an independent Tau-specific test and not a
direct replication of the Paper 1 A/C endpoint. Conditional projection
specificity and independent matched-tracer replication therefore remain open.

Later Paper 8 public-data routes do not change that boundary. LITTLE THINGS
provides mixed one-family transfer in 14 galaxies; the PHANGS low-order routes
either satisfy the morphology-orthogonal null or fail wrong-family/source-label
specificity; and the higher-dimensional PHANGS confirmatory packet fails its
predeclared spatial-support gate without releasing a score. These are useful
negative or caveated transfer results, not a replication of the Paper 1 A/C
endpoint.

## Main Files

```text
LICENSE
CITATION.cff
requirements.txt
tests/
figures/
paper1_submission_source/main.tex
paper1_submission_source/main.pdf
paper1_submission_source/figures/
studies/sparc_residual_coherence_test_v01/paper_packet_v06_distance_balanced/manuscript_draft.md
studies/sparc_residual_coherence_test_v01/paper_packet_v06_distance_balanced/manuscript_draft.pdf
studies/sparc_residual_coherence_test_v01/paper_packet_v06_distance_balanced/labeling_protocol.md
studies/sparc_residual_coherence_test_v01/paper_packet_v06_distance_balanced/external_evidence_table.csv
studies/sparc_residual_coherence_test_v01/paper_packet_v06_distance_balanced/baseline_score_comparisons.md
studies/sparc_residual_coherence_test_v01/paper_packet_v06_distance_balanced/selection_observability_appendix.md
studies/sparc_residual_coherence_test_v01/paper_packet_v06_distance_balanced/controlled_regression_appendix.md
studies/sparc_residual_coherence_test_v01/paper_packet_v06_distance_balanced/effect_size_appendix.md
studies/sparc_residual_coherence_test_v01/paper_packet_v06_distance_balanced/inclination_systematics_appendix.md
```

## Included Data

```text
outputs/external_proxy_v06_distance_balanced
outputs/hecate_crossmatch_summary.csv
studies/sparc_residual_coherence_test_v01/coherence_labels_v06_distance_balanced.csv
```

The repository includes derived residual, control, and labeling artifacts. Raw SPARC rotmod files and SPARC Table1 metadata are not redistributed here; they can be downloaded into the expected local paths with the script below.

## Full-4D Score Boundary

The later compiler requires the source-frozen standard excess
`E_K = (K_HH - K_std) - C K_VV^-1 C^dagger`. Paper 1 does not reconstruct
this object, so none of its frozen SPARC statistics changes or becomes a
physical Tau score.

## Reproduce The Packet

Create an environment with Python 3.10 or newer, then install the package in editable mode:

```bash
python -m pip install -e .
```

Regenerate the public manuscript packet:

```bash
python studies/sparc_residual_coherence_test_v01/download_sparc_data.py
python studies/sparc_residual_coherence_test_v01/make_labeling_protocol_and_baselines.py
python studies/sparc_residual_coherence_test_v01/make_selection_and_regression_appendix.py
python studies/sparc_residual_coherence_test_v01/make_effect_size_and_systematics_appendix.py
python studies/sparc_residual_coherence_test_v01/make_manuscript_pdf.py
PYTHONPATH=src python -m pytest -q
```

The commands write regenerated tables, figures, appendices, and the PDF into the same paths cited by the manuscript.

## arXiv Source Package

Build a LaTeX source package for arXiv with:

```bash
python studies/sparc_residual_coherence_test_v01/make_arxiv_source.py
```

This writes:

```text
paper1_submission_source/main.tex
paper1_submission_source/main.pdf
paper1_submission_source/figures/
arxiv_submission_source.zip
```

The arXiv ZIP is built from `paper1_submission_source/` and excludes the compiled PDF and temporary LaTeX build files. The source directory keeps the same publication layout used by the Paper 2 and Paper 3 repositories. The PNG figure files are generated from the canonical SVG figures; the SVG figures remain in the repository and Zenodo package as vector source artifacts.

## Publication Hygiene

The repository is intended to be public. It excludes local caches, virtual environments, macOS metadata, raw SPARC downloads, SPARC Table1 metadata, and extracted SPARC rotmod files through `.gitignore`.

The tracked `outputs/` files are derived reproducibility artifacts used by the packet. Raw SPARC inputs are fetched on demand by `download_sparc_data.py` and should remain untracked.

## Scope

This repository is a reproducibility package for Paper 1 only. It does not include private development notes or broader Tau Core theory work that is not required to reproduce the SPARC residual-disturbance audit.

<!-- BEGIN OBSERVER UPDATE 20260914 -->
## Observer realization update (2026-09-14)

For galactic inference, these observer constructions do not derive a rotation-curve correction or identify a measured residual as a parent effect. Existing endpoint freezes and scores are unchanged.

The manuscript distinguishes inherited BRAC contact, conditional coherent-state
selection and interacting local covariance from physical observer identification,
preparation and stable resolution. Those physical claims remain open. No
empirical score was changed. The [dependency and source-result ledger](data/derived/observer_update_2026_09_14.json) records the assumptions and controls.
<!-- END OBSERVER UPDATE 20260914 -->
