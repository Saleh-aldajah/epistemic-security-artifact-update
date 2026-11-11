# IEEE S&P submission checklist — Epistemic Security

Rules below are from the S&P 2026 call for papers (ieee-security.org/TC/SP2026/cfpapers.html, read 27 Oct 2026); the 2027/2028 calls have historically repeated them, but re-read the live call for the cycle you submit to.

## 0. Deadline and cycle

The manuscript is experiment-complete, with zero `\PENDING{}` uses. Confirm
the current cycle's abstract deadline, paper deadline, page rules, and
registration requirements against the official IEEE S&P call before upload.
Do not submit the same paper to another venue while it is under S&P review.

## 1. Format (verified in this build)

- [x] `\documentclass[conference,compsoc]{IEEEtran}`, IEEEtran.cls **V1.8b** bundled in the zip
- [x] US letter, 10 pt, two columns (IEEEtran defaults)
- [x] 13 pages of text: §1–§8 end on page 13
- [x] Ethics considerations and LLM usage considerations present as unnumbered sections after the Conclusion (both excluded from the 13-page count by the CFP)
- [x] References + appendices ≤ 5 pages: p. 14–18 → total 18 pages
- [x] 0 LaTeX errors, 0 overfull boxes, 0 undefined citations/references (Tectonic build, 11 Nov 2026; `latexmkrc` provided)
- [x] Appendices C and D are self-contained: mechanism predicates and proofs, executable semantics results, and evidence status are printed in the manuscript rather than deferred to the artifact
- [ ] Re-check the page count after every source edit; the budget has **no slack**

## 2. Anonymity

- [x] Byline `Anonymous Author(s)`; no affiliation, funding, or acknowledgment text
- [x] The NDSS source's non-anonymized author comment is removed from every shipped `.tex` (also scrubbed from `build/original_ndss_main.tex`); author names live only in the separately delivered `EpistemicSecurity_AUTHORS_camera_ready_DO_NOT_UPLOAD.txt`, which is not in the Overleaf zip
- [x] Prior work cited in the third person; no "our previous work"
- [ ] Replace the placeholder artifact URL in `\bibitem{artifact}` (anonymous.4open.science/…-AF35) with the real anonymized repository (Anonymous GitHub / GitFront); check that the repository, commit messages, file headers, `README`, Lean module names, and the hash-pinned `/env` contain no author names, institution names, or usernames
- [ ] Check `main.pdf` metadata (`pdfinfo main.pdf`: Author field must be empty) before upload
- [ ] ORCID is required for every author at abstract registration (register early; no name appears in the PDF)

## 3. Scientific completeness — the PENDING list

**Update 7 Nov 2026 (RQ3/RQ4 closed).** RQ3 shows a material utility cost (−0.268 [−0.333, −0.199]) but a significant advantage over B2strict (+0.107 [+0.057, +0.156]) and a borderline advantage over B1 (+0.055, Holm p=0.052). RQ4(a) replicates on gpt-4.1-mini (824 episodes) and RQ4(c) on `tool_knowledge` (618 episodes). RQ4(b) completed 120 episodes but is uninformative (1/60 susceptibility). AgentDyn completed 1,120 episodes with 30 voided attempts excluded: ASR 0.470 → 0.237, RD −0.232 [−0.286, −0.178], Fisher p=4.76e-16. Final Tectonic build: 18 pages, 0 errors, 0 overfull, 0 undefined references, visually inspected. Replacement v2 DOI is registered as `10.5281/zenodo.24075933`; **`grep -c '\\PENDING{' main.tex` = 0**. v4 timestamp completed at block 974389 (2026-11-03T13:03:48Z); v5 timestamp completed at block 974430 (2026-11-03T19:47:14Z).

**Update 3 Nov 2026 (RQ1/RQ2/sensitivity closed).** RQ1 has 1,442 episodes with zero voids and ties DEI/B1 at ASR 0.087; RQ2 has 640 + 80 episodes with zero voids and refutes zero honest cost (23/26 catch, 4/29 false quarantine, δ3 miss 15/27). The τ sweep finds a 0.50–0.60 cliff. **Six `\PENDING{}` occurrences remain**: block time, RQ3, two RQ4 markers, abstract/C3. Tectonic build: 18 pages, 0 errors, 0 overfull, 0 undefined references, visually inspected.

**Update 3 Nov 2026 (RQ5 closed).** Deposit v4 (`10.5281/zenodo.23914405`) registers replacement-2 with real MCP `tools/call` and three independent restarts per arm. All 27 cells passed with zero errors; A2−A0 p50 overhead is 10.1/6.1/2.7% at 5/25/100 req/s, and RLA passed 1,000 iterations with zero errors. Table 3 and RQ5 are macro-filled from `testbed_v4.json`; replacement-1 results are excluded. **18 `\PENDING{}` occurrences on 18 lines remain**: A 1, C 9, D 2, E 1, F 2, G 1, H 2.

**Update 1 Nov 2026 (calibration + closure audit).** Held-out benign is 56 (not 60) after the development-case audit; RQ3 runs four arms (1,164 episodes) and carries the registered utility contrasts against B2strict and B1. RQ2 runs 4 seeds (640 main + 80 oracle): 40 separable attacks and 60 actionable controls; F2's 20 non-action controls are reported but excluded from gate denominators. RQ1 is seven arms throughout, including B2strict in Table 4. AgentDyn is pre-registered as **not run**. The runner now records a deterministic shuffled-order digest (CHANGELOG §12). After restoring the B2strict row, **36 `\PENDING{}` occurrences on 28 lines** remain; every one belongs to A–H and no marker is silently removed.

**Update 1 Nov 2026.** Items 2–4 of the day plan are closed in the text and code (CHANGELOG §10): pilot relabel done; gate δ3-enforced/δ2-observed registered; RQ2 probe families built and validated offline; registration deposit v2 generated and manifest-verified (`dei_live/registration/`, procedure in `DEPOSIT.md`). The "Braille" family in row 7 was mis-sourced and is replaced by AgentDojo's `tool_knowledge` attack. Remaining for you to run, in order: deposit + timestamp (#9) → Table 3 testbed run (#5) → RQ1 six-arm campaign (#10, #11) → probe runs (#6, #15) → RQ3 crossover (#16) → RQ4 (#7, #17) → offline τ/ℓ_β sweep (#8) → `analyze.py --macros` → abstract/C2/C3 sentences (#1, #2) → `grep -c '\\PENDING{' main.tex` must print 0.

**Update 28 Oct 2026.** Closed since the first draft: #3 (Lean, `DeiSafety_v2_I4`), #4 and #18 (I4 in `dei_monitor` and in `czta_ref` v9). Changed: #5 is now the full Table 3 re-measurement on v9 with arms A0/A1/A2 (the v8 numbers are retired, see CHANGELOG §9), run on the Keycloak testbed with `czta_v9/run_protocol.py --gateway-url … --token-cmd …`; the abstract, C2, RQ5 and the maturity table take their values from that run. Added: the pilot relabel (F1) and the "provider default temperature" statement (F2) once you confirm. The original table below is kept for reference.


The final `.tex` must satisfy `grep -c '\\PENDING' main.tex` → **0** (the macro definition line is the only permitted occurrence). Each marker, what fills it, and where it is specified:

| # | Location (main.tex / PDF) | What is pending | Specified in |
| --- | --- | --- | --- |
| 1 | abstract | one sentence per RQ1–RQ4 with the measured numbers | — |
| 2 | §1, contribution C3 | RQ1–RQ4 numbers | — |
| 3 | §3.3, Prop. 1 proof | extend `DeiSafety.lean` with the I4 clause (prefix-decidability of the slot check); re-run `check_formal.sh` | artifact `DeiSafety.lean` |
| 4 | §4.2, Table 2, I4 row | implement the I4 slot check in `czta_ref` (`vals` recorder + β lookup at admission) | §3.2 Def. 7, Alg. 1 |
| 5 | §4.5, Table 3 note | re-measure p50/p95 and mediated overhead with the I4 check on the path | §4.5 harness |
| 6 | §5.2 | deployable-gate run: fp and miss of δ2/δ3 against the oracle δ1 per Prop. 5, on the choice-laundering probe families | §5.1 |
| 7 | §6.1, Suites and models | RQ4 runs (registered in `design.md`): (a) OpenAI gpt-4.1-mini, arms no-defense/dei/dei+gate/b1 on the full held-out set; (b) post-fix qwen3 family on your Ollama/vLLM endpoint, no-defense/dei on the 60 workspace held-out security cases (120 episodes); (c) `tool_knowledge` attack family on gemini-2.5-flash, no-defense/dei/b1 on the 150 held-out security cases; (d) AgentDyn **not run** by pre-deposit decision; no importer or episodes are claimed | `registration/design.md` RQ4 |
| 8 | §6.1, Deployed policy objects | τ_c and ℓ_β sensitivity sweep over security and utility | B7 |
| 9 | §6.1, Development vs. test | deposit record: hash-sealed, publicly timestamped deposit of held-out case sets, baseline configs, and the utility MID **before** any RQ1–RQ4 run (UNIVERSE E9) | E9 |
| 10 | §6.1, Baselines | run B1 argument–instruction matching, B2 tool filter, B3 I4-alone under the identical harness | A9 / F4.1 |
| 11 | §6.2 RQ1 text | B1–B3 results and the resulting claim; if B1 matches the admission arm, RQ1 is a statement about I4, and the paper must say so | F4.1 |
| 12–14 | Table 4, rows B1–B3 and B2strict | ASR, Wilson CI, false-block per baseline | — |
| 15 | §6.3 RQ2 | gate value on choice-laundering probes (two files the user may delete; send-now vs. send-later; recipient from the user's own contacts) that survive I4; quarantine rate vs. B1; false-quarantine on the benign arm | §3.4 Cor. 2, §5.2 |
| 16 | §6.4 RQ3 | paired crossover, 291 pairs per contrast, MID 10 points; paired RD with Newcombe interval; Holm secondaries vs B2strict/B1; per-invariant false-block; failure taxonomy (defense-induced / model-induced / degenerate) | UNIVERSE E5 |
| 17 | §6.5 RQ4 | RQ4 results, each with its own primary comparison and Wilson intervals | E3b, E6 |
| 18 | Appendices C and D | mechanism predicates and proofs, executable semantics results, and final evidence status printed directly in the manuscript | closed 11 Nov 2026 |

Also update `results_macros.tex` by re-running `recompute_and_emit_macros.py` on the new logs and extend it to emit the RD/RR macros now hand-entered in `results_macros_derived.tex` (header TODO), so that no figure in the paper is typed by hand.

Order that respects the development/test separation: **(9) deposit → (3),(4),(5) implementation → (10),(6),(15) baselines and probes → (16) RQ3 → (7),(17) RQ4 → (11),(12–14),(1),(2),(18) write-up.**

## 4. Content rules

- [x] Ethics considerations section present (mandatory; a paper without one may be rejected without review)
- [x] LLM usage considerations section present (required when LLMs were used in any part of the work)
- [x] No CVE identifiers or vendor-identifying vulnerability details (none in the paper)
- [x] No fabricated or extrapolated numbers; every measured value traces to the NDSS submission's logs or to `results_macros_derived.tex` arithmetic
- [ ] Open-science / artifact: S&P does not mandate an artifact at submission, but the Availability section promises one; make sure the anonymized repository contains what it lists (czta_ref, reference semantics, Lean, harnesses, logs, manifest, deposits)

## 5. Final scrub before upload

```
python3 -I build/assemble.py            # only if parts/ were edited
pdflatex main; pdflatex main; pdflatex main
grep -c '\\PENDING{' main.tex          # must print 0
grep -n -i '<surname-1>\|<surname-2>\|<institution>' main.tex   # fill in the real names locally; must print nothing
pdfinfo main.pdf | grep -E 'Pages|Author'          # Pages: ≤18, Author: (empty)
grep -c '^!' main.log                   # 0
grep -c 'Overfull' main.log             # 0
```

Then submit `main.pdf` through the S&P HotCRP for the chosen cycle, after mandatory abstract/author/COI registration one week earlier.
