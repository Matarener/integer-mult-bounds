#!/usr/bin/env python3
"""prims_extra back-tests (MOREPRIMS): P8-acc replays #5802 from #5786 at the PR kappa; P8-ret value check; merge3 of #5795 onto #5802.  usage: tests/prims_extra_test.py"""
import sys,os
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,os.path.join(HERE,'..'))
os.environ.setdefault('TK_FREE_BOUNDS','1')
import tkcommon as T, movekit as M, prims_extra as PE
fails=[]
def need(c,what):
    print(('PASS ' if c else 'FAIL ')+what,flush=True)
    if not c: fails.append(what)
b=T.load('5786')[1]
w=b
for (i1,i2,fp) in sorted([(12135,12138,529),(12265,12268,541),(12392,12395,549)],reverse=True):
    w=PE.apply_edit(w,dict(prim='P8',kind='acc',idx=[i1,i2],fp=fp,pull=1))
o=M.evaluate(w); need(o.get('legal') and abs(o['kappa']-0.0031233605997331364)<1e-15,'P8 acc x3 from #5786 = #5802 kappa (%s)'%o.get('kappa'))
need(w['verifier_profile']['lifetimes']==30 and w['verifier_profile']['owned_fields']<=28,'stamped pins: 30 lifetimes, owned_fields %d (<=28 of PR5802: free ids reused)'%w['verifier_profile']['owned_fields'])

# ---- P8GAP: #5811 (a SIX-event accumulation, hidden by the old KMAX=3 cap) is rediscovered by the site generator from the frontier stack word
SK=os.path.join(HERE,'..','ext','MOREPRIMS','CANDIDATE-5796-5795-on5802.json.gz')
if os.path.exists(SK):
    os.environ.pop('TK_VERIFIER_PROFILE',None); T._ACT[0]=False      # each word is judged under ITS profile family, not the one activated by the first word loaded above
    ws=M.pin(T.load(SK)[1]); k0=M.evaluate(ws); k0=k0.get('kappa')
    ch=PE.level(ws,window=(11900,12100),topq=3,log=lambda *x:None)
    ok=bool(ch) and ch[0][2]['kind']=='acc' and len(ch[0][2]['idx'])==6 and abs(ch[0][0]-0.003124186336633743)<1e-14
    need(ok,'P8 level (default KMAX) on the #5802+#5795+#5796 stack rediscovers #5811 (6-event acc, t=92) kappa %s'%(ch[0][0] if ch else None))
    vs=M.View(ws); S0=vs.S; idx=[i for i,e in enumerate(S0) if e[0]=='ADD' and e[1]==92 and e[2] in(63,61,103,18,45,108)]
    o=M.evaluate(PE.apply_edit(ws,dict(prim='P8',kind='acc',idx=idx,fp=1091,pull=1),vs)); need(o.get('legal') and abs(o['kappa']-0.003124186336633743)<1e-14,'explicit #5811 edit legal at the PR kappa')
    os.environ.pop('TK_VERIFIER_PROFILE',None); T._ACT[0]=False
    w58=T.load('5802')[1]; v8=M.View(M.pin(w58)); S8=v8.S; i8=[i for i,e in enumerate(S8) if e[0]=='ADD' and e[1]==92 and e[2] in(63,61,103,18,45,108)]
    o8=M.evaluate(PE.apply_edit(M.pin(w58),dict(prim='P8',kind='acc',idx=i8,fp=1091,pull=1),v8)); need(o8.get('legal') and o8['kappa']<M.evaluate(M.pin(w58))['kappa'],'raw #5802: bridge legal via the backward pull of t, a DIP (pays only after the #5796 retime)')

# ---- P12 (Weyl exchange): exact lemma + value-exactness of applied edits (independent Fraction oracle PE.sim_rows)
from fractions import Fraction as _Q
need(PE.sim_rows(PE.weyl_exchange(0,1,9),2)=={0:{1:_Q(1)},1:{0:_Q(1)}},'Weyl exchange: 4 events exchange two registers exactly')
need(PE.sim_rows([['INIT',5,9]]+PE.weyl_load(5,0,1,9),2,(5,))=={0:{0:_Q(1)},1:{0:_Q(1)},5:{1:_Q(1)}},'#5786 gadget: h=H, f=H, o=old f (hub copy-in via Weyl swap)')
if os.path.exists(SK):
    os.environ.pop('TK_VERIFIER_PROFILE',None); T._ACT[0]=False
    wv=M.pin(T.load(SK)[1]); vv=M.View(wv); base=PE.sim_rows(vv.S,vv.n); eds=list(PE.sites12(vv,window=(12000,12300)))[:25]; okv=0
    for ed in eds:
        S2,_,_=PE.parts(vv,ed); okv+= PE.sim_rows(S2,vv.n)==base
    need(eds and okv==len(eds),'P12 edits are value-exact (%d of %d sites, final rows identical)'%(okv,len(eds)))
print('FAILED' if fails else 'ALL PASS'); sys.exit(1 if fails else 0)
