"""alignbuild.api -- the five pinned builders behind ONE interface (BULKGEN, Oct 28; notes toolkit/module docstring).

Every side is a strip-and-rebuild solver: it deletes one class of events/stops of a word and re-solves them from the rules, and it is accepted
only if the result is LEGAL at kappa == the kappa of the word it was given (|dk| < 1e-13, exact `tk price`).  So rebuild(word) returns a word
with the SAME exact kappa whose events of the selected sides were produced by rules, not copied from the swarm.

    word in, word out:   step(side_script, word_in, word_out, argv) -> StepResult      (one builder call, one subprocess)
    exact kappa check:   kappa_of(path) -> dict(kappa, legal, events, side_ok, ...)     (`tk price --json`, Decimal-50)
    composed chain:      rebuild(word, out, sides, ...) -> dict                          (the verified FULLWORD order, filtered by `sides`)

sides (names of `tk rebuild --sides`): skeleton (SKELORIGIN sb -> skeleton.py), routing (YROUTE yb -> routing.py; fused: skeleton.py calls it, so
`routing` selects the same steps as `skeleton`), hubs (HUBRULES hubs.py + OWNEDHUB hubs_owned.py), markets (MKTCOMPACT markets.py + MKTO2/FULLWORD
markets_full.py), signal (SIGPIN sigside.py).  The plan (which octets / hub frames / duals / roots, in which order, with which flags) is a JSON
manifest; data/manifest_6030.json is #6030's.  No environment variable is set here or at import; builders get none."""
import os, sys, json, gzip, subprocess, time, shutil

HERE = os.path.dirname(os.path.abspath(__file__))
TK = os.path.dirname(HERE)
W = TK
PY = sys.executable
SIDES = ('skeleton', 'routing', 'hubs', 'markets', 'signal')
TOL = 1e-13
MANIFEST6030 = os.path.join(HERE, 'data', 'manifest_6030.json')


def resolve(spec):
    """path to WORD.json[.gz] or a name in toolkit/words/ (e.g. 6030)"""
    for p in (spec, os.path.join(TK, 'words', spec + '.json.gz'), os.path.join(TK, 'words', spec + '.json'), os.path.join(TK, 'words', spec)):
        if os.path.isfile(p): return os.path.abspath(p)
    raise SystemExit('rebuild: no such word %r' % spec)


def nevents(path):
    op = gzip.open if path.endswith('.gz') else open
    with op(path, 'rt') as fh: return len(json.load(fh)['program'])


def kappa_of(path):
    """exact `tk price --json` of a word file (Decimal-50 kappa string -> float in 'kappa'; also legal, events, side_ok, event_slack)"""
    p = subprocess.run([PY, '-B', os.path.join(TK, 'tk.py'), 'price', path, '--json', '--no-cache'], capture_output=True, text=True, cwd=W)
    txt = p.stdout
    try: o = json.loads(txt[txt.index('{'):])
    except Exception: return dict(kappa=None, legal=False, events=None, side_ok=False, error=(p.stdout + p.stderr)[-400:])
    s = o.get('side', {})
    return dict(kappa=float(o['kappa']), kappa_str=o['kappa'], legal=bool(o['legal']), events=o['events'], side_ok=(s.get('ok', None) if isinstance(s, dict) and 'ok' in s else not bool(o.get('violations'))),
                event_slack=o.get('budgets', {}).get('event_slack'), sha=o.get('sha'), violations=o.get('violations', []))


def _result_line(out):
    res = [l for l in out.splitlines() if 'RESULT' in l]
    return (res[-1] if res else (out.strip().splitlines() or ['NO OUTPUT'])[-1]).strip()


def step(script, argv, out_path, cwd=None, timeout=None):
    """run ONE builder script (alignbuild/<script>) in its own process: returns (output_exists, result_line, stdout+stderr)"""
    if os.path.exists(out_path): os.remove(out_path)
    p = subprocess.run([PY, '-B', os.path.join(HERE, script)] + [str(a) for a in argv], capture_output=True, text=True, cwd=cwd or W, timeout=timeout)
    o = p.stdout + p.stderr
    return os.path.exists(out_path), _result_line(o), o


def load_manifest(spec=None):
    return json.load(open(spec or MANIFEST6030))


def expand(manifest, sides):
    """the ordered step list of the manifest restricted to `sides` (routing == skeleton: fused)"""
    want = set(sides)
    if 'routing' in want: want.add('skeleton')
    bad = want - set(SIDES)
    if bad: raise SystemExit('rebuild: unknown side(s) %s (choose from %s)' % (sorted(bad), ','.join(SIDES)))
    steps = []
    for blk in manifest['plan']:
        if blk['side'] not in want: continue
        for it in blk['items']:
            if blk['kind'] == 'octets': steps.append(dict(side='skeleton', label='skel%d' % it, script=blk['script'], tail=['--octet', it] + list(blk.get('flags', [])), order='wo'))
            elif blk['kind'] in ('hub', 'dual'):
                steps.append(dict(side=blk['side'], label='%s%d' % ('h' if blk['kind'] == 'hub' else 'm', it), script=blk['script'], mid=[it], tail=list(blk.get('flags', [])), order='wgo'))
            elif blk['kind'] == 'root':
                for mode in blk['modes']:
                    regs = blk.get('regs', {}).get(str(it))
                    steps.append(dict(side='signal', label='g%d_%s' % (it, mode), script=blk['script'], tail=['--root', it, '--mode', mode, '--stops', '--time', 'all', '--freebounds'] + (['--regs', regs] if regs else []), order='wo'))
    return steps


def _argv(st, cur, nxt):
    if st['order'] == 'wo': return [cur, nxt] + st['tail']
    return [cur] + st['mid'] + [nxt] + st['tail']


def _rebuild(word, out, sides=SIDES, workdir=None, manifest=None, resume=False, checks=True, max_events=26000, log=print, kref=None, gate='exact'):
    """Run the composed chain on `word` (path).  Each step runs on the previous accepted output and is accepted only if the output exists, is legal and
    |kappa - kappa(word)| < 1e-13; a failing step is logged GAP and skipped (never-lose).  Returns a summary dict (also written to workdir/rebuild.json)."""
    word = resolve(word); out = os.path.abspath(out)
    workdir = os.path.abspath(workdir or os.path.join(HERE, 'out', 'rebuild_' + os.path.basename(word).split('.')[0]))
    os.makedirs(workdir, exist_ok=True)
    m = load_manifest(manifest) if not isinstance(manifest, dict) else manifest
    steps = expand(m, sides)
    k0 = kappa_of(word) if kref is None else dict(kappa=kref)
    log('start %s: kappa %s, %d steps (%s)' % (os.path.basename(word), k0.get('kappa_str', k0['kappa']), len(steps), ','.join(sides)))
    cur = word; recs = []; t0 = time.time(); kcur = k0['kappa']
    for i, st in enumerate(steps):
        nxt = os.path.join(workdir, 's%02d_%s.json.gz' % (i, st['label'])); ts = time.time()
        if resume and os.path.exists(nxt): exists, res, o = True, '(resumed)', ''
        else: exists, res, o = step(st['script'], _argv(st, cur, nxt), nxt)
        ok = False; kk = None
        if exists:
            kk = kappa_of(nxt); ok = kk['kappa'] is not None and kk['legal'] and (abs(kk['kappa'] - k0['kappa']) < TOL if gate == 'exact' else kk['kappa'] > kcur - TOL)   # RULEAUDIT --gate up: accept any legal step that does not lower kappa
        open(os.path.join(workdir, 's%02d_%s.log' % (i, st['label'])), 'w').write(o)
        recs.append(dict(i=i, side=st['side'], label=st['label'], ok=ok, kappa=(kk or {}).get('kappa'), events=(kk or {}).get('events'), result=res[:200], seconds=round(time.time() - ts, 1)))
        log('%02d %-8s %-12s %s events %s  %s  [%ds]' % (i, st['side'], st['label'], 'OK ' if ok else 'GAP', recs[-1]['events'], res[:110], recs[-1]['seconds']))
        if ok: cur = nxt; kcur = max(kcur, kk['kappa'])
    shutil.copyfile(cur, out)
    fin = kappa_of(out)
    summ = dict(word=word, out=out, sides=list(sides), kappa_in=k0['kappa'], kappa_out=fin['kappa'], kappa_str=fin.get('kappa_str'), exact=(fin['kappa'] is not None and abs(fin['kappa'] - k0['kappa']) < TOL),
                legal=fin['legal'], events=fin['events'], events_ok=(fin['events'] is not None and (max_events<=0 or fin['events'] <= max_events)), steps_ok=sum(r['ok'] for r in recs), steps=len(recs),
                gaps=[r['label'] for r in recs if not r['ok']], seconds=round(time.time() - t0), records=recs)
    if checks: summ['checks'] = final_checks(word, out)
    json.dump(summ, open(os.path.join(workdir, 'rebuild.json'), 'w'), indent=1)
    return summ


def final_checks(base, new):
    """SPAN5/JR laws on all frames (surgery/validate.py --all, base vs new) and the native pair check (tk check --native)"""
    c = {}
    p = subprocess.run([PY, '-B', os.path.join(TK, 'surgery', 'validate.py'), base, new, '--all'], capture_output=True, text=True, cwd=W)
    o = p.stdout + p.stderr
    c['validate_new_violations'] = [l for l in o.splitlines() if l.strip().startswith(('SPAN5', 'JR'))]
    c['validate_ok'] = bool(c['validate_new_violations']) and all(l.rstrip().endswith('[]') for l in c['validate_new_violations'])
    p = subprocess.run([PY, '-B', os.path.join(TK, 'tk.py'), 'check', '--native', new], capture_output=True, text=True, cwd=W)
    o = p.stdout + p.stderr
    c['check_native_tail'] = o.strip().splitlines()[-2:]
    c['check_ok'] = ' LEGAL' in o and ' 0 bad' in o
    return c


def rebuild(word, out, sides=SIDES, **kw):
    """Run the composed chain (see _rebuild).  The builders' step outputs are intermediate words, so they are judged under the INPUT word's verifier profile
    (not the newest profile of its family); TK_PROFILE is pinned for the duration of the call and restored afterwards."""
    old = os.environ.get('TK_PROFILE'); pinned = False
    try:
        if not old:
            sys.path.insert(0, TK) if TK not in sys.path else None
            import tkcommon as _C
            os.environ['TK_PROFILE'] = _C.profile_of(_C.load(resolve(word))[1])[0]; pinned = True
        return _rebuild(word, out, sides, **kw)
    finally:
        if pinned: os.environ.pop('TK_PROFILE', None)
