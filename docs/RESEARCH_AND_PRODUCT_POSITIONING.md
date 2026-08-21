# Software Resilience Stack v1.0 — Research & Product Positioning

## 1. System Definition
The **Software Resilience Stack** is an **Evidence + Verification + Decision layer** operating above the lifecycle of AI-generated or AI-modified code.

It is **not**:
- An LLM coding agent
- A unit testing framework
- An SBOM scanner
- A CI/CD runner

It **is**:
An evidence orchestration engine that converts heterogeneous artifacts (provenance, static properties, runtime events, dependency observations, reproducibility checks) into a non-compensatory **Reliability Vector** and enforces auditable policy decisions (`MERGE`, `HUMAN_REVIEW`, `REJECT`).

---

## 2. Fundamental Architectural Rule: Fail-Closed Evidence

> **"Absence of Evidence is NOT Evidence of Success."**

The greatest failure mode in software verification is not merely missing a bug, but treating **missing evidence** as implicit proof of safety (**false assurance**).

The Software Resilience Stack enforces a strict, fail-closed state transition model:

```text
       No Evidence / Unexecuted Check
                   │
                   ▼
           UNKNOWN / REVIEW
                   │
    ┌──────────────┴──────────────┐
    ▼                             ▼
Invalid / Failed Evidence    Verified Execution & Proof
    │                             │
    ▼                             ▼
FAIL / REJECT               PASS Candidate
```

### Policy Rules for Evidence Verification:
- **No Evidence**: Any dimension lacking explicit, executed verification defaults to `UNKNOWN` or `REVIEW`, blocking `AUTO_MERGE`.
- **Invalid / Corrupted Evidence**: Schema validation failure or broken signature triggers an immediate `FAIL` and `REJECT`.
- **Verified Evidence**: A dimension transitions to `PASS` only when explicit proof of successful execution (`executed = true`) and zero violations are validated.

---

## 3. Claim Matrix & Verification Boundaries

| Claim / Component | Status | Evidence Boundary |
| :--- | :--- | :--- |
| **Architecture Feasibility** | **SUPPORTED** | Executed PoC pipeline with 5 artifact contracts & collector/validator. |
| **Fail-Closed Evidence Model** | **SUPPORTED** | Absence of evidence defaults to `UNKNOWN`/`REVIEW`, blocking false assurance. |
| **Artifact Contracts & Schemas** | **SUPPORTED** | Draft 2020-12 JSON Schema validation on all PoC inputs. |
| **Multi-Dimensional Decision Engine** | **SUPPORTED** | Deterministic vector evaluation across controlled fixtures. |
| **Controlled Injected Failure Detection (A–D)** | **SUPPORTED** | 100% detection rate on bundled synthetic corpus. |
| **Local VSA / DSSE Integration** | **SUPPORTED** | Local in-toto VSA generation and Ed25519 signature validation. |
| **Real C-Extension GIL Causality** | **OPEN** | Controlled harness exists (`experiments/real_gil/`); pending CPython `3.13t/3.14t` execution. |
| **Production SLSA Provenance** | **OPEN** | Currently uses local builder fixture; requires third-party CI builder integration. |
| **Production VSA / Trust Root** | **OPEN** | Key management & DSSE envelope require external PKI / KMS trust root. |
| **Large-Scale Corpus Validation** | **OPEN** | Pending multi-repository empirical trial (20–50 external repos). |
| **Realistic False Positive / Negative Rates** | **OPEN** | Unknown outside synthetic/controlled fixture sets. |
| **Threshold Calibration** | **UNKNOWN** | Risk thresholds & confidence metrics are uncalibrated hypotheses. |
| **General Software Reliability Claim** | **NOT ESTABLISHED** | Synthetic fixture success does not imply general software reliability. |

---

## 4. Problem Definition
Existing software engineering workflows produce disconnected outputs:
- LLM Patch Generators
- Unit / Property Tests
- SAST / DAST Scanners
- Dependency Integrity Scanners (SBOM / SLSA)
- Reproducible Build Verifiers
- Runtime Observability Monitors

**The Gap**: How to transform an AI-generated code change into a **deterministically auditable engineering decision** based on multi-level evidence, runtime state, dependency integrity, and explicit policy constraints.

---

## 5. Core Innovations

### A. Evidence Orchestration + Policy Composition
Instead of creating duplicate standards, the Stack orchestrates existing standards (in-toto, SLSA, VSA, CycloneDX/SPDX) into a single decision substrate.

### B. Non-Compensatory Reliability Vector
Reliability is represented as a structured vector rather than a scalar score (e.g., 87/100):
```json
{
  "functional": "PASS",
  "semantic": "PASS",
  "dependency": "WARN",
  "runtime": "PASS",
  "concurrency": "FAIL",
  "security": "PASS",
  "observability": "PASS",
  "reproducibility": "VERIFIED"
}
```
**Policy Principle**: Safety constraints are non-compensatory. High scores in Security, Functional Tests, and Observability **cannot offset a Concurrency failure**.

### C. AI-Aware Software Provenance Chain
Extends traditional source provenance backward to the AI generation boundary:
`Prompt Snapshot -> Agent ID / Model Version -> Generation Policy -> Patch Diff -> Verification Evidence -> Build Provenance -> Runtime Snapshot -> Auditable Decision`

### D. Scope-Bounded Reproducibility
Distinguishes between `REPRODUCIBLE` (artifact reconstructed from declared inputs) and `VERIFIED_REPRODUCIBLE` (independent rebuild verification in isolated environments).

---

## 6. Core Assumptions (Assumptions A–F)

- **Assumption A (Evidence Integrity & Non-Vacuity)**: Submitted evidence is truthful and explicitly verified. Absence of evidence triggers fail-closed rules rather than assumed success.
- **Assumption B (Test Completeness)**: Passing tests reflect functional correctness (bounded by test suite quality).
- **Assumption C (Invariant Correctness)**: Policy validators rely on correctly specified invariants (garbage invariants produce reliable wrong decisions).
- **Assumption D (Runtime Causality)**: State transitions (e.g., GIL reactivation) are causally attributed to specific imports via temporal ordering and controls.
- **Assumption E (Dependency Completeness)**: Declared dependencies account for dynamic imports, plugins, and native libraries without false drift flags.
- **Assumption F (Measurable Reproducibility)**: Determinism is evaluated within defined environment bounds (excluding non-deterministic network/hardware noise).

---

## 7. Research Questions (RQ1–RQ7)

- **RQ1 (Evidence Completeness)**: What minimum set of heterogeneous artifacts is necessary to decide patch safety?
- **RQ2 (Failure Detection Sensitivity)**: How effectively does the vector detect subtle semantic, dependency, and concurrency faults?
- **RQ3 (Causal Attribution)**: Can runtime policy violations be attributed to specific native imports with zero false attribution?
- **RQ4 (Decision Determinism)**: Does the policy engine produce 100% deterministic outputs for identical evidence inputs?
- **RQ5 (Reproducibility Verification)**: How frequently do AI-generated patches satisfy deterministic build guarantees?
- **RQ6 (Repository Generalization)**: How stable are decision rules across diverse external codebases and build systems?
- **RQ7 (FP / FN & Calibration)**: What are the empirical false positive and false negative rates when evaluated against mutation baselines?

---

## 8. Target Applications & Product Vision

### A. AI Coding Governance Gateway (Resilience Gateway)
A Webhook / PR Check layer integrated into GitHub/GitLab:
`PR Event -> Evidence Collector -> Validator Fleet -> Reliability Vector Engine -> Webhook Status (Merge / Review / Reject)`

### B. High-Assurance AI Software Supply Chain
Immutable attestation trail binding AI prompt intent, generated diff, test run, dependency reconciliation, and SLSA provenance into a VSA for downstream deployment.

---

## 9. Phase 2 Roadmap: Assumption Audit & External Validation v2

1. **Real GIL Execution**: Complete free-threaded CPython `3.13t/3.14t` experiment runs on GitHub Actions.
2. **Production SLSA / VSA / DSSE**: Transition from local PoC key/builder fixtures to standard DSSE envelope signing with external KMS keys.
3. **Controlled Mutation Corpus**: Implement systematically mutated patch sets to measure vector sensitivity and false positive/negative rates.
4. **External Public Corpus Trial**: Evaluate 20–50 real-world repositories with independent ground-truth labels on a network-enabled runner.
5. **Threshold & Risk Tier Calibration**: Calibrate policy risk tiers against empirical post-merge fault rates.
