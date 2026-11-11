#!/usr/bin/env python3
"""
P3 AI-assisted title/abstract screening via Anthropic Message Batches API.

Modes (auto-detected from data/P3-batch-state.json):
  submit  — load P3-screening.csv, build batch requests, submit, save state
  poll    — check batch status, print progress
  collect — download results, write back to P3-screening.csv

Usage:
  python scripts/ai_screening.py            # auto-detect mode
  python scripts/ai_screening.py submit     # force submit
  python scripts/ai_screening.py poll       # force poll
  python scripts/ai_screening.py collect    # force collect
"""

import csv
import json
import re
import sys
from pathlib import Path

import anthropic

BASE  = Path(__file__).resolve().parent.parent
DATA  = BASE / "data"
CSV   = DATA / "P3-screening.csv"
STATE = DATA / "P3-batch-state.json"

MODEL = "claude-haiku-4-5-20251001"

SYSTEM_PROMPT = """You are a systematic-literature-review assistant helping screen papers for a study titled:

  "Epistemic Security in Distributed Human-AI Symbiosis"

The study examines how retrieval-augmented generation (RAG), LLM agents, and human-AI decision-support systems can be compromised through attacks on the information environment — including prompt injection, knowledge poisoning, misinformation propagation, source-credibility manipulation, and epistemic trust violations — and what governance, provenance, and technical controls can mitigate those threats.

INCLUSION CRITERIA (title/abstract screen):
• include_core   — directly addresses epistemic security, prompt injection, RAG poisoning, LLM agent attacks, knowledge/data provenance, human-AI trust calibration, or misinformation in AI-assisted decision-support
• include_background — useful background on human factors in AI decisions, source credibility, cognitive trust, zero-trust architectures applied to AI, or systematic surveys of adjacent attack classes
• uncertain      — cannot determine from title/abstract alone; full text needed

EXCLUSION CRITERIA:
• not_ai_security        — does not involve AI security, LLM security, or AI-assisted decision-making security
• not_within_scope       — AI security paper but focused on unrelated threat class (e.g., pure adversarial vision, hardware side-channels with no AI angle)
• no_technical_content   — opinion, news, or editorial with no empirical/technical content
• opinion_or_news        — blog post, commentary, news article
• duplicate              — already marked duplicate (do not re-screen these)
• non_english            — not in English
• not_scholarly_or_standards_source — LinkedIn post, vendor white-paper without peer review, etc.

Respond ONLY with a JSON object on one line — no prose, no markdown fences:
{"decision": "<value>", "reason": "<exclusion_reason_or_empty>", "note": "<one-sentence rationale>"}

decision must be one of: include_core, include_background, exclude, uncertain
reason must be one of the EXCLUSION CRITERIA keys above when decision=exclude, otherwise empty string."""


def load_state() -> dict | None:
    if STATE.exists():
        return json.loads(STATE.read_text())
    return None


def save_state(data: dict) -> None:
    STATE.write_text(json.dumps(data, indent=2))


def load_pending_records() -> list[dict]:
    """Return records where screening_decision is blank (not yet screened, not a dup)."""
    with open(CSV, newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    pending = [r for r in rows if not r.get("screening_decision", "").strip()]
    return pending


def load_all_records() -> list[dict]:
    with open(CSV, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def write_back(results: dict[str, dict]) -> None:
    """Merge AI results into P3-screening.csv keyed by record_id."""
    rows = load_all_records()
    fieldnames = rows[0].keys() if rows else []
    updated = 0
    for row in rows:
        rid = row["record_id"]
        if rid in results:
            res = results[rid]
            row["screening_decision"] = res.get("decision", "uncertain")
            row["exclusion_reason"]   = res.get("reason", "")
            # Prepend AI note to existing notes
            ai_note = res.get("note", "")
            existing = row.get("notes", "").strip()
            row["notes"] = f"ai:{ai_note}" + (f" | {existing}" if existing else "")
            updated += 1

    with open(CSV, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(fieldnames))
        writer.writeheader()
        writer.writerows(rows)
    print(f"  Wrote {updated} AI decisions back to {CSV.name}")


def build_user_message(rec: dict) -> str:
    title    = rec.get("title", "").strip() or "(no title)"
    abstract = rec.get("abstract", "").strip() or "(no abstract)"
    year     = rec.get("year", "").strip()
    venue    = rec.get("venue", "").strip()
    db       = rec.get("source_database", "").strip()
    doc_type = rec.get("document_type", "").strip()

    parts = [f"Title: {title}"]
    if year:
        parts.append(f"Year: {year}")
    if venue:
        parts.append(f"Venue: {venue}")
    if db:
        parts.append(f"Source: {db}")
    if doc_type:
        parts.append(f"Document type: {doc_type}")
    parts.append(f"Abstract: {abstract}")
    return "\n".join(parts)


def do_submit(client: anthropic.Anthropic) -> None:
    pending = load_pending_records()
    if not pending:
        print("No pending records to screen.")
        return
    print(f"Building {len(pending)} batch requests...")

    requests = []
    for rec in pending:
        requests.append(
            anthropic.types.message_create_params.Request(
                custom_id=rec["record_id"],
                params=anthropic.types.MessageCreateParamsNonStreaming(
                    model=MODEL,
                    max_tokens=256,
                    system=[
                        {
                            "type": "text",
                            "text": SYSTEM_PROMPT,
                            "cache_control": {"type": "ephemeral"},
                        }
                    ],
                    messages=[
                        {
                            "role": "user",
                            "content": build_user_message(rec),
                        }
                    ],
                ),
            )
        )

    # Anthropic Batches API max is 10,000 requests per batch
    BATCH_SIZE = 10_000
    batch_ids = []
    for chunk_start in range(0, len(requests), BATCH_SIZE):
        chunk = requests[chunk_start : chunk_start + BATCH_SIZE]
        batch = client.messages.batches.create(requests=chunk)
        batch_ids.append(batch.id)
        print(f"  Submitted batch {batch.id} ({len(chunk)} requests, status={batch.processing_status})")

    save_state({"batch_ids": batch_ids, "total": len(pending)})
    print(f"State saved to {STATE.name}. Run again to poll.")


def do_poll(client: anthropic.Anthropic) -> None:
    state = load_state()
    if not state:
        print("No state file found. Run 'submit' first.")
        sys.exit(1)

    all_ended = True
    for bid in state["batch_ids"]:
        batch = client.messages.batches.retrieve(bid)
        rc = batch.request_counts
        print(
            f"  Batch {bid}: {batch.processing_status}"
            f"  processing={rc.processing}"
            f"  succeeded={rc.succeeded}"
            f"  errored={rc.errored}"
            f"  canceled={rc.canceled}"
            f"  expired={rc.expired}"
        )
        if batch.processing_status != "ended":
            all_ended = False

    if all_ended:
        print("\nAll batches ended. Run again (or 'collect') to download results.")
    else:
        print("\nBatch(es) still processing. Try again later.")


def do_collect(client: anthropic.Anthropic) -> None:
    state = load_state()
    if not state:
        print("No state file found. Run 'submit' first.")
        sys.exit(1)

    results: dict[str, dict] = {}
    for bid in state["batch_ids"]:
        batch = client.messages.batches.retrieve(bid)
        if batch.processing_status != "ended":
            print(f"Batch {bid} is not yet ended (status={batch.processing_status}). Poll first.")
            sys.exit(1)

        print(f"Downloading results for batch {bid}...")
        for result in client.messages.batches.results(bid):
            rid = result.custom_id
            if result.result.type == "succeeded":
                raw = result.result.message.content[0].text.strip()
                # Strip markdown code fences if the model added them
                raw = re.sub(r"^```[a-z]*\n?", "", raw, flags=re.I)
                raw = re.sub(r"\n?```$", "", raw)
                try:
                    parsed = json.loads(raw)
                    decision = parsed.get("decision", "uncertain")
                    reason   = parsed.get("reason", "")
                    note     = parsed.get("note", "")
                    # Validate decision value
                    valid_decisions = {"include_core", "include_background", "exclude", "uncertain"}
                    if decision not in valid_decisions:
                        decision = "uncertain"
                        note = f"invalid_decision_value:{decision} | {note}"
                    results[rid] = {"decision": decision, "reason": reason, "note": note}
                except json.JSONDecodeError:
                    results[rid] = {
                        "decision": "uncertain",
                        "reason": "",
                        "note": f"json_parse_error | raw={raw[:120]}",
                    }
            elif result.result.type == "errored":
                err = result.result.error
                results[rid] = {
                    "decision": "uncertain",
                    "reason": "",
                    "note": f"api_error:{err.type}",
                }
            else:
                results[rid] = {
                    "decision": "uncertain",
                    "reason": "",
                    "note": f"unexpected_result_type:{result.result.type}",
                }

    print(f"  Collected {len(results)} results.")

    # Tally decisions
    from collections import Counter
    counts = Counter(v["decision"] for v in results.values())
    for dec, n in sorted(counts.items()):
        print(f"    {dec:<22} {n:>5}")

    write_back(results)
    STATE.unlink(missing_ok=True)
    print("State file removed. Screening complete.")


def auto_detect_mode(state: dict | None) -> str:
    if state is None:
        return "submit"
    # Check if any batch is still processing
    client = anthropic.Anthropic()
    for bid in state["batch_ids"]:
        batch = client.messages.batches.retrieve(bid)
        if batch.processing_status != "ended":
            return "poll"
    return "collect"


def main() -> None:
    mode_arg = sys.argv[1].lower() if len(sys.argv) > 1 else None
    client   = anthropic.Anthropic()
    state    = load_state()

    if mode_arg:
        mode = mode_arg
    else:
        mode = auto_detect_mode(state)
        print(f"Auto-detected mode: {mode}")

    if mode == "submit":
        do_submit(client)
    elif mode == "poll":
        do_poll(client)
    elif mode == "collect":
        do_collect(client)
    else:
        print(f"Unknown mode '{mode}'. Use: submit | poll | collect")
        sys.exit(1)


if __name__ == "__main__":
    main()
