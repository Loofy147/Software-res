# Software Resilience Stack — Evidence PoC v0.1

Minimal discriminating experiment for AI-generated software reliability evidence.

## Scope

The PoC implements:

- five artifact contracts with JSON Schema validation
- an Evidence Collector
- a provenance fixture generator using an in-toto Statement containing a SLSA v1 provenance predicate
- Ed25519 signing/verification for local PoC manifests
- Verification jobs for unit/property evidence fixtures
- declared-vs-runtime dependency reconciliation
- CPython GIL runtime observation (`sys._is_gil_enabled()` when available)
- reproducibility checks using two build outputs
- a deterministic multi-dimensional Reliability Vector decision engine
- intentional experiments A–E

## Important boundary

The provenance generator is a **local builder fixture**, not a production SLSA builder. It produces a structurally valid in-toto Statement-shaped artifact for the PoC and records its reference in the Evidence Manifest. Production deployment should replace it with real CI-builder provenance/attestations and independent signature/key management.

## Run

```bash
python -m pip install -r requirements.txt
pytest -q
python -m resilience_poc.cli run-experiments
python -m resilience_poc.cli collect fixtures/experiments/A/01_generated_patch.json
python -m resilience_poc.cli validate <manifest-id>
```

API server:

```bash
uvicorn resilience_poc.api:app --app-dir src --reload
```

Endpoints:

- `POST /collector/submit`
- `POST /validator/validate/{manifest_id}`
- `GET /artifacts/{artifact_id}`

## Evidence model

SLSA v1.2 provenance is represented as the predicate inside an in-toto Statement. The project-specific Evidence Manifest points to that provenance and adds AI-specific evidence, runtime data, reproducibility data, and references to the other evidence artifacts.

## Python GIL check

The runtime detector uses `sys._is_gil_enabled()` only when running on CPython versions that expose it. It also captures interpreter/build metadata so a missing method is treated as `unknown`, not as evidence that the GIL is disabled.

## Current PoC verification status

The bundled logical fixtures produce the expected policy decisions:

- A -> AUTO_MERGE
- B -> REJECT / `DEP_DRIFT`
- C -> REJECT / `SEM_INV_VIOLATION`
- D1 -> AUTO_MERGE / `VERIFIED_REPRODUCIBLE`
- D2 -> REJECT / `NOT_REPRODUCIBLE`
- E -> REJECT / `UNEXPECTED_GIL_REACTIVATION`

Experiment E is currently a **causality-shaped fixture**, not proof from a real third-party incompatible C extension. A real deployment must execute the before-import/import/after-import sequence on a free-threaded CPython build and verify the observed transition.

## Phase A — Real GIL Experiment v1

This repository now contains a real C-extension experiment harness under `experiments/real_gil/`:

- `compatible_ext`: multi-phase extension that declares `Py_mod_gil = Py_MOD_GIL_NOT_USED` on free-threaded builds.
- `incompatible_ext`: intentionally omits the `Py_mod_gil` slot; on a free-threaded CPython build its import should cause the GIL to be enabled unless GIL re-enable is explicitly prohibited by runtime policy.
- `run_real_gil_experiment.py`: captures preflight, before/after GIL state, import events, extension identity, temporal ordering, and causal attribution.
- `.github/workflows/real-gil.yml`: runs the experiment on CPython `3.13t` and `3.14t` using `actions/setup-python`.

The local execution environment used for this PoC currently has CPython 3.13.5 with `Py_GIL_DISABLED=0`. Therefore the real Phase A treatment/control cannot be claimed as executed here. The harness correctly returns `ENVIRONMENT_NOT_READY / FREE_THREADED_RUNTIME_UNAVAILABLE` instead of fabricating a result. The local C extensions do compile and the event logger was exercised on the normal-GIL interpreter.

The Phase A batch runner executes independent processes for five control and five treatment runs and computes the acceptance metrics. It is fail-closed when the required free-threaded runtime is unavailable.

### Phase A acceptance protocol

Use at least 5 control runs with `compatible_ext` and 5 treatment runs with `incompatible_ext` on a genuine free-threaded CPython runtime. The treatment is accepted only when `gil_before == false`, the import occurs between the two observations, `gil_after == true`, and the extension identity is captured. A real run should also preserve raw logs and the SLSA/in-toto provenance reference.
