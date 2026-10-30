"""Exact EVENT-LEVEL lattice retime (MODELERR2/ev_lat.py, path-portable copy). usage: evlat.py WORD OUT.json.gz TL K MAXM"""
import sys,os,collections,gzip,json
import os;sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)));from tkcommon import INFRA;sys.path.insert(0,INFRA)
import legal,price_exact as X,lattice_retime as LR
from ortools.sat.python import cp_model
path,outp,TL,K=sys.argv[1],sys.argv[2],float(sys.argv[3]),int(sys.argv[4]);MAXM=int(sys.argv[5])
import tkcommon;legal_pr=tkcommon.profile_of(legal.load(path))[1];legal_decay=legal_pr['decay']      # tail-decay constant of the word's verifier profile
w=legal.load(path);rep=legal.check(w);T,P=X.invoice(rep);pc=X.Pricer(T,P);k0=pc.k
# owned-role count comes from the word's verifier profile (legal.nown): no 8-owned assumption
import linwt; cwP,cwT=linwt.weights(pc)   # RETIMEGAP: symmetric exact-first-order weights (infra/linwt.py)
fr=legal.spans(w);NH=len(w['initial']);NR=NH+legal.nown(w);live=list(w['live']);liveS=set(live);main=liveS|{r+112 for r in live}
RET=set(legal.retired_of(w)); OWN=legal.owned_set(w)     # prepared573: the retired public role is an owned scratch role (several lifetimes)
ports=w['ports'];prog=w['program']
dimf=lambda f:len(w['frames'][f])
# ---- timelines
# every owned LIFETIME is its own timeline (virtual id >= 10**6 + i); an owned role used for several lifetimes (573) must not lose the earlier ones
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
# ---- L/U bits (owned excluded)
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
COV={};UNCOV=[]
Lc={};Uc={}
def Lset(b):
    if b not in Lc: Lc[b]=spanbits(b)
    return Lc[b]
def Uset(b):
    if b not in Uc: Uc[b]=perpbits(b)
    return Uc[b]
# ---- domains
natS={k:fr[f] for k,f in nat.items()}
dom={}
for r,l in tl.items():
    for j,k in enumerate(l):
        if k in dom: continue
        cand={natS[k]}
        dom[k]=cand
        for r2 in (r,):
            pass
partners=collections.defaultdict(set)   # node -> registers
for r,l in tl.items():
    for k in l: partners[k].add(r)
for k in list(dom):
    cand=set([natS[k]])
    for r in partners[k]:
        l=tl[r]; j=l.index(k)
        for d in range(-K,K+1):
            if 0<=j+d<len(l): cand.add(natS[l[j+d]])
    lo=Lset(LB.get(k,0)); hi=Uset(UB.get(k,0))
    own=any(r>=NH for r in partners[k])
    if not own: cand={s for s in cand if lo<=s<=hi or s==natS[k]}
    cand.add(natS[k])
    if not own and lo<=hi:
        Lb=LR.basis_of(lo);Ub=LR.basis_of(hi);m=len(Ub)-len(Lb)
        if m<=MAXM: cand|=set(LR.subspaces_between(Lb,Ub))
    if not own: cand.add(lo) if lo<=hi else None; cand.add(hi) if lo<=hi else None
    if not own and lo<=hi and k[0]=='E':
        mm=len(LR.basis_of(hi))-len(LR.basis_of(lo)); COV[mm]=COV.get(mm,0)+1
        if mm>MAXM: UNCOV.append(k)
    dom[k]=sorted(cand,key=lambda s:(len(s),sorted(s)[:6]))
print('COVERAGE free-interval dim(U/L) histogram over unowned ADD/COPY events:',dict(sorted(COV.items())),'| events whose interval exceeds MAXM=%d (candidates = native/neighbour/L/U only, NOT all subspaces): %d'%(MAXM,len(UNCOV)),flush=True)
anch=set()
for r in live: anch.add(('I',r))
for r in live: anch.add(('F',r+112))
for k in anch: dom[k]=[natS[k]]
print('nodes',len(dom),'avg dom %.2f'%(sum(len(v) for v in dom.values())/len(dom)),flush=True)
M=cp_model.CpModel();x={};Dv={}
for k,d in dom.items():
    xs=[]
    for i,S in enumerate(d): x[k,i]=M.NewBoolVar(''); xs.append(x[k,i])
    M.AddExactlyOne(xs)
    dims=[len(S).bit_length()-1 for S in d]
    Dv[k]=M.NewIntVar(min(dims),max(dims),'')
    M.Add(Dv[k]==sum(dm*x[k,i] for i,dm in enumerate(dims)))
    nidx=d.index(natS[k]); M.AddHint(x[k,nidx],1)
tab=[0]+[cwP[d] for d in range(1,10)];obj=[]
for r,l in tl.items():
    own=r>=NH
    for a,b in zip(l,l[1:]):
        if a==b: continue
        lo,hi=(b,a) if own else (a,b)   # S_lo <= S_hi
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
if os.environ.get('NATONLY'):      # diagnostic: is the word's own assignment feasible in the model?  (prints the native objective)
    for k,d in dom.items(): M.Add(x[k,d.index(natS[k])]==1)
NATOBJ=None if os.environ.get('NATONLY') else linwt.native_objective(M)      # RETIMEGAP: model objective of the native assignment
S_=cp_model.CpSolver();S_.parameters.max_time_in_seconds=TL;S_.parameters.num_workers=int(os.environ.get('HEAVY_THREADS','4'))
st=S_.Solve(M)
print(S_.StatusName(st),'obj',S_.ObjectiveValue(),flush=True)
if st not in(cp_model.OPTIMAL,cp_model.FEASIBLE): sys.exit()
chosen={k:next(dom[k][i] for i in range(len(dom[k])) if S_.BooleanValue(x[k,i])) for k in dom}
# ---- realise
w2=json.loads(json.dumps(w));ftab={frozenset(fr[i]):i for i in range(len(fr))}
def fid(S):
    if S not in ftab: w2['frames'].append(sorted_basis(S)); ftab[S]=len(w2['frames'])-1
    return ftab[S]
def sorted_basis(S):
    b=[];sp={0}
    for v in sorted(S):
        if v not in sp: b.append(v); sp|={x^v for x in sp}
    return b
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
    else: # SCALE
        e[-1]=fid(cur[r]); newp.append(e)
for r in range(NH):
    if r not in RET: need_move(r,chosen[('F',r)])
w2['program']=newp
w2['initial']=[w['initial'][r] if r in RET else fid(chosen[('I',r)]) for r in range(NH)]
w2['final']=[w['final'][r] if r in RET else fid(chosen[('F',r)]) for r in range(NH)]
json.dump(w2,gzip.open(outp,'wt'))
rep2=legal.check(w2);print('REALISED legal',rep2['ok'],rep2['violations'][:3],flush=True)
if rep2['ok']:
    T2,P2=X.invoice(rep2);print('EXACT kappa %.12f base %.12f gain %.3e'%(X.kappa(T2,P2),k0,X.kappa(T2,P2)-k0),'side',tkcommon.side_of(T2,P2,legal_pr)['ok'])
    if NATOBJ is not None: print('MODELGAP model_gain %.4e exact_gain %.4e diff %.3e'%((S_.ObjectiveValue()-NATOBJ)/1e16,X.kappa(T2,P2)-k0,(S_.ObjectiveValue()-NATOBJ)/1e16-(X.kappa(T2,P2)-k0)),flush=True)
    print('paid',{d:rep2['paid'].get(d,0) for d in range(1,10)},'help',rep2['helpers'])
