from __future__ import annotations

import importlib
import platform
import sys
from typing import Any


def observe_cpython_gil() -> dict[str, Any]:
    implementation = platform.python_implementation()
    supported = implementation == "CPython" and hasattr(sys, "_is_gil_enabled")
    observed = sys._is_gil_enabled() if supported else None
    return {
        "implementation": implementation,
        "version": platform.python_version(),
        "build_supports_free_threading": "free-threaded" in sys.version.lower() or "freethreaded" in sys.version.lower(),
        "runtime_gil_requested": None,
        "runtime_gil_observed": observed,
        "observation_method": "CPython:sys._is_gil_enabled" if supported else "unsupported",
        "python_version_string": sys.version,
        "loaded_modules_count": len(sys.modules),
    }


def snapshot() -> dict[str, Any]:
    return {"gil": observe_cpython_gil(), "loaded_modules": sorted(m for m in sys.modules if m)}


def run_import_causality(module_name: str) -> dict[str, Any]:
    before = observe_cpython_gil()
    error = None
    try:
        importlib.import_module(module_name)
    except Exception as exc:  # intentional fixture support
        error = f"{type(exc).__name__}: {exc}"
    after = observe_cpython_gil()
    reactivated = before.get("runtime_gil_observed") is False and after.get("runtime_gil_observed") is True
    return {
        "module": module_name,
        "before": before,
        "after": after,
        "error": error,
        "unexpected_gil_reactivation": reactivated,
    }
