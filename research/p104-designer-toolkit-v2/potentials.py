"""potentials -- law-derived structural potentials Phi(word) for search and generator look-ahead (HEURISTICS.  Scope [TOOLING / search heuristics].
No side effects at import; no env is read or set.  Words are dicts (initial, live, frames, program) or paths/aliases (tkcommon.load).

Every potential is an AVOIDABLE COST or a CAPACITY under a stated law; none uses a reference word's constants (anti-copying rule, module docstring sec. 0).
Laws used:
  R0 law (EXACT accounting, gapmap/kernel2net): R0(reg) = D ln D - sum_i r_i ln r_i over the register's MOVE chain dims; additive over jumps; kappa ~ 1/(131.2 + .02364 R0) (MODEL).
  Nesting law (EXACT, legal.py): public frames only ascend, owned only descend; content at frame g reaches only registers whose later frames contain g.
  Rank criterion (EXACT, JOINTFRAMES sec. 1): a late birth at g needs its junk column in the span of registers co-present at g; r(g) readers need <= r(g) independent carriers.
  Kill precondition (EXACT, k2 mvKill): a rung (stop) can be deleted only if it holds ADDs only and each ADD is re-deliverable.
All per-register potentials are sums of per-register terms (per_reg=True returns the terms), so a generator updates them by recomputing only the registers its edit touches.

API
  stops(w)                  -> {r: [Stop(dim, frame, nadd, blocked, events)]}  (public registers, chain order)
  rung_slack(w, p=.5)       -> F0..F3 of k2phi.inc (EXACT parity with the C++ PHI line, tests/heuristics_test.py)
  event_slack(w, cap=26000) -> F4 (insertion capacity)
  lifetime_slack(w)         -> R0 a helper saves if born at its first-use stop (start) / ended at its last-use stop (end): MODEL ceiling (needs the rank criterion to be realised)
  idle_partners(w)          -> helpers whose last event is a READ, idling above it: count and idle-tail R0 (BOTTOMSHARE dead partners), MODEL ceiling
  handoff(w, cuts=(5,6,7))  -> per cut c: registers crossing c, mean jump length across c, R0 that ending each crossing chain at its last stop <= c would save (law upper bound)
  market(w)                 -> per frame g: k(g) co-present registers with events, r(g) readers (Y with final frame containing g); late-birth R0 at frames with k(g)-1 >= r(g)
  shared_subsums(w)         -> duplicated register values (same projective value held by two registers: one could serve both) and bracket pairs z+=ch ... z-=ch (cancellation)
  side_slack(w)             -> admit.check slacks of gamma, delta, events, scalar at the word's profile tail (EXACT, slow ~1 s)
  delivery(w)               -> D0..D3 of k2phi.inc via the C++ engine (needs its Index; ~1 s): kill-ready R0, one-delivery-away R0, ...
  score(w, weights=None, expensive=False) -> dict of every cheap feature + 'phi' = sum weights[k]*feature[k]
"""
import os,sys,math,collections,random
HERE=os.path.dirname(os.path.abspath(__file__))
for _p in (HERE,os.path.join(HERE,'synth')):
    if _p not in sys.path: sys.path.insert(0,_p)
Stop=collections.namedtuple('Stop','dim frame nadd blocked events')
def _H(r): return r*math.log(r) if r>0 else 0.0
def tax(ds):
    """R0 law on a set of chain dims"""
    ds=sorted(set(ds))
    if len(ds)<2: return 0.0
    return _H(ds[-1]-ds[0])-sum(_H(b-a) for a,b in zip(ds,ds[1:]))
def _load(w):
    if isinstance(w,dict): return w
    import tkcommon; return tkcommon.load(w)[1]
def _roles(w):
    import kernel2net as KN; return KN.roles(w)
def _dims(w): return [len(b) for b in w['frames']]
def stops(w):
    w=_load(w); n=len(w['initial']); role=_roles(w); dim=_dims(w)
    cur={r:w['initial'][r] for r in range(n) if role(r)!='O'}; st={r:[] for r in cur}; cn={r:0 for r in cur}; cb={r:False for r in cur}; ce={r:[] for r in cur}
    def close(r): st[r].append(Stop(dim[cur[r]],cur[r],cn[r],cb[r],ce[r])); cn[r]=0; cb[r]=False; ce[r]=[]
    for i,e in enumerate(w['program']):
        o=e[0]
        if o=='MOVE':
            r=e[1]
            if r in cur: close(r); cur[r]=e[3]
        elif o=='ADD':
            for r in (e[1],e[2]):
                if r in cur: cn[r]+=1; ce[r].append(i)
        elif o=='COPY':
            for r in (e[1],e[2]):
                if r in cur: cb[r]=True; ce[r].append(i)
        else:
            r=e[1]
            if r in cur: cb[r]=True; ce[r].append(i)
    for r in cur: close(r)
    return st
def _fixed(role,r,j,ns): return role(r) in 'XY' and (j==0 or j==ns-1)
def rung_slack(w,p=.5,per_reg=False,_st=None):
    """F0 sum s_j p^n_j, F1 sum s_j [n_j<=1], F2 blocked stops, F3 sum n_j/100 over killable stops (k2phi.inc law, EXACT parity)"""
    w=_load(w); role=_roles(w); st=_st or stops(w); F=[0.0]*4; pr={}
    for r,L in st.items():
        ns=len(L)
        if ns<2: continue
        dims=[s.dim for s in L]; T=tax(dims); f=[0.0]*4
        for j,s in enumerate(L):
            if _fixed(role,r,j,ns): continue
            if s.blocked: f[2]+=1; continue
            if s.nadd<=0: continue
            sj=T-tax(dims[:j]+dims[j+1:]); f[0]+=sj*p**s.nadd; f[1]+=sj if s.nadd<=1 else 0; f[3]+=s.nadd*.01
        for k in range(4): F[k]+=f[k]
        if per_reg: pr[r]=f
    out=dict(F0_rung=F[0],F1_free=F[1],F2_blocked=F[2],F3_drain=F[3])
    if per_reg: out['per_reg']=pr
    return out
def event_slack(w,cap=26000):
    w=_load(w); return dict(F4_events=(cap-len(w['program']))*1e-3)
def lifetime_slack(w,per_reg=False,_st=None):
    """helper h: start = tax(chain) - tax(chain from its first stop holding an event); end = tax(chain) - tax(chain up to its last stop holding an event).  MODEL ceiling."""
    w=_load(w); role=_roles(w); st=_st or stops(w); S=E=B=0.0; pr={}
    for r,L in st.items():
        if role(r)!='H' or len(L)<2: continue
        dims=[s.dim for s in L]; used=[j for j,s in enumerate(L) if s.events]
        if not used: continue
        a,b=used[0],used[-1]; T=tax(dims); s=T-tax(dims[a:]); e=T-tax(dims[:b+1]); bo=T-tax(dims[a:b+1])
        S+=s; E+=e; B+=bo
        if per_reg: pr[r]=(s,e,bo)
    out=dict(L_start=S,L_end=E,L_both=B)
    if per_reg: out['per_reg']=pr
    return out
def idle_partners(w,_st=None):
    """helpers whose LAST event reads them (source of an ADD) and that then idle to their end: count, idle-tail R0 (end-early ceiling of dead partners)"""
    w=_load(w); role=_roles(w); st=_st or stops(w); P=w['program']; cnt=0; R=0.0
    for r,L in st.items():
        if role(r)!='H' or len(L)<2: continue
        used=[j for j,s in enumerate(L) if s.events]
        if not used: continue
        b=used[-1]; last=L[b].events[-1]; e=P[last]
        if e[0]=='ADD' and e[2]==r and b<len(L)-1:
            dims=[s.dim for s in L]; cnt+=1; R+=tax(dims)-tax(dims[:b+1])
    return dict(I_count=cnt,I_R0=R)
def handoff(w,cuts=(5,6,7),_st=None):
    """cut c: registers whose chain crosses c (a jump a<=c<b), their mean jump length across c, and R0 saved if each ended at its last stop <= c (law upper bound: content above c must
    then be carried by someone else, so this is the avoidable cost a handoff can at most recover)"""
    w=_load(w); st=_st or stops(w); out={}
    for c in cuts:
        n=0; J=0; R=0.0
        for r,L in st.items():
            dims=[s.dim for s in L]
            for a,b in zip(dims,dims[1:]):
                if a<=c<b:
                    n+=1; J+=b-a; below=[d for d in dims if d<=c]; R+=tax(dims)-tax(below); break
        out['H%d_n'%c]=n; out['H%d_jump'%c]=J/n if n else 0.0; out['H%d_R0'%c]=R
    return out
def _spans(w):
    sp=[]
    for b in w['frames']:
        s={0}
        for v in b: s|={x^v for x in s}
        sp.append(frozenset(s))
    return sp
def market(w,_st=None):
    """k(g) = public registers with an event at g; r(g) = Y mains whose FINAL frame contains g (nesting law: only they can read content at g).
    Necessary condition for late births at g (rank criterion): k(g)-1 >= r(g).  M_ready = start-late R0 of helpers whose first-use frame satisfies it (MODEL ceiling);
    M_gap = sum over first-use frames of max(0, r(g)-(k(g)-1)) (carriers missing)."""
    w=_load(w); role=_roles(w); st=_st or stops(w); sp=_spans(w)
    fin={r:L[-1].frame for r,L in st.items() if role(r)=='Y'}
    k=collections.Counter()
    for r,L in st.items():
        for s in L:
            if s.events: k[s.frame]+=1
    rc={}
    def readers(g):
        if g not in rc: rc[g]=sum(1 for y,f in fin.items() if sp[g]<=sp[f])
        return rc[g]
    ready=0.0; gap=0; nf=0
    for r,L in st.items():
        if role(r)!='H' or len(L)<2: continue
        used=[j for j,s in enumerate(L) if s.events]
        if not used or used[0]==0: continue
        g=L[used[0]].frame; rg=readers(g); kk=k[g]-1; dims=[s.dim for s in L]
        if kk>=rg: ready+=tax(dims)-tax(dims[used[0]:]); nf+=1
        else: gap+=rg-kk
    return dict(M_ready=ready,M_nready=nf,M_gap=gap)
_P61=(1<<61)-1
def shared_subsums(w,seed=12345):
    """random evaluation mod 2^61-1 (3 coordinates) of every register version; D_dup = versions whose projective value is ALSO held by another register at that time
    (one register could serve both readers: a merge/reuse opportunity), D_brk = bracket pairs z += c h ... z += -c h (junk-free difference, cancellation)."""
    from fractions import Fraction as Q
    w=_load(w); n=len(w['initial']); rnd=random.Random(seed); K=3
    val={r:[rnd.randrange(1,_P61) for _ in range(K)] for r in range(n)}
    def cm(c):
        q=Q(c); return q.numerator%_P61*pow(q.denominator%_P61,_P61-2,_P61)%_P61
    def key(v):
        if not any(v): return None
        i=next(j for j in range(K) if v[j]); inv=pow(v[i],_P61-2,_P61); return (i,)+tuple(x*inv%_P61 for x in v)
    held=collections.defaultdict(set); kr={}
    for r in range(n):
        kk=key(val[r]); kr[r]=kk
        if kk: held[kk].add(r)
    dup=0; last=collections.defaultdict(dict); brk=0
    def setv(r,v):
        nonlocal dup
        o=kr.get(r)
        if o: held[o].discard(r)
        kk=key(v); kr[r]=kk; val[r]=v
        if kk:
            if held[kk]: dup+=1
            held[kk].add(r)
    for e in w['program']:
        o=e[0]
        if o=='ADD':
            d,s,c=e[1],e[2],cm(e[3]); sv=val.get(s,[0]*K); dv=val.get(d,[0]*K)
            setv(d,[(a+c*b)%_P61 for a,b in zip(dv,sv)])
            q=Q(e[3]); pv=last[d].get(s)
            if pv is not None and pv==-q: brk+=1; del last[d][s]
            else: last[d][s]=q
        elif o=='COPY': setv(e[1],[cm(e[3])*b%_P61 for b in val.get(e[2],[0]*K)])
        elif o=='SCALE': c=cm(e[2]); setv(e[1],[c*b%_P61 for b in val[e[1]]])
        elif o in('INIT','CLEAR'): setv(e[1],[0]*K)
    return dict(D_dup=dup,D_brk=brk)
def side_slack(w):
    import admit
    rep=admit.check(_load(w)); out={}
    for c in rep['constraints']:
        nm=c['name'].lower()
        for key in ('gamma','delta','event','scalar'):
            if key in nm and ('S_'+key) not in out:
                try: out['S_'+key]=float(c['slack'])
                except Exception: pass
    return out
def delivery(w,binary=None):
    """D0..D3 from the C++ engine (k2phi.inc phiDeliv on the word's net, 1 iteration, no search effect)"""
    import tempfile,subprocess,kernel2net as KN
    from k2 import engine
    w=_load(w); d=tempfile.mkdtemp(prefix='phi_'); net=os.path.join(d,'w.net'); KN.dump_net(w,net)
    r=engine.run(net,'sa',dict(iters=1,flog=os.devnull,free=1),binary=binary)
    for ln in r['lines']:
        if ln.startswith('PHI'):
            t=ln.split('| D')[1].split(); F=ln.split('| F')[1].split('Phi')[0].split()
            return dict(D0_ready=float(t[0]),D1_one=float(t[1]),D2_soft=float(t[2]),D3_deliv=float(t[3]),cxx_F=[float(x) for x in F])
    raise RuntimeError('no PHI line: '+'\n'.join(r['lines'][-3:]))
CHEAP=('rung_slack','event_slack','lifetime_slack','idle_partners','handoff','market','shared_subsums')
def score(w,weights=None,expensive=False,cap=26000):
    """all cheap potentials (one stops() pass shared) + optional expensive ones; phi = sum weights[name]*value"""
    w=_load(w); st=stops(w); out={}
    out.update(rung_slack(w,_st=st)); out.update(event_slack(w,cap)); out.update(lifetime_slack(w,_st=st)); out.update(idle_partners(w,_st=st))
    out.update(handoff(w,_st=st)); out.update(market(w,_st=st)); out.update(shared_subsums(w))
    if expensive: out.update(side_slack(w)); out.update(delivery(w))
    out['phi']=sum(float(v)*out.get(k,0.0) for k,v in (weights or {}).items())
    return out
if __name__=='__main__':
    import json
    a=sys.argv[1:]; ex='--expensive' in a; a=[x for x in a if not x.startswith('--')]
    for p in a: print(p,json.dumps(score(p,expensive=ex),default=float))
