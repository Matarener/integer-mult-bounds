#!/usr/bin/env python3
"""Regression test for tk.  usage: tests/regress.py [--quick] [--solver] [--pricer] [--real W[,W..]] [--full]
 --quick   fast stdlib tests only (~20 s): price x5 words, check (legal + three localised mutants), diff, hops, sens, gen (workspace only)
 --solver  retime 5551 --free starts,finals == #5561 and evretime 5561 K2/MAXM0 (CP-SAT, needs ortools; skipped with a notice if absent)
 --pricer  rank-r owned-pivot pricing (PR5392 package): verify_r and the rank-8 synthetic (~75 s)
 --real L  the unmodified real verifier stack on words L (5551,5553,5561; ~200 s each)
 default   = --quick --solver --pricer (the solver part is skipped without ortools);  --full = default + --real 5551,5553,5561 (~15 min)"""
import sys,os,subprocess,json,gzip,copy,tempfile,re
HERE=os.path.dirname(os.path.abspath(__file__)); TK=os.path.join(HERE,'..','tk')
PKG=False      # the full suite runs in the package (infra/ and data/ ship with it)
D=HERE+'/../data/'
fails=[];n=0;tmp=tempfile.mkdtemp()
EXT_OK=os.path.isdir(HERE+'/../ext/K2BACKTEST')      # fixtures of the k2 engine tests (nets, fork binaries, MARKETS words) are not shipped
if not EXT_OK: print('SKIP k2unify_test, k2levers_test: need unshipped inputs under ext/ (K2BACKTEST, K2PUSH, K2SEARCH)',flush=True)
def tk(*a,ok=None):
    r=subprocess.run(([sys.executable,'-B',os.path.join(HERE,'..','tk.py')] if PKG else [TK])+list(a),capture_output=True,text=True); return r.returncode,r.stdout+r.stderr
import time as _t
_T0=[_t.time()]; TIMING='--time' in sys.argv
def need(cond,what):
    global n; n+=1
    now=_t.time(); dt=now-_T0[0]; _T0[0]=now      # HYGIENE: --time prints the seconds since the previous check (profile)
    print(('PASS ' if cond else 'FAIL ')+what+(('   [%.1fs]'%dt) if TIMING else ''),flush=True)
    if not cond: fails.append(what)
os.environ.setdefault('TK_PYTHON',sys.executable); os.environ.setdefault('TK_ACCEPT_CACHE','0'); os.environ.setdefault('TK_PRICERUN_CACHE','0')      # SPEED: regress exercises the REAL accept path, never the memos (override by exporting =1)
A=sys.argv[1:]; full='--full' in A; FAST='--fast' in A      # --fast (HYGIENE): <=2 min smoke subset of --quick
FASTSET={'fastnative_test','nincr_test','gensearch_test','pscreen_test','screen_smoke','primmine_open_test','clsfix_test','learned_test','shipcheck_test','framegap_test','canon_test','import_env_test','side_tail_test','gapmap_test','genpipe2_test','k2screen_fallback_test','leverbank_test','surgery_test','alignbuild_test','autoanat_test','bulk_test'}
try:
    import networkx; HAVE_NX=True
except ImportError: HAVE_NX=False
NXSET={'leverbank_test','genpipe2_test'}      # the gen2 generators import networkx, which generic CI does not provide
if not HAVE_NX: print('SKIP leverbank_test, genpipe2_test: networkx is not installed',flush=True)
def want(name): return ((not FAST) or name in FASTSET) and (HAVE_NX or name not in NXSET)
real=[x for x in (A[A.index('--real')+1].split(',') if '--real' in A else (['5551','5553','5561'] if full else []))]
only=[f for f in('--fast','--quick','--solver','--pricer','--reorder','--split','--split-full') if f in A]
do_quick=full or not (only or real) or '--quick' in A or FAST; do_solver=(full or not (only or real) or '--solver' in A) and not FAST; do_pricer=(full or not (only or real) or '--pricer' in A) and not FAST
try:
    import ortools; HAVE_ORTOOLS=True
except ImportError: HAVE_ORTOOLS=False
if do_quick:
    # 1. price: published claims
    for w,exp,kap in(('5545','.00304117181649','0.0030411718164'),('5551','.00304153116715','0.00304153116714'),('5553','.0030428242','0.00304282426236'),('5561','.0030814243','0.0030814243338')):
        rc,o=tk('price',w); need('expected %s: MATCH'%exp in o and kap in o,'price %s reproduces %s'%(w,exp))
    for w in ('5907','5827'):    # SPLICE: side check at the word's adopted tail (c,b,u), not the legacy 17/18/.2
        rc,o=tk('price',w,'--no-cache'); need('-> ok' in o and 'FAIL' not in o,'price %s: side ok at the profile tail'%w)
    rc,o=tk('price','5561s'); need('expected .0030768800: MATCH' in o,'price 5561s (starts-only) reproduces .0030768800')
    # 1b. fastnative == reference native pair check (small word, ~15 s)
    if not PKG:
        r=subprocess.run([sys.executable,'-B',HERE+'/fastnative_test.py','--quick'],capture_output=True,text=True); need(r.returncode==0 and 'mismatches 0' in r.stdout,'fastnative bit-exact vs reference native_pair (--quick)')
    if not PKG and os.path.exists(HERE+'/incr_test.py') and want('incr_test'):
        r=subprocess.run([sys.executable,'-B',HERE+'/incr_test.py'],capture_output=True,text=True); need(r.returncode==0,'incr: IncrWord == full check/price (init, bounds, short differential fuzz)')
        if r.returncode: print(r.stdout[-800:])
    if not PKG and os.path.exists(HERE+'/nincr_test.py') and want('nincr_test'):
        r=subprocess.run([sys.executable,'-B',HERE+'/nincr_test.py'],capture_output=True,text=True); need(r.returncode==0,'nincr: C replay kernel == IncrWord (init, TK_NATIVE_CORE factory, short exact lockstep fuzz)')
        if r.returncode: print(r.stdout[-800:])
    if not PKG and os.path.exists(HERE+'/fastsites_test.py') and want('fastsites_test'):
        r=subprocess.run([sys.executable,'-B',HERE+'/fastsites_test.py'],capture_output=True,text=True); need(r.returncode==0 and 'FAILS 0' in r.stdout,'FASTSITES: delta quick == full quick, incremental rebuild == full rebuild, ratio-form proxy_sites / indexed merge / incremental proxy pool == reference')
        if r.returncode: print(r.stdout[-800:])
    if not PKG and os.path.exists(HERE+'/relay_test.py') and want('relay_test'):
        r=subprocess.run([sys.executable,'-B',HERE+'/relay_test.py'],capture_output=True,text=True); need(r.returncode==0 and ' 0 FAIL' in r.stdout,'relay: spansolve + tk relay back-tests (#5713 exact, #5605 joint + absorb)')
        if r.returncode: print(r.stdout[-800:])
    if not PKG and os.path.isdir(HERE+'/../synth') and want('synth'):
        rc,o=tk('synth','--roundtrip','5718'); need(rc==0 and 'SAME=True' in o and 'EQUAL=True' in o,'synth: spec_from_word(5718) -> gen -> realise reproduces the legal word, same kappa and canon hash')
        import tempfile; fgw=tempfile.mkdtemp()+'/frontgen.json.gz'
        rc,o=tk('synth','--front-gen','--anchor','5756','--no-gap','--out',fgw); need(rc==0 and 'value_ok True' in o and 'bad native pairs 0' in o and 'violations 0' in o,'synth FRONTGEN: unhinted front end + junk generator -> legal (IncrWord, TK_FREE_BOUNDS=1) and symbolic value check ok')
        rc2,o2=subprocess.run([TK,'check',fgw],capture_output=True,text=True,env=dict(os.environ,TK_FREE_BOUNDS='1',TK_PROFILE='5756')).returncode,''
        need(rc2==0,'synth FRONTGEN: tk check on the written word (endpoint rows by random evaluation = values delivered)')
        hsw=tempfile.mkdtemp()+'/hs.json.gz'
        rc,o=tk('synth','--front-gen','--anchor','5756','--helpers','shared','--no-gap','--out',hsw); need(rc==0 and 'value_ok True' in o and 'bad native pairs 0' in o and 'violations 0' in o and "'hs_source': 'stored plan'" in o,'synth HELPERSHARE: shared residual carriers (Y chains) legal, values exact')
        hbw=tempfile.mkdtemp()+'/hub.json.gz'
        rc,o=tk('synth','--front-gen','--anchor','5756','--helpers','hub','--no-gap','--out',hbw); need(rc==0 and 'value_ok True' in o and 'bad native pairs 0' in o and 'violations 0' in o and 'kappa 0.00128294' in o,'synth HUBGEN: annealed X flags + aggregated private hubs (stored plan) legal, values exact, kappa .0012829 > GENBACK grouped')
        hlw=tempfile.mkdtemp()+'/hl.json.gz'
        rc,o=tk('synth','--front-gen','--anchor','5756','--helpers','ladder','--no-gap','--out',hlw); need(rc==0 and 'value_ok True' in o and 'bad native pairs 0' in o and 'violations 0' in o and 'kappa 0.00134636' in o,'synth HUBLADDER: hub-hub merge ladders with shared hubs (stored plan) legal, values exact, kappa .0013464 > HUBGEN .0012829')
        mhw=tempfile.mkdtemp()+'/mh.json.gz'
        rc,o=tk('synth','--front-gen','--anchor','5756','--helpers','mainhub','--no-gap','--out',mhw); need(rc==0 and 'value_ok True' in o and 'bad native pairs 0' in o and 'violations 0' in o and 'kappa 0.00151097' in o,'synth MAINHUB: mains as hubs (Y-Y Haar pairs, X packets) + root trees (stored plan) legal, values exact, kappa .0015110 > HUBLADDER .0013464')
        ssw=tempfile.mkdtemp()+'/ss.json.gz'
        rc,o=tk('synth','--front-gen','--anchor','5756','--helpers','cse','--no-gap','--out',ssw); need(rc==0 and 'value_ok True' in o and 'bad native pairs 0' in o and 'violations 0' in o and 'kappa 0.00154815' in o,'synth SHAREDSUM: mainhub residual + shared signal relays on the root lattice (stored plan data/sharedsum_signal.json) legal, values exact, kappa .0015482 > MAINHUB .0015110')
        jfw=tempfile.mkdtemp()+'/jf.json.gz'
        rc,o=tk('synth','--front-gen','--anchor','5756','--helpers','joint','--no-gap','--out',jfw); need(rc==0 and 'value_ok True' in o and 'bad native pairs 0' in o and 'violations 0' in o and 'kappa 0.00155744' in o,'synth JOINTFEED: mainhub residual/root trees + root copies as joint signal+residual feeders (stored plan data/jointfeed_plan.txt, signal data/jointfeed_signal.json) legal, values exact, kappa .0015574 > SHAREDSUM .0015482')
        for bm,bk_,nm in(('dilworth','0.001044509046329','52 chain-cover copies'),('grouped','0.001252043933281','laminar Y-group tree')):
            rc,o=tk('synth','--front-gen','--anchor','5756','--no-gap','--back',bm); need(rc==0 and 'value_ok True' in o and 'bad native pairs 0' in o and 'violations 0' in o and 'kappa '+bk_ in o,'synth GENBACK back=%s (%s): legal, symbolic value ok, exact kappa %s'%(bm,nm,bk_))
    if not PKG and os.path.exists(HERE+'/gensearch_test.py') and want('gensearch_test'):
        r=subprocess.run([sys.executable,'-B',HERE+'/gensearch_test.py'],capture_output=True,text=True); need(r.returncode==0 and 'FAILS 0' in r.stdout,'GENSEARCH: spec ids deterministic, L1 kappa_hat = exact for the star spec, root_flip neutral, resume cache, R0 tax of STAR')
    if not PKG and os.path.exists(HERE+'/prims_extra_test.py') and want('prims_extra_test'):
        r=subprocess.run([sys.executable,'-B',HERE+'/prims_extra_test.py'],capture_output=True,text=True); need(r.returncode==0 and 'ALL PASS' in r.stdout,'P8GAP: P8 back-tests (#5802 from #5786, #5811 from the frontier stack, raw-#5802 dip), P12 Weyl lemma + value-exactness')
    if not PKG and os.path.exists(HERE+'/handover_test.py') and want('handover_test'):
        r=subprocess.run([sys.executable,'-B',HERE+'/handover_test.py'],capture_output=True,text=True); need(r.returncode==0 and 'ALL PASS' in r.stdout,'LATECUT: P13 hand-over back-test (#5774 hubs 623/696 -> #5786 pre/end set, solved LP, exact value check, legal)')
    if not PKG and os.path.exists(HERE+'/pscreen_test.py') and want('pscreen_test'):
        r=subprocess.run([sys.executable,'-B',HERE+'/pscreen_test.py','--quick'],capture_output=True,text=True); need(r.returncode==0 and 'ALL PASS' in r.stdout,'P8GAP: every primitive P1-P12 + macros is a registered eval screen and a FRONTAUTO screen')
    if EXT_OK and want('k2unify_test'):
        r=subprocess.run([sys.executable,'-B',HERE+'/k2unify_test.py','--quick'],capture_output=True,text=True); need(r.returncode==0 and 'ALL PASS' in r.stdout,'K2UNIFY: unified k2net engine == old fork binaries (bit-exact), python == C++ walks (#5811/#5827/#5907, 15 move families), BIT #5708, h1-twin rediscovery, k2sa screen')
        if r.returncode: print(r.stdout[-1500:])
    if not PKG and os.path.exists(HERE+'/k2frames_test.py') and want('k2frames_test'):
        r=subprocess.run([sys.executable,'-B',HERE+'/k2frames_test.py','--quick'],capture_output=True,text=True); need(r.returncode==0 and 'ALL PASS' in r.stdout,'K2FRAMES: python == C++ accept-all walks incl. fnew (frame creation) + own (helper->owned relay) on #5811/#5786, FULLVERIFY with the new families, #5756 from #5751 by one fnew, #5802 relay pattern by one own')
        if r.returncode: print(r.stdout[-1500:])
    if not PKG and os.path.exists(HERE+'/heuristics_test.py') and want('heuristics_test'):
        r=subprocess.run([sys.executable,'-B',HERE+'/heuristics_test.py','--quick'],capture_output=True,text=True); need(r.returncode==0 and 'ALL PASS' in r.stdout,'HEURISTICS: potentials flag-off exact (logging never changes a trajectory), python == C++ rung slack, ready-kill look-ahead pairs with blind (h1 twin at it 16400), shaped arms track exact kappa')
        if r.returncode: print(r.stdout[-1500:])
    if EXT_OK and want('k2levers_test'):
        r=subprocess.run([sys.executable,'-B',HERE+'/k2levers_test.py','--quick'],capture_output=True,text=True); need(r.returncode==0 and 'ALL PASS' in r.stdout,'K2LEVERS: python == C++ accept-all walk incl. lbirth (late birth) + eend (early end) on MARKETS/o1, eend fixture restores #5907 exactly, FULLVERIFY with the new families, lbirth-only SA rediscovers ylate (17 births)')
        if r.returncode: print(r.stdout[-1500:])
    if not PKG and os.path.exists(HERE+'/screen_smoke.py') and want('screen_smoke'):
        r=subprocess.run([sys.executable,'-B',HERE+'/screen_smoke.py','--fast' if FAST else '--quick'],capture_output=True,text=True); need(r.returncode==0 and 'ALL PASS' in r.stdout,'SCREENSMOKE: every registered screen (pscreen sets, movekit classes, eval wrappers/argv) is EXECUTED on a window of #5660: no exception, output legal, kappa not lower')
        if r.returncode: print(r.stdout[-1500:],r.stderr[-400:])
    if not PKG and os.path.exists(HERE+'/window_test.py') and want('window_test'):
        r=subprocess.run([sys.executable,'-B',HERE+'/window_test.py'],capture_output=True,text=True); need(r.returncode==0 and 'FAILS 0' in r.stdout,'SCREENSMOKE: prims window semantics (program-index windows translate to View.S, over-long windows clamp instead of IndexError)')
        if r.returncode: print(r.stdout[-800:],r.stderr[-400:])
    if not PKG and os.path.exists(HERE+'/primmine_open_test.py') and want('primmine_open_test'):
        r=subprocess.run([sys.executable,'-B',HERE+'/primmine_open_test.py'],capture_output=True,text=True); need(r.returncode==0 and 'FAILS 0' in r.stdout,'SCREENSMOKE: PRIMMINE depth-5-exhausted rules = reorder + one P3 (and sign twins)')
    if not PKG and os.path.exists(HERE+'/clsfix_test.py') and want('clsfix_test'):
        r=subprocess.run([sys.executable,'-B',HERE+'/clsfix_test.py'],capture_output=True,text=True); need(r.returncode==0 and 'FAILS 0' in r.stdout,'CLSFIX: PRIMMINE classifier ranges over all linearisations (rule A forward = one P3; former cap rules classify)')
    if not PKG and os.path.exists(HERE+'/s2s_test.py') and want('s2s_test'):
        r=subprocess.run([sys.executable,'-B',HERE+'/s2s_test.py'],capture_output=True,text=True); need(r.returncode==0 and 'FAILS 0' in r.stdout,'GENSPLICE: s2s state-to-state window synthesis (empty edit, small windows #5718/#5756, #5774 whole-word compaction, tamper detection)')
        if r.returncode: print(r.stdout[-800:])
    if not PKG and os.path.exists(HERE+'/learned_test.py') and want('learned_test'):
        r=subprocess.run([sys.executable,'-B',HERE+'/learned_test.py'],capture_output=True,text=True); need(r.returncode==0 and 'FAILS 0' in r.stdout,'GENLEARN: rule_audit lineage conformance (tight endpoints, no idle stops, dim-0 junk), learned modes no-op, tightness priced')
        if r.returncode: print(r.stdout[-800:],r.stderr[-400:])
    if not PKG and os.path.exists(HERE+'/admit_test.py') and want('admit_test'):
        r=subprocess.run([sys.executable,'-B',HERE+'/admit_test.py'],capture_output=True,text=True); need(r.returncode==0 and 'FAIL' not in r.stdout,'admit: oracle == real pricing acceptance (5756 + decay negative), event/scalar slack, compact preserves values')
    if not PKG and os.path.exists(HERE+'/shipcheck_test.py') and want('shipcheck_test'):
        r=subprocess.run([sys.executable,'-B',HERE+'/shipcheck_test.py'],capture_output=True,text=True); need(r.returncode==0 and 'FAIL' not in r.stdout,'shipcheck: verdict classes, minimal literals, derived stack anchors')
        if r.returncode: print(r.stdout[-1200:],r.stderr[-600:])
    if not PKG and os.path.exists(HERE+'/framegap_test.py') and want('framegap_test'):
        r=subprocess.run([sys.executable,'-B',HERE+'/framegap_test.py'],capture_output=True,text=True); need(r.returncode==0 and 'FAIL' not in r.stdout,'framegap: main X-final/Y-initial frames enforced (triv rejected, #5907/#5827 legal)')
        if r.returncode: print(r.stdout[-1200:],r.stderr[-600:])
    if os.path.exists(HERE+'/leverbank_test.py') and want('leverbank_test'):
        r=subprocess.run([sys.executable,'-B',HERE+'/leverbank_test.py'],capture_output=True,text=True); need(r.returncode==0 and 'ALL PASS' in r.stdout,'LEVERBANK: default tk gen2 order,purex chain bit-exact (o1/r104 content sha), levers/stack.py with no lever == purex2, own:479@560 == m479')
    if os.path.exists(HERE+'/genpipe2_test.py') and want('genpipe2_test'):
        r=subprocess.run([sys.executable,'-B',HERE+'/genpipe2_test.py','--fast' if FAST else '--chain'],capture_output=True,text=True); need(r.returncode==0 and 'ALL PASS' in r.stdout,'GENPIPE2 (tk gen2): '+('stage smoke b0/yl1 bit-exact (--fast)' if FAST else 'full chain relaytop..purex reproduces allh_d3, b0, yl1, o1, o1y and r104 .0030170593878 bit-exact'))
        if r.returncode: print(r.stdout[-1200:],r.stderr[-600:])
    if os.path.exists(HERE+'/k2screen_fallback_test.py') and want('k2screen_fallback_test'):
        r=subprocess.run([sys.executable,'-B',HERE+'/k2screen_fallback_test.py']+(['--fast'] if FAST else []),capture_output=True,text=True); need(r.returncode==0 and 'ALL PASS' in r.stdout,'GEN2POLISH: k2sa native-ref refusal caused only by the inventory literal falls back to tk check --native (free bounds); ILLEGAL / bad native pair / other refusal still reject')
        if r.returncode: print(r.stdout[-1200:],r.stderr[-600:])
    if os.path.exists(HERE+'/canon_test.py') and want('canon_test'):
        r=subprocess.run([sys.executable,'-B',HERE+'/canon_test.py'],capture_output=True,text=True); need(r.returncode==0 and 'ALL PASS' in r.stdout,'HYGIENE: realised K2 words byte-canonical (bool MOVE private flags, PKGPREP normalise dump)')
        if r.returncode: print(r.stdout[-800:],r.stderr[-400:])
    if os.path.exists(HERE+'/surgery_test.py') and want('surgery_test'):
        r=subprocess.run([sys.executable,'-B',HERE+'/surgery_test.py']+(['--fast'] if FAST else []),capture_output=True,text=True); need(r.returncode==0 and 'ALL PASS' in r.stdout,'SURGPREP: surgery extract->splice round trip bit-exact on 6030 octets (+pool), relabel/shrink layouts, negative control, SPAN5 law + JR validate')
        if r.returncode: print(r.stdout[-1200:],r.stderr[-600:])
    if os.path.exists(HERE+'/autoanat_test.py') and want('autoanat_test'):
        r=subprocess.run([sys.executable,'-B',HERE+'/autoanat_test.py'],capture_output=True,text=True); need(r.returncode==0 and 'ALL PASS' in r.stdout,'AUTOANAT: auto_anatomy word filter, idempotent cpuq enqueue, price/gapmap legs on 6030, notable-vs-6030 rule, corpus + STATE digest (scratch files)')
        if r.returncode: print(r.stdout[-1200:],r.stderr[-600:])
    if os.path.exists(HERE+'/bulk_test.py') and want('bulk_test'):
        r=subprocess.run([sys.executable,'-B',HERE+'/bulk_test.py']+(['--fast'] if FAST else []),capture_output=True,text=True); need(r.returncode==0 and 'ALL PASS' in r.stdout,'BULKEVAL: tk bulk 2-word mini corpus (#6030,#5551): all steps, exact kappa, sorted summary, resume')
    if os.path.exists(HERE+'/alignbuild_test.py') and want('alignbuild_test'):
        r=subprocess.run([sys.executable,'-B',HERE+'/alignbuild_test.py','--fast'],capture_output=True,text=True); need(r.returncode==0 and 'ALL PASS' in r.stdout,'BULKGEN: tk anatomy 6030 (published ledger numbers) + tk rebuild skeleton/hub mini chain at exact kappa')
        if r.returncode: print(r.stdout[-1200:],r.stderr[-600:])
        if not FAST:      # the FULL rebuild of #6030 (all five sides, ~65 min): kappa == #6030 exactly, events <= 26000, SPAN5/JR 0, native 0 bad.  Run regress --quick via $TK_HQ
            r=subprocess.run([sys.executable,'-B',HERE+'/alignbuild_test.py','--quick'],capture_output=True,text=True); need(r.returncode==0 and 'ALL PASS' in r.stdout,'BULKGEN: tk rebuild 6030 (skeleton,routing,hubs,markets,signal) reproduces FULL_final at exact kappa, events <= 26000')
            if r.returncode: print(r.stdout[-1800:],r.stderr[-600:])
    if os.path.exists(HERE+'/import_env_test.py') and want('import_env_test'):
        r=subprocess.run([sys.executable,'-B',HERE+'/import_env_test.py']+(['--fast'] if FAST else []),capture_output=True,text=True); need(r.returncode==0 and 'ALL PASS' in r.stdout,'HYGIENE: importing toolkit modules does not change os.environ'+(' (--fast: the modules that used to set TK_FREE_BOUNDS + drivers)' if FAST else ''))
        if r.returncode: print(r.stdout[-800:],r.stderr[-400:])
    if os.path.exists(HERE+'/handoff6030_test.py') and want('handoff6030_test'):      # SPEED: hand-off screen no longer crashes on INIT-framed owned registers (#5811+)
        r=subprocess.run([sys.executable,'-B',HERE+'/handoff6030_test.py'],capture_output=True,text=True); need(r.returncode==0 and 'ALL PASS' in r.stdout,'handoff: tk eval 6030 --screens handoff runs the screen without error (rc 0, no traceback)')
        if r.returncode: print(r.stdout[-800:],r.stderr[-400:])
    if os.path.exists(HERE+'/speed_test.py') and want('speed_test'):      # SPEED (Oct 28): caches / parallel native / fast adapters / kappa_dec are exact
        r=subprocess.run([sys.executable,'-B',HERE+'/speed_test.py'],capture_output=True,text=True); need(r.returncode==0 and 'ALL PASS' in r.stdout,'SPEED: fingerprint index, parallel native pairs, fast adapters, hoisted kappa_dec, price.run memo key all exact')
        if r.returncode: print(r.stdout[-1200:],r.stderr[-400:])
    for tn,msg in(('side_tail_test','TKHYG2: every X.side caller (price, movekit, incr, evalincr, split, legalize) uses the adopted (c,b,u) tail: side ok on #5907/#5827; no direct tail-less X.side in toolkit'),('gapmap_test','TKHYG2: gapmap default = jump-level cut table (== SPLICE/topcost.py), --bands legacy table kept')):
        if os.path.exists(HERE+'/%s.py'%tn) and want(tn):
            r=subprocess.run([sys.executable,'-B',HERE+'/%s.py'%tn],capture_output=True,text=True); need(r.returncode==0,msg)
            if r.returncode: print(r.stdout[-800:],r.stderr[-400:])
    # 2. check: legal words, localised illegal mutants
    for w in('5545','5551','5553','5561','5561s'):
        rc,o=tk('check',w); need(rc==0 and 'LEGAL' in o and 'ILLEGAL' not in o,'check %s legal'%w)
    src=json.load(gzip.open(HERE+'/../words/5551.json.gz'))
    def mut(name,fn):
        w=copy.deepcopy(src); fn(w); p=os.path.join(tmp,name+'.json.gz'); json.dump(w,gzip.open(p,'wt')); return p
    def m_move(w):
        for i,e in enumerate(w['program']):
            if e[0]=='MOVE' and i>800: e[3]=e[2]; w['_ev']=i; return
    def m_final(w): w['final'][300]=w['initial'][300]
    def m_add(w):
        for i,e in enumerate(w['program']):
            if e[0]=='ADD' and i>500: e[2]=(e[2]+1)%735; return
    rc,o=tk('check',mut('mv',m_move)); need(rc==1 and 'Nested chronological transport' in o and 'event 9415' in o and 'reg 546 is helper' in o,'check localises a bad MOVE (rule, event, register role)')
    rc,o=tk('check',mut('fin',m_final)); need(rc==1 and 'Final frames' in o and 'reg 300 is helper' in o,'check localises a wrong final frame (register 300)')
    rc,o=tk('check',mut('add',m_add)); need(rc==1 and 'Endpoint rows' in o and 'reg 181 is Y' in o,'check localises a corrupted ADD to its endpoint row (reg 181)')
    if FAST:      # --fast stops here: the remaining quick sections (accept x4 ~60 s, native 12 s, split 32 s, decompile, handoff, gen) run in --quick
        print('\n%d checks, %d failed (--fast)'%(n,len(fails))); sys.exit(1 if fails else 0)
    # 2b. prepared573 verifier profile (PR5612 delayed shared preparation; TK573): the same numbers as #5612's own chain (chain5612: interval, 66618 paid, 13030 fields)
    for w,lo,hi,paid in(('5612','0.00310299359333','0.00310299359334','66636'),('on5612','0.00310440547057','0.00310440547058','66618')):
        rc,o=tk('check',w); need(rc==0 and ' LEGAL' in o and 'ILLEGAL' not in o,'check %s legal under the prepared573 profile'%w)
        rc,o=tk('price',w); need('crossing interval [%s, %s]'%(lo,hi) in o and 'paid calls %s'%paid in o and 'fields 13030' in o and 'surplus 760' in o and ('profile p5612' in o or 'profile 5612' in o) and 'MATCH' in o and 'MISMATCH' not in o,'price %s: interval (%s,%s), %s paid, 13030 fields, surplus 760'%(w,lo,hi,paid))
    psrc=json.load(gzip.open(HERE+'/../words/on5612.json.gz'))
    def pmut(name,fn):
        w=copy.deepcopy(psrc); fn(w); p=os.path.join(tmp,name+'.json.gz'); json.dump(w,gzip.open(p,'wt')); return p
    def pm_noret(w): del w['retired_public']                          # same program, no prepared interface: plain PR5599 rules reject the 573 INIT
    def pm_clear(w): w['program']=[e for e in w['program'] if not(e[0]=='CLEAR' and e[1]==573 and e[2]==603)]      # last lifetime never erased
    def pm_life(w):                                                     # drop a whole 573 lifetime (INIT..CLEAR) -> census 10
        P=w['program']; i=[k for k,e in enumerate(P) if e[0]=='INIT' and e[1]==573][1]; j=[k for k,e in enumerate(P) if e[0]=='CLEAR' and e[1]==573 and k>i][0]
        w['program']=P[:i]+P[j+1:]
    def pm_ints(w): w['independent_public']=w['independent_public'][:-1]
    rc,o=tk('check',pmut('p_noret',pm_noret)); need(rc==1 and 'Owned initialization' in o,'without `retired_public` the 573 INIT is rejected (the old rule)')
    rc,o=tk('check',pmut('p_clear',pm_clear)); need(rc==1 and 'All public and owned exits' in o,'prepared word: missing final CLEAR 573 rejected (owned exit)')
    rc,o=tk('check',pmut('p_life',pm_life)); need(rc==1 and ('Complete owned lifetime census' in o or 'Endpoint rows' in o),'prepared word: a deleted 573 lifetime is rejected (census / endpoint rows)')
    rc,o=tk('check',pmut('p_int',pm_ints)); need(rc==1 and 'Exact independent and owned interface' in o,'prepared word: wrong independent_public interface rejected')
    rc,o=tk('accept','on5612'); need(rc==0 and '"ok": true' in o and '"crossing_lo": "0.00310440547057"' in o and '"crossing_hi": "0.00310440547058"' in o and '"native_pairs": 2917' in o and '"paid_calls": 66618' in o,'accept on5612 = real prepared573_local + 5599 native + caller + PR5612 pricing.py: PASS, interval/2917 native maps/66618 paid as chain5612')
    def pm_add(w):
        for i,e in enumerate(w['program']):
            if e[0]=='ADD' and i>9000 and e[1]!=573 and e[2]!=573: e[2]=(e[2]+1)%748; return
    rc,o=tk('accept',pmut('p_add',pm_add)); need(rc==1 and '"ok": false' in o,'accept rejects a corrupted prepared word')
    # 2c. owned_fields profile p5660 (PR5627 local.py: 743 public + 9 owned, peak<=2, 11 lifetimes; pricing reserve 1e-12): #5644 / #5650 / #5660 reproduce their published crossing intervals
    for w,lo,hi,paid in(('5644','0.00310626336369','0.00310626336370','66492'),('5650','0.00310644469581','0.00310644469582','66492'),('5660','0.00310676334487','0.00310676334488','66474')):
        rc,o=tk('check',w); need(rc==0 and ' LEGAL' in o and 'ILLEGAL' not in o,'check %s legal under the owned_fields profile'%w)
        rc,o=tk('price',w); need('crossing interval [%s, %s]'%(lo,hi) in o and 'paid calls %s'%paid in o and 'fields 12958' in o and 'surplus 760' in o and ('profile p5660' in o or 'profile 5660' in o or 'profile 5644' in o or 'profile 5650' in o) and 'MATCH' in o and 'MISMATCH' not in o,'price %s: interval (%s,%s), %s paid, 12958 fields, surplus 760'%(w,lo,hi,paid))
        rc,o=tk('accept',w); need(rc==0 and '"ok": true' in o and '"crossing_lo": "%s"'%lo in o and '"crossing_hi": "%s"'%hi in o and '"paid_calls": %s'%paid in o and '"outer_checks": [\n  54,\n  4' in o,'accept %s = PR5627 local.py + native + caller + #5660 pricing.py (reserve 1e-12): PASS, published interval, %s paid, 54+4 outer predicates'%(w,paid))
    rc,o=tk('check','5660','--native'); need(rc==0 and '2917 distinct frame pairs, 0 bad' in o,'check 5660 --native: 2917 distinct frame pairs all legal')
    osrc=json.load(gzip.open(HERE+'/../words/5660.json.gz'))
    def omut(name,fn):
        w=copy.deepcopy(osrc); fn(w); p=os.path.join(tmp,name+'.json.gz'); json.dump(w,gzip.open(p,'wt')); return p
    def om_nofield(w): del w['owned_fields']                         # PR5599 rules: 8 owned roles, peak 1 -> the 9th owned role is out of range
    def om_ten(w): w['owned_fields']=10
    def om_clear(w): w['program'].pop(max(i for i,e in enumerate(w['program']) if e[0]=='CLEAR'))      # a last owned lifetime never erased (verify.py control missing_owned_erasure)
    def om_life(w):                                                   # drop a whole owned lifetime INIT..CLEAR -> census 10 (and the rows that lifetime built)
        P=w['program']; i=[k for k,e in enumerate(P) if e[0]=='INIT'][1]; j=[k for k,e in enumerate(P) if e[0]=='CLEAR' and k>i and e[1]==P[i][1]][0]; w['program']=P[:i]+P[j+1:]
    rc,o=tk('check',omut('o_nof',om_nofield)); need(rc==1 and ('Role index' in o or 'Owned initialization' in o),'owned_fields word without the key: 9th owned role rejected (PR5599 rules)')
    rc,o=tk('check',omut('o_ten',om_ten)); need(rc==1 and 'Owned inventory bound' in o,'owned_fields=10 rejected (8<=owned<=9)')
    rc,o=tk('check',omut('o_clr',om_clear)); need(rc==1 and 'All public and owned exits' in o,'owned_fields word: missing final CLEAR rejected (owned exit)')
    rc,o=tk('check',omut('o_life',om_life)); need(rc==1 and ('Complete public and owned inventories' in o or 'Endpoint rows' in o),'owned_fields word: a deleted owned lifetime is rejected (census / endpoint rows)')
    def om_add(w):
        for i,e in enumerate(w['program']):
            if e[0]=='ADD' and i>9000: e[2]=(e[2]+1)%743; return
    rc,o=tk('accept',omut('o_add',om_add)); need(rc==1 and '"ok": false' in o,'accept rejects a corrupted owned_fields word')
    # 2d. owned-role count generalisation (OWNEDN): the screens read nown/owned_set from the word's verifier profile (PR5627 local.py owned_fields = 9 owned roles, role 751 with 3 lifetimes)
    rc,o=tk('split','5660','--max','1'); need(rc==0 and 'start kappa 0.0031067633449 public 743' in o and '0 legal improving hits' in o,'split runs on the 9-owned #5660 (0 hits, no refusal)')
    dg9=os.path.join(tmp,'5660.dag.json.gz'); rw9=os.path.join(tmp,'5660_rt.json.gz')
    rc,o=tk('decompile','5660','--out',dg9); need(rc==0 and 'owned 9)' in o and '22015 value ops' in o and 'delivered outputs equal the contract: True' in o,'decompile 5660: 9 owned roles, 22015 value ops, delivered outputs == contract')
    rc,o=tk('realise',dg9,'--out',rw9); need(rc==0 and 'check: LEGAL' in o and 'kappa = 0.0031067633448766' in o,'realise(decompile 5660) is LEGAL with kappa .0031067633448766')
    rc,o=tk('diff','5660',rw9); need('delta +0.0000e+00' in o and 'paid-call histogram changes (rank:(A,B)): {}' in o and 'credited helper rank changes: {}' in o and 'endpoint spans changed: {}' in o,'round-tripped #5660 has the same invoice (MOVEs within one inter-op block may be reordered)')
    rc,o=tk('handoff','5660','--inline'); need(rc==0 and 'positive: {}' in o and 'CANDIDATE' not in o and 'S: 10020 raw' in o,'handoff 5660: runs with 9 owned roles, no positive successor hand-off')
    pj=os.path.join(tmp,'prof.json'); json.dump(dict(public=743,owned_fields=9,lifetimes=11,peak=1),open(pj,'w')); os.environ['TK_VERIFIER_PROFILE']=pj
    rc,o=tk('check','5660','--json'); os.environ.pop('TK_VERIFIER_PROFILE')
    need(rc==1 and 'All public and owned exits' in o,'verifier pins come from a profile object (TK_VERIFIER_PROFILE peak=1 rejects #5660)')
    rc,o=tk('handoff','5660','--selftest'); need(rc==0 and 'C recovers 429/429' in o,'handoff selftest on #5660: pooled class recovers all 429 existing helper tails')
    # 3. diff
    rc,o=tk('diff','5551','5561'); need('scalar program identical: True' in o and "removed {'MOVE': 170}" in o and "'helper initial': 168" in o and "'helper final': 23" in o,'diff 5551 5561: 170 MOVEs deleted, 168 starts + 23 finals changed')
    rc,o=tk('diff','5551','5551'); need('delta +0.0000e+00' in o and 'removed {}' in o,'diff A A is empty')
    # 4. hops
    M=D+'Smodel.json'
    rc,o=tk('hops',M); need(rc==0 and 'HOPS 916 ' in o,'hops unsigned reproduces 916 (HOPILP)')
    rc,o=tk('hops',M,'--signed'); need(rc==0 and 'HOPS 2797 ' in o,'hops signed verifies 2797 (SIGNHOP S.out)')
    bad=os.path.join(tmp,'prog.txt'); L=open(D+'rc1.txt').read().splitlines(); open(bad,'w').write('\n'.join(L[1:])+'\n')
    rc,o=tk('hops',M,'--program',bad); need(rc==1 and 'ILLEGAL' in o,'hops rejects a program with a node removed')
    # 4b. sens (P104CLEAN published marginals on #5545)
    rc,o=tk('sens','5545'); need(rc==0 and 'base 0.0030411718164907' in o and 'remove one rank-1 paid 7.2500764' in o and 'remove rank-2 paid 0.000144703612' in o and 'handoff 4+5 (T credit only) 1.35596876' in o and 'merge r1xk -> rk, k=9 4.35117960' in o,'sens 5545 reproduces the P104CLEAN marginals (+7.25e-5 per rank-1 paid, 4+5 hand-off 1.356e-6, ...)')
    # 4d. decompile / realise (TKSYNTH): word -> value DAG -> word
    dg=os.path.join(tmp,'5561.dag.json.gz'); rw=os.path.join(tmp,'5561_rt.json.gz')
    rc,o=tk('decompile','5561','--out',dg); need(rc==0 and 'delivered outputs equal the contract: True' in o and '21686 value ops' in o,'decompile 5561: DAG with 21686 value ops, delivered outputs == contract')
    rc,o=tk('realise',dg,'--out',rw); need(rc==0 and 'check: LEGAL' in o and 'kappa = 0.0030814243338015' in o,'realise(decompile 5561) is LEGAL with kappa .0030814243338015 (exact round trip)')
    rc,o=tk('diff','5561',rw); need('delta +0.0000e+00' in o and 'removed {}' in o and 'added {}' in o,'round-tripped word has the same invoice and event multiset as #5561')
    rc,o=tk('realise',dg,'--schedule','lazy','--out',os.path.join(tmp,'lazy.json.gz')); need(rc==0 and 'check: LEGAL' in o and 'kappa = 0.0030814243338015' in o,'realise with the lazy schedule (hops re-derived) is LEGAL, same kappa')
    rc,o=tk('realise',dg,'--drop-helper','706','--out',os.path.join(tmp,'drop.json.gz')); need(rc==1 and 'DROPPED helpers [706]: 12 ops removed' in o and 'UNDELIVERED outputs: 7 registers' in o and 'reg 119 (Y)' in o and '[Endpoint rows (random evaluation)]' in o and 'rows differ: [119, 121, 169, 191, 193, 204, 206]' in o,'realise with helper 706 deleted: localised (7 undelivered Y rows, Endpoint rows + helper-rank violations)')
    # 4e. handoff screen (TKHANDOFF): must reproduce #5569's helper 706 / frame 559 on #5561, find nothing positive on #5569, C self-test complete
    rc,o=tk('handoff','5561','--inline','--apply'); need(rc==0 and 'h=706  549->559 (fin 127)' in o and "[(173, '-1/2')]" in o and 'kappa 0.00308181851522' in o and 'positive: {\'ret\': 1}' in o and 'APPLIED 1 hand-offs' in o and '-> 0.003081818515222295' in o,'handoff 5561 reproduces #5569 (helper 706, 549->559, partner 173 coef -1/2, kappa .0030818185152) and --apply lands on it')
    rc,o=tk('handoff','5569','--inline'); need(rc==0 and 'positive: {}' in o and 'CANDIDATE' not in o,'handoff 5569: no positive successor hand-off left (S, C, B classes)')
    rc,o=tk('handoff','5561','--selftest'); need(rc==0 and 'C recovers 404/404' in o,'handoff selftest: pooled class recovers all 404 existing helper tails')
    rc,o=tk('price','5569'); need('expected .0030818185: MATCH' in o,'price 5569 reproduces .0030818185')
    # 4c. gen (S4GEN GENFULL2): workspace only
    if not PKG and os.path.isdir(D+'../S4GEN'):
        rc,o=tk('gen'); need(rc==0 and 'hubs 921 maxk 44' in o and 'chain cost 4010.092015 (d 0.000000)' in o and 'filter miss fw 0 bw 0' in o,'gen full0: 921 hubs from chains alone, native chain cost, filter 0/0')
if do_solver and not HAVE_ORTOOLS: print("SKIP solver tests (ortools not installed)")
do_reorder=do_solver or '--reorder' in A
if do_solver and HAVE_ORTOOLS:
    out=os.path.join(tmp,'rt.json.gz')
    rc,o=tk('retime','5551','--free','starts,finals','--tl','600','--out',out,'--wait','--name','tk_regress_rt')
    need('"kappa": "0.0030814243338015' in o and '"realised_legal": true' in o,'retime 5551 --free starts,finals reproduces #5561 kappa .0030814243338')
    rc,o=tk('price',out); need(rc==0 and 'kappa = 0.00308142433380154' in o,'tk price on the retimed word')
    rc,o=tk('diff',out,'5561'); need("removed {}" in o and 'delta +0.0000e+00' in o,'retimed word has the same invoice as #5561')
    eo=os.path.join(tmp,'ev.json.gz')
    rc,o=tk('evretime','5561','--k','2','--maxm','0','--tl','600','--out',eo,'--wait','--name','tk_regress_ev')
    need('OPTIMAL' in o and 'REALISED legal True' in o and 'EXACT kappa 0.003081500768 base 0.003081424334' in o,'evretime 5561 K2/MAXM0 reproduces .003081500768 (+7.6e-8, free ADD placement)')
    rc,o=tk('price',eo); need(rc==0 and 'kappa = 0.0030815007' in o,'tk price on the event-level retimed word')
    e9=os.path.join(tmp,'ev69.json.gz')
    rc,o=tk('evretime','5569','--k','2','--maxm','0','--tl','600','--out',e9,'--wait','--name','tk_regress_ev69')
    need('OPTIMAL' in o and 'REALISED legal True' in o and 'EXACT kappa 0.003081894969 base 0.003081818515' in o and 'COVERAGE' in o,'evretime 5569 K2/MAXM0 rediscovers #5580 contact step (ADD 451+=228, +7.645e-8)')
    rc,o=tk('diff',e9,'5580'); need('delta +0.0000e+00' in o and 'scalar program identical: True' in o and 'paid-call histogram changes (rank:(A,B)): {}' in o,'evretime(5569) has #5580 invoice and scalar program')
    import gzip,json
    ww=json.load(gzip.open(e9,'rt')); ev=[e for e in ww['program'] if e[0]=='ADD' and e[1]==451 and e[2]==228 and e[3]=='1']
    need(len(ev)==1 and ww['frames'][ev[0][-1]]==[11,21,33,455],'ADD 451+=228 now at the 4-dim chart [11,21,33,455]')
if do_reorder and HAVE_ORTOOLS:
    out=None
    # reorder (commuting reads/writes change places, relat.py): windowed so each solve is seconds
    ro=os.path.join(tmp,'ro80.json.gz')
    rc,o=tk('reorder','5580','--window','13520','13640','--tl','120','--out',ro,'--inline')
    need('OPTIMAL' in o and 'REALISED legal True' in o and 'EXACT kappa 0.003084155550804' in o,'reorder 5580 (window 13520-13640) rediscovers #5565 Stage A (write-epoch commute on port 198), kappa .0030841555508')
    rc,o=tk('diff',ro,'5565A'); need('delta +0.0000e+00' in o and 'paid-call histogram changes (rank:(A,B)): {}' in o,'reorder(5580) Stage-A word has the same invoice as 5565A')
    ro1=os.path.join(tmp,'ro51.json.gz')
    rc,o=tk('reorder','5551','--window','13900','14700','--tl','120','--out',ro1,'--inline')
    m_=re.search(r'EXACT kappa (\S+) ',o)
    need('REALISED legal True' in o and m_ and float(m_.group(1))>0.00304195140018,'reorder 5551 (window 13900-14700) reaches beyond #5565-old (read-epoch commute) .00304195140018')
    rc,o=tk('reorder','5599','--window','13520','13640','--tl','60','--out',os.path.join(tmp,'ro99.json.gz'),'--inline')
    need('REALISED legal True' in o and 'EXACT kappa' in o,'reorder runs on the N=750 #5599 word')
    rc,o=tk('reorder','5660','--window','13500','13700','--tl','60','--out',os.path.join(tmp,'ro60.json.gz'),'--inline')
    need('OPTIMAL' in o and 'REALISED legal True' in o and 'EXACT kappa 0.003106763344877 base 0.003106763344877' in o,'reorder runs on the 9-owned #5660 (window 13500-13700, role 751 lifetimes renamed): OPTIMAL, legal, no gain')

if do_pricer:
    rc,o=tk('pricer'); need(rc==0 and 'PASS_CONDITIONAL_KAPPA_00302725_OWNED_TRANSPOSE' in o,'pricer: verify_r reproduces PR5392 RESULT (r_q = 9)')
    rc,o=tk('pricer','--synth'); need(rc==0 and 'base root 0.00302728824993' in o and 'root [0.00309953590148,0.00309953590149] delta_lo=7.2248e-05' in o and 'root [0.00317177354692,0.00317177354693] delta_lo=1.4449e-04' in o,'pricer --synth: rank-8 pivot k=1 +7.2248e-5, k=2 +1.4449e-4')
if real:     # the real-stack runs are independent: start them concurrently (cached per word), then check each
    sys.path.insert(0,os.path.join(HERE,'..'))
    import tkcommon; tkcommon.closure_root()      # extract the capsule once, before the concurrent runs
    EXP={"5551":"0.00304153116714","5553":"0.00304282426236","5561":"0.00308142433380"}
    cmd=(lambda w:([sys.executable,'-B',os.path.join(HERE,'..','tk.py')] if PKG else [TK])+['price',w,'--real','--wait'])
    procs={w:subprocess.Popen(cmd(w),stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True) for w in real}
    for w in real:
        o=procs[w].communicate()[0]
        need('"error"' not in o and '"interval"' in o,'real stack accepts %s (replay, columns, native, caller, price.run, 54+4 outer checks)'%w)
        m=re.search(r'"crossing_lo": "([0-9.]+)"',o); need(bool(m) and m.group(1)==EXP[w],'real stack crossing %s == %s'%(w,EXP[w]))
if '--split' in A or '--split-full' in A:
    # split (SPLITGEN): the #5599 screen on #5565 finds the 13 H9 sites; first greedy step = H5+H4 split (+1.396e-6, +20 events), then #5599n has no hit
    rc,o=tk('split','5565','--max','1')
    need(rc==0 and '116 hits' in o and 'ranks [5, 4] dk +1.396e-06 (+20 events)' in o and 'kappa 0.0030866062700' in o,'split 5565: 116 hits, first step H9->H5+H4 kappa .0030866062700 (+20 events)')
    rc,o=tk('split','5599n','--max','1'); need(rc==0 and '0 hits' in o,'split 5599n: no further hit (screen fixed point)')
if '--split-full' in A:
    out=os.path.join(tmp,'sg.json.gz'); rc,o=tk('split','5565','--apply','--max','60','--out',out)     # ~10 min
    m=re.search(r'wrote .* : (\d+) splits, kappa ([0-9.]+)',o); need(bool(m) and int(m.group(1))>=13 and float(m.group(2))>=0.0031004563,'split 5565 greedy rediscovers >=13 splits and kappa >= #5599 (.0031004563)')
print('\n%d checks, %d failed'%(n,len(fails)))
sys.exit(1 if fails else 0)
