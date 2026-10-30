#!/usr/bin/env python3
"""quick NATIVECORE test: native.nincr.NIncrWord == incr.IncrWord (initial state exact; short lockstep fuzz incl. out-of-representation events), and the TK_NATIVE_CORE=1 evaluator factory."""
import sys,os,subprocess
TD=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,TD+'/..')
from tkcommon import *
import incr
from native import nincr
bad=0
for name,pf in (('5580',None),('5718','5718')):
    a=incr.IncrWord(name,profile=pf); b=nincr.NIncrWord(name,profile=pf)
    ok=a.viol==b.viol and a.kappa==b.kappa and a.ledger()==b.ledger() and a.legal_all==b.legal_all and b._decode(b.endstate)==a.endstate
    print(('PASS ' if ok else 'FAIL ')+'nincr init == incr %s'%name); bad+=not ok
os.environ['TK_NATIVE_CORE']='1'; ok=isinstance(nincr.make_incr('5580'),nincr.NIncrWord); os.environ['TK_NATIVE_CORE']='0'; ok=ok and type(nincr.make_incr('5580')) is incr.IncrWord
print(('PASS ' if ok else 'FAIL ')+'make_incr honours TK_NATIVE_CORE'); bad+=not ok
r=subprocess.run([sys.executable,'-B',TD+'/incr_fuzz.py','--native-only','--words','5580,5718','--n','60','--quiet'],capture_output=True,text=True)
ok=r.returncode==0 and 'TOTAL mismatches 0' in r.stdout; print(('PASS ' if ok else 'FAIL ')+'nincr lockstep fuzz vs IncrWord 5580,5718 x60 edits (exact equality)'); bad+=not ok
if not ok: print(r.stdout[-500:],r.stderr[-800:])
import random
from wsearch import evalincr as EV
rnd=random.Random(7); okd=True
for t in range(3000):
    n=rnd.choice([0,1,2,5,17,64,65,1023,1024,1025,2048,3000,5000]); A=[('ADD',i%7,i%5,'1',3) for i in range(n)]
    for j in range(len(A)): A[j]=(A[j][0],rnd.randrange(4),rnd.randrange(4),rnd.choice(['1','2']),rnd.randrange(3))
    Bp=list(A) if rnd.random()<0.5 else [tuple(e) for e in A]
    for _ in range(rnd.choice([0,1,1,2,3])):
        if not Bp: break
        k=rnd.randrange(len(Bp)+1); op=rnd.random()
        if op<0.3 and k<len(Bp): Bp[k]=('X',k,0,'1',0)
        elif op<0.6: Bp.insert(k,('Y',k,0,'1',0))
        elif k<len(Bp): del Bp[k]
    m=min(len(A),len(Bp)); i=EV._lcp(A,Bp,m); i0=EV._lcp_gallop(A,Bp,m)
    j=EV._lcs(A,Bp,m-i); j0=EV._lcp_gallop(A[::-1],Bp[::-1],m-i)
    if (i,j)!=(i0,j0): okd=False; print('lcp/lcs differ',n,len(Bp),(i,j),(i0,j0)); break
print(('PASS ' if okd else 'FAIL ')+'evalincr block _lcp/_lcs == galloping reference (3000 random list pairs)'); bad+=not okd
sys.exit(1 if bad else 0)
