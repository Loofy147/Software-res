from __future__ import annotations

import base64
import json
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from .security import canonical_json, sha256_bytes
from .storage import put_json

SLSA_PREDICATE = "https://slsa.dev/provenance/v1"


def build_provenance(patch: dict, builder_id: str = "builder://poc-local") -> tuple[dict, str, str]:
    subject_name = patch["target_repository"]
    patch_digest = sha256_bytes(canonical_json(patch))
    statement = {
        "_type": "https://in-toto.io/Statement/v1",
        "subject": [{"name": subject_name, "digest": {"sha256": patch_digest}}],
        "predicateType": SLSA_PREDICATE,
        "predicate": {
            "buildDefinition": {
                "buildType": "https://example.invalid/software-resilience-poc/build/v0",
                "externalParameters": {"sourceRevision": patch["target_repository"]},
                "internalParameters": {"pocMode": True},
                "resolvedDependencies": [],
            },
            "runDetails": {
                "builder": {"id": builder_id},
                "metadata": {
                    "invocationId": f"inv-{uuid4()}",
                    "startedOn": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
                    "finishedOn": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
                },
                "byproducts": [],
            },
        },
    }
    envelope_payload = base64.b64encode(canonical_json(statement)).decode()
    envelope = {
        "payloadType": "application/vnd.in-toto+json",
        "payload": envelope_payload,
        "signatures": [],
        "statement": statement,
    }
    envelope_id = f"intoto-{uuid4()}"
    provenance_id = f"slsa-{uuid4()}"
    put_json(envelope, envelope_id)
    put_json({"predicateType": SLSA_PREDICATE, "statement": statement}, provenance_id)
    return envelope, envelope_id, provenance_id
