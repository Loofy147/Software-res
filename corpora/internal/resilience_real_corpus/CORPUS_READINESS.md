# Real Corpus Readiness v1

## Current corpus
- 11 real repositories / commit records
- source_kind: `real_patch`
- evaluation_status: `metadata_only`
- ground_truth_status: `unknown`

## What is established by intake
- Repository identity is recorded.
- Commit SHA and commit URL are recorded.
- Commit message and timestamp are recorded.
- Duplicate record IDs and malformed SHAs are rejected.
- No correctness label is fabricated at intake.

## What is NOT established yet
- Functional correctness of the selected patches.
- Semantic-defect labels.
- Dependency drift for each repository.
- Reproducibility result for each build.
- Runtime/concurrency compatibility.
- Security verdicts.
- AI-generation provenance for the historical patches.

## Evaluation conversion protocol
For each intake record:
1. materialize the exact commit and parent;
2. capture the real diff and source revision;
3. build in a clean environment;
4. collect dependency/SBOM evidence;
5. run the repository's native verification suite;
6. generate Evidence Manifest + provenance;
7. run the Reliability Vector;
8. assign ground-truth labels only from observed evidence, maintainer/CI evidence, or controlled mutation experiments.

## Sampling rule
Do not mix historical real patches, synthetic mutations, and AI-generated patches in a single accuracy denominator. Report each source class separately and report an overall aggregate only when denominators and labels are comparable.
