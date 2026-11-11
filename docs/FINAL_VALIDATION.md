# Final validation record — Epistemic Security

## Experimental completion

- **RQ1:** 1,442 episodes, zero voided. DEI and B1 tie at ASR 0.087, so RQ1 is reported as an I4 result, not full-DEI superiority.
- **RQ2:** 640 probe + 80 oracle episodes, zero voided. δ3 catches 23/26 separable commitments and falsely quarantines 4/29 actionable controls; δ3 misses 15/27 oracle-positive cases. The zero-honest-cost prediction is refuted.
- **RQ3:** 1,164 episodes, 50 voided, 1 degenerate. DEI+gate completion RD −0.268 [−0.333, −0.199] versus no defense; +0.107 [+0.057, +0.156] versus B2strict; +0.055 [+0.003, +0.106], Holm p=0.052, versus B1.
- **RQ4(a):** 824 episodes, zero voided. No defense 0.480, DEI 0.107, DEI+gate 0.060, B1 0.087.
- **RQ4(c):** 618 episodes, 20 voided. No defense 0.540, DEI 0.100, B1 0.080. The additional 168 benign episodes beyond the planned 450 are secondary only.
- **RQ4(b):** completed 120 episodes but is uninformative (1/60 susceptibility); see `RQ4B_LIMITATION.md`.
- **AgentDyn:** completed 1,120 episodes with 30 voided attempts excluded: ASR 0.470 → 0.237, RD −0.232 [−0.286, −0.178], Fisher p=4.76e-16.
- **RQ5:** all 27 cells passed with zero errors. A2−A0 p50 overhead 10.1% / 6.1% / 2.7% at 5/25/100 req/s; RLA 1,000 iterations with zero errors.

All statistics were independently recomputed from the raw JSONL. Mock and development data were not substituted for registered results.

## Manuscript checks

- Final Tectonic build: **18 pages**, 0 errors, 0 overfull boxes, 0 undefined citations/references.
- All 18 pages rendered and visually inspected; no clipping, blank pages, or broken glyphs.
- Macro identifiers normalized to letter-only LaTeX commands and namespaced per experiment to avoid redefinition.
- Large appendix tables are retained in the artifact rather than printed; required mechanism definition and labels remain valid.

## Deposit status

- v2 timestamp complete: Bitcoin block **974214**, block time **2026-11-02T05:06:44Z**.
- v2 and v3 Zenodo records were deleted and must be recreated at final upload; their archives and OTS proofs remain valid locally.
- v4 and v5 records remain active. v4 timestamp completed at block **974389** (`2026-11-03T13:03:48Z`); v5 timestamp completed at block **974430** (`2026-11-03T19:47:14Z`).
- Replacement v2 DOI is registered as `10.5281/zenodo.24075933`.
- Archive integrity is verified by the accompanying manifests and fresh extraction checks.
- `grep -c '\\PENDING{' main.tex` = **0**.

No result, sample, interval, or completion claim was fabricated.

## Framing

The final manuscript is explicitly framed as **I4-centered admission, measured trade-offs, and conditional gate value**. It does not claim full-DEI superiority or a general counterfactual defense. Conditional catch, false quarantines, oracle misses, material utility cost, and the uninformative qwen3:8b outcome are reported as limitations rather than hidden caveats.
