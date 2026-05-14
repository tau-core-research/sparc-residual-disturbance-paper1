"""Import helpers for source-locked external SPARC proxy catalogues."""

from __future__ import annotations

import csv
import gzip
import re
from dataclasses import dataclass
from pathlib import Path

from taucore.external import EXTERNAL_PROXY_FIELDNAMES


@dataclass(frozen=True)
class ProxyLayer:
    hi_asymmetry: str = ""
    hi_source: str = ""
    velocity_lopsidedness: str = ""
    velocity_source: str = ""
    bar_or_warp: str = ""
    bar_source: str = ""
    interaction: str = ""
    interaction_source: str = ""
    near_neighbor_density: str = ""
    environment_source: str = ""
    group_environment: str = ""
    notes: str = ""


@dataclass(frozen=True)
class HecateEntry:
    pgc: str = ""
    objname: str = ""
    distance_mpc: str = ""
    velocity_kms: str = ""
    morph_t: str = ""
    stellar_mass_log: str = ""


def normalize_name(value: str) -> str:
    return re.sub(r"[^A-Z0-9]", "", value.upper())


def name_aliases(value: str) -> set[str]:
    key = normalize_name(value)
    if not key:
        return set()
    aliases = {key}
    numeric_catalog = re.match(r"^(UGC|DDO)0*(\d+)$", key)
    if numeric_catalog:
        aliases.add(f"{numeric_catalog.group(1)}{int(numeric_catalog.group(2))}")
    eso_with_g = re.match(r"^ESO0*(\d+)G0*(\d+)$", key)
    if eso_with_g:
        aliases.add(f"ESO{int(eso_with_g.group(1)):03d}G{int(eso_with_g.group(2)):03d}")
        aliases.add(f"ESO{int(eso_with_g.group(1)):03d}{int(eso_with_g.group(2)):03d}")
    eso_without_g = re.match(r"^ESO0*(\d+)(\d{3})$", key)
    if eso_without_g:
        aliases.add(f"ESO{int(eso_without_g.group(1)):03d}G{int(eso_without_g.group(2)):03d}")
        aliases.add(f"ESO{int(eso_without_g.group(1)):03d}{int(eso_without_g.group(2)):03d}")
    return aliases


def ugc_number(galaxy_name: str) -> str:
    match = re.match(r"UGC0*(\d+)$", normalize_name(galaxy_name))
    return str(int(match.group(1))) if match else ""


def _slice(raw: str, start: int, end: int) -> str:
    return raw[start - 1 : end].strip()


def _read_lines(path: Path) -> list[str]:
    if path.suffix == ".gz":
        with gzip.open(path, "rt", encoding="utf-8", errors="ignore") as handle:
            return handle.read().splitlines()
    return path.read_text(encoding="utf-8", errors="ignore").splitlines()


def _rc3_bar_flag(type_code: str) -> str:
    compact = normalize_name(type_code)
    if not compact or "?" in type_code:
        return ""
    if "B" in compact or "X" in compact:
        return "1"
    if "A" in compact:
        return "0"
    return ""


def read_rc3_bar_proxy(path: str | Path) -> dict[str, ProxyLayer]:
    rows: dict[str, ProxyLayer] = {}
    for raw in _read_lines(Path(path)):
        name = _slice(raw, 63, 74)
        altname = _slice(raw, 75, 89)
        type_code = _slice(raw, 118, 124)
        flag = _rc3_bar_flag(type_code)
        if not flag:
            continue
        layer = ProxyLayer(
            bar_or_warp=flag,
            bar_source="VizieR VII/155 RC3 morphology family proxy",
            notes=f"RC3 type={type_code}; bar/intermediate-bar proxy only, not a warp flag.",
        )
        for key in {normalize_name(name), normalize_name(altname)}:
            if key:
                rows[key] = layer
    return rows


def read_whisp_morphology(paths: list[str | Path]) -> dict[str, ProxyLayer]:
    rows: dict[str, ProxyLayer] = {}
    for path in paths:
        for raw in _read_lines(Path(path)):
            ugc = _slice(raw, 1, 5)
            if not ugc.isdigit():
                continue
            hi_asymmetry = _slice(raw, 312, 325)
            lopsidedness = _slice(raw, 522, 538)
            if not hi_asymmetry and not lopsidedness:
                continue
            rows[str(int(ugc))] = ProxyLayer(
                hi_asymmetry=hi_asymmetry,
                hi_source="VizieR J/MNRAS/416/2415 WHISP HI morphology",
                notes="WHISP HI map morphology proxies: A asymmetry and Lop lopsidedness.",
            )
    return rows


def _whisp_flag(value: str) -> str:
    stripped = value.strip()
    if not stripped or stripped.lower() == "n.a.":
        return ""
    return "high" if "*" in stripped else "low"


def read_whisp_interaction(path: str | Path) -> dict[str, ProxyLayer]:
    rows: dict[str, ProxyLayer] = {}
    for raw in _read_lines(Path(path)):
        ugc = _slice(raw, 1, 5)
        if not ugc.isdigit():
            continue
        kin = _whisp_flag(_slice(raw, 74, 77))
        interaction = "1" if _slice(raw, 79, 79) == "+" else "0"
        rows[str(int(ugc))] = ProxyLayer(
            velocity_lopsidedness=kin,
            velocity_source="VizieR J/A+A/442/137 WHISP kinematical asymmetry flag",
            interaction=interaction,
            interaction_source="VizieR J/A+A/442/137 WHISP interaction flag",
            notes="WHISP categorical kinematical asymmetry and interaction flags.",
        )
    return rows


def _reynolds_value(raw: str, start: int, end: int) -> str:
    value = _slice(raw, start, end)
    return value if value and value != "?" else ""


def read_reynolds_asymmetry(paths: list[str | Path]) -> dict[str, ProxyLayer]:
    rows: dict[str, ProxyLayer] = {}
    for path in paths:
        table = Path(path).name
        is_lvhis = table == "tablea1.dat"
        for raw in _read_lines(Path(path)):
            name = _slice(raw, 1, 8 if is_lvhis else 7)
            if not name:
                continue
            amap = _reynolds_value(raw, 43 if is_lvhis else 42, 46 if is_lvhis else 45)
            avel = _reynolds_value(raw, 58 if is_lvhis else 57, 62 if is_lvhis else 61)
            if not amap and not avel:
                continue
            rows[normalize_name(name)] = ProxyLayer(
                hi_asymmetry=amap,
                hi_source="VizieR J/MNRAS/493/5089 Reynolds+2020 Amap",
                velocity_lopsidedness=avel,
                velocity_source="VizieR J/MNRAS/493/5089 Reynolds+2020 Avel",
                near_neighbor_density=_reynolds_value(raw, 10 if is_lvhis else 9, 14 if is_lvhis else 13),
                environment_source="VizieR J/MNRAS/493/5089 Reynolds+2020 logrho",
                notes="Reynolds+2020 diagnostic HI asymmetry; Avel is not WHISP epsilon_kin.",
            )
    return rows


def _parse_float(value: str) -> float | None:
    try:
        return float(value.strip())
    except ValueError:
        return None


def _csv_float(value: str) -> str:
    parsed = _parse_float(value)
    return f"{parsed:.4g}" if parsed is not None else ""


def _hecate_aliases(row: dict[str, str]) -> set[str]:
    aliases = set()
    for field in ("OBJNAME", "ID_NED", "ID_NEDD", "ID_IRAS"):
        value = row.get(field, "")
        if normalize_name(value) == "-":
            continue
        aliases.update(name_aliases(value))
    pgc = row.get("PGC", "").strip()
    if pgc.isdigit():
        number = str(int(pgc))
        aliases.add(f"PGC{number}")
        aliases.add(f"PGC{int(pgc):06d}")
    return aliases


def read_hecate_crossmatch(path: str | Path) -> dict[str, HecateEntry]:
    """Read HECATE identity aliases and basic host metadata.

    HECATE is treated as a crossmatch layer here, not as a direct disturbance
    label source.
    """

    rows: dict[str, HecateEntry] = {}
    with Path(path).open(newline="", encoding="utf-8", errors="ignore") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            aliases = _hecate_aliases(row)
            if not aliases:
                continue
            entry = HecateEntry(
                pgc=row.get("PGC", "").strip(),
                objname=row.get("OBJNAME", "").strip(),
                distance_mpc=_csv_float(row.get("D", "")),
                velocity_kms=_csv_float(row.get("V", "")),
                morph_t=_csv_float(row.get("T", "")),
                stellar_mass_log=_csv_float(row.get("logM_HEC", "")),
            )
            for alias in aliases:
                rows[alias] = entry
    return rows


def read_yu_alfalfa_profile_asymmetry(path: str | Path) -> dict[str, ProxyLayer]:
    """Read Yu+2022 ALFALFA global HI profile asymmetry by UGC/AGC id.

    The Yu catalogue uses integrated HI profile asymmetry, not resolved HI
    morphology. Keep it as a conservative fallback when stronger HI-map
    proxies are absent.
    """

    rows: dict[str, ProxyLayer] = {}
    for raw in _read_lines(Path(path)):
        if not raw.startswith("AGC"):
            continue
        agc = _slice(raw, 5, 10)
        if not agc.isdigit():
            continue
        ugc = str(int(agc))
        if int(agc) >= 100000:
            continue
        af = _parse_float(_slice(raw, 80, 83))
        ac = _parse_float(_slice(raw, 90, 94))
        notes = _slice(raw, 150, 158)
        if af is None:
            continue
        if af >= 1.2:
            proxy = "high"
        elif af <= 1.05:
            proxy = "low"
        else:
            proxy = ""
        if not proxy:
            continue
        asymmetry_note = f"Af={af:.2f}; Ac={ac:.2f}" if ac is not None else f"Af={af:.2f}"
        rows[ugc] = ProxyLayer(
            hi_asymmetry=proxy,
            hi_source="VizieR J/ApJS/261/21 Yu+2022 ALFALFA global HI profile asymmetry",
            notes="Yu+2022 global HI profile asymmetry fallback; "
            + asymmetry_note
            + (f"; notes={notes}" if notes else ""),
        )
    return rows


def read_ungc_environment(path: str | Path) -> dict[str, ProxyLayer]:
    """Read Karachentsev+2013 Local Volume tidal-index environment proxies."""

    rows: dict[str, ProxyLayer] = {}
    for raw in _read_lines(Path(path)):
        name = _slice(raw, 1, 18)
        if not name:
            continue
        theta_1 = _parse_float(_slice(raw, 94, 97))
        main_disturber = _slice(raw, 99, 113)
        theta_5 = _parse_float(_slice(raw, 115, 118))
        theta_j = _parse_float(_slice(raw, 120, 124))
        if theta_1 is None and theta_j is None:
            continue
        if theta_1 is None:
            group_environment = ""
        elif theta_1 > 0:
            group_environment = "group"
        else:
            group_environment = "isolated"
        density = f"{theta_j:.2f}" if theta_j is not None else ""
        notes = []
        if theta_1 is not None:
            notes.append(f"Theta1={theta_1:.1f}")
        if theta_5 is not None:
            notes.append(f"Theta5={theta_5:.1f}")
        if theta_j is not None:
            notes.append(f"Thetaj={theta_j:.2f}")
        if main_disturber:
            notes.append(f"main_disturber={main_disturber}")
        rows[normalize_name(name)] = ProxyLayer(
            near_neighbor_density=density,
            environment_source="VizieR J/AJ/145/101 Karachentsev+2013 Local Volume tidal indices",
            group_environment=group_environment,
            notes="Karachentsev+2013 environment proxy; " + "; ".join(notes),
        )
    return rows


def _append(existing: str, addition: str) -> str:
    if not addition:
        return existing
    return f"{existing}; {addition}" if existing else addition


def build_external_proxy_manifest(
    galaxy_names: list[str],
    rc3_by_name: dict[str, ProxyLayer],
    whisp_morph_by_ugc: dict[str, ProxyLayer],
    whisp_flags_by_ugc: dict[str, ProxyLayer],
    reynolds_by_name: dict[str, ProxyLayer],
    yu_profile_by_ugc: dict[str, ProxyLayer] | None = None,
    ungc_environment_by_name: dict[str, ProxyLayer] | None = None,
) -> list[dict[str, str]]:
    rows = []
    for galaxy_name in galaxy_names:
        key = normalize_name(galaxy_name)
        ugc = ugc_number(galaxy_name)
        layers = [
            rc3_by_name.get(key, ProxyLayer()),
            whisp_morph_by_ugc.get(ugc, ProxyLayer()),
            whisp_flags_by_ugc.get(ugc, ProxyLayer()),
            reynolds_by_name.get(key, ProxyLayer()),
            (yu_profile_by_ugc or {}).get(ugc, ProxyLayer()),
            (ungc_environment_by_name or {}).get(key, ProxyLayer()),
        ]
        row = {field: "" for field in EXTERNAL_PROXY_FIELDNAMES}
        row["GalaxyName"] = galaxy_name
        notes = []
        for layer in layers:
            row["HIAsymmetry"] = row["HIAsymmetry"] or layer.hi_asymmetry
            row["HIAsymmetrySource"] = row["HIAsymmetrySource"] or layer.hi_source
            row["VelocityFieldLopsidedness"] = (
                row["VelocityFieldLopsidedness"] or layer.velocity_lopsidedness
            )
            row["VelocityFieldLopsidednessSource"] = (
                row["VelocityFieldLopsidednessSource"] or layer.velocity_source
            )
            row["BarOrWarpFlag"] = row["BarOrWarpFlag"] or layer.bar_or_warp
            row["BarOrWarpSource"] = row["BarOrWarpSource"] or layer.bar_source
            row["InteractionFlag"] = row["InteractionFlag"] or layer.interaction
            row["InteractionSource"] = row["InteractionSource"] or layer.interaction_source
            row["NearNeighborDensity"] = row["NearNeighborDensity"] or layer.near_neighbor_density
            row["EnvironmentSource"] = row["EnvironmentSource"] or layer.environment_source
            row["GroupEnvironmentFlag"] = row["GroupEnvironmentFlag"] or layer.group_environment
            if layer.notes:
                notes.append(layer.notes)

        source_locked = any(
            row[field]
            for field in (
                "HIAsymmetry",
                "VelocityFieldLopsidedness",
                "BarOrWarpFlag",
                "InteractionFlag",
                "NearNeighborDensity",
                "GroupEnvironmentFlag",
            )
        )
        row["SourceLockedBeforeFit"] = "true" if source_locked else "false"
        row["ExternalProxyStatus"] = "source_locked_partial" if source_locked else "missing"
        row["Notes"] = _append("; ".join(notes), "no TPG residual fields used")
        rows.append(row)
    return rows


def write_external_proxy_manifest(rows: list[dict[str, str]], path: str | Path) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=EXTERNAL_PROXY_FIELDNAMES, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
