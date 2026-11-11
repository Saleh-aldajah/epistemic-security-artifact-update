# P3 exact executed-search report

**Search execution date:** 24 May 2026  
**Final record-level adjudication:** 11 July 2026  
**Scope:** PRISMA-S execution ledger for the abstract-level evidence map.

## Accounting boundary

Only the 17 database/query exports listed below contribute to the PRISMA flow. The broader search-string library also contains candidate strategies that were prepared but not executed; those strategies are identified separately and do not contribute records, duplicates, screening decisions, or evidence-map frequencies.

The executed ledger reconciles to **6,512 raw records**, **4,129 duplicate records**, and **2,383 unique records screened**.

## Source-level totals

| Source | Executed exports | Raw records | Duplicates | Unique records | Core | Background | Excluded |
|---|---:|---:|---:|---:|---:|---:|---:|
| ACM Digital Library | 3 | 2,233 | 1,495 | 738 | 65 | 247 | 426 |
| IEEE Xplore | 3 | 626 | 260 | 366 | 144 | 144 | 78 |
| Scopus | 3 | 2,296 | 1,132 | 1,164 | 318 | 506 | 340 |
| Web of Science Core Collection | 3 | 1,311 | 1,214 | 97 | 11 | 32 | 54 |
| Semantic Scholar | 3 | 38 | 20 | 18 | 14 | 2 | 2 |
| USENIX Security/SOUPS | 2 | 8 | 8 | 0 | 0 | 0 | 0 |
| **Total** | **17** | **6,512** | **4,129** | **2,383** | **552** | **931** | **900** |

The two records marked uncertain in the export manifest were resolved during final adjudication; the released final decision file contains zero unresolved records.

## Exact executed strategies and export counts

### ACM Digital Library

#### P3-ACM-broad (broad)

- **Search date:** 2026-05-24
- **Date range and limits:** 2017-2026; foundational human-factors and cognition papers may be included through backward snowballing
- **Export fields:** title; authors; year; venue; abstract; DOI; URL; source; citation count; keywords; document type; affiliations; references if available
- **Accounting:** 745 identified; 745 duplicates; 0 unique; 0 core; 0 background; 0 excluded (final dispositions); 0 uncertain before final adjudication.
- **Exact search string:**

```text
("retrieval augmented generation" OR RAG OR "LLM agent" OR "AI agent" OR "decision support" OR "human-AI" OR "human AI" OR "tool-using agent") AND ("prompt injection" OR poisoning OR misinformation OR disinformation OR "source credibility" OR provenance OR lineage OR attestation OR "trust calibration" OR "epistemic")  [Advanced Search in ACM Guide to Computing Literature; filter Publication Date: 2017-2026]
```

#### P3-ACM-focused (focused)

- **Search date:** 2026-05-24
- **Date range and limits:** 2017-2026; foundational human-factors and cognition papers may be included through backward snowballing
- **Export fields:** title; authors; year; venue; abstract; DOI; URL; source; citation count; keywords; document type; affiliations; references if available
- **Accounting:** 745 identified; 11 duplicates; 734 unique; 65 core; 247 background; 422 excluded (final dispositions); 2 uncertain before final adjudication.
- **Exact search string:**

```text
("retrieval augmented generation" OR RAG OR "LLM agent" OR "AI agent" OR "decision support" OR "human-AI" OR "human AI" OR "tool-using agent") AND ("prompt injection" OR poisoning OR misinformation OR disinformation OR "source credibility" OR provenance OR lineage OR attestation OR "trust calibration" OR "epistemic") AND (security OR integrity OR governance OR audit OR calibration OR "zero trust" OR forensic OR accountability OR cognition)  [Advanced Search in ACM Guide to Computing Literature; filter Publication Date: 2017-2026]
```

#### P3-ACM-survey (survey)

- **Search date:** 2026-05-24
- **Date range and limits:** 2017-2026; foundational human-factors and cognition papers may be included through backward snowballing
- **Export fields:** title; authors; year; venue; abstract; DOI; URL; source; citation count; keywords; document type; affiliations; references if available
- **Accounting:** 743 identified; 739 duplicates; 4 unique; 0 core; 0 background; 4 excluded (final dispositions); 0 uncertain before final adjudication.
- **Exact search string:**

```text
("retrieval augmented generation" OR RAG OR "LLM agent" OR "AI agent" OR "decision support" OR "human-AI" OR "human AI" OR "tool-using agent") AND (survey OR taxonomy OR systematization OR SoK OR "systematic review" OR benchmark) AND ("prompt injection" OR poisoning OR misinformation OR disinformation OR "source credibility" OR provenance OR lineage OR attestation OR "trust calibration" OR "epistemic")  [Advanced Search in ACM Guide to Computing Literature; filter Publication Date: 2017-2026]
```

### IEEE Xplore

#### P3-IEEE-broad (broad)

- **Search date:** 2026-05-24
- **Date range and limits:** 2017-2026; foundational human-factors and cognition papers may be included through backward snowballing
- **Export fields:** title; authors; year; venue; abstract; DOI; URL; source; citation count; keywords; document type; affiliations; references if available
- **Accounting:** 366 identified; 225 duplicates; 141 unique; 37 core; 56 background; 48 excluded (final dispositions); 0 uncertain before final adjudication.
- **Exact search string:**

```text
(("retrieval augmented generation" OR RAG OR "LLM agent" OR "AI agent" OR "decision support" OR "human-AI" OR "human AI" OR "tool-using agent") AND ("prompt injection" OR poisoning OR misinformation OR disinformation OR "source credibility" OR provenance OR lineage OR attestation OR "trust calibration" OR "epistemic"))  [Command Search; filter Years: 2017-2026; content type: Conferences/Journals/Early Access]
```

#### P3-IEEE-focused (focused)

- **Search date:** 2026-05-24
- **Date range and limits:** 2017-2026; foundational human-factors and cognition papers may be included through backward snowballing
- **Export fields:** title; authors; year; venue; abstract; DOI; URL; source; citation count; keywords; document type; affiliations; references if available
- **Accounting:** 191 identified; 0 duplicates; 191 unique; 91 core; 73 background; 27 excluded (final dispositions); 0 uncertain before final adjudication.
- **Exact search string:**

```text
(("retrieval augmented generation" OR RAG OR "LLM agent" OR "AI agent" OR "decision support" OR "human-AI" OR "human AI" OR "tool-using agent") AND ("prompt injection" OR poisoning OR misinformation OR disinformation OR "source credibility" OR provenance OR lineage OR attestation OR "trust calibration" OR "epistemic") AND (security OR integrity OR governance OR audit OR calibration OR "zero trust" OR forensic OR accountability OR cognition))  [Command Search; filter Years: 2017-2026; content type: Conferences/Journals/Early Access]
```

#### P3-IEEE-survey (survey)

- **Search date:** 2026-05-24
- **Date range and limits:** 2017-2026; foundational human-factors and cognition papers may be included through backward snowballing
- **Export fields:** title; authors; year; venue; abstract; DOI; URL; source; citation count; keywords; document type; affiliations; references if available
- **Accounting:** 69 identified; 35 duplicates; 34 unique; 16 core; 15 background; 3 excluded (final dispositions); 0 uncertain before final adjudication.
- **Exact search string:**

```text
(("retrieval augmented generation" OR RAG OR "LLM agent" OR "AI agent" OR "decision support" OR "human-AI" OR "human AI" OR "tool-using agent") AND (survey OR taxonomy OR systematization OR SoK OR "systematic review" OR benchmark) AND ("prompt injection" OR poisoning OR misinformation OR disinformation OR "source credibility" OR provenance OR lineage OR attestation OR "trust calibration" OR "epistemic"))  [Command Search; filter Years: 2017-2026; content type: Conferences/Journals/Early Access]
```

### Scopus

#### P3-SCOPUS-broad (broad)

- **Search date:** 2026-05-24
- **Date range and limits:** 2017-2026; foundational human-factors and cognition papers may be included through backward snowballing
- **Export fields:** title; authors; year; venue; abstract; DOI; URL; source; citation count; keywords; document type; affiliations; references if available
- **Accounting:** 1,523 identified; 360 duplicates; 1,163 unique; 318 core; 505 background; 340 excluded (final dispositions); 0 uncertain before final adjudication.
- **Exact search string:**

```text
TITLE-ABS-KEY(("retrieval augmented generation" OR RAG OR "LLM agent" OR "AI agent" OR "decision support" OR "human-AI" OR "human AI" OR "tool-using agent") AND ("prompt injection" OR poisoning OR misinformation OR disinformation OR "source credibility" OR provenance OR lineage OR attestation OR "trust calibration" OR "epistemic")) AND PUBYEAR > 2016 AND PUBYEAR < 2027
```

#### P3-SCOPUS-focused (focused)

- **Search date:** 2026-05-24
- **Date range and limits:** 2017-2026; foundational human-factors and cognition papers may be included through backward snowballing
- **Export fields:** title; authors; year; venue; abstract; DOI; URL; source; citation count; keywords; document type; affiliations; references if available
- **Accounting:** 561 identified; 560 duplicates; 1 unique; 0 core; 1 background; 0 excluded (final dispositions); 0 uncertain before final adjudication.
- **Exact search string:**

```text
TITLE-ABS-KEY(("retrieval augmented generation" OR RAG OR "LLM agent" OR "AI agent" OR "decision support" OR "human-AI" OR "human AI" OR "tool-using agent") AND ("prompt injection" OR poisoning OR misinformation OR disinformation OR "source credibility" OR provenance OR lineage OR attestation OR "trust calibration" OR "epistemic") AND (security OR integrity OR governance OR audit OR calibration OR "zero trust" OR forensic OR accountability OR cognition)) AND PUBYEAR > 2016 AND PUBYEAR < 2027
```

#### P3-SCOPUS-survey (survey)

- **Search date:** 2026-05-24
- **Date range and limits:** 2017-2026; foundational human-factors and cognition papers may be included through backward snowballing
- **Export fields:** title; authors; year; venue; abstract; DOI; URL; source; citation count; keywords; document type; affiliations; references if available
- **Accounting:** 212 identified; 212 duplicates; 0 unique; 0 core; 0 background; 0 excluded (final dispositions); 0 uncertain before final adjudication.
- **Exact search string:**

```text
TITLE-ABS-KEY(("retrieval augmented generation" OR RAG OR "LLM agent" OR "AI agent" OR "decision support" OR "human-AI" OR "human AI" OR "tool-using agent") AND (survey OR taxonomy OR systematization OR SoK OR "systematic review" OR benchmark) AND ("prompt injection" OR poisoning OR misinformation OR disinformation OR "source credibility" OR provenance OR lineage OR attestation OR "trust calibration" OR "epistemic")) AND PUBYEAR > 2016 AND PUBYEAR < 2027
```

### Web of Science Core Collection

#### P3-WEB-broad (broad)

- **Search date:** 2026-05-24
- **Date range and limits:** 2017-2026; foundational human-factors and cognition papers may be included through backward snowballing
- **Export fields:** title; authors; year; venue; abstract; DOI; URL; source; citation count; keywords; document type; affiliations; references if available
- **Accounting:** 902 identified; 805 duplicates; 97 unique; 11 core; 32 background; 54 excluded (final dispositions); 0 uncertain before final adjudication.
- **Exact search string:**

```text
TS=(("retrieval augmented generation" OR RAG OR "LLM agent" OR "AI agent" OR "decision support" OR "human-AI" OR "human AI" OR "tool-using agent") AND ("prompt injection" OR poisoning OR misinformation OR disinformation OR "source credibility" OR provenance OR lineage OR attestation OR "trust calibration" OR "epistemic")) AND PY=(2017-2026)
```

#### P3-WEB-focused (focused)

- **Search date:** 2026-05-24
- **Date range and limits:** 2017-2026; foundational human-factors and cognition papers may be included through backward snowballing
- **Export fields:** title; authors; year; venue; abstract; DOI; URL; source; citation count; keywords; document type; affiliations; references if available
- **Accounting:** 282 identified; 282 duplicates; 0 unique; 0 core; 0 background; 0 excluded (final dispositions); 0 uncertain before final adjudication.
- **Exact search string:**

```text
TS=(("retrieval augmented generation" OR RAG OR "LLM agent" OR "AI agent" OR "decision support" OR "human-AI" OR "human AI" OR "tool-using agent") AND ("prompt injection" OR poisoning OR misinformation OR disinformation OR "source credibility" OR provenance OR lineage OR attestation OR "trust calibration" OR "epistemic") AND (security OR integrity OR governance OR audit OR calibration OR "zero trust" OR forensic OR accountability OR cognition)) AND PY=(2017-2026)
```

#### P3-WEB-survey (survey)

- **Search date:** 2026-05-24
- **Date range and limits:** 2017-2026; foundational human-factors and cognition papers may be included through backward snowballing
- **Export fields:** title; authors; year; venue; abstract; DOI; URL; source; citation count; keywords; document type; affiliations; references if available
- **Accounting:** 127 identified; 127 duplicates; 0 unique; 0 core; 0 background; 0 excluded (final dispositions); 0 uncertain before final adjudication.
- **Exact search string:**

```text
TS=(("retrieval augmented generation" OR RAG OR "LLM agent" OR "AI agent" OR "decision support" OR "human-AI" OR "human AI" OR "tool-using agent") AND (survey OR taxonomy OR systematization OR SoK OR "systematic review" OR benchmark) AND ("prompt injection" OR poisoning OR misinformation OR disinformation OR "source credibility" OR provenance OR lineage OR attestation OR "trust calibration" OR "epistemic")) AND PY=(2017-2026)
```

### Semantic Scholar

#### P3-SEMANTIC-broad (broad)

- **Search date:** 2026-05-24
- **Date range and limits:** 2017-2026; foundational human-factors and cognition papers may be included through backward snowballing
- **Export fields:** title; authors; year; venue; abstract; DOI; URL; source; citation count; keywords; document type; affiliations; references if available
- **Accounting:** 18 identified; 5 duplicates; 13 unique; 9 core; 2 background; 2 excluded (final dispositions); 0 uncertain before final adjudication.
- **Exact search string:**

```text
retrieval augmented generation RAG LLM agent prompt injection poisoning misinformation disinformation
```

#### P3-SEMANTIC-focused (focused)

- **Search date:** 2026-05-24
- **Date range and limits:** 2017-2026; foundational human-factors and cognition papers may be included through backward snowballing
- **Export fields:** title; authors; year; venue; abstract; DOI; URL; source; citation count; keywords; document type; affiliations; references if available
- **Accounting:** 10 identified; 5 duplicates; 5 unique; 5 core; 0 background; 0 excluded (final dispositions); 0 uncertain before final adjudication.
- **Exact search string:**

```text
retrieval augmented generation RAG LLM agent prompt injection poisoning misinformation disinformation security robustness provenance
```

#### P3-SEMANTIC-survey (survey)

- **Search date:** 2026-05-24
- **Date range and limits:** 2017-2026; foundational human-factors and cognition papers may be included through backward snowballing
- **Export fields:** title; authors; year; venue; abstract; DOI; URL; source; citation count; keywords; document type; affiliations; references if available
- **Accounting:** 10 identified; 10 duplicates; 0 unique; 0 core; 0 background; 0 excluded (final dispositions); 0 uncertain before final adjudication.
- **Exact search string:**

```text
retrieval augmented generation RAG LLM agent prompt injection poisoning misinformation disinformation survey taxonomy benchmark
```

### USENIX Security/SOUPS

#### P3-USENIX-broad (broad)

- **Search date:** 2026-05-24
- **Date range and limits:** 2017-2026; foundational human-factors and cognition papers may be included through backward snowballing
- **Export fields:** title; authors; year; venue; abstract; DOI; URL; source; citation count; keywords; document type; affiliations; references if available
- **Accounting:** 4 identified; 4 duplicates; 0 unique; 0 core; 0 background; 0 excluded (final dispositions); 0 uncertain before final adjudication.
- **Exact search string:**

```text
site:usenix.org (("retrieval augmented generation" OR RAG OR "LLM agent" OR "AI agent" OR "decision support" OR "human-AI" OR "human AI" OR "tool-using agent") AND ("prompt injection" OR poisoning OR misinformation OR disinformation OR "source credibility" OR provenance OR lineage OR attestation OR "trust calibration" OR "epistemic")) after:2017-01-01 before:2027-01-01
```

#### P3-USENIX-focused (focused)

- **Search date:** 2026-05-24
- **Date range and limits:** 2017-2026; foundational human-factors and cognition papers may be included through backward snowballing
- **Export fields:** title; authors; year; venue; abstract; DOI; URL; source; citation count; keywords; document type; affiliations; references if available
- **Accounting:** 4 identified; 4 duplicates; 0 unique; 0 core; 0 background; 0 excluded (final dispositions); 0 uncertain before final adjudication.
- **Exact search string:**

```text
site:usenix.org (("retrieval augmented generation" OR RAG OR "LLM agent" OR "AI agent" OR "decision support" OR "human-AI" OR "human AI" OR "tool-using agent") AND ("prompt injection" OR poisoning OR misinformation OR disinformation OR "source credibility" OR provenance OR lineage OR attestation OR "trust calibration" OR "epistemic") AND (security OR integrity OR governance OR audit OR calibration OR "zero trust" OR forensic OR accountability OR cognition)) after:2017-01-01 before:2027-01-01
```

## Prepared but not executed strategies

The following entries remain in the strategy library for transparency but were not executed as independent exports and are excluded from all PRISMA counts:

- **Crossref:** P3-CROSSREF-broad, P3-CROSSREF-focused, P3-CROSSREF-survey
- **DBLP:** P3-DBLP-broad, P3-DBLP-focused, P3-DBLP-survey
- **NDSS Symposium:** P3-NDSS-broad, P3-NDSS-focused, P3-NDSS-survey
- **USENIX Security/SOUPS:** P3-USENIX-survey
- **arXiv:** P3-ARXIV-broad, P3-ARXIV-focused, P3-ARXIV-survey

For USENIX Security/SOUPS, the broad and focused site-derived searches were executed. The prepared survey query was not separately exported and is therefore listed here as not executed.

## Reproduction notes

Database interfaces and indexes change over time, so rerunning the exact strings after the cutoff may produce different counts. The auditable public object for this review is the rights-cleared identification ledger, restricted-input checksum manifest, record-level decisions and fingerprints, and this execution ledger. Access-controlled databases may require institutional subscriptions. The strategy was not independently PRESS-reviewed, and no search update was performed after 24 May 2026; both are reported as limitations.
