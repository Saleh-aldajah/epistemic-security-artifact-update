# CHANGELOG — NDSS 2027 submission → IEEE S&P version

Source of record for the reviewer items below: `NDSS2027_Review_Validation_and_Resubmission_Plan` (project doc `claude/ndss2027-review-validation-and-resubmission-plan.md`). Item codes A1–A9 are Review A, B1–B14 Review B, F4.1/F4.2 the two findings the reviewers did not state.

The refurbished manuscript compiles with `pdflatex ×3` to **18 pages, 0 errors, 0 overfull boxes, 0 undefined references**: body (§1–§8) ends on page 13; Ethics / LLM-usage / Availability (excluded from the body count by the S&P CFP) and the references start on page 14; appendices A–D run p. 15–18. This is exactly the S&P budget (13 pages of text + ≤5 pages of references/appendices, ≤18 total).

**Nothing numeric was invented.** Every measured value in the paper is a value that was in the NDSS submission or is arithmetically derived from one (`results_macros_derived.tex`). Every experiment the reviews require but that has not been run is marked in the PDF with a red `[PENDING: …]` marker (18 of them; list in `SUBMISSION_CHECKLIST.md`). The final submission must contain none.

---

## 1. Structural changes (A1, B2, B5, B10, B14, F4.2)

| Change | Where | Answers |
| --- | --- | --- |
| One research question (“which part of an agent's reasons for acting can a runtime monitor enforce, and what does the remainder cost?”) stated in the first paragraph; three contributions **C1** definition + monitorability theorems, **C2** CZTA + gate, **C3** evaluation; novelty scope paragraph. Seven NDSS contributions → three. | §1 | A1, B2, B5 |
| Positioning moved to the front: §2.3 opens with the delta against Qu et al., Shen, CXI, Ray, CaMeL (Table 1) before any review material. | §2.3, Table 1 | B5 |
| PRISMA protocol, search freezes, registration mechanics, reliability audit (κ/AC1), corpus figures, human-factors pilot and the architecture appendix **removed** from the paper. The taxonomy survives as a half-page (§2.1) with one sentence of provenance; the crosswalk table keeps each class's share of the 552-record core corpus (Appendix B). The removed material is intact in `build/original_ndss_main.tex` for the journal SoK. | §2.1, App. B | A1, B10, B14 |
| Architecture (Fig. 1), workflow example, instantiation table (Table 2), TCB inventory and security analysis, overhead table all moved **from appendices into the main text** as §4. | §4 | A1, A6 |
| Every cross-reference is now a `\ref`/`\cite`; the six hard-coded references that pointed to the wrong section after renumbering (“Appendix A(a)/(c)”, “Definition 11”, “§IV-H(2)/(3)”, “Def. 10 below”) are gone; the duplicated paragraph, orphan fragment and empty appendix heading are gone. Verified by compiling and reading the PDF, not the source. | whole paper | A1 |
| Abstract restricted to live-model numbers: 18/40 → 2/40, Fisher p (macro `\GateVsNdFisherP`), RD −0.400 [−0.568, −0.232] (macros), 0.20 ms, utility pilot unresolved (p = 0.49). The 0.5B-driver numbers (“blocks 10.3%”, “0% false-quarantine”) and the pre-fix open-weight “no susceptibility” sentence are out of the abstract. | abstract | F4.2, B9 |
| The maturity table now names the reference-semantics suite as a *semantics check* distinct from the live gateway (“10/10 … constructed suite”), and lists the live authorization-layer result separately (3 prevented, 1 detected-not-prevented, 1 boundary). The §IV-F / §V-E contradiction (“MCP patterns test the coverage claim” vs. “not epistemic-layer tests”) is resolved: §3.5 says the coverage claim is tested by the crosswalk suite and the executed counterexample; §4.4 says the MCP patterns test the authorization layer. | Table 7 (App. D), §3.5, §4.4 | F4.2 |

## 2. Formal precision (A2, A3, A4, A5, B3, B7, B13)

| Change | Where | Answers |
| --- | --- | --- |
| **Definition 1 “Policy objects”** declares, before any invariant: the lattice L with the concrete instance UNTRUSTED ⊏ MEDIUM ⊏ TRUSTED; the channel labeler λ: Ch → L with ℓ(e) := λ(ch(e)); ℓ_min; C_prot; ℓ_req; τ (τ_c); the binding policy β with ℓ_β; the endorsement policy π with Authorized(ρ, b, ℓ′); ε; Δ_irrel. Nothing is used before it is declared. | §3.1, Def. 1 | A2, A5 |
| Labeler specified as a function of channel identity plus authentication evidence; **Assumption 2 (Trusted TCB)** states labeler and value-recorder correctness explicitly and names the excluded attack (channel spoofing); exercised in the running example. | §3.1, §3.3, §4.3 | A3, B7 |
| Attestation instantiated in one paragraph: who signs an evidence atom, the trusted root (realm key for user channels, ledger key otherwise), validity windows (token expiry / attestation TTL), what fails verification. | §3.1 after Def. 2 | A4 |
| One sentence on what the meet rule guarantees (a derived belief's label is a certified lower bound on the trust of its inputs); PROV moved to a recording-convention remark. | §3.1 | A5 |
| **New invariant I4, argument binding** (Def. 7): every bound argument slot s ∈ β(c(a)) must be named in vals(b) of some cited belief with ℓ(b) ⊒ ℓ_β(c, s). Proved a prefix-decidable safety property (Prop. 1 extended; Appendix A). The former I4 (counterfactual-dependence bound) is now **I5**. DEI = Lift(I1 ∧ I2 ∧ I3 ∧ I4) ∩ I5. Algorithm 1 gains the `vals` recorder and the I4 branch. | §3.2, Alg. 1, App. A | B3, F4.1 |
| Corollary 2 restated narrowly as **choice laundering**: the adversary strategy is quantified over A_β(S0), actions whose bound arguments are all trusted-derivable from the honest support. Remark (residual) states that the two executed probes (file 13; attacker recipient) are *not* instances — they violate I4 and are caught at admission. | §3.4, App. A | F4.1 |
| Threat model paragraph on reasoning manipulation / chain-of-thought poisoning: model-internal, so it surfaces as an I5 violation or as out-of-scope model poisoning; the gateway's own attack surface is analyzed in §4.3. | §2.2 | B13, A6 |
| Deployed scorer S = Σw/(1+Σw) shown to satisfy A1–A3 in two lines (qualifying atoms only; x/(1+x) increasing with w ≥ 0; fixed weights inside the TCB); τ_c and ℓ_β sensitivity sweep **registered** (PENDING). | §6.1 Deployed policy objects | B7 |

## 3. Examples and falsifiability (B1, B12, A6)

| Change | Where | Answers |
| --- | --- | --- |
| One **running example** — “delete file 0 (user) vs. planted file 13 (injection)”, with the choice-laundering variant “delete file 0 now, before the backup completes” — carried through Example 1 (policy objects), Example 2 (the five invariants on an honest and an attacked trace), Example 3 (protocol / Algorithm 1), Example 4 (CZTA workflow) and the gate. | §3–§5 | B1, A6 |
| **Falsifiability walk-through** (§3.5): the two traces of Example 2 are walked through the protocol; which refutation condition fires, which does not, and what distinguishes a definition failure from a deployment failure. | §3.5 | B12 |

## 4. Gate (A7, A9, B8)

| Change | Where | Answers |
| --- | --- | --- |
| Perturbation set made explicit: δ1 oracle plant removal (development only); δ2 removal of cited sub-ℓ_req support and δ3 removal of uncited content (both non-oracle, registered as the deployable gate); fp/miss reported per Prop. 5 (PENDING run). | §5.1, Alg. 2 | A7 |
| Stochasticity: re-commitments at temperature 0 / fixed seed; **tool-state divergence**: the counterfactual plane is assembled from ledgered atoms, never by re-querying tools; a flip not attributable to the removed content is quarantined anyway (**conservative default, stated**). | §5.1 | A7 |
| Gate value is now to be demonstrated on choice-laundering probes that *survive* argument binding, against baseline B1 — the only design in which the gate can show incremental value (PENDING). | §5.2, §6.3 | A9, B8, F4.1 |

## 5. Evaluation design (A8, A9, B4, B6, B9, B11)

| Change | Where | Answers |
| --- | --- | --- |
| RQ1–RQ5 stated; **development vs. test** separation declared: the four probes, five MCP patterns and the 16-task 0.5B workload are development evidence; the 40-case grid and 24-case benign arm are held-out; held-out sets, baseline configs and the utility MID to be deposited hash-sealed before the RQ1–RQ4 runs (PENDING deposit record). | §6.1 | A8 |
| **Baselines** B1 argument–instruction matching, B2 tool filter (CaMeL lineage), B3 I4 alone, under the identical harness (PENDING rows in Table 4). | §6.1, Table 4 | A9, B8 |
| **RQ3** registered paired crossover: 291 pairs per contrast, MID 10 points (80 % power; 355/arm for 90 %); per-episode failure taxonomy (defense-induced / model-induced / degenerate). The n = 24 pilot is reported as a pilot that cannot resolve the question. | §6.4 | B4, B11 |
| **RQ4** generality: second frontier endpoint, post-fix open-weight re-run (the pre-fix 0/120 is labelled unreliable), AgentDyn (60 tasks / 560 injections), and a second attack family (PENDING). *1 Nov: the second family is AgentDojo's `tool_knowledge` attack; the earlier "Braille-obfuscated" family was mis-sourced, see §10.* | §6.5 | B6, B9 |
| 0.5B-driver results confined to “existence” evidence (the counterexample exists; the oracle gate quarantines it) and labelled as such in the maturity table. | §6.3, Table 7 | B9 |

## 6. S&P-specific additions

* `\documentclass[conference,compsoc]{IEEEtran}` (IEEEtran V1.8b bundled), US letter, 10 pt.
* `\section*{Ethics considerations}` (mandatory; does not count toward the 13 body pages): testbed under the authors' control, no third-party systems probed, no disclosure required; the taxonomy's literature review used expert annotators coding public bibliographic metadata (no personal data); no human-subjects study in this paper (the threshold-adjudication pilot awaits an ethics determination and contributes no result); attack content is the public AgentDojo corpus plus local constructed probes.
* `\section*{LLM usage considerations}` (required when LLMs are used; also excluded from the body count): discloses LLM assistance for editing, LaTeX, figure-consistency checks, drafting definitions/proofs from author-specified theorem statements, and Lean scripts; every statement author-verified, every Lean script kernel-checked, every number recomputed from logs.
* `\section*{Availability}` citing an anonymized artifact placeholder (`\bibitem{artifact}`, anonymous.4open.science) — replace with the real anonymized link.
* Byline “Anonymous Author(s)”; the non-anonymized author comment from the NDSS source was **removed** from every shipped `.tex` (kept in the separately delivered `EpistemicSecurity_AUTHORS_camera_ready_DO_NOT_UPLOAD.txt`, outside the Overleaf project).
* Three new references: `artifact`, `bhagwatkar2025firewalls` (arXiv:2510.05244), `agentdyn` (arXiv:2602.03117). Reviewer-facing “Verified against …” notes stripped from all bibitems and preserved in `BIB_ANNOTATIONS.md`.

## 7. Design decision you can revert: I4

Adding I4 is the one change that alters the paper's claims rather than its presentation. It was made because Reviewer B's “simpler check” (match the action's arguments against the user instruction) catches both executed laundering probes at admission, so without I4 the gate's only evidence is also obtained by a weaker mechanism (F4.1). With I4, (a) that check is a special case of the enforceable fragment, (b) Corollary 2 is restated so that it remains true, and (c) the gate's value is to be shown where it actually exists — choice laundering with trusted-derivable arguments.

Cost of the decision: `DeiSafety.lean` must be extended to the I4 clause; `czta_ref` must implement the slot check and the overhead re-measured; the new probe family must be built. To revert, delete Def. 7, the I4 branch of Algorithm 1, the A_β(S0) restriction in Cor. 2 and Appendix A's ¬viol₄ clause, and rename I5 back to I4 — but then F4.1 stands unanswered.

## 8. Divergence from the resubmission plan

The plan recommended splitting into a CSF paper (formal core) and a systems paper. At your direction this version keeps C1–C3 together for S&P, which accepts theory-plus-system papers; the scoping review and the reliability audit (n = 114 frozen sample, κ/AC1) are out of this paper and remain available for a journal SoK. The PENDING list is the experimental programme the plan's §6 specified (UNIVERSE v4 E3b, E5, E6, E9).

## 9. 28 Oct 2026 — artifact audit findings folded into the manuscript

Three findings from the artifact audit (project docs `sp2028-step1-artifact-audit.md`, `sp2028-czta-ref-audit-and-v9.md`) changed the text:

| Finding | Edit |
| --- | --- |
| **F1** the NDSS live "monitor" arms were an unconditional protected-tool blocklist with a no-op gate | Pending your confirmation: Table 4 / abstract relabel of the n = 40 grid as a protected-tool-filter pilot; all arms re-run under the registration (`dei_live`). Threats-to-validity sentence already updated ("the live grid predates the I4 implementation and enforced only the citation contract"). |
| **F2** temperature never sent (agentdojo maps 0.0 → NOT_GIVEN) | Registered harness sends temperature and seed explicitly; the text will state the pilot's effective temperature as "provider default". |
| **F4** `czta_ref` v8.0.0 does not realize Algorithm 1 (a SOC-scenario policy pipeline with an in-band injection score; no belief store, receipts, lattice meet, endorsement API, or aggregator at τ_c) | §4.3 rewritten around **czta_ref v9** (`dei_monitor` I1–I4 on the trust path; v8's authorization layer, RLA, governance and identity modules kept byte-for-byte; 1,155 trusted lines; `/env` binds hashes); the v8 statement is made explicitly; **Table 3 and every mention of 0.20/0.28 ms, 0.18/0.12 ms, 0.68 ms, 16–19 % are retired to PENDING** (abstract, C2, §4.5, RQ5, maturity table) pending the v9 run on the Keycloak testbed with arms A0/A1/A2. |

Also closed: PENDING #3 (Lean I4 extension, kernel-checked), #4/#18 (I4 implemented in `dei_monitor` and in the v9 gateway), and the Remark 1 regression (O(1) window receipt). The manuscript compiles at 18 pages, body ending on page 13, 0 errors / overfull / undefined; 34 PENDING markers (each Table 3 cell counts).

## 10. 1 Nov 2026 — decisions taken and items closed (day plan items 2–4)

Decisions (yours): (a) the n = 40 grid is **relabelled as a pilot** and every arm is re-run under the registration; (b) the ℓ_β rule is **external targets TRUSTED, internal handles MEDIUM**; (c) the second frontier endpoint is **OpenAI gpt-4.1-mini** (gpt-4o if the model string is rejected at run start); (d) the open-weight family runs on **your Ollama/vLLM endpoint**.

| Change | Where |
| --- | --- |
| Pilot relabel throughout: abstract, C3, §6.1 (temperature statement: pilot at provider default, registered harness explicit 0.7 + seed), §6.2 ("A protected-tool filter already collapses this family (pilot)"), Table 4 split into *Pilot grid* / *Registered campaign* blocks, RQ3 pilot paragraph, threats, maturity table ("measured (development)"). | §6, Table 4, Table 7 |
| Gate semantics registered: **δ3 enforced** (a flip under removal of non-support tool atoms quarantines), **δ2 observed** (logged, never enforced; its co-located-plant flips are the resolution limit at atom granularity), δ1 oracle development-only. Prop. 5's approximation gap restated over the enforced set E. | §5.2, §6.1 policy objects, `dei_live/gate.py`, `policy.json` |
| RQ2 registered design written: choice-laundering families F1 (wrong file; co-located / separate placements), F2 (premature send), F3 (wrong option); 20 probes + 20 honest controls; registered prediction (δ3 catches F1-separate and F2 at zero honest cost, cannot see co-located plants; δ2 flags co-located plants only with every honest commitment needing the same atom). Offline construction run (`test_probes.py`) confirms I1–I4 and B1 admit all 20 laundered actions and the honest 20/20 complete. | §6.3, `probes/choice_laundering.py` |
| RQ3 registered study: 97 tasks × 3 seeds = 291 pairs; **headline paired RD with Newcombe interval**, exact McNemar secondary, task-level cluster bootstrap sensitivity; MID 10 points; power statement corrected (independent-arms floor 266/arm at 80 %, 355 at 90 %; the paired design is at least as powerful when within-task correlation is non-negative). | §6.4 |
| RQ5 folded to one sentence pointing at Table 3 (v9 testbed run pending). | §6.6 |
| **Correction**: §6.1 attributed a "Braille-obfuscated attack family" to arXiv:2510.05244; the v2 full text contains no such attack (its AgentDojo attacks are `important_instruction`, `tool_knowledge`, and second-order templates). RQ4's second attack family is now the benchmark's own `tool_knowledge` attack, cited as that paper's cascade Stage 1. `BIB_ANNOTATIONS.md` carries the correction note. | §6.1, bib |
| Registration deposit **v2** regenerated (`dei_live/registration/`): policy `ec1669fc…`, 150 + 60 held-out cases, 20 + 20 probe cases, `design.md` with the final arms/δ semantics/RQ4 endpoints, manifest over every file that will run; `DEPOSIT.md` gives the Zenodo/OSF + OpenTimestamps procedure. **Not yet deposited — that is your step (#9).** | `dei_live/registration/` |
| Harness: `seed` rejection by an OpenAI-compatible endpoint is caught once, retried without seed, and logged per episode as `seed_sent=false`; the explicit temperature is never dropped. | `dei_live/pipeline.py` |
| Page fit restored after the above: 18 pages, body ends on page 13, 0 errors / overfull / undefined references; 29 PENDING markers (Table 3 cells, Table 4 registered rows, RQ2–RQ5 results, deposit record, abstract/C2/C3 sentences). | — |

## 11. 1 Nov 2026 (afternoon) — calibration validation of the registered design

Triggered by the request to validate that every pending item closes in a defensible way. Changes made before the deposit (the deposit is still v2, regenerated; nothing has been timestamped yet):

| Finding | Change |
| --- | --- |
| **Development/test leak.** The archived logs (Work_1.zip) show the post-fix open-weight run used `user_task_0` of every suite (6 of its cases were in the held-out set) and the 0.5B honest workload on which τ_c was fixed used 22 workspace benign tasks (14 of the 16 held-out workspace benign tasks). | `development_cases.json` now lists every case any development run touched; held-out benign = **56** (all benign tasks no run touched: workspace 2, slack 20, travel 19, banking 15); security stays 150 with the open-weight run's cases excluded. Security cases whose *user task* served the τ_c workload remain (benign traces only) and are a registered descriptive stratum beside the τ sweep. §6.1, abstract and Table 4 say 56. |
| **RQ1 benign arm underpowered for a false-block difference** (MDE ≈ 21 points at 56 vs 56), yet the paper's bar sentence is "admission at lower benign cost than the filter". | RQ3 crossover now runs **no-defense, dei+gate, B1, B2strict** on the 97 tasks × 3 seeds (1,164 episodes); primary unchanged (dei+gate − no-defense, paired RD + Newcombe); registered paired secondaries dei+gate − B2strict and − B1 (Holm, family of 2). The RQ1 benign arm is descriptive. |
| **RQ2 single replicate too coarse** (5 probes per cell; 5/5 gives Wilson [0.57, 1.00]). | Initially increased to 3 seeds; the closure audit then found that F2 honest controls propose no protected action and cannot enter a gate denominator. Final design: **4 registered seeds**, 40 separable-plant episodes and 60 actionable honest-control evaluations, with F2's 20 non-action episodes reported but never scored as gate non-flips. Main = 640 episodes; oracle = 80. Wilson + probe-level cluster bootstrap. |
| **Power statements verified numerically.** | Independent-arms floor 266/355 reproduced; paired McNemar power at 291 pairs: 0.83 at the independence bound (discordance 0.345), 0.88 at 0.30, 0.97 at 0.20 — the "at least as powerful" claim holds for non-negative within-task correlation; RQ1 MDE 0.14–0.16 (power ≈ 1 for a pilot-size effect); dei vs B1 at Holm level resolves ≥ 0.11; RQ4(b) MDE 0.20–0.24. Added to `design.md`. |
| Page fit after the edits. | 18 pages, body ends p. 13, 0 errors / overfull / undefined; 27 PENDING lines. |

Observed in the upload, not a manuscript change: the 26 Oct confirmatory run on the open-weight endpoint voided its first 12 episodes with "Connection error" (fail-fast). The registered RQ4(b) run should be preceded by a two-episode smoke test (`--sec 2 --util 1`) against the endpoint.

## 12. 1 Nov 2026 (closure audit) — protocol–implementation reconciliation

The rescue calibration was necessary but not sufficient. A second adversarial read checked every registered claim against the runner, analyzer, probe construction, and episode totals. All changes below occurred **before** public deposit or timestamping. The user delegated the three open choices; the deposit therefore freezes **56 benign tasks, gpt-4.1-mini, and AgentDyn = not run**.

| Additional defect found | Resolution and executable check |
| --- | --- |
| RQ1 registered seven arms, while the text/table said six and omitted B2strict. | Seven arms throughout; B2strict added to Table 4. This adds one genuine measurement marker: the manuscript now has **36 `\PENDING{}` occurrences on 28 lines** (A 1, B 18, C 9, D 2, E 1, F 2, G 1, H 2). |
| `--oracle-delta1` without `--kind security` would produce 120 episodes, not the registered 60. | Final RQ2 uses `--kind security`; four seeds produce **80** oracle episodes. Main RQ2 = **640**. |
| “Registered random order” was stated but the runner used nested case/arm/rep loops. | `episode-order-v1`: deterministic SHA-256-seeded shuffle bound to cases, arms, replicates, model, temperature, and attack. Digest appears in the run header and every episode. Mock resume preserved eight records with no duplicates and the same digest. |
| F2 honest controls propose no protected action. Counting them as gate non-flips would inflate the false-quarantine denominator. | Four seeds yield **40 separable attacks** and **60 actionable controls**. F2's 20 non-action controls are reported as episodes but excluded from gate denominators. The full 640-episode mock grid asserted 40/60 exactly. |
| 0/60 was described as strictly below 0.06. | Exact Wilson upper = **0.0601739**, reported as **<0.061**; rule-of-three = 0.050. The 39/40 illustration is Wilson [0.871, 0.996]. |
| RQ1's small benign arm was still described as deciding the filter's benign-cost bar. | The 56-task arm is descriptive only. Only the powered RQ3 paired contrasts vs. B2strict and B1 (Holm family of two) decide comparative benign cost. |
| Analyzer did not emit all registered outputs. | Added RQ1 Holm comparisons and per-suite/τ strata; RQ2 pooled primary macros, probe-cluster intervals, and oracle confusion/fp/miss reconciliation; RQ3 Newcombe RD, exact McNemar, task-cluster bootstrap, Holm secondaries, protected-use/development-contact strata, and failure taxonomy; tau/ell_beta macros and CSV. Unevaluated perturbations are `not run`, never 0/n. |
| Degenerate failures were registered but not observable in episode records. | Empty failed main-model outputs are logged as `null_output`/`degenerate`; defense-induced classification takes precedence when a block/quarantine exists. |
| Power claims needed estimator and baseline qualifications. | `power_verify.py` reproduces 266/355, paired asymptotic 0.831/0.880/0.971, RQ1/RQ4 MDE ranges, and probe bounds. Exact-McNemar sensitivity = 0.810/0.862/0.970. The 0.11 Holm MDE is stated at baseline ASR 0.15 (baseline-dependent), not universally. |

**Offline validation:** live harness 7/7; analysis 6/6; reference monitor 20/20; LaunderBench I4 regression 5/5 (after correcting its stale import); full RQ2 mock 640 episodes; registration audit PASS; manifest 21/21. Archived open-weight development logs (80 + 16 episodes) have zero overlap with the repaired held-out set and zero unregistered case IDs. Power and registration audits are stored under `dei_live/validation/`.

**Build and run status:** Tectonic produced 19 pages with 0 errors, 0 undefined citations/references, and 3 overfull warnings; all rendered pages were visually inspected. The earlier 18-page pdflatex budget remains a build record to recheck after splicing, not a claim reproduced by this engine. AgentDyn is not run and is never pooled or silently dropped. No paid or registered episode was started. The previous open-weight tunnel still fails DNS resolution (`curl` exit 6); RQ4(b) therefore remains blocked until the endpoint is restarted and the two-episode development-case smoke passes. The manuscript remains experiment-incomplete by design.

## 13. 3 Nov 2026 — RQ5 / Table 3 closed with replacement-2 (deposit v4)

The original v9 package could not be located. A replacement was built from the supplied v8 modules and then corrected twice before any accepted measurement. The intermediate replacement-1 runs are **excluded**: they lacked independent gateway restarts and used a generic HTTP endpoint rather than MCP JSON-RPC.

The accepted implementation is `v9-replacement-2`: all ten v8 modules preserved byte-for-byte, real MCP `tools/call`, strict RS256/JWKS validation, I1–I4 admission, a sealed Ed25519 ledger, and a fresh gateway process for each repetition. Deposit v4 is DOI `10.5281/zenodo.23914405`, archive SHA-256 `d97f136951e2c08f163766eb1285b75dd7ed5e330ae7dbffd23d9983bbdfff3b`, manifest SHA-256 `c67de99877e43732b0de639a60a701e2880bc81af1386d1b797caae671946071`.

All 27 arm × rate × repetition cells passed with zero errors. Table cells are **mean p50 and mean p95 across three independently restarted repetitions**, generated by `build/emit_rq5_macros.py` from the deposited raw records. A2−A0 p50 overhead is **10.1%**, **6.1%**, and **2.7%** at 5/25/100 req/s. A2 RLA sign/verify is **1.42/2.14 ms** and **1.47/2.18 ms** p50/p95 over 1,000 iterations with zero errors.

The abstract, C2, architecture description, Table 3, RQ5, and maturity table now name the replacement explicitly. The original registration is DOI `10.5281/zenodo.23875699`; its archive and manifest hashes are in §6.1. Only the OpenTimestamps Bitcoin block-time evidence remains pending in group A. RQ5's 18 former markers are closed; **18 `\PENDING{}` occurrences remain** (A 1, C 9, D 2, E 1, F 2, G 1, H 2). Tectonic: 19 pages, 0 errors, 0 undefined citations/references, 3 overfull warnings; all pages visually inspected.

## 14. 3 Nov 2026 — RQ1, RQ2, and sensitivity closed

RQ1 completed 1,442 episodes with zero voids. Admission and B1 both have ASR 0.087, so RQ1 is explicitly a result about I4 rather than full-DEI superiority; B2strict has ASR 0.047 but higher descriptive benign cost. Table 4 contains all seven arms with macro-emitted cells.

RQ2 completed 640 probe and 80 oracle episodes with zero voids. Deployable δ3 catches 23/26 separable commitments (0.885, Wilson [0.710, 0.960]) and falsely quarantines 4/29 actionable controls (0.138 [0.055, 0.306]); only 26 separable and 29 actionable evaluations arose and non-actions were not imputed. Oracle δ3 is TP 12 / FN 15 / FP 5 / TN 2 (miss 0.556, FP rate 0.714); δ2 is TP 15 / FN 12 / FP 6 / TN 1. The zero-honest-cost prediction is refuted and the gate's value is stated conditionally.

The offline sweep is flat at τ = 0.30/0.45/0.50 and drops to zero at 0.60/0.67; the all-TRUSTED binding rule reduces security admissions to 19/184 while leaving benign admissions at 22/51.

All macro identifiers were normalized to letter-only LaTeX commands and RQ2 macros were namespaced to avoid redefinition. Large appendix tables were moved to the artifact with labeled short sections retained; mechanism Definition 11 remains in the paper. Final Tectonic build: **18 pages, 0 errors, 0 overfull boxes, 0 undefined citations/references**, with all 18 pages visually inspected. Six pending items remain: A block time, RQ3, two RQ4 markers, and abstract/C3 sentences.

## 15. 7 Nov 2026 — RQ3 and RQ4 closed; final manuscript

RQ3 completed 1,164 episodes with 50 voided and 1 degenerate. DEI+gate changes completion by −0.268 (Newcombe [−0.333, −0.199]) versus no defense, a material utility cost, but outperforms B2strict by +0.107 ([+0.057, +0.156], Holm p<0.001) and B1 by +0.055 ([+0.003, +0.106], Holm p=0.052, borderline). Failure taxonomy: DEI+gate 74 defense-induced / 115 model-induced / 0 degenerate; B2strict 132 / 88 / 0.

RQ4(a) completed 824 episodes with zero voids. On gpt-4.1-mini: no defense 0.480, DEI 0.107, DEI+gate 0.060, B1 0.087. RQ4(c) completed 618 episodes with 20 voided. On `tool_knowledge`: no defense 0.540, DEI 0.100, B1 0.080. All 150-security-case rows have Wilson intervals. The extra 168 benign episodes beyond the planned 450 are secondary and are not promoted to primary evidence.

RQ4(b) is **not run** because repeated 240-second inference timeouts prevented a valid open-weight replication; no susceptibility or robustness is claimed. AgentDyn is **not run** and is never pooled or silently dropped.

Abstract and C3 now report the I4-localized result, the gate's measured limits, and the security–utility trade-off. Final Tectonic build: **18 pages, 0 errors, 0 overfull boxes, 0 undefined citations/references**, with all 18 pages visually inspected. Only three deposit-evidence items remain: replacement v2 DOI, v4 block time, and v5 block time.

## 16. 7 Nov 2026 — timestamps and final artifact status

OpenTimestamps completed for all three code/deposit lines: registration v2 block 974214 (2026-11-02T05:06:44Z), testbed v4 block 974389 (2026-11-03T13:03:48Z), and campaign hotfix v5 block 974430 (2026-11-03T19:47:14Z). The final reproducibility archive SHA-256 is `5e7995e852774159124656b96e1ad09b10cb12da80b91e70d5df91dee3136c60`; its 21 registration entries and 34 testbed entries verify after fresh extraction. Only the replacement v2 DOI remains pending because the original v2/v3 Zenodo records were deleted. No experiment or timestamp item remains open.

## 17. 8 Nov 2026 — AgentDyn and open-weight generality resolved

AgentDyn completed 1,120 episodes with 30 voided attempts excluded. ASR falls from 0.470 to 0.237 (RD −0.232 [−0.286, −0.178], Fisher p=4.76e-16), providing independent dynamic-suite generality. The earlier 240-episode subset was discarded as incomplete and not analyzed.

The open-weight row is completed but uninformative: qwen3:8b follows 1/60 no-defense injections and 0/60 under DEI, so no susceptibility or robustness is claimed. This is distinct from the former timeout-only not-run status and is reported as a limitation of the model, not as evidence of defense effectiveness.

## 18. 8 Nov 2026 — I4-centered framing

The title and contribution framing are now explicit: **I4-centered admission, measured trade-offs, and conditional gate value**. The manuscript does not claim full-DEI superiority or a general counterfactual defense. The abstract states the admission result directly: every bound argument of a protected action must be named by a cited belief of sufficient standing. RQ2's conditional catch, false quarantines, oracle misses, and RQ3's material utility cost are presented as first-class limits rather than hidden caveats. AgentDyn and `tool_knowledge` provide replication; qwen3:8b is reported as uninformative, not as resistance.

## 19. 8 Nov 2026 — S&P-focused abstract

The abstract now presents CZTA as the physical realization of Algorithm 1 and Proposition 1, with mean p50 5.02 ms at 25 req/s and A2−A0 overhead of 2.7–10.1% across 5–100 req/s. It explicitly frames the admission result as I4, not full-DEI superiority, and states that counterfactual limitations are implementation-specific rather than inevitable consequences of hyperproperties. It avoids claims that counterfactual defenses are doomed, while retaining the gate's measured miss, false-quarantine, and utility costs as evidence of the boundary.

## 20. 9 Nov 2026 — replacement v2 DOI and final zero-PENDING build

Replacement v2 is now registered as DOI `10.5281/zenodo.24075933`, linking the complete manuscript and reproducibility archive. The final build has **zero `\PENDING{}` markers**, 18 pages, 0 errors, 0 overfull boxes, and 0 undefined citations/references. Credential scans found no actual secrets; credential-like strings occur only inside AgentDyn's public attack examples and are retained as benchmark content, not as credentials.
