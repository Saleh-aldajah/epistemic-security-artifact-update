"""Strict RS256/JWKS validation using cryptography only (no JWT bypass)."""
from __future__ import annotations

import base64
import json
import time
from functools import lru_cache

import httpx
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from .config import settings

bearer = HTTPBearer(auto_error=False)


def b64url_decode(value: str) -> bytes:
    return base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))


def b64url_uint(value: str) -> int:
    return int.from_bytes(b64url_decode(value), "big")


@lru_cache(maxsize=4)
def _jwks_document() -> dict:
    cfg = settings()
    if cfg.jwks_json:
        return json.loads(cfg.jwks_json)
    if not cfg.jwks_url:
        raise RuntimeError("Set CZTA_JWKS_URL or the offline-test CZTA_JWKS_JSON")
    response = httpx.get(cfg.jwks_url, timeout=10.0)
    response.raise_for_status()
    return response.json()


def verify_token(token: str) -> dict:
    cfg = settings()
    try:
        parts = token.split(".")
        if len(parts) != 3:
            raise ValueError("JWT must have three segments")
        header = json.loads(b64url_decode(parts[0]))
        claims = json.loads(b64url_decode(parts[1]))
        signature = b64url_decode(parts[2])
        if header.get("alg") != "RS256":
            raise ValueError("Only RS256 is accepted")
        keys = [k for k in _jwks_document().get("keys", [])
                if k.get("kid") == header.get("kid") and k.get("kty") == "RSA"]
        if len(keys) != 1:
            raise ValueError("Unknown or ambiguous kid")
        jwk = keys[0]
        public_key = rsa.RSAPublicNumbers(b64url_uint(jwk["e"]), b64url_uint(jwk["n"])).public_key()
        public_key.verify(signature, f"{parts[0]}.{parts[1]}".encode("ascii"),
                          padding.PKCS1v15(), hashes.SHA256())
        now = time.time()
        if claims.get("iss") != cfg.issuer:
            raise ValueError("Issuer mismatch")
        audiences = claims.get("aud")
        audiences = [audiences] if isinstance(audiences, str) else audiences or []
        if cfg.audience not in audiences:
            raise ValueError("Audience mismatch")
        if not isinstance(claims.get("exp"), (int, float)) or not isinstance(claims.get("iat"), (int, float)):
            raise ValueError("exp and iat are required numeric claims")
        if now > claims["exp"] + 30:
            raise ValueError("Token expired")
        if claims["iat"] > now + 30 or claims.get("nbf", claims["iat"]) > now + 30:
            raise ValueError("Token not yet valid")
    except Exception as exc:
        raise HTTPException(status_code=401, detail="invalid_token") from exc
    scopes = set(claims.get("scope", "").split())
    scopes |= set(claims.get("scp", []))
    if "tool:execute" not in scopes:
        raise HTTPException(status_code=403, detail="insufficient_scope")
    return claims


async def require_token(credentials: HTTPAuthorizationCredentials | None = Depends(bearer)) -> dict:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(status_code=401, detail="missing_bearer_token")
    return verify_token(credentials.credentials)
