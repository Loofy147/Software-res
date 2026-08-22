from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from jsonschema import Draft202012Validator, FormatChecker

from .models import decision_for_vector
from .provenance import SLSA_PREDICATE
from .repro import assess_reproducibility
from .security import sign_json, verify_json
from .storage import get_json, put_json
from .vsa import build_vsa, sha256_bytes, canonical_json
from .dsse import ensure_ecdsa_p256_keypair, sign_dsse

BASE = Path(__file__).resolve().parents[2]
SCHEMAS = BASE / "schemas"
KEYS = BASE / "keys"
PRIVATE = KEYS / "poc_ed25519_private.pem"
PUBLIC = KEYS / "poc_ed25519_public.pem"
DSSE_PRIVATE = KEYS / "poc_dsse_p256_private.pem"
DSSE_PUBLIC = KEYS / "poc_dsse_p256_public.pem"


def load_schema(name: str) -> dict:
    return json.loads((SCHEMAS / name).read_text())


def validate_schema(obj: dict, name: str) -> list[str]:
    validator = Draft202012Validator(load_schema(name), format_checker=FormatChecker())
    return [e.message for e in validator.iter_errors(obj)]


def validate_provenance(envelope: dict) -> list[str]:
    errors: list[str] = []
    statement = envelope.get("statement")
    if not isinstance(statement, dict):
        return ["missing in-toto statement"]
    if statement.get("_type") != "https://in-toto.io/Statement/v1":
        errors.append("invalid in-toto statement type")
    if statement.get("predicateType") != SLSA_PREDICATE:
        errors.append("invalid SLSA provenance predicate type")
    if not statement.get("subject"):
        errors.append("missing provenance subject")
    predicate = statement.get("predicate", {})
    if not predicate.get("buildDefinition") or not predicate.get("runDetails"):
        errors.append("incomplete SLSA provenance predicate")
    return errors


def reconcile_dependencies(declared: list[dict[str, Any]], runtime: list[dict[str, Any]]) -> dict[str, Any]:
    declared_pkgs = {item.get("uri", "").split("@", 1)[0] for item in declared}
    runtime_pkgs = {item.get("module", "") for item in runtime}
    # PoC normalization: module names are compared against package resource suffixes.
    declared_names = {x.removeprefix("pkg:pypi/") for x in declared_pkgs}
    missing = sorted(runtime_pkgs - declared_names)
    return {"mismatches": [{"type": "undeclared_runtime_import", "module": m} for m in missing], "count": len(missing)}


def build_vector(manifest: dict, test_ev: dict, dep_ev: dict, repro: dict, gil: dict, semantic_fail: bool = False, security_fail: bool = False, concurrency_reactivation: bool = False, runtime_evidence: dict | None = None, observability_evidence: dict | None = None) -> dict:
    semantic_status = "fail" if semantic_fail else ("warn" if test_ev["property_tests"]["violations"] else "pass")
    dependency_status = "fail" if dep_ev["dependency_drift"]["count"] else "pass"
    concurrency_fail = bool(concurrency_reactivation or gil.get("unexpected_gil_reactivation"))
    concurrency_status = "fail" if concurrency_fail else ("pass" if gil.get("runtime_gil_observed") is not None else "unknown")
    supply_checks = dep_ev.get("supply_chain_checks", {})
    security_checks_executed = supply_checks.get("executed") is True
    security_status = "unknown"
    if security_fail or (security_checks_executed and (not supply_checks.get("signatures_valid") or not supply_checks.get("cve_policy_pass"))):
        security_status = "fail"
    elif security_checks_executed:
        security_status = "pass"

    unit = test_ev.get("unit_tests", {})
    tests_executed = unit.get("executed") is True and int(unit.get("count", 0)) > 0
    if not tests_executed:
        functional_status = "unknown"
    else:
        functional_status = "pass" if unit.get("failed", 0) == 0 else "fail"

    runtime_ok = isinstance(runtime_evidence, dict) and runtime_evidence.get("executed") is True and runtime_evidence.get("status") == "pass"
    observability_ok = isinstance(observability_evidence, dict) and observability_evidence.get("executed") is True

    vector = {
        "id": f"rv-{uuid4()}",
        "target_revision": manifest.get("source_revision", manifest.get("ai_evidence", {}).get("target_repository", manifest.get("generated_patch_ref", "unknown"))),
        "functional": {"status": functional_status, "evidence_refs": [test_ev["id"]], "failure_codes": [] if functional_status == "pass" else ["UNIT_TEST_FAILURE"]},
        "semantic": {"status": semantic_status, "evidence_refs": [test_ev["id"]], "failure_codes": ["SEM_INV_VIOLATION"] if semantic_fail else []},
        "dependency": {"status": dependency_status, "evidence_refs": [dep_ev["id"]], "failure_codes": ["DEP_DRIFT"] if dependency_status == "fail" else []},
        "runtime": {"status": "pass" if runtime_ok else "unknown", "evidence_refs": [manifest["id"]], "failure_codes": [] if runtime_ok else ["RUNTIME_EVIDENCE_MISSING"]},
        "concurrency": {"status": concurrency_status, "evidence_refs": [manifest["id"]], "failure_codes": ["UNEXPECTED_GIL_REACTIVATION"] if concurrency_fail else []},
        "security": {"status": security_status, "evidence_refs": [dep_ev["id"]], "failure_codes": ["UNSIGNED_MATERIAL"] if security_status == "fail" else []},
        "observability": {"status": "pass" if observability_ok else "unknown", "evidence_refs": [test_ev["id"]], "failure_codes": [] if observability_ok else ["OBSERVABILITY_EVIDENCE_MISSING"]},
        "reproducibility": {"level": repro["level"], "evidence_refs": [manifest["id"]], "failure_codes": ["NOT_REPRODUCIBLE"] if repro["level"] == "NOT_REPRODUCIBLE" else []},
        "mandatory_invariant_failures": (["SEM_INV_VIOLATION"] if semantic_fail else []),
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }
    vector["decision"] = decision_for_vector(vector)

    # Phase B VSA: the PoC intentionally makes no SLSA level claim.
    # AUTO_MERGE maps to PASSED; REVIEW/REJECT map to FAILED until policy verification completes.
    unsigned_patch = dict(manifest)
    unsigned_patch.pop("integrity_signature", None)
    artifact_digest = "sha256:" + sha256_bytes(canonical_json(unsigned_patch))
    vsa_result = "PASSED" if vector["decision"]["outcome"] == "AUTO_MERGE" else "FAILED"
    vsa_levels = ["SLSA_BUILD_LEVEL_UNEVALUATED"] if vsa_result == "PASSED" else ["FAILED"]
    vsa = build_vsa(
        artifact_name=manifest["generated_patch_ref"],
        artifact_digest=artifact_digest,
        resource_uri=f"urn:resilience:artifact:{manifest['generated_patch_ref']}",
        verifier_id="urn:resilience-poc:validator",
        verifier_version={"software-resilience-poc": "0.2.0"},
        policy_uri="urn:resilience-poc:policy:v1",
        policy_digest="sha256:" + "0" * 64,
        input_attestations=[
            {"uri": manifest["slsa_provenance_ref"], "digest": {"sha256": manifest["slsa_provenance_ref"].split(":")[-1]}}
        ],
        verification_result=vsa_result,
        verified_levels=vsa_levels,
        slsa_version="1.2",
    )
    vsa_id = f"vsa-{uuid4()}"
    vsa["id"] = vsa_id
    vsa["integrity_signature"] = sign_json(vsa, PRIVATE)
    put_json(vsa, vsa_id)

    # SLSA/in-toto recommended envelope: DSSE with P-256/SHA-256.
    # The key is generated lazily for the PoC and is intentionally not a production trust root.
    ensure_ecdsa_p256_keypair(DSSE_PRIVATE, DSSE_PUBLIC)
    dsse_id = f"vsa-dsse-{uuid4()}"
    dsse_envelope = sign_dsse(vsa, DSSE_PRIVATE)
    dsse_envelope["id"] = dsse_id
    dsse_envelope["attestation_type"] = "https://slsa.dev/verification_summary/v1"
    put_json(dsse_envelope, dsse_id)

    vector["vsa_ref"] = f"urn:uuid:{vsa_id}"
    vector["vsa_dsse_ref"] = f"urn:uuid:{dsse_id}"
    vector["integrity_signature"] = sign_json(vector, PRIVATE)
    return vector


def validate_manifest(manifest_id: str) -> dict[str, Any]:
    manifest = get_json(manifest_id)
    errors = validate_schema(manifest, "02_evidence_manifest.schema.json")
    envelope_id = manifest["intoto_envelope_ref"].rsplit("/", 1)[-1].split(":")[-1]
    # PoC stores direct IDs in final segment in refs; accept direct local refs too.
    envelope = get_json(envelope_id)
    errors.extend(validate_provenance(envelope))
    if errors:
        return {"status": "invalid", "errors": errors}

    generated = get_json(manifest["generated_patch_ref"])
    unsigned_manifest = dict(manifest)
    manifest_signature = unsigned_manifest.pop("integrity_signature", None)
    if not manifest_signature or not PUBLIC.exists() or not verify_json(unsigned_manifest, manifest_signature, PUBLIC):
        return {"status": "invalid", "errors": ["manifest integrity signature verification failed"]}
    unsigned_patch = dict(generated)
    patch_signature = unsigned_patch.pop("integrity_signature", None)
    if not patch_signature or not PUBLIC.exists() or not verify_json(unsigned_patch, patch_signature, PUBLIC):
        return {"status": "invalid", "errors": ["generated patch integrity signature verification failed"]}
    test_ev = generated.get("fixture_test_evidence")
    dep_ev = generated.get("fixture_dependency_report")
    if test_ev is None or dep_ev is None:
        return {
            "status": "review",
            "errors": ["MISSING_VERIFICATION_EVIDENCE"],
            "reliability_vector": {
                "decision": {"outcome": "REVIEW", "rule": "mandatory_verification_evidence_missing"}
            },
        }
    contract_errors = validate_schema(test_ev, "03_test_evidence.schema.json") + validate_schema(dep_ev, "04_dependency_report.schema.json")
    if contract_errors:
        return {"status": "invalid", "errors": contract_errors}

    repro = manifest["reproducibility"]
    gil = manifest["runtime_descriptor"].get("gil", {})
    vector = build_vector(
        manifest, test_ev, dep_ev, repro, gil,
        semantic_fail=bool(generated.get("fixture_semantic_fail", False)),
        concurrency_reactivation=bool(manifest["runtime_descriptor"].get("unexpected_gil_reactivation", False)),
        runtime_evidence=generated.get("fixture_runtime_evidence"),
        observability_evidence=generated.get("fixture_observability_evidence"),
    )

    test_id = test_ev["id"]
    dep_id = dep_ev["id"]
    put_json(test_ev, test_id)
    put_json(dep_ev, dep_id)
    put_json(vector, vector["id"])
    return {"status": "completed", "reliability_vector": vector}
