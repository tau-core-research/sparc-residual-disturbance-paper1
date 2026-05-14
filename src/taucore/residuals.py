"""Residual calculations for the SPARC Tau Core pilot."""

from __future__ import annotations

import csv
import math
from dataclasses import dataclass
from pathlib import Path

from taucore.galaxy_activation import (
    DEFAULT_A0_M_S2,
    DEFAULT_ALPHA,
    DEFAULT_UPSILON_BULGE,
    DEFAULT_UPSILON_DISK,
    acceleration_m_s2,
    baryonic_speed_squared_kms2,
    predicted_speed_kms,
    tpg_factor,
)
from taucore.sparc import SparcRotmodTable


@dataclass(frozen=True)
class ResidualPoint:
    galaxy_name: str
    radius_kpc: float
    vobs_kms: float
    err_vobs_kms: float
    vn_kms: float
    a_n_m_s2: float
    factor_tpg: float
    vpred_kms: float
    log_residual: float


@dataclass(frozen=True)
class GalaxyResidualSummary:
    galaxy_name: str
    n_points: int
    rms_log_tpg: float
    weighted_rms_log_tpg: float
    mean_log_residual_tpg: float
    outer_mean_log_residual_tpg: float
    min_radius_kpc: float
    max_radius_kpc: float
    mean_err_vobs_kms: float


def compute_residual_points(
    table: SparcRotmodTable,
    alpha: float = DEFAULT_ALPHA,
    a0_m_s2: float = DEFAULT_A0_M_S2,
    upsilon_disk: float = DEFAULT_UPSILON_DISK,
    upsilon_bulge: float = DEFAULT_UPSILON_BULGE,
    s_tau: float = 1.0,
) -> list[ResidualPoint]:
    points: list[ResidualPoint] = []

    for row in table.rows:
        vn2 = baryonic_speed_squared_kms2(
            row.vgas_kms,
            row.vdisk_kms,
            row.vbul_kms,
            upsilon_disk=upsilon_disk,
            upsilon_bulge=upsilon_bulge,
        )
        a_n = acceleration_m_s2(vn2, row.radius_kpc)
        factor = tpg_factor(a_n, alpha=alpha, a0_m_s2=a0_m_s2, s_tau=s_tau)
        vpred = predicted_speed_kms(vn2, factor)

        if row.vobs_kms <= 0 or vpred <= 0 or not math.isfinite(vpred):
            continue

        points.append(
            ResidualPoint(
                galaxy_name=table.galaxy_name,
                radius_kpc=row.radius_kpc,
                vobs_kms=row.vobs_kms,
                err_vobs_kms=row.err_vobs_kms,
                vn_kms=math.sqrt(vn2),
                a_n_m_s2=a_n,
                factor_tpg=factor,
                vpred_kms=vpred,
                log_residual=math.log(row.vobs_kms / vpred),
            )
        )

    return points


def summarize_galaxy(points: list[ResidualPoint]) -> GalaxyResidualSummary:
    if not points:
        raise ValueError("Cannot summarize an empty residual point list.")

    residuals = [point.log_residual for point in points]
    weights = [1.0 / (point.err_vobs_kms**2) for point in points if point.err_vobs_kms > 0]
    weighted_residuals = [
        (point.log_residual, 1.0 / (point.err_vobs_kms**2))
        for point in points
        if point.err_vobs_kms > 0
    ]

    rms = math.sqrt(sum(residual * residual for residual in residuals) / len(residuals))
    if weighted_residuals and sum(weights) > 0:
        weighted_rms = math.sqrt(
            sum(weight * residual * residual for residual, weight in weighted_residuals) / sum(weights)
        )
    else:
        weighted_rms = math.nan

    sorted_points = sorted(points, key=lambda point: point.radius_kpc)
    outer_start = max(0, math.floor(len(sorted_points) * 2 / 3))
    outer = sorted_points[outer_start:]

    return GalaxyResidualSummary(
        galaxy_name=points[0].galaxy_name,
        n_points=len(points),
        rms_log_tpg=rms,
        weighted_rms_log_tpg=weighted_rms,
        mean_log_residual_tpg=sum(residuals) / len(residuals),
        outer_mean_log_residual_tpg=sum(point.log_residual for point in outer) / len(outer),
        min_radius_kpc=min(point.radius_kpc for point in points),
        max_radius_kpc=max(point.radius_kpc for point in points),
        mean_err_vobs_kms=sum(point.err_vobs_kms for point in points) / len(points),
    )


def summarize_tables(tables: list[SparcRotmodTable]) -> list[GalaxyResidualSummary]:
    summaries: list[GalaxyResidualSummary] = []
    for table in tables:
        points = compute_residual_points(table)
        if points:
            summaries.append(summarize_galaxy(points))
    return summaries


def write_summary_csv(summaries: list[GalaxyResidualSummary], path: str | Path) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(GalaxyResidualSummary.__dataclass_fields__)

    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for summary in summaries:
            writer.writerow(summary.__dict__)

