"""genpipe2 -- `tk gen2`: the from-scratch generator as ONE reproducible command (GENPIPE2.

  tk gen2 [--out DIR] [--stages relaytop,routeb,ylate,order,purex,polish] [--seed 0] [--list]
          [--d3-dirs 120,85,75,51,102,30,45] [--relaytop-dirs 30,45,51,75,85,102,120] [--order-dirs 51,30,45,75,120,102,85]
          [--ylate-cap 4] [--dims 4,8] [--no-xstops] [--sweep OUT.jsonl] [--expect]

Stages (each = one subprocess of a toolkit/gen2/ module, venv python, env set only inside the stage's main; each writes its word,
an exact `tk price` kappa line and a record in OUT/stages.jsonl):
  relaytop  RELAYTOP  edge-cover top, D3 reader pairing, self-dual ports, root sinks            -> allh_d3.json.gz   (.0025498457553)
  routeb    SIGFUSE   roots as sources + sigfuse.fuse_share, D3 order --d3-dirs (b0 order)       -> b0.json.gz        (.0029000603871)
  ylate     JOINTFRAMES late births on b0 (ylate.py)                                             -> yl1.json.gz       (.0029031190012)
  order     MARKETS   route B with sink-grouping order --order-dirs                              -> o1.json.gz        (.0029461448190)
            then ylate on o1                                                                     -> o1y.json.gz       (.0029493782308)
  purex     PUREX     early ends  purex2.py o1 --dims 4,8 --xstops   (NOTE: on o1, not o1y)       -> r104.json.gz      (.0030170593878)
  --lever   LEVERBANK opt-in early-end levers inside the purex step (gen2/levers/; repeatable; off = bit-exact)
  fold      GENUPGRADE: R-FOLD final pass (RULEMINE census + fold.py) on the last word; 0 sites on every gen2 word so far
  polish    B0POLISH chain on o1y: purex2 (px) -> k2sa (px_k2sa, ~50 min) -> tk eval evretime,retime (polished); TK_FREE_BOUNDS=1 in the child env only -> polished.json.gz (.0030572; HEAVY: hq only)
Data flow: relaytop is a stand-alone ancestor (routeb regenerates the same model with root sources; it does not read allh_d3);
ylate reads b0; order regenerates the model with a new sink-grouping order (it does NOT keep b0's bottom); purex reads o1.
Stages are composable: a missing input is built from the earlier stages that make it, or taken from OUT/ if the file is there
(delete it or use a new --out to rebuild).  --sweep OUT.jsonl runs MARKETS' 5040-order model sweep (heavy: hq only).
--expect compares each kappa with the lane value and exits 1 on a difference > 1e-13 (the quick regress check).
Byte identity: stage code writes gzip with a time header, so file sha differs run to run; the CONTENT sha (decompressed JSON) is
printed and `canonical` files (tkcommon.save_canonical, mtime 0) are written as NAME.canon.json.gz.  Heavy runs: $TK_HQ only."""
import sys, os, json, gzip, time, hashlib, subprocess, shutil
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path: sys.path.insert(0, HERE)
G2 = HERE + '/gen2'
W = os.path.dirname(os.path.abspath(__file__))
STAGES = ('relaytop', 'routeb', 'ylate', 'order', 'purex', 'polish', 'fold')
D3 = '120,85,75,51,102,30,45'; D3SORTED = '30,45,51,75,85,102,120'; ORDER = '51,30,45,75,120,102,85'
EXPECT = dict(allh_d3=0.0025498457553, b0=0.0029000603871, yl1=0.0029031190012, o1=0.0029461448190, o1y=0.0029493782308, r104=0.0030170593878)

def log(*a): print(time.strftime('%H:%M:%S'), *a, flush=True)

def run_py(script, args, cwd):
    cmd = [sys.executable, '-B', G2 + '/' + script] + [str(x) for x in args]
    log('RUN', ' '.join(cmd[2:]))
    env = dict(os.environ); env.pop('TK_FREE_BOUNDS', None)           # each stage sets what it needs inside main()
    p = subprocess.run(cmd, cwd=cwd, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    if p.returncode: print(p.stdout[-3000:]); raise SystemExit('stage script failed: %s (rc %d)' % (script, p.returncode))
    return p.stdout

def content_sha(path):
    return hashlib.sha256(gzip.open(path).read()).hexdigest()[:16]

def price(path):
    """exact kappa line via the same code as `tk price`: -> dict(kappa float, sha, legal(tk check), events, public)"""
    import price as PR
    return PR.fast(path, json.load(gzip.open(path)), use_cache=False)

class Run:
    def __init__(s, a):
        s.a = a; s.out = os.path.abspath(a.out); os.makedirs(s.out, exist_ok=True)
        s.recs = []; s.bad = []
    def path(s, name): return '%s/%s.json.gz' % (s.out, name)
    def have(s, name): return os.path.exists(s.path(name))
    def record(s, stage, name, dt, extra=None):
        p = s.path(name); o = price(p)
        import tkcommon
        w = json.load(gzip.open(p)); tkcommon.save_canonical(w, '%s/%s.canon.json.gz' % (s.out, name))
        r = dict(stage=stage, word=name, path=p, kappa=float(o['kappa']), kappa_str=o['kappa'], file_sha=o['sha'], content_sha=content_sha(p),
                 canon_sha=tkcommon.sha('%s/%s.canon.json.gz' % (s.out, name))[:16], events=o['events'], public=o['public'],
                 side=str(o.get('side'))[:80], sec=round(dt, 1), params=extra or {})
        s.recs.append(r); open(s.out + '/stages.jsonl', 'a').write(json.dumps(r) + '\n')
        e = EXPECT.get(name); tag = ''
        if e is not None and s.a.expect:
            ok = abs(r['kappa'] - e) < 1e-13; tag = ' EXPECT %.13f %s' % (e, 'OK' if ok else 'DIFF')
            if not ok: s.bad.append(name)
        log('KAPPA %-8s %.13f  events %d  content_sha %s%s' % (name, r['kappa'], r['events'], r['content_sha'], tag))
        return r
    # ---- stages
    def relaytop(s):
        t = time.time(); run_py('relaytop.py', [s.a.seed, s.path('allh_d3')] + ['--dirs', s.a.relaytop_dirs], s.out); s.record('relaytop', 'allh_d3', time.time() - t, dict(seed=s.a.seed, dirs=s.a.relaytop_dirs))
    def routeb(s, name='b0', dirs=None, stage='routeb'):
        t = time.time(); dirs = dirs or s.a.d3_dirs
        g = getattr(s.a, 'gauge', None)
        gs = getattr(s.a, 'gshape', 'ent') or 'ent'
        run_py('route_b.py', [s.a.seed, s.path(name), '--dirs', dirs] + ([] if g is None else ['--gauge', g]) + ([] if gs == 'ent' else ['--gshape', gs]), s.out)
        s.record(stage, name, time.time() - t, dict(seed=s.a.seed, dirs=dirs, **({} if g is None else dict(gauge=g)), **({} if gs == 'ent' else dict(gshape=gs))))
    def ylate(s, src, name, stage='ylate'):
        if not s.have(src): s.build(src)
        t = time.time(); run_py('ylate.py', [s.path(src), s.path(name), '--cap', s.a.ylate_cap], s.out); s.record(stage, name, time.time() - t, dict(src=src, cap=s.a.ylate_cap))
    def order(s):
        s.routeb('o1', s.a.order_dirs, 'order'); s.ylate('o1', 'o1y', 'order')
    def purex_cmd(s, src, dst):
        """purex2 (default, bit-exact) or, with --lever SPEC (opt-in, LEVERBANK), gen2/levers/stack.py = purex2 + the levers in ONE joint dim-0 solve."""
        args = [s.path(src), s.path(dst), '--dims', s.a.dims] + ([] if s.a.no_xstops else ['--xstops'])
        if getattr(s.a, 'lawprune', False): args += ['--lawprune', '--dyfix']   # GENUPGRADE: lemma-attributed ender pruning + exact dyadic Z factoriser, only on failure (a solving config is untouched)
        lv = list(getattr(s.a, 'lever', None) or [])
        if not lv: run_py('purex2.py', args, s.out); return {}
        for x in lv: args += ['--lever', x]
        run_py('levers/stack.py', args + ['--report', s.out + '/%s.levers.json' % dst], s.out); return dict(levers=lv)
    def purex(s):
        if not s.have('o1'): s.routeb('o1', s.a.order_dirs, 'order')
        t = time.time(); name = 'r104L' if getattr(s.a, 'lever', None) else 'r104'
        ex = s.purex_cmd('o1', name); s.record('purex', name, time.time() - t, dict(src='o1', dims=s.a.dims, xstops=not s.a.no_xstops, **ex))
    def run_tk(s, argv, free=True, extra_env=None):
        """`tk <argv>` as a subprocess; TK_FREE_BOUNDS=1 is put in the CHILD env only (never at import, never in this process)."""
        cmd = [sys.executable, '-B', HERE + '/tk.py'] + [str(x) for x in argv]
        log('RUN tk', ' '.join(cmd[3:]))
        env = dict(os.environ, PYTHONHASHSEED='0'); env.pop('TK_FREE_BOUNDS', None)
        if free: env['TK_FREE_BOUNDS'] = '1'
        env.update(extra_env or {})
        p = subprocess.run(cmd, cwd=s.out, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        open(s.out + '/polish.log', 'a').write('$ tk %s\n%s\n' % (' '.join(map(str, argv)), p.stdout))
        if p.returncode: print(p.stdout[-3000:]); raise SystemExit('tk %s failed (rc %d)' % (argv[0], p.returncode))
        return p.stdout
    def polish(s):
        """B0POLISH chain on the generator word o1y (MAP gotcha 15): purex2 (pre-reorder word) -> k2sa -> eval (evretime, retime; handoff off by default).
        Sub-steps (--polish-steps): purex, k2sa, eval.  Every sub-step logs an exact kappa line + a stages.jsonl record.  k2sa is wall-clock SA: its output varies run to run
        (seeds fixed, but --polish-tl budgets are seconds), so the exact B0POLISH kappa is reproduced by running `eval` on its k2sa word."""
        steps = [x for x in s.a.polish_steps.split(',') if x]
        if not s.have('o1y'): s.build('o1y')
        cur = 'o1y'
        if 'purex' in steps:                       # purex2 asserts 'body op after F9 block' on reordered words: it must run first
            t = time.time(); ex = s.purex_cmd('o1y', 'px')
            s.record('polish-purex', 'px', time.time() - t, dict(src='o1y', dims=s.a.dims, xstops=not s.a.no_xstops, **ex))
        if s.have('px'): cur = 'px'
        if 'k2sa' in steps:
            t = time.time(); o = s.path('px_k2sa'); tl = float(s.a.polish_tl)
            if os.path.exists(o): os.remove(o)
            s.run_tk(['pscreen', s.path(cur), '--set', 'k2sa', '--tl', tl, '--out', o], extra_env=dict(K2SA_SEEDS=s.a.polish_seeds))
            if not os.path.exists(o): shutil.copy(s.path(cur), o); log('k2sa found no gain: px_k2sa = input')
            s.record('polish-k2sa', 'px_k2sa', time.time() - t, dict(src=cur, tl=tl, seeds=s.a.polish_seeds))
        if s.have('px_k2sa'): cur = 'px_k2sa'
        if 'eval' in steps:
            t = time.time(); ed = s.out + '/eval'
            s.run_tk(['eval', s.path(cur), '--screens', s.a.polish_screens, '--rounds', s.a.polish_rounds, '--k', 2, '--maxm', 0, '--tl', s.a.polish_eval_tl, '--accept', 'fast', '--no-accept-each', '--out', ed, '--force'],
                     extra_env=dict(TK_RETIME_ANYOWNED='1') if getattr(s.a, 'lever', None) else None)     # LEVERBANK: own levers add owned fields; eval's retime guard would skip retime (-8e-6)
            import eval as E
            b = '%s/words/%s.best.json.gz' % (ed, E.wname(s.path(cur)))
            if not os.path.exists(b): raise SystemExit('eval wrote no best word: ' + b)
            shutil.copy(b, s.path('polished'))
            s.record('polish-eval', 'polished', time.time() - t, dict(src=cur, screens=s.a.polish_screens, rounds=s.a.polish_rounds, tl=s.a.polish_eval_tl))
    def fold(s):
        """GENUPGRADE: R-FOLD (Lemma 6, RULEMINE fold.py) as a final pass on the last word of the run: census first (seconds); fold.py (iob2 exact
        re-solves, LEGAL + kappa strictly up per site, heavy) only when sites exist.  Writes NAME_fold.json.gz; records 'sites 0' otherwise."""
        src = next((n for n in ('polished', 'px_k2sa', 'px', 'r104L', 'r104', 'o1y', 'o1', 'yl1', 'b0') if s.have(n)), None)
        if src is None: raise SystemExit('fold: no word in --out')
        rm = W + '/ext/RULEMINE'
        p = subprocess.run([sys.executable, '-B', rm + '/census.py', s.path(src)], cwd=rm, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        lines = [l for l in p.stdout.splitlines() if l.strip()]
        if p.returncode or not lines or lines[-1].strip() == 'NONE':
            log('FOLD %s: %s' % (src, 'no R-FOLD sites (Lemma 6 precondition fails everywhere)' if not p.returncode else 'census failed rc %d' % p.returncode))
            open(s.out + '/stages.jsonl', 'a').write(json.dumps(dict(stage='fold', word=src, sites=0, rc=p.returncode)) + '\n'); return
        t = time.time(); dst = src + '_fold'
        q = subprocess.run([sys.executable, '-B', rm + '/fold.py', s.path(src), s.path(dst)], cwd=rm, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        open(s.out + '/fold.log', 'a').write(q.stdout)
        if q.returncode or not s.have(dst): log('FOLD failed rc %d (see fold.log); word unchanged' % q.returncode); return
        s.record('fold', dst, time.time() - t, dict(src=src))
    def build(s, name):
        {'allh_d3': s.relaytop, 'b0': s.routeb, 'o1': lambda: s.routeb('o1', s.a.order_dirs, 'order'), 'yl1': lambda: s.ylate('b0', 'yl1'), 'o1y': s.order, 'r104': s.purex}[name]()

def sweep(a):
    """MARKETS sweep of all 5040 sink-grouping orders (model R0 after rt.build + edges.land); writes jsonl.  Heavy: submit through $TK_HQ."""
    run_py('sweep.py', [os.path.abspath(a.sweep)], os.path.dirname(os.path.abspath(a.sweep)))

def run(a):
    if a.sweep: sweep(a); return 0
    R = Run(a)
    for st in [x for x in a.stages.split(',') if x]:
        if st not in STAGES: raise SystemExit('unknown stage %s (have %s)' % (st, ','.join(STAGES)))
        log('--- stage', st)
        if st == 'routeb' and R.have('b0') and not a.force: R.record('routeb', 'b0', 0, dict(reused=True))
        elif st == 'routeb': R.routeb()
        elif st == 'relaytop': R.relaytop()
        elif st == 'ylate': R.ylate('b0', 'yl1')
        elif st == 'order': R.order()
        elif st == 'purex': R.purex()
        elif st == 'polish': R.polish()
        elif st == 'fold': R.fold()
    if R.bad: log('EXPECT FAILED for', R.bad); return 1
    return 0

def add_parsers(sp):
    p = sp.add_parser('gen2', help='from-scratch generator, stages 1-5 (relaytop, routeb, ylate, order, purex) in one command; r104 = .0030171 (genpipe2.py docstring)')
    p.add_argument('--out', default=W + '/ext/GENPIPE2/run', help='output dir (words, canon copies, stages.jsonl)')
    p.add_argument('--stages', default='routeb,ylate,order,purex', help='comma list of: ' + ','.join(STAGES) + ' (relaytop is a stand-alone ancestor, off by default)')
    p.add_argument('--seed', type=int, default=0, help='rt.build seed of the residual-network model (relaytop, routeb, order)')
    p.add_argument('--d3-dirs', default=D3, help='D3 sink-grouping order for routeb (b0 order)')
    p.add_argument('--relaytop-dirs', default=D3SORTED, help='D3 direction list for relaytop (the allh_d3 word used the SORTED list; the b0 order gives .0025422)')
    p.add_argument('--order-dirs', default=ORDER, help='sink-grouping order for the order stage (MARKETS best: 51,30,45,...)')
    p.add_argument('--gauge', type=int, default=None, help='root gauge 0..15 (MOONSHOT3 BLIND cliques x u/z flip) for route B; default = geometric roots (r104 path)')
    p.add_argument('--ylate-cap', type=int, default=4); p.add_argument('--dims', default='4,8', help='purex2 ender dims'); p.add_argument('--no-xstops', action='store_true')
    p.add_argument('--polish-steps', default='purex,k2sa,eval', help='polish sub-steps to run (comma list of purex,k2sa,eval); a missing earlier word is taken from --out')
    p.add_argument('--polish-tl', type=float, default=3530, help='k2sa pscreen --tl seconds (~85%% split over --polish-seeds; 3530 = 2 x 25 min)'); p.add_argument('--polish-seeds', default='1,2')
    p.add_argument('--polish-screens', default='evretime,retime', help='tk eval screens (handoff is opt-in: slow on 23k-event words)'); p.add_argument('--polish-rounds', type=int, default=2); p.add_argument('--polish-eval-tl', type=float, default=600)
    p.add_argument('--lever', action='append', default=None, metavar='SPEC', help='LEVERBANK (opt-in): add a lever to the purex step (own:H@G | own:auto | hub:R,../X,.. | relay:H[:dmax] | relay:auto | skip:H,..); purex then writes r104L instead of r104 (polish keeps px). Default off = bit-exact purex2. See gen2/levers/bank.py, module docstring')
    p.add_argument('--lawprune', action='store_true', help='GENUPGRADE (opt-in): purex2 drops exactly the enders a violated law names (Exit Lemma L2 / slot law L1 / stuck rows) and re-solves; a config that solves is byte-identical')
    p.add_argument('--gshape', default='ent', help='GENUPGRADE (opt-in): rt.build gain shape for routeb/order; taxW = exact chain-tax marginal (Lemma 4) with entry weight W (default ent = unchanged)')
    p.add_argument('--sweep', help='run the 5040-order model sweep to this jsonl instead (heavy, hq only)')
    p.add_argument('--expect', action='store_true', help='fail (exit 1) when a stage kappa differs from the lane value by > 1e-13')
    p.add_argument('--force', action='store_true', help='rebuild routeb even when OUT/b0.json.gz exists')
    p.add_argument('--list', action='store_true', help='print stages and expected kappas')

def main(a):
    if a.list:
        for k, v in EXPECT.items(): print('%-8s %.13f' % (k, v))
        return 0
    return run(a)
