"""Offline-only RSA/JWKS fixtures; never use these keys in production."""
from __future__ import annotations

import base64
import json
import time
from pathlib import Path

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa

ROOT = Path(__file__).resolve().parent
KEY_PATH = ROOT / "offline_test_rsa_private.pem"
JWKS_PATH = ROOT / "offline_test_jwks.json"
KID = "offline-test-key-1"


def b64url(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).rstrip(b"=").decode("ascii")


def _uint(value: int, length: int) -> str:
    return b64url(value.to_bytes(length, "big"))


def ensure_fixtures():
    if not KEY_PATH.exists():
        key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        KEY_PATH.write_bytes(key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        ))
    private = serialization.load_pem_private_key(KEY_PATH.read_bytes(), password=None)
    numbers = private.public_key().public_numbers()
    n = _uint(numbers.n, 256)
    e = _uint(numbers.e, 3)
    document = {"keys": [{"kty": "RSA", "use": "sig", "alg": "RS256", "kid": KID, "n": n, "e": e}]}
    JWKS_PATH.write_text(json.dumps(document, indent=2) + "\n")
    return private, document


def make_token(scope="tool:execute", issuer="http://127.0.0.1:8080/realms/czta",
               audience="czta-gateway", expires_in=3600, not_before_offset=0):
    private, _ = ensure_fixtures()
    now = int(time.time())
    header = {"alg": "RS256", "typ": "JWT", "kid": KID}
    claims = {
        "sub": "offline-benchmark-agent",
        "iss": issuer,
        "aud": audience,
        "iat": now + not_before_offset,
        "nbf": now + not_before_offset,
        "exp": now + expires_in,
        "scope": scope,
        "azp": "czta-benchmark-client",
    }
    first = b64url(json.dumps(header, separators=(",", ":")).encode())
    second = b64url(json.dumps(claims, separators=(",", ":")).encode())
    signature = private.sign(f"{first}.{second}".encode("ascii"), padding.PKCS1v15(), hashes.SHA256())
    return f"{first}.{second}.{b64url(signature)}"
