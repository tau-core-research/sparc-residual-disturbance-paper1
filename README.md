# SPARC Residual-Disturbance Paper 1

This repository is the public reproducibility package for:

**External structural disturbance is associated with increased low-acceleration residual scatter in SPARC galaxies: a residual-blind audit**

The package preserves the relative paths cited by the manuscript. The main paper packet is:

```text
studies/sparc_residual_coherence_test_v01/paper_packet_v06_distance_balanced
```

Archived reproducibility package DOI: [10.5281/zenodo.20183485](https://doi.org/10.5281/zenodo.20183485)

## Theory Context

The broader Tau Core / projection-theory background is maintained separately at:

```text
https://github.com/tau-core-research/tau-core-theory
```

This Paper 1 repository is a standalone reproducibility package. It does not require accepting the Tau Core theory hub; the manuscript should be read as a residual-blind SPARC residual-disturbance audit.

## Main Files

```text
LICENSE
CITATION.cff
requirements.txt
tests/
figures/
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
arxiv/main.tex
arxiv/figures/
arxiv_submission_source.zip
```

The arXiv source package uses PNG figure files generated from the canonical SVG figures. The SVG figures remain in the repository and Zenodo package as vector source artifacts.

## Publication Hygiene

The repository is intended to be public. It excludes local caches, virtual environments, macOS metadata, raw SPARC downloads, SPARC Table1 metadata, and extracted SPARC rotmod files through `.gitignore`.

The tracked `outputs/` files are derived reproducibility artifacts used by the packet. Raw SPARC inputs are fetched on demand by `download_sparc_data.py` and should remain untracked.

## Scope

This repository is a reproducibility package for Paper 1 only. It does not include private development notes or broader Tau Core theory work that is not required to reproduce the SPARC residual-disturbance audit.
