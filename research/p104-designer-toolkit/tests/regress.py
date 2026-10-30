#!/usr/bin/env python3
"""Regression test for tk.  usage: tests/regress.py [--quick] [--solver] [--pricer] [--real W[,W..]] [--full]
 --quick   fast stdlib tests only (~20 s): price x5 words, check (legal + three localised mutants), diff, hops, sens, gen (workspace only)
 --solver  retime 5551 --free starts,finals == #5561 and evretime 5561 K2/MAXM0 (CP-SAT, needs ortools; skipped with a notice if absent)
 --pricer  rank-r owned-pivot pricing (PR5392 package): verify_r and the rank-8 synthetic (~75 s)
 --real L  the unmodified real verifier stack on words L (5551,5553,5561; ~200 s each)
 default   = --quick --solver --pricer (the solver part is skipped without ortools);  --full = default + --real 5551,5553,5561 (~15 min)"""
import sys,os,subprocess,json,gzip,copy,tempfile,re
HERE=os.path.dirname(os.path.abspath(__file__)); TK=os.path.join(HERE,'..','tk')
PKG=os.path.isdir(HERE+'/../infra')
D=(HERE+'/../data/') if PKG else os.environ['TK_WORKSPACE']+'/cards/WILD/DESIGNER/'      # hops fixtures: package data/ or workspace
fails=[];n=0;tmp=tempfile.mkdtemp()
def tk(*a,ok=None):
    r=subprocess.run(([sys.executable,'-B',os.path.join(HERE,'..','tk.py')] if PKG else [TK])+list(a),capture_output=True,text=True); return r.returncode,r.stdout+r.stderr
def need(cond,what):
    global n; n+=1
    print(('PASS ' if cond else 'FAIL ')+what,flush=True)
    if not cond: fails.append(what)
A=sys.argv[1:]; full='--full' in A
real=[x for x in (A[A.index('--real')+1].split(',') if '--real' in A else (['5551','5553','5561'] if full else []))]
only=[f for f in('--quick','--solver','--pricer') if f in A]
do_quick=full or not (only or real) or '--quick' in A; do_solver=full or not (only or real) or '--solver' in A; do_pricer=full or not (only or real) or '--pricer' in A
try:
    import ortools; HAVE_ORTOOLS=True
except ImportError: HAVE_ORTOOLS=False
if do_quick:
    # 1. price: published claims
    for w,exp,kap in(('5545','.00304117181649','0.0030411718164'),('5551','.00304153116715','0.00304153116714'),('5553','.0030428242','0.00304282426236'),('5561','.0030814243','0.0030814243338')):
        rc,o=tk('price',w); need('expected %s: MATCH'%exp in o and kap in o,'price %s reproduces %s'%(w,exp))
    rc,o=tk('price','5561s'); need('expected .0030768800: MATCH' in o,'price 5561s (starts-only) reproduces .0030768800')
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
    # 3. diff
    rc,o=tk('diff','5551','5561'); need('scalar program identical: True' in o and "removed {'MOVE': 170}" in o and "'helper initial': 168" in o and "'helper final': 23" in o,'diff 5551 5561: 170 MOVEs deleted, 168 starts + 23 finals changed')
    rc,o=tk('diff','5551','5551'); need('delta +0.0000e+00' in o and 'removed {}' in o,'diff A A is empty')
    # 4. hops
    M=D+('Smodel.json' if PKG else 'SIGNHOP/Smodel.npy')
    rc,o=tk('hops',M); need(rc==0 and 'HOPS 916 ' in o,'hops unsigned reproduces 916 (HOPILP)')
    rc,o=tk('hops',M,'--signed'); need(rc==0 and 'HOPS 2797 ' in o,'hops signed verifies 2797 (SIGNHOP S.out)')
    bad=os.path.join(tmp,'prog.txt'); L=open(D+('rc1.txt' if PKG else 'HOPILP/rc1.txt')).read().splitlines(); open(bad,'w').write('\n'.join(L[1:])+'\n')
    rc,o=tk('hops',M,'--program',bad); need(rc==1 and 'ILLEGAL' in o,'hops rejects a program with a node removed')
    # 4b. sens (P104CLEAN published marginals on #5545)
    rc,o=tk('sens','5545'); need(rc==0 and 'base 0.0030411718164907' in o and 'remove one rank-1 paid 7.2500764' in o and 'remove rank-2 paid 0.000144703612' in o and 'handoff 4+5 (T credit only) 1.35596876' in o and 'merge r1xk -> rk, k=9 4.35117960' in o,'sens 5545 reproduces the P104CLEAN marginals (+7.25e-5 per rank-1 paid, 4+5 hand-off 1.356e-6, ...)')
    # 4c. gen (S4GEN GENFULL2): workspace only
    if not PKG and os.path.isdir(D+'../S4GEN'):
        rc,o=tk('gen'); need(rc==0 and 'hubs 921 maxk 44' in o and 'chain cost 4010.092015 (d 0.000000)' in o and 'filter miss fw 0 bw 0' in o,'gen full0: 921 hubs from chains alone, native chain cost, filter 0/0')
if do_solver and not HAVE_ORTOOLS: print("SKIP solver tests (ortools not installed)")
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
print('\n%d checks, %d failed'%(n,len(fails)))
sys.exit(1 if fails else 0)
