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


def test_high_risk_never_auto_merges():
    v={
      "functional":{"status":"pass"},"dependency":{"status":"pass"},"reproducibility":{"level":"REPRODUCIBLE"},
      "concurrency":{"status":"pass"},"security":{"status":"pass"}
    }
    assert decision_for_vector(v, risk_tier="high")["outcome"] == "REVIEW"


def test_missing_verification_evidence_cannot_become_pass():
    from resilience_poc.collector import collect
    from resilience_poc.validator import validate_manifest

    patch = {
        "id": "patch-no-evidence-test",
        "producer_agent": "test-agent",
        "target_repository": "repo@sha:123",
        "agent_metadata": {"generation_policy_id": "policy-123"},
        "risk_tier": "low",
    }
    manifest = collect(patch)
    result = validate_manifest(manifest["id"])
    assert result["status"] == "review"
    assert "MISSING_VERIFICATION_EVIDENCE" in result["errors"]
    assert result["reliability_vector"]["decision"]["outcome"] == "REVIEW"


def test_property_based_vector_decision_invariants():
    import random
    statuses = ["pass", "warn", "fail", "unknown"]
    repro_levels = ["NOT_REPRODUCIBLE", "REPRODUCIBLE", "VERIFIED_REPRODUCIBLE"]
    risk_tiers = ["low", "medium", "high", "critical"]

    rnd = random.Random(42)
    for _ in range(200):
        v = {
            "functional": {"status": rnd.choice(statuses)},
            "dependency": {"status": rnd.choice(statuses)},
            "concurrency": {"status": rnd.choice(statuses)},
            "security": {"status": rnd.choice(statuses)},
            "reproducibility": {"level": rnd.choice(repro_levels)},
            "mandatory_invariant_failures": ["FAIL_INV"] if rnd.random() < 0.2 else [],
        }
        tier = rnd.choice(risk_tiers)
        decision = decision_for_vector(v, risk_tier=tier)
        outcome = decision["outcome"]

        # Invariant I1: Critical FAIL, mandatory failure, or unreproducible -> REJECT
        has_critical_fail = any(v[d]["status"] == "fail" for d in ["functional", "dependency", "concurrency", "security"])
        if has_critical_fail or v["mandatory_invariant_failures"] or v["reproducibility"]["level"] == "NOT_REPRODUCIBLE":
            assert outcome == "REJECT"

        # Invariant I2: Any unknown/warn critical dimension -> never AUTO_MERGE
        has_critical_warn_unk = any(v[d]["status"] in {"warn", "unknown"} for d in ["functional", "dependency", "concurrency", "security"])
        if has_critical_warn_unk:
            assert outcome in {"REVIEW", "REJECT"}

        # Invariant I3: Non-low risk tier -> never AUTO_MERGE
        if tier != "low":
            assert outcome in {"REVIEW", "REJECT"}

        # Invariant I4: AUTO_MERGE requires all critical dimensions pass, reproducible, no mandatory failure, low risk
        if outcome == "AUTO_MERGE":
            assert not has_critical_fail
            assert not has_critical_warn_unk
            assert not v["mandatory_invariant_failures"]
            assert v["reproducibility"]["level"] in {"REPRODUCIBLE", "VERIFIED_REPRODUCIBLE"}
            assert tier == "low"


def test_unknown_runtime_and_observability_are_not_passes():
    from resilience_poc.validator import build_vector
    v = build_vector(
        {"id":"m","generated_patch_ref":"p","source_revision":"repo@sha:test","ai_evidence":{"target_repository":"repo@sha:test"},"slsa_provenance_ref":"link:x"},
        {"id":"t","unit_tests":{"executed":True,"count":1,"failed":0},"property_tests":{"violations":0}},
        {"id":"d","dependency_drift":{"count":0},"supply_chain_checks":{"executed":True,"signatures_valid":True,"cve_policy_pass":True}},
        {"level":"REPRODUCIBLE"}, {},
    )
    assert v["runtime"]["status"] == "unknown"
    assert v["observability"]["status"] == "unknown"
    assert v["decision"]["outcome"] == "REVIEW"
