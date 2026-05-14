# Inclination And Systematics Appendix

This appendix collects geometry and measurement-systematics risks that are not fully resolved by the current packet. It is intentionally conservative: the aim is to state what remains vulnerable, not to promote a new endpoint.

## Inclination-Bin Residual Summary

| inclination bin | n A | median A | n C | median C | C-A direction |
| --- | ---: | ---: | ---: | ---: | --- |
| 30-45 | 0 |  | 4 | 0.211381 |  |
| 45-60 | 4 | 0.1315 | 11 | 0.146478 | C>A |
| 60-75 | 8 | 0.136373 | 7 | 0.239111 | C>A |
| 75-85 | 5 | 0.101666 | 6 | 0.264812 | C>A |

## Risk Counts

| class | n | inc < 40 | inc > 75 | inc err >= 7 | mean Vobs err >= 5 | Rmax < 5 kpc |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| A | 17 | 0 | 4 | 3 | 6 | 2 |
| C | 28 | 2 | 4 | 5 | 7 | 6 |

## Remaining Systematics

- Edge-on systems can suffer from line-of-sight integration, dust, and vertical structure effects even when they pass the inclination quality gate.
- Lower-inclination systems can amplify deprojection uncertainty, especially when non-circular motions are present.
- Beam smearing is not directly controlled because homogeneous beam-size or physical HI-resolution measurements are not yet in the packet.
- Asymmetric drift and pressure support can matter in low-mass or gas-rich galaxies and may increase residual scatter independently of the fixed low-acceleration residual score.
- Non-circular motions, bars, tidal disturbances, and warps are partly the phenomenon being labeled, but they also make any smooth axisymmetric rotation-curve score less appropriate.

Interpretation: the current quality gate removes the most extreme inclination failures, but it does not eliminate geometry or kinematic-systematics concerns. These risks should remain limitations until a follow-up sample includes homogeneous resolution, beam, and velocity-field quality metadata.
