# Evidence Semantics v0.2.1

## Purpose

v0.2.1 introduces an explicit epistemic state for evidence, separate from the policy status of a Reliability Vector dimension.

## States

- UNOBSERVED: required evidence is absent or insufficient to establish a result.
- PASS: required evidence was observed and supports the dimension.
- FAIL: observed evidence establishes a failure.
- INVALID: evidence cannot be trusted.
- STALE: evidence existed but is outside its declared validity window.
- CONFLICT: independently presented evidence disagrees.

## Precedence

INVALID > CONFLICT > STALE > FAIL > PASS > UNOBSERVED.

A PASS and FAIL pair is therefore CONFLICT rather than silently becoming FAIL.

## Policy mapping

- PASS preserves the dimension status.
- UNOBSERVED, STALE, and CONFLICT cannot create PASS; on critical dimensions they produce REVIEW unless an independent hard failure exists.
- INVALID is treated as a hard trust failure and produces REJECT on critical dimensions.

## Boundary

This is a local semantics kernel. It is not a complete provenance trust system, does not establish independent ground truth, and does not estimate real-world false positive/negative rates.
