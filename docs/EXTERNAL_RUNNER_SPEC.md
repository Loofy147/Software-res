# External Runner Specification v1

## Purpose
Execute the external public corpus on a network-enabled CI runner because the local analysis container cannot perform outbound Git checkout/build.

## Per-repository sequence
1. Resolve default-branch HEAD to an immutable commit SHA and record it.
2. Checkout the exact SHA.
3. Capture license and manifest metadata.
4. Detect build system and test command without inventing commands.
5. Create a hermetic-ish job environment and record runtime/tool versions.
6. Run native tests/build where a repository-provided command is identifiable.
7. Capture lockfiles, dependency metadata, SBOM/provenance where available.
8. Emit raw logs and normalized evidence.
9. Only assign ground-truth labels when an independent reference exists.
10. Feed evidence into the Software Resilience validator and emit a Reliability Vector.

## Safety rule
A project that cannot be built or tested is not automatically REJECT. It is `UNKNOWN/BLOCKED` with an explicit reason unless policy says otherwise.

## Statistics rule
Detection/FP/FN rates require labeled cases. Metadata-only or unlabeled repository runs must not enter those denominators.
