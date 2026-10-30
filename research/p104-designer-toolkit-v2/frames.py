"""frames -- ONE exact frame-assignment routine for the toolkit (REALISEFIX.

Given a legal word (event order, operands, per-register timelines fixed) choose every free frame -- the frame of every ADD/COPY/CLEAR/INIT event, the helper initial/final frames --
to MAXIMISE kappa subject to the frame law (strict nesting along register timelines, public ascending / owned descending, literal X ports / Y hyperplanes pinned, helper rank > 0).
MOVEs are re-derived just in time.  This is the event-level lattice retime of evlat.py (CP-SAT over per-event subspace domains, exact symmetric linearisation of kappa from infra/linwt.py),
packaged as a function on word dicts so every realiser can call it, with the invariant that the result is NEVER worse than the input:
    w2,info = frames.assign(w, tl=300, K=2, maxm=0, threads=2)
  * the stored assignment is in every domain and is the solver hint, so the model optimum >= the stored one;
  * the result is re-checked by legal.check and re-priced EXACTLY (price_exact); if it is illegal or its exact kappa is below the input's, the INPUT word is returned (info['kept']='input').
    (second-order model error is ~1e-8 relative; info['gain'] is the exact gain)
  * info = dict(status, kappa0, kappa, gain, model_gain, nodes, kept, seconds).
CPU: CP-SAT.  Interactive callers must run it through $TK_HQ (the CLI `python frames.py WORD OUT [TL K MAXM]` is the hq payload); threads <= HEAVY_THREADS (default 2).
Fast pre-pass `best_closure(candidates)`: pick the best exact-priced word among several frame completions of one event structure (e.g. hybrid / minimal closure of alias_core) -- microseconds
per candidate with the delta evaluator is NOT used here; each candidate costs one legal.check."""
import sys,os,collections,gzip,json,time
from tkcommon import *
import linwt

def _check_price(w):
    rep=legal.check(w,maxviol=3)
    if not rep['ok']: return None,None
    T,P=X.invoice(rep); return X.kappa(T,P),(T,P)

def best_closure(cands):
    """cands: iterable of (label, word|None).  -> (label, word, kappa) of the legal word with the highest exact kappa (None if none legal)"""
    best=None
    for lab,w in cands:
        if w is None: continue
        k,_=_check_price(w)
        if k is not None and (best is None or k>best[2]): best=(lab,w,k)
    return best

def assign(w,tl=300.0,K=2,maxm=0,threads=None,log=None,hint='nat'):
    """see module doc.  Does not modify w."""
    t0=time.time(); log=log or (lambda *a:None)
    rep0=legal.check(w,maxviol=3)
    if not rep0['ok']: return w,dict(status='INPUT_ILLEGAL',kept='input')
    T,P=X.invoice(rep0); pc=X.Pricer(T,P); k0=pc.k
    res=_solve(w,pc,tl,K,maxm,threads or int(os.environ.get('HEAVY_THREADS','2')),log,hint)
    if res is None: return w,dict(status='NO_SOLUTION',kappa0=k0,kappa=k0,gain=0.0,kept='input',seconds=round(time.time()-t0,1))
    w2,info=res
    k2,_=_check_price(w2)
    info.update(kappa0=k0,seconds=round(time.time()-t0,1))
    if k2 is None or k2<k0:
        info.update(kept='input',kappa=k0,gain=0.0,realised_kappa=k2); return w,info
    info.update(kept='new',kappa=k2,gain=k2-k0); return w2,info

def _sorted_basis(S):
    b=[];sp={0}
    for v in sorted(S):
        if v not in sp: b.append(v); sp|={x^v for x in sp}
    return b

def _solve(w,pc,TL,K,MAXM,threads,log,hint='nat'):
    import lattice_retime as LR
    from ortools.sat.python import cp_model
    k0=pc.k; cwP,cwT=linwt.weights(pc)
    fr=legal.spans(w);NH=len(w['initial']);NR=NH+legal.nown(w);live=list(w['live']);liveS=set(live);main=liveS|{r+112 for r in live}
    RET=set(legal.retired_of(w)); OWN=legal.owned_set(w)
    ports=w['ports'];prog=w['program']
    tl=collections.defaultdict(list); nat={}; vid={}
    V=lambda r: vid.get(r,r)
    for r in range(NH):
        if r in RET: continue
        tl[r].append(('I',r)); nat[('I',r)]=w['initial'][r]
    for i,e in enumerate(prog):
        op,r=e[0],e[1]
        if op in('ADD','COPY'):
            k=('E',i); nat[k]=e[-1]; tl[V(r)].append(k); tl[V(e[2])].append(k)
        elif op=='INIT': vid[r]=10**6+i; tl[vid[r]]=[('E',i)]; nat[('E',i)]=e[2]
        elif op=='CLEAR': tl[V(r)].append(('E',i)); nat[('E',i)]=e[2]
    for r in range(NH):
        if r in RET: continue
        tl[r].append(('F',r)); nat[('F',r)]=w['final'][r]
    lb=[0]*NR;ub=[0]*NR;LB={};UB={}
    for k,r in enumerate(live): lb[r]|=1<<k
    for i,e in enumerate(prog):
        op,r=e[0],e[1]
        if op in('ADD','COPY'):
            ro,so=r in OWN,e[2] in OWN
            b=(0 if ro else lb[r])|(0 if so else lb[e[2]])
            if not ro: lb[r]=b
            if not so: lb[e[2]]=b
            LB[('E',i)]=b
    for r in range(NH):
        if r not in RET: LB[('F',r)]=lb[r]; LB[('I',r)]=(1<<live.index(r)) if r in liveS else 0
    for k,r in enumerate(live): ub[r+112]|=1<<k
    for i in range(len(prog)-1,-1,-1):
        e=prog[i];op,r=e[0],e[1]
        if op in('ADD','COPY'):
            ro,so=r in OWN,e[2] in OWN
            b=(0 if ro else ub[r])|(0 if so else ub[e[2]])
            if not ro: ub[r]=b
            if not so: ub[e[2]]=b
            UB[('E',i)]=b
    for r in range(NH):
        if r not in RET: UB[('I',r)]=ub[r]; UB[('F',r)]=(1<<live.index(r-112)) if (r-112 in liveS and r>=112) else 0
    def spanbits(bits):
        s={0}
        for k in range(len(live)):
            if bits>>k&1:
                v=ports[k]
                if v not in s: s|={x^v for x in s}
        return frozenset(s)
    def perpbits(bits):
        ps=[ports[k] for k in range(len(live)) if bits>>k&1]
        return frozenset(x for x in range(512) if all(bin(x&p).count('1')%2==0 for p in ps))
    Lc={};Uc={}
    def Lset(b):
        if b not in Lc: Lc[b]=spanbits(b)
        return Lc[b]
    def Uset(b):
        if b not in Uc: Uc[b]=perpbits(b)
        return Uc[b]
    natS={k:fr[f] for k,f in nat.items()}
    partners=collections.defaultdict(set)
    for r,l in tl.items():
        for k in l: partners[k].add(r)
    idx={}
    for r,l in tl.items():
        for j,k in enumerate(l): idx[(r,k)]=j
    dom={}
    for k in natS:
        cand=set([natS[k]])
        for r in partners[k]:
            l=tl[r]; j=idx[(r,k)]
            for d in range(-K,K+1):
                if 0<=j+d<len(l): cand.add(natS[l[j+d]])
        lo=Lset(LB.get(k,0)); hi=Uset(UB.get(k,0))
        own=any(r>=NH for r in partners[k])
        if not own: cand={s for s in cand if lo<=s<=hi or s==natS[k]}
        cand.add(natS[k])
        if not own and lo<=hi:
            Lb=LR.basis_of(lo);Ub=LR.basis_of(hi);m=len(Ub)-len(Lb)
            if m<=MAXM: cand|=set(LR.subspaces_between(Lb,Ub))
            cand.add(lo); cand.add(hi)
        dom[k]=sorted(cand,key=lambda s:(len(s),sorted(s)[:6]))
    for r in live: dom[('I',r)]=[natS[('I',r)]]
    for r in live: dom[('F',r+112)]=[natS[('F',r+112)]]
    log('nodes',len(dom),'avg dom %.2f'%(sum(len(v) for v in dom.values())/len(dom)))
    M=cp_model.CpModel();x={};Dv={}
    for k,d in dom.items():
        xs=[]
        for i,S in enumerate(d): x[k,i]=M.NewBoolVar(''); xs.append(x[k,i])
        M.AddExactlyOne(xs)
        dims=[len(S).bit_length()-1 for S in d]
        Dv[k]=M.NewIntVar(min(dims),max(dims),'')
        M.Add(Dv[k]==sum(dm*x[k,i] for i,dm in enumerate(dims)))
        h=natS[k]
        if hint=='min' and not any(r>=NH for r in partners[k]):
            lo_=Lset(LB.get(k,0))
            if lo_ in d: h=lo_            # minimal-frame hint (join of lower anchors): the closure(minimal) assignment of ALIAS; the stored assignment stays in every domain
        M.AddHint(x[k,d.index(h)],1)
    tab=[0]+[cwP[d] for d in range(1,10)];obj=[]
    for r,l in tl.items():
        own=r>=NH
        for a,b in zip(l,l[1:]):
            if a==b: continue
            lo,hi=(b,a) if own else (a,b)
            for i,S in enumerate(dom[lo]):
                ok=[x[hi,j] for j,Tt in enumerate(dom[hi]) if S<=Tt]
                M.AddBoolOr(ok+[x[lo,i].Not()])
            for j,Tt in enumerate(dom[hi]):
                ok=[x[lo,i] for i,S in enumerate(dom[lo]) if S<=Tt]
                M.AddBoolOr(ok+[x[hi,j].Not()])
            dl=M.NewIntVar(0,9,'');M.Add(dl==Dv[hi]-Dv[lo])
            c=M.NewIntVar(0,max(tab),'');M.AddElement(dl,tab,c);obj.append(-c)
    tabT=[cwT[d] for d in range(1,10)]
    for r in range(NH):
        if r in main or r in RET: continue
        rk=M.NewIntVar(1,9,'');M.Add(rk==Dv[('F',r)]-Dv[('I',r)])
        g=M.NewIntVar(0,max(tabT),'');M.AddElement(rk-1,tabT,g);obj.append(g)
    M.Maximize(sum(obj))
    natobj=linwt.native_objective(M) if hint=='nat' else None      # (the native objective needs the model hinted at the stored assignment)
    S_=cp_model.CpSolver();S_.parameters.max_time_in_seconds=TL;S_.parameters.num_workers=max(1,threads)
    st=S_.Solve(M)
    log(S_.StatusName(st),'obj',S_.ObjectiveValue())
    if st not in(cp_model.OPTIMAL,cp_model.FEASIBLE): return None
    chosen={k:next(dom[k][i] for i in range(len(dom[k])) if S_.BooleanValue(x[k,i])) for k in dom}
    w2=json.loads(json.dumps(w));ftab={frozenset(fr[i]):i for i in range(len(fr))}
    def fid(S):
        if S not in ftab: w2['frames'].append(_sorted_basis(S)); ftab[S]=len(w2['frames'])-1
        return ftab[S]
    cur={};newp=[]
    for r in range(NH):
        if r not in RET: cur[r]=chosen[('I',r)]
    def need_move(r,target):
        if cur.get(r) is not None and cur[r]!=target:
            newp.append(['MOVE',r,fid(cur[r]),fid(target),r in OWN])
        cur[r]=target
    for i,e in enumerate(prog):
        op,r=e[0],e[1];e=list(e)
        if op=='MOVE': continue
        if op=='INIT': cur[r]=chosen[('E',i)]; e[2]=fid(cur[r]); newp.append(e)
        elif op=='CLEAR': need_move(r,chosen[('E',i)]); e[2]=fid(chosen[('E',i)]); newp.append(e); cur[r]=None
        elif op in('ADD','COPY'):
            F=chosen[('E',i)]; need_move(r,F); need_move(e[2],F); e[-1]=fid(F); newp.append(e)
        else: e[-1]=fid(cur[r]); newp.append(e)
    for r in range(NH):
        if r not in RET: need_move(r,chosen[('F',r)])
    w2['program']=newp
    w2['initial']=[w['initial'][r] if r in RET else fid(chosen[('I',r)]) for r in range(NH)]
    w2['final']=[w['final'][r] if r in RET else fid(chosen[('F',r)]) for r in range(NH)]
    mg=None if natobj is None else (S_.ObjectiveValue()-natobj)/1e16
    return w2,dict(status=S_.StatusName(st),model_gain=mg,nodes=len(dom),bound_gain=None if natobj is None else (S_.BestObjectiveBound()-natobj)/1e16)

def main(argv):
    path,out=argv[0],argv[1]; tl=float(argv[2]) if len(argv)>2 else 300; K=int(argv[3]) if len(argv)>3 else 2; maxm=int(argv[4]) if len(argv)>4 else 0; hint=argv[5] if len(argv)>5 else 'nat'
    w=legal.load(path)
    try: tkcommon_activate=activate; tkcommon_activate(w)
    except Exception: pass
    w2,info=assign(w,tl=tl,K=K,maxm=maxm,log=lambda *a:print(*a,flush=True),hint=hint)
    json.dump(w2,gzip.open(out,'wt'))
    print('RESULT',json.dumps(info,default=str),flush=True)
if __name__=='__main__': main(sys.argv[1:])
