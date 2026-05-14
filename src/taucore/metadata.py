"""SPARC galaxy-level metadata parsing."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class SparcGalaxyMetadata:
    galaxy_name: str
    hubble_type: int
    distance_mpc: float
    distance_error_mpc: float
    distance_quality: int
    inclination_deg: float
    inclination_error_deg: float


def parse_sparc_table1(path: str | Path) -> dict[str, SparcGalaxyMetadata]:
    """Parse the local compact SPARC Table 1 metadata file.

    Expected columns:
    `Name HubType D(Mpc) e_D Q_D i(deg) e_i`.
    Comment lines starting with `#` are ignored.
    """

    rows: dict[str, SparcGalaxyMetadata] = {}
    for raw_line in Path(path).read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue

        tokens = line.split()
        if len(tokens) < 7:
            continue

        rows[tokens[0]] = SparcGalaxyMetadata(
            galaxy_name=tokens[0],
            hubble_type=int(tokens[1]),
            distance_mpc=float(tokens[2]),
            distance_error_mpc=float(tokens[3]),
            distance_quality=int(tokens[4]),
            inclination_deg=float(tokens[5]),
            inclination_error_deg=float(tokens[6]),
        )

    return rows

