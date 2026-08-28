# Strategic Evaluation: Software Resilience Stack (v0.2.0 / Phase 2 Transition)

**Date**: August 2026
**Target Audience**: Executive Stakeholders, Technical Architects, Security & AI Governance Engineers, Open-Source Maintainers
**Author**: Engineering & AI Resilience Taskforce

---

## Executive Summary

The **Software Resilience Stack** is an **evidence orchestration, verification, and decision engine** designed specifically to govern AI-generated and AI-modified software patches. Rather than generating code or running basic unit tests, the Stack operates above the software development lifecycle (SDLC) as an immutable, fail-closed evaluation layer. It aggregates multi-dimensional evidence (provenance, static properties, runtime observations, dependency integrity, and build reproducibility) into a **non-compensatory Reliability Vector** and outputs deterministic policy decisions: `AUTO_MERGE`, `REVIEW`, or `REJECT`.

This strategic evaluation assesses **what** has been built, **how** it should be deployed, **why** its architectural approach is necessary, **where** it creates the most leverage, and **whether** further engineering investment and commercial development are justified.

---

## 1. What We Have: Current Technical State & Artifact Inventory

The codebase currently stands at version **v0.2.0** with a fully verified Proof-of-Concept (PoC) pipeline and controlled fixture test suite.

### 1.1 Architecture & Core Components

1. **Artifact Contracts & JSON Schemas (`schemas/`)**:
   - Draft 2020-12 JSON Schemas for 5 heterogeneous input contracts: Evidence Manifests, Test Evidence, Dependency Reports, Software Provenance, and Verification State Attestations (VSA).
2. **Fail-Closed Evidence Collector & Validator (`src/resilience_poc/collector.py`, `validator.py`)**:
   - Implements the core principle: *"Absence of evidence is NOT evidence of success."*
   - Unexecuted or missing checks automatically default to `UNKNOWN` or `REVIEW`, blocking `AUTO_MERGE`. Corrupted signatures or schema violations force immediate `FAIL` and `REJECT`.
3. **Non-Compensatory Reliability Vector Engine (`src/resilience_poc/validator.py`)**:
   - Evaluates 8 distinct dimensions: `functional`, `semantic`, `dependency`, `runtime`, `concurrency`, `security`, `observability`, and `reproducibility`.
   - Enforces non-compensatory decision rules: high test coverage or security scores **cannot offset** a concurrency failure or build non-reproducibility.
4. **Cryptographic Attestations & In-Toto DSSE (`src/resilience_poc/dsse.py`, `vsa.py`)**:
   - Ed25519 and DSSE P-256 envelope signing for in-toto Verification Summary Attestations (VSA), establishing an auditable supply chain chain-of-custody.
5. **Real-GIL C-Extension Experiment Harness (`experiments/real_gil/`)**:
   - Controlled environment-gated harness testing CPython free-threaded (`3.13t/3.14t`) GIL reactivation causality with C-extension fixtures (`compatible_ext` and `incompatible_ext`).

### 1.2 Verification & Test Results (Local Execution Summary)

- **Unit & Integration Tests**: 26/26 tests passing (`pytest`).
- **Policy Invariant Mutation Checks**: 3/3 policy mutants killed (`tools/mutation_check.py`), proving the decision engine resists policy corruption (`unknown_to_pass`, `fail_condition_removed`, `risk_gate_removed`).
- **Controlled Benchmark Fixtures (A–E)**: 100% decision determinism and expected outcome alignment:
  - **A1/A2**: Normal passing patch -> `AUTO_MERGE` (or `REVIEW` based on risk tier).
  - **B**: Dependency vulnerability injected -> `REJECT`.
  - **C**: Semantic invariant failure -> `REJECT`.
  - **D1/D2**: Verified reproducible vs. non-reproducible build -> `AUTO_MERGE` vs `REJECT`.
  - **E**: GIL reactivation / concurrency failure -> `REJECT`.

---

## 2. How We Should Use It: Deployment & System Integration

The Software Resilience Stack is designed to operate as a **gatekeeper layer** inserted between AI code generation tools and production codebases.

```
┌────────────────────────┐      ┌───────────────────────────┐      ┌─────────────────────────────┐
│ AI Code Generator /    │      │  Continuous Integration   │      │ Software Resilience Stack   │
│ Coding Agent           │ ───> │  Runner & Test Harness    │ ───> │  (Gateway Engine)           │
│ (Patch + Diff)         │      │  (Artifact Generation)    │      │                             │
└────────────────────────┘      └───────────────────────────┘      └──────────────┬──────────────┘
                                                                                  │
                                                                       ┌──────────┴──────────┐
                                                                       ▼                     ▼
                                                                [AUTO_MERGE]        [REVIEW / REJECT]
                                                                (GitHub Bot)        (Human Oversight)
```

### 2.1 Recommended Workflow Architecture

1. **Pull Request Trigger**: An AI agent submits a PR with a patch diff and an initial provenance record.
2. **Collector Execution**: CI runners execute test suites, static scanners, dependency analyzers, and build verifiers, emitting standard JSON evidence payloads.
3. **Vector Evaluation**: The Stack ingests the evidence manifest, validates all schemas, checks cryptographic signatures, evaluates risk tiers, and builds the non-compensatory Reliability Vector.
4. **Policy Enforcement**:
   - **`AUTO_MERGE`**: All critical dimensions `PASS`, build is `VERIFIED_REPRODUCIBLE`, risk tier is acceptable. The PR is merged automatically.
   - **`REVIEW`**: Missing optional evidence (`UNKNOWN`), elevated risk tier, or warning states. Flagged for human review with an explicit audit summary.
   - **`REJECT`**: Hard failure in functional, security, concurrency, or reproducibility dimensions. PR is blocked and feedback is routed back to the AI agent.

---

## 3. Why: Core Engineering Principles & Value Proposition

### 3.1 The Fail-Closed Evidence Principle
Standard CI tools often treat unexecuted tests or missing scanner reports as implicit passes. In an era where AI agents can generate thousands of PRs automatically, **false assurance** is a catastrophic failure mode. The Stack's fail-closed design guarantees that every decision is backed by executed, verifiable evidence.

### 3.2 Non-Compensatory Evaluation vs. Aggregate Scores
Scalar scores (e.g., "88/100 code quality") are dangerously misleading because high coverage in unit tests can obscure a fatal race condition or dynamic vulnerability. The Stack's non-compensatory model ensures that safety invariants are absolute—a failure in any critical dimension rejects the candidate regardless of performance in other areas.

### 3.3 Attestable Supply Chain Trust
By wrapping decisions in DSSE envelopes and generating in-toto VSAs, the Stack creates an immutable audit trail binding prompt intent, code diff, runtime verification, and policy outcome together.

---

## 4. Where: Target Applications & High-Value Scenarios

1. **Automated AI PR Gateways (Resilience Gateway)**: GitHub/GitLab webhooks managing high-velocity AI agent pull requests in enterprise repositories.
2. **High-Assurance Infrastructure & Native Code**: Financial, aerospace, medical, or low-level systems (e.g., C-extensions, free-threaded CPython) where concurrency and memory safety errors carry massive risks.
3. **Regulatory & Compliance Frameworks**: Compliance with emerging AI safety legislation (EU AI Act, NIST AI RMF, SLSA Level 3+) requiring auditable chains of provenance and deterministic policy enforcement for AI-modified software.

---

## 5. Does It Worth Pursuing and Building? Strategic Decision & ROI Analysis

### 5.1 Final Verdict: **YES — STRONGLY WORTH PURSUING**

The Software Resilience Stack solves a critical bottleneck in AI-assisted software engineering: **trust and scale**. As LLM agents lower the cost of code generation to near zero, the bottleneck shifts entirely to **verification, review, and governance**. Without an automated, fail-closed decision layer, organizations face "PR fatigue" and heightened security risk.

### 5.2 ROI & Strategic Value Drivers
- **Developer Velocity**: Automates safe merging of low-risk, verified AI PRs (`AUTO_MERGE`), freeing engineers to focus on complex architecture.
- **Risk Mitigation**: Prevents silent regression, dependency injection attacks, and concurrency bugs from entering main branches.
- **Auditability**: Provides zero-trust cryptographic attestations for enterprise compliance.

### 5.3 Open Gaps & Phase 2 Roadmap
To move from v0.2.0 PoC to a production enterprise product, the following milestones must be executed:
1. **Real GIL Environment Validation**: Execute free-threaded CPython `3.13t/3.14t` runs on real hardware/CI runners.
2. **Production SLSA / KMS Key Management**: Move from local Ed25519 PoC keys to cloud KMS / Sigstore trust roots.
3. **Multi-Repo Empirical Evaluation**: Test the gateway across 20–50 open-source and enterprise repositories to calibrate false positive/negative rates.
4. **Policy Threshold Calibration**: Refine risk-tier policies against empirical post-merge fault data.

---

## Conclusion
The **Software Resilience Stack** is a high-value, highly timely innovation. Its architectural foundation is sound, verified, and policy-resilient. Proceeding with Phase 2 implementation will position the product as an essential security and governance engine for the AI software supply chain.
