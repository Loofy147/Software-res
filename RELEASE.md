# v0.2.0 — Engineering hardening

v0.2.0 preserves the frozen v0.1.0 architecture while hardening version consistency, risk-tier propagation, release hygiene, and policy regression resistance.

## One-sentence scope
A small evidence-validation PoC that converts explicit software evidence into a non-compensatory Reliability Vector and deterministic merge/review/reject decision.

## Verification
- 26 pytest tests passing.
- 3/3 targeted policy mutants killed (`tools/mutation_check.py`).
- Controlled A–E decisions match expected outcomes (`python -m resilience_poc.cli run-experiments`).
- Wheel builds and installs cleanly into a fresh virtual environment (`pip install -e '.[test]'`).
- Automated CI workflows added for GitHub Actions (`.github/workflows/ci.yml`).

## Not claimed
This release does not claim real free-threaded runtime causality, production SLSA trust, external-corpus effectiveness, calibrated thresholds, or general reliability improvement.
