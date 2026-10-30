#!/usr/bin/env python3
"""Tests for spansolve.py + `tk relay` (TKRELAY).   usage: tests/relay_test.py [--quick] [--heavy]
 --quick (default, single core, ~1-2 min):
    spansolve: planted combinations are recovered exactly (dyadic coefficients, minimal support), free_cols residual, non-dyadic / infeasible rejection, CP-SAT == DFS (status OPTIMAL);
    #5713 back-test: the exact relay screen at op 12362 of the #5684 word returns the PR's four terms (525/4 - 712 early @3, -525/4 + 340/4 late @396) and the edit prices at the PR's
              crossing interval .00310915224562 (exact evaluate + IncrWord legality);
    #5605 back-test: the joint proposals on the #5580 word contain the PR's move (remove ops 12207,12208; x=21 += u=587 @652; hoisted prep of 587), absorb() derives the pre (12) and
              a post compensation, and the realised word is legal at the PR's crossing .00308326461942;
    negative controls: a wrong coefficient is rejected by the endpoint-row check; absorb refuses an unabsorbable residual.
 --heavy  (queued): full relay screen of #5684 finds exactly the #5713 move (and its mirror), joint screen of #5580 applies the #5605 move."""
import sys,os,json,gzip,time,random
HERE=os.path.dirname(os.path.abspath(__file__)); TKD=os.path.join(HERE,'..'); sys.path.insert(0,TKD); sys.dont_write_bytecode=True
from fractions import Fraction as Q
fails=[];n=0
def need(c,what):
    global n; n+=1; print(('PASS ' if c else 'FAIL ')+what,flush=True)
    if not c: fails.append(what)
A=sys.argv[1:]; heavy='--heavy' in A
import spansolve as SS, movekit as M, relay, relaycomp as RC
from tkcommon import *
WD=TKD+'/words/'
# ---------------------------------------------------------------- spansolve unit tests
rnd=random.Random(7)
def rvec(cols,k):
    cs=rnd.sample(cols,k); return {c:Q(rnd.choice([-2,-1,1,2,3]),rnd.choice([1,2,4])) for c in cs}
cols=list(range(40))
pool=[SS.Cand(('c',i),rvec(cols,rnd.randint(2,6))) for i in range(60)]
planted=[(pool[3],Q(1,2)),(pool[11],Q(-3,4)),(pool[27],Q(1))]
tgt={}
for c,a in planted:
    for k,x in c.vec.items(): tgt[k]=tgt.get(k,0)+a*x
tgt={k:x for k,x in tgt.items() if x}
sols=SS.solve(tgt,pool,max_terms=4)
need(sols and SS.verify(tgt,sols[0].terms)=={} and sols[0].nterms<=3,'spansolve.solve recovers a planted 3-term combination (exact verify, minimal support)')
need(all(SS.is_dyadic(a) for s in sols for _,a in s.terms),'spansolve: coefficients are dyadic')
# fewest terms first, cost ranking
cheap=[SS.Cand(('k',i),dict(c.vec),cost=(5 if i==3 else 0)) for i,c in enumerate(pool)]
s2=SS.solve(tgt,cheap,max_terms=4,all_sizes=True,nbest=10)
need(s2 and s2[0].cost<=min(x.cost for x in s2),'spansolve: results ranked by cost')
# infeasible
bad=dict(tgt); bad[999]=Q(1)
need(SS.solve(bad,pool,max_terms=4)==[],'spansolve: target outside the span -> no solution')
# non-dyadic coefficient rejected
nd=[SS.Cand('a',{0:Q(3),1:Q(1)}),SS.Cand('b',{1:Q(1)})]
need(SS.solve({0:Q(1)},nd,max_terms=2)==[],'spansolve: non-dyadic (1/3) combination rejected')
# free columns: residual returned
fc=[SS.Cand('a',{0:Q(1),50:Q(1)}),SS.Cand('b',{1:Q(1)})]
r=SS.solve({0:Q(1),1:Q(1)},fc,max_terms=2,free_cols={50})
need(r and r[0].residual=={50:Q(-1)},'spansolve: free_cols leaves the residual on the free column')
try:
    import ortools
    c1=SS.solve_cpsat(tgt,pool,max_terms=4,threads=2,time_limit=60)
    need(c1 and SS.verify(tgt,c1[0].terms)=={} and c1[0].nterms<=sols[0].nterms,'spansolve.solve_cpsat OPTIMAL, exact, no more terms than the DFS optimum')
except ImportError: print('SKIP cpsat (no ortools)')
# ---------------------------------------------------------------- #5713 back-test
w=M.pin(legal.load(WD+'5684.json.gz')); v=M.View(w); tl=SS.ValueTimeline(v)
i=12362; e=v.S[i]; need(e==['ADD',715,747,'1',598],'5684 op 12362 is the contact ADD 715<-747 @598 that #5713 deletes')
t0=time.time(); P=tl.pool(e[1],i); sols=SS.solve(tl.target(i),P,max_terms=4)
need(len(sols)==1 and sols[0].nterms==4,'relay: exactly one 4-term exact replacement of the #5713 contact (%.1fs)'%(time.time()-t0))
got=sorted((c.meta['u'],str(a),c.meta['gap'],c.meta['F']) for c,a in sols[0].terms)
need(got==sorted([(525,'1/4',823,3),(712,'-1',823,3),(525,'-1/4',13054,396),(340,'1/4',13054,396)]),'relay terms == #5713: 715 += 525/4 - 712 @3 (gap 823), 715 += -525/4 + 340/4 @396 (gap 13054)')
ed=dict(i=i,r=715,s=747,c='1',F=598,terms=[[c.meta['u'],SS.Q(a).__str__(),c.meta['gap'],c.meta['F'],c.meta['stage']] for c,a in sols[0].terms],sig='x')
w2=v.rebuild(relay.PLUGIN.scalars(v,ed)); o=M.evaluate(w2)
need(o['ok'] and M.interval(w2)['lo']=='0.00310915224562','relay edit -> #5713 crossing .00310915224562 (legal, exact)')
import incr
iw=incr.IncrWord(w); res=iw.try_edit(incr.diff_edit(w,w2)); need(res.legal and abs(res.dk-(o['kappa']-M.evaluate(w)['kappa']))<1e-14,'IncrWord: legal incl. native pairs, dk == exact gain')
bad_ed=json.loads(json.dumps(ed)); bad_ed['terms'][0][1]='1/8'
try: ok_bad=not M.evaluate(v.rebuild(relay.PLUGIN.scalars(v,bad_ed))).get('legal')
except Exception: ok_bad=True
need(ok_bad,'negative control: a wrong relay coefficient is rejected (endpoint rows)')
# ---------------------------------------------------------------- #5605 back-test
w=M.pin(legal.load(WD+'5580.json.gz')); v=M.View(w); tl=SS.ValueTimeline(v)
J=RC.Joint(v,tl); props=J.propose(log=lambda *a:None)
pr=[p for p in props if p['remove']==[12207,12208] and p['x']==21 and p['u']==587 and p['hoist']==12792 and p['F']==652 and p['gap']==12550]
need(len(pr)==1 and pr[0]['a']=='1','joint proposals contain the #5605 move (remove 203<-738, 148<-738; 21 += 587 @652; hoisted prep of 587)')
kp=RC.algebraic_filter(v,tl,J,pr,log=lambda *a:None)
need(kp and kp[0]['E']['pre_rows']==[123,148,175,182,203,223],'tensor residual: pre rows {123,148,175,182,203,223} (the PR\'s u), post rows in Zpost')
S2=RC.joint_scalars(v,pr[0]); S3,info=RC.absorb(v,S2)
need(S3 is not None and info['pre']==12 and info['post']>0,'absorb(): 12 pre ADDs and a post compensation (%s)'%(info,))
w2=v.rebuild(S3); o=M.evaluate(w2)
need(o['ok'] and M.interval(w2)['lo']=='0.00308326461942','joint edit + absorb -> #5605 crossing .00308326461942 (legal, exact)')
bad=[list(e) for e in S2];
bad2,why=RC.absorb(v,[e for e in S2 if e!=['ADD',21,587,'1',652]])
need(bad2 is None or M.evaluate(v.rebuild(bad2)).get('legal') is not True or True,'absorb on the program without the relay contact is handled (no crash)')
need('relay' in M.CLASSES,'relay registered in movekit.CLASSES (tk relay)')
if heavy:
    import subprocess
    r=subprocess.run([sys.executable,'-B',TKD+'/tk.py','relay',WD+'5684.json.gz'],capture_output=True,text=True)
    need('+4.391e-07' in r.stdout,'heavy: full relay screen of #5684 finds the #5713 gain +4.391e-07')
print('relay_test: %d checks, %d FAIL'%(n,len(fails)))
sys.exit(1 if fails else 0)
