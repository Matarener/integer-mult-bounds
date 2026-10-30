"""tk pricer [--pivots 9,9,...|--synth K] [--wait]
Rank-r owned-pivot pricing (PRICE8): price.py / verify.py of the PR5392 native-transpose-owned package generalised to an arbitrary owned-pivot rank r_q (price_r.py, verify_r.py).
Default `--verify` : run verify_r.py (all r_q = 9) -> reproduces the published RESULT.json (PASS_CONDITIONAL_KAPPA_00302725_OWNED_TRANSPOSE, raw root interval [.0030272882499,..]).
`--synth K`        : synth.py -- K relations (1 or 2) owned at rank 8 instead of 9 in all 18 calls: every price.py assertion passes; k=1 raw crossing [.00309953590148,.00309953590149]
                     (delta +7.2248e-5 = 4.0138e-6 per call-instance, surplus 770), k=2 .00317177354692 (+1.4449e-4, surplus 788).
Needs the unmodified PR5392 package research/native-transpose-owned (a repo path in package mode; PRICE8/src/t5392 in the workspace).  The result is a CEILING on the crossing, not a word."""
import sys,os,subprocess,re
from tkcommon import *
def nto():
    for p in (os.environ.get('TK_NTO',''),HERE+'/../native-transpose-owned',W + '/ext/PRICE8/src/t5392/research/native-transpose-owned'):
        if p and os.path.exists(p+'/word.py'): return os.path.abspath(p)
    raise SystemExit('tk pricer: PR5392 package research/native-transpose-owned not found (set TK_NTO)')
def run(script,args=()):
    d=nto(); env=dict(os.environ,TK_NTO=d,PYTHONDONTWRITEBYTECODE='1')
    r=subprocess.run([PY,'-B',HERE+'/pricer/'+script]+list(args),capture_output=True,text=True,env=env,cwd=d)
    return r.returncode,r.stdout+r.stderr
def main(a):
    if a.synth: rc,o=run('synth.py')
    else: rc,o=run('verify_r.py')
    print(o.rstrip()); return rc
