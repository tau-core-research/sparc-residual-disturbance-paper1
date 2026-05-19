#!/usr/bin/env python3
"""Build an arXiv-oriented LaTeX source package from the manuscript packet."""

from __future__ import annotations

import csv
import math
import re
import shutil
import zipfile
from pathlib import Path

import fitz
import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[2]
PACKET = ROOT / "studies/sparc_residual_coherence_test_v01/paper_packet_v06_distance_balanced"
SOURCE = PACKET / "manuscript_draft.md"
ARXIV = ROOT / "arxiv"
FIGURES = ARXIV / "figures"
ZIP_PATH = ROOT / "arxiv_submission_source.zip"
ILLUSTRATIVE_CURVES = ROOT / "studies/illustrative_rotation_curves"


FORMULAS = {
    "V_bar^2(R) = V_gas(R)|V_gas(R)| + Upsilon_d V_disk^2(R) + Upsilon_b V_bulge^2(R)": (
        r"V_{\rm bar}^2(R)=V_{\rm gas}(R)|V_{\rm gas}(R)|"
        r"+\Upsilon_d V_{\rm disk}^2(R)+\Upsilon_b V_{\rm bulge}^2(R)"
    ),
    "a_N(R) = V_bar^2(R) / R": r"a_N(R)=\frac{V_{\rm bar}^2(R)}{R}",
    "F_proj(R) = 1 + S_tau alpha ln(1 + a0 / a_N(R))": (
        r"F_{\rm proj}(R)=1+S_\tau\alpha\ln\!\left(1+\frac{a_0}{a_N(R)}\right)"
    ),
    "V_model(R) = F_proj(R) V_bar(R)": r"V_{\rm model}(R)=F_{\rm proj}(R)V_{\rm bar}(R)",
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


FIGURE_MAP = {
    "figures/quality_pass_rms_distribution.svg": "quality_pass_rms_distribution.png",
    "figures/control_forest_plot.svg": "control_forest_plot.png",
    "figures/distance_stratified_effects.svg": "distance_stratified_effects.png",
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def illustrative_rotation_rows() -> dict[str, list[dict[str, str]]]:
    path = ILLUSTRATIVE_CURVES / "paper1_context_rotation_points.csv"
    if not path.exists():
        return {}
    rows: dict[str, list[dict[str, str]]] = {}
    for row in read_csv(path):
        rows.setdefault(row["GalaxyName"], []).append(row)
    return rows


def render_illustrative_rotation_figure() -> None:
    model_rows = illustrative_rotation_rows()
    galaxies = ["NGC2403", "NGC1705"]
    if not set(galaxies) <= set(model_rows):
        return

    plt.rcParams.update(
        {
            "font.size": 11,
            "axes.titlesize": 12,
            "axes.labelsize": 11,
            "xtick.labelsize": 10,
            "ytick.labelsize": 10,
            "legend.fontsize": 8,
            "figure.dpi": 180,
            "savefig.dpi": 300,
            "axes.spines.top": False,
            "axes.spines.right": False,
        }
    )
    fig, axes = plt.subplots(2, 2, figsize=(9.0, 6.5), sharex="col")
    for col, galaxy in enumerate(galaxies):
        points = sorted(model_rows[galaxy], key=lambda row: float(row["RadiusKpc"]))
        radii = [float(point["RadiusKpc"]) for point in points]
        vobs = [float(point["VobsKms"]) for point in points]
        verr = [float(point["ErrVobsKms"]) for point in points]
        vbar = [float(point["VbarKms"]) for point in points]
        projection = [float(point["AbsResidualProjection"]) for point in points]
        mond = [float(point["AbsResidualMONDSimple"]) for point in points]
        rar = [float(point["AbsResidualRAR"]) for point in points]
        cls = points[0]["Class"]

        ax_curve = axes[0][col]
        ax_curve.errorbar(
            radii,
            vobs,
            yerr=verr,
            fmt="o",
            ms=3.3,
            lw=0.8,
            color="#111827",
            ecolor="#9ca3af",
            capsize=1.4,
            label="$V_{\\rm obs}$",
            zorder=5,
        )
        ax_curve.plot(radii, vbar, color="#6b7280", lw=1.35, linestyle="--", label="$V_{\\rm bar}$ baseline")
        ax_curve.set_title(f"{galaxy} external class {cls}", fontsize=11)
        ax_curve.set_ylabel("velocity [km s$^{-1}$]")
        ax_curve.grid(True, alpha=0.22)
        if col == 1:
            ax_curve.legend(frameon=False, fontsize=7.5, loc="best")

        ax_diag = axes[1][col]
        ax_diag.axhline(0.0, color="#111827", lw=0.7, alpha=0.5)
        ax_diag.plot(radii, projection, color="#b91c1c", lw=1.25, label="projection")
        ax_diag.plot(radii, mond, color="#2563eb", lw=1.0, linestyle="-.", label="MOND")
        ax_diag.plot(radii, rar, color="#0891b2", lw=1.0, linestyle=":", label="RAR")
        ax_diag.set_ylabel("absolute log residual")
        ax_diag.set_xlabel("radius [kpc]")
        ax_diag.grid(True, alpha=0.22)
        if col == 1:
            ax_diag.legend(frameon=False, fontsize=7.5, loc="best")

    fig.suptitle("External-label rotation-curve context", fontsize=12)
    fig.tight_layout(rect=(0, 0, 1, 0.96))
    FIGURES.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIGURES / "illustrative_rotation_curves.png", bbox_inches="tight", metadata={"CreationDate": None})
    plt.close(fig)


def tex_escape(text: str) -> str:
    placeholders: list[str] = []

    def code_sub(match: re.Match[str]) -> str:
        code = match.group(1)
        if re.search(r"[/.]", code) and " " not in code:
            placeholders.append(r"\path{" + code + "}")
        else:
            placeholders.append(r"\texttt{" + tex_escape_plain(code) + "}")
        return f"@@CODE{len(placeholders) - 1}@@"

    text = re.sub(r"`([^`]+)`", code_sub, text)
    text = tex_escape_plain(text)
    text = re.sub(
        r"doi:([0-9][0-9A-Za-z./-]*[0-9A-Za-z/-])",
        r"\\href{https://doi.org/\1}{\\nolinkurl{doi:\1}}",
        text,
    )
    text = text.replace("α", r"$\alpha$")
    text = text.replace("μ", r"$\mu$")
    text = text.replace("Δ", r"$\Delta$")
    text = text.replace("≈", r"$\approx$")
    text = text.replace("<=", r"$\leq$")
    text = text.replace(">=", r"$\geq$")
    text = text.replace("<<", r"$\ll$")
    text = text.replace(">>", r"$\gg$")
    text = text.replace("C>A", r"C$>$A")
    text = text.replace("C-minus-A", r"C-minus-A")
    text = text.replace("C-A", r"C-A")
    for idx, value in enumerate(placeholders):
        text = text.replace(f"@@CODE{idx}@@", value)
    return text


def tex_escape_plain(text: str) -> str:
    replacements = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    return "".join(replacements.get(char, char) for char in text)


def table_to_latex(rows: list[str]) -> list[str]:
    parsed = [[cell.strip() for cell in row.strip().strip("|").split("|")] for row in rows]
    header = parsed[0]
    body = parsed[2:]
    widths = " ".join(["Y"] * len(header))
    out = [
        r"\begin{table}[htbp]",
        r"\centering",
        r"\footnotesize",
        r"\setlength{\tabcolsep}{3pt}",
        rf"\begin{{tabularx}}{{\linewidth}}{{{widths}}}",
        r"\toprule",
        " & ".join(tex_escape(cell) for cell in header) + r" \\",
        r"\midrule",
    ]
    for row in body:
        out.append(" & ".join(tex_escape(cell) for cell in row) + r" \\")
    out.extend([r"\bottomrule", r"\end{tabularx}", r"\end{table}"])
    return out


def image_to_latex(line: str) -> list[str]:
    match = re.match(r"!\[(.*?)\]\((.*?)\)", line)
    if not match:
        return []
    caption, source_path = match.groups()
    caption = re.sub(r"^Figure\s+\d+\.\s*", "", caption)
    filename = FIGURE_MAP.get(source_path)
    if filename is None:
        return []
    return [
        r"\begin{figure}[htbp]",
        r"\centering",
        rf"\includegraphics[width=0.86\linewidth]{{figures/{filename}}}",
        rf"\caption{{{tex_escape(caption)}}}",
        rf"\label{{fig:{Path(filename).stem}}}",
        r"\end{figure}",
    ]


def code_line_to_latex(line: str) -> str:
    if line.startswith("python "):
        return rf"\texttt{{python}} \path{{{line[len('python '):]}}}\\"
    if "/" in line and " " not in line:
        return rf"\path{{{line}}}\\"
    return r"\texttt{" + tex_escape_plain(line) + r"}\\"


def convert_markdown_to_latex(markdown: str) -> str:
    lines = markdown.splitlines()
    title = lines[0].lstrip("# ").strip()
    output: list[str] = []
    output.extend(
        [
            r"\documentclass[11pt]{article}",
            r"\usepackage[utf8]{inputenc}",
            r"\usepackage[T1]{fontenc}",
            r"\usepackage{amsmath}",
            r"\usepackage{amssymb}",
            r"\usepackage{booktabs}",
            r"\usepackage{graphicx}",
            r"\usepackage{geometry}",
            r"\usepackage{hyperref}",
            r"\usepackage{xurl}",
            r"\usepackage{tabularx}",
            r"\geometry{margin=1in}",
            r"\emergencystretch=2em",
            r"\newcolumntype{Y}{>{\raggedright\arraybackslash}X}",
            r"\hypersetup{colorlinks=true,linkcolor=blue,citecolor=blue,urlcolor=blue}",
            rf"\title{{{tex_escape(title)}}}",
            r"\author{Jozsef Olcsak}",
            r"\date{May 14, 2026}",
            r"\begin{document}",
            r"\maketitle",
        ]
    )

    index = 1
    in_abstract = False
    while index < len(lines):
        line = lines[index]
        stripped = line.strip()

        if not stripped:
            index += 1
            continue

        if stripped == "## Abstract":
            output.append(r"\begin{abstract}")
            in_abstract = True
            index += 1
            continue

        if stripped.startswith("## ") and in_abstract:
            output.append(r"\end{abstract}")
            in_abstract = False

        if stripped == "$$":
            formula_lines = []
            index += 1
            while index < len(lines) and lines[index].strip() != "$$":
                formula_lines.append(lines[index].strip())
                index += 1
            formula = FORMULAS.get(" ".join(formula_lines), " ".join(formula_lines))
            output.extend([r"\begin{equation}", formula, r"\end{equation}"])
            index += 1
            continue

        if stripped.startswith("```"):
            block = []
            index += 1
            while index < len(lines) and not lines[index].strip().startswith("```"):
                block.append(lines[index])
                index += 1
            output.extend([r"\begin{flushleft}", r"\footnotesize"])
            output.extend(code_line_to_latex(line) for line in block)
            output.append(r"\end{flushleft}")
            index += 1
            continue

        if stripped.startswith("|") and index + 1 < len(lines) and lines[index + 1].strip().startswith("|"):
            table = []
            while index < len(lines) and lines[index].strip().startswith("|"):
                table.append(lines[index])
                index += 1
            output.extend(table_to_latex(table))
            continue

        if stripped.startswith("!["):
            output.extend(image_to_latex(stripped))
            index += 1
            continue

        if stripped.startswith("## "):
            heading = re.sub(r"^\d+\.\s+", "", stripped[3:])
            if heading == "References":
                output.append(r"\section*{References}")
            else:
                output.append(rf"\section{{{tex_escape(heading)}}}")
            index += 1
            continue

        if stripped.startswith("### "):
            output.append(rf"\subsection{{{tex_escape(stripped[4:])}}}")
            index += 1
            continue

        if re.match(r"^\d+\.\s+", stripped):
            items = []
            while index < len(lines) and re.match(r"^\d+\.\s+", lines[index].strip()):
                items.append(re.sub(r"^\d+\.\s+", "", lines[index].strip()))
                index += 1
            output.append(r"\begin{enumerate}")
            output.extend(rf"\item {tex_escape(item)}" for item in items)
            output.append(r"\end{enumerate}")
            continue

        if stripped.startswith("- "):
            items = []
            while index < len(lines) and lines[index].strip().startswith("- "):
                items.append(lines[index].strip()[2:])
                index += 1
            output.append(r"\begin{itemize}")
            output.extend(rf"\item {tex_escape(item)}" for item in items)
            output.append(r"\end{itemize}")
            continue

        paragraph = [stripped]
        index += 1
        while index < len(lines):
            nxt = lines[index].strip()
            if (
                not nxt
                or nxt.startswith("#")
                or nxt.startswith("|")
                or nxt.startswith("!")
                or nxt.startswith("```")
                or nxt == "$$"
                or nxt.startswith("- ")
                or re.match(r"^\d+\.\s+", nxt)
            ):
                break
            paragraph.append(nxt)
            index += 1
        output.append(tex_escape(" ".join(paragraph)) + "\n")

    if in_abstract:
        output.append(r"\end{abstract}")
    latex = "\n".join(output)
    data_anchor = (
        "The statistic is intentionally simple, because the sample is modest and the main risk is not underfitting "
        "but over-interpreting a flexible analysis.\n"
    )
    illustrative_block = r"""
\begin{figure}[htbp]
\centering
\includegraphics[width=0.94\linewidth]{figures/illustrative_rotation_curves.png}
\caption{External-label rotation-curve context for NGC2403, a regular class-A disk, and NGC1705, a disturbed class-C dwarf. The upper panels show observed rotation curves against the baryonic baseline; the lower panels show the per-radius absolute residual profiles that feed the score families. This visualization is not a primary endpoint and is not used for labeling, threshold selection, or model tuning.}
\label{fig:illustrative_rotation_curves}
\end{figure}
"""
    if data_anchor in latex:
        latex = latex.replace(data_anchor, data_anchor + illustrative_block + "\n", 1)
    output.extend([r"\end{document}", ""])
    return latex + "\n" + "\n".join([r"\end{document}", ""])


def render_png_figures() -> None:
    FIGURES.mkdir(parents=True, exist_ok=True)
    for source, target in FIGURE_MAP.items():
        svg = PACKET / source
        doc = fitz.open(str(svg))
        pix = doc[0].get_pixmap(matrix=fitz.Matrix(2.5, 2.5), alpha=False)
        pix.save(FIGURES / target)
        shutil.copy2(svg, FIGURES / Path(source).name)
    render_illustrative_rotation_figure()


def build_zip() -> None:
    if ZIP_PATH.exists():
        ZIP_PATH.unlink()
    with zipfile.ZipFile(ZIP_PATH, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(ARXIV.rglob("*")):
            if path.is_file() and path.suffix not in {".aux", ".log", ".out", ".pdf"}:
                arcname = str(path.relative_to(ARXIV))
                info = zipfile.ZipInfo(arcname)
                info.date_time = (2026, 5, 14, 0, 0, 0)
                info.compress_type = zipfile.ZIP_DEFLATED
                archive.writestr(info, path.read_bytes())


def main() -> None:
    ARXIV.mkdir(exist_ok=True)
    render_png_figures()
    (ARXIV / "main.tex").write_text(convert_markdown_to_latex(SOURCE.read_text(encoding="utf-8")), encoding="utf-8")
    (ARXIV / "README.md").write_text(
        "\n".join(
            [
                "# arXiv source package",
                "",
                "Upload the contents of this directory, or `arxiv_submission_source.zip`, to arXiv.",
                "The PNG figures are generated from the canonical SVG figures in the manuscript packet.",
                "The full reproducibility package is archived at doi:10.5281/zenodo.20183485.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    build_zip()
    print(ARXIV / "main.tex")
    print(ZIP_PATH)


if __name__ == "__main__":
    main()
