"""SPARC rotmod parsing utilities."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class SparcRotmodRow:
    radius_kpc: float
    vobs_kms: float
    err_vobs_kms: float
    vgas_kms: float
    vdisk_kms: float
    vbul_kms: float
    surface_brightness_disk: float
    surface_brightness_bulge: float


@dataclass(frozen=True)
class SparcRotmodTable:
    galaxy_name: str
    rows: tuple[SparcRotmodRow, ...]
    source_path: Path | None = None

    def __post_init__(self) -> None:
        if not self.rows:
            raise ValueError("SPARC rotmod table must contain at least one row.")


def parse_rotmod_file(path: str | Path) -> SparcRotmodTable:
    """Parse a SPARC `*_rotmod.dat` file.

    Expected columns:
    `Rad Vobs errV Vgas Vdisk Vbul SBdisk SBbul`.
    """

    file_path = Path(path)
    rows: list[SparcRotmodRow] = []

    for raw_line in file_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue

        tokens = line.split()
        if len(tokens) < 8:
            continue

        rows.append(
            SparcRotmodRow(
                radius_kpc=float(tokens[0]),
                vobs_kms=max(0.0, float(tokens[1])),
                err_vobs_kms=max(0.0, float(tokens[2])),
                vgas_kms=float(tokens[3]),
                vdisk_kms=max(0.0, float(tokens[4])),
                vbul_kms=max(0.0, float(tokens[5])),
                surface_brightness_disk=max(0.0, float(tokens[6])),
                surface_brightness_bulge=max(0.0, float(tokens[7])),
            )
        )

    if not rows:
        raise ValueError(f"SPARC rotmod file contains no data rows: {file_path}")

    rows.sort(key=lambda row: row.radius_kpc)
    name = file_path.name.split("_rotmod", maxsplit=1)[0]
    return SparcRotmodTable(name, tuple(rows), file_path)


def find_rotmod_files(root: str | Path, include_backups: bool = False) -> list[Path]:
    """Find rotmod files below `root`.

    By default this only returns canonical `*_rotmod.dat` files and skips
    `*.dat_` backup copies.
    """

    root_path = Path(root)
    patterns: Iterable[str] = ("*_rotmod.dat", "*_rotmod.dat_") if include_backups else ("*_rotmod.dat",)
    files: list[Path] = []
    for pattern in patterns:
        files.extend(root_path.rglob(pattern))
    return sorted(set(files))


def load_rotmod_directory(root: str | Path, include_backups: bool = False) -> list[SparcRotmodTable]:
    return [parse_rotmod_file(path) for path in find_rotmod_files(root, include_backups)]
