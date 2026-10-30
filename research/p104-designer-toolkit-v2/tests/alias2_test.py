#!/usr/bin/env python3
"""P15 (prims_alias2) tests on mh_I: (1) soundness of the exact cross-term test: every combo that passes it and closes no cycle gives a program that passes the FULL poset recheck;
(2) a short greedy run yields a legal word (tk M.evaluate) with strictly fewer helpers and kappa >= the base; (3) the pscreen hook exists.  ~1 min, single core."""
import sys,os,random,time
HERE=os.path.dirname(os.path.abspath(__file__)); TK=os.path.join(HERE,'..'); sys.path.insert(0,TK)
os.environ.setdefault('TK_FREE_BOUNDS','1')
W=os.environ.get('MHI',os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')) + '/ext/MAINHUB/words/mh_I.json.gz')
if not os.path.exists(W): print('SKIP (no mh_I)'); sys.exit(0)
import prims_alias2 as P2, alias_core as A, movekit as M
fails=[]
def need(c,what):
    print(('PASS ' if c else 'FAIL ')+what,flush=True)
    if not c: fails.append(what)
w=A.loadw(W); Wk=P2.Work(w); need(Wk.feasible(),'base program is poset-feasible (0 bad events)')
random.seed(11); hs=random.sample(sorted(Wk.byh),120); n=bad=cyc=0
for h in hs:
    r=P2.plan_victim(Wk,h,top=3)
    if r is None: continue
    plan,sl=r
    for j in range(len(plan)):
        for alt in plan[j][5]:
            ch=[x[5][0] for x in plan]; ch[j]=alt
            S2=P2.build(Wk,h,sl,plan,ch)
            if S2 is None: cyc+=1; continue
            S2,rem=A.dce(S2,Wk.I.role,Wk.I.n); n+=1
            if not P2.poset_ok(Wk.I,S2): bad+=1
    if n>=40: break
print('combos checked',n,'cycles',cyc,'poset-bad',bad)
need(n>=10 and bad==0,'cross-term test is sound: %d combos, 0 full-recheck failures'%n)
w3,rem,acc=P2.run(w,tl=80,maxacc=6,maxpass=1,log=lambda *a:None)
need(w3 is not None and len(acc)>=1,'greedy accepts victims (%d)'%len(acc))
if w3 is not None:
    o=M.evaluate(w3); k0=M.evaluate(M.pin(w))['kappa']
    need(o.get('legal') and len(w3['initial'])<len(w['initial']) and o['kappa']>=k0,'result legal, %d fewer helpers, kappa %.10f >= %.10f'%(len(w['initial'])-len(w3['initial']),o['kappa'],k0))
import prims_alias2 as PA2
need(all(hasattr(PA2,f) for f in('sites','apply','level')),'pscreen hooks sites/apply/level present')
print('FAILS',len(fails)); sys.exit(1 if fails else 0)
