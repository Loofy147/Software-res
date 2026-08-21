# Experimental Protocols

## Phase A — Real GIL
Control: free-threaded CPython + compatible extension -> GIL False -> False.
Treatment: free-threaded CPython + intentionally incompatible extension -> GIL False -> True.
Required causal evidence: runtime snapshot before import, extension import event, runtime snapshot after import, extension identity, monotonic ordering, and provenance.

## Phase B — VSA/DSSE
Produce an in-toto statement carrying the SLSA verification-summary predicate, wrap it in DSSE, sign it in the local PoC, and verify the envelope before linking it into the Reliability Vector.

## External held-out corpus
Pin every project to an immutable SHA before execution. Record repository metadata, license metadata, build system, dependency lock artifacts, and independent reference evidence. Never infer ground truth from the validator's own output.
