"""K2UNIFY tests (toolkit/k2, module docstring).  run: python3 -B tests/k2unify_test.py [--quick|--full]
 1 build + the unified binary reproduces the OLD fork binaries bit for bit on fixed seeds (k2s_v2 on #5827, k2h1 hop recipe on the compacted candidate), if those binaries exist
 2 python == C++ on random accept-all move walks (ALL 15 move families) for #5811, #5827, #5907's word: legal.check, kernel2net R0, price_exact kappa, exact Fraction contract replay vs the C++ header
 3 BIT #5708: k2bit incremental cost == full bitword pricing after a reloc/conj/merge walk (the C++ engine is complex-only; BIT stays the python reference engine behind the same CostModel plug)
 4 rediscovery back-test: h1's twin rung kill (470@593) from #5907's word by the K2PUSH recipe (hop, seed 501, s2s-compacted candidate) -- kappa >= .0031258115;
   --full also: #5907's own edit from #5827 (k2s v2 recipe, seed 51, 700k its)
 5 k2sa screen executes (tiny budget) and returns the input word when nothing is found
--quick (regress): ~60 s."""
import sys,os,json,gzip,time,tempfile,subprocess
HERE=os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0,HERE); sys.path.insert(0,os.path.join(HERE,'synth'))
W=os.path.abspath(os.path.join(HERE,'..'))
ok=True; full='--full' in sys.argv
def chk(c,m):
    global ok; print(('PASS ' if c else 'FAIL ')+m,flush=True); ok&=bool(c)
from k2 import engine
import tkcommon,kernel2net as KN,k2search_validate as V
tmp=tempfile.mkdtemp(prefix='k2ut_')
t0=time.time(); engine.build(); chk(os.path.exists(engine.binpath()),'unified k2 binary builds (%.0f s)'%(time.time()-t0))
def net_of(alias):
    from k2 import screen as K2S_
    p,w=tkcommon.load(alias); w,_=K2S_.compact(w,log=lambda *a:None)       # s2s pre-pass: the raw words sit at the 26000 event cap, a walk would mostly bounce off it
    n=os.path.join(tmp,alias+'.net'); KN.dump_net(w,n); return n,w
# ---- 1. old-binary compatibility (bit-exact trajectories)
K2S=W + '/ext/K2SEARCH/k2s_v2'; K2H1=W + '/ext/K2PUSH/k2h1'; CAND=W + '/ext/K2PUSH/net_cand_s2s.txt'
if os.path.exists(K2S) and os.path.exists(W + '/ext/K2BACKTEST/net_5827.txt'):
    o=dict(iters=6000,t0=.3,t1=.01,seed=51,peel=2,weights='1,.5,1,.5,1,3,.5,.3,3')
    a=engine.run(W + '/ext/K2BACKTEST/net_5827.txt','sa',o); b=engine.run(W + '/ext/K2BACKTEST/net_5827.txt','sa',o,binary=K2S)
    chk(a.get('best_kappa')==b.get('best_kappa') and a.get('nev')==b.get('nev') and a.get('final')==b.get('final'),'unified == k2s_v2 on #5827 (6000 its, seed 51): final %s nev %s'%(a.get('final'),a.get('nev')))
if os.path.exists(K2H1) and os.path.exists(CAND):
    o=dict(hop7=1,iters=8001,t0=.3,t1=.01,seed=501,peel=2,cap=25999,evpen=.5,evt=23000,weights='1,.5,1,.5,1,3,.3,1.5,3')
    a=engine.run(CAND,'sa',o); b=engine.run(CAND,'sa',o,binary=K2H1)
    chk(a.get('best_kappa')==b.get('best_kappa') and a.get('nev')==b.get('nev') and a.get('final')==b.get('final'),'unified == k2h1 (hop, event pressure) on the compacted candidate (8000 its): final %s nev %s'%(a.get('final'),a.get('nev')))
# ---- 2. python == C++ on random walks, all move families
ALL='1,1,1,.5,.5,2,.5,0,2,1,1,1,1,1,1,2'
for alias,seed in (('5811',7),('5827',8),('5907',9)):
    n,w=net_of(alias); out=os.path.join(tmp,'w'+alias+'.net')
    r=engine.run(n,'walk',dict(iters=8000 if full else 4000,seed=seed,peel=2,out=out,weights=ALL),timeout=280)
    acc=sum(int(l.split()[-1]) for l in r['lines'] if l.startswith('  ') and ' accepted ' in l)
    base=os.path.join(tmp,alias+'.base.json.gz'); json.dump(w,gzip.open(base,'wt'))
    res=V.validate(out,base,os.path.join(tmp,alias+'.out.json.gz'),exact=True)
    chk(res['legal_ok'] and res['kappa_match'] and res['R0_match'] and res.get('exact_ok') and res['rendezvous_viol']==0,
        '#%s walk (%d accepted moves, %d events): python == C++ (kappa %.13f R0 %.3f), legal, exact contract'%(alias,acc,res['events'],res['kappa'],res['R0']))
    fam=sorted(l.split()[0] for l in r['lines'] if l.startswith('  ') and ' accepted ' in l and int(l.split()[-1])>0)
    chk(acc>300 and len(fam)>=8,'#%s walk exercised the move set: %d accepted, families %s'%(alias,acc,','.join(fam)))
# ---- 2b. incremental engine == full engine: K2S_FULLVERIFY=1 re-verifies EVERY proposal with the full verifier, rebuilds EVERY accepted index from scratch and checks cleanup() is the identity on the fast path
n5907,w5907=net_of('5907')
for tag,o,env in (('all families, plateau SA',dict(iters=6000 if not full else 20000,t0=.5,t1=.05,seed=3,peel=2,evpen=.5,evt=22000,weights='1,.7,1,.5,1,2,.5,0,2,.5,.3,.3,.5,.5,1.5,1.5'),{}),
                  ('multi-reader hop + recursive delivery + hopkill',dict(iters=3000,t0=.5,t1=.05,seed=4,peel=2,hopk=3,hopkill=True,weights='1,.5,1,.5,1,3,.3,0,3,0,0,0,0,0,1.5'),{'K2S_REC':'1'})):
    e=engine.env_for(n5907,'sa',o); e.update(env); e.update(K2S_FULLVERIFY='1',K2S_PROFILE='1'); pr=subprocess.run([engine.binpath()],env=e,capture_output=True,text=True,timeout=290); r=dict(rc=pr.returncode,lines=pr.stdout.splitlines())
    bad=[l for l in r['lines'] if 'MISMATCH' in l]; inc=[l for l in r['lines'] if l.startswith('VERIFYINC')]
    chk(r['rc']==0 and not bad,'incremental verify/index == full on every proposal and accepted move (%s): rc %s %s'%(tag,r['rc'],bad[:1] or (inc or [''])[0]))
r=engine.run(n5907,'sa',dict(iters=4000,t0=.3,t1=.01,seed=5,peel=2,cost='r0',weights='1,.5,1,.5,1,3,.3,0,3,0,0,0,0,0,1.5'),timeout=200)
chk(r.get('best_R0') is not None and r['best_R0']<=r['input'].get('R0',1e9)+1e-6,'cost model R0 (K2S_COST=r0): best R0 %.3f <= input %.3f'%(r.get('best_R0',-1),r['input'].get('R0',-1)))
# ---- 3. BIT #5708
try:
    import bitword,k2bit_search as KS,random
    from synth import k2bit
    st=KS.S('bit5708'); rng=random.Random(5); base=st.cost; nacc=0
    for m in ('reloc','conj','merge'):
        k=0
        for _ in range(3000):
            if st.step(rng,0.0,(m,)) is not None: k+=1
            if k>=30: break
        nacc+=k
    w2,Vv=st.verify(); net=k2bit.encode(w2); cm=k2bit.BitCost('bit5708'); v=cm.exact(net)
    chk(not Vv and cm.legal(net) and v==bitword.price(w2,st.ctx)['raw'] and abs(st.cost-base)<1e-9,'BIT #5708: %d accepted moves, legal, CostModel.exact == bitword.price, incremental cost == base'%nacc)
except Exception as e: chk(False,'BIT #5708 parity raised %r'%e)
# ---- 4. rediscovery
if os.path.exists(CAND) or True:
    w5907=tkcommon.load('5907')[1]
    from k2 import screen as K2S_
    w1,ci=K2S_.compact(w5907,log=lambda *a:None); n=os.path.join(tmp,'c.net'); KN.dump_net(w1,n)
    chk(ci.get('compacted') and ci['events']<22000,'s2s pre-pass frees events on #5907 (%s -> %s)'%(ci.get('events_before'),ci.get('events')))
    t=time.time(); r=engine.run(n,'sa',dict(hop7=1,iters=100000,t0=.3,t1=.01,seed=501,peel=2,cap=25999,evpen=.5,evt=23000,weights='1,.5,1,.5,1,3,.3,1.5,3'),timeout=290)
    chk((r.get('best_kappa') or 0)>=0.0031258115,'rediscovery: h1 twin (rung 470@593 kill) from #5907 in 100k its: kappa %s (%.0f s)'%(r.get('best_kappa'),time.time()-t))
if full:
    n=W + '/ext/K2BACKTEST/net_5827.txt'; t=time.time()
    r=engine.run(n,'sa',dict(iters=700000,t0=.3,t1=.01,seed=51,peel=2,cap=26000,weights='1,.5,1,.5,1,3,.3,.2,3'),timeout=1500)
    chk((r.get('best_kappa') or 0)>=0.00312528,'rediscovery: #5907 edit (rung 468@593 kill) from #5827, seed 51: kappa %s (%.0f s)'%(r.get('best_kappa'),time.time()-t))
# ---- 4c. #5827 from #5811 (K2BACKTEST miss, class "kill + MOVE slide + two-term delivery"): the kslide move
n5811=os.path.join(tmp,'5811raw.net'); w5811=tkcommon.load('5811')[1]; KN.dump_net(w5811,n5811)
r=engine.run(n5811,'sa',dict(iters=60000,t0=.3,t1=.01,seed=1,peel=2,weights='1,.5,1,.5,1,0,0,0,0,0,0,0,0,0,0,4',out=os.path.join(tmp,'k5827.net')),timeout=200)
chk(abs((r.get('best_kappa') or 0)-0.0031247668151)<1e-12,'rediscovery: #5827 from #5811 by kslide (kill + MOVE slide + two-term delivery), 60k its: kappa %s'%r.get('best_kappa'))
if r.get('best_kappa'):
    base=os.path.join(tmp,'b5811.json.gz'); json.dump(w5811,gzip.open(base,'wt')); res=V.validate(os.path.join(tmp,'k5827.net'),base,os.path.join(tmp,'k5827.json.gz'),exact=True)
    chk(res['legal_ok'] and res['kappa_match'] and res.get('exact_ok'),'  ... python == C++ on the kslide result (legal, kappa %.14f, exact contract)'%res['kappa'])
# ---- 5. k2sa screen (fresh process: the verifier profile is auto-selected once per process)
r=subprocess.run([sys.executable,'-B',os.path.join(HERE,'tk.py'),'pscreen','5660','--set','k2sa','--tl','6'],capture_output=True,text=True,env=dict({k:v for k,v in os.environ.items() if not k.startswith('TK_')},K2SA_NATIVE_REF='0',K2SA_SEEDS='1'))
chk(r.returncode==0 and 'Traceback' not in r.stdout+r.stderr and 'RESULT k2sa' in r.stdout and 'not encodable' not in r.stdout and 'illegal' not in r.stdout,'tk pscreen --set k2sa runs on #5660 (compaction + SA + validation path): '+(r.stdout.strip().splitlines() or ['?'])[-1][:100])
# ---- 5b. the screen's gain path end to end (deterministic: fixed iterations, K2PUSH recipe): compaction -> SA -> validate -> word
code=("import sys,json; sys.path.insert(0,%r); sys.path.insert(0,%r)\nimport tkcommon\nfrom k2 import screen as S\np,w=tkcommon.load('5907')\n"
      "w2,ch=S.run(w,tl=60,seeds=(501,),native_ref=False,fixed_iters=100000,recipe=dict(hop7=True,weights='1,.5,1,.5,1,3,.3,1.5,3',evpen=.5,evt=23000,cap=25999))\nprint('GAIN',json.dumps(ch[0]['gain'] if ch else None)); print('FLAGS',all(type(e[4]) is bool for e in w2['program'] if e[0]=='MOVE'))")%(HERE,os.path.join(HERE,'synth'))
r=subprocess.run([sys.executable,'-B','-c',code],capture_output=True,text=True,env={k:v for k,v in os.environ.items() if not k.startswith('TK_')})
g=[l for l in r.stdout.splitlines() if l.startswith('GAIN')]
chk(bool(g) and g[0]!='GAIN null' and float(g[0].split()[1])>5e-7 and 'FLAGS True' in r.stdout,'k2sa screen gain path on #5907 (compact -> SA -> validate): %s'%(g[0] if g else (r.stdout+r.stderr)[-300:]))
print('%d s'%(time.time()-t0)); print('ALL PASS' if ok else 'FAILED'); sys.exit(0 if ok else 1)
