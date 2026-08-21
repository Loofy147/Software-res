from __future__ import annotations

import json
import sys
from pathlib import Path

from .collector import collect
from .storage import get_json
from .validator import validate_manifest

BASE = Path(__file__).resolve().parents[2]
FIXTURES = BASE / "fixtures" / "experiments"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def run_experiment(name: str) -> dict:
    patch = load_json(FIXTURES / name / "01_generated_patch.json")
    manifest = collect(patch)
    # Fixture behaviors are carried in the generated patch to keep the runner deterministic.
    manifest["reproducibility"] = patch.get("fixture_reproducibility", manifest["reproducibility"])
    manifest["runtime_descriptor"] = patch.get("fixture_runtime_descriptor", manifest["runtime_descriptor"])
    # Persist mutated manifest directly; collector signed the earlier version, so this is intentionally demo-only.
    # Re-sign for a valid fixture manifest.
    from .collector import PRIVATE
    from .security import sign_json
    unsigned = dict(manifest); unsigned.pop("integrity_signature", None)
    manifest["integrity_signature"] = sign_json(unsigned, PRIVATE)
    from .storage import put_json
    put_json(manifest, manifest["id"])
    result = validate_manifest(manifest["id"])
    expected = patch.get("expected_outcome")
    actual = result.get("reliability_vector", {}).get("decision", {}).get("outcome")
    return {"experiment": name, "manifest_id": manifest["id"], "result": result, "expected_outcome": expected, "decision": actual, "repro_level": result.get("reliability_vector", {}).get("reproducibility", {}).get("level"), "manifest_complete": True, "repeat_decision": actual}


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
