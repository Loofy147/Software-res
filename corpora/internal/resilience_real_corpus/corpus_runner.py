from __future__ import annotations

import argparse
import json
import math
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

ALLOWED_SOURCE_KINDS = {"fixture", "real_patch", "real_repository", "synthetic_mutation"}
REQUIRED = {
    "record_id", "project_id", "patch_id", "source_kind",
    "expected_outcome", "actual_outcome", "evidence_complete", "decision_repeatable",
}


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        row = json.loads(line)
        missing = sorted(REQUIRED - row.keys())
        if missing:
            raise ValueError(f"line {line_no}: missing {missing}")
        if row["source_kind"] not in ALLOWED_SOURCE_KINDS:
            raise ValueError(f"line {line_no}: invalid source_kind={row['source_kind']!r}")
        rows.append(row)
    if not rows:
        raise ValueError("corpus is empty")
    return rows


def rate(num: int, den: int) -> float | None:
    return round(num / den, 6) if den else None


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    injected = [r for r in rows if r.get("injected_failure_code")]
    clean = [r for r in rows if not r.get("injected_failure_code")]
    by_kind: dict[str, list[dict[str, Any]]] = defaultdict(list)
    by_failure: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for r in rows:
        by_kind[r["source_kind"]].append(r)
        if r.get("injected_failure_code"):
            by_failure[r["injected_failure_code"]].append(r)

    detected = [r for r in injected if r["actual_outcome"] == "REJECT"]
    missed = [r for r in injected if r["actual_outcome"] != "REJECT"]
    false_pos = [r for r in clean if r["actual_outcome"] == "REJECT"]
    expected_match = sum(r["expected_outcome"] == r["actual_outcome"] for r in rows)
    complete = sum(bool(r["evidence_complete"]) for r in rows)
    deterministic = sum(bool(r["decision_repeatable"]) for r in rows)
    reproducible_eligible = [r for r in rows if r.get("repro_level") is not None]
    reproducible_success = [r for r in reproducible_eligible if r["repro_level"] in {"REPRODUCIBLE","VERIFIED_REPRODUCIBLE"}]

    return {
        "dataset": {
            "records": len(rows),
            "projects": len({r["project_id"] for r in rows}),
            "patches": len({(r["project_id"], r["patch_id"]) for r in rows}),
            "source_kind_counts": dict(sorted(Counter(r["source_kind"] for r in rows).items())),
        },
        "quality": {
            "evidence_completeness_rate": rate(complete, len(rows)),
            "decision_determinism_rate": rate(deterministic, len(rows)),
            "decision_accuracy_against_expected": rate(expected_match, len(rows)),
        },
        "failure_detection": {
            "detection_rate": rate(len(detected), len(injected)),
            "false_positive_rate": rate(len(false_pos), len(clean)),
            "false_negative_rate": rate(len(missed), len(injected)),
            "injected_failures": len(injected),
            "clean_runs": len(clean),
        },
        "reproducibility": {
            "eligible_runs": len(reproducible_eligible),
            "reproduction_success": rate(len(reproducible_success), len(reproducible_eligible)),
            "non_reproducibility_detection_rate": rate(
                sum(r.get("injected_failure_code") == "NOT_REPRODUCIBLE" and r.get("actual_outcome") == "REJECT" for r in rows),
                sum(r.get("injected_failure_code") == "NOT_REPRODUCIBLE" for r in rows),
            ),
        },
        "by_source_kind": {
            kind: summarize_subset(subset)
            for kind, subset in sorted(by_kind.items())
        },
        "by_failure_code": {
            code: summarize_subset(subset)
            for code, subset in sorted(by_failure.items())
        },
        "coverage": {
            "failure_codes": sorted({r["injected_failure_code"] for r in injected}),
            "source_kinds": sorted(by_kind),
        },
    }


def summarize_subset(rows: list[dict[str, Any]]) -> dict[str, Any]:
    injected = [r for r in rows if r.get("injected_failure_code")]
    clean = [r for r in rows if not r.get("injected_failure_code")]
    detected = sum(r["actual_outcome"] == "REJECT" for r in injected)
    fp = sum(r["actual_outcome"] == "REJECT" for r in clean)
    return {
        "records": len(rows),
        "detection_rate": rate(detected, len(injected)),
        "false_positive_rate": rate(fp, len(clean)),
        "evidence_completeness_rate": rate(sum(bool(r["evidence_complete"]) for r in rows), len(rows)),
        "decision_determinism_rate": rate(sum(bool(r["decision_repeatable"]) for r in rows), len(rows)),
    }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("dataset", type=Path)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    result = summarize(load_jsonl(args.dataset))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
