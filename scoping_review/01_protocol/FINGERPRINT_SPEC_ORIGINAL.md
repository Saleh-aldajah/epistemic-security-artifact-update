# Bibliographic fingerprint specification

## Purpose

Fingerprints allow a rights-cleared public row to be aligned with a lawfully obtained local bibliographic record without redistributing title or abstract text. A match indicates equality under the normalization procedure; it does not certify the source platform, copyright status, or semantic correctness.

## Normalization

For each text field:

1. convert to Unicode Normalization Form KC (NFKC);
2. lowercase using Python's Unicode-aware `str.lower()`;
3. collapse every run of whitespace to one ASCII space; and
4. strip leading and trailing whitespace.

## Field hashes

- `title_sha256` = SHA-256 of the normalized title encoded as UTF-8.
- `abstract_sha256` = SHA-256 of the normalized abstract encoded as UTF-8.
- Empty fields therefore hash to the standard SHA-256 digest of the empty byte string.

## Combined bibliographic fingerprint

Normalize these fields in order:

1. title;
2. authors;
3. year;
4. venue;
5. DOI; and
6. abstract.

Join the six normalized UTF-8 strings with the ASCII unit separator byte `0x1F`, then compute SHA-256. Store the lowercase hexadecimal digest in `bibliographic_fingerprint_sha256`.

Pseudocode:

```python
normalized = [normalize(value) for value in [title, authors, year, venue, doi, abstract]]
payload = "\x1f".join(normalized).encode("utf-8")
digest = hashlib.sha256(payload).hexdigest()
```

## Stability limits

A publisher correction, punctuation change, reordered author list, enriched abstract, DOI normalization change, or database-specific metadata variant changes the digest. The fingerprint is an integrity/alignment aid for the retained normalized representation, not a universal scholarly-work identifier. Use DOI where available and treat the fingerprint as supplementary.
