# SPARC v0.5 Null-Model Stress Tests

These checks protect the fixed primary endpoint; they are not alternate endpoints.

| check | n A | n C | diff | p | CI low | CI high | detail |
| --- | --- | --- | --- | --- | --- | --- | --- |
| primary_permutation_bootstrap | 17 | 28 | 0.08427 | 0.0009999 | 0.04481 | 0.1599 | count-preserving permutation/bootstrap on fixed quality-pass A/C labels |
| A_C_leave_one_out | 17 | 28 | 0.08427 |  |  |  | sign_flips=0; max_abs_change=0.00478942; largest_influence=ESO079-G014 |
