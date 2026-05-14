#!/usr/bin/env python3
"""Download external HI/asymmetry sources for continuous S_tau construction."""

from __future__ import annotations

import csv
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from astroquery.vizier import Vizier


STUDY = ROOT / "studies/sparc_residual_coherence_test_v01"
PACKET = STUDY / "paper_packet_v06_distance_balanced"
SOURCE_DIR = ROOT / "data/external/s_tau_sources"
EVIDENCE_TABLE = PACKET / "external_evidence_table.csv"


CATALOGS = {
    "reynolds2020_hi_asymmetry": "J/MNRAS/493/5089",
    "whisp_hi_morphology": "J/MNRAS/416/2415",
    "yu2022_alfalfa_profile_asymmetry": "J/ApJS/261/21",
    "whisp_merger_morphology": "J/MNRAS/416/2437",
}


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


def clean_cell(value: object) -> str:
    text = str(value)
    if text in {"--", "nan", "None"}:
        return ""
    return text.strip()


def table_to_rows(table) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for item in table:
        rows.append({name: clean_cell(item[name]) for name in table.colnames})
    return rows


def normalize_name(value: str) -> set[str]:
    names: set[str] = set()
    text = value.strip().upper()
    if not text:
        return names
    compact = re.sub(r"[^A-Z0-9]", "", text)
    if compact:
        names.add(compact)
    for prefix in ["UGC", "NGC", "IC", "DDO", "ESO"]:
        match = re.search(rf"\b{prefix}\s*0*([0-9]+)\b", text)
        if match:
            width = 5 if prefix == "UGC" else 4 if prefix in {"NGC", "DDO"} else 0
            number = int(match.group(1))
            names.add(f"{prefix}{number:0{width}d}" if width else f"{prefix}{number}")
    agc = re.search(r"\bAGC\s*0*([0-9]+)\b", text)
    if agc:
        names.add(f"AGC{int(agc.group(1)):06d}")
    return names


def source_aliases(row: dict[str, str], source: str) -> set[str]:
    aliases: set[str] = set()
    for key in ["Name", "SimbadName", "Simbad", "LEDA"]:
        if key in row:
            aliases.update(normalize_name(row[key]))
    if "UGC" in row and row["UGC"]:
        try:
            aliases.add(f"UGC{int(float(row['UGC'])):05d}")
        except ValueError:
            aliases.update(normalize_name(row["UGC"]))
    if "AGC" in row and row["AGC"]:
        try:
            aliases.add(f"AGC{int(float(row['AGC'])):06d}")
        except ValueError:
            aliases.update(normalize_name(row["AGC"]))
    return aliases


def download_catalogs() -> dict[str, list[dict[str, str]]]:
    Vizier.ROW_LIMIT = -1
    all_rows: dict[str, list[dict[str, str]]] = {}
    SOURCE_DIR.mkdir(parents=True, exist_ok=True)
    for source_name, catalog_id in CATALOGS.items():
        tables = Vizier.get_catalogs(catalog_id)
        for key in tables.keys():
            table = tables[key]
            short_table = key.split("/")[-1]
            output = SOURCE_DIR / f"{source_name}_{short_table}.csv"
            rows = table_to_rows(table)
            write_csv(output, list(rows[0].keys()) if rows else [], rows)
            all_rows[f"{source_name}:{short_table}"] = rows
    return all_rows


def match_sources(all_rows: dict[str, list[dict[str, str]]]) -> None:
    evidence_rows = read_csv(EVIDENCE_TABLE)
    targets = {row["GalaxyName"]: row for row in evidence_rows}
    target_aliases = {
        name: normalize_name(name)
        for name in targets
    }

    match_rows: list[dict[str, object]] = []
    for source_key, rows in all_rows.items():
        source_name, table_name = source_key.split(":", maxsplit=1)
        for row in rows:
            aliases = source_aliases(row, source_name)
            if not aliases:
                continue
            for galaxy_name, names in target_aliases.items():
                if not aliases.intersection(names):
                    continue
                match_rows.append(
                    {
                        "GalaxyName": galaxy_name,
                        "Class": targets[galaxy_name]["Class"],
                        "Source": source_name,
                        "Table": table_name,
                        "MatchedAliases": ";".join(sorted(aliases.intersection(names))),
                        "SourceName": row.get("Name") or row.get("SimbadName") or row.get("UGC") or row.get("AGC") or "",
                        "Amap": row.get("Amap", ""),
                        "Avel": row.get("Avel", ""),
                        "Aspec": row.get("Aspec", ""),
                        "Aflux": row.get("Aflux", ""),
                        "Apeak": row.get("Apeak", ""),
                        "WHISP_A": row.get("A", ""),
                        "WHISP_Lop": row.get("Lop", ""),
                        "WHISP_Gini": row.get("Gini", ""),
                        "WHISP_M20": row.get("M20", ""),
                        "WHISP_GM": row.get("GM", ""),
                        "Af": row.get("Af", ""),
                        "Ac": row.get("Ac", ""),
                        "Cv": row.get("Cv", ""),
                        "K": row.get("K", ""),
                    }
                )

    fields = [
        "GalaxyName",
        "Class",
        "Source",
        "Table",
        "MatchedAliases",
        "SourceName",
        "Amap",
        "Avel",
        "Aspec",
        "Aflux",
        "Apeak",
        "WHISP_A",
        "WHISP_Lop",
        "WHISP_Gini",
        "WHISP_M20",
        "WHISP_GM",
        "Af",
        "Ac",
        "Cv",
        "K",
    ]
    match_rows.sort(key=lambda row: (str(row["GalaxyName"]), str(row["Source"]), str(row["Table"])))
    write_csv(PACKET / "s_tau_source_matches.csv", fields, match_rows)

    matched_galaxies = sorted({str(row["GalaxyName"]) for row in match_rows})
    source_counts: dict[str, int] = {}
    for row in match_rows:
        source_counts[str(row["Source"])] = source_counts.get(str(row["Source"]), 0) + 1
    lines = [
        "# S_tau Source Data Coverage",
        "",
        "External HI/asymmetry catalog data downloaded from VizieR and matched to the quality-pass evidence-table galaxies by normalized object names.",
        "",
        f"Quality-pass target galaxies: {len(targets)}",
        f"Matched galaxies: {len(matched_galaxies)}",
        f"Unmatched galaxies: {len(targets) - len(matched_galaxies)}",
        "",
        "| source | matched rows |",
        "| --- | ---: |",
    ]
    for source, count in sorted(source_counts.items()):
        lines.append(f"| {source} | {count} |")
    lines.extend(
        [
            "",
            "Matched galaxies:",
            "",
            "```text",
            ", ".join(matched_galaxies),
            "```",
            "",
            "Raw downloaded tables are stored under `data/external/s_tau_sources/`.",
        ]
    )
    (PACKET / "s_tau_source_coverage.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    all_rows = download_catalogs()
    match_sources(all_rows)


if __name__ == "__main__":
    main()
