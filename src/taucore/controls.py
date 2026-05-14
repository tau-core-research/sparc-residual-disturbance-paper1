"""Quality-control summaries for the SPARC coherence pilot."""

from __future__ import annotations

import csv
import json
import statistics
from dataclasses import dataclass
from pathlib import Path

from taucore.coherence import (
    BinaryComparisonResult,
    LabelGroupResult,
    binary_comparison,
    compare_label_groups,
    grouped_metric_values,
    trend_test,
)


@dataclass(frozen=True)
class JoinedGalaxyRow:
    galaxy_name: str
    label: str
    rms_log_tpg: float
    weighted_rms_log_tpg: float
    outer_mean_log_residual_tpg: float
    n_points: int
    mean_err_vobs_kms: float
    max_radius_kpc: float
    inclination_deg: float | None
    inclination_error_deg: float | None
    hubble_type: int | None
    distance_quality: int | None


@dataclass(frozen=True)
class QualityThresholds:
    min_points: int = 8
    max_mean_err_vobs_kms: float = 6.0
    min_inclination_deg: float = 30.0
    max_inclination_deg: float = 85.0
    max_inclination_error_deg: float = 10.0


@dataclass(frozen=True)
class QualityGroupSummary:
    label: str
    n: int
    median_n_points: float
    median_mean_err_vobs_kms: float
    median_max_radius_kpc: float
    median_inclination_error_deg: float


@dataclass(frozen=True)
class LeaveOneOutInfluence:
    removed_galaxy: str
    removed_label: str
    base_difference: float
    difference_after_removal: float
    absolute_change: float
    sign_preserved: bool


@dataclass(frozen=True)
class ThresholdSensitivityRow:
    min_points: int
    max_mean_err_vobs_kms: float
    quality_passed: int
    n_a: int
    n_b: int
    n_c: int
    c_minus_nonc_diff: float
    c_minus_nonc_sign_positive: bool
    trend_spearman: float


@dataclass(frozen=True)
class ControlledReport:
    total_matched: int
    quality_passed: int
    quality_failed: int
    thresholds: QualityThresholds
    quality_group_summaries: list[QualityGroupSummary]
    quality_pass_groups: list[LabelGroupResult]
    quality_pass_comparisons: list[BinaryComparisonResult]
    quality_pass_trend_spearman: float
    quality_pass_trend_p: float
    quality_pass_c_minus_nonc_leave_one_out: list[LeaveOneOutInfluence]


def _optional_float(value: str) -> float | None:
    value = value.strip()
    return float(value) if value else None


def _optional_int(value: str) -> int | None:
    value = value.strip()
    return int(float(value)) if value else None


def read_diagnostics(path: str | Path) -> dict[str, dict[str, str]]:
    with Path(path).open(newline="", encoding="utf-8") as handle:
        return {row["galaxy_name"]: row for row in csv.DictReader(handle)}


def join_control_rows(
    residual_rows: dict[str, dict[str, str]],
    label_rows: dict[str, dict[str, str]],
    diagnostic_rows: dict[str, dict[str, str]],
) -> list[JoinedGalaxyRow]:
    joined: list[JoinedGalaxyRow] = []
    for galaxy_name, label_row in label_rows.items():
        residual_row = residual_rows.get(galaxy_name)
        diagnostic_row = diagnostic_rows.get(galaxy_name)
        if residual_row is None or diagnostic_row is None:
            continue
        joined.append(
            JoinedGalaxyRow(
                galaxy_name=galaxy_name,
                label=label_row["S_tau_class"].strip().upper(),
                rms_log_tpg=float(residual_row["rms_log_tpg"]),
                weighted_rms_log_tpg=float(residual_row["weighted_rms_log_tpg"]),
                outer_mean_log_residual_tpg=float(residual_row["outer_mean_log_residual_tpg"]),
                n_points=int(float(diagnostic_row["n_points"])),
                mean_err_vobs_kms=float(diagnostic_row["mean_err_vobs_kms"]),
                max_radius_kpc=float(diagnostic_row["max_radius_kpc"]),
                inclination_deg=_optional_float(diagnostic_row["inclination_deg"]),
                inclination_error_deg=_optional_float(diagnostic_row["inclination_error_deg"]),
                hubble_type=_optional_int(diagnostic_row["hubble_type"]),
                distance_quality=_optional_int(diagnostic_row["distance_quality"]),
            )
        )
    return joined


def passes_quality(row: JoinedGalaxyRow, thresholds: QualityThresholds) -> bool:
    if row.n_points < thresholds.min_points:
        return False
    if row.mean_err_vobs_kms > thresholds.max_mean_err_vobs_kms:
        return False
    if row.inclination_deg is None or row.inclination_error_deg is None:
        return False
    if row.inclination_deg < thresholds.min_inclination_deg:
        return False
    if row.inclination_deg > thresholds.max_inclination_deg:
        return False
    if row.inclination_error_deg > thresholds.max_inclination_error_deg:
        return False
    return True


def quality_group_summaries(rows: list[JoinedGalaxyRow]) -> list[QualityGroupSummary]:
    summaries: list[QualityGroupSummary] = []
    labels = sorted({row.label for row in rows})
    for label in labels:
        group = [row for row in rows if row.label == label]
        inc_errors = [row.inclination_error_deg for row in group if row.inclination_error_deg is not None]
        summaries.append(
            QualityGroupSummary(
                label=label,
                n=len(group),
                median_n_points=statistics.median(row.n_points for row in group),
                median_mean_err_vobs_kms=statistics.median(row.mean_err_vobs_kms for row in group),
                median_max_radius_kpc=statistics.median(row.max_radius_kpc for row in group),
                median_inclination_error_deg=statistics.median(inc_errors) if inc_errors else float("nan"),
            )
        )
    return summaries


def _rows_to_residual_and_label_dicts(
    rows: list[JoinedGalaxyRow],
) -> tuple[dict[str, dict[str, str]], dict[str, dict[str, str]]]:
    residual_rows = {
        row.galaxy_name: {
            "galaxy_name": row.galaxy_name,
            "rms_log_tpg": str(row.rms_log_tpg),
            "weighted_rms_log_tpg": str(row.weighted_rms_log_tpg),
            "outer_mean_log_residual_tpg": str(row.outer_mean_log_residual_tpg),
        }
        for row in rows
    }
    label_rows = {
        row.galaxy_name: {
            "GalaxyName": row.galaxy_name,
            "S_tau_class": row.label,
        }
        for row in rows
    }
    return residual_rows, label_rows


def median_difference_for_rows(
    rows: list[JoinedGalaxyRow],
    left_labels: set[str],
    right_labels: set[str],
    metric: str = "rms_log_tpg",
) -> float:
    left = [getattr(row, metric) for row in rows if row.label in left_labels]
    right = [getattr(row, metric) for row in rows if row.label in right_labels]
    if not left or not right:
        return float("nan")
    return statistics.median(right) - statistics.median(left)


def leave_one_out_influence(
    rows: list[JoinedGalaxyRow],
    left_labels: set[str],
    right_labels: set[str],
    metric: str = "rms_log_tpg",
) -> list[LeaveOneOutInfluence]:
    base = median_difference_for_rows(rows, left_labels, right_labels, metric=metric)
    influences: list[LeaveOneOutInfluence] = []
    for row in rows:
        reduced = [candidate for candidate in rows if candidate.galaxy_name != row.galaxy_name]
        after = median_difference_for_rows(reduced, left_labels, right_labels, metric=metric)
        influences.append(
            LeaveOneOutInfluence(
                removed_galaxy=row.galaxy_name,
                removed_label=row.label,
                base_difference=base,
                difference_after_removal=after,
                absolute_change=abs(after - base),
                sign_preserved=(base > 0 and after > 0) or (base < 0 and after < 0) or base == after,
            )
        )

    return sorted(influences, key=lambda item: item.absolute_change, reverse=True)


def build_controlled_report(
    rows: list[JoinedGalaxyRow],
    thresholds: QualityThresholds = QualityThresholds(),
    permutations: int = 10000,
    bootstrap: int = 2000,
    seed: int = 12345,
) -> ControlledReport:
    passed = [row for row in rows if passes_quality(row, thresholds)]
    residual_rows, label_rows = _rows_to_residual_and_label_dicts(passed)
    grouped = grouped_metric_values(residual_rows, label_rows)
    trend = trend_test(grouped, permutations=permutations, seed=seed + 3)

    comparisons = [
        binary_comparison(
            grouped,
            name="nonA_minus_A",
            left_labels={"A"},
            right_labels={"B", "C"},
            permutations=permutations,
            bootstrap=bootstrap,
            seed=seed,
        ),
        binary_comparison(
            grouped,
            name="C_minus_nonC",
            left_labels={"A", "B"},
            right_labels={"C"},
            permutations=permutations,
            bootstrap=bootstrap,
            seed=seed + 1,
        ),
        binary_comparison(
            grouped,
            name="C_minus_A",
            left_labels={"A"},
            right_labels={"C"},
            permutations=permutations,
            bootstrap=bootstrap,
            seed=seed + 2,
        ),
    ]

    return ControlledReport(
        total_matched=len(rows),
        quality_passed=len(passed),
        quality_failed=len(rows) - len(passed),
        thresholds=thresholds,
        quality_group_summaries=quality_group_summaries(rows),
        quality_pass_groups=compare_label_groups(residual_rows, label_rows),
        quality_pass_comparisons=comparisons,
        quality_pass_trend_spearman=trend.spearman_rho_label_order,
        quality_pass_trend_p=trend.permutation_p_one_sided,
        quality_pass_c_minus_nonc_leave_one_out=leave_one_out_influence(
            passed,
            left_labels={"A", "B"},
            right_labels={"C"},
        ),
    )


def write_controlled_report_json(report: ControlledReport, path: str | Path) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "total_matched": report.total_matched,
        "quality_passed": report.quality_passed,
        "quality_failed": report.quality_failed,
        "thresholds": report.thresholds.__dict__,
        "quality_group_summaries": [row.__dict__ for row in report.quality_group_summaries],
        "quality_pass_groups": [row.__dict__ for row in report.quality_pass_groups],
        "quality_pass_comparisons": [row.__dict__ for row in report.quality_pass_comparisons],
        "quality_pass_trend": {
            "spearman_rho_label_order": report.quality_pass_trend_spearman,
            "permutation_p_one_sided": report.quality_pass_trend_p,
        },
        "quality_pass_c_minus_nonc_leave_one_out": [
            row.__dict__ for row in report.quality_pass_c_minus_nonc_leave_one_out
        ],
    }
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def threshold_sensitivity_grid(
    rows: list[JoinedGalaxyRow],
    min_points_values: list[int],
    max_mean_err_values: list[float],
    base_thresholds: QualityThresholds = QualityThresholds(),
) -> list[ThresholdSensitivityRow]:
    grid_rows: list[ThresholdSensitivityRow] = []
    for min_points in min_points_values:
        for max_mean_err in max_mean_err_values:
            thresholds = QualityThresholds(
                min_points=min_points,
                max_mean_err_vobs_kms=max_mean_err,
                min_inclination_deg=base_thresholds.min_inclination_deg,
                max_inclination_deg=base_thresholds.max_inclination_deg,
                max_inclination_error_deg=base_thresholds.max_inclination_error_deg,
            )
            passed = [row for row in rows if passes_quality(row, thresholds)]
            counts = {label: sum(row.label == label for row in passed) for label in ("A", "B", "C")}
            diff = median_difference_for_rows(passed, left_labels={"A", "B"}, right_labels={"C"})
            residual_rows, label_rows = _rows_to_residual_and_label_dicts(passed)
            grouped = grouped_metric_values(residual_rows, label_rows)
            trend = trend_test(grouped, permutations=1000, seed=12345)
            grid_rows.append(
                ThresholdSensitivityRow(
                    min_points=min_points,
                    max_mean_err_vobs_kms=max_mean_err,
                    quality_passed=len(passed),
                    n_a=counts["A"],
                    n_b=counts["B"],
                    n_c=counts["C"],
                    c_minus_nonc_diff=diff,
                    c_minus_nonc_sign_positive=diff > 0,
                    trend_spearman=trend.spearman_rho_label_order,
                )
            )
    return grid_rows


def write_threshold_sensitivity_csv(rows: list[ThresholdSensitivityRow], path: str | Path) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(ThresholdSensitivityRow.__dataclass_fields__)
    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row.__dict__)
