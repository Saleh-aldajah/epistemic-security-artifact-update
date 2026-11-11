# Provenance and implementation status

- The ten files under `czta_ref/` are preserved byte-for-byte from the user-supplied `czta_ref_v8.0.0` archive. Their hashes are asserted by `tests/test_offline.py`.
- `czta_gateway/dei_monitor.py` is the supplied I1–I4 reference monitor.
- New replacement code adds the FastAPI gateway, strict RS256 validation, arm construction, sealed ledger, offline fixtures, and latency protocol.
- This is **not** the original missing `czta_v9` package and has no claim to byte identity with it. Its implementation identifier is `v9-replacement-2`.
- No latency result from v8 is reused. Registered Table 3 results must come from this package after a separate deposit v4 and OpenTimestamps proof. The earlier replacement-1 results are excluded because they lacked independent process restarts and MCP transport.
- Third-party Python dependencies are declared in `requirements.txt`. No third-party model, dataset, or production credential is bundled.
