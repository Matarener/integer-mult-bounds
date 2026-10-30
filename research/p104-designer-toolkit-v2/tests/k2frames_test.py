"""K2FRAMES tests (toolkit/k2/k2frames.inc, module docstring).  run: python3 -B tests/k2frames_test.py [--quick|--full]
 1 python == C++ on accept-all random walks over ALL 18 move families incl. fnew (frame creation) and own (helper->owned relay) from s2s-compacted #5811 and #5786:
   legal.check (with the owned-inventory literals the relays retarget), kernel2net R0, price_exact kappa, exact Fraction contract, rendezvous 0; both new families accepted >= 10x
 2 K2S_FULLVERIFY=1 SA with fnew/own: every proposal == full verifier, every accepted index == from-scratch build (new frames, new owned registers, merges, cuts, relays)
 3 back-test hits (census, seed 3, 4000 samples per move): #5756 from #5751 by ONE fnew (kappa == PR #5756 .00311313797336, legal, python == C++);
   one own move on #5751 = the #5802 relay pattern (helper 173: 559 rung dropped, reads of 613/611 relayed by an owned register) kappa .0031133688741, legal with retargeted lifetimes
--quick (regress): ~60 s.  Round 2: C++ scalar budget == price_exact.budgets (actual owned lifetimes) on the relay-heavy walk words; own seeds main stops too."""
import sys,os,json,gzip,time,tempfile,subprocess
HERE=os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0,HERE); sys.path.insert(0,os.path.join(HERE,'synth'))
ok=True; full='--full' in sys.argv
def chk(c,m):
    global ok; print(('PASS ' if c else 'FAIL ')+m,flush=True); ok&=bool(c)
from k2 import engine
import tkcommon,kernel2net as KN,k2search_validate as V
tmp=tempfile.mkdtemp(prefix='k2ft_'); t0=time.time(); engine.build()
ALL='1,1,1,.5,.5,2,.5,0,2,1,1,1,1,1,1,2,.5,.25'   # new families light enough that the walk's kappa stays far from the bisection floor (a real python == C++ kappa check)
def fams(r): return {l.split()[0]:int(l.split()[-1]) for l in r['lines'] if l.startswith('  ') and ' accepted ' in l}
def validate(net,base,alias,out):
    name,_=tkcommon.profile_of(tkcommon.load(alias)[1])
    with tkcommon.use_profile(name): return V.validate(net,base,out,exact=True)
def good(res): return res['legal_ok'] and res['kappa_match'] and res['R0_match'] and res.get('exact_ok') and res['rendezvous_viol']==0
# ---- 1. python == C++ walks
from k2 import screen as K2S_
for alias,seed in (('5811',7),('5786',11)):
    p,w=tkcommon.load(alias)
    with tkcommon.use_profile(tkcommon.profile_of(w)[0]): w,_=K2S_.compact(w,log=lambda *a:None)     # one verifier profile per word (the process-wide activation keeps the first)
    n=os.path.join(tmp,alias+'.net'); KN.dump_net(w,n)
    base=os.path.join(tmp,alias+'.base.json.gz'); json.dump(w,gzip.open(base,'wt')); out=os.path.join(tmp,'w'+alias+'.net')
    r=engine.run(n,'walk',dict(iters=8000 if full else 4000,seed=seed,peel=2,out=out,weights=ALL),timeout=280); F=fams(r)
    res=validate(out,base,alias,os.path.join(tmp,alias+'.out.json.gz'))
    dr=[l for l in r['lines'] if l.startswith('DREL')]
    chk(good(res) and res['kappa']>1e-4,'#%s walk (%d accepted, fnew %d, own %d, %d events): python == C++ (kappa %.13f R0 %.3f), legal, exact contract | %s'%(alias,sum(F.values()),F.get('fnew',0),F.get('own',0),res['events'],res['kappa'],res['R0'],(dr or ['?'])[0][:90]))
    # scalar budget: C++ routes must count the ACTUAL owned lifetimes (price_exact.budgets), on the relay-heavy walk word
    import legal,price_exact as X, re
    r2=engine.run(out,'walk',dict(iters=0,seed=1),timeout=60); m=[re.search(r'lifetimes (\d+) budget (\d+)',l) for l in r2['lines'] if l.startswith('INPUT')]
    with tkcommon.use_profile(tkcommon.profile_of(tkcommon.load(alias)[1])[0]): rep=legal.check(legal.load(os.path.join(tmp,alias+'.out.json.gz')))
    B=X.budgets(rep); lt0=sum(1 for e in w['program'] if e[0]=='INIT')
    chk(m and m[0] and int(m[0].group(1))==rep['lifetimes']>lt0 and int(m[0].group(2))==B['scalar_budget_used'],'#%s scalar budget C++ == python on the relay-heavy walk word: lifetimes %s (input %d) budget %s vs %s'%(alias,m and m[0] and m[0].group(1),lt0,m and m[0] and m[0].group(2),B['scalar_budget_used']))
    chk(F.get('fnew',0)>=10 and F.get('own',0)>=10 and sum(1 for v in F.values() if v)>=8,'#%s walk exercised fnew/own and the move set: %s'%(alias,','.join(k for k,v in sorted(F.items()) if v)))
# ---- 2. FULLVERIFY
n5811=os.path.join(tmp,'5811.net')
e=engine.env_for(n5811,'sa',dict(iters=3000 if not full else 12000,t0=.5,t1=.05,seed=3,peel=2,evpen=.5,evt=22000,weights='1,.7,1,.5,1,2,.5,0,2,.5,.3,.3,.5,.5,1.5,1.5,2,2')); e.update(K2S_FULLVERIFY='1')
pr=subprocess.run([engine.binpath()],env=e,capture_output=True,text=True,timeout=290); L=pr.stdout.splitlines(); bad=[l for l in L if 'MISMATCH' in l]
F={l.split()[0]:int(l.split()[-1]) for l in L if l.startswith('  ') and ' accepted ' in l}
chk(pr.returncode==0 and not bad and F.get('fnew',0)+F.get('own',0)>0,'incremental verify/index == full on every proposal and accepted move with fnew/own (accepted fnew %d own %d): rc %s %s'%(F.get('fnew',0),F.get('own',0),pr.returncode,bad[:1]))
# ---- 3. back-test hits by census on the raw #5751 net
w5751=tkcommon.load('5751')[1]; n=os.path.join(tmp,'5751raw.net'); KN.dump_net(w5751,n); base=os.path.join(tmp,'b5751.json.gz'); json.dump(w5751,gzip.open(base,'wt'))
o=os.path.join(tmp,'c5751.net'); r=engine.run(n,'census',dict(ktries=1,samples=4000,peel=2,seed=3,out=o),timeout=200)
mv={l.split()[1]:l for l in r['lines'] if l.startswith('MOVE ')}
for m,kap,what in (('fnew',0.00311313797336,'#5756 from #5751 by ONE fnew (frame creation: cluster at frame 477 (dim 8) -> new dim-4 frame)'),('own',0.0031133688741,'own on #5751 = the #5802 relay pattern (helper 173 rung 549->559 dropped, reads relayed by an owned register)')):
    f=o+'.'+m; res=validate(f,base,'5751',os.path.join(tmp,m+'5751.json.gz')) if os.path.exists(f) else None
    chk(res is not None and good(res) and abs(res['kappa']-kap)<1e-12,'%s: kappa %s legal %s (%s)'%(what,res and res['kappa'],res and res['legal_ok'],(mv.get(m) or '?')[:70]))
print('%d s'%(time.time()-t0)); print('ALL PASS' if ok else 'FAILED'); sys.exit(0 if ok else 1)
