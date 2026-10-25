"""Constructor v2: each release d += w_d h slides to a chosen slot of its commuting range; minimal release frames."""
import copy,itertools
from fractions import Fraction as Q
from timeline import *
from construct import exact_fixed, span_masks, basis

def commute_range(ev,c,d,h):
    """Positions p >= c where the release into d can be inserted (before event p).
    Stops at the first read, scale or warp of d, or write of h."""
    out=[c]
    for p in range(c,len(ev)):
        e=ev[p]; g=e['g']; k=e['kind']
        if k=='corr': continue
        if k in ('warp','awarp'):
            if g[1] in (d,h): break
        elif g[0]=='add':
            if g[2]==d or g[1]==h: break
        elif g[0]=='scale':
            if g[1] in (d,h) and g[2]!=g[3]: break
        out.append(p+1)
    return out

def insertable(ev,w,p):
    if p>=len(ev): return True
    e=ev[p]
    if e['sec']=='A': return e['idx']>=w['prelude_events']
    return e['sec'] in ('B','warp','restore') or (e['sec']=='cut' and e['idx']==0)

def assemble(w,ev,h,P,c,inserts):
    """inserts: list of (p, gate without frame). Deletes h's contacts before c. Returns the word (release frames still to fill)."""
    dele={(e['sec'],e['idx']) for e in ev[:c] if h in touched(e)}
    for e in ev[:c]:
        if h in touched(e): assert e['kind']=='add' and e['g'][2]==h,(e['sec'],e['idx'])
    at={}
    for p,g in inserts: at.setdefault(p,[]).append(g)
    x=copy.deepcopy(w)
    npre=w['prelude_events']
    x['compensation']=[g for i,g in enumerate(w['compensation']) if ('comp',i) not in dele]
    A=[];B=[];Rs=[];positions={};mark=[]
    for e in ev:
        p=e['pos']
        if p in at:
            sec=e['sec']; tgt={'A':A,'cut':B,'B':B,'warp':B,'restore':Rs}[sec]
            for g in at[p]: tgt.append(g); mark.append(g)
        if e['sec']=='A':
            if ('A',e['idx']) not in dele: A.append(copy.deepcopy(e['g']))
        elif e['sec']=='B':
            positions[e['idx']]=positions.get(e['idx'],len(B)) if False else positions.get(e['idx'],None)
            if ('B',e['idx']) not in dele: B.append(copy.deepcopy(e['g']))
        elif e['sec']=='restore':
            if ('restore',e['idx']) not in dele: Rs.append(copy.deepcopy(e['g']))
    for g in at.get(len(ev),[]): Rs.append(g); mark.append(g)
    x['A']=A; x['B']=B; x['restore']=Rs
    x['prelude_events']=npre-sum(1 for (s,i) in dele if s=='A' and i<npre)
    # warps: position = B index of the first B gate that followed the warp
    newidx={}; j=0
    for e in ev:
        if e['sec']=='B' and ('B',e['idx']) not in dele:
            pass
    # recompute by walking the events
    j=0; warp_pos={}
    for e in ev:
        if e['pos'] in at and e['sec'] in ('cut','B','warp'): j+=len(at[e['pos']])
        if e['sec']=='warp': warp_pos[e['idx']]=j
        if e['sec']=='B' and ('B',e['idx']) not in dele: j+=1
    for k,rec in enumerate(x['warps'],1): rec[0]=warp_pos[k]
    x['start_extra'][str(h)]=list(basis(P))
    return x,mark

def fill_frames(x,mark):
    """Minimal frame of each release: join of the current frames of its two registers (frame_bill order)."""
    ids={id(g) for g in mark}
    bill,widths,chain,start,end=None,None,None,None,None
    ports=x['ports']; removed=set(x['removed'])
    cur={}
    for r in range(704):
        if r in removed: continue
        if r<112: cur[r]=C.span((ports[r],))
        else: cur[r]=C.ZERO
    for q,U in x['start_extra'].items(): cur[int(q)]=C.span(U)
    for i,g in enumerate(x['A']):
        if g[0]=='warp': cur[g[1]]=C.span(g[4]); continue
        if id(g) in ids:
            R=span_masks(cur[g[1]],cur[g[2]]); g.append(basis(R))
        for r in C.touched(g): cur[r]=C.span(g[-1])
    levels={C.V+int(t):C.span(U) for t,U in x['target_levels'].items()}
    for q,U in zip(x['centers'],x['center_frames']):
        served={levels.get(gg[1],C.ZERO) for gg in x['cut'] if gg[2]==q}
        T=C.span(U)
        for S in sorted(served,key=lambda m:-C.dim(m)): T=S
        cur[q]=T
    at={}
    for k,rec in enumerate(x['warps'],1): at.setdefault(rec[0],[]).append(k)
    for p in range(len(x['B'])+1):
        for k in at.get(p,()): cur[x['warps'][k-1][1]]=C.span(x['warps'][k-1][4])
        if p<len(x['B']):
            g=x['B'][p]
            if id(g) in ids:
                R=span_masks(cur[g[1]],cur[g[2]]); g.append(basis(R))
            for r in C.touched(g): cur[r]=C.span(g[-1])
    for g in x['restore']:
        if id(g) in ids:
            R=span_masks(cur[g[1]],cur[g[2]]); g.append(basis(R))
        for r in C.touched(g): cur[r]=C.span(g[-1])
    x['cleanup']=C.derive_cleanup(x)
    return x

def try_build(w,ev,h,P,c,v,maxcombo=64):
    """Try release placements (latest first). Returns (word, bill, widths, placement) or (None, reason)."""
    donors={r:Q(q) for r,q in v.items() if r!=h and q}
    opts={}
    for d in donors:
        rng=[p for p in commute_range(ev,c,d,h) if insertable(ev,w,p)]
        if not rng: return None,('no slot for',d)
        # slots just before an event touching d, then the range end; latest first
        key=[p for p in rng if p<len(ev) and d in touched(ev[p])]
        cand=sorted(set(key+[rng[-1],rng[0]]),reverse=True)[:4]
        opts[d]=cand
    best=None; last=None
    ds=list(donors)
    late=[opts[d][0] for d in ds]; early=[opts[d][-1] for d in ds]
    combos=[late,early]+[[early[i] if i==j else late[i] for i in range(len(ds))] for j in range(len(ds))]
    tried=set()
    for combo in combos:
        if tuple(combo) in tried: continue
        tried.add(tuple(combo))
        ins=[(p,['add',d,h,donors[d].numerator,donors[d].denominator]) for d,p in zip(ds,combo)]
        try:
            x,mark=assemble(w,ev,h,P,c,ins); x=fill_frames(x,mark)
            b,wd,*_=C.frame_bill(x); C.hygiene(x)
        except Exception as ex:
            last=str(ex)[:120]; continue
        if best is None or score(b)<score(best[1]): best=(x,b,wd,dict(zip(ds,combo)))
    return (best if best else (None,last))

def score(b):
    a=0.00173
    return sum(n*r**(1-a) for r,n in b.items())
