from datetime import datetime, timezone

from resilience_poc.evidence import EvidenceState, assess_evidence
from resilience_poc.models import decision_for_vector


def base_vector():
    return {
        "functional": {"status": "pass", "evidence_state": "PASS"},
        "dependency": {"status": "pass", "evidence_state": "PASS"},
        "reproducibility": {"level": "REPRODUCIBLE"},
        "concurrency": {"status": "pass", "evidence_state": "PASS"},
        "security": {"status": "pass", "evidence_state": "PASS"},
    }


def test_evidence_states_have_explicit_semantics():
    assert assess_evidence([]) == EvidenceState.UNOBSERVED
    assert assess_evidence([{"status": "pass"}]) == EvidenceState.PASS
    assert assess_evidence([{"status": "fail"}]) == EvidenceState.FAIL
    assert assess_evidence([{"valid": False}]) == EvidenceState.INVALID
    assert assess_evidence([{"status": "pass", "stale": True}]) == EvidenceState.STALE
    assert assess_evidence([{"conflict": True}]) == EvidenceState.CONFLICT


def test_conflict_has_precedence_over_failure():
    assert assess_evidence([{"status": "fail"}, {"status": "pass"}]) == EvidenceState.CONFLICT


def test_stale_expiry_is_detected():
    now = datetime(2026, 10, 5, tzinfo=timezone.utc)
    assert assess_evidence([{"status": "pass", "expires_at": "2026-10-04T00:00:00Z"}], now=now) == EvidenceState.STALE


def test_missing_evidence_cannot_auto_merge():
    v = base_vector()
    v["security"] = {"status": "pass", "evidence_state": "UNOBSERVED"}
    assert decision_for_vector(v)["outcome"] == "REVIEW"


def test_invalid_evidence_rejects():
    v = base_vector()
    v["security"] = {"status": "pass", "evidence_state": "INVALID"}
    assert decision_for_vector(v)["outcome"] == "REJECT"


def test_stale_or_conflicting_evidence_requires_review():
    for state in ("STALE", "CONFLICT"):
        v = base_vector()
        v["security"] = {"status": "pass", "evidence_state": state}
        assert decision_for_vector(v)["outcome"] == "REVIEW"


def test_explicit_pass_preserves_auto_merge():
    assert decision_for_vector(base_vector())["outcome"] == "AUTO_MERGE"
