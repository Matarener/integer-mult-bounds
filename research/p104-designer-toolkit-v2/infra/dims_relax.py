"""DIMENSION-LEVEL CEILING for frame retiming of a FIXED circuit, with the verifier's real freedom (tests P104CH 'rigid').
Variables: dim D(c) of every ADD-equal-frame cluster c.  Constraints (necessary conditions only): chain links strictly ascending
(owned: descending), D(c) in [dim L(c), dim U(c)] where L=sum / U=intersection of ANCHORED frames below/above (all subspaces of F2^9),
anchors per mode.  Objective = linearised kappa (exact marginal tables x18 calls): sum_h cwT[rank_h] - sum_links cwP[|dD|].
rank_h = D(final)-D(initial) for helpers (>=1).  MODE 'P104CH' anchors every initial/final (sanity: ceiling must be ~0);
'VERIFIER' anchors only X initial and Y final.  Ceiling = relaxation (dims only, ignores strict subspace nesting between neighbours
and lattice feasibility), so gain<=0 would be a PROOF of dimension rigidity, gain>0 is only a LEAD.  Run via hq (CP-SAT).
python dims_relax.py WORD.json.gz MODE [TL]"""
import sys,os,collections,legal,price_exact as X
from ortools.sat.python import cp_model
def build(w):
    prog=w['program'];NH=len(w['initial']);live=set(w['live']);main=live|{r+112 for r in live}
    parent={}
    def find(x):
        while parent.setdefault(x,x)!=x: parent[x]=parent[parent[x]]; x=parent[x]
        return x
    stop=collections.defaultdict(int); chain=collections.defaultdict(list)
    for r in range(NH): chain[r].append((0,w['initial'][r]))
    # owned registers can have several lifetimes (PR5627 owned_fields word: role 751 has 3).  Each lifetime after the first gets its own virtual id (10**6+event index) so its
    # clusters / chain are separate (otherwise INIT would overwrite the earlier lifetime's chain).  rv[i] = virtual id of the destination register of event i, sv[i] = of the source.
    virt={};seen=set();rv=[];sv=[]
    for i,e in enumerate(prog):
        op,r=e[0],e[1]
        if op=='INIT':
            if r in seen: virt[r]=10**6+i
            seen.add(r)
        v=virt.get(r,r); rv.append(v); sv.append(virt.get(e[2],e[2]) if op in('ADD','COPY') else None)
        if op=='MOVE': stop[v]+=1; chain[v].append((stop[v],e[3]))
        elif op=='INIT': chain[v]=[(0,e[2])]; stop[v]=0
        elif op in('ADD','COPY'): parent[find((v,stop[v]))]=find((sv[-1],stop[sv[-1]]))
    cf={}
    for r in chain:
        for s,f in chain[r]: cf[find((r,s))]=f
    links=[]
    for r,ch in chain.items():
        for (s1,f1),(s2,f2) in zip(ch,ch[1:]): links.append((find((r,s1)),find((r,s2)),r))
    return dict(NH=NH,live=live,main=main,chain=chain,cf=cf,links=links,find=find,stop=stop,rv=rv,sv=sv)
def run(path,mode,TL=300):
    w=legal.load(path);B=build(w);NH=B['NH'];live=B['live'];main=B['main'];find=B['find'];stop=B['stop'];cf=B['cf']
    fr=legal.spans(w);dim=lambda f:len(w['frames'][f])
    rep=legal.check(w);T,P=X.invoice(rep);pc=X.Pricer(T,P);k0=pc.k
    import linwt; cwP,cwT=linwt.weights(pc)   # RETIMEGAP: symmetric exact-first-order weights (infra/linwt.py)
    A=set()
    for r in range(NH):
        if mode=='P104CH' or r in live: A.add(find((r,0)))
        if mode=='P104CH' or (r in main and r not in live): A.add(find((r,stop[r])))
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
    def dim_of_sum(fs):
        s={0}
        for f in fs:
            for v in w['frames'][f]:
                if v not in s: s|={x^v for x in s}
        return len(s).bit_length()-1
    lowd={};upd={}
    below={a:reach(dn,a) for a in A};above={a:reach(up,a) for a in A}
    Ls=collections.defaultdict(list);Us=collections.defaultdict(list)
    for a in A:
        for c in above[a]: Ls[c].append(cf[a])
        for c in below[a]: Us[c].append(a)
    M=cp_model.CpModel();D={}
    for c in cf:
        if c in A: lo=hi=dim(cf[c])
        else:
            lo=dim_of_sum(Ls[c]) if Ls[c] else 0
            if Us[c]:
                U=None
                for a in Us[c]:
                    s=set(fr[cf[a]]); U=s if U is None else U&s
                hi=len(U).bit_length()-1
            else: hi=9
            lo=min(lo,dim(cf[c])); hi=max(hi,dim(cf[c]))
        D[c]=M.NewIntVar(lo,hi,f'D{c}')
    obj=[];tab=[cwP[d] for d in range(1,10)];tabT=[cwT[d] for d in range(1,10)]
    for a,b,r in B['links']:
        lo,hi=(a,b) if r<NH else (b,a)
        M.Add(D[hi]>=D[lo]+1)
        dl=M.NewIntVar(1,9,'');M.Add(dl==D[hi]-D[lo])
        cst=M.NewIntVar(0,max(tab),'');M.AddElement(dl-1,tab,cst);obj.append(-cst)
    for r in range(NH):
        if r in main: continue
        a,b=find((r,0)),find((r,stop[r]))
        rk=M.NewIntVar(1,9,'');M.Add(rk==D[b]-D[a])
        g=M.NewIntVar(0,max(tabT),'');M.AddElement(rk-1,tabT,g);obj.append(g)
    M.Maximize(sum(obj))
    nat=0
    for a,b,r in B['links']:
        lo,hi=(a,b) if r<NH else (b,a); nat-=cwP[dim(cf[hi])-dim(cf[lo])]
    for r in range(NH):
        if r in main: continue
        nat+=cwT[dim(cf[find((r,stop[r]))])-dim(cf[find((r,0))])]
    for c in cf: M.AddHint(D[c],dim(cf[c]))
    S=cp_model.CpSolver();S.parameters.max_time_in_seconds=TL;S.parameters.num_workers=int(os.environ.get('HEAVY_THREADS','4'))
    st=S.Solve(M)
    print(mode,S.StatusName(st),'native obj',nat,'best',S.ObjectiveValue(),'bound',S.BestObjectiveBound(),'ceiling dkappa(linearised) %.3e'%((S.BestObjectiveBound()-nat)/1e16),'found %.3e'%((S.ObjectiveValue()-nat)/1e16),flush=True)
    import collections as C
    Pn=C.Counter();Tn=C.Counter()
    for a,b,r in B['links']:
        lo,hi=(a,b) if r<NH else (b,a); Pn[S.Value(D[hi])-S.Value(D[lo])]+=1
    for r in range(NH):
        if r in main: continue
        Tn[S.Value(D[find((r,stop[r]))])-S.Value(D[find((r,0))])]+=1
    Tx,Px=X.invoice(dict(paid=Pn,helpers=Tn)); kn=X.kappa(Tx,Px)
    print('EXACT invoice kappa of relaxed dims: %.10f  (base %.10f)  gain %.3e'%(kn,k0,kn-k0))
    print('paid hist change:',{d:Pn.get(d,0)-rep['paid'].get(d,0) for d in range(1,10)},' helper-rank hist change:',{d:Tn.get(d,0)-rep['helpers'].get(d,0) for d in range(1,10)})
    nhc=sum(1 for r in range(NH) if r not in main and (S.Value(D[find((r,stop[r]))])-S.Value(D[find((r,0))]))!=dim(cf[find((r,stop[r]))])-dim(cf[find((r,0))]))
    print('helpers whose credited rank changes:',nhc)
    chg=[(c,dim(cf[c]),S.Value(D[c])) for c in cf if S.Value(D[c])!=dim(cf[c])]
    print('clusters whose dim changes in best:',len(chg),chg[:10])
if __name__=='__main__': run(sys.argv[1],sys.argv[2],float(sys.argv[3]) if len(sys.argv)>3 else 300)
