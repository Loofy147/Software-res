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
    )
    payload = json.loads(result.stdout)
    if payload["runtime_before"]["build_supports_free_threading"]:
        assert result.returncode in {0, 10}
        assert payload["status"] != "ENVIRONMENT_NOT_READY"
    else:
        assert result.returncode == 20
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
    )
    payload = json.loads(result.stdout)
    assert result.returncode == 20 if payload["environment_ready"] is False else result.returncode in {0, 1}
    assert payload["environment_ready"] is False
    assert payload["accepted"] is False


def test_real_gil_environment_not_ready_has_nonzero_exit_code():
    runner = ROOT / "experiments" / "real_gil" / "run_real_gil_experiment.py"
    proc = subprocess.run(
        [sys.executable, str(runner), "compatible_ext"],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    payload = json.loads(proc.stdout)
    if payload["status"] == "ENVIRONMENT_NOT_READY":
        assert proc.returncode == 20


def test_phase_a_batch_environment_not_ready_has_nonzero_exit_code():
    runner = ROOT / "experiments" / "real_gil" / "run_phase_a_batch.py"
    proc = subprocess.run(
        [sys.executable, str(runner), "--runs", "1"],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    summary = json.loads((ROOT / "artifacts" / "real-gil" / "phase-a-summary.json").read_text())
    if not summary["environment_ready"]:
        assert proc.returncode == 20
