#!/usr/bin/env python3
"""Build paper-facing labeling evidence and alternative baseline-score tables."""

from __future__ import annotations

import argparse
import csv
import math
import random
import re
import statistics
import sys
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from taucore.coherence import read_coherence_labels, read_residual_summary
from taucore.controls import QualityThresholds, join_control_rows, passes_quality, read_diagnostics
from taucore.galaxy_activation import (
    DEFAULT_A0_M_S2,
    DEFAULT_ALPHA,
    DEFAULT_UPSILON_BULGE,
    DEFAULT_UPSILON_DISK,
    acceleration_m_s2,
    baryonic_speed_squared_kms2,
    tpg_factor,
)
from taucore.sparc import SparcRotmodTable, load_rotmod_directory


STUDY = ROOT / "studies/sparc_residual_coherence_test_v01"
PACKET = STUDY / "paper_packet_v06_distance_balanced"
OUTPUTS = ROOT / "outputs/external_proxy_v06_distance_balanced"
LABELS = STUDY / "coherence_labels_v06_distance_balanced.csv"
V05_WORKBOOK = STUDY / "external_proxy_review_workbook_v05_final.csv"
DEFAULT_ROTMOD = ROOT / "data/sparc/Rotmod_LTG"


@dataclass(frozen=True)
class ScoreSummary:
    galaxy_name: str
    score: str
    n_points: int
    rms_log: float


@dataclass(frozen=True)
class PointResidual:
    galaxy_name: str
    label: str
    radius_kpc: float
    radius_fraction: float
    a_n_over_a0: float
    residuals: dict[str, float]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def quality_pass_names() -> dict[str, str]:
    residual_rows = read_residual_summary(OUTPUTS / "sparc_residual_summary.csv")
    label_rows = read_coherence_labels(LABELS)
    diagnostic_rows = read_diagnostics(OUTPUTS / "coherence_label_diagnostics.csv")
    joined = join_control_rows(residual_rows, label_rows, diagnostic_rows)
    thresholds = QualityThresholds()
    return {row.galaxy_name: row.label for row in joined if passes_quality(row, thresholds)}


def quality_pass_label_rows() -> dict[str, dict[str, str]]:
    quality = quality_pass_names()
    return {
        row["GalaxyName"]: row
        for row in read_csv(LABELS)
        if row["GalaxyName"] in quality
    }


def parse_notes(notes: str) -> dict[str, str]:
    parsed: dict[str, str] = {}
    for part in notes.split(";"):
        if "=" in part:
            key, value = part.split("=", maxsplit=1)
            parsed[key.strip()] = value.strip()
    return parsed


def make_external_evidence_table() -> None:
    quality_labels = quality_pass_names()
    labels = read_csv(LABELS)
    workbook = {row["GalaxyName"]: row for row in read_csv(V05_WORKBOOK)}
    rows: list[dict[str, object]] = []

    for row in labels:
        name = row["GalaxyName"]
        if name not in quality_labels:
            continue
        notes = parse_notes(row.get("Notes", ""))
        review = workbook.get(name, {})
        rows.append(
            {
                "GalaxyName": name,
                "Class": row["S_tau_class"],
                "QualityPass": "true",
                "Confidence": row["LabelConfidence"],
                "EvidenceType": notes.get("evidence_type", review.get("EvidenceType", "")),
                "Reviewer": notes.get("reviewer", review.get("Reviewer", "")),
                "ReviewedDate": notes.get("reviewed_date", review.get("ReviewedDate", "")),
                "ResidualBlind": row["IsBlindLabel"],
                "EvidenceSummary": row["LabelReason"],
                "Source1": notes.get("source1", review.get("Source1", "")),
                "Source2": notes.get("source2", review.get("Source2", "")),
                "Source3": notes.get("source3", review.get("Source3", "")),
            }
        )

    rows.sort(key=lambda item: (str(item["Class"]), str(item["GalaxyName"])))
    fields = [
        "GalaxyName",
        "Class",
        "QualityPass",
        "Confidence",
        "EvidenceType",
        "Reviewer",
        "ReviewedDate",
        "ResidualBlind",
        "EvidenceSummary",
        "Source1",
        "Source2",
        "Source3",
    ]
    write_csv(PACKET / "external_evidence_table.csv", fields, rows)

    counts = {label: sum(1 for row in rows if row["Class"] == label) for label in ["A", "B", "C"]}
    lines = [
        "# External Evidence Table",
        "",
        "Quality-pass rows only. Labels were assigned from source-backed external evidence under residual blinding.",
        "",
        f"Counts: A={counts['A']}, B={counts['B']}, C={counts['C']}.",
        "",
        "| Galaxy | Class | Confidence | Evidence type | Residual blind | Sources | Evidence summary |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        sources = ", ".join(
            source
            for source in [str(row["Source1"]), str(row["Source2"]), str(row["Source3"])]
            if source
        )
        summary = str(row["EvidenceSummary"]).replace("|", "/")
        if len(summary) > 260:
            summary = summary[:257].rstrip() + "..."
        lines.append(
            "| {GalaxyName} | {Class} | {Confidence} | {EvidenceType} | {ResidualBlind} | {sources} | {summary} |".format(
                sources=sources.replace("|", "/"),
                summary=summary,
                **row,
            )
        )
    (PACKET / "external_evidence_table.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    protocol = """# Labeling Protocol

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
"""
    (PACKET / "labeling_protocol.md").write_text(protocol, encoding="utf-8")


def make_continuous_s_tau_manifest() -> None:
    evidence_rows = read_csv(PACKET / "external_evidence_table.csv")
    downloaded = downloaded_s_tau_by_galaxy()
    downloaded_soft = downloaded_soft_s_tau_by_galaxy()
    manifest_rows: list[dict[str, object]] = []
    for row in evidence_rows:
        if row["GalaxyName"] in downloaded:
            s_tau, reason = downloaded[row["GalaxyName"]]
            method = "downloaded_catalog_numeric_proxy"
        else:
            s_tau, method, reason = continuous_s_tau_from_evidence(row)
        manifest_rows.append(
            {
                "GalaxyName": row["GalaxyName"],
                "Class": row["Class"],
                "EvidenceType": row["EvidenceType"],
                "S_tau_continuous": f"{s_tau:.6g}",
                "S_tau_soft_calibrated": f"{downloaded_soft.get(row['GalaxyName'], (max(0.55, min(0.95, 0.55 + 0.4 * s_tau)), 'soft_from_primary'))[0]:.6g}",
                "MappingMethod": method,
                "MappingReason": reason,
                "ResidualBlind": row["ResidualBlind"],
            }
        )

    write_csv(
        PACKET / "continuous_s_tau_manifest.csv",
        [
            "GalaxyName",
            "Class",
            "EvidenceType",
            "S_tau_continuous",
            "S_tau_soft_calibrated",
            "MappingMethod",
            "MappingReason",
            "ResidualBlind",
        ],
        manifest_rows,
    )

    by_method = {}
    for row in manifest_rows:
        by_method[row["MappingMethod"]] = by_method.get(row["MappingMethod"], 0) + 1
    lines = [
        "# Continuous S_tau Manifest",
        "",
        "First residual-blind operational candidate for a continuous Tau Core coherence parameter. This manifest is generated only from external evidence-table text and source fields, not from residuals.",
        "",
        "Mapping priority:",
        "",
        "```text",
        "1. Downloaded VizieR catalog proxies when present: WHISP, Reynolds, Yu/ALFALFA.",
        "2. Quantitative proxies parsed from evidence text when no downloaded catalog match exists.",
        "3. Evidence-type fallback when no numeric proxy is available.",
        "4. Class fallback only if neither numeric proxy nor evidence type is usable.",
        "```",
        "",
        "Counts by mapping method:",
        "",
        "| method | n |",
        "| --- | ---: |",
    ]
    for method, count in sorted(by_method.items()):
        lines.append(f"| {method} | {count} |")
    lines.extend(
        [
            "",
            "| Galaxy | Class | Evidence type | S_tau | soft S_tau | method | reason |",
            "| --- | --- | --- | ---: | ---: | --- | --- |",
        ]
    )
    for row in manifest_rows:
        lines.append(
            "| {GalaxyName} | {Class} | {EvidenceType} | {S_tau_continuous} | {S_tau_soft_calibrated} | {MappingMethod} | {MappingReason} |".format(
                **row
            )
        )
    (PACKET / "continuous_s_tau_manifest.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    protocol = """# Continuous / Held-Out S_tau Protocol Draft

## Goal

Define a more serious Tau Core extension than the naive A/B/C switch:

```text
F_tau(a_N, S_tau) = 1 + S_tau alpha ln(1 + a0/a_N)
```

The purpose is to compare the old high-coherence TPG limit (`S_tau=1`) against an externally defined continuous coherence parameter.

## Non-Negotiable Rule

`S_tau` must be defined without using residuals, score values, p-values, class medians, or any Tau Core/MOND/RAR comparison output.

## Current Candidate

The current manifest uses source-backed external evidence:

```text
Reynolds Amap/Avel low-asymmetry proxies
Yu+2022 ALFALFA Af/Ac global HI profile asymmetry
WHISP resolved HI morphology asymmetry A
evidence-type fallback for rows without quantitative proxies
```

The manifest carries two versions:

```text
S_tau_continuous      = direct monotone mapping, useful as a stress test
S_tau_soft_calibrated = conservative mapping constrained to [0.55, 0.95]
```

The numeric mapping is intentionally monotone:

```text
lower asymmetry -> higher S_tau
higher disturbance -> lower S_tau, but the soft-calibrated version does not switch off the response
ambiguous/no-data -> S_tau near 0.5
```

## Held-Out Source-Family Test

For the next paper-grade pass, use source families instead of tuning on the same evidence:

```text
train/freeze mapping family A: Reynolds + Yu global asymmetry
test family B: WHISP resolved HI morphology

or

train/freeze mapping family A: WHISP morphology
test family B: Reynolds/Yu global asymmetry
```

The statistic should be computed only after choosing the family split and mapping constants.

## Why This Is Better Than A/B/C Switching

The naive rule `A=1, B=0.5, C=0` reuses the endpoint grouping as the model input and pushes disturbed galaxies toward the Newtonian baseline. It increases A/C separation but worsens global residual scatter. A continuous source-backed score can be tested as a physical covariate rather than as a hard label switch.

## Held-Out Rule

For a paper-grade test, one of the following must be used:

```text
1. Train/freeze the S_tau mapping on one source family and test on another.
2. Freeze the mapping on current SPARC labels and evaluate on an independent validation sample.
3. Use numeric proxies only for S_tau and reserve A/C labels only for evaluation.
```

The current manifest is a scaffold. It should not be treated as proof until one of these held-out rules is applied.

## Preferred Next Endpoint

```text
primary_model = F_tau(a_N, S_tau_continuous_external)
primary_comparator = old fixed projection plus MOND/RAR
primary_statistic = galaxy-level paired residual improvement and residual-shape interaction
primary_validation = held-out evidence family or independent sample
```
"""
    (PACKET / "continuous_s_tau_protocol.md").write_text(protocol, encoding="utf-8")


def speed_factor(score: str, a_n: float) -> float:
    if a_n <= 0:
        return math.nan
    if score == "projection_fixed":
        return tpg_factor(a_n, alpha=DEFAULT_ALPHA, a0_m_s2=DEFAULT_A0_M_S2, s_tau=1.0)
    if score == "newtonian_baryonic":
        return 1.0
    if score == "mond_simple_mu":
        g_ratio = 0.5 * (1.0 + math.sqrt(1.0 + 4.0 * DEFAULT_A0_M_S2 / a_n))
        return math.sqrt(g_ratio)
    if score == "rar_mcgaugh":
        denom = 1.0 - math.exp(-math.sqrt(a_n / DEFAULT_A0_M_S2))
        if denom <= 0:
            return math.nan
        return math.sqrt(1.0 / denom)
    raise ValueError(score)


def tau_factor(a_n: float, s_tau: float) -> float:
    return tpg_factor(a_n, alpha=DEFAULT_ALPHA, a0_m_s2=DEFAULT_A0_M_S2, s_tau=s_tau)


def class_s_tau(label: str) -> float:
    return {"A": 1.0, "B": 0.5, "C": 0.0}.get(label, 0.5)


def evidence_s_tau(label_row: dict[str, str]) -> float:
    notes = parse_notes(label_row.get("Notes", ""))
    evidence_type = notes.get("evidence_type", "").strip().lower()
    label = label_row.get("S_tau_class", "").strip().upper()
    if evidence_type in {"regular_kinematics", "low_asymmetry"}:
        return 1.0
    if evidence_type in {"disturbed_hi", "tidal", "interaction", "warp", "lopsided_kinematics"}:
        return 0.0
    if label == "A":
        return 0.85
    if label == "C":
        return 0.15
    return 0.5


def clamp(value: float, lower: float = 0.0, upper: float = 1.0) -> float:
    return max(lower, min(upper, value))


def first_float(pattern: str, text: str) -> float | None:
    match = re.search(pattern, text, flags=re.IGNORECASE)
    return float(match.group(1)) if match else None


def continuous_s_tau_from_evidence(evidence_row: dict[str, str]) -> tuple[float, str, str]:
    text = " ".join(
        [
            evidence_row.get("EvidenceSummary", ""),
            evidence_row.get("Source1", ""),
            evidence_row.get("Source2", ""),
            evidence_row.get("Source3", ""),
        ]
    )
    evidence_type = evidence_row.get("EvidenceType", "").strip().lower()
    label = evidence_row.get("Class", "").strip().upper()

    amap = first_float(r"\bAmap\s*=\s*([0-9.]+)", text)
    avel = first_float(r"\bAvel\s*=\s*([0-9.]+)", text)
    af = first_float(r"\bAf\s*=\s*([0-9.]+)", text)
    ac = first_float(r"\bAc\s*=\s*([0-9.]+)", text)
    whisp_a = first_float(r"\bA\s*=\s*([0-9.]+)", text)

    components: list[float] = []
    reasons: list[str] = []
    if amap is not None:
        components.append(clamp(1.0 - amap / 0.8))
        reasons.append(f"Amap={amap:g}")
    if avel is not None:
        components.append(clamp(1.0 - avel / 0.15))
        reasons.append(f"Avel={avel:g}")
    if af is not None:
        components.append(clamp(1.0 - max(0.0, af - 1.0) / 0.5))
        reasons.append(f"Af={af:g}")
    if ac is not None:
        components.append(clamp(1.0 - max(0.0, ac - 1.0) / 0.5))
        reasons.append(f"Ac={ac:g}")
    if whisp_a is not None and evidence_type in {"disturbed_hi", "mixed", "interaction", "warp", "tidal"}:
        components.append(clamp(1.0 - whisp_a / 1.2))
        reasons.append(f"WHISP_A={whisp_a:g}")

    if components:
        return statistics.median(components), "quantitative_external_proxy", "; ".join(reasons)

    fallback = {
        "regular_kinematics": 0.9,
        "low_asymmetry": 0.85,
        "mixed": 0.5,
        "no_data": 0.5,
        "other": 0.5,
        "disturbed_hi": 0.2,
        "interaction": 0.15,
        "tidal": 0.1,
        "warp": 0.2,
    }.get(evidence_type)
    if fallback is not None:
        return fallback, "evidence_type_fallback", evidence_type
    return class_s_tau(label), "class_fallback", label


def component_from_positive_asymmetry(value: str, scale: float, label: str) -> tuple[float, str] | None:
    if not value:
        return None
    try:
        number = float(value)
    except ValueError:
        return None
    return clamp(1.0 - number / scale), f"{label}={number:g}"


def soft_component_from_positive_asymmetry(value: str, scale: float, label: str) -> tuple[float, str] | None:
    if not value:
        return None
    try:
        number = float(value)
    except ValueError:
        return None
    # Soft calibration: disturbance modulates the high-coherence response, but
    # does not switch it off. This keeps S_tau in [0.55, 0.95].
    return clamp(0.95 - 0.40 * min(number / scale, 1.0), 0.55, 0.95), f"{label}={number:g}"


def component_from_profile_ratio(value: str, label: str) -> tuple[float, str] | None:
    if not value:
        return None
    try:
        number = float(value)
    except ValueError:
        return None
    return clamp(1.0 - max(0.0, number - 1.0) / 0.5), f"{label}={number:g}"


def soft_component_from_profile_ratio(value: str, label: str) -> tuple[float, str] | None:
    if not value:
        return None
    try:
        number = float(value)
    except ValueError:
        return None
    excess = min(max(0.0, number - 1.0) / 0.5, 1.0)
    return clamp(0.95 - 0.40 * excess, 0.55, 0.95), f"{label}={number:g}"


def downloaded_s_tau_by_galaxy() -> dict[str, tuple[float, str]]:
    path = PACKET / "s_tau_source_matches.csv"
    if not path.exists():
        return {}
    grouped: dict[str, list[tuple[float, str]]] = {}
    for row in read_csv(path):
        galaxy = row["GalaxyName"]
        components = [
            component_from_positive_asymmetry(row.get("Amap", ""), 0.8, "Amap"),
            component_from_positive_asymmetry(row.get("Avel", ""), 0.15, "Avel"),
            component_from_positive_asymmetry(row.get("WHISP_A", ""), 1.2, "WHISP_A"),
            component_from_positive_asymmetry(row.get("WHISP_Lop", ""), 1.5, "WHISP_Lop"),
            component_from_profile_ratio(row.get("Af", ""), "Af"),
            component_from_profile_ratio(row.get("Ac", ""), "Ac"),
        ]
        for component in components:
            if component is not None:
                grouped.setdefault(galaxy, []).append(component)
    result: dict[str, tuple[float, str]] = {}
    for galaxy, components in grouped.items():
        values = [value for value, _reason in components]
        reasons = "; ".join(reason for _value, reason in components)
        result[galaxy] = (statistics.median(values), reasons)
    return result


def downloaded_soft_s_tau_by_galaxy() -> dict[str, tuple[float, str]]:
    return downloaded_soft_s_tau_by_galaxy_for_sources(None)


def downloaded_soft_s_tau_by_galaxy_for_sources(source_family: str | None) -> dict[str, tuple[float, str]]:
    path = PACKET / "s_tau_source_matches.csv"
    if not path.exists():
        return {}
    grouped: dict[str, list[tuple[float, str]]] = {}
    for row in read_csv(path):
        source = row.get("Source", "")
        if source_family == "whisp" and not source.startswith("whisp"):
            continue
        if source_family == "global" and source not in {
            "reynolds2020_hi_asymmetry",
            "yu2022_alfalfa_profile_asymmetry",
        }:
            continue
        galaxy = row["GalaxyName"]
        components = [
            soft_component_from_positive_asymmetry(row.get("Amap", ""), 0.8, "Amap"),
            soft_component_from_positive_asymmetry(row.get("Avel", ""), 0.15, "Avel"),
            soft_component_from_positive_asymmetry(row.get("WHISP_A", ""), 1.2, "WHISP_A"),
            soft_component_from_positive_asymmetry(row.get("WHISP_Lop", ""), 1.5, "WHISP_Lop"),
            soft_component_from_profile_ratio(row.get("Af", ""), "Af"),
            soft_component_from_profile_ratio(row.get("Ac", ""), "Ac"),
        ]
        for component in components:
            if component is not None:
                grouped.setdefault(galaxy, []).append(component)
    result: dict[str, tuple[float, str]] = {}
    for galaxy, components in grouped.items():
        values = [value for value, _reason in components]
        reasons = "; ".join(reason for _value, reason in components)
        result[galaxy] = (statistics.median(values), reasons)
    return result


def summarize_tau_score(table: SparcRotmodTable, score: str, s_tau: float | None = None) -> ScoreSummary | None:
    residuals: list[float] = []
    for row in table.rows:
        vn2 = baryonic_speed_squared_kms2(
            row.vgas_kms,
            row.vdisk_kms,
            row.vbul_kms,
            upsilon_disk=DEFAULT_UPSILON_DISK,
            upsilon_bulge=DEFAULT_UPSILON_BULGE,
        )
        a_n = acceleration_m_s2(vn2, row.radius_kpc)
        if score in {"tau_core_s_class", "tau_core_s_evidence", "tau_core_s_continuous", "tau_core_s_soft"}:
            if s_tau is None:
                raise ValueError(f"s_tau is required for {score}")
            factor = tau_factor(a_n, s_tau)
        else:
            factor = speed_factor(score, a_n)
        if vn2 <= 0 or row.vobs_kms <= 0 or not math.isfinite(factor):
            continue
        vpred = math.sqrt(vn2) * factor
        if vpred > 0 and math.isfinite(vpred):
            residuals.append(math.log(row.vobs_kms / vpred))
    if not residuals:
        return None
    rms = math.sqrt(sum(value * value for value in residuals) / len(residuals))
    return ScoreSummary(table.galaxy_name, score, len(residuals), rms)


def summarize_score(table: SparcRotmodTable, score: str) -> ScoreSummary | None:
    residuals: list[float] = []
    for row in table.rows:
        vn2 = baryonic_speed_squared_kms2(
            row.vgas_kms,
            row.vdisk_kms,
            row.vbul_kms,
            upsilon_disk=DEFAULT_UPSILON_DISK,
            upsilon_bulge=DEFAULT_UPSILON_BULGE,
        )
        a_n = acceleration_m_s2(vn2, row.radius_kpc)
        factor = speed_factor(score, a_n)
        if vn2 <= 0 or row.vobs_kms <= 0 or not math.isfinite(factor):
            continue
        vpred = math.sqrt(vn2) * factor
        if vpred > 0 and math.isfinite(vpred):
            residuals.append(math.log(row.vobs_kms / vpred))
    if not residuals:
        return None
    rms = math.sqrt(sum(value * value for value in residuals) / len(residuals))
    return ScoreSummary(table.galaxy_name, score, len(residuals), rms)


def point_residuals(table: SparcRotmodTable, label: str, scores: list[str]) -> list[PointResidual]:
    points: list[PointResidual] = []
    max_radius = max(row.radius_kpc for row in table.rows)
    for row in table.rows:
        vn2 = baryonic_speed_squared_kms2(
            row.vgas_kms,
            row.vdisk_kms,
            row.vbul_kms,
            upsilon_disk=DEFAULT_UPSILON_DISK,
            upsilon_bulge=DEFAULT_UPSILON_BULGE,
        )
        a_n = acceleration_m_s2(vn2, row.radius_kpc)
        if vn2 <= 0 or row.vobs_kms <= 0 or a_n <= 0:
            continue
        residuals: dict[str, float] = {}
        for score in scores:
            factor = speed_factor(score, a_n)
            if not math.isfinite(factor):
                continue
            vpred = math.sqrt(vn2) * factor
            if vpred > 0 and math.isfinite(vpred):
                residuals[score] = math.log(row.vobs_kms / vpred)
        if len(residuals) == len(scores):
            points.append(
                PointResidual(
                    galaxy_name=table.galaxy_name,
                    label=label,
                    radius_kpc=row.radius_kpc,
                    radius_fraction=row.radius_kpc / max_radius if max_radius > 0 else math.nan,
                    a_n_over_a0=a_n / DEFAULT_A0_M_S2,
                    residuals=residuals,
                )
            )
    return points


def acceleration_bin(a_n_over_a0: float) -> str:
    if a_n_over_a0 < 0.1:
        return "aN/a0<0.1"
    if a_n_over_a0 < 0.3:
        return "0.1<=aN/a0<0.3"
    if a_n_over_a0 < 1.0:
        return "0.3<=aN/a0<1"
    return "aN/a0>=1"


def radius_bin(radius_fraction: float) -> str:
    if radius_fraction < 1 / 3:
        return "inner_R<0.33Rmax"
    if radius_fraction < 2 / 3:
        return "middle_0.33-0.67Rmax"
    return "outer_R>=0.67Rmax"


def median_or_nan(values: list[float]) -> float:
    return statistics.median(values) if values else math.nan


def rankdata(values: list[float]) -> list[float]:
    order = sorted(range(len(values)), key=lambda idx: values[idx])
    ranks = [0.0] * len(values)
    cursor = 0
    while cursor < len(values):
        end = cursor
        while end + 1 < len(values) and values[order[end + 1]] == values[order[cursor]]:
            end += 1
        rank = (cursor + end + 2) / 2.0
        for idx in range(cursor, end + 1):
            ranks[order[idx]] = rank
        cursor = end + 1
    return ranks


def pearson(xs: list[float], ys: list[float]) -> float:
    if len(xs) < 2 or len(xs) != len(ys):
        return math.nan
    mean_x = sum(xs) / len(xs)
    mean_y = sum(ys) / len(ys)
    cov = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys))
    var_x = sum((x - mean_x) ** 2 for x in xs)
    var_y = sum((y - mean_y) ** 2 for y in ys)
    if var_x <= 0 or var_y <= 0:
        return math.nan
    return cov / math.sqrt(var_x * var_y)


def spearman(xs: list[float], ys: list[float]) -> float:
    return pearson(rankdata(xs), rankdata(ys))


def bootstrap_ci(c_values: list[float], a_values: list[float], seed: int, iterations: int = 10000) -> tuple[float, float]:
    rng = random.Random(seed)
    diffs = []
    for _ in range(iterations):
        c_sample = [rng.choice(c_values) for _ in c_values]
        a_sample = [rng.choice(a_values) for _ in a_values]
        diffs.append(statistics.median(c_sample) - statistics.median(a_sample))
    diffs.sort()
    return diffs[int(0.025 * iterations)], diffs[int(0.975 * iterations)]


def permutation_p(c_values: list[float], a_values: list[float], seed: int, iterations: int = 10000) -> float:
    rng = random.Random(seed)
    observed = statistics.median(c_values) - statistics.median(a_values)
    pooled = c_values + a_values
    n_c = len(c_values)
    hits = 0
    for _ in range(iterations):
        shuffled = pooled[:]
        rng.shuffle(shuffled)
        diff = statistics.median(shuffled[:n_c]) - statistics.median(shuffled[n_c:])
        if diff >= observed:
            hits += 1
    return (hits + 1) / (iterations + 1)


def make_baseline_comparisons(rotmod_dir: Path) -> None:
    labels = quality_pass_names()
    label_rows = quality_pass_label_rows()
    continuous_manifest = {
        row["GalaxyName"]: float(row["S_tau_continuous"])
        for row in read_csv(PACKET / "continuous_s_tau_manifest.csv")
    }
    soft_manifest = {
        row["GalaxyName"]: float(row["S_tau_soft_calibrated"])
        for row in read_csv(PACKET / "continuous_s_tau_manifest.csv")
    }
    tables = {table.galaxy_name: table for table in load_rotmod_directory(rotmod_dir)}
    scores = [
        "projection_fixed",
        "tau_core_s_class",
        "tau_core_s_evidence",
        "tau_core_s_continuous",
        "tau_core_s_soft",
        "newtonian_baryonic",
        "mond_simple_mu",
        "rar_mcgaugh",
    ]
    summary_rows: list[dict[str, object]] = []
    by_score: dict[str, dict[str, float]] = {score: {} for score in scores}

    for name in labels:
        table = tables.get(name)
        if table is None:
            continue
        for score in scores:
            s_tau = None
            if score == "tau_core_s_class":
                s_tau = class_s_tau(labels[name])
            elif score == "tau_core_s_evidence":
                s_tau = evidence_s_tau(label_rows[name])
            elif score == "tau_core_s_continuous":
                s_tau = continuous_manifest[name]
            elif score == "tau_core_s_soft":
                s_tau = soft_manifest[name]
            summary = summarize_tau_score(table, score, s_tau=s_tau)
            if summary is None:
                continue
            by_score[score][name] = summary.rms_log
            summary_rows.append(
                {
                    "GalaxyName": name,
                    "Class": labels[name],
                    "Score": score,
                    "NPoints": summary.n_points,
                    "RmsLog": f"{summary.rms_log:.12g}",
                }
            )

    write_csv(
        PACKET / "baseline_score_by_galaxy.csv",
        ["GalaxyName", "Class", "Score", "NPoints", "RmsLog"],
        sorted(summary_rows, key=lambda row: (str(row["Score"]), str(row["Class"]), str(row["GalaxyName"]))),
    )

    comparison_rows: list[dict[str, object]] = []
    labels_for_scores = {
        "projection_fixed": "Fixed projection score",
        "tau_core_s_class": "Tau Core S_tau class-gated",
        "tau_core_s_evidence": "Tau Core S_tau evidence-gated",
        "tau_core_s_continuous": "Tau Core S_tau continuous external",
        "tau_core_s_soft": "Tau Core S_tau soft-calibrated",
        "newtonian_baryonic": "Newtonian baryonic",
        "mond_simple_mu": "MOND simple-mu",
        "rar_mcgaugh": "Empirical RAR",
    }
    for idx, score in enumerate(scores):
        a_values = [by_score[score][name] for name, label in labels.items() if label == "A" and name in by_score[score]]
        c_values = [by_score[score][name] for name, label in labels.items() if label == "C" and name in by_score[score]]
        if not a_values or not c_values:
            continue
        diff = statistics.median(c_values) - statistics.median(a_values)
        ci_low, ci_high = bootstrap_ci(c_values, a_values, seed=20260514 + idx)
        p = permutation_p(c_values, a_values, seed=20260614 + idx)
        comparison_rows.append(
            {
                "Score": score,
                "Description": labels_for_scores[score],
                "N_A": len(a_values),
                "N_C": len(c_values),
                "Median_A": f"{statistics.median(a_values):.6g}",
                "Median_C": f"{statistics.median(c_values):.6g}",
                "C_minus_A": f"{diff:.6g}",
                "PermutationP_C_greater_A": f"{p:.6g}",
                "BootstrapCI95Low": f"{ci_low:.6g}",
                "BootstrapCI95High": f"{ci_high:.6g}",
            }
        )

    write_csv(
        PACKET / "baseline_score_comparisons.csv",
        [
            "Score",
            "Description",
            "N_A",
            "N_C",
            "Median_A",
            "Median_C",
            "C_minus_A",
            "PermutationP_C_greater_A",
            "BootstrapCI95Low",
            "BootstrapCI95High",
        ],
        comparison_rows,
    )

    lines = [
        "# Alternative Baseline-Score Comparisons",
        "",
        "Same quality-pass A/C sample and same median C-minus-A statistic. Positive values mean disturbed C galaxies have larger residual scatter.",
        "",
        "`Fixed projection score` is the old high-coherence TPG limit (`S_tau=1`). The two Tau Core rows are operational extended candidates with external, residual-blind `S_tau` mappings; they are sensitivity tests, not primary Paper 1 endpoints.",
        "",
        "| Score | n_A | n_C | median A | median C | C-A | one-sided p | 95% bootstrap CI |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for row in comparison_rows:
        lines.append(
            "| {Description} | {N_A} | {N_C} | {Median_A} | {Median_C} | {C_minus_A} | {PermutationP_C_greater_A} | [{BootstrapCI95Low}, {BootstrapCI95High}] |".format(
                **row
            )
        )
    lines.extend(
        [
            "",
            "Interpretation: these are baseline-score stress tests, not replacement primary endpoints. If several smooth residual scores show the same direction, the paper should phrase the result as a residual-disturbance association rather than uniqueness of the fixed projection prescription. If the `S_tau`-gated variants mechanically increase A/C separation, that is expected: the same external labels are being used to gate the response and should not be reused as independent proof.",
        ]
    )
    (PACKET / "baseline_score_comparisons.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    performance_rows: list[dict[str, object]] = []
    old = by_score["projection_fixed"]
    for score in scores:
        values = by_score[score]
        common_names = sorted(set(values) & set(old))
        for label in ["A", "B", "C", "all"]:
            names = [
                name
                for name in common_names
                if label == "all" or labels.get(name) == label
            ]
            if not names:
                continue
            rms_values = [values[name] for name in names]
            old_values = [old[name] for name in names]
            paired_delta = [values[name] - old[name] for name in names]
            performance_rows.append(
                {
                    "Score": score,
                    "Description": labels_for_scores[score],
                    "Class": label,
                    "N": len(names),
                    "MedianRmsLog": f"{statistics.median(rms_values):.6g}",
                    "MedianDeltaVsFixedProjection": f"{statistics.median(paired_delta):.6g}",
                    "MedianOldFixedProjection": f"{statistics.median(old_values):.6g}",
                }
            )

    write_csv(
        PACKET / "taucore_extended_formula_comparison.csv",
        [
            "Score",
            "Description",
            "Class",
            "N",
            "MedianRmsLog",
            "MedianDeltaVsFixedProjection",
            "MedianOldFixedProjection",
        ],
        performance_rows,
    )

    perf_lines = [
        "# Old TPG vs Operational Extended Tau Core Formulae",
        "",
        "This table separates two questions:",
        "",
        "```text",
        "1. Does a score separate A and C labels?",
        "2. Does a score improve residual scatter relative to the old fixed projection score?",
        "```",
        "",
        "The old fixed projection score is the `S_tau=1` high-coherence TPG limit. The operational extended candidates use externally assigned `S_tau` mappings. Negative `delta vs old` means the candidate has lower median rms-log residual than the old fixed projection score for that class.",
        "",
        "| Score | Class | n | median rms-log | old fixed-projection median | delta vs old |",
        "| --- | --- | ---: | ---: | ---: | ---: |",
    ]
    for row in performance_rows:
        perf_lines.append(
            "| {Description} | {Class} | {N} | {MedianRmsLog} | {MedianOldFixedProjection} | {MedianDeltaVsFixedProjection} |".format(
                **row
            )
        )
    perf_lines.extend(
        [
            "",
            "Current reading: the class/evidence-gated `S_tau` variants strongly increase A/C separation because C rows are pushed toward the Newtonian baseline. That is not automatically better physics. A paper-grade extended Tau Core test should use held-out labels or independent radial `S_tau(R)` evidence before treating improved separation as validation.",
        ]
    )
    (PACKET / "taucore_extended_formula_comparison.md").write_text("\n".join(perf_lines) + "\n", encoding="utf-8")


def make_soft_s_tau_freeze_and_heldout(rotmod_dir: Path) -> None:
    freeze = """# Frozen Soft S_tau Mapping v0.1

Status: frozen operational candidate for held-out source-family testing. This rule was set after the hard and direct mappings proved too suppressive, and before any future independent validation run.

## Formula

The extended candidate is:

```text
F_tau(a_N, S_tau) = 1 + S_tau alpha ln(1 + a0/a_N)
```

The old TPG/high-coherence limit is:

```text
S_tau = 1
```

## Soft Mapping Constants

For positive asymmetry-like quantities where larger means less coherent:

```text
S_tau_component = clamp(0.95 - 0.40 * min(value / scale, 1), 0.55, 0.95)
```

Scales:

```text
Amap scale      = 0.8
Avel scale      = 0.15
WHISP_A scale   = 1.2
WHISP_Lop scale = 1.5
```

For profile ratios such as Yu/ALFALFA `Af` and `Ac`:

```text
excess = min(max(0, value - 1) / 0.5, 1)
S_tau_component = clamp(0.95 - 0.40 * excess, 0.55, 0.95)
```

Galaxy-level `S_tau` is the median of available source components. Missing numeric source data fall back to the predeclared evidence-type soft transform already recorded in `continuous_s_tau_manifest.csv`.

## Held-Out Source Families

The source-family split is:

```text
WHISP family  = whisp_hi_morphology + whisp_merger_morphology
Global family = Reynolds+2020 HI asymmetry + Yu+2022 ALFALFA profile asymmetry
```

The held-out sanity check is not a final validation. It asks whether the soft mapping behaves similarly when built from one source family and compared on galaxies also covered by the other source family.
"""
    (PACKET / "soft_s_tau_frozen_mapping.md").write_text(freeze, encoding="utf-8")

    labels = quality_pass_names()
    tables = {table.galaxy_name: table for table in load_rotmod_directory(rotmod_dir)}
    family_maps = {
        "whisp": downloaded_soft_s_tau_by_galaxy_for_sources("whisp"),
        "global": downloaded_soft_s_tau_by_galaxy_for_sources("global"),
    }
    old_scores: dict[str, float] = {}
    for name, table in tables.items():
        summary = summarize_tau_score(table, "projection_fixed")
        if summary is not None:
            old_scores[name] = summary.rms_log

    rows: list[dict[str, object]] = []
    for family, s_map in family_maps.items():
        other_family = "global" if family == "whisp" else "whisp"
        subsets = {
            "family_covered": sorted(set(s_map) & set(labels) & set(tables)),
            "other_family_overlap": sorted(set(s_map) & set(family_maps[other_family]) & set(labels) & set(tables)),
        }
        for subset_name, names in subsets.items():
            if not names:
                continue
            for label in ["A", "B", "C", "all"]:
                label_names = [name for name in names if label == "all" or labels[name] == label]
                if not label_names:
                    continue
                new_values = []
                old_values = []
                for name in label_names:
                    summary = summarize_tau_score(tables[name], "tau_core_s_soft", s_tau=s_map[name][0])
                    if summary is not None and name in old_scores:
                        new_values.append(summary.rms_log)
                        old_values.append(old_scores[name])
                if not new_values:
                    continue
                deltas = [new - old for new, old in zip(new_values, old_values)]
                rows.append(
                    {
                        "MappingFamily": family,
                        "EvaluationSubset": subset_name,
                        "Class": label,
                        "N": len(new_values),
                        "MedianSoftRmsLog": f"{statistics.median(new_values):.6g}",
                        "MedianOldTpgRmsLog": f"{statistics.median(old_values):.6g}",
                        "MedianDeltaVsOld": f"{statistics.median(deltas):.6g}",
                    }
                )

    overlap = sorted(set(family_maps["whisp"]) & set(family_maps["global"]))
    agreement_rows: list[dict[str, object]] = []
    if overlap:
        whisp_values = [family_maps["whisp"][name][0] for name in overlap]
        global_values = [family_maps["global"][name][0] for name in overlap]
        agreement_rows.append(
            {
                "NOverlap": len(overlap),
                "Pearson": f"{pearson(whisp_values, global_values):.6g}",
                "Spearman": f"{spearman(whisp_values, global_values):.6g}",
                "MedianWhispS": f"{statistics.median(whisp_values):.6g}",
                "MedianGlobalS": f"{statistics.median(global_values):.6g}",
                "OverlapGalaxies": ";".join(overlap),
            }
        )

    write_csv(
        PACKET / "soft_s_tau_heldout_source_family_test.csv",
        [
            "MappingFamily",
            "EvaluationSubset",
            "Class",
            "N",
            "MedianSoftRmsLog",
            "MedianOldTpgRmsLog",
            "MedianDeltaVsOld",
        ],
        rows,
    )
    write_csv(
        PACKET / "soft_s_tau_source_family_agreement.csv",
        ["NOverlap", "Pearson", "Spearman", "MedianWhispS", "MedianGlobalS", "OverlapGalaxies"],
        agreement_rows,
    )

    lines = [
        "# Soft S_tau Held-Out Source-Family Test",
        "",
        "Frozen mapping: `soft_s_tau_frozen_mapping.md`.",
        "",
        "This is a source-family sanity check, not a final independent validation. It keeps WHISP-derived and Reynolds/Yu-derived `S_tau` mappings separate.",
        "",
        "## Residual Performance",
        "",
        "| mapping family | evaluation subset | class | n | soft rms | old TPG rms | delta vs old |",
        "| --- | --- | --- | ---: | ---: | ---: | ---: |",
    ]
    for row in rows:
        lines.append(
            "| {MappingFamily} | {EvaluationSubset} | {Class} | {N} | {MedianSoftRmsLog} | {MedianOldTpgRmsLog} | {MedianDeltaVsOld} |".format(
                **row
            )
        )
    lines.extend(["", "## Source-Family Agreement", ""])
    if agreement_rows:
        agreement = agreement_rows[0]
        lines.extend(
            [
                f"Overlap galaxies: {agreement['NOverlap']}",
                f"Pearson correlation: {agreement['Pearson']}",
                f"Spearman correlation: {agreement['Spearman']}",
                f"Median WHISP S_tau: {agreement['MedianWhispS']}",
                f"Median global S_tau: {agreement['MedianGlobalS']}",
                "",
                "```text",
                str(agreement["OverlapGalaxies"]),
                "```",
            ]
        )
    else:
        lines.append("No overlap between WHISP and global source-family mappings.")
    lines.extend(
        [
            "",
            "Reading: if the soft mapping only works in the family used to build it, it is not yet paper-grade. A stronger version needs either better cross-family agreement or a genuinely independent validation sample.",
        ]
    )
    (PACKET / "soft_s_tau_heldout_source_family_test.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def make_taucore_specificity_map(rotmod_dir: Path) -> None:
    labels = quality_pass_names()
    tables = {table.galaxy_name: table for table in load_rotmod_directory(rotmod_dir)}
    scores = ["projection_fixed", "mond_simple_mu", "rar_mcgaugh"]
    points: list[PointResidual] = []
    for name, label in labels.items():
        if label not in {"A", "C"}:
            continue
        table = tables.get(name)
        if table is not None:
            points.extend(point_residuals(table, label, scores))

    point_rows: list[dict[str, object]] = []
    for point in points:
        abs_projection = abs(point.residuals["projection_fixed"])
        abs_mond = abs(point.residuals["mond_simple_mu"])
        abs_rar = abs(point.residuals["rar_mcgaugh"])
        point_rows.append(
            {
                "GalaxyName": point.galaxy_name,
                "Class": point.label,
                "RadiusKpc": f"{point.radius_kpc:.6g}",
                "RadiusFraction": f"{point.radius_fraction:.6g}",
                "RadiusBin": radius_bin(point.radius_fraction),
                "aN_over_a0": f"{point.a_n_over_a0:.6g}",
                "AccelerationBin": acceleration_bin(point.a_n_over_a0),
                "AbsResidualProjection": f"{abs_projection:.12g}",
                "AbsResidualMONDSimple": f"{abs_mond:.12g}",
                "AbsResidualRAR": f"{abs_rar:.12g}",
                "ProjectionMinusMONDAbs": f"{abs_projection - abs_mond:.12g}",
                "ProjectionMinusRARAbs": f"{abs_projection - abs_rar:.12g}",
            }
        )

    write_csv(
        PACKET / "taucore_specificity_point_map.csv",
        [
            "GalaxyName",
            "Class",
            "RadiusKpc",
            "RadiusFraction",
            "RadiusBin",
            "aN_over_a0",
            "AccelerationBin",
            "AbsResidualProjection",
            "AbsResidualMONDSimple",
            "AbsResidualRAR",
            "ProjectionMinusMONDAbs",
            "ProjectionMinusRARAbs",
        ],
        point_rows,
    )

    galaxy_bin_rows: list[dict[str, object]] = []
    for bin_type, bin_fn, bin_order in [
        (
            "acceleration",
            lambda point: acceleration_bin(point.a_n_over_a0),
            ["aN/a0<0.1", "0.1<=aN/a0<0.3", "0.3<=aN/a0<1", "aN/a0>=1"],
        ),
        (
            "radius",
            lambda point: radius_bin(point.radius_fraction),
            ["inner_R<0.33Rmax", "middle_0.33-0.67Rmax", "outer_R>=0.67Rmax"],
        ),
    ]:
        for bin_name in bin_order:
            for comparator, comparator_label in [("mond_simple_mu", "MOND simple-mu"), ("rar_mcgaugh", "Empirical RAR")]:
                galaxy_names = sorted({point.galaxy_name for point in points if bin_fn(point) == bin_name})
                for galaxy_name in galaxy_names:
                    group = [
                        point
                        for point in points
                        if point.galaxy_name == galaxy_name and bin_fn(point) == bin_name
                    ]
                    if not group:
                        continue
                    deltas = [
                        abs(point.residuals["projection_fixed"]) - abs(point.residuals[comparator])
                        for point in group
                    ]
                    galaxy_bin_rows.append(
                        {
                            "GalaxyName": galaxy_name,
                            "Class": group[0].label,
                            "BinType": bin_type,
                            "Bin": bin_name,
                            "Comparator": comparator,
                            "ComparatorLabel": comparator_label,
                            "NPoints": len(group),
                            "MedianProjectionMinusComparator": f"{statistics.median(deltas):.12g}",
                        }
                    )

    write_csv(
        PACKET / "taucore_specificity_galaxy_bin_map.csv",
        [
            "GalaxyName",
            "Class",
            "BinType",
            "Bin",
            "Comparator",
            "ComparatorLabel",
            "NPoints",
            "MedianProjectionMinusComparator",
        ],
        galaxy_bin_rows,
    )

    strata = []
    for bin_type, bin_fn, bin_order in [
        (
            "acceleration",
            lambda point: acceleration_bin(point.a_n_over_a0),
            ["aN/a0<0.1", "0.1<=aN/a0<0.3", "0.3<=aN/a0<1", "aN/a0>=1"],
        ),
        (
            "radius",
            lambda point: radius_bin(point.radius_fraction),
            ["inner_R<0.33Rmax", "middle_0.33-0.67Rmax", "outer_R>=0.67Rmax"],
        ),
    ]:
        for bin_name in bin_order:
            group = [point for point in points if bin_fn(point) == bin_name]
            if not group:
                continue
            for comparator, label in [("mond_simple_mu", "MOND simple-mu"), ("rar_mcgaugh", "Empirical RAR")]:
                a_values = [
                    abs(point.residuals["projection_fixed"]) - abs(point.residuals[comparator])
                    for point in group
                    if point.label == "A"
                ]
                c_values = [
                    abs(point.residuals["projection_fixed"]) - abs(point.residuals[comparator])
                    for point in group
                    if point.label == "C"
                ]
                all_values = a_values + c_values
                strata.append(
                    {
                        "BinType": bin_type,
                        "Bin": bin_name,
                        "Comparator": comparator,
                        "ComparatorLabel": label,
                        "N_A_points": len(a_values),
                        "N_C_points": len(c_values),
                        "MedianProjectionMinusComparator_A": f"{median_or_nan(a_values):.6g}",
                        "MedianProjectionMinusComparator_C": f"{median_or_nan(c_values):.6g}",
                        "Interaction_CminusA": f"{(median_or_nan(c_values) - median_or_nan(a_values)):.6g}",
                        "MedianProjectionMinusComparator_All": f"{median_or_nan(all_values):.6g}",
                    }
                )

    write_csv(
        PACKET / "taucore_specificity_map.csv",
        [
            "BinType",
            "Bin",
            "Comparator",
            "ComparatorLabel",
            "N_A_points",
            "N_C_points",
            "MedianProjectionMinusComparator_A",
            "MedianProjectionMinusComparator_C",
            "Interaction_CminusA",
            "MedianProjectionMinusComparator_All",
        ],
        strata,
    )

    galaxy_strata = []
    for bin_type in ["acceleration", "radius"]:
        bins = sorted({row["Bin"] for row in galaxy_bin_rows if row["BinType"] == bin_type})
        for bin_name in bins:
            for comparator, comparator_label in [("mond_simple_mu", "MOND simple-mu"), ("rar_mcgaugh", "Empirical RAR")]:
                rows = [
                    row
                    for row in galaxy_bin_rows
                    if row["BinType"] == bin_type and row["Bin"] == bin_name and row["Comparator"] == comparator
                ]
                a_values = [
                    float(row["MedianProjectionMinusComparator"])
                    for row in rows
                    if row["Class"] == "A"
                ]
                c_values = [
                    float(row["MedianProjectionMinusComparator"])
                    for row in rows
                    if row["Class"] == "C"
                ]
                if not a_values or not c_values:
                    continue
                interaction = statistics.median(c_values) - statistics.median(a_values)
                galaxy_strata.append(
                    {
                        "BinType": bin_type,
                        "Bin": bin_name,
                        "Comparator": comparator,
                        "ComparatorLabel": comparator_label,
                        "N_A_galaxies": len(a_values),
                        "N_C_galaxies": len(c_values),
                        "MedianProjectionMinusComparator_A": f"{statistics.median(a_values):.6g}",
                        "MedianProjectionMinusComparator_C": f"{statistics.median(c_values):.6g}",
                        "Interaction_CminusA": f"{interaction:.6g}",
                        "MedianProjectionMinusComparator_All": f"{statistics.median(a_values + c_values):.6g}",
                    }
                )

    write_csv(
        PACKET / "taucore_specificity_galaxy_bin_summary.csv",
        [
            "BinType",
            "Bin",
            "Comparator",
            "ComparatorLabel",
            "N_A_galaxies",
            "N_C_galaxies",
            "MedianProjectionMinusComparator_A",
            "MedianProjectionMinusComparator_C",
            "Interaction_CminusA",
            "MedianProjectionMinusComparator_All",
        ],
        galaxy_strata,
    )

    lines = [
        "# Tau Core Specificity Map",
        "",
        "This is a pre-specification scaffold for a Tau Core-vs-MOND/RAR discriminator. It compares pointwise absolute log residuals on the same quality-pass A/C galaxies.",
        "",
        "Definition:",
        "",
        "```text",
        "delta_abs = abs(residual_projection_fixed) - abs(residual_comparator)",
        "interaction = median(delta_abs | C, bin) - median(delta_abs | A, bin)",
        "```",
        "",
        "Negative `delta_abs` means the fixed projection score has smaller absolute residuals than the comparator in that bin. Positive `interaction` means projection loses more ground in disturbed C rows than in regular A rows.",
        "",
        "| Bin type | Bin | Comparator | n A pts | n C pts | median delta A | median delta C | interaction C-A | median delta all |",
        "| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in strata:
        lines.append(
            "| {BinType} | {Bin} | {ComparatorLabel} | {N_A_points} | {N_C_points} | {MedianProjectionMinusComparator_A} | {MedianProjectionMinusComparator_C} | {Interaction_CminusA} | {MedianProjectionMinusComparator_All} |".format(
                **row
            )
        )
    lines.extend(
        [
            "",
            "Galaxy-aggregated companion summary, using each galaxy-bin median as one statistical unit:",
            "",
            "| Bin type | Bin | Comparator | n A gal | n C gal | median delta A | median delta C | interaction C-A | median delta all |",
            "| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for row in galaxy_strata:
        lines.append(
            "| {BinType} | {Bin} | {ComparatorLabel} | {N_A_galaxies} | {N_C_galaxies} | {MedianProjectionMinusComparator_A} | {MedianProjectionMinusComparator_C} | {Interaction_CminusA} | {MedianProjectionMinusComparator_All} |".format(
                **row
            )
        )
    lines.extend(
        [
            "",
            "Reading guide: this table does not yet prove Tau Core specificity. It identifies where a future preregistered test should look for a different residual shape than MOND/RAR: acceleration bins, radius bins, and the A/C interaction of projection-vs-comparator residual differences.",
        ]
    )
    (PACKET / "taucore_specificity_map.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rotmod-dir", type=Path, default=DEFAULT_ROTMOD)
    args = parser.parse_args()
    make_external_evidence_table()
    make_continuous_s_tau_manifest()
    make_baseline_comparisons(args.rotmod_dir)
    make_taucore_specificity_map(args.rotmod_dir)
    make_soft_s_tau_freeze_and_heldout(args.rotmod_dir)


if __name__ == "__main__":
    main()
