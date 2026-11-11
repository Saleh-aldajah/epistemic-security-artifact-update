"""Canonical reasoning-lineage attestations with Ed25519 signatures."""
from __future__ import annotations

import base64
import copy
import hashlib
import json
from typing import Any, Dict, Tuple

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey
from cryptography.hazmat.primitives import serialization
from jsonschema import Draft202012Validator


def canonical_json(value: Dict[str, Any]) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def artifact_digest(payload: Dict[str, Any]) -> str:
    return "sha256:" + hashlib.sha256(canonical_json(payload)).hexdigest()


def generate_keypair() -> Tuple[Ed25519PrivateKey, Ed25519PublicKey]:
    private = Ed25519PrivateKey.generate()
    return private, private.public_key()


def private_key_from_seed(seed: int, *, domain: str = "czta-benchmark") -> Ed25519PrivateKey:
    """Derive a deterministic Ed25519 test key.

    This helper is only for reproducible synthetic artifacts. Production
    deployments must use protected, independently generated signing keys.
    """
    raw = hashlib.sha256(f"{domain}:{seed}".encode("utf-8")).digest()
    return Ed25519PrivateKey.from_private_bytes(raw)


def public_key_b64(public: Ed25519PublicKey) -> str:
    raw = public.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )
    return base64.b64encode(raw).decode("ascii")


def public_key_from_signer(signer: str) -> Ed25519PublicKey:
    prefix = "did:key:ed25519:"
    if not signer.startswith(prefix):
        raise ValueError("Unsupported signer identifier")
    raw = base64.b64decode(signer[len(prefix):], validate=True)
    return Ed25519PublicKey.from_public_bytes(raw)


def sign_attestation(attestation: Dict[str, Any], private: Ed25519PrivateKey) -> Dict[str, Any]:
    signed = copy.deepcopy(attestation)
    signed.pop("signature", None)
    signature = private.sign(canonical_json(signed))
    signed["signature"] = base64.b64encode(signature).decode("ascii")
    return signed


def verify_attestation(attestation: Dict[str, Any], public: Ed25519PublicKey) -> bool:
    try:
        unsigned = copy.deepcopy(attestation)
        signature = base64.b64decode(unsigned.pop("signature"), validate=True)
        public.verify(signature, canonical_json(unsigned))
        return True
    except Exception:
        return False


def validate_schema(attestation: Dict[str, Any], schema: Dict[str, Any]) -> None:
    Draft202012Validator(schema).validate(attestation)
