from __future__ import annotations

import json
import sys
from pathlib import Path
from importlib import resources

from .collector import collect
from .storage import get_json
from .validator import validate_manifest

BASE = Path(__file__).resolve().parents[2]
FIXTURES = resources.files("resilience_poc").joinpath("resources", "fixtures", "experiments")

EXPECTED_FAILURE_CODES = {
    "A": [],
    "B": ["DEP_DRIFT"],
    "C": ["SEM_INV_VIOLATION"],
    "D1": [],
    "D2": ["NOT_REPRODUCIBLE"],
    "E": ["UNEXPECTED_GIL_REACTIVATION"],
}

EXPECTED_REPRODUCTION = {
    "A": True,
    "B": True,
    "C": True,
    "D1": True,
    "D2": False,
    "E": True,
}


def load_json(path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def run_experiment(name: str) -> dict:
    patch = load_json(FIXTURES.joinpath(name, "01_generated_patch.json"))
    patch["fixture_test_evidence"] = {
        "id": f"testev-{name}",
        "evidence_manifest_ref": f"fixture:{name}",
        "unit_tests": {"executed": True, "count": 24, "passed": 24 if name not in {"B", "C"} else 23, "failed": 0 if name not in {"B", "C"} else 1, "coverage_percent": 78.4},
        "property_tests": {"executed": True, "framework": "fixture", "cases_run": 1200, "violations": 1 if name == "C" else 0},
        "fuzzing": {"executed": False},
        "test_environment": {"container_image": "fixture"},
        "integrity_signature": "fixture",
    }
    patch["fixture_dependency_report"] = {
        "id": f"depreport-{name}",
        "evidence_manifest_ref": f"fixture:{name}",
        "declared_lockfile_ref": "fixture:lock",
        "declared_materials": [],
        "runtime_imports": [{"module": "missing_pkg", "version": "0.0", "source": "fixture"}] if name == "B" else [],
        "dependency_drift": {"mismatches": [{"type": "undeclared_runtime_import", "module": "missing_pkg"}] if name == "B" else [], "count": 1 if name == "B" else 0},
        "sbom_ref": "fixture:sbom",
        "supply_chain_checks": {"executed": True, "signatures_valid": True, "cve_policy_pass": True},
        "integrity_signature": "fixture",
    }
    patch["fixture_semantic_fail"] = name == "C"
    patch["fixture_runtime_evidence"] = {"executed": True, "status": "pass", "checks": ["runtime_smoke"]}
    patch["fixture_observability_evidence"] = {"executed": True, "coverage": 1.0}
    patch["fixture_runtime_descriptor"] = {
        "implementation": "CPython", "language": "python", "version": "3.14-fixture",
        "build": {"free_threaded": False, "build_flags": []},
        "gil": {"build_supports_free_threading": False, "runtime_gil_requested": True, "runtime_gil_observed": True, "observation_method": "fixture"},
        "unexpected_gil_reactivation": name == "E",
        "platform": "linux-x86_64",
    }

    manifest = collect(patch)
    manifest["reproducibility"] = patch.get("fixture_reproducibility", manifest["reproducibility"])
    manifest["runtime_descriptor"] = patch.get("fixture_runtime_descriptor", manifest["runtime_descriptor"])

    from .collector import PRIVATE
    from .security import sign_json
    unsigned = dict(manifest)
    unsigned.pop("integrity_signature", None)
    manifest["integrity_signature"] = sign_json(unsigned, PRIVATE)
    from .storage import put_json
    put_json(manifest, manifest["id"])

    result = validate_manifest(manifest["id"])
    expected = patch.get("expected_outcome")
    actual = result.get("reliability_vector", {}).get("decision", {}).get("outcome")

    # True replay: re-read the same persisted evidence and run the validator again.
    replay_result = validate_manifest(manifest["id"])
    replay_decision = replay_result.get("reliability_vector", {}).get("decision", {}).get("outcome")

    return {
        "experiment": name,
        "manifest_id": manifest["id"],
        "result": result,
        "expected_outcome": expected,
        "expected_failure_codes": EXPECTED_FAILURE_CODES[name],
        "decision": actual,
        "replay_decision": replay_decision,
        "repro_level": result.get("reliability_vector", {}).get("reproducibility", {}).get("level"),
        "expected_reproduction_success": EXPECTED_REPRODUCTION[name],
    }


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print("usage: python -m resilience_poc.cli run-experiments | collect <patch.json> | validate <manifest_id>")
        return 2
    if argv[1] == "run-experiments":
        outputs = [run_experiment(x) for x in sorted(p.name for p in FIXTURES.iterdir() if p.is_dir())]
        from .metrics import summarize
        print(json.dumps({"experiments": outputs, "metrics": summarize(outputs)}, indent=2))
        expected_ok = all(o["decision"] == o["expected_outcome"] for o in outputs)
        return 0 if expected_ok and all(o["result"]["status"] == "completed" for o in outputs) else 1
    if argv[1] == "collect":
        manifest = collect(load_json(Path(argv[2])))
        print(json.dumps(manifest, indent=2))
        return 0
    if argv[1] == "validate":
        print(json.dumps(validate_manifest(argv[2]), indent=2))
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
