#!/usr/bin/env python3
"""Open-loop Poisson latency protocol for the replacement CZTA testbed.

Registered default: 20 s warm-up + 60 s measured, rates 5/25/100 req/s,
three repetitions per arm. Measured errors are never discarded.
"""
from __future__ import annotations

import argparse
import asyncio
import json
import math
import os
import random
import subprocess
import time
from pathlib import Path

import httpx

from czta_gateway.config import code_manifest_hash
from czta_gateway.fixtures import mcp_payload


def percentile(values, q):
    if not values:
        return None
    values = sorted(values)
    pos = (len(values) - 1) * q
    lo, hi = math.floor(pos), math.ceil(pos)
    if lo == hi:
        return values[lo]
    return values[lo] * (hi - pos) + values[hi] * (pos - lo)


def token_from_command(command: str) -> str:
    result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
    lines = [line.strip() for line in result.stdout.splitlines() if line.strip()]
    if not lines:
        raise RuntimeError("token command produced no token")
    return lines[-1]


async def one_request(client, url, token, measured):
    payload = mcp_payload(f"benchmark-{time.time_ns()}", "0")
    started = time.perf_counter()
    try:
        response = await client.post(url, json=payload, headers={"Authorization": f"Bearer {token}"})
        elapsed = (time.perf_counter() - started) * 1000.0
        body = response.json()
        result = body.get("result", {})
        error = None
        if response.status_code != 200 or not result.get("structuredContent", {}).get("ok"):
            error = f"HTTP {response.status_code}: {str(body)[:180]}"
    except Exception as exc:
        elapsed = (time.perf_counter() - started) * 1000.0
        error = f"{type(exc).__name__}: {str(exc)[:180]}"
    return (elapsed, error) if measured else (None, error)


async def run_rate(client, gateway, token, arm, rate, rep, warmup, duration, seed):
    rng = random.Random(f"{seed}|{arm}|{rate}|{rep}")
    times = []
    t = 0.0
    while True:
        t += rng.expovariate(rate)
        if t >= warmup + duration:
            break
        times.append(t)
    loop = asyncio.get_running_loop()
    started = loop.time()
    tasks = []
    for t in times:
        delay = started + t - loop.time()
        if delay > 0:
            await asyncio.sleep(delay)
        tasks.append(asyncio.create_task(one_request(client, f"{gateway}/mcp", token, t >= warmup)))
    results = await asyncio.gather(*tasks)
    latencies, errors = [], []
    for result in results:
        latency, error = result
        if latency is not None:
            latencies.append(latency)
        if error is not None:
            errors.append(error)
    # Warm-up errors are protocol failures too; they are retained without retry.
    return {
        "arm": arm,
        "rate_req_s": rate,
        "rep": rep,
        "warmup_s": warmup,
        "measured_s": duration,
        "scheduled_requests": len(times),
        "measured_requests": len(latencies),
        "achieved_req_s": len(latencies) / duration if duration else 0.0,
        "p50_ms": percentile(latencies, 0.50),
        "p95_ms": percentile(latencies, 0.95),
        "errors": errors,
    }


async def rla_microbenchmark(client, gateway, token, iterations):
    sign_latencies, verify_latencies, errors = [], [], []
    for i in range(iterations):
        payload = {"benchmark": "rla", "iteration": i}
        started = time.perf_counter()
        try:
            response = await client.post(f"{gateway}/v1/rla/sign", json=payload,
                                         headers={"Authorization": f"Bearer {token}"})
            sign_latencies.append((time.perf_counter() - started) * 1000.0)
            response.raise_for_status()
            signed = response.json()
            started = time.perf_counter()
            verify = await client.post(f"{gateway}/v1/rla/verify", json=signed,
                                       headers={"Authorization": f"Bearer {token}"})
            verify_latencies.append((time.perf_counter() - started) * 1000.0)
            verify.raise_for_status()
            if not verify.json().get("valid"):
                errors.append(f"RLA verification failed at iteration {i}")
        except Exception as exc:
            errors.append(f"RLA iteration {i}: {type(exc).__name__}: {str(exc)[:160]}")
    return {
        "iterations": iterations,
        "sign_p50_ms": percentile(sign_latencies, 0.50),
        "sign_p95_ms": percentile(sign_latencies, 0.95),
        "verify_p50_ms": percentile(verify_latencies, 0.50),
        "verify_p95_ms": percentile(verify_latencies, 0.95),
        "errors": errors,
    }


async def main_async(args):
    gateway = args.gateway_url.rstrip("/")
    async with httpx.AsyncClient(timeout=httpx.Timeout(30.0), limits=httpx.Limits(max_connections=200)) as client:
        env_response = await client.get(f"{gateway}/env")
        env_response.raise_for_status()
        env = env_response.json()
        if env.get("arm") != args.arm:
            raise RuntimeError(f"Gateway arm is {env.get('arm')}, expected {args.arm}")
        if env.get("code_manifest_sha256") != code_manifest_hash():
            raise RuntimeError("Gateway /env code hash does not match the shipped protocol package")
        runs = []
        for rate in args.rates:
            for rep in range(1, args.reps + 1):
                print(f"RUN arm={args.arm} rate={rate} rep={rep} warmup={args.warmup}s measured={args.duration}s", flush=True)
                token = token_from_command(args.token_cmd)
                result = await run_rate(client, gateway, token, args.arm, rate, rep,
                                        args.warmup, args.duration, args.seed)
                runs.append(result)
                print(json.dumps({k: v for k, v in result.items() if k != "errors"}), flush=True)
                if result["errors"]:
                    print(f"ERROR COUNT: {len(result['errors'])}; first: {result['errors'][0]}", flush=True)
        rla = None
        if args.arm == "A2":
            token = token_from_command(args.token_cmd)
            rla = await rla_microbenchmark(client, gateway, token, args.rla_iterations)
    errors = [{"rate_req_s": r["rate_req_s"], "rep": r["rep"], "errors": r["errors"]} for r in runs if r["errors"]]
    if rla and rla["errors"]:
        errors.append({"rla": rla["errors"]})
    return {
        "protocol": "czta-v9-replacement-open-loop-v2",
        "implementation": env,
        "arm": args.arm,
        "seed": args.seed,
        "warmup_s": args.warmup,
        "measured_s": args.duration,
        "reps": args.reps,
        "rates_req_s": args.rates,
        "runs": runs,
        "rla": rla,
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
    }


def parse_rates(text):
    return [float(x) for x in text.split(",") if x.strip()]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--gateway-url", required=True)
    parser.add_argument("--token-cmd", required=True, help="shell command that prints a Keycloak RS256 token")
    parser.add_argument("--arm", choices=["A0", "A1", "A2"], required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--warmup", type=float, default=20.0)
    parser.add_argument("--duration", type=float, default=60.0)
    parser.add_argument("--rates", type=parse_rates, default=parse_rates("5,25,100"))
    parser.add_argument("--reps", type=int, default=3)
    parser.add_argument("--seed", type=int, default=20260814)
    parser.add_argument("--rla-iterations", type=int, default=1000)
    parser.add_argument("--smoke", action="store_true")
    args = parser.parse_args()
    if args.smoke:
        args.warmup, args.duration, args.rates, args.reps, args.rla_iterations = 1.0, 3.0, [5.0], 1, 10
    result = asyncio.run(main_async(args))
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2) + "\n")
    print(f"WROTE {out}: {result['status']}")
    raise SystemExit(0 if result["status"] == "PASS" else 1)


if __name__ == "__main__":
    main()
