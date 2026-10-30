"""K2LEVERS tests (toolkit/k2/k2levers.inc, module docstring).  run: python3 -B tests/k2levers_test.py [--quick|--full]
 1 python == C++ on an accept-all random walk over ALL 20 move families incl. lbirth (late birth) and eend (early end) from MARKETS/o1 (route-B word):
   legal.check (only the base word's own public-inventory literal flag allowed), kernel2net R0, price_exact kappa, exact Fraction contract, rendezvous 0; lbirth >= 20 and eend >= 1 accepted
 2 eend fixture: an early-ending rider of s2s-compacted #5907 is lengthened by one F9 stop holding a cancelling ADD pair; ONE forced eend (K2S_LVSEED, FULLVERIFY) restores #5907's kappa exactly, validated
 3 K2S_FULLVERIFY=1 SA with lbirth/eend in the mix: every proposal == full verifier, every accepted index == from-scratch build
 4 rediscovery: lbirth-only SA on MARKETS/o1 (20000 its, seed 1) makes the 17 late births of ylate (o1 -> o1y): kappa .0029491103038 (o1y .0029493782308), python == C++
--quick (regress): ~40 s.  New families have weight 0 by default: the k2unify bit-exact tests cover the unchanged trajectories."""
import sys,os,json,gzip,time,tempfile,subprocess
HERE=os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0,HERE); sys.path.insert(0,os.path.join(HERE,'synth'))
ok=True; full='--full' in sys.argv
def chk(c,m):
    global ok; print(('PASS ' if c else 'FAIL ')+m,flush=True); ok&=bool(c)
from k2 import engine
import tkcommon,kernel2net as KN,k2search_validate as V
W=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),'ext')      # unshipped fixtures (nets, MARKETS words) live under ext/
O1=os.path.join(W,'MARKETS','o1.json.gz')
tmp=tempfile.mkdtemp(prefix='k2lt_'); t0=time.time(); engine.build()
ALL='1,1,1,.5,.5,2,.5,0,2,1,1,1,1,1,1,2,.5,.25,3,3'
def fams(lines): return {l.split()[0]:int(l.split()[-1]) for l in lines if l.startswith('  ') and ' accepted ' in l}
def validate(net,base,out):
    name,_=tkcommon.profile_of(tkcommon.load(base)[1])
    with tkcommon.use_profile(name): return V.validate(net,base,out,exact=True)
def good(res,allow=()):
    viol_ok=res['legal_ok'] or all(v[1] in allow for v in res['violations'])
    return viol_ok and res['kappa_match'] and res['R0_match'] and res.get('exact_ok') and res['rendezvous_viol']==0
def run(net,mode,env,timeout=280):
    e=dict(os.environ,K2_NET=net,K2_SEARCH=mode); e.update(env); p=subprocess.run([engine.binpath()],env=e,capture_output=True,text=True,timeout=timeout); return p.returncode,p.stdout.splitlines()
PUB=('Public inventory bound',)      # MARKETS/o1's own literal flag (public 968), present in the input word too
w1=tkcommon.load(O1)[1]; n1=os.path.join(tmp,'o1.net'); KN.dump_net(w1,n1)
# ---- 1. python == C++ walk
out=os.path.join(tmp,'o1w.net'); rc,L=run(n1,'walk',dict(K2S_ITERS='8000' if full else '4000',K2S_SEED='5',K2S_PEEL='2',K2S_W=ALL,K2S_OUT=out)); F=fams(L)
res=validate(out,O1,os.path.join(tmp,'o1w.json.gz'))
chk(rc==0 and good(res,PUB) and res['kappa']>1e-4,'o1 walk (%d accepted, lbirth %d, eend %d, %d events): python == C++ (kappa %.13f R0 %.3f), legal (base literal only), exact contract'%(sum(F.values()),F.get('lbirth',0),F.get('eend',0),res['events'],res['kappa'],res['R0']))
chk(F.get('lbirth',0)>=20 and F.get('eend',0)>=1,'walk exercised lbirth/eend: %s'%({k:v for k,v in F.items() if v}))
# ---- 2. eend fixture on #5907
from k2 import screen as K2S_
p,w=tkcommon.load('5907')
with tkcommon.use_profile(tkcommon.profile_of(w)[0]): wc,_=K2S_.compact(w,log=lambda *a:None)
nc=os.path.join(tmp,'5907c.net'); KN.dump_net(wc,nc); base=os.path.join(tmp,'5907c.json.gz'); json.dump(wc,gzip.open(base,'wt'))
L0=[l for l in open(nc).read().split('\n') if l]; Fd={}; R={}
for l in L0:
    t=l.split()
    if t[0]=='F': Fd[int(t[1])]=int(t[2])
    elif t[0]=='R': R[int(t[1])]=(t[2],int(t[3]))
cur={r:f for r,(ro,f) in R.items()}; nst={r:1 for r in R}
for l in L0:
    t=l.split()
    if t[0]=='M': cur[int(t[1])]=int(t[2]); nst[int(t[1])]+=1
F9=max(Fd,key=lambda f:Fd[f]); riders=[r for r,(ro,f) in R.items() if ro=='H' and Fd[cur[r]]<9 and nst[r]>=2]; pals=[r for r,(ro,f) in R.items() if ro=='H' and cur[r]==F9]
r=riders[len(riders)//2]; s=pals[0]; hdr=L0[0].split(); hdr[4]=str(int(hdr[4])+3)
nl=os.path.join(tmp,'5907L.net'); open(nl,'w').write('\n'.join([' '.join(hdr)]+L0[1:]+['M %d %d'%(r,F9),'A %d %d 1 %d'%(r,s,F9),'A %d %d -1 %d'%(r,s,F9)])+'\n')
oe=os.path.join(tmp,'5907e.net'); rc,L=run(nl,'walk',dict(K2S_ITERS='3',K2S_SEED='1',K2S_LVSEED='%d,%d'%(r,nst[r]-1),K2S_FULLVERIFY='1',K2S_W='0,'*19+'1',K2S_OUT=oe))
k0=[l for l in L if l.startswith('INPUT')]; Fe=fams(L); res=validate(oe,base,os.path.join(tmp,'5907e.json.gz'))
kc=float([l for l in L if l.startswith('FINAL')][0].split()[2]) if rc==0 else 0
chk(rc==0 and Fe.get('eend',0)==1 and good(res) and abs(res['kappa']-0.0031252890988)<1e-12,'eend fixture: rider %d of #5907 lengthened to F9 (%s), ONE eend ends it again: kappa %.13f == #5907 .0031252890988, legal, exact, FULLVERIFY clean'%(r,(k0 or ['?'])[0][30:62],res['kappa']))
# ---- 3. FULLVERIFY SA
rc,L=run(n1,'sa',dict(K2S_FULLVERIFY='1',K2S_ITERS='12000' if full else '3000',K2S_SEED='3',K2S_T0='.5',K2S_T1='.05',K2S_PEEL='2',K2S_W='1,.7,1,.5,1,2,.5,0,2,.5,.3,.3,.5,.5,1.5,1.5,1,1,3,3')); bad=[l for l in L if 'MISMATCH' in l]; F=fams(L)
chk(rc==0 and not bad and F.get('lbirth',0)>0,'incremental verify/index == full on every proposal and accepted move with lbirth/eend (accepted lbirth %d eend %d): rc %s %s'%(F.get('lbirth',0),F.get('eend',0),rc,bad[:1]))
# ---- 4. ylate rediscovery by lbirth alone
o4=os.path.join(tmp,'o1lb.net'); rc,L=run(n1,'sa',dict(K2S_ITERS='20000',K2S_SEED='1',K2S_T0='.3',K2S_T1='.01',K2S_W='0,'*18+'1,0',K2S_OUT=o4)); F=fams(L)
res=validate(o4,O1,os.path.join(tmp,'o1lb.json.gz'))
chk(rc==0 and good(res,PUB) and F.get('lbirth',0)==17 and abs(res['kappa']-0.0029491103038)<1e-12,'lbirth-only SA on o1: %d late births (ylate: 17), kappa %.13f (o1 .0029461448190, o1y .0029493782308), python == C++, exact'%(F.get('lbirth',0),res['kappa']))
print('%d s'%(time.time()-t0)); print('ALL PASS' if ok else 'FAILED'); sys.exit(0 if ok else 1)
