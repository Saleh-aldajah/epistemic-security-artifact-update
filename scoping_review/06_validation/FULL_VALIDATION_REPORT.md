# Full PRISMA record-level validation report — v8.0.0

## Executive result

The retained corpus reconciles to **6,512 identified records across 17 executed query exports**, **4,129 duplicates**, and **2,383 unique title/abstract records screened**. Final decisions are **552 core**, **931 background**, and **900 excluded**, with **zero unresolved records**. Every unique record has a retained title/abstract screening rationale, and every excluded record has one controlled primary exclusion reason.

## What is complete

- Exact database, query family, search string, search date, date limits, export-field specification, and per-query accounting for all 17 executed exports.
- A full 6,512-row source-text ledger with titles, authors, venue, DOI/URL where retained, and abstracts where present.
- A complete 2,383-row unique screening ledger with final inclusion/exclusion decision and rationale.
- Separate full lists for 552 core records, 931 background records, 900 exclusions, and 4,129 duplicates.
- All 4,129 duplicate rows linked to a canonical retained record. The earlier public ledger left 15 target identifiers blank; this release repairs those links transparently from the retained `dup_of`/`fuzzy_dup_of` notes or exact DOI/title matching.
- The complete 552-row charting matrix, including both computational codebook implementations, agreement flags, confidence labels, and adjudicated labels.
- A separate 118-source foundational/standards bibliography, excluded from evidence-map denominators.
- PRISMA-ScR, PRISMA-S, and PRISMA abstract checklists.

## Methodological boundary

This is a **PRISMA-ScR-aligned abstract evidence map**, not a full-text intervention review. The prespecified unit was the bibliographic record plus title/abstract. Report retrieval, report-level exclusion, effect estimation, and risk-of-bias appraisal were not completed stages. Human calibration and the targeted 91-record full-text lineage appraisal remain prospective protocols; no human-human kappa or full-text mechanism result is claimed.

## Search provenance limitation

The original platform-native ACM, IEEE, Scopus, Web of Science, Semantic Scholar, and USENIX export files were not retained. The earliest retained record-level object is the normalized 6,512-row source-text corpus. Exact strings, dates, field specifications, counts, and record-level source/query assignments are preserved, but the native export files cannot be supplied or independently inspected.

## Screening reproducibility limitation

The screening prompt, batch inputs, decisions, exclusion reasons, and rationales are retained. The exact hosted model build, decoding configuration, and complete interaction transcript are not. The original AI-assisted screening therefore cannot be claimed as exactly model-rerunnable or equivalent to independent human double screening.

## Metadata completeness

- Missing title: 0
- Missing authors: 11
- Missing year: 0
- Missing venue: 8
- Missing DOI: 26
- Missing URL: 1298
- Missing abstract: 17

Missing values are left blank and listed in `03_records/MISSING_METADATA_RECORDS.csv`; none were invented.

## Fingerprint validation finding

The earlier public package documented an NFKC/lowercase/whitespace-collapse SHA-256 specification. Recalculation against the retained 6,512-row source-text snapshot found:

- title hashes: 6390 matches, 122 mismatches;
- abstract hashes: 5563 matches, 949 mismatches;
- combined bibliographic fingerprints: 5517 matches, 995 mismatches.

This does not change any PRISMA counts or decisions, but it means the prior public fingerprints should not be treated as universally aligning to the retained source-text snapshot. The full ledger preserves both the released and recomputed values and identifies every mismatch. The recomputed values are the appropriate alignment hashes for this private package.

## Rights boundary

Because this release contains bulk abstracts and other third-party bibliographic text, it is marked restricted/internal. Public redistribution requires a source-platform and publisher rights review.
