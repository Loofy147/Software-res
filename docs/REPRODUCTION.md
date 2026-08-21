# Reproduction Guide

## Local PoC
1. Create a Python 3.13+ environment.
2. Install requirements from `core/requirements.txt`.
3. Run the non-runtime fixture suite with pytest.
4. Run the corpus/assumption tests.

## Real-GIL CI
Use the GitHub Actions workflow in `core/.github/workflows/real-gil.yml` on a repository runner with free-threaded CPython support. The workflow must fail closed when `Py_GIL_DISABLED != 1` or `_is_gil_enabled()` is initially true.

## External corpus
Use a runner with outbound Git access. Pin to recorded immutable SHAs before checkout. Generate new evidence artifacts rather than treating repository metadata as evaluation results.
