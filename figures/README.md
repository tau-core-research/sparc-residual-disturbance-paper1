# Figures

This directory mirrors manuscript figures and generated visual diagnostics used in the arXiv source package:

- `quality_pass_rms_distribution.svg`
- `control_forest_plot.svg`
- `distance_stratified_effects.svg`
- `projection_vs_mond_rotation_examples.png`

The three SVG figures are mirrored from the canonical packet copies under:

```text
studies/sparc_residual_coherence_test_v01/paper_packet_v06_distance_balanced/figures
```

The PNG diagnostic is regenerated directly from SPARC rotmod rows by:

```bash
python studies/sparc_residual_coherence_test_v01/make_arxiv_source.py
```

Regenerate the canonical packet figures and PDF with:

```bash
python studies/sparc_residual_coherence_test_v01/make_manuscript_pdf.py
```
