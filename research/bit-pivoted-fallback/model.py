"""Paid pivoting for a split-projector partial interchange. Apache-2.0."""

from dataclasses import dataclass
from math import gcd


def require(condition, message):
    if not condition:
        raise ValueError(message)


def eye(n):
    return [[int(i == j) for j in range(n)] for i in range(n)]


def mul(a, b, modulus):
    return [[sum(x * y for x, y in zip(row, col)) % modulus
             for col in zip(*b)] for row in a]


def inverse(a, modulus):
    n = len(a)
    rows = [list(row) + unit for row, unit in zip(a, eye(n))]
    for k in range(n):
        candidates = [i for i in range(k, n) if gcd(rows[i][k], modulus) == 1]
        require(candidates, "matrix has no unit pivot")
        i = candidates[0]
        rows[k], rows[i] = rows[i], rows[k]
        scale = pow(rows[k][k], -1, modulus)
        rows[k] = [x * scale % modulus for x in rows[k]]
        for i in range(n):
            if i != k:
                c = rows[i][k]
                rows[i] = [(x - c * y) % modulus
                           for x, y in zip(rows[i], rows[k])]
    require([row[:n] for row in rows] == eye(n), "inverse endpoint")
    return [row[n:] for row in rows]


@dataclass(frozen=True)
class Op:
    kind: str
    target: int
    source: int
    value: int = 1


def row_op(a, op, modulus):
    i, k = op.target, op.source
    if op.kind == "swap":
        a[i], a[k] = a[k], a[i]
    else:
        require(op.kind == "add", "row operation kind")
        a[i] = [(x + op.value * y) % modulus for x, y in zip(a[i], a[k])]


def column_op(a, op, modulus):
    i, k = op.target, op.source
    for row in a:
        if op.kind == "swap":
            row[i], row[k] = row[k], row[i]
        else:
            row[i] = (row[i] + op.value * row[k]) % modulus


def eliminate(p, rank, modulus):
    m = len(p)
    a, left, right = [row[::-1] for row in p], eye(m), eye(m)
    heads, tails, pivots = [], [], []
    for k in range(rank):
        last = m - 1 - k
        candidates = [(i, j) for i in range(k, m) for j in range(last + 1)
                      if gcd(a[i][j], modulus) == 1]
        require(candidates, "split rank requires another unit pivot")
        i, j = candidates[0]
        if i != k:
            op = Op("swap", k, i)
            row_op(a, op, modulus)
            row_op(left, op, modulus)
            heads.append(op)
        if j != last:
            op = Op("swap", last, j)
            column_op(a, op, modulus)
            column_op(right, op, modulus)
            tails.append(op)
        pivot = a[k][last]
        pivots.append(pivot)
        inv = pow(pivot, -1, modulus)
        for i in range(k + 1, m):
            op = Op("add", i, k, -a[i][last] * inv % modulus)
            row_op(a, op, modulus)
            row_op(left, op, modulus)
            heads.append(op)
        for j in range(last):
            op = Op("add", j, last, -a[k][j] * inv % modulus)
            column_op(a, op, modulus)
            column_op(right, op, modulus)
            tails.append(op)
    target = [[0] * m for _ in range(m)]
    for k, pivot in enumerate(pivots):
        target[k][m - 1 - k] = pivot
    require(a == target, "full-ring rank remainder is zero")
    return left, right, tuple(pivots), heads, tails


@dataclass(frozen=True)
class Plan:
    m: int
    rank: int
    modulus: int
    pivots: tuple
    adapter: tuple
    pivot_swaps: int


def compile_plan(p, rank, modulus):
    m = len(p)
    require(2 <= m <= 64 and 1 <= rank < m, "dimension/rank domain")
    require(isinstance(modulus, int) and 3 <= modulus
            and modulus.bit_length() <= 4096 and modulus % 2, "odd modulus domain")
    require(all(len(row) == m for row in p), "square projector")
    require(all(isinstance(x, int) and 0 <= x < modulus for row in p for x in row),
            "canonical residue entries")
    require(mul(p, p, modulus) == p, "idempotent input")
    left, right, pivots, heads, tails = eliminate(p, rank, modulus)
    li, ri = inverse(left, modulus), inverse(right, modulus)
    u = mul(mul(left, p, modulus), li, modulus)
    s = mul(ri, li[::-1], modulus)
    j = [[0] * m for _ in range(m)]
    for k, pivot in enumerate(pivots):
        j[m - 1 - k][k] = pow(pivot, -1, modulus)
    ju = mul(j, u, modulus)
    cross = [[((s[i][k] if k < rank else 0) - ju[i][k]) % modulus
              for k in range(m)] for i in range(m)]
    adapter = list(heads)
    for op in tails:
        if op.kind == "swap":
            adapter.append(Op("swap", m + op.target, m + op.source))
        else:
            adapter.append(Op("add", m + op.source, m + op.target,
                              -op.value % modulus))
    adapter.extend(Op("add", m + i, k, cross[i][k])
                   for i in range(m) for k in range(m))
    require(all(op.target > op.source for op in adapter if op.kind == "add"),
            "every adapter addition has a later target")
    swaps = sum(op.kind == "swap" for op in adapter)
    require(swaps <= 2 * rank, "at most two pivot swaps per stage")
    row_slots = rank * (m - 1) - rank * (rank - 1) // 2
    require(sum(op.kind == "add" for op in adapter) == 2 * row_slots + m * m,
            "all row, column and cross ADD slots retained")
    return Plan(m, rank, modulus, pivots, tuple(adapter), swaps)


def reversed_child(data, start, end, width, weights, modulus):
    require(width >= 1 and start + width <= end and end + width <= len(data),
            "disjoint ordered child fields")
    require(len(weights) == width and all(gcd(x, modulus) == 1 for x in weights),
            "child weight units")
    for j in range(width):
        i, k, unit = start + j, end + width - 1 - j, weights[j]
        data[i], data[k] = (unit * data[k] % modulus,
                            pow(unit, -1, modulus) * data[i] % modulus)


def reverse_field(data, start, width, modulus, trace):
    half = width // 2
    if half:
        reversed_child(data, start, start + width - half, half,
                       [1] * half, modulus)
        trace.append(half)


def physical_swap(data, first, second, weights, modulus, trace):
    """Two ascending f-atom fields, with matching-index weights."""
    f = len(weights)
    if first > second:
        first, second = second, first
        weights = [pow(x, -1, modulus) for x in weights]
    reverse_field(data, second, f, modulus, trace)
    reversed_child(data, first, second, f, weights, modulus)
    trace.append(f)
    reverse_field(data, second, f, modulus, trace)


def position(role, column, m, f):
    return role * f + column if role < m else role * f + f - 1 - column


def apply_adapter(data, plan, f, weights, trace, undo=False, omit_swaps=False):
    m, modulus = plan.m, plan.modulus
    ops = tuple(reversed(plan.adapter)) if undo else plan.adapter
    units = list(weights) + [1] * (m * f)
    for op in ops:
        if op.kind == "swap":
            if omit_swaps:
                continue
            first, second = op.target * f, op.source * f
            ratios = [units[first + j] * pow(units[second + j], -1, modulus)
                      % modulus for j in range(f)]
            physical_swap(data, first, second, ratios, modulus, trace)
        else:
            for j in range(f):
                i, k = position(op.target, j, m, f), position(op.source, j, m, f)
                coefficient = op.value * units[i] * pow(units[k], -1, modulus)
                sign = -1 if undo else 1
                data[i] = (data[i] + sign * coefficient * data[k]) % modulus


def execute(plan, data, f, weights, omit_swaps=False, omit_return=False):
    require(1 <= f <= 8, "checker fiber bound")
    require(len(data) == 2 * plan.m * f and len(weights) == plan.m * f,
            "physical data and weight extent")
    require(all(isinstance(x, int) and 0 <= x < plan.modulus for x in data),
            "canonical data residues")
    require(all(isinstance(x, int) and 0 < x < plan.modulus for x in weights),
            "canonical weight residues")
    require(all(gcd(x, plan.modulus) == 1 for x in weights), "ancestor weight units")
    out, trace = list(data), []
    apply_adapter(out, plan, f, weights, trace, omit_swaps=omit_swaps)
    child_weights = [weights[k * f + j] * pivot % plan.modulus
                     for k, pivot in enumerate(plan.pivots) for j in range(f)]
    reversed_child(out, 0, (2 * plan.m - plan.rank) * f,
                   plan.rank * f, child_weights, plan.modulus)
    if not omit_return:
        apply_adapter(out, plan, f, weights, trace, undo=True, omit_swaps=omit_swaps)
    require(len(trace) <= 12 * plan.rank, "charged pivot-child bound")
    require(all(width <= f for width in trace), "pivot-child width bound")
    return out, tuple(trace)
