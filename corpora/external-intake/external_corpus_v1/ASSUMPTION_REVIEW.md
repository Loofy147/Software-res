# External Corpus v1 — Assumption Review

| Assumption / claim | Status |
|---|---|
| Public repository can be used as independent evaluation input | ESTABLISHED, subject to repository license and service terms |
| Repository identity is independent of user's repositories | EXPERIMENTALLY_SUPPORTED by repository ownership metadata |
| HEAD is an immutable evaluation target | CONTRADICTED; HEAD must be resolved and pinned |
| Public repository test suite is ground truth | UNKNOWN / HYPOTHESIS |
| CI pass/fail is sufficient ground truth for semantic correctness | UNKNOWN / HYPOTHESIS |
| License metadata is static | CONTRADICTED; verify at ingest |
| Cross-ecosystem results are directly comparable | OPEN |
| Existing maintainers' tests detect all semantic defects | UNKNOWN |
| Reliability Vector can be calibrated from this corpus | OPEN until sufficient labeled observations exist |

## Required next step

For every repository: resolve immutable commit SHA -> materialize clean checkout -> record license -> detect build/test system -> run validation -> collect independent reference evidence -> only then create evaluation labels.
