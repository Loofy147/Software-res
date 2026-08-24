from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from .provenance import build_provenance
from .security import ensure_keypair, sign_json
from .storage import put_json
from .runtime_paths import KEYS

BASE = Path(__file__).resolve().parents[2]
PRIVATE = KEYS / "poc_ed25519_private.pem"
PUBLIC = KEYS / "poc_ed25519_public.pem"


def collect(patch: dict) -> dict:
    ensure_keypair(PRIVATE, PUBLIC)
    patch = dict(patch)
    unsigned = dict(patch)
    unsigned.pop("integrity_signature", None)
    patch["integrity_signature"] = sign_json(unsigned, PRIVATE)
    put_json(patch, patch["id"])

    _envelope, envelope_id, provenance_id = build_provenance(patch)
    manifest_id = f"evmanifest-{uuid4()}"
    manifest = {
        "id": manifest_id,
        "type": "EvidenceManifest",
        "producer_agent": patch["producer_agent"],
        "risk_tier": patch.get("risk_tier", "low"),
        "generated_patch_ref": patch["id"],
        "source_revision": patch.get("target_repository", "unknown"),
        "intoto_envelope_ref": f"link://in-toto/envelope/{envelope_id}",
        "slsa_provenance_ref": f"link://slsa/provenance/{provenance_id}",
        "ai_evidence": {
            "prompt_snapshot_ref": f"urn:uuid:{patch['id']}",
            "generation_policy_id": patch["agent_metadata"]["generation_policy_id"],
            "agent_confidence": patch["agent_metadata"].get("confidence_score"),
            "target_repository": patch["target_repository"],
        },
        "dependency_lock_ref": "link://locks/fixture-lock",
        "runtime_descriptor": {
            "implementation": "unknown",
            "language": "unknown",
            "version": "unknown",
            "build": {"free_threaded": False, "build_flags": []},
            "gil": {
                "build_supports_free_threading": None,
                "runtime_gil_requested": None,
                "runtime_gil_observed": None,
                "observation_method": "not_observed_at_collection",
            },
            "platform": "linux-x86_64",
        },
        "reproducibility": {
            "level": "NOT_REPRODUCIBLE",
            "artifact_identity": None,
            "comparison": {"same_declared_inputs": False, "same_artifact_identity": False, "independent_rebuilds": False},
        },
        "evidence_payload_ref": "link://artifacts/pending",
        "integrity_signature": "pending",
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }
    unsigned_manifest = dict(manifest)
    unsigned_manifest.pop("integrity_signature", None)
    manifest["integrity_signature"] = sign_json(unsigned_manifest, PRIVATE)
    put_json(manifest, manifest_id)
    return manifest
