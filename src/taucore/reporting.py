"""Markdown reporting helpers for Tau Core studies."""

from __future__ import annotations

import csv
import json
from pathlib import Path


def read_csv_rows(path: str | Path) -> list[dict[str, str]]:
    with Path(path).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def read_json(path: str | Path) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _fmt(value: object, digits: int = 4) -> str:
    if isinstance(value, float):
        return f"{value:.{digits}g}"
    try:
        return f"{float(str(value)):.{digits}g}"
    except (TypeError, ValueError):
        return str(value)


def render_sparc_pilot_markdown(
    stats: dict,
    control: dict,
    metric_rows: list[dict[str, str]],
    threshold_rows: list[dict[str, str]],
    figure_paths: list[str] | None = None,
    title: str = "SPARC Residual-Coherence Pilot v0.1 Summary",
    label_note: str = "Labels are currently machine-suggested residual-blind scaffolding, not final reviewed labels.",
) -> str:
    groups = {row["label"]: row for row in stats["groups"]}
    comparisons = {row["name"]: row for row in stats["binary_comparisons"]}
    control_comparisons = {
        row["name"]: row for row in control.get("quality_pass_comparisons", [])
    }
    c_minus_nonc = comparisons.get("C_minus_nonC", {})
    control_c_minus_nonc = control_comparisons.get("C_minus_nonC", {})
    positive_thresholds = [
        row for row in threshold_rows if row.get("c_minus_nonc_sign_positive") == "True"
    ]
    valid_thresholds = [
        row
        for row in threshold_rows
        if int(float(row.get("n_c", "0"))) > 0 and int(float(row.get("n_a", "0"))) + int(float(row.get("n_b", "0"))) > 0
    ]
    loo = control.get("quality_pass_c_minus_nonc_leave_one_out", [])
    sign_flips = [row for row in loo if not row.get("sign_preserved", False)]

    lines = [
        f"# {title}",
        "",
        "## Status",
        "",
        "This is an exploratory pilot summary generated from local outputs. It is not a final paper result.",
        "The current strongest claim is that low-coherence / disturbed candidates show larger TPG residual scatter than non-C galaxies.",
        "",
        "## Class Medians",
        "",
        "| Class | n | median RMS | median weighted RMS | median outer residual |",
        "|---|---:|---:|---:|---:|",
    ]

    for label in ("A", "B", "C"):
        row = groups.get(label)
        if row:
            lines.append(
                "| "
                f"{label} | {row['n']} | {_fmt(row['median_rms_log_tpg'])} | "
                f"{_fmt(row['median_weighted_rms_log_tpg'])} | "
                f"{_fmt(row['median_outer_mean_log_residual_tpg'])} |"
            )

    lines.extend(
        [
            "",
            "## Primary C-vs-nonC Result",
            "",
            "| Metric | Difference | one-sided p | 95% bootstrap CI |",
            "|---|---:|---:|---:|",
            "| RMS log TPG | "
            f"{_fmt(c_minus_nonc.get('median_difference_right_minus_left'))} | "
            f"{_fmt(c_minus_nonc.get('permutation_p_one_sided'))} | "
            f"[{_fmt(c_minus_nonc.get('bootstrap_ci95_low'))}, {_fmt(c_minus_nonc.get('bootstrap_ci95_high'))}] |",
            "",
            "## Quality-Control Subset",
            "",
            f"Quality-passed galaxies: {control.get('quality_passed')} / {control.get('total_matched')}.",
            "",
            "| Comparison | Difference | one-sided p | 95% bootstrap CI |",
            "|---|---:|---:|---:|",
            "| C minus non-C | "
            f"{_fmt(control_c_minus_nonc.get('median_difference_right_minus_left'))} | "
            f"{_fmt(control_c_minus_nonc.get('permutation_p_one_sided'))} | "
            f"[{_fmt(control_c_minus_nonc.get('bootstrap_ci95_low'))}, {_fmt(control_c_minus_nonc.get('bootstrap_ci95_high'))}] |",
            "",
            "## Robustness Checks",
            "",
            f"- Threshold sensitivity: {len(positive_thresholds)} / {len(valid_thresholds)} valid cells kept C-minus-nonC positive.",
            f"- Leave-one-out sign flips in quality-pass C-minus-nonC: {len(sign_flips)}.",
            "- Metric robustness summary:",
            "",
            "| Metric | Direction | C-minus-nonC diff | p | CI |",
            "|---|---|---:|---:|---:|",
        ]
    )

    for row in metric_rows:
        if row["comparison"] != "C_minus_nonC":
            continue
        lines.append(
            "| "
            f"{row['metric']} | {row['alternative']} | "
            f"{_fmt(row['median_diff_right_minus_left'])} | "
            f"{_fmt(row['perm_p_one_sided'])} | "
            f"[{_fmt(row['ci95_low'])}, {_fmt(row['ci95_high'])}] |"
        )

    lines.extend(
        [
            "",
            "## Claim Ladder",
            "",
            "1. Strongest current claim: C / low-coherence candidates have larger TPG residual scatter than non-C.",
            "2. Moderate claim: A / high-coherence candidates tend to have lower scatter than non-A.",
            "3. Weakest claim: strict A < B < C ordering. Do not promote this yet.",
            "",
            "## Limits",
            "",
            f"- {label_note}",
            "- The quality-pass C sample is small, so quality-cut results are suggestive rather than decisive.",
            "- A paper-level claim needs reviewed labels and an external or held-out proxy pass.",
        ]
    )

    if figure_paths:
        lines.extend(["", "## Figures", ""])
        for path in figure_paths:
            label = Path(path).stem.replace("_", " ")
            lines.append(f"- [{label}]({path})")

    return "\n".join(lines) + "\n"
