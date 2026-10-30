#!/usr/bin/env python3
"""AUTOMACRO test: RSPLIT rediscovers #5827 from #5811 at the PR kappa (window back-test), autodec explains the #5811 -> #5827 diff as P1c + owned correction, pscreen carries the screen."""
import sys,os
HERE=os.path.dirname(os.path.abspath(__file__)); TK=os.path.join(HERE,'..'); sys.path.insert(0,TK)
os.environ.setdefault('TK_FREE_BOUNDS','1')
fails=[]
def need(c,what):
    print(('PASS ' if c else 'FAIL ')+what,flush=True)
    if not c: fails.append(what)
import movekit as M, automacro_rsplit as RS, autodec as AD
from tkcommon import load
p,w=load('5811'); w=M.pin(w)
w2,chain=RS.run(w,tl=120,steps=1,log=lambda *x:None,window=(12560,12660),topq=20)
k=M.evaluate(w2)['kappa']
need(len(chain)==1 and abs(k-0.003124766815079838)<1e-15,'RSPLIT: #5811 -> #5827 rediscovered at the PR kappa (%.15f, edit %s)'%(k,chain[:1]))
d=AD.decompose('5811','5827')
need(len(d['clusters'])==1 and 'P1c' in d['clusters'][0]['tags'][0] and any(t.startswith('P1c-owned-corr') for t in d['clusters'][0]['tags']),'autodec: #5811 -> #5827 = P1c + owned correction (%s)'%d['clusters'][0]['tags'])
need('automacro' in open(os.path.join(TK,'pscreen.py')).read(),'pscreen carries the automacro screen')
print('ALL PASS' if not fails else 'FAILS %d'%len(fails)); sys.exit(1 if fails else 0)
