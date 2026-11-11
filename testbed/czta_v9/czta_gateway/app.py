"""Replacement CZTA testbed: A0 passthrough, A1 monitor, A2 monitor+sealed ledger."""
from __future__ import annotations

from contextlib import asynccontextmanager
import json

import httpx
from fastapi import Depends, FastAPI, HTTPException, Request

from czta_ref.rla import sign_attestation, verify_attestation

from .auth import require_token
from .config import code_hashes, code_manifest_hash, settings
from .ledger import SealedLedger
from .monitor import monitor_from_payload


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.http = httpx.AsyncClient(timeout=httpx.Timeout(30.0))
    yield
    await app.state.http.aclose()


def create_app() -> FastAPI:
    cfg = settings()
    app = FastAPI(title="CZTA v9 replacement testbed", lifespan=lifespan)
    app.state.cfg = cfg
    app.state.ledger = SealedLedger(cfg.ledger_seed) if cfg.arm == "A2" else None

    @app.get("/health")
    async def health():
        return {"ok": True, "arm": cfg.arm}

    @app.get("/env")
    async def env():
        return {
            "implementation": "v9-replacement-2",
            "arm": cfg.arm,
            "arm_semantics": {
                "A0": "authorization + upstream only",
                "A1": "I1-I3 monitor (empty beta), no ledger",
                "A2": "I1-I4 monitor + sealed Ed25519 ledger",
            }[cfg.arm],
            "code_manifest_sha256": code_manifest_hash(),
            "code_hashes": code_hashes(),
            "issuer": cfg.issuer,
            "audience": cfg.audience,
            "upstream": cfg.upstream,
            "tau": 0.45,
        }

    async def process_decision(payload: dict, claims: dict, request_id: str):
        try:
            action = payload["action"]
            support = list(action["support"])
            args = dict(action.get("args", {}))
            if cfg.arm == "A0":
                decision = {"admit": True, "invariant": None, "reason": "passthrough"}
            else:
                monitor = monitor_from_payload(payload, cfg.arm)
                result = monitor.admit_action(str(action["class"]), support, payload.get("evidence_weights"), args)
                decision = {
                    "admit": result.verdict.name == "ADMIT",
                    "invariant": result.invariant,
                    "reason": result.reason,
                }
        except (KeyError, TypeError, ValueError) as exc:
            raise HTTPException(status_code=400, detail=f"invalid_decision_request: {exc}") from exc

        if not decision["admit"]:
            return {"ok": False, "blocked": True, "arm": cfg.arm, "request_id": request_id, "decision": decision}

        attestation = None
        if app.state.ledger is not None:
            attestation = app.state.ledger.append({
                "request_id": request_id,
                "subject": claims.get("sub"),
                "action": action,
                "decision": decision,
            })
        try:
            upstream_response = await app.state.http.post(
                app.state.cfg.upstream,
                json={"request_id": request_id, "action": action, "arm": cfg.arm},
            )
            upstream_response.raise_for_status()
            upstream = upstream_response.json()
        except (httpx.HTTPError, ValueError) as exc:
            raise HTTPException(status_code=502, detail="upstream_failure") from exc
        return {
            "ok": True,
            "blocked": False,
            "arm": cfg.arm,
            "request_id": request_id,
            "decision": decision,
            "attestation": None if attestation is None else {"seq": attestation["seq"], "sha256": attestation["sha256"]},
            "upstream": upstream,
        }

    @app.post("/v1/decide")
    async def decide(request: Request, claims: dict = Depends(require_token)):
        payload = await request.json()
        request_id = str(payload.get("request_id") or request.headers.get("x-request-id", "unnamed"))
        return await process_decision(payload, claims, request_id)

    @app.post("/mcp")
    async def mcp(request: Request, claims: dict = Depends(require_token)):
        envelope = await request.json()
        request_id = envelope.get("id")
        if envelope.get("jsonrpc") != "2.0" or envelope.get("method") != "tools/call" or request_id is None:
            return {"jsonrpc": "2.0", "id": request_id,
                    "error": {"code": -32601, "message": "Only tools/call is supported"}}
        params = envelope.get("params") or {}
        if params.get("name") != "czta.decide" or not isinstance(params.get("arguments"), dict):
            return {"jsonrpc": "2.0", "id": request_id,
                    "error": {"code": -32602, "message": "Expected czta.decide with an arguments object"}}
        result = await process_decision(params["arguments"], claims, str(request_id))
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "content": [{"type": "text", "text": json.dumps(result, separators=(",", ":"))}],
                "structuredContent": result,
                "isError": not result["ok"],
            },
        }

    @app.post("/v1/rla/sign")
    async def rla_sign(request: Request, _: dict = Depends(require_token)):
        if app.state.ledger is None:
            raise HTTPException(status_code=409, detail="RLA signing is enabled only on A2")
        payload = await request.json()
        payload["signer"] = app.state.ledger.signer
        return sign_attestation(payload, app.state.ledger.private)

    @app.post("/v1/rla/verify")
    async def rla_verify(request: Request, _: dict = Depends(require_token)):
        if app.state.ledger is None:
            raise HTTPException(status_code=409, detail="RLA verification is enabled only on A2")
        payload = await request.json()
        return {"valid": verify_attestation(payload, app.state.ledger.public)}

    @app.get("/ledger/verify")
    async def ledger_verify(_: dict = Depends(require_token)):
        if app.state.ledger is None:
            raise HTTPException(status_code=409, detail="Ledger is enabled only on A2")
        return {"valid": app.state.ledger.verify(), "records": len(app.state.ledger.records)}

    return app


app = create_app()
