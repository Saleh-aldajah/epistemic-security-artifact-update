# AI Security SoK Portfolio: PRISMA-Style Corpus Protocol

Prepared: 2026-05-24

## Purpose

This package operationalizes a PRISMA-style corpus construction workflow for four AI security Systematization of Knowledge manuscripts. It is designed for A*-venue review expectations: exact search dates, database-specific search strings, inclusion and exclusion rules, deduplication, title/abstract screening, full-text eligibility screening, coded artifact matrices, and inter-rater agreement reporting.

The package follows PRISMA 2020 reporting logic for transparent identification, screening, eligibility, and inclusion. Because ACM Digital Library, IEEE Xplore, Scopus, and Web of Science require authenticated exports, this package includes execution-ready queries, spreadsheet workbooks, scripts for open APIs, and placeholders for raw database hit counts. The existing manuscript bibliographies have been extracted as a seed corpus and should be treated as other-source records until database searches are executed.

## Portfolio scope

| Paper | Working topic | Primary date range | Seed bibliography records |
|---|---|---:|---:|
| P1 | Modality Gap | 2018-2026 | 63 |
| P2 | Verifiable AI Infrastructure | 2017-2026 | 79 |
| P3 | Epistemic Security | 2017-2026; foundational human-factors and cognition papers may be included through backward snowballing | 118 |
| P4 | A2A Agent Security | 2019-2026 | 85 |

Total seed records extracted from the refurbished manuscripts: 345. Deduplicated seed records across the portfolio: 317.

## Databases and sources

Primary scholarly databases:

- ACM Digital Library / ACM Guide to Computing Literature
- IEEE Xplore
- Scopus
- Web of Science Core Collection
- Semantic Scholar Graph API
- arXiv cs.CR, cs.AI, cs.LG, cs.HC where relevant
- Crossref REST API
- DBLP

Security venue hand-searches:

- IEEE Symposium on Security and Privacy
- USENIX Security Symposium
- ACM CCS
- NDSS Symposium
- IEEE SaTML
- USENIX SOUPS where human factors are relevant

Standards and protocol sources may be included as non-peer-reviewed but citable governance artifacts when they define deployed security mechanisms, protocol behavior, or compliance requirements.

## Common PRISMA workflow

1. Identification: execute all database-specific strings; export raw results; log raw hit counts and filters in `data/templates/database_export_manifest_template.csv`.
2. Import: convert RIS, BibTeX, CSV, and API JSONL exports to normalized CSV using `scripts/merge_exports.py` and `scripts/normalize_bibtex.py`.
3. Deduplication: deduplicate by DOI, arXiv ID, title fingerprint, and first-author/year collision using `scripts/deduplicate_records.py`.
4. Title/abstract screening: two coders screen a 20 percent stratified subsample plus all uncertain records; each record receives include, background, exclude, duplicate, or uncertain.
5. Full-text eligibility: retrieve PDFs or official pages; exclude with one primary exclusion reason.
6. Coding: code included core records against the shared and paper-specific schemas.
7. Agreement: compute Cohen's kappa for binary inclusion and each major categorical coding dimension using `scripts/compute_kappa.py`.
8. Adjudication: reconcile disagreements and log adjudication notes.
9. Reporting: generate PRISMA counts and diagrams with `scripts/build_prisma_counts.py` and `scripts/render_prisma_diagram.py`.

## Common inclusion criteria

- The work makes a technical, empirical, taxonomic, protocol, benchmark, system, governance, or threat-model contribution to AI security.
- The work is within the paper-specific scope and primary date range, except for explicitly marked foundational background.
- The source is peer-reviewed, a reputable preprint with technical content, a formal standards/protocol document, or a citable industrial/security report with methodological value.
- The work includes enough metadata to be cited and coded reproducibly.

## Common exclusion criteria

- No AI, ML, agentic, multimodal, provenance, or human-AI security relevance.
- Pure opinion, product marketing, news, or unsubstantiated commentary.
- Duplicate, superseded preprint, inaccessible full text, or non-English record when no reliable translation is available.
- Operational exploit-only material without scholarly, defensive, or measurement contribution.
- Papers whose contribution is purely about generic cybersecurity without AI-system relevance, unless included as foundational background for identity, authorization, provenance, or zero trust.

## Paper-specific research questions

### P1. Modality Gap

- RQ1: What attack classes exploit modality translation or representation gaps in multimodal AI systems?
- RQ2: Which security properties are violated across text, image, audio, document, video, and sensor carriers?
- RQ3: What empirical evidence exists for policy invariance under translation and cross-modal alignment degradation?
- RQ4: Which defenses operate at surface modality, canonical semantic representation, policy gate, or downstream action gate?

Core inclusion focus: security-relevant failures where equivalent or near-equivalent semantic content changes policy, alignment, or downstream action after modality translation.

Coding dimensions: Modality carrier, Attack class, Semantic translation path, Alignment degradation mode, Defense layer, Empirical artifact.

### P2. Verifiable AI Infrastructure

- RQ1: What artifacts in ML pipelines are made verifiable by existing cryptographic, attestation, or transparency mechanisms?
- RQ2: Which threat classes are addressed by provenance receipts and which remain outside their guarantees?
- RQ3: How do receipt strength, verification cost, leakage, and deployment friction vary across evidence levels?
- RQ4: What benchmarks or case studies exist for verifiable AI in critical infrastructure?

Core inclusion focus: verifiable evidence for datasets, models, pipelines, runtimes, outputs, or governance claims in high-stakes ML systems.

Coding dimensions: Evidence layer, Receipt level, Cryptographic primitive, Runtime trust assumption, Threat mitigated, Deployment domain.

### P3. Epistemic Security

- RQ1: What security failures compromise epistemic artifacts in human-AI workflows?
- RQ2: Which trust boundaries separate open-world information, corpora, retrievers, prompts, tools, agents, humans, and organizations?
- RQ3: What controls provide claim-level mediation, lineage, calibration, and forensic replay?
- RQ4: How has existing literature evaluated human reliance, trust calibration, and evidence presentation under adversarial conditions?

Core inclusion focus: security, provenance, cognitive, and governance mechanisms that affect integrity of claims, evidence, source authority, calibration, or organizational decision state in human-AI systems.

Coding dimensions: Epistemic asset, Trust boundary, Attack class, Human factor, CZTA control, Lineage evidence.

### P4. A2A Agent Security

- RQ1: How do prompt injection and tool-use attacks propagate across agent-to-agent workflow boundaries?
- RQ2: Which authorization and identity primitives are used or proposed for agent delegation?
- RQ3: What evidence exists for cascade depth, privilege amplification, taint loss, audit completeness, and revocation latency?
- RQ4: Which reference architectures enforce deterministic control instead of relying on model self-policing?

Core inclusion focus: security failures and controls for autonomous or semi-autonomous multi-agent workflows, tool calls, delegation, protocol identity, taint propagation, or cascading jailbreaks.

Coding dimensions: Agent topology, Delegation model, Attack propagation substrate, Identity level, Authorization creep type, Audit/taint evidence.

## Reporting requirements

Each manuscript should report: database names, search dates, complete search strings, number of records at each PRISMA stage, inclusion/exclusion criteria, coder training procedure, inter-rater agreement, coded artifact matrix, limitations of corpus coverage, and artifact availability.

## Source notes

Use the official PRISMA 2020 flow diagram structure and reporting checklist. The package stores plain-text URLs and API endpoints in scripts and documentation so reviewers can reproduce the corpus construction without relying on unpublished search choices.
