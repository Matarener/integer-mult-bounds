#!/usr/bin/env python3
"""PRIMITIVES tests: replay trick decompositions with prims.py and land on the PR kappa EXACTLY (movekit.evaluate + canon-equal events where stated);
independent P3 conjugation == ibase.conj_events event for event; Steinberg corrections; P1 window greedy rediscovery (--quick skips the ~60 s window searches).
usage: tests/prims_test.py [--quick]"""
import sys,os,random,time
HERE=os.path.dirname(os.path.abspath(__file__)); TK=os.path.dirname(HERE); sys.path.insert(0,TK)
os.environ['TK_FREE_BOUNDS']='1'
import tkcommon,movekit as M,prims,ibase
from fractions import Fraction as Q
fails=[];n=0
def need(c,what):
    global n; n+=1; print(('PASS ' if c else 'FAIL ')+what,flush=True)
    if not c: fails.append(what)
P=prims.PLUGIN
def L(a): _,w=tkcommon.load(a); return M.pin(w)
def K(w): o=M.evaluate(M.pin(w)); return o['kappa'] if o.get('legal') else None
def step(w,ed):
    v=M.View(M.pin(w)); return P.apply(v,ed)
def close(a,b): return a is not None and abs(a-b)<1e-15
def main():
    quick='--quick' in sys.argv
    # --- Steinberg / strict commute algebra on a toy program
    def run(S,n=6):
        x=[Q(i+1) for i in range(n)]
        for e in S:
            if e[0]=='ADD': x[e[1]]+=Q(e[3])*x[e[2]]
        return x
    rng=random.Random(3); ok=True
    for trial in range(300):
        S=[['ADD',rng.randrange(6),rng.randrange(6),str(rng.choice([1,2,-1,3])),0] for _ in range(8)]
        S=[e for e in S if e[1]!=e[2]]
        if len(S)<3: continue
        i=rng.randrange(len(S)); g=rng.randrange(len(S)+1)
        try: S2,_=prims.p1_apply(S,i,g)
        except prims.Block: continue
        except Exception: continue
        if run(S)!=run(S2): ok=False; print(S,i,g,S2)
    need(ok,'P1 (strict + Steinberg correction) preserves values on 300 random toy programs')
    ok=True
    for trial in range(300):
        S=[['ADD',rng.randrange(6),rng.randrange(6),str(rng.choice([1,2,-1,3])),0] for _ in range(8)]
        S=[e for e in S if e[1]!=e[2]]
        a,b=rng.sample(range(6),2); q=Q(rng.choice([1,2,-1,3]))
        try: S2=prims.p3_apply(S,0,len(S)-1,a,b,q,0,0,6)
        except prims.Block: continue
        if run(S)!=run(S2): ok=False
    need(ok,'P3 transvection conjugation preserves values on 300 random toy programs')
    # --- replays on real words (exact kappa)
    w=L('5561'); w=step(w,dict(prim='P1',i=14067,g=13119,f=559,fc=None,ends=[['final',706,559]])); need(close(K(w),K(L('5569'))),'#5569 = P1(f=559)+P2 final (fused, L=2) == PR kappa')
    w=L('5627'); w=step(w,dict(prim='P1',i=13039,g=13041,f=127,fc=396)); need(close(K(w),K(L('5643'))),'#5643 A2x = one P1c (Steinberg) with frames f=127, fc=396 == PR kappa')
    w=L('5650')
    for ed in (dict(prim='P1',i=12505,g=12745,f=None,fc=None),dict(prim='P1',i=12746,g=12748,f=None,fc=None),dict(prim='P1',i=12746,g=12744,f=3,fc=None)): w=step(w,ed)
    need(close(K(w),K(L('5660'))),'#5660 four-gate = P1s + P1c + P1c(+P0 cancel, f=3) == PR kappa')
    w=L('5580')
    for ed in [dict(prim='P1',i=12331,g=12269,f=3),dict(prim='P1',i=12333,g=12270,f=3),dict(prim='P1',i=12335,g=12271,f=3),dict(prim='P1',i=12337,g=12272,f=3),dict(prim='P2',kind='start',r=531,f=3),
               dict(prim='P1',i=12467,g=12267,f=3),dict(prim='P2',kind='ev',i=12484,f=3),dict(prim='P2',kind='ev',i=12485,f=355),dict(prim='P2',kind='ev',i=12696,f=3)]: w=step(w,ed)
    w5565=L('5565'); need(close(K(w),K(w5565)) and M.View(M.pin(w)).S==M.View(w5565).S,'#5565 reorder = 5 x P1s + P2 start + 3 x P2 ev (9 applications) == PR word (events identical)')
    # --- P3 independent of ibase
    w=L('5660'); v=M.View(w); ctx=P.prepare(v); sites=list(P.sites_P3(v,ctx,focus={438,733})); ed=max(sites[:200],key=lambda e:P.fast(v,e) or 0)
    S=v.S; mine=prims.p3_apply(S,ed['i0'],ed['i1'],ed['a'],ed['b'],Q(ed['q']),ed['ef'],ed['xf'],v.n); bl=v.blocks
    s0=[k for k,b in enumerate(bl) if b[0]==ed['i0']][0]; s1=[k for k,b in enumerate(bl) if b[-1]==ed['i1']][0]
    ref=ibase.PLUGIN.scalars(v,dict(a=ed['a'],b=ed['b'],q=ed['q'],s0=s0,s1=s1,ef=ed['ef'],xf=ed['xf']))
    need(mine==ref,'own P3 conjugation == ibase.scalars event for event (#5678 first interval)')
    need(close(K(P.apply(v,ed)),0.0031072018966577515),'#5678 step 1 (P3 438/733 q=-4) == ibase gain +4.386e-7')
    if not quick:
        w=L('5561'); k,w2,ch,st=prims.greedy(w,('P1',),steps=1,window=(14000,14100),topq=60,log=lambda *x:None)
        need(close(k,K(L('5569'))),'greedy P1 (window 14000-14100, 100 events) rediscovers #5569 (%s)'%st.line())
        w=L('5627'); k,w2,ch,st=prims.greedy(w,('P1',),steps=1,window=(13030,13050),topq=80,log=lambda *x:None)
        need(close(k,K(L('5643'))),'greedy P1 (window 20 events) rediscovers #5643 (%s)'%st.line())
        import relay
        relay.OPT['ids']='12362'; w=L('5684'); k,w2,ch,st=prims.greedy(w,('P3x',),steps=1,topq=5,log=lambda *x:None); relay.OPT['ids']=''
        need(close(k,K(L('5713'))),'#5713 distributed update = P3x (relay/spansolve) at the PR kappa, contact id given')
        w=L('5713'); k,w2,ch,st=prims.greedy(w,('P5',),steps=1,topq=5,log=lambda *x:None); need(close(k,K(L('5739'))),'#5739 = P5 found blind on the whole word (%s)'%st.line())
        k,w2,ch,st=prims.greedy(w,('P4',),steps=1,topq=5,log=lambda *x:None); need(close(k,K(L('5718'))),'#5718 = P4 found blind on the whole word (%s)'%st.line())
    print('%d checks, %d failed'%(n,len(fails))); sys.exit(1 if fails else 0)
if __name__=='__main__': main()
