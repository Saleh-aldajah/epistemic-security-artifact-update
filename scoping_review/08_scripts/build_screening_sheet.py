#!/usr/bin/env python3
"""
P3 PRISMA screening sheet builder.

Reads all raw source files (IEEE CSV, Scopus CSV, USNIX CSV, WoS XLS,
Semantic Scholar CSV, ACM BIB), normalises them into the common_fields
schema from coding_schema.yml, deduplicates (DOI-exact then fuzzy-title),
and writes data/P3-screening.csv ready for title/abstract screening.
"""

import csv
import re
import sys
from pathlib import Path

import bibtexparser
import pandas as pd
from rapidfuzz import fuzz

BASE = Path(__file__).resolve().parent.parent
DATA = BASE / "data"
OUT  = DATA / "P3-screening.csv"

COMMON_FIELDS = [
    "record_id", "paper_id", "source_database", "query_id",
    "title", "authors", "year", "venue", "doi", "url", "abstract",
    "document_type", "peer_review_status",
    "screening_decision", "exclusion_reason", "full_text_status",
    "coder_1", "coder_2", "adjudicated_decision", "notes",
    "Epistemic asset", "Trust boundary", "Attack class",
    "Human factor", "CZTA control", "Lineage evidence",
]

FUZZY_TITLE_THRESHOLD = 90  # token_sort_ratio >= this → duplicate


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def norm_doi(raw) -> str:
    if not raw:
        return ""
    s = str(raw).strip().lower()
    s = re.sub(r"^https?://doi\.org/", "", s)
    s = re.sub(r"^doi:\s*", "", s, flags=re.I)
    return s.strip()


def norm_title(title: str) -> str:
    return re.sub(r"\s+", " ", str(title).strip().lower())


def infer_peer_review(doc_type: str, venue: str) -> str:
    dt = str(doc_type).lower()
    v  = str(venue).lower()
    if any(x in dt for x in ("conference", "proceedings", "journal", "article")):
        return "peer_reviewed"
    if "arxiv" in v or "preprint" in dt:
        return "preprint"
    return "unknown"


def blank_record() -> dict:
    return {f: "" for f in COMMON_FIELDS}


def query_type(stem: str) -> str:
    s = stem.lower()
    if "survey" in s:
        return "survey"
    if "focus" in s:
        return "focused"
    return "broad"


# ---------------------------------------------------------------------------
# Source parsers — each returns a list of dicts (un-numbered)
# ---------------------------------------------------------------------------

def parse_ieee_csv(path: Path) -> list[dict]:
    df = pd.read_csv(path, encoding="utf-8-sig")
    qt = query_type(path.stem)
    records = []
    for _, row in df.iterrows():
        r = blank_record()
        r.update(
            paper_id="P3",
            source_database="IEEE Xplore",
            query_id=qt,
            title=str(row.get("Document Title") or "").strip(),
            authors=str(row.get("Authors") or "").strip(),
            year=str(row.get("Publication Year") or "").strip(),
            venue=str(row.get("Publication Title") or "").strip(),
            doi=norm_doi(row.get("DOI")),
            url=str(row.get("PDF Link") or "").strip(),
            abstract=str(row.get("Abstract") or "").strip(),
            document_type=str(row.get("Document Identifier") or "").strip(),
            peer_review_status=infer_peer_review(
                row.get("Document Identifier", ""), row.get("Publication Title", "")
            ),
        )
        records.append(r)
    return records


def parse_scopus_csv(path: Path, db_name: str = "Scopus") -> list[dict]:
    df = pd.read_csv(path, encoding="utf-8-sig")
    qt = query_type(path.stem)
    records = []
    for _, row in df.iterrows():
        r = blank_record()
        r.update(
            paper_id="P3",
            source_database=db_name,
            query_id=qt,
            title=str(row.get("Title") or "").strip(),
            authors=str(row.get("Authors") or "").strip(),
            year=str(row.get("Year") or "").strip(),
            venue=str(row.get("Source title") or "").strip(),
            doi=norm_doi(row.get("DOI")),
            url=str(row.get("Link") or "").strip(),
            abstract=str(row.get("Abstract") or "").strip(),
            document_type=str(row.get("Document Type") or "").strip(),
            peer_review_status=infer_peer_review(
                row.get("Document Type", ""), row.get("Source title", "")
            ),
        )
        records.append(r)
    return records


def parse_wos_xls(path: Path) -> list[dict]:
    df = pd.read_excel(path)
    qt = query_type(path.stem)
    records = []
    for _, row in df.iterrows():
        r = blank_record()
        r.update(
            paper_id="P3",
            source_database="Web of Science Core Collection",
            query_id=qt,
            title=str(row.get("Article Title") or "").strip(),
            authors=str(row.get("Authors") or "").strip(),
            year=str(row.get("Publication Year") or "").strip(),
            venue=str(row.get("Source Title") or "").strip(),
            doi=norm_doi(row.get("DOI")),
            url=str(row.get("DOI Link") or "").strip(),
            abstract=str(row.get("Abstract") or "").strip(),
            document_type=str(row.get("Document Type") or "").strip(),
            peer_review_status=infer_peer_review(
                row.get("Document Type", ""), row.get("Source Title", "")
            ),
        )
        records.append(r)
    return records


def parse_semantic_scholar_csv(path: Path) -> list[dict]:
    df = pd.read_csv(path, encoding="utf-8-sig")
    qt = query_type(path.stem)
    records = []

    if "abstract_or_result_text" in df.columns:
        # Full Semantic Scholar export format
        for _, row in df.iterrows():
            raw_id = str(row.get("doi_or_identifier") or "").strip()
            doi = ""
            url = str(row.get("primary_url") or "").strip()
            if raw_id.lower().startswith("arxiv:"):
                url = url or f"https://arxiv.org/abs/{raw_id[6:]}"
            else:
                doi = norm_doi(raw_id)

            r = blank_record()
            r.update(
                paper_id="P3",
                source_database="Semantic Scholar",
                query_id=qt,
                title=str(row.get("title") or "").strip(),
                authors=str(row.get("authors") or "").strip(),
                year=str(row.get("year") or "").strip(),
                venue=str(row.get("venue_or_source") or "").strip(),
                doi=doi,
                url=url,
                abstract=str(row.get("abstract_or_result_text") or "").strip(),
                document_type=str(row.get("publication_type") or "").strip(),
                peer_review_status=infer_peer_review(
                    row.get("publication_type", ""), row.get("venue_or_source", "")
                ),
                notes=str(row.get("notes") or "").strip(),
            )
            records.append(r)

    elif "abstract" in df.columns and "url" in df.columns:
        # Minimal RAG results format (title, year, abstract, url)
        for _, row in df.iterrows():
            r = blank_record()
            r.update(
                paper_id="P3",
                source_database="Semantic Scholar",
                query_id="broad",
                title=str(row.get("title") or "").strip(),
                year=str(row.get("year") or "").strip(),
                url=str(row.get("url") or "").strip(),
                abstract=str(row.get("abstract") or "").strip(),
            )
            records.append(r)

    return records


def parse_acm_bib(path: Path) -> list[dict]:
    qt = query_type(path.stem)
    with open(path, encoding="utf-8") as fh:
        db = bibtexparser.load(fh)
    records = []
    for entry in db.entries:
        venue = (
            entry.get("booktitle")
            or entry.get("journal")
            or entry.get("series")
            or ""
        )
        doi = norm_doi(entry.get("doi") or entry.get("ID") or "")
        url = entry.get("url") or ""
        title = re.sub(r"[{}]", "", entry.get("title") or "").strip()
        abstract = re.sub(r"[{}]", "", entry.get("abstract") or "").strip()
        venue = re.sub(r"[{}]", "", venue).strip()

        r = blank_record()
        r.update(
            paper_id="P3",
            source_database="ACM Digital Library",
            query_id=qt,
            title=title,
            authors=str(entry.get("author") or "").strip(),
            year=str(entry.get("year") or "").strip(),
            venue=venue,
            doi=doi,
            url=url,
            abstract=abstract,
            document_type=entry.get("ENTRYTYPE") or "",
            peer_review_status=infer_peer_review(
                entry.get("ENTRYTYPE") or "", venue
            ),
        )
        records.append(r)
    return records


# ---------------------------------------------------------------------------
# Deduplication
# ---------------------------------------------------------------------------

def deduplicate(records: list[dict]) -> list[dict]:
    """
    Pass 1 — exact DOI: first occurrence wins, rest marked duplicate.
    Pass 2 — fuzzy title (token_sort_ratio >= FUZZY_TITLE_THRESHOLD) among
              records not already marked duplicate.
    """
    # Pass 1: DOI
    doi_to_id: dict[str, str] = {}
    for rec in records:
        doi = rec["doi"]
        if doi and doi not in doi_to_id:
            doi_to_id[doi] = rec["record_id"]

    for rec in records:
        doi = rec["doi"]
        if doi and doi_to_id.get(doi) != rec["record_id"]:
            rec["screening_decision"] = "duplicate"
            rec["notes"] = f"dup_of:{doi_to_id[doi]}"

    # Pass 2: fuzzy title among non-duplicates
    canonical_titles: list[tuple[str, str]] = []  # (norm_title, record_id)
    for rec in records:
        if rec["screening_decision"] == "duplicate":
            continue
        t = norm_title(rec["title"])
        if not t:
            continue
        matched = False
        for ct, cid in canonical_titles:
            if fuzz.token_sort_ratio(t, ct) >= FUZZY_TITLE_THRESHOLD:
                rec["screening_decision"] = "duplicate"
                rec["notes"] = f"fuzzy_dup_of:{cid}"
                matched = True
                break
        if not matched:
            canonical_titles.append((t, rec["record_id"]))

    return records


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def load_all_records() -> list[dict]:
    all_records: list[dict] = []

    # IEEE (CSV, multiple files)
    for p in sorted(DATA.glob("P3-IEEE-*.csv")):
        recs = parse_ieee_csv(p)
        print(f"  IEEE     {p.name}: {len(recs)} records")
        all_records.extend(recs)

    # Scopus — regular
    for p in sorted(DATA.glob("P3-Scopus-*.csv")):
        recs = parse_scopus_csv(p, db_name="Scopus")
        print(f"  Scopus   {p.name}: {len(recs)} records")
        all_records.extend(recs)

    # USNIX Security (Scopus export)
    for p in sorted(DATA.glob("P3-USNIX*.csv")):
        recs = parse_scopus_csv(p, db_name="USENIX Security/SOUPS")
        print(f"  USENIX   {p.name}: {len(recs)} records")
        all_records.extend(recs)

    # Web of Science (XLS)
    for p in sorted(DATA.glob("P3-WEB-*.xls")):
        recs = parse_wos_xls(p)
        print(f"  WoS      {p.name}: {len(recs)} records")
        all_records.extend(recs)

    # Semantic Scholar CSVs
    for p in sorted(DATA.glob("P3-Semantic-*.csv")):
        recs = parse_semantic_scholar_csv(p)
        print(f"  SS       {p.name}: {len(recs)} records")
        all_records.extend(recs)

    # Semantic Scholar RAG results (separate minimal file)
    rag = DATA / "semantic_scholar_rag_results.csv"
    if rag.exists():
        recs = parse_semantic_scholar_csv(rag)
        print(f"  SS RAG   {rag.name}: {len(recs)} records")
        all_records.extend(recs)

    # ACM (BIB)
    for p in sorted(DATA.glob("P3-ACM-*.bib")):
        recs = parse_acm_bib(p)
        print(f"  ACM      {p.name}: {len(recs)} records")
        all_records.extend(recs)

    return all_records


def main():
    print("Loading sources...")
    records = load_all_records()
    print(f"\nTotal before dedup: {len(records)}")

    # Assign sequential record IDs
    for i, rec in enumerate(records, start=1):
        rec["record_id"] = f"P3-{i:04d}"

    print("Deduplicating...")
    records = deduplicate(records)

    dup_count   = sum(1 for r in records if r["screening_decision"] == "duplicate")
    uniq_count  = len(records) - dup_count
    print(f"  Duplicates flagged : {dup_count}")
    print(f"  Unique records     : {uniq_count}")

    print(f"\nWriting {OUT.name}...")
    with open(OUT, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=COMMON_FIELDS)
        writer.writeheader()
        writer.writerows(records)

    print(f"Done — {len(records)} rows written to {OUT}")

    # Summary by source
    print("\nBreakdown by source_database:")
    from collections import Counter
    src_counts = Counter(r["source_database"] for r in records)
    for src, n in sorted(src_counts.items()):
        duped = sum(
            1 for r in records
            if r["source_database"] == src and r["screening_decision"] == "duplicate"
        )
        print(f"  {src:<40} {n:>5} total  ({duped} duped)")

    print("\nBreakdown by query_id:")
    qt_counts = Counter(r["query_id"] for r in records if r["screening_decision"] != "duplicate")
    for qt, n in sorted(qt_counts.items()):
        print(f"  {qt:<12} {n:>5} unique")


if __name__ == "__main__":
    main()
