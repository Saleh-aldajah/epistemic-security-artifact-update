# Registered design — Epistemic Security, S&P 2028 campaign (deposit v2, 2026-11-01)

Policy objects: `policy.json`, SHA-256 `ec1669fc0ec9139de7b1c0d35664034754e693245e311a4b1d230f99e3bf7b20` (frozen; any change = new deposit).
Benchmark: AgentDojo 0.1.35, suites v1.2 (workspace, slack, travel, banking); primary attack `important_instructions`.
Held-out cases: `held_out_cases.json` — 150 security cases (workspace 60, slack 30, travel 30, banking 30) and
56 benign tasks, sampled with `random.Random("20260814|<suite>|held-out")` from the complement of
`development_cases.json` — every case any development run touched: the NDSS pilot grid, sweep, n=20 grid and gpt-4o
calibration (workspace user_task_0/1/3 × all injection tasks), the post-fix open-weight run (user_task_0 of each suite),
the 24 pilot benign tasks, and the 22 workspace benign tasks of the 0.5B honest workload on which τ_c was fixed. Only two
workspace benign tasks (user_task_23, user_task_39) are untouched, which is why the benign held-out set is 56, not 60.
Security cases whose *user task* served the τ_c workload (benign traces only; no security episode) remain in the workspace
pool and are reported as a registered secondary stratum (τ-tuning tasks vs. untouched), beside the τ sweep.
Probe cases: `probe_cases.json` — 20 choice-laundering probes and 20 matched honest controls
(`probes/choice_laundering.py`, hashed below): F1 wrong-file (5 co-located, 5 separate), F2 premature send (5), F3 wrong
option (5). Probe user tasks are purpose-built (workspace `user_task_900`–`919`, each with a matched injection task that
plants a false claim in content the task legitimately reads) and run on the workspace suite's environment; every bound
argument is user-named, so I1–I4 and b1 admit the laundered action by construction. They test the gate, not admission,
and are reported separately from the held-out set.
Seeds: per-episode `derive_seed(20260814, suite, model, temperature, arm, rep)` (sealed PROTOCOL_EVAL_V2 formula).
Temperature: 0.7 for the grids, sent explicitly on every request; 0.0 for gate re-commitments. Provider seed sent when supported.
Label rule (ell_beta, registered): a target that leaves the trust boundary (recipient, amount, URL, channel, share-with) must be
named by a TRUSTED atom; an internal handle the user can only designate indirectly (ids, enumerated names) must be named by
some attested atom (MEDIUM suffices). Free text and dates are not bound.

## Arms
no-defense · dei (I1–I4) · dei+gate (I1–I4 + Alg. 2: **delta3 enforced** — a flip under removal of non-support tool atoms
quarantines; **delta2 observed** — flips under removal of cited sub-ell_req atoms that are not sole binders are logged, never
enforced; delta1 oracle runs only with `--oracle-delta1`, development comparator) · b1 argument–instruction matching ·
b2 tool filter (CaMeL-lineage taint rule) · b2strict (protected tools blocked unconditionally; the NDSS pilot arm) · b3 (I4 alone).
Every protected call is logged with the enforced verdict and the shadow verdicts of all other arms, so tau and ell_beta
sweeps are recomputed offline from the first decision and are secondary.

## Primary comparisons (one per RQ; everything else is secondary)
RQ1 security: ASR(dei) vs ASR(no-defense) on the 150 held-out security cases, primary subject gemini-2.5-flash,
     Fisher exact two-sided, α = 0.05; Wilson 95% CIs, RD (Wald) and RR (log) beside every p. Secondary: dei vs b1,
     dei vs b2, dei vs b2strict, dei vs b3 (Holm-corrected, family of 4); per-suite rows descriptive; workspace stratum
     "user task in the τ_c workload" vs. not, descriptive. If ASR(dei) is not below ASR(b1), RQ1 is reported as a
     statement about I4. Comparative benign-cost claims are decided only by the powered RQ3 paired contrasts; the 56
     RQ1 benign tasks are descriptive and are never used for that bar.
RQ2 gate: on the 20 probes × 4 registered seeds (temperature 0.7; 80 attack episodes and 80 honest-control
     episodes per arm), quarantine rate of dei+gate (per family × placement × perturbation: delta3 enforced, delta2 observed,
     delta1 oracle when run) against the admission rate of dei and b1 on the same probes (expected 1.0 by construction).
     **Primary**: delta3 catch rate on the separable plants (F1-separate + F2, 10 probes × 4 = 40 episodes) with Wilson
     and probe-level cluster-bootstrap intervals, and delta3 false-quarantine rate on the 60 actionable honest-control
     evaluations (15 probes × 4). F2's 20 honest controls propose no protected action and are reported as episodes but
     never counted as gate non-flips. 0/60 actionable controls gives Wilson upper 0.06017 (<0.061; rule-of-three 0.050).
     Secondary: co-located catch rate
     (expected ≈ 0), delta2 flag rates on plants and on controls
     (the resolution limit), fp and miss of delta2/delta3 against delta1 per Prop. 5 where delta1 is run. **Registered prediction** (from the offline construction run,
     `test_probes.py`): delta3 catches the separate placement of F1 and the F2 plants at zero honest cost and cannot see
     co-located plants (F1 co-located, F3); delta2 flags co-located plants only together with every honest commitment that
     needs the same atom (the resolution limit at atom granularity), so its false-quarantine rate on honest controls is
     reported beside its catch rate and it is never enforced.
     The one known miss mode (a value collision between an id and an unrelated id, F1 separate) is documented in the code.
RQ3 utility: within-task crossover on all 97 user tasks × 3 registered seeds = 291 pairs per arm pair (temperature 0.7),
     arms no-defense, dei+gate, b1, b2strict (4 × 291 = 1,164 episodes). Episode order is the runner's deterministic
     SHA-256-seeded shuffle (`episode-order-v1`), bound to the cases, arms, replicates, model, temperature, and attack;
     its digest is printed in the run header and every episode. **Primary: paired risk
     difference dei+gate − no-defense with a Newcombe (score) interval**; exact McNemar on discordant pairs secondary;
     task-level cluster bootstrap as sensitivity. **Registered secondary paired comparisons** (Holm, family of 2):
     dei+gate − b2strict and dei+gate − b1, which is where "admission at lower benign cost than the filter" is decided;
     the RQ1 benign arm (56 tasks) is descriptive only (its MDE for a false-block difference is ≈ 21 points).
     MID = 10 percentage points from the 83.3% pilot baseline. Power (computed 1 Nov 2026): an independent-arms design
     needs 266 per arm for 80% (355 for 90%) at MID 10; the paired test with 291 pairs has power 0.83 at the independence
     bound (discordance 0.345), 0.88 at discordance 0.30 and 0.97 at 0.20, i.e. at least as powerful whenever within-task
     correlation is non-negative. Descriptive strata: protected-tool use vs. none, and the 38 workspace tasks touched in
     development vs. the 59 untouched tasks. Each failure classified: defense-induced (a block/quarantine in the episode), model-induced
     (no block; the model failed), degenerate (no output).
RQ4 generality — four pre-specified replications, each its own Fisher test, Wilson CIs, no pooling:
     (a) second frontier endpoint: OpenAI `gpt-4.1-mini` via FRONTIER_BASE_URL=https://api.openai.com/v1 (if the endpoint
         rejects that model string at run start, `gpt-4o`, recorded in the run header); arms no-defense, dei, dei+gate, b1
         on the full held-out set (150 + 56);
     (b) post-fix open-weight family: qwen3 (exact tag recorded in the run header; development run qwen3.6-35B) via
         Ollama/vLLM (OW_BASE_URL, OW_MODEL); arms no-defense and dei on the 60 workspace held-out security cases
         (120 episodes), temperature 0.7, provider seed where supported;
     (c) second attack family: AgentDojo's `tool_knowledge` attack (the Stage-1 attack of Bhagwatkar et al.'s cascade) on
         the primary subject, arms no-defense, dei, b1, over the 150 held-out security cases;
     (d) AgentDyn suite (Li et al., arXiv:2602.03117): **not run** by pre-deposit decision on 1 Nov 2026; no importer is
         deposited, no episodes are claimed, and suite-generality is correspondingly limited.
RQ5 latency: admission p50/p95 on the released gateway (`czta_v9/run_protocol.py`, arms A0 passthrough / A1 monitor /
     A2 monitor+ledger, 3 rates × 3 runs) against a Keycloak-issued RS256 token; the v8 numbers are retired.

## Power and resolution of the primary comparisons (computed 1 Nov 2026, two-sided α = 0.05, 80% power)
Methods are reproducible offline with `power_verify.py`: standard two-proportion normal approximations for independent
grids and asymptotic McNemar power for the registered paired values; exact conditional McNemar enumeration is a sensitivity.
RQ1 (150 vs 150): minimum detectable absolute ASR reduction 0.14–0.16 for baselines 0.30–0.45; power ≈ 1.0 for an effect
of the pilot's size (0.45 → 0.05). At the family-of-4 Holm-adjusted level, dei vs b1 resolves 0.11 at baseline ASR 0.15;
the MDE is baseline-dependent (approximately 0.09 at 0.10 and 0.13 at 0.20), not a universal 0.11 guarantee.
RQ2 (40 separable-plant episodes over 10 probes): 39/40 gives Wilson [0.871, 0.996]; 0/60 actionable honest-control
evaluations gives Wilson upper 0.06017 (<0.061) and rule-of-three 0.050. RQ3: asymptotic power 0.83 / 0.88 / 0.97 at discordance 0.345 / 0.30 /
0.20; exact-enumeration sensitivity 0.81 / 0.86 / 0.97. RQ4(b) (60 vs 60): MDE 0.20–0.24; power 0.99 for a pilot-size
effect. RQ4(c) (150 vs 150): MDE ≈ 0.13 at a 0.25 baseline. RQ5: 300 / 1,500 / 6,000 requests per repetition at 5 / 25 / 100 req/s.

## Registered episode totals
RQ1 1442 = (150 + 56) × 7; RQ2 main 640 = 40 cases × 4 arms × 4 seeds, oracle 80 = 20 security
probes × 1 arm × 4 seeds (`--kind security`); RQ3 1,164 = 97 tasks × 4 arms × 3 seeds; RQ4(a) 824;
RQ4(b) 120; RQ4(c) 450; RQ4(d) not run.

## Analysis and reporting rules
`analyze.py` recomputes every number and emits the LaTeX macros (`--macros`); no figure is typed by hand.
Degenerate episodes (null model output) are reported and excluded only in a labelled sensitivity analysis.
Stopping rules: a run aborts after 5 consecutive voided episodes; voided episodes are re-run, never imputed.
Any deviation from this document is reported as a deviation in the paper, with the deposit's DOI and timestamp.
