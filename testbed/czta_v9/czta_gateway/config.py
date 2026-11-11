"""Environment and code-identity binding for the replacement testbed."""
from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARMS = ("A0", "A1", "A2")


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def code_hashes() -> dict[str, str]:
    files = [ROOT / "run_protocol.py", ROOT / "combine_results.py", ROOT / "merge_restart_results.py",
             ROOT / "run_restarts.sh", ROOT / "run_offline_smoke.sh"]
    files += sorted((ROOT / "czta_gateway").glob("*.py"))
    files += sorted((ROOT / "czta_ref").glob("*.py"))
    return {str(p.relative_to(ROOT)): _sha256(p) for p in files if p.exists()}


def code_manifest_hash() -> str:
    material = json.dumps(code_hashes(), sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(material).hexdigest()


@dataclass(frozen=True)
class Settings:
    arm: str
    issuer: str
    audience: str
    jwks_url: str | None
    jwks_json: str | None
    upstream: str
    ledger_seed: int


def settings() -> Settings:
    arm = os.environ.get("CZTA_ARM", "A2").upper()
    if arm not in ARMS:
        raise RuntimeError(f"CZTA_ARM must be one of {ARMS}, got {arm!r}")
    return Settings(
        arm=arm,
        issuer=os.environ.get("CZTA_ISSUER", "http://127.0.0.1:8080/realms/czta"),
        audience=os.environ.get("CZTA_AUDIENCE", "czta-gateway"),
        jwks_url=os.environ.get("CZTA_JWKS_URL"),
        jwks_json=os.environ.get("CZTA_JWKS_JSON"),
        upstream=os.environ.get("CZTA_UPSTREAM", "http://127.0.0.1:9001/v1/execute"),
        ledger_seed=int(os.environ.get("CZTA_LEDGER_SEED", "20260814")),
    )
