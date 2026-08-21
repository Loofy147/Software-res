import json
from pathlib import Path

from corpus_runner import load_jsonl, summarize

BASE = Path(__file__).resolve().parents[1] / "baseline" / "corpus-example.jsonl"


def test_corpus_summary_fixture_only():
    result = summarize(load_jsonl(BASE))
    assert result["failure_detection"]["detection_rate"] == 1.0
    assert result["failure_detection"]["false_positive_rate"] == 0.0
    assert result["failure_detection"]["false_negative_rate"] == 0.0
    assert result["quality"]["decision_determinism_rate"] == 1.0
    assert result["quality"]["evidence_completeness_rate"] == 1.0
    assert result["reproducibility"]["non_reproducibility_detection_rate"] == 1.0
    assert result["dataset"]["projects"] == 1


def test_empty_dataset_rejected(tmp_path):
    p = tmp_path / "empty.jsonl"
    p.write_text("\n")
    try:
        load_jsonl(p)
        assert False, "expected ValueError"
    except ValueError as exc:
        assert "empty" in str(exc)
