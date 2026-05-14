"""Coherence-label comparison utilities."""

from __future__ import annotations

import csv
import json
import random
import statistics
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class LabelGroupResult:
    label: str
    n: int
    median_rms_log_tpg: float
    median_weighted_rms_log_tpg: float
    median_outer_mean_log_residual_tpg: float


@dataclass(frozen=True)
class BinaryComparisonResult:
    name: str
    metric: str
    left_label: str
    right_label: str
    alternative: str
    n_left: int
    n_right: int
    median_left: float
    median_right: float
    median_difference_right_minus_left: float
    permutation_p_one_sided: float
    bootstrap_ci95_low: float
    bootstrap_ci95_high: float


@dataclass(frozen=True)
class TrendResult:
    metric: str
    n: int
    alternative: str
    spearman_rho_label_order: float
    permutation_p_one_sided: float


def read_residual_summary(path: str | Path) -> dict[str, dict[str, str]]:
    with Path(path).open(newline="", encoding="utf-8") as handle:
        return {row["galaxy_name"]: row for row in csv.DictReader(handle)}


def read_coherence_labels(path: str | Path) -> dict[str, dict[str, str]]:
    with Path(path).open(newline="", encoding="utf-8") as handle:
        rows = {}
        for row in csv.DictReader(handle):
            galaxy_name = row.get("GalaxyName", "").strip()
            label = row.get("S_tau_class", "").strip().upper()
            if galaxy_name and label:
                rows[galaxy_name] = row
        return rows


def compare_label_groups(
    residual_rows: dict[str, dict[str, str]],
    label_rows: dict[str, dict[str, str]],
) -> list[LabelGroupResult]:
    grouped: dict[str, list[dict[str, str]]] = {}
    for galaxy_name, label_row in label_rows.items():
        residual_row = residual_rows.get(galaxy_name)
        if residual_row is None:
            continue
        label = label_row["S_tau_class"].strip().upper()
        grouped.setdefault(label, []).append(residual_row)

    results: list[LabelGroupResult] = []
    for label in sorted(grouped):
        rows = grouped[label]
        results.append(
            LabelGroupResult(
                label=label,
                n=len(rows),
                median_rms_log_tpg=statistics.median(float(row["rms_log_tpg"]) for row in rows),
                median_weighted_rms_log_tpg=statistics.median(
                    float(row["weighted_rms_log_tpg"]) for row in rows
                ),
                median_outer_mean_log_residual_tpg=statistics.median(
                    float(row["outer_mean_log_residual_tpg"]) for row in rows
                ),
            )
        )
    return results


def grouped_metric_values(
    residual_rows: dict[str, dict[str, str]],
    label_rows: dict[str, dict[str, str]],
    metric: str = "rms_log_tpg",
) -> dict[str, list[float]]:
    grouped: dict[str, list[float]] = {}
    for galaxy_name, label_row in label_rows.items():
        residual_row = residual_rows.get(galaxy_name)
        if residual_row is None:
            continue
        label = label_row["S_tau_class"].strip().upper()
        grouped.setdefault(label, []).append(float(residual_row[metric]))
    return grouped


def median_difference(right: list[float], left: list[float]) -> float:
    return statistics.median(right) - statistics.median(left)


def bootstrap_median_difference_ci(
    right: list[float],
    left: list[float],
    iterations: int = 2000,
    seed: int = 12345,
) -> tuple[float, float]:
    if not right or not left:
        return (float("nan"), float("nan"))

    rng = random.Random(seed)
    diffs: list[float] = []
    for _ in range(iterations):
        right_sample = [right[rng.randrange(len(right))] for _ in right]
        left_sample = [left[rng.randrange(len(left))] for _ in left]
        diffs.append(median_difference(right_sample, left_sample))

    diffs.sort()
    low_idx = int(0.025 * (len(diffs) - 1))
    high_idx = int(0.975 * (len(diffs) - 1))
    return (diffs[low_idx], diffs[high_idx])


def permutation_median_difference_p(
    right: list[float],
    left: list[float],
    iterations: int = 10000,
    seed: int = 12345,
    alternative: str = "greater",
) -> float:
    """One-sided permutation p-value for median-difference direction."""

    if not right or not left:
        return float("nan")
    if alternative not in {"greater", "less"}:
        raise ValueError("alternative must be 'greater' or 'less'.")

    observed = median_difference(right, left)
    values = list(right) + list(left)
    n_right = len(right)
    rng = random.Random(seed)
    count = 1
    for _ in range(iterations):
        rng.shuffle(values)
        perm_right = values[:n_right]
        perm_left = values[n_right:]
        permuted = median_difference(perm_right, perm_left)
        if alternative == "greater" and permuted >= observed:
            count += 1
        elif alternative == "less" and permuted <= observed:
            count += 1
    return count / (iterations + 1)


def binary_comparison(
    grouped: dict[str, list[float]],
    name: str,
    left_labels: set[str],
    right_labels: set[str],
    metric: str = "rms_log_tpg",
    permutations: int = 10000,
    bootstrap: int = 2000,
    seed: int = 12345,
    alternative: str = "greater",
) -> BinaryComparisonResult:
    left = [value for label in left_labels for value in grouped.get(label, [])]
    right = [value for label in right_labels for value in grouped.get(label, [])]
    ci_low, ci_high = bootstrap_median_difference_ci(right, left, iterations=bootstrap, seed=seed)
    p_value = permutation_median_difference_p(
        right,
        left,
        iterations=permutations,
        seed=seed,
        alternative=alternative,
    )

    return BinaryComparisonResult(
        name=name,
        metric=metric,
        left_label="+".join(sorted(left_labels)),
        right_label="+".join(sorted(right_labels)),
        alternative=alternative,
        n_left=len(left),
        n_right=len(right),
        median_left=statistics.median(left) if left else float("nan"),
        median_right=statistics.median(right) if right else float("nan"),
        median_difference_right_minus_left=median_difference(right, left) if left and right else float("nan"),
        permutation_p_one_sided=p_value,
        bootstrap_ci95_low=ci_low,
        bootstrap_ci95_high=ci_high,
    )


def _rankdata(values: list[float]) -> list[float]:
    indexed = sorted(enumerate(values), key=lambda item: item[1])
    ranks = [0.0] * len(values)
    i = 0
    while i < len(indexed):
        j = i + 1
        while j < len(indexed) and indexed[j][1] == indexed[i][1]:
            j += 1
        avg_rank = (i + 1 + j) / 2.0
        for k in range(i, j):
            ranks[indexed[k][0]] = avg_rank
        i = j
    return ranks


def _pearson(xs: list[float], ys: list[float]) -> float:
    if len(xs) != len(ys) or len(xs) < 2:
        return float("nan")
    mean_x = statistics.mean(xs)
    mean_y = statistics.mean(ys)
    dx = [x - mean_x for x in xs]
    dy = [y - mean_y for y in ys]
    denom_x = sum(x * x for x in dx)
    denom_y = sum(y * y for y in dy)
    if denom_x <= 0 or denom_y <= 0:
        return float("nan")
    return sum(x * y for x, y in zip(dx, dy)) / (denom_x * denom_y) ** 0.5


def spearman(xs: list[float], ys: list[float]) -> float:
    return _pearson(_rankdata(xs), _rankdata(ys))


def trend_test(
    grouped: dict[str, list[float]],
    metric: str = "rms_log_tpg",
    permutations: int = 10000,
    seed: int = 12345,
    alternative: str = "greater",
) -> TrendResult:
    if alternative not in {"greater", "less"}:
        raise ValueError("alternative must be 'greater' or 'less'.")

    label_order = {"A": 0.0, "B": 1.0, "C": 2.0}
    labels: list[float] = []
    values: list[float] = []
    for label, order in label_order.items():
        for value in grouped.get(label, []):
            labels.append(order)
            values.append(value)

    observed = spearman(labels, values)
    rng = random.Random(seed)
    count = 1
    shuffled = list(values)
    for _ in range(permutations):
        rng.shuffle(shuffled)
        permuted = spearman(labels, shuffled)
        if alternative == "greater" and permuted >= observed:
            count += 1
        elif alternative == "less" and permuted <= observed:
            count += 1

    return TrendResult(
        metric=metric,
        n=len(values),
        alternative=alternative,
        spearman_rho_label_order=observed,
        permutation_p_one_sided=count / (permutations + 1),
    )


def write_stats_json(
    path: str | Path,
    group_results: list[LabelGroupResult],
    comparisons: list[BinaryComparisonResult],
    trend: TrendResult,
) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "groups": [result.__dict__ for result in group_results],
        "binary_comparisons": [result.__dict__ for result in comparisons],
        "trend": trend.__dict__,
    }
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def write_blank_label_manifest(residual_rows: dict[str, dict[str, str]], path: str | Path) -> None:
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
        for galaxy_name in sorted(residual_rows):
            writer.writerow(
                {
                    "GalaxyName": galaxy_name,
                    "S_tau_class": "",
                    "S_tau_proxy": "",
                    "LabelConfidence": "",
                    "LabelReason": "",
                    "LabelSource": "",
                    "IsBlindLabel": "true",
                    "Notes": "",
                }
            )
