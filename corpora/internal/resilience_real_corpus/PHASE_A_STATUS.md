# Phase A — Real GIL Experiment Status

## Local verification

The local environment is a regular CPython build:

- `Py_GIL_DISABLED = 0`
- `sys._is_gil_enabled() = True`

Therefore a real free-threaded causal result is **not claimed locally**.

The harness fails closed with:

- `ENVIRONMENT_NOT_READY`
- `FREE_THREADED_RUNTIME_UNAVAILABLE`

## Test status

- pytest: 13/13 passed (including VSA builder/validator)
- C-extension fixtures: build successfully on the local CPython runtime
- Batch aggregator: verified fail-closed on non-free-threaded runtime

## Real-runtime acceptance

The GitHub Actions workflow runs five independent control processes and five independent treatment processes on free-threaded CPython 3.13t and 3.14t.

Acceptance requires:

- control: 5/5 `False -> False`
- treatment: 5/5 `False -> True`
- causal attribution: 100%
- evidence-chain completeness: 100%
- deterministic decisions
- no false-positive GIL reactivation in control

The first successful free-threaded CI run is the point at which
`Real GIL Causality` may be upgraded from `OPEN` to `EXPERIMENTALLY_SUPPORTED`.

## Phase B — VSA MVP

The PoC now emits and validates an in-toto VSA predicate using the SLSA v1.2 predicate type:
`https://slsa.dev/verification_summary/v1`.

The VSA deliberately claims `SLSA_BUILD_LEVEL_UNEVALUATED`; the PoC does not claim an actual SLSA build level.
The VSA is also protected by the PoC's Ed25519 integrity signature, but this is not yet a production DSSE/in-toto signature envelope.
