#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Independent finite oracles and production-path rejection controls.

The large census is separate. These checks target the frame lattice, the
new-gap reduction, source binding, scalar conjugation, and sensitivity.
"""
from collections import Counter
from copy import deepcopy
from fractions import Fraction
from itertools import combinations
import json
from pathlib import Path
import types

P = Path(__file__).resolve().parent
V = types.ModuleType('entry')
V.__file__ = str(P / 'verify.py')
exec(compile((P / 'verify.py').read_bytes(), V.__file__, 'exec'), V.__dict__)
S, C, A = V.setup()
R = S.R
checks = Counter()


def require(ok, message):
    if not ok:
        raise ValueError(message)


def rejects(fn, name):
    try:
        fn()
    except (ValueError, C.AuditFailure):
        checks[name] += 1
        return
    raise ValueError('negative control accepted: ' + name)


def xor_span(vectors):
    """Independent subset-XOR enumeration, not the source join/basis routine."""
    values = {0}
    for v in vectors:
        values = values | {x ^ v for x in values}
    return values


def independent_frames(low, high, dimension):
    low_points = {x for x in range(512) if low >> x & 1}
    high_points = {x for x in range(512) if high >> x & 1}
    representatives = []
    covered = set(low_points)
    for v in sorted(high_points - low_points):
        if v not in covered:
            representatives.append(v)
            covered.update({v ^ x for x in low_points})
    answer = set()
    # Enumerate all independent quotient bases of the required size.
    for combo in combinations(representatives, dimension - R.rank(low)):
        points = {x ^ y for x in low_points for y in xor_span(combo)}
        if len(points) == 1 << dimension:
            answer.add(sum(1 << x for x in points))
    return answer


def as_hist(rows):
    return Counter({tuple(row['delta']): row['count'] for row in rows})


# Source-corruption and sign controls are exercised with assertions disabled too.
sources = json.loads((P / 'SOURCES.json').read_text())
row = sources['snapshots'][0]
rejects(lambda: V.authenticate((P / row['local']).read_bytes() + b'x', row), 'source_mutant')
rejects(lambda: S.rows(Counter({(0, 1, -2, 1, 0, 0, 0, 0, 0, 0): 1})), 'profitable_exchange')
rejects(lambda: S.frames(1, R.span((1, 2, 4, 8, 16)), 1), 'resource_guard')
require([len(independent_frames(1, R.span((1, 2, 4)), d)) for d in range(4)] == [1, 7, 7, 1], 'F2^3 lattice')
checks['known_lattice'] += 1

for tag in ('base', 'extra'):
    word = V.load(tag)
    fixed, variable, _, intervals = S.first_moves(word)
    for low, high, d in sorted(intervals):
        require(set(S.frames(low, high, d)) == independent_frames(low, high, d), 'quotient frame enumeration')
        checks['frame_intervals'] += 1
    bridge = S.bridge_census(word, fixed)
    sample = set((sec, p) for sec, p, *_ in bridge['nonzero_cases'])
    for sec in S.PHASES:
        keys = sorted(k for k in fixed if k[0] == sec)
        sample.update(keys[j] for j in (0, len(keys) // 2, len(keys) - 1))
    for sec, p in sorted(sample):
        i, cut, frame = fixed[(sec, p)]
        middle = R.apply_move(word, sec, i, cut, R.basis(frame))
        require(C.frame_bill(middle)[0] == C.frame_bill(word)[0], 'fixed swap not neutral')
        third = [j for j, g in enumerate(middle[sec]) if g[0] == 'add' and j not in (p, p + 1)]
        both = [j for j in third if set(R.touched(word[sec][j])) & set(R.touched(word[sec][p]))
                and set(R.touched(word[sec][j])) & set(R.touched(word[sec][p + 1]))]
        full = list(S.candidates(middle, sec, third, window=(p + 1, p + 1)))
        expected = Counter(d for j, _, _, _, _, d in full if j in both)
        fast = S.bridge_census(word, {(sec, p): fixed[(sec, p)]})
        require(as_hist(fast['profiles']) == expected, 'fast bridge versus full trace')
        # For a non-bridge gate, a before/between/after baseline placement must
        # supply the same exact signed price; do not assume the pruning lemma.
        untouched = sorted(set(j for j, *_ in full) - set(both))
        baseline = {}
        for j, _, d, _, _, delta in S.candidates(word, sec, untouched, window=(p - 1, p + 2)):
            baseline.setdefault(j, set()).add((d, delta))
        for j, _, d, _, _, delta in full:
            if j not in both:
                require((d, delta) in baseline.get(j, set()), 'non-bridge localisation')
                checks['unpruned_nonbridge_prices'] += 1
        checks['bridge_trace_comparisons'] += 1
    # Disable the actual bridge predicate in an isolated module. Its missing
    # nonzero cases must be detected by the same complete-bridge comparison.
    mutant = types.ModuleType('mutant')
    mutant.__file__ = str(P / 'search.py')
    source = (P / 'search.py').read_text()
    old = 'and touched[j] & touched[p + 1]'
    require(source.count(old) == 1, 'production predicate preimage')
    exec(compile(source.replace(old, 'and False'), mutant.__file__, 'exec'), mutant.__dict__)
    require(mutant.bridge_census(word, fixed) != bridge, 'bridge-disable sensitivity')
    checks['production_predicate_sensitivity'] += 1
    # Every changed-frame first word is independently billed in the full
    # census. Here one neutral and one losing case receive literal undo checks.
    for neutral in (True, False):
        sec, i, cut, frame, delta, _ = next(v for v in variable if (v[4] == S.ZERO) == neutral)
        middle = R.apply_move(word, sec, i, cut, R.basis(frame))
        moved = cut - (cut > i)
        undo_cut = i + (moved < i)
        restored = R.apply_move(middle, sec, moved, undo_cut, word[sec][i][-1])
        restored[sec][i][-1] = deepcopy(word[sec][i][-1])
        require(restored == word, 'same-gate collapse/undo')
        checks['literal_undo'] += 1
    # Credited counterfactual PR2957 rollback and recovery, not a new gain.
    oldword = deepcopy(word)
    g, h = oldword['A'][4043:4045]
    require(g[:5] == ['add', 81, 40, 1, 1] and h[:5] == ['add', 81, 17, 1, 1], 'control preimages')
    oldword['A'][4043:4045] = [h[:-1] + [g[-1]], g]
    oldword['cleanup'] = C.derive_cleanup(oldword)
    before, widths, *_ = C.frame_bill(oldword)
    oldword['report']['local_profile'] = {str(r): n for r, n in before.items()}
    recovered = R.apply_move(oldword, 'A', 4043, 4045, h[-1])
    recovered['A'][4044][-1] = deepcopy(h[-1])
    recovered['cleanup'] = C.derive_cleanup(recovered)
    after, widths2, *_ = C.frame_bill(recovered)
    recovered['report']['local_profile'] = {str(r): n for r, n in after.items()}
    require(recovered == word and widths == widths2, 'literal positive-control recovery')
    delta = tuple(after.get(r, 0) - before.get(r, 0) if r else 0 for r in range(10))
    require(delta == (0, 1, -1, -1, 1, 0, 0, 0, 0, 0), 'control profile')
    rejects(lambda: S.rows(Counter({delta: 1})), 'credited_positive_control')
    A.semantics(C, oldword)
    A.semantics(C, recovered)
    checks['dirty_word_controls'] += 2
    bad = deepcopy(recovered)
    bad['A'][4044][3] *= -1
    bad['cleanup'] = C.derive_cleanup(bad)
    rejects(lambda: A.semantics(C, bad), 'wrong_scalar_fresh_cleanup')
    bad = deepcopy(recovered)
    bad['A'][4044][-1] = []
    rejects(lambda: C.frame_bill(bad), 'wrong_frame')
    barrier = next(i for i in range(word['prelude_events'], len(word['A']) - 1)
                   if word['A'][i][0] == 'add' and not R.crosses(word['A'][i], word['A'][i + 1]))
    rejects(lambda: R.apply_move(word, 'A', barrier, barrier + 2, word['A'][barrier][-1]), 'scalar_barrier')

# Independent elementary-matrix calculation for crossing destination/source
# scales in both directions, including negative and fractional powers of two.
def matrix(gates):
    state = [[Fraction(i == j) for j in range(3)] for i in range(3)]
    for g in gates:
        if g[0] == 'add':
            q = Fraction(g[3], g[4])
            state[g[1]] = [x + q * y for x, y in zip(state[g[1]], state[g[2]])]
        else:
            q = Fraction(g[2], g[3])
            state[g[1]] = [q * x for x in state[g[1]]]
    return state

for c in (Fraction(-3, 2), Fraction(1, 4)):
    for q in (Fraction(-2), Fraction(2), Fraction(-1, 2), Fraction(1, 2)):
        for r in range(3):
            for right in (False, True):
                add = ['add', 0, 1, c.numerator, c.denominator, []]
                scale = ['scale', r, q.numerator, q.denominator, []]
                gates = [add, scale] if right else [scale, add]
                toy = {'A': gates, 'B': [], 'restore': [], 'prelude_events': 0, 'warps': []}
                changed = R.apply_move(toy, 'A', 0 if right else 1, 2 if right else 0, [])
                require(matrix(gates) == matrix(changed['A']), 'exact conjugation matrix')
                checks['scale_conjugations'] += 1

print(json.dumps({'status': 'PASS_LOCAL_TWO_ADD_CONTROLS', 'checks': dict(sorted(checks.items())),
                  'new_circuit_gain': False}, sort_keys=True))
