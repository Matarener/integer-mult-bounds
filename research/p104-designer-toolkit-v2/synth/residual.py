"""synth.residual -- RESIDUAL lane: absorb part of the x_i residual AT THE SOURCE (the owned root's descent).  See ../module docstring.

Spec key `residual: taps` (frontgen, back end 'star' only).  Construction ('reverse-accumulating descent'):
  root k descends along a flag H_k = F_8 > F_7 > ... > F_1 = <l_k> (rank-1 owned MOVEs, owned tax 7 ln 7 per root),
  at F_t: first the TAPS (copies u(j,k) of the readers j whose tap stage is t receive cin*root), then the root ADDs the carriers of the ports of F_t \\ F_{t-1}.
  So a reader tapping at F_t receives root_k restricted to ports(H_k) \\ ports(F_t).  F_t inside H_k and inside Q_j means every port of F_t is ORTHOGONAL
  to p_j: the N_j (non-orthogonal) part is untouched (exactness kept), and the residual of root k on ports(F_t) is never created.
  A reader taps at the largest flag frame inside Q_j.  Ports added at F_1 (seen by nobody) are dropped with their carriers.
Flags: beam search minimising residual NONZEROS (data/residual_flags.json, deterministic). On a geometry-hash miss the in-module Fraction search is SLOW (>5 min): pre-seed the cache with ext/RESIDUAL/flag2.py (numpy).
plan(ctx) -> dict(stage_of_port={(k,i):t or None}, frames={(k,t):basis}, tap={(j,k):t}, res=[[Fraction]] (the tapped residual), info)
"""
import os,json,hashlib
from fractions import Fraction as Q
HERE=os.path.dirname(os.path.abspath(__file__)); DATA=os.path.join(HERE,'data','residual_flags.json')
par=lambda a,b:bin(a&b).count('1')&1
def _span(b):
    s={0}
    for v in b: s|={x^v for x in s}
    return s
def _basis(vs):
    b=[]; sp={0}
    for v in vs:
        if v not in sp: b.append(v); sp|={x^v for x in sp}
    return b
def _tapped_res(ports,U,line,S4,C2,flags):
    m=len(ports); K=len(S4)
    res=[[Q(sum(2*C2[j][k]*S4[k][i] for k in range(K)),4)-(1 if i==j else 0) for i in range(m)] for j in range(m)]
    tap={}
    for k in range(K):
        fl=flags.get(k)
        if not fl: continue
        sp=[_span(F) for F in fl]
        for j in range(m):
            if not C2[j][k]: continue
            t=max(t for t,F in enumerate(fl) if all(par(v,ports[j])==0 for v in F))
            tap[(j,k)]=t
            for i in range(m):
                if S4[k][i] and ports[i] in sp[t]: res[j][i]-=Q(2*C2[j][k]*S4[k][i],4)
    return res,tap
def _nnz(res): return sum(1 for r in res for v in r if v)
def search_flags(ports,U,line,S4,C2,beam=8,passes=2):
    K=len(S4); flags={}
    Hk={k:[v for v in range(512) if par(v,U[k])==0] for k in range(K)}
    for _ in range(passes):
        for k in range(K):
            cur=[[line[k]]]; cands=[cur]
            for t in range(2,8):
                nxt=[]
                for fl in cands:
                    top=_span(fl[-1]); seen=set()
                    for v in Hk[k]:
                        if v in top: continue
                        key=frozenset(_span(fl[-1]+[v]))
                        if key in seen: continue
                        seen.add(key); nf=fl+[_basis(fl[-1]+[v])]; flags[k]=nf
                        nxt.append((_nnz(_tapped_res(ports,U,line,S4,C2,flags)[0]),nf))
                nxt.sort(key=lambda x:x[0]); cands=[c[1] for c in nxt[:beam]]
            flags[k]=cands[0]
    return flags
def geo_hash(ports,U,line,S4,C2): return hashlib.sha256(json.dumps([ports,U,line,S4,C2]).encode()).hexdigest()[:16]
def load_flags(ports,U,line,S4,C2):
    h=geo_hash(ports,U,line,S4,C2)
    if os.path.exists(DATA):
        J=json.load(open(DATA))
        if J.get('hash')==h: return {int(k):v for k,v in J['flags'].items()}
    fl=search_flags(ports,U,line,S4,C2)
    try: json.dump(dict(hash=h,flags={str(k):v for k,v in fl.items()}),open(DATA,'w'))
    except OSError: pass
    return fl
def plan(ctx):
    ports,U,line,S4,C2=ctx['ports'],ctx['U'],ctx['line'],ctx['S4'],ctx['C2']; m=len(ports); K=len(S4)
    flags=load_flags(ports,U,line,S4,C2)
    res,tap=_tapped_res(ports,U,line,S4,C2,flags)
    # stage of each root port: the largest t with p_i NOT in F_t (added at F_{t+1}); t index into flag list (0 = <l_k>), stage 7 = H_k itself
    stage={}; dropped=0
    for k in range(K):
        sp=[_span(F) for F in flags[k]]
        for i in range(m):
            if not S4[k][i]: continue
            inside=[t for t in range(len(sp)) if ports[i] in sp[t]]
            t0=min(inside) if inside else len(sp)          # smallest flag frame containing p_i; added at that frame (len(sp) = at H_k)
            if t0==0: stage[(k,i)]=None; dropped+=1      # only F_1=<l_k> contains it: added after the last tap, never seen
            else: stage[(k,i)]=t0
    # sanity: a reader tapping at t sees exactly the ports with stage > t
    for (j,k),t in tap.items():
        spt=_span(flags[k][t])
        for i in range(m):
            if S4[k][i] and ((stage[(k,i)] is not None and stage[(k,i)]>t) != (ports[i] not in spt)): raise AssertionError('tap order')
    frames={(k,t):flags[k][t] for k in range(K) for t in range(len(flags[k]))}
    return dict(stage=stage,frames=frames,tap=tap,res=res,flags=flags,info=dict(residual_nnz=_nnz(res),dropped_carriers=dropped,tap_hist={t:sum(1 for v in tap.values() if v==t) for t in range(7)}))
