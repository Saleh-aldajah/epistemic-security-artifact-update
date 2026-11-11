# CZTA v9-compatible replacement testbed

**Status:** replacement implementation `v9-replacement-2`, not the missing original v9 package. Built from the supplied v8 modules with a new I1–I4 trust path, strict RS256/JWKS validation, sealed Ed25519 ledger, real MCP `tools/call` transport, and an open-loop latency protocol with a fresh gateway process for each repetition. **Deposit v4 is required before any registered Table 3 measurement.**

## Arms

- **A0:** authorization + upstream only.
- **A1:** I1–I3 monitor (empty binding policy), no ledger.
- **A2:** I1–I4 monitor + sealed Ed25519 hash-chain ledger.

All arms share the same authorization and upstream path. `/env` publishes the code hashes and the manifest hash that `run_protocol.py` checks before any run.

## Offline validation

Install dependencies into an isolated environment:

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
```

Run:

```bash
python3 -m tests.test_offline
bash run_offline_smoke.sh A0
bash run_offline_smoke.sh A1
bash run_offline_smoke.sh A2
```

The tests cover I4 admission, real RSA/JWKS acceptance and rejection, ledger tamper detection, v8 byte identity, actual HTTP decisions, RLA sign/verify, and the open-loop protocol. Offline RSA keys are generated test fixtures and are not production credentials.

## Keycloak prerequisites

You need a realm and confidential client configured for service-account tokens:

- Realm issuer example: `http://127.0.0.1:8080/realms/czta`
- JWKS URL: `http://127.0.0.1:8080/realms/czta/protocol/openid-connect/certs`
- Token URL: `http://127.0.0.1:8080/realms/czta/protocol/openid-connect/token`
- Client audience: `czta-gateway`
- Scope: `tool:execute`
- Grant: `client_credentials`

`get_realm_token.sh` reads `KEYCLOAK_TOKEN_URL`, `KEYCLOAK_CLIENT_ID`, and `KEYCLOAK_CLIENT_SECRET` from the shell only. Do not write the secret into this package or chat.

## Run one arm

Start the upstream stub (for a testbed/upper-bound measurement):

```bash
python3 -m uvicorn czta_gateway.stub:app --host 127.0.0.1 --port 9001
```

In another terminal:

```bash
export CZTA_ARM=A0
export CZTA_JWKS_URL=http://127.0.0.1:8080/realms/czta/protocol/openid-connect/certs
export CZTA_ISSUER=http://127.0.0.1:8080/realms/czta
export CZTA_AUDIENCE=czta-gateway
export CZTA_UPSTREAM=http://127.0.0.1:9001/v1/execute
export KEYCLOAK_TOKEN_URL=http://127.0.0.1:8080/realms/czta/protocol/openid-connect/token
export KEYCLOAK_CLIENT_ID=czta-benchmark-client
export KEYCLOAK_CLIENT_SECRET='...'  # shell only

python3 -m uvicorn czta_gateway.app:app --host 127.0.0.1 --port 9000
```

In a third terminal, run a short real-Keycloak smoke first:

```bash
python3 run_protocol.py \
  --gateway-url http://127.0.0.1:9000 \
  --token-cmd 'bash get_realm_token.sh' \
  --arm A0 --smoke --out results/smoke_A0.json
```

Then run the restart-aware registered protocol, with the gateway stopped first:

```bash
bash run_restarts.sh A0 'bash get_realm_token.sh'
bash run_restarts.sh A1 'bash get_realm_token.sh'
bash run_restarts.sh A2 'bash get_realm_token.sh'
```

Each command performs **three independent gateway restarts**, and each restart runs **20 s warm-up + 60 s measured at 5/25/100 req/s**. Decisions use real MCP `tools/call` JSON-RPC transport. Measured errors are retained and make the run fail. Tokens are refreshed per repetition. A2 also measures RLA sign/verify (1,000 iterations by default).

For a quick check of the restart logic, use `CZTA_SMOKE=1` with the same command; smoke outputs are not manuscript results.

Combine only after all three arms pass:

```bash
python3 combine_results.py results/testbed_A0.json results/testbed_A1.json results/testbed_A2.json --out results/testbed.json
```

The combined file includes per-rate p50/p95 values and A2−A0 relative overhead. With a stub upstream, this is a testbed/upper-bound overhead measurement, not a production-latency claim.

## Before using the results

1. Publish the replacement package as **deposit v4** and timestamp its `MANIFEST.sha256`.
2. Report the replacement and the new DOI/hash as a deviation from the missing original v9 package.
3. Ensure every protocol run has zero errors and that `/env` hashes match the deposited code.
4. Do not use retired v8 latency numbers or present this replacement as the original v9.
