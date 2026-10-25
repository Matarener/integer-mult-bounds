#!/usr/bin/env python3
"""Independent action-table algebra for the immutable CUT58 declaration.

No historical source module or constructor is imported.  A monomial is a
permutation and its phase on every old-four-bit character.  Its global Gaussian
phase is retained separately, so equality covers every positive tensor count f.
Apache-2.0; substantial OpenAI Codex assistance.
"""
from collections import Counter, deque
from fractions import Fraction
import argparse
import hashlib
import gzip
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = HERE / 'source' / 'CUT58.json.gz'

def read_source():
    raw = gzip.decompress(SOURCE.read_bytes())
    need(hashlib.sha256(raw).hexdigest() == '7553ec4f63272cd4b8efb16b2ec01183240be248e36a5dc45df32f9ebd24de58', 'immutable predecessor payload')
    return raw
SOURCE_SHA256 = '7553ec4f63272cd4b8efb16b2ec01183240be248e36a5dc45df32f9ebd24de58'


def need(condition, message):
    if not condition:
        raise ValueError(message)


def table(data, coordinates):
    """Decode the declared action by evaluating every binary character."""
    size = 1 << len(coordinates)
    positions = {j: i for i, j in enumerate(coordinates)}
    permutations, phases = [], []
    for local in range(size):
        x = sum(((local >> i) & 1) << j for i, j in enumerate(coordinates))
        y = data['offset']
        for j, row in enumerate(data['rows']):
            y ^= ((row & x).bit_count() & 1) << j
        need(not (y & ~sum(1 << j for j in coordinates)), 'closed coordinate action')
        permutations.append(sum(((y >> j) & 1) << i for j, i in positions.items()))
        q = data.get('constant', 0)
        for j in coordinates:
            if (x >> j) & 1:
                q += data['alpha'][j] + 2 * ((data['quad'][j] & x).bit_count() & 1)
        phases.append(q % 4)
    return tuple(permutations), tuple(phases), data.get('global_phase', 0) % 4


def identity(bits):
    return tuple(range(1 << bits)), (0,) * (1 << bits), 0


def compose(a, b):
    """A B acts first by B, directly on every character."""
    return (tuple(a[0][y] for y in b[0]),
            tuple((b[1][x] + a[1][b[0][x]]) % 4 for x in range(len(b[0]))),
            (a[2] + b[2]) % 4)


def inverse(a):
    p = [0] * len(a[0])
    for x, y in enumerate(a[0]):
        p[y] = x
    return tuple(p), tuple(-a[1][x] % 4 for x in p), -a[2] % 4


def power(a, n):
    out = identity((len(a[0]) - 1).bit_length())
    if n < 0:
        a, n = inverse(a), -n
    for _ in range(n):
        out = compose(out, a)
    return out


def native_polar(a):
    """Recover binary polar from phase differences, with no chart constructor."""
    q = a[1]
    bits = (len(q) - 1).bit_length()
    rows = []
    for i in range(bits):
        row = ((q[1 << i] - q[0]) & 1) << i
        for j in range(bits):
            if i == j:
                continue
            difference = (q[(1 << i) | (1 << j)] - q[1 << i] - q[1 << j] + q[0]) % 4
            need(difference % 2 == 0, 'Gaussian quadratic phase')
            row |= (difference // 2) << j
        rows.append(row)
    return tuple(rows)


def binary_rank(rows):
    basis = {}
    for row in rows:
        while row:
            pivot = row.bit_length() - 1
            if pivot in basis:
                row ^= basis[pivot]
            else:
                basis[pivot] = row
                break
    return len(basis)


def rank(a):
    return binary_rank(native_polar(a))


def generated(generators):
    bits = (len(next(iter(generators.values()))[0]) - 1).bit_length()
    start = identity(bits)
    words = {start: ''}
    queue = deque([start])
    while queue:
        a = queue.popleft()
        for name, b in generators.items():
            c = compose(a, b)
            if c not in words:
                words[c] = words[a] + name
                queue.append(c)
    return words


def word(text, generators):
    out = identity((len(next(iter(generators.values()))[0]) - 1).bit_length())
    for name in text:
        out = compose(out, generators[name])
    return out


def order(a):
    out = identity((len(a[0]) - 1).bit_length())
    for k in range(1, 257):
        out = compose(out, a)
        if out == identity((len(a[0]) - 1).bit_length()):
            return k
    raise ValueError('order beyond declared screen')


def representatives(group):
    out, seen = [], set()
    for g, text in group.items():
        if g not in seen:
            out.append((g, text))
            seen.add(g)
            seen.add((g[0], g[1], (g[2] + 2) % 4))
    need(len(seen) == len(group), 'literal sign pairs exhaust group')
    return out


def mod_basis(vectors, prime=5):
    basis, selected = {}, []
    for label, vector in vectors:
        row = list(vector)
        for pivot, old in sorted(basis.items()):
            if row[pivot]:
                c = row[pivot]
                row = [(a - c * b) % prime for a, b in zip(row, old)]
        if any(row):
            pivot = next(j for j, a in enumerate(row) if a)
            c = pow(row[pivot], -1, prime)
            basis[pivot] = [a * c % prime for a in row]
            selected.append(label)
    return basis, selected


def mod_determinant(matrix, prime=5):
    matrix = [list(row) for row in matrix]
    determinant = 1
    for i in range(len(matrix)):
        pivot = next((j for j in range(i, len(matrix)) if matrix[j][i]), None)
        need(pivot is not None, 'nonsingular fixed feature certificate')
        if pivot != i:
            matrix[i], matrix[pivot] = matrix[pivot], matrix[i]
            determinant = -determinant
        c = matrix[i][i]
        determinant = determinant * c % prime
        for j in range(i + 1, len(matrix)):
            t = matrix[j][i] * pow(c, -1, prime) % prime
            matrix[j] = [(a - t * b) % prime for a, b in zip(matrix[j], matrix[i])]
    return determinant


def tensor_feature_certificate(reps):
    """An actual 64 by 64 integer Gaussian minor, certified modulo 5."""
    entries = {}
    for x in range(16):
        for y in range(16):
            feature = [pow(2, g[1][x], 5) if g[0][x] == y else 0 for g, _ in reps]
            if any(feature):
                entries[x, y] = feature
    basis1, _ = mod_basis(entries.items())
    products = (((a, b), [x * y % 5 for x, y in zip(v, w)])
                for a, v in entries.items() for b, w in entries.items())
    basis2, selected = mod_basis(products)
    need(len(basis2) == len(reps) == 64, 'tensor-square faithful modulo literal sign')
    fixed = [[a * b % 5 for a, b in zip(entries[tuple(x)], entries[tuple(y)])] for x, y in selected]
    determinant = mod_determinant(fixed)
    need(determinant != 0, 'nonzero Gaussian minor reduced modulo 5')
    return {'one_coordinate_rank_mod5': len(basis1),
            'two_coordinate_rank_mod5': len(basis2),
            'prime': 5, 'gaussian_i_mod_prime': 2,
            'representatives': [text for _, text in reps],
            'selected_tensor_entries': selected,
            'selected_minor_determinant_mod5': determinant}


UNITS = ((1, 0), (0, 1), (-1, 0), (0, -1))


def gaussian_add(a, b):
    return a[0] + b[0], a[1] + b[1]


def gaussian_multiply(a, b):
    return a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0]


def f1_kernel_control(generators):
    # This fixed relation was found by independent exact Gaussian elimination.
    # At f=1 it is zero, while its W-sign twist has a nonzero (0,0) entry.
    terms = [('KWKWKWK', (1, 0)), ('WWW', (1, 0)), ('WKWWK', (-1, 0)),
             ('KWWKW', (-1, 0)), ('KWWKWW', (0, 1)), ('WKWKWW', (0, 1)),
             ('WKWKW', (-1, 0)), ('KWWWK', (-1, 0)), ('WWKWK', (-1, 0)),
             ('KWKWW', (-1, 0)), ('KWWWKW', (0, 1)), ('WKWWKW', (0, 1)),
             ('WWKWKW', (0, 1)), ('KWKWWW', (0, 1)), ('', (0, -1)),
             ('WWWW', (0, -1))]
    original, twisted = {}, {}
    for text, coefficient in terms:
        g = word(text, generators)
        for x in range(16):
            key = g[0][x], x
            a = gaussian_multiply(coefficient, UNITS[(g[1][x] + g[2]) % 4])
            original[key] = gaussian_add(original.get(key, (0, 0)), a)
            if text.count('W') % 2:
                a = -a[0], -a[1]
            twisted[key] = gaussian_add(twisted.get(key, (0, 0)), a)
    need(all(a == (0, 0) for a in original.values()), 'fixed f1 kernel relation')
    need(twisted[0, 0] == (0, -8), 'W-sign twist does not preserve f1 kernel')
    return {'terms': terms, 'original_matrix_is_zero': True,
            'W_twisted_entry_row0_column0': twisted[0, 0],
            'meaning': 'Rejects applying the W-sign or KW-sign twist to arbitrary f1 physical equalities.'}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--write-report', type=Path)
    parser.add_argument('--check-report', type=Path)
    args = parser.parse_args()
    need(not (args.write_report and args.check_report), 'generation and fixed report verification are separate operations')
    raw = read_source()
    need(hashlib.sha256(raw).hexdigest() == SOURCE_SHA256, 'immutable CUT58 source bytes')
    src = json.loads(raw)
    ops = src['operators']
    K, W = (table(ops[name], tuple(range(4))) for name in ('K', 'W'))
    T = table(ops['T'], (10, 11))
    I4, I2 = identity(4), identity(2)
    minus4 = I4[0], I4[1], 2
    minus2 = I2[0], I2[1], 2
    need(power(K, 2) == minus4, 'K squared is literal -I for all f')
    need(power(T, 2) == minus2, 'T squared is literal -I for all f')
    need(power(W, 8) == I4, 'W eighth power')
    need(power(compose(K, W), 4) == I4, 'KW fourth power')
    need(power(compose(W, K), 4) == I4, 'WK fourth power')
    names = ('K', 'W', 'KK', 'WW', 'KW', 'WK', 'KWK', 'WKW', 'KWW', 'WWK', 'KWWW', 'WWWK', 'WWWW')
    words = generated({'K': K, 'W': W})
    need(len(words) == 128, 'exact group closure size')
    for g, text in words.items():
        for name, h in (('K', K), ('W', W)):
            other = words[compose(g, h)]
            need(tuple(other.count(c) % 2 for c in 'KW') ==
                 tuple((text.count(c) + (name == c)) % 2 for c in 'KW'),
                 'every generator transition preserves both sign characters')
    # All all-f scalar elements have trivial K and W sign characters.
    for g, text in words.items():
        if g[0] == I4[0] and len(set(g[1])) == 1:
            need(text.count('K') % 2 == text.count('W') % 2 == 0, 'scalar-compatible characters')
    for g, text in words.items():
        p, q = text.count('K') % 2, text.count('W') % 2
        need(rank(g) >= 2 * (q + (p ^ q)), 'complete group native-rank character tariff')
    zero = [g for g in words if rank(g) == 0]
    zero_set = set(zero)
    closed = all(compose(a, b) in zero_set for a in zero for b in zero)
    normal = closed and all(compose(compose(g, a), inverse(g)) in zero_set for g in words for a in zero)
    result = {
        'source_sha256': hashlib.sha256(raw).hexdigest(),
        'representation': 'complete old-four-bit action table, separate all-f global phase',
        'all_positive_f_equalities': ['K^2=-I', 'T^2=-I', 'W^8=I', '(KW)^4=I', '(WK)^4=I', '[K,T]=[W,T]=0'],
        'products': {name: {'rank_per_f': rank(word(name, {'K': K, 'W': W})), 'order': order(word(name, {'K': K, 'W': W})), 'polar_rows': native_polar(word(name, {'K': K, 'W': W}))} for name in names},
        'old_group_order': len(words),
        'old_group_rank_histogram': dict(sorted(Counter(map(rank, words)).items())),
        'parity_rank_histograms': {str((p, q)): dict(sorted(Counter(rank(g) for g, text in words.items() if (text.count('K') % 2, text.count('W') % 2) == (p, q)).items())) for p in (0, 1) for q in (0, 1)},
        'exact_group_census': [{'word': text, 'K_parity': text.count('K') % 2, 'W_parity': text.count('W') % 2, 'rank_per_f': rank(g)} for g, text in words.items()],
        'tensor_feature_certificate': tensor_feature_certificate(representatives(words)),
        'f1_kernel_control': f1_kernel_control({'K': K, 'W': W}),
        'rank_zero_subgroup_closed': closed,
        'rank_zero_subgroup_normal': normal,
    }
    normalized = json.loads(json.dumps(result))
    if args.write_report:
        args.write_report.write_text(json.dumps(normalized, indent=2, sort_keys=True) + '\n')
        print('WROTE_INDEPENDENT_GROUP_AND_FAITHFULNESS_REPORT', args.write_report)
    elif args.check_report:
        need(json.loads(args.check_report.read_text()) == normalized, 'fixed independent report differs')
        print('PASS_INDEPENDENT_GROUP_AND_FAITHFULNESS_REPORT', 'group128', 'f2rank64', 'allf>=2', 'f1twist_control_rejected')
    else:
        print(json.dumps(normalized, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
