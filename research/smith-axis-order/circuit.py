"""Heterogeneous integral Smith tensor; exact Gaussian residue arithmetic.

All arrays are owned scratch. Erasure and physical routing are outside the
addition-precision tariff. No predecessor implementation is imported.
"""

from fractions import Fraction

Gaussian = tuple[int, int]
MAX_AXES = 8
MAX_PRECISION = 64
MAX_GAP = 64


def validate(gaps: tuple[int, ...], precision: int) -> None:
    if not isinstance(gaps, tuple) or not 1 <= len(gaps) <= MAX_AXES:
        raise ValueError("expected 1..8 axes as a tuple")
    if type(precision) is not int or not 0 <= precision <= MAX_PRECISION:
        raise ValueError("precision must be an integer in 0..64")
    if any(type(gap) is not int or not 0 <= gap <= MAX_GAP for gap in gaps):
        raise ValueError("gaps must be integers in 0..64")


def validate_order(order: tuple[int, ...], width: int) -> None:
    if not isinstance(order, tuple) or len(order) != width:
        raise ValueError("order must have one entry per axis")
    if any(type(axis) is not int for axis in order):
        raise ValueError("axis indices must be integers")
    if sorted(order) != list(range(width)):
        raise ValueError("order must be a permutation")


def mul(left: Gaussian, right: Gaussian) -> Gaussian:
    a, b = left
    c, d = right
    return a * c - b * d, a * d + b * c


def pi_power(exponent: int) -> Gaussian:
    # At most 8*64 valuation units in a tensor coordinate.
    if type(exponent) is not int or not 0 <= exponent <= MAX_AXES * MAX_GAP:
        raise ValueError("invalid valuation exponent")
    value = (1, 0)
    for _ in range(exponent):
        value = mul(value, (1, 1))
    return value


def residue(value: Gaussian, precision: int) -> Gaussian:
    """A fundamental parallelogram representative modulo (1+i)**precision."""
    modulus = pi_power(precision)
    a, b = modulus
    x, y = value
    norm = a * a + b * b
    quotient = ((x * a + y * b) // norm, (y * a - x * b) // norm)
    removed = mul(quotient, modulus)
    return x - removed[0], y - removed[1]


def gather_mass(gaps: tuple[int, ...], precision: int, order: tuple[int, ...]) -> int:
    validate(gaps, precision)
    validate_order(order, len(gaps))
    demands = [precision]
    total = 0
    for position, axis in enumerate(order):
        total += (1 << (len(gaps) - position - 1)) * sum(demands)
        demands += [max(0, demand - gaps[axis]) for demand in demands]
    return total


def optimal_orders(
    gaps: tuple[int, ...], precision: int
) -> tuple[tuple[int, ...], tuple[int, ...]]:
    validate(gaps, precision)
    gather = tuple(sorted(range(len(gaps)), key=lambda axis: -gaps[axis]))
    return gather, tuple(reversed(gather))


def optimal_mass(gaps: tuple[int, ...], precision: int) -> int:
    gather, _ = optimal_orders(gaps, precision)
    return 2 * gather_mass(gaps, precision, gather)


def is_optimal_order(
    gaps: tuple[int, ...], precision: int, order: tuple[int, ...]
) -> bool:
    validate(gaps, precision)
    validate_order(order, len(gaps))
    clipped = [min(gaps[axis], precision) for axis in order]
    return all(
        left >= right for left, right in zip(clipped[:-1], clipped[1:], strict=True)
    )


def exchange_delta(
    prefix_gaps: tuple[int, ...], a: int, b: int, precision: int
) -> Fraction:
    """Normalized gather difference for orders (a,b) and (b,a)."""
    validate(prefix_gaps + (a, b), precision)
    remaining = [precision]
    for gap in prefix_gaps:
        remaining += [max(0, demand - gap) for demand in remaining]
    return Fraction(
        sum(max(0, value - a) - max(0, value - b) for value in remaining),
        2 * len(remaining),
    )


def check_inputs(
    gaps: tuple[int, ...],
    precision: int,
    gather: tuple[int, ...],
    delivery: tuple[int, ...],
    values: tuple[Gaussian, ...],
) -> None:
    validate(gaps, precision)
    validate_order(gather, len(gaps))
    validate_order(delivery, len(gaps))
    if not isinstance(values, tuple) or len(values) != 1 << len(gaps):
        raise ValueError("input must contain exactly 2**n Gaussian integers")
    for value in values:
        if (
            not isinstance(value, tuple)
            or len(value) != 2
            or any(type(part) is not int or abs(part) > 10**6 for part in value)
        ):
            raise ValueError(
                "Gaussian coordinates must be integer pairs of height <=10**6"
            )


def gather_pass(
    gaps: tuple[int, ...], precision: int, order: tuple[int, ...], work: list[Gaussian]
) -> tuple[list[int], int]:
    demands = [precision] * len(work)
    mass = 0
    for axis in order:
        bit = 1 << axis
        for low in range(len(work)):
            if low & bit:
                continue
            high = low | bit
            q = demands[low]
            if q != demands[high]:
                raise ArithmeticError("gather pair precision mismatch")
            # a <- a-i*b before discarding digits of b.
            a, b = work[low], work[high]
            work[low] = residue((a[0] + b[1], a[1] - b[0]), q)
            demands[high] = max(0, q - gaps[axis])
            work[high] = residue(b, demands[high])
            mass += q
    return demands, mass


def delivery_pass(
    gaps: tuple[int, ...],
    precision: int,
    order: tuple[int, ...],
    work: list[Gaussian],
    demands: list[int],
) -> int:
    tags = [
        sum(gap for axis, gap in enumerate(gaps) if index & (1 << axis))
        for index in range(len(work))
    ]
    mass = 0
    for axis in order:
        bit = 1 << axis
        scale = pi_power(gaps[axis])
        for low in range(len(work)):
            if low & bit:
                continue
            high = low | bit
            q = max(0, precision - tags[low])
            if (
                tags[high] != tags[low] + gaps[axis]
                or demands[low] != q
                or demands[high] != max(0, q - gaps[axis])
            ):
                raise ArithmeticError("delivery tag/precision mismatch")
            a = work[low]
            b = mul(scale, work[high])
            work[high] = residue((a[0] + b[0], a[1] + b[1]), q)
            work[low] = residue((-a[1], a[0]), q)
            tags[high] = tags[low]
            demands[high] = q
            mass += q
    if any(tags) or any(q != precision for q in demands):
        raise ArithmeticError("incomplete delivery")
    return mass


def execute(
    gaps: tuple[int, ...],
    precision: int,
    gather: tuple[int, ...],
    delivery: tuple[int, ...],
    values: tuple[Gaussian, ...],
) -> tuple[tuple[Gaussian, ...], int]:
    check_inputs(gaps, precision, gather, delivery, values)
    work = [residue(value, precision) for value in values]
    demands, first_mass = gather_pass(gaps, precision, gather, work)
    second_mass = delivery_pass(gaps, precision, delivery, work, demands)
    return tuple(work), first_mass + second_mass
