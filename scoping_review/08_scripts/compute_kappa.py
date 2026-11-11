#!/usr/bin/env python3
"""Compute Cohen's kappa for two coder columns in a CSV."""
import argparse, csv
from collections import Counter

def kappa(labels1, labels2):
    pairs=[(a,b) for a,b in zip(labels1,labels2) if a!='' and b!='']
    if not pairs: return None
    n=len(pairs); agree=sum(1 for a,b in pairs if a==b)/n
    c1=Counter(a for a,b in pairs); c2=Counter(b for a,b in pairs)
    pe=sum((c1[k]/n)*(c2[k]/n) for k in set(c1)|set(c2))
    return 1.0 if pe==1 else (agree-pe)/(1-pe)

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--infile', required=True); ap.add_argument('--coder-a', required=True); ap.add_argument('--coder-b', required=True); ap.add_argument('--out', default=None); args=ap.parse_args()
    with open(args.infile, newline='', encoding='utf-8') as f: rows=list(csv.DictReader(f))
    val=kappa([r.get(args.coder_a,'') for r in rows],[r.get(args.coder_b,'') for r in rows])
    text=f'cohen_kappa,{val:.4f}\n' if val is not None else 'cohen_kappa,NA\n'
    if args.out: open(args.out,'w',encoding='utf-8').write(text)
    else: print(text, end='')
if __name__=='__main__': main()
