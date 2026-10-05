# Changelog

## 0.2.1 — Evidence Semantics
- Added explicit evidence states: UNOBSERVED, PASS, FAIL, INVALID, STALE, CONFLICT.
- Added deterministic evidence-state precedence and policy mapping.
- Extended Reliability Vector dimensions with evidence_state.
- Added regression tests for missing, invalid, stale, and conflicting evidence.
- Added controlled Decision Separation Benchmark v1.
- This release does not claim real-world accuracy or provenance trust.

## 0.2.0 — Engineering Hardening

### Included
- Centralized package version (0.2.0) across VERSION, pyproject.toml, src/resilience_poc/__init__.py, and src/resilience_poc/api.py
- Explicit risk_tier propagation in Evidence Manifest and Reliability Vector passed directly into policy engine
- Policy invariant test suite enforcing safety properties
- Automated policy mutation verification killing 3/3 target policy mutants
- GitHub Actions CI workflow for automated testing and policy verification
- Updated package Python requirement (>=3.12,<3.15)

### Explicitly deferred
- Real free-threaded CPython causal result (environment-gated)
- Production SLSA builder provenance and trust root
- Production key management
- External held-out corpus execution and independent labels
- Threshold calibration and production SLAs

## 0.1.0 — Frozen PoC Release
- Evidence artifact contracts and JSON Schema validation
- Fail-closed Evidence Collector/Validator
- Non-compensatory Reliability Vector and deterministic policy engine
- Local Ed25519 and DSSE P-256 PoC signing/verification
- Controlled experiments A–E
- Real-GIL experiment harness with environment gating
- Reproducibility and dependency evidence paths
- Pinned direct runtime dependencies
- Installable Python wheel
