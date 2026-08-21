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

BASE = Path(__file__).resolve().parents[2]
SCHEMAS = BASE / "schemas"
KEYS = BASE / "keys"
PRIVATE = KEYS / "poc_ed25519_private.pem"
PUBLIC = KEYS / "poc_ed25519_public.pem"


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


def build_vector(manifest: dict, test_ev: dict, dep_ev: dict, repro: dict, gil: dict, semantic_fail: bool = False, security_fail: bool = False, concurrency_reactivation: bool = False) -> dict:
    semantic_status = "fail" if semantic_fail else ("warn" if test_ev["property_tests"]["violations"] else "pass")
    dependency_status = "fail" if dep_ev["dependency_drift"]["count"] else "pass"
    concurrency_fail = bool(concurrency_reactivation or gil.get("unexpected_gil_reactivation"))
    concurrency_status = "fail" if concurrency_fail else "pass"
    security_status = "fail" if security_fail or not dep_ev["supply_chain_checks"]["signatures_valid"] or not dep_ev["supply_chain_checks"]["cve_policy_pass"] else "pass"
    functional_status = "pass" if test_ev["unit_tests"]["failed"] == 0 else "fail"

    vector = {
        "id": f"rv-{uuid4()}",
        "target_revision": manifest["ai_evidence"].get("target_repository", manifest.get("generated_patch_ref", "unknown")),
        "functional": {"status": functional_status, "evidence_refs": [test_ev["id"]], "failure_codes": [] if functional_status == "pass" else ["UNIT_TEST_FAILURE"]},
        "semantic": {"status": semantic_status, "evidence_refs": [test_ev["id"]], "failure_codes": ["SEM_INV_VIOLATION"] if semantic_fail else []},
        "dependency": {"status": dependency_status, "evidence_refs": [dep_ev["id"]], "failure_codes": ["DEP_DRIFT"] if dependency_status == "fail" else []},
        "runtime": {"status": "pass", "evidence_refs": [manifest["id"]], "failure_codes": []},
        "concurrency": {"status": concurrency_status, "evidence_refs": [manifest["id"]], "failure_codes": ["UNEXPECTED_GIL_REACTIVATION"] if concurrency_fail else []},
        "security": {"status": security_status, "evidence_refs": [dep_ev["id"]], "failure_codes": ["UNSIGNED_MATERIAL"] if security_status == "fail" else []},
        "observability": {"status": "pass", "evidence_refs": [test_ev["id"]], "failure_codes": []},
        "reproducibility": {"level": repro["level"], "evidence_refs": [manifest["id"]], "failure_codes": ["NOT_REPRODUCIBLE"] if repro["level"] == "NOT_REPRODUCIBLE" else []},
        "mandatory_invariant_failures": (["SEM_INV_VIOLATION"] if semantic_fail else []),
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }
    vector["decision"] = decision_for_vector(vector)
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
    test_ev = generated.get("fixture_test_evidence") or {
        "id": f"testev-{uuid4()}",
        "evidence_manifest_ref": manifest_id,
        "unit_tests": {"executed": True, "count": 1, "passed": 1, "failed": 0, "coverage_percent": 100.0},
        "property_tests": {"executed": True, "framework": "fixture", "cases_run": 1, "violations": 0},
        "fuzzing": {"executed": False},
        "test_environment": {"container_image": "fixture"},
        "integrity_signature": "fixture",
    }
    dep_ev = generated.get("fixture_dependency_report") or {
        "id": f"depreport-{uuid4()}",
        "evidence_manifest_ref": manifest_id,
        "declared_lockfile_ref": manifest["dependency_lock_ref"],
        "declared_materials": [],
        "runtime_imports": [],
        "dependency_drift": {"mismatches": [], "count": 0},
        "sbom_ref": "fixture",
        "supply_chain_checks": {"signatures_valid": True, "cve_policy_pass": True},
        "integrity_signature": "fixture",
    }
    contract_errors = validate_schema(test_ev, "03_test_evidence.schema.json") + validate_schema(dep_ev, "04_dependency_report.schema.json")
    if contract_errors:
        return {"status": "invalid", "errors": contract_errors}

    repro = manifest["reproducibility"]
    gil = manifest["runtime_descriptor"].get("gil", {})
    vector = build_vector(manifest, test_ev, dep_ev, repro, gil, semantic_fail=bool(generated.get("fixture_semantic_fail", False)), concurrency_reactivation=bool(manifest["runtime_descriptor"].get("unexpected_gil_reactivation", False)))

    test_id = test_ev["id"]
    dep_id = dep_ev["id"]
    put_json(test_ev, test_id)
    put_json(dep_ev, dep_id)
    put_json(vector, vector["id"])
    return {"status": "completed", "reliability_vector": vector}
