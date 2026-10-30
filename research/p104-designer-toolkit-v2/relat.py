"""Exact EVENT-ORDER + frame retime (tk reorder).  evlat.py generalised: every ADD/COPY event has its own frame variable AND events that commute may change places.
usage: reorder.py WORD OUT.json.gz TL K MAXM [LO HI]      (LO HI = optional event window: only events/registers touched in [LO,HI] are free, the rest is pinned)

Commutation classes (trace theory of the scalar program; MOVEs carry only frames and are re-derived):
  ADD(t,s): reads s (access R), additively writes t (access W).  Two events commute iff on every shared register they are both R or both W
  (reads of one register commute; additive writes into one register commute; a read and a write do not; ADD(t,s),ADD(t',s') with s!=t', s'!=t).
  SCALE / INIT / CLEAR / COPY, and any event touching an OWNED register (>=NH), are barriers (fixed order) -- the owned-touching freedom is NOT explored (next lever).
Per public register the timeline is  I, epoch_1, ..., epoch_m, F  where an epoch is a maximal run of R accesses or of W accesses (barriers are singleton epochs).
Model (CP-SAT): frame x[node,i]; register with only singleton epochs -> consecutive-pair nesting + cost (== evlat); register with a multi-member epoch ('flex') ->
  all frames it visits are a chain (pairwise nested), dims are monotone across epochs, cost = chain cost through the SET of dims visited.
Realisation: sort every epoch by (chosen dim, original index), topologically sort the union of per-register orders (ties by original index), re-insert MOVEs, legal.check + exact price.
Permissive L/U domain bounds use only the values/demands forced by epoch order (the original evlat bounds also credit same-epoch siblings)."""
import sys,os,collections,gzip,json,heapq
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)));from tkcommon import INFRA;sys.path.insert(0,INFRA)
import legal,price_exact as X,lattice_retime as LR
from ortools.sat.python import cp_model
path,outp,TL,K=sys.argv[1],sys.argv[2],float(sys.argv[3]),int(sys.argv[4]);MAXM=int(sys.argv[5])
WLO,WHI=(int(sys.argv[6]),int(sys.argv[7])) if len(sys.argv)>7 else (None,None)
CAP=int(os.environ.get('REORDER_CAP','40'))
import tkcommon;legal_pr=tkcommon.profile_of(legal.load(path))[1];legal_decay=legal_pr['decay']      # tail-decay constant of the word's verifier profile
w=legal.load(path);rep=legal.check(w);T,P=X.invoice(rep);pc=X.Pricer(T,P);k0=pc.k
import linwt; cwP,cwT=linwt.weights(pc)   # RETIMEGAP: symmetric exact-first-order weights (infra/linwt.py)
fr=legal.spans(w);NH=len(w['initial']);NR=NH+legal.nown(w);live=list(w['live']);liveS=set(live);main=liveS|{r+112 for r in live}
ports=w['ports']
# prepared573: the retired public role (573) is an OWNED scratch role with several lifetimes.  Each lifetime is renamed to its own virtual owned register id (>= NH+8) for the
# model (owned-register barriers, per-lifetime timelines) and mapped back by unmap() when the word is realised.  No-op for words without `retired_public`.
RET=set(legal.retired_of(w));PUB=[r for r in range(NH) if r not in RET];VB=NH+legal.nown(w);OWN=legal.owned_set(w)
import collections as _C
MULTI=RET|{r for r,c in _C.Counter(e[1] for e in w['program'] if e[0]=='INIT').items() if c>1 and r in OWN}   # owned roles with several lifetimes (8-owned words: none -> numbering unchanged)
_vm={};_n=0;prog=[];_back={}
for _e in w['program']:
    _e=list(_e)
    if _e[0]=='INIT' and _e[1] in MULTI:   # every lifetime of a multi-lifetime owned role (573 of a prepared word, role 751 of an owned_fields word) gets its own virtual id
         _vm[_e[1]]=VB+_n;_back[VB+_n]=_e[1];_n+=1
    if _e[1] in _vm: _e[1]=_vm[_e[1]]
    if _e[0] in('ADD','COPY') and _e[2] in _vm: _e[2]=_vm[_e[2]]
    if _e[0]=='CLEAR' and _e[1] in _back and _back[_e[1]] in _vm: del _vm[_back[_e[1]]]
    prog.append(_e)
NR=VB+_n
def unmap(e):
    e=list(e);e[1]=_back.get(e[1],e[1])
    if e[0] in('ADD','COPY'): e[2]=_back.get(e[2],e[2])
    return e
def inwin(i): return WLO is None or WLO<=i<=WHI
# ---------- accesses
def accesses(e):
    op=e[0];r=e[1]
    if op in('ADD','COPY'):
        s=e[2]
        if op=='ADD' and r<NH and s<NH: return [(r,'W'),(s,'R')]
        return [(r,'B'),(s,'B')]
    return [(r,'B')]
seq=collections.defaultdict(list)     # reg -> [(kind,item)]  item=('I',r)|('E',i)|('S',i)|('F',r)
nat={}
for r in PUB: seq[r].append(('B',('I',r))); nat[('I',r)]=w['initial'][r]
touched=set()
for i,e in enumerate(prog):
    op=e[0]
    if op=='MOVE': continue
    if op in('ADD','COPY'): nat[('E',i)]=e[-1]
    elif op in('INIT','CLEAR'): nat[('E',i)]=e[2]
    for r,kd in accesses(e):
        seq[r].append((kd,('E',i) if op!='SCALE' else ('S',i)))
        if inwin(i): touched.add(r)
for r in PUB: seq[r].append(('B',('F',r))); nat[('F',r)]=w['final'][r]
tl={r:[it for kd,it in l if it[0]!='S'] for r,l in seq.items()}
epochs={}     # reg -> list of epochs (list of node items, singleton barrier epochs skipped when SCALE only)
epid={}
for r,l in seq.items():
    ep=[];last=None
    for kd,it in l:
        if kd!='B' and ep and last==kd: ep[-1].append(it)
        else: ep.append([it])
        last=kd
    epochs[r]=[[it for it in E if it[0]!='S'] for E in ep]
    epochs[r]=[E for E in epochs[r] if E]
flex={r for r,E in epochs.items() if r<NH and any(len(x)>1 for x in E)}
print('registers with timeline',len(tl),'flex (multi-member epoch)',len(flex),'events in multi epochs',sum(len(x) for r in flex for x in epochs[r] if len(x)>1),flush=True)
# ---------- permissive L/U bits (value bits forced by epoch order)
Lb={};Ub={}
V=[0]*NR;Vb=[0]*NR;lastk=[None]*NR
for k,r in enumerate(live): V[r]|=1<<k
LB={}
for r in PUB: LB[('I',r)]=V[r] if r in liveS else 0
for i,e in enumerate(prog):
    op=e[0]
    if op=='MOVE': continue
    ac=accesses(e)
    if op=='ADD' and len(ac)==2 and ac[0][1]=='W':
        t,s=e[1],e[2]
        if lastk[t]!='W': Vb[t]=V[t]
        LB[('E',i)]=V[s]|Vb[t]; V[t]|=V[s]
        lastk[t]='W'; lastk[s]='R'
    else:
        b=0
        for r,kd in ac:
            if r<NH: b|=V[r]
            lastk[r]='B'
        LB[('E',i)]=b
for r in PUB: LB[('F',r)]=V[r]
D=[0]*NR;Dh=[0]*NR;lastk=[None]*NR
for k,r in enumerate(live): D[r+112]|=1<<k
UB={}
for i in range(len(prog)-1,-1,-1):
    e=prog[i];op=e[0]
    if op=='MOVE': continue
    ac=accesses(e)
    if op=='ADD' and len(ac)==2 and ac[0][1]=='W':
        t,s=e[1],e[2]
        if lastk[t]!='W': Dh[t]=D[t]
        if lastk[s]!='R': Dh[s]=D[s]
        UB[('E',i)]=Dh[t]|Dh[s]; D[s]|=Dh[t]
        lastk[t]='W'; lastk[s]='R'
    else:
        b=0
        for r,kd in ac:
            if r<NH: b|=D[r]
            lastk[r]='B'
        UB[('E',i)]=b
for r in PUB: UB[('I',r)]=D[r]; UB[('F',r)]=(1<<live.index(r-112)) if (r-112 in liveS and r>=112) else 0
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
# ---------- node set, free nodes
natS={k:fr[f] for k,f in nat.items()}
partners=collections.defaultdict(set)
for r,l in tl.items():
    for k in l: partners[k].add(r)
def isfree(k):
    if WLO is None: return True
    if k[0]=='E': return inwin(k[1])
    return k[1] in touched
pos={}
for r,l in tl.items():
    for j,k in enumerate(l): pos[r,k]=j
epo={}     # (r,node)->(a,b) index range of its epoch in tl[r]
for r,E in epochs.items():
    p=0
    for ep in E:
        for k in ep: epo[r,k]=(p,p+len(ep)-1)
        p+=len(ep)
anch=set(('I',r) for r in live)|set(('F',r+112) for r in live)
dom={};COV={};UNCOV=[]
for k in nat:
    cand={natS[k]}
    if not isfree(k) or k in anch: dom[k]=[natS[k]]; continue
    own=any(r>=NH for r in partners[k])
    for r in partners[k]:
        l=tl[r];j=pos[r,k];a,b=epo[r,k]
        idx=set()
        for c in (j,a,b):
            for d in range(-K,K+1):
                if 0<=c+d<len(l): idx.add(c+d)
        if b-a>=1: idx|=set(range(max(a,0),min(b,len(l)-1)+1))
        if len(idx)>CAP: idx=set(sorted(idx,key=lambda q:abs(q-j))[:CAP])
        for q in idx: cand.add(natS[l[q]])
    lo=Lset(LB.get(k,0));hi=Uset(UB.get(k,0))
    if not own: cand={s for s in cand if lo<=s<=hi or s==natS[k]}
    cand.add(natS[k])
    if not own and lo<=hi:
        Lbb=LR.basis_of(lo);Ubb=LR.basis_of(hi);m=len(Ubb)-len(Lbb)
        if m<=MAXM: cand|=set(LR.subspaces_between(Lbb,Ubb))
        cand.add(lo);cand.add(hi)
        if k[0]=='E':
            COV[m]=COV.get(m,0)+1
            if m>MAXM: UNCOV.append(k)
    dom[k]=sorted(cand,key=lambda s:(len(s),sorted(s)[:6]))
print('COVERAGE dim(U/L) histogram (free unowned ADD/COPY):',dict(sorted(COV.items())),'| exceeding MAXM=%d: %d'%(MAXM,len(UNCOV)),flush=True)
print('nodes',len(dom),'free',sum(1 for k in dom if len(dom[k])>1),'avg dom %.2f'%(sum(len(v) for v in dom.values())/len(dom)),flush=True)
M=cp_model.CpModel();x={};Dv={}
for k,d in dom.items():
    xs=[]
    for i,S in enumerate(d): x[k,i]=M.NewBoolVar(''); xs.append(x[k,i])
    M.AddExactlyOne(xs)
    dims=[len(S).bit_length()-1 for S in d]
    Dv[k]=M.NewIntVar(min(dims),max(dims),'')
    M.Add(Dv[k]==sum(dm*x[k,i] for i,dm in enumerate(dims)))
tab=[0]+[cwP[d] for d in range(1,10)];obj=[]
nd=lambda k:len(natS[k]).bit_length()-1
HINT=[]     # (var,value) complete hint of the native solution
for k in dom: HINT.append((Dv[k],nd(k)))
def pairs(r,l):
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
        HINT.append((dl,nd(hi)-nd(lo)));HINT.append((c,tab[nd(hi)-nd(lo)]))
nflexfree=0
for r,l in tl.items():
    if r not in flex: pairs(r,l); continue
    if all(len(dom[k])==1 for k in l): pairs(r,l); continue      # fully pinned flex register: order irrelevant
    nflexfree+=1
    # chain variables u[S]
    nat_here={natS[k] for k in l}
    u={}
    for k in l:
        for i,S in enumerate(dom[k]):
            if S not in u: u[S]=M.NewBoolVar('');HINT.append((u[S],int(S in nat_here)))
            M.AddImplication(x[k,i],u[S])
    Ss=list(u)
    usrc=collections.defaultdict(list)
    for k in l:
        for i,S in enumerate(dom[k]): usrc[S].append(x[k,i])
    for S in Ss: M.Add(u[S]<=sum(usrc[S]))
    for a in range(len(Ss)):
        for b in range(a+1,len(Ss)):
            if not(Ss[a]<=Ss[b] or Ss[b]<=Ss[a]): M.AddBoolOr([u[Ss[a]].Not(),u[Ss[b]].Not()])
    # dims monotone across epochs
    prevHi=None
    for E in epochs[r]:
        Hi=M.NewIntVar(0,9,'')
        for k in E:
            M.Add(Dv[k]<=Hi)
            if prevHi is not None: M.Add(Dv[k]>=prevHi)
        prevHi=Hi;HINT.append((Hi,max(nd(k) for k in E)))
    # cost over the set of visited dims
    dset=sorted({len(S).bit_length()-1 for S in Ss});y={}
    vis=sorted({nd(k) for k in l})
    for d in dset:
        y[d]=M.NewBoolVar('');HINT.append((y[d],int(d in vis)))
        for S in Ss:
            if len(S).bit_length()-1==d: M.AddImplication(u[S],y[d])
        M.Add(y[d]<=sum(u[S] for S in Ss if len(S).bit_length()-1==d))
    for ia,d1 in enumerate(dset):
        for ib in range(ia+1,len(dset)):
            d2=dset[ib];pay=M.NewBoolVar('')
            M.Add(pay>=y[d1]+y[d2]-1-sum(y[dd] for dd in dset[ia+1:ib]))
            M.AddImplication(pay,y[d1]);M.AddImplication(pay,y[d2])
            for dd in dset[ia+1:ib]: M.AddImplication(pay,y[dd].Not())
            HINT.append((pay,int(d1 in vis and d2 in vis and not any(dd in vis for dd in dset[ia+1:ib]))))
            obj.append(-cwP[d2-d1]*pay)
print('flex registers with free nodes',nflexfree,flush=True)
tabT=[cwT[d] for d in range(1,10)]
for r in PUB:
    if r in main: continue
    rk=M.NewIntVar(1,9,'');M.Add(rk==Dv[('F',r)]-Dv[('I',r)])
    g=M.NewIntVar(0,max(tabT),'');M.AddElement(rk-1,tabT,g);obj.append(g)
    HINT.append((rk,nd(('F',r))-nd(('I',r))));HINT.append((g,tabT[nd(('F',r))-nd(('I',r))-1]))
for k,d in dom.items():
    if len(d)>1: obj.append(x[k,d.index(natS[k])])      # tie-break: prefer the native frame (<< 1 unit of any priced gap)
M.Maximize(sum(obj))
NW=int(os.environ.get('HEAVY_THREADS','4'))
if os.environ.get('FORCE'):      # diagnostic: force the frames of another word (same scalar program up to commuting) and report what the model cannot represent
    w3=legal.load(os.environ['FORCE']);fr3=legal.spans(w3);key=lambda e:(e[0],e[1],e[2] if e[0] in('ADD','COPY') else None,str(e[-2]) if e[0] in('ADD','COPY','SCALE') else str(e[2:]))
    pool=collections.defaultdict(list)
    for e in w3['program']:
        if e[0]!='MOVE': pool[key(e)].append(fr3[e[-1]] if e[0] in('ADD','COPY','SCALE') else fr3[e[2]])
    miss=0;forced=0
    for i,e in enumerate(prog):
        if e[0] in('ADD','COPY'):
            F=pool[key(e)].pop(0);k=('E',i)
            if F in dom[k]: M.Add(x[k,dom[k].index(F)]==1);forced+=1
            else: miss+=1;print('FORCE missing candidate for',i,e,'dim',len(F).bit_length()-1,'native dim',nd(k),'lo<=F',Lset(LB[k])<=F,'F<=hi',F<=Uset(UB[k]),flush=True)
    for r in PUB:
        for k,F in((('I',r),fr3[w3['initial'][r]]),(('F',r),fr3[w3['final'][r]])):
            if F in dom[k]: M.Add(x[k,dom[k].index(F)]==1)
            elif F!=natS[k]: miss+=1;print('FORCE missing',k,'dim',len(F).bit_length()-1,flush=True)
    print('FORCE forced',forced,'missing',miss,flush=True)
M.ClearHints()
for k,d in dom.items():
    for i_ in range(len(d)): M.AddHint(x[k,i_],int(i_==d.index(natS[k])))
for v_,val_ in HINT: M.AddHint(v_,val_)
NATOBJ=linwt.native_objective(M) if not os.environ.get('NOSOLVE') else None      # RETIMEGAP (includes the +1/native tie-breaks)
items=[i for i,e in enumerate(prog) if e[0]!='MOVE']
def build_order(chosen):
    """returns (neworder or None, list of cycles; each cycle = list of flipped (a,b) epoch edges)"""
    dimc=lambda k:len(chosen[k]).bit_length()-1
    succ=collections.defaultdict(set);indeg=collections.Counter();why={}
    def edge(a,b,r):
        if a==b or b in succ[a]: return
        succ[a].add(b);indeg[b]+=1;why[a,b]=r
    for r,l in seq.items():
        ep=[];last=None
        for kd,it in l:
            if kd!='B' and ep and last==kd: ep[-1].append(it)
            else: ep.append([it])
            last=kd
        order=[]
        for E in ep:
            order+=sorted(E,key=lambda it:((dimc(it) if (it in chosen and r in flex) else 0),it[1]))
        ids=[it[1] for it in order if it[0] in('E','S')]
        for a,b in zip(ids,ids[1:]): edge(a,b,r)
    cycles=[]
    for rounds in range(200):
        ind=collections.Counter(indeg);h=[i for i in items if ind[i]==0];heapq.heapify(h);no=[]
        while h:
            i=heapq.heappop(h);no.append(i)
            for j in succ[i]:
                ind[j]-=1
                if ind[j]==0: heapq.heappush(h,j)
        if len(no)==len(items): return (no if not cycles else None),cycles
        rem={i for i in items if ind[i]>0};pred=collections.defaultdict(list)
        for a_ in rem:
            for b_ in succ[a_]:
                if b_ in rem: pred[b_].append(a_)
        cur_=min(rem);seen=[]
        while cur_ not in seen:
            seen.append(cur_);cur_=pred[cur_][0]
        cyc=seen[seen.index(cur_):][::-1]
        edges=list(zip(cyc,cyc[1:]+cyc[:1]))
        flipped=[(a,b) for a,b in edges if a>b]
        cycles.append(flipped)
        a,b=flipped[0] if flipped else edges[0]      # break one edge and look for further cycles
        succ[a].discard(b);indeg[b]-=1
    return None,cycles
cutz={}
def add_cut(flipped):
    zs=[]
    for a,b in flipped:
        if (a,b) not in cutz:
            z=M.NewBoolVar('');M.Add(Dv[('E',a)]>=Dv[('E',b)]).OnlyEnforceIf(z);cutz[a,b]=z
        zs.append(cutz[a,b])
    M.AddBoolOr(zs)
neworder=None;ncut=0
for it_ in range(int(os.environ.get('REORDER_ITERS','25'))):
    S_=cp_model.CpSolver();S_.parameters.max_time_in_seconds=TL;S_.parameters.num_workers=NW
    st=S_.Solve(M) if not os.environ.get('NOSOLVE') else cp_model.OPTIMAL
    if not os.environ.get('NOSOLVE'): print('iter',it_,S_.StatusName(st),'obj',S_.ObjectiveValue(),'bound',S_.BestObjectiveBound(),'cuts',ncut,flush=True)
    if st not in(cp_model.OPTIMAL,cp_model.FEASIBLE): sys.exit()
    if os.environ.get('DBGALL'):
        def rc(r,ch):
            l=tl[r];ds=[len(ch[k]).bit_length()-1 for k in l]
            if r in flex:
                v=sorted(set(ds));return sum(tab[b-a] for a,b in zip(v,v[1:]))
            return sum(tab[abs(b-a)] if r<NH else tab[abs(b-a)] for a,b in zip(ds,ds[1:]))
        ch2={k:next(dom[k][i] for i in range(len(dom[k])) if S_.BooleanValue(x[k,i])) for k in dom}
        dif=[(rc(r,natS)-rc(r,ch2),r) for r in tl];dif.sort();print('DBGALL worst',dif[:5],'best',dif[-5:],'sum',sum(d for d,_ in dif),flush=True)
    if os.environ.get('DBG'):
        rr=int(os.environ['DBG']);print('DBG tl',[(k,len(dom[k]),[len(S).bit_length()-1 for S in dom[k]],[len(S).bit_length()-1 for S in [dom[k][i] for i in range(len(dom[k])) if S_.BooleanValue(x[k,i])]]) for k in tl[rr]][:12],'flex',rr in flex,flush=True)
    chosen=dict(natS) if os.environ.get('NOSOLVE') else {k:next(dom[k][i] for i in range(len(dom[k])) if S_.BooleanValue(x[k,i])) for k in dom}
    neworder,cycles=build_order(chosen)
    if neworder is not None: break
    if not cycles or any(not c for c in cycles): print('REJECT: cyclic precedence with no flipped edge (bug)',flush=True);sys.exit()
    for c in cycles: add_cut(c);ncut+=1
    M.ClearHints()
    for k,d in dom.items():
        for i_ in range(len(d)): M.AddHint(x[k,i_],int(i_==d.index(natS[k])))
    for v_,val_ in HINT: M.AddHint(v_,val_)
if neworder is None: print('REJECT: cyclic precedence after cuts',flush=True);sys.exit()
moved=sum(1 for a,b in zip(neworder,items) if a!=b)
print('events at a new position:',moved,'cuts',ncut,flush=True)
# ---------- realise
w2=json.loads(json.dumps(w));ftab={frozenset(fr[i]):i for i in range(len(fr))}
def sorted_basis(S):
    b=[];sp={0}
    for v in sorted(S):
        if v not in sp: b.append(v); sp|={x^v for x in sp}
    return b
def fid(S):
    if S not in ftab: w2['frames'].append(sorted_basis(S)); ftab[S]=len(w2['frames'])-1
    return ftab[S]
cur={};newp=[]
for r in PUB: cur[r]=chosen[('I',r)]
def need_move(r,target):
    if cur.get(r) is not None and cur[r]!=target:
        newp.append(['MOVE',_back.get(r,r),fid(cur[r]),fid(target),r>=NH])
    cur[r]=target
for i in neworder:
    e=list(prog[i]);op,r=e[0],e[1]
    if op=='INIT': cur[r]=chosen[('E',i)]; e[2]=fid(cur[r]); newp.append(unmap(e))
    elif op=='CLEAR': need_move(r,chosen[('E',i)]); e[2]=fid(chosen[('E',i)]); newp.append(unmap(e)); cur[r]=None
    elif op in('ADD','COPY'):
        F=chosen[('E',i)]; need_move(r,F); need_move(e[2],F); e[-1]=fid(F); newp.append(unmap(e))
    else:
        e[-1]=fid(cur[r]); newp.append(unmap(e))
for r in PUB: need_move(r,chosen[('F',r)])
w2['program']=newp
w2['initial']=[w['initial'][r] if r in RET else fid(chosen[('I',r)]) for r in range(NH)]
w2['final']=[w['final'][r] if r in RET else fid(chosen[('F',r)]) for r in range(NH)]
json.dump(w2,gzip.open(outp,'wt'))
rep2=legal.check(w2);print('REALISED legal',rep2['ok'],rep2['violations'][:3],flush=True)
if rep2['ok']:
    T2,P2=X.invoice(rep2);print('EXACT kappa %.15f base %.15f gain %.3e'%(X.kappa(T2,P2),k0,X.kappa(T2,P2)-k0),'side',tkcommon.side_of(T2,P2,legal_pr)['ok'])
    if NATOBJ is not None:
        tie=sum(S_.Value(x[k,d.index(natS[k])])-1 for k,d in dom.items() if len(d)>1)      # tie-break terms: native=1 each -> remove from the model gain
        print('MODELGAP model_gain %.4e exact_gain %.4e diff %.3e'%((S_.ObjectiveValue()-NATOBJ-tie)/1e16,X.kappa(T2,P2)-k0,(S_.ObjectiveValue()-NATOBJ-tie)/1e16-(X.kappa(T2,P2)-k0)),flush=True)
    print('paid',{d:rep2['paid'].get(d,0) for d in range(1,10)},'help',rep2['helpers'],'events',len(newp),flush=True)
