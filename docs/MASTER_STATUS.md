# Software Resilience Stack v1.0 — Consolidated Master Status

## Scope
This package consolidates the implementation work completed for the Software Resilience Stack PoC through Phase B, corpus intake, external public corpus preparation, and assumption review.

## Evidence status
- Artifact contracts: EXPERIMENTALLY_SUPPORTED in the PoC fixtures.
- Evidence Collector / Validator: EXPERIMENTALLY_SUPPORTED on the controlled fixture suite; fail-closed evidence gating strengthened in Audit v2.
- Reliability Vector and deterministic decision engine: EXPERIMENTALLY_SUPPORTED on controlled cases.
- A–D injected failures: EXPERIMENTALLY_SUPPORTED on controlled fixtures.
- VSA + DSSE integration: EXPERIMENTALLY_SUPPORTED in the local MVP harness.
- Real GIL causality on free-threaded CPython + actual native extension: OPEN.
- Production SLSA builder provenance: OPEN.
- Independent production trust-root / verifier deployment: OPEN.
- External public-repository build/test evaluation: READY FOR EXTERNAL RUNNER; not executed in the current container because outbound checkout/build access is unavailable.
- Production thresholds: HYPOTHESES / NOT CALIBRATED.
- Generalization: OPEN.

## Important interpretation rule
Controlled fixture results are not external validation. A perfect fixture result demonstrates that the pipeline detects the injected conditions represented by the fixtures; it does not establish general reliability across arbitrary software.

## Reproducibility metric separation
Keep these separate:
- Reproduction Success: successful reproducible builds / eligible reproducibility attempts.
- Non-Reproducibility Detection Rate: correctly detected non-reproducible builds / injected non-reproducible builds.

## Real-GIL experiment
The repository contains a control/treatment harness designed for CPython free-threaded builds. The experiment is intentionally fail-closed when the runtime is not genuinely free-threaded. No real-runtime causal success is claimed in this package.

## Corpus separation
Three evidence populations must remain distinct:
1. Internal/user-owned corpus.
2. Controlled synthetic/injected benchmark.
3. External public-repository corpus.

Do not combine their accuracy metrics into a single headline number.
