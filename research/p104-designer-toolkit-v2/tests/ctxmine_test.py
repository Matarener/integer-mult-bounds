#!/usr/bin/env python3
"""CTXMINE test: the lifted-guard window search rediscovers #5827 from #5811 (owned correction hoist), equiv() rejects a value-changing edit, pscreen carries the ctxmine screen."""
import sys,os
HERE=os.path.dirname(os.path.abspath(__file__)); TK=os.path.join(HERE,'..'); sys.path.insert(0,TK)
os.environ.setdefault('TK_FREE_BOUNDS','1')
fails=[]
def need(c,what):
    print(('PASS ' if c else 'FAIL ')+what,flush=True)
    if not c: fails.append(what)
import movekit as M, ctxmine as CM
from tkcommon import load
p,w=load('5811'); w=M.pin(w); v=M.View(w)
for _ in range(6): M.quick(v,v.S)
r=CM.search(v,12600,12608,depth=3,beam=100,tl=60)
need(bool(r) and abs(M.evaluate(v.rebuild(r[0]['S']))['kappa']-0.003124766815079838)<1e-15 and 'LIFT' in r[0]['tags'],'ctxmine: #5811 -> #5827 rediscovered (LIFT path %s)'%(str(r[0]['path']) if r else None,))
S2=[list(e) for e in v.S]; S2[12607]=['ADD',S2[12607][1],S2[12607][2],'2',S2[12607][4]]
need(not CM.equiv(v.S,S2),'equiv rejects a coefficient change')
need('ctxmine' in open(os.path.join(TK,'pscreen.py')).read(),'pscreen carries the ctxmine screen')
print('ALL PASS' if not fails else 'FAILS %d'%len(fails)); sys.exit(1 if fails else 0)
