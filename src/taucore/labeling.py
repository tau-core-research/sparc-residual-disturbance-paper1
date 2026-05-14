"""Residual-blind coherence-label worksheet generation."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

from taucore.metadata import SparcGalaxyMetadata
from taucore.sparc import SparcRotmodTable


@dataclass(frozen=True)
class LabelDiagnostic:
    galaxy_name: str
    n_points: int
    mean_err_vobs_kms: float
    max_radius_kpc: float
    hubble_type: int | None
    distance_quality: int | None
    inclination_deg: float | None
    inclination_error_deg: float | None
    suggested_class: str
    suggested_proxy: float
    label_confidence: str
    reason: str


def build_label_diagnostic(
    table: SparcRotmodTable,
    metadata: SparcGalaxyMetadata | None = None,
) -> LabelDiagnostic:
    """Build a residual-blind label suggestion from metadata and data quality.

    This is intentionally conservative. It is a worksheet generator, not a
    substitute for human blind labeling from morphology / external catalogs.
    """

    n_points = len(table.rows)
    mean_err = sum(row.err_vobs_kms for row in table.rows) / n_points
    max_radius = max(row.radius_kpc for row in table.rows)
    reasons: list[str] = []
    penalties = 0
    bonuses = 0

    if n_points >= 15:
        bonuses += 1
        reasons.append("many rotation-curve points")
    elif n_points < 8:
        penalties += 2
        reasons.append("few rotation-curve points")

    if mean_err <= 3.0:
        bonuses += 1
        reasons.append("low mean Vobs error")
    elif mean_err >= 8.0:
        penalties += 1
        reasons.append("high mean Vobs error")

    if max_radius >= 8.0:
        bonuses += 1
        reasons.append("extended radial coverage")
    elif max_radius < 3.0:
        penalties += 1
        reasons.append("short radial coverage")

    if metadata is not None:
        inclination = metadata.inclination_deg
        inclination_error = metadata.inclination_error_deg

        if 40.0 <= inclination <= 80.0 and inclination_error <= 5.0:
            bonuses += 1
            reasons.append("well-conditioned inclination")
        elif inclination < 30.0 or inclination > 85.0:
            penalties += 2
            reasons.append("face-on or edge-on inclination risk")
        elif inclination_error >= 10.0:
            penalties += 1
            reasons.append("large inclination uncertainty")

        if metadata.distance_quality <= 3:
            bonuses += 1
            reasons.append("good distance-quality flag")
        elif metadata.distance_quality >= 5:
            penalties += 1
            reasons.append("weak distance-quality flag")

        if 3 <= metadata.hubble_type <= 7:
            bonuses += 1
            reasons.append("disk-like Hubble type")
        elif metadata.hubble_type >= 10:
            penalties += 1
            reasons.append("irregular/dwarf Hubble type")
    else:
        penalties += 1
        reasons.append("missing SPARC Table1 metadata")

    score = bonuses - penalties
    if score >= 4 and penalties == 0:
        suggested_class = "A"
        suggested_proxy = 1.0
        confidence = "Medium"
    elif score <= 0 or penalties >= 3:
        suggested_class = "C"
        suggested_proxy = 0.0
        confidence = "Low"
    else:
        suggested_class = "B"
        suggested_proxy = 0.5
        confidence = "Medium" if penalties <= 1 else "Low"

    return LabelDiagnostic(
        galaxy_name=table.galaxy_name,
        n_points=n_points,
        mean_err_vobs_kms=mean_err,
        max_radius_kpc=max_radius,
        hubble_type=metadata.hubble_type if metadata else None,
        distance_quality=metadata.distance_quality if metadata else None,
        inclination_deg=metadata.inclination_deg if metadata else None,
        inclination_error_deg=metadata.inclination_error_deg if metadata else None,
        suggested_class=suggested_class,
        suggested_proxy=suggested_proxy,
        label_confidence=confidence,
        reason="; ".join(reasons),
    )


def write_label_diagnostics(diagnostics: list[LabelDiagnostic], path: str | Path) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(LabelDiagnostic.__dataclass_fields__)
    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for diagnostic in diagnostics:
            writer.writerow(diagnostic.__dict__)


def write_suggested_label_manifest(diagnostics: list[LabelDiagnostic], path: str | Path) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "GalaxyName",
        "S_tau_class",
        "S_tau_proxy",
        "LabelConfidence",
        "LabelReason",
        "LabelSource",
        "IsBlindLabel",
        "Notes",
    ]
    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for diagnostic in diagnostics:
            writer.writerow(
                {
                    "GalaxyName": diagnostic.galaxy_name,
                    "S_tau_class": diagnostic.suggested_class,
                    "S_tau_proxy": diagnostic.suggested_proxy,
                    "LabelConfidence": diagnostic.label_confidence,
                    "LabelReason": diagnostic.reason,
                    "LabelSource": "rotmod quality + SPARC Table1 metadata; residual-blind worksheet v0.1",
                    "IsBlindLabel": "true",
                    "Notes": "machine suggestion; review before preregistration",
                }
            )


def reviewed_candidate_from_diagnostic(row: dict[str, str]) -> dict[str, str]:
    """Apply conservative residual-blind v0.2 review rules to one diagnostic row."""

    galaxy_name = row["galaxy_name"]
    n_points = int(float(row["n_points"]))
    mean_err = float(row["mean_err_vobs_kms"])
    max_radius = float(row["max_radius_kpc"])
    hubble_type = int(float(row["hubble_type"])) if row["hubble_type"].strip() else 99
    distance_quality = int(float(row["distance_quality"])) if row["distance_quality"].strip() else 9
    inclination = float(row["inclination_deg"]) if row["inclination_deg"].strip() else -1.0
    inclination_error = (
        float(row["inclination_error_deg"]) if row["inclination_error_deg"].strip() else 99.0
    )

    reasons: list[str] = []

    a_conditions = [
        n_points >= 15,
        mean_err <= 6.0,
        max_radius >= 8.0,
        40.0 <= inclination <= 80.0,
        inclination_error <= 5.0,
        distance_quality <= 3,
        3 <= hubble_type <= 7,
    ]
    if all(a_conditions):
        label = "A"
        proxy = "1.0"
        confidence = "Medium"
        reasons.extend(
            [
                "disk-like Hubble type",
                "adequate point count",
                "extended radial coverage",
                "usable inclination geometry",
                "good distance-quality flag",
            ]
        )
    else:
        strong_c_reasons: list[str] = []
        if n_points < 8:
            strong_c_reasons.append("few rotation-curve points")
        if max_radius < 3.0:
            strong_c_reasons.append("short radial coverage")
        if mean_err >= 8.0:
            strong_c_reasons.append("high mean Vobs error")
        if inclination < 30.0 or inclination > 85.0:
            strong_c_reasons.append("face-on or edge-on inclination risk")
        if inclination_error >= 10.0:
            strong_c_reasons.append("large inclination uncertainty")
        if distance_quality >= 5:
            strong_c_reasons.append("weak distance-quality flag")
        if hubble_type >= 10 and (n_points < 12 or max_radius < 6.0):
            strong_c_reasons.append("irregular/dwarf system with limited geometry support")

        if strong_c_reasons:
            label = "C"
            proxy = "0.0"
            confidence = "Medium" if len(strong_c_reasons) >= 2 else "Low"
            reasons.extend(strong_c_reasons)
        else:
            label = "B"
            proxy = "0.5"
            confidence = "Medium"
            reasons.append("mixed or insufficient evidence for A or C")

    return {
        "GalaxyName": galaxy_name,
        "S_tau_class": label,
        "S_tau_proxy": proxy,
        "LabelConfidence": confidence,
        "LabelReason": "; ".join(reasons),
        "LabelSource": "residual-blind internal v0.2 review rules from rotmod quality + SPARC Table1 metadata",
        "IsBlindLabel": "true",
        "Notes": "candidate reviewed-label pass; no TPG residual fields used",
    }


def write_reviewed_candidate_labels(diagnostic_rows: list[dict[str, str]], path: str | Path) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "GalaxyName",
        "S_tau_class",
        "S_tau_proxy",
        "LabelConfidence",
        "LabelReason",
        "LabelSource",
        "IsBlindLabel",
        "Notes",
    ]
    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in diagnostic_rows:
            writer.writerow(reviewed_candidate_from_diagnostic(row))
