import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "experiments" / "real_gil" / "run_real_gil_experiment.py"


def test_real_gil_runner_refuses_non_free_threaded_environment(tmp_path):
    result = subprocess.run(
        [sys.executable, str(RUNNER), "incompatible_ext", "--expect-reactivation"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    payload = json.loads(result.stdout)
    if payload["runtime_before"]["build_supports_free_threading"]:
        assert payload["status"] != "ENVIRONMENT_NOT_READY"
    else:
        assert payload["status"] == "ENVIRONMENT_NOT_READY"
        assert payload["failure_code"] == "FREE_THREADED_RUNTIME_UNAVAILABLE"


def test_local_c_extension_control_import_sequence_runs_without_reactivation():
    ext_dir = ROOT / "experiments" / "real_gil" / "compatible_ext"
    build = subprocess.run(
        [sys.executable, "setup.py", "build_ext", "--inplace"],
        cwd=ext_dir,
        text=True,
        capture_output=True,
    )
    assert build.returncode == 0, build.stderr
    result = subprocess.run(
        [sys.executable, str(RUNNER), "compatible_ext", "--no-free-threading-required"],
        cwd=ROOT,
        env={**__import__("os").environ, "PYTHONPATH": str(ext_dir)},
        text=True,
        capture_output=True,
        check=True,
    )
    payload = json.loads(result.stdout)
    assert payload["temporal_order_ok"] is True
    assert payload["causal_attribution"] is False


def test_phase_a_batch_fails_closed_when_free_threading_is_unavailable(tmp_path):
    batch = ROOT / "experiments" / "real_gil" / "run_phase_a_batch.py"
    result = subprocess.run(
        [sys.executable, str(batch), "--runs", "1"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    payload = json.loads(result.stdout)
    assert payload["environment_ready"] is False
    assert payload["accepted"] is False
