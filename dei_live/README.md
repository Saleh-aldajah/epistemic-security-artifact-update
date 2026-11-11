# dei_live — the registered live-model harness (S&P version)

## Final execution addendum (11 Nov 2026)

The registration instructions below preserve the pre-run design. Final raw
logs are under `../results/`: RQ1–RQ4(c), AgentDyn, and the subsequently added
RQ4(b) log. AgentDyn completed 1,120 analyzed episodes with 30 voided attempts
excluded. RQ4(b) completed 120 episodes but remains uninformative at 1/60
susceptibility. These final execution records supersede the historical
AgentDyn not-run planning decision; they do not rewrite the registered design.

Replaces `agentdojo_integration.py` / `arms.py` of the NDSS campaign kit. Built 27 Oct 2026 after the
step-1 audit found that the NDSS live arms were an unconditional protected-tool blocklist with a no-op gate
and no temperature control (project doc `sp2028-step1-artifact-audit.md`).

## What it is
* **A real admission layer at the sink.** `DEIToolsExecutor` sits where the gateway sits: every proposed
  tool call is admitted or denied against the episode's ledger before execution; denied calls return an
  error tool-result so the agent can continue.
* **Channel labels, no oracle.** `Ledger.from_messages`: user turn and system prompt TRUSTED, every tool
  result MEDIUM, model text is not evidence. Nothing is labelled by content.
* **Value recorder.** `Atom.names(value)`: canonical forms (lower-case, punctuation-normalised, e-mail,
  ISO/month-day dates, numerics) with token-boundary matching ("0" does not match "10").
* **Policy objects in one file** (`dei_live/policy.py`): protected tools → classes, bound slots with ℓ_β
  (external targets TRUSTED, internal handles MEDIUM), ℓ_req, τ_c, the directive lexicon, the gate's δ
  definitions. `policy_hash()` is the value the paper cites; `make_registration.py` deposits it.
* **I1–I4 admission** (`dei_live/admission.py`): support(a) = atoms naming any short argument value plus
  user atoms expressing the action class; I1 attested roots ≥ floor; I3 S = n/(1+n) over qualifying
  atoms at ℓ_req ≥ τ; I4 every bound slot value named at ≥ ℓ_β. Logged per decision: S, τ, qualifying
  atoms, per-slot best label — the τ / ℓ_β sweep is recomputed offline by `analyze.py`.
* **Baselines under the same interceptor**: `b1` argument–instruction matching, `b2` CaMeL-lineage taint
  rule, `b2strict` (the NDSS pilot arm, for replication), `b3` I4 alone. Every arm's verdict is logged
  as a shadow on every protected call of every episode.
* **The gate** (`dei_live/gate.py`, Alg. 2): δ2 removes cited sub-ℓ_req tool atoms that are not the sole
  binder of a bound slot; δ3 removes uncited tool atoms; δ1 oracle plant removal only when payloads are
  supplied (development). Re-commitment at temperature 0 on the ledgered plane (no tool re-queries); a
  changed canonical action, no action, or a failed re-commitment quarantines (conservative default).
* **Temperature and seed are sent explicitly on every request** (`ExplicitLLM`; agentdojo 0.1.35 maps
  0.0 to NOT_GIVEN — this does not). Episode order is a deterministic SHA-256-seeded shuffle whose digest is
  bound to the full design and recorded in the header and every episode; resume preserves that order.

## Verified offline (no network)
`python3 -I test_dei_live.py` — 8/8 against the real workspace suite with a scripted model:
an injection-following model is caught by dei (I3/I4) and by every baseline; the benign "delete the
largest file" task is admitted by dei and b3 and falsely blocked by b1, b2 and b2strict; choice laundering
(the plant flips the ORDER of two user-authorised deletes) passes I1–I4 and is quarantined by δ2, while the
honest run is stable; temperatures 0.7 / 0.0 arrive at the client as sent; empty failed outputs are logged for the
registered failure taxonomy. `python3 -I test_analyze.py` — 6/6 synthetic-data tests cover paired statistics,
Holm-adjusted RQ3 contrasts, probe pooled/oracle macros, and unevaluated-perturbation denominators.
`python3 power_verify.py` reproduces the registered power claims; `python3 validate_registration.py` checks case
separation, episode totals, and deterministic episode ordering. `PROBE_REPS=4 python3 test_probes.py` runs the full
640-episode mock RQ2 grid and asserts the 40-attack/60-actionable-control primary denominators.
`python3 -I run_campaign.py --mock ...` runs the whole campaign loop offline; `analyze.py` reproduces the
archived n = 40 statistics to the digit (18/40, 2/40, p = 5.31e-5, RD −0.400 [−0.568, −0.232]).

## Running the registered campaign (your machine, your keys) — in this order
Keys and endpoints come from the environment only; never paste them into chat or files.
```
pip install agentdojo==0.1.35 openai tenacity
python3 -I test_dei_live.py && python3 -I test_probes.py && python3 -I test_analyze.py  # 8/8, construction, 6/6
python3 power_verify.py && python3 validate_registration.py

# 0. Deposit + timestamp BEFORE any paid episode (PENDING #9) — see registration/DEPOSIT.md
sha256sum -c registration/MANIFEST.sha256

# 1. RQ1 (+ descriptive benign arm) on the primary subject: seven arms, held-out set  (PENDING #10, #11, Table 4)
export FRONTIER_API_KEY=...  FRONTIER_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai/  FRONTIER_MODEL=gemini-2.5-flash
for s in workspace slack travel banking; do
  python3 run_campaign.py --suite $s --cases registration/held_out_cases.json \
     --arms no-defense,dei,dei+gate,b1,b2,b2strict,b3 --temperature 0.7 --out out/rq1_$s.jsonl
done

# 2. RQ2 probes: 20 choice-laundering probes + 20 honest controls, 4 registered seeds  (PENDING #6, #15)
#    Primary gate denominators: 40 separable attacks; 60 ACTIONABLE honest controls (F2 non-actions excluded).
python3 run_campaign.py --probes --reps 4 --arms no-defense,dei,dei+gate,b1 --temperature 0.7 --out out/rq2_probes.jsonl
python3 run_campaign.py --probes --kind security --reps 4 --arms dei+gate --temperature 0.7 --oracle-delta1 --out out/rq2_probes_oracle.jsonl   # 80 episodes: development comparator

# 3. RQ3 crossover: all 97 user tasks x 3 seeds; primary dei+gate vs no-defense, secondary vs b2strict and b1  (PENDING #16)
for s in workspace slack travel banking; do
  python3 run_campaign.py --suite $s --sec 0 --util 99 --reps 3 --arms no-defense,dei+gate,b1,b2strict --temperature 0.7 --out out/rq3_$s.jsonl
done

# 4. RQ4  (PENDING #7, #17) — each row its own run header
#   (a) second frontier endpoint
FRONTIER_BASE_URL=https://api.openai.com/v1 FRONTIER_MODEL=gpt-4.1-mini FRONTIER_API_KEY=... \
  bash -c 'for s in workspace slack travel banking; do python3 run_campaign.py --suite $s --cases registration/held_out_cases.json \
     --arms no-defense,dei,dei+gate,b1 --temperature 0.7 --out out/rq4a_$s.jsonl; done'
#   (b) post-fix open-weight family on your Ollama/vLLM endpoint (60 workspace held-out security cases x 2 arms = 120 episodes)
#   First run this TWO-episode development-case connectivity smoke (workspace/user_task_0; never a held-out result):
OW_BASE_URL=http://localhost:11434/v1 OW_MODEL=<qwen3 tag> python3 run_campaign.py --model-kind ow --suite workspace \
     --kind security --sec 1 --util 0 --arms no-defense,dei --temperature 0.7 --out out/rq4b_smoke.jsonl
OW_BASE_URL=http://localhost:11434/v1 OW_MODEL=<qwen3 tag> python3 run_campaign.py --model-kind ow --suite workspace \
     --cases registration/held_out_cases.json --kind security --arms no-defense,dei --temperature 0.7 --out out/rq4b_workspace.jsonl
#   (c) second attack family on the primary subject
for s in workspace slack travel banking; do
  python3 run_campaign.py --suite $s --cases registration/held_out_cases.json --attack tool_knowledge \
     --arms no-defense,dei,b1 --temperature 0.7 --out out/rq4c_$s.jsonl
done
#   (d) AgentDyn: only if an importer is deposited as a MANIFEST addendum before the run; otherwise reported as "not run".

# 5. Analysis and macros (every number in the paper comes from here)
cat out/rq1_*.jsonl > out/rq1_all.jsonl
python3 analyze.py out/rq1_all.jsonl --macros results_macros_rq1.tex \
  --development-cases registration/development_cases.json --strata registration/strata.json
python3 analyze.py out/rq2_probes.jsonl --oracle-log out/rq2_probes_oracle.jsonl --macros results_macros_rq2.tex
cat out/rq3_*.jsonl > out/rq3_all.jsonl
python3 analyze.py out/rq3_all.jsonl --macros results_macros_rq3.tex \
  --development-cases registration/development_cases.json
python3 power_verify.py --out validation/power.json
python3 validate_registration.py --out validation/registration_audit.json
```
`--kind security|utility` restricts any case set, including a deposited one. Resumable (re-run continues), aborts after 5 consecutive voided episodes, 240 s per-episode timeout
with a handler (a hung call voids the episode instead of killing the run). If an endpoint rejects `seed`, the call
is retried once without it and the episode records `seed_sent=false`; temperature is never dropped.

Table 3 (RQ5, PENDING #5) is measured with the separate `czta_v9` package on the Keycloak testbed:
`python3 run_protocol.py --gateway-url https://<gateway> --token-cmd '<command printing a Keycloak RS256 token>'`.

## Deposit v2 (1 Nov 2026)
`registration/` now carries the final design: δ3 enforced / δ2 observed, the 20 + 20 probe cases × 4 seeds, RQ4 endpoints
(OpenAI gpt-4.1-mini; qwen3 via Ollama/vLLM; `tool_knowledge`; AgentDyn **not run** by pre-deposit decision), RQ3 headline = paired RD with
a Newcombe interval plus registered paired secondaries vs. b2strict and b1. Held-out benign = **56** (every benign task
untouched by any development run; 38 of the 40 workspace tasks were used by the pilot or the 0.5B τ-tuning workload),
security = 150 with the post-fix open-weight run's cases (user_task_0 of each suite) excluded. The manifest hashes every
file that will run, including `probes/choice_laundering.py`.

## Seed-rejection hotfix (3 Nov 2026)

The Gemini OpenAI-compatible endpoint rejects `seed` with HTTP 400, but its short exception text contains only `Error code: 400`. The fallback now inspects the provider response body as well as the exception text before dropping `seed` once and recording `seed_sent=false`. Temperature is never dropped. `test_seed_rejection_uses_response_body_fallback` covers this exact behavior; the harness is now 8/8. Deposit this hotfix before any paid registered episode.
