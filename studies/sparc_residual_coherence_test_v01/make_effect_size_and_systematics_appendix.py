#!/usr/bin/env python3
"""Build effect-size and systematics appendices for the SPARC Paper 1 packet."""

from __future__ import annotations

import csv
import math
import random
import statistics
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from taucore.coherence import read_coherence_labels, read_residual_summary
from taucore.controls import QualityThresholds, join_control_rows, passes_quality, read_diagnostics


STUDY = ROOT / "studies/sparc_residual_coherence_test_v01"
PACKET = STUDY / "paper_packet_v06_distance_balanced"
OUTPUTS = ROOT / "outputs/external_proxy_v06_distance_balanced"
LABELS = STUDY / "coherence_labels_v06_distance_balanced.csv"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, object]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def median(values: list[float]) -> float:
    return statistics.median(values) if values else math.nan


def mad(values: list[float]) -> float:
    if not values:
        return math.nan
    med = median(values)
    return median([abs(value - med) for value in values])


def pooled_sd(a: list[float], c: list[float]) -> float:
    if len(a) < 2 or len(c) < 2:
        return math.nan
    var_a = statistics.variance(a)
    var_c = statistics.variance(c)
    return math.sqrt(((len(a) - 1) * var_a + (len(c) - 1) * var_c) / (len(a) + len(c) - 2))


def auc_common_language(a: list[float], c: list[float]) -> float:
    wins = 0.0
    total = 0
    for cv in c:
        for av in a:
            total += 1
            if cv > av:
                wins += 1.0
            elif cv == av:
                wins += 0.5
    return wins / total if total else math.nan


def cliff_delta(a: list[float], c: list[float]) -> float:
    auc = auc_common_language(a, c)
    return 2.0 * auc - 1.0 if math.isfinite(auc) else math.nan


def bootstrap_metric(
    a: list[float],
    c: list[float],
    metric,
    seed: int,
    iterations: int = 5000,
) -> tuple[float, float]:
    rng = random.Random(seed)
    values = []
    for _ in range(iterations):
        aa = [rng.choice(a) for _ in a]
        cc = [rng.choice(c) for _ in c]
        values.append(metric(aa, cc))
    values.sort()
    return values[int(0.025 * iterations)], values[int(0.975 * iterations)]


def score_values() -> dict[str, dict[str, list[float]]]:
    grouped: dict[str, dict[str, list[float]]] = {}
    for row in read_csv(PACKET / "baseline_score_by_galaxy.csv"):
        score = row["Score"]
        klass = row["Class"]
        if klass not in {"A", "C"}:
            continue
        grouped.setdefault(score, {}).setdefault(klass, []).append(float(row["RmsLog"]))
    return grouped


def make_effect_size_appendix() -> None:
    labels = {
        "projection_fixed": "Fixed projection score",
        "newtonian_baryonic": "Newtonian baryonic",
        "mond_simple_mu": "MOND simple-mu",
        "rar_mcgaugh": "Empirical RAR",
    }
    rows = []
    for idx, (score, by_class) in enumerate(score_values().items()):
        if score not in labels or "A" not in by_class or "C" not in by_class:
            continue
        a = by_class["A"]
        c = by_class["C"]
        diff = median(c) - median(a)
        psd = pooled_sd(a, c)
        pooled_mad = mad(a + c)
        robust_d = diff / (1.4826 * pooled_mad) if pooled_mad > 0 else math.nan
        cohen_like = diff / psd if psd > 0 else math.nan
        auc = auc_common_language(a, c)
        cliffs = cliff_delta(a, c)
        auc_low, auc_high = bootstrap_metric(a, c, auc_common_language, seed=20260514 + idx)
        rows.append(
            {
                "Score": score,
                "Description": labels[score],
                "N_A": len(a),
                "N_C": len(c),
                "Median_A": f"{median(a):.6g}",
                "Median_C": f"{median(c):.6g}",
                "MedianDiff_C_minus_A": f"{diff:.6g}",
                "CohenLikeD": f"{cohen_like:.6g}",
                "RobustMedianD": f"{robust_d:.6g}",
                "CommonLanguageAUC": f"{auc:.6g}",
                "AUC_CI95Low": f"{auc_low:.6g}",
                "AUC_CI95High": f"{auc_high:.6g}",
                "CliffsDelta": f"{cliffs:.6g}",
            }
        )
    order = {"projection_fixed": 0, "newtonian_baryonic": 1, "mond_simple_mu": 2, "rar_mcgaugh": 3}
    rows.sort(key=lambda row: order.get(str(row["Score"]), 99))
    write_csv(
        PACKET / "effect_size_summary.csv",
        [
            "Score",
            "Description",
            "N_A",
            "N_C",
            "Median_A",
            "Median_C",
            "MedianDiff_C_minus_A",
            "CohenLikeD",
            "RobustMedianD",
            "CommonLanguageAUC",
            "AUC_CI95Low",
            "AUC_CI95High",
            "CliffsDelta",
        ],
        rows,
    )

    lines = [
        "# Effect-Size Appendix",
        "",
        "The primary paper statistic is a median C-minus-A residual-scatter difference. This appendix translates the same A/C separation into scale-free effect-size and classification-sanity quantities. These are descriptive checks, not new primary endpoints.",
        "",
        "Definitions:",
        "",
        "```text",
        "Cohen-like d      = median(C)-median(A) divided by pooled standard deviation",
        "robust median d   = median(C)-median(A) divided by 1.4826 * pooled MAD",
        "common-language AUC = P(rms_C > rms_A) + 0.5 P(tie)",
        "Cliff's delta     = 2*AUC - 1",
        "```",
        "",
        "| score | n A | n C | C-A median diff | Cohen-like d | robust median d | AUC | AUC 95% CI | Cliff delta |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | ---: |",
    ]
    for row in rows:
        lines.append(
            "| {Description} | {N_A} | {N_C} | {MedianDiff_C_minus_A} | {CohenLikeD} | {RobustMedianD} | {CommonLanguageAUC} | [{AUC_CI95Low}, {AUC_CI95High}] | {CliffsDelta} |".format(
                **row
            )
        )
    lines.extend(
        [
            "",
            "Interpretation: the fixed projection, MOND-like, and empirical RAR scores show moderate A/C separation by common-language AUC, while the Newtonian baryonic baseline is close to weak/non-informative in this sample. This supports the paper's restrained reading: the signal is tied to low-acceleration residual regularity, not uniquely to the projection formula.",
        ]
    )
    (PACKET / "effect_size_appendix.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def quality_rows() -> list[object]:
    joined = join_control_rows(
        read_residual_summary(OUTPUTS / "sparc_residual_summary.csv"),
        read_coherence_labels(LABELS),
        read_diagnostics(OUTPUTS / "coherence_label_diagnostics.csv"),
    )
    return [row for row in joined if passes_quality(row, QualityThresholds())]


def make_systematics_appendix() -> None:
    rows = quality_rows()
    ac = [row for row in rows if row.label in {"A", "C"}]
    bins = [
        ("30-45", lambda value: 30 <= value < 45),
        ("45-60", lambda value: 45 <= value < 60),
        ("60-75", lambda value: 60 <= value < 75),
        ("75-85", lambda value: 75 <= value <= 85),
    ]
    out_rows = []
    for name, predicate in bins:
        for klass in ["A", "C"]:
            values = [
                row.rms_log_tpg
                for row in ac
                if row.label == klass and row.inclination_deg is not None and predicate(row.inclination_deg)
            ]
            out_rows.append(
                {
                    "InclinationBinDeg": name,
                    "Class": klass,
                    "N": len(values),
                    "MedianRmsLog": f"{median(values):.6g}" if values else "",
                }
            )

    risk_rows = []
    for klass in ["A", "C"]:
        group = [row for row in ac if row.label == klass]
        low_inc = [row for row in group if row.inclination_deg is not None and row.inclination_deg < 40]
        high_inc = [row for row in group if row.inclination_deg is not None and row.inclination_deg > 75]
        high_inc_err = [row for row in group if row.inclination_error_deg is not None and row.inclination_error_deg >= 7]
        high_v_err = [row for row in group if row.mean_err_vobs_kms >= 5]
        short_radius = [row for row in group if row.max_radius_kpc < 5]
        risk_rows.append(
            {
                "Class": klass,
                "N": len(group),
                "InclinationLt40": len(low_inc),
                "InclinationGt75": len(high_inc),
                "InclinationErrorGe7": len(high_inc_err),
                "MeanErrVobsGe5": len(high_v_err),
                "MaxRadiusLt5Kpc": len(short_radius),
            }
        )
    write_csv(
        PACKET / "inclination_systematics_summary.csv",
        ["InclinationBinDeg", "Class", "N", "MedianRmsLog"],
        out_rows,
    )
    write_csv(
        PACKET / "systematics_risk_counts.csv",
        [
            "Class",
            "N",
            "InclinationLt40",
            "InclinationGt75",
            "InclinationErrorGe7",
            "MeanErrVobsGe5",
            "MaxRadiusLt5Kpc",
        ],
        risk_rows,
    )

    lines = [
        "# Inclination And Systematics Appendix",
        "",
        "This appendix collects geometry and measurement-systematics risks that are not fully resolved by the current packet. It is intentionally conservative: the aim is to state what remains vulnerable, not to promote a new endpoint.",
        "",
        "## Inclination-Bin Residual Summary",
        "",
        "| inclination bin | n A | median A | n C | median C | C-A direction |",
        "| --- | ---: | ---: | ---: | ---: | --- |",
    ]
    by_bin = {}
    for row in out_rows:
        by_bin.setdefault(row["InclinationBinDeg"], {})[row["Class"]] = row
    for name, _predicate in bins:
        a = by_bin.get(name, {}).get("A", {})
        c = by_bin.get(name, {}).get("C", {})
        med_a = a.get("MedianRmsLog", "")
        med_c = c.get("MedianRmsLog", "")
        direction = ""
        if med_a != "" and med_c != "":
            direction = "C>A" if float(med_c) > float(med_a) else "C<=A"
        lines.append(f"| {name} | {a.get('N', 0)} | {med_a} | {c.get('N', 0)} | {med_c} | {direction} |")
    lines.extend(
        [
            "",
            "## Risk Counts",
            "",
            "| class | n | inc < 40 | inc > 75 | inc err >= 7 | mean Vobs err >= 5 | Rmax < 5 kpc |",
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for row in risk_rows:
        lines.append(
            "| {Class} | {N} | {InclinationLt40} | {InclinationGt75} | {InclinationErrorGe7} | {MeanErrVobsGe5} | {MaxRadiusLt5Kpc} |".format(
                **row
            )
        )
    lines.extend(
        [
            "",
            "## Remaining Systematics",
            "",
            "- Edge-on systems can suffer from line-of-sight integration, dust, and vertical structure effects even when they pass the inclination quality gate.",
            "- Lower-inclination systems can amplify deprojection uncertainty, especially when non-circular motions are present.",
            "- Beam smearing is not directly controlled because homogeneous beam-size or physical HI-resolution measurements are not yet in the packet.",
            "- Asymmetric drift and pressure support can matter in low-mass or gas-rich galaxies and may increase residual scatter independently of the projection score.",
            "- Non-circular motions, bars, tidal disturbances, and warps are partly the phenomenon being labeled, but they also make any smooth axisymmetric rotation-curve score less appropriate.",
            "",
            "Interpretation: the current quality gate removes the most extreme inclination failures, but it does not eliminate geometry or kinematic-systematics concerns. These risks should remain limitations until a follow-up sample includes homogeneous resolution, beam, and velocity-field quality metadata.",
        ]
    )
    (PACKET / "inclination_systematics_appendix.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    make_effect_size_appendix()
    make_systematics_appendix()
    print(PACKET / "effect_size_appendix.md")
    print(PACKET / "inclination_systematics_appendix.md")


if __name__ == "__main__":
    main()
