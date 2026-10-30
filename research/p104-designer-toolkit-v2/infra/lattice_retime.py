"""EXACT-LATTICE RETIMING of a fixed circuit with the verifier's real freedom  (successor of P104CH/dims_relax.py).
Fixed: event order, ADD/COPY/SCALE operands (value DAG), stops (MOVE count per register).  Free: the SUBSPACE of F2^9 at every
ADD-equal-frame cluster, subject to  L(c) <= F <= U(c)  (L = sum / U = intersection of ANCHORED frames below/above),
strict nesting along register chains (owned: descending), literal pins only on X initial <p_i> and Y final p_j^perp (MODE VERIFIER)
or on all initial/final (MODE P104CH, reproduces the 'anchored' setting).  Helper credit rank = dim(final)-dim(initial) >= 1.
Domains: all subspaces in [L,U] when dim(U/L)<=5 (<=374), else {native frame, L, U, word frames inside [L,U]}.
Objective: linearised kappa (cwT/cwP exact marginal tables x18).  Output: realised WORD (frames rewritten) -> legal.check + exact kappa.
usage: lattice_retime.py WORD MODE TL OUT.json.gz     (run via hq; CP-SAT)"""
import sys,os,collections,itertools,gzip,json,legal,price_exact as X
from ortools.sat.python import cp_model
import dims_relax as DR
MAXQ=5
STOPFREE=os.environ.get('STOPFREE','0')=='1'   # allow a register's stop to collapse (equal frames, MOVE deleted, cost 0)
def bitmask(vs):
    m=0
    for v in vs: m|=1<<v
    return m
def span_of(basis):
    s={0}
    for v in basis:
        if v not in s: s|={x^v for x in s}
    return s
def basis_of(s):
    b=[];sp={0}
    for v in sorted(s):
        if v not in sp: b.append(v); sp|={x^v for x in sp}
    return b
def subspaces_between(Lb,Ub):
    """all subspaces S with span(Lb) <= S <= span(Ub): enumerate via quotient. Lb,Ub bases (Ub contains Lb)."""
    L=span_of(Lb); U=span_of(Ub)
    # complement basis of L in U
    comp=[];sp=set(L)
    for v in sorted(U):
        if v not in sp: comp.append(v); sp|={x^v for x in sp}
    m=len(comp); res=set()
    # enumerate subspaces of F2^m by closure: DFS over generated sets
    def lift(mask): 
        v=0
        for i in range(m):
            if mask>>i&1: v^=comp[i]
        return v
    seen=set(); frontier=[frozenset([0])]; seen.add(frozenset([0]))
    allsub=[frozenset([0])]
    while frontier:
        nf=[]
        for S in frontier:
            for v in range(1,1<<m):
                if v in S: continue
                T=frozenset(S|{x^v for x in S})
                if T not in seen: seen.add(T); nf.append(T); allsub.append(T)
        frontier=nf
    out=[]
    for S in allsub:
        full=set(L)
        for v in S: 
            lv=lift(v); full|={x^lv for x in L}
        out.append(frozenset(full))
    return out
def run(path,mode,TL,outp):
    w=legal.load(path);B=DR.build(w);NH=B['NH'];live=B['live'];main=B['main'];find=B['find'];stop=B['stop'];cf=B['cf']
    fr=legal.spans(w);dimf=lambda f:len(w['frames'][f])
    rep=legal.check(w);T,P=X.invoice(rep);pc=X.Pricer(T,P);k0=pc.k
    import linwt; cwP,cwT=linwt.weights(pc)   # RETIMEGAP: symmetric exact-first-order weights (infra/linwt.py)
    A=set()
    for r in range(NH):
        if mode in('P104CH','FINAL') or r in live: A.add(find((r,0)))     # FINAL: finals free, initials pinned
        if mode in('P104CH','START') or (r in main and r not in live): A.add(find((r,stop[r])))   # START: starts free, finals pinned
    up=collections.defaultdict(list);dn=collections.defaultdict(list)
    for a,b,r in B['links']:
        lo,hi=(a,b) if r<NH else (b,a); up[lo].append(hi); dn[hi].append(lo)
    def reach(adj,s):
        seen={s};st=[s]
        while st:
            x=st.pop()
            for y in adj[x]:
                if y not in seen: seen.add(y);st.append(y)
        return seen
    below={a:reach(dn,a) for a in A};above={a:reach(up,a) for a in A}
    Ls=collections.defaultdict(list);Us=collections.defaultdict(list)
    for a in A:
        for c in above[a]: Ls[c].append(a)
        for c in below[a]: Us[c].append(a)
    wf_masks={}                       # word frames as sets
    dom={}
    for c in cf:
        if c in A: dom[c]=[frozenset(fr[cf[c]])]; continue
        Lbasis=[v for a in Ls[c] for v in w['frames'][cf[a]]]
        Lset=span_of(Lbasis); Uset=None
        for a in Us[c]:
            s=set(fr[cf[a]]); Uset=s if Uset is None else Uset&s
        if Uset is None: Uset=set(range(512))
        Lb=basis_of(Lset);Ub=basis_of(Uset)
        m=len(Ub)-len(Lb)
        nat=frozenset(fr[cf[c]])
        if not(Lset<=nat<=Uset): print('WARN native outside [L,U]',c)
        if m<=MAXQ: d=set(subspaces_between(Lb,Ub))
        else:
            d={frozenset(Lset),frozenset(Uset)}
            for f in fr:
                if Lset<=f<=Uset: d.add(frozenset(f))
        d.add(nat); dom[c]=sorted(d,key=lambda s:(len(s),sorted(s)[:8]))
    # unary pruning by anchored neighbours handled through clauses; build model
    M=cp_model.CpModel();x={};Dv={}
    for c in cf:
        xs=[]
        for i,S in enumerate(dom[c]): x[c,i]=M.NewBoolVar(''); xs.append(x[c,i])
        M.AddExactlyOne(xs)
        dims=[len(S).bit_length()-1 for S in dom[c]]
        Dv[c]=M.NewIntVar(min(dims),max(dims),'')
        M.Add(Dv[c]==sum(dm*x[c,i] for i,dm in enumerate(dims)))
    for a,b,r in B['links']:
        lo,hi=(a,b) if r<NH else (b,a)
        for i,S in enumerate(dom[lo]):
            ok=[x[hi,j] for j,Tt in enumerate(dom[hi]) if (S<=Tt if STOPFREE else S<Tt)]
            M.AddBoolOr(ok+[x[lo,i].Not()])
        for j,Tt in enumerate(dom[hi]):
            ok=[x[lo,i] for i,S in enumerate(dom[lo]) if (S<=Tt if STOPFREE else S<Tt)]
            M.AddBoolOr(ok+[x[hi,j].Not()])
    tab=([0] if STOPFREE else [])+[cwP[d] for d in range(1,10)];tabT=[cwT[d] for d in range(1,10)];obj=[]
    for a,b,r in B['links']:
        lo,hi=(a,b) if r<NH else (b,a)
        dl=M.NewIntVar(0 if STOPFREE else 1,9,'');M.Add(dl==Dv[hi]-Dv[lo]);cst=M.NewIntVar(0,max(tab),'');M.AddElement(dl-(0 if STOPFREE else 1),tab,cst);obj.append(-cst)
    for r in range(NH):
        if r in main: continue
        a,b=find((r,0)),find((r,stop[r]))
        rk=M.NewIntVar(1,9,'');M.Add(rk==Dv[b]-Dv[a]);g=M.NewIntVar(0,max(tabT),'');M.AddElement(rk-1,tabT,g);obj.append(g)
    M.Maximize(sum(obj))
    for c in cf:
        nat=frozenset(fr[cf[c]])
        for i,S in enumerate(dom[c]): M.AddHint(x[c,i],1 if S==nat else 0)
    S_=cp_model.CpSolver();S_.parameters.max_time_in_seconds=TL;S_.parameters.num_workers=int(os.environ.get('HEAVY_THREADS','4'))
    nat_obj=0
    for a,b,r in B['links']:
        lo,hi=(a,b) if r<NH else (b,a); nat_obj-=cwP[dimf(cf[hi])-dimf(cf[lo])]
    for r in range(NH):
        if r in main: continue
        nat_obj+=cwT[dimf(cf[find((r,stop[r]))])-dimf(cf[find((r,0))])]
    st=S_.Solve(M)
    print(mode,S_.StatusName(st),'domain sizes: total',sum(len(d) for d in dom.values()),'max',max(len(d) for d in dom.values()),
          'ceiling(linearised) %.3e  found %.3e'%((S_.BestObjectiveBound()-nat_obj)/1e16,(S_.ObjectiveValue()-nat_obj)/1e16),flush=True)
    if st not in (cp_model.OPTIMAL,cp_model.FEASIBLE): return
    chosen={c:next(dom[c][i] for i in range(len(dom[c])) if S_.BooleanValue(x[c,i])) for c in cf}
    # realise
    w2=json.loads(json.dumps(w)); ftab={}
    for i,b in enumerate(w['frames']): ftab[frozenset(fr[i])]=i
    def fid(S):
        if S not in ftab: w2['frames'].append(basis_of(S)); ftab[S]=len(w2['frames'])-1
        return ftab[S]
    stp=collections.defaultdict(int)
    for r in range(NH): stp[r]=0
    newp=[]
    for e in w['program']:
        e=list(e);op,r=e[0],e[1]
        if op=='MOVE':
            a=find((r,stp[r])); stp[r]+=1; b=find((r,stp[r])); e[2]=fid(chosen[a]); e[3]=fid(chosen[b])
            if chosen[a]==chosen[b]: continue          # collapsed stop: MOVE deleted
        elif op=='INIT': stp[r]=0; e[2]=fid(chosen[find((r,0))])
        elif op=='CLEAR': e[2]=fid(chosen[find((r,stp[r]))])
        else: e[-1]=fid(chosen[find((r,stp[r]))])
        newp.append(e)
    w2['program']=newp
    w2['initial']=[fid(chosen[find((r,0))]) for r in range(NH)]
    w2['final']=[fid(chosen[find((r,stp[r]))]) for r in range(NH)]
    json.dump(w2,gzip.open(outp,'wt'))
    rep2=legal.check(w2);print('REALISED legal',rep2['ok'],rep2['violations'][:3])
    if rep2['ok']:
        T2,P2=X.invoice(rep2);print('EXACT invoice kappa %.10f (base %.10f) gain %.3e'%(X.kappa(T2,P2),k0,X.kappa(T2,P2)-k0),'side',X.side(T2,P2)['ok'])
        print('paid change',{d:rep2['paid'].get(d,0)-rep['paid'].get(d,0) for d in range(1,10)},'helper rank change',{d:rep2['helpers'].get(d,0)-rep['helpers'].get(d,0) for d in range(1,10)})
if __name__=='__main__': run(sys.argv[1],sys.argv[2],float(sys.argv[3]),sys.argv[4])
