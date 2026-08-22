# Assumption Review and Open Questions

## Experimentally supported (limited to tested scope)
- Five-artifact contract structure works in the PoC.
- Evidence manifests can be collected and validated for the fixture cases.
- Multi-dimensional decision rules are deterministic for the tested cases.
- Controlled A–D injected failure cases are detected as designed.
- VSA/DSSE local integration verifies the project-produced attestation structure.

## Hypotheses / not established
- Any proposed production threshold such as AI rework <15% or OOTB run rate >=75%.
- A single semantic-defect-rate target that generalizes across projects.
- That agent confidence scores are calibrated predictors of actual code reliability.
- That the current failure taxonomy covers most real-world AI-generated software failures.

## Open empirical questions
- Does an actual incompatible CPython native extension produce the expected causal GIL transition under the selected free-threaded runtime?
- Can the SLSA provenance produced by an external CI builder be consumed and verified end-to-end by the stack?
- How often do real projects exhibit declared-vs-actual dependency drift?
- How stable are the decision rules across languages, build systems, and repository sizes?
- What is the false-negative rate on real defects when an independent reference label exists?
- Which dimensions are actually predictive of post-merge defects?
