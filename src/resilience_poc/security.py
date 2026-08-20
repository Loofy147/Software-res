from __future__ import annotations

import base64
import hashlib
import json
from pathlib import Path

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey


def canonical_json(data: object) -> bytes:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def ensure_keypair(private_path: Path, public_path: Path) -> None:
    if private_path.exists() and public_path.exists():
        return
    private = Ed25519PrivateKey.generate()
    private_path.parent.mkdir(parents=True, exist_ok=True)
    private_path.write_bytes(private.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption(),
    ))
    public_path.write_bytes(private.public_key().public_bytes(
        serialization.Encoding.PEM,
        serialization.PublicFormat.SubjectPublicKeyInfo,
    ))


def sign_json(data: dict, private_path: Path) -> str:
    private = serialization.load_pem_private_key(private_path.read_bytes(), password=None)
    signature = private.sign(canonical_json(data))
    return "ed25519:" + base64.b64encode(signature).decode()


def verify_json(data: dict, signature_text: str, public_path: Path) -> bool:
    if not signature_text.startswith("ed25519:"):
        return False
    signature = base64.b64decode(signature_text.split(":", 1)[1])
    public = serialization.load_pem_public_key(public_path.read_bytes())
    try:
        public.verify(signature, canonical_json(data))
        return True
    except Exception:
        return False
