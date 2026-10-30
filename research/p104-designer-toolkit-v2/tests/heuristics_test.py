"""heuristics_test.py [--quick] -- HEURISTICS lane (toolkit/module docstring): k2phi.inc potentials + shaped search.
1 flag-off exactness: logging (K2S_FLOG/K2S_FSNAP) never changes a trajectory (same FINAL + per-family counts with and without it)
2 parity: potentials.rung_slack(word) == the C++ PHI line F0..F3 on #5827 and #5811 (EXACT formulas, 1e-6)
3 look-ahead pairing: K2S_PHILA leaves the run bit-identical to blind until it fires; on #5907 (s2s-compacted) seed 501 it takes the h1 twin rung kill at it 16400 (blind: 24120)
4 shaped arms run (tie / shape / segment) and keep exact-kappa best tracking (best >= input, FINAL parsed)
No env is set at import; options go to the child env only."""
import os,sys,json,tempfile,subprocess,hashlib
HERE=os.path.dirname(os.path.abspath(__file__)); TK=os.path.dirname(HERE)
for p in (TK,os.path.join(TK,'synth')):
    if p not in sys.path: sys.path.insert(0,p)
FAIL=[]
def chk(c,m): print(('PASS ' if c else 'FAIL ')+m,flush=True); (None if c else FAIL.append(m))
from k2 import engine
import tkcommon,kernel2net as KN,potentials as P
tmp=tempfile.mkdtemp(prefix='heur_')
def net_of(alias,compact=False):
    w=tkcommon.load(alias)[1]
    if compact:
        from k2 import screen; w,_=screen.compact(w,log=lambda *a:None)
    n=os.path.join(tmp,alias+('c' if compact else '')+'.net'); KN.dump_net(w,n); return n,w
def sig(r): return hashlib.md5('\n'.join(l for l in r['lines'] if l.startswith('FINAL') or 'accepted' in l).encode()).hexdigest()
def run(net,o,env=None):
    e=engine.env_for(net,'sa',o); e.update(env or {}); p=subprocess.run([engine.build()],env=e,capture_output=True,text=True,timeout=600); return p.stdout.splitlines()
n5827,w5827=net_of('5827')
FR='1,1,1,0.5,1,2,0.5,0.3,2,0,0,0,0,0,1,3,2,2'
o=dict(iters=15000,t0=.3,t1=.01,seed=3,peel=2,weights=FR)
a=engine.run(n5827,'sa',o); b=engine.run(n5827,'sa',dict(o,flog=os.path.join(tmp,'f.txt'),flogn=500,fsnap=5000))
chk(sig(a)==sig(b) and a.get('best_kappa')==b.get('best_kappa'),'logging + snapshots leave the trajectory bit-identical (#5827, 15k its): best %s'%a.get('best_kappa'))
for alias,(n,w) in (('5827',(n5827,w5827)),('5811',net_of('5811'))):
    L=run(n,dict(iters=1,flog=os.devnull)); ph=[l for l in L if l.startswith('PHI')][0]; F=[float(x) for x in ph.split('| F')[1].split('Phi')[0].split()]
    py=P.rung_slack(w); pv=[py['F0_rung'],py['F1_free'],py['F2_blocked'],py['F3_drain']]
    chk(all(abs(x-y)<1e-6*max(1,abs(y)) for x,y in zip(pv,F[:4])),'potentials.rung_slack == C++ PHI F0..F3 on #%s: %s'%(alias,[round(x,4) for x in pv]))
n5907,w5907c=net_of('5907',compact=True)
rec=dict(hop7=1,iters=30000,t0=.3,t1=.01,seed=501,peel=2,cap=25999,evpen=.5,evt=23000,weights='1,.5,1,.5,1,3,.3,1.5,3')
lg=os.path.join(tmp,'la.log'); lo=os.path.join(tmp,'la.net'); L=run(n5907,dict(rec,iters=20000,log=lg,out=lo),{'K2S_PHILA':'200'}); imp=[l.split() for l in open(lg)]
chk(bool(imp) and imp[0][0]=='16400' and imp[0][1]=='lookahead' and float(imp[0][3])>=.0031258115,'look-ahead takes the h1 twin rung kill at it 16400 on compacted #5907 seed 501 (blind finds it at 24120): %s'%(imp[:1],))
import gzip,k2search_validate as V
bw=os.path.join(tmp,'c5907.json.gz'); json.dump(w5907c,gzip.open(bw,'wt')); vr=V.validate(lo,bw,os.path.join(tmp,'la.json.gz'),exact=True)
chk(vr['legal_ok'] and vr['kappa_match'] and vr.get('exact_ok') and vr['rendezvous_viol']==0,'look-ahead result: python == C++ (legal, exact contract, kappa %.13f)'%vr['kappa'])
for tag,env,oo in (('tie',{},dict(phi=1,phitau=1)),('shape',{},dict(phi=1,phia=.1)),('segment',{'K2S_PHISEG':'1000','K2S_PHISEGTAU':'1'},{})):
    L=run(n5827,dict(o,iters=6000,**oo),env); fin=[l for l in L if l.startswith('FINAL')]
    ok=bool(fin) and float(fin[0].split('best kappa')[1].split()[0])>=.0031247668151-1e-13
    chk(ok,'%s arm runs, exact-kappa best tracked: %s'%(tag,fin[0][-45:] if fin else L[-2:]))
print('ALL PASS' if not FAIL else 'FAILED %d'%len(FAIL))
sys.exit(1 if FAIL else 0)
