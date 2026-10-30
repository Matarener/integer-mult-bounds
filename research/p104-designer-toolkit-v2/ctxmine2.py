"""ctxmine2 -- CTXMINE2: ctxmine's real-context window closure + the moves CTXMINE did not cover (CTXMINE2.
New move kinds (all generated on the REAL word, guards lifted, every kept node value-checked):
  CJ  P3 conjugation INSIDE the closure: T=I+q E_ab around a span of 1-3 events of the window (prims.p3_apply with pub lifted: owned operands allowed); root nodes only (cost)
  RD  read redirect: an ADD/COPY source s is replaced by another register s' holding the EQUAL VALUE at that time (numeric check on a random-input replay of the real prefix, mod 2^61-1; improving
      nodes are re-proved exactly by movekit.evaluate in the scan driver)
  CS  coefficient split: ADD(t,s,c) -> ADD(t,s,c-d);ADD(t,s,d) (d in c/2, +-1; the +-2 -> 1+1 and dyadic cases)
  CM  coefficient merge: adjacent ADD(t,s,a);ADD(t,s,b) -> ADD(t,s,a+b)  (the reverse; dropped when a+b=0)
plus all of ctxmine's H/T/SH/CC.  API: search2(v,num,lo,hi,...), Num(v.S,v.n).  Never sets env at import."""
import time,random,collections
from fractions import Fraction as Q
import movekit as M
from movekit import qs
import prims, ctxmine as CM
from prims import Block
P=(1<<61)-1
_mc={}
def modq(x):
    r=_mc.get(x)
    if r is None:
        q=Q(x); r=q.numerator%P*pow(q.denominator,-1,P)%P; _mc[x]=r
    return r
def step(st,e,dead=None):
    op=e[0]; r=e[1]
    if op=='ADD': st[r]=(st.get(r,0)+modq(e[3])*st.get(e[2],0))%P
    elif op=='COPY': st[r]=st.get(e[2],0)
    elif op=='SCALE': st[r]=st.get(r,0)*modq(e[2])%P
    elif op=='INIT': st[r]=0
    elif dead is not None: dead.add(r)
class Num:
    """random-input replay of the real word S with checkpoints every `stride` events: equal-valued registers <=> equal linear forms (whp)"""
    def __init__(s,S,n,stride=128,seed=7):
        rnd=random.Random(seed); s.n=n; s.stride=stride; st={r:rnd.randrange(1,P) for r in range(n)}; s.cps=[]
        for k,e in enumerate(S):
            if k%stride==0: s.cps.append(dict(st))
            step(st,e)
    def state(s,S,c):
        k0=c//s.stride*s.stride; st=dict(s.cps[k0//s.stride])
        for k in range(k0,c): step(st,S[k])
        return st
def num_equiv(num,Sa,Sb):
    n=min(len(Sa),len(Sb)); p=0
    while p<n and Sa[p]==Sb[p]: p+=1
    q=0
    while q<n-p and Sa[len(Sa)-1-q]==Sb[len(Sb)-1-q]: q+=1
    st=num.state(Sa,p); a=dict(st); b=dict(st); dead=set(); regs=set()
    for e in Sa[p:len(Sa)-q]: step(a,e,dead); regs.add(e[1]); regs.add(e[2]) if e[0] in('ADD','COPY') else 0
    for e in Sb[p:len(Sb)-q]: step(b,e,dead); regs.add(e[1]); regs.add(e[2]) if e[0] in('ADD','COPY') else 0
    return all(a.get(r,0)==b.get(r,0) for r in regs if r not in dead)

def _fr(e): return e[-1]
def children2(S,lo,hi,pub,num,kinds=('RD','CS','CM','CJ'),fmax=2):
    """yield (desc,S2,(lo2,hi2),tags) for the new move kinds"""
    n=len(S); hi=min(hi,n)
    if 'RD' in kinds:
        st=num.state(S,lo); rev=collections.defaultdict(set)
        for r,x in st.items():
            if x: rev[x].add(r)
        for i in range(lo,hi):
            e=S[i]
            if e[0] in('ADD','COPY'):
                sv=st.get(e[2],0)
                if sv:
                    for s2 in sorted(rev[sv]-{e[2],e[1]})[:6]:
                        yield ('RD',i,e[2],s2),S[:i]+[e[:2]+[s2]+e[3:]]+S[i+1:],(lo,hi),{'RD','LIFT'}
            old=st.get(e[1],0); step(st,e)
            if e[0] in('ADD','COPY','SCALE','INIT'):
                new=st.get(e[1],0)
                if old!=new:
                    if old: rev[old].discard(e[1])
                    if new: rev[new].add(e[1])
    for i in range(lo,hi):
        e=S[i]
        if e[0]!='ADD': continue
        t,s,c,f=e[1],e[2],Q(e[3]),e[4]
        if 'CS' in kinds:
            ds={c/2,Q(1),Q(-1)}-{0,c}
            fs=[f]+[x for x in CM.near_frames(S,i,[t,s])[:fmax] if x!=f]
            for d in sorted(ds):
                for f2 in fs:
                    yield ('CS',i,str(d),f2),S[:i]+[['ADD',t,s,qs(c-d),f],['ADD',t,s,qs(d),f2]]+S[i+1:],(lo,hi+1),{'CS','LIFT'}
        if 'CM' in kinds and i+1<hi and S[i+1][0]=='ADD' and S[i+1][1]==t and S[i+1][2]==s:
            c2=c+Q(S[i+1][3]); 
            for f2 in {f,S[i+1][4]}:
                mid=[] if c2==0 else [['ADD',t,s,qs(c2),f2]]
                yield ('CM',i,f2),S[:i]+mid+S[i+2:],(lo,hi-2+len(mid)),{'CM','LIFT'}
    if 'CJ' in kinds:
        R=[]
        for k in range(max(0,lo-1),min(n,hi+1)):
            for r in (S[k][1:3] if S[k][0] in('ADD','COPY') else S[k][1:2]):
                if isinstance(r,int) and r not in R: R.append(r)
        seen=set()
        for i0 in range(lo,hi):
            for ln in (1,2):
                i1=i0+ln-1
                if i1>=hi: break
                span=S[i0:i1+1]
                if any(x[0] in('INIT','CLEAR') for x in span): break
                for e in span:
                    if e[0]!='ADD': continue
                    u,v,c=e[1],e[2],Q(e[3])
                    qs_=sorted({Q(1),Q(-1),c,-c})
                    cands=[(a,u) for a in R if a!=u and a!=v]+[(v,b) for b in R if b!=v and b!=u]
                    for (a,b) in cands:
                        for q in qs_:
                            key=(i0,i1,a,b,q)
                            if key in seen: continue
                            seen.add(key)
                            try: S2=prims.p3_apply(S,i0,i1,a,b,q,S[i0][-1],S[i1][-1],10**9)
                            except (Block,ValueError,KeyError,IndexError,ZeroDivisionError): continue
                            if len(S2)-len(S)>4: continue
                            yield ('CJ',i0,i1,a,b,str(q)),S2,(lo,hi+len(S2)-len(S)),{'CJ','LIFT'}

def search2(v,num,lo,hi,depth=3,tol=1e-5,beam=100,k0=None,log=None,tl=60,fmax=3,D=5,kinds=('H','T','SH','CC'),kinds2=('RD','CS','CM','CJ'),stats=None,eps=1e-15,rec_per=None):
    """like ctxmine.search with the extra kinds; CJ only from the root.  -> improving nodes best first.  stats counts children per move kind."""
    S0=v.S; pub=v.n; t0=time.time()
    k0=k0 if k0 is not None else M.quick(v,S0)[0]
    seen={CM._key(S0,lo,hi)}; front=[(k0,S0,(lo,hi),(),frozenset())]; found=[]; cnt=collections.Counter()
    for d in range(1,depth+1):
        nxt=[]
        for (k,S,(l,h),path,tags) in front:
            k2s=tuple(x for x in kinds2 if x!='CJ' or d==1)
            gens=[CM.children(S,l,h,pub,D=D,fmax=fmax,kinds=kinds),children2(S,l,h,pub,num,kinds=k2s)]
            for gen in gens:
                for desc,S2,(l2,h2),tg in gen:
                    if time.time()-t0>tl: break
                    key=CM._key(S2,l2,h2)
                    if key in seen: continue
                    seen.add(key); kd=desc[0]; cnt['children']+=1; cnt['c_'+kd]+=1
                    try: k2,_=M.quick(v,S2)
                    except Exception: k2=None
                    if k2 is None: cnt['illegal']+=1; continue
                    cnt['legal']+=1; cnt['l_'+kd]+=1
                    tags2=tags|frozenset(tg)
                    ok=CM.equiv(S0,S2) or ('RD' in tags2 and num_equiv(num,S0,S2))
                    if not ok: cnt['NOTEQUIV']+=1; continue
                    path2=path+(desc,)
                    if k2>k0+eps: found.append(dict(kappa=k2,gain=k2-k0,path=path2,tags=sorted(tags2),lo=l2,hi=h2,S=S2))
                    if k2>=k0-tol: nxt.append((k2,S2,(l2,h2),path2,tags2))
        nxt.sort(key=lambda x:-x[0]); front=nxt[:beam]
        if log: log('   depth %d: legal %d, frontier %d, improving %d [%.1fs]'%(d,cnt['legal'],len(front),len(found),time.time()-t0))
        if time.time()-t0>tl or not front: break
    found.sort(key=lambda x:-x['gain'])
    if stats is not None: stats.update(cnt)
    return found
