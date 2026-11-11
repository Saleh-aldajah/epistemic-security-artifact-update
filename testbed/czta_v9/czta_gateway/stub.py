"""Local upstream stub used only for offline validation and upper-bound overhead runs."""
from __future__ import annotations

import asyncio
import os

from fastapi import FastAPI, Request

app = FastAPI(title="CZTA upstream stub")


@app.get("/health")
async def health():
    return {"ok": True, "stub": True}


@app.post("/v1/execute")
async def execute(request: Request):
    delay = float(os.environ.get("CZTA_STUB_DELAY_MS", "0")) / 1000.0
    if delay:
        await asyncio.sleep(delay)
    payload = await request.json()
    return {"ok": True, "executed": True, "request_id": payload.get("request_id")}
