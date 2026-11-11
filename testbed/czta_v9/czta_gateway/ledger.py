"""Hash-chained, Ed25519-signed reasoning-lineage ledger for arm A2."""
from __future__ import annotations

import hashlib
import threading
import time
from typing import Any

from czta_ref.rla import canonical_json, private_key_from_seed, public_key_b64, sign_attestation, verify_attestation


class SealedLedger:
    def __init__(self, seed: int):
        self.private = private_key_from_seed(seed, domain="czta-v9-replacement-ledger")
        self.public = self.private.public_key()
        self.signer = "did:key:ed25519:" + public_key_b64(self.public)
        self.records: list[dict[str, Any]] = []
        self.prev = "0" * 64
        self.lock = threading.Lock()

    def append(self, record: dict[str, Any]) -> dict[str, Any]:
        with self.lock:
            unsigned = {
                "seq": len(self.records),
                "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "prev": self.prev,
                "record": record,
            }
            digest = hashlib.sha256(canonical_json(unsigned)).hexdigest()
            unsigned["sha256"] = digest
            unsigned["signer"] = self.signer
            signed = sign_attestation(unsigned, self.private)
            self.records.append(signed)
            self.prev = digest
            return signed

    def verify(self) -> bool:
        with self.lock:
            prev = "0" * 64
            for expected_seq, record in enumerate(self.records):
                if record.get("seq") != expected_seq or record.get("prev") != prev:
                    return False
                unsigned = {k: v for k, v in record.items() if k not in ("signature", "signer", "sha256")}
                digest = hashlib.sha256(canonical_json(unsigned)).hexdigest()
                if digest != record.get("sha256") or not verify_attestation(record, self.public):
                    return False
                prev = digest
            return True
