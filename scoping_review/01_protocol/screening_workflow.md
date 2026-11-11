# Screening Workflow

Prepared: 2026-05-24

## Roles

- Lead reviewer: owns query execution, deduplication, adjudication, and final PRISMA counts.
- Coder A and Coder B: independently screen the calibration set and the 20 percent stratified reliability sample.
- Domain adjudicator: resolves persistent disagreements where technical interpretation is disputed.

## Stage 0: calibration

1. Select 20 records per paper from the seed corpus: 10 likely include, 5 likely exclude, 5 ambiguous.
2. Coders independently classify each record as include_core, include_background, exclude, duplicate, superseded, or uncertain.
3. Discuss disagreements and update the coding dictionary before formal screening.

## Stage 1: identification

Execute the database search strings and log raw hit counts. Store raw exports under `data/raw/<paper_id>/<database>/`. Do not edit raw exports.

## Stage 2: deduplication

Deduplicate in this order: DOI, arXiv ID, exact normalized title, fuzzy normalized title plus first author/year, and manual adjudication for near duplicates.

## Stage 3: title/abstract screening

Each record receives one screening decision and, if excluded, one primary exclusion reason. Ambiguous records should proceed to full-text review rather than being excluded early.

## Stage 4: full-text eligibility

Retrieve the full text. Code ineligible records with a single dominant reason. For superseded preprints, include the published version and retain the preprint only as a linked duplicate.

## Stage 5: full coding

Code all included core records on common and paper-specific dimensions. Background-only records are not used in taxonomy counts unless explicitly stated.

## Stage 6: reliability and adjudication

Compute kappa before adjudication. After adjudication, freeze `screening_decisions_final.csv` and regenerate PRISMA counts.

## File naming convention

`<paper_id>_<database>_<query_id>_<YYYYMMDD>.<ext>`

Example: `P4_SemanticScholar_P4-SEMANTIC-focused_20260524.jsonl`.
