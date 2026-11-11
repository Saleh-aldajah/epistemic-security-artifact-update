#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -ne 2 ]; then
  echo "Usage: bash run_restarts.sh A0|A1|A2 'token-command'" >&2
  exit 2
fi
ARM="$1"
TOKEN_CMD="$2"
cd "$(dirname "$0")"
mkdir -p results
GATEWAY_PID=""

cleanup() {
  if [ -n "$GATEWAY_PID" ]; then
    kill "$GATEWAY_PID" 2>/dev/null || true
    wait "$GATEWAY_PID" 2>/dev/null || true
  fi
}
trap cleanup EXIT

curl -fsS --max-time 3 http://127.0.0.1:9001/health >/dev/null || {
  echo "Upstream stub is not healthy on port 9001" >&2
  exit 1
}

for REP in 1 2 3; do
  if curl -fsS --max-time 1 http://127.0.0.1:9000/health >/dev/null 2>&1; then
    echo "Port 9000 is already occupied; stop the old gateway first" >&2
    exit 1
  fi
  echo "RESTART arm=$ARM rep=$REP"
  CZTA_ARM="$ARM" python3 -m uvicorn czta_gateway.app:app --host 127.0.0.1 --port 9000 \
    > "results/restart_${ARM}_rep${REP}.log" 2>&1 &
  GATEWAY_PID=$!
  ready=0
  for _ in $(seq 1 60); do
    if curl -fsS --max-time 1 "http://127.0.0.1:9000/health" >/dev/null 2>&1; then
      ready=1
      break
    fi
    sleep 0.5
  done
  if [ "$ready" -ne 1 ]; then
    echo "Gateway failed to start; see results/restart_${ARM}_rep${REP}.log" >&2
    exit 1
  fi
  if [ "${CZTA_SMOKE:-0}" = "1" ]; then
    python3 run_protocol.py \
      --gateway-url http://127.0.0.1:9000 \
      --token-cmd "$TOKEN_CMD" \
      --arm "$ARM" --smoke \
      --out "results/restart_${ARM}_rep${REP}.json"
  else
    python3 run_protocol.py \
      --gateway-url http://127.0.0.1:9000 \
      --token-cmd "$TOKEN_CMD" \
      --arm "$ARM" --reps 1 --rates 5,25,100 \
      --out "results/restart_${ARM}_rep${REP}.json"
  fi
  kill "$GATEWAY_PID" 2>/dev/null || true
  wait "$GATEWAY_PID" 2>/dev/null || true
  GATEWAY_PID=""
  for _ in $(seq 1 30); do
    if ! curl -fsS --max-time 1 http://127.0.0.1:9000/health >/dev/null 2>&1; then
      break
    fi
    sleep 0.2
  done
done

python3 merge_restart_results.py --arm "$ARM" \
  "results/restart_${ARM}_rep1.json" \
  "results/restart_${ARM}_rep2.json" \
  "results/restart_${ARM}_rep3.json" \
  --out "results/testbed_${ARM}.json"
