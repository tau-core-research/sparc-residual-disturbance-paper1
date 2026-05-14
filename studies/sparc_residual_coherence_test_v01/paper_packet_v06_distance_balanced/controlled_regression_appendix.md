# Controlled Regression Appendix

These regressions are stress checks, not replacements for the frozen primary median/permutation endpoint. The dependent variable is galaxy-level `rms_log_tpg`. The class coefficient is coded `C=1, A=0`; positive values mean C galaxies retain larger residual scatter after the listed observability covariates are included.

The estimator is Huber robust regression, chosen because the A/C sample includes high-leverage residual-scatter rows. Covariates are standardized, except the class indicator. Distance and maximum radius enter as log-scaled standardized variables. The reported p-value is a label-permutation p-value for the class coefficient with the covariate matrix held fixed.

| model | n | class coeff | one-sided permutation p | bootstrap 95% CI | covariates |
| --- | ---: | ---: | ---: | --- | --- |
| class_only | 45 | 0.091688 | 0.00149925 | [0.0378615, 0.155902] |  |
| distance_only | 45 | 0.0760024 | 0.00949525 | [-0.00506519, 0.147939] | log_DistanceMpc |
| distance_radius | 45 | 0.0459048 | 0.089955 | [-0.0669473, 0.113627] | log_DistanceMpc;log_MaxRadiusKpc |
| distance_radius_quality | 45 | 0.0481963 | 0.0934533 | [-0.0962454, 0.121662] | log_DistanceMpc;log_MaxRadiusKpc;NPoints;MeanErrVobsKms |
| observability_core | 45 | 0.0703847 | 0.0264868 | [-0.125206, 0.14764] | log_DistanceMpc;log_MaxRadiusKpc;NPoints;MeanErrVobsKms;InclinationDeg;InclinationErrorDeg;HubbleType |
| mass_subset | 21 | 0.0417431 | 0.188906 | [-0.350949, 0.330942] | log_DistanceMpc;log_MaxRadiusKpc;NPoints;MeanErrVobsKms;InclinationDeg;InclinationErrorDeg;HubbleType;HecateStellarMassLog |

Interpretation: the class coefficient is positive in simpler robust specifications, but it weakens once distance, radial coverage, sampling quality, inclination, and Hubble-type covariates are included together. This is exactly why the paper should keep distance/radius/observability as the main limitation and should not describe the result as an observability-proof physical detection. The HECATE mass-subset regression is reported only as supportive stress information because mass coverage is incomplete and the sample becomes small.
