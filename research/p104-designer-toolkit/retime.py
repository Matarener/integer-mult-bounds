"""tk retime WORD --free LIST [--tl SECS] [--out OUT.json.gz] [--wait]
Exact-lattice retime of a FIXED circuit (event order, ADD/COPY/SCALE operands and per-register MOVE counts fixed; only frame subspaces of F2^9 and
which equal-frame stops collapse change).  Successor of infra/lattice_retime.py with named freedoms.  Model: CP-SAT over, for every ADD-equal-frame
cluster, a subspace in [L,U] (sum / intersection of the pinned frames below / above), strict nesting along register chains, helper credit rank >= 1,
objective = linearised kappa (exact marginal tables x18 calls); the realised word is re-checked by legal.check and re-priced EXACTLY (price_exact).
--free (comma list; everything not named stays pinned to the input word's span):
  starts     helper (non-main) initial frames
  finals     helper (non-main) final frames
  stops      a stop may collapse into its neighbour when their frames become equal (MOVE deleted; cost 0).  Implied by starts/finals (the verifier does
             not mind), so `--free starts,finals` = verifier freedom of PR5561; `--free stops` alone collapses with endpoints pinned.
  mainstops  intermediate frames of MAIN registers (X source / Y target chains).  FREE BY DEFAULT (naming it is a no-op): #5561 relabels 149 main
             stops because they share ADD charts with retimed helper stops; pinning them (`--pin mainstops`) costs 1.4e-5 of kappa on #5551.
  mainends   X final and Y initial frames (X initial and Y final are the literal ports and are NEVER free)
`--pin mainstops` forces main-register intermediate frames to stay as in the input word.
Without --inline the solve is queued through W/bin/hq.sh (job tk_retime_*, 4 CP-SAT threads, <=4 heavy jobs machine-wide)."""
import sys,os,collections,gzip,json,time
from tkcommon import *
FREEABLE={'starts','finals','stops','mainstops','mainends'}
def solve(path,free,TL,outp,threads=None,pin=()):
    import lattice_retime as LR, dims_relax as DR
    from ortools.sat.python import cp_model
    w=legal.load(path);B=DR.build(w);NH=B['NH'];live=B['live'];main=B['main'];find=B['find'];stop=B['stop'];cf=B['cf']
    fr=legal.spans(w);dimf=lambda f:len(w['frames'][f])
    rep=legal.check(w)
    if not rep['ok']: print('input word illegal:',rep['violations'][:3]); return dict(error='input illegal')
    T,P=X.invoice(rep);pc=X.Pricer(T,P);k0=pc.k
    cwP={d:round(1e16*(k0-pc.delta(None,{d:18}))) for d in range(1,10)}
    cwT={d:round(1e16*(pc.delta({d:18},None)-k0)) for d in range(1,10)}
    stopfree=bool(free&{'stops','starts','finals'})
    A=set()
    for r in range(NH):
        ini,fin=find((r,0)),find((r,stop[r]))
        if r in live: A.add(ini)                                  # literal port
        if r in main and r not in live: A.add(fin)                # Y final: literal hyperplane
        if r in main:
            if 'mainends' not in free:
                A.add(ini); A.add(fin)
        else:
            if 'starts' not in free: A.add(ini)
            if 'finals' not in free: A.add(fin)
    if 'mainstops' in pin:
        for r in main:
            for s in range(1,stop[r]): A.add(find((r,s)))
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
    dom={}
    for c in cf:
        if c in A: dom[c]=[frozenset(fr[cf[c]])]; continue
        Lset=LR.span_of([v for a in Ls[c] for v in w['frames'][cf[a]]]); Uset=None
        for a in Us[c]:
            s=set(fr[cf[a]]); Uset=s if Uset is None else Uset&s
        if Uset is None: Uset=set(range(512))
        Lb=LR.basis_of(Lset);Ub=LR.basis_of(Uset);m=len(Ub)-len(Lb);nat=frozenset(fr[cf[c]])
        if m<=LR.MAXQ: d=set(LR.subspaces_between(Lb,Ub))
        else:
            d={frozenset(Lset),frozenset(Uset)}
            for f in fr:
                if Lset<=f<=Uset: d.add(frozenset(f))
        d.add(nat); dom[c]=sorted(d,key=lambda s:(len(s),sorted(s)[:8]))
    M=cp_model.CpModel();x={};Dv={}
    for c in cf:
        xs=[]
        for i,S in enumerate(dom[c]): x[c,i]=M.NewBoolVar(''); xs.append(x[c,i])
        M.AddExactlyOne(xs)
        dims=[len(S).bit_length()-1 for S in dom[c]]
        Dv[c]=M.NewIntVar(min(dims),max(dims),''); M.Add(Dv[c]==sum(dm*x[c,i] for i,dm in enumerate(dims)))
    lt=(lambda S,Tt:S<=Tt) if stopfree else (lambda S,Tt:S<Tt)
    for a,b,r in B['links']:
        lo,hi=(a,b) if r<NH else (b,a)
        for i,S in enumerate(dom[lo]): M.AddBoolOr([x[hi,j] for j,Tt in enumerate(dom[hi]) if lt(S,Tt)]+[x[lo,i].Not()])
        for j,Tt in enumerate(dom[hi]): M.AddBoolOr([x[lo,i] for i,S in enumerate(dom[lo]) if lt(S,Tt)]+[x[hi,j].Not()])
    tab=([0] if stopfree else [])+[cwP[d] for d in range(1,10)];tabT=[cwT[d] for d in range(1,10)];obj=[]
    for a,b,r in B['links']:
        lo,hi=(a,b) if r<NH else (b,a)
        dl=M.NewIntVar(0 if stopfree else 1,9,'');M.Add(dl==Dv[hi]-Dv[lo]);cst=M.NewIntVar(0,max(tab),'');M.AddElement(dl-(0 if stopfree else 1),tab,cst);obj.append(-cst)
    for r in range(NH):
        if r in main: continue
        a,b=find((r,0)),find((r,stop[r]))
        rk=M.NewIntVar(1,9,'');M.Add(rk==Dv[b]-Dv[a]);g=M.NewIntVar(0,max(tabT),'');M.AddElement(rk-1,tabT,g);obj.append(g)
    M.Maximize(sum(obj))
    for c in cf:
        nat=frozenset(fr[cf[c]])
        for i,S in enumerate(dom[c]): M.AddHint(x[c,i],1 if S==nat else 0)
    S_=cp_model.CpSolver();S_.parameters.max_time_in_seconds=TL;S_.parameters.num_workers=threads or int(os.environ.get('HEAVY_THREADS','4'))
    nat_obj=0
    for a,b,r in B['links']:
        lo,hi=(a,b) if r<NH else (b,a); nat_obj-=cwP[dimf(cf[hi])-dimf(cf[lo])]
    for r in range(NH):
        if r not in main: nat_obj+=cwT[dimf(cf[find((r,stop[r]))])-dimf(cf[find((r,0))])]
    t0=time.time(); st=S_.Solve(M)
    res=dict(free=sorted(free),pin=sorted(pin),status=S_.StatusName(st),pinned_clusters=len(A),clusters=len(cf),domain_total=sum(len(d) for d in dom.values()),
             ceiling_lin=(S_.BestObjectiveBound()-nat_obj)/1e16,found_lin=(S_.ObjectiveValue()-nat_obj)/1e16,seconds=round(time.time()-t0),base_kappa=k0)
    print(json.dumps(res),flush=True)
    if st not in (cp_model.OPTIMAL,cp_model.FEASIBLE): return res
    chosen={c:next(dom[c][i] for i in range(len(dom[c])) if S_.BooleanValue(x[c,i])) for c in cf}
    w2=json.loads(json.dumps(w)); ftab={}
    for i,b in enumerate(w['frames']): ftab[frozenset(fr[i])]=i
    def fid(S):
        if S not in ftab: w2['frames'].append(LR.basis_of(S)); ftab[S]=len(w2['frames'])-1
        return ftab[S]
    stp=collections.defaultdict(int); newp=[]
    for e in w['program']:
        e=list(e);op,r=e[0],e[1]
        if op=='MOVE':
            a=find((r,stp[r])); stp[r]+=1; b=find((r,stp[r])); e[2]=fid(chosen[a]); e[3]=fid(chosen[b])
            if chosen[a]==chosen[b]: continue
        elif op=='INIT': stp[r]=0; e[2]=fid(chosen[find((r,0))])
        elif op=='CLEAR': e[2]=fid(chosen[find((r,stp[r]))])
        else: e[-1]=fid(chosen[find((r,stp[r]))])
        newp.append(e)
    w2['program']=newp
    w2['initial']=[fid(chosen[find((r,0))]) for r in range(NH)]
    w2['final']=[fid(chosen[find((r,stp[r]))]) for r in range(NH)]
    if outp: json.dump(w2,gzip.open(outp,'wt'))
    rep2=legal.check(w2); res['realised_legal']=rep2['ok']; res['violations']=[list(map(str,v)) for v in rep2['violations'][:3]]
    if rep2['ok']:
        T2,P2=X.invoice(rep2); res['kappa']=str(X.kappa_dec(T2,P2,50))[:20]; res['gain']=float(X.kappa(T2,P2)-k0); res['side_ok']=X.side(T2,P2)['ok']
        res['moves_deleted']=sum(1 for e in w['program'] if e[0]=='MOVE')-sum(1 for e in newp if e[0]=='MOVE'); res['out']=outp
    print('RESULT',json.dumps(res,default=str),flush=True)
    return res
def parse_free(s):
    f={x.strip() for x in s.split(',') if x.strip()}
    if f-FREEABLE: raise SystemExit('tk retime: unknown freedom %s (choose from %s)'%(sorted(f-FREEABLE),sorted(FREEABLE)))
    return f
def main(a):
    path,w=load(a.word); free=parse_free(a.free)
    pin=set(a.pin.split(',')) if a.pin else set()
    out=a.out or '%s/%s__%s.json.gz'%(OUT,os.path.basename(path).split('.')[0] if a.word not in ALIASES else a.word,'_'.join(sorted(free))+('_pin'+a.pin.replace(',','') if a.pin else ''))
    os.makedirs(os.path.dirname(out),exist_ok=True)
    if a.inline:
        r=solve(path,free,a.tl,out,pin=pin); return 0 if r and not r.get('error') else 1
    name=a.name or 'tk_retime_%s_%s'%(sha(path)[:8],'_'.join(sorted(free)))
    ok=submit(name,a.tl+600,[PY,'-B',HERE+'/tk.py','retime',path,'--free',a.free,'--tl',str(a.tl),'--out',out,'--inline']+(['--pin',a.pin] if a.pin else []),a.wait,threads=4)
    print('log: %s/jobs/%s.log   output: %s'%(W,name,out))
    if a.wait:
        print(open(W+'/jobs/%s.log'%name).read()[-1500:])
