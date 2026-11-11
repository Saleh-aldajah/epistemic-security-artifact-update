#!/usr/bin/env python3
"""Deduplicate normalized corpus CSV by DOI/arXiv/title fingerprint."""
import argparse, csv, re

def norm_title(t):
    t=(t or '').lower(); t=re.sub(r'[^a-z0-9]+',' ',t); t=re.sub(r'\b(the|a|an)\b',' ',t); return re.sub(r'\s+',' ',t).strip()
def norm_doi(d):
    d=(d or '').lower().strip(); return re.sub(r'^https?://(dx\.)?doi\.org/','',d)
def key(row):
    doi=norm_doi(row.get('doi') or row.get('DOI') or '')
    arxiv=row.get('arxiv_id') or row.get('eprint') or ''
    if doi: return 'doi:'+doi
    if arxiv: return 'arxiv:'+arxiv.lower()
    return 'title:'+norm_title(row.get('title') or '')

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--infile', required=True); ap.add_argument('--out', required=True); ap.add_argument('--dups', required=True); args=ap.parse_args()
    with open(args.infile, newline='', encoding='utf-8') as f: rows=list(csv.DictReader(f))
    seen={}; keep=[]; dups=[]
    for r in rows:
        k=key(r)
        if k in seen:
            r['duplicate_of']=seen[k].get('record_id','') or seen[k].get('title','')
            r['duplicate_key']=k; dups.append(r)
        else:
            r['dedupe_key']=k; seen[k]=r; keep.append(r)
    fields=sorted(set().union(*(r.keys() for r in keep+dups))) if rows else []
    for path, data in [(args.out, keep),(args.dups, dups)]:
        with open(path,'w',newline='',encoding='utf-8') as f:
            w=csv.DictWriter(f, fieldnames=fields, extrasaction='ignore'); w.writeheader(); w.writerows(data)
if __name__=='__main__': main()
