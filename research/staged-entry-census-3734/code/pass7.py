"""Pass 7: B windows, B frames re-solvable (A fixed).

Exact feasibility by the minimal B assignment (pointwise minimal among assignments keeping A and
the other entrances/terminals). Release vectors: pure retiming, sparse strict. Placements: several
frame-change points per recipient.
"""
import sys,json,time,bisect,itertools,os
import numpy as np
from fractions import Fraction as Q
from collections import defaultdict
from multiprocessing import Pool
from scipy.optimize import linprog
from timeline import *
from candidates import candidates
from construct import basis, span_masks
from construct2 import assemble, insertable, score
from repair import repair
TAG=sys.argv[1]; NCUT=int(sys.argv[2]); K=int(sys.argv[3])
w=load(TAG); ev=events(w); con=contacts(ev)
bill0,wd0,chain,start,end=C.frame_bill(w)
rest=set(map(int,w['helper_final'])); removed=set(w['removed'])
live=[r for r in range(704) if r not in removed]
D=[r for r in range(224,704) if r not in removed and r not in rest]
centres=set(w['centers'])
first_B=next(e['pos'] for e in ev if e['sec'] in ('cut','B','warp'))
ftime=defaultdict(list); blocks=defaultdict(list); hwrites=defaultdict(list)
for e in ev:
    k=e['kind']; g=e['g']; p=e['pos']
    if k=='corr': continue
    if k in ('warp','awarp'): blocks[g[1]].append(p); hwrites[g[1]].append(p); ftime[g[1]].append(p); continue
    if g[0]=='add': blocks[g[2]].append(p); hwrites[g[1]].append(p)
    elif g[0]=='scale' and g[2]!=g[3]: blocks[g[1]].append(p); hwrites[g[1]].append(p)
    if e['sec'] in ('A','B','restore'):
        for r in C.touched(g): ftime[r].append(p)
def nxt(lst,p):
    i=bisect.bisect_left(lst,p); return lst[i] if i<len(lst) else len(ev)
def positions(h,c,r,k):
    if r==h or r in centres: return []
    stop=min(nxt(blocks[r],c),nxt(hwrites[h],c))
    lo=max(c,first_B)
    if stop<lo: return []
    pts={stop,lo}
    for lst in (ftime[r],ftime[h]):
        i=bisect.bisect_left(lst,lo); j=bisect.bisect_right(lst,stop); pts.update(lst[i:j])
    out=[]
    for p in sorted(pts,reverse=True):
        q=p
        while q>=lo and not insertable(ev,w,q): q-=1
        if q>=lo and q not in out: out.append(q)
    if len(out)<=k: return out
    idx=sorted(set(np.linspace(0,len(out)-1,k).astype(int)))
    return [out[i] for i in idx]
def exact_release(h,c,v):
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
def evaluate(h,P,c,a,place):
    ins=[(place[r],['add',r,h,q.numerator,q.denominator]) for r,q in sorted(a.items())]
    out={}
    for mode in ('repair','minimalB'):
        try:
            x,mark=assemble(w,ev,h,P,c,ins); x,_=repair(x,mark,minimal_B=(mode=='minimalB'),cleanup=False)
            b,wd,*_=C.frame_bill(x); out[mode]=(b,wd)
        except Exception as ex:
            out[mode]=None
    return out
def work(hs):
    cand=[c for c in candidates(w,ev,con,start,end,(8,)) if c['h'] in hs and c['lo']>=first_B]
    byc=defaultdict(list)
    for cd in cand:
        for p in set(np.linspace(cd['lo'],cd['hi'],NCUT).astype(int))|{cd['hi']}:
            q=p
            while q<=cd['hi'] and not insertable(ev,w,q): q+=1
            if q<=cd['hi']: byc[q].append(cd)
    X=np.eye(704); cons=[]
    for cc in w['initial_corrections']:
        row=np.zeros(704); row[cc['source']]=1; cons.append(row)
    res=[]
    last=max(byc) if byc else -1
    for pos in range(last+1):
        for cd in byc.get(pos,()):
            h=cd['h']; P=cd['P']
            vecs=[]
            vecs.append(('retime',{h:Q(1)}))
            # sparse strict solution (greedy pursuit)
            A=np.vstack([X-np.eye(704)]+([np.array(cons)] if cons else []))
            ah=A[:,h]; act=[d for d in D if d!=h and np.any(np.abs(A[:,d])>1e-12)]
            if act and np.any(np.abs(ah)>1e-12):
                Ad=A[:,act]; nrm=np.sqrt((Ad*Ad).sum(0)); sel=[]; r=-ah.copy()
                for _ in range(10):
                    sc=np.abs(Ad.T@r)/nrm; sc[sel]=-1; k=int(np.argmax(sc))
                    if sc[k]<1e-12: break
                    sel.append(k); sol,*_=np.linalg.lstsq(Ad[:,sel],-ah,rcond=None); r=-ah-Ad[:,sel]@sol
                    if np.linalg.norm(r)<1e-9:
                        vecs.append(('strict',{h:Q(1),**{act[i]:Q(sol[j]).limit_denominator(1<<20) for j,i in enumerate(sel)}})); break
            seen=set()
            for kind,v in vecs:
                a=exact_release(h,pos,v)
                if a is None: continue
                key=tuple(sorted(a))
                if key in seen: continue
                seen.add(key)
                opts={r:positions(h,pos,r,K) for r in a}
                if any(not o for o in opts.values()):
                    res.append(dict(h=h,P=basis(P),cut=pos,kind=kind,a={str(r):str(q) for r,q in a.items()},status='no-slot')); continue
                rs=list(a)
                if len(rs)<=2: combos=list(itertools.product(*[opts[r] for r in rs]))
                else:
                    m=min(len(o) for o in opts.values())
                    combos=[tuple(opts[r][min(i,len(opts[r])-1)] for r in rs) for i in range(K)]
                    combos+=[tuple(opts[r][-1] if r==s else opts[r][0] for r in rs) for s in rs]
                best=None
                for combo in dict.fromkeys(combos):
                    place=dict(zip(rs,combo))
                    out=evaluate(h,P,pos,a,place)
                    for mode,val in out.items():
                        if val is None: continue
                        b,wd=val; s=score(b)
                        if best is None or s<best['score']:
                            best=dict(score=s,mode=mode,bill=b,widths=wd,place={str(r):p for r,p in place.items()})
                res.append(dict(h=h,P=basis(P),cut=pos,kind=kind,a={str(r):str(q) for r,q in a.items()},
                                status='ok' if best else 'infeasible',best=best))
        if pos==len(ev): break
        e=ev[pos]; g=e['g']; k=e['kind']
        if k in ('warp','awarp'): cons.append(X[g[1]].copy())
        elif k=='corr': pass
        elif g[0]=='add': X[g[1]]+=g[3]/g[4]*X[g[2]]
        elif g[0]=='scale': X[g[1]]*=g[2]/g[3]
    return res
if __name__=='__main__':
    allc=candidates(w,ev,con,start,end,(8,))
    hs=sorted({c['h'] for c in allc if c['lo']>=first_B})
    if len(sys.argv)>4 and sys.argv[4]: hs=[h for h in hs if h in set(int(x) for x in sys.argv[4].split(','))]
    chunks=[hs[i::5] for i in range(5)]
    t0=time.time()
    with Pool(5) as pool: parts=pool.map(work,chunks)
    res=[r for p in parts for r in p]
    json.dump(dict(bill0=bill0,widths0=wd0,results=res),open(f'pass7-{TAG.replace("/","_")}.json','w'))
    from collections import Counter
    print('statuses',Counter((r['kind'],r['status']) for r in res))
    print('feasible helpers:',sorted({r['h'] for r in res if r['status']=='ok'}))
    print('seconds',round(time.time()-t0,1))
