"""Exact finite corroboration of the unequal-gain cycle theorem.

Produced by Nick Petalas. Apache-2.0.
The arbitrary-width theorem is the written proof, not these finite fixtures.
"""

import json
from collections.abc import Callable
from fractions import Fraction as Q
from hashlib import sha256
from itertools import product
from pathlib import Path

Matrix = tuple[tuple[Q, ...], ...]
MAX_SIZE = 14
BISECTION_STEPS = 24


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def identity(n: int) -> Matrix:
    require(1 <= n <= MAX_SIZE, "matrix size")
    return tuple(tuple(Q(i == j) for j in range(n)) for i in range(n))


def transpose(a: Matrix) -> Matrix:
    return tuple(zip(*a, strict=True))


def multiply(a: Matrix, b: Matrix) -> Matrix:
    n = len(a)
    require(1 <= n <= MAX_SIZE and len(b) == n, "matrix sizes")
    columns = transpose(b)
    return tuple(
        tuple(
            sum((x * y for x, y in zip(row, col, strict=True)), Q(0)) for col in columns
        )
        for row in a
    )


def validate(gains: tuple[Q, ...], edges: tuple[Matrix, ...], r: Q) -> None:
    w = len(gains)
    require(2 <= w <= 7 and len(edges) == w, "cycle size")
    d = len(edges[0])
    require(d in (1, 2) and w * d <= MAX_SIZE, "internal dimension")
    require(0 < r < 1 and all(g > 0 for g in gains), "positive gains and mean")
    gain_product = Q(1)
    for gain in gains:
        gain_product *= gain
    require(gain_product == r**w, "fixed product")
    for edge in edges:
        require(len(edge) == d and all(len(row) == d for row in edge), "edge shape")
        require(multiply(transpose(edge), edge) == identity(d), "unitary edge")


def cycle(gains: tuple[Q, ...], edges: tuple[Matrix, ...], r: Q) -> Matrix:
    validate(gains, edges, r)
    w, d = len(gains), len(edges[0])
    a = [list(row) for row in identity(w * d)]
    for j, gain in enumerate(gains):
        for row, col in product(range(d), repeat=2):
            a[j * d + row][((j + 1) % w) * d + col] += gain * edges[j][row][col]
    return tuple(tuple(row) for row in a)


def gauge(gains: tuple[Q, ...], r: Q, d: int) -> tuple[Q, ...]:
    weights = [Q(1)]
    for gain in gains[:-1]:
        weights.append(r * weights[-1] / gain)
    require(r * weights[-1] == gains[-1], "closing gauge")
    return tuple(weight for weight in weights for _ in range(d))


def check_similarity(a: Matrix, b: Matrix, weights: tuple[Q, ...]) -> None:
    n = len(a)
    require(len(b) == n and len(weights) == n, "similarity sizes")
    require(all(weights), "invertible gauge")
    conjugated = tuple(
        tuple(a[i][j] * weights[j] / weights[i] for j in range(n)) for i in range(n)
    )
    require(conjugated == b, "weighted-to-uniform similarity")


def positive_definite(a: Matrix) -> bool:
    """Exact Schur elimination; nonpositive pivots reject strict positivity."""
    n = len(a)
    require(1 <= n <= MAX_SIZE and a == transpose(a), "symmetric bounded matrix")
    work = [list(row) for row in a]
    for k in range(n):
        pivot = work[k][k]
        if pivot <= 0:
            return False
        for i in range(k + 1, n):
            for j in range(i, n):
                value = work[i][j] - work[i][k] * work[j][k] / pivot
                work[i][j] = work[j][i] = value
    return True


def shift(a: Matrix, t: Q, sign: int) -> Matrix:
    n = len(a)
    return tuple(
        tuple(sign * a[i][j] - (t if i == j else 0) for j in range(n)) for i in range(n)
    )


def extreme_bounds(a: Matrix) -> tuple[Q, Q, Q, Q]:
    """Enclose both extremes of a positive Gram matrix by rational PD tests."""
    gram = multiply(transpose(a), a)
    require(positive_definite(gram), "invertible observation")
    cap = 1 + max(sum(abs(value) for value in row) for row in gram)
    min_lo, min_hi, max_lo, max_hi = Q(0), cap, Q(0), cap
    for _ in range(BISECTION_STEPS):
        mid = (min_lo + min_hi) / 2
        if positive_definite(shift(gram, mid, 1)):
            min_lo = mid
        else:
            min_hi = mid
        mid = (max_lo + max_hi) / 2
        if positive_definite(shift(gram, -mid, -1)):
            max_hi = mid
        else:
            max_lo = mid
    require(0 < min_lo <= min_hi < cap and 0 < max_lo <= max_hi, "root brackets")
    return min_lo, min_hi, max_lo, max_hi


def check_weight_diagonals(a: Matrix, gains: tuple[Q, ...], d: int) -> None:
    n = len(a)
    t = tuple(tuple(a[i][j] - Q(i == j) for j in range(n)) for i in range(n))
    left, right = multiply(transpose(t), t), multiply(t, transpose(t))
    expected_left = tuple(
        tuple(
            gains[(i // d - 1) % len(gains)] ** 2 if i == j else Q(0) for j in range(n)
        )
        for i in range(n)
    )
    expected_right = tuple(
        tuple(gains[i // d] ** 2 if i == j else Q(0) for j in range(n))
        for i in range(n)
    )
    require(left == expected_left and right == expected_right, "gain diagonals")
    require((left == right) == (len(set(gains)) == 1), "normality equality")


def edge_families(w: int) -> tuple[tuple[Matrix, ...], ...]:
    sigma = Q((-1) ** (w + 1))
    scalar = tuple(((Q(1),),) for _ in range(w - 1))
    rotation = ((Q(3, 5), Q(-4, 5)), (Q(4, 5), Q(3, 5)))
    reflection = ((Q(1), Q(0)), (Q(0), Q(-1)))
    bases = tuple((identity(2), rotation, reflection)[j % 3] for j in range(w))
    prefix = tuple(multiply(bases[j], transpose(bases[j + 1])) for j in range(w - 1))
    closing = tuple(tuple(sigma * x for x in row) for row in bases[-1])
    noncentral = multiply(bases[-1], reflection)
    return (
        scalar + (((sigma,),),),
        scalar + (((-sigma,),),),
        prefix + (closing,),
        prefix + (noncentral,),
    )


def fixtures() -> dict[str, int]:
    counts = {
        "literal_cycles": 0,
        "uniform_controls": 0,
        "strict_gaps": 0,
        "noncommuting_cycles": 0,
        "gains_above_one": 0,
    }
    for w, r in product((2, 3, 4, 5, 7), (Q(1, 3), Q(1, 2))):
        exponents = ((0,) * w, (1, -1) + (0,) * (w - 2), (2,) + (0,) * (w - 2) + (-2,))
        for edges in edge_families(w):
            d = len(edges[0])
            b = cycle((r,) * w, edges, r)
            require(
                multiply(transpose(b), b) == multiply(b, transpose(b)),
                "normal comparator",
            )
            b_min_lo, _, _, b_max_hi = extreme_bounds(b)
            noncommuting = any(
                multiply(x, y) != multiply(y, x) for x, y in product(edges, repeat=2)
            )
            for powers in exponents:
                gains = tuple(r * Q(2) ** power for power in powers)
                a = cycle(gains, edges, r)
                check_similarity(a, b, gauge(gains, r, d))
                check_weight_diagonals(a, gains, d)
                counts["literal_cycles"] += 1
                counts["noncommuting_cycles"] += int(noncommuting)
                counts["gains_above_one"] += int(max(gains) > 1)
                if len(set(gains)) == 1:
                    require(a == b, "uniform attainment")
                    counts["uniform_controls"] += 1
                    continue
                _, a_min_hi, a_max_lo, _ = extreme_bounds(a)
                require(
                    a_max_lo * b_min_lo > b_max_hi * a_min_hi,
                    "strict condition gap from disjoint rational bounds",
                )
                counts["strict_gaps"] += 1
    return counts


def expect_rejection(action: Callable[..., object], args: tuple, label: str) -> None:
    try:
        action(*args)
    except ValueError:
        return
    raise ValueError("control accepted: " + label)


def controls() -> tuple[str, ...]:
    r, edges = Q(1, 2), (((Q(1),),), ((Q(-1),),))
    invalid = (
        ("zero gain", cycle, ((Q(0), Q(1)), edges, r)),
        ("negative gains", cycle, ((Q(-1), Q(-1, 4)), edges, r)),
        ("wrong product", cycle, ((Q(1), Q(1, 2)), edges, r)),
        ("zero mean", cycle, ((r, r), edges, Q(0))),
        ("unit mean", cycle, ((r, r), edges, Q(1))),
        ("one bank", cycle, ((r,), edges[:1], r)),
        ("nonunitary", cycle, ((r, r), (((Q(2),),), edges[1]), r)),
        ("wrong shape", cycle, ((r, r), (identity(2), edges[1]), r)),
    )
    for label, action, args in invalid:
        expect_rejection(action, args, label)
    gains = (Q(1), Q(1, 4))
    a, b = cycle(gains, edges, r), cycle((r, r), edges, r)
    expect_rejection(check_similarity, (a, b, (Q(1), Q(2))), "reversed gauge")
    gram = multiply(transpose(a), a)
    require(gram == ((Q(17, 16), Q(3, 4)), (Q(3, 4), Q(2))), "literal two-bank Gram")
    require(gram[0][0] + gram[1][1] == Q(49, 16), "two-bank trace")
    require(
        gram[0][0] * gram[1][1] - gram[0][1] ** 2 == Q(25, 16), "two-bank determinant"
    )
    require(
        gram != tuple(tuple(Q(5, 4) * x for x in row) for row in identity(2)),
        "same spectrum does not preserve Euclidean conditioning",
    )
    weights = gauge(gains, r, 1)
    metric = tuple(
        tuple(1 / weights[i] ** 2 if i == j else Q(0) for j in range(2))
        for i in range(2)
    )
    require(
        multiply(transpose(a), multiply(metric, a))
        == tuple(tuple(Q(5, 4) * x for x in row) for row in metric),
        "bank-weighted norm is a different contract",
    )
    require(not positive_definite(((Q(1), Q(1)), (Q(1), Q(1)))), "singular pivot")
    require(not positive_definite(((Q(1), Q(2)), (Q(2), Q(1)))), "indefinite pivot")
    return tuple(row[0] for row in invalid) + (
        "reversed gauge",
        "same-spectrum exhibit",
        "changed-metric exhibit",
        "singular",
        "indefinite",
    )


def main() -> None:
    counts = fixtures()
    labels = controls()
    counts["boundary_controls"] = len(labels)
    package = Path(__file__).resolve().parent
    names = ("README.md", "SOURCES.json", "TASK.json", "VERIFY.json", "verify.py")
    hashes = {name: sha256((package / name).read_bytes()).hexdigest() for name in names}
    receipt = {
        "status": "PASS_UNEQUAL_GAIN_CYCLE_OPTIMUM",
        "claim_type": "scoped proof",
        "finite_evidence": counts,
        "control_labels": labels,
        "bisection_steps": BISECTION_STEPS,
        "source_sha256": hashes,
    }
    print(json.dumps(receipt, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
