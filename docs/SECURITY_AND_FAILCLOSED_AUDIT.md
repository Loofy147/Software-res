# Security and Fail-Closed Audit v2

## Closed vulnerabilities / false-assurance paths

### 1. Missing verification fallback — CLOSED
Previously, missing Test Evidence / Dependency Evidence could be replaced by synthetic passing evidence. This created a direct false-assurance path.

Current behavior: missing required verification evidence returns REVIEW.

### 2. Runtime PASS without runtime evidence — CLOSED
The validator previously emitted runtime=pass by construction. Runtime is now UNKNOWN unless explicit runtime evidence is present.

### 3. Observability PASS without observability evidence — CLOSED
Observability is now UNKNOWN until explicit evidence exists.

### 4. Security checks without execution proof — CLOSED
Supply-chain security status now requires `executed=true` plus successful checks.

### 5. High-risk auto-merge — CLOSED
Only low-risk changes can auto-merge under the current policy. Medium/high remain REVIEW.

### 6. Runtime state invented at collection time — CLOSED
The collector no longer claims CPython/GIL observations before a runtime check has executed.

## Remaining trust gaps
- PoC signing keys are not production trust roots.
- DSSE verification must be bound to an independently managed key/trust identity.
- SLSA provenance must come from the real builder rather than a locally synthesized object.
- Dependency reconciliation still needs language-specific resolution semantics.
- Semantic correctness remains dependent on the quality and coverage of invariants/tests.

## Rule
Any evidence absent, unverifiable, stale, or contradictory must reduce confidence or force REVIEW/REJECT according to policy. The validator must never manufacture positive evidence.
