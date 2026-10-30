"""Compile a dual dyadic pair to ADD and unit SCALE operations.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
"""
from fractions import Fraction as Q


def need(test, message):
    if not test:
        raise ValueError(message)


def dyadic(q):
    return q.denominator & (q.denominator - 1) == 0


def unit(q):
    n = abs(q.numerator)
    return n > 0 and n & (n - 1) == 0 and dyadic(q)


def inverse(ops):
    return [(op, r, s, 1 / c if op == 'SCALE' else -c)
            for op, r, s, c in reversed(ops)]


def apply(ops, vector):
    out = list(map(Q, vector))
    for op, r, s, c in ops:
        if op == 'ADD':
            out[r] += c * out[s]
        else:
            need(op == 'SCALE', 'Known operation')
            out[r] *= c
    return out


def compile_basis(a, b, pivot):
    """Return R with a R = e_p^T and R e_p = b, in execution order."""
    a, b = list(map(Q, a)), list(map(Q, b))
    n = len(a)
    need(n == len(b) and 0 <= pivot < n, 'Matching nonempty vectors and pivot')
    need(all(dyadic(q) for q in a + b), 'Dyadic input coefficients')
    need(sum(x * y for x, y in zip(a, b)) == 1, 'Dual pairing equals one')
    current, right = a[:], []

    def emit(op, r, s, c):
        c = Q(c)
        if (op == 'ADD' and not c) or (op == 'SCALE' and c == 1):
            return
        right.append((op, r, s, c))
        if op == 'ADD':
            current[s] += c * current[r]
        else:
            current[r] *= c

    def swap(r, s):
        emit('ADD', r, s, 1)
        emit('ADD', s, r, -1)
        emit('ADD', r, s, 1)
        emit('SCALE', s, s, -1)

    denominator = max(q.denominator for q in a)
    for r in range(n):
        emit('SCALE', r, r, denominator)
    for s in range(n):
        if s == pivot:
            continue
        while current[s]:
            quotient = current[pivot] // current[s]
            emit('ADD', s, pivot, -quotient)
            swap(pivot, s)
    need(unit(current[pivot]), 'Primitive row over the dyadic ring')
    emit('SCALE', pivot, pivot, 1 / current[pivot])
    target = [Q(i == pivot) for i in range(n)]
    need(current == target, 'Euclidean row reduction')

    # If P is the right product, c = P^-1 b and c[p] = 1.
    c = apply(inverse(list(reversed(right))), b)
    need(c[pivot] == 1, 'Normalized column pivot')
    shear = [('ADD', r, pivot, value) for r, value in enumerate(c)
             if r != pivot and value]
    return shear + list(reversed(right))
