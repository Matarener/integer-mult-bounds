"""Sharp exact module at the actual P104 correlated window. Apache-2.0."""

import json
import sys
from collections import Counter
from fractions import Fraction

from algebra import (HERE, INPUTS, WIDTH, ZERO, digest, in_newton, load,
                     monomial, native, need, plan, wrapper)

TARGETS = ('D31', 'D30', 'D29', 'D28', 'D27', 'Q7')


def producer(word):
    needed, events = set(TARGETS), []
    for event in range(2024, -1, -1):
        row = word['program'][event]
        if row[1] in needed:
            events.append(event)
            if row[0] == 'add':
                needed.add(row[2])
    events.reverse()
    need(len(events) == 257 and len(needed) == 58, 'producer closure')
    need(Counter(word['program'][i][0] for i in events) ==
         {'transport': 200, 'add': 57}, 'producer operations')
    active = {'Y27', 'Y26'}
    active_events = []
    frames = {name: word['initial_frames'][name] for name in needed}
    need(all(frame == [] for frame in frames.values()), 'initial empty frames')
    for i in events:
        row = word['program'][i]
        if row[0] == 'transport':
            need(frames[row[1]] == row[2], 'chronological frame')
            frames[row[1]] = row[3]
        else:
            need(frames[row[1]] == frames[row[2]] == row[4], 'ADD common frame')
            if row[2] in active:
                active.add(row[1])
                active_events.append(i)
    need(active_events == [1090, 1129], 'exact correlated source readers')
    d_events = [i for i in events if word['program'][i][1] == 'D31'
                and 1090 <= i <= 1129]
    need(d_events == [1090, 1092, 1129], 'literal cancellation window')
    need(word['program'][1090] == ['add', 'D31', 'Y27', '1/4', [157, 56, 2]],
         'first quarter read')
    need(word['program'][1129] == ['add', 'D31', 'Y26', '1/4', [152, 56, 5, 2]],
         'second quarter read')
    paths = {name: [i for i in events if i < stop and
                   word['program'][i][:2] == ['transport', name]]
             for name, stop in [('Y27', 1090), ('Y26', 1129)]}
    need(all(word['program'][i][0] == 'transport' for i in events
             if word['program'][i][1] in paths), 'borrowed source paths')
    return {'events': events, 'dependencies': sorted(needed), 'paths': paths,
            'window': d_events, 'first_frame': [157, 56, 2],
            'second_frame': [152, 56, 5, 2]}


def quarter(vector):
    need(all(v % 4 == 0 for z in vector for v in z), 'nonintegral quarter')
    return [(a // 4, b // 4) for a, b in vector]


def exact_window(w, recipe):
    v = wrapper(w, plan(recipe['right']), inverse=True)
    first = quarter(v)
    moved = native(first, recipe)
    second = quarter(native(v, recipe))
    need(moved == second, 'linear exact window')
    need(all((a[0] - b[0], a[1] - b[1]) == ZERO
             for a, b in zip(moved, second, strict=True)), 'cancellation')
    return first


def replay_slice(word, recipes, cone, y):
    state = {name: [ZERO] * WIDTH for name in cone['dependencies']}
    state['Y27'] = y[:]
    state['Y26'] = [(-a, -b) for a, b in y]
    need(in_newton(y), 'original source in B9')
    for i in cone['events']:
        row = word['program'][i]
        if row[0] == 'transport':
            if any(z != ZERO for z in state[row[1]]):
                state[row[1]] = native(state[row[1]], recipes[i])
        else:
            p, q = Fraction(row[3]).as_integer_ratio()
            source = state[row[2]]
            need(all(p * v % q == 0 for z in source for v in z), 'slice ADD integrality')
            state[row[1]] = [(a[0] + p * b[0] // q, a[1] + p * b[1] // q)
                             for a, b in zip(state[row[1]], source, strict=True)]
    need(all(all(z == ZERO for z in state[name]) for name in TARGETS),
         'six exact zero collector inputs')
    return {name: digest(state[name]) for name in TARGETS}


def basis_checks(recipe):
    exponents = [max(s.bit_count(), 4 + bool(s & 1)) for s in range(WIDTH)]
    failures = Counter()
    for mask, exponent in enumerate(exponents):
        w = monomial(mask, exponent)
        need(in_newton(w), 'admitted basis in B9')
        exact_window(w, recipe)
        if exponent > mask.bit_count():
            weakened = monomial(mask, exponent - 1)
            need(in_newton(weakened), 'weakened basis remains in B9')
            try:
                exact_window(weakened, recipe)
            except ValueError as exc:
                need(str(exc) in ('nonintegral quarter', 'nonintegral ideal pair'),
                     'expected arithmetic failure')
                failures[str(exc)] += 1
            else:
                raise ValueError('one-pi weakening unexpectedly exact')
    extra = [k - s.bit_count() for s, k in enumerate(exponents)]
    need(sum(extra) == 280 and sum(extra) < 4 * WIDTH, 'sharp index')
    return {'exponents': exponents, 'extra_exponent_histogram': dict(Counter(extra)),
            'basis_accepted': WIDTH, 'one_pi_weakenings_rejected': sum(failures.values()),
            'failure_modes': dict(failures), 'index_B9_log2': sum(extra),
            'index_over_four_B9_log2': 4 * WIDTH - sum(extra)}


def representative_slices(word, recipes, cone):
    records = []
    right = plan(recipes[1092]['right'])
    for mask in (0, 1, 2, 3, 15, 31, 255, 511):
        exponent = max(mask.bit_count(), 4 + bool(mask & 1))
        w = monomial(mask, exponent)
        y = wrapper(w, right, inverse=True)
        for i in reversed(cone['paths']['Y27']):
            y = native(y, recipes[i], inverse=True)
        need(in_newton(y), 'inverse-path Newton membership')
        output = replay_slice(word, recipes, cone, y)
        records.append({'mask': mask, 'exponent': exponent, 'source_sha256': digest(y),
                        'source_in_four_B9': in_newton(quarter(y))
                        if all(v % 4 == 0 for z in y for v in z) else False,
                        'output_sha256': output})
    need(any(not r['source_in_four_B9'] for r in records), 'strict entrance extension')
    return records


def calculate():
    word, recipes = load()
    cone = producer(word)
    need(recipes[1092]['rank'] == 1, 'single coordinate stage')
    return {'schema_version': 1, 'source_hashes': INPUTS, 'producer': cone,
            'native_window_sha256': digest(recipes[1092]),
            'maximal_module': basis_checks(recipes[1092]),
            'literal_slice_fixtures': representative_slices(word, recipes, cone),
            'scope': '257-event dependency slice; noncone outputs unclaimed'}


def main():
    need(sys.argv[1:] in ([], ['--emit']), 'usage: verify.py [--emit]')
    result = calculate()
    if sys.argv[1:] == ['--emit']:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        with (HERE / 'RESULT.json').open('rb') as handle:
            raw = handle.read(1024 * 1024 + 1)
        need(len(raw) <= 1024 * 1024, 'receipt capacity')
        need(digest(json.loads(raw)) == digest(result), 'complete receipt mismatch')
        print('PASS_P104_CORRELATED_EXACT_MODULE index_log2=280 basis=512')


if __name__ == '__main__':
    main()
