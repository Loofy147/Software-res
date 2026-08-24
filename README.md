# Software Resilience Stack — v0.1.0

Evidence Collector/Validator MVP for AI-generated or AI-modified software. It validates explicit evidence, produces a non-compensatory Reliability Vector, and returns `AUTO_MERGE`, `REVIEW`, or `REJECT` without fabricating positive evidence.

## Install and run

```bash
python -m venv .venv && . .venv/bin/activate && python -m pip install -e '.[test]' && pytest -q && python -m resilience_poc.cli run-experiments
```

The expected controlled-fixture result is six matching decisions (A–E). The real free-threaded CPython experiment is environment-gated and returns a non-zero status when the required runtime is unavailable.

## v0.1 boundary

Included: evidence contracts, fail-closed validation, Reliability Vector decisions, local Ed25519/DSSE PoC signing, controlled A–E fixtures, and the Real-GIL harness.

Not included: production SLSA builder trust, production key management, real external-corpus execution, calibrated thresholds, or proof of general reliability.
