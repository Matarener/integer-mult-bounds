"""synth.sharedsum -- SHAREDSUM lane (see ../module docstring).  Scope [toolkit synth, emergent sharing via linear CSE + hash-consing].

frontgen hook `helpers: cse`.  Inputs: demand vectors + frame law + R0 (nothing copied from a swarm word).
  residual + root trees : synth.mainhub plan (MAINHUB_PLAN / data/mainhub_plan.txt), unchanged
  SIGNAL (this module)  : a CSE over the Boolean lattice of roots.  Y_j needs sum_k 2C_jk R_k; R_k exists only on root k's descent (frames inside H_k, all containing l_k),
                          and l_a is in no H_b (a != b), so one chain can meet at most one root: the other roots must be RELAYED.  A relay of root k (helper) reads R_k at <l_k>
                          and climbs through line-span frames F_S = <l_s : s in S>; a collector Z_j (one per Y) climbs F_{S_1} < F_{S_2} < ... (S_t = first t roots of an
                          ordering of T_j = {k : C_jk != 0}) and at F_{S_t} reads the relay of the root that joins there (coefficient 2C_jk: demand-driven read), then Y_j += Z_j at Q_j.
                          A relay is shared by every Z that joins its root at a set on its chain; relay chains = greedy chain cover of the join sets (inclusion + strictly rising dim).
                          The orderings are annealed against the R0 tax (Z chains + relay chains).  Relays are restored by frontgen's T trick (they are 'copies' with cin=1).
plan_signal(...) -> dict(orders, relays=[(k,[S..])]); cached in data/sharedsum_signal.json.  apply(bk, ctx) -> new bk (copies = relays, ysteps without copy reads, hub = mainhub dict + Z).
"""
import os,sys,json,math,random,collections
from fractions import Fraction as Fr
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,os.path.dirname(HERE))
SIGDATA=os.path.join(HERE,'data','sharedsum_signal.json')
def _H(r): return r*math.log(r) if r>0 else 0.0
def _rank(vs):
    b=[]
    for v in vs:
        for x in b: v=min(v,v^x)
        if v: b.append(v)
    return len(b)
def tax(ds,top):
    prev=0; t=_H(top)
    for d in ds: t-=_H(d-prev); prev=d
    return t-_H(top-prev)
def _steps(o,cut):
    """Z_j's stops: groups of the ordering o; cut[t]=1 -> Z stops after o[t] (the last position always stops)"""
    g=[]; cur=[]
    for t,k in enumerate(o):
        cur.append(k)
        if t==len(o)-1 or cut[t]: g.append(cur); cur=[]
    return g
def _cost(orders,line,cuts=None):
    dS={}
    def d(S):
        if S not in dS: dS[S]=_rank([line[k] for k in S])
        return dS[S]
    joins=collections.defaultdict(set); ztax=0.0
    for j,o in enumerate(orders):
        S=frozenset(); ds=[]
        for g in _steps(o,cuts[j] if cuts else [1]*len(o)):
            S=S|set(g)
            for k in g: joins[k].add(S)
            if not ds or d(S)>ds[-1]: ds.append(d(S))
        ztax+=tax(ds+[8],9)
    rel=[]; rtax=0.0
    for k in sorted(joins):
        chains=[]
        for S in sorted(joins[k],key=lambda s:(len(s),sorted(s))):
            for c in chains:
                if c[-1]<S and d(c[-1])<d(S): c.append(S); break
            else: chains.append([S])
        for c in chains:
            ds=[1]+[d(S) for S in c if d(S)>1]; rtax+=tax(ds,9); rel.append((k,c))
    return ztax,rtax,rel
def plan_signal(C2,line,seed=1,iters=60000,T0=3.0):
    m=len(C2); rng=random.Random(seed)
    orders=[[k for k in range(len(C2[0])) if C2[j][k]] for j in range(m)]
    for o in orders: rng.shuffle(o)
    cuts=[[1]*len(o) for o in orders]
    cur=_cost(orders,line,cuts); E=lambda c:c[0]+c[1]; Tm=T0; best=(E(cur),[o[:] for o in orders],[c[:] for c in cuts])
    for it in range(iters):
        j=rng.randrange(m); o=orders[j]
        if len(o)<2: continue
        old=o[:]; oc=cuts[j][:]
        if rng.random()<0.6: a,b=rng.sample(range(len(o)),2); o[a],o[b]=o[b],o[a]
        else: t=rng.randrange(len(o)-1); cuts[j][t]^=1
        new=_cost(orders,line,cuts)
        if E(new)<=E(cur) or rng.random()<math.exp((E(cur)-E(new))/Tm):
            cur=new
            if E(cur)<best[0]: best=(E(cur),[o[:] for o in orders],[c[:] for c in cuts])
        else: orders[j]=old; cuts[j]=oc
        Tm=max(0.05,Tm*0.9999)
    orders,cuts=best[1],best[2]; z,r,rel=_cost(orders,line,cuts)
    return dict(orders=orders,cuts=cuts,relays=[(k,[sorted(S) for S in c]) for k,c in rel],ztax=z,rtax=r,seed=seed,iters=iters)
def load_signal(C2,line):
    if os.path.exists(SIGDATA):
        J=json.load(open(SIGDATA))
        if J.get('C2')==C2 and J.get('line')==line: return J
    J=min((plan_signal(C2,line,seed=sd) for sd in (1,2,3)),key=lambda J:J['ztax']+J['rtax']); J['C2']=C2; J['line']=line; json.dump(J,open(SIGDATA,'w')); return J
def apply(bk,ctx):
    from synth import mainhub as MHB
    C2=ctx['C2']; line=ctx['line']; fid=ctx['fid']; Qf=ctx['Qf']; F9=ctx['F9']; m=len(C2)
    hub=MHB.apply(bk,ctx)
    if os.environ.get('SHAREDSUM_SIGNAL','1')=='0':      # control: mainhub + star copies
        b2=dict(bk); b2['rcar']=[]; b2['hub']=hub; return b2
    SG=load_signal(C2,line)
    copies=[]; where={}
    for ri,(k,ch) in enumerate(SG['relays']):
        copies.append(dict(k=k,cin=Fr(1)))
        for S in ch: where[(k,frozenset(S))]=ri
    hubs=list(hub['hubs']); post=[]; prer=[]
    for j,o in enumerate(SG['orders']):
        z=len(hubs); hubs.append(dict(j=j,hid=('Z',j)))
        S=frozenset()
        for g in _steps(o,SG.get('cuts',[[1]*len(x) for x in SG['orders']])[j]):
            S=S|set(g); f=fid([line[s] for s in sorted(S)]); d=_rank([line[s] for s in S])
            for k in g:
                c=Fr(2*C2[j][k])
                post.append(dict(dst=('H',z),src=('C',where[(k,S)]),coef=c,frame=f,dim=d,h=0))
                prer.append(dict(dst=('H',z),src=('C',where[(k,S)]),coef=-c,frame=F9))
        post.append(dict(dst=('Y',j),src=('H',z),coef=Fr(1),frame=Qf[j],dim=8,h=1))
    hub=dict(hub,hubs=hubs,post=post,prerestore=prer)
    info=dict(hub.get('info') or {}); info.update(signal_relays=len(copies),signal_Z=m,model_ztax=SG['ztax'],model_relay_tax=SG['rtax']); hub['info']=info
    b2=dict(bk); b2['rcar']=[]; b2['hub']=hub; b2['copies']=copies; b2['ysteps']={j:[(Qf[j],[],[])] for j in range(m)}
    return b2
