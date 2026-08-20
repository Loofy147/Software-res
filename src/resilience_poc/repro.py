from __future__ import annotations

from typing import Any


def assess_reproducibility(build_a: dict[str, Any], build_b: dict[str, Any], independent: bool = True) -> dict[str, Any]:
    same_inputs = build_a.get("declared_inputs_digest") == build_b.get("declared_inputs_digest")
    same_artifact = build_a.get("artifact_digest") == build_b.get("artifact_digest")
    artifact_identity = build_a.get("artifact_digest") if same_artifact else None

    if same_inputs and same_artifact and independent:
        level = "VERIFIED_REPRODUCIBLE"
    elif same_inputs and same_artifact:
        level = "REPRODUCIBLE"
    else:
        level = "NOT_REPRODUCIBLE"

    return {
        "level": level,
        "artifact_identity": artifact_identity,
        "comparison": {
            "same_declared_inputs": same_inputs,
            "same_artifact_identity": same_artifact,
            "independent_rebuilds": independent,
        },
    }
