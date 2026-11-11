# Offline validation record

Date: 2 November 2026

- `python3 -m tests.test_offline`: **5/5 passed**.
  - A1 admits an I4-unbound action (empty beta); A2 blocks it on I4; valid A2 action admits.
  - Sealed ledger verifies; a one-field tamper is detected.
  - Real RS256 token accepted; wrong audience, expired token, future token rejected; insufficient scope rejected with 403.
  - `/env` code hashes are present.
  - All ten supplied v8 module hashes match exactly.
- `bash run_offline_smoke.sh A0`: **PASS** over actual HTTP.
- `bash run_offline_smoke.sh A1`: **PASS** over actual HTTP.
- `bash run_offline_smoke.sh A2`: **PASS** over actual HTTP, including RLA sign/verify.
- `CZTA_SMOKE=1 bash run_restarts.sh A2 'python3 make_test_token.py'`: **PASS** for three independent gateway restarts over real MCP `tools/call` transport, with restart outputs merged by `merge_restart_results.py`.
- `python3 make_manifest.py && sha256sum -c MANIFEST.sha256`: **all entries OK**.

No real Keycloak measurement is claimed. Offline smoke latencies are not Table 3 results and are intentionally not reproduced here.
