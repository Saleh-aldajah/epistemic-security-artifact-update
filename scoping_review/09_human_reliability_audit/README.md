# Human Reliability Audit (n=114) — reproducibility

This is the human inter-rater reliability sub-study for the scoping review's
attack-class charting (paper Section on the audit; amendment log P3-A11).

## Files
- coder_B_sheet_completed.csv       Coder B, 114 records (eligibility + class)
- coder_Aprime_round3_sheet.csv     Coder A' (validated replacement), 114 records
- coder_A_sheet.csv,                original Coder A passes (INVALIDATED under
  coder_A_round2_sheet_classified.csv   forensic gates; retained for transparency,
                                        excluded from all statistics)
- calibration_sheet.csv             15-record calibration set
- adjudication_WAVE1_completed.csv  Expert 3's 44 adjudicated disagreements
                                    (assessment_1/2 in randomized order + finals)
- ADJUDICATOR_INSTRUCTIONS.md       the blind adjudication protocol
- crosswalk_ground_truth.json       class -> invariant crosswalk reference

## record_key
Each coder received a differently-tokenized sheet (per-coder row shuffling was a
validity control), so the raw `token` columns do NOT align across coders. A
`record_key` column (a stable hash of the record title) is provided so the two
coders and the adjudicator can be joined WITHOUT any title/abstract text in the
public release. Titles/abstracts themselves are omitted per the rights boundary.

## Reproduce the reported statistics
Join coder_B and coder_Aprime on record_key. Then:
- Human-human ELIGIBILITY agreement over all 114 -> kappa = 0.24, Gwet AC1 = 0.77
- Human-human CLASS agreement over co-classed pairs (n=106) -> kappa = 0.70, AC1 = 0.72
- Reference standard = agreements + Expert-3 adjudication of disagreements
  -> 98 core / 11 background / 5 exclude
- Human-automation CLASS (adjudicated core vs pipeline label) -> kappa = 0.48, AC1 = 0.52
- PPV of core inclusion = 0.86 (Wilson 95% CI 0.78-0.91)

An independent recomputation from these sheets reproduces the eligibility
kappa (0.235) and the 98/11/5 ground truth exactly. Class kappa depends on the
co-classing rule (pairs where both coders assigned a class); the sealed pipeline
value is 0.70 at n=106.

## Note on the invalidated Coder A passes
Two Coder A passes failed pre-registered forensic gates (a skipped calibration in
one; a physically implausible completion time with baseline-level note specificity
in the other). They were invalidated, the engagement terminated, and Coder A'
coded under strengthened terms. The invalidated files are included ONLY for audit
transparency and contribute to NO reported statistic. See amendment log P3-A11.
