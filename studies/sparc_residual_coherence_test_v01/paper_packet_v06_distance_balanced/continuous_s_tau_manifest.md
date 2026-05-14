# Continuous S_tau Manifest

First residual-blind operational candidate for a continuous Tau Core coherence parameter. This manifest is generated only from external evidence-table text and source fields, not from residuals.

Mapping priority:

```text
1. Downloaded VizieR catalog proxies when present: WHISP, Reynolds, Yu/ALFALFA.
2. Quantitative proxies parsed from evidence text when no downloaded catalog match exists.
3. Evidence-type fallback when no numeric proxy is available.
4. Class fallback only if neither numeric proxy nor evidence type is usable.
```

Counts by mapping method:

| method | n |
| --- | ---: |
| downloaded_catalog_numeric_proxy | 32 |
| evidence_type_fallback | 41 |

| Galaxy | Class | Evidence type | S_tau | soft S_tau | method | reason |
| --- | --- | --- | ---: | ---: | --- | --- |
| CamB | A | regular_kinematics | 0.9 | 0.91 | evidence_type_fallback | regular_kinematics |
| DDO154 | A | regular_kinematics | 0.9 | 0.91 | evidence_type_fallback | regular_kinematics |
| ESO079-G014 | A | regular_kinematics | 0.9 | 0.91 | evidence_type_fallback | regular_kinematics |
| ESO116-G012 | A | regular_kinematics | 0.9 | 0.91 | evidence_type_fallback | regular_kinematics |
| NGC2403 | A | regular_kinematics | 0.9 | 0.91 | evidence_type_fallback | regular_kinematics |
| NGC3198 | A | low_asymmetry | 0.865833 | 0.896333 | downloaded_catalog_numeric_proxy | Amap=0.14; Avel=0.014 |
| NGC3917 | A | regular_kinematics | 0.9 | 0.91 | evidence_type_fallback | regular_kinematics |
| NGC3972 | A | regular_kinematics | 0.9 | 0.91 | evidence_type_fallback | regular_kinematics |
| NGC4183 | A | regular_kinematics | 0.9 | 0.91 | evidence_type_fallback | regular_kinematics |
| NGC4559 | A | low_asymmetry | 0.822917 | 0.879167 | downloaded_catalog_numeric_proxy | Amap=0.15; Avel=0.025 |
| NGC5585 | A | low_asymmetry | 0.772083 | 0.858833 | downloaded_catalog_numeric_proxy | Amap=0.13; Avel=0.044 |
| NGC6503 | A | regular_kinematics | 0.9 | 0.91 | evidence_type_fallback | regular_kinematics |
| NGC7331 | A | regular_kinematics | 0.9 | 0.91 | evidence_type_fallback | regular_kinematics |
| UGC00128 | A | low_asymmetry | 0.81 | 0.874 | downloaded_catalog_numeric_proxy | Af=1.04; Ac=1.15 |
| UGC00191 | A | low_asymmetry | 0.97 | 0.938 | downloaded_catalog_numeric_proxy | Af=1.01; Ac=1.02 |
| UGC05716 | A | low_asymmetry | 0.99 | 0.946 | downloaded_catalog_numeric_proxy | Af=1.01; Ac=1 |
| UGC05764 | A | low_asymmetry | 0.94 | 0.926 | downloaded_catalog_numeric_proxy | Af=1.02; Ac=1.04 |
| D631-7 | B | no_data | 0.5 | 0.75 | evidence_type_fallback | no_data |
| DDO064 | B | other | 0.5 | 0.75 | evidence_type_fallback | other |
| DDO161 | B | other | 0.5 | 0.75 | evidence_type_fallback | other |
| DDO168 | B | other | 0.5 | 0.75 | evidence_type_fallback | other |
| DDO170 | B | no_data | 0.5 | 0.75 | evidence_type_fallback | no_data |
| F571-8 | B | no_data | 0.5 | 0.75 | evidence_type_fallback | no_data |
| F574-1 | B | no_data | 0.5 | 0.75 | evidence_type_fallback | no_data |
| F583-4 | B | no_data | 0.5 | 0.75 | evidence_type_fallback | no_data |
| KK98-251 | B | no_data | 0.5 | 0.75 | evidence_type_fallback | no_data |
| NGC0247 | B | other | 0.5 | 0.75 | evidence_type_fallback | other |
| NGC0801 | B | no_data | 0.5 | 0.75 | evidence_type_fallback | no_data |
| NGC1003 | B | other | 0.5 | 0.75 | evidence_type_fallback | other |
| NGC1090 | B | other | 0.5 | 0.75 | evidence_type_fallback | other |
| NGC2903 | B | mixed | 0.5 | 0.75 | evidence_type_fallback | mixed |
| NGC5033 | B | other | 0.5 | 0.75 | evidence_type_fallback | other |
| NGC5371 | B | other | 0.5 | 0.75 | evidence_type_fallback | other |
| NGC6015 | B | other | 0.5 | 0.75 | evidence_type_fallback | other |
| UGC02259 | B | no_data | 0.5 | 0.75 | evidence_type_fallback | no_data |
| UGC04483 | B | other | 0.375833 | 0.700333 | downloaded_catalog_numeric_proxy | WHISP_A=0.749 |
| UGC05721 | B | mixed | 0.476667 | 0.740667 | downloaded_catalog_numeric_proxy | WHISP_A=0.628; WHISP_Lop=1.371; WHISP_A=0.628; Af=1.07; Ac=1.2 |
| UGC06399 | B | no_data | 0.5 | 0.75 | evidence_type_fallback | no_data |
| UGC07089 | B | mixed | 0 | 0.55 | downloaded_catalog_numeric_proxy | WHISP_A=1.247 |
| UGC07524 | B | mixed | 0.499167 | 0.749667 | downloaded_catalog_numeric_proxy | WHISP_A=0.61; WHISP_Lop=1.403; WHISP_A=0.601; Af=1.05; Ac=1.12 |
| UGC09133 | B | mixed | 0.473333 | 0.739333 | downloaded_catalog_numeric_proxy | WHISP_A=0.632; WHISP_Lop=1.389; WHISP_A=0.632; Af=1.09; Ac=1.27 |
| UGC11820 | B | no_data | 0.73 | 0.842 | downloaded_catalog_numeric_proxy | Af=1.07; Ac=1.2 |
| UGC12732 | B | mixed | 0.520833 | 0.758333 | downloaded_catalog_numeric_proxy | WHISP_A=0.588; WHISP_Lop=1.414; WHISP_A=0.575; Af=1.07; Ac=1.2 |
| UGCA442 | B | other | 0.5 | 0.75 | evidence_type_fallback | other |
| UGCA444 | B | no_data | 0.5 | 0.75 | evidence_type_fallback | no_data |
| IC2574 | C | disturbed_hi | 0.2 | 0.63 | evidence_type_fallback | disturbed_hi |
| NGC0055 | C | disturbed_hi | 0.2 | 0.63 | evidence_type_fallback | disturbed_hi |
| NGC1705 | C | disturbed_hi | 0.2 | 0.63 | evidence_type_fallback | disturbed_hi |
| NGC2366 | C | disturbed_hi | 0.2 | 0.63 | evidence_type_fallback | disturbed_hi |
| NGC2976 | C | tidal | 0.1 | 0.59 | evidence_type_fallback | tidal |
| NGC3109 | C | warp | 0.2 | 0.63 | evidence_type_fallback | warp |
| NGC3741 | C | warp | 0.2 | 0.63 | evidence_type_fallback | warp |
| NGC5055 | C | tidal | 0.71125 | 0.8345 | downloaded_catalog_numeric_proxy | Amap=0.27; Avel=0.036 |
| UGC00731 | C | disturbed_hi | 0.3425 | 0.687 | downloaded_catalog_numeric_proxy | WHISP_A=0.648; WHISP_Lop=1.414; WHISP_A=0.789 |
| UGC02455 | C | disturbed_hi | 0.439167 | 0.725667 | downloaded_catalog_numeric_proxy | WHISP_A=0.673; WHISP_Lop=1.414; WHISP_A=1.126; Af=1.13; Ac=1.19 |
| UGC03580 | C | disturbed_hi | 0.193333 | 0.627333 | downloaded_catalog_numeric_proxy | WHISP_A=0.968; WHISP_Lop=1.376; WHISP_A=0.968 |
| UGC04305 | C | disturbed_hi | 0.09 | 0.586 | downloaded_catalog_numeric_proxy | WHISP_A=1.092; WHISP_Lop=1.414; WHISP_A=1.09 |
| UGC04325 | C | disturbed_hi | 0.229167 | 0.641667 | downloaded_catalog_numeric_proxy | WHISP_A=0.925; WHISP_Lop=1.414; WHISP_A=0.825 |
| UGC04499 | C | disturbed_hi | 0.348333 | 0.689333 | downloaded_catalog_numeric_proxy | WHISP_A=0.714; WHISP_Lop=1.414; WHISP_A=0.782 |
| UGC05253 | C | interaction | 0 | 0.55 | downloaded_catalog_numeric_proxy | WHISP_A=1.46; WHISP_Lop=1.352; WHISP_A=1.477 |
| UGC05829 | C | disturbed_hi | 0.0925 | 0.587 | downloaded_catalog_numeric_proxy | WHISP_A=1.089; WHISP_Lop=1.414; WHISP_A=1.196; Af=1.02; Ac=1.07 |
| UGC05918 | C | disturbed_hi | 0 | 0.55 | downloaded_catalog_numeric_proxy | WHISP_A=1.93; WHISP_Lop=1.397; WHISP_A=1.946 |
| UGC06446 | C | disturbed_hi | 0.400833 | 0.710333 | downloaded_catalog_numeric_proxy | WHISP_A=0.703; WHISP_Lop=1.38; WHISP_A=0.719 |
| UGC06818 | C | interaction | 0.15 | 0.61 | evidence_type_fallback | interaction |
| UGC06917 | C | disturbed_hi | 0.2 | 0.63 | evidence_type_fallback | disturbed_hi |
| UGC06973 | C | interaction | 0.15 | 0.61 | evidence_type_fallback | interaction |
| UGC07323 | C | disturbed_hi | 0.383333 | 0.703333 | downloaded_catalog_numeric_proxy | WHISP_A=0.74; WHISP_Lop=1.414; WHISP_A=0.74 |
| UGC07399 | C | disturbed_hi | 0.0966667 | 0.588667 | downloaded_catalog_numeric_proxy | WHISP_A=1.084; WHISP_Lop=1.381; WHISP_A=1.084 |
| UGC07577 | C | disturbed_hi | 0 | 0.55 | downloaded_catalog_numeric_proxy | WHISP_A=2; WHISP_Lop=1.406; WHISP_A=2 |
| UGC07603 | C | disturbed_hi | 0.235833 | 0.644333 | downloaded_catalog_numeric_proxy | WHISP_A=0.917; WHISP_Lop=1.414; WHISP_A=0.917; Af=1.03; Ac=1.05 |
| UGC08490 | C | disturbed_hi | 0.23 | 0.642 | downloaded_catalog_numeric_proxy | WHISP_A=0.924; WHISP_Lop=1.414; WHISP_A=0.911 |
| UGC08837 | C | disturbed_hi | 0.186667 | 0.624667 | downloaded_catalog_numeric_proxy | WHISP_A=0.976; WHISP_Lop=1.414; WHISP_A=0.896 |
| UGC12632 | C | disturbed_hi | 0.04 | 0.566 | downloaded_catalog_numeric_proxy | WHISP_A=1.152; WHISP_Lop=1.394; WHISP_A=1.168 |
