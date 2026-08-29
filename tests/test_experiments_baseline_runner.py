from __future__ import annotations

import json
from pathlib import Path
import pytest

from experiments_baseline_runner import load_records, summarize, main


def test_baseline_runner_summarize(tmp_path: Path):
    dataset_file = tmp_path / "baseline_dataset.jsonl"
    rows = [
        {
            "project_id": "proj1",
            "patch_id": "patch1",
            "expected_outcome": "AUTO_MERGE",
            "actual_outcome": "AUTO_MERGE",
            "injected_failure_code": None,
            "evidence_complete": True,
            "decision_repeatable": True,
        },
        {
            "project_id": "proj1",
            "patch_id": "patch2",
            "expected_outcome": "REJECT",
            "actual_outcome": "REJECT",
            "injected_failure_code": "SEM_INV_VIOLATION",
            "evidence_complete": True,
            "decision_repeatable": True,
        },
    ]
    dataset_file.write_text("\n".join(json.dumps(r) for r in rows) + "\n")

    records = load_records(dataset_file)
    summary = summarize(records)

    assert summary["records"] == 2
    assert summary["projects"] == 1
    assert summary["patches"] == 2
    assert summary["detection_rate"] == 1.0
    assert summary["false_positive_rate"] == 0.0
    assert summary["false_negative_rate"] == 0.0
    assert summary["decision_accuracy_against_expected"] == 1.0
    assert summary["decision_determinism_rate"] == 1.0
    assert summary["evidence_completeness_rate"] == 1.0


def test_baseline_runner_empty_dataset(tmp_path: Path):
    empty_file = tmp_path / "empty.jsonl"
    empty_file.write_text("\n")
    with pytest.raises(ValueError, match="baseline dataset is empty"):
        load_records(empty_file)


def test_baseline_runner_missing_fields(tmp_path: Path):
    invalid_file = tmp_path / "invalid.jsonl"
    invalid_file.write_text(json.dumps({"project_id": "p1"}) + "\n")
    with pytest.raises(ValueError, match="line 1: missing"):
        load_records(invalid_file)


def test_baseline_runner_main(tmp_path: Path, monkeypatch, capsys):
    dataset_file = tmp_path / "baseline_dataset.jsonl"
    output_file = tmp_path / "output_summary.json"
    rows = [
        {
            "project_id": "proj1",
            "patch_id": "patch1",
            "expected_outcome": "AUTO_MERGE",
            "actual_outcome": "AUTO_MERGE",
            "injected_failure_code": None,
            "evidence_complete": True,
            "decision_repeatable": True,
        }
    ]
    dataset_file.write_text(json.dumps(rows[0]) + "\n")

    monkeypatch.setattr("sys.argv", ["experiments_baseline_runner.py", str(dataset_file), "--output", str(output_file)])
    ret = main()
    assert ret == 0
    assert output_file.exists()
    out = json.loads(output_file.read_text())
    assert out["records"] == 1
