#!/usr/bin/env python3
"""Build selection-function notes and controlled regression checks for Paper 1."""

from __future__ import annotations

import csv
import math
import random
import statistics
import sys
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from taucore.coherence import read_coherence_labels, read_residual_summary
from taucore.controls import QualityThresholds, join_control_rows, passes_quality, read_diagnostics
from taucore.metadata import parse_sparc_table1


STUDY = ROOT / "studies/sparc_residual_coherence_test_v01"
PACKET = STUDY / "paper_packet_v06_distance_balanced"
OUTPUTS = ROOT / "outputs/external_proxy_v06_distance_balanced"
LABELS = STUDY / "coherence_labels_v06_distance_balanced.csv"
SPARC_TABLE1 = ROOT / "data/external/SPARC_Table1.txt"
HECATE = ROOT / "outputs/hecate_crossmatch_summary.csv"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def fnum(value: str | None) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except ValueError:
        return None


def median(values: list[float]) -> float:
    return statistics.median(values) if values else math.nan


def permutation_p_greater(c_values: list[float], a_values: list[float], seed: int, iterations: int = 10000) -> float:
    if not c_values or not a_values:
        return math.nan
    observed = median(c_values) - median(a_values)
    pooled = c_values + a_values
    n_c = len(c_values)
    rng = random.Random(seed)
    hits = 1
    for _ in range(iterations):
        sample = pooled[:]
        rng.shuffle(sample)
        diff = median(sample[:n_c]) - median(sample[n_c:])
        if diff >= observed:
            hits += 1
    return hits / (iterations + 1)


def quality_rows() -> list[dict[str, object]]:
    metadata = parse_sparc_table1(SPARC_TABLE1)
    hecate = {row["GalaxyName"]: row for row in read_csv(HECATE)} if HECATE.exists() else {}
    joined = join_control_rows(
        read_residual_summary(OUTPUTS / "sparc_residual_summary.csv"),
        read_coherence_labels(LABELS),
        read_diagnostics(OUTPUTS / "coherence_label_diagnostics.csv"),
    )
    rows: list[dict[str, object]] = []
    for row in joined:
        if not passes_quality(row, QualityThresholds()):
            continue
        meta = metadata.get(row.galaxy_name)
        h = hecate.get(row.galaxy_name, {})
        rows.append(
            {
                "GalaxyName": row.galaxy_name,
                "Class": row.label,
                "RmsLog": row.rms_log_tpg,
                "NPoints": row.n_points,
                "MeanErrVobsKms": row.mean_err_vobs_kms,
                "MaxRadiusKpc": row.max_radius_kpc,
                "InclinationDeg": row.inclination_deg,
                "InclinationErrorDeg": row.inclination_error_deg,
                "HubbleType": row.hubble_type,
                "DistanceMpc": meta.distance_mpc if meta else math.nan,
                "DistanceErrorMpc": meta.distance_error_mpc if meta else math.nan,
                "DistanceQuality": row.distance_quality,
                "HecateDistanceMpc": fnum(h.get("HecateDistanceMpc")),
                "HecateMorphT": fnum(h.get("HecateMorphT")),
                "HecateStellarMassLog": fnum(h.get("HecateStellarMassLog")),
            }
        )
    return rows


def dwarf_like(row: dict[str, object]) -> bool:
    value = row.get("HubbleType")
    return isinstance(value, (int, float)) and value >= 8


def make_selection_appendix(rows: list[dict[str, object]]) -> None:
    covariates = [
        ("DistanceMpc", "SPARC distance [Mpc]"),
        ("DistanceErrorMpc", "SPARC distance uncertainty [Mpc]"),
        ("MaxRadiusKpc", "maximum fitted rotation-curve radius [kpc]"),
        ("NPoints", "rotation-curve point count"),
        ("MeanErrVobsKms", "mean Vobs uncertainty [km/s]"),
        ("InclinationDeg", "inclination [deg]"),
        ("InclinationErrorDeg", "inclination uncertainty [deg]"),
        ("HubbleType", "SPARC Hubble type code"),
        ("HecateStellarMassLog", "HECATE log stellar mass"),
    ]
    classes = ["A", "B", "C"]
    summary_rows: list[dict[str, object]] = []
    for key, description in covariates:
        for klass in classes:
            values = [
                float(row[key])
                for row in rows
                if row["Class"] == klass and row.get(key) is not None and math.isfinite(float(row[key]))
            ]
            summary_rows.append(
                {
                    "Covariate": key,
                    "Description": description,
                    "Class": klass,
                    "N": len(values),
                    "Median": f"{median(values):.6g}" if values else "",
                }
            )
    write_csv(
        PACKET / "selection_observability_summary.csv",
        ["Covariate", "Description", "Class", "N", "Median"],
        summary_rows,
    )

    a_rows = [row for row in rows if row["Class"] == "A"]
    c_rows = [row for row in rows if row["Class"] == "C"]
    dwarf_a = sum(1 for row in a_rows if dwarf_like(row))
    dwarf_c = sum(1 for row in c_rows if dwarf_like(row))
    whisp_matches = {row["GalaxyName"] for row in read_csv(PACKET / "s_tau_source_matches.csv") if row["Source"].startswith("whisp")}
    whisp_a = sum(1 for row in a_rows if row["GalaxyName"] in whisp_matches)
    whisp_c = sum(1 for row in c_rows if row["GalaxyName"] in whisp_matches)

    lines = [
        "# Selection / Observability Appendix",
        "",
        "This appendix addresses the main reviewer-facing selection-function risk: nearby or better-resolved galaxies may reveal structural disturbance more easily than distant systems. The table below is descriptive rather than a new primary endpoint.",
        "",
        "## Available Observability Proxies",
        "",
        "| proxy | role | status |",
        "| --- | --- | --- |",
        "| SPARC distance | first-order observability and physical-resolution proxy | available for all quality-pass rows |",
        "| maximum rotation-curve radius | radial-coverage / scale proxy | available for all quality-pass rows |",
        "| rotation-curve point count | sampling-density proxy | available for all quality-pass rows |",
        "| mean Vobs uncertainty | kinematic measurement-quality proxy | available for all quality-pass rows |",
        "| inclination and inclination uncertainty | projection-geometry proxy | available for all quality-pass rows after quality gate |",
        "| Hubble type | dwarf/late-type composition proxy | available for all quality-pass rows |",
        "| HECATE stellar mass | mass proxy | incomplete; use only as supportive control |",
        "| HI beam size / physical HI resolution | direct beam-smearing proxy | not present in the current SPARC packet |",
        "| homogeneous resolved HI morphology | direct disturbance observability proxy | partial WHISP-family coverage only |",
        "",
        "## Median Balance Summary",
        "",
        "| covariate | n A | median A | n B | median B | n C | median C |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    by_cov = {}
    for row in summary_rows:
        by_cov.setdefault(row["Covariate"], {})[row["Class"]] = row
    descriptions = {key: description for key, description in covariates}
    for key, _description in covariates:
        a = by_cov[key].get("A", {})
        b = by_cov[key].get("B", {})
        c = by_cov[key].get("C", {})
        lines.append(
            f"| {descriptions[key]} | {a.get('N', 0)} | {a.get('Median', '')} | "
            f"{b.get('N', 0)} | {b.get('Median', '')} | {c.get('N', 0)} | {c.get('Median', '')} |"
        )
    lines.extend(
        [
            "",
            "## Composition Checks",
            "",
            f"- Late-type/dwarf-like proxy (`HubbleType >= 8`): A={dwarf_a}/{len(a_rows)}, C={dwarf_c}/{len(c_rows)}.",
            f"- WHISP-family external HI morphology coverage in quality-pass A/C: A={whisp_a}/{len(a_rows)}, C={whisp_c}/{len(c_rows)}.",
            "",
            "## Interpretation",
            "",
            "The appendix strengthens the paper by making the selection risk explicit rather than burying it in limitations. Distance and radius remain the strongest imbalances, so they should stay in the main text as limitations. The current packet does not include homogeneous beam-size or physical HI-resolution measurements; therefore the paper should not claim that beam smearing or disturbance observability is fully controlled.",
        ]
    )
    (PACKET / "selection_observability_appendix.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def standardize(values: np.ndarray) -> np.ndarray:
    mean = float(np.mean(values))
    std = float(np.std(values, ddof=1))
    if std == 0 or not math.isfinite(std):
        return values * 0.0
    return (values - mean) / std


def regression_matrix(rows: list[dict[str, object]], covariates: list[str]) -> tuple[np.ndarray, np.ndarray, list[str], list[str]]:
    usable = []
    for row in rows:
        if row["Class"] not in {"A", "C"}:
            continue
        if all(row.get(key) is not None and math.isfinite(float(row[key])) for key in covariates):
            usable.append(row)
    y = np.array([float(row["RmsLog"]) for row in usable], dtype=float)
    columns = [np.ones(len(usable)), np.array([1.0 if row["Class"] == "C" else 0.0 for row in usable])]
    names = ["Intercept", "Class_C_vs_A"]
    for key in covariates:
        raw = np.array([float(row[key]) for row in usable], dtype=float)
        if key in {"DistanceMpc", "MaxRadiusKpc"}:
            raw = np.log(np.maximum(raw, 1e-9))
            name = f"log_{key}"
        else:
            name = key
        columns.append(standardize(raw))
        names.append(name)
    return y, np.column_stack(columns), names, [str(row["GalaxyName"]) for row in usable]


def ols_beta(y: np.ndarray, x: np.ndarray) -> np.ndarray:
    return np.linalg.lstsq(x, y, rcond=None)[0]


def huber_beta(y: np.ndarray, x: np.ndarray, tuning: float = 1.345, max_iter: int = 100) -> np.ndarray:
    beta = ols_beta(y, x)
    for _ in range(max_iter):
        residual = y - x @ beta
        scale = 1.4826 * np.median(np.abs(residual - np.median(residual)))
        if not math.isfinite(scale) or scale <= 1e-12:
            scale = float(np.std(residual, ddof=1))
        if not math.isfinite(scale) or scale <= 1e-12:
            return beta
        scaled = np.abs(residual) / scale
        weights = np.ones_like(scaled)
        mask = scaled > tuning
        weights[mask] = tuning / scaled[mask]
        xw = x * np.sqrt(weights[:, None])
        yw = y * np.sqrt(weights)
        next_beta = ols_beta(yw, xw)
        if np.max(np.abs(next_beta - beta)) < 1e-10:
            return next_beta
        beta = next_beta
    return beta


def permutation_class_p(y: np.ndarray, x: np.ndarray, seed: int, iterations: int = 2000) -> float:
    observed = huber_beta(y, x)[1]
    rng = np.random.default_rng(seed)
    class_col = x[:, 1].copy()
    hits = 1
    for _ in range(iterations):
        xp = x.copy()
        xp[:, 1] = rng.permutation(class_col)
        beta = huber_beta(y, xp)[1]
        if beta >= observed:
            hits += 1
    return hits / (iterations + 1)


def bootstrap_ci(y: np.ndarray, x: np.ndarray, seed: int, iterations: int = 2000) -> tuple[float, float]:
    rng = np.random.default_rng(seed)
    n = len(y)
    values = []
    for _ in range(iterations):
        idx = rng.integers(0, n, n)
        try:
            values.append(float(huber_beta(y[idx], x[idx])[1]))
        except np.linalg.LinAlgError:
            continue
    values.sort()
    if not values:
        return math.nan, math.nan
    return values[int(0.025 * len(values))], values[int(0.975 * len(values))]


def make_regression(rows: list[dict[str, object]]) -> None:
    specs = [
        (
            "class_only",
            [],
            "A/C quality-pass rows without covariates; robust regression analogue of a class contrast",
        ),
        (
            "distance_only",
            ["DistanceMpc"],
            "A/C quality-pass rows adjusted for SPARC distance only",
        ),
        (
            "distance_radius",
            ["DistanceMpc", "MaxRadiusKpc"],
            "A/C quality-pass rows adjusted for distance and radial coverage",
        ),
        (
            "distance_radius_quality",
            ["DistanceMpc", "MaxRadiusKpc", "NPoints", "MeanErrVobsKms"],
            "A/C quality-pass rows adjusted for distance, radius, and rotation-curve sampling/uncertainty",
        ),
        (
            "observability_core",
            [
                "DistanceMpc",
                "MaxRadiusKpc",
                "NPoints",
                "MeanErrVobsKms",
                "InclinationDeg",
                "InclinationErrorDeg",
                "HubbleType",
            ],
            "A/C quality-pass rows with SPARC observability covariates",
        ),
        (
            "mass_subset",
            [
                "DistanceMpc",
                "MaxRadiusKpc",
                "NPoints",
                "MeanErrVobsKms",
                "InclinationDeg",
                "InclinationErrorDeg",
                "HubbleType",
                "HecateStellarMassLog",
            ],
            "A/C quality-pass rows with HECATE stellar-mass coverage",
        ),
    ]
    output_rows: list[dict[str, object]] = []
    coefficient_rows: list[dict[str, object]] = []
    for idx, (name, covariates, description) in enumerate(specs):
        y, x, names, galaxies = regression_matrix(rows, covariates)
        beta = huber_beta(y, x)
        p = permutation_class_p(y, x, seed=20260514 + idx)
        ci_low, ci_high = bootstrap_ci(y, x, seed=20260614 + idx)
        output_rows.append(
            {
                "Model": name,
                "Description": description,
                "N": len(y),
                "NGalaxies": ";".join(galaxies),
                "ClassCoefficient_C_vs_A": f"{beta[1]:.6g}",
                "PermutationP_CoeffGreaterZero": f"{p:.6g}",
                "BootstrapCI95Low": f"{ci_low:.6g}",
                "BootstrapCI95High": f"{ci_high:.6g}",
                "Covariates": ";".join(names[2:]),
            }
        )
        for term, value in zip(names, beta):
            coefficient_rows.append(
                {
                    "Model": name,
                    "Term": term,
                    "Coefficient": f"{value:.6g}",
                }
            )

    write_csv(
        PACKET / "controlled_regression_summary.csv",
        [
            "Model",
            "Description",
            "N",
            "NGalaxies",
            "ClassCoefficient_C_vs_A",
            "PermutationP_CoeffGreaterZero",
            "BootstrapCI95Low",
            "BootstrapCI95High",
            "Covariates",
        ],
        output_rows,
    )
    write_csv(PACKET / "controlled_regression_coefficients.csv", ["Model", "Term", "Coefficient"], coefficient_rows)

    lines = [
        "# Controlled Regression Appendix",
        "",
        "These regressions are stress checks, not replacements for the frozen primary median/permutation endpoint. The dependent variable is galaxy-level `rms_log_tpg`. The class coefficient is coded `C=1, A=0`; positive values mean C galaxies retain larger residual scatter after the listed observability covariates are included.",
        "",
        "The estimator is Huber robust regression, chosen because the A/C sample includes high-leverage residual-scatter rows. Covariates are standardized, except the class indicator. Distance and maximum radius enter as log-scaled standardized variables. The reported p-value is a label-permutation p-value for the class coefficient with the covariate matrix held fixed.",
        "",
        "| model | n | class coeff | one-sided permutation p | bootstrap 95% CI | covariates |",
        "| --- | ---: | ---: | ---: | --- | --- |",
    ]
    for row in output_rows:
        lines.append(
            "| {Model} | {N} | {ClassCoefficient_C_vs_A} | {PermutationP_CoeffGreaterZero} | [{BootstrapCI95Low}, {BootstrapCI95High}] | {Covariates} |".format(
                **row
            )
        )
    lines.extend(
        [
            "",
            "Interpretation: the class coefficient is positive in simpler robust specifications, but it weakens once distance, radial coverage, sampling quality, inclination, and Hubble-type covariates are included together. This is exactly why the paper should keep distance/radius/observability as the main limitation and should not describe the result as an observability-proof physical detection. The HECATE mass-subset regression is reported only as supportive stress information because mass coverage is incomplete and the sample becomes small.",
        ]
    )
    (PACKET / "controlled_regression_appendix.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    rows = quality_rows()
    make_selection_appendix(rows)
    make_regression(rows)
    print(PACKET / "selection_observability_appendix.md")
    print(PACKET / "controlled_regression_appendix.md")


if __name__ == "__main__":
    main()
