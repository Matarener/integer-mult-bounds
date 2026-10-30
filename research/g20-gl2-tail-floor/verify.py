#!/usr/bin/env python3
"""Exact G20 XOR census. Charan/theon199 + OpenAI Codex, Apache-2.0.

No predecessor executable is imported. check.py uses full truth tables instead.
"""
import argparse
from collections import Counter, deque
from copy import deepcopy
from hashlib import sha1, sha256
from itertools import permutations, product
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
GENERATORS = [(d, s) for d in range(4) for s in range(4) if d != s]
IDENTITY = sum(1 << (5*i) for i in range(4))
BASES = list(permutations((1, 2, 3), 2))
COMPONENTS = [[20, 21, 24, 25], [16, 17, 28, 29], [18, 19, 26, 27]]
SOURCE_SHA256 = '978536e852c0cfbc150f143e19d2cfddbb434bac6017d914974eb99f641593a8'
SOURCE_BLOB = '73fa9f40a032f11dabf357eba69066fcf9bf0a02'


def need(ok, message):
    if not ok:
        raise ValueError(message)


def step(state, gate):
    d, s = gate
    return state ^ (((state >> (4*s)) & 15) << (4*d))


def source(raw):
    need(sha256(raw).hexdigest() == SOURCE_SHA256, 'source SHA256')
    need(sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
         == SOURCE_BLOB, 'source Git blob')
    return json.loads(raw)


def boundary_rows(word):
    rows = [1 << i for i in range(32)]
    for op, d, s in word:
        need(op in ('ADD', 'SWAP') and 0 <= d < 32 and 0 <= s < 32 and d != s,
             'boundary instruction')
        if op == 'ADD':
            rows[d] ^= rows[s]
        else:
            rows[d], rows[s] = rows[s], rows[d]
    return rows


def bind_components(controller):
    """Bind every source instruction touching the three direct summands."""
    b = controller['boundaries']
    for side in ('left', 'right'):
        rows = boundary_rows(b[side + '_program'])
        need(rows == b[side + '_rows'], 'source boundary rows')
        for roles in COMPONENTS:
            owned = set(roles)
            for _, d, s in b[side + '_program']:
                need((d in owned) == (s in owned), 'component isolation')
            restricted = [sum(((rows[d] >> s) & 1) << j
                              for j, s in enumerate(roles)) for d in roles]
            need(restricted == [4, 8, 1, 2], 'complete two-pair exchange')
            need(all((rows[d] >> s) & 1 == 0 for d in roles
                     for s in range(32) if s not in owned), 'no external input')
    diag = controller['diagonal']
    need(len(diag) == 32, 'diagonal size')
    for a, b, c, d in COMPONENTS:
        need(diag[a] == diag[b] and diag[c] == diag[d], 'equal target pair')
        need(diag[a] != diag[c], 'distinct target pairs')


def enumerate_group():
    distances, parents = {IDENTITY: 0}, {}
    queue = deque([IDENTITY])
    while queue:
        state = queue.popleft()
        for index, gate in enumerate(GENERATORS):
            nxt = step(state, gate)
            if nxt not in distances:
                distances[nxt] = distances[state] + 1
                parents[nxt] = state, index
                queue.append(nxt)
    return distances, parents


def word_for(state, parents):
    word = []
    while state != IDENTITY:
        state, index = parents[state]
        word.append(index)
    return word[::-1]


def target(a, b):
    # R S, with R exchanging the pairs and S=diag(A,B).
    return sum(row << (4*i) for i, row in enumerate([b[0] << 2, b[1] << 2, *a]))


def construct():
    distances, parents = enumerate_group()
    candidates = []
    for a, b in product(BASES, repeat=2):
        state = target(a, b)
        candidates.append(dict(A=list(a), B=list(b), state=state,
                               cost=distances[state], word=word_for(state, parents)))
    return dict(schema='g20-gl2-tail-floor/v1', source_sha256=SOURCE_SHA256,
                components=COMPONENTS, generators=[list(g) for g in GENERATORS],
                potential=sorted([state, d] for state, d in distances.items()),
                candidates=candidates)


def rank(state):
    basis = {}
    for i in range(4):
        row = (state >> (4*i)) & 15
        while row:
            p = row.bit_length() - 1
            if p not in basis:
                basis[p] = row
                break
            row ^= basis[p]
    return len(basis)


def validate(certificate):
    need(certificate['schema'] == 'g20-gl2-tail-floor/v1', 'certificate schema')
    need(certificate['source_sha256'] == SOURCE_SHA256, 'certificate source')
    need(certificate['components'] == COMPONENTS, 'component coverage')
    need(certificate['generators'] == [list(g) for g in GENERATORS], 'paid alphabet')
    pairs = certificate['potential']
    need(all(type(s) is int and type(d) is int and 0 <= s < 65536 and 0 <= d <= 9
             for s, d in pairs), 'potential types and range')
    distances = dict(pairs)
    need(len(pairs) == len(distances) == 20160, 'complete unique potential domain')
    need(set(distances) == {s for s in range(65536) if rank(s) == 4},
         'every invertible binary matrix')
    need(distances[IDENTITY] == 0, 'identity potential')
    edges = 0
    for state, d in distances.items():
        neighbors = [distances[step(state, gate)] for gate in GENERATORS]
        need(all(abs(e-d) <= 1 for e in neighbors), 'unit-edge potential inequality')
        need(state == IDENTITY or d > 0 and d-1 in neighbors, 'descending path')
        edges += len(neighbors)
    candidates = certificate['candidates']
    need([(c['A'], c['B']) for c in candidates] ==
         [(list(a), list(b)) for a, b in product(BASES, repeat=2)], 'all 36 bases')
    for c in candidates:
        a, b = tuple(c['A']), tuple(c['B'])
        state = target(a, b)
        need(c['state'] == state and c['cost'] == distances[state], 'candidate potential')
        need(len(c['word']) == c['cost'], 'complete charged word')
        actual = IDENTITY
        for index in c['word']:
            need(type(index) is int and 0 <= index < len(GENERATORS), 'gate index')
            actual = step(actual, GENERATORS[index])
        need(actual == state, 'literal endpoint')
    histogram = Counter(c['cost'] for c in candidates)
    need(min(histogram) == 6, 'sharp local floor')
    return dict(states=len(distances), directed_edges=edges,
                full_rank_matrices=20160, pair_bases=36, components=COMPONENTS,
                candidate_cost_histogram={str(k): v for k, v in sorted(histogram.items())},
                minimum_per_side_per_component=6, component_local_tail_per_side=18,
                component_local_tail_both_sides_111_ports=3996)


def reject(action, expected):
    try:
        action()
    except ValueError as error:
        need(str(error) == expected, 'wrong negative-control failure: ' + str(error))
    else:
        raise ValueError('negative control accepted: ' + expected)


def controls(cert, controller, raw):
    cases = []
    reject(lambda: source(raw + b' '), 'source SHA256')
    cases.append('source_byte_drift')
    for name, mutate, reason in [
        ('missing_state', lambda x: x['potential'].pop(), 'complete unique potential domain'),
        ('false_distance', lambda x: x['potential'].__setitem__(0, [x['potential'][0][0], 0]),
         'unit-edge potential inequality'),
        ('missing_pair_basis', lambda x: x['candidates'].pop(), 'all 36 bases'),
        ('unpaid_final_xor', lambda x: x['candidates'][0]['word'].pop(), 'complete charged word'),
        ('wrong_generator', lambda x: x['generators'][0].__setitem__(1, 0), 'paid alphabet'),
        ('wrong_endpoint', lambda x: x['candidates'][0].__setitem__('state', IDENTITY),
         'candidate potential'),
        ('wrong_paid_word', lambda x: x['candidates'][0]['word'].__setitem__(0, 0),
         'literal endpoint'),
    ]:
        bad = deepcopy(cert)
        mutate(bad)
        reject(lambda: validate(bad), reason)
        cases.append(name)
    for name, mutate, reason in [
        ('unequal_target_pair', lambda x: x['diagonal'].__setitem__(20, 0), 'equal target pair'),
        ('cross_component_gate', add_cross_component_gate, 'component isolation'),
    ]:
        bad = deepcopy(controller)
        mutate(bad)
        reject(lambda: bind_components(bad), reason)
        cases.append(name)
    return cases


def add_cross_component_gate(controller):
    controller['boundaries']['right_program'].append(['ADD', 20, 0])
    controller['boundaries']['right_rows'] = boundary_rows(controller['boundaries']['right_program'])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write-new', type=Path, help='emit evidence to a fresh directory only')
    args = parser.parse_args()
    raw = (HERE/'inputs/CONTROLLER.json').read_bytes()
    controller = source(raw)
    bind_components(controller)
    certificate = construct() if args.write_new else json.loads((HERE/'CERTIFICATE.json').read_bytes())
    result = validate(certificate)
    result['negative_controls'] = controls(certificate, controller, raw)
    result['status'] = 'PASS_G20_GL2_TAIL_FLOOR'
    if args.write_new:
        args.write_new.mkdir(parents=True, exist_ok=False)
        (args.write_new/'CERTIFICATE.json').write_text(json.dumps(certificate, separators=(',', ':'))+'\n')
        (args.write_new/'RESULT.json').write_text(json.dumps(result, indent=2)+'\n')
    else:
        need(result == json.loads((HERE/'RESULT.json').read_bytes()), 'exact result receipt')
    print(json.dumps(result, sort_keys=True))


if __name__ == '__main__':
    main()
