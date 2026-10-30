#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Chris R / Clear1nsight, with substantial OpenAI Codex assistance.
"""Parabolic graph compiler and ordered-operation model; no physical backend."""
from itertools import combinations
from math import gcd, prod


def require(test, message):
    if not test:
        raise ValueError(message)


def identity(n):
    return [[int(i == j) for j in range(n)] for i in range(n)]


def multiply(a, b, modulus):
    out = [[0] * len(b[0]) for _ in a]
    for i in range(len(a)):
        for k, x in enumerate(a[i]):
            if x:
                for j, y in enumerate(b[k]):
                    if y:
                        out[i][j] = (out[i][j] + x*y) % modulus
    return out


def inverse(a, modulus):
    n = len(a)
    work = [list(row) + unit for row, unit in zip(a, identity(n))]
    for j in range(n):
        pivot = next((k for k in range(j, n) if gcd(work[k][j], modulus) == 1), None)
        require(pivot is not None, 'nonunit minor')
        work[j], work[pivot] = work[pivot], work[j]
        scalar = pow(work[j][j], -1, modulus)
        work[j] = [scalar*x % modulus for x in work[j]]
        for k in range(n):
            if k != j:
                scalar = work[k][j]
                work[k] = [(x-scalar*y) % modulus for x, y in zip(work[k], work[j])]
    return [row[n:] for row in work]


def row_add(matrix, i, j, a, modulus):
    matrix[i] = [(x+a*y) % modulus for x, y in zip(matrix[i], matrix[j])]


def word_matrix(word, n, modulus):
    ans = identity(n)
    for i, j, a in word:
        row_add(ans, i, j, a, modulus)
    return ans


def invert_word(word):
    return [(i, j, -a) for i, j, a in reversed(word)]


def choose_chart(projector, rank, modulus, supplied=None):
    n = len(projector)
    candidates = [tuple(supplied)] if supplied is not None else combinations(range(n), rank)
    for subset in candidates:
        require(len(subset) == rank and tuple(sorted(set(subset))) == subset and
                all(0 <= i < n for i in subset), 'invalid principal subset')
        try:
            inverse([[projector[i][j] for j in subset] for i in subset], modulus)
        except ValueError:
            continue
        return subset
    raise ValueError('no unit principal chart')


def pivot_groups(n, rank, subset):
    # One active candidate per stage permits grouping the three signed-swap
    # shears into three stars. Zero flags retain fixed support and full payment.
    groups = []
    for i in range(rank):
        candidates = range(i+1, n-rank+i+1)
        first = [(i, k, int(subset[i] == k)) for k in candidates]
        middle = [(k, i, -int(subset[i] == k)) for k in candidates]
        groups.extend([('star', first), ('star', middle), ('star', first[:])])
    require(sum(len(word) for _, word in groups) == 3*rank*(n-rank), 'pivot schedule count')
    return groups


def diagonal_word(diagonal, modulus, rank=None):
    require(prod(diagonal) % modulus == 1, 'diagonal determinant')
    n, out = len(diagonal), []
    count = n-1 if rank is None else rank
    require(all(diagonal[i] == 1 for i in range(count+1, n)), 'unused kernel diagonal')
    for i, a in enumerate(diagonal[:count]):
        k = count
        out += [(k, i, -a*(a-1)), (i, k, -pow(a, -1, modulus)),
                (k, i, a-1), (i, k, 1)]
    return out


def compile_banks(projector, rank, weights, modulus, supplied=None):
    n = len(projector)
    require(0 < rank < n, 'nontrivial rank')
    require(multiply(projector, projector, modulus) == projector, 'idempotence')
    require(len(weights) == n and all(gcd(x, modulus) == 1 for x in weights), 'unit weights')
    subset = choose_chart(projector, rank, modulus, supplied)
    pivots = pivot_groups(n, rank, subset)
    jmat = word_matrix([entry for _, word in pivots for entry in word], n, modulus)
    q = multiply(multiply(jmat, projector, modulus), inverse(jmat, modulus), modulus)
    a = [row[:rank] for row in q[:rank]]
    b = [row[rank:] for row in q[:rank]]
    c = [row[:rank] for row in q[rank:]]
    x = multiply(c, inverse(a, modulus), modulus)
    z = [[-entry % modulus for entry in row] for row in b]
    upper = [(i, rank+k, z[i][k]) for i in range(rank) for k in range(n-rank)]
    lower = [(rank+k, i, x[k][i]) for k in range(n-rank) for i in range(rank)]
    t0 = word_matrix(upper+lower, n, modulus)
    e = [[int(i == j and i < rank) for j in range(n)] for i in range(n)]
    require(multiply(multiply(t0, e, modulus), inverse(t0, modulus), modulus) == q,
            'rank or graph identity')
    # J H J^-1 is diagonal; signed permutation signs cancel.
    d = [weights[next(k for k, v in enumerate(row) if v)] for row in jmat]
    normalized = d[:rank]+[1]*(n-rank)
    normalized[rank] = pow(prod(d[:rank]) % modulus, -1, modulus)
    upper_h = [(i, k, a*d[i]*pow(d[k], -1, modulus) % modulus) for i, k, a in upper]
    lower_h = [(i, k, a*d[i]*pow(d[k], -1, modulus) % modulus) for i, k, a in lower]
    tail = [('graph', upper), ('graph', lower)] + inverse_groups(pivots)
    head = [('single', diagonal_word(normalized, modulus, rank)), ('graph', upper_h),
            ('graph', lower_h)] + inverse_groups(pivots)
    return dict(head=head, tail=tail, subset=list(subset))


def inverse_groups(groups):
    return [(kind, invert_word(word)) for kind, word in reversed(groups)]


def route_groups(groups, n, rank, reflected=False):
    """Return abstract completed primitive calls in chronological left-action order."""
    position = (lambda i: n-1-i) if reflected else (lambda i: i)
    events = []
    t = min(rank, n-rank)
    pairs = [(i, n-t+i) for i in range(t)]
    permutation = list(range(n))
    for i, k in pairs:
        permutation[i], permutation[k] = permutation[k], permutation[i]
    for kind, word in groups:
        if kind in ('graph', 'star'):
            local_pairs = pairs
            local_permutation = permutation
            if kind == 'star':
                vertices = {i for i,j,_ in word} | {j for i,j,_ in word}
                centre = min(vertices)
                endpoint = max(vertices)
                require(all(i == centre or j == centre for i,j,_ in word), 'fixed-centre star')
                local_pairs = [(centre, endpoint)]
                local_permutation = list(range(n))
                local_permutation[centre],local_permutation[endpoint] = endpoint,centre
            ordered = [position(j) < position(i) for i, j, _ in word]
            require(all(ordered) or not any(ordered), 'one bipartite orientation')
            if all(ordered):
                events.extend(('add', i, j, a) for i, j, a in word)
            else:
                events.extend(('swap', i, k, 0) for i, k in local_pairs)
                events.extend(('add', local_permutation[i], local_permutation[j], a) for i, j, a in word)
                events.extend(('swap', i, k, 0) for i, k in reversed(local_pairs))
        else:
            for i, j, a in word:
                if position(j) < position(i):
                    events.append(('add', i, j, a))
                else:
                    events.extend([('swap', i, j, 0), ('add', j, i, a), ('swap', i, j, 0)])
    require(all(kind != 'add' or position(j) < position(i) for kind, i, j, _ in events),
            'every emitted ADD is physically ordered')
    return events


def execute(events, n, modulus):
    ans = identity(n)
    for kind, i, j, a in events:
        if kind == 'swap':
            ans[i], ans[j] = ans[j], ans[i]
        elif kind == 'add':
            row_add(ans, i, j, a, modulus)
        else:
            raise ValueError('unknown primitive')
    return ans


def direct_residual(q, weights, modulus):
    n = len(q)
    ans = [[0]*(2*n) for _ in range(2*n)]
    for i in range(n):
        for j in range(n):
            c = (int(i == j)-q[i][j]) % modulus
            ans[i][j] = weights[i]*c*pow(weights[j], -1, modulus) % modulus
            ans[i][n+j] = weights[i]*q[i][j] % modulus
            ans[n+i][j] = q[i][j]*pow(weights[j], -1, modulus) % modulus
            ans[n+i][n+j] = c
    return ans


def block_diagonal(a, b):
    n = len(a)
    return [row+[0]*n for row in a] + [[0]*n+row for row in b]


def complete_model(projector, rank, weights, modulus, supplied=None):
    n = len(projector)
    banks = compile_banks(projector, rank, weights, modulus, supplied)
    matrices, counts, supports = {}, {'add': 0, 'swap': 0}, []
    for bank in ('head', 'tail'):
        for backwards in (False, True):
            groups = inverse_groups(banks[bank]) if backwards else banks[bank]
            events = route_groups(groups, n, rank, bank == 'tail')
            for kind, *_ in events:
                counts[kind] += 1
            matrices[bank, backwards] = execute(events, n, modulus)
            supports.append([(kind, i, j) for kind, i, j, _ in events])
            if backwards:
                require(multiply(matrices[bank, False], matrices[bank, True], modulus) == identity(n),
                        'each bank restored exactly')
    k = block_diagonal(matrices['head', False], matrices['tail', False])
    kinv = block_diagonal(matrices['head', True], matrices['tail', True])
    e = [[int(i == j and i < rank) for j in range(n)] for i in range(n)]
    result = multiply(multiply(k, direct_residual(e, [1]*n, modulus), modulus), kinv, modulus)
    require(result == direct_residual(projector, weights, modulus), 'complete weighted COPY identity')
    require(counts == invoice(n, rank), 'enumerated full invoice')
    return dict(matrix=result, counts=counts, subset=banks['subset'], supports=supports)


def invoice(n=64, rank=7):
    return {'add': 20*rank*(n-rank)+8*rank,
            'swap': 20*rank+8*min(rank, n-rank)}
