"""Security and compatibility checks for the replacement testbed (offline only)."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

from fastapi import HTTPException

from .offline_fixtures import JWKS_PATH, ensure_fixtures, make_token

ensure_fixtures()
os.environ["CZTA_JWKS_JSON"] = JWKS_PATH.read_text()
os.environ["CZTA_ARM"] = "A2"
os.environ["CZTA_ISSUER"] = "http://127.0.0.1:8080/realms/czta"
os.environ["CZTA_AUDIENCE"] = "czta-gateway"

from czta_gateway.auth import verify_token  # noqa: E402
from czta_gateway.config import code_hashes  # noqa: E402
from czta_gateway.fixtures import benchmark_payload  # noqa: E402
from czta_gateway.ledger import SealedLedger  # noqa: E402
from czta_gateway.monitor import monitor_from_payload  # noqa: E402

V8_HASHES = {
    "__init__.py": "f7e2ddb69d6137a0c7fb71c5f2500e5e78474a684bbcf1561c6cd1fc9545307d",
    "benchmark.py": "cd19cc2f2407e7a614923532a405b84765e1988af5b66661a3b9cfe639fbd51a",
    "governance.py": "243c833eed47e66e33735a9e64977bac90bd30a3afb6a74e77ce542da07549e4",
    "identity.py": "8805af35c80b6a8e0bfb34da0a2d4820bf2568d4dcc59900b53f47c5adb32de2",
    "localization.py": "89835a2228878ce3e82552b4169aec19718eeef2134a347a97b160766b819a64",
    "mcp_gateway.py": "eeda25f25526b57015c528e3ea31d8c073e968f317f4dcd3ef7f08d210af1bc6",
    "pipeline.py": "a21dc18a7c60b5c2a5b1683fee09e29f397482f18d5c419b44cfa493b642f28c",
    "rla.py": "b7b42e3b08e10e584e0120e280907f73d852a1aac6059c8217cc71d12c15d3df",
    "scenario.py": "73daff757eb2434e7c41729c630e76c21a844046fc223f33067bc66a85d2f169",
    "trust_analytics.py": "ef4435730285848357f58d1263ac0bdd7ce9195ad93e848c8fc114fbe8879f25",
}
ROOT = Path(__file__).resolve().parents[1]


def test_monitor_arms():
    valid = benchmark_payload("0")
    result = monitor_from_payload(valid, "A2").admit_action("delete", ["b_user"], valid["evidence_weights"], {"file_id": "0"})
    assert result.verdict.name == "ADMIT"
    attack = benchmark_payload("13")
    a1 = monitor_from_payload(attack, "A1").admit_action("delete", ["b_user"], attack["evidence_weights"], {"file_id": "13"})
    assert a1.verdict.name == "ADMIT"  # I4 is intentionally vacuous on A1
    a2 = monitor_from_payload(attack, "A2").admit_action("delete", ["b_user"], attack["evidence_weights"], {"file_id": "13"})
    assert a2.verdict.name == "BLOCK" and a2.invariant == "I4"


def test_ledger_and_tamper_detection():
    ledger = SealedLedger(42)
    ledger.append({"request_id": "one", "decision": {"admit": True}})
    assert ledger.verify()
    ledger.records[0]["record"]["decision"]["admit"] = False
    assert not ledger.verify()


def test_rs256_and_claims():
    claims = verify_token(make_token())
    assert claims["sub"] == "offline-benchmark-agent"
    for kwargs in ({"audience": "wrong"}, {"expires_in": -3600}, {"not_before_offset": 3600}):
        try:
            verify_token(make_token(**kwargs))
            raise AssertionError(f"invalid token accepted: {kwargs}")
        except HTTPException as exc:
            assert exc.status_code == 401
    try:
        verify_token(make_token(scope="read:only"))
        raise AssertionError("insufficient scope accepted")
    except HTTPException as exc:
        assert exc.status_code == 403


def test_code_identity():
    hashes = code_hashes()
    assert "czta_gateway/app.py" in hashes and "czta_ref/rla.py" in hashes
    assert len(hashes["czta_gateway/app.py"]) == 64


def test_v8_bytes_preserved():
    for name, expected in V8_HASHES.items():
        actual = hashlib.sha256((ROOT / "czta_ref" / name).read_bytes()).hexdigest()
        assert actual == expected, name


def main():
    tests = [test_monitor_arms, test_ledger_and_tamper_detection, test_rs256_and_claims,
             test_code_identity, test_v8_bytes_preserved]
    for test in tests:
        test()
        print("PASS", test.__name__)
    print(f"{len(tests)}/{len(tests)} offline tests passed")


if __name__ == "__main__":
    main()
