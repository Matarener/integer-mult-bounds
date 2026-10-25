#!/usr/bin/env python3
import json, gzip, hashlib, argparse
from fractions import Fraction
from pathlib import Path
from math import gcd

parser=argparse.ArgumentParser()
parser.add_argument('--source-dir',type=Path,required=True)
parser.add_argument('--source-receipt',type=Path,required=True)
parser.add_argument('--output',type=Path)
args=parser.parse_args()
ROOT=args.source_dir
RECEIPT=args.source_receipt
def need(test,message):
    if not test: raise RuntimeError(message)
def rank(rows):
    a=[[Fraction(v) for v in row] for row in rows]
    h=0
    for c in range(8):
        i=next((i for i in range(h,len(a)) if a[i][c]),None)
        if i is None: continue
        a[h],a[i]=a[i],a[h]
        pivot=a[h][c]
        a[h]=[v/pivot for v in a[h]]
        for j in range(h+1,len(a)):
            v=a[j][c]
            if v:a[j]=[u-v*w for u,w in zip(a[j],a[h])]
        h+=1
        if h==len(a):break
    return h
raws={name:(ROOT/(name+'.json.gz')).read_bytes() for name in ['WORD','GEOMETRY']}
word,geo=[json.loads(gzip.decompress(raws[name])) for name in ['WORD','GEOMETRY']]
expected=json.loads(RECEIPT.read_bytes())['actual_source_trace']['exact_rational_frame_ranks']
ranks=[rank([geo['lines'][j] for j in frame]) for frame in geo['frames']]
need(ranks==expected,'fraction RREF disagreement with fraction-free submitted ranks')
frames=[set(x) for x in geo['frames']]
actual=word['start'][:]+[None]
moves=0
for i,row in enumerate(word['records']):
    op,d,s,c,f,_=row
    if op==0:
        need(actual[d]==s,'move entrance mismatch')
        need(frames[s] <= frames[c], 'upward literal generator inclusion')
        need(ranks[c]-ranks[s]==f and f>0,'move rank mismatch')
        actual[d]=c;moves+=1
    elif op==1:
        need(actual[d]==actual[s]==f,'ADD frame mismatch')
    elif op==2:actual[660]=f
    elif op==3:actual[660]=None
need(actual[:-1]==word['final'] and actual[-1] is None,'final frame mismatch')
for p in range(111):
    n=geo['lines'][p]
    fr=word['final'][111+p]
    need(sum(x*x for x in n)==4 and ranks[fr]==7,'cap dimension')
    need(all(sum(x*y for x,y in zip(n,geo['lines'][q]))==0 for q in frames[fr]),'cap orthogonality')
result={'status':'PASS','method':'independent Fraction Gaussian elimination with forward row reduction; no producer or submitted checker import','checked_frame_ranks':len(ranks),'checked_MOVE_events':moves,'checked_final_cap_equalities':111,'scope_excludes':['K/R coefficients','K-supported recipient projected ranks','decoded scalar endpoint','physical MOVE semantics'],'inputs':{k:hashlib.sha256(v).hexdigest() for k,v in raws.items()},'rank_census':{str(v):ranks.count(v) for v in sorted(set(ranks))}}
if args.output is not None:
    args.output.write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
print(json.dumps(result,sort_keys=True))
