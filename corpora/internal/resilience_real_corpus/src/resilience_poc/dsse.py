from __future__ import annotations

import base64
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec

DSSE_PAYLOAD_TYPE = "application/vnd.in-toto+json"
DSSE_VERSION = "DSSEv1"


def _b64e(data: bytes) -> str:
    return base64.b64encode(data).decode("ascii")


def _b64d(value: str) -> bytes:
    return base64.b64decode(value.encode("ascii"), validate=True)


def pae(payload_type: str, payload: bytes) -> bytes:
    """DSSE v1 Pre-Authentication Encoding (PAE)."""
    type_b = payload_type.encode("utf-8")
    return (
        DSSE_VERSION.encode("ascii")
        + b" " + str(len(type_b)).encode("ascii") + b" " + type_b
        + b" " + str(len(payload)).encode("ascii") + b" " + payload
    )


def canonical_statement(statement: dict[str, Any]) -> bytes:
    """Stable JSON bytes for the PoC payload; DSSE authenticates these exact bytes."""
    return json.dumps(
        statement, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")


def ensure_ecdsa_p256_keypair(private_path: Path, public_path: Path) -> None:
    if private_path.exists() and public_path.exists():
        return
    private = ec.generate_private_key(ec.SECP256R1())
    private_path.parent.mkdir(parents=True, exist_ok=True)
    private_path.write_bytes(
        private.private_bytes(
            serialization.Encoding.PEM,
            serialization.PrivateFormat.PKCS8,
            serialization.NoEncryption(),
        )
    )
    public_path.write_bytes(
        private.public_key().public_bytes(
            serialization.Encoding.PEM,
            serialization.PublicFormat.SubjectPublicKeyInfo,
        )
    )


def key_id_from_public_key(public_key: ec.EllipticCurvePublicKey) -> str:
    der = public_key.public_bytes(
        serialization.Encoding.DER,
        serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    return hashlib.sha256(der).hexdigest()[:16]


def sign_dsse(
    statement: dict[str, Any],
    private_path: Path,
    *,
    payload_type: str = DSSE_PAYLOAD_TYPE,
) -> dict[str, Any]:
    private = serialization.load_pem_private_key(private_path.read_bytes(), password=None)
    if not isinstance(private, ec.EllipticCurvePrivateKey):
        raise TypeError("DSSE key must be an EC private key")
    payload = canonical_statement(statement)
    signature = private.sign(pae(payload_type, payload), ec.ECDSA(hashes.SHA256()))
    keyid = key_id_from_public_key(private.public_key())
    return {
        "payload": _b64e(payload),
        "payloadType": payload_type,
        "signatures": [{"keyid": keyid, "sig": _b64e(signature)}],
    }


def verify_dsse(
    envelope: dict[str, Any],
    public_path: Path,
    *,
    expected_payload_type: str = DSSE_PAYLOAD_TYPE,
    expected_subject_digest: str | None = None,
) -> tuple[bool, list[str], dict[str, Any] | None]:
    errors: list[str] = []
    if envelope.get("payloadType") != expected_payload_type:
        errors.append("INVALID_D_SSE_PAYLOAD_TYPE")
    payload_text = envelope.get("payload")
    signatures = envelope.get("signatures")
    if not isinstance(payload_text, str):
        errors.append("MISSING_D_SSE_PAYLOAD")
    if not isinstance(signatures, list) or not signatures:
        errors.append("MISSING_D_SSE_SIGNATURE")
    if errors:
        return False, errors, None

    try:
        payload = _b64d(payload_text)
    except Exception:
        return False, ["INVALID_D_SSE_PAYLOAD_ENCODING"], None

    public = serialization.load_pem_public_key(public_path.read_bytes())
    if not isinstance(public, ec.EllipticCurvePublicKey):
        return False, ["INVALID_D_SSE_PUBLIC_KEY"], None

    keyid = key_id_from_public_key(public)
    matching = [s for s in signatures if s.get("keyid") == keyid]
    if not matching:
        return False, ["D_SSE_KEYID_MISMATCH"], None

    sig_ok = False
    for sig_obj in matching:
        try:
            signature = _b64d(sig_obj["sig"])
            public.verify(signature, pae(expected_payload_type, payload), ec.ECDSA(hashes.SHA256()))
            sig_ok = True
            break
        except Exception:
            continue
    if not sig_ok:
        return False, ["D_SSE_SIGNATURE_INVALID"], None

    try:
        statement = json.loads(payload.decode("utf-8"))
    except Exception:
        return False, ["D_SSE_PAYLOAD_NOT_JSON"], None

    if expected_subject_digest is not None:
        expected = expected_subject_digest.removeprefix("sha256:")
        subjects = statement.get("subject") or []
        actual = subjects[0].get("digest", {}).get("sha256") if subjects else None
        if actual != expected:
            errors.append("D_SSE_SUBJECT_DIGEST_MISMATCH")

    return not errors, errors, statement
