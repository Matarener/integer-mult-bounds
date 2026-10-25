"""Exact source patch, scalar identity and literal frame invoice.
Adapted from a separate OpenAI Codex review by Ross Richardson.
Assertions must remain active; the public driver starts this in an unoptimized
child interpreter with an isolated bytecode-cache namespace."""
from pathlib import Path
from fractions import Fraction as Q
from collections import Counter,defaultdict
from functools import lru_cache
import gzip,hashlib,json,sys
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
SRC=ROOT/'research/rank7-coupled-586-588-carrier-fold/edits'
@lru_cache(None)
def span(xs):
    a={0}
    for x in xs:a|={v^x for v in tuple(a)}
    return frozenset(a)
def dim(s):
    d=len(s).bit_length()-1;assert len(s)==1<<d;return d
FULL=span(tuple(1<<i for i in range(9)))
def read(p):return json.loads(gzip.decompress(p.read_bytes()))
def scalar(g):return g[:5] if g[0]=='add' else g[:4]
def profile(w):
    removed=set(w['removed']);current={r:span((w['ports'][r],)) if r<112 else span(tuple(w['start_extra'].get(str(r),[]))) for r in range(704)}
    counts=Counter();positive=0
    def climb(r,E):
        nonlocal positive
        E=span(tuple(E));assert current[r]<=E,(r,current[r],E)
        d=dim(E)-dim(current[r]);current[r]=E
        if d:counts[d]+=1;positive+=1
    def gate(g):
        if g[0]=='warp':
            r=g[1];assert current[r]==span(tuple(g[3]));current[r]=span(tuple(g[4]))
        else:
            for r in g[1:3] if g[0]=='add' else g[1:2]:climb(r,g[-1])
    for g in w['A']:gate(g)
    for r,E in zip(w['centers'],w['center_frames']):climb(r,E)
    for t in range(112):climb(112+t,w.get('target_levels',{}).get(str(t),[]))
    at=defaultdict(list)
    for p,r,G,U,E in w['warps']:at[p].append((r,U,E))
    for i in range(len(w['B'])+1):
        for r,U,E in at[i]:
            assert current[r]==span(tuple(U)),('native entry',i,r)
            current[r]=span(tuple(E))
        if i<len(w['B']):gate(w['B'][i])
    for g in w['restore']:gate(g)
    for r in range(704):
        if r in removed:continue
        E=w['helper_final'].get(str(r),list(FULL))
        if 112<=r<224:E=[x for x in FULL if not (x&w['ports'][r-112]).bit_count()%2]
        climb(r,E)
    # Separately paid private center descents through every served target level.
    for r,E in zip(w['centers'],w['center_frames']):
        U=span(tuple(E))
        levels={span(tuple(w.get('target_levels',{}).get(str(g[1]-112),[]))) for g in w['cut'] if g[2]==r}
        for T in sorted(levels,key=len,reverse=True):
            assert T<=U
            d=dim(U)-dim(T)
            if d:counts[d]+=1;positive+=1
            U=T
    inventory=Counter()
    for r in range(224,704):
        if r in removed:continue
        start=span(tuple(w['start_extra'].get(str(r),[])))
        end=span(tuple(w['helper_final'].get(str(r),list(FULL))))
        width=dim(end)-dim(start)
        if width:inventory[width]+=1
    return dict(sorted(counts.items())),dict(sorted(inventory.items())),positive

