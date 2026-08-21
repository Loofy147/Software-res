import json
from pathlib import Path

from resilience_poc.models import decision_for_vector
from resilience_poc.repro import assess_reproducibility
from resilience_poc.runtime_checks import observe_cpython_gil
from resilience_poc.validator import validate_schema

ROOT=Path(__file__).resolve().parents[1]


def test_repro_verified():
    r=assess_reproducibility(
        {"declared_inputs_digest":"x","artifact_digest":"a"},
        {"declared_inputs_digest":"x","artifact_digest":"a"},
        independent=True,
    )
    assert r["level"]=="VERIFIED_REPRODUCIBLE"


def test_repro_fails_on_different_artifacts():
    r=assess_reproducibility(
        {"declared_inputs_digest":"x","artifact_digest":"a"},
        {"declared_inputs_digest":"x","artifact_digest":"b"},
        independent=True,
    )
    assert r["level"]=="NOT_REPRODUCIBLE"


def test_decision_rejects_critical_failure():
    v={
      "functional":{"status":"pass"},"dependency":{"status":"fail"},"reproducibility":{"level":"REPRODUCIBLE"},
      "concurrency":{"status":"pass"},"security":{"status":"pass"}
    }
    assert decision_for_vector(v)["outcome"]=="REJECT"


def test_decision_review_on_unknown():
    v={
      "functional":{"status":"pass"},"dependency":{"status":"pass"},"reproducibility":{"level":"REPRODUCIBLE"},
      "concurrency":{"status":"unknown"},"security":{"status":"pass"}
    }
    assert decision_for_vector(v)["outcome"]=="REVIEW"


def test_python_gil_observer_has_expected_shape():
    r=observe_cpython_gil()
    assert "implementation" in r and "runtime_gil_observed" in r


def test_all_schemas_load():
    for name in [
        '01_generated_patch.schema.json','02_evidence_manifest.schema.json','03_test_evidence.schema.json',
        '04_dependency_report.schema.json','05_reliability_vector.schema.json']:
        schema=json.loads((ROOT/'schemas'/name).read_text())
        assert schema['$schema']
