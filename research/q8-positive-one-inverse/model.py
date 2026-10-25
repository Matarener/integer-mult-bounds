"""Exact positive-label Q8 calls. Nick Petalas. Apache-2.0."""

from itertools import product

# Codes are (axis << 1) | sign, axes 1,i,j,k. The sign is the group z.
AXES = ((0, 2, 4, 6), (2, 1, 6, 5), (4, 7, 1, 2), (6, 4, 3, 1))


def group_mul(a, b):
    return AXES[a >> 1][b >> 1] ^ (a & 1) ^ (b & 1)


def shift(mask, g):
    answer = 0
    for h in range(8):
        if mask >> h & 1:
            answer ^= 1 << group_mul(h, g)
    return answer


SHIFTS = tuple(tuple(shift(mask, g) for mask in range(256)) for g in range(8))


def require(condition, message):
    if not condition:
        raise ValueError(message)


def validate_call(call, roles):
    g, u, v = call
    require(1 <= roles <= 8, "roles outside 1..8 replay bound")
    require(g in (2, 4), "only positive i,j calls are paid")
    require(0 < u < 1 << roles and 0 < v < 1 << roles, "bad role vector")
    require((u & v).bit_count() % 2 == 1, "call must be idempotent")


def identity(roles):
    return tuple(int(a == b) for a in range(roles) for b in range(roles))


def endpoint(targets):
    return tuple(
        1 << g if a == b else 0
        for a, g in enumerate(targets)
        for b in range(len(targets))
    )


def step(matrix, call, roles):
    """Right multiplication, preserving the full noncommuting group order."""
    g, u, v = call
    answer = list(matrix)
    for a in range(roles):
        column = 0
        for b in range(roles):
            if u >> b & 1:
                column ^= matrix[a * roles + b]
        delta = SHIFTS[g][column] ^ column
        for b in range(roles):
            if v >> b & 1:
                answer[a * roles + b] ^= delta
    return tuple(answer)


def evaluate(word, roles):
    require(1 <= roles <= 8 and len(word) <= 64, "word exceeds replay bound")
    matrix = identity(roles)
    for call in word:
        validate_call(call, roles)
        matrix = step(matrix, call, roles)
    return matrix


def alphabet(roles):
    require(1 <= roles <= 3, "exhaustive alphabet bound is three roles")
    return tuple(
        (g, u, v)
        for g in (2, 4)
        for u in range(1, 1 << roles)
        for v in range(1, 1 << roles)
        if (u & v).bit_count() % 2
    )


def tariff(targets, alpha, beta):
    require(1 <= len(targets) <= 8, "target replay bound is eight roles")
    require(all(g in (0, 2, 3, 4, 5) for g in targets), "target outside theorem")
    negative = sum(g in (3, 5) for g in targets)
    require(negative <= 1, "exact tariff requires at most one inverse target")
    require(alpha >= 0 and beta >= 0, "prices must be nonnegative")
    return (
        alpha * sum(g in (2, 3) for g in targets)
        + beta * sum(g in (4, 5) for g in targets)
        + 2 * negative * min(alpha, beta)
    )


def construction(targets, alpha, beta):
    tariff(targets, alpha, beta)
    cheaper = 2 if alpha <= beta else 4
    word = []
    for a, g in enumerate(targets):
        if g:
            word.append((g & ~1, 1 << a, 1 << a))
            if g & 1:
                word.extend([(cheaper, 1 << a, 1 << a)] * 2)
    return tuple(word)


def diagonal_targets(matrix, roles):
    targets = []
    for a in range(roles):
        for b in range(roles):
            if a != b and matrix[a * roles + b]:
                return None
        value = matrix[a * roles + a]
        if value == 0 or value & (value - 1):
            return None
        targets.append(value.bit_length() - 1)
    return tuple(targets)


def exhaustive_saturation():
    """Every positive word of length <=3 at one, two and three roles."""
    counts = []
    for roles in range(1, 4):
        factors = alphabet(roles)
        checked = saturating = 0
        for length in range(4):
            for word in product(factors, repeat=length):
                matrix = evaluate(word, roles)
                targets = diagonal_targets(matrix, roles)
                checked += 1
                if targets is None or any(g not in (0, 2, 3, 4, 5) for g in targets):
                    continue
                active = sum(g != 0 for g in targets)
                require(length >= active, "support floor failed")
                require((length - active) % 2 == 0, "trace parity failed")
                if length == active:
                    require(all(g not in (3, 5) for g in targets), "signed saturation")
                    # The equality argument forces every paired v_l.u_m=delta_lm.
                    require(
                        all(
                            ((x[2] & y[1]).bit_count() % 2) == (a == b)
                            for a, x in enumerate(word)
                            for b, y in enumerate(word)
                        ),
                        "equality pairing failed",
                    )
                    saturating += 1
        counts.append(
            {
                "roles": roles,
                "factors": len(factors),
                "words": checked,
                "saturating_words": saturating,
            }
        )
    return counts
