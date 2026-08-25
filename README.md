# Software Resilience Stack — v0.2.0

Evidence Collector/Validator MVP for AI-generated or AI-modified software. It validates explicit evidence, produces a non-compensatory Reliability Vector, and returns `AUTO_MERGE`, `REVIEW`, or `REJECT` without fabricating positive evidence.

## Install and run

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -e '.[test]'
pytest -q
python3 tools/mutation_check.py
python3 -m resilience_poc.cli run-experiments
```

The expected controlled-fixture result is six matching decisions (A–E) and 3/3 policy mutants killed. The real free-threaded CPython experiment is environment-gated and returns a non-zero status when the required free-threaded CPython runtime is unavailable.

## v0.2 boundary

Included:
- Evidence contracts and JSON Schema validation
- Fail-closed Evidence Collector / Validator with risk-tier propagation
- Non-compensatory Reliability Vector and deterministic policy engine
- Local Ed25519 and DSSE P-256 PoC signing / verification
- Controlled experiment fixtures A–E (AUTO_MERGE, REVIEW, REJECT)
- Real-GIL experiment harness with environment gating
- Centralized package versioning (`0.2.0`) and policy invariant/mutation checks

Not included:
- Production SLSA builder trust / production key management
- Real external-corpus execution / independent ground truth labels
- Calibrated thresholds or proof of general software reliability
