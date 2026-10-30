#!/usr/bin/env python3
"""tk bulk CORPUS_DIR --out results.jsonl   (BULKEVAL, Oct 28; TOOLING / bulk evaluation, no kappa claim)

Evaluate MANY words in one command and produce a comparable table.  CORPUS_DIR holds `manifest.jsonl` + `words/*.json.gz` (see ext/CORPUS/build_corpus.py)
or is simply a directory of WORD.json[.gz] files (manifest synthesised from the file names).

Steps per word (each a `tk` child process; a failing step is recorded, never fatal):
  price      tk price --json                 exact kappa, legality, events, public, side, profile
  check      tk check --native --json        legality + native frame-pair check (fastnative); if the strict profile refuses, re-run once with
                                             TK_FREE_BOUNDS=1 in the CHILD env (reports `free_legal`: only inventory/bound literals relaxed)
  shipcheck  tk shipcheck --json --base B    shippable as a package?  B = newest adopted profile with the word's public-register count (else 6030)
  gapmap     gapmap.py --json --no-struct W REF   R0 component gap vs REF (default #6030): per-side ledger of the word (X/Y mains, owned, H signal, H residual)
  anatomy    tk anatomy --no-lifetimes --json   skeleton/hub/copy/signal ledger (seconds); `--lifetimes` adds the exact end replay (heavy, ~40 s/new word)
Parallelism: --jobs N worker THREADS, each running one word's steps as sequential child processes (default 2 = the heavy-job limit; run the whole thing as ONE
hq job: `--hq` submits it through $TK_HQ).  Resumable: results.jsonl is append-only, one merged record per (sha); a word whose requested steps are all
recorded OK is skipped (use --force to redo, --steps to choose).  Summary: results.summary.md + results.summary.csv sorted by kappa (also `--summary-only`).
No env mutation at import; the only env change is TK_FREE_BOUNDS=1 in the child of the free re-check."""
import os, sys, json, gzip, glob, csv, time, subprocess, threading, hashlib, re
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
W = HERE
PY = sys.executable
TK = HERE + '/tk.py'
ALL_STEPS = ['price', 'check', 'shipcheck', 'gapmap', 'anatomy']
SCHEMA = 'tk-bulk/1'


def add_parsers(sp):
    p = sp.add_parser('bulk', help='bulk evaluation of a CORPUS dir: price + check --native + shipcheck + gapmap + anatomy per word -> results.jsonl + sorted summary table (resumable)')
    p.add_argument('corpus', help='dir with manifest.jsonl + words/, or a dir of WORD.json[.gz]')
    p.add_argument('--out', help='results.jsonl (default CORPUS/results.jsonl)')
    p.add_argument('--jobs', type=int, default=2, help='worker threads, <=2 heavy (default 2)')
    p.add_argument('--steps', default=','.join(ALL_STEPS), help='comma list of ' + '/'.join(ALL_STEPS))
    p.add_argument('--only', help='comma list of ids (substring match) to evaluate')
    p.add_argument('--limit', type=int, default=0)
    p.add_argument('--ref', default='6030', help='gapmap reference word (profile/words alias or path); default #6030')
    p.add_argument('--lifetimes', action='store_true', help='anatomy: include the exact end replay (heavy)')
    p.add_argument('--force', action='store_true', help='redo steps even if recorded')
    p.add_argument('--summary-only', action='store_true')
    p.add_argument('--top', type=int, default=20)
    p.add_argument('--step-timeout', type=float, default=900)
    p.add_argument('--hq', action='store_true', help='submit this command through $TK_HQ (one heavy slot) and return')
    p.add_argument('--name', default='BULKEVAL')


# ---------------------------------------------------------------- corpus
def content_sha(path):
    op = gzip.open if path.endswith('.gz') else open
    return hashlib.sha256(op(path, 'rb').read()).hexdigest()[:16]


def load_corpus(d):
    d = os.path.abspath(d)
    man = d + '/manifest.jsonl'
    rows = []
    if os.path.exists(man):
        for ln in open(man):
            if ln.strip():
                r = json.loads(ln); r['path'] = os.path.join(d, r['file']); rows.append(r)
    else:
        for f in sorted(glob.glob(d + '/**/*.json*', recursive=True)):
            if not f.endswith(('.json', '.json.gz')) or 'results' in os.path.basename(f) or 'manifest' in os.path.basename(f): continue
            rows.append(dict(id=re.sub(r'\.json(\.gz)?$', '', os.path.basename(f)), kind='?', source='dir', sha=content_sha(f), path=f, claimed_kappa=None))
    return rows


def adopted_publics():
    """public-register count -> newest adopted PR number (profiles/N.json)"""
    best = {}
    for f in glob.glob(HERE + '/profiles/*.json'):
        try:
            j = json.load(open(f))
        except Exception:
            continue
        if j.get('pr') and j.get('public') and not os.path.basename(f).startswith('bit'):
            best[j['public']] = max(best.get(j['public'], 0), int(j['pr']))
    return best


# ---------------------------------------------------------------- steps
def run(cmd, timeout, env_extra=None):
    env = None
    if env_extra:
        env = dict(os.environ); env.update(env_extra)
    t = time.time()
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, env=env)
        return r.returncode, r.stdout, r.stderr, time.time() - t
    except subprocess.TimeoutExpired:
        return 124, '', 'timeout %ds' % timeout, time.time() - t


def jparse(txt):
    """first top-level JSON object in txt (tools may print text around it)"""
    i = txt.find('{')
    if i < 0: return None
    try:
        return json.JSONDecoder().raw_decode(txt[i:])[0]
    except Exception:
        return None


def s_price(path, ctx):
    rc, out, err, dt = run([PY, '-B', TK, 'price', path, '--json'], ctx['to'])
    j = jparse(out)
    if not j or 'kappa' not in j: return dict(ok=False, err=(err or out)[-300:], sec=round(dt, 1))
    sd = j.get('side') or {}
    b = j.get('budgets') or {}
    return dict(ok=True, kappa=float(j['kappa']), kappa_str=j['kappa'], legal=bool(j.get('legal')), nviol=len(j.get('violations') or []), viol=[str(v)[:80] for v in (j.get('violations') or [])[:3]],
                events=j.get('events'), public=j.get('public'), profile=j.get('profile'), side_ok=sd.get('ok'), event_slack=b.get('event_slack'), sumT=j.get('sumT'), sec=round(dt, 1))


def s_check(path, ctx):
    rc, out, err, dt = run([PY, '-B', TK, 'check', path, '--native', '--json'], ctx['to'])
    j = jparse(out)
    if not j: return dict(ok=False, err=(err or out)[-300:], sec=round(dt, 1))
    nat = j.get('native') or {}
    r = dict(ok=True, legal=bool(j.get('legal')), native_bad=nat.get('nbad'), native_pairs=nat.get('distinct_pairs'), legal_native=j.get('legal_native'),
             nviol=len(j.get('violations') or []), viol=[str(v)[:80] for v in (j.get('violations') or [])[:3]], rc=rc, sec=round(dt, 1))
    if not r['legal_native'] and not r['legal']:
        rc2, out2, _, dt2 = run([PY, '-B', TK, 'check', path, '--native', '--json'], ctx['to'], {'TK_FREE_BOUNDS': '1'})
        j2 = jparse(out2)
        if j2: r['free_legal'] = bool(j2.get('legal_native', j2.get('legal'))); r['free_native_bad'] = (j2.get('native') or {}).get('nbad'); r['sec'] = round(dt + dt2, 1)
    return r


def s_shipcheck(path, ctx):
    pub = ctx['public']
    base = str(ctx['bases'].get(pub, 6030))
    rc, out, err, dt = run([PY, '-B', TK, 'shipcheck', path, '--base', base, '--json'], ctx['to'])
    j = jparse(out)
    if not j or 'verdict' not in j: return dict(ok=False, err=(err or out)[-300:], base=base, sec=round(dt, 1))
    return dict(ok=True, base=base, verdict=j['verdict'], fails_at_base=j.get('fails_at_base'), nblock=len(j.get('blockers') or []), admissible_after=j.get('admissible_after'), sec=round(dt, 1))


def s_gapmap(path, ctx):
    rc, out, err, dt = run([PY, '-B', HERE + '/gapmap.py', '--json', '--no-struct', path, ctx['ref']], ctx['to'])
    j = jparse(out)
    if not j or 'rows' not in j: return dict(ok=False, err=(err or out)[-300:], sec=round(dt, 1))
    return dict(ok=True, ref=ctx['ref_name'], rows={r['component']: [round(r['A'], 3), round(r['B'], 3)] for r in j['rows']}, A_total=j['A_total'], B_total=j['B_total'],
                delta_total=j['delta_total'], A_kappa_pred=j['A_kappa_pred'], B_kappa_pred=j['B_kappa_pred'], A_events=(j.get('A') or {}).get('events'), sec=round(dt, 1))


def s_anatomy(path, ctx):
    if not ctx.get('anatomy_ok'): return dict(ok=False, skipped='tk anatomy not available')
    cmd = [PY, '-B', TK, 'anatomy', path, '--json'] + ([] if ctx['lifetimes'] else ['--no-lifetimes'])
    rc, out, err, dt = run(cmd, ctx['to'])
    j = jparse(out)
    if not j or 'invoice' not in j: return dict(ok=False, err=(err or out)[-300:], sec=round(dt, 1))
    inv = j['invoice']; ht = j.get('hubs_total') or {}; sk = j.get('skeleton') or {}
    r = dict(ok=True, R0=inv.get('total'), exact_R0=inv.get('exact_total'), kappa_pred=inv.get('kappa_pred'), classes=inv.get('R0'), counts=inv.get('counts'),
             owned=inv.get('owned'), X_tax=(sk.get('X') or {}).get('tax'), Y_tax=(sk.get('Y') or {}).get('tax'), hub_NET=ht.get('NET'), hub_n=ht.get('nH'),
             copies=(j.get('copies') or {}).get('n_pure_crossing'), copy_events=(j.get('copies') or {}).get('copy_events'), signal=j.get('signal'), lifetimes=ctx['lifetimes'], sec=round(dt, 1))
    if ctx['lifetimes']:
        for k in ('lifetimes', 'attrib', 'life'):
            if k in j and k != 'lifetimes': r['life_' + k] = j[k]
        r['life_keys'] = [k for k in j if k not in ('word', 'content_sha', 'regs', 'events', 'invoice', 'skeleton', 'hubs', 'hubs_total', 'copies', 'signal')]
    return r


def s_retain(path, ctx):
    """RETAINOP (opt-in, `--steps retain`): R-RETAIN greedy (alignbuild/retain.py); a word with accepted sites is written to <corpus>/retain/<id>.json.gz"""
    import re
    outd = ctx.get('retain_dir') or (os.path.dirname(os.path.abspath(path)) + '/retain'); os.makedirs(outd, exist_ok=True)
    dst = '%s/%s' % (outd, os.path.basename(path)); 
    if os.path.exists(dst): os.remove(dst)
    rc, out, err, dt = run([PY, '-B', HERE + '/alignbuild/retain.py', path, dst], ctx['to'])
    m = re.search(r'RETAIN accepted (\d+) sites, kappa ([0-9.]+)', out); b = re.search(r'base legal (\w+) kappa ([0-9.]+)', out)
    if rc or not m or not b: return dict(ok=False, err=(err or out)[-300:], sec=round(dt, 1))
    nsite = len(re.findall(r'^round \d+: [1-9]', out, re.M))
    return dict(ok=True, base_legal=b.group(1) == 'True', base_kappa=float(b.group(2)), n_accepted=int(m.group(1)), kappa=float(m.group(2)), d_kappa=float(m.group(2)) - float(b.group(2)),
                out=dst if int(m.group(1)) else None, sec=round(dt, 1))


STEP_FN = dict(price=s_price, check=s_check, shipcheck=s_shipcheck, gapmap=s_gapmap, anatomy=s_anatomy, retain=s_retain)


# ---------------------------------------------------------------- results store
def load_results(out):
    res = {}
    if os.path.exists(out):
        for ln in open(out):
            if not ln.strip(): continue
            try:
                r = json.loads(ln)
            except Exception:
                continue
            cur = res.setdefault(r['sha'], dict(sha=r['sha'], steps={}))
            cur.update({k: v for k, v in r.items() if k != 'steps'})
            cur['steps'].update(r.get('steps', {}))
    return res


def needed(rec, steps, force, lifetimes):
    """steps still to do for a recorded sha: missing, failed before (retry), skipped before, or anatomy needing lifetimes"""
    if force or not rec: return list(steps)
    out = []
    for s in steps:
        st = rec['steps'].get(s)
        if not st or not st.get('ok') or (s == 'anatomy' and lifetimes and not st.get('lifetimes')):
            out.append(s)
    return out


# ---------------------------------------------------------------- summary
SIDE_COLS = [('X mains', 'X'), ('Y mains', 'Y'), ('owned (O)', 'O'), ('H signal (touch owned)', 'Hsig'), ('H residual bottom (mid<4.5)', 'Hbot'), ('H residual central (mid=4.5)', 'Hmid'), ('H residual top (mid>4.5)', 'Htop')]


def row_of(rec):
    s = rec['steps']; p = s.get('price', {}); c = s.get('check', {}); sh = s.get('shipcheck', {}); g = s.get('gapmap', {}); a = s.get('anatomy', {})
    ck = rec.get('claimed_kappa')
    k = p.get('kappa')
    row = dict(id=rec.get('id'), kind=rec.get('kind'), source=rec.get('source'), sha=rec['sha'][:8], kappa=k, claimed=ck,
               d_claim_ppm=(round((k - ck) / ck * 1e6, 1) if (k and ck) else None), events=p.get('events'), public=p.get('public'), profile=p.get('profile'),
               legal=p.get('legal'), native=('ok' if (c.get('ok') and c.get('legal_native')) else ('FREE-ok' if c.get('free_legal') else ('BAD' if c.get('ok') else None))),
               native_bad=c.get('native_bad'), ship=(sh.get('verdict') or '').split(' (')[0][:34], ship_base=sh.get('base'), R0=g.get('A_total') or a.get('R0'),
               law_kappa=g.get('A_kappa_pred') or a.get('kappa_pred'), dR0_ref=(round(g['delta_total'], 1) if g.get('ok') else None))
    rows = g.get('rows') or {}
    for full, short in SIDE_COLS:
        row['R0_' + short] = round(rows[full][0], 1) if full in rows else None
    row['hubNET'] = a.get('hub_NET'); row['copies'] = a.get('copies'); row['Xtax'] = a.get('X_tax'); row['Ytax'] = a.get('Y_tax')
    row['valid'] = bool(p.get('legal')) and (c.get('native_bad') in (0, None)) and bool(c.get('ok', True))
    row['failed'] = ','.join(k for k, v in s.items() if not v.get('ok') and not v.get('skipped')) or None
    return row


def write_summary(res, out, top):
    rows = [row_of(r) for r in res.values() if 'price' in r['steps']]
    rows.sort(key=lambda r: (not r['valid'], -round(r['kappa'] or 0, 13), r['events'] or 0, r['id']))      # VALID (price-legal + native 0 bad) words first: an illegal/partial word's kappa is not comparable
    base = out[:-6] if out.endswith('.jsonl') else out
    cols = list(rows[0].keys()) if rows else []
    with open(base + '.summary.csv', 'w', newline='') as f:
        w = csv.writer(f); w.writerow(['rank'] + cols)
        for i, r in enumerate(rows, 1): w.writerow([i] + [r[c] for c in cols])

    def fmt(v):
        if v is None: return ''
        if isinstance(v, float): return ('%.10f' % v) if abs(v) < 1 and v != 0 else ('%.1f' % v)
        return str(v)
    md = ['# bulk evaluation summary (%d words, sorted: valid words by exact kappa, then illegal/partial)\n' % len(rows),
          'Columns: R0_* = per-side R0 ledger of the word (gapmap components: X/Y mains, owned O, H signal, H residual by mid-dim band); dR0_ref = total R0 minus reference; '
          'native = check --native (FREE-ok = legal only with TK_FREE_BOUNDS, i.e. package inventory literals); ship = tk shipcheck verdict vs ship_base; d_claim_ppm = (exact - claimed)/claimed.\n']
    show = ['rank', 'id', 'kappa', 'claimed', 'd_claim_ppm', 'events', 'public', 'valid', 'native', 'ship', 'R0', 'dR0_ref'] + ['R0_' + s for _, s in SIDE_COLS] + ['hubNET', 'failed']
    nvalid = sum(r['valid'] for r in rows)
    md.append('## top %d valid words (%d of %d are price-legal with 0 bad native pairs; illegal/partial words are listed last and their kappa is NOT comparable)\n' % (top, nvalid, len(rows)))
    md.append('| ' + ' | '.join(show) + ' |'); md.append('|' + '---|' * len(show))
    for i, r in enumerate(rows[:top], 1):
        d = dict(r, rank=i); md.append('| ' + ' | '.join(fmt(d.get(c)) for c in show) + ' |')
    md.append('\n## all words (valid first by kappa, then illegal/partial)\n'); md.append('| ' + ' | '.join(show) + ' |'); md.append('|' + '---|' * len(show))
    for i, r in enumerate(rows, 1):
        d = dict(r, rank=i if r['valid'] else '-'); md.append('| ' + ' | '.join(fmt(d.get(c)) for c in show) + ' |')
    open(base + '.summary.md', 'w').write('\n'.join(md) + '\n')
    return rows


# ---------------------------------------------------------------- main
def main(a):
    if a.hq:
        cmd = [PY, '-B', TK, 'bulk', a.corpus, '--jobs', str(a.jobs), '--steps', a.steps, '--ref', a.ref, '--top', str(a.top), '--step-timeout', str(a.step_timeout)]
        for flag, v in (('--out', a.out), ('--only', a.only)):
            if v: cmd += [flag, v]
        if a.lifetimes: cmd.append('--lifetimes')
        if a.force: cmd.append('--force')
        if a.limit: cmd += ['--limit', str(a.limit)]
        r = subprocess.run(['env', 'THREADS=2', W + '/$TK_HQ', a.name, '14400'] + cmd, capture_output=True, text=True)
        print(r.stdout + r.stderr); return r.returncode
    corpus = load_corpus(a.corpus)
    out = os.path.abspath(a.out or (os.path.abspath(a.corpus) + '/results.jsonl'))
    steps = [s for s in a.steps.split(',') if s]
    bad = [s for s in steps if s not in STEP_FN]
    if bad: raise SystemExit('unknown step %s' % bad)
    res = load_results(out)
    if a.summary_only:
        write_summary(res, out, a.top); print('summary ->', out[:-6] + '.summary.md'); return 0
    if a.only:
        keys = a.only.split(','); corpus = [r for r in corpus if any(k == r['id'] or k in r['id'] for k in keys)]
    if a.limit: corpus = corpus[:a.limit]
    # reference word for gapmap
    ref = a.ref
    ref_path = None
    for r in load_corpus(a.corpus):
        if r['id'] in (ref, 'pr' + ref): ref_path = r['path']
    if ref_path is None:
        sys.path.insert(0, HERE)
        import tkcommon
        ref_path = tkcommon.resolve(ref) if (ref in tkcommon.ALIASES or os.path.exists(ref)) else None
    if ref_path is None and os.path.exists(HERE + '/words/%s.json.gz' % ref): ref_path = HERE + '/words/%s.json.gz' % ref
    if ref_path is None: raise SystemExit('bulk: gapmap reference %r not found' % ref)
    bases = adopted_publics()
    anatomy_ok = subprocess.run([PY, '-B', TK, 'anatomy', '-h'], capture_output=True).returncode == 0
    lock = threading.Lock(); done = [0]
    todo = []
    for r in corpus:
        need = needed(res.get(r['sha']), steps, a.force, a.lifetimes)
        if need: todo.append((r, need))
    print('bulk: %d words in corpus, %d to (re)evaluate, %d already complete; out=%s' % (len(corpus), len(todo), len(corpus) - len(todo), out), flush=True)

    def work(item):
        r, need = item
        ctx = dict(to=a.step_timeout, bases=bases, ref=ref_path, ref_name=ref, anatomy_ok=anatomy_ok, lifetimes=a.lifetimes, public=r.get('public'))
        got = {}
        t = time.time()
        for s in [x for x in ALL_STEPS + ['retain'] if x in need]:            # fixed order: price first
            try:
                got[s] = STEP_FN[s](r['path'], ctx)
            except Exception as e:                               # never fatal
                got[s] = dict(ok=False, err='exception %r' % (e,))
        rec = {k: r.get(k) for k in ('id', 'kind', 'source', 'pr', 'sha', 'claimed_kappa', 'events', 'public')}
        rec.update(schema=SCHEMA, steps=got, t=round(time.time() - t, 1), at=time.strftime('%Y-%m-%d %H:%M:%S'))
        with lock:
            with open(out, 'a') as f: f.write(json.dumps(rec) + '\n')
            done[0] += 1
            p = got.get('price', {})
            print('[%d/%d] %-34s %s  %s  %.0fs' % (done[0], len(todo), r['id'], ('k=%.10f' % p['kappa']) if p.get('ok') else 'price:FAIL',
                  ' '.join('%s:%s' % (k, 'ok' if v.get('ok') else ('skip' if v.get('skipped') else 'FAIL')) for k, v in got.items()), time.time() - t), flush=True)
        return rec

    os.makedirs(os.path.dirname(out), exist_ok=True)
    with ThreadPoolExecutor(max_workers=max(1, min(a.jobs, 2))) as ex:
        list(ex.map(work, todo))
    res = load_results(out)
    rows = write_summary(res, out, a.top)
    print('summary ->', out[:-6] + '.summary.md', '(%d rows)' % len(rows))
    return 0
