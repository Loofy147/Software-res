from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import os
import platform
import sys
import sysconfig
import time
from datetime import datetime, timezone
from contextlib import redirect_stderr, redirect_stdout
import io
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ARTIFACTS = ROOT / "artifacts" / "real-gil"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def gil_enabled() -> bool | None:
    fn = getattr(sys, "_is_gil_enabled", None)
    return bool(fn()) if callable(fn) else None


def runtime_snapshot() -> dict:
    return {
        "timestamp": utc_now(),
        "monotonic_ns": time.monotonic_ns(),
        "implementation": sys.implementation.name,
        "version": platform.python_version(),
        "version_string": sys.version,
        "platform": platform.platform(),
        "executable": sys.executable,
        "py_gil_disabled": sysconfig.get_config_var("Py_GIL_DISABLED"),
        "build_supports_free_threading": sysconfig.get_config_var("Py_GIL_DISABLED") == 1,
        "gil_enabled": gil_enabled(),
        "python_gil_env": os.environ.get("PYTHON_GIL"),
        "argv": sys.argv[:],
        "loaded_modules_count": len(sys.modules),
        "loaded_modules": sorted(sys.modules),
    }


def module_path(module_name: str) -> str | None:
    try:
        spec = importlib.util.find_spec(module_name)
    except Exception:
        return None
    return spec.origin if spec else None


def sha256_file(path: str | None) -> str | None:
    if not path or path in {"built-in", "frozen"}:
        return None
    p = Path(path)
    if not p.exists() or not p.is_file():
        return None
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def run(module_name: str, expected_reactivation: bool, require_free_threading: bool) -> dict:
    events = []
    preflight = runtime_snapshot()
    events.append({"event_type": "runtime_preflight", **preflight})
    events.append({
        "event_type": "gil_before_import",
        "timestamp": utc_now(),
        "monotonic_ns": time.monotonic_ns(),
        "gil_enabled": gil_enabled(),
    })

    import_start = {
        "event_type": "extension_import_start",
        "timestamp": utc_now(),
        "monotonic_ns": time.monotonic_ns(),
        "module": module_name,
        "module_path": module_path(module_name),
    }
    events.append(import_start)

    stdout_buf, stderr_buf, error = io.StringIO(), io.StringIO(), None
    try:
        with redirect_stdout(stdout_buf), redirect_stderr(stderr_buf):
            importlib.import_module(module_name)
    except Exception as exc:
        error = {"type": type(exc).__name__, "message": str(exc)}
    stdout = stdout_buf.getvalue()
    stderr = stderr_buf.getvalue()

    import_end = {
        "event_type": "extension_import_end",
        "timestamp": utc_now(),
        "monotonic_ns": time.monotonic_ns(),
        "module": module_name,
        "module_path": module_path(module_name),
        "module_sha256": sha256_file(module_path(module_name)),
        "error": error,
    }
    events.append(import_end)
    events.append({
        "event_type": "gil_after_import",
        "timestamp": utc_now(),
        "monotonic_ns": time.monotonic_ns(),
        "gil_enabled": gil_enabled(),
    })

    postflight = runtime_snapshot()
    events.append({"event_type": "runtime_postflight", **postflight})

    before = preflight["gil_enabled"]
    after = postflight["gil_enabled"]
    reactivated = before is False and after is True
    temporal_order_ok = events[1]["monotonic_ns"] < events[2]["monotonic_ns"] < events[3]["monotonic_ns"] < events[4]["monotonic_ns"]
    causal_attribution = reactivated and temporal_order_ok and error is None

    if require_free_threading and not preflight["build_supports_free_threading"]:
        status = "ENVIRONMENT_NOT_READY"
        failure_code = "FREE_THREADED_RUNTIME_UNAVAILABLE"
    elif require_free_threading and before is not False:
        status = "INVALID_PRECONDITION"
        failure_code = "GIL_NOT_DISABLED_AT_START"
    elif causal_attribution and expected_reactivation:
        status = "PASS"
        failure_code = "UNEXPECTED_GIL_REACTIVATION"
    elif causal_attribution and not expected_reactivation:
        status = "FAIL"
        failure_code = "FALSE_POSITIVE_GIL_REACTIVATION"
    elif expected_reactivation:
        status = "FAIL"
        failure_code = "EXPECTED_GIL_REACTIVATION_NOT_OBSERVED"
    else:
        status = "PASS" if before is after else "FAIL"
        failure_code = None if status == "PASS" else "UNEXPECTED_GIL_STATE_CHANGE"

    result = {
        "experiment": "REAL_GIL",
        "module": module_name,
        "expected_reactivation": expected_reactivation,
        "require_free_threading": require_free_threading,
        "status": status,
        "failure_code": failure_code,
        "causal_attribution": causal_attribution,
        "temporal_order_ok": temporal_order_ok,
        "runtime_before": preflight,
        "runtime_after": postflight,
        "events": events,
        "captured_stdout": stdout,
        "captured_stderr": stderr,
        "generated_at": utc_now(),
    }
    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    filename = f"{module_name.replace('.', '_')}-{datetime.now().strftime('%Y%m%dT%H%M%SZ')}-{time.monotonic_ns()}.json"
    (ARTIFACTS / filename).write_text(json.dumps(result, indent=2, sort_keys=True))
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("module")
    parser.add_argument("--expect-reactivation", action="store_true")
    parser.add_argument("--no-free-threading-required", action="store_true")
    args = parser.parse_args()
    result = run(
        args.module,
        expected_reactivation=args.expect_reactivation,
        require_free_threading=not args.no_free_threading_required,
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    status = result["status"]
    if status == "PASS":
        return 0
    elif status == "ENVIRONMENT_NOT_READY":
        return 20
    elif status == "INVALID_PRECONDITION":
        return 21
    else:
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
