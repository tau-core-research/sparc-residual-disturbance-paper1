"""Coherence-gated galactic activation formulas."""

from __future__ import annotations

import math

KPC_IN_METERS = 3.085677581e19
DEFAULT_ALPHA = 0.360
DEFAULT_A0_M_S2 = 1.2e-10
DEFAULT_UPSILON_DISK = 0.5
DEFAULT_UPSILON_BULGE = 0.7


def baryonic_speed_squared_kms2(
    vgas_kms: float,
    vdisk_kms: float,
    vbul_kms: float,
    upsilon_disk: float = DEFAULT_UPSILON_DISK,
    upsilon_bulge: float = DEFAULT_UPSILON_BULGE,
) -> float:
    """Return SPARC baryonic Newtonian speed squared in `(km/s)^2`."""

    return vgas_kms * abs(vgas_kms) + upsilon_disk * vdisk_kms**2 + upsilon_bulge * vbul_kms**2


def acceleration_m_s2(vn_squared_kms2: float, radius_kpc: float) -> float:
    if radius_kpc <= 0:
        raise ValueError("radius_kpc must be positive.")
    if vn_squared_kms2 <= 0:
        return 0.0
    return vn_squared_kms2 * 1_000_000.0 / (radius_kpc * KPC_IN_METERS)


def tpg_factor(
    a_n_m_s2: float,
    alpha: float = DEFAULT_ALPHA,
    a0_m_s2: float = DEFAULT_A0_M_S2,
    s_tau: float = 1.0,
) -> float:
    """Return `1 + S_tau alpha ln(1 + a0/a_N)`.

    `s_tau=1` is the full high-coherence TPG limit.
    """

    if a_n_m_s2 <= 0:
        return math.nan
    return 1.0 + s_tau * alpha * math.log1p(a0_m_s2 / a_n_m_s2)


def predicted_speed_kms(vn_squared_kms2: float, factor: float) -> float:
    if vn_squared_kms2 <= 0 or not math.isfinite(factor):
        return math.nan
    return factor * math.sqrt(vn_squared_kms2)

