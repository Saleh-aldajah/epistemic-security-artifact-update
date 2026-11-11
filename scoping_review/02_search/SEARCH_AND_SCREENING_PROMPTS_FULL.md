# Exact search, extraction, screening, and charting instructions

**Release:** v8.0.0

## Scope and execution boundary

Only the 17 strategies marked `executed` contributed to PRISMA counts. Thirteen prepared strategies were not executed and contribute zero records. Searches were executed on 24 May 2026, covering 2017–2026.

## Executed database strategies

### P3-ACM-broad — ACM Digital Library (broad)

- Date range: 2017-2026; foundational human-factors and cognition papers may be included through backward snowballing
- Search date: 2026-05-24
- Records identified: 745
- Duplicates removed: 745
- Unique screened: 0
- Core/background/excluded: 0/0/0
- Export fields: title; authors; year; venue; abstract; DOI; URL; source; citation count; keywords; document type; affiliations; references if available

```text
("retrieval augmented generation" OR RAG OR "LLM agent" OR "AI agent" OR "decision support" OR "human-AI" OR "human AI" OR "tool-using agent") AND ("prompt injection" OR poisoning OR misinformation OR disinformation OR "source credibility" OR provenance OR lineage OR attestation OR "trust calibration" OR "epistemic")  [Advanced Search in ACM Guide to Computing Literature; filter Publication Date: 2017-2026]
```

Record listing: `05_records_by_executed_query/P3-ACM-broad__745_records.csv`

### P3-ACM-focused — ACM Digital Library (focused)

- Date range: 2017-2026; foundational human-factors and cognition papers may be included through backward snowballing
- Search date: 2026-05-24
- Records identified: 745
- Duplicates removed: 11
- Unique screened: 734
- Core/background/excluded: 65/247/422
- Export fields: title; authors; year; venue; abstract; DOI; URL; source; citation count; keywords; document type; affiliations; references if available

```text
("retrieval augmented generation" OR RAG OR "LLM agent" OR "AI agent" OR "decision support" OR "human-AI" OR "human AI" OR "tool-using agent") AND ("prompt injection" OR poisoning OR misinformation OR disinformation OR "source credibility" OR provenance OR lineage OR attestation OR "trust calibration" OR "epistemic") AND (security OR integrity OR governance OR audit OR calibration OR "zero trust" OR forensic OR accountability OR cognition)  [Advanced Search in ACM Guide to Computing Literature; filter Publication Date: 2017-2026]
```

Record listing: `05_records_by_executed_query/P3-ACM-focused__745_records.csv`

### P3-ACM-survey — ACM Digital Library (survey)

- Date range: 2017-2026; foundational human-factors and cognition papers may be included through backward snowballing
- Search date: 2026-05-24
- Records identified: 743
- Duplicates removed: 739
- Unique screened: 4
- Core/background/excluded: 0/0/4
- Export fields: title; authors; year; venue; abstract; DOI; URL; source; citation count; keywords; document type; affiliations; references if available

```text
("retrieval augmented generation" OR RAG OR "LLM agent" OR "AI agent" OR "decision support" OR "human-AI" OR "human AI" OR "tool-using agent") AND (survey OR taxonomy OR systematization OR SoK OR "systematic review" OR benchmark) AND ("prompt injection" OR poisoning OR misinformation OR disinformation OR "source credibility" OR provenance OR lineage OR attestation OR "trust calibration" OR "epistemic")  [Advanced Search in ACM Guide to Computing Literature; filter Publication Date: 2017-2026]
```

Record listing: `05_records_by_executed_query/P3-ACM-survey__743_records.csv`

### P3-IEEE-broad — IEEE Xplore (broad)

- Date range: 2017-2026; foundational human-factors and cognition papers may be included through backward snowballing
- Search date: 2026-05-24
- Records identified: 366
- Duplicates removed: 225
- Unique screened: 141
- Core/background/excluded: 37/56/48
- Export fields: title; authors; year; venue; abstract; DOI; URL; source; citation count; keywords; document type; affiliations; references if available

```text
(("retrieval augmented generation" OR RAG OR "LLM agent" OR "AI agent" OR "decision support" OR "human-AI" OR "human AI" OR "tool-using agent") AND ("prompt injection" OR poisoning OR misinformation OR disinformation OR "source credibility" OR provenance OR lineage OR attestation OR "trust calibration" OR "epistemic"))  [Command Search; filter Years: 2017-2026; content type: Conferences/Journals/Early Access]
```

Record listing: `05_records_by_executed_query/P3-IEEE-broad__366_records.csv`

### P3-IEEE-focused — IEEE Xplore (focused)

- Date range: 2017-2026; foundational human-factors and cognition papers may be included through backward snowballing
- Search date: 2026-05-24
- Records identified: 191
- Duplicates removed: 0
- Unique screened: 191
- Core/background/excluded: 91/73/27
- Export fields: title; authors; year; venue; abstract; DOI; URL; source; citation count; keywords; document type; affiliations; references if available

```text
(("retrieval augmented generation" OR RAG OR "LLM agent" OR "AI agent" OR "decision support" OR "human-AI" OR "human AI" OR "tool-using agent") AND ("prompt injection" OR poisoning OR misinformation OR disinformation OR "source credibility" OR provenance OR lineage OR attestation OR "trust calibration" OR "epistemic") AND (security OR integrity OR governance OR audit OR calibration OR "zero trust" OR forensic OR accountability OR cognition))  [Command Search; filter Years: 2017-2026; content type: Conferences/Journals/Early Access]
```

Record listing: `05_records_by_executed_query/P3-IEEE-focused__191_records.csv`

### P3-IEEE-survey — IEEE Xplore (survey)

- Date range: 2017-2026; foundational human-factors and cognition papers may be included through backward snowballing
- Search date: 2026-05-24
- Records identified: 69
- Duplicates removed: 35
- Unique screened: 34
- Core/background/excluded: 16/15/3
- Export fields: title; authors; year; venue; abstract; DOI; URL; source; citation count; keywords; document type; affiliations; references if available

```text
(("retrieval augmented generation" OR RAG OR "LLM agent" OR "AI agent" OR "decision support" OR "human-AI" OR "human AI" OR "tool-using agent") AND (survey OR taxonomy OR systematization OR SoK OR "systematic review" OR benchmark) AND ("prompt injection" OR poisoning OR misinformation OR disinformation OR "source credibility" OR provenance OR lineage OR attestation OR "trust calibration" OR "epistemic"))  [Command Search; filter Years: 2017-2026; content type: Conferences/Journals/Early Access]
```

Record listing: `05_records_by_executed_query/P3-IEEE-survey__69_records.csv`

### P3-USENIX-broad — USENIX Security/SOUPS (broad)

- Date range: 2017-2026; foundational human-factors and cognition papers may be included through backward snowballing
- Search date: 2026-05-24
- Records identified: 4
- Duplicates removed: 4
- Unique screened: 0
- Core/background/excluded: 0/0/0
- Export fields: title; authors; year; venue; abstract; DOI; URL; source; citation count; keywords; document type; affiliations; references if available

```text
site:usenix.org (("retrieval augmented generation" OR RAG OR "LLM agent" OR "AI agent" OR "decision support" OR "human-AI" OR "human AI" OR "tool-using agent") AND ("prompt injection" OR poisoning OR misinformation OR disinformation OR "source credibility" OR provenance OR lineage OR attestation OR "trust calibration" OR "epistemic")) after:2017-01-01 before:2027-01-01
```

Record listing: `05_records_by_executed_query/P3-USENIX-broad__4_records.csv`

### P3-USENIX-focused — USENIX Security/SOUPS (focused)

- Date range: 2017-2026; foundational human-factors and cognition papers may be included through backward snowballing
- Search date: 2026-05-24
- Records identified: 4
- Duplicates removed: 4
- Unique screened: 0
- Core/background/excluded: 0/0/0
- Export fields: title; authors; year; venue; abstract; DOI; URL; source; citation count; keywords; document type; affiliations; references if available

```text
site:usenix.org (("retrieval augmented generation" OR RAG OR "LLM agent" OR "AI agent" OR "decision support" OR "human-AI" OR "human AI" OR "tool-using agent") AND ("prompt injection" OR poisoning OR misinformation OR disinformation OR "source credibility" OR provenance OR lineage OR attestation OR "trust calibration" OR "epistemic") AND (security OR integrity OR governance OR audit OR calibration OR "zero trust" OR forensic OR accountability OR cognition)) after:2017-01-01 before:2027-01-01
```

Record listing: `05_records_by_executed_query/P3-USENIX-focused__4_records.csv`

### P3-SCOPUS-broad — Scopus (broad)

- Date range: 2017-2026; foundational human-factors and cognition papers may be included through backward snowballing
- Search date: 2026-05-24
- Records identified: 1523
- Duplicates removed: 360
- Unique screened: 1163
- Core/background/excluded: 318/505/340
- Export fields: title; authors; year; venue; abstract; DOI; URL; source; citation count; keywords; document type; affiliations; references if available

```text
TITLE-ABS-KEY(("retrieval augmented generation" OR RAG OR "LLM agent" OR "AI agent" OR "decision support" OR "human-AI" OR "human AI" OR "tool-using agent") AND ("prompt injection" OR poisoning OR misinformation OR disinformation OR "source credibility" OR provenance OR lineage OR attestation OR "trust calibration" OR "epistemic")) AND PUBYEAR > 2016 AND PUBYEAR < 2027
```

Record listing: `05_records_by_executed_query/P3-SCOPUS-broad__1523_records.csv`

### P3-SCOPUS-focused — Scopus (focused)

- Date range: 2017-2026; foundational human-factors and cognition papers may be included through backward snowballing
- Search date: 2026-05-24
- Records identified: 561
- Duplicates removed: 560
- Unique screened: 1
- Core/background/excluded: 0/1/0
- Export fields: title; authors; year; venue; abstract; DOI; URL; source; citation count; keywords; document type; affiliations; references if available

```text
TITLE-ABS-KEY(("retrieval augmented generation" OR RAG OR "LLM agent" OR "AI agent" OR "decision support" OR "human-AI" OR "human AI" OR "tool-using agent") AND ("prompt injection" OR poisoning OR misinformation OR disinformation OR "source credibility" OR provenance OR lineage OR attestation OR "trust calibration" OR "epistemic") AND (security OR integrity OR governance OR audit OR calibration OR "zero trust" OR forensic OR accountability OR cognition)) AND PUBYEAR > 2016 AND PUBYEAR < 2027
```

Record listing: `05_records_by_executed_query/P3-SCOPUS-focused__561_records.csv`

### P3-SCOPUS-survey — Scopus (survey)

- Date range: 2017-2026; foundational human-factors and cognition papers may be included through backward snowballing
- Search date: 2026-05-24
- Records identified: 212
- Duplicates removed: 212
- Unique screened: 0
- Core/background/excluded: 0/0/0
- Export fields: title; authors; year; venue; abstract; DOI; URL; source; citation count; keywords; document type; affiliations; references if available

```text
TITLE-ABS-KEY(("retrieval augmented generation" OR RAG OR "LLM agent" OR "AI agent" OR "decision support" OR "human-AI" OR "human AI" OR "tool-using agent") AND (survey OR taxonomy OR systematization OR SoK OR "systematic review" OR benchmark) AND ("prompt injection" OR poisoning OR misinformation OR disinformation OR "source credibility" OR provenance OR lineage OR attestation OR "trust calibration" OR "epistemic")) AND PUBYEAR > 2016 AND PUBYEAR < 2027
```

Record listing: `05_records_by_executed_query/P3-SCOPUS-survey__212_records.csv`

### P3-WEB-broad — Web of Science Core Collection (broad)

- Date range: 2017-2026; foundational human-factors and cognition papers may be included through backward snowballing
- Search date: 2026-05-24
- Records identified: 902
- Duplicates removed: 805
- Unique screened: 97
- Core/background/excluded: 11/32/54
- Export fields: title; authors; year; venue; abstract; DOI; URL; source; citation count; keywords; document type; affiliations; references if available

```text
TS=(("retrieval augmented generation" OR RAG OR "LLM agent" OR "AI agent" OR "decision support" OR "human-AI" OR "human AI" OR "tool-using agent") AND ("prompt injection" OR poisoning OR misinformation OR disinformation OR "source credibility" OR provenance OR lineage OR attestation OR "trust calibration" OR "epistemic")) AND PY=(2017-2026)
```

Record listing: `05_records_by_executed_query/P3-WEB-broad__902_records.csv`

### P3-WEB-focused — Web of Science Core Collection (focused)

- Date range: 2017-2026; foundational human-factors and cognition papers may be included through backward snowballing
- Search date: 2026-05-24
- Records identified: 282
- Duplicates removed: 282
- Unique screened: 0
- Core/background/excluded: 0/0/0
- Export fields: title; authors; year; venue; abstract; DOI; URL; source; citation count; keywords; document type; affiliations; references if available

```text
TS=(("retrieval augmented generation" OR RAG OR "LLM agent" OR "AI agent" OR "decision support" OR "human-AI" OR "human AI" OR "tool-using agent") AND ("prompt injection" OR poisoning OR misinformation OR disinformation OR "source credibility" OR provenance OR lineage OR attestation OR "trust calibration" OR "epistemic") AND (security OR integrity OR governance OR audit OR calibration OR "zero trust" OR forensic OR accountability OR cognition)) AND PY=(2017-2026)
```

Record listing: `05_records_by_executed_query/P3-WEB-focused__282_records.csv`

### P3-WEB-survey — Web of Science Core Collection (survey)

- Date range: 2017-2026; foundational human-factors and cognition papers may be included through backward snowballing
- Search date: 2026-05-24
- Records identified: 127
- Duplicates removed: 127
- Unique screened: 0
- Core/background/excluded: 0/0/0
- Export fields: title; authors; year; venue; abstract; DOI; URL; source; citation count; keywords; document type; affiliations; references if available

```text
TS=(("retrieval augmented generation" OR RAG OR "LLM agent" OR "AI agent" OR "decision support" OR "human-AI" OR "human AI" OR "tool-using agent") AND (survey OR taxonomy OR systematization OR SoK OR "systematic review" OR benchmark) AND ("prompt injection" OR poisoning OR misinformation OR disinformation OR "source credibility" OR provenance OR lineage OR attestation OR "trust calibration" OR "epistemic")) AND PY=(2017-2026)
```

Record listing: `05_records_by_executed_query/P3-WEB-survey__127_records.csv`

### P3-SEMANTIC-broad — Semantic Scholar (broad)

- Date range: 2017-2026; foundational human-factors and cognition papers may be included through backward snowballing
- Search date: 2026-05-24
- Records identified: 18
- Duplicates removed: 5
- Unique screened: 13
- Core/background/excluded: 9/2/2
- Export fields: title; authors; year; venue; abstract; DOI; URL; source; citation count; keywords; document type; affiliations; references if available

```text
retrieval augmented generation RAG LLM agent prompt injection poisoning misinformation disinformation
```

Record listing: `05_records_by_executed_query/P3-SEMANTIC-broad__18_records.csv`

### P3-SEMANTIC-focused — Semantic Scholar (focused)

- Date range: 2017-2026; foundational human-factors and cognition papers may be included through backward snowballing
- Search date: 2026-05-24
- Records identified: 10
- Duplicates removed: 5
- Unique screened: 5
- Core/background/excluded: 5/0/0
- Export fields: title; authors; year; venue; abstract; DOI; URL; source; citation count; keywords; document type; affiliations; references if available

```text
retrieval augmented generation RAG LLM agent prompt injection poisoning misinformation disinformation security robustness provenance
```

Record listing: `05_records_by_executed_query/P3-SEMANTIC-focused__10_records.csv`

### P3-SEMANTIC-survey — Semantic Scholar (survey)

- Date range: 2017-2026; foundational human-factors and cognition papers may be included through backward snowballing
- Search date: 2026-05-24
- Records identified: 10
- Duplicates removed: 10
- Unique screened: 0
- Core/background/excluded: 0/0/0
- Export fields: title; authors; year; venue; abstract; DOI; URL; source; citation count; keywords; document type; affiliations; references if available

```text
retrieval augmented generation RAG LLM agent prompt injection poisoning misinformation disinformation survey taxonomy benchmark
```

Record listing: `05_records_by_executed_query/P3-SEMANTIC-survey__10_records.csv`

## Title/abstract screening prompt

# P3 PRISMA Screening — ChatGPT Instructions

## Your Task

You are performing **title/abstract screening** for a systematic literature review. You will be given a CSV file containing academic paper records. For each record, you must decide whether the paper should be included, excluded, or flagged as uncertain based on the criteria below.

## Paper Context

**Study title:** Epistemic Security in Distributed Human-AI Symbiosis

**What this study is about:**
This review examines how retrieval-augmented generation (RAG) systems, LLM agents, and human-AI decision-support tools can be compromised through attacks on the information environment — including prompt injection, knowledge poisoning, misinformation propagation, source-credibility manipulation, and violations of epistemic trust — and what governance, provenance, and technical controls can mitigate those threats.

**Core concepts in scope:**
- Retrieval-Augmented Generation (RAG) attacks: knowledge/corpus poisoning, adversarial retrieval manipulation
- LLM agent security: prompt injection, tool poisoning, indirect injection via retrieved content
- Epistemic trust and human-AI decision-making: trust calibration, over-reliance, automation bias
- Source credibility and provenance in AI pipelines
- Misinformation and disinformation in AI-assisted workflows
- Zero-trust architectures applied to AI systems
- Human factors in AI-assisted decision support (cognitive biases, trust calibration)
- Systematic surveys of any of the above attack classes or defenses

**Out of scope:**
- Pure computer vision adversarial attacks with no LLM/agent angle
- Hardware side-channel attacks with no AI component
- General network/system security unrelated to AI
- Opinion pieces, news, editorials

---

## Screening Decisions

For each record, assign exactly one `screening_decision`:

| Decision | When to use |
|---|---|
| `include_core` | Directly addresses epistemic security, RAG poisoning, prompt injection, LLM agent attacks, knowledge provenance, or misinformation in AI-assisted decision-support |
| `include_background` | Useful background on human factors in AI decisions, source credibility, cognitive trust, zero-trust for AI, or surveys of adjacent attack classes |
| `exclude` | Does not meet inclusion criteria — assign an `exclusion_reason` (see below) |
| `uncertain` | Cannot determine from title/abstract alone; full text needed |

**Exclusion reasons** (use one of these exact strings when decision = `exclude`):

| Reason | When to use |
|---|---|
| `not_ai_security` | Does not involve AI security or AI-assisted decision-making security |
| `not_within_scope` | AI security paper but focused on unrelated threat class |
| `no_technical_content` | Opinion, news, or editorial with no empirical/technical content |
| `opinion_or_news` | Blog post, commentary, news article |
| `non_english` | Not in English |
| `not_scholarly_or_standards_source` | Vendor white-paper, LinkedIn post, or non-peer-reviewed source |

---

## Input Format

Each batch CSV has these columns:

- `record_id` — unique identifier (e.g., P3-0001)
- `title` — paper title
- `year` — publication year
- `venue` — journal or conference name
- `source_database` — where it was retrieved from (IEEE, Scopus, etc.)
- `document_type` — article type
- `abstract` — paper abstract (may be empty for a small number of records)

---

## Output Format

Produce a CSV file with exactly these columns and **one row per input record**:

```
record_id,screening_decision,exclusion_reason,notes
P3-0001,include_core,,RAG poisoning attack with empirical evaluation
P3-0002,exclude,not_ai_security,focuses on hardware fault injection only
P3-0003,uncertain,,abstract too brief to determine scope
```

Rules:
- Every input `record_id` must appear in the output
- `exclusion_reason` must be non-empty when `screening_decision` is `exclude`, empty otherwise
- `notes` should be a brief (one sentence) plain-English rationale
- Do not add extra columns or change column names
- Output the CSV inside a code block so it can be copied cleanly

---

## How to Process a Batch

1. I will upload a file called `batch_XX.csv`
2. Use Python (Code Interpreter) to read the file and screen each record
3. Output the results CSV for that batch
4. I will save the results and upload the next batch

**If the abstract is empty:** Base the decision on title, venue, and document type alone. Use `uncertain` if there is truly not enough information.

---

## Example Decisions

**include_core:**
> "PoisonedRAG: Knowledge Corruption Attacks to Retrieval-Augmented Generation of Large Language Models" (2024)
> → RAG poisoning attack, directly in scope

**include_background:**
> "Automation Bias in Human-AI Decision Making: A Meta-Analysis" (2022)
> → Human factors / trust calibration, useful background

**exclude / not_ai_security:**
> "Deep Learning-Based Traffic Sign Detection for Autonomous Vehicles" (2021)
> → Computer vision, no epistemic security or AI agent angle

**exclude / not_within_scope:**
> "Side-Channel Attacks on Neural Network Accelerators via Power Analysis" (2023)
> → AI hardware security, not epistemic/agent security

**uncertain:**
> "Trust and Transparency in AI Systems" (2020) — abstract missing
> → Cannot determine without full text


## Disclosure

The screening prompt is retained. The exact hosted model build, decoding parameters, and complete interaction transcript were not retained; therefore the original AI-assisted screening is auditable from inputs, prompt, outputs, and rationales but is not exactly model-rerunnable.