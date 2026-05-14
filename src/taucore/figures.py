"""Small dependency-free SVG figures for study reports."""

from __future__ import annotations

import csv
import statistics
from pathlib import Path


def read_csv_rows(path: str | Path) -> list[dict[str, str]]:
    with Path(path).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _scale(value: float, min_value: float, max_value: float, low: float, high: float) -> float:
    if max_value == min_value:
        return (low + high) / 2.0
    return low + (value - min_value) / (max_value - min_value) * (high - low)


def _svg_text(x: float, y: float, text: str, size: int = 12, anchor: str = "middle") -> str:
    return (
        f'<text x="{x:.2f}" y="{y:.2f}" font-family="Arial, sans-serif" '
        f'font-size="{size}" text-anchor="{anchor}" fill="#222">{text}</text>'
    )


def render_class_scatter_svg(
    residual_rows: list[dict[str, str]],
    label_rows: list[dict[str, str]],
    metric: str = "rms_log_tpg",
    title: str = "Residual scatter by coherence class",
    ylabel: str | None = None,
) -> str:
    labels = {
        row["GalaxyName"]: row["S_tau_class"].strip().upper()
        for row in label_rows
        if row.get("GalaxyName") and row.get("S_tau_class")
    }
    grouped: dict[str, list[tuple[str, float]]] = {"A": [], "B": [], "C": []}
    for row in residual_rows:
        name = row["galaxy_name"]
        label = labels.get(name)
        if label in grouped:
            grouped[label].append((name, float(row[metric])))

    values = [value for rows in grouped.values() for _, value in rows]
    min_value = 0.0
    max_value = max(values) * 1.08 if values else 1.0
    width = 760
    height = 460
    left = 80
    right = width - 40
    top = 60
    bottom = height - 70
    colors = {"A": "#2b8cbe", "B": "#7bccc4", "C": "#f03b20"}
    x_positions = {"A": 190, "B": 380, "C": 570}

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        _svg_text(width / 2, 30, title, size=20),
        f'<line x1="{left}" y1="{bottom}" x2="{right}" y2="{bottom}" stroke="#333"/>',
        f'<line x1="{left}" y1="{top}" x2="{left}" y2="{bottom}" stroke="#333"/>',
    ]
    for tick in range(6):
        value = min_value + (max_value - min_value) * tick / 5.0
        y = _scale(value, min_value, max_value, bottom, top)
        parts.append(f'<line x1="{left-5}" y1="{y:.2f}" x2="{right}" y2="{y:.2f}" stroke="#ddd"/>')
        parts.append(_svg_text(left - 10, y + 4, f"{value:.2f}", size=12, anchor="end"))

    for label, rows in grouped.items():
        x = x_positions[label]
        parts.append(_svg_text(x, bottom + 34, f"{label} (n={len(rows)})", size=15))
        if rows:
            median = statistics.median(value for _, value in rows)
            y_med = _scale(median, min_value, max_value, bottom, top)
            parts.append(
                f'<line x1="{x-55}" y1="{y_med:.2f}" x2="{x+55}" y2="{y_med:.2f}" '
                f'stroke="#111" stroke-width="3.5"/>'
            )
        for idx, (_, value) in enumerate(sorted(rows)):
            jitter = ((idx * 37) % 41) - 20
            y = _scale(value, min_value, max_value, bottom, top)
            parts.append(
                f'<circle cx="{x + jitter:.2f}" cy="{y:.2f}" r="4.5" '
                f'fill="{colors[label]}" opacity="0.68"/>'
            )

    parts.append(_svg_text(22, (top + bottom) / 2, ylabel or metric, size=14, anchor="middle"))
    parts.append("</svg>")
    return "\n".join(parts)


def render_threshold_sensitivity_svg(
    rows: list[dict[str, str]],
    title: str = "C-minus-nonC sensitivity across quality cuts",
) -> str:
    min_points_values = sorted({int(row["min_points"]) for row in rows})
    max_err_values = sorted({float(row["max_mean_err_vobs_kms"]) for row in rows})
    by_cell = {
        (int(row["min_points"]), float(row["max_mean_err_vobs_kms"])): row
        for row in rows
    }
    diffs = [float(row["c_minus_nonc_diff"]) for row in rows]
    max_abs = max(abs(value) for value in diffs) if diffs else 1.0
    width = 760
    height = 420
    left = 130
    top = 70
    cell_w = 120
    cell_h = 70

    def color(value: float) -> str:
        strength = min(1.0, abs(value) / max_abs)
        if value >= 0:
            red = int(255 - 120 * strength)
            green = int(245 - 40 * strength)
            blue = int(240 - 190 * strength)
        else:
            red = int(240 - 170 * strength)
            green = int(245 - 80 * strength)
            blue = int(255 - 40 * strength)
        return f"#{red:02x}{green:02x}{blue:02x}"

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        _svg_text(width / 2, 30, title, size=18),
        _svg_text(420, 58, "max mean Vobs error", size=12),
    ]
    for col, max_err in enumerate(max_err_values):
        x = left + col * cell_w
        parts.append(_svg_text(x + cell_w / 2, top - 12, f"{max_err:g}", size=12))
    for r, min_points in enumerate(min_points_values):
        y = top + r * cell_h
        parts.append(_svg_text(left - 18, y + cell_h / 2 + 4, f"{min_points}", size=12, anchor="end"))
        for col, max_err in enumerate(max_err_values):
            x = left + col * cell_w
            row = by_cell[(min_points, max_err)]
            diff = float(row["c_minus_nonc_diff"])
            n_c = int(row["n_c"])
            parts.append(
                f'<rect x="{x:.2f}" y="{y:.2f}" width="{cell_w-4}" height="{cell_h-4}" '
                f'fill="{color(diff)}" stroke="#444"/>'
            )
            parts.append(_svg_text(x + cell_w / 2 - 2, y + 28, f"{diff:.3f}", size=13))
            parts.append(_svg_text(x + cell_w / 2 - 2, y + 49, f"nC={n_c}", size=11))
    parts.append(_svg_text(34, top + len(min_points_values) * cell_h / 2, "min points", size=12))
    parts.append("</svg>")
    return "\n".join(parts)


def write_svg(svg: str, path: str | Path) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(svg, encoding="utf-8")
