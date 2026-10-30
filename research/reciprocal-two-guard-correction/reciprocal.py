"""Two-guard reciprocal construction; see PROOF.md for the real-input theorem."""

from dataclasses import dataclass
from fractions import Fraction

MAX_TARGET = 4096


@dataclass(frozen=True)
class Result:
    value: Fraction
    stages: tuple[tuple[int, int, Fraction], ...]
    center: int
    selected: int
    candidates: int


def floor_grid(value: Fraction, bits: int) -> Fraction:
    if not 0 <= bits <= MAX_TARGET + 2:
        raise ValueError("unsupported grid precision")
    scale = 1 << bits
    return Fraction((value.numerator << bits) // value.denominator, scale)


def newton_step(c: Fraction, x: Fraction, bits: int) -> Fraction:
    prefix = floor_grid(c, bits)
    product = floor_grid(prefix * x, bits)
    return floor_grid(x * (2 - product), bits)


def evaluate(c: Fraction, target: int) -> Result:
    """Use two fractional guard bits and a bounded final correction.

    This research implementation caps targets at 4096. The written arithmetic
    proof covers every positive integer target. No division by c is used.
    """
    if type(target) is not int or not 1 <= target <= MAX_TARGET:
        raise ValueError("target must be an integer in 1..4096")
    if not isinstance(c, Fraction) or not 1 <= c < 2:
        raise ValueError("input must be a rational in [1,2)")
    if max(c.numerator.bit_length(), c.denominator.bit_length()) > 16384:
        raise ValueError("rational input exceeds the research bit budget")
    x = newton_step(c, Fraction(5, 8), 6)
    m = 2
    stages = [(m, 6, x)]
    for _ in range(max(0, target - 2)):
        if m >= target:
            break
        m = min(2 * m - 1, target)
        x = newton_step(c, x, m + 2)
        stages.append((m, m + 2, x))
    scale = 1 << (target + 2)
    center = (x.numerator << (target + 2)) // x.denominator
    prefix = (c.numerator << (target + 2)) // c.denominator
    candidates = tuple(j for j in range(center - 6, center + 7)
                       if scale // 2 <= j <= scale)
    if not candidates:
        raise ArithmeticError("empty correction window")
    unit = 1 << (2 * (target + 2))
    selected = candidates[0]
    best = abs(unit - prefix * selected)
    for j in candidates[1:]:
        score = abs(unit - prefix * j)
        if score < best:
            selected, best = j, score
    return Result(Fraction(selected, scale), tuple(stages), center,
                  selected, len(candidates))
