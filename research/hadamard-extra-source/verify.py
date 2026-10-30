"""Exact new Hadamard connector and literal dirty-child replay; stdlib only."""
import hashlib
import json
from pathlib import Path
import sys

H = ((1, 1, 1, 1), (1, -1, 1, -1),
     (1, 1, -1, -1), (1, -1, -1, 1))
SOURCE = ((0, -1), (1, -1), (0, 1), (3, 1), (2, -1),
          (3, -1), (1, 1), (0, 1), (0, -1), (2, 1))
# (visited source-prefix number, output, sign); repeated taps are paid.
TAPS = ((1, 1, -1), (1, 3, -1), (2, 0, -1),
        (3, 1, 1), (3, 1, 1), (4, 0, 1), (4, 2, -1),
        (5, 1, -1), (5, 3, 1), (6, 0, -1),
        (8, 2, 1), (10, 0, 1))
A_LENGTH = (2, 3, 4, 5)
B_LENGTH = (1, 2, 3, 4)
FILES = ('README.md', 'SOURCES.json', 'TASK.json', 'VERIFY.json', 'verify.py')


def require(condition, message):
    if not condition:
        raise ValueError(message)


def program():
    calls = []
    for t in range(11):
        if t:
            j, sign = SOURCE[t - 1]
            calls.append((8, j, ('B', j), sign))
        for at, i, sign in TAPS:
            if at == t:
                calls.append((4 + i, 8, ('A', i), sign))
    require(len(calls) == 22, 'top-level call count')
    return tuple(calls)


def formal_endpoint(calls):
    # Each polynomial maps (outer-to-inner operator word, initial role) to Z.
    rows = [{((), r): 1} for r in range(12)]
    for dst, src, label, sign in calls:
        require(0 <= dst < 12 and 0 <= src < 12 and dst != src,
                'invalid register pair')
        require(sign in (-1, 1), 'invalid sign')
        for (word, root), coefficient in tuple(rows[src].items()):
            key = ((label,) + word, root)
            rows[dst][key] = rows[dst].get(key, 0) + sign * coefficient
            if rows[dst][key] == 0:
                del rows[dst][key]
        require(len(rows[dst]) <= 2048, 'formal polynomial capacity')
    return rows


def expected_endpoint():
    rows = [{((), r): 1} for r in range(12)]
    for i in range(4):
        for j in range(4):
            rows[4 + i][((('A', i), ('B', j)), j)] = H[i][j]
    return rows


def factors(label):
    kind, i = label
    length = A_LENGTH[i] if kind == 'A' else B_LENGTH[i]
    # Listed in application order; the rightmost matrix acts first.
    return tuple((kind, i, k) for k in range(length))


def lower(calls):
    leaves = []
    echoes = 0
    max_depth = 0
    stack = [(d, s, factors(op), sign, (9, 10, 11))
             for d, s, op, sign in reversed(calls)]
    for _ in range(512):
        if not stack:
            break
        dst, src, fs, sign, scratch = stack.pop()
        require(dst != src and dst not in scratch and src not in scratch,
                'dirty scratch aliases an active role')
        max_depth = max(max_depth, 3 - len(scratch))
        if len(fs) == 1:
            leaves.append((dst, src, fs[0], sign))
            continue
        require(len(fs) <= 5 and scratch, 'child depth capacity')
        echoes += 1
        u, rest = scratch[0], scratch[1:]
        cut = len(fs) // 2
        b, a = fs[:cut], fs[cut:]
        parts = [(u, src, b, 1, rest), (dst, u, a, 1, rest),
                 (u, src, b, -1, rest), (dst, u, a, -1, rest)]
        if sign == -1:
            parts = [(d, s, f, -e, pool)
                     for d, s, f, e, pool in reversed(parts)]
        stack.extend(reversed(parts))
    require(not stack, 'lowering iteration bound')
    require(len(leaves) == 208 and echoes == 62 and max_depth == 3,
            'complete child bill')
    return tuple(leaves), echoes


def primitive_expected():
    rows = [{((), r): 1} for r in range(12)]
    for i in range(4):
        for j in range(4):
            word = tuple(reversed(factors(('A', i))))
            word += tuple(reversed(factors(('B', j))))
            rows[4 + i][(word, j)] = H[i][j]
    return rows


def matrix(label, variant):
    kind, i, k = label
    n = 1 + i + 2 * k + (7 if kind == 'A' else 0) + variant
    return ((n % 5 - 2, (n * n + 1) % 7 - 3),
            ((3 * n + 2) % 7 - 3, (n + 3) % 5 - 2))


def apply_matrix(m, v):
    return tuple(sum(m[i][j] * v[j] for j in range(2)) for i in range(2))


def dense_replay(calls, initial, variant):
    rows = [tuple(row) for row in initial]
    for dst, src, label, sign in calls:
        value = apply_matrix(matrix(label, variant), rows[src])
        rows[dst] = tuple(rows[dst][k] + sign * value[k] for k in range(2))
    return rows


def dense_expected(initial, variant):
    rows = [tuple(row) for row in initial]
    for i in range(4):
        for j in range(4):
            value = tuple(initial[j])
            for op in factors(('B', j)) + factors(('A', i)):
                value = apply_matrix(matrix(op, variant), value)
            rows[4 + i] = tuple(rows[4 + i][k] + H[i][j] * value[k]
                                for k in range(2))
    return rows


def check_dense(leaves):
    count = 0
    inverse = tuple((d, s, op, -sign) for d, s, op, sign in reversed(leaves))
    for variant in range(4):
        inputs = []
        for column in range(24):
            inputs.append([tuple(int(2 * r + k == column) for k in range(2))
                           for r in range(12)])
        inputs += [[(r - 7, 3 * r - 8) for r in range(12)],
                   [(5 - 2 * r, r * r - 9) for r in range(12)]]
        for initial in inputs:
            result = dense_replay(leaves, initial, variant)
            require(result == dense_expected(initial, variant), 'dense endpoint')
            require(dense_replay(inverse, result, variant) == initial,
                    'literal full inverse')
            count += 1
    return count


def controls(calls, leaves):
    rejected = 0
    target = expected_endpoint()
    for i in range(len(calls)):
        require(formal_endpoint(calls[:i] + calls[i + 1:]) != target,
                'undetected missing top-level call')
        rejected += 1
    require(formal_endpoint(leaves[:-1]) != primitive_expected(),
            'undetected missing primitive restoration')
    rejected += 1
    # Change one demanded sign: the computed map must reject the false target.
    wrong = expected_endpoint()
    wrong[4][((('A', 0), ('B', 0)), 0)] = -1
    require(formal_endpoint(calls) != wrong, 'undetected target-sign error')
    rejected += 1
    try:
        formal_endpoint(((8, 8, ('A', 0), 1),))
    except ValueError:
        rejected += 1
    else:
        raise ValueError('accepted aliasing')
    return rejected


def receipt():
    hashes = {}
    for name in FILES:
        with (Path(__file__).resolve().parent / name).open('rb') as handle:
            data = handle.read(131073)
        require(len(data) <= 131072, 'receipt file capacity')
        hashes[name] = hashlib.sha256(data).hexdigest()
    return hashes


def main():
    calls = program()
    require(formal_endpoint(calls) == expected_endpoint(), 'formal query map')
    leaves, echoes = lower(calls)
    require(formal_endpoint(leaves) == primitive_expected(), 'formal leaf map')
    a_profile = tuple(sum(op == ('A', i) for _, _, op, _ in calls)
                      for i in range(4))
    b_profile = tuple(sum(op == ('B', i) for _, _, op, _ in calls)
                      for i in range(4))
    require(a_profile == (4, 4, 2, 2) and b_profile == (4, 2, 2, 2),
            'query profiles')
    require(sum(op[0] == 'B' for _, _, op, _ in leaves) == 64, 'source price')
    require(sum(op[0] == 'A' for _, _, op, _ in leaves) == 144, 'readout price')
    print(json.dumps({'status': 'PASS_HADAMARD_EXTRA_SOURCE',
                      'primitive_calls': len(leaves), 'echo_nodes': echoes,
                      'top_level_queries': len(calls),
                      'source_profile': b_profile, 'readout_profile': a_profile,
                      'dense_inputs_and_inverse_pairs': check_dense(leaves),
                      'rejection_controls': controls(calls, leaves),
                      'package_sha256': receipt(), 'python': sys.version,
                      'claim': 'exact construction; no new kappa'}, sort_keys=True))


if __name__ == '__main__':
    main()
