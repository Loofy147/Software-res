# Gap Analysis v2 — Current vs Desired State

## Executive conclusion
The PoC architecture is implementation-capable and experimentally supported only on controlled cases. The largest remaining gaps are not core architecture gaps; they are evidence/trust gaps and external execution gaps.

## Current state
- Five artifact contracts: tested.
- Evidence collection/validation: tested on fixtures.
- Non-compensatory Reliability Vector policy: tested.
- VSA/DSSE structure: tested locally.
- Real free-threaded GIL causality: not yet executed on a genuine free-threaded runner.
- Production SLSA provenance: not yet verified end-to-end.
- External public repository execution: prepared, but current container has no outbound checkout/build access.
- Threshold calibration: not established.

## Highest-value gaps
1. Real runtime causality (GIL): requires external runner.
2. Real builder provenance: requires CI builder evidence and signature verification.
3. External corpus execution: requires outbound runner.
4. Independent reference labels for defect detection: required before FP/FN claims.
5. Trust-root deployment: project-generated keys are PoC-only and are not a production trust base.

## Security / fail-closed corrections applied
- Validator no longer fabricates passing Test Evidence or Dependency Evidence when absent.
- Missing verification evidence routes to REVIEW.
- Runtime and observability are no longer default PASS; they require evidence.
- Supply-chain checks require an explicit executed flag.
- High-risk changes cannot AUTO-MERGE.
- Source revision is captured explicitly in the Evidence Manifest.
- Runtime collector no longer claims observed CPython/GIL facts at collection time; those fields remain unknown until runtime evidence exists.
- Test and dependency schemas now require execution/result fields.

## Desired state
A held-out external evaluation pipeline in a network-enabled CI runner, pinned to immutable SHAs, producing provenance + verification evidence + Reliability Vector + DSSE/VSA, and using independent reference labels for any statistical accuracy claim.

## Non-goals
This project does not replace SLSA, in-toto, SBOM tooling, static analyzers, test frameworks, or CI systems. It composes their evidence into an auditable policy decision.
