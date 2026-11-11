# Epistemic Security — IEEE S&P version (Overleaf project)

Refurbished from the NDSS 2027 submission (#1108, Round-1 reject) according to
the review validation in `CHANGELOG.md`. This is the **IEEE S&P submission
project**; confirm the live cycle requirements before upload.

## Files that Overleaf compiles

| File | Role |
| --- | --- |
| `main.tex` | the manuscript (assembled; edit it directly from here on, or edit `build/parts/` and re-run the assembler) |
| `results_macros.tex` | AUTO-GENERATED live-model numbers (n = 40 grid). Regenerate with `recompute_and_emit_macros.py`; Table 4, §6, and the abstract update automatically |
| `results_macros_derived.tex` | RD/RR and their intervals derived from the same counts (hand-entered; header has the TODO to make the recompute script emit them) |
| `IEEEtran.cls` | V1.8b, as the S&P call requires (`[conference,compsoc]`) |
| `latexmkrc` | pdflatex build; Overleaf picks it up |

Current build record (Tectonic, 11 Nov 2026): **18 pages, 0 errors, 0
overfull boxes, and 0 undefined citations/references**. All 18 pages were
rendered and visually inspected. Appendices C and D now contain the mechanism
predicates and proofs, executable reference-semantics results, and final
evidence status directly; their technical content is not deferred to the
anonymized artifact.

## Status

The paper is **experiment- and deposit-complete**: zero `\PENDING{}`
markers remain. Replacement v2 DOI is `10.5281/zenodo.24075933`. v4 and v5
OpenTimestamps proofs are complete (blocks 974389 and 974430). RQ3 shows a material utility cost but a
significant advantage over B2strict; RQ4(a) replicates on gpt-4.1-mini and
RQ4(c) on `tool_knowledge`. RQ4(b) is completed but uninformative (1/60 susceptibility). AgentDyn is
complete: ASR 0.470 → 0.237 over 1,120 episodes with 30 voided attempts
excluded. RQ1 is seven arms; RQ2 is
four seeds with 40 separable attacks and 60 actionable controls; RQ3 is 291
pairs per contrast. Table 3 now comes
from deposit v4's restart-aware MCP testbed (`v9-replacement-2`), with all 27
cells passing and A2−A0 p50 overhead of 10.1/6.1/2.7% at 5/25/100 req/s.
RQ1 has 1,442 episodes and ties DEI/B1 at ASR 0.087; RQ2 has 640 + 80
episodes and refutes zero honest cost (23/26 catch, 4/29 false quarantine,
δ3 miss 15/27). No number was invented or filled from mock episodes. The
calibrated registration, power validator, case-separation audit, and analysis
pipeline are in the accompanying `dei_live` package. `SUBMISSION_CHECKLIST.md`
§3 gives the run order and current validation record.

## Other files

| File | Role |
| --- | --- |
| `CHANGELOG.md` | reviewer item → edit mapping (A1–A9, B1–B14, F4.1/F4.2); the one revertible design decision (I4) |
| `SUBMISSION_CHECKLIST.md` | S&P rules, deadlines, PENDING list, final scrub commands |
| `BIB_ANNOTATIONS.md` | the "Verified against …" notes stripped from the bibitems |
| (delivered separately, not in this zip) `EpistemicSecurity_AUTHORS_camera_ready_DO_NOT_UPLOAD.txt` | author metadata recovered from the NDSS source comment; keep it out of the Overleaf project until acceptance |
| `build/assemble.py` | one-time build aid: splices hand-written `build/parts/*.tex` with edited blocks of `build/original_ndss_main.tex` (the NDSS source, author comment scrubbed) into `main.tex`, asserting every replacement. `python3 -I build/assemble.py` from the project root reproduces `main.tex` byte-for-byte. Delete `build/` once you start editing `main.tex` directly |

Overleaf: upload the zip as a new project; `main.tex` is the root document.
The `build/` folder is ignored by the compiler.
