"""Exact arithmetic for one changed borrowing contract. Nick Petalas. Apache-2.0."""

from fractions import Fraction
from itertools import pairwise

CUTOFF = 245767
TAIL = 1 << 20
PRIME = 213 * (1 << 80) + 1


def need(condition, message):
    if not condition:
        raise ValueError(message)


def depth(width):
    need(type(width) is int and 0 <= width <= TAIL, "depth replay capacity")
    for count in range(2 * width.bit_length() + 1):
        if width < 64:
            return count
        width = 42 * (width // 64)
    raise ValueError("depth contraction bound")


def staircase():
    thresholds = [0, 64]
    for _ in range(64):
        following = 64 * ((thresholds[-1] + 41) // 42)
        need(following > thresholds[-1], "strict inverse staircase")
        thresholds.append(following)
        if following > TAIL:
            return thresholds
    raise ValueError("inverse staircase capacity")


def finite_slabs():
    thresholds = staircase()
    rows = []
    for d in range(1, len(thresholds) - 1):
        first = max(CUTOFF, 4 * thresholds[d] - 2)
        last = min(TAIL - 1, 4 * thresholds[d + 1] - 3)
        if first > last:
            continue
        required = 8192 * d + (14 + 15 * d + 79) // 80
        need(first > 2 * required, "entire slab has strict borrowing fit")
        need((first + 2) // 4 >= 64, "entire slab has an internal body")
        need(depth((first + 2) // 4) == d, "first endpoint depth")
        need(depth((last + 2) // 4) == d, "last endpoint depth")
        rows.append(
            dict(
                first=first,
                last=last,
                depth=d,
                required_upper=required,
                first_margin=first - 2 * required,
            )
        )
    need(rows[0]["first"] == CUTOFF, "finite cover starts at cutoff")
    need(rows[-1]["last"] == TAIL - 1, "finite cover reaches tail")
    for left, right in pairwise(rows):
        need(left["last"] + 1 == right["first"], "no missing finite interval")
    need(17 * 20 < 10000, "exact atom width two throughout finite cover")
    return rows


def tail_certificate():
    need(2 * 42**2 < 64**2, "two recursive steps more than halve width")
    need(9475 < 2**14 and 28416 < 2**15, "compiled stock coefficients")
    need(29 < 80, "log stock below 4097*w*d")
    need(17 * 21 < 5000 and 2 < Fraction(3, 2) ** 2, "initial tail power bound")
    initial = 16388 * 21 * Fraction(3, 2) + 1
    ratio = Fraction(22, 21) * Fraction(3, 4)
    need(initial == 516223 and initial < 2**19, "initial dyadic tail margin")
    need(
        ratio == Fraction(11, 14) and Fraction(1, 2) <= ratio < 1,
        "all later normalized bounds contract",
    )
    need(2**10 // 4 - 1 > 64, "tail body lower bound")
    return dict(
        first_dyadic_index=20,
        initial_upper=int(initial),
        initial_limit=2**19,
        normalized_ratio=str(ratio),
        minimum_body_lower=255,
    )


def prime_certificate(q=PRIME, witness=7):
    need(type(q) is int and q == PRIME, "prescribed exact prime")
    need(type(witness) is int and 1 < witness < q, "prime witness range")
    residue = pow(witness, (q - 1) // 2, q)
    need(residue == q - 1, "order forces every prime divisor above square root")
    need(((1 << 80) + 1) ** 2 > q, "prime-divisor bound exceeds square root")
    return dict(
        q=str(q),
        odd_cofactor=213,
        power_of_two=80,
        witness=witness,
        half_order_residue=str(residue),
    )


def boundary_certificate():
    e = CUTOFF - 1
    maximum = (e - 1) // 2
    body = (e - maximum) // 2
    d = depth(body)
    coefficient = 9475 * 28416**d
    need((e, maximum, body, d) == (245766, 122882, 61442, 15), "sharp boundary geometry")
    need(1 < e**17 < 2**10000, "boundary atom width exactly two")
    need(4 * PRIME**2 < coefficient < PRIME**3, "exact coefficient enclosure")
    need(2 * d < PRIME - 1, "P(q)^d greater than one half")
    need(8192 * d + 3 == maximum + 1, "strict and covering both require one more")
    return dict(
        width=e,
        maximum_legal_k=maximum,
        minimum_body=body,
        minimum_depth=d,
        both_required_k=maximum + 1,
        coefficient=str(coefficient),
        lower_power_factor=4,
        lower_power_exponent=2,
        upper_power_exponent=3,
    )


def certificate():
    return dict(
        cutoff=CUTOFF,
        boundary=CUTOFF - 1,
        predicates=["S<=q^k", "S<2*q^k"],
        finite_slabs=finite_slabs(),
        tail=tail_certificate(),
        prime=prime_certificate(),
        no_fit=boundary_certificate(),
    )
