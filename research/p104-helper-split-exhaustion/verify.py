#!/usr/bin/env python3
"""Verify the helper-split exhaustion census on the PR5907 P104 word.  Apache-2.0.

Prepared for Matarener with Claude (Anthropic), via Claude Code.  Python 3.12, standard library only.
Checks: (0) pinned live inputs and the PR5907 local profiles; (1) the exact census under the PR5599 contract
(group supports) finds no split cut on the PR5907 word; (2) the relaxed necessary-condition census (boundary
supports) also finds none; (3) positive control: on the PR5565 source word the same census finds the first
PR5599 split (cut 13775, chart 120) and the authors' witness from SPLITS.json passes the independent exact check;
(4) decision-procedure controls on synthetic instances and a corrupted witness; (5) RESULT.json equals the
recomputed receipt.
"""
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import importlib.util, json, sys, time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WORD = ROOT/'research/p104-helper468-rung-removal/WORD.json.gz'
RESULT5907 = ROOT/'research/p104-helper468-rung-removal/RESULT.json'
WORD5565 = ROOT/'research/p104-helper-subspace-splits/inputs/PR5565-WORD.json.gz'
SPLITS = ROOT/'research/p104-helper-subspace-splits/SPLITS.json'


def need(ok, why):
    if not ok:
        raise ValueError(why)


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec); sys.modules[name] = mod; spec.loader.exec_module(mod)
    return mod


def profiles(w):
    """Own count of the local paid profile (MOVE rank = chart dimension difference) and helper profile."""
    dims = [len(f) for f in w['frames']]
    paid = Counter(abs(dims[e[3]] - dims[e[2]]) for e in w['program'] if e[0] == 'MOVE')
    main = set(w['live']) | {r + 112 for r in w['live']}
    helpers = Counter(dims[w['final'][r]] - dims[w['initial'][r]] for r in range(w['public']) if r not in main)
    return {str(k): v for k, v in sorted(paid.items())}, {str(k): v for k, v in sorted(helpers.items())}


def summary(counts, classes):
    kinds = Counter(c['kind'] for c in classes)
    return {'evaluations': counts['evaluations'], 'groups': counts['groups'], 'helpers': counts['helpers'],
            'no_pure_prefix': counts.get('no_pure_prefix', 0), 'no_pure_suffix': counts.get('no_pure_suffix', 0),
            'classes': dict(sorted(kinds.items())), 'witnesses': counts['witnesses'],
            'distinct_cut_frame_pairs': len({(c['cut_after'], c['frame']) for c in classes}),
            'frames_with_both_directions': sorted({c['frame'] for c in classes})}


def main():
    t0 = time.time()
    C = load('p104_split_census', HERE/'splitcensus.py')
    pins = json.loads((HERE/'SOURCES.json').read_text())
    for row in pins['files']:
        if row['usage'] == 'input':
            need(sha256((ROOT/row['path']).read_bytes()).hexdigest() == row['sha256'], 'source pin '+row['path'])
    word = C.read(WORD)
    paid, helpers = profiles(word)
    local = json.loads(RESULT5907.read_text())['local']
    need(paid == local['paid'] and helpers == local['helpers'] and word['public'] == local['public_inputs'], 'PR5907 local profiles')
    need(len(word['program']) == 25998 and word['owned_fields'] == 29, 'PR5907 word size')
    print('pins and profiles ok', flush=True)
    # (1) the PR5599 contract: supports inside the helper group
    counts_g, classes_g = C.census(word, 'group', 'group')
    need(counts_g['witnesses'] == 0, 'no PR5599 split on the PR5907 word')
    need(counts_g['evaluations'] == 8913 and counts_g['groups'] == 69 and counts_g['helpers'] == 562, 'census coverage')
    print('group supports', summary(counts_g, classes_g), flush=True)
    # (2) relaxed necessary condition: every role starting at U / ending at V
    counts_b, classes_b = C.census(word, 'boundary', 'boundary')
    need(counts_b['witnesses'] == 0, 'no split under the boundary relaxation')
    need(all(c['kind'] in ('F1zero', 'F2zero') for c in classes_b), 'every two-sided class is an orthogonality failure')
    print('boundary supports', summary(counts_b, classes_b), flush=True)
    # (3) positive control on the PR5565 source word
    source = C.read(WORD5565)
    counts_p, classes_p = C.census(source, 'group', 'group', cut_range=(13700, 13800))
    hit = next((c for c in classes_p if c['cut_after'] == 13775 and c['frame'] == 120 and c['kind'] == 'witness'), None)
    need(hit is not None and hit['ranks'] == [5, 4] and 648 in hit['pivots'], 'positive control: first PR5599 split found')
    main_roles = set(source['live']) | {r + 112 for r in source['live']}
    group = {r for r in range(source['public']) if r not in main_roles and (source['initial'][r], source['final'][r]) == (3, 127)}
    own = tuple({int(k): Q(v) for k, v in hit['witness'][s].items()} for s in 'abcd')
    C.check_witness(source, 13775, 120, *own, group)
    authors = json.load(open(SPLITS))[0]
    need(authors['cut_after'] == 13775 and authors['frame'] == 120, 'authors first split location')
    theirs = tuple({int(k): Q(v) for k, v in authors[s].items()} for s in 'abcd')
    C.check_witness(source, 13775, 120, *theirs, group)
    print('positive control', summary(counts_p, classes_p), 'own witness and authors witness pass', flush=True)
    # (4) controls
    def rejected(fn, why):
        try:
            fn()
        except ValueError:
            return 'rejected'
        raise ValueError('control accepted: '+why)
    bad = dict(theirs[1]); k = min(bad); bad[k] += 1
    ctrl = {'corrupted_authors_b': rejected(lambda: C.check_witness(source, 13775, 120, theirs[0], bad, theirs[2], theirs[3], group), 'corrupted b'),
            'wrong_cut': rejected(lambda: C.check_witness(source, 13700, 120, *theirs, group), 'wrong cut')}
    one = lambda r: {r: Q(1)}
    kind, _ = C.decide([(one(1), one(10))], [(one(2), one(10))]); need(kind == 'F1zero', 'synthetic F1zero'); ctrl['synthetic_F1zero'] = kind
    kind, _ = C.decide([(one(1), one(10))], [(one(1), {10: Q(2)})]); need(kind == 'mismatch', 'synthetic mismatch'); ctrl['synthetic_mismatch'] = kind
    A = [({1: Q(1)}, {10: Q(1)}), ({2: Q(1)}, {11: Q(1)})]; B = [({1: Q(1)}, {10: Q(2)}), ({2: Q(1)}, {11: Q(1), 10: Q(-1)})]
    kind, wit = C.decide(A, B); need(kind == 'witness' and wit is not None, 'synthetic witness'); ctrl['synthetic_witness'] = kind
    print('controls', ctrl, flush=True)
    result = {'word': 'research/p104-helper468-rung-removal/WORD.json.gz', 'events': len(word['program']), 'public_inputs': word['public'],
              'local_paid': paid, 'local_helpers': helpers,
              'group_supports': summary(counts_g, classes_g), 'boundary_supports': summary(counts_b, classes_b),
              'group_classes': classes_g, 'boundary_classes': [{k: v for k, v in c.items() if k != 'witness'} for c in classes_b],
              'positive_control_pr5565': {'cut_range': [13700, 13800], **summary(counts_p, classes_p),
                                          'first_split': {k: hit[k] for k in ('cut_after', 'frame', 'ranks', 'dim_A', 'dim_B', 'pivots')}},
              'controls': ctrl}
    if '--write' in sys.argv:
        (HERE/'RESULT.json').write_text(json.dumps(result, indent=1, sort_keys=True)+'\n')
    need(json.loads((HERE/'RESULT.json').read_text()) == result, 'RESULT.json equals the recomputed receipt')
    print('PASS_P104_HELPER_SPLIT_EXHAUSTION %.1fs' % (time.time()-t0))


if __name__ == '__main__':
    main()
