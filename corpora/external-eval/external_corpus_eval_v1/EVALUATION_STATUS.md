# External Public Corpus v1 — Evaluation Status

## Intake
10 independent public repositories are registered.

## What is established
- Repository identity and public visibility were verified through GitHub repository metadata.
- Default branches were recorded.
- Corpus is separated from the user's internal repositories and synthetic fixtures.
- Ground truth remains UNKNOWN.

## What is not established yet
- Clean checkout/build success.
- Test pass/fail under our validator.
- Dependency reconciliation.
- Reproducibility.
- Security findings.
- Semantic-defect labels.
- Reliability Vector performance.

## Execution constraint
The current execution container cannot resolve external GitHub network hosts. Therefore repository checkout/build was not performed here and no execution result is claimed.

## Next execution unit
For each repository:
1. Resolve an immutable commit SHA.
2. Checkout cleanly.
3. Detect build/test/package ecosystem.
4. Run repository-native tests.
5. Generate dependency/SBOM/provenance evidence.
6. Run the Software Resilience Validator.
7. Store results separately from observed repository-native evidence.
8. Assign ground-truth status only when supported by independent evidence.
