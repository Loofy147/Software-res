from __future__ import annotations

from typing import Iterable

DIMENSIONS = (
    "functional",
    "semantic",
    "dependency",
    "runtime",
    "concurrency",
    "security",
    "observability",
    "reproducibility",
)


def _vector_complete(row: dict) -> bool:
    vector = row.get("result", {}).get("reliability_vector", {})
    if not vector:
        return False
    for dim in DIMENSIONS:
        if dim not in vector:
            return False
        if dim == "reproducibility":
            if not vector[dim].get("evidence_refs"):
                return False
        else:
            if not vector[dim].get("evidence_refs"):
                return False
            if vector[dim].get("evidence_state") == "UNOBSERVED":
                return False
    return True


def _observed_failure_codes(row: dict) -> set[str]:
    vector = row.get("result", {}).get("reliability_vector", {})
    codes = set(vector.get("mandatory_invariant_failures", []))
    for dim in DIMENSIONS:
        if dim == "reproducibility":
            codes.update(vector.get(dim, {}).get("failure_codes", []))
        else:
            codes.update(vector.get(dim, {}).get("failure_codes", []))
    return codes


def summarize(results: Iterable[dict]) -> dict:
    rows = list(results)
    injected = [r for r in rows if r.get("expected_failure_codes")]
    controls = [r for r in rows if not r.get("expected_failure_codes")]

    correctly_classified = sum(
        bool(set(r["expected_failure_codes"]) <= _observed_failure_codes(r))
        for r in injected
    )
    false_positives = sum(1 for r in controls if r.get("decision") != "AUTO_MERGE")
    missed = len(injected) - correctly_classified

    replayable = [r for r in rows if r.get("replay_decision") is not None]
    deterministic = sum(
        r.get("decision") == r.get("replay_decision")
        for r in replayable
    )

    complete = sum(_vector_complete(r) for r in rows)

    repro_success_rows = [
        r for r in rows if r.get("expected_reproduction_success") is True
    ]
    repro_success = sum(
        r.get("repro_level") in {"REPRODUCIBLE", "VERIFIED_REPRODUCIBLE"}
        for r in repro_success_rows
    )

    non_repro_rows = [
        r for r in rows if r.get("expected_reproduction_success") is False
    ]
    non_repro_detected = sum(
        r.get("repro_level") == "NOT_REPRODUCIBLE"
        for r in non_repro_rows
    )

    return {
        "failure_code_detection_rate": correctly_classified / len(injected) if injected else 0.0,
        "false_positive_rate": false_positives / len(controls) if controls else 0.0,
        "false_negative_rate": missed / len(injected) if injected else 0.0,
        "decision_determinism": deterministic / len(replayable) if replayable else 0.0,
        "evidence_completeness": complete / len(rows) if rows else 0.0,
        "reproduction_success": repro_success / len(repro_success_rows) if repro_success_rows else None,
        "non_reproducibility_detection_rate": non_repro_detected / len(non_repro_rows) if non_repro_rows else None,
        "decision_accuracy_against_expected": sum(
            r.get("decision") == r.get("expected_outcome") for r in rows
        ) / len(rows) if rows else 0.0,
        "runs": len(rows),
    }
