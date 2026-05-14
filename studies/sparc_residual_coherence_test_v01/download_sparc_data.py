#!/usr/bin/env python3
"""Download the SPARC inputs used by the public reproduction workflow.

The repository ships derived analysis tables, but not the raw SPARC rotmod
files. This script downloads the public SPARC Zenodo archive and places the
files at the paths expected by the regeneration scripts.
"""

from __future__ import annotations

import shutil
import zipfile
from pathlib import Path
from urllib.request import urlretrieve


ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data"
EXTERNAL = DATA / "external"
SPARC = DATA / "sparc"
ROTMOD_DIR = SPARC / "Rotmod_LTG"

ZENODO_RECORD = "https://zenodo.org/records/16284118"
ROTMOD_URL = f"{ZENODO_RECORD}/files/Rotmod_LTG.zip?download=1"
TABLE1_URL = f"{ZENODO_RECORD}/files/SPARC_Lelli2016c.mrt?download=1"


def download(url: str, output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists() and output.stat().st_size > 0:
        print(f"exists: {output}")
        return
    print(f"download: {url}")
    urlretrieve(url, output)


def write_compact_table1(mrt_path: Path, output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# SPARC Table 1 compact metadata derived from SPARC_Lelli2016c.mrt",
        "# Source: https://doi.org/10.5281/zenodo.16284118",
        "# Columns: Galaxy name | HubType | D (Mpc) | e_D (Mpc) | f_D | Inc (deg) | e_Inc (deg)",
        "#",
        "# Name          HubType  D(Mpc)  e_D   f_D  i(deg)  e_i",
    ]
    for raw in mrt_path.read_text(encoding="utf-8").splitlines():
        stripped = raw.strip()
        if not stripped or stripped.startswith(("Title:", "Authors:", "Table:", "=", "-", "Byte", "Bytes", "Note")):
            continue
        parts = stripped.split()
        if len(parts) < 7:
            continue
        try:
            hubble_type = int(parts[1])
            distance = float(parts[2])
            distance_error = float(parts[3])
            distance_method = int(parts[4])
            inclination = float(parts[5])
            inclination_error = float(parts[6])
        except ValueError:
            continue
        lines.append(
            f"{parts[0]:<12} {hubble_type:>3d} {distance:>10.2f} {distance_error:>6.2f} "
            f"{distance_method:>3d} {inclination:>8.1f} {inclination_error:>6.1f}"
        )
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote: {output}")


def extract_rotmods(zip_path: Path) -> None:
    ROTMOD_DIR.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path) as archive:
        members = [member for member in archive.namelist() if member.endswith("_rotmod.dat")]
        for member in members:
            target = ROTMOD_DIR / Path(member).name
            if not target.exists():
                with archive.open(member) as src, target.open("wb") as dst:
                    shutil.copyfileobj(src, dst)
    print(f"rotmod files: {len(list(ROTMOD_DIR.glob('*_rotmod.dat')))} in {ROTMOD_DIR}")


def main() -> None:
    archive_dir = DATA / "raw" / "sparc_zenodo_16284118"
    rotmod_zip = archive_dir / "Rotmod_LTG.zip"
    table1_mrt = archive_dir / "SPARC_Lelli2016c.mrt"

    download(ROTMOD_URL, rotmod_zip)
    download(TABLE1_URL, table1_mrt)
    extract_rotmods(rotmod_zip)
    write_compact_table1(table1_mrt, EXTERNAL / "SPARC_Table1.txt")


if __name__ == "__main__":
    main()
