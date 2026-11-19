# Source-header anomaly amendment

2026-11-17, before accepting any empirical estimator output. The strict parser found a source inconsistency: `pg_jun`'s comment labels 29 fault columns, while `PG_JUN_ERR` declares 27. Its companion `pg_nov` also declares 27. Source computation loops over columns 2 through `err+1`, taking the declared error count as the data boundary; each raw row has the fixed 35-column width and zero padding beyond that boundary.

For this unchanged source SHA256 only, permit the exact known `pg_jun` header-comment mismatch as an explicit anomaly. Use its declared 27 reference columns and preserve all remaining values as checked zero padding. Record the exception in normalized data and results. Every other header, width, binary-field and padding check remains strict. Do not silently generalize this exception to another source or infer dimensions from observed positives.

This corrects parsing of an old comment, not an estimator parameter, outcome definition or chosen matrix. If any purported padding value is nonzero, or a source hash/declaration differs, reject the exception and stop. The original protocol remains unchanged for audit.

Source: `sources/umd-total.cc`, SHA256 `696c9397d1213da986db451ab83c369e328e46d6d22afd9091c2ea066faffbcd`, `PG_JUN_ERR` declaration, `pg_jun` initializer/header, and `combine_teams` loop over `l=2; l<err+2; l++`.
