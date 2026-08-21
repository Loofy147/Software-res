# Software Resilience Stack — Assumption Review v1

Status labels: ESTABLISHED, EXPERIMENTALLY_SUPPORTED, USER_REPORTED, INFERENCE, HYPOTHESIS, OPEN.

| Assumption / Claim | Status | Evidence / Required next test |
|---|---|---|
| Five artifact contracts are syntactically and operationally usable | EXPERIMENTALLY_SUPPORTED | Local PoC tests; revalidate against real CI artifacts |
| Reliability Vector is preferable to a single aggregate score for critical gates | INFERENCE / DESIGN CHOICE | Stress-test policy under conflicting dimensions |
| Decision engine is deterministic | EXPERIMENTALLY_SUPPORTED | Existing fixture suite; repeat with real corpus |
| Fixture failures A–D are detected | EXPERIMENTALLY_SUPPORTED | Existing injected-failure experiments |
| Real GIL reactivation can be detected causally using before/import/after events | HYPOTHESIS | Execute Phase A on real free-threaded CPython + native extension |
| `sys._is_gil_enabled()` is sufficient as an observation of process GIL state | ESTABLISHED for CPython | Must still record implementation/version/build context |
| Missing free-threading declaration can trigger GIL re-enablement on extension import | ESTABLISHED CPython behavior | Validate with actual fixture on free-threaded runner |
| VSA predicate/schema integration is valid | EXPERIMENTALLY_SUPPORTED | DSSE/VSA tests; validate with independent verifier |
| Custom Ed25519/ECDSA PoC signing is production-grade attestation | OPEN / REJECTED CLAIM | Replace with managed trust root and independent verification |
| SLSA provenance is actually produced by the build system | OPEN | Real builder integration required |
| Reproducibility can be judged from normalized artifact identity | DESIGN HYPOTHESIS | Define normalization semantics per artifact type |
| Verified reproducibility requires independent rebuild/provenance checks | DESIGN / STANDARDS-ALIGNED | Implement independent builder verification |
| Declared-vs-runtime dependency reconciliation detects meaningful drift | EXPERIMENTALLY_SUPPORTED only on fixtures | Test package managers, optional deps, dynamic imports, plugins |
| 0 unexpected GIL reactivations / <15% rework / etc. are production thresholds | HYPOTHESIS | Calibrate from real corpus; do not enforce yet |
| Small corpus metrics generalize to production | OPEN | Expand to 10–20 repos and multiple agents/failure classes |
| AI confidence score is useful evidence of code reliability | HYPOTHESIS | Correlate confidence with downstream defects; do not trust by default |
| Semantic defect density per KLOC is stable enough for policy | OPEN | Compare across languages, modules, and test strategies |
| Evidence completeness implies evidence validity | REJECTED | Separate presence from cryptographic/reference validation |

## Review gates before production policy

1. Real free-threaded CPython experiment succeeds with independent control/treatment runs.
2. SLSA provenance is emitted by the actual builder, not reconstructed by the collector.
3. VSA is independently verifiable from a trust root.
4. Corpus contains real repositories/patches and reports source provenance.
5. Thresholds are calibrated from distributions, with confidence intervals and drift monitoring.
6. Policy engine is tested against adversarial combinations of dimensions.
7. Reproducibility semantics are defined per artifact class.
8. Dependency reconciliation covers dynamic/runtime-loaded dependencies.
