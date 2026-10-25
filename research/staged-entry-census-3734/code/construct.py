"""Literal staged-entry construction on a BORROW-WORD (first version: all releases at the cut)."""
import copy
from fractions import Fraction as Q
from timeline import *

def frames_before(w,ev,c):
    """Current frame of every register just before event c (old word), simulated as in frame_bill."""
    bill,widths,chain,start,end=C.frame_bill(w)
    cur=dict(start)
    centre_done=False
    levels={C.V+int(t):C.span(U) for t,U in w['target_levels'].items()}
    for e in ev[:c]:
        k=e['kind']; g=e['g']
        if e['sec'] in ('corr','pre','comp'): continue
        if e['sec']=='cut':
            if not centre_done:
                for q,U in zip(w['centers'],w['center_frames']):
                    served={levels.get(gg[1],C.ZERO) for gg in w['cut'] if gg[2]==q}
                    T=C.span(U)
                    for S in sorted(served,key=lambda m:-C.dim(m)): T=S
                    cur[q]=T
                centre_done=True
            continue
        if k=='awarp':
            cur[g[1]]=C.span(g[4]); continue
        if k=='warp':
            cur[g[1]]=C.span(w['warps'][g[2]-1][4]); continue
        for r in C.touched(g): cur[r]=e['frame']
    return cur

def exact_fixed(w,ev,c,v):
    """v: dict register->Fraction. Propagate v exactly over [0,c); true iff M_c v = v and no warp or correction sees v."""
    x={r:Q(q) for r,q in v.items() if q}
    for e in ev[:c]:
        k=e['kind']; g=e['g']
        if k=='corr':
            if x.get(g['source'],0): return False,'correction'
            continue
        if k in ('warp','awarp'):
            if x.get(g[1],0): return False,('warp',e['pos'])
            continue
        if g[0]=='add':
            s=x.get(g[2],0)
            if s:
                y=x.get(g[1],0)+Q(g[3],g[4])*s
                if y: x[g[1]]=y
                else: x.pop(g[1],None)
        elif g[0]=='scale':
            if g[1] in x: x[g[1]]*=Q(g[2],g[3])
    want={r:Q(q) for r,q in v.items() if q}
    return x==want, None

def build(w,ev,h,P,c,v,R=None):
    """Delete h's contacts before c, insert d += w_d h just before event c, raise h's entrance to P."""
    con=[e for e in ev[:c] if h in touched(e)]
    for e in con:
        g=e['g']
        assert e['kind']=='add' and g[2]==h, ('contact non supprimable',e['sec'],e['idx'],g)
    donors={r:Q(q) for r,q in v.items() if r!=h and q}
    if R is None:
        cur=frames_before(w,ev,c)
        R=P
        for d in donors: R=span_masks(R,cur[d])
    Rb=basis(R)
    rel=[['add',d,h,q.numerator,q.denominator,list(Rb)] for d,q in sorted(donors.items())]
    x=copy.deepcopy(w)
    dele={(e['sec'],e['idx']) for e in con}
    for sec in ('compensation','A','restore'):
        key={'compensation':'comp'}.get(sec,sec)
        x[sec]=[g for i,g in enumerate(w[sec]) if (key,i) not in dele]
    # position d'insertion
    e=ev[c] if c<len(ev) else None
    sec=e['sec'] if e else 'restore_end'
    if sec=='A':
        ndel=sum(1 for (s,i) in dele if s=='A' and i<e['idx'])
        j=e['idx']-ndel; x['A']=x['A'][:j]+rel+x['A'][j:]
        bpos=None
    elif sec in ('cut','B','warp'):
        if sec=='cut': bpos=0
        elif sec=='B': bpos=e['idx']
        else: bpos=w['warps'][e['idx']-1][0]   # before B[p] but after the warps at p
    elif sec=='restore':
        ndel=sum(1 for (s,i) in dele if s=='restore' and i<e['idx'])
        j=e['idx']-ndel; x['restore']=x['restore'][:j]+rel+x['restore'][j:]
        bpos=None
    else:
        raise ValueError('cut inside '+sec)
    # B: deletions, then insertion, warps shifted
    nb=[];positions={}
    for i in range(len(w['B'])+1):
        positions[i]=len(nb)
        if bpos is not None and i==bpos: nb+=rel
        if i==len(w['B']): break
        if ('B',i) in dele: continue
        nb.append(copy.deepcopy(w['B'][i]))
    x['B']=nb
    for rec in x['warps']: rec[0]=positions[rec[0]]
    x['start_extra'][str(h)]=list(basis(P))
    x['cleanup']=C.derive_cleanup(x)
    return x,R

def span_masks(a,b):
    pts=C.points(a); out=a
    for y in C.points(b):
        if not out>>y&1:
            out|=sum(1<<(p^y) for p in C.points(out))
    return out

def basis(mask):
    """Echelon basis (decreasing leading bits) of a subspace given as a point-set mask."""
    pts=C.points(mask); bas=[]
    for p in sorted(pts,reverse=True):
        q=p
        for b in bas:
            if q^b<q: q^=b
        if q: bas.append(q)
    # decreasing leading-bit order
    bas.sort(reverse=True)
    assert C.span(tuple(bas))==mask
    return bas
