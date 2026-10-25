#!/usr/bin/env python3
"""Exact two-axis boundary audit. Apache-2.0; scope and credit in README."""
import argparse
from collections import Counter
import hashlib
import itertools
import json
from pathlib import Path
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
J = [0, 1, 3, 6, 22, 31, 93, 103]

def need(ok, why):
    if not ok:
        raise ValueError(why)

def read(path):
    def unique(pairs):
        d = {}
        for k, v in pairs:
            need(k not in d, 'duplicate JSON key')
            d[k] = v
        return d
    return json.loads(path.read_text(encoding='utf-8'), object_pairs_hook=unique)

def canonical(x):
    return (json.dumps(x, sort_keys=True, separators=(',', ':')) + '\n').encode()

def authenticate():
    for row in read(HERE / 'SOURCES.json')['files']:
        if row['usage'] != 'input':
            continue
        p = ROOT / row['path']
        need(not p.is_symlink(), 'source symlink')
        raw = p.read_bytes()
        need(hashlib.sha256(raw).hexdigest() == row['sha256'], 'source hash: ' + row['path'])
        need(hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest() == row['git_blob'], 'source blob')

def rank_binary(rows):
    basis = {}
    for v in rows:
        while v:
            b = v.bit_length() - 1
            if b in basis:
                v ^= basis[b]
            else:
                basis[b] = v
                break
    return len(basis)

def inverse_binary(rows):
    n = len(rows)
    a = [r | (1 << (n + i)) for i, r in enumerate(rows)]
    for j in range(n):
        k = next(i for i in range(j, n) if a[i] >> j & 1)
        a[j], a[k] = a[k], a[j]
        for i in range(n):
            if i != j and a[i] >> j & 1:
                a[i] ^= a[j]
    need([v & ((1 << n) - 1) for v in a] == [1 << i for i in range(n)], 'binary inverse')
    return [v >> n for v in a]

def geometry():
    roots = set()
    for i, j in itertools.combinations(range(8), 2):
        for s in (-1, 1):
            r = [0] * 8
            r[i], r[j] = 2, 2 * s
            roots.add(tuple(r))
    for signs in itertools.product((-1, 1), repeat=7):
        if signs.count(-1) % 2 == 0:
            roots.add((1,) + signs)
    roots = sorted(roots)
    dot = lambda a, b: sum(x * y for x, y in zip(a, b))
    rows = [sum((((dot(a, b) // 4) + 1) & 1) << j for j, b in enumerate(roots)) for a in roots]
    ix, base = [], []
    for i, r in enumerate(rows):
        if rank_binary(base + [r]) > len(base):
            ix.append(i)
            base.append(r)
    need(len(ix) == 9, 'root-code rank')
    labels = [sum(((r >> j) & 1) << k for k, j in enumerate(ix)) for r in rows]
    dual = inverse_binary([labels[i] for i in ix])
    def pairing(a, b):
        db = sum(((r & b).bit_count() % 2) << i for i, r in enumerate(dual))
        return (a & db).bit_count() % 2
    space, orth = list(range(512)), []
    for dim in range(9, 0, -1):
        for v in space:
            if not pairing(v, v):
                continue
            rest = [w for w in space if not pairing(v, w)]
            if dim == 1 or any(pairing(w, w) for w in rest):
                orth.append(v)
                space = rest
                break
        else:
            raise ValueError('orthonormal basis')
    physical = [sum(pairing(l, v) << j for j, v in enumerate(orth)) for l in labels]
    need(len(set(physical)) == 120, 'distinct physical roots')
    need(all(((physical[i] & physical[j]).bit_count() % 2) == ((rows[i] >> j) & 1)
             for i in range(120) for j in range(120)), 'all physical pairings')
    fixture = read(ROOT / 'research/p104-native-channel/inputs/P104-FIXTURE.json')['section4_explicit_P104']
    removed = {tuple(r) for r in fixture['F0'] + fixture['C']}
    original_ports = [r for r in roots if r not in removed]
    order = J + [i for i in range(104) if i not in J]
    ports = [original_ports[i] for i in order]
    p = [physical[roots.index(r)] for r in ports]
    need(len(p) == 104 and all(v.bit_count() % 2 for v in p), 'odd P104 roots')
    A2 = [[dot(r, s) // 4 for s in ports] for r in ports]
    B2 = [row[8:] for row in A2[:8]]
    need(sum(bool(v) for row in B2 for v in row) == 384, 'B support')
    need(all(sum(B2[i][t] * B2[j][t] for t in range(96)) == 48 * (i == j)
             for i in range(8) for j in range(8)), 'BBt = 12I')
    D2 = [[(2 * (i == j) if i < 8 and j < 8 else A2[i][j] - 2 * (i == j))
           for j in range(104)] for i in range(104)]
    Di2 = [[(-22 * (i == j) if i < 8 and j < 8 else
             -2 * (i == j) if i >= 8 and j >= 8 else A2[i][j])
            for j in range(104)] for i in range(104)]
    need(all(sum(D2[i][k] * Di2[k][j] for k in range(104)) == 4 * (i == j)
             for i in range(104) for j in range(104)), 'D inverse')
    return p, D2, Di2, {'pivots': ix, 'dual': dual, 'orth': orth}

def add(a, b):
    return [(x[0] + y[0], x[1] + y[1]) for x, y in zip(a, b)]

def neg(a):
    return [(-x, -y) for x, y in a]

def phase(a, powers):
    return [((x, y), (-y, x), (-x, -y), (y, -x))[k % 4] for (x, y), k in zip(a, powers)]

def halfmat(rows, vec):
    out = []
    for row in rows:
        a = sum(c * vec[j][0] for j, c in enumerate(row) if c)
        b = sum(c * vec[j][1] for j, c in enumerate(row) if c)
        need(a % 2 == b % 2 == 0, 'integer replay scale')
        out.append((a // 2, b // 2))
    return out

def mask(a):
    return [(0, 0)] * 8 + a[8:]

def encode(a, b, D, t):
    return add(halfmat(D, a), phase(mask(b), t)), b

def decode(r, b, Di, t):
    return halfmat(Di, add(r, neg(phase(mask(b), t)))), b

def physical_correct(r, b, D, Di, t):
    a, _ = decode(r, b, Di, t)
    return encode(a, add(b, phase(a, [-v for v in t])), D, t)

def conjugated(r, b, Di, t, wrong=False):
    delta = add(halfmat(Di, r), neg(halfmat(Di, phase(mask(b), t))))
    return (r if wrong else add(r, mask(delta))), add(b, phase(delta, [-v for v in t]))

def reader_word(D):
    word = [('add', i, 104+i, -1) for i in range(8)]
    word += [('half', 104+i) for i in range(104)]
    word += [('add', i, 104+j, -D[i][j]) for i in range(104) for j in range(104)
             if D[i][j] and not (i < 8 and i == j)]
    word += [('double', 104+i) for i in range(104)]
    return word

def check_reader(D, word):
    state = [[2 * (i == j) for j in range(280)] for i in range(280)]
    counts = Counter()
    for op in word:
        counts[op[0]] += 1
        t = op[1]
        if op[0] == 'add':
            _, t, s, c = op
            need(t < 104 and 104 <= s < 208 and c in (-1, 1), 'strict unit reader')
            state[t] = [a+c*b for a, b in zip(state[t], state[s])]
        elif op[0] == 'half':
            need(all(v % 2 == 0 for v in state[t]), 'reader exact half')
            state[t] = [v//2 for v in state[t]]
        elif op[0] == 'double':
            state[t] = [2*v for v in state[t]]
        else:
            raise ValueError('reader instruction')
    for i in range(280):
        want = [2 * (i == j) for j in range(280)]
        if i < 104:
            for j in range(104):
                want[104+j] -= D[i][j]
        need(state[i] == want, 'complete reader endpoint/donor/dirty return')
    need(dict(counts) == {'add': 5000, 'half': 104, 'double': 104}, 'reader bill')
    return {'events': len(word), 'counts': dict(counts), 'input_columns': 280,
            'coefficient_sha256': hashlib.sha256(canonical(state)).hexdigest()}

def cost_gate(profile, progress=2312, stages=208, ports=104, axes=9, extras=0, paid_banks=0):
    need(all(type(k) is int and type(v) is int and 0 < k <= axes * axes and v >= 0
             for k, v in profile.items()), 'cost profile')
    need(type(paid_banks) is int and paid_banks >= 0 and extras >= 0, 'nonnegative added costs')
    W = 2 * ports * ports + 2 * ports * 72 + paid_banks
    m = axes * axes
    required_progress = W * m - ports * ports
    remaining = required_progress - stages * progress
    need(remaining >= 0, 'coverage premise')
    bill = stages * sum(r * n for r, n in profile.items()) + remaining + extras
    return {'m': m, 'W': W, 'data_pairs': ports * ports, 'local_calls': stages,
            'required_progress': required_progress, 'remaining_rank': remaining,
            'lower_mass': bill, 'capacity': W * m, 'excess': bill - W * m}

def compute():
    authenticate()
    p, D, Di, iso = geometry()
    need(sum(bool(x) for row in D for x in row) == 5000, 'direct encoded reader count')
    reader = check_reader(D, reader_word(D))
    tensor = lambda a, b: sum((b << (9 * k)) for k in range(9) if (a >> k) & 1)
    product_lines = [tensor(a, b) for a in p for b in p]
    need(len(set(product_lines)) == 10816 and all(u.bit_count() % 2 for u in product_lines),
         'explicit nondegenerate tensor lines')
    weights = Counter(u.bit_count() % 4 for u in product_lines)
    # The old triple generators have weight nine; these product root lines
    # need their actual port-dependent phase, not the inherited constant i^9.
    need(set(weights) <= {1, 3}, 'odd tensor weights')
    for z in range(512):
        Z = sum((1 << (9 * k)) for k in range(9) if z >> k & 1)
        need(all((u.bit_count() + (Z ^ u).bit_count() +
                  2 * ((Z ^ u) & u).bit_count() - Z.bit_count()) % 4 == 0
                 for u in product_lines), 'physical endpoint normalization')
    commuting, defect_blocks = [], 0
    for z in range(512):
        t = [(v & z).bit_count() % 2 for v in p]
        mismatch = sum(bool(D[i][j]) and t[i] != t[j] for i in range(104) for j in range(104))
        defect_blocks += mismatch
        if not mismatch:
            commuting.append(z)
        for seed in (1, 7):
            r = [(16 * (((i * seed + 3) % 13) - 6), 16 * (((i + seed) % 7) - 3)) for i in range(104)]
            b = [(16 * (((i + seed) % 11) - 5), 16 * (((i * seed) % 5) - 2)) for i in range(104)]
            need(physical_correct(r, b, D, Di, t) == conjugated(r, b, Di, t), 'physical conjugation')
    need(commuting == [0, 511], 'homogeneous phase controls')
    columns = 0
    for z in (0, 1, 232, 511):
        t = [(v & z).bit_count() % 2 for v in p]
        for j in range(208):
            r, b = [(0, 0)] * 104, [(0, 0)] * 104
            (r if j < 104 else b)[j % 104] = (16, 0)
            need(physical_correct(r, b, D, Di, t) == conjugated(r, b, Di, t), 'all-column conjugation')
            columns += 1
    i, j = next((i, j) for i in range(8) for j in range(8, 104) if D[i][j])
    z = next(z for z in range(512) if ((p[i] ^ p[j]) & z).bit_count() % 2)
    order = J + [k for k in range(104) if k not in J]
    witness = {'row_port': order[i], 'donor_port': order[j],
               'p_row': p[i], 'p_donor': p[j], 'frequency': z,
               'q': p[0], 'u_row': tensor(p[i], p[0]), 'u_donor': tensor(p[j], p[0]),
               'D_twice_coefficient': D[i][j], 'physical_difference_rank': '2^(m-1)'}
    word = read(ROOT / 'research/p104-native-channel/inputs/LOWRANK-WITNESS.json')
    profile = Counter(op[4] for op in word['program'] if op[0] == 'transport')
    persistent = sum(len(word['final_frames'][r]) - len(v) for r, v in word['initial_frames'].items())
    need(persistent == 2312 and sum(r * n for r, n in profile.items()) == 2368, 'inherited channel invoice')
    profile[1] += 208
    gate = cost_gate(profile, persistent)
    need(gate['excess'] == 44096 and gate['lower_mass'] == 3009344, 'two-axis stop')
    need(cost_gate(profile, paid_banks=123)['excess'] == gate['excess'], 'fully paid banks')
    return {'schema_version': 1, 'status': 'PASS_P104_TWO_AXIS_COMPATIBILITY',
            'scope': 'Physical endpoint equations and explicit tensor-line scaffold; conditional unchanged-profile cost rejection, not a global owner embedding or supplier.',
            'root_pairings': 14400, 'physical_labels': p, 'label_isometry': iso,
            'tensor_lines': 10816, 'tensor_dimension': 81,
            'tensor_weights_mod_four': dict(sorted(weights.items())),
            'constant_weight_nine_phase_failures': weights[3],
            'normalization_character_checks': 512 * 10816,
            'D_entries': 5000, 'D_inverse_checked_entries': 10816,
            'literal_reader': reader,
            'phase_patterns': 512, 'commuting_patterns': commuting,
            'noncommuting_patterns': 510, 'commutator_nonzero_blocks': defect_blocks,
            'dense_conjugation_fixtures': 1024, 'independent_data_columns': columns,
            'encoded_residual_change_rank_per_address': 96,
            'dirty_roles': 72, 'dirty_action': 'identity in compatibility maps; completed physical F is inherited, not freshly executed',
            'witness': witness, 'gate': gate,
            'decision': 'NARROW; no native/supplier expansion within the rejected scaffold'}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--write-result', action='store_true')
    args = ap.parse_args()
    result = compute()
    if args.write_result:
        need(not (HERE / 'RESULT.json').exists(), 'refuse receipt overwrite')
        (HERE / 'RESULT.json').write_bytes(canonical(result))
    else:
        expected = read(HERE / 'RESULT.json')
        need(type(expected.get('schema_version')) is int and canonical(expected) == canonical(result), 'exact typed result')
    print(result['status'])

if __name__ == '__main__':
    main()
