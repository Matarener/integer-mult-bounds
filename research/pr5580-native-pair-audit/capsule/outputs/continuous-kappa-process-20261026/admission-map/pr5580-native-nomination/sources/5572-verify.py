#!/usr/bin/env python3
"""Independent native-map inventory, caller binding, replay and funding audit of PR5551.  Apache-2.0.

Prepared for Matarener with Claude (Anthropic), via Claude Code.
Layers (all on the canonical research/p104-joint-contact word):
  1. own exact replay of the PR5551 and PR5545 words (no source imports) and the coupled-contact delta;
  2. Chris R / Clear1nsight's byte-pinned PR5550 caller and target-binding checker, run on the PR5551
     word with four literal input lines changed in a temporary copy (positive control: unchanged
     PR5550 output on PR5545);
  3. dense all-column comparison, with absolute phase, of every distinct native MOVE map, every helper
     endpoint normalizer and every intrinsic main adapter of the PR5551 word, using PR5548's credited
     dense interpreter.  Default: a fixed deterministic subset (all added maps, every helper endpoint,
     every adapter and every 32nd MOVE map) compared with FULL-CHECK.json; --full checks every map;
  4. own decimal interval engine for the raw moment crossing and the claimed/tested savings.
"""
from collections import Counter
from decimal import Decimal, getcontext
from fractions import Fraction as Q
from hashlib import sha256
from multiprocessing import Pool
from pathlib import Path
import gzip
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WORD = ROOT/'research/p104-joint-contact/WORD.json.gz'
RESULT = ROOT/'research/p104-joint-contact/RESULT.json'
PRED = ROOT/'research/p104-full-frame-contact/WORD.json.gz'
AUDIT = ROOT/'research/p104-caller-independent-audit'
CHECK = 'outputs/p104-caller-route-audit-v2-20261025/check.py'
EXPECTED_5550 = 'b51a7d19c10faea7d569a48e9536db8ba1e7418f8dd8dfb25646cc87cc9c4009'
CLIFFORD = ROOT/'research/p104-native-channel/vendor/clifford_exact.py'
LITERAL = ROOT/'research/p104-native-channel/vendor/native_verify.py'
DENSE = ROOT/'research/p104-contact-independent-audit/capsule/outputs/p104-native-contact-audit-20261025/check.py'
PROFILE = {4: 51, 5: 36, 7: 24, 8: 122, 9: 294}
ADDED = {(17, 720), (17, 782), (615, 207), (775, 207)}

REPLACEMENTS = (
    ("    word = read(PRIOR/'sources/contact/WORD.json.gz')\n",
     "    word = read(Path(os.environ['P104_WORD']))\n"
     "    FREE = json.loads(Path(os.environ['P104_INVOICE']).read_text())\n"),
    ("helper_profile == Counter({4:51, 5:36, 7:24, 8:122, 9:294})",
     "helper_profile == Counter({int(k):v for k,v in json.loads(os.environ['P104_PROFILE']).items()})"),
    ("    costs = source['complete_cost']\n",
     "    costs = FREE\n"),
    ("nr['local_routes'] == 5334000 and sum(paid_local.values()) == 3624",
     "nr['local_routes'] == (sum(paid_local.values())+2*527+208+4*104+4*8)*1000 and sum(paid_local.values()) == int(os.environ['P104_MOVES'])"),
)


def need(ok, why):
    if not ok:
        raise ValueError(why)


def hashlib_file(path):
    return sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    raw = Path(path).read_bytes()
    return json.loads(gzip.decompress(raw) if str(path).endswith('.gz') else raw)


def authenticate():
    for row in json.loads((HERE/'SOURCES.json').read_text())['files']:
        need(hashlib_file(ROOT/row['path']) == row['sha256'], 'source pin '+row['path'])
    for name, digest in json.loads((AUDIT/'CAPSULE-INVENTORY.json').read_text())['files'].items():
        if name.startswith('capsule/'):
            need(hashlib_file(AUDIT/name) == digest, 'PR5550 capsule byte '+name)


# ---------------------------------------------------------------- layer 1: own replay
def span(basis):
    s = {0}
    for v in basis:
        need(type(v) is int and 0 < v < 512 and v not in s, 'independent binary basis')
        s |= {x ^ v for x in s}
    return frozenset(s)


def replay(w):
    S = [span(f) for f in w['frames']]
    n = w['public']
    live = set(w['live'])
    cur = list(w['initial'])+[None]*8
    rows = [{r: Q(1)} for r in range(n+8)]
    owned, paid, peak = set(), Counter(), 0
    for e in w['program']:
        op, r = e[0], e[1]
        if op == 'MOVE':
            a, b, private = e[2], e[3], e[4]
            need(cur[r] == a and (r in owned) == private, 'transport source and ownership')
            need(S[b] < S[a] if private else S[a] < S[b], 'strict nesting')
            paid[abs(len(w['frames'][b])-len(w['frames'][a]))] += 1
            cur[r] = b
        elif op == 'INIT':
            need(r >= n and r not in owned, 'owned initialization')
            owned.add(r)
            peak = max(peak, len(owned))
            rows[r], cur[r] = {}, e[2]
        elif op == 'CLEAR':
            need(r in owned and cur[r] == e[2], 'owned erasure')
            owned.discard(r)
            rows[r], cur[r] = {}, None
        else:
            q, f = Q(e[-2]), e[-1]
            need(q != 0 and cur[r] == f, 'destination chart')
            if op == 'SCALE':
                rows[r] = {k: q*v for k, v in rows[r].items()}
            else:
                s = e[2]
                need(s != r and cur[s] == f, 'common chart')
                if op == 'COPY':
                    need(r in owned and not rows[r], 'COPY into cleared owned field')
                    rows[r] = {k: q*v for k, v in rows[s].items()}
                else:
                    need(op == 'ADD', 'opcode')
                    t = dict(rows[r])
                    for k, v in rows[s].items():
                        t[k] = t.get(k, 0)+q*v
                    rows[r] = {k: v for k, v in t.items() if v}
    need(not owned and peak == 1 and cur[:n] == w['final'], 'public and owned exits')
    for r in range(n+8):
        expected = {r: Q(1)} if r < n else {}
        if r-112 in live:
            expected[r-112] = Q(1)
        need(rows[r] == expected, 'endpoint row %d' % r)
    main = live | {r+112 for r in live}
    helpers = Counter(len(w['frames'][w['final'][r]])-len(w['frames'][w['initial'][r]]) for r in range(n) if r not in main)
    return paid, helpers, S


def layer1(new, old):
    pn, hn, Sn = replay(new)
    po, ho, So = replay(old)
    need(hn == ho == Counter(PROFILE), 'helper profile retained')
    strip = lambda w: [e[:-1] if e[0] in ('ADD', 'COPY', 'SCALE') else e[:2] for e in w['program'] if e[0] != 'MOVE']
    need(strip(new) == strip(old), 'scalar and owned program identical up to frame labels')
    sn = [e for e in new['program'] if e[0] != 'MOVE']
    so = [e for e in old['program'] if e[0] != 'MOVE']
    edits = Counter(x[0] for x, y in zip(so, sn) if So[x[-1]] != Sn[y[-1]])
    sites = [[k, x[1], x[2]] for k, (x, y) in enumerate(zip(so, sn)) if x[0] == 'ADD' and So[x[-1]] != Sn[y[-1]]]
    delta = {r: pn[r]-po[r] for r in sorted(set(pn) | set(po)) if pn[r] != po[r]}
    need(dict(edits) == {'ADD': 6, 'SCALE': 15}, 'six ADD and fifteen SCALE chart edits')
    need(delta == {1: 2, 2: -3, 3: 1, 4: -1, 5: 1}, 'local paid delta 2H1-3H2+H3-H4+H5')
    need(all(So[old[k][r]] == Sn[new[k][r]] for k in ('initial', 'final') for r in range(new['public'])), 'all public endpoint spans retained')
    return {'paid_local': {str(k): v for k, v in sorted(pn.items())}, 'moves': sum(pn.values()), 'helper_profile': {str(k): v for k, v in sorted(hn.items())},
            'chart_edits': dict(edits), 'add_sites': sites, 'local_paid_delta': {str(k): v for k, v in delta.items()}, 'endpoint_rows_checked': new['public']+8}


# ---------------------------------------------------------------- layer 2: PR5550 caller checker
def run_checker(work, word_path, invoice, profile, moves):
    inv = work/'invoice.json'
    inv.write_text(json.dumps(invoice))
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', P104_WORD=str(word_path), P104_INVOICE=str(inv),
               P104_PROFILE=json.dumps(profile), P104_MOVES=str(moves))
    env.pop('P104_TRACE_FILE', None)
    command = [sys.executable, '-X', 'pycache_prefix='+str(work/'bytecode')]+(['-O'] if sys.flags.optimize else [])+['-B', str(work/'capsule'/CHECK.replace('check.py', 'check_free.py'))]
    done = subprocess.run(command, cwd=work/'capsule', env=env, capture_output=True, timeout=300)
    return done.returncode, done.stdout, done.stderr.decode(errors='replace')


def layer2(cost):
    with tempfile.TemporaryDirectory(prefix='p104-5551-caller-') as tmp:
        work = Path(tmp)
        shutil.copytree(AUDIT/'capsule', work/'capsule')
        text = (work/'capsule'/CHECK).read_text()
        for old, new in REPLACEMENTS:
            need(text.count(old) == 1, 'literal present once: '+old.strip()[:60])
            text = text.replace(old, new)
        (work/'capsule'/CHECK.replace('check.py', 'check_free.py')).write_text(text)
        prior = AUDIT/'capsule/outputs/p104-contact-reassessment-20261025/sources/contact'
        code, out, err = run_checker(work, prior/'WORD.json.gz', read(prior/'RESULT.json')['complete_cost'], PROFILE, 3624)
        need(code == 0 and not err and sha256(out).hexdigest() == EXPECTED_5550, 'positive control reproduces PR5550 output: '+err[-1500:])
        code, out, err = run_checker(work, WORD, cost, PROFILE, 3624)
        need(code == 0 and not err, 'PR5551 caller checker: '+err[-1500:])
        res = json.loads(out)
        need(res['status'] == 'PASS_SCOPED_CALLER_AND_TARGET_BINDING' and len(res['controls']) == 10, 'scoped caller status and controls')
        need(sum(res['paid'].values()) == 69912 and sum(res['targets'].values()) == 12814, 'complete invoice')
        bad = dict(cost, paid=dict(cost['paid'], **{'1': cost['paid']['1']+1}))
        code, _, err = run_checker(work, WORD, bad, PROFILE, 3624)
        need(code != 0 and 'complete unchanged paid/target invoice' in err, 'changed invoice rejected')
        o = res['ordinary']
        return {'status': res['status'], 'paid_jobs': 69912, 'productive_fields': 12814, 'fresh_helpers': res['native_checks']['fresh_helpers'],
                'exact_native_checks': res['native_checks']['distinct_signed_Pauli_and_independent_phase_anchors'],
                'ordinary_passes': o['abstract_address_phase_scalar_pass_upper'], 'ordinary_allowance': o['retained_raw_scalar_upper'],
                'positive_control_pr5550_output': EXPECTED_5550, 'output_sha256': sha256(out).hexdigest(), 'changed_invoice': 'rejected'}


# ---------------------------------------------------------------- layer 3: dense native inventory
_M = {}


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _init():
    _M['C'] = _load('audit5551_clifford', CLIFFORD)
    _M['V'] = _load('audit5551_literal', LITERAL)
    _M['D'] = _load('audit5551_dense', DENSE)
    _M['F'] = read(WORD)['frames']


def compare(actual, expected, rank):
    D = _M['D']
    a, b = D.compile_circuit(actual), D.compile_circuit(expected)
    h = sha256()
    for column in range(512):
        left, right = D.dense_column(a, column), D.dense_column(b, column)
        need(left == right, 'exact complex column %d' % column)
        re, im, d = left
        need(sum(v*v for v in re)+sum(v*v for v in im) == 1 << (2*d), 'exact column norm')
        need(sum(bool(x or y) for x, y in zip(re, im)) == 1 << rank, 'measured child rank')
        h.update(json.dumps([column, d, re, im], separators=(',', ':')).encode())
    return h.hexdigest()


def dense_task(task):
    C, V, F = _M['C'], _M['V'], _M['F']
    kind, a, b, q = task
    if kind in ('move', 'helper'):
        rec, _ = C.lower_child(C.canonical_frame(9, tuple(F[a])).adjoint().then(C.canonical_frame(9, tuple(F[b]))))
        rank = abs(len(F[a])-len(F[b]))
        need(rec['rank'] == rank, 'lowered rank')
        return [list(task), rank, compare(V.recipe(rec), V.adjoint(V.frame(F[a], 9))+V.frame(F[b], 9), rank)]
    if kind == 'main_in':
        op, expected = C.cgate(9, q, 1).adjoint().then(C.canonical_frame(9, tuple(F[a]))), V.adjoint((('C', q, 1),))+V.frame(F[a], 9)
    else:
        op, expected = C.canonical_frame(9, tuple(F[a])).adjoint().then(C.cgate(9, q, -1).then(C.fourier(9))), V.adjoint(V.frame(F[a], 9))+(('C', q, -1),)+V.fourier(9)
    rec, _ = C.lower_child(op)
    need(rec['rank'] == 0, 'intrinsic adapter is monomial')
    return [list(task), 0, compare(V.recipe(rec), expected, 0)]


def inventory(w):
    live = set(w['live'])
    main = live | {r+112 for r in live}
    moves = sorted({(e[2], e[3]) for e in w['program'] if e[0] == 'MOVE'})
    helpers = sorted({(w['initial'][r], w['final'][r]) for r in range(w['public']) if r not in main})
    tasks = [('move', a, b, 0) for a, b in moves]+[('helper', a, b, 0) for a, b in helpers]
    tasks += [('main_in', w['initial'][r], 0, q) for r, q in zip(w['live'], w['ports'])]
    tasks += [('main_out', w['final'][r+112], 0, q) for r, q in zip(w['live'], w['ports'])]
    return tasks


def layer3(w, old, full, jobs):
    tasks = inventory(w)
    pairs = lambda x: {(e[2], e[3]) for e in x['program'] if e[0] == 'MOVE'}
    need(sum(t[0] == 'move' for t in tasks) == 2940 and pairs(w)-pairs(old) == ADDED, 'distinct MOVE inventory and the four maps new relative to PR5545')
    chosen = tasks if full else [t for i, t in enumerate(tasks) if t[0] != 'move' or (t[1], t[2]) in ADDED or i % 32 == 0]
    if jobs > 1:
        with Pool(jobs, initializer=_init) as pool:
            done = pool.map(dense_task, chosen, chunksize=8)
    else:
        _init()
        done = [dense_task(t) for t in chosen]
    # Controls on one added map: phase-only fault invisible to signed tableaux, wrong child sign.
    if not _M:
        _init()
    C, V, D, F = _M['C'], _M['V'], _M['D'], _M['F']
    a, b = 615, 207
    rec, _ = C.lower_child(C.canonical_frame(9, tuple(F[a])).adjoint().then(C.canonical_frame(9, tuple(F[b]))))
    actual, expected = V.recipe(rec), V.adjoint(V.frame(F[a], 9))+V.frame(F[b], 9)
    fault = actual+(('phase', 1),)
    need(V.tableau(fault) == V.tableau(actual) and D.first_difference(fault, expected) is not None, 'phase-only fault rejected densely')
    flipped = list(actual)
    i = next(i for i, g in enumerate(flipped) if g[0] == 'C')
    flipped[i] = ('C', flipped[i][1], -flipped[i][2])
    need(D.first_difference(tuple(flipped), expected) is not None, 'wrong child sign rejected')
    record = {'tasks_total': len(tasks), 'tasks_checked': len(done), 'full': full,
              'kinds': dict(Counter(t[0] for t in chosen)), 'ranks': {str(k): v for k, v in sorted(Counter(d[1] for d in done).items())},
              'complex_entries_compared': 512*512*len(done), 'controls': {'phase_only_fault': 'rejected', 'wrong_child_sign': 'rejected'}}
    return record, done


# ---------------------------------------------------------------- layer 4: own interval engine
def layer4(cost):
    getcontext().prec = 80
    pad = Decimal(10)**-70

    def power(r, t):
        v = (t*Decimal(r).ln()).exp()
        return v*(1-pad), v*(1+pad)

    def margin(k):
        t, lo, hi = 1-k, Decimal(0), Decimal(0)
        for r, n in cost['targets'].items():
            x, y = power(int(r), t)
            lo, hi = lo+n*x, hi+n*y
        for r, n in cost['paid'].items():
            x, y = power(int(r), t)
            lo, hi = lo-n*y, hi-n*x
        return lo, hi
    lo, hi, grid = 0, 10**12, 10**14
    while hi-lo > 1:
        m = (lo+hi)//2
        if margin(Decimal(m)/grid)[0] > 0:
            lo = m
        else:
            hi = m
    need(margin(Decimal(lo)/grid)[0] > 0 and margin(Decimal(hi)/grid)[1] < 0, 'strict crossing enclosure')
    author = [Q(x) for x in cost['raw_root_interval']]
    need(Q(lo, grid) == author[0] and Q(hi, grid) == author[1], 'crossing equals author interval')
    signs = {k: ('positive' if margin(Decimal(k))[0] > 0 else 'negative' if margin(Decimal(k))[1] < 0 else 'undecided')
             for k in ('.00304117', '.00304153', '.0030415305', '.00304154')}
    need(signs == {'.00304117': 'positive', '.00304153': 'positive', '.0030415305': 'positive', '.00304154': 'negative'}, 'claimed/tested signs')
    return {'raw_crossing': [str(Q(lo, grid)), str(Q(hi, grid))], 'signs': signs,
            'engine': 'decimal, 80 digits, correctly rounded ln/exp padded by 1e-70 relative; independent of both source engines and the PR5551 funding peer'}


def main():
    full = '--full' in sys.argv
    jobs = int(sys.argv[sys.argv.index('--jobs')+1]) if '--jobs' in sys.argv else 1
    authenticate()
    print('PASS authenticated canonical sources and PR5550 capsule', flush=True)
    word, old, cost = read(WORD), read(PRED), read(RESULT)['complete_cost']
    out = {'layer1_replay': layer1(word, old)}
    print('PASS layer 1 own replay and delta', out['layer1_replay']['chart_edits'], out['layer1_replay']['local_paid_delta'], flush=True)
    out['layer2_caller'] = layer2(cost)
    print('PASS layer 2 PR5550 caller checker on PR5551', flush=True)
    out['layer4_funding'] = layer4(cost)
    print('PASS layer 4 own interval engine', out['layer4_funding']['raw_crossing'], flush=True)
    record, done = layer3(word, old, full, jobs)
    print('PASS layer 3 dense maps', record['tasks_checked'], 'of', record['tasks_total'], flush=True)
    full_path = HERE/'FULL-CHECK.json'
    if full and '--write' in sys.argv:
        full_path.write_text(json.dumps({'schema': 'p104-5551-dense-inventory/1', 'maps': done}, separators=(',', ':'))+'\n')
    reference = {json.dumps(d[0]): d for d in json.loads(full_path.read_text())['maps']}
    need(len(reference) == record['tasks_total'], 'FULL-CHECK covers the whole inventory')
    for d in done:
        need(reference[json.dumps(d[0])] == d, 'matrix digest equals FULL-CHECK for '+json.dumps(d[0]))
    out['layer3_dense'] = dict(record, full_check_sha256=hashlib_file(full_path))
    out['layer3_dense'].pop('tasks_checked')
    out['layer3_dense'].pop('kinds')
    out['layer3_dense'].pop('ranks')
    out['layer3_dense'].pop('complex_entries_compared')
    out['layer3_dense'].pop('full')
    if '--write' in sys.argv:
        (HERE/'RESULT.json').write_text(json.dumps(out, indent=1, sort_keys=True)+'\n')
    else:
        need(json.loads(json.dumps(out)) == json.loads((HERE/'RESULT.json').read_text()), 'complete result equals RESULT.json')
    print('PASS_P104_JOINT_CONTACT_NATIVE_CALLER_AUDIT', 'full' if full else 'subset')


if __name__ == '__main__':
    main()
