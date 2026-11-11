#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
export PYTHONPATH="/mnt/agents/output/pylibs${PYTHONPATH:+:$PYTHONPATH}"
python3 -c 'from tests.offline_fixtures import ensure_fixtures; ensure_fixtures()'
export CZTA_JWKS_JSON="$(cat tests/offline_test_jwks.json)"
export CZTA_ISSUER="http://127.0.0.1:8080/realms/czta"
export CZTA_AUDIENCE="czta-gateway"
export CZTA_UPSTREAM="http://127.0.0.1:9001/v1/execute"
ARM="${1:-A2}"
export CZTA_ARM="$ARM"

python3 -m uvicorn czta_gateway.stub:app --host 127.0.0.1 --port 9001 > /tmp/czta_stub_smoke.log 2>&1 &
STUB_PID=$!
python3 -m uvicorn czta_gateway.app:app --host 127.0.0.1 --port 9002 > /tmp/czta_gateway_smoke.log 2>&1 &
GATEWAY_PID=$!
cleanup() { kill "$GATEWAY_PID" "$STUB_PID" 2>/dev/null || true; }
trap cleanup EXIT

for _ in $(seq 1 60); do
  if curl -sf http://127.0.0.1:9001/health >/dev/null && curl -sf http://127.0.0.1:9002/health >/dev/null; then
    break
  fi
  sleep 0.5
done
curl -sf http://127.0.0.1:9002/env >/dev/null
python3 run_protocol.py --gateway-url http://127.0.0.1:9002 --token-cmd 'python3 make_test_token.py' --arm "$ARM" --smoke --out "results/offline_smoke_${ARM}.json"
