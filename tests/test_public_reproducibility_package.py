from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "studies/sparc_residual_coherence_test_v01/paper_packet_v06_distance_balanced"


def test_manuscript_referenced_paths_exist():
    required = [
        PACKET / "manuscript_draft.md",
        PACKET / "manuscript_draft.pdf",
        PACKET / "labeling_protocol.md",
        PACKET / "external_evidence_table.csv",
        PACKET / "final_tables.md",
        PACKET / "distance_stratified_control.md",
        PACKET / "scale_matched_stress.md",
        PACKET / "radius_control_stress.md",
        PACKET / "scale_mass_distance_control.md",
        PACKET / "baseline_score_comparisons.md",
        PACKET / "baseline_score_by_galaxy.csv",
        PACKET / "selection_observability_appendix.md",
        PACKET / "controlled_regression_appendix.md",
        PACKET / "effect_size_appendix.md",
        PACKET / "inclination_systematics_appendix.md",
        PACKET / "figures/quality_pass_rms_distribution.svg",
        PACKET / "figures/control_forest_plot.svg",
        PACKET / "figures/distance_stratified_effects.svg",
        ROOT / "outputs/external_proxy_v06_distance_balanced/sparc_residual_summary.csv",
        ROOT / "outputs/external_proxy_v06_distance_balanced/coherence_label_diagnostics.csv",
        ROOT / "outputs/hecate_crossmatch_summary.csv",
    ]
    missing = [str(path.relative_to(ROOT)) for path in required if not path.exists()]
    assert missing == []


def test_downloaded_sparc_inputs_when_present():
    rotmod_dir = ROOT / "data/sparc/Rotmod_LTG"
    table1 = ROOT / "data/external/SPARC_Table1.txt"
    if not rotmod_dir.exists() and not table1.exists():
        return
    assert table1.exists()
    assert len(list(rotmod_dir.glob("*_rotmod.dat"))) == 175


def test_public_package_is_english_only():
    assert not list(PACKET.glob("*_hu.*"))

    public_text = "\n".join(
        path.read_text(encoding="utf-8", errors="ignore")
        for path in [
            ROOT / "README.md",
            PACKET / "manuscript_draft.md",
            PACKET / "packet_manifest.json",
        ]
    )
    assert "_hu." not in public_text


def test_core_scripts_are_importable():
    import taucore.coherence  # noqa: F401
    import taucore.controls  # noqa: F401
    import taucore.figures  # noqa: F401
    import taucore.galaxy_activation  # noqa: F401
    import taucore.metadata  # noqa: F401
    import taucore.sparc  # noqa: F401
