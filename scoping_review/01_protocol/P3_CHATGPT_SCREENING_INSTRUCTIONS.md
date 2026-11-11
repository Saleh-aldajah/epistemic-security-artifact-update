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
