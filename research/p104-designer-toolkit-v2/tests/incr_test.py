#!/usr/bin/env python3
"""quick INCR test: IncrWord initial state == legal.check/price (5580, 5718 default profile + adopted, 5751), also under TK_FREE_BOUNDS; then a short differential fuzz."""
import sys,os,subprocess
TD=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,TD+'/..')
from tkcommon import *
import incr
bad=0
def chk(name,pf,free):
    global bad
    if free: os.environ['TK_FREE_BOUNDS']='1'
    else: os.environ.pop('TK_FREE_BOUNDS',None)
    iw=incr.IncrWord(name,profile=pf); _,w=load(name)
    with use_profile(iw.profile):
        rep=legal.check(w); T,Pp=X.invoice(rep)
    ok=[(i,r) for i,r,_ in iw.viol[:50]]==[(i,r) for i,r,_ in rep['violations']] and iw.ledger()==(T,Pp) and abs(iw.kappa-X.kappa(T,Pp))<1e-15
    print(('PASS ' if ok else 'FAIL ')+'incr init == legal.check/price %s profile=%s free_bounds=%s'%(name,pf,free)); bad+=not ok
for name,pf in (('5580',None),('5718',None),('5718','5718'),('5751','5751')):
    for free in (False,True): chk(name,pf,free)
os.environ.pop('TK_FREE_BOUNDS',None)
r=subprocess.run([sys.executable,'-B',TD+'/incr_fuzz.py','--words','5580,5718','--n','25','--quiet'],capture_output=True,text=True)
ok=r.returncode==0 and 'TOTAL mismatches 0' in r.stdout; print(('PASS ' if ok else 'FAIL ')+'incr differential fuzz 5580,5718 x25 edits'); bad+=not ok
if not ok: print(r.stdout[-500:],r.stderr[-800:])
sys.exit(1 if bad else 0)
