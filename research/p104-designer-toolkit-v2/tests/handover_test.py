#!/usr/bin/env python3
"""LATECUT back-test: P13 (handover.py) rediscovers #5786's hand-overs from #5774 with the compensation SOLVED, not hard-coded.  usage: tests/handover_test.py"""
import sys,os
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,os.path.join(HERE,'..'))
os.environ.setdefault('TK_FREE_BOUNDS','1')
import tkcommon as T, movekit as M, handover as H
from fractions import Fraction as Q
fails=[]
def need(c,what):
    print(('PASS ' if c else 'FAIL ')+what,flush=True)
    if not c: fails.append(what)
os.environ.pop('TK_VERIFIER_PROFILE',None); T._ACT[0]=False
w=M.pin(T.load('5774')[1] if False else T.load(os.path.join(HERE,'..','words','5774.json.gz'))[1]); v=M.View(w); k0=M.evaluate(w)['kappa']
# 1. hub 623 (variant A: cut before the first run on chart 117, p moves there)
pl=H.plan(v,623,12179)
pre={T_:Q(x).limit_denominator(64) for T_,s,x in pl['sol']['pre']}
PR={205:1,546:-2,547:2,548:2,549:2,558:-4,568:4,569:2,570:4,575:2,576:2,624:1,625:-1,627:Q(-1,2),732:Q(1,2)}
need(pre=={k:Q(x) for k,x in PR.items()},'LP compensation of hub 623 = the 15 hoisted pre ADDs of #5786 (T += c p @Z) exactly, found without hints')
end={T_:Q(x).limit_denominator(64) for T_,x in pl['sol']['end']}
need(end=={k:-Q(x) for k,x in PR.items()},'... and the 15 end ADDs T -= c f @G are their negatives')
need(any(sr=='o' and T_==v.n and abs(c)==1 for (T_,t,c,sr) in pl['sol']['win']),'... and the injection f += o (K0 enters the new register) is one of the window options')
S2,ini,fin,_=H.apply_parts(v,dict(p=623,c=12179))
need(H.verify_rows(v,S2,len(ini))==[],'exact Fraction check: every public final row unchanged, new register identity')
w1=H.apply_edit(w,dict(p=623,c=12179),v); o1=M.evaluate(w1)
need(o1.get('legal') and abs(o1['kappa']-k0-3.2315670639394486e-07)<2e-11,'hub 623 alone legal, dk=%.4e (+3.2316e-7)'%(o1['kappa']-k0 if o1.get('kappa') else 0))
# 2. hub 696 (variant B: p rests on 1031 after its three packet writes; non-Z sources undone on F)
w2=H.apply_edit(w,dict(p=696,c=12433,F=1031),v); o2=M.evaluate(w2)
need(o2.get('legal') and abs(o2['kappa']-k0-3.2315e-07)<5e-10,'hub 696 alone legal, dk=%.4e'%(o2['kappa']-k0 if o2.get('kappa') else 0))
# 3. stacked
v1=M.View(w1); ev=[i for i,e in enumerate(v1.S) if e[0] in('ADD','COPY') and 696 in e[1:3] and e[-1]==1031]
w3=H.apply_edit(w1,dict(p=696,c=ev[-1]+1,F=1031),v1); o3=M.evaluate(w3)
need(o3.get('legal') and o3['kappa']-k0>6.4e-7,'623 then 696: legal, dk=%.4e (#5786 total +7.29e-7 incl. the third piece)'%(o3['kappa']-k0 if o3.get('kappa') else 0))
need(w3['verifier_profile']['public']==v.n+2 and len(M.View(w3).S)<26000,'pins stamped: public %d, events %d'%(w3['verifier_profile']['public'],len(M.View(w3).S)))
# 3b. joint planner (plan_multi) with one hub = the single-hub planner (same words, same kappa); two coupled hubs are infeasible in this option family (documented)
wm=H.apply_edit(w,dict(hubs=[dict(p=623,c=12179)]),v); om=M.evaluate(wm)
need(om.get('legal') and abs(om['kappa']-o1['kappa'])<1e-15,'plan_multi([623]) == plan(623): same kappa')
try: H.apply_edit(w,dict(hubs=[dict(p=623,c=12179),dict(p=624,c=12180)]),v); jointok=True
except H.Block: jointok=False
need(not jointok,'joint {623,624}: LP-infeasible (shared carrier 629 -> register 706), documented in module docstring')
# 4. split2 untouched / still importable and registered next to it
import split2, pscreen, prims_extra
need(hasattr(split2,'PLUGIN') and 'handover' in pscreen.SETS and pscreen.PRIMS_COVERED.get('P13')=='handover','split2 unchanged; P13 registered in pscreen')
print('FAILED' if fails else 'ALL PASS'); sys.exit(1 if fails else 0)
