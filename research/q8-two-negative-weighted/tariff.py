"""Exact positive-Q8 class-count fronts in three explicitly bounded families."""

from fractions import Fraction


def require(condition, message):
    if not condition:
        raise ValueError(message)


def parameters(target):
    require(type(target) is tuple and 2 <= len(target) <= 12, "target role limit")
    require(
        all(type(g) is int and g in (0, 2, 3, 4, 5) for g in target),
        "target label",
    )
    negative = sum(g in (3, 5) for g in target)
    si = sum(g in (2, 3) for g in target)
    sj = sum(g in (4, 5) for g in target)
    universal = negative == 2 and si + sj in (2, 3)
    finite = negative == 3 and len(target) == 3
    require(universal or finite, "outside proved family")
    return si, sj, negative


def prices(alpha, beta):
    for value in (alpha, beta):
        require(
            type(value) in (int, Fraction) and value >= 0, "nonnegative rational price"
        )
    return Fraction(alpha), Fraction(beta)


def frontier(target):
    si, sj, negative = parameters(target)
    return tuple((si + 2 * a, sj + 2 * (negative - a)) for a in range(negative + 1))


def minimum(target, alpha, beta):
    alpha, beta = prices(alpha, beta)
    si, sj, negative = parameters(target)
    return alpha * si + beta * sj + 2 * negative * min(alpha, beta)


def witness(target, i_corrections):
    _, _, negative = parameters(target)
    require(
        type(i_corrections) is int and 0 <= i_corrections <= negative,
        "correction count",
    )
    word = []
    used = 0
    for role, g in enumerate(target):
        axis = 1 << role
        if g in (3, 5):
            cheap = 2 if used < i_corrections else 4
            word.extend(((axis, axis, cheap),) * 2)
            used += 1
        if g:
            word.append((axis, axis, 2 if g in (2, 3) else 4))
    require(used == negative and len(word) <= 9, "witness size invariant")
    return tuple(word)


def optimal_word(target, alpha, beta):
    alpha, beta = prices(alpha, beta)
    negative = parameters(target)[2]
    return witness(target, negative if alpha <= beta else 0)


def counts(word):
    require(type(word) is tuple and len(word) <= 48, "call limit")
    for call in word:
        require(type(call) is tuple and len(call) == 3, "call shape")
        u, v, g = call
        require(all(type(x) is int for x in call), "call type")
        require(0 < u < 4096 and 0 < v < 4096, "call vector limit")
        require(g in (2, 4) and (u & v).bit_count() % 2 == 1, "paid idempotent")
    return sum(g == 2 for _, _, g in word), sum(g == 4 for _, _, g in word)


def dominated(target, count_pair):
    require(type(count_pair) is tuple and len(count_pair) == 2, "count pair")
    require(
        all(type(x) is int and 0 <= x <= 48 for x in count_pair),
        "count boundary",
    )
    si, sj, negative = parameters(target)
    ni, nj = count_pair
    require(ni >= si and nj >= sj, "label rank floor")
    require((ni - si) % 2 == (nj - sj) % 2 == 0, "label trace parity")
    require(ni + nj >= si + sj + 2 * negative, "retained unit minimum")
    candidates = [p for p in frontier(target) if p[0] <= ni and p[1] <= nj]
    require(bool(candidates), "frontier domination invariant")
    return candidates[0]
