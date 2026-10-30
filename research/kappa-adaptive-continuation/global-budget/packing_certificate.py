#!/usr/bin/env python3
"""Small exact pattern-dual tools, independent of the floating point search.

The weak-duality argument follows the credited staged544-clock-ceiling work
of Erwan Secousses / ChaloupeMusic (PR3815). This implementation uses the
separately retained outward-rational invoice engine and validates every bin
pattern, so a proposed basis is only a nomination, never a trusted optimum.
Apache-2.0; substantial OpenAI Codex assistance under the user's direction.
"""
from fractions import Fraction as F


WIDTHS = (4, 5, 6, 7, 8, 9)


def patterns(capacity):
    """Every nonnegative integer width tuple fitting the bin, including empty."""
    def visit(index, remaining, prefix):
        if index == len(WIDTHS):
            yield tuple(prefix), remaining
            return
        width = WIDTHS[index]
        for count in range(remaining // width + 1):
            yield from visit(index + 1, remaining - count*width, prefix + [count])
    yield from visit(0, capacity, [])


def solve(matrix, rhs):
    n = len(rhs)
    assert len(matrix) == n and all(len(row) == n for row in matrix)
    a = [[F(value) for value in row] + [F(value)]
         for row, value in zip(matrix, rhs)]
    for col in range(n):
        pivot = next(row for row in range(col, n) if a[row][col])
        a[col], a[pivot] = a[pivot], a[col]
        scale = a[col][col]
        a[col] = [value/scale for value in a[col]]
        for row in range(n):
            if row == col or not a[row][col]:
                continue
            scale = a[row][col]
            a[row] = [x-scale*y for x, y in zip(a[row], a[col])]
    solution = [row[-1] for row in a]
    assert all(sum(F(x)*y for x, y in zip(row, solution)) == F(value)
               for row, value in zip(matrix, rhs))
    return solution


def certify(I, *, dimension, productive, calls, local, bins, supply, basis, endpoint,
            perturb_width9=F(0)):
    """Certify a lower bound on the paid invoice minus its productive count.

For each bin c and pattern p, pi*p+mu[c] <= lower(cost(remainder)).
Thus any fill using these bin/helper counts has invoice >= local+dual.
No time, integrality or single-call uniqueness restrictions are needed.
    """
    caps = tuple(sorted(bins))
    cost = {0: F(0)}
    cost.update({r: I.cost(r, dimension, endpoint)[0]
                 for r in range(1, max(caps)+1)})
    matrix, rhs = [], []
    for cap, pattern in basis:
        rem = cap-sum(w*n for w, n in zip(WIDTHS, pattern))
        I.need(cap in bins and rem >= 0, 'nominated dual basis is a bin pattern')
        matrix.append(list(pattern)+[int(c == cap) for c in caps])
        rhs.append(cost[rem])
    dual = solve(matrix, rhs)
    dual[5] += perturb_width9
    pi = dual[:6]
    mu = dict(zip(caps, dual[6:]))
    smallest, worst, count = None, None, 0
    for cap in caps:
        for pattern, rem in patterns(cap):
            reduced = cost[rem]-mu[cap]-sum(x*n for x, n in zip(pi, pattern))
            count += 1
            if smallest is None or reduced < smallest:
                smallest, worst = reduced, (cap, pattern, rem)
    idle_lower = sum(mu[c]*bins[c] for c in caps) + sum(
        x*calls*supply[w] for w, x in zip(WIDTHS, pi))
    local_lower = I.weighted({r: calls*n for r, n in local.items()}, dimension, endpoint)[0]
    bound = local_lower+idle_lower-productive
    return {
        'endpoint': str(endpoint), 'patterns_checked': count,
        'dual_feasible': smallest >= 0,
        'minimum_reduced_cost': str(smallest), 'worst_pattern': worst,
        'width_dual': {str(w): str(x) for w, x in zip(WIDTHS, pi)},
        'bin_dual': {str(c): str(x) for c, x in mu.items()},
        'paid_invoice_minus_productive_lower_bound': str(bound),
        'lower_bound_decimal': I.decimal(bound),
        'strictly_excludes_endpoint': smallest >= 0 and bound > 0,
    }
