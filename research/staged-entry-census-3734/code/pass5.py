"""Pass 5: general form of the staged entry, other frames fixed.

For (h, P, c): v = e_h + w with w on ordinary non-restored helpers (a certificate only). Actual
releases a = M_c v - e_h. Constraint: a_r = 0 for every register r whose release is not frame
compatible (no slot of its commuting range hosts R = P + frame(r) inside both next frames).
Nonzero releases are then placed (latest compatible slot) and the word checked by frame_bill.
"""
import sys,json,time,bisect,itertools
import numpy as np
from fractions import Fraction as Q
from collections import defaultdict
from scipy.optimize import linprog
from timeline import *
from candidates import candidates
from construct import basis, span_masks
from construct2 import assemble, fill_frames, insertable, score
tag=sys.argv[1]; NS=int(sys.argv[2]) if len(sys.argv)>2 else 16
only=set(int(x) for x in sys.argv[3].split(',')) if len(sys.argv)>3 and sys.argv[3] else None
w=load(tag); ev=events(w); con=contacts(ev)
bill0,wd0,chain,start,end=C.frame_bill(w)
cand=candidates(w,ev,con,start,end)
if only: cand=[c for c in cand if c['h'] in only]
rest=set(map(int,w['helper_final'])); removed=set(w['removed'])
live=[r for r in range(704) if r not in removed]
D=[r for r in range(224,704) if r not in removed and r not in rest]
centres=set(w['centers'])
first_B=next(e['pos'] for e in ev if e['sec'] in ('cut','B','warp'))
# frame timeline
ftime=defaultdict(list); fval=defaultdict(list)
for r in start: ftime[r].append(-1); fval[r].append(start[r])
levels={C.V+int(t):C.span(U) for t,U in w['target_levels'].items()}
centre_done=False
blocks=defaultdict(list)          # positions where a release into r stops commuting
hwrites=defaultdict(list)
for e in ev:
    k=e['kind']; g=e['g']; p=e['pos']
    if k=='corr': continue
    if k in ('warp','awarp'): blocks[g[1]].append(p); hwrites[g[1]].append(p)
    elif g[0]=='add': blocks[g[2]].append(p); hwrites[g[1]].append(p)
    elif g[0]=='scale' and g[2]!=g[3]: blocks[g[1]].append(p); hwrites[g[1]].append(p)
    if e['sec'] in ('pre','comp'): continue
    if e['sec']=='cut':
        if not centre_done:
            for q,U in zip(w['centers'],w['center_frames']):
                served={levels.get(gg[1],C.ZERO) for gg in w['cut'] if gg[2]==q}
                T=C.span(U)
                for S in sorted(served,key=lambda m:-C.dim(m)): T=S
                ftime[q].append(p); fval[q].append(T)
            centre_done=True
        continue
    if k=='awarp': regs=[(g[1],C.span(g[4]))]
    elif k=='warp': regs=[(g[1],C.span(w['warps'][g[2]-1][4]))]
    else: regs=[(r,e['frame']) for r in C.touched(g)]
    for r,f in regs: ftime[r].append(p); fval[r].append(f)
def frame_at(r,p):
    i=bisect.bisect_left(ftime[r],p)-1; return fval[r][i]
def next_frame(r,p):
    i=bisect.bisect_left(ftime[r],p)
    return fval[r][i] if i<len(ftime[r]) else end[r]
def nxt(lst,p):
    i=bisect.bisect_left(lst,p); return lst[i] if i<len(lst) else len(ev)
def release_slot(h,P,c,r):
    """Latest slot hosting the release into r, or None. Frames are constant between contacts of r or
    h, so only those change points are tested."""
    if r==h or r in centres: return None
    stop=min(nxt(blocks[r],c),nxt(hwrites[h],c))
    lo=c if not (112<=r<224 or r<112) else max(c,first_B)
    if stop<lo: return None
    pts={stop}
    for lst in (ftime[r],ftime[h]):
        i=bisect.bisect_left(lst,lo); j=bisect.bisect_right(lst,stop)
        pts.update(lst[i:j])
    for p in sorted(pts,reverse=True):
        q=p
        while q>=lo and not insertable(ev,w,q): q-=1
        if q<lo: continue
        R=span_masks(P,frame_at(r,q))
        if (R & next_frame(r,q))==R and (R & next_frame(h,q))==R: return q
    return None
okpos=lambda e: e['sec'] in ('A','B','restore') or (e['sec']=='cut' and e['idx']==0)
samples=defaultdict(set); byh=defaultdict(list)
for c in cand: byh[c['h']].append(c)
for h,cs in byh.items():
    lo=min(c['lo'] for c in cs); hi=max(c['hi'] for c in cs)
    for p in set(np.linspace(lo,hi,NS).astype(int))|{hi}:
        while p<=hi and not okpos(ev[p]): p+=1
        if p<=hi: samples[p].add(h)
X=np.eye(704); cons=[]
for cc in w['initial_corrections']:
    row=np.zeros(704); row[cc['source']]=1; cons.append(row)
def solve(A_rows,h,slots):
    """min sum|a_r| over compatible r, subject to incompatible rows vanishing; returns v or None."""
    allowed=sorted(slots)
    inc=[r for r in live if r!=h and r not in slots]
    M=np.vstack([X[inc]]+([np.array(cons)] if cons else []))
    cols=[h]+[d for d in D if d!=h]
    Mc=M[:,cols]
    keep=np.where(np.abs(Mc).sum(0)>0)[0]
    if 0 not in keep: keep=np.r_[0,keep]
    Mc=Mc[:,keep]; cols=[cols[i] for i in keep]
    rows=np.where(np.abs(Mc).sum(1)>0)[0]; Mc=Mc[rows]
    # existence
    if Mc.shape[0]:
        sol,*_=np.linalg.lstsq(Mc[:,1:],-Mc[:,0],rcond=None) if Mc.shape[1]>1 else (np.zeros(0),)
        if np.linalg.norm(Mc[:,1:]@sol+Mc[:,0] if Mc.shape[1]>1 else Mc[:,0])>1e-8: return None
    # L1 on a: variables w (free), a = Xa v; |a| through t >= +-a
    Xa=X[allowed][:,cols]
    n=len(cols)-1; m=len(allowed)
    # variables : w (n, libres), t (m, >=0)
    cvec=np.r_[np.zeros(n),np.ones(m)]
    Aub=np.block([[Xa[:,1:],-np.eye(m)],[-Xa[:,1:],-np.eye(m)]]); bub=np.r_[-Xa[:,0],Xa[:,0]]
    Aeq=np.c_[Mc[:,1:],np.zeros((Mc.shape[0],m))] if Mc.shape[0] else None
    beq=-Mc[:,0] if Mc.shape[0] else None
    res=linprog(cvec,A_ub=Aub,b_ub=bub,A_eq=Aeq,b_eq=beq,bounds=[(None,None)]*n+[(0,None)]*m,method='highs')
    if res.status!=0: return None
    wv=res.x[:n]
    v={cols[0]:1.0,**{cols[i+1]:wv[i] for i in range(n) if abs(wv[i])>1e-10}}
    return v
def exact_release(h,c,v):
    """Propagate v exactly over [0,c); return a = M_c v - e_h, or None if a warp or correction sees v."""
    x={r:Q(q) for r,q in v.items() if q}
    for e in ev[:c]:
        k=e['kind']; g=e['g']
        if k=='corr':
            if x.get(g['source'],0): return None
            continue
        if k in ('warp','awarp'):
            if x.get(g[1],0): return None
            continue
        if g[0]=='add':
            s=x.get(g[2],0)
            if s:
                y=x.get(g[1],0)+Q(g[3],g[4])*s
                if y: x[g[1]]=y
                else: x.pop(g[1],None)
        elif g[0]=='scale':
            if g[1] in x: x[g[1]]*=Q(g[2],g[3])
    x[h]=x.get(h,0)-1
    return {r:q for r,q in x.items() if q}
results=[]; t0=time.time()
hi_all=max(samples) if samples else -1
for pos in range(0,hi_all+1):
    if pos in samples:
        for h in samples[pos]:
            for c in byh[h]:
                if not (c['lo']<=pos<=c['hi']): continue
                slots={}
                for r in live:
                    s=release_slot(h,c['P'],pos,r)
                    if s is not None: slots[r]=s
                v=solve(None,h,slots)
                if v is None:
                    results.append(dict(h=h,pos=pos,P=basis(c['P']),nslots=len(slots),status='no-identity')); continue
                v={r:Q(q).limit_denominator(1<<20) for r,q in v.items()}
                a=exact_release(h,pos,v)
                if a is None or any(r not in slots for r in a):
                    results.append(dict(h=h,pos=pos,P=basis(c['P']),nslots=len(slots),status='inexact')); continue
                ins=[(slots[r],['add',r,h,q.numerator,q.denominator]) for r,q in sorted(a.items())]
                try:
                    x,mark=assemble(w,ev,h,c['P'],pos,ins); x=fill_frames(x,mark)
                    b,wd,*_=C.frame_bill(x); C.hygiene(x)
                    results.append(dict(h=h,pos=pos,P=basis(c['P']),nslots=len(slots),status='ok',
                        a={str(r):str(q) for r,q in a.items()},v={str(r):str(q) for r,q in v.items()},
                        place={str(r):slots[r] for r in a},bill=b,widths=wd))
                except Exception as ex:
                    results.append(dict(h=h,pos=pos,P=basis(c['P']),nslots=len(slots),status='frames',
                        a={str(r):str(q) for r,q in a.items()},why=str(ex)[:120]))
    if pos%1000==0: print('pos',pos,len(results),round(time.time()-t0,1),flush=True)
    if pos==len(ev): break
    e=ev[pos]; g=e['g']; k=e['kind']
    if k in ('warp','awarp'): cons.append(X[g[1]].copy())
    elif k=='corr': pass
    elif g[0]=='add': X[g[1]]+=g[3]/g[4]*X[g[2]]
    elif g[0]=='scale': X[g[1]]*=g[2]/g[3]
json.dump(dict(bill0=bill0,widths0=wd0,results=results),open(f'pass5-{tag.replace("/","_")}.json','w'))
from collections import Counter
print('statuses',Counter(r['status'] for r in results))
print('helpers with a valid construction:',sorted({r['h'] for r in results if r['status']=='ok'}))
print('seconds',round(time.time()-t0,1))
