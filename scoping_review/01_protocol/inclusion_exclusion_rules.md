# Inclusion and Exclusion Rules

Prepared: 2026-05-24

## Universal inclusion criteria

- The record is about AI/ML security, agent security, multimodal security, provenance, verification, human-AI epistemic integrity, or related technical governance.
- The record provides a citable scholarly, standards, benchmark, system, or formal threat-model contribution.
- The abstract or full text contains enough information to code attack/defense layer, artifact type, evidence type, and limitations.
- The record falls within the primary date range unless tagged as foundational background.
- The record is available in English or can be reliably translated without loss of technical detail.

## Universal exclusion criteria

- not_ai_security
- not_within_scope
- no_technical_content
- opinion_or_news
- duplicate
- superseded_by_published_version
- non_english
- full_text_unavailable
- unsafe_operational_payload_only
- not_scholarly_or_standards_source

## P1. Modality Gap

Include records focused on security-relevant failures where equivalent or near-equivalent semantic content changes policy, alignment, or downstream action after modality translation.

Required coding dimensions: Modality carrier, Attack class, Semantic translation path, Alignment degradation mode, Defense layer, Empirical artifact.

## P2. Verifiable AI Infrastructure

Include records focused on verifiable evidence for datasets, models, pipelines, runtimes, outputs, or governance claims in high-stakes ML systems.

Required coding dimensions: Evidence layer, Receipt level, Cryptographic primitive, Runtime trust assumption, Threat mitigated, Deployment domain.

## P3. Epistemic Security

Include records focused on security, provenance, cognitive, and governance mechanisms that affect integrity of claims, evidence, source authority, calibration, or organizational decision state in human-AI systems.

Required coding dimensions: Epistemic asset, Trust boundary, Attack class, Human factor, CZTA control, Lineage evidence.

## P4. A2A Agent Security

Include records focused on security failures and controls for autonomous or semi-autonomous multi-agent workflows, tool calls, delegation, protocol identity, taint propagation, or cascading jailbreaks.

Required coding dimensions: Agent topology, Delegation model, Attack propagation substrate, Identity level, Authorization creep type, Audit/taint evidence.

