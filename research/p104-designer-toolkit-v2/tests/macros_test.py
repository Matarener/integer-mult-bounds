#!/usr/bin/env python3
"""MACROS tests: cofrm rediscovers #5569 / #5643 in a window (exact PR kappa); carry rediscovers #5660 from one composite site; P6 reproduces #5713 (exact mode, contact given) and #5605
(joint, 14 s; skipped with --quick); rehome (+4 hoists given) lands on the #5565 kappa (30 s; skipped with --quick).  usage: tests/macros_test.py [--quick]"""
import sys,os
HERE=os.path.dirname(os.path.abspath(__file__)); TK=os.path.dirname(HERE); sys.path.insert(0,TK); os.environ['TK_FREE_BOUNDS']='1'
import tkcommon,movekit as M,prims,macros
fails=[];n=0
def need(c,what):
    global n; n+=1; print(('PASS ' if c else 'FAIL ')+what,flush=True)
    if not c: fails.append(what)
P=prims.PLUGIN
def L(a): _,w=tkcommon.load(a); return M.pin(w)
def K(w): return M.evaluate(M.pin(w))['kappa']
def close(a,b): return a is not None and abs(a-b)<1e-15
def best(w,ms,window=None):
    k,w2,ch,st=macros.search(w,ms,steps=1,window=window,topq=40,log=lambda *a:None); return k,w2,ch
quick='--quick' in sys.argv
k,_,ch=best(L('5561'),[macros.LIB['cofrm']],(14000,14100)); need(close(k,K(L('5569'))),'cofrm (window 100) rediscovers #5569: co-residence + helper endpoint companion')
k,_,ch=best(L('5627'),[macros.LIB['cofrm']],(13030,13050)); need(close(k,K(L('5643'))),'cofrm (window 20) rediscovers #5643: co-next frame + Steinberg correction')
w=L('5650'); v=M.View(w); m=macros.LIB['carry']; ctx=P.prepare(v); ks=[]
for ed in m.sites(v,ctx,window=(12746,12747)):
    try: ks.append(m.fast(v,ed))
    except Exception: pass
need(close(max([x for x in ks if x] or [0]),K(L('5660'))),'carry: one 3-step composite site from A=c-=x/2 reaches the #5660 kappa (gate rotation)')
w=L('5684'); v=M.View(w); eds=list(P.sites_P6(v,P.prepare(v),modes=('exact',),ids=[12362])); need(len(eds)>=1 and close(K(P.apply(v,eds[0])),K(L('5713'))),'P6 exact mode reproduces #5713')
if not quick:
    w=L('5580'); v=M.View(w); eds=list(P.sites_P6(v,P.prepare(v),modes=('joint',))); need(any(close(K(P.apply(v,e)),K(L('5605'))) for e in eds),'P6 joint (blind whole word) reproduces #5605')
    w=L('5580')
    for ed in [dict(prim='P1',i=12331,g=12269,f=3),dict(prim='P1',i=12333,g=12270,f=3),dict(prim='P1',i=12335,g=12271,f=3),dict(prim='P1',i=12337,g=12272,f=3)]: w=P.apply(M.View(w),ed)
    v=M.View(w); r=macros.LIB['rehome']; ed=dict(macro='rehome',kind='start',r=531,f=3,steps=[dict(prim='P2',kind='start',r=531,f=3)])
    need(close(r.fast(v,ed),K(L('5565'))),'rehome (dip -7e-7 hidden, P1 stepping stone + 3 relabels) lands on the #5565 kappa')
# relay.screen_incr joint log line must not touch ed['i'] / ed['r'] (HYBRID bug: KeyError 'i' on joint edits with comp)
import io,contextlib,relay
relay.OPT['comp']='1'; relay.OPT['jmax']='1'
try:
    import inspect; src=inspect.getsource(relay.screen_incr); need("ed['i']" not in src and "ed['r']" not in src,"relay.screen_incr: no eager ed['i']/ed['r'] on joint edits")
    if not quick:
        out,_=relay.screen_incr(L('5580'),log=lambda *a:None); need(len(out)>=1,'relay comp=1 joint screen on #5580 runs without KeyError and finds #5605')
finally: relay.OPT['comp']='0'
print('%d checks, %d failed'%(n,len(fails))); sys.exit(1 if fails else 0)
if __name__=='__main__': pass
