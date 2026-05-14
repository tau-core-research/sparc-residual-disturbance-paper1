# Frozen Soft S_tau Mapping v0.1

Status: frozen operational candidate for held-out source-family testing. This rule was set after the hard and direct mappings proved too suppressive, and before any future independent validation run.

## Formula

The extended candidate is:

```text
F_tau(a_N, S_tau) = 1 + S_tau alpha ln(1 + a0/a_N)
```

The old TPG/high-coherence limit is:

```text
S_tau = 1
```

## Soft Mapping Constants

For positive asymmetry-like quantities where larger means less coherent:

```text
S_tau_component = clamp(0.95 - 0.40 * min(value / scale, 1), 0.55, 0.95)
```

Scales:

```text
Amap scale      = 0.8
Avel scale      = 0.15
WHISP_A scale   = 1.2
WHISP_Lop scale = 1.5
```

For profile ratios such as Yu/ALFALFA `Af` and `Ac`:

```text
excess = min(max(0, value - 1) / 0.5, 1)
S_tau_component = clamp(0.95 - 0.40 * excess, 0.55, 0.95)
```

Galaxy-level `S_tau` is the median of available source components. Missing numeric source data fall back to the predeclared evidence-type soft transform already recorded in `continuous_s_tau_manifest.csv`.

## Held-Out Source Families

The source-family split is:

```text
WHISP family  = whisp_hi_morphology + whisp_merger_morphology
Global family = Reynolds+2020 HI asymmetry + Yu+2022 ALFALFA profile asymmetry
```

The held-out sanity check is not a final validation. It asks whether the soft mapping behaves similarly when built from one source family and compared on galaxies also covered by the other source family.
