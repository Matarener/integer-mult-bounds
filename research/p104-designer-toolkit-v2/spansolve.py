"""spansolve -- exact minimal-cost span solver (TKRELAY).  General infrastructure for every screen that asks
"is this linear form a combination of values that already exist (at the right place/time), and what is the cheapest such combination?"

    from spansolve import Cand, solve, solve_cpsat, verify, ValueTimeline

DATA
    form   = sparse linear form {col: Fraction}  (columns = the word's input rows; dag.apply_forms forms, so dyadic)
    Cand(key, vec, cost=0, group=None, meta=None)   one AVAILABLE VALUE: key identifies it (e.g. (reg, op_index, frame)), vec is its form,
                                                    cost is paid when the term is used (e.g. extra paid MOVE ranks), group = cost-sharing class (see group_cost)
SOLVERS  (both return a list of Sol, best first; a Sol has .terms [(Cand, Fraction coef)], .cost, .nterms, .residual)
    solve(target, cands, max_terms=4, ...)    exact: support pruning -> feasibility rank test (mod p) -> complete DFS over supports of size <= max_terms
                                              (branch on a target column that is still uncovered: some chosen term must cover it) -> coefficients solved
                                              in Fraction arithmetic and verified exactly; dyadic / size filter (legal.check: denominator 2^k, |q|+1 < 2^16).
                                              Ranking cost = sum(cost) + sum(group_cost[g] for the groups used)  (default cost 0 -> fewest terms first).
    solve_cpsat(target, cands, ...)           the same optimisation as an integer program (one binary per candidate, integer numerators over a common power-of-two
                                              denominator, one equality per column); minimises cost (+ term count * term_weight) and REQUIRES status OPTIMAL
                                              (raises otherwise).  Run it through $TK_HQ with >= 2 threads (threads= parameter); use it for the cost layer when the
                                              candidate pool is big or max_terms > 4.  solve() is the cheap first pass / cross-check.
    free_cols=set(...)   (both) columns that need NOT match: the system is solved on the other columns and each Sol carries .residual = target - sum(a_k v_k)
                          restricted to free_cols, so a caller that can repair a residual (RELAYGEN pre/post ADDs at frames 3/127) keeps control of that step.
    verify(target, terms) exact check (Fractions) of sum(a v) == target.
TIMELINES
    ValueTimeline(view)   (view = movekit.View or anything with .S scalar program, .w word)   symbolic forward pass with dag.apply_forms: form_after[i] for every scalar op i,
                          per-register event lists, and the FREE RESIDENCY INTERVALS used to place a new ADD without any new MOVE (just-in-time MOVE semantics of View.rebuild):
        tl.intervals(r, skip=())      -> list of (F, lo, hi, vid, stage): register r sits in frame F for every insertion gap g in [lo, hi] and holds the value written by op `vid`
                                         (vid = -1: the initial value e_r) -- gap g means "before scalar op g".  stage 0 = r still at its previous frame, stage 1 = r already moved
                                         to the frame of its next event (a point interval at that event).  `skip` = op indices treated as deleted (the removed contact).
        tl.form(r, vid)               the form of the value written by op vid to r (vid -1: initial)
        tl.window(r, i)               (lo, hi): insertion gaps for which no read/scale/copy/clear of r lies between the gap and op i (additions to r commute)
        tl.pool(r, i, ...)            candidate list for "replace the contact at op i by free terms on the same target": intersects r's intervals with every other register's.
    The ranking is only exact w.r.t. the algebra; every produced edit must still go through legal.check / IncrWord (tk relay does that).
Complexity notes: pruning is exact (a column outside the target support that only one candidate covers kills that candidate; iterated), DFS cost is
(branching factor)^max_terms with a numpy-vectorised reduction per node; node_limit guards it (the result then has .complete == False)."""
import itertools,time,sys
from fractions import Fraction as Q
import numpy as np
PR=2147483629          # prime < 2^31: products fit int64
class Cand:
    __slots__=('key','vec','cost','group','meta')
    def __init__(s,key,vec,cost=0,group=None,meta=None):
        s.key=key; s.vec=vec; s.cost=cost; s.group=group; s.meta=meta
    def __repr__(s): return 'Cand(%r,nnz=%d,cost=%s)'%(s.key,len(s.vec),s.cost)
class Sol:
    __slots__=('terms','cost','residual','complete')
    def __init__(s,terms,cost,residual=None): s.terms=terms; s.cost=cost; s.residual=residual or {}
    @property
    def nterms(s): return len(s.terms)
    def __repr__(s): return 'Sol(cost=%s,%s)'%(s.cost,[(c.key,str(a)) for c,a in s.terms])
def _inv(x): return pow(x%PR,PR-2,PR)
def _modq(x):
    x=Q(x); return x.numerator%PR*_inv(x.denominator)%PR
def is_dyadic(a):
    a=Q(a); d=a.denominator; return not(d&(d-1)) and abs(a)+1<2**16
def verify(target,terms,free_cols=()):
    """exact: sum a*vec == target outside free_cols; -> residual dict on free_cols (or None if the non-free part differs)"""
    acc={}
    for c,a in terms:
        for k,v in c.vec.items(): acc[k]=acc.get(k,0)+a*v
    free=set(free_cols); res={}
    for k in set(acc)|set(target):
        d=target.get(k,0)-acc.get(k,0)
        if d:
            if k in free: res[k]=d
            else: return None
    return res
_PV={}
def _pv(vec):
    """cached (sorted cols tuple, mod-p values tuple, proportionality key) of a form object (kept alive by the cache so id() stays valid)"""
    h=_PV.get(id(vec))
    if h is not None and h[0] is vec: return h[1]
    ks=sorted(vec); vs=[_modq(vec[k]) for k in ks]
    sc=_inv(vs[0]) if vs else 1
    key=(tuple(ks),tuple(x*sc%PR for x in vs)) if vs else None
    if len(_PV)>400000: _PV.clear()
    r=(tuple(ks),tuple(vs),key); _PV[id(vec)]=(vec,r); return r
def _dedupe_and_prune(target,cands,free):
    """drop zero vectors, proportional duplicates (cheapest kept) and unsupported candidates (iterated). -> list of (cand, vec restricted to non-free cols)"""
    out={}
    for c in cands:
        if free:
            v={k:x for k,x in c.vec.items() if k not in free and x}
            if not v: continue
            kk=_pv(v)[2]
        else:
            if not c.vec: continue
            v=c.vec; kk=_pv(v)[2]
        if kk is None: continue
        if kk not in out or c.cost<out[kk][0].cost: out[kk]=(c,v)
    items=list(out.values()); tsup={k for k in target if k not in free and target[k]}
    while True:
        cnt={}
        for c,v in items:
            for k in v:
                if k not in tsup: cnt[k]=cnt.get(k,0)+1
        keep=[(c,v) for c,v in items if all(k in tsup or cnt[k]>1 for k in v)]
        if len(keep)==len(items): break
        items=keep
    return items
def solve(target,cands,max_terms=4,free_cols=(),nbest=5,group_cost=None,node_limit=200000,all_sizes=False,time_limit=None,dyadic=True):
    """minimal-cost exact combinations of `cands` equal to `target` (outside free_cols).  -> list of Sol (best first, <= nbest).  Sol.complete False if node_limit/time_limit hit.
    all_sizes=False: stop at the first support size that has a solution (fewest terms), then rank that size by cost; True: collect all sizes <= max_terms and rank by cost."""
    free=set(free_cols); gcost=group_cost or {}
    tv={k:x for k,x in target.items() if k not in free and x}
    if not tv: return [Sol([],0,{k:x for k,x in target.items() if k in free})]
    items=_dedupe_and_prune(target,cands,free)
    if not items: return []
    cov={k for _,v in items for k in v}
    if any(k not in cov for k in tv): return []          # a target column nobody covers
    cols=sorted(set(tv)|cov); ci={k:i for i,k in enumerate(cols)}; n=len(cols); m=len(items)
    M=np.zeros((m,n),dtype=np.int64)
    for a,(c,v) in enumerate(items):
        ks,vs,_k=_pv(v)
        M[a,[ci[k] for k in ks]]=vs
    t=np.zeros(n,dtype=np.int64)
    for k,x in tv.items(): t[ci[k]]=_modq(x)
    # feasibility: t in the row space of M (mod p)?
    if not _in_span(M,t): return []
    t0=time.time(); st=dict(nodes=0,complete=True); found=[]
    MT=np.ascontiguousarray(M.T); cnt0=(M!=0).sum(axis=0).astype(np.int64)
    order_cost=[it[0].cost for it in items]
    def dfs(patched,cnt,excl,rho,chosen,depth):
        if st['nodes']>=node_limit or (time_limit and time.time()-t0>time_limit): st['complete']=False; return
        st['nodes']+=1
        nzc=np.flatnonzero(rho)
        if len(nzc)==0: found.append(tuple(chosen)); return
        if depth==max_terms: return
        counts=cnt[nzc]; j=int(np.argmin(counts))
        if counts[j]<=0: return
        c=int(nzc[j]); col=MT[c].copy()
        for a_,row_ in patched.items(): col[a_]=row_[c]
        nzrows=np.flatnonzero(col!=0); nzrows=nzrows[~excl[nzrows]]
        branch=sorted((int(a_) for a_ in nzrows),key=lambda a_:order_cost[a_])
        if depth==max_terms-1:          # last level: the residual must be a multiple of one reduced row
            rc=int(rho[c])
            for a in branch:
                row=patched.get(a); row=M[a] if row is None else row
                if not np.array_equal((int(row[c])*rho)%PR,(rc*row)%PR): continue
                found.append(tuple(chosen+[a]))
            st['nodes']+=len(branch); return
        excl=excl.copy(); cnt=cnt.copy()
        for a in branch:
            row=patched.get(a); row=M[a] if row is None else row
            row=(row*_inv(int(row[c])))%PR
            p2=dict(patched); c2=cnt.copy()
            for b in nzrows:
                b=int(b)
                if excl[b] and b!=a: continue
                rb=patched.get(b); rb=M[b] if rb is None else rb
                nw=(rb-int(rb[c])*row)%PR
                c2+=(nw!=0).astype(np.int64)-(rb!=0).astype(np.int64); p2[b]=nw
            rho2=(rho-int(rho[c])*row)%PR
            dfs(p2,c2,excl,rho2,chosen+[a],depth+1)
            # exclude a for the later siblings
            ra=patched.get(a); ra=M[a] if ra is None else ra
            cnt-= (ra!=0).astype(np.int64); excl[a]=True
            if st['nodes']>=node_limit: break
    dfs({},cnt0,np.zeros(m,dtype=bool),t.copy(),[],0)
    sols=[]; seen=set()
    for ch in found:
        fs=frozenset(ch)
        if fs in seen: continue
        seen.add(fs)
        sol=_exact([items[a][0] for a in ch],target,free,dyadic)
        if sol is not None:
            used={c.group for c,_ in sol.terms if c.group is not None}
            sol.cost=sum(c.cost for c,_ in sol.terms)+sum(gcost.get(g,0) for g in used); sols.append(sol)
    if sols and not all_sizes:
        k0=min(x.nterms for x in sols); sols=[x for x in sols if x.nterms==k0]
    sols.sort(key=lambda s:(s.cost,s.nterms))
    for s in sols: s.complete=st['complete']
    return sols[:nbest]
def _in_span(M,t):
    """t in rowspace(M) mod PR: elimination of M, then reduce t"""
    A=M.copy(); piv=[]; r=0; m,n=A.shape
    for c in range(n):
        if r>=m: break
        nz=np.flatnonzero(A[r:,c])
        if len(nz)==0: continue
        k=r+int(nz[0]); A[[r,k]]=A[[k,r]]
        A[r]=(A[r]*_inv(int(A[r,c])))%PR
        f=A[:,c].copy(); f[r]=0
        idx=np.flatnonzero(f)
        if len(idx): A[idx]=(A[idx]-f[idx,None]*A[r][None,:])%PR
        piv.append(c); r+=1
    v=t.copy()
    for i,c in enumerate(piv):
        if v[c]: v=(v-v[c]*A[i])%PR
    return not v.any()
def _exact(cs,target,free,dyadic):
    """solve sum a_k vec_k = target on the non-free columns exactly (Fractions); None if inconsistent / non-unique / not dyadic"""
    cols=sorted({k for c in cs for k in c.vec if k not in free}|{k for k in target if k not in free and target[k]})
    K=len(cs); rows=[[c.vec.get(k,Q(0)) for c in cs]+[Q(target.get(k,0))] for k in cols]
    piv=[]; r=0
    for j in range(K):
        p=next((i for i in range(r,len(rows)) if rows[i][j]!=0),None)
        if p is None: return None            # dependent chosen set (should not occur)
        rows[r],rows[p]=rows[p],rows[r]; d=rows[r][j]; rows[r]=[x/d for x in rows[r]]
        for i in range(len(rows)):
            if i!=r and rows[i][j]!=0:
                f=rows[i][j]; rows[i]=[x-f*y for x,y in zip(rows[i],rows[r])]
        piv.append(j); r+=1
    if any(rows[i][K]!=0 for i in range(r,len(rows))): return None
    a=[rows[i][K] for i in range(K)]
    if any(x==0 for x in a): return None
    if dyadic and not all(is_dyadic(x) for x in a): return None
    terms=list(zip(cs,a)); res=verify(target,terms,free)
    if res is None: return None
    return Sol(terms,0,res)
def solve_cpsat(target,cands,max_terms=6,free_cols=(),nbest=1,group_cost=None,term_weight=1,threads=2,time_limit=120,max_num=1<<17,log=False):
    """cost-minimising integer program.  a_k = n_k / D (D = common power-of-two denominator of all vectors and the target); one equality per column;
    binary y_k with |n_k| <= max_num*y_k, sum y_k <= max_terms; objective  sum (cost_k+term_weight) y_k + sum group_cost[g]*z_g.  Raises RuntimeError unless the status is OPTIMAL.
    -> [Sol] (the optimum) or [] if INFEASIBLE."""
    from ortools.sat.python import cp_model
    free=set(free_cols); gcost=group_cost or {}
    items=_dedupe_and_prune(target,cands,free)
    tv={k:x for k,x in target.items() if k not in free and x}
    if not tv: return [Sol([],0,{k:x for k,x in target.items() if k in free})]
    if not items: return []
    den=1
    for x in list(tv.values())+[x for _,v in items for x in v.values()]: den=max(den,Q(x).denominator)
    if den&(den-1): raise ValueError('non-dyadic form denominators')
    cols=sorted(set(tv)|{k for _,v in items for k in v})
    mdl=cp_model.CpModel(); m=len(items)
    nvar=[mdl.NewIntVar(-max_num,max_num,'n%d'%a) for a in range(m)]; y=[mdl.NewBoolVar('y%d'%a) for a in range(m)]
    for a in range(m):
        mdl.Add(nvar[a]<=max_num*y[a]); mdl.Add(nvar[a]>=-max_num*y[a]); mdl.Add(nvar[a]!=0).OnlyEnforceIf(y[a])
    mdl.Add(sum(y)<=max_terms)
    colterms={k:[] for k in cols}
    for a,(c,v) in enumerate(items):
        for k,x in v.items(): colterms[k].append((a,int(Q(x)*den)))
    for k in cols:
        # sum_a (x_ak*den) n_a = target_k * den^2 ... (a_a = n_a/den): sum x_ak n_a/den = t_k  <=> sum (x_ak*den) n_a = t_k*den*den
        mdl.Add(sum(co*nvar[a] for a,co in colterms[k])==int(Q(tv.get(k,0))*den*den))
    groups=sorted({c.group for c,_ in items if c.group is not None},key=repr); z={g:mdl.NewBoolVar('z%d'%i) for i,g in enumerate(groups)}
    for a,(c,_) in enumerate(items):
        if c.group is not None: mdl.AddImplication(y[a],z[c.group])
    obj=sum((int(items[a][0].cost)+term_weight)*y[a] for a in range(m))+sum(int(gcost.get(g,0))*z[g] for g in groups)
    mdl.Minimize(obj)
    sv=cp_model.CpSolver(); sv.parameters.num_workers=max(2,threads); sv.parameters.max_time_in_seconds=time_limit; sv.parameters.log_search_progress=log
    stt=sv.Solve(mdl)
    if stt==cp_model.INFEASIBLE: return []
    if stt!=cp_model.OPTIMAL: raise RuntimeError('spansolve.solve_cpsat: status %s (need OPTIMAL)'%sv.StatusName(stt))
    chosen=[(items[a][0],Q(sv.Value(nvar[a]),den)) for a in range(m) if sv.Value(y[a])]
    res=verify(target,chosen,free)
    if res is None: raise RuntimeError('spansolve.solve_cpsat: solution fails exact verification')
    used={c.group for c,_ in chosen if c.group is not None}
    s=Sol(chosen,sum(c.cost for c,_ in chosen)+sum(gcost.get(g,0) for g in used),res); s.complete=True; return [s]
# ---------------------------------------------------------------------------------------------------------------------------- timelines
class ValueTimeline:
    """value history of a word's scalar program.  view.S = non-MOVE events; op index i = index in S.  See the module docstring."""
    def __init__(s,view,forms=None):
        import dag as D
        w=view.w; s.view=view; s.S=S=view.S; s.n=n=view.n; s.NR=view.NR; s.own=view.own
        s.init=list(w['initial'])+[None]*(s.NR-n); s.fin=list(w['final'])+[None]*(s.NR-n)
        meta=dict(npub=n,nowned=s.NR-n,live=list(w['live']))
        ops=[]
        for e in S:
            if e[0] in('ADD','COPY'): ops.append([e[0],e[1],e[2],e[3],e[4],None])
            elif e[0]=='SCALE': ops.append(['SCALE',e[1],None,e[2],e[3],None])
            else: ops.append([e[0],e[1],None,None,e[2],None])
        s.form_after=[None]*len(ops)
        def on(i,r,f): s.form_after[i]=dict(f); return f
        D.apply_forms(ops,meta,on_op=on)
        s.init_form=lambda r:{r:Q(1)}
        # per register involvement events: (i, frame, kind) kind 'w' (written), 'r' (read only), 'b' barrier flag computed separately
        ev=[[] for _ in range(s.NR)]; s.barrier=[[] for _ in range(s.NR)]
        for i,e in enumerate(S):
            op=e[0]; r=e[1]
            if op in('INIT','CLEAR'): ev[r].append((i,e[2],'w' if op=='INIT' else 'c')); s.barrier[r].append(i)
            elif op=='SCALE': ev[r].append((i,e[3],'w')); s.barrier[r].append(i)
            else:
                f=e[4]
                if op=='COPY': ev[r].append((i,f,'w')); s.barrier[r].append(i)
                else: ev[r].append((i,f,'w'))            # ADD into r commutes with insertion
                ev[e[2]].append((i,f,'r')); s.barrier[e[2]].append(i)
        s.ev=ev
    def form(s,r,vid):
        return {r:Q(1)} if vid<0 else s.form_after[vid]
    def window(s,r,i):
        """(lo,hi) insertion gaps around op i with no barrier of r strictly between the gap and i: gap g allowed iff no barrier b with min(g,i)<=b<max(g,i)... (barrier at i itself excluded: i is an ADD into r)"""
        import bisect
        b=s.barrier[r]; k=bisect.bisect_left(b,i)
        lo=(b[k-1]+1) if k>0 else 0
        k2=bisect.bisect_right(b,i)
        hi=b[k2] if k2<len(b) else len(s.S)
        return lo,hi
    def intervals(s,r,skip=()):
        """free residency intervals of register r: list of (F,lo,hi,vid,stage); ops in `skip` are ignored (deleted)"""
        skip=set(skip); N=len(s.S); out=[]
        cf=s.init[r] if r<s.n else None; vid=-1; li=-1; alive=r<s.n
        tail=[(N,s.fin[r],'e')] if (r<s.n and s.fin[r] is not None) else []
        for i,f,k in [x for x in s.ev[r] if x[0] not in skip]+tail:
            if alive:
                out.append((cf,li+1,i,vid,0))
                if f!=cf: out.append((f,i,i,vid,1))
            if k=='w': vid=i; cf=f; alive=True
            elif k=='r': cf=f
            elif k=='c': alive=False; cf=None; vid=-1
            li=i
        return out
    def _index(s):
        """global index F -> arrays (lo,hi,u,vid,stage) of every register's intervals"""
        if getattr(s,'_ix',None) is not None: return s._ix
        import numpy as np
        acc={}
        for u in range(s.NR):
            for F,a,b,vid,st in s.intervals(u):
                acc.setdefault(F,[]).append((a,b,u,vid,st))
        s._ix={F:np.array(v,dtype=np.int64) for F,v in acc.items()}; return s._ix
    def _pindex(s):
        """intervals during which a register must make a (single, paid) MOVE from cf to nf: arrays (lo,hi,u,vid,pairid) + pair table"""
        if getattr(s,'_pix',None) is not None: return s._pix
        import numpy as np
        rows=[]; pairs={}; plist=[]
        for u in range(s.NR):
            for F,a,b,vid,st in s.intervals(u):
                pass
        # rebuild from events: A-type interval (cf, li+1..i) whose next frame f != cf
        for u in range(s.NR):
            cf=s.init[u] if u<s.n else None; vid=-1; li=-1; alive=u<s.n
            tail=[(len(s.S),s.fin[u],'e')] if (u<s.n and s.fin[u] is not None) else []
            for i,f,k in list(s.ev[u])+tail:
                if alive and cf is not None and f is not None and f!=cf:
                    pid=pairs.get((cf,f,u>=s.n))
                    if pid is None: pid=pairs[(cf,f,u>=s.n)]=len(plist); plist.append((cf,f,u>=s.n))
                    rows.append((li+1,i,u,vid,pid))
                if k=='w': vid=i; cf=f; alive=True
                elif k=='r': cf=f
                elif k=='c': alive=False; cf=None; vid=-1
                li=i
        s._pix=(np.array(rows,dtype=np.int64).reshape(-1,5),plist); return s._pix
    def pool_paid(s,r,i,exclude=()):
        """candidates that need ONE extra MOVE stop of the source (cf < F < nf strictly nested in its direction); Cand.cost = 1.  r itself must be free-resident at F."""
        import numpy as np
        e=s.S[i]; src=e[2]; skip={i}; lo,hi=s.window(r,i); fr=s.view.spans
        byF={}
        for F,a,b,_v,st in s.intervals(r,skip):
            a=max(a,lo); b=min(b,hi)
            if a<=b: byF.setdefault(F,[]).append((a,b,st))
        if not byF: return []
        A,plist=s._pindex(); out=[]
        for F,rl in byF.items():
            ok=np.array([ (fr[F]<fr[cf] and fr[nf]<fr[F]) if own else (fr[cf]<fr[F]<fr[nf]) for cf,nf,own in plist],dtype=bool)
            if not len(A): continue
            good=ok[A[:,4]]&(A[:,2]!=r)&(A[:,2]!=src)
            for ra,rb,rst in rl:
                m=good&(A[:,0]<=rb)&(A[:,1]>=ra)
                for a,b,u,vid,pid in A[m]:
                    u=int(u); vec=s.form(u,int(vid))
                    if not vec or u in exclude: continue
                    g=max(int(a),ra); g2=min(int(b),rb)
                    out.append(Cand((u,int(vid),F,g,rst,'paid'),vec,1,None,dict(u=u,vid=int(vid),F=F,gap=g,gap_hi=g2,stage=rst,paid=1)))
        return out
    def pool(s,r,i,exclude=()):
        """candidates (Cand) for replacing op i (an ADD into r) by terms on r placed with NO new MOVE (JIT semantics).  key=(u,vid,F,gap,stage);
        meta = dict(u,vid,F,gap,gap_hi,stage): the term may be inserted at any gap in [gap,gap_hi] (stage = r's stage there, orders same-gap terms)."""
        import numpy as np
        e=s.S[i]; src=e[2] if e[0]=='ADD' else None
        skip={i}; lo,hi=s.window(r,i)
        byF={}
        for F,a,b,_v,st in s.intervals(r,skip):
            a=max(a,lo); b=min(b,hi)
            if a<=b: byF.setdefault(F,[]).append((a,b,st))
        if not byF: return []
        ix=s._index(); out=[]; touched={r,src}
        extra={}                                    # recomputed intervals of the source register (its stays merge when op i is removed)
        if src is not None:
            for F,a,b,vid,st in s.intervals(src,skip): extra.setdefault(F,[]).append((a,b,src,vid,st))
        for F,rl in byF.items():
            A=ix.get(F); rows=[]
            if A is not None: rows.append(A[~np.isin(A[:,2],list(touched))])
            if F in extra: rows.append(np.array(extra[F],dtype=np.int64))
            for ra,rb,rst in rl:
                for B in rows:
                    if not len(B): continue
                    m=(B[:,0]<=rb)&(B[:,1]>=ra)
                    for a,b,u,vid,st in B[m]:
                        u=int(u)
                        if u in exclude: continue
                        vec=s.form(u,int(vid))
                        if not vec: continue
                        g=max(int(a),ra); g2=min(int(b),rb)
                        out.append(Cand((u,int(vid),F,g,rst),vec,0,None,dict(u=u,vid=int(vid),F=F,gap=g,gap_hi=g2,stage=rst)))
        return out
    def version(s,r,g):
        """vid of the value register r holds at insertion gap g (last write strictly before op g; -1 = initial value)"""
        import bisect
        if getattr(s,'_wl',None) is None: s._wl={}
        L=s._wl.get(r)
        if L is None: L=s._wl[r]=[i for i,f,k in s.ev[r] if k=='w']
        j=bisect.bisect_left(L,g)-1
        return L[j] if j>=0 else -1
    def target(s,i):
        """form added to the target by ADD op i: c * form(src at gap i)"""
        e=s.S[i]; q=Q(e[3]); f=s.form(e[2],s.version(e[2],i)); return {k:q*x for k,x in f.items()}
