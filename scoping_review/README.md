# Epistemic Security PRISMA full record validation package — v8.0.0

This restricted internal package supplies the complete record-level audit requested for the PRISMA-ScR-aligned abstract evidence map.

## Core files

- `03_records/ALL_IDENTIFIED_6512_FULL_WITH_ABSTRACTS.csv`: every identified row, including duplicate mapping, exact query, final canonical disposition, rationale, and hash validation.
- `03_records/UNIQUE_SCREENED_2383_FULL_WITH_ABSTRACTS.csv`: every unique screened record with final decision and comment.
- `03_records/INCLUDED_CORE_552_FULL_WITH_ABSTRACTS.csv`
- `03_records/INCLUDED_BACKGROUND_931_FULL_WITH_ABSTRACTS.csv`
- `03_records/EXCLUDED_900_FULL_WITH_ABSTRACTS.csv`
- `03_records/DUPLICATES_4129_FULL_WITH_ABSTRACTS.csv`
- `03_records/CORE_552_FULL_CHARTING_WITH_ABSTRACTS.csv`
- `03_records/FOUNDATIONAL_118_SOURCES.csv` and `.bib`
- `02_search/EXECUTED_SEARCH_LEDGER_17.csv`: exact executed query ledger.
- `02_search/SEARCH_AND_SCREENING_PROMPTS_FULL.md`: all executed database queries and the retained screening prompt.
- `05_records_by_executed_query/`: one complete record file for each of the 17 executed exports.
- `04_records_by_database/`: one complete record file for each of the six exported sources.
- `06_validation/FULL_VALIDATION_REPORT.md`: limitations, repairs, and validation findings.

## Count reconciliation

6,512 identified - 4,129 duplicates = 2,383 screened = 552 core + 931 background + 900 excluded.

## Important limitation

This is an abstract-level map. It does not contain completed human double-screening or full-text eligibility/appraisal results. Those activities must not be inferred from the presence of prospective calibration and full-text protocol files.

## Sharing

See `RIGHTS_AND_SHARING_BOUNDARY.md` before public redistribution.
