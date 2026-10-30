#!/usr/bin/env python3
"""RETIMEGAP regression: every lattice screen's MODEL gain must equal the EXACT price gain of its realised word.  usage: tests/retimegap_test.py [--quick|--full]
Bug it guards (Oct 26): cwT[d]=delta(T+18)-k0 and cwP[d]=k0-delta(P+18) were separate finite differences (differ ~3e-4 rel.), so a table move that cancels exactly in
the true kappa (#5660: helper rank 7->6 together with paid 7->6) was credited +3.26e-8 by `tk retime` (exact 0).  Weights now come from infra/linwt.py (cwT==cwP).
 tol = 1e-8 + 0.03*|exact gain|  (the residual left is second order in the total table change; measured 5551: 5.2e-7 on +4.0e-5; 5660 evretime: 5e-9 on -4.1e-6)
 --quick (default, single core ~2 min): unit checks + `retime` on 5551 5561 5580 5599 5660 5718 (data profile) ; --full adds evretime and reorder on 5660 (TL 60 each, MODELGAP line)."""
import sys,os,json,subprocess,tempfile,re
HERE=os.path.dirname(os.path.abspath(__file__)); TKD=os.path.join(HERE,'..'); sys.path.insert(0,TKD)
from tkcommon import *
import linwt
PY=sys.executable; fails=[]
def need(c,what):
    print(('PASS ' if c else 'FAIL ')+what,flush=True)
    if not c: fails.append(what)
tol=lambda g:1e-8+0.03*abs(g)
env=dict(os.environ,HEAVY_THREADS='1')
def tk(*a,e=None):
    r=subprocess.run([PY,'-B',os.path.join(TKD,'tk.py')]+list(a),capture_output=True,text=True,timeout=900,env=e or env); return r.stdout+r.stderr
# unit: symmetric weights, a T-move and a P-move at the same rank cancel exactly
w=legal.load(ALIASES['5660']);rep=legal.check(w);T,P=X.invoice(rep);pc=X.Pricer(T,P)
cwP,cwT=linwt.weights(pc)
need(cwP==cwT,'cwT == cwP (a T move and a P move at one rank cancel in the model as in the exact price)')
k0=pc.k; k1=X.kappa({**T,7:T[7]-18,6:T.get(6,0)+18},{**P,7:P[7]-18,6:P.get(6,0)+18})
need(abs(k1-k0)<1e-13,'exact: helper rank 7->6 together with paid 7->6 changes kappa by %.1e'%(k1-k0))
out=tempfile.mkdtemp(); d=os.path.dirname(HERE)
for name,extra in (('5551',{}),('5561',{}),('5580',{}),('5599',{}),('5660',{}),('5718',{'TK_VERIFIER_PROFILE':os.path.join(TKD,'profiles','5718.json')})):
    o=tk('retime',name,'--free','starts,finals,stops','--tl','100','--inline','--out',out+'/%s.json.gz'%name,e=dict(env,**extra))
    m=re.search(r'^RESULT (\{.*\})$',o,re.M)
    if not m: need(False,'retime %s produced a RESULT (%s)'%(name,o[-200:])); continue
    r=json.loads(m.group(1)); g=r['gain']; f=r['found_lin']
    need(r['realised_legal'] and abs(f-g)<=tol(g),'retime %-5s %s model %.4e exact %.4e |diff| %.2e <= tol %.2e'%(name,r['status'],f,g,abs(f-g),tol(g)))
    if name in('5660','5718'): need(abs(g)<1e-12,'retime %s: no fake gain (exact %.3e)'%(name,g))
if '--full' in sys.argv:
    for sc,extra in (('evretime',[]),('reorder',[])):
        o=tk(sc,'5660','--k','2','--maxm','0','--tl','60','--inline','--out',out+'/%s.json.gz'%sc)
        m=re.search(r'MODELGAP model_gain (\S+) exact_gain (\S+) diff (\S+)',o)
        if not m: need(False,'%s 5660 printed MODELGAP (%s)'%(sc,o[-200:])); continue
        mg,eg,df=map(float,m.groups()); need(abs(df)<=tol(eg),'%s 5660 model %.4e exact %.4e |diff| %.2e <= tol %.2e'%(sc,mg,eg,abs(df),tol(eg)))
print('FAILS',fails if fails else 'none'); sys.exit(1 if fails else 0)
