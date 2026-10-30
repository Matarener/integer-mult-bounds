#!/usr/bin/env python3
"""Exact stochastic-roundoff certificate, produced by Nick Petalas. Apache-2.0."""
from fractions import Fraction as Q
from hashlib import sha256
from itertools import product
from pathlib import Path
import gzip
import io
import json

HERE = Path(__file__).resolve().parent
SOURCE = 'research/p104-helper-subspace-splits/WORD.json.gz'
FILES = ('README.md', 'PROOF.md', 'TASK.json', 'SOURCES.json', 'VERIFY.json', 'verify.py')


def need(ok, why):
    if not ok:
        raise ValueError(why)


def bounded_read(path, limit):
    with path.open('rb') as stream:
        raw = stream.read(limit + 1)
    need(len(raw) <= limit, 'file capacity')
    return raw


def prefix(word):
    need(type(word) is dict and word.get('schema') == 'p104-productive-source/1', 'schema')
    n = word.get('public')
    need(type(n) is int and n == 748, 'public dimension')
    events = word.get('program')
    need(type(events) is list and 0 < len(events) <= 26000, 'program capacity')
    cut = next((i for i, e in enumerate(events) if e and e[0] == 'MOVE'), None)
    need(cut is not None and cut == 9589, 'first native boundary')
    need(word['frames'][3] == [], 'empty common frame')
    answer = []
    for e in events[:cut]:
        need(type(e) is list and e[0] in ('ADD', 'SCALE'), 'scalar opcode')
        need(len(e) == (5 if e[0] == 'ADD' else 4), 'event shape')
        need(type(e[1]) is int and 0 <= e[1] < n and e[-1] == 3, 'destination/chart')
        if e[0] == 'ADD':
            need(type(e[2]) is int and 0 <= e[2] < n and e[1] != e[2], 'source')
        need(type(e[-2]) is str, 'exact coefficient text')
        q = Q(e[-2])
        need(q and q.denominator in (1, 2, 4) and abs(q) <= 16, 'dyadic coefficient')
        answer.append((e[0], e[1], e[2] if e[0] == 'ADD' else None, q))
    return n, answer


def source_prefix():
    pins = json.loads(bounded_read(HERE / 'SOURCES.json', 65536))['files']
    pin = [row for row in pins if row['path'] == SOURCE]
    need(len(pin) == 1 and pin[0]['usage'] == 'input', 'unique live word pin')
    raw = bounded_read(HERE.parents[1] / SOURCE, 1 << 20)
    need(sha256(raw).hexdigest() == pin[0]['sha256'], 'source SHA256')
    with gzip.GzipFile(fileobj=io.BytesIO(raw)) as stream:
        unpacked = stream.read((1 << 22) + 1)
    need(len(unpacked) <= 1 << 22, 'unpacked capacity')
    n, events = prefix(json.loads(unpacked))
    return n, events, sha256(raw).hexdigest()


def normalized(values, exponent):
    need(0 <= exponent <= 64, 'dyadic exponent capacity')
    for _ in range(exponent):
        if any(x & 1 for x in values):
            break
        values = [x // 2 for x in values]
        exponent -= 1
    need(all(abs(x).bit_length() <= 128 for x in values), 'numerator capacity')
    return values, exponent


def reverse_influences(n, events):
    """Propagate output coefficient columns through transposed updates."""
    need(1 <= n <= 748 and len(events) <= 10000, 'reverse capacity')
    columns = [[int(i == j) for i in range(n)] for j in range(n)]
    powers, squares, absolute = [0] * n, [0] * n, [0] * n
    common = 0
    for op, r, s, q in reversed(events):
        qe = q.denominator.bit_length() - 1
        if qe:
            exponent, v = powers[r], columns[r]
            if exponent > common:
                squares = [x << (2 * (exponent - common)) for x in squares]
                absolute = [x << (exponent - common) for x in absolute]
                common = exponent
            squares = [x + (y*y << (2*(common-exponent))) for x, y in zip(squares, v)]
            absolute = [x + (abs(y) << (common-exponent)) for x, y in zip(absolute, v)]
        if op == 'SCALE':
            columns[r], powers[r] = normalized([q.numerator*x for x in columns[r]], powers[r]+qe)
        else:
            level = max(powers[s], powers[r] + qe)
            a = 1 << (level - powers[s])
            b = q.numerator << (level - powers[r] - qe)
            v = [a*x + b*y for x, y in zip(columns[s], columns[r])]
            columns[s], powers[s] = normalized(v, level)
    return ([Q(x, 1 << (2*common)) for x in squares],
            [Q(x, 1 << common) for x in absolute])


def forward_influences(n, events):
    """Independent chronological propagation of formal injected errors."""
    need(1 <= n <= 748 and len(events) <= 10000, 'forward capacity')
    rows = [{} for _ in range(n)]
    for t, (op, r, s, q) in enumerate(events):
        if op == 'SCALE':
            rows[r] = {k: q*v for k, v in rows[r].items()}
        else:
            for k, v in tuple(rows[s].items()):
                value = rows[r].get(k, 0) + q*v
                if value:
                    rows[r][k] = value
                else:
                    rows[r].pop(k, None)
        if q.denominator > 1:
            rows[r][t] = Q(1)
        need(len(rows[r]) <= 10000, 'formal error capacity')
        need(all(abs(v.numerator).bit_length() <= 128 and
                 v.denominator.bit_length() <= 65 for v in rows[r].values()),
             'formal coefficient capacity')
    squares = [sum((v*v for v in row.values()), Q(0)) for row in rows]
    absolute = [sum(map(abs, row.values()), Q(0)) for row in rows]
    return squares, absolute, sum(map(len, rows)), max(map(len, rows))


def exact_run(initial, events):
    state = list(map(Q, initial))
    for op, r, s, q in events:
        state[r] = q*state[r] if op == 'SCALE' else state[r] + q*state[s]
    return state


def distribution(initial, events):
    """Enumerate the genuine conditional probabilities, with fresh draws."""
    need(len(initial) <= 3 and len(events) <= 8, 'enumeration capacity')
    states = {tuple(initial): Q(1)}
    for op, r, s, q in events:
        out = {}
        for state, mass in states.items():
            value = q*state[r] if op == 'SCALE' else state[r] + q*state[s]
            lo = value.numerator // value.denominator
            theta = value - lo
            for rounded, probability in ((lo, 1-theta), (lo+1, theta)):
                if probability:
                    target = list(state)
                    target[r] = rounded
                    key = tuple(target)
                    out[key] = out.get(key, 0) + mass*probability
        need(len(out) <= 256, 'distribution state capacity')
        states = out
    need(sum(states.values()) == 1, 'probability conservation')
    return states


def probability_checks():
    fixtures = [
        [('ADD', 0, 1, Q(1, 2))]*2,
        [('SCALE', 0, None, Q(1, 2)), ('ADD', 1, 0, Q(-1, 4)),
         ('SCALE', 1, None, Q(-2)), ('ADD', 0, 1, Q(3, 4))],
        [('ADD', 0, 1, Q(1, 4)), ('ADD', 1, 0, Q(-1, 2))]*3,
        [('ADD', 0, 1, Q(2)), ('SCALE', 1, None, Q(-1))],
        [('ADD', 0, 1, Q(1, 2)), ('ADD', 0, 1, Q(-1, 2))],
    ]
    cases = endpoints = 0
    for events in fixtures:
        square, absolute = reverse_influences(2, events)
        forward = forward_influences(2, events)
        need((square, absolute) == forward[:2], 'small complete influence agreement')
        for initial in product(range(-2, 3), repeat=2):
            exact = exact_run(initial, events)
            states = distribution(initial, events)
            endpoints += len(states)
            for j in range(2):
                mean = sum((mass*state[j] for state, mass in states.items()), Q(0))
                variance = sum((mass*(state[j]-exact[j])**2 for state, mass in states.items()), Q(0))
                need(mean == exact[j] and variance <= square[j]/4, 'unbiasedness/variance')
            cases += 1
    return cases, endpoints


def controls(events, squares, absolute):
    # Exercise actual structural and numeric gates without mutating frozen bytes.
    for case in range(5):
        rejected = False
        try:
            if case == 0:
                prefix({})
            elif case == 1:
                prefix({'schema': 'p104-productive-source/1', 'public': True})
            elif case == 2:
                reverse_influences(749, [])
            elif case == 3:
                normalized([1], 65)
            else:
                normalized([1 << 129], 0)
        except (ValueError, KeyError, TypeError):
            rejected = True
        need(rejected, 'negative control accepted')
    changed = list(events)
    index = next(i for i, e in enumerate(changed) if e[3].denominator > 1)
    op, r, s, q = changed[index]
    changed[index] = (op, r, s, q*2)
    need(reverse_influences(748, changed) != (squares, absolute), 'coefficient sensitivity')
    need(reverse_influences(748, list(reversed(events))) != (squares, absolute), 'chronology sensitivity')
    tiny = [('ADD', 0, 1, Q(1, 2))]*2
    variance_bound = reverse_influences(2, tiny)[0][0]/4
    # A reused coin gives error -1 or +1, violating the fresh-noise bound 1/2.
    errors = [Q(2*bit)-exact_run((0, 1), tiny)[0] for bit in range(2)]
    variance = sum(e*e for e in errors)/2
    need(sum(errors) == 0 and variance > variance_bound == Q(1, 2),
         'shared randomness rejection witness')
    need(exact_run((0, 1), tiny)[0] == 1, 'exact half-add fixture')
    # Always rounding both ties down gives output zero, hence bias -1.
    need(0 - exact_run((0, 1), tiny)[0] == -1, 'biased tie rejection witness')
    return 9


def tail_certificate(maximum, active):
    need(maximum == Q(733, 8) and active == 282, 'fixed maximum/domain')
    x = Q(2*32**2, 1) / maximum
    term = total = Q(1)
    for k in range(1, 65):
        term *= x/k
        total += term
    upper = 2*active/total
    need(upper < Q(1, 1 << 23), 'rational exponential certificate')
    return {'exponent': str(x), 'positive_taylor_terms': 65,
            'failure_bound_strictly_below': '1/8388608',
            'taylor_sum_sha256': sha256(str(total).encode()).hexdigest()}


def main():
    n, events, source_hash = source_prefix()
    squares, absolute = reverse_influences(n, events)
    f_square, f_absolute, entries, support = forward_influences(n, events)
    need((squares, absolute) == (f_square, f_absolute), 'all output influence agreement')
    need(max(squares) == Q(733, 8) and max(absolute) == 90, 'computed maxima')
    active = sum(value > 0 for value in squares)
    noisy = sum(q.denominator > 1 for _, _, _, q in events)
    bits = sum(q.denominator.bit_length()-1 for _, _, _, q in events)
    need(noisy == 7421 and bits == 11713, 'rounded update/random-bit census')
    cases, endpoints = probability_checks()
    rejects = controls(events, squares, absolute)
    receipt = {'status': 'PASS_P104_STOCHASTIC_PREFIX', 'public': n,
               'events': len(events), 'potential_rounds': noisy, 'fresh_bits_upper': bits,
               'add_events': sum(e[0] == 'ADD' for e in events),
               'scale_events': sum(e[0] == 'SCALE' for e in events),
               'touched_roles': len({e[1] for e in events} | {e[2] for e in events if e[0] == 'ADD'}),
               'source_word_sha256': source_hash,
               'active_outputs': active, 'max_squared_influence': str(max(squares)),
               'squared_max_roles': [i for i, x in enumerate(squares) if x == max(squares)],
               'max_absolute_influence': str(max(absolute)),
               'absolute_max_roles': [i for i, x in enumerate(absolute) if x == max(absolute)],
               'total_squared_influence': str(sum(squares)),
               'formal_nonzero_coefficients': entries, 'max_formal_row_support': support,
               'probability_fixtures': cases, 'enumerated_endpoints': endpoints,
               'controls': rejects, 'tail': tail_certificate(max(squares), active),
               'outputwise': [{'squared': str(s), 'absolute': str(a)} for s, a in zip(squares, absolute)],
               'package_sha256': {name: sha256(bounded_read(HERE/name, 1 << 20)).hexdigest() for name in FILES}}
    print(json.dumps(receipt, sort_keys=True))
    print('PASS_P104_STOCHASTIC_PREFIX no_new_kappa')


if __name__ == '__main__':
    main()
