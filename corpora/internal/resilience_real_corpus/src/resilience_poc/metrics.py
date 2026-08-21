from __future__ import annotations

from typing import Iterable


def summarize(results: Iterable[dict]) -> dict:
    rows = list(results)
    injected = [r for r in rows if r.get("expected_outcome") == "REJECT"]
    clean = [r for r in rows if r.get("expected_outcome") == "AUTO_MERGE"]
    total_injected = len(injected)
    detected = sum(1 for r in injected if r["decision"] == "REJECT")
    false_positives = sum(1 for r in clean if r["decision"] != "AUTO_MERGE")
    missed = total_injected - detected
    deterministic = all(r.get("decision") == r.get("repeat_decision", r.get("decision")) for r in rows)
    complete = sum(1 for r in rows if r.get("manifest_complete", False)) / len(rows) if rows else 0.0
    reproducible = sum(1 for r in rows if r.get("repro_level") in {"REPRODUCIBLE", "VERIFIED_REPRODUCIBLE"}) / len(rows) if rows else 0.0
    return {
        "detection_rate": detected / total_injected if total_injected else 0.0,
        "false_positive_rate": false_positives / len(clean) if clean else 0.0,
        "false_negative_rate": missed / total_injected if total_injected else 0.0,
        "decision_determinism": 1.0 if deterministic else 0.0,
        "evidence_completeness": complete,
        "reproduction_success": reproducible,
        "runs": len(rows),
    }
