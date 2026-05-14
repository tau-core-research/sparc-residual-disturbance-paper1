# Selection / Observability Appendix

This appendix addresses the main reviewer-facing selection-function risk: nearby or better-resolved galaxies may reveal structural disturbance more easily than distant systems. The table below is descriptive rather than a new primary endpoint.

## Available Observability Proxies

| proxy | role | status |
| --- | --- | --- |
| SPARC distance | first-order observability and physical-resolution proxy | available for all quality-pass rows |
| maximum rotation-curve radius | radial-coverage / scale proxy | available for all quality-pass rows |
| rotation-curve point count | sampling-density proxy | available for all quality-pass rows |
| mean Vobs uncertainty | kinematic measurement-quality proxy | available for all quality-pass rows |
| inclination and inclination uncertainty | projection-geometry proxy | available for all quality-pass rows after quality gate |
| Hubble type | dwarf/late-type composition proxy | available for all quality-pass rows |
| HECATE stellar mass | mass proxy | incomplete; use only as supportive control |
| HI beam size / physical HI resolution | direct beam-smearing proxy | not present in the current SPARC packet |
| homogeneous resolved HI morphology | direct disturbance observability proxy | partial WHISP-family coverage only |

## Median Balance Summary

| covariate | n A | median A | n B | median B | n C | median C |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| SPARC distance [Mpc] | 17 | 13.8 | 28 | 12.3 | 28 | 7.83 |
| SPARC distance uncertainty [Mpc] | 17 | 2.5 | 28 | 2.8 | 28 | 2.19 |
| maximum fitted rotation-curve radius [kpc] | 17 | 14.86 | 28 | 12.465 | 28 | 6.945 |
| rotation-curve point count | 17 | 17 | 28 | 15.5 | 28 | 13 |
| mean Vobs uncertainty [km/s] | 17 | 2.63545 | 28 | 3.98061 | 28 | 3.56033 |
| inclination [deg] | 17 | 67 | 28 | 63.5 | 28 | 56.5 |
| inclination uncertainty [deg] | 17 | 3 | 28 | 4.5 | 28 | 3.5 |
| SPARC Hubble type code | 17 | 6 | 28 | 8 | 28 | 9 |
| HECATE log stellar mass | 10 | 9.956 | 9 | 10.51 | 11 | 8.771 |

## Composition Checks

- Late-type/dwarf-like proxy (`HubbleType >= 8`): A=6/17, C=21/28.
- WHISP-family external HI morphology coverage in quality-pass A/C: A=0/17, C=18/28.

## Interpretation

The appendix strengthens the paper by making the selection risk explicit rather than burying it in limitations. Distance and radius remain the strongest imbalances, so they should stay in the main text as limitations. The current packet does not include homogeneous beam-size or physical HI-resolution measurements; therefore the paper should not claim that beam smearing or disturbance observability is fully controlled.
