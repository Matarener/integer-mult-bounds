#!/usr/bin/env python3
"""Verify the post-cut information-loss census for PR5718-shape leak classes on the PR6030 and PR5907 P104 words.
Apache-2.0.  Python 3.12, standard library only.  Checks:
 (0) pinned input bytes: the PR6040 census module, the PR6045 correction module and the two words;
 (1) the re-run class census equals PR6040's own census counts on both words;
 (2) rank: the final field matrix has exact rank n = 770 on both words, so (rank never increases along a word)
     every intermediate state has rank 770 and its left kernel has dimension N - n = 29;
 (3) the left-kernel tracker holds 29 vectors at every cut; at every cut they are linearly independent and
     annihilate the exact field matrix, hence they span the left kernel (by (2));
 (4) a randomized brute-force comparison of the tracker's redundant set with exact ranks on small words;
 (5) the census: a leak class (cut i, pivot p) is 'information-lost' when p is outside the kernel support at i
     (no post-cut linear program legalizes it, README Lemma 1); the residual classes go through the chart-local
     combination closure and PR6045's span decision;
 (6) the one residual PR5907 witness: an explicit 20-event chart-local correction program, lowered and simulated
     directly, leaves every O output exactly equal to the original and passes PR6040's pairing test; three
     perturbed programs are rejected;
 (7) RESULT.json equals the recomputed receipt.
"""
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import importlib.util, json, random, sys, time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PINS = {'inputs/shapesplit.py': '11e8ef691b28fb4f401a8c2e97b6d462e7a004f0e215a28579d6a654b4ca3304',   # PR6040 1889253f
        'inputs/leakfix.py': 'dbbdc9ff9ebb55f1b9e832dcbe1aa5e407e7932a8d958a006bdaca6055e7f4ee'}      # PR6045 23abc007
for rel, h in PINS.items():
    if sha256((HERE/rel).read_bytes()).hexdigest() != h:
        raise SystemExit('pinned input does not match: ' + rel)   # checked before any imported code runs


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec); sys.modules[name] = mod; spec.loader.exec_module(mod)
    return mod


SS = _load('pr6040_shapesplit', HERE/'inputs'/'shapesplit.py')   # leakfix reuses this module object
L = _load('pr6045_leakfix', HERE/'inputs'/'leakfix.py')
sys.path.insert(0, str(HERE))
import kernel as KM      # noqa: E402
import check as C        # noqa: E402

WORDS = {'pr6030': 'research/p104-helper470-twin-rung-removal/WORD.json.gz',
         'pr5907': 'research/p104-helper468-rung-removal/WORD.json.gz'}
need = KM.need
WITNESS = {'word': 'pr5907', 'cut_after': 13776, 'pivot': 699, 'chart': 1031,
           'comb': {'696': '1', '698': '-1', '699': '1', '700': '-1', '702': '-1', '767': '-1', '792': '1'},
           'targets': [[697, '1'], [698, '2'], [700, '-1']]}


def pins():
    src = json.loads((HERE/'SOURCES.json').read_text())
    for row in src['files']:
        need(sha256((ROOT/row['path']).read_bytes()).hexdigest() == row['sha256'], 'pin ' + row['path'])
    return {k: SS.read(ROOT/v) for k, v in WORDS.items()}


def exact_rank(rows):
    piv = {}
    for r in rows:
        v = {k: x for k, x in r.items() if x}
        while v:
            k = min(v)
            if k not in piv:
                s = 1 / v[k]; piv[k] = {a: b * s for a, b in v.items()}; break
            C.add(v, piv[k], -v[k])
    return len(piv)


def tracker_audit(w, cuts):
    """Run the tracker alongside the exact field matrix; at every cut check |K| = N - n, independence, annihilation."""
    n = w['public']; m = w['owned_fields']; N = n + m
    rows, cur = C.start(w)
    K = KM.Kernel(N, range(n, N))
    out = {}
    for t, e in enumerate(w['program']):
        C.step(rows, cur, e); K.apply(e)
        if t in cuts:
            need(len(K.vecs) == N - n, 'tracker dimension N - n')
            need(exact_rank(K.vecs) == N - n, 'tracker vectors independent')
            for c in K.vecs:
                acc = {}
                for f, x in c.items():
                    C.add(acc, rows[f], x)
                need(not acc, 'tracker vector annihilates the field matrix')
            out[t] = frozenset(K.support())
    need(exact_rank(rows) == n, 'final field matrix has rank n')
    return out


def brute(seed=20261028, trials=300):
    """Small random words: the tracker's redundant set equals {f : rank(W without f) = rank(W)} at every event."""
    rnd = random.Random(seed)
    for _ in range(trials):
        n, m = rnd.randint(1, 4), rnd.randint(0, 3); N = n + m
        rows = [{r: Q(1)} if r < n else {} for r in range(N)]
        K = KM.Kernel(N, range(n, N))
        for _ in range(rnd.randint(1, 12)):
            r = rnd.randrange(N); f = rnd.choice([x for x in range(N) if x != r] or [r])
            op = rnd.choice(['ADD', 'ADD', 'SCALE', 'INIT', 'CLEAR', 'COPY'] if f != r else ['SCALE', 'INIT', 'CLEAR'])
            q = Q(rnd.choice([-2, -1, 1, 2, 3]), rnd.choice([1, 2]))
            e = {'ADD': ['ADD', r, f, str(q), 0], 'SCALE': ['SCALE', r, str(q), 0], 'INIT': ['INIT', r, 0],
                 'CLEAR': ['CLEAR', r, 0], 'COPY': ['COPY', r, f, str(rnd.choice([0, 1, -2])), 0]}[op]
            K.apply(e)
            if op in ('INIT', 'CLEAR'): rows[r] = {}
            elif op == 'SCALE': rows[r] = {k: v * q for k, v in rows[r].items()}
            elif op == 'COPY': rows[r] = {k: v * Q(e[-2]) for k, v in rows[f].items() if v * Q(e[-2])}
            else: C.add(rows[r], rows[f], q)
            rk = exact_rank(rows)
            red = {g for g in range(N) if exact_rank(rows[:g] + rows[g + 1:]) == rk}
            need(K.support() == red, 'tracker redundant set equals brute-force rank test')
            need(len(K.vecs) == N - rk and exact_rank(K.vecs) == N - rk, 'tracker dimension equals N - rank')
    return trials


def census(w):
    classes, counts = L.leak_classes(w)
    need(counts == SS.census(w, 'empty')[0], 'class census equals PR6040 census')
    leak = [c for c in classes if c['kind'] == 'leak']
    need(all(c['row_p'] for c in leak), 'retired value nonzero in every leak class')
    supp = tracker_audit(w, {c['cut_after'] for c in leak})
    resid = [c for c in leak if c['pivot'] in supp[c['cut_after']]]
    iv = {}
    for c in resid:
        iv[(c['cut_after'], c['pivot'])], _ = KM.closure_intervals(w, c['cut_after'], c['pivot'])
    spans = L.correction_spans(w, resid, iv)
    rows = []
    for ci, c in enumerate(resid):
        kind, rho = L.decide(c, spans[ci])
        pts = iv[(c['cut_after'], c['pivot'])]
        rows.append({'cut_after': c['cut_after'], 'pivot': c['pivot'], 'frame': c['frame'], 'leak': c['leak'],
                     'usable_points': len(pts), 'charts': sorted({x[1] for x in pts}),
                     'kind': kind if pts else 'no_usable_combination', 'rho': rho})
    return {'leak_classes': len(leak), 'information_lost': len(leak) - len(resid), 'residual': len(resid),
            'residual_kinds': dict(sorted(Counter(r['kind'] for r in rows).items())), 'residual_classes': rows}, classes


def witness(w, classes):
    W = WITNESS; cut, p = W['cut_after'], W['pivot']
    batches = [{'after_event': cut, 'chart': W['chart'], 'comb': W['comb'], 'target': t, 'mu': mu} for t, mu in W['targets']]
    zcol, ins = C.check(w, cut, p, batches)
    cls = [c for c in classes if (c['cut_after'], c['pivot']) == (cut, p)]
    need(len(cls) == 1 and cls[0]['kind'] == 'leak', 'witness class is a PR6040 leak class')
    c = cls[0]
    need(SS.functional_witness(c['A'], p, c['free'], zcol.get(p, Q(0))), 'PR6040 pairing test passes with rho = z-coefficient at p')
    rejected = 0
    for bad in ([batches[0], batches[1], dict(batches[2], mu='-2')], batches[:2],
                [dict(batches[0], mu='2'), batches[1], batches[2]]):
        try:
            C.check(w, cut, p, bad)
        except ValueError:
            rejected += 1
    need(rejected == 3, 'three perturbed programs rejected')
    return {'class': {'cut_after': cut, 'pivot': p, 'frame': c['frame'], 'leak': c['leak'], 'V': w['final'][p]},
            'batches': batches, 'inserted_events': len(ins),
            'inserted_ops': dict(sorted(Counter(e[0] for e in ins).items())),
            'z_column': {str(k): str(v) for k, v in sorted(zcol.items())}, 'perturbed_rejected': rejected}


def main():
    t0 = time.time()
    ws = pins()
    need(len(ws['pr6030']['program']) == 22803 and len(ws['pr5907']['program']) == 25998, 'word sizes')
    print('pins ok', flush=True)
    out = {'schema': 'p104-post-cut-information-loss/v1', 'brute_force_trials': brute()}
    print('brute force ok', flush=True)
    for k in ('pr6030', 'pr5907'):
        out[k], classes = census(ws[k])
        print(k, out[k]['information_lost'], out[k]['residual'], out[k]['residual_kinds'], flush=True)
        if k == WITNESS['word']:
            out['pr5907_witness'] = witness(ws[k], classes)
            print('witness', out['pr5907_witness']['z_column'], flush=True)
    need(out['pr6030']['residual_kinds'].get('witness', 0) == 0, 'no residual witness on the selected PR6030 word')
    text = json.dumps(out, indent=1, sort_keys=True) + '\n'
    if '--write' in sys.argv:
        (HERE/'RESULT.json').write_text(text)
    need((HERE/'RESULT.json').read_text() == text, 'RESULT.json equals the recomputed receipt')
    print('PASS_P104_POST_CUT_INFORMATION_LOSS (%.0f s)' % (time.time() - t0))


if __name__ == '__main__':
    main()
