# Reproduction Guide

## Local PoC (v0.2.0)
1. Create a Python 3.12+ environment:
   ```bash
   python3 -m venv .venv && source .venv/bin/activate
   pip install -e '.[test]'
   ```
2. Run the unit test suite with pytest:
   ```bash
   pytest -v
   ```
3. Run the policy mutation check:
   ```bash
   python3 tools/mutation_check.py
   ```
4. Run the controlled A–E experiments CLI:
   ```bash
   python3 -m resilience_poc.cli run-experiments
   ```

## Standard CI
Use `.github/workflows/ci.yml` for automated testing across Python 3.12 and 3.13 runners on push/PR to `main`.

## Real-GIL CI
Use `.github/workflows/real-gil.yml` on a repository runner with free-threaded CPython support (`3.13t` / `3.14t`). The workflow fails closed when `Py_GIL_DISABLED != 1` or `_is_gil_enabled()` is initially true.

## External corpus
Use a runner with outbound Git access. Pin to recorded immutable SHAs before checkout. Generate new evidence artifacts rather than treating repository metadata as evaluation results.
