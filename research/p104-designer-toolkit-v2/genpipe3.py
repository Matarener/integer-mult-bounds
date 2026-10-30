"""genpipe3 -- `tk gen3`: gen2 + a Y-ROUTE stage (GENHUBS+, GEN3 section of MAP.md).

  tk gen3 [--out DIR] [--stages gen2,yroute,signal,post,screens] [--from WORD] [gen2 knobs: --seed --gauge --order-dirs --d3-dirs]
          [--yroute-max N] [--yroute-census-only] [--post-passes fold,hoist] [--screens evretime,retime] [--list]

Stages (each callable on its own; a stage reads the newest word in --out, or --from WORD; every stage writes OUT/<stage>.json.gz, an exact
`tk price` kappa line and a record in OUT/stages.jsonl; never-lose: a stage that finds nothing copies its input):
  gen2     `tk gen2 --lawprune` (routeb, ylate, order, purex) in OUT/gen2/ -> gen2.json.gz                    (GENPIPE2 + GENUPGRADE)
  primgen  PRIMGEN (opt-in, use INSTEAD of gen2; module docstring): gen2's route-B bottom, then the FANLAND landing = exact greedy over
           'reader stops at the piece frame g (any dim) and reads the piece there' vs gen2's landing copies (O1 relaxed; fan-out), realised by
           route_b.main unchanged (PRIMGEN/primgen_rb.py), then purex2 --dims D --xstops --lawprune --dyfix.  --primgen-aware charges each touched Y the
           Q_y ender purex would lose (on gen2 this leaves 0 sites: the lever is purex's ender at equal tax, sec 2 of the notes).   -> primgen.json.gz
  span     PRIMGEN SPAN MODEL (opt-in, after gen2 or primgen): X mains as RELAYS on the pre-purex route-B word (OUT/gen2/o1 or OUT/primgen/o1pg, or
           --from a pre-purex word): PRIMGEN/spanrelay.py = exact greedy [census: nest + P1 net < 0 -> exact holder test (co-present rows span X's own
           content before the helper's first delivery) -> value-exact build (X absorbs the helper's reads, peels its own content, delivers in its place;
           helper -> one jump) -> Y dim-0 loads + Gauss-Jordan F9 repair -> LEGAL + kappa up], then purex2 --dims 4,8 --xstops --lawprune --dyfix.  -> span.json.gz
  yroute   Y-MEET lever (GENHUBS/ymeet.py census + ymeet_apply.py exact construction per site): a Y main stops at a frame F < Q_y and reads there the
           helpers that today land on it at Q_y; each such helper ENDS at F (later stops gone).  Greedy: best model site first, exact jr
           via ymeet_apply.py (direct value-exact construction: read moved to F, L ended at F, jr.clean_ender, freed-reader repair by jr.solve, legal.check), greedy on the running word, accepted only if LEGAL with kappa strictly up; re-census per round.
           Heavy (jr ~minutes/site, GBs RSS): run gen3 with this stage through $TK_HQ.        -> yroute.json.gz
  signal   gen2's signal is route-B (sigfuse) and is built INSIDE the gen2 stage; there is no splice tool for a signal graft (SURGBUILD2
           sec 0).  This stage records the signal ledger (H signal R0, owned staging) and passes the word through.  -> signal.json.gz
  post     GENUPGRADE constructor passes (rebuild.post: R-FOLD fold.py, H-HOIST hoist.py), each kept only if LEGAL and kappa up.  -> post.json.gz
  retain   RETAINOP R-RETAIN (alignbuild/retain.py, opt-in; module docstring): retained-operand stop drop (swarm #6167 edit) on the newest word, exact
           LEGAL + kappa-up per site, never-lose.  Also reachable as `--post-passes fold,hoist,retain`.                         -> retain.json.gz
  screens  `tk eval --screens S --accept fast` (TK_FREE_BOUNDS=1 in the child env only: gen2 words are price-legal only under the
           convention literal, public ~965).                                                         -> screens.json.gz
No env is set in this process or at import.  Heavy runs: $TK_HQ only."""
import sys, os, json, gzip, time, shutil, subprocess, argparse
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path: sys.path.insert(0, HERE)
W = os.path.dirname(os.path.abspath(__file__))
GH = W + '/ext/GENHUBS'
STAGES = ('gen2', 'primgen', 'span', 'yroute', 'signal', 'post', 'retain', 'screens')
DEFAULT_STAGES = 'gen2,yroute,signal,post,screens'   # primgen is opt-in (PRIMGEN lane): it REPLACES gen2 as the generator stage
PG = W + '/ext/PRIMGEN'
PY = sys.executable

def log(*a): print(time.strftime('%H:%M:%S'), *a, flush=True)

def price(path):
    import price as PR
    return PR.fast(path, json.load(gzip.open(path)), use_cache=False)

def child_env(free=True):
    env = dict(os.environ, PYTHONHASHSEED='0'); env.pop('TK_FREE_BOUNDS', None)
    if free: env['TK_FREE_BOUNDS'] = '1'
    return env

class Run:
    def __init__(s, a):
        s.a = a; s.out = os.path.abspath(a.out); os.makedirs(s.out, exist_ok=True)
    def path(s, name): return '%s/%s.json.gz' % (s.out, name)
    def have(s, name): return os.path.exists(s.path(name))
    def cur(s, before):
        """input word of a stage: --from (first stage only), else the newest earlier stage word present in --out"""
        if s.a.from_ and not getattr(s, '_used_from', False): s._used_from = True; return os.path.abspath(s.a.from_)
        for st in reversed(STAGES[:STAGES.index(before)]):
            if s.have(st): return s.path(st)
        raise SystemExit('gen3 %s: no input word (give --from WORD or run an earlier stage)' % before)
    def record(s, stage, extra=None, t0=None):
        p = s.path(stage); o = price(p)
        r = dict(stage=stage, path=p, kappa=float(o['kappa']), kappa_str=o['kappa'], events=o['events'], public=o['public'], sec=round(time.time() - (t0 or time.time()), 1), **(extra or {}))
        open(s.out + '/stages.jsonl', 'a').write(json.dumps(r, default=str) + '\n')
        log('KAPPA %-8s %.13f  events %d  public %s' % (stage, r['kappa'], r['events'], r['public'])); return r
    # ---- stages
    def gen2(s):
        t0 = time.time(); g = s.out + '/gen2'
        argv = [PY, '-B', HERE + '/tk.py', 'gen2', '--out', g, '--stages', 'routeb,ylate,order,purex', '--seed', str(s.a.seed), '--lawprune',
                '--order-dirs', s.a.order_dirs, '--d3-dirs', s.a.d3_dirs] + ([] if s.a.gauge is None else ['--gauge', str(s.a.gauge)])
        log('RUN', ' '.join(argv[2:]))
        env = dict(os.environ); env.pop('TK_FREE_BOUNDS', None)
        p = subprocess.run(argv, cwd=s.out, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        open(s.out + '/gen2.log', 'w').write(p.stdout)
        if p.returncode or not os.path.exists(g + '/r104.json.gz'): print(p.stdout[-2000:]); raise SystemExit('gen3 gen2 stage failed (rc %d)' % p.returncode)
        shutil.copy(g + '/r104.json.gz', s.path('gen2')); s.record('gen2', dict(seed=s.a.seed, gauge=s.a.gauge, order=s.a.order_dirs), t0)
    def primgen(s):
        t0 = time.time(); wd = s.out + '/primgen'; os.makedirs(wd, exist_ok=True)
        o1 = wd + '/o1pg.json.gz'; r = wd + '/r104pg.json.gz'
        argv = [PY, '-B', PG + '/primgen_rb.py', str(s.a.seed), o1, '--dirs', s.a.order_dirs, '--greedy'] + (['--purex-aware'] if s.a.primgen_aware else []) + \
               ([] if s.a.gauge is None else ['--gauge', str(s.a.gauge)])
        log('RUN', ' '.join(argv[2:]))
        env = dict(os.environ); env.pop('TK_FREE_BOUNDS', None)
        p = subprocess.run(argv, cwd=wd, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        open(wd + '/primgen_rb.log', 'w').write(p.stdout)
        if p.returncode or not os.path.exists(o1): print(p.stdout[-2000:]); raise SystemExit('gen3 primgen: route-B realisation failed (rc %d)' % p.returncode)
        argv = [PY, '-B', HERE + '/gen2/purex2.py', o1, r, '--dims', s.a.primgen_dims, '--xstops', '--lawprune', '--dyfix']
        log('RUN', ' '.join(argv[2:]))
        p = subprocess.run(argv, cwd=wd, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        open(wd + '/purex.log', 'w').write(p.stdout)
        if p.returncode or not os.path.exists(r): print(p.stdout[-2000:]); raise SystemExit('gen3 primgen: purex2 failed (rc %d)' % p.returncode)
        info = json.load(open(o1.replace('.json.gz', '.primgen.json')))
        shutil.copy(r, s.path('primgen'))
        s.record('primgen', dict(seed=s.a.seed, gauge=s.a.gauge, order=s.a.order_dirs, aware=s.a.primgen_aware, dims=s.a.primgen_dims,
                                 model_base=round(info['base'], 3), model_R0=round(info['R0'], 3), direct_landings=info['nZ']), t0)
    def span(s):
        t0 = time.time(); wd = s.out + '/span'; os.makedirs(wd, exist_ok=True)
        if s.a.from_ and not getattr(s, '_used_from', False): s._used_from = True; src = os.path.abspath(s.a.from_)
        else:
            src = next((p for p in (s.out + '/primgen/o1pg.json.gz', s.out + '/gen2/o1.json.gz') if os.path.exists(p)), None)
            if src is None: raise SystemExit('gen3 span: needs a pre-purex word (run gen2 or primgen first, or --from)')
        so = wd + '/o1span.json.gz'; r = wd + '/r104span.json.gz'
        env = dict(os.environ); env.pop('TK_FREE_BOUNDS', None)
        argv = [PY, '-B', PG + '/spanrelay.py', src, so]; log('RUN', ' '.join(argv[2:]))
        p = subprocess.run(argv, cwd=wd, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        open(wd + '/spanrelay.log', 'w').write(p.stdout)
        if p.returncode or not os.path.exists(so): print(p.stdout[-2000:]); raise SystemExit('gen3 span: spanrelay failed (rc %d)' % p.returncode)
        m = [l for l in p.stdout.splitlines() if l.startswith('SPANRELAY')]
        argv = [PY, '-B', HERE + '/gen2/purex2.py', so, r, '--dims', '4,8', '--xstops', '--lawprune', '--dyfix']; log('RUN', ' '.join(argv[2:]))
        p = subprocess.run(argv, cwd=wd, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        open(wd + '/purex.log', 'w').write(p.stdout)
        if p.returncode or not os.path.exists(r): print(p.stdout[-2000:]); raise SystemExit('gen3 span: purex2 failed (rc %d)' % p.returncode)
        shutil.copy(r, s.path('span')); s.record('span', dict(src=src, spanrelay=m[-1] if m else None), t0)
    def yroute(s):
        t0 = time.time(); src = s.cur('yroute'); wd = s.out + '/yroute'; os.makedirs(wd, exist_ok=True)
        cur = wd + '/w0.json.gz'; shutil.copy(src, cur); acc = []; k = 0
        while True:
            cen = wd + '/ymeet_%d.jsonl' % k
            q = subprocess.run([PY, '-B', GH + '/ymeet.py', cur, cen], cwd=GH, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            log('YROUTE census %d: %s' % (k, ' | '.join(q.stdout.strip().splitlines()[:3])))
            if q.returncode: print(q.stdout[-2000:]); raise SystemExit('ymeet failed')
            if s.a.yroute_census_only: break
            nxt = wd + '/w%d.json.gz' % (k + 1); res = wd + '/apply_%d.jsonl' % k
            p = subprocess.run([PY, '-B', GH + '/ymeet_apply.py', cur, cen, res, '--greedy', nxt, '--max', str(s.a.yroute_max)], cwd=GH, env=child_env(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            open(wd + '/apply.log', 'a').write(p.stdout)
            log('YROUTE apply %d: %s' % (k, (p.stdout.strip().splitlines() or ['(no output)'])[-1]))
            if p.returncode or not os.path.exists(nxt): break
            acc.append(nxt); cur = nxt; k += 1
            if k >= s.a.yroute_rounds: break
        shutil.copy(cur, s.path('yroute')); s.record('yroute', dict(src=src, accepted=acc, census_only=bool(s.a.yroute_census_only)), t0)
    def signal(s):
        t0 = time.time(); src = s.cur('signal'); extra = {}
        if s.a.siggen:   # SIGGEN lane: contract + floor + exact per-root signal re-solve (feeds, reads), never-lose (ext/SIGGEN, module docstring)
            wd = s.out + '/signal'; os.makedirs(wd, exist_ok=True); SG = W + '/ext/SIGGEN'
            q = subprocess.run([PY, '-B', SG + '/contract.py', src, '--floor', '--quiet', '--out', wd + '/contract.json'], cwd=SG, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            open(wd + '/contract.log', 'w').write(q.stdout)
            fl = [l for l in q.stdout.splitlines() if l.startswith('ALL carriers')]
            dst = wd + '/siggen.json.gz'
            argv = [PY, '-B', SG + '/siggen.py', src, dst, '--log', wd + '/siggen.jsonl', '--couriers', '--f0', '--free-bounds', '--workdir', wd + '/steps']
            log('RUN', ' '.join(argv[2:]))
            env = dict(os.environ); env.pop('TK_FREE_BOUNDS', None)
            p = subprocess.run(argv, cwd=SG, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            open(wd + '/siggen.log', 'w').write(p.stdout)
            fin = [l for l in p.stdout.splitlines() if l.startswith('FINAL')]
            ok = p.returncode == 0 and os.path.exists(dst)
            if ok:
                k0, k1 = price(src)['kappa'], price(dst)['kappa']; ok = float(k1) >= float(k0)
            shutil.copy(dst if ok else src, s.path('signal'))
            extra = dict(siggen=True, siggen_kept=ok, contract_floor=fl[0] if fl else None, siggen_final=fin[0][:200] if fin else None, rc=p.returncode)
        else:
            shutil.copy(src, s.path('signal'))
        import gapmap
        c = gapmap.components(json.load(gzip.open(s.path('signal'))))
        s.record('signal', dict(src=src, H_signal_R0=round(c['R0']['H signal (touch owned)'], 2), owned_staging=round(c['owned']['staging'], 2), H_signal_n=c['counts'].get('Hsig'),
                                note='SIGGEN exact re-solve' if s.a.siggen else 'route-B signal built inside gen2; pass-through', **extra), t0)
    def post(s):
        t0 = time.time(); src = s.cur('post'); wd = s.out + '/post'; os.makedirs(wd, exist_ok=True)
        base = wd + '/in.json.gz'; shutil.copy(src, base)
        import rebuild
        fin = rebuild.post(base, [x for x in s.a.post_passes.split(',') if x])
        shutil.copy(fin, s.path('post')); s.record('post', dict(src=src, passes=s.a.post_passes, changed=fin != base), t0)
    def retain(s):
        t0 = time.time(); src = s.cur('retain'); wd = s.out + '/retain'; os.makedirs(wd, exist_ok=True)
        dst = wd + '/retain.json.gz'
        p = subprocess.run([PY, '-B', HERE + '/alignbuild/retain.py', src, dst], cwd=HERE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        open(wd + '/retain.log', 'w').write(p.stdout)
        shutil.copy(dst if p.returncode == 0 and os.path.exists(dst) else src, s.path('retain'))
        s.record('retain', dict(src=src, changed=os.path.exists(dst), summary=(p.stdout.strip().splitlines() or [''])[-1][:300]), t0)
    def screens(s):
        t0 = time.time(); src = s.cur('screens'); ed = s.out + '/eval'
        argv = [PY, '-B', HERE + '/tk.py', 'eval', src, '--screens', s.a.screens, '--rounds', str(s.a.rounds), '--accept', 'fast', '--no-accept-each', '--out', ed, '--force']
        log('RUN', ' '.join(argv[2:]))
        p = subprocess.run(argv, cwd=s.out, env=child_env(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        open(s.out + '/screens.log', 'w').write(p.stdout)
        import eval as E
        b = '%s/words/%s.best.json.gz' % (ed, E.wname(src))
        shutil.copy(b if os.path.exists(b) else src, s.path('screens')); s.record('screens', dict(src=src, screens=s.a.screens, improved=os.path.exists(b), rc=p.returncode), t0)

def add_parsers(sp):
    p = sp.add_parser('gen3', help='gen2 (--lawprune) [or primgen: fan-out landing] + Y-route stage (Y-MEET lever, exact jr) + signal ledger + post fold,hoist + exact screens (genpipe3.py docstring)')
    p.add_argument('--out', default=W + '/ext/GENHUBS/run', help='output dir')
    p.add_argument('--stages', default=DEFAULT_STAGES, help='comma list of: ' + ','.join(STAGES) + ' (default %s; primgen replaces gen2)' % DEFAULT_STAGES)
    p.add_argument('--from', dest='from_', default=None, help='input word for the first stage run (skips gen2)')
    p.add_argument('--seed', type=int, default=0); p.add_argument('--gauge', type=int, default=None)
    p.add_argument('--order-dirs', default='51,30,45,75,120,102,85'); p.add_argument('--d3-dirs', default='120,85,75,51,102,30,45')
    p.add_argument('--yroute-max', type=int, default=200, help='max accepted Y-route sites'); p.add_argument('--yroute-rounds', type=int, default=3, help='census + greedy rounds')
    p.add_argument('--yroute-census-only', action='store_true', help='census only (seconds): no jr, word passes through')
    p.add_argument('--post-passes', default='fold,hoist'); p.add_argument('--screens', default='evretime,retime'); p.add_argument('--rounds', type=int, default=2)
    p.add_argument('--primgen-aware', action='store_true', help='primgen: charge the purex Q_y ender a low read forfeits (gen2: 0 sites)')
    p.add_argument('--primgen-dims', default='4,8', help='primgen: purex2 ender dims (1,2,..,8 = free end frames)')
    p.add_argument('--siggen', action='store_true', help='signal stage: SIGGEN contract/floor + exact per-root feed/read re-solve (never-lose; default = ledger pass-through)')
    p.add_argument('--list', action='store_true', help='print the stages')

def main(a):
    if a.list:
        print('\n'.join(STAGES)); return 0
    R = Run(a)
    for st in [x for x in a.stages.split(',') if x]:
        if st not in STAGES: raise SystemExit('unknown stage %s (have %s)' % (st, ','.join(STAGES)))
        log('--- stage', st); getattr(R, st)()
    return 0
