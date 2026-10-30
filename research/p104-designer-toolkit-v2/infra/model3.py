"""P104HUB v2: free schedule + free frame vocabulary on a neighbourhood V. Path (succ-arc) formulation per register.
usage: model2.py OUT.json TLIMIT V_SPEC   V_SPEC = 'none' | 'rand:SEED:K' | 'all' | comma list of registers"""
import sys,json,os,random,collections,bisect
from base import *
from ortools.sat.python import cp_model
import pr
OUT=sys.argv[1]; TL=float(sys.argv[2]); VS=sys.argv[3]
n=len(prog); dimf=lambda f:len(fr[f])
def sp(b):
    s={0}
    for v in b: s|={x^v for x in s}
    return frozenset(s)
SPN={}
def S(f):
    if f not in SPN: SPN[f]=sp(fr[f])
    return SPN[f]
mv=collections.defaultdict(list)
for i,e in enumerate(prog):
    if e[0]=='MOVE': mv[e[1]].append(i)
FR={}
for r in range(N):
    if r<NH: FR[r]=[w['initial'][r]]+[prog[i][3] for i in mv[r]]
    else: FR[r]=[[e for e in prog if e[0]=='INIT' and e[1]==r][0][2]]+[prog[i][3] for i in mv[r]]
def nstop(r,i): return bisect.bisect_left(mv[r],i)
helpers=[r for r in range(NH) if r not in main]
partners=collections.defaultdict(set)
for e in prog:
    if e[0]=='ADD' and e[1]<NH and e[2]<NH: partners[e[1]].add(e[2]); partners[e[2]].add(e[1])
if VS=='none': V=set()
elif VS=='all': V=set(range(NH))
elif VS.startswith('rand:'):
    _,sd,K=VS.split(':'); rr=random.Random(int(sd)); V=set(rr.sample(helpers,int(K)))
elif VS.startswith('nbr:'):   # helper seed + its H partners
    _,sd,K=VS.split(':'); rr=random.Random(int(sd)); s0=rr.choice(helpers); V={s0}; fr_=[s0]
    while len(V)<int(K) and fr_:
        x=fr_.pop(0)
        for p in sorted(partners[x]):
            if p<NH and p not in V and len(V)<int(K): V.add(p); fr_.append(p)
else: V=set(int(x) for x in VS.split(','))
print('V size',len(V),flush=True)
X={}
for r in range(N):
    nat=list(dict.fromkeys(FR[r]))
    if r in V:
        lo=S(FR[r][0]); hi=S(FR[r][-1]); cand=set(nat)
        for p in partners[r]:
            for f in FR[p]:
                if lo<=S(f)<=hi: cand.add(f)
        X[r]=sorted(cand,key=lambda f:(dimf(f),f))
    else: X[r]=nat
M=cp_model.CpModel(); H=n
t={i:M.NewIntVar(0,H,f't{i}') for i,e in enumerate(prog) if e[0]!='MOVE'}
bar=[]
state=collections.defaultdict(lambda:{'ph':'w','gate':None,'mem':[]})
def newbar(preds):
    b=M.NewIntVar(0,H,f'b{len(bar)}'); bar.append(b)
    for u in preds: M.Add(t[u]<=b) if isinstance(u,int) else M.Add(u<=b)
    return b
def close(x):
    s=state[x]
    if not s['mem']: return s['gate']
    b=newbar(s['mem']); s['mem']=[]; s['gate']=b; return b
def strict_after(gate,v):
    if gate is None: return
    if isinstance(gate,int): M.Add(t[gate]+1<=t[v])
    else: M.Add(gate+1<=t[v])
def reader(x,v):
    s=state[x]
    if s['ph']=='w': close(x); s['ph']='r'
    strict_after(s['gate'],v); s['mem'].append(v)
def writer(x,v):
    s=state[x]
    if s['ph']=='r': close(x); s['ph']='w'
    strict_after(s['gate'],v); s['mem'].append(v)
def hardw(x,v):
    s=state[x]; g=close(x); strict_after(g,v); s['ph']='w'; s['gate']=v; s['mem']=[]
for i,e in enumerate(prog):
    op=e[0]
    if op=='MOVE': continue
    if op=='ADD': reader(e[2],i); writer(e[1],i)
    elif op=='COPY': reader(e[2],i); hardw(e[1],i)
    else: hardw(e[1],i)
# INFRA FIX (legality oracle finding): verifier needs peak owned fields == 1 (local.py replay), i.e. owned lifetimes
# INIT..CLEAR pairwise disjoint; the original model2 left them unordered, and every solution came out with peak 8.
_inits=[(i,e[1]) for i,e in enumerate(prog) if e[0]=='INIT']; _clr={e[1]:i for i,e in enumerate(prog) if e[0]=='CLEAR'}
for (_i,_r),(_j,_r2) in zip(_inits,_inits[1:]): M.Add(t[_clr[_r]]<t[_j])
# per-register path model
cv={}; A={}; D={}; succ={}; obj=[]
base=pr.kap(pr.T,pr.P); cw={}
for d in range(1,10):
    P2=collections.Counter(pr.P); P2[d]+=18; cw[d]=base-pr.kap(pr.T,P2)
cw={d:round(1e15*(cw[d]-d*cw[1])) for d in cw}
priv=lambda r:r>=NH
for r in range(N):
    Xr=X[r]; init=FR[r][0]; fin=FR[r][-1]
    for f in Xr:
        cv[(r,f)]=M.NewBoolVar(f'c{r}_{f}')
        A[(r,f)]=M.NewIntVar(0,H+1,f'A{r}_{f}'); D[(r,f)]=M.NewIntVar(0,H+1,f'D{r}_{f}')
        M.Add(A[(r,f)]<=D[(r,f)])
    M.Add(cv[(r,init)]==1); M.Add(cv[(r,fin)]==1)
    M.Add(A[(r,init)]==0); M.Add(D[(r,fin)]==H+1)
    if priv(r):
        for f in Xr: M.Add(cv[(r,f)]==1)
        for f,g in zip(FR[r],FR[r][1:]): M.Add(D[(r,f)]<=A[(r,g)])
        continue
    out={f:[] for f in Xr}; inn={f:[] for f in Xr}
    for ii,f in enumerate(Xr):
        for g in Xr[ii+1:]:
            if dimf(g)>dimf(f) and S(f)<S(g):
                s=M.NewBoolVar(f's{r}_{f}_{g}'); succ[(r,f,g)]=s; out[f].append(s); inn[g].append(s)
                M.Add(D[(r,f)]<=A[(r,g)]).OnlyEnforceIf(s)
                obj.append(cw[dimf(g)-dimf(f)]*s)
    for f in Xr:
        if f!=fin: M.Add(sum(out[f])==cv[(r,f)])
        else: M.Add(sum(out[f])==0)
        if f!=init: M.Add(sum(inn[f])==cv[(r,f)])
        else: M.Add(sum(inn[f])==0)
def place(r,f,i,lit=None):
    a=M.Add(A[(r,f)]<=t[i]); b=M.Add(t[i]<D[(r,f)])
    if lit is not None: a.OnlyEnforceIf(lit); b.OnlyEnforceIf(lit)
yv=[]
for i,e in enumerate(prog):
    op=e[0]
    if op=='MOVE': continue
    if op=='ADD':
        a,b=e[1],e[2]
        if priv(a) or priv(b):
            for r in (a,b):
                f=FR[r][nstop(r,i)]; M.Add(cv[(r,f)]==1); place(r,f,i)
            continue
        opts=[f for f in X[a] if (b,f) in cv]
        nat=FR[a][nstop(a,i)]; assert FR[b][nstop(b,i)]==nat
        if len(opts)==1:
            M.Add(cv[(a,nat)]==1); M.Add(cv[(b,nat)]==1); place(a,nat,i); place(b,nat,i); continue
        ys=[]
        for f in opts:
            y=M.NewBoolVar(f'y{i}_{f}'); ys.append(y); yv.append((i,f,y))
            M.AddImplication(y,cv[(a,f)]); M.AddImplication(y,cv[(b,f)])
            place(a,f,i,y); place(b,f,i,y)
        M.AddExactlyOne(ys)
    else:
        rs=[e[1]]+([e[2]] if op=='COPY' else [])
        for r in rs:
            f=FR[r][nstop(r,i)]; M.Add(cv[(r,f)]==1); place(r,f,i)
M.Minimize(sum(obj))
# hint
for i in t: M.AddHint(t[i],i)
natc=set()
for r in range(N):
    for f in X[r]: M.AddHint(cv[(r,f)],1 if f in FR[r] else 0)
    ch=list(dict.fromkeys(FR[r]))
    for j,f in enumerate(ch):
        if f in FR[r]:
            idx=[x for x,g in enumerate(FR[r]) if g==f]
            M.AddHint(A[(r,f)],0 if j==0 else mv[r][idx[0]-1]); M.AddHint(D[(r,f)],H+1 if j==len(ch)-1 else mv[r][idx[-1]])
for r in range(N):
    ch=FR[r]; hs=set()
    for j in range(len(ch)-1):
        if (r,ch[j],ch[j+1]) in succ: hs.add((r,ch[j],ch[j+1]))
    for k_,x in succ.items():
        if k_[0]==r: M.AddHint(x,1 if k_ in hs else 0)
for (i,f,y) in yv: M.AddHint(y,1 if FR[prog[i][1]][nstop(prog[i][1],i)]==f else 0)
nat=sum(cw[dimf(b)-dimf(a)] for r in range(NH) for a,b in zip(FR[r],FR[r][1:]))
print('model vars',len(M.Proto().variables),'cons',len(M.Proto().constraints),'native obj',nat,flush=True)
S_=cp_model.CpSolver(); S_.parameters.max_time_in_seconds=TL; S_.parameters.num_workers=int(os.environ.get('HEAVY_THREADS','4')); S_.parameters.log_search_progress=False
class CB(cp_model.CpSolverSolutionCallback):
    def __init__(s): super().__init__()
    def on_solution_callback(s):
        d={'obj':s.ObjectiveValue(),'t':{i:s.Value(v) for i,v in t.items()},
           'path':{str(r):None for r in range(0)},
           'succ':[[r,f,g] for (r,f,g),x in succ.items() if s.BooleanValue(x)],
           'A':{f'{r},{f}':s.Value(v) for (r,f),v in A.items() if s.BooleanValue(cv[(r,f)])},
           'y':{str(i):f for (i,f,y) in yv if s.BooleanValue(y)}}
        json.dump(d,open(OUT,'w'))
print(M.Validate()[:600],flush=True)
st=S_.Solve(M,CB())
print(S_.StatusName(st),S_.ObjectiveValue(),S_.BestObjectiveBound(),'native',nat,'gain_kappa_approx %.3e'%((nat-S_.ObjectiveValue())/1e15),flush=True)
