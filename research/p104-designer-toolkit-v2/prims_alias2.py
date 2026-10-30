"""prims_alias2 -- P15 SRCREORDER: helper alias JOINTLY with re-ordering of the reader's source reads (SRCREORDER.

P14 (alias_core) redirects a victim helper's reads to a keeper of equal X-content but tests ONE absolute time slot tau for both the keeper's window and the reader's chain.
Frames and values only see per-register CHAIN order, so here the redirected read N (reader d2 += keeper h1) is inserted at any slot q of the keeper's chain inside its content window
and any slot p of the reader's write group that held the old read (writes commute; kid reads and other source reads of the reader keep their chain place; X picks / hub reads of the
reader are moved in absolute time by the linear extension).  N is the only new edge, so the exact vector-clock test is
    (forb(anc(h1@q)) & desc(d2@p)) == 0   and   (forb(anc(d2@p)) & desc(h1@q)) == 0        (forb(A) = OR over lower anchors a in A of ~allowed[a])
with clocks of the program MINUS the victim.  A linear extension (Kahn) exists iff the slot edges close no cycle.  The built program is re-checked by the full Poset, frames are re-planned by
alias_core.closure (hybrid), junk re-solved exactly by alias_core.solve_junk, indices re-packed (alias_core.relabel); exact M.evaluate is the judge.
API:  Work(w) / Work(base=Wk,S=S2)          analysis state of a program
      plan_victim(Wk,h)  -> (per read: sorted candidate combos (h1,q,p,sc1,score), Slots) or None
      try_victim(Wk,h)   -> (S2, removed) or None            (all reads redirected, exact poset-feasible, closure-feasible)
      run(w,...)         -> (word, removed, accepted)        greedy passes + realise
      sites(w) / apply(w,ss) / level(w,tl,log)               pscreen hooks ('alias2')
"""
import sys,os,copy,heapq,collections,time,json,gzip
import alias_core as A
import movekit as M
from fractions import Fraction as F
from bisect import bisect_left
qs=M.qs
STAT=collections.Counter()

def info_S(I,S):
    """shallow copy of Info I with the program replaced by S (roles/dims/frames unchanged); dirty reads recomputed"""
    J=copy.copy(I); J.S=S; role,dim,n=I.role,I.dim,I.n
    val=[None]*(n+64)
    for r in range(n): val[r]={r:F(1)}
    for r in range(n,n+64): val[r]={}
    dirty=collections.defaultdict(list); xread=collections.defaultdict(set)
    for i,e in enumerate(S):
        if e[0]=='ADD':
            d,t,c,f=e[1],e[2],F(e[3]),e[4]; vs=val[t]
            if role.get(t)=='H':
                if any(role.get(k)!='H' for k in vs): xread[t].add(i)
            if role.get(t)=='H' and 0<dim[f]<=9:
                xs={k:x for k,x in vs.items() if role.get(k)!='H'}
                if xs:
                    k0=min(xs); sc=xs[k0]
                    dirty[tuple(sorted((k,x/sc) for k,x in xs.items()))].append((i,d,t,c,f,sc))
            vd=val[d]
            for k,x in vs.items():
                nx=vd.get(k,0)+c*x
                if nx==0: vd.pop(k,None)
                else: vd[k]=nx
        elif e[0] in('INIT','CLEAR'): val[e[1]]={}
    J.dirty=dirty; J.xread=xread
    return J
def info_light(I,S):
    J=copy.copy(I); J.S=S; return J

class Work:
    """analysis state of a program over the fixed register roles of a word (Work(w) or Work(base=other,S=program))"""
    def __init__(s,w=None,S=None,base=None):
        if base is None:
            s.C=A.Ctx(M.pin(w)); s.w=s.C.w; s.I=info_S(s.C.I,s.C.I.S)
        else:
            s.C=base.C; s.w=base.w; s.I=info_S(base.I,S)
        s.n=s.I.n; s.own=s.I.v.own; s.S=s.I.S
        s.T=A.TL(s.I); s.win=A.windows(s.I); s.P=A.Poset(s.I)
        s.rd={}
        for key,L in s.I.dirty.items():
            for (i,d,t,c,f,sc) in L: s.rd[i]=(key,d,t,F(c),f,sc)
        s.byh=collections.defaultdict(list)
        for i,(key,d,t,c,f,sc) in s.rd.items(): s.byh[t].append(i)
    def feasible(s):
        P=s.P
        return not any(e[0]=='ADD' and P.bad(P.anc[i],P.desc[i]) for i,e in enumerate(s.S))

def poset_ok(I,S):
    P=A.Poset(info_light(I,S))
    return not any(e[0]=='ADD' and P.bad(P.anc[i],P.desc[i]) for i,e in enumerate(S))

class Slots:
    """clock tables of the program minus a victim: forb/desc at every chain slot"""
    def __init__(s,Wk,h):
        S=Wk.S; s.Wk=Wk; I=Wk.I
        s.keep=[k for k,e in enumerate(S) if not ((e[0] in('ADD','COPY') and (e[1]==h or e[2]==h)) or (e[0] in('INIT','CLEAR','SCALE') and e[1]==h))]
        s.S_b=[S[k] for k in s.keep]; s.op=s.keep
        J=info_light(I,s.S_b); s.P=A.Poset(J); s.T=A.TL(J)
        s.chains={r:[j for j,_ in L] for r,L in s.T.t.items()}
        s.chop={r:[s.op[j] for j in L] for r,L in s.chains.items()}
        s._fc={}
    def forb(s,A_):
        f=s._fc.get(A_)
        if f is None:
            f=0;x=A_; al=s.P.allowed
            while x:
                lb=x&-x; f|=~al[lb.bit_length()-1]; x^=lb
            s._fc[A_]=f
        return f
    def anc(s,r,k):
        L=s.chains.get(r,[]); P=s.P
        return P.anc[L[k-1]] if k>0 else ((1<<P.xi[r]) if r in P.xi else 0)
    def desc(s,r,k):
        L=s.chains.get(r,[]); P=s.P
        return P.desc[L[k]] if k<len(L) else ((1<<P.yi[r]) if r in P.yi else 0)

def plan_victim(Wk,h,top=8):
    """per dirty read of h: up to `top` best candidate combos (h1,q,p,sc1,score) passing the exact cross-term test (acyclicity not yet checked); None if some read has none"""
    I=Wk.I; own=Wk.own; reads=sorted(Wk.byh[h])
    if not reads: return None
    if len(Wk.w['frames'][Wk.w['initial'][h]])!=0: return None       # helper with a non-trivial initial value: its junk cannot be re-solved at the head
    if not I.xread[h]<=set(reads): return None                         # some other read (dim 0 or > 9) of the victim carries X content
    for i2 in reads:
        d2=Wk.rd[i2][1]
        if d2 in own or d2==h or I.role.get(d2) not in('H','Y'): return None
    sl=Slots(Wk,h); S_b=sl.S_b; out=[]
    readers={Wk.rd[i][1] for i in reads}      # a reader of the victim cannot be a keeper (its window content was built from the victim)
    for i2 in reads:
        key,d2,t,c,f2,sc2=Wk.rd[i2]
        L=sl.chains.get(d2,[]); chd=sl.chop.get(d2,[]); kk=bisect_left(chd,i2)
        isw=lambda j: S_b[j][0]=='ADD' and S_b[j][1]==d2
        kl=kk
        while kl>0 and isw(L[kl-1]): kl-=1
        kr=kk
        while kr<len(L) and isw(L[kr]): kr+=1
        ds=[(p,sl.forb(sl.anc(d2,p)),sl.desc(d2,p)) for p in range(kl,kr+1)]
        best={}
        for (h1,i0,i1,sc1) in Wk.win[key]:
            if h1==h or h1==d2 or h1 in readers: continue
            op1=sl.chop.get(h1,[]); k0=bisect_left(op1,i0); k1=bisect_left(op1,i1)
            for q in range(k0+1,k1+1):
                fH=sl.forb(sl.anc(h1,q)); dH=sl.desc(h1,q)
                tq=op1[q-1]
                for (p,fD,dD) in ds:
                    if (fH&dD) or (fD&dH): continue
                    tp=chd[p] if p<len(chd) else i2
                    sc=abs(tq-tp)
                    cur=best.get(h1)
                    if cur is None or sc<cur[4]: best[h1]=(h1,q,p,sc1,sc)
        if not best: return None
        out.append((i2,d2,c,f2,sc2,sorted(best.values(),key=lambda x:x[4])[:top]))
    return out,sl

def build(Wk,h,sl,plan,choice):
    """program with the victim removed and one N per read inserted at the chosen chain slots; Kahn linear extension (key = old position); None on a cycle"""
    S_b=sl.S_b; m=len(S_b); ev=[list(e) for e in S_b]; nn=len(plan)
    chains={r:list(L) for r,L in sl.chains.items()}
    ins=collections.defaultdict(list); newkey=[]
    for j,((i2,d2,c,f2,sc2,_),ch) in enumerate(zip(plan,choice)):
        h1,q,p,sc1,_s=ch; x=m+j
        ev.append(['ADD',d2,h1,qs(c*sc2/sc1),f2]); newkey.append(float(i2))
        ins[(h1,q)].append(x); ins[(d2,p)].append(x)
    for (r,k),xs in sorted(ins.items(),key=lambda t:-t[0][1]):
        chains.setdefault(r,[])[k:k]=xs
    tot=m+nn; succ=[[] for _ in range(tot)]; indeg=[0]*tot
    for r,L in chains.items():
        for a,b in zip(L,L[1:]):
            if a!=b: succ[a].append(b); indeg[b]+=1
    key=[float(o) for o in sl.op]+newkey
    hp=[(key[x],x) for x in range(tot) if indeg[x]==0]; heapq.heapify(hp); out=[]
    while hp:
        _,x=heapq.heappop(hp); out.append(x)
        for y in succ[x]:
            indeg[y]-=1
            if indeg[y]==0: heapq.heappush(hp,(key[y],y))
    if len(out)<tot: return None
    return [ev[x] for x in out]

TOP=int(os.environ.get('P15_TOP','8')); MAXTRY=int(os.environ.get('P15_MAXTRY','24'))
def try_victim(Wk,h,top=None,maxtry=None,closure=True):
    top=top or TOP; maxtry=maxtry or MAXTRY
    r=plan_victim(Wk,h,top)
    if r is None: STAT['noplan']+=1; return None
    plan,sl=r; I=Wk.I
    first=[x[5][0] for x in plan]; plans=[first]
    for j in range(len(plan)):
        for alt in plan[j][5][1:]: p=list(first); p[j]=alt; plans.append(p)
    for pl in plans[:maxtry]:
        S2=build(Wk,h,sl,plan,pl)
        if S2 is None: STAT['cycle']+=1; continue
        S2,removed=A.dce(S2,I.role,I.n); removed=set(removed)|{h}
        if not poset_ok(I,S2): STAT['poset']+=1; continue
        if closure:
            cl=A.closure(Wk.C,S2,removed,'hybrid')
            if isinstance(cl,str): STAT['closure']+=1; continue
            if not xcols_ok(Wk,S2): STAT['VALUE']+=1; continue
        STAT['ok']+=1; return S2,removed
    return None

def xcols_ok(Wk,S):
    """the X-part (non-helper columns) of every final row equals the target's (junk = helper columns is re-solved later, X content must be exact)"""
    I=Wk.I; n=I.n; role=I.role
    V=A.simulate(S,n,n+Wk.w.get('owned_fields',8)+8); T=A.target(Wk.w)
    for r in range(n):
        a={k:x for k,x in V[r].items() if role.get(k)!='H'}; b={k:x for k,x in T[r].items() if role.get(k)!='H'}
        if a!=b: return False
    return True

def realise2(C,S2,removed,junk=True):
    """alias_core.realise from an already edited program"""
    I=C.I; w=C.w; n=I.n
    cl=A.closure(C,S2,removed,'hybrid')
    if isinstance(cl,str): return None,'closure:'+cl.split()[0]
    spans,fin,ini0=cl
    mp,nn=A.relabel(C,removed)
    frames=[list(b) for b in w['frames']]; fidx={x:i for i,x in enumerate(I.sp)}
    def fid(span):
        i=fidx.get(span)
        if i is None: frames.append(A.basis_of(span)); i=len(frames)-1; fidx[span]=i
        return i
    S3=[]
    for e,spn in zip(S2,spans):
        e=list(e); f=fid(spn)
        if e[0]=='INIT': e=['INIT',mp[e[1]],f]
        elif e[0]=='CLEAR': e=['CLEAR',mp[e[1]],f]
        elif e[0] in('ADD','COPY'): e=[e[0],mp[e[1]],mp[e[2]],e[3],f]
        else: e=[e[0],mp[e[1]]]+e[2:-1]+[f]
        S3.append(e)
    ini=[None]*nn; fn=[None]*nn
    for r in range(n):
        if r in removed: continue
        ini[mp[r]]=fid(ini0[r]); fn[mp[r]]=fid(fin[r])
    w2=dict(w); w2['frames']=frames; w2['initial']=ini; w2['final']=fn
    vp=dict(w.get('verifier_profile') or {}); vp['public']=nn; w2['verifier_profile']=vp
    w2['live']=[mp[r] for r in w['live']]
    if w2['live']!=w['live']: return None,'live relabel'
    if junk:
        r=A.solve_junk(w2,S3,nn)
        if isinstance(r,str): return None,'junk:'+r
        S3=r
    return M.View(w2).rebuild_ref(S3),'ok'

def run(w,tl=240,log=print,maxacc=10**9,order=None,maxpass=3,state=None,judge=(os.environ.get('P15_JUDGE','1')=='1'),mingain=0.0):
    """greedy: scan victims, accept every poset/closure/value-feasible one whose EXACT kappa (realise2 + M.evaluate of the cumulative state) does not drop by more than -mingain
    (judge=False: no per-accept pricing, final word priced once).  Returns (word or None, removed set, accepted list)"""
    t0=time.time(); w=M.pin(w)
    Wk=state or Work(w); C=Wk.C; removed=set(); acc=[]; kcur=C.k0; wbest=None
    for ps in range(maxpass):
        hs=order(Wk) if order else sorted(Wk.byh,key=lambda h:(len(Wk.byh[h]),h))
        nacc=0; tried=0
        for h in hs:
            if time.time()-t0>tl or len(acc)>=maxacc: break
            if h in removed or h not in Wk.byh: continue
            tried+=1
            r=try_victim(Wk,h)
            if r is None: continue
            S2,rem=r
            if judge:
                w3,why=realise2(C,S2,removed|rem)
                if w3 is None: STAT['realise-fail']+=1; continue
                o=M.evaluate(w3)
                if not o.get('legal') or o['kappa']<=kcur+mingain: STAT['kappa-']+=1; continue
                kcur=o['kappa']; wbest=w3
            removed|=rem; acc.append(h); nacc+=1
            Wk=Work(base=Wk,S=S2)
            if len(acc)%25==0: log('  accepted',len(acc),'tried',tried,'%.0fs'%(time.time()-t0),'kappa %.10f'%kcur,dict(STAT))
        log('pass',ps,'accepted',nacc,'total',len(acc),'%.0fs'%(time.time()-t0))
        if nacc==0 or time.time()-t0>tl or len(acc)>=maxacc: break
    if not acc: return None,removed,acc
    if judge: return wbest,removed,acc
    w3,why=realise2(C,Wk.S,removed)
    if w3 is None: log('realise failed',why); return None,removed,acc
    return w3,removed,acc

# ---- pscreen / tk hooks (set 'alias2')
def base(w):
    """the word re-realised with hybrid frames and no edit (identity edit reproduces the original kappa exactly)"""
    import prims_alias as PA
    return PA.base(w)
def sites(w,maxn=10**9):
    """candidate victims: helpers all of whose dirty reads have an exact-feasible (keeper, slot, slot) combo"""
    Wk=Work(M.pin(w)); out=[]
    for h in sorted(Wk.byh):
        r=plan_victim(Wk,h,top=1)
        if r is not None: out.append(dict(prim='P15',victim=h,keepers=[x[5][0][0] for x in r[0]]))
        if len(out)>=maxn: break
    return out
def apply(w,ss,tl=3600):
    """redirect the victims named in ss (greedily, state carried; infeasible ones are skipped); returns the new word or None"""
    vs={s['victim'] for s in ss}; Wk=Work(M.pin(w))
    w3,rem,acc=run(w,tl=tl,order=lambda W:[h for h in sorted(W.byh) if h in vs],maxpass=2,state=Wk,log=lambda *a:None)
    return w3
def level(w,tl=300,log=print,batch=10**9):
    """pscreen level: one greedy sweep (all poset/closure-feasible victims), exact M.evaluate is the judge"""
    w3,rem,acc=run(w,tl=tl*0.8,maxacc=batch,maxpass=2,log=log)
    if w3 is None: return []
    o=M.evaluate(w3)
    return [(o['kappa'],w3,dict(prim='P15',removed=len(acc)))] if o.get('legal') else []
