"""Enumerate small stabilizer states and Clifford actions in two ways.

The literal vectors use projective phases 0, 1, i, -1, -i. The second
enumerator uses signed Pauli images and no state vectors.
Ali Romman, with substantial OpenAI Codex assistance. Apache-2.0.
"""
from collections import Counter, deque

UNITS = ((0, 0), (1, 0), (0, 1), (-1, 0), (0, -1))


def require(ok, message):
    if not ok:
        raise ValueError(message)


def canonical(values):
    a, b = next(value for value in values if value != (0, 0))
    norm = a*a+b*b
    result = []
    for c, d in values:
        if not (c or d):
            result.append(0)
            continue
        require(c*c+d*d == norm, "Unequal stabilizer amplitude magnitudes")
        real, imag = c*a+d*b, d*a-c*b
        require(real % norm == imag % norm == 0, "Non-Gaussian projective phase")
        result.append(UNITS.index((real//norm, imag//norm)))
    return tuple(result)


def literal_gate(state, gate):
    kind, j, *other = gate
    if kind == "H":
        out = []
        for x in range(len(state)):
            a, b = UNITS[state[x & ~(1 << j)]]
            c, d = UNITS[state[x | (1 << j)]]
            sign = -1 if x >> j & 1 else 1
            out.append((a+sign*c, b+sign*d))
        return canonical(out)
    if kind == "S":
        out = [0 if value == 0 else 1+(value-1+((x >> j) & 1)) % 4
               for x, value in enumerate(state)]
    elif kind == "CX":
        k = other[0]
        out = [state[x ^ (((x >> j) & 1) << k)] for x in range(len(state))]
    else:
        raise ValueError("Unknown literal gate")
    phase = next(value-1 for value in out if value)
    return tuple(0 if value == 0 else 1+(value-1-phase) % 4 for value in out)


def gates(n):
    out = [(kind, j) for j in range(n) for kind in ("H", "S")]
    out += [("CX", j, j+1) for j in range(n-1)]
    out += [("CX", j+1, j) for j in range(n-1)]
    return out


def orbit(initial, alphabet):
    found = {initial}
    queue = deque([initial])
    while queue:
        state = queue.popleft()
        for gate in alphabet:
            value = literal_gate(state, gate)
            if value not in found:
                found.add(value)
                queue.append(value)
    return sorted(found)


def stabilizer_states(n):
    return orbit((1,)+(0,)*((1 << n)-1), gates(n))


def clifford_choi(n):
    initial = tuple(int((x & ((1 << n)-1)) == (x >> n)) for x in range(1 << (2*n)))
    return orbit(initial, gates(n))


def state_overlap_histogram(states):
    histogram = Counter()
    zero = 0
    for state in states:
        if not state[0]:
            zero += 1
        else:
            support = sum(bool(x) for x in state)
            require(support & (support-1) == 0, "State support is not a power of two")
            histogram[support.bit_length()-1] += 1
    return dict(sorted(histogram.items())), zero


def choi_overlap_histogram(states, n):
    histogram = Counter()
    zero = 0
    dimension = 1 << n
    for state in states:
        row_weight = sum(bool(x) for x in state[:dimension])
        require(row_weight > 0 and row_weight & (row_weight-1) == 0, "Clifford row weight")
        a = b = 0
        for x in range(dimension):
            c, d = UNITS[state[x | (x << n)]]
            a += c
            b += d
        numerator = a*a+b*b
        if not numerator:
            zero += 1
            continue
        denominator = row_weight*dimension*dimension
        require(denominator % numerator == 0, "Clifford trace norm divisor")
        quotient = denominator//numerator
        require(quotient & (quotient-1) == 0, "Clifford trace norm power")
        histogram[quotient.bit_length()-1] += 1
    return dict(sorted(histogram.items())), zero


def binary_rank(rows):
    pivots = {}
    for row in rows:
        while row:
            bit = row.bit_length()-1
            if bit not in pivots:
                pivots[bit] = row
                break
            row ^= pivots[bit]
    return len(pivots)


def pauli_gate(value, gate):
    x, z, phase = value
    kind, j, *other = gate
    if kind == "H":
        a, b = (x >> j) & 1, (z >> j) & 1
        phase += 2*a*b
        if a != b:
            x ^= 1 << j
            z ^= 1 << j
    elif kind == "S":
        a = (x >> j) & 1
        phase += a
        z ^= a << j
    elif kind == "CX":
        k = other[0]
        x ^= ((x >> j) & 1) << k
        z ^= ((z >> k) & 1) << j
    else:
        raise ValueError("Unknown Pauli gate")
    return x, z, phase % 4


def pauli_product(a, b):
    x, z, p = a
    y, w, q = b
    return x ^ y, z ^ w, (p+q+2*((z & y).bit_count() % 2)) % 4


def pauli_image(tableau, x, z):
    n = len(tableau)//2
    value = (0, 0, (x & z).bit_count() % 4)
    for j in range(n):
        if x >> j & 1:
            value = pauli_product(value, tableau[j])
    for j in range(n):
        if z >> j & 1:
            value = pauli_product(value, tableau[n+j])
    return value


def pauli_census(n):
    initial = tuple([(1 << j, 0, 0) for j in range(n)]+[(0, 1 << j, 0) for j in range(n)])
    found, queue = {initial}, deque([initial])
    alphabet = gates(n)
    while queue:
        tableau = queue.popleft()
        for gate in alphabet:
            value = tuple(pauli_gate(p, gate) for p in tableau)
            if value not in found:
                found.add(value)
                queue.append(value)
    histogram, zero, fibers = Counter(), 0, {}
    for tableau in found:
        columns = tuple(x | (z << n) for x, z, _ in tableau)
        rank = binary_rank([x ^ (1 << j) for j, x in enumerate(columns)])
        trace = 0
        for x in range(1 << n):
            for z in range(1 << n):
                a, b, phase = pauli_image(tableau, x, z)
                if (a, b) == (x, z):
                    delta = (phase-(x & z).bit_count()) % 4
                    require(delta in (0, 2), "Non-Hermitian fixed-Pauli phase")
                    trace += 1 if delta == 0 else -1
        require(trace in (0, 1 << (2*n-rank)), "Pauli trace magnitude")
        fiber = fibers.setdefault(columns, [rank, 0, 0])
        fiber[1] += 1
        fiber[2] += bool(trace)
        if trace:
            histogram[rank] += 1
        else:
            zero += 1
    for rank, size, nonzero in fibers.values():
        require(size == 1 << (2*n), "Projective Pauli fiber size")
        require(nonzero == 1 << rank, "Nonzero-trace Pauli fiber count")
    return {"projective_order": len(found), "symplectic_order": len(fibers),
            "overlaps": dict(sorted(histogram.items())), "zero_overlaps": zero,
            "displacement_ranks": dict(sorted(Counter(row[0] for row in fibers.values()).items()))}
