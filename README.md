# SPARC Residual-Disturbance Paper 1

This repository is the public reproducibility package for:

**External structural disturbance predicts low-acceleration rotation-curve residual scatter in SPARC**

The package preserves the relative paths cited by the manuscript. The main paper packet is:

```text
studies/sparc_residual_coherence_test_v01/paper_packet_v06_distance_balanced
```

## Main Files

```text
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
data/sparc/Rotmod_LTG
data/external/SPARC_Table1.txt
outputs/external_proxy_v06_distance_balanced
outputs/hecate_crossmatch_summary.csv
studies/sparc_residual_coherence_test_v01/coherence_labels_v06_distance_balanced.csv
```

The SPARC rotmod files and SPARC Table1 metadata are included so the baseline-score and observability appendices can be regenerated from this repository without depending on the original development workspace.

## Reproduce The Packet

Create an environment with Python 3.10 or newer, then install the package in editable mode:

```bash
python -m pip install -e .
```

Regenerate the public manuscript packet:

```bash
python studies/sparc_residual_coherence_test_v01/make_labeling_protocol_and_baselines.py
python studies/sparc_residual_coherence_test_v01/make_selection_and_regression_appendix.py
python studies/sparc_residual_coherence_test_v01/make_effect_size_and_systematics_appendix.py
python studies/sparc_residual_coherence_test_v01/make_manuscript_pdf.py
PYTHONPATH=src python -m pytest -q
```

The commands write regenerated tables, figures, appendices, and the PDF into the same paths cited by the manuscript.

## Scope

This repository is a reproducibility package for Paper 1 only. It does not include private development notes or broader Tau Core theory work that is not required to reproduce the SPARC residual-disturbance audit.
