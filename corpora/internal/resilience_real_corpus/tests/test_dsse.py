import json
from pathlib import Path

from resilience_poc.dsse import (
    DSSE_PAYLOAD_TYPE,
    ensure_ecdsa_p256_keypair,
    sign_dsse,
    verify_dsse,
)


def test_dsse_sign_verify(tmp_path: Path):
    priv = tmp_path / "dsse-private.pem"
    pub = tmp_path / "dsse-public.pem"
    ensure_ecdsa_p256_keypair(priv, pub)
    statement = {
        "_type": "https://in-toto.io/Statement/v1",
        "subject": [{"name": "artifact", "digest": {"sha256": "a" * 64}}],
        "predicateType": "https://slsa.dev/verification_summary/v1",
        "predicate": {"verificationResult": "PASSED"},
    }
    env = sign_dsse(statement, priv)
    ok, errors, decoded = verify_dsse(
        env, pub, expected_subject_digest="sha256:" + "a" * 64
    )
    assert ok, errors
    assert decoded == statement
    assert env["payloadType"] == DSSE_PAYLOAD_TYPE


def test_dsse_rejects_tampered_payload(tmp_path: Path):
    priv = tmp_path / "dsse-private.pem"
    pub = tmp_path / "dsse-public.pem"
    ensure_ecdsa_p256_keypair(priv, pub)
    statement = {"_type": "https://in-toto.io/Statement/v1", "subject": []}
    env = sign_dsse(statement, priv)
    payload = json.loads(__import__("base64").b64decode(env["payload"]).decode())
    payload["subject"] = [{"name": "tampered", "digest": {"sha256": "b" * 64}}]
    env["payload"] = __import__("base64").b64encode(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    ).decode()
    ok, errors, _ = verify_dsse(env, pub)
    assert not ok
    assert "D_SSE_SIGNATURE_INVALID" in errors
