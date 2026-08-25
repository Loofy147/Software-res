# Execution State v2 (v0.2.0)

## Current result
- Local test suite: 26/26 PASS.
- Policy mutants killed: 3/3 (`tools/mutation_check.py`).
- Controlled A–D + fixture E: supported in the controlled fixture domain (A–E expected decisions matched).
- Fail-closed verification gating: strengthened.
- Runtime/observability/security evidence: fail-closed semantics enforced; missing evidence defaults to UNKNOWN / REVIEW / REJECT.
- High-risk policy: REVIEW / REJECT, never AUTO_MERGE.
- Risk-tier propagation: explicit in Evidence Manifest, Reliability Vector, and Policy Engine.
- CI Workflow: automated GitHub Actions testing on Python 3.12 and 3.13 (`.github/workflows/ci.yml`).

## External execution path
The current container has no outbound checkout/build access. The external repository `Loofy147/Software-res` serves as the external source of truth for CI execution. GitHub Actions supports free-threaded CPython via `actions/setup-python@v5` and `3.13t`/`3.14t`. The external evaluation workflow emits immutable commit SHAs, build/test results, dependency evidence, runtime evidence, and raw artifacts.

## No false claims
External repository evaluation is pending workflow execution on GitHub runners. No accuracy, FP/FN, or generalization claim is made from repository metadata alone.
