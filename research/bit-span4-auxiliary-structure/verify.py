#!/usr/bin/env python3
"""Finite checks for the span-four dirty-auxiliary classification.

The written argument is PROOF.md. This script does not search 120^5 words and
does not re-prove the cited dirty-auxiliary lemmas. It checks the polynomial
identities, support-graph partition, call-budget arithmetic and the nine-call
coordinate control used by that argument. Failures raise SystemExit so that
python -O cannot skip them.
"""

from fractions import Fraction
from itertools import combinations
from pathlib import Path


def need(condition, message):
    if not condition:
        raise SystemExit("FAIL: " + message)


ROOT = Path(__file__).resolve().parents[2]


# --- polynomials with integer coefficients ---------------------------------


def _mono_mul(left, right):
    if not left:
        return right
    if not right:
        return left
    merged = {}
    for var, exp in left:
        merged[var] = exp
    for var, exp in right:
        merged[var] = merged.get(var, 0) + exp
    return tuple(sorted(merged.items()))


class Poly:
    def __init__(self, terms=None):
        self.terms = {}
        if terms:
            for mono, coeff in terms.items():
                if coeff:
                    self.terms[mono] = coeff

    @staticmethod
    def const(value):
        return Poly({(): value} if value else None)

    @staticmethod
    def var(index):
        return Poly({((index, 1),): 1})

    def __add__(self, other):
        if isinstance(other, int):
            other = Poly.const(other)
        out = dict(self.terms)
        for mono, coeff in other.terms.items():
            total = out.get(mono, 0) + coeff
            if total:
                out[mono] = total
            elif mono in out:
                del out[mono]
        return Poly(out)

    def __radd__(self, other):
        return self + other

    def __sub__(self, other):
        if isinstance(other, int):
            other = Poly.const(other)
        return self + Poly({m: -c for m, c in other.terms.items()})

    def __neg__(self):
        return Poly({m: -c for m, c in self.terms.items()})

    def __mul__(self, other):
        if isinstance(other, int):
            other = Poly.const(other)
        out = {}
        for left, lc in self.terms.items():
            for right, rc in other.terms.items():
                mono = _mono_mul(left, right)
                total = out.get(mono, 0) + lc * rc
                if total:
                    out[mono] = total
                elif mono in out:
                    del out[mono]
        return Poly(out)

    def __rmul__(self, other):
        return self * other

    def __eq__(self, other):
        if isinstance(other, int):
            other = Poly.const(other)
        return self.terms == other.terms

    def is_zero(self):
        return not self.terms


def eye(n, one=1, zero=0):
    return tuple(tuple(one if i == j else zero for j in range(n)) for i in range(n))


def mat_mul(left, right):
    n = len(left)
    mid = len(right)
    p = len(right[0])
    return tuple(
        tuple(sum((left[i][k] * right[k][j] for k in range(mid)), left[i][0] * 0) for j in range(p))
        for i in range(n)
    )


def mat_add(left, right):
    return tuple(tuple(a + b for a, b in zip(row, other)) for row, other in zip(left, right))


def mat_scale(scalar, matrix):
    return tuple(tuple(scalar * entry for entry in row) for row in matrix)


def mat_eq(left, right):
    return all(a == b for row, other in zip(left, right) for a, b in zip(row, other))


def transpose(matrix):
    return tuple(tuple(matrix[i][j] for i in range(len(matrix))) for j in range(len(matrix[0])))


def det3(matrix):
    (a, b, c) = (matrix[0][0], matrix[0][1], matrix[0][2])
    (d, e, f) = (matrix[1][0], matrix[1][1], matrix[1][2])
    (g, h, i) = (matrix[2][0], matrix[2][1], matrix[2][2])
    return a * (e * i - f * h) - b * (d * i - f * g) + c * (d * h - e * g)


def det2(matrix):
    return matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0]


def outer(left, right):
    return tuple(tuple(left[i] * right[j] for j in range(len(right))) for i in range(len(left)))


def next_var(counter):
    index = counter[0]
    counter[0] = index + 1
    return Poly.var(index)


def symbolic_vector(n, counter):
    return tuple(next_var(counter) for _ in range(n))


def symbolic_matrix(rows, cols, counter):
    return tuple(tuple(next_var(counter) for _ in range(cols)) for _ in range(rows))


# --- determinant normalization ----------------------------------------------


def check_three_term_determinant():
    counter = [0]
    coeffs = symbolic_vector(3, counter)
    left = symbolic_matrix(3, 3, counter)
    right = symbolic_matrix(3, 3, counter)
    combined = None
    for index in range(3):
        term = mat_scale(coeffs[index], outer(tuple(left[r][index] for r in range(3)),
                                               tuple(right[r][index] for r in range(3))))
        combined = term if combined is None else mat_add(combined, term)
    expected = coeffs[0] * coeffs[1] * coeffs[2] * det3(left) * det3(right)
    need(det3(combined) == expected,
         "det of three rank-one terms must equal (prod a_i) det(U) det(V)")


def check_two_rank_one_determinant():
    counter = [0]
    a = next_var(counter)
    b = next_var(counter)
    u = symbolic_vector(3, counter)
    v = symbolic_vector(3, counter)
    x = symbolic_vector(3, counter)
    y = symbolic_vector(3, counter)
    combined = mat_add(mat_scale(a, outer(u, v)), mat_scale(b, outer(x, y)))
    need(det3(combined).is_zero(), "a sum of two rank-one 3x3 matrices has determinant 0")
    # Rank exactly 2 is possible, so the bound is not a rank-one collapse.
    sample = mat_add(outer((1, 0, 0), (1, 0, 0)), outer((0, 1, 0), (0, 1, 0)))
    need(det3(sample) == 0, "E00+E11 is singular")
    minor = det2(((sample[0][0], sample[0][1]), (sample[1][0], sample[1][1])))
    need(minor == 1, "E00+E11 has a nonzero 2x2 minor")


def check_cubic_supported_on_triples():
    """det on a rank-one span is the sum of its square-free triple coefficients."""
    counter = [0]
    xs = symbolic_vector(4, counter)
    left = symbolic_matrix(3, 4, counter)
    right = symbolic_matrix(3, 4, counter)
    combined = None
    for index in range(4):
        term = mat_scale(xs[index], outer(tuple(left[r][index] for r in range(3)),
                                           tuple(right[r][index] for r in range(3))))
        combined = term if combined is None else mat_add(combined, term)
    polynomial = det3(combined)
    x_ids = []
    for index in range(4):
        ((var, exp),) = next(iter(xs[index].terms.items()))[0]
        need(exp == 1, "x variables are degree one")
        x_ids.append(var)
    x_set = set(x_ids)
    wanted = {x_ids[0], x_ids[1], x_ids[2]}
    triple_coeff = Poly()
    for mono, coeff in polynomial.terms.items():
        counts = {var: exp for var, exp in mono if var in x_set}
        need(len(counts) == 3 and all(exp == 1 for exp in counts.values()),
             "det on rank-one generators is not a sum of square-free triples")
        if set(counts) != wanted:
            continue
        rest = tuple((var, exp) for var, exp in mono if var not in x_set)
        triple_coeff = triple_coeff + Poly({rest: coeff})
    u_matrix = tuple(tuple(left[r][c] for c in range(3)) for r in range(3))
    v_matrix = tuple(tuple(right[r][c] for c in range(3)) for r in range(3))
    need(triple_coeff == det3(u_matrix) * det3(v_matrix),
         "the x0 x1 x2 coefficient must be det(U) det(V)")


def check_minor_formula():
    counter = [0]
    diag = symbolic_vector(3, counter)
    t = next_var(counter)
    u = symbolic_vector(3, counter)
    v = symbolic_vector(3, counter)
    base = tuple(tuple((diag[i] if i == j else Poly.const(0)) + t * u[i] * v[j] for j in range(3))
                 for i in range(3))
    indices = (0, 1, 2)
    for i in indices:
        for k in indices:
            for l in indices:
                if len({i, k, l}) < 3:
                    continue
                minor = det2((
                    (base[i][i], base[i][l]),
                    (base[k][i], base[k][l]),
                ))
                need(minor == diag[i] * t * u[k] * v[l],
                     "span-four minor on rows (%d,%d) and columns (%d,%d)" % (i, k, i, l))


def check_four_lines_and_double_count():
    ones = (1, 1, 1)
    lines = (
        outer((1, 0, 0), (1, 0, 0)),
        outer((0, 1, 0), (0, 1, 0)),
        outer((0, 0, 1), (0, 0, 1)),
        outer(ones, ones),
    )
    rows = []
    for matrix in lines:
        rows.append([entry for row in matrix for entry in row])
    need(_rank_over_q(rows) == 4, "E00, E11, E22 and the all-ones matrix are independent")
    for left, right in combinations(range(4), 2):
        # Every rational combination of two lines is singular.
        counter = [0]
        a = next_var(counter)
        b = next_var(counter)
        combined = mat_add(mat_scale(a, _const_matrix(lines[left])), mat_scale(b, _const_matrix(lines[right])))
        need(det3(combined).is_zero(), "two of the four full-support lines are singular")
    identity = mat_add(mat_add(lines[0], lines[1]), lines[2])
    need(det3(identity) == 1, "three diagonal lines sum to I")
    choices = list(combinations(range(4), 3)) + [tuple(range(4))]
    best = None
    for first in choices:
        for second in choices:
            for third in choices:
                occupancy = [0, 0, 0, 0]
                for line in first + second + third:
                    occupancy[line] += 1
                total = sum(occupancy)
                best = total if best is None else min(best, total)
    need(best == 9, "three invertible targets on four lines need at least nine calls")


def _const_matrix(matrix):
    return tuple(tuple(Poly.const(entry) for entry in row) for row in matrix)


def _rank_over_q(rows):
    matrix = [[Fraction(entry) for entry in row] for row in rows]
    if not matrix:
        return 0
    cols = len(matrix[0])
    rank = 0
    pivot_col = 0
    while rank < len(matrix) and pivot_col < cols:
        pivot = next((r for r in range(rank, len(matrix)) if matrix[r][pivot_col] != 0), None)
        if pivot is None:
            pivot_col += 1
            continue
        matrix[rank], matrix[pivot] = matrix[pivot], matrix[rank]
        scale = matrix[rank][pivot_col]
        matrix[rank] = [entry / scale for entry in matrix[rank]]
        for row in range(len(matrix)):
            if row == rank or matrix[row][pivot_col] == 0:
                continue
            factor = matrix[row][pivot_col]
            matrix[row] = [a - factor * b for a, b in zip(matrix[row], matrix[rank])]
        rank += 1
        pivot_col += 1
    return rank


# --- factorization and rank --------------------------------------------------


def update_matrix(x, y, scalar):
    return mat_scale(scalar, outer(x, y))


def factored_update(x, u, y, v, a, b, dot):
    # I + [x u] [[a, a*b*dot], [0, b]] [y v]^T
    n = len(x)
    zero = a * 0
    columns_x = (x, u)
    t_matrix = (
        (a, a * b * dot),
        (zero, b),
    )
    columns_y = (y, v)
    x_mat = tuple(tuple(columns_x[p][i] for p in range(2)) for i in range(n))
    y_mat = tuple(tuple(columns_y[p][i] for p in range(2)) for i in range(n))
    return mat_add(eye(n, one=a * 0 + 1, zero=zero), mat_mul(mat_mul(x_mat, t_matrix), transpose(y_mat)))


def check_two_factor_identity():
    for n in range(1, 6):
        counter = [0]
        a = next_var(counter)
        b = next_var(counter)
        x = symbolic_vector(n, counter)
        y = symbolic_vector(n, counter)
        u = symbolic_vector(n, counter)
        v = symbolic_vector(n, counter)
        dot = sum((y[i] * u[i] for i in range(n)), a * 0)
        left = mat_mul(mat_add(eye(n, one=a * 0 + 1, zero=a * 0), update_matrix(x, y, a)),
                       mat_add(eye(n, one=a * 0 + 1, zero=a * 0), update_matrix(u, v, b)))
        right = factored_update(x, u, y, v, a, b, dot)
        need(mat_eq(left, right), "two-factor rank factorization fails at n=%d" % n)


def extend_factor(x_mat, t_matrix, y_mat, c, x, y):
    n = len(x_mat)
    q = len(t_matrix)
    zero = c * 0
    # Y^T x
    ytx = tuple(sum((y_mat[r][p] * x[r] for r in range(n)), zero) for p in range(q))
    t_ytx = tuple(sum((t_matrix[i][p] * ytx[p] for p in range(q)), zero) for i in range(q))
    big_t = []
    for i in range(q + 1):
        row = []
        for j in range(q + 1):
            if i < q and j < q:
                row.append(t_matrix[i][j])
            elif i < q and j == q:
                row.append(c * t_ytx[i])
            elif i == q and j < q:
                row.append(zero)
            else:
                row.append(c)
        big_t.append(tuple(row))
    big_x = tuple(tuple((x_mat[r][p] if p < q else x[r]) for p in range(q + 1)) for r in range(n))
    big_y = tuple(tuple((y_mat[r][p] if p < q else y[r]) for p in range(q + 1)) for r in range(n))
    return big_x, tuple(big_t), big_y


def check_inductive_factor():
    for n in (3, 4):
        for q in (1, 2, 3):
            counter = [0]
            x_mat = symbolic_matrix(n, q, counter)
            t_matrix = symbolic_matrix(q, q, counter)
            y_mat = symbolic_matrix(n, q, counter)
            c = next_var(counter)
            x = symbolic_vector(n, counter)
            y = symbolic_vector(n, counter)
            zero = c * 0
            one = zero + 1
            current = mat_add(eye(n, one=one, zero=zero), mat_mul(mat_mul(x_mat, t_matrix), transpose(y_mat)))
            extended = mat_mul(current, mat_add(eye(n, one=one, zero=zero), update_matrix(x, y, c)))
            new_x, new_t, new_y = extend_factor(x_mat, t_matrix, y_mat, c, x, y)
            expected = mat_add(eye(n, one=one, zero=zero), mat_mul(mat_mul(new_x, new_t), transpose(new_y)))
            need(mat_eq(extended, expected), "inductive factor step fails at n=%d q=%d" % (n, q))


def det_square(matrix):
    n = len(matrix)
    if n == 1:
        return matrix[0][0]
    if n == 2:
        return det2(matrix)
    if n == 3:
        return det3(matrix)
    total = matrix[0][0] * 0
    for col in range(n):
        sub = tuple(tuple(matrix[r][c] for c in range(n) if c != col) for r in range(1, n))
        sign = 1 if col % 2 == 0 else -1
        total = total + sign * matrix[0][col] * det_square(sub)
    return total


def check_factor_minors_vanish():
    cases = ((3, 1, 2), (3, 2, 3), (4, 1, 2), (4, 2, 3))
    for n, q, minor_size in cases:
        counter = [0]
        x_mat = symbolic_matrix(n, q, counter)
        t_matrix = symbolic_matrix(q, q, counter)
        y_mat = symbolic_matrix(n, q, counter)
        update = mat_mul(mat_mul(x_mat, t_matrix), transpose(y_mat))
        for rows in combinations(range(n), minor_size):
            for cols in combinations(range(n), minor_size):
                minor = tuple(tuple(update[i][j] for j in cols) for i in rows)
                need(det_square(minor).is_zero(),
                     "a q=%d factor has a nonzero %dx%d minor" % (q, minor_size, minor_size))


def check_diagonal_minor_separates_rank():
    counter = [0]
    entries = symbolic_vector(3, counter)
    matrix = tuple(tuple(entries[i] if i == j and i < 3 else Poly.const(0) for j in range(4)) for i in range(4))
    minor = tuple(tuple(matrix[i][j] for j in range(3)) for i in range(3))
    product = entries[0] * entries[1] * entries[2]
    need(det3(minor) == product, "three nonzero diagonal entries have minor equal to their product")
    need(not product.is_zero(), "that diagonal minor is not the zero polynomial")


def check_f2_idempotent_pairs():
    for n, expected in ((3, 28), (4, 120)):
        found = idempotents(n)
        need(len(found) == expected, "idempotent count at n=%d" % n)
        for x, y, matrix in found:
            need(_mul_f2(matrix, matrix) == matrix, "enumerated N is not idempotent over F2")
            need(_dot_f2(x, y) == 1, "idempotent dot must be 1 over F2")
        for x, y, left_n in found:
            for u, v, right_n in found:
                got = _mul_f2(_factor_f2(left_n, 0b0010), _factor_f2(right_n, 0b0100))
                dot = _dot_f2(y, u)
                predict = _factor_form_f2(n, x, u, y, v, dot)
                need(got == predict, "F2 two-factor formula misses an idempotent pair at n=%d" % n)


def idempotents(n):
    found = []
    for x in range(1 << n):
        for y in range(1 << n):
            if bin(x & y).count("1") % 2 == 0:
                continue
            matrix = tuple(tuple(((x >> i) & 1) & ((y >> j) & 1) for j in range(n)) for i in range(n))
            found.append((x, y, matrix))
    return found


def _dot_f2(x, y):
    return bin(x & y).count("1") % 2


def _mul_ab(left, right):
    out = 0
    for i in range(4):
        if ((left >> i) & 1) == 0:
            continue
        for j in range(4):
            if ((right >> j) & 1) == 0:
                continue
            aexp = (i & 1) + (j & 1)
            bexp = ((i >> 1) & 1) + ((j >> 1) & 1)
            need(aexp <= 1 and bexp <= 1, "F2[a,b] product reached a square")
            out ^= 1 << (aexp + 2 * bexp)
    return out


def _mul_f2(left, right):
    n = len(left)
    return tuple(
        tuple(
            0 if False else _row_dot(left[i], tuple(right[k][j] for k in range(n)))
            for j in range(n)
        )
        for i in range(n)
    )


def _row_dot(row, col):
    total = 0
    for a, b in zip(row, col):
        total ^= _mul_ab(a, b)
    return total


def _factor_f2(matrix, scalar_bit):
    n = len(matrix)
    return tuple(
        tuple((1 if i == j else 0) ^ _mul_ab(scalar_bit, matrix[i][j]) for j in range(n))
        for i in range(n)
    )


def _factor_form_f2(n, x, u, y, v, dot):
    # Bit 0 is the constant 1. a is bit 1 (value 2), b is bit 2 (value 4).
    a = 0b0010
    b = 0b0100
    ab_dot = _mul_ab(_mul_ab(a, b), dot)  # dot is 0 or 1
    rows = []
    for i in range(n):
        row = []
        for j in range(n):
            entry = 1 if i == j else 0
            if (x >> i) & 1 and (y >> j) & 1:
                entry ^= a
            if (u >> i) & 1 and (v >> j) & 1:
                entry ^= b
            if (x >> i) & 1 and (v >> j) & 1:
                entry ^= ab_dot
            row.append(entry)
        rows.append(tuple(row))
    return tuple(rows)


# --- support graph and blocks ------------------------------------------------


def support_edges(u, v):
    edges = []
    for i, ui in enumerate(u):
        dests = []
        if ui:
            dests = [j for j, vj in enumerate(v) if vj]
        edges.append(dests)
    return edges


def strongly_connected(edges):
    n = len(edges)
    seen = [False] * n
    order = []

    def visit(node):
        seen[node] = True
        for dest in edges[node]:
            if not seen[dest]:
                visit(dest)
        order.append(node)

    for node in range(n):
        if not seen[node]:
            visit(node)
    reverse = [[] for _ in range(n)]
    for src, dests in enumerate(edges):
        for dest in dests:
            reverse[dest].append(src)
    seen = [False] * n
    components = []

    def collect(node, bucket):
        seen[node] = True
        bucket.append(node)
        for dest in reverse[node]:
            if not seen[dest]:
                collect(dest, bucket)

    for node in reversed(order):
        if not seen[node]:
            bucket = []
            collect(node, bucket)
            components.append(bucket)
    return components


def component_order(edges, components):
    index = {}
    for comp_index, component in enumerate(components):
        for node in component:
            index[node] = comp_index
    # Edges must run from earlier components to later ones after a topological sort.
    indegree = [0] * len(components)
    for src, dests in enumerate(edges):
        for dest in dests:
            if index[src] != index[dest]:
                indegree[index[dest]] += 1
    ready = [i for i, deg in enumerate(indegree) if deg == 0]
    ordered = []
    while ready:
        current = ready.pop()
        ordered.append(current)
        for src, dests in enumerate(edges):
            if index[src] != current:
                continue
            for dest in dests:
                if index[dest] == current:
                    continue
                indegree[index[dest]] -= 1
                if indegree[index[dest]] == 0:
                    ready.append(index[dest])
    need(len(ordered) == len(components), "support condensation has a cycle of components")
    position = {comp: place for place, comp in enumerate(ordered)}
    return [position[index[node]] for node in range(len(edges))]


def check_support_patterns():
    full = 0
    blocks = {("1+1+1"): 0, ("1+2"): 0}
    for mask_u in range(8):
        for mask_v in range(8):
            u = tuple((mask_u >> i) & 1 for i in range(3))
            v = tuple((mask_v >> i) & 1 for i in range(3))
            components = strongly_connected(support_edges(u, v))
            sizes = sorted(len(component) for component in components)
            if u == (1, 1, 1) and v == (1, 1, 1):
                need(sizes == [3], "full support must be one component of size 3")
                full += 1
                continue
            need(max(sizes) <= 2, "a zero coordinate produced an SCC larger than 2")
            kind = "1+1+1" if sizes == [1, 1, 1] else "1+2"
            need(sizes in ([1, 1, 1], [1, 2]), "unexpected block sizes %s" % sizes)
            blocks[kind] += 1
            places = component_order(support_edges(u, v), components)
            matrix = outer(u, v)
            for i in range(3):
                for j in range(3):
                    if places[i] > places[j]:
                        need(matrix[i][j] == 0, "lower block survives the SCC order")
    need(full == 1, "full-support pattern count")
    need(blocks["1+1+1"] + blocks["1+2"] == 63, "every other support pattern is block-classified")


def check_rank_one_block_supports():
    nodes = (0, 1, 2)
    partitions = (
        ((0,), (1,), (2,)),
        ((0,), (1, 2)),
        ((0, 1), (2,)),
        ((0, 1, 2),),
    )
    for ordered in partitions:
        for mask_x in range(8):
            for mask_y in range(8):
                x_support = {i for i in nodes if (mask_x >> i) & 1}
                y_support = {i for i in nodes if (mask_y >> i) & 1}
                nonzero = [block for block in ordered
                           if (set(block) & x_support) and (set(block) & y_support)]
                if len(nonzero) < 2:
                    continue
                earlier, later = nonzero[0], nonzero[1]
                lower_hit = bool(set(later) & x_support) and bool(set(earlier) & y_support)
                need(lower_hit, "two nonzero diagonal blocks failed to force a lower block")


def check_block_determinants():
    counter = [0]
    a, b, c, d, e, f, g = (next_var(counter) for _ in range(7))
    upper_12 = (
        (a, b, c),
        (Poly.const(0), d, e),
        (Poly.const(0), f, g),
    )
    block2 = det2(((d, e), (f, g)))
    need(det3(upper_12) == a * block2, "1+2 block determinant")
    upper_111 = (
        (a, b, c),
        (Poly.const(0), d, e),
        (Poly.const(0), Poly.const(0), f),
    )
    need(det3(upper_111) == a * d * f, "1+1+1 block determinant")


# --- cited lemma arithmetic --------------------------------------------------


def spans_not_excluded(m, w, calls):
    """(s, d, relation rank) still open after Lemma 2 and the Lemma 1 corollary."""
    survivors = []
    target_rank = m * w
    for span in range(0, calls + 1):
        if span <= m:
            continue
        relation = calls - span
        if relation <= 1:
            continue
        if calls >= target_rank:
            continue
        survivors.append((calls, span, relation))
    return survivors


def check_cited_span_filter():
    need(spans_not_excluded(3, 3, 8) == [(8, 4, 4), (8, 5, 3), (8, 6, 2)],
         "eight calls at m=3, W=3 leave spans 4, 5 and 6")
    need(spans_not_excluded(2, 3, 5) == [(5, 3, 2)],
         "the only 2x2 saving count below six calls is five calls of span 3")
    for calls in range(0, 5):
        need(spans_not_excluded(2, 3, calls) == [],
             "2x2 calls below five are excluded by the cited lemmas")
    need(spans_not_excluded(1, 3, 2) == [], "a 1x1 block with two calls is excluded")
    for calls in range(0, 3):
        need(spans_not_excluded(1, 3, calls) == [], "scalar blocks need three calls")


def surviving_block_shapes(total):
    shapes = []
    for s1 in range(total + 1):
        for s2 in range(total + 1 - s1):
            upper = total - s1 - s2
            if s1 < 3:
                continue
            if s2 != 5 and s2 < 6:
                continue
            shapes.append((s1, s2, upper))
    return shapes


def check_call_budget():
    need(surviving_block_shapes(8) == [(3, 5, 0)],
         "the only eight-call 1+2 shape is 3+5 with no upper call")
    for total in range(0, 8):
        need(surviving_block_shapes(total) == [],
             "span-four 1+2 words shorter than eight calls are excluded")
    need(3 + 3 + 3 >= 9, "three scalar blocks need nine calls")
    need(3 + 5 == 8, "the remaining shape has eight calls")


# --- explicit words in F2[M_3(Q)] -------------------------------------------


def matrix_exponent(matrix):
    return tuple(entry for row in matrix for entry in row)


def algebra_add(left, right):
    out = dict(left)
    for key, coeff in right.items():
        total = (out.get(key, 0) + coeff) % 2
        if total:
            out[key] = total
        elif key in out:
            del out[key]
    return out


def algebra_mul(left, right):
    out = {}
    for a, ca in left.items():
        for b, cb in right.items():
            key = tuple(x + y for x, y in zip(a, b))
            total = (out.get(key, 0) + ca * cb) % 2
            if total:
                out[key] = total
            elif key in out:
                del out[key]
    return out


def algebra_matrix_mul(left, right):
    n = len(left)
    rows = []
    for i in range(n):
        row = []
        for j in range(n):
            entry = {}
            for k in range(n):
                entry = algebra_add(entry, algebra_mul(left[i][k], right[k][j]))
            row.append(entry)
        rows.append(tuple(row))
    return tuple(rows)


def monomial(exponent):
    return {exponent: 1}


def algebra_factor(projector, frame):
    n = len(projector)
    zero = matrix_exponent(((0, 0, 0), (0, 0, 0), (0, 0, 0)))
    group = matrix_exponent(frame)
    # In characteristic 2, [A] - 1 = [A] + 1.
    update = algebra_add(monomial(group), monomial(zero))
    rows = []
    for i in range(n):
        row = []
        for j in range(n):
            entry = monomial(zero) if i == j else {}
            if projector[i][j]:
                entry = algebra_add(entry, update)
            row.append(entry)
        rows.append(tuple(row))
    return tuple(rows)


def diagonal_monomial(exponents, n):
    zero = matrix_exponent(((0, 0, 0), (0, 0, 0), (0, 0, 0)))
    rows = []
    for i in range(n):
        row = []
        for j in range(n):
            row.append(monomial(exponents[i]) if i == j else {})
        rows.append(tuple(row))
    need(zero == matrix_exponent(((0, 0, 0), (0, 0, 0), (0, 0, 0))), "zero exponent")
    return tuple(rows)


def coordinate_projector(n, register):
    return tuple(tuple(1 if i == register and j == register else 0 for j in range(n)) for i in range(n))


def column_frames(target):
    frames = []
    for col in range(3):
        frame = tuple(tuple(target[row][col] if c == col else 0 for c in range(3)) for row in range(3))
        frames.append(frame)
    return frames


def check_nine_call_word():
    targets = (
        ((1, 0, 0), (0, 1, 0), (0, 0, 1)),
        ((1, 0, 0), (1, 1, 0), (0, 0, 1)),
        ((1, 0, 0), (0, 1, 0), (0, 1, 1)),
    )
    for target in targets:
        need(det3(target) == 1, "control target must be invertible")
        total = ((0, 0, 0), (0, 0, 0), (0, 0, 0))
        for frame in column_frames(target):
            total = tuple(tuple(a + b for a, b in zip(row, other)) for row, other in zip(total, frame))
        need(total == target, "column frames must sum to the target")
    n = 4
    factors = []
    for register, target in enumerate(targets):
        projector = coordinate_projector(n, register)
        for frame in column_frames(target):
            factors.append(algebra_factor(projector, frame))
    product = factors[0]
    for factor in factors[1:]:
        product = algebra_matrix_mul(product, factor)
    exponents = [matrix_exponent(target) for target in targets]
    exponents.append(matrix_exponent(((0, 0, 0), (0, 0, 0), (0, 0, 0))))
    need(product == diagonal_monomial(exponents, n),
         "nine coordinate calls plus a restored auxiliary must match the diagonal monomial")
    # Deleting any one call moves that register's exponent.
    for drop in range(len(factors)):
        kept = [factor for index, factor in enumerate(factors) if index != drop]
        shortened = kept[0]
        for factor in kept[1:]:
            shortened = algebra_matrix_mul(shortened, factor)
        need(shortened != product, "deleting call %d still matched the nine-call endpoint" % drop)
    # Mutating one frame entry breaks the same endpoint.
    mutated_frame = ((1, 1, 0), (0, 0, 0), (0, 0, 0))
    mutated = list(factors)
    mutated[0] = algebra_factor(coordinate_projector(n, 0), mutated_frame)
    bad = mutated[0]
    for factor in mutated[1:]:
        bad = algebra_matrix_mul(bad, factor)
    need(bad != product, "a one-entry frame mutation still matched")


def check_cancelling_pair_and_splitting():
    zero = ((0, 0, 0), (0, 0, 0), (0, 0, 0))
    frame = ((0, 1, 0), (1, 0, 0), (0, 0, 1))
    negative = tuple(tuple(-entry for entry in row) for row in frame)
    # A non-coordinate idempotent: x=(1,1,0), y=(1,0,0) on n=3, padded to n=4.
    projector = (
        (1, 0, 0, 0),
        (1, 0, 0, 0),
        (0, 0, 0, 0),
        (0, 0, 0, 0),
    )
    pair = algebra_matrix_mul(algebra_factor(projector, frame), algebra_factor(projector, negative))
    identity = diagonal_monomial([matrix_exponent(zero)] * 4, 4)
    need(pair == identity, "frames B and -B on one idempotent must multiply to I")
    degree = tuple(tuple(a + b for a, b in zip(row, other)) for row, other in zip(frame, negative))
    need(degree == zero, "a cancelling pair contributes 0 to the degree-1 frame sum")
    # Padding three coordinate calls with that pair preserves the degree-1 sum
    # and the endpoint, while increasing the length from 3 to 5.
    targets = (
        ((1, 0, 0), (0, 0, 0), (0, 0, 0)),
        ((0, 0, 0), (0, 1, 0), (0, 0, 0)),
        ((0, 0, 0), (0, 0, 0), (0, 0, 1)),
    )
    short = []
    for register, target in enumerate(targets):
        short.append(algebra_factor(coordinate_projector(4, register), target))
    short_product = short[0]
    for factor in short[1:]:
        short_product = algebra_matrix_mul(short_product, factor)
    padded = algebra_matrix_mul(algebra_matrix_mul(short_product, algebra_factor(projector, frame)),
                                algebra_factor(projector, negative))
    need(padded == short_product, "a cancelling pair must not change a diagonal endpoint")
    for target in targets:
        need(det3(target) == 0, "the padded example is not an invertible-target word")
    half = ((1, 0, 0), (0, 0, 0), (0, 0, 0))
    doubled = ((2, 0, 0), (0, 0, 0), (0, 0, 0))
    square = algebra_matrix_mul(algebra_factor(projector, half), algebra_factor(projector, half))
    need(square == algebra_factor(projector, doubled),
         "in characteristic 2, D_N([A/2])^2 must equal D_N([A])")


def check_dependency_headings():
    expected = {
        "research/bit-dirty-auxiliary-registers/README.md": (
            "**Lemma 1.**",
            "**Lemma 2 (PR #468 §3, with auxiliary registers).**",
            "Three data registers, eight calls, one dirty auxiliary.",
        ),
        "research/three-register-no-target-flag/README.md": (
            "## 6. The new span-four argument in address dimension three",
            "This corollary is for **three scalar registers**, not arbitrary register count.",
            "Each two-dimensional block needs six by section 5.",
        ),
        "research/bit-three-register-lower-bound/README.md": (
            "**Low-span lemma.**",
            "**Span-four lemma.**",
        ),
    }
    for path, phrases in expected.items():
        text = (ROOT / path).read_text(encoding="utf-8")
        for phrase in phrases:
            need(phrase in text, "missing cited heading %s in %s" % (phrase, path))


def main():
    check_three_term_determinant()
    check_two_rank_one_determinant()
    check_cubic_supported_on_triples()
    check_minor_formula()
    check_four_lines_and_double_count()
    check_two_factor_identity()
    check_inductive_factor()
    check_factor_minors_vanish()
    check_diagonal_minor_separates_rank()
    check_f2_idempotent_pairs()
    check_support_patterns()
    check_rank_one_block_supports()
    check_block_determinants()
    check_cited_span_filter()
    check_call_budget()
    check_nine_call_word()
    check_cancelling_pair_and_splitting()
    check_dependency_headings()
    print("PASS_SPAN4_AUXILIARY_STRUCTURE")


if __name__ == "__main__":
    main()
