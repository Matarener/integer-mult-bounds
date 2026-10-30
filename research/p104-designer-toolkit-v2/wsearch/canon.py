"""canon -- canonical word hash (SEARCHCORE).  hash(w) is invariant under
  * relabelling of HELPER registers (public registers that are neither live X, nor X+112 Y),
  * the order of COMMUTING events (relat.py epochs: ADD(t,s) on public t,s = W on t / R on s; reads of one register commute, additive writes into one register commute;
    SCALE / INIT / CLEAR / COPY, any event touching an owned register, and every MOVE of a register are barriers on that register) -- this includes the order of MOVEs
    of different registers (MOVE order inside inter-op blocks),
  * the numbering / basis choice of frames (a frame is identified by its RREF basis, i.e. its span as a GF(2) subspace),
and distinguishes words whose per-register timelines (events, MOVE trajectories, quotients q, frames, initial/final frames) differ, hence words that price differently.
INIT/CLEAR additionally share one global pseudo-register (the owned-lifetime peak rule is order dependent).
Method: lexicographically least topological order of the trace (heap over the ready items; key = item content with helpers coloured by 3 rounds of colour refinement),
then helpers are renamed by first appearance in that order.  Residual ambiguity only for colour-symmetric helpers that are not automorphic (then equal words may hash apart: a
missed dedupe, never a false merge).
canon_hash(w) -> 32 hex chars.   canon_form(w) -> (header, items) for debugging."""
import heapq,hashlib,collections
from fractions import Fraction as Q
import sys,os
HERE=os.path.dirname(os.path.abspath(__file__)); TK=os.path.dirname(HERE)
if TK not in sys.path: sys.path.insert(0,TK)
import legal

def rref(basis):
    piv={}
    for v in basis:
        for p,b in piv.items():
            if v>>p&1: v^=b
        if v:
            p=v.bit_length()-1
            for q in list(piv):
                if piv[q]>>p&1: piv[q]^=v
            piv[p]=v
    return tuple(sorted(piv.values(),reverse=True))
def _h(x,n=6): return hashlib.blake2b(repr(x).encode(),digest_size=n).hexdigest()
def _q(q): return str(Q(q))

def _prepare(w):
    n=len(w['initial']); live=set(w['live']); OWN=set(legal.owned_set(w))
    fid=[_h(rref(b)) for b in w['frames']]
    def isH(r): return r<n and r not in live and (r-112) not in live and r not in OWN
    items=[]; acc=[]       # items: (kind, regs-with-roles tuple, rest tuple) ; acc: per item list of (reg, access)
    for e in w['program']:
        op=e[0]; r=e[1]
        if op=='MOVE': items.append(('M',(r,),(fid[e[2]],fid[e[3]],int(bool(e[4]))))); acc.append([(r,'B')])
        elif op=='INIT': items.append(('I',(r,),(fid[e[2]],))); acc.append([(r,'B'),('LIFE','B')])
        elif op=='CLEAR': items.append(('C',(r,),(fid[e[2]],))); acc.append([(r,'B'),('LIFE','B')])
        elif op=='SCALE': items.append(('S',(r,),(_q(e[2]),fid[e[3]]))); acc.append([(r,'B')])
        else:
            s=e[2]; items.append(('A' if op=='ADD' else 'Y',(r,s),(_q(e[3]),fid[e[4]])))
            acc.append([(r,'W'),(s,'R')] if (op=='ADD' and r<n and s<n and r not in OWN and s not in OWN) else [(r,'B'),(s,'B')])
    return n,live,OWN,fid,isH,items,acc

def _colors(w,n,isH,fid,items,rounds=3):
    H=[r for r in range(n) if isH(r)]
    col={r:_h((fid[w['initial'][r]],fid[w['final'][r]])) for r in H}
    if not H: return col
    inc=collections.defaultdict(list)       # helper -> item indices
    for i,(k,regs,rest) in enumerate(items):
        for r in set(regs):
            if r in col: inc[r].append(i)
    def tok(r): return ('h',col[r]) if r in col else r
    for _ in range(rounds):
        sig=[(k,tuple(tok(r) for r in regs),rest) for (k,regs,rest) in items]
        new={}
        for h in H:
            new[h]=_h((col[h],sorted(repr((sig[i],tuple(j for j,r in enumerate(items[i][1]) if r==h))) for i in inc[h])),8)
        col=new
    return col

def canon_form(w):
    n,live,OWN,fid,isH,items,acc=_prepare(w)
    col=_colors(w,n,isH,fid,items)
    def tok(r): return ('h',col[r]) if r in col else ('o' if r in OWN else 'r',r)
    key=[(k,tuple(tok(r) for r in regs),rest) for (k,regs,rest) in items]
    # epochs per register
    tl=collections.defaultdict(list)
    for i,a in enumerate(acc):
        for reg,kd in a: tl[reg].append((kd,i))
    epoch_of=collections.defaultdict(list)     # item -> [(reg,epoch idx)]
    epochs={}
    for reg,l in tl.items():
        E=[];last=None
        for kd,i in l:
            if kd!='B' and E and last==kd: E[-1].append(i)
            else: E.append([i])
            last=kd
        epochs[reg]=E
        for ei,m in enumerate(E):
            for i in m: epoch_of[i].append((reg,ei))
    need=[len(epoch_of[i]) for i in range(len(items))]
    rem={reg:len(E[0]) for reg,E in epochs.items()}; cur={reg:0 for reg in epochs}
    heap=[]
    def activate(reg):
        for i in epochs[reg][cur[reg]]:
            need[i]-=1
            if need[i]==0: heapq.heappush(heap,(key[i],i))
    for reg in epochs: activate(reg)
    order=[]; label={}
    while heap:
        k,i=heapq.heappop(heap); order.append(i)
        for reg,ei in epoch_of[i]:
            rem[reg]-=1
            if rem[reg]==0 and ei+1<len(epochs[reg]):
                cur[reg]=ei+1; rem[reg]=len(epochs[reg][ei+1]); activate(reg)
    assert len(order)==len(items),'canon: dependency cycle'
    out=[]
    def lab(r):
        if r in col:
            if r not in label: label[r]=len(label)
            return ('h',label[r])
        return ('o' if r in OWN else 'r',r)
    for i in order:
        k,regs,rest=items[i]; out.append((k,tuple(lab(r) for r in regs),rest))
    hdr=[n,legal.nown(w),tuple(sorted(w['live'])),tuple(w.get('ports',())),tuple(sorted(legal.retired_of(w)))]
    reg_rows=[(r,fid[w['initial'][r]],fid[w['final'][r]]) for r in range(n) if r not in col]
    hl=sorted((label[h],fid[w['initial'][h]],fid[w['final'][h]]) for h in label)
    un=sorted((fid[w['initial'][h]],fid[w['final'][h]]) for h in col if h not in label)
    return (hdr,reg_rows,hl,un),out
def canon_hash(w):
    hd,items=canon_form(w); m=hashlib.blake2b(digest_size=16); m.update(repr(hd).encode())
    for it in items: m.update(repr(it).encode())
    return m.hexdigest()
