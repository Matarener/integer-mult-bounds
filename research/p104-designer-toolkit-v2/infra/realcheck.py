"""Run the REAL PR5544 verifier stack (local.replay + reverse_columns + native + price.run) on a candidate WORD.json.gz.
Everything verify.py does except the frozen-artifact equality and source-pin authentication (which pin the old word).
usage: python -B realcheck.py WORD.json.gz     (cwd-independent; ~3-5 min, use hq)"""
import sys,gzip,json,time
import os
REAL=os.environ.get('REALDIR',os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')) + '/ext/AUDIT5544/src/r/research/p104-productive-controller')
sys.path.insert(0,REAL); sys.dont_write_bytecode=True
import local as L, caller as C
import types,os
from fractions import Fraction as Q
def patched_price(kappa_str,sumT,sumP,surplus):
    src=open(REAL+'/price.py').read()
    import re
    src=re.sub(r"KAPPA, TESTED = Q\('[^']*'\), Q\('[^']*'\)","KAPPA, TESTED = Q('%s'), Q('%s')+Q(5,10**9)"%(kappa_str,kappa_str),src)
    src=re.sub(r"sum\(targets.values\(\)\) == \d+ and sum\(paid.values\(\)\) == \d+","sum(targets.values()) == %d and sum(paid.values()) == %d"%(sumT,sumP),src)
    src=re.sub(r"== 760,","== %d,"%surplus,src)
    m=types.ModuleType('price_patched'); exec(compile(src,'price_patched','exec'),m.__dict__); return m
t=time.time(); w=json.load(gzip.open(sys.argv[1]))
local=L.replay(w); print('replay OK',local['paid'],local['helpers'],'%.0fs'%(time.time()-t),flush=True)
cols=L.reverse_columns(w); print('reverse columns OK',flush=True)
native=L.native(w); print('native OK maps',native['distinct_maps'],'%.0fs'%(time.time()-t),flush=True)
controller=C.construct(); physical=C.physical(controller,w)
import price_exact as X, legal
rep=legal.check(w); T,Pp=X.invoice(rep); k=X.kappa(T,Pp); kstr='%.9f'%(k-5e-9-2e-9)    # 8-digit claim just below the root, as the PRs do
surplus=sum(r*n for r,n in T.items())-sum(r*n for r,n in Pp.items()); sumP=sum(Pp.values())
print('claim KAPPA',kstr,'sumP',sumP,'surplus',surplus,flush=True)
P=patched_price(kstr,sum(T.values()),sumP,surplus)
try:
    res=P.run(local,native,controller,physical)
    print('PRICE.RUN OK  kappa root interval',res['raw_root_interval'],flush=True)
except Exception as e:
    print('PRICE.RUN raised:',repr(e)[:300],flush=True)
    print('exact-invoice kappa (own pricer) %.12f'%X.kappa(T,Pp))
