"""Controlled decision-separation benchmark for evidence semantics."""
from __future__ import annotations

import json

from resilience_poc.models import decision_for_vector


def base_vector():
    return {
        "functional": {"status": "pass", "evidence_state": "PASS"},
        "dependency": {"status": "pass", "evidence_state": "PASS"},
        "reproducibility": {"level": "REPRODUCIBLE"},
        "concurrency": {"status": "pass", "evidence_state": "PASS"},
        "security": {"status": "pass", "evidence_state": "PASS"},
    }


def baseline_status_only(vector):
    critical = ("functional", "dependency", "concurrency", "security")
    if any(vector[d].get("status") == "fail" for d in critical):
        return "REJECT"
    if any(vector[d].get("status") in {"warn", "unknown"} for d in critical):
        return "REVIEW"
    if vector.get("reproducibility", {}).get("level") == "NOT_REPRODUCIBLE":
        return "REJECT"
    return "AUTO_MERGE"


def run():
    paired_states = [
        ("missing", "UNOBSERVED", "REVIEW"),
        ("invalid", "INVALID", "REJECT"),
        ("stale", "STALE", "REVIEW"),
        ("conflict", "CONFLICT", "REVIEW"),
    ]
    rows = []
    for name, evidence_state, expected_kernel in paired_states:
        v = base_vector()
        v["security"] = {"status": "pass", "evidence_state": evidence_state}
        kernel = decision_for_vector(v)["outcome"]
        baseline = baseline_status_only(v)
        rows.append({
            "case": name,
            "kernel": kernel,
            "baseline_status_only": baseline,
            "expected_kernel": expected_kernel,
            "separated": kernel != baseline,
        })

    clean = base_vector()
    failed = base_vector()
    failed["security"] = {"status": "fail", "evidence_state": "FAIL"}

    negative_controls = [
        {"case": "clean_pass", "kernel": decision_for_vector(clean)["outcome"], "baseline_status_only": baseline_status_only(clean)},
        {"case": "explicit_fail", "kernel": decision_for_vector(failed)["outcome"], "baseline_status_only": baseline_status_only(failed)},
    ]

    separation_rate = sum(r["separated"] for r in rows) / len(rows)
    return {
        "benchmark": "decision-separation-v1",
        "warning": "controlled semantic capability test; not a field accuracy estimate",
        "cases": rows,
        "negative_controls": negative_controls,
        "semantic_separation_rate": separation_rate,
        "all_expected": all(r["kernel"] == r["expected_kernel"] for r in rows)
        and negative_controls[0]["kernel"] == negative_controls[0]["baseline_status_only"] == "AUTO_MERGE"
        and negative_controls[1]["kernel"] == negative_controls[1]["baseline_status_only"] == "REJECT",
    }


if __name__ == "__main__":
    result = run()
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result["all_expected"] else 1)
