"""Exact finite corroboration of the mixed-negative Q8 boundary-rank proof."""

import hashlib
import itertools
import json
from pathlib import Path
import random

ROOT = Path(__file__).resolve().parent
MAX_DIM = 16


def require(ok, message):
    if not ok:
        raise ValueError(message)


def rank(rows):
    require(len(rows) <= MAX_DIM, "rank row capacity")
    pivots = [0] * MAX_DIM
    total = 0
    for value in rows:
        require(type(value) is int and 0 <= value < 1 << MAX_DIM, "rank domain")
        for pivot in range(MAX_DIM - 1, -1, -1):
            if value >> pivot & 1:
                if pivots[pivot]:
                    value ^= pivots[pivot]
                else:
                    pivots[pivot] = value
                    total += 1
                    break
    return total


def mm(a, b):
    require(len(a) <= MAX_DIM and len(b) <= MAX_DIM, "matrix capacity")
    result = []
    for row in a:
        require(0 <= row < 1 << len(b), "matrix inner dimension")
        value = 0
        for j, other in enumerate(b):
            if row >> j & 1:
                value ^= other
        result.append(value)
    return tuple(result)


def add(a, b):
    require(len(a) == len(b), "matrix sum shape")
    return tuple(x ^ y for x, y in zip(a, b, strict=True))


def ident(n):
    require(type(n) is int and 0 <= n <= MAX_DIM, "identity capacity")
    return tuple(1 << j for j in range(n))


def group_product(a, b):
    ai, aj, bi, bj = a & 1, a >> 1 & 1, b & 1, b >> 1 & 1
    central = (a >> 2) ^ (b >> 2) ^ (ai & bi) ^ (aj & bj) ^ (aj & bi)
    return central << 2 | (ai ^ bi) | (aj ^ bj) << 1


def mul(a, b):
    value = 0
    for i in range(8):
        for j in range(8):
            if (a >> i & 1) and (b >> j & 1):
                value ^= 1 << group_product(i, j)
    return value


def hamilton(a, b):
    """Independent signed-unit table, in the same eight group basis slots."""
    axes = ((0, 1, 2, 3), (1, 0, 3, 2), (2, 3, 0, 1), (3, 2, 1, 0))
    signs = ((0, 0, 0, 0), (0, 1, 0, 1), (0, 1, 1, 0), (0, 0, 1, 1))
    x, y = a & 3, b & 3
    return axes[x][y] + 4 * ((a >> 2) ^ (b >> 2) ^ signs[x][y])


def basis(swapped=False):
    x, y, tau = (5, 3, 17) if swapped else (3, 5, 17)
    q = mul(x, y)
    values = (1, x, y, tau, q, mul(tau, x), mul(tau, y), mul(tau, q))
    inverse = {}
    for mask in range(256):
        value = 0
        for j, element in enumerate(values):
            if mask >> j & 1:
                value ^= element
        require(value not in inverse, "dependent algebra basis")
        inverse[value] = mask
    return inverse


def algebra_checks():
    require(
        all(
            group_product(a, b) == hamilton(a, b)
            for a, b in itertools.product(range(8), repeat=2)
        ),
        "Hamilton disagreement",
    )
    cases = 0
    for swapped in (False, True):
        inverse = basis(swapped)
        x, y = (5, 3) if swapped else (3, 5)
        for length in range(1, 6):
            for labels in itertools.product((0, 1), repeat=length):
                value = 1
                for label in labels:
                    value = mul(value, (x, y)[label])
                coeff = inverse[value]
                if length == 2:
                    require(
                        (coeff >> 3 & 1) == int(labels != (0, 1)), "quadratic table"
                    )
                    require(((coeff >> 5 ^ coeff >> 6) & 1) == 0, "pair cubic sum")
                elif length == 3:
                    a, b, c = labels
                    predicted = int((a, b) != (0, 1)) * int((b, c) != (0, 1))
                    predicted ^= int(a == 0 and c == 1)
                    require(
                        ((coeff >> 5 ^ coeff >> 6) & 1) == predicted, "triple table"
                    )
                elif length >= 4:
                    require(coeff in (0, 128), "fourth degree leakage")
                    if length == 5:
                        require(value == 0, "fifth degree leakage")
                cases += 1
    return {"Hamilton_products": 64, "basis_values": 512, "increment_products": cases}


def validate_word(word, roles):
    require(type(roles) is int and 1 <= roles <= 8, "role capacity")
    require(1 <= len(word) <= MAX_DIM, "word capacity")
    for g, u, v in word:
        require(type(g) is int and g in (1, 2), "paid label")
        require(type(u) is int and type(v) is int, "projector type")
        require(0 < u < 1 << roles and 0 < v < 1 << roles, "projector dimension")
        require((u & v).bit_count() % 2 == 1, "projector idempotence")


def endpoint(word, roles):
    validate_word(word, roles)
    state = [[int(a == b) for b in range(roles)] for a in range(roles)]
    for g, u, v in word:
        selected = [0] * roles
        for a in range(roles):
            if v >> a & 1:
                for b in range(roles):
                    selected[b] ^= state[a][b]
        change = [mul(1 ^ (1 << g), value) for value in selected]
        for a in range(roles):
            if u >> a & 1:
                state[a] = [p ^ q for p, q in zip(state[a], change, strict=True)]
    return tuple(tuple(row) for row in state)


def direct_column(word, roles, column):
    state = [0] * roles
    state[column // 8] = 1 << (column % 8)
    for g, u, v in word:
        selected = 0
        for a in range(roles):
            if v >> a & 1:
                selected ^= state[a]
        changed = selected
        for k in range(8):
            if selected >> k & 1:
                changed ^= 1 << hamilton(g, k)
        for a in range(roles):
            if u >> a & 1:
                state[a] ^= changed
    return tuple(state)


def coefficient(state, inverse, bit):
    return tuple(
        sum(((inverse[value] >> bit) & 1) << j for j, value in enumerate(row))
        for row in state
    )


def chronology(word, roles, swapped=False):
    validate_word(word, roles)
    labels = tuple((3 - g if swapped else g) for g, _, _ in word)
    x = tuple(
        sum(((u >> r) & 1) << k for k, (_, u, _) in enumerate(word))
        for r in range(roles)
    )
    y = tuple(v for _, _, v in word)
    gram = mm(y, x)
    lower = tuple(row & ((1 << k) - 1) for k, row in enumerate(gram))
    mask_i = sum((g == 1) << k for k, g in enumerate(labels))
    mask_j = ((1 << len(word)) - 1) ^ mask_i
    h = tuple(
        row & (~mask_j if g == 1 else -1) for row, g in zip(lower, labels, strict=True)
    )
    square = mm(lower, lower)
    correction = tuple(
        row & mask_j if g == 1 else 0 for row, g in zip(square, labels, strict=True)
    )
    return x, y, h, correction, mask_i, mask_j


def check_word(word, roles):
    state = endpoint(word, roles)
    for swapped in (False, True):
        inverse = basis(swapped)
        x, y, h, c, mask_i, mask_j = chronology(word, roles, swapped)
        xi = tuple(row & mask_i for row in x)
        xj = tuple(row & mask_j for row in x)
        require(mm(xi, y) == coefficient(state, inverse, 1), "first i coefficient")
        require(mm(xj, y) == coefficient(state, inverse, 2), "first j coefficient")
        require(
            mm(mm(x, h), y) == coefficient(state, inverse, 3), "quadratic chronology"
        )
        cubic = mm(mm(x, add(mm(h, h), c)), y)
        actual = add(coefficient(state, inverse, 5), coefficient(state, inverse, 6))
        require(cubic == actual, "cubic chronology")
    for column in range(8 * roles):
        expected = []
        for row in state:
            value = 0
            for k in range(8):
                if row[column // 8] >> k & 1:
                    value ^= 1 << hamilton(k, column % 8)
            expected.append(value)
        require(tuple(expected) == direct_column(word, roles, column), "dirty action")
    return 8 * roles


def generic_checks():
    rng = random.Random(2026101804)
    columns = 0
    words = 0
    for roles in range(1, 7):
        for length in range(1, 13):
            for _ in range(3):
                word = []
                for _ in range(length):
                    u = rng.randrange(1, 1 << roles)
                    candidates = tuple(
                        v for v in range(1, 1 << roles) if (u & v).bit_count() % 2
                    )
                    word.append((rng.choice((1, 2)), u, rng.choice(candidates)))
                columns += check_word(tuple(word), roles)
                words += 1
    return {"generic_words": words, "generic_dirty_columns": columns}


def boundary_checks():
    pairs = 0
    nonzero_products = 0
    for t in (1, 2):
        for n in range(1, 4):
            for xb, yb in itertools.product(range(1 << (t * n)), repeat=2):
                x = tuple((xb >> (n * j)) & ((1 << n) - 1) for j in range(t))
                y = tuple((yb >> (t * j)) & ((1 << t) - 1) for j in range(n))
                product_rank = rank(mm(x, y))
                require(
                    rank(x) + rank(y) <= n + product_rank, "boundary rank inequality"
                )
                nonzero_products += product_rank > 0
                pairs += 1
    require(rank(ident(2)) * 2 > 2, "missing nonzero-product control")
    return {"boundary_pairs": pairs, "nonzero_boundary_products": nonzero_products}


def cubic_rank_check(x, y, k):
    t, n = len(x), len(y)
    require(rank(k) == n, "K invertibility")
    require(mm(x, y) == ident(t), "XY identity")
    require(mm(mm(x, k), y) == (0,) * t, "XKY zero")
    value = rank(mm(mm(x, mm(k, k)), y))
    require(value >= 3 * t - n, "cubic rank lower bound")
    return value


def cubic_checks():
    fixtures = 0
    for t in (1, 2):
        n = 2 * t
        x = ident(t)
        y = ident(t) + (0,) * t
        for bits in range(1 << (n * n - t * t)):
            k, at = [], 0
            for row in range(n):
                value = 0
                for col in range(n):
                    if row >= t or col >= t:
                        value |= ((bits >> at) & 1) << col
                        at += 1
                k.append(value)
            if rank(k) == n:
                require(
                    cubic_rank_check(x, y, tuple(k)) == t, "saturated cubic fixture"
                )
                fixtures += 1
    return {"cubic_equality_fixtures": fixtures}


def admissible(ti, tj, ni, nj):
    require(
        all(type(v) is int and 0 <= v <= 96 for v in (ti, tj, ni, nj)), "count domain"
    )
    t, n = ti + tj, ni + nj
    require(0 < t <= 32, "target capacity")
    return (
        ni >= ti
        and nj >= tj
        and (ni - ti) % 2 == 0
        and (nj - tj) % 2 == 0
        and n + min(ni, nj) >= 3 * t
        and 2 * n + ni >= 6 * t - ti
        and 2 * n + nj >= 6 * t - tj
    )


def count_checks():
    accepted = 0
    for t in range(1, 17):
        for ti in range(t + 1):
            tj = t - ti
            for n in range(3 * t + 1):
                for ni in range(n + 1):
                    if admissible(ti, tj, ni, n - ni):
                        require(5 * n >= 11 * t, "uniform 11t/5 consequence")
                        accepted += 1
    require(not admissible(2, 2, 4, 4), "balanced eight-call exclusion")
    require(admissible(2, 2, 4, 6), "ten-call necessary-count control")
    return {"accepted_count_pairs": accepted, "balanced_four_target_lengths": [10, 12]}


def endpoint_checks():
    endpoints = 0
    columns = 0
    for t in range(1, 5):
        for ti in range(t + 1):
            for dirt in range(3):
                roles = t + dirt
                labels = (1,) * ti + (2,) * (t - ti)
                word = tuple(
                    (g, 1 << j, 1 << j) for j, g in enumerate(labels) for _ in range(3)
                )
                state = endpoint(word, roles)
                for a, row in enumerate(state):
                    for b, value in enumerate(row):
                        desired = 1 << (labels[a] ^ 4) if a < t else 1
                        require(value == (desired if a == b else 0), "direct endpoint")
                require(
                    admissible(ti, t - ti, 3 * ti, 3 * (t - ti)), "upper word count"
                )
                columns += check_word(word, roles)
                endpoints += 1
    return {"direct_endpoints": endpoints, "endpoint_dirty_columns": columns}


def source_checks():
    retention = json.loads((ROOT / "inputs/RETENTION.json").read_text())
    require(len(retention["files"]) == 4, "proof source closure")
    for item in retention["files"]:
        name = item["retained_path"]
        require(
            name.startswith("inputs/pr")
            and name.endswith("-PROOF.md")
            and "/" not in name[7:],
            "retained source path",
        )
        require(
            hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == item["sha256"],
            "retained proof bytes",
        )
    return {
        "retained_proof_sources": 4,
        "proof_sha256": hashlib.sha256((ROOT / "PROOF.md").read_bytes()).hexdigest(),
    }


def run_checks():
    result = {
        "status": "PASS_Q8_MIXED_BOUNDARY_RANK",
        "scope": "finite corroboration; see universal proof",
    }
    for part in (
        algebra_checks(),
        generic_checks(),
        boundary_checks(),
        cubic_checks(),
        count_checks(),
        endpoint_checks(),
        source_checks(),
    ):
        require(not result.keys() & part.keys(), "duplicate receipt key")
        result.update(part)
    return result


def main():
    actual = run_checks()
    expected = json.loads((ROOT / "RESULT.json").read_text())
    require(actual == expected, "finite receipt mismatch")
    print(json.dumps(actual, sort_keys=True))


if __name__ == "__main__":
    main()
