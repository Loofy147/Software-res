# External Public Corpus v1

This corpus is an independent evaluation intake set of public GitHub repositories. It is intentionally separate from the user's repositories and from synthetic fixtures.

## Rules

1. Repository visibility does not imply a ground-truth label.
2. Every evaluation must resolve `HEAD` to an immutable commit SHA before execution.
3. `ground_truth_status=unknown` remains until independent evidence exists.
4. License metadata must be re-verified at ingest time; `to_verify_at_ingest` entries must not be redistributed as source-code bundles until verified.
5. Evaluation outputs are derived artifacts: manifests, provenance references, test reports, dependency reports, and Reliability Vectors.
6. Training/calibration data must not be mixed with the held-out evaluation set.

## Intended composition

- 6 Python-focused projects, including NumPy for native-code/runtime coverage.
- 4 JavaScript/TypeScript/Node.js projects.
- Mix of frameworks, libraries, testing/tooling, and build systems.

## Current status

`intake_only`: repository identity selected; exact revision still needs to be resolved and pinned at evaluation time.

No accuracy, false-positive, or false-negative claims may be derived from this intake file alone.
