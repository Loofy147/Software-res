# Software Resilience Stack — Assumption Review and Open Questions

## Core Assumptions (Assumptions A–F)

### Assumption A — Evidence Integrity (Truthfulness)
- **Statement**: Submitted evidence manifests, test logs, and provenance attestations accurately reflect actual executions and have not been altered or fabricated.
- **Risk**: Malicious or broken telemetry could submit passing results for unsafe code.
- **Mitigation**: Cryptographic signing (Ed25519/DSSE) by trusted build/verification infrastructure and independent verifiers.

### Assumption B — Test Completeness & Coverage
- **Statement**: Test suites and property checks are sufficiently complete to detect functional and behavioral regressions.
- **Risk**: `passing tests != functional correctness`. Weak test suites yield false confidence (`False Positives` for safety).
- **Mitigation**: Combine functional unit tests with property-based testing, SAST, dynamic analysis, and mutation testing metrics.

### Assumption C — Correctness of Invariant Specifications
- **Statement**: The invariant validators and policy rules are correctly defined.
- **Risk**: Garbage invariants lead to highly deterministic, completely wrong governance decisions.
- **Mitigation**: Formal schema validation, peer review of policy contracts, and continuous verification of policy engine rules against ground-truth failure datasets.

### Assumption D — Runtime Observation Causality
- **Statement**: Observed runtime state transitions (e.g., CPython GIL reactivation) are causally attributable to specific imported modules or patches.
- **Risk**: Confounding environmental factors or indirect background threads could trigger state transitions, causing false attribution.
- **Mitigation**: Strict temporal sequence ordering (pre-flight snapshot, import event under control, post-flight snapshot) and baseline controls (Phase A experiment protocol).

### Assumption E — Completeness of Dependency Reconciliation
- **Statement**: Reconciling declared vs runtime dependencies accurately captures the true dependency footprint.
- **Risk**: Dynamic imports, plugin architectures, subprocess calls, or native binary bindings might not appear in standard import hooks, causing false dependency drift signals or undetected shadow dependencies.
- **Mitigation**: Multi-layer dependency verification combining static SBOMs, import hooks, and runtime binary tracking.

### Assumption F — Measurability of Reproducibility
- **Statement**: Software build determinism can be reliably verified by re-executing builds in isolated environments.
- **Risk**: Non-deterministic factors (timestamps, external network calls, compiler ordering, hardware variances) can break build identity without altering functional behavior.
- **Mitigation**: Scope-bounded reproducibility checks (`REPRODUCIBLE` vs `VERIFIED_REPRODUCIBLE`) and pinned toolchain environments.

---

## Open Empirical Questions (RQ1–RQ7)

1. **RQ1 (Evidence Completeness)**: What minimum set of evidence artifacts is required to reach high-confidence governance decisions?
2. **RQ2 (Failure Detection)**: How effective is the Reliability Vector at detecting subtle multi-dimensional failure classes (A–E) compared to conventional single-score CI?
3. **RQ3 (Causal Attribution)**: Does the Phase A experiment harness reliably attribute C-extension GIL reactivation to the treatment extension with zero false attribution?
4. **RQ4 (Decision Determinism)**: Is the decision engine 100% deterministic under replay of identical evidence graphs?
5. **RQ5 (Reproducibility)**: What fraction of AI-generated code modifications satisfy strict reproducible build criteria?
6. **RQ6 (Generalization)**: How do policy rules perform across diverse external open-source repositories (20–50 projects)?
7. **RQ7 (FP/FN & Sensitivity)**: What are the empirical false positive and false negative rates when evaluated against mutation-generated patch corpora?
