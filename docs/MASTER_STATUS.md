# Software Resilience Stack v1.0 — Consolidated Master Status

## Overview & Positioning Reference
For the complete research framing, product architecture, claim matrix, and Phase 2 roadmap, see [`RESEARCH_AND_PRODUCT_POSITIONING.md`](RESEARCH_AND_PRODUCT_POSITIONING.md).

## Scope
This repository provides the core implementation and proof-of-concept for the Software Resilience Stack v1.0, an evidence-driven verification and governance layer for AI-generated code.

## Claim Matrix Summary
- **Architecture & Contracts**: `SUPPORTED` (5 schemas, local evidence collector & multi-dimensional validator).
- **Fail-Closed Evidence Model**: `SUPPORTED` (Absence of evidence defaults to `UNKNOWN`/`REVIEW`, eliminating false assurance).
- **Decision Engine Determinism**: `SUPPORTED` (100% deterministic decision logic across controlled fixtures).
- **Controlled Injected Fault Detection (A–D)**: `SUPPORTED` (100% detection rate on controlled synthetic benchmarks).
- **VSA & DSSE Attestation Structure**: `SUPPORTED` (Local in-toto VSA generator & Ed25519 signature envelope).
- **Real GIL Causality on Free-Threaded CPython**: `OPEN` (Controlled harness ready in `experiments/real_gil/`; CI execution pending on `3.13t`/`3.14t`).
- **Production SLSA Builder Integration**: `OPEN` (Local builder fixture in place; production deployment requires external CI builder attestation).
- **External Repository Evaluation**: `OPEN` (External corpus runner ready; awaiting multi-repo execution on network runner).
- **False Positive / Negative Calibration**: `OPEN` (Synthetic benchmark FPR/FNR is 0.00; real-world rates to be established via mutation testing).
- **General Software Reliability Claim**: `NOT ESTABLISHED` (Controlled fixture success is architectural proof of concept, not a generalized statistical claim).

## Core Architectural Principles
1. **Evidence Orchestration over Standards Reinvention**: Integrates in-toto, SLSA, VSA, CycloneDX, and pytest without inventing redundant provenance specifications.
2. **Fail-Closed Evidence Model**: "Absence of Evidence is NOT Evidence of Success." Missing checks default to `UNKNOWN`/`REVIEW`; invalid checks fail closed to `REJECT`.
3. **Non-Compensatory Reliability Vector**: Safety-critical dimensions (concurrency, security, dependency integrity) act as non-compensatory hard constraints. Averaging scores is explicitly rejected.
4. **AI-Aware Provenance Chain**: Records prompt snapshot, agent identity, generation policy, and patch diff alongside standard build and test evidence.

## Assumptions & Open Empirical Questions
See [`ASSUMPTIONS_AND_OPEN_QUESTIONS.md`](ASSUMPTIONS_AND_OPEN_QUESTIONS.md) for detailed definitions of Assumptions A through F (Evidence Integrity, Test Completeness, Invariant Correctness, Runtime Causality, Dependency Completeness, Measurable Reproducibility).

## Next Phase: Assumption Audit & External Validation v2
1. Real GIL Execution on CPython 3.13t/3.14t CI.
2. Production SLSA & DSSE attestation pipeline integration.
3. Mutation-based benchmark evaluation to measure vector sensitivity (TP, TN, FP, FN).
4. Multi-repo empirical trial (20–50 open-source repositories).
5. Risk-tier and threshold calibration against empirical post-merge defect rates.
