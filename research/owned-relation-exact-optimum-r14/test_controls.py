#!/usr/bin/env python3
"""Rejecting mutation controls for relations.py (Part B).  Standard library only."""
import copy, gzip, json, sys
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import relations as R  # noqa: E402


def rejects(fn):
    try:
        fn()
    except SystemExit as e:
        return str(e).startswith('FAIL')
    return False


def main():
    word = json.loads(gzip.decompress(R.WORD.read_bytes()))
    c = word['canonical']; fr = c['frames']
    trank = {i: len(fr[c['final'][i]]) - len(fr[c['start'][i]]) for i in range(224, R.NL)}
    free = {i for i in range(224, R.NL) if c['start'][i] == 0}
    t = 1 - R.C_SELECTED
    pw = lambda r: (t * R.D(r).ln()).exp()
    results = {}
    # 1. a corrupted climb rank breaks the pinned paid profile
    bad = copy.deepcopy(word)
    i = next(i for i, e in enumerate(bad['programs']['backward']) if e[0] == 'climb')
    bad['programs']['backward'][i][5] += 1
    results['corrupted_climb_rank'] = rejects(lambda: R.replay(bad, 'backward', free))
    climbs, options = R.replay(word, 'backward', free)
    # 2. a fabricated climb whose component is a combination of two existing ones breaks independence
    a, b = climbs[0][2][()], climbs[1][2][()]
    fake = dict(a); R.add_into(fake, b, Q(3))
    results['dependent_component'] = rejects(lambda: R.optimum(climbs + [(0, 1, {(7,): fake})], options, trank, pw))
    # 3. a centre option pointing outside the component span is rejected
    stray = dict(options[0][2][()]); stray[max(free)] = stray.get(max(free), 0) + Q(1)
    results['option_outside_span'] = rejects(
        lambda: R.optimum(climbs, options + [(options[0][0], 8, {(): stray})], trank, pw))
    # 4. dropping one #5383 relation breaks the attainment check
    orig = R.RELATIONS.read_text

    class Drop:
        def __init__(self, path): self.path = path
        def read_text(self, encoding=None):
            d = json.loads(orig(encoding='utf-8')); d['rows'] = d['rows'][:-1]; return json.dumps(d)
        def read_bytes(self): return self.path.read_bytes()
        def relative_to(self, other): return self.path.relative_to(other)
    saved = R.RELATIONS
    R.RELATIONS = Drop(saved)
    try:
        results['dropped_5383_relation'] = rejects(R.build)
    finally:
        R.RELATIONS = saved
    # 5. a tampered stored result is rejected by main()
    path = HERE / 'RESULT-RELATIONS.json'
    text = path.read_text(encoding='utf-8')
    tampered = json.loads(text); tampered['orientations']['forward']['optimum_per_local'] = '1'
    real = R.HERE
    tmp = Path(__import__('tempfile').mkdtemp())
    (tmp / 'RESULT-RELATIONS.json').write_text(json.dumps(tampered))
    (tmp / 'SOURCES.json').write_text((HERE / 'SOURCES.json').read_text())
    R.HERE = tmp; sys.argv = ['relations.py']
    try:
        results['tampered_result'] = rejects(R.main)
    finally:
        R.HERE = real
    print(json.dumps(results, sort_keys=True))
    if not all(results.values()):
        raise SystemExit('FAIL: a mutation was accepted')
    print('PASS_OWNED_RELATION_EXACT_OPTIMUM_CONTROLS')


if __name__ == '__main__':
    main()
