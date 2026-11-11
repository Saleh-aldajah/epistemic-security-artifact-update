#!/usr/bin/env python3
"""Build PRISMA counts from a finalized screening CSV."""
import argparse, csv
from collections import Counter

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--screening', required=True); ap.add_argument('--out', required=True); args=ap.parse_args()
    with open(args.screening, newline='', encoding='utf-8') as f: rows=list(csv.DictReader(f))
    for pid in sorted(set(r.get('paper_id','') for r in rows)):
        sub=[r for r in rows if r.get('paper_id')==pid]
        c=Counter(r.get('screening_decision','') for r in sub)
        stages=[
            ('records_screened', len(sub)),
            ('records_excluded_title_abstract', c.get('exclude',0)),
            ('studies_included_core', c.get('include_core',0)),
            ('studies_included_background', c.get('include_background',0)),
            ('duplicates', c.get('duplicate',0)),
            ('uncertain', c.get('uncertain',0)),
        ]
        with open(args.out.replace('.csv',f'_{pid}.csv'),'w',newline='',encoding='utf-8') as f:
            w=csv.writer(f); w.writerow(['paper_id','stage','count'])
            for s,n in stages: w.writerow([pid,s,n])
if __name__=='__main__': main()
