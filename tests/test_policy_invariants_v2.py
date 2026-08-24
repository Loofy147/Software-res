from resilience_poc.models import decision_for_vector


def base_vector():
    return {
        "functional": {"status": "pass"},
        "dependency": {"status": "pass"},
        "reproducibility": {"level": "REPRODUCIBLE"},
        "concurrency": {"status": "pass"},
        "security": {"status": "pass"},
    }


def test_any_critical_unknown_cannot_auto_merge():
    for dim in ("functional", "dependency", "concurrency", "security"):
        v = base_vector(); v[dim] = {"status": "unknown"}
        assert decision_for_vector(v)["outcome"] == "REVIEW"


def test_any_critical_fail_rejects():
    for dim in ("functional", "dependency", "concurrency", "security"):
        v = base_vector(); v[dim] = {"status": "fail"}
        assert decision_for_vector(v)["outcome"] == "REJECT"


def test_non_low_risk_never_auto_merges():
    for risk in ("medium", "high", "critical"):
        assert decision_for_vector(base_vector(), risk_tier=risk)["outcome"] == "REVIEW"
