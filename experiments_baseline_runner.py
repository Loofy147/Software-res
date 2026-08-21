from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any


REQUIRED_FIELDS = {
    "project_id",
    "patch_id",
    "expected_outcome",
    "actual_outcome",
    "injected_failure_code",
    "evidence_complete",
    "decision_repeatable",
}


def load_records(path: Path) -> list[dict[str, Any]]:
    records = []
    for line_no, line in enumerate(path.read_text().splitlines(), 1):
        if not line.strip():
            continue
        row = json.loads(line)
        missing = sorted(REQUIRED_FIELDS - set(row))
        if missing:
            raise ValueError(f"line {line_no}: missing {missing}")
        records.append(row)
    if not records:
        raise ValueError("baseline dataset is empty")
    return records


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    injected = [r for r in rows if r["injected_failure_code"]]
    controls = [r for r in rows if not r["injected_failure_code"]]
    detected = [r for r in injected if r["actual_outcome"] == "REJECT"]
    missed = [r for r in injected if r["actual_outcome"] != "REJECT"]
    false_positive = [r for r in controls if r["actual_outcome"] == "REJECT"]
    valid_decision = [r for r in rows if r["expected_outcome"] == r["actual_outcome"]]

    by_failure = Counter(r["injected_failure_code"] for r in injected)
    detected_by_failure = Counter(r["injected_failure_code"] for r in detected)

    return {
        "records": len(rows),
        "projects": len({r["project_id"] for r in rows}),
        "patches": len({(r["project_id"], r["patch_id"]) for r in rows}),
        "detection_rate": len(detected) / len(injected) if injected else None,
        "false_positive_rate": len(false_positive) / len(controls) if controls else None,
        "false_negative_rate": len(missed) / len(injected) if injected else None,
        "decision_accuracy_against_expected": len(valid_decision) / len(rows),
        "decision_determinism_rate": sum(bool(r["decision_repeatable"]) for r in rows) / len(rows),
        "evidence_completeness_rate": sum(bool(r["evidence_complete"]) for r in rows) / len(rows),
        "failures_by_code": dict(sorted(by_failure.items())),
        "detected_by_code": dict(sorted(detected_by_failure.items())),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("dataset", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    records = load_records(args.dataset)
    result = summarize(records)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
