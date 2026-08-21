from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PREDICATE_TYPE = "https://slsa.dev/verification_summary/v1"
STATEMENT_TYPE = "https://in-toto.io/Statement/v1"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_json(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()


def build_vsa(
    *,
    artifact_name: str,
    artifact_digest: str,
    resource_uri: str,
    verifier_id: str,
    verifier_version: dict[str, str],
    policy_uri: str,
    policy_digest: str,
    input_attestations: list[dict[str, Any]],
    verification_result: str,
    verified_levels: list[str],
    dependency_levels: dict[str, int] | None = None,
    slsa_version: str = "1.2",
) -> dict[str, Any]:
    if verification_result not in {"PASSED", "FAILED"}:
        raise ValueError("verification_result must be PASSED or FAILED")
    if not artifact_digest.startswith("sha256:"):
        raise ValueError("artifact_digest must be sha256:<hex>")
    if not policy_digest.startswith("sha256:"):
        raise ValueError("policy_digest must be sha256:<hex>")
    if verification_result == "FAILED" and verified_levels != ["FAILED"]:
        raise ValueError("FAILED VSA must use verified_levels=['FAILED']")

    predicate = {
        "verifier": {
            "id": verifier_id,
            "version": verifier_version,
        },
        "timeVerified": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "resourceUri": resource_uri,
        "policy": {
            "uri": policy_uri,
            "digest": {"sha256": policy_digest.split(":", 1)[1]},
        },
        "inputAttestations": input_attestations,
        "verificationResult": verification_result,
        "verifiedLevels": verified_levels,
        "slsaVersion": slsa_version,
    }
    if dependency_levels is not None:
        predicate["dependencyLevels"] = dependency_levels

    return {
        "_type": STATEMENT_TYPE,
        "subject": [{"name": artifact_name, "digest": {"sha256": artifact_digest.split(":", 1)[1]}}],
        "predicateType": PREDICATE_TYPE,
        "predicate": predicate,
    }


def validate_vsa(vsa: dict[str, Any], *, expected_artifact_digest: str | None = None,
                 expected_resource_uri: str | None = None) -> tuple[bool, list[str]]:
    errors: list[str] = []
    if vsa.get("_type") != STATEMENT_TYPE:
        errors.append("INVALID_STATEMENT_TYPE")
    if vsa.get("predicateType") != PREDICATE_TYPE:
        errors.append("INVALID_VSA_PREDICATE_TYPE")

    subjects = vsa.get("subject")
    if not isinstance(subjects, list) or len(subjects) != 1:
        errors.append("INVALID_SUBJECT")
    else:
        digest = subjects[0].get("digest", {}).get("sha256")
        if not isinstance(digest, str) or len(digest) != 64:
            errors.append("INVALID_SUBJECT_DIGEST")
        elif expected_artifact_digest and digest != expected_artifact_digest.removeprefix("sha256:"):
            errors.append("SUBJECT_DIGEST_MISMATCH")

    predicate = vsa.get("predicate")
    if not isinstance(predicate, dict):
        errors.append("MISSING_PREDICATE")
        return False, errors

    verifier = predicate.get("verifier")
    if not isinstance(verifier, dict) or not verifier.get("id"):
        errors.append("MISSING_VERIFIER")

    policy = predicate.get("policy")
    if not isinstance(policy, dict) or not policy.get("uri"):
        errors.append("MISSING_POLICY")
    elif not policy.get("digest", {}).get("sha256"):
        errors.append("MISSING_POLICY_DIGEST")

    result = predicate.get("verificationResult")
    if result not in {"PASSED", "FAILED"}:
        errors.append("INVALID_VERIFICATION_RESULT")

    levels = predicate.get("verifiedLevels")
    if not isinstance(levels, list) or not levels:
        errors.append("MISSING_VERIFIED_LEVELS")
    elif result == "FAILED" and levels != ["FAILED"]:
        errors.append("FAILED_VSA_LEVEL_MISMATCH")

    if expected_resource_uri is not None and predicate.get("resourceUri") != expected_resource_uri:
        errors.append("RESOURCE_URI_MISMATCH")

    return not errors, errors


def write_vsa(vsa: dict[str, Any], path: str | Path) -> None:
    Path(path).write_text(json.dumps(vsa, indent=2, sort_keys=True) + "\n")
