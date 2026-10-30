"""tk rebuild WORD [--sides skeleton,routing,hubs,markets,signal] [--out FILE] [--workdir DIR] [--manifest FILE] [--resume] [--no-checks] [--json]

Re-derive the events of the selected sides of a word from the pinned rule builders (alignbuild/: SKELORIGIN sb, YROUTE yb, HUBRULES/OWNEDHUB hubs,
MKTCOMPACT/FULLWORD markets, SIGPIN signal), composed in the verified order, each step accepted only if LEGAL at the input word's exact kappa
(|dk| < 1e-13).  On #6030 with all sides it reproduces FULL_final: kappa .003125811557911897, 23333 events (cap 26000), SPAN5/JR 0, native 0 bad.
Exit 0 iff the final word has the input kappa exactly, is legal and has <= --max-events events.  Heavy (~65 min with markets): run directly (or through an optional job-queue wrapper, $TK_HQ).
Scope: TOOLING / composition.  The default manifest (alignbuild/data/manifest_6030.json) and the (source, reader-Y) incidence (alignbuild/data/y1,y4.pkl)
carry #6030's frame/register ids, so other words must share that numbering (the octet class around #6030) or bring their own manifest; steps that do not
solve are logged GAP and skipped (never-lose).  Details: module docstring, MAP.md."""
import sys, os, json
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path: sys.path.insert(0, HERE)


def add_parsers(sp):
    p = sp.add_parser('rebuild', help='re-derive skeleton/routing/hubs/markets/signal of a word from the pinned rule builders at exact kappa (alignbuild/; hq for the full chain)')
    p.add_argument('word', help='path or name in words/ (e.g. 6030)')
    p.add_argument('--sides', default='skeleton,routing,hubs,markets,signal', help='comma list of skeleton,routing,hubs,markets,signal (routing is fused into skeleton)')
    p.add_argument('--out', help='final word (default alignbuild/out/rebuild_NAME/final.json.gz)')
    p.add_argument('--workdir', help='step words + logs (default alignbuild/out/rebuild_NAME)')
    p.add_argument('--manifest', help='plan JSON (default alignbuild/data/manifest_6030.json)')
    p.add_argument('--resume', action='store_true', help='reuse step files already in --workdir (gate re-evaluated)')
    p.add_argument('--no-checks', action='store_true', help='skip validate.py --all and check --native on the final word')
    p.add_argument('--max-events', type=int, default=26000, help='0 = no event cap (CAPFREE)'); p.add_argument('--json', action='store_true')
    p.add_argument('--gate', default='exact', choices=['exact', 'up'], help='RULEAUDIT (opt-in): step acceptance; exact = |dk|<1e-13 vs the input (default), up = any legal step with kappa >= the current accepted kappa')
    p.add_argument('--post', default='', help='GENUPGRADE (opt-in) constructor passes after the exact-kappa chain, in order: fold (R-FOLD, Lemma 6, RULEMINE fold.py; heavy ~15 min/site), hoist (H-HOIST gauge stop drop, alignbuild/hoist.py), retain (R-RETAIN retained-operand stop drop, alignbuild/retain.py; module docstring). Each accepted only if LEGAL with kappa strictly up; writes OUT.post.json.gz. On #6030: fold,hoist reaches r245g kappa .0031283932032711 exactly; fold,hoist,retain reaches W6167 .003128652015904 exactly')


def main(a):
    from alignbuild import api
    name = os.path.basename(a.word).split('.')[0]
    wd = os.path.abspath(a.workdir or os.path.join(HERE, 'alignbuild', 'out', 'rebuild_' + name))
    out = a.out or os.path.join(wd, 'final.json.gz')
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    import tkcommon as C
    prof0 = os.environ.get('TK_PROFILE') or C.profile_of(C.load(api.resolve(a.word))[1])[0]      # fold/hoist outputs keep the input's inventory: judge them under its profile
    s = api.rebuild(a.word, out, [x for x in a.sides.split(',') if x], workdir=wd, manifest=a.manifest, resume=a.resume, checks=not a.no_checks, max_events=a.max_events, log=lambda *x: print(*x, flush=True), gate=getattr(a, 'gate', 'exact'))
    if a.json: print(json.dumps({k: v for k, v in s.items() if k != 'records'}, indent=1, default=str))
    else:
        print('kappa in %.15g out %s  exact=%s legal=%s | events %s (<= %d: %s) | steps ok %d/%d, gaps %s | %ds' % (s['kappa_in'], s['kappa_str'], s['exact'], s['legal'], s['events'], a.max_events, s['events_ok'], s['steps_ok'], s['steps'], s['gaps'], s['seconds']))
        for k, v in s.get('checks', {}).items(): print('  check', k, v)
        print('wrote', s['out'])
    ok = s['exact'] and s['legal'] and s['events_ok'] and all(s.get('checks', {}).get(k, True) for k in ('validate_ok', 'check_ok'))
    if a.post: post(s['out'], [x for x in a.post.split(',') if x], prof0)
    return 0 if ok else 1


def post(word, passes, prof0=None):
    """GENUPGRADE: constructor post-passes (never-lose: a pass that finds no site / fails leaves the word unchanged).  -> path of the final word"""
    import subprocess
    cur = word; base = word[:-8] if word.endswith('.json.gz') else word
    for ps in passes:
        dst = '%s.%s.json.gz' % (base, ps)
        if ps == 'fold': cmd = [sys.executable, '-B', os.path.join(HERE, 'alignbuild', 'fold.py'), cur, dst]; cwd = HERE
        elif ps == 'hoist': cmd = [sys.executable, '-B', os.path.join(HERE, 'alignbuild', 'hoist.py'), cur, dst]; cwd = HERE
        elif ps == 'retain': cmd = [sys.executable, '-B', os.path.join(HERE, 'alignbuild', 'retain.py'), cur, dst]; cwd = HERE
        else: raise SystemExit('rebuild --post: unknown pass %s (fold, hoist, retain)' % ps)
        env = dict(os.environ)
        if not os.environ.get('TK_PROFILE'):      # fold/hoist keep the input's inventory (its profile); retain adds a lifetime, so it is judged under the newest profile of the family
            if ps != 'retain' and prof0: env['TK_PROFILE'] = prof0
        p = subprocess.run(cmd, cwd=cwd, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        print(p.stdout[-1500:], flush=True)
        if p.returncode == 0 and os.path.exists(dst): cur = dst; print('POST %s -> %s' % (ps, dst), flush=True)
        else: print('POST %s: no change (rc %d)' % (ps, p.returncode), flush=True)
    if cur != word:
        import shutil; shutil.copy(cur, base + '.post.json.gz'); print('POST final', base + '.post.json.gz', flush=True)
    return cur
