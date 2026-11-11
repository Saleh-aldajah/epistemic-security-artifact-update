# Epistemic Security — reproducibility artifact

This repository contains the manuscript, executable monitor, formal proofs,
registered evaluation harness, raw episode logs, analysis outputs, testbed, and
scoping-review materials for **Epistemic Security: Enforceable Admission and
the Limits of Counterfactual Defense**.

## Repository update — 11 November 2026

- Updated the IEEE S&P manuscript and Overleaf sources. Appendices C and D now
  print the mechanism predicates and proofs, executable reference-semantics
  results, and final evidence status directly rather than deferring them to
  this artifact.
- Final manuscript: **18 pages**, zero compilation errors, zero overfull boxes,
  zero undefined citations/references, and zero pending markers. Every page was
  rendered and visually inspected.
- Added the raw RQ4(b) episode log at
  `results/rq4b/rq4b_workspace.jsonl`. RQ4(b) completed 120 episodes but is
  uninformative at 1/60 susceptibility; it is not presented as a robustness
  result.
- Included the completed AgentDyn replication log at
  `results/agentdyn/agentdyn_all.jsonl`: 1,120 analyzed episodes with 30
  voided attempts excluded. Upstream suite-version metadata is under
  `docs/agentdyn/`; third-party source code is not redistributed here.
- Added the Lean 4 development under `formal/` and the executable reference
  semantics and property tests under `reference_semantics/`.

## Layout

| Path | Contents |
| --- | --- |
| `manuscript/` | Revised IEEE S&P PDF, LaTeX source, macros, and Overleaf build files |
| `dei_live/` | Registered AgentDojo/live-model harness, analysis, registration, and tests |
| `results/` | Raw RQ1–RQ4 and AgentDyn JSONL logs plus generated LaTeX result macros |
| `testbed/czta_v9/` | Replacement-2 CZTA gateway, reference implementation, and RQ5 testbed |
| `reference_semantics/` | Executable monitor, constructed red-team suite, and property tests |
| `formal/` | Lean 4 safety development, check script, and recorded kernel-check log |
| `scoping_review/` | Protocol, search records, codebooks, validation, and reliability-audit materials |
| `validation/` | Power and registration-audit outputs |
| `docs/` | Final validation, RQ4(b) limitation, and AgentDyn provenance metadata |

## Status and interpretation

RQ1–RQ5 are complete. Development measurements are labeled separately from
held-out results. RQ4(b) is completed but uninformative. AgentDyn is a
completed dynamic-suite replication; suite-generality remains bounded by its
task and model coverage. The registration files under `dei_live/registration/`
preserve the **pre-run** design, including the original AgentDyn not-run
decision. The final execution record is in `docs/FINAL_VALIDATION.md` and the
`results/` directory, not in that historical registration decision.

## Verification

Use an isolated Python environment and install the harness dependencies:
`agentdojo==0.1.35`, `openai`, and `tenacity`. The CZTA testbed has its own
`testbed/czta_v9/requirements.txt`.

```bash
# Integrity of every file in this repository
sha256sum -c MANIFEST.sha256

# Live-harness offline tests
cd dei_live
python3 -I test_dei_live.py
python3 -I test_analyze.py
python3 -I test_probes.py
python3 power_verify.py
python3 validate_registration.py

# Executable reference-semantics property tests
cd ../reference_semantics
python3 -I test_monitor.py

# Manuscript source regeneration (optional; main.tex is already assembled)
cd ../manuscript
python3 -I build/assemble.py
```

Compile `manuscript/main.tex` with the bundled `IEEEtran.cls` using the normal
Overleaf workflow or an equivalent IEEEtran-compatible LaTeX installation.
The Lean development can be re-checked with `formal/check_formal.sh` on a
machine with the Lean 4 toolchain installed.

## Anonymity and data handling

The manuscript uses an anonymous byline and contains no author affiliation or
acknowledgment metadata. Before publication or mirror refresh, review binary
PDFs and images as well as text for identifying information. The scoping
review releases bibliographic records and role-labelled codes, not personal
information about annotators. API keys, endpoint credentials, production
tokens, and non-public infrastructure details must not be added to this
repository.
