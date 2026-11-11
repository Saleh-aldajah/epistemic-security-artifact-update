#!/usr/bin/env bash
set -euo pipefail
: "${KEYCLOAK_TOKEN_URL:?Set KEYCLOAK_TOKEN_URL}"
: "${KEYCLOAK_CLIENT_ID:?Set KEYCLOAK_CLIENT_ID}"
: "${KEYCLOAK_CLIENT_SECRET:?Set KEYCLOAK_CLIENT_SECRET in the shell only}"
: "${KEYCLOAK_SCOPE:=tool:execute}"

curl -fsS --max-time 20 \
  -u "${KEYCLOAK_CLIENT_ID}:${KEYCLOAK_CLIENT_SECRET}" \
  -d grant_type=client_credentials \
  -d scope="${KEYCLOAK_SCOPE}" \
  "${KEYCLOAK_TOKEN_URL}" \
| python3 -c 'import json,sys; print(json.load(sys.stdin)["access_token"])'
