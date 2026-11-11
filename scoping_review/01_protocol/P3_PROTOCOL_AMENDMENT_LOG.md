# P3 protocol amendment and deviation log

**Parent protocol:** `AI_Security_PRISMA_Master_Protocol.md` (prepared 24 May 2026)  
**Paper:** P3 — Epistemic Security in Distributed Human–AI Systems  
**Finalized for submission:** 11 July 2026  
**Registration status:** The protocol was retained in the project but was not prospectively registered in an external registry.

## Purpose of this log

The parent protocol was a portfolio-level workflow that anticipated full-text eligibility review, dual human coding, and a wider set of candidate databases for four papers. P3 was completed as an **abstract-level scoping evidence map embedded in a security SoK**, not as a full-text systematic review. This log records every material P3 deviation so readers can distinguish prespecified intentions from the implemented review.

## Amendments and deviations

| ID | Implemented change | Timing/status | Rationale and consequence |
|---|---|---|---|
| P3-A1 | The unit of synthesis was fixed as the bibliographic record plus title/abstract. Full-text retrieval, report-level exclusion, risk-of-bias appraisal, and effect synthesis were not eligibility stages. | Implemented during P3 corpus finalization; documented before submission but after search execution. | The objective is breadth-oriented mapping of mechanisms, controls, and evidence types. Results cannot establish study quality, intervention effects, or whether an abstract overstates the full paper. |
| P3-A2 | The executed search was bounded to ACM Digital Library, IEEE Xplore, Scopus, Web of Science Core Collection, Semantic Scholar, and USENIX Security/SOUPS. | Searches executed 24 May 2026. | Candidate strategies for NDSS, arXiv, Crossref, and DBLP were prepared but not executed as independent exports. They do not contribute to PRISMA counts. The exact 17 executed exports are isolated in `P3_executed_search_strategies.csv` and `P3_EXECUTED_SEARCH_REPORT.md`. |
| P3-A3 | Title/abstract screening was conducted in five fixed AI-assisted batches using the versioned instructions in `P3_CHATGPT_SCREENING_INSTRUCTIONS.md`. | Implemented before final adjudication. | The released decisions and one-sentence rationales are the audit object. The exact hosted model build, decoding parameters, and complete interaction transcript were not preserved; therefore the screening step is not claimed to be exactly model-rerunnable or equivalent to dual independent human screening. |
| P3-A4 | Two records initially marked uncertain were resolved by final record-level adjudication from the available title/abstract metadata: one to background and one to exclusion for no technical content. | 11 July 2026. | The final file contains zero unresolved records. The original uncertain state remains recoverable in the batch and manifest artifacts. |
| P3-A5 | Full-corpus charting over all 552 core records used two independently specified transparent lexical implementations followed by a deterministic adjudication rule; the reported corpus-wide attack-class prevalence is that computational map. Its two-implementation agreement is a computational reproducibility/stability audit, not human inter-rater reliability. | Implemented during final evidence-map construction. | Attack-class prevalence over the full corpus is the principal quantitative result. Human inter-rater reliability is established separately on a frozen sample under amendment P3-A11, and lower-stability charting dimensions remain exploratory. |
| P3-A6 | The charting schema was expanded to include evidence tier and evaluation evidence in addition to the P3 dimensions listed in the parent protocol. | Implemented before final synthesis. | The added dimensions support evidence-maturity and evaluation-gap analysis. Definitions and rules are released in the coding dictionary and finalizer script. |
| P3-A7 | A model-independent CZTA reference-monitor benchmark and signed reasoning-lineage artifact were added as a constructive systems contribution separate from the review. | Added after evidence-map synthesis and completed before submission. | The benchmark tests encoded policy and lineage invariants on synthetic SOC episodes. It is not evidence about LLM accuracy, human performance, or production effectiveness. Policy code does not read attack/scoring labels; regression tests enforce this separation. |
| P3-A8 | No search update was performed after 24 May 2026, and the search strategy was not independently PRESS-reviewed. | Final submission boundary. | Both are explicit limitations. Database reruns after the cutoff may yield different counts. |
| P3-A9 | The scoping review and the CZTA benchmark use public bibliographic metadata and synthetic/local tests with no recruited participants, identifiable personal data, live infrastructure, or operational exploitation. The reliability sub-study (P3-A11) engaged expert annotators to code publicly available record metadata (titles/abstracts) against the codebook; it collected no personal or sensitive data about the annotators and released only their per-record codes under role labels. | Final submission boundary. | Consistent with the paper's Ethics Considerations. Future human-subjects studies involving participant data (e.g. the planned operator human-factors study) require prospective ethics review, which is noted as pending in the paper. |
| P3-A10 | The original platform-native database export files were not present in the supplied project. The combined normalized corpus is the earliest retained record-level object. | Discovered during final reproducibility audit; documented before submission. | The public 6,512-row identification ledger preserves record identifiers, source/query metadata, dispositions, available DOIs, and SHA-256 fingerprints; a restricted-input manifest records the internal normalized corpus by digest. Native RIS/BibTeX/CSV exports cannot be independently inspected, and no reconstructed file is labeled as an original export. |

| P3-A11 | A human inter-rater reliability sub-study was conducted on the frozen 20% audit sample (n=114). Two domain experts independently coded eligibility and primary attack class, blind to all automated labels and to each other; a third expert adjudicated the 44 records with an eligibility- or class-level disagreement to seal a reference standard (98 core / 11 background / 5 exclude). Coder validity was protected by tokenized per-coder instruments, per-coder row shuffling, receipt hashing, and forensic quality gates; two coding passes that failed pre-registered gates (a skipped calibration; a physically implausible return time with baseline-level note specificity) were invalidated and a replacement expert coded under strengthened terms. All invalidated passes are excluded from every statistic. | Conducted after initial evidence-map construction; sealed 15 July 2026. | Reportable reliability: human-human eligibility kappa=0.24 / Gwet AC1=0.77 (prevalence-depressed kappa; Gwet rationale pre-registered); human-human attack-class kappa=0.70 / AC1=0.72 (n=106 co-classed pairs); human-automation attack-class kappa=0.48 / AC1=0.52 on the 98 adjudicated-core records, versus 0.83 pipeline self-agreement (reported as a validity finding). Positive predictive value of core inclusion 0.86 (Wilson 95% CI 0.78-0.91). Because the frozen sample is all pipeline-positive, screening sensitivity/specificity are not identifiable from it; a disjoint pipeline-negatives stratum (NS-114) is registered but uncoded at submission. Coder sheets, adjudication file, and instructions ship in 09_human_reliability_audit/ with an anonymous record_key that reproduces these statistics without exposing full-text. |
## Final implemented design

- **Identification:** 6,512 exported records from 17 executed query exports across six sources.
- **Deduplication:** 4,129 duplicate records removed; 2,383 unique records retained.
- **Screening:** five AI-assisted title/abstract batches plus final adjudication.
- **Final states:** 552 core records, 931 contextual/background records, 900 exclusions, zero unresolved.
- **Charting:** eight dimensions over the 552-record core map using two transparent implementations and deterministic adjudication.
- **Human reliability sub-study (P3-A11):** two experts independently coded a frozen 20% sample (n=114) blind to automated labels; a third expert adjudicated 44 disagreements to seal a 98/11/5 reference standard. Human inter-rater reliability: eligibility kappa=0.24/AC1=0.77, class kappa=0.70/AC1=0.72 (n=106).
- **Separate foundational corpus:** 118 standards and backward-snowballed sources used for conceptual synthesis but excluded from map frequencies.
- **Constructive evaluation:** deterministic reference-monitor benchmark, control ablations, ten-seed sensitivity analysis, signed lineage example, schema validation, tamper test, and label-leakage regression test.

## Bias and interpretation statement

Because several amendments were documented after search execution and original platform-native exports were unavailable, the corpus-wide map should be interpreted as a transparent, reproducible **abstract evidence map**, not as a definitive full-text systematic review. The primary AI-assisted screening pass was not itself duplicated by dual human screening across the full corpus; instead, a frozen 20% sample received independent human double-coding and third-expert adjudication (P3-A11), which is the study's human-reliability evidence and is reported with its limitations (notably that the all-positive sample leaves screening sensitivity/specificity unidentifiable pending NS-114). Releasing rights-cleared row-level identifiers, decisions, rationales, both charting outputs, final labels, fingerprints, exact strategies, and accounting enables independent auditing and re-analysis of public outputs but does not remove provenance, selection, or classification bias. Re-running lexical coding requires lawful access to the omitted source text.

## 2026-07-11 - Reviewer-rescue amendment v3.0.0

- Preserved the abstract-level eligibility unit and original computational code matrix.
- Revalidated all 91 broad signed/cryptographic candidates using a high-specificity title/abstract rule.
- Added the additive `Lineage evidence v3` field rather than overwriting the v2 label.
- Corrected explicit cryptographic/attestation evidence to 9/552 and no-explicit-lineage evidence to 196/552.
- Added prospective protocols for full-text extraction and two-expert coding of the deterministic 114-record audit sample.
- Explicitly records that full-text appraisal and human calibration were not performed in this release.
- Added agent identity, earned autonomy, MCP gateway, bounded trust analytics, RLA v2.0, and control-plane diagnostic artifacts outside the evidence-map denominator.

## 2026-07-11 - Reviewer-rescue amendment v4.0.0

- Preserved all executed search, record-screening, map-frequency, and v3 lineage-correction data without changing denominators.
- Added prospective human-factors, consumer health/finance, organizational-incentive, and multilingual validation protocols outside the evidence-map denominator.
- Added signed localization and translation state to RLA v2.1 and two deterministic regression tests.
- Added a deterministic power-planning sensitivity; no participant data or effect estimate is reported.

## 2026-07-12 - Reviewer-rescue amendment v6.0.0

- Added governance-quorum, degraded-safe localization UX, and consumer-health KPI calibration as constructive/prospective extensions.
- Updated RLA to v2.2 and the regression suite to 21 tests.
- Did not alter search execution, eligibility, screening, charting, PRISMA accounting, evidence-map frequencies, or benchmark outcomes.
- Governance examples use deterministic test keys; pilot-calibration rows are synthetic; no human or field result is claimed.
