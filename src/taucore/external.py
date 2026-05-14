"""External proxy manifest helpers for SPARC label enrichment."""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ExternalProxyReadiness:
    total: int
    partial_disturbance: int
    minimal_ready: int
    extended_ready: int
    source_locked: int


EXTERNAL_PROXY_FIELDNAMES = [
    "GalaxyName",
    "HIAsymmetry",
    "HIAsymmetrySource",
    "VelocityFieldLopsidedness",
    "VelocityFieldLopsidednessSource",
    "BarOrWarpFlag",
    "BarOrWarpSource",
    "InteractionFlag",
    "InteractionSource",
    "NearNeighborDensity",
    "EnvironmentSource",
    "GroupEnvironmentFlag",
    "SourceLockedBeforeFit",
    "ExternalProxyStatus",
    "Notes",
]

LABEL_FIELDNAMES = [
    "GalaxyName",
    "S_tau_class",
    "S_tau_proxy",
    "LabelConfidence",
    "LabelReason",
    "LabelSource",
    "IsBlindLabel",
    "Notes",
]


def read_external_proxy_manifest(path: str | Path) -> list[dict[str, str]]:
    with Path(path).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _present(row: dict[str, str], field: str) -> bool:
    return bool(row.get(field, "").strip())


def _trueish(row: dict[str, str], field: str) -> bool:
    return row.get(field, "").strip().lower() in {"1", "true", "yes", "y"}


def summarize_external_proxy_readiness(rows: list[dict[str, str]]) -> ExternalProxyReadiness:
    partial = 0
    minimal = 0
    extended = 0
    locked = 0
    for row in rows:
        has_disturbance = any(
            _present(row, field)
            for field in (
                "HIAsymmetry",
                "VelocityFieldLopsidedness",
                "BarOrWarpFlag",
                "InteractionFlag",
            )
        )
        has_environment = _present(row, "NearNeighborDensity") or _present(row, "GroupEnvironmentFlag")
        is_locked = _trueish(row, "SourceLockedBeforeFit")
        partial += int(has_disturbance)
        minimal += int(has_disturbance and is_locked)
        extended += int(has_disturbance and has_environment and is_locked)
        locked += int(is_locked)

    return ExternalProxyReadiness(
        total=len(rows),
        partial_disturbance=partial,
        minimal_ready=minimal,
        extended_ready=extended,
        source_locked=locked,
    )


def write_external_readiness_json(readiness: ExternalProxyReadiness, path: str | Path) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(readiness.__dict__, indent=2), encoding="utf-8")


def write_blank_external_proxy_manifest(galaxy_names: list[str], path: str | Path) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=EXTERNAL_PROXY_FIELDNAMES, lineterminator="\n")
        writer.writeheader()
        for galaxy_name in galaxy_names:
            writer.writerow(
                {
                    "GalaxyName": galaxy_name,
                    "SourceLockedBeforeFit": "false",
                    "ExternalProxyStatus": "missing",
                    "Notes": "external proxy fields pending",
                }
            )


def normalize_external_proxy_row(row: dict[str, str]) -> dict[str, str]:
    """Normalize current and legacy external-manifest column names."""

    aliases = {
        "GalaxyName": ["GalaxyName", "galaxy"],
        "HIAsymmetry": ["HIAsymmetry", "hi_asymmetry_external"],
        "HIAsymmetrySource": ["HIAsymmetrySource", "disturbance_source_reference"],
        "VelocityFieldLopsidedness": [
            "VelocityFieldLopsidedness",
            "velocity_field_lopsidedness_external",
        ],
        "VelocityFieldLopsidednessSource": [
            "VelocityFieldLopsidednessSource",
            "disturbance_source_reference",
        ],
        "BarOrWarpFlag": ["BarOrWarpFlag", "bar_or_warp_flag_external"],
        "BarOrWarpSource": ["BarOrWarpSource", "source_reference", "proxy_source_reference"],
        "InteractionFlag": ["InteractionFlag", "whisp_interaction_flag_external"],
        "InteractionSource": ["InteractionSource", "disturbance_source_reference"],
        "NearNeighborDensity": ["NearNeighborDensity", "near_neighbor_density_external"],
        "EnvironmentSource": ["EnvironmentSource", "environment_source", "proxy_source_reference"],
        "GroupEnvironmentFlag": ["GroupEnvironmentFlag", "group_environment_flag_external"],
        "SourceLockedBeforeFit": ["SourceLockedBeforeFit", "source_locked_before_fit"],
        "ExternalProxyStatus": [
            "ExternalProxyStatus",
            "external_proxy_status",
            "disturbance_proxy_status",
        ],
        "Notes": ["Notes", "notes"],
    }
    normalized = {}
    for target, candidates in aliases.items():
        normalized[target] = next(
            (row.get(candidate, "").strip() for candidate in candidates if row.get(candidate, "").strip()),
            "",
        )
    return normalized


def _numeric_state(value: str, high_threshold: float) -> str:
    stripped = value.strip().lower()
    if not stripped:
        return "unknown"
    if stripped in {"1", "true", "yes", "y", "high", "disturbed", "barred", "warp", "group"}:
        return "disturbed"
    if stripped in {"0", "false", "no", "n", "low", "clean", "isolated", "none"}:
        return "calm"
    try:
        return "disturbed" if float(stripped) >= high_threshold else "calm"
    except ValueError:
        return "unknown"


def external_proxy_label_from_manifest(row: dict[str, str]) -> dict[str, str]:
    """Create a residual-blind label from source-locked external proxy fields."""

    normalized = normalize_external_proxy_row(row)
    galaxy_name = normalized["GalaxyName"]
    source_locked = normalized["SourceLockedBeforeFit"].lower() in {"1", "true", "yes", "y"}
    states = {
        "HI asymmetry": _numeric_state(normalized["HIAsymmetry"], high_threshold=0.2),
        "velocity-field lopsidedness": _numeric_state(
            normalized["VelocityFieldLopsidedness"], high_threshold=0.1
        ),
        "bar/warp flag": _numeric_state(normalized["BarOrWarpFlag"], high_threshold=0.5),
        "interaction flag": _numeric_state(normalized["InteractionFlag"], high_threshold=0.5),
        "near-neighbor density": _numeric_state(
            normalized["NearNeighborDensity"], high_threshold=3.0
        ),
        "group environment": _numeric_state(normalized["GroupEnvironmentFlag"], high_threshold=0.5),
    }
    disturbed = [name for name, state in states.items() if state == "disturbed"]
    calm = [name for name, state in states.items() if state == "calm"]

    if not source_locked:
        label = "B"
        proxy = "0.5"
        confidence = "Low"
        reason = "external proxy source is not locked before residual comparison"
    elif "interaction flag" in disturbed:
        label = "C"
        proxy = "0.0"
        confidence = "High"
        reason = "external interaction flag present"
    elif len(disturbed) >= 2:
        label = "C"
        proxy = "0.0"
        confidence = "Medium"
        reason = "multiple external disturbance proxies present: " + "; ".join(disturbed)
    elif len(calm) >= 3 and not disturbed:
        label = "A"
        proxy = "1.0"
        confidence = "Medium"
        reason = "multiple external calm proxies present: " + "; ".join(calm)
    else:
        label = "B"
        proxy = "0.5"
        confidence = "Medium" if disturbed or calm else "Low"
        reason = "external proxy evidence is mixed or incomplete"

    return {
        "GalaxyName": galaxy_name,
        "S_tau_class": label,
        "S_tau_proxy": proxy,
        "LabelConfidence": confidence,
        "LabelReason": reason,
        "LabelSource": "residual-blind external proxy manifest v0.2",
        "IsBlindLabel": "true",
        "Notes": normalized["Notes"],
    }


def write_external_proxy_labels(rows: list[dict[str, str]], path: str | Path) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=LABEL_FIELDNAMES, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow(external_proxy_label_from_manifest(row))
