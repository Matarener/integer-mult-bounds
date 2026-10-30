#!/usr/bin/env python3
"""SCREENSMOKE: prims window semantics.  Windows were View.S indices (MOVEs removed) while callers think in w['program'] indices; an over-long window raised IndexError in sites_P1/P2.
Now: wspace='S' (legacy default) clamps; wspace='program' translates program indices to S indices (prims.prog_to_S_window).  usage: tests/window_test.py [--full]"""
import sys,os
HERE=os.path.dirname(os.path.abspath(__file__)); TK=os.path.dirname(HERE); sys.path.insert(0,TK)
os.environ.setdefault('TK_FREE_BOUNDS','1')
import tkcommon,movekit as M,prims
fails=[]
def need(c,what):
    print(('PASS ' if c else 'FAIL ')+what,flush=True)
    if not c: fails.append(what)
def L(a): _,w=tkcommon.load(a); return M.pin(w)
w=L('5660'); nP=len(w['program']); v=M.View(w); nS=len(v.S); pi=[i for i,e in enumerate(w['program']) if e[0]!='MOVE']
need(nP>nS,'5660 has MOVE events (program %d > S %d), so the two index spaces differ'%(nP,nS))
need(prims.prog_to_S_window(w,(0,nP))==(0,nS) and prims.prog_to_S_window(w,(pi[500],pi[900]))==(500,900) and prims.prog_to_S_window(w,(nP+50,nP+90))==(nS,nS),'prog_to_S_window maps program indices to S indices (+ clamps past the end)')
need(prims.clamp_S_window(w,(0,nP))==(0,nS),'clamp_S_window clamps an over-long window')
ctx=prims.PLUGIN.prepare(v)
for p in ('P1','P2'):
    ws=prims.clamp_S_window(w,(0,nP)); n=sum(1 for _ in prims.PLUGIN.sites(v,ctx,prims=(p,),window=ws)); need(n>0,'%s sites with the clamped over-long window: no IndexError (%d sites)'%(p,n))
a,b=pi[17000],pi[17150]
sa=list(prims.PLUGIN.sites(v,ctx,prims=('P1',),window=prims.prog_to_S_window(w,(a,b)))); sb=list(prims.PLUGIN.sites(v,ctx,prims=('P1',),window=(17000,17150)))
need(sa==sb and len(sa)>0,'program window (%d,%d) selects exactly the sites of S window (17000,17150): %d sites'%(a,b,len(sa)))
k,w2,ch,st=prims.greedy(w,('P1',),steps=1,window=(nP-200,nP+500),topq=5,tl=20,log=lambda *x:None,wspace='program'); need(k is not None,'greedy(wspace=program) with a window running past the end runs')
if '--full' in sys.argv:
    w=L('5561'); pi=[i for i,e in enumerate(w['program']) if e[0]!='MOVE']
    k,_,_,st=prims.greedy(w,('P1',),steps=1,window=(pi[14000],pi[14100]),topq=60,log=lambda *x:None,wspace='program')
    o=M.evaluate(L('5569')); need(abs(k-o['kappa'])<1e-15,'greedy P1 with the PROGRAM-index window equivalent to S (14000,14100) rediscovers #5569')
print('FAILS',len(fails)); sys.exit(1 if fails else 0)
