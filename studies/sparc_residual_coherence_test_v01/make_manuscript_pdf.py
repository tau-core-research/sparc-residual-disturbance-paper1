#!/usr/bin/env python3
"""Render the manuscript draft to a figure-rich PDF."""

from __future__ import annotations

import csv
import hashlib
import re
import statistics
import sys
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.graphics.shapes import Circle, Drawing, Line, Rect, String
from reportlab import rl_config
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    Flowable,
    HRFlowable,
    Image,
    Paragraph,
    Preformatted,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

rl_config.invariant = 1

from taucore.coherence import read_coherence_labels, read_residual_summary
from taucore.controls import QualityThresholds, join_control_rows, passes_quality, read_diagnostics
from taucore.figures import render_class_scatter_svg, write_svg


PACKET = ROOT / "studies/sparc_residual_coherence_test_v01/paper_packet_v06_distance_balanced"
OUTPUTS = ROOT / "outputs/external_proxy_v06_distance_balanced"
LABELS = ROOT / "studies/sparc_residual_coherence_test_v01/coherence_labels_v06_distance_balanced.csv"
SOURCE = PACKET / "manuscript_draft.md"
PDF = PACKET / "manuscript_draft.pdf"
FORMULA_DIR = PACKET / "figures/formulas"
FORMULA_DPI = 240
FORMULA_FONT_SIZE = 11
FONT_DIR = Path("/System/Library/Fonts/Supplemental")
BODY_FONT = "TauTimes"
BOLD_FONT = "TauTimes-Bold"
ITALIC_FONT = "TauTimes-Italic"


def register_unicode_fonts() -> None:
    fonts = {
        BODY_FONT: FONT_DIR / "Times New Roman.ttf",
        BOLD_FONT: FONT_DIR / "Times New Roman Bold.ttf",
        ITALIC_FONT: FONT_DIR / "Times New Roman Italic.ttf",
    }
    for name, path in fonts.items():
        if name not in pdfmetrics.getRegisteredFontNames():
            pdfmetrics.registerFont(TTFont(name, str(path)))


register_unicode_fonts()


styles = getSampleStyleSheet()
styles.add(
    ParagraphStyle(
        name="PaperTitle",
        parent=styles["Title"],
        fontName=BOLD_FONT,
        fontSize=18,
        leading=22,
        alignment=TA_CENTER,
        spaceAfter=18,
    )
)
styles.add(
    ParagraphStyle(
        name="PaperH2",
        parent=styles["Heading2"],
        fontName=BOLD_FONT,
        fontSize=13,
        leading=16,
        spaceBefore=14,
        spaceAfter=8,
    )
)
styles.add(
    ParagraphStyle(
        name="PaperH3",
        parent=styles["Heading3"],
        fontName=BOLD_FONT,
        fontSize=11.2,
        leading=14,
        spaceBefore=10,
        spaceAfter=5,
    )
)
styles.add(
    ParagraphStyle(
        name="PaperBody",
        parent=styles["BodyText"],
        fontName=BODY_FONT,
        fontSize=10.4,
        leading=13.6,
        alignment=TA_LEFT,
        spaceAfter=7,
    )
)
styles.add(
    ParagraphStyle(
        name="PaperList",
        parent=styles["PaperBody"],
        leftIndent=16,
        firstLineIndent=-10,
        spaceAfter=4,
    )
)
styles.add(
    ParagraphStyle(
        name="Caption",
        parent=styles["BodyText"],
        fontName=ITALIC_FONT,
        fontSize=8.6,
        leading=10.5,
        alignment=TA_LEFT,
        textColor=colors.HexColor("#333333"),
        spaceBefore=4,
        spaceAfter=8,
    )
)
styles.add(
    ParagraphStyle(
        name="PaperCode",
        parent=styles["Code"],
        fontName="Courier",
        fontSize=8.0,
        leading=10,
        leftIndent=8,
        rightIndent=8,
        backColor=colors.HexColor("#f5f5f5"),
        borderColor=colors.HexColor("#dddddd"),
        borderWidth=0.4,
        borderPadding=5,
        spaceBefore=4,
        spaceAfter=8,
    )
)
styles.add(
    ParagraphStyle(
        name="Formula",
        parent=styles["BodyText"],
        fontName=ITALIC_FONT,
        fontSize=11.0,
        leading=16.0,
        alignment=TA_CENTER,
        leftIndent=12,
        rightIndent=12,
        spaceBefore=6,
        spaceAfter=10,
    )
)
styles.add(
    ParagraphStyle(
        name="PaperSmall",
        parent=styles["BodyText"],
        fontName=BODY_FONT,
        fontSize=8.2,
        leading=10.0,
        spaceAfter=5,
    )
)

INLINE_CODE = re.compile(r"`([^`]+)`")
IMAGE_LINE = re.compile(r"!\[(.*?)\]\((.*?)\)")


def para_text(line: str) -> str:
    parts = []
    cursor = 0
    for match in INLINE_CODE.finditer(line):
        parts.append(escape(line[cursor : match.start()]))
        parts.append(f'<font name="Courier">{escape(match.group(1))}</font>')
        cursor = match.end()
    parts.append(escape(line[cursor:]))
    return "".join(parts)


def formula_mathtext(lines: list[str]) -> str:
    joined = " ".join(lines)
    exact = {
        "V_bar^2(R) = V_gas(R)|V_gas(R)| + Upsilon_d V_disk^2(R) + Upsilon_b V_bulge^2(R)": (
            r"V_{\rm bar}^2(R)=V_{\rm gas}(R)|V_{\rm gas}(R)|"
            r"+\Upsilon_d V_{\rm disk}^2(R)+\Upsilon_b V_{\rm bulge}^2(R)"
        ),
        "a_N(R) = V_bar^2(R) / R": r"a_N(R)=\frac{V_{\rm bar}^2(R)}{R}",
        "F_proj(R) = 1 + S_tau alpha ln(1 + a0 / a_N(R))": (
            r"F_{\rm proj}(R)=1+S_\tau\alpha\ln\!\left(1+\frac{a_0}{a_N(R)}\right)"
        ),
        "V_model(R) = F_proj(R) V_bar(R)": (
            r"V_{\rm model}(R)=F_{\rm proj}(R)V_{\rm bar}(R)"
        ),
        "epsilon_i = ln(V_obs,i / V_model,i)": (
            r"\epsilon_i=\ln\!\left(\frac{V_{{\rm obs},i}}{V_{{\rm model},i}}\right)"
        ),
        "rms_log = [(1/N) sum_i epsilon_i^2]^(1/2)": (
            r"{\rm rms}_{\log}=\left(\frac{1}{N}\sum_i\epsilon_i^2\right)^{1/2}"
        ),
        "Delta_AC = median(rms_log | C, selected) - median(rms_log | A, selected)": (
            r"\Delta_{AC}={\rm median}({\rm rms}_{\log}\mid C,{\rm selected})"
            r"-{\rm median}({\rm rms}_{\log}\mid A,{\rm selected})"
        ),
    }
    return exact.get(joined, joined)


def formula_image(lines: list[str]) -> Image:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    formula = formula_mathtext(lines)
    cache_key = f"v2|dpi={FORMULA_DPI}|font={FORMULA_FONT_SIZE}|{formula}"
    digest = hashlib.sha256(cache_key.encode("utf-8")).hexdigest()[:16]
    output = FORMULA_DIR / f"formula_{digest}.png"
    output.parent.mkdir(parents=True, exist_ok=True)
    if not output.exists():
        fig = plt.figure(figsize=(6.6, 0.42), dpi=FORMULA_DPI)
        fig.patch.set_alpha(0)
        fig.text(0.5, 0.5, f"${formula}$", ha="center", va="center", fontsize=FORMULA_FONT_SIZE)
        fig.savefig(output, transparent=True, bbox_inches="tight", pad_inches=0.04)
        plt.close(fig)
    image = Image(str(output))
    image.drawWidth = image.imageWidth / FORMULA_DPI * inch
    image.drawHeight = image.imageHeight / FORMULA_DPI * inch
    max_width = 5.45 * inch
    if image.drawWidth > max_width:
        scale = max_width / image.drawWidth
        image.drawWidth *= scale
        image.drawHeight *= scale
    image.hAlign = "CENTER"
    return image


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def fmt(value: float, digits: int = 3) -> str:
    return f"{value:.{digits}f}"


def quality_pass_rows():
    residual_rows = read_residual_summary(OUTPUTS / "sparc_residual_summary.csv")
    label_rows = read_coherence_labels(LABELS)
    diagnostic_rows = read_diagnostics(OUTPUTS / "coherence_label_diagnostics.csv")
    joined = join_control_rows(residual_rows, label_rows, diagnostic_rows)
    thresholds = QualityThresholds()
    return [row for row in joined if passes_quality(row, thresholds)]


class DrawingFlowable(Flowable):
    def __init__(self, drawing: Drawing):
        super().__init__()
        self.drawing = drawing
        self.width = drawing.width
        self.height = drawing.height

    def wrap(self, avail_width: float, avail_height: float) -> tuple[float, float]:
        return self.width, self.height

    def draw(self) -> None:
        self.drawing.drawOn(self.canv, 0, 0)


def audit_flow_drawing() -> Drawing:
    drawing = Drawing(500, 130)
    boxes = [
        ("External", "source evidence"),
        ("Freeze", "labels + gate"),
        ("Model", "residual audit"),
        ("Test", "C minus A"),
    ]
    x0 = 15
    for idx, (title, subtitle) in enumerate(boxes):
        x = x0 + idx * 120
        drawing.add(Rect(x, 45, 92, 46, rx=5, ry=5, fillColor=colors.HexColor("#f7f7f2"), strokeColor=colors.HexColor("#333333")))
        drawing.add(String(x + 46, 72, title, fontName="Helvetica-Bold", fontSize=10, textAnchor="middle"))
        drawing.add(String(x + 46, 57, subtitle, fontName="Helvetica", fontSize=8, textAnchor="middle", fillColor=colors.HexColor("#444444")))
        if idx < len(boxes) - 1:
            drawing.add(Line(x + 92, 68, x + 116, 68, strokeColor=colors.HexColor("#333333"), strokeWidth=1.3))
            drawing.add(Line(x + 116, 68, x + 110, 72, strokeColor=colors.HexColor("#333333"), strokeWidth=1.3))
            drawing.add(Line(x + 116, 68, x + 110, 64, strokeColor=colors.HexColor("#333333"), strokeWidth=1.3))
    drawing.add(String(250, 112, "Residual-blind model audit flow", fontName="Helvetica-Bold", fontSize=12, textAnchor="middle"))
    return drawing


def class_residual_drawing(weighted: bool = False) -> Drawing:
    metric = "weighted_rms_log_tpg" if weighted else "rms_log_tpg"
    rows = quality_pass_rows()
    grouped = {
        label: sorted([getattr(row, metric) for row in rows if row.label == label])
        for label in ["A", "B", "C"]
    }
    values = [value for group in grouped.values() for value in group]
    drawing = Drawing(500, 245)
    left, bottom, width, height = 70, 50, 360, 140
    max_value = max(values) * 1.08 if values else 1.0
    drawing.add(Line(left, bottom, left, bottom + height, strokeColor=colors.black))
    drawing.add(Line(left, bottom, left + width, bottom, strokeColor=colors.black))
    palette = {"A": "#2b8cbe", "B": "#7bccc4", "C": "#f03b20"}
    x_positions = {"A": left + 70, "B": left + 180, "C": left + 290}

    def y(value: float) -> float:
        return bottom + value / max_value * height

    for tick in range(5):
        value = max_value * tick / 4.0
        yy = y(value)
        drawing.add(Line(left - 4, yy, left + width, yy, strokeColor=colors.HexColor("#dddddd"), strokeWidth=0.4))
        drawing.add(String(left - 9, yy - 3, f"{value:.2f}", fontName="Helvetica", fontSize=7.5, textAnchor="end"))

    for label, group in grouped.items():
        x = x_positions[label]
        drawing.add(String(x, bottom - 18, f"{label} (n={len(group)})", fontName="Helvetica-Bold", fontSize=9, textAnchor="middle"))
        if group:
            median = statistics.median(group)
            drawing.add(Line(x - 38, y(median), x + 38, y(median), strokeColor=colors.black, strokeWidth=2.3))
        for idx, value in enumerate(group):
            jitter = ((idx * 37) % 41) - 20
            drawing.add(
                Circle(
                    x + jitter * 0.75,
                    y(value),
                    2.8,
                    fillColor=colors.HexColor(palette[label]),
                    strokeColor=None,
                )
            )
    ylabel = "weighted rms-log residual" if weighted else "rms-log residual"
    drawing.add(String(250, 222, f"Quality-selected {ylabel} distribution by external class", fontName="Helvetica-Bold", fontSize=11, textAnchor="middle"))
    drawing.add(String(43, 120, "residual scatter", fontName="Helvetica", fontSize=8, textAnchor="middle", transform=[0, 1, -1, 0, 43, 120]))
    return drawing


def forest_rows() -> list[dict[str, object]]:
    primary = next(
        row
        for row in read_csv(PACKET / "final_comparisons.csv")
        if row["view"] == "quality_pass" and row["comparison"] == "C_minus_A"
    )
    scale_rows = {row["control"]: row for row in read_csv(PACKET / "scale_matched_stress.csv")}
    radius_rows = {row["control"]: row for row in read_csv(PACKET / "radius_control_stress.csv")}
    distance_rows = read_csv(PACKET / "distance_stratified_control.csv")
    distance_effect = sum(
        float(row["median_diff_C_minus_A"]) * float(row["weight_min_n"])
        for row in distance_rows
    ) / sum(float(row["weight_min_n"]) for row in distance_rows)
    return [
        {
            "label": "Primary selected C-A",
            "effect": float(primary["median_difference_right_minus_left"]),
            "ci_low": float(primary["bootstrap_ci95_low"]),
            "ci_high": float(primary["bootstrap_ci95_high"]),
            "p": float(primary["permutation_p_one_sided"]),
            "detail": "17 A / 28 C",
        },
        {
            "label": "Distance matched pairs",
            "effect": float(scale_rows["greedy_unique_sparc_distance_mpc_matched_pairs"]["effect"]),
            "ci_low": float(scale_rows["greedy_unique_sparc_distance_mpc_matched_pairs"]["ci95_low"]),
            "ci_high": float(scale_rows["greedy_unique_sparc_distance_mpc_matched_pairs"]["ci95_high"]),
            "p": float(scale_rows["greedy_unique_sparc_distance_mpc_matched_pairs"]["p"]),
            "detail": "17 pairs",
        },
        {
            "label": "Distance-stratified bins",
            "effect": distance_effect,
            "ci_low": None,
            "ci_high": None,
            "p": 0.00939906,
            "detail": "within-bin permutation",
        },
        {
            "label": "Radius common support",
            "effect": float(radius_rows["radius_overlap_window"]["effect"]),
            "ci_low": float(radius_rows["radius_overlap_window"]["ci95_low"]),
            "ci_high": float(radius_rows["radius_overlap_window"]["ci95_high"]),
            "p": float(radius_rows["radius_overlap_window"]["p"]),
            "detail": "17 A / 26 C",
        },
        {
            "label": "Radius matched pairs",
            "effect": float(radius_rows["greedy_unique_radius_matched_pairs"]["effect"]),
            "ci_low": float(radius_rows["greedy_unique_radius_matched_pairs"]["ci95_low"]),
            "ci_high": float(radius_rows["greedy_unique_radius_matched_pairs"]["ci95_high"]),
            "p": float(radius_rows["greedy_unique_radius_matched_pairs"]["p"]),
            "detail": "17 pairs",
        },
        {
            "label": "HECATE mass matched",
            "effect": float(scale_rows["greedy_unique_hecate_stellar_mass_log_matched_pairs"]["effect"]),
            "ci_low": float(scale_rows["greedy_unique_hecate_stellar_mass_log_matched_pairs"]["ci95_low"]),
            "ci_high": float(scale_rows["greedy_unique_hecate_stellar_mass_log_matched_pairs"]["ci95_high"]),
            "p": float(scale_rows["greedy_unique_hecate_stellar_mass_log_matched_pairs"]["p"]),
            "detail": "10 pairs; incomplete coverage",
        },
    ]


def control_forest_drawing() -> Drawing:
    rows = forest_rows()
    drawing = Drawing(500, 280)
    left, right = 210, 430
    top, row_gap = 220, 30
    scale_min, scale_max = -0.12, 0.23

    def x(value: float) -> float:
        return left + (value - scale_min) / (scale_max - scale_min) * (right - left)

    drawing.add(String(250, 258, "C-minus-A effect across primary and control analyses", fontName="Helvetica-Bold", fontSize=11, textAnchor="middle"))
    drawing.add(Line(left, 42, right, 42, strokeColor=colors.black))
    drawing.add(Line(x(0), 48, x(0), 238, strokeColor=colors.HexColor("#777777"), strokeWidth=0.7, strokeDashArray=[4, 3]))
    for tick in [-0.1, 0.0, 0.1, 0.2]:
        drawing.add(Line(x(tick), 38, x(tick), 46, strokeColor=colors.black, strokeWidth=0.5))
        drawing.add(String(x(tick), 25, f"{tick:.1f}", fontName="Helvetica", fontSize=7, textAnchor="middle"))
    for idx, row in enumerate(rows):
        y = top - idx * row_gap
        effect = float(row["effect"])
        ci_low = row["ci_low"]
        ci_high = row["ci_high"]
        drawing.add(String(18, y - 3, str(row["label"]), fontName="Helvetica", fontSize=8.2, textAnchor="start"))
        drawing.add(String(470, y - 3, f"p={float(row['p']):.4f}", fontName="Helvetica", fontSize=7.6, textAnchor="end"))
        if ci_low is not None and ci_high is not None:
            drawing.add(Line(x(float(ci_low)), y, x(float(ci_high)), y, strokeColor=colors.HexColor("#116466"), strokeWidth=3.4))
        else:
            drawing.add(Line(x(effect) - 7, y, x(effect) + 7, y, strokeColor=colors.HexColor("#116466"), strokeWidth=3.4))
        drawing.add(Circle(x(effect), y, 3.8, fillColor=colors.HexColor("#d1495b"), strokeColor=None))
        drawing.add(String(x(effect), y + 10, fmt(effect, 3), fontName="Helvetica", fontSize=7, textAnchor="middle"))
        drawing.add(String(18, y - 14, str(row["detail"]), fontName="Helvetica", fontSize=6.8, fillColor=colors.HexColor("#555555")))
    drawing.add(String(250, 8, "median residual difference; positive values support the predicted C>A direction", fontName="Helvetica", fontSize=7, textAnchor="middle"))
    return drawing


def distance_strata_drawing() -> Drawing:
    rows = read_csv(PACKET / "distance_stratified_control.csv")
    values = [
        (
            row["distance_bin"],
            int(row["n_A"]),
            int(row["n_C"]),
            float(row["median_diff_C_minus_A"]),
        )
        for row in rows
    ]
    drawing = Drawing(500, 225)
    left, bottom, width, height = 75, 50, 350, 125
    max_value = max(value for _, _, _, value in values) * 1.35
    drawing.add(String(250, 203, "Within-distance-bin C-minus-A effects", fontName="Helvetica-Bold", fontSize=11, textAnchor="middle"))
    drawing.add(Line(left, bottom, left, bottom + height, strokeColor=colors.black))
    drawing.add(Line(left, bottom, left + width, bottom, strokeColor=colors.black))
    for tick in range(4):
        value = max_value * tick / 3.0
        y = bottom + value / max_value * height
        drawing.add(Line(left - 4, y, left + width, y, strokeColor=colors.HexColor("#dddddd"), strokeWidth=0.4))
        drawing.add(String(left - 9, y - 3, f"{value:.2f}", fontName="Helvetica", fontSize=7, textAnchor="end"))
    bar_w = 46
    for idx, (label, n_a, n_c, value) in enumerate(values):
        x = left + 27 + idx * 82
        h = height * value / max_value
        drawing.add(Rect(x, bottom, bar_w, h, fillColor=colors.HexColor("#6a994e"), strokeColor=None))
        drawing.add(String(x + bar_w / 2, bottom - 15, label, fontName="Helvetica", fontSize=8, textAnchor="middle"))
        drawing.add(String(x + bar_w / 2, bottom - 27, f"A={n_a}, C={n_c}", fontName="Helvetica", fontSize=6.5, textAnchor="middle"))
        drawing.add(String(x + bar_w / 2, bottom + h + 7, f"{value:.3f}", fontName="Helvetica", fontSize=8, textAnchor="middle"))
    drawing.add(String(250, 11, "all SPARC distance bins retain positive C-minus-A direction", fontName="Helvetica", fontSize=7, textAnchor="middle"))
    return drawing


def threshold_placeholder_drawing() -> Drawing:
    rows = read_csv(OUTPUTS / "threshold_sensitivity.csv")
    min_points_values = sorted({int(row["min_points"]) for row in rows})
    max_err_values = sorted({float(row["max_mean_err_vobs_kms"]) for row in rows})
    by_cell = {
        (int(row["min_points"]), float(row["max_mean_err_vobs_kms"])): row
        for row in rows
    }
    diffs = [float(row["c_minus_nonc_diff"]) for row in rows]
    max_diff = max(abs(value) for value in diffs) if diffs else 1.0
    drawing = Drawing(500, 250)
    left, top = 105, 58
    cell_w, cell_h = 92, 34

    def color(value: float) -> colors.Color:
        strength = min(1.0, abs(value) / max_diff)
        if value >= 0:
            return colors.Color(0.90 - 0.35 * strength, 0.97 - 0.14 * strength, 0.86 - 0.62 * strength)
        return colors.Color(0.86 - 0.40 * strength, 0.92 - 0.30 * strength, 0.98)

    drawing.add(String(250, 225, "C-minus-nonC sensitivity across quality cuts", fontName="Helvetica-Bold", fontSize=11, textAnchor="middle"))
    drawing.add(String(247, 205, "max mean Vobs error", fontName="Helvetica", fontSize=8.5, textAnchor="middle"))
    for col, max_err in enumerate(max_err_values):
        x = left + col * cell_w
        drawing.add(String(x + cell_w / 2, top - 8, f"{max_err:g}", fontName="Helvetica", fontSize=8, textAnchor="middle"))
    for row_index, min_points in enumerate(min_points_values):
        y = top + row_index * cell_h
        drawing.add(String(left - 12, y + cell_h / 2 - 3, f"{min_points}", fontName="Helvetica", fontSize=8, textAnchor="end"))
        for col, max_err in enumerate(max_err_values):
            x = left + col * cell_w
            row = by_cell[(min_points, max_err)]
            diff = float(row["c_minus_nonc_diff"])
            drawing.add(Rect(x, y, cell_w - 3, cell_h - 3, fillColor=color(diff), strokeColor=colors.HexColor("#555555"), strokeWidth=0.4))
            drawing.add(String(x + cell_w / 2, y + 19, f"{diff:.3f}", fontName="Helvetica", fontSize=8, textAnchor="middle"))
            drawing.add(String(x + cell_w / 2, y + 8, f"nC={row['n_c']}", fontName="Helvetica", fontSize=6.8, textAnchor="middle"))
    drawing.add(String(48, 126, "min points", fontName="Helvetica", fontSize=8, textAnchor="middle"))
    return drawing


def figure_for(path: str) -> Drawing:
    if path.endswith("quality_pass_rms_distribution.svg"):
        return class_residual_drawing(weighted=False)
    if path.endswith("quality_pass_weighted_rms_distribution.svg"):
        return class_residual_drawing(weighted=True)
    if path.endswith("review_gate_flow.svg"):
        return audit_flow_drawing()
    if path.endswith("class_rms_scatter.svg"):
        return class_residual_drawing(weighted=False)
    if path.endswith("primary_c_minus_a.svg"):
        return control_forest_drawing()
    if path.endswith("class_weighted_rms_scatter.svg"):
        return class_residual_drawing(weighted=True)
    if path.endswith("threshold_sensitivity.svg"):
        return threshold_placeholder_drawing()
    if path.endswith("control_forest_plot.svg"):
        return control_forest_drawing()
    if path.endswith("distance_stratified_effects.svg"):
        return distance_strata_drawing()
    return audit_flow_drawing()


def write_quality_pass_svg_artifacts() -> None:
    rows = quality_pass_rows()
    residual_rows = [
        {
            "galaxy_name": row.galaxy_name,
            "rms_log_tpg": str(row.rms_log_tpg),
            "weighted_rms_log_tpg": str(row.weighted_rms_log_tpg),
        }
        for row in rows
    ]
    label_rows = [
        {
            "GalaxyName": row.galaxy_name,
            "S_tau_class": row.label,
        }
        for row in rows
    ]
    write_svg(
        render_class_scatter_svg(
            residual_rows,
            label_rows,
            metric="rms_log_tpg",
            title="Quality-selected residual scatter by external class",
            ylabel="rms-log residual",
        ),
        PACKET / "figures/quality_pass_rms_distribution.svg",
    )
    write_svg(
        render_class_scatter_svg(
            residual_rows,
            label_rows,
            metric="weighted_rms_log_tpg",
            title="Quality-selected weighted residual scatter by external class",
            ylabel="weighted rms-log residual",
        ),
        PACKET / "figures/quality_pass_weighted_rms_distribution.svg",
    )


def svg_text(x: float, y: float, text: str, size: int = 12, anchor: str = "middle") -> str:
    return (
        f'<text x="{x:.2f}" y="{y:.2f}" font-family="Arial, sans-serif" '
        f'font-size="{size}" text-anchor="{anchor}" fill="#222">{escape(text)}</text>'
    )


def render_control_forest_svg() -> str:
    rows = forest_rows()
    width, height = 760, 430
    left, right = 310, 680
    top, row_gap = 95, 45
    scale_min, scale_max = -0.12, 0.23

    def x(value: float) -> float:
        return left + (value - scale_min) / (scale_max - scale_min) * (right - left)

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        svg_text(width / 2, 32, "C-minus-A effect across primary and control analyses", size=18),
        f'<line x1="{left}" y1="370" x2="{right}" y2="370" stroke="#333"/>',
        f'<line x1="{x(0):.2f}" y1="62" x2="{x(0):.2f}" y2="370" stroke="#777" stroke-dasharray="5,5"/>',
    ]
    for tick in [-0.1, 0.0, 0.1, 0.2]:
        parts.append(f'<line x1="{x(tick):.2f}" y1="365" x2="{x(tick):.2f}" y2="376" stroke="#333"/>')
        parts.append(svg_text(x(tick), 394, f"{tick:.1f}", size=11))
    for idx, row in enumerate(rows):
        y = top + idx * row_gap
        effect = float(row["effect"])
        ci_low = row["ci_low"]
        ci_high = row["ci_high"]
        parts.append(svg_text(36, y + 4, str(row["label"]), size=12, anchor="start"))
        parts.append(svg_text(36, y + 21, str(row["detail"]), size=10, anchor="start"))
        parts.append(svg_text(725, y + 4, f"p={float(row['p']):.4f}", size=11, anchor="end"))
        if ci_low is not None and ci_high is not None:
            parts.append(
                f'<line x1="{x(float(ci_low)):.2f}" y1="{y:.2f}" x2="{x(float(ci_high)):.2f}" y2="{y:.2f}" '
                'stroke="#116466" stroke-width="7" stroke-linecap="round"/>'
            )
        else:
            parts.append(
                f'<line x1="{x(effect) - 14:.2f}" y1="{y:.2f}" x2="{x(effect) + 14:.2f}" y2="{y:.2f}" '
                'stroke="#116466" stroke-width="7" stroke-linecap="round"/>'
            )
        parts.append(f'<circle cx="{x(effect):.2f}" cy="{y:.2f}" r="6" fill="#d1495b"/>')
        parts.append(svg_text(x(effect), y - 13, fmt(effect, 3), size=10))
    parts.append(svg_text(width / 2, 418, "median residual difference; positive values support the predicted C>A direction", size=11))
    parts.append("</svg>")
    return "\n".join(parts)


def render_distance_strata_svg() -> str:
    rows = read_csv(PACKET / "distance_stratified_control.csv")
    values = [
        (
            row["distance_bin"],
            int(row["n_A"]),
            int(row["n_C"]),
            float(row["median_diff_C_minus_A"]),
        )
        for row in rows
    ]
    width, height = 760, 400
    left, bottom, plot_w, plot_h = 90, 305, 600, 220
    max_value = max(value for _, _, _, value in values) * 1.35
    bar_w = 78

    def y(value: float) -> float:
        return bottom - value / max_value * plot_h

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        svg_text(width / 2, 32, "Within-distance-bin C-minus-A effects", size=18),
        f'<line x1="{left}" y1="{bottom}" x2="{left + plot_w}" y2="{bottom}" stroke="#333"/>',
        f'<line x1="{left}" y1="{bottom - plot_h}" x2="{left}" y2="{bottom}" stroke="#333"/>',
    ]
    for tick in range(5):
        value = max_value * tick / 4.0
        yy = y(value)
        parts.append(f'<line x1="{left - 5}" y1="{yy:.2f}" x2="{left + plot_w}" y2="{yy:.2f}" stroke="#ddd"/>')
        parts.append(svg_text(left - 12, yy + 4, f"{value:.2f}", size=11, anchor="end"))
    for idx, (label, n_a, n_c, value) in enumerate(values):
        x0 = left + 65 + idx * 135
        yy = y(value)
        parts.append(f'<rect x="{x0:.2f}" y="{yy:.2f}" width="{bar_w}" height="{bottom - yy:.2f}" fill="#6a994e"/>')
        parts.append(svg_text(x0 + bar_w / 2, yy - 9, f"{value:.3f}", size=12))
        parts.append(svg_text(x0 + bar_w / 2, bottom + 25, label, size=12))
        parts.append(svg_text(x0 + bar_w / 2, bottom + 43, f"A={n_a}, C={n_c}", size=10))
    parts.append(svg_text(27, 205, "C-A diff", size=12))
    parts.append(svg_text(width / 2, 382, "all SPARC distance bins retain positive C-minus-A direction", size=11))
    parts.append("</svg>")
    return "\n".join(parts)


def write_control_svg_artifacts() -> None:
    write_svg(render_control_forest_svg(), PACKET / "figures/control_forest_plot.svg")
    write_svg(render_distance_strata_svg(), PACKET / "figures/distance_stratified_effects.svg")


def markdown_table(headers: list[str], rows: list[list[str]]) -> Table:
    data = [[Paragraph(para_text(cell), styles["PaperSmall"]) for cell in headers]]
    data.extend([[Paragraph(para_text(cell), styles["PaperSmall"]) for cell in row] for row in rows])
    available = letter[0] - 1.4 * inch
    col_width = available / max(len(headers), 1)
    table = Table(data, colWidths=[col_width] * len(headers), hAlign="LEFT", repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#eeeeee")),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#bbbbbb")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ]
        )
    )
    return table


def parse_table(lines: list[str], index: int) -> tuple[list[str], list[list[str]], int]:
    block = []
    while index < len(lines) and lines[index].strip().startswith("|"):
        block.append([cell.strip() for cell in lines[index].strip().strip("|").split("|")])
        index += 1
    return block[0], block[2:], index


def is_table(lines: list[str], index: int) -> bool:
    if index + 1 >= len(lines):
        return False
    if not lines[index].strip().startswith("|"):
        return False
    rule = lines[index + 1].strip().replace("|", "").replace(" ", "")
    return bool(rule) and set(rule).issubset(set("-:"))


def build_story(source: Path) -> list[object]:
    story: list[object] = []
    lines = source.read_text(encoding="utf-8").splitlines()
    in_code = False
    in_formula = False
    code_lines: list[str] = []
    formula_lines: list[str] = []
    index = 0
    while index < len(lines):
        line = lines[index]
        stripped = line.strip()

        if stripped == "$$":
            if in_formula:
                story.append(Spacer(1, 4))
                story.append(formula_image(formula_lines))
                story.append(Spacer(1, 8))
                formula_lines = []
                in_formula = False
            else:
                in_formula = True
            index += 1
            continue
        if in_formula:
            formula_lines.append(stripped)
            index += 1
            continue
        if stripped.startswith("```"):
            if in_code:
                story.append(Preformatted("\n".join(code_lines), styles["PaperCode"]))
                code_lines = []
                in_code = False
            else:
                in_code = True
            index += 1
            continue
        if in_code:
            code_lines.append(line)
            index += 1
            continue
        if not stripped:
            index += 1
            continue
        image = IMAGE_LINE.match(stripped)
        if image:
            caption, image_path = image.groups()
            story.append(Spacer(1, 6))
            story.append(DrawingFlowable(figure_for(image_path)))
            story.append(Paragraph(para_text(caption), styles["Caption"]))
            story.append(HRFlowable(width="100%", thickness=0.3, color=colors.HexColor("#dddddd"), spaceAfter=6))
            index += 1
            continue
        if is_table(lines, index):
            headers, rows, index = parse_table(lines, index)
            story.append(markdown_table(headers, rows))
            story.append(Spacer(1, 8))
            continue
        if stripped.startswith("# "):
            story.append(Paragraph(para_text(stripped[2:]), styles["PaperTitle"]))
        elif stripped.startswith("## "):
            story.append(Paragraph(para_text(stripped[3:]), styles["PaperH2"]))
        elif stripped.startswith("### "):
            story.append(Paragraph(para_text(stripped[4:]), styles["PaperH3"]))
        elif re.match(r"^\d+\. ", stripped):
            story.append(Paragraph(para_text(stripped), styles["PaperList"]))
        elif stripped.startswith("- "):
            story.append(Paragraph("&bull; " + para_text(stripped[2:]), styles["PaperList"]))
        else:
            paragraph = [stripped]
            cursor = index + 1
            while cursor < len(lines):
                nxt = lines[cursor].strip()
                if (
                    not nxt
                    or nxt.startswith("#")
                    or nxt.startswith("```")
                    or nxt.startswith("|")
                    or nxt.startswith("- ")
                    or re.match(r"^\d+\. ", nxt)
                    or IMAGE_LINE.match(nxt)
                ):
                    break
                paragraph.append(nxt)
                cursor += 1
            story.append(Paragraph(para_text(" ".join(paragraph)), styles["PaperBody"]))
            index = cursor - 1
        index += 1
    return story


def footer(label: str):
    def draw_footer(canvas, doc) -> None:
        canvas.saveState()
        canvas.setFont(BODY_FONT, 8)
        canvas.setFillColor(colors.HexColor("#555555"))
        canvas.drawString(doc.leftMargin, 0.45 * inch, label)
        canvas.drawRightString(letter[0] - doc.rightMargin, 0.45 * inch, str(canvas.getPageNumber()))
        canvas.restoreState()

    return draw_footer


def render_pdf(source: Path, pdf: Path, title: str, footer_label: str) -> None:
    write_quality_pass_svg_artifacts()
    write_control_svg_artifacts()
    doc = SimpleDocTemplate(
        str(pdf),
        pagesize=letter,
        rightMargin=0.7 * inch,
        leftMargin=0.7 * inch,
        topMargin=0.7 * inch,
        bottomMargin=0.7 * inch,
        title=title,
        author="Residual coherence study",
    )
    draw_footer = footer(footer_label)
    doc.build(build_story(source), onFirstPage=draw_footer, onLaterPages=draw_footer)
    print(pdf)


def main() -> None:
    render_pdf(
        SOURCE,
        PDF,
        "SPARC residual-disturbance manuscript",
        "SPARC residual-disturbance manuscript",
    )


if __name__ == "__main__":
    main()
