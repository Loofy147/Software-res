# Phase B status

- VSA predicate: SLSA v1.2 verification summary.
- DSSE envelope: implemented with ECDSA P-256/SHA-256 and DSSE v1 PAE.
- VSA DSSE signature verification: experimentally supported by local tests.
- Reliability Vector: emits `vsa_ref` and `vsa_dsse_ref`.
- Baseline runner: implemented; no claim about generalization until a real corpus is supplied.
- Real-GIL causality: OPEN; requires an actual free-threaded CPython runner.
- Production key management / trust root: OPEN.
