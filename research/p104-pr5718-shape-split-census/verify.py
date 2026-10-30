#!/usr/bin/env python3
"""Verify the PR5718-shape split census on the PR5713 source word and the PR5907 word.  Apache-2.0.

Prepared by Nick Petalas.  Python 3.12, standard library only.
Checks: (0) pinned input bytes; (1) calibration: on the PR5713 source word the census finds PR5718's own split
(cut after event 14330, chart 602, helper 708, ranks (2, 7)) and every witness lies on that chart and helper;
(2) on the PR5907 word the census finds no witness under either input rule; (3) synthetic controls of the exact
pairing decision; (4) RESULT.json equals the recomputed receipt.  Run with --write to regenerate RESULT.json.
"""
from collections import Counter, defaultdict
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import gzip, importlib.util, io, json, sys, tarfile, time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WORD5907 = 'research/p104-helper468-rung-removal/WORD.json.gz'
TAR5713 = 'research/p104-two-boundary-helper-split/inputs/pr5713-source.tar'
MEMBER5713 = 'research/p104-temporal-updates/WORD.json.gz'


def need(ok, why):
    if not ok:
        raise SystemExit('FAIL: ' + why)


def load_module():
    spec = importlib.util.spec_from_file_location('p104_shape_split', HERE/'shapesplit.py')
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    return mod


def pinned_inputs():
    pins = {row['path']: row['sha256'] for row in json.loads((HERE/'SOURCES.json').read_text())['files']
            if row['usage'] == 'input'}
    need(set(pins) == {WORD5907, TAR5713}, 'declared live inputs')
    for path, digest in pins.items():
        need(sha256((ROOT/path).read_bytes()).hexdigest() == digest, 'pinned bytes of ' + path)
    with tarfile.open(ROOT/TAR5713) as tar:
        raw = tar.extractfile(MEMBER5713).read()
    return json.loads(gzip.decompress((ROOT/WORD5907).read_bytes())), json.loads(gzip.decompress(raw)), \
        sha256(raw).hexdigest()


def summary(counts, classes):
    leak = [c for c in classes if c['kind'] == 'leak']
    per_pivot = defaultdict(list)
    for c in leak:
        per_pivot[c['pivot']].append(c)
    return {
        'evaluations': counts['evaluations'], 'pivots': counts['pivots'],
        'no_helper_prefix': counts.get('no_helper_prefix', 0),
        'classes': dict(sorted(Counter(c['kind'] for c in classes).items())),
        'witnesses': [{k: c[k] for k in ('cut_after', 'frame', 'group', 'pivot', 'ranks')}
                      for c in classes if c['kind'] == 'witness'],
        'pairing_failures': [{k: c[k] for k in ('cut_after', 'frame', 'group', 'pivot', 'ranks')}
                             for c in classes if c['kind'] == 'pairing'],
        'min_leak': min((c['leak'] for c in leak), default=None),
        'leak_size_counts': dict(sorted(Counter(str(min(c['leak'], 6)) if c['leak'] < 6 else '6+' for c in leak).items())),
        'leak_by_pivot': {str(p): {'classes': len(v), 'first_cut': v[0]['cut_after'], 'last_cut': v[-1]['cut_after'],
                                   'min_leak': min(c['leak'] for c in v), 'group': v[0]['group']}
                          for p, v in sorted(per_pivot.items())},
    }


def controls(M):
    """Exact pairing decision on synthetic subspaces (each A entry is (coefficients over fields, image c))."""
    p = 'p'
    A = [({p: Q(1)}, {'x': Q(1)})]
    need(M.functional_witness(A, p, {'x'}, Q(0)), 'free image coordinate gives a witness')
    need(not M.functional_witness(A, p, set(), Q(0)), 'no free coordinate and c_p = 0 gives none')
    A = [({p: Q(1)}, {p: Q(2)})]
    need(M.functional_witness(A, p, set(), Q(1, 2)), 'a_p = d_p * c_p gives a witness')
    need(not M.functional_witness(A, p, set(), Q(1)), 'a_p != d_p * c_p on a line gives none')
    A = [({p: Q(1)}, {p: Q(2)}), ({'q': Q(1)}, {p: Q(1)})]
    need(M.functional_witness(A, p, set(), Q(1)), 'a second direction repairs the pairing')
    A = [({'q': Q(1)}, {'x': Q(1)})]
    need(not M.functional_witness(A, p, {'x'}, Q(0)), 'a_p = 0 everywhere gives none')
    return 6


def main():
    t0 = time.time()
    M = load_module()
    w5907, w5713, sha5713 = pinned_inputs()
    receipt = {'schema': 'p104-pr5718-shape-split-census/1',
               'inputs': {'PR5907_word': WORD5907, 'PR5713_word': TAR5713 + ':' + MEMBER5713,
                          'PR5713_word_sha256': sha5713},
               'runs': {}}
    for name, w in (('PR5713', w5713), ('PR5907', w5907)):
        for in_kind in ('boundary', 'empty'):
            counts, classes = M.census(w, in_kind)
            receipt['runs'][name + '/' + in_kind] = summary(counts, classes)
    for in_kind in ('boundary', 'empty'):
        cal = receipt['runs']['PR5713/' + in_kind]['witnesses']
        need({'cut_after': 14330, 'frame': 602, 'group': [3, 127], 'pivot': 708, 'ranks': [2, 7]} in cal,
             'calibration recovers PR5718 split at cut 14330, chart 602, helper 708')
        need(all(c['frame'] == 602 and c['pivot'] == 708 for c in cal), 'calibration witnesses on chart 602 only')
        need(receipt['runs']['PR5907/' + in_kind]['witnesses'] == [], 'no PR5718-shape split on PR5907')
    receipt['synthetic_controls'] = controls(M)
    path = HERE/'RESULT.json'
    text = json.dumps(receipt, sort_keys=True, separators=(',', ':')) + '\n'
    if '--write' in sys.argv:
        path.write_text(text)
    need(path.read_text() == text, 'RESULT.json equals the recomputed receipt')
    r = receipt['runs']['PR5907/empty']
    print('PR5713 calibration witnesses:', len(receipt['runs']['PR5713/empty']['witnesses']),
          '| PR5907 classes:', r['classes'], '| min leak', r['min_leak'], '| %.1fs' % (time.time() - t0))
    print('PASS_P104_PR5718_SHAPE_SPLIT_CENSUS')


if __name__ == '__main__':
    main()
