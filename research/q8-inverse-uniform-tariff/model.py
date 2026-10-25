"""Exact Q8 coefficients and the support/parity tariff certificate."""

from itertools import product

LABELS = (2, 3, 4, 5)
MAX_ROLES = 8
MAX_CALLS = 48
UNIT = (
    ((0, 0), (0, 1), (0, 2), (0, 3)),
    ((0, 1), (1, 0), (0, 3), (1, 2)),
    ((0, 2), (1, 3), (1, 0), (0, 1)),
    ((0, 3), (0, 2), (1, 1), (1, 0)),
)
Call = tuple[int, int, int]
Matrix = tuple[tuple[int, ...], ...]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def group(a: int, b: int) -> int:
    sign, axis = UNIT[a // 2][b // 2]
    return 2 * axis + (sign ^ (a & 1) ^ (b & 1))


def rank(vectors: list[int] | tuple[int, ...]) -> int:
    basis = [0] * MAX_ROLES
    for original in vectors:
        value = original
        for pivot in range(MAX_ROLES - 1, -1, -1):
            if value & (1 << pivot):
                if basis[pivot]:
                    value ^= basis[pivot]
                else:
                    basis[pivot] = value
                    break
    return sum(bool(value) for value in basis)


def identity(roles: int) -> Matrix:
    return tuple(tuple(int(i == j) for j in range(roles)) for i in range(roles))


def target(elements: tuple[int, ...]) -> Matrix:
    return tuple(
        tuple((1 << element) if i == j else 0 for j in range(len(elements)))
        for i, element in enumerate(elements)
    )


def step(state: Matrix, call: Call) -> Matrix:
    label, u, v = call
    rows = [list(row) for row in state]
    for i, row in enumerate(state):
        aggregate = 0
        for j, entry in enumerate(row):
            if u & (1 << j):
                aggregate ^= entry
        change = aggregate
        for element in range(8):
            if aggregate & (1 << element):
                change ^= 1 << group(element, label)
        for j in range(len(state)):
            if v & (1 << j):
                rows[i][j] ^= change
    return tuple(tuple(row) for row in rows)


def validate_word(roles: int, word: tuple[Call, ...]) -> None:
    require(type(roles) is int and 1 <= roles <= MAX_ROLES, "invalid roles")
    require(len(word) <= MAX_CALLS, "too many calls")
    for call in word:
        require(len(call) == 3, "invalid call shape")
        label, u, v = call
        require(all(type(item) is int for item in call), "integer calls required")
        require(label in LABELS, "unpriced address label")
        require(0 < u < (1 << roles) and 0 < v < (1 << roles), "invalid coupling")


def endpoint(roles: int, word: tuple[Call, ...]) -> Matrix:
    validate_word(roles, word)
    state = identity(roles)
    for call in word:
        state = step(state, call)
    return state


def coefficient(state: Matrix, selector: int) -> tuple[int, ...]:
    return tuple(
        sum(((entry & selector).bit_count() & 1) << j for j, entry in enumerate(row))
        for row in state
    )


def projector_sum(
    roles: int, word: tuple[Call, ...], labels: tuple[int, ...]
) -> tuple[int, ...]:
    rows = [0] * roles
    for label, u, v in word:
        if label in labels:
            for i in range(roles):
                if u & (1 << i):
                    rows[i] ^= v
    return tuple(rows)


def check_invariants(state: Matrix, word: tuple[Call, ...]) -> None:
    roles = len(state)
    for labels, selector in (((2, 3), 204), ((4, 5), 240), (LABELS, 60)):
        expected = projector_sum(roles, word, labels)
        require(coefficient(state, selector) == expected, "first-order quotient")
    require(
        coefficient(state, 255) == coefficient(identity(roles), 255), "augmentation"
    )
    u_vectors = [u for _, u, _ in word]
    v_vectors = [v for _, _, v in word]
    combined = projector_sum(roles, word, LABELS)
    require(
        rank(u_vectors) + rank(v_vectors) <= len(word) + rank(combined), "Sylvester"
    )
    difference = tuple(
        tuple(entry ^ int(i == j) for j, entry in enumerate(row))
        for i, row in enumerate(state)
    )
    for element in range(8):
        rows = coefficient(difference, 1 << element)
        columns = [
            sum(((row >> j) & 1) << i for i, row in enumerate(rows))
            for j in range(roles)
        ]
        require(rank(u_vectors + columns) == rank(u_vectors), "image support")
        require(rank(v_vectors + list(rows)) == rank(v_vectors), "row support")


def counts(elements: tuple[int, ...]) -> tuple[int, int, int, int]:
    return tuple(
        sum(element in block for element in elements)
        for block in ((2, 3), (4, 5), (6, 7), (1,))
    )


def tariff(elements: tuple[int, ...], alpha: int, beta: int) -> int:
    require(
        type(alpha) is int and type(beta) is int and min(alpha, beta) >= 0,
        "invalid prices",
    )
    si, sj, sk, central = counts(elements)
    return alpha * (si + sk) + beta * (sj + sk) + 2 * central * min(alpha, beta)


def witness(elements: tuple[int, ...], alpha: int, beta: int) -> tuple[Call, ...]:
    cheap = 2 if alpha <= beta else 4
    recipes = ((), (cheap, cheap), (2,), (3,), (4,), (5,), (2, 4), (4, 2))
    return tuple(
        (label, 1 << role, 1 << role)
        for role, element in enumerate(elements)
        for label in recipes[element]
    )


def check_target(
    elements: tuple[int, ...], word: tuple[Call, ...], alpha: int, beta: int
) -> None:
    state = endpoint(len(elements), word)
    require(state == target(elements), "full dirty endpoint")
    check_invariants(state, word)
    si, sj, sk, central = counts(elements)
    active = si + sj + sk + central
    require(rank([u for _, u, _ in word]) >= active, "active image rank")
    require(rank([v for _, _, v in word]) >= active, "active row rank")
    require(
        rank(projector_sum(len(elements), word, LABELS)) == si + sj,
        "combined endpoint parity rank",
    )
    ni = sum(label in (2, 3) for label, _, _ in word)
    nj = len(word) - ni
    require(ni >= si + sk and nj >= sj + sk, "separate label floors")
    require(ni + nj >= si + sj + 2 * sk + 2 * central, "joint floor")
    require(alpha * ni + beta * nj == tariff(elements, alpha, beta), "attaining tariff")


def fixtures() -> tuple[tuple[int, ...], ...]:
    return (
        tuple(product(range(8), repeat=2))
        + tuple(product(range(8), repeat=3))
        + (
            tuple(range(8)),
            (1, 6, 7, 3, 5, 0, 0, 0),
            (1,) * 8,
            (6, 7) * 4,
        )
    )
