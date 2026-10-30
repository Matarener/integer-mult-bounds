#!/usr/bin/env python3
"""Verify the dynamic capture census on the final G20 BIT word (PR5708).  Apache-2.0.

Prepared for Matarener with Claude (Anthropic), via Claude Code.  Python 3.12, standard library only.
Checks: (0) pinned inputs and the PR5708 local paid profile; (1) single-helper captures with any injected
payload and all dead/live epochs; (2) helper pairs whose joint ownership lengthens a dead interval;
(3) exact two-helper census under the individual schedule; (4) joint token bound for any owned set;
(5) positive control: on the PR5667 word the single census rediscovers exactly the nine PR5665/PR5671
late-binding captures; (6) RESULT.json equals the recomputed receipt.  `--write` regenerates RESULT.json.
"""
from collections import Counter
from fractions import Fraction as Fr
from hashlib import sha256
from pathlib import Path
import importlib.util, json, sys, time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
FRAMES = ROOT/'research/g20-conjugation-admission/prior/prior/prior/source/vendor/g20/inputs/FRAMES.json'
WORD = ROOT/'research/g20-conjugation-admission/WORD.json.gz'
LOCAL = ROOT/'research/g20-conjugation-admission/LOCAL-RESULT.json'
INVOICE = ROOT/'research/g20-conjugation-admission/INVOICE.json'
WORD5667 = ROOT/'research/g20-late-binding-admission/prior/WORD.json.gz'
CUTS = ROOT/'research/g20-late-binding-admission/CUTS.json'
C_TARGET = Fr(37, 10000)
C_CONTROL = Fr(35, 10000)
EPS = 1e-9


def need(ok, why):
    if not ok:
        raise SystemExit('FAIL: ' + why)


def log(*a):
    print(time.strftime('%H:%M:%S'), *a, flush=True)


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def r6(x):
    return round(x, 6)


def main():
    K = load('g20_capture', HERE/'capture.py')
    for row in json.loads((HERE/'SOURCES.json').read_text())['files']:
        if row['usage'] == 'input':
            need(sha256((ROOT/row['path']).read_bytes()).hexdigest() == row['sha256'], 'input ' + row['path'])
    log('PASS_INPUTS_AUTHENTICATED')
    res = {'C': str(C_TARGET)}
    t = 1 - float(C_TARGET)

    # (0) source profile
    W = K.Word(WORD, FRAMES)
    _, _, _, paid, _ = W.replay()
    want = json.loads(LOCAL.read_text())['stats']['paid']
    need({str(k): v for k, v in paid.items()} == want, 'PR5708 local paid profile')
    need(Counter(W.target_rank.values()) == Counter({8: 413, 4: 2}), 'helper targets')
    res['source'] = {'events': len(W.rec), 'wires': W.width, 'owned': len(W.owned), 'helpers': len(W.helpers),
                     'paid': {str(k): paid[k] for k in sorted(paid)}}
    log('PASS_SOURCE_PROFILE', res['source'])

    # (1) single helpers
    singles = K.analyze_sets(W, [(h,) for h in W.helpers], C_TARGET)
    need(all(len(r['epochs']) == 1 for r in singles), 'one live interval per helper')
    need(all(not r['multi'] for r in singles), 'single-symbol dependence')
    need(not K.reads_before_injection(W, singles), 'no reads before injection')
    need(all(len(r['dead_own']) <= 1 and all(x[2] <= 2 for x in r['dead_own']) for r in singles),
         'at most one free own query, rank <= 2')
    best = max(r['bound'] for r in singles)
    pos = [r['set'][0] for r in singles if r['bound'] > EPS]
    need(not pos, 'a single-helper capture pays its target: %s' % pos)
    hist = Counter((tuple(x[2] for x in r['dead_own']), tuple(sorted(x[2] for x in r['epochs'][0]['best'])))
                   for r in singles)
    neutral = [r['set'][0] for r in singles if abs(r['bound']) <= EPS]
    res['single'] = {'helpers': len(singles), 'epochs_per_helper': 1, 'positive': 0, 'best_gain': r6(best),
                     'neutral': neutral,
                     'max_removed_rank_mass': max(sum(x[2] for x in r['dead_own']) +
                                                  sum(x[2] for x in r['epochs'][0]['best']) for r in singles),
                     'profile': sorted([[list(a), list(b), n] for (a, b), n in hist.items()])}
    log('PASS_SINGLE', {k: v for k, v in res['single'].items() if k != 'profile'})

    # (2) joint deadness
    pp = K.partner_pairs(W)
    sets = sorted({tuple(sorted(p)) for p in pp})
    joint = K.analyze_sets(W, sets, C_TARGET, ignore_partners=True)
    res['joint_dead_pairs'] = []
    for r in joint:
        row = {'pair': r['set'], 'epochs': len(r['epochs']), 'bound': r6(r['bound'])}
        if r['bound'] > EPS:
            g = K.exact_joint_pair(W, r, C_TARGET)
            need(g[0] <= EPS, 'joint-dead pair pays: %s' % (r['set'],))
            row['exact_best_gain'] = r6(g[0])
            row['exact_removed_ranks'] = g[1]
        res['joint_dead_pairs'].append(row)
    log('PASS_JOINT_DEAD', res['joint_dead_pairs'])

    # (3) pairs
    stats, exact, best2 = K.pair_census(W, singles, C_TARGET)
    need(best2 is None or best2[0] <= EPS, 'pair pays: %s' % (best2,))
    need(stats['pairs_without_shared_query_max_gain'] <= EPS, 'pairs without shared query')
    res['pairs'] = {'with_shared_query': stats['pairs'], 'closed_by_row_class_bound':
                    stats.get('closed_by_row_class_bound', 0), 'enumerated': stats.get('enumerated', 0),
                    'best_gain': r6(best2[0]) if best2 else None,
                    'best_pair': [best2[1], best2[2]] if best2 else None,
                    'best_removed_ranks': best2[3] if best2 else None}
    log('PASS_PAIRS', res['pairs'])

    # (4) joint token bound
    tb = K.token_bound(W, singles, C_TARGET)
    cap = tb['N'] / 4
    d2, d1 = 2 ** t, 1.0
    res['joint_bound'] = dict(tb, per_helper_gain_max={
        'free_own_rank2': r6(cap + d2 - 8 ** t), 'free_own_rank1': r6(cap + d1 - 8 ** t),
        'no_free_own': r6(cap - 8 ** t)},
        helpers_with_free_rank2=sum(1 for r in singles if any(x[2] == 2 for x in r['dead_own'])),
        )
    need(cap + d1 - 8 ** t < 0, 'token bound closes helpers without a rank-2 free query')
    inv = json.loads(INVOICE.read_text())
    calls = 18
    F = sum(n * int(k) ** t for k, n in inv['targets'].items()) - sum(n * int(k) ** t for k, n in inv['paid'].items())
    need(F < 0, 'PR5708 invoice is below the target')
    per_word = -F / calls
    gmax = cap + d2 - 8 ** t
    import math
    res['target'] = {'invoice_moment_at_C': r6(F), 'calls': calls, 'needed_per_local_word': r6(per_word),
                     'min_free_rank2_helpers_in_any_set_reaching_C': math.ceil(per_word / gmax)}
    log('PASS_TOKEN_BOUND', {k: v for k, v in res['joint_bound'].items() if k != 'set_sizes'})

    # (5) positive control
    W2 = K.Word(WORD5667, FRAMES)
    s2 = K.analyze_sets(W2, [(h,) for h in W2.helpers], C_CONTROL)
    pos2 = sorted(r['set'][0] for r in s2 if r['bound'] > EPS)
    sel = sorted(x['helper'] for x in json.loads(CUTS.read_text())['selected'])
    need(pos2 == sel, 'control rediscovers PR5671 cuts: %s vs %s' % (pos2, sel))
    shapes = Counter((tuple(x[2] for x in r['dead_own']), tuple(sorted(x[2] for x in r['epochs'][0]['best'])))
                     for r in s2 if r['set'][0] in sel)
    need(shapes == Counter({((1,), (7,)): 9}), 'control shapes H1+H7')
    res['control_PR5667'] = {'C': str(C_CONTROL), 'positive': pos2, 'shape': 'free own H1 + removed H7'}
    log('PASS_CONTROL', res['control_PR5667'])

    path = HERE/'RESULT.json'
    if '--write' in sys.argv:
        path.write_text(json.dumps(res, indent=1, sort_keys=True) + '\n')
    need(json.loads(path.read_text()) == json.loads(json.dumps(res, sort_keys=True)), 'RESULT.json')
    print('PASS_G20_DYNAMIC_CAPTURE_CENSUS', flush=True)


if __name__ == '__main__':
    main()
