#!/usr/bin/env python3
"""Exact affine-tag membership and adversaries in the promised quadratic class."""

from dataclasses import dataclass
from hashlib import sha256
from itertools import combinations, product
import json
from pathlib import Path
from random import Random
from typing import Callable


MAX_AXES = 64
MAX_TERMS = 1 + MAX_AXES * (MAX_AXES + 1) // 2


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def dimension(n: int) -> None:
    if type(n) is not int or not 1 <= n <= MAX_AXES:
        raise ValueError("dimension must be an integer in 1..64")


def pairs(n: int) -> tuple[tuple[int, int], ...]:
    dimension(n)
    return tuple(combinations(range(n), 2))


@dataclass(frozen=True)
class Phase:
    constant: int
    linear: tuple[int, ...]
    quadratic: tuple[int, ...]

    def __post_init__(self) -> None:
        if type(self.linear) is not tuple or type(self.quadratic) is not tuple:
            raise ValueError("phase coefficients must be immutable tuples")
        dimension(len(self.linear))
        if type(self.constant) is not int or self.constant not in range(4):
            raise ValueError("constant must be in Z/4")
        if any(type(a) is not int or a not in range(4) for a in self.linear):
            raise ValueError("linear coefficients must be in Z/4")
        if len(self.quadratic) != len(pairs(len(self.linear))):
            raise ValueError("wrong number of quadratic coefficients")
        if any(type(b) is not int or b not in (0, 1) for b in self.quadratic):
            raise ValueError("quadratic coefficients must be binary")

    def at(self, x: int) -> int:
        n = len(self.linear)
        if type(x) is not int or not 0 <= x < 1 << n:
            raise ValueError("address outside the binary cube")
        value = self.constant
        for i in range(n):
            value += self.linear[i] * ((x >> i) & 1)
        for b, (i, j) in zip(self.quadratic, pairs(n), strict=True):
            value += 2 * b * ((x >> i) & 1) * ((x >> j) & 1)
        return value % 4


def null_vector(rows: tuple[int, ...], width: int) -> int | None:
    """Return a nonzero binary null vector, or None for full column rank."""
    if not 1 <= width <= MAX_TERMS:
        raise ValueError("unsupported binary matrix width")
    if len(rows) > MAX_TERMS or any(not 0 <= r < 1 << width for r in rows):
        raise ValueError("binary matrix exceeds the bounded domain")
    pivots: dict[int, int] = {}
    for row in rows:
        for p in range(width - 1, -1, -1):
            if row >> p & 1:
                if p in pivots:
                    row ^= pivots[p]
                else:
                    pivots[p] = row
                    break
    free = next((p for p in range(width) if p not in pivots), None)
    if free is None:
        return None
    vector = 1 << free
    for p in range(width):
        if p in pivots and (pivots[p] & vector).bit_count() % 2:
            vector |= 1 << p
    require(all((r & vector).bit_count() % 2 == 0 for r in rows), "null vector")
    return vector


def affine_value(columns: tuple[int, ...], offset: int, x: int) -> int:
    value = offset
    for i, col in enumerate(columns):
        if x >> i & 1:
            value ^= col
    return value


def check_affine(columns: tuple[int, ...], offset: int) -> None:
    n = len(columns)
    dimension(n)
    if type(offset) is not int or not 0 <= offset < 1 << n:
        raise ValueError("bad affine offset")
    if any(type(c) is not int or not 0 <= c < 1 << n for c in columns):
        raise ValueError("bad binary column")
    if null_vector(columns, n) is not None:
        raise ValueError("affine matrix is singular")


def test_points(n: int) -> tuple[int, ...]:
    dimension(n)
    return (0,) + tuple(1 << i for i in range(n)) + tuple(
        (1 << i) | (1 << j) for i, j in pairs(n)
    )


def certify(columns: tuple[int, ...], offset: int,
            oracle: Callable[[int], int]) -> tuple[int, int]:
    """Decide i^q(x)|Ax+b> = i^c J_(A,b) Z_t, assuming q is quadratic.

    The oracle's polynomial promise is a precondition, not something tested here.
    A valid affine descriptor is checked before any oracle call.
    """
    check_affine(columns, offset)
    n = len(columns)
    values: dict[int, int] = {}
    for x in test_points(n):
        q = oracle(x)
        if type(q) is not int or q not in range(4):
            raise ValueError("phase oracle must return an integer in Z/4")
        values[x] = (q - affine_value(columns, offset, x).bit_count()
                     + x.bit_count()) % 4
    constant = values[0]
    tag = 0
    for i in range(n):
        delta = (values[1 << i] - constant) % 4
        if delta % 2:
            raise ValueError("odd residual linear coefficient")
        tag |= (delta // 2) << i
    for i, j in pairs(n):
        x = (1 << i) | (1 << j)
        if values[x] != (constant + 2 * ((tag & x).bit_count() % 2)) % 4:
            raise ValueError("nonzero residual quadratic coefficient")
    return constant, tag


def monomials(n: int, x: int) -> int:
    row = 1 | (x << 1)
    for k, (i, j) in enumerate(pairs(n), n + 1):
        row |= (((x >> i) & 1) * ((x >> j) & 1)) << k
    return row


def adversary(n: int, points: tuple[int, ...]) -> Phase:
    """A non-tag residual vanishing on any fewer than d queried addresses."""
    dimension(n)
    d = 1 + n + len(pairs(n))
    if len(points) >= d or any(type(x) is not int or not 0 <= x < 1 << n
                               for x in points):
        raise ValueError("adversary needs fewer than d valid queries")
    anchor = points[0] if points else 0
    differences = tuple(x ^ anchor for x in points[1:])
    mask = null_vector(differences, n)
    if mask is not None:
        constant = -((mask & anchor).bit_count() % 2) % 4
        linear = tuple((mask >> i) & 1 for i in range(n))
        cross = tuple(((mask >> i) & 1) * ((mask >> j) & 1) for i, j in pairs(n))
        return Phase(constant, linear, cross)
    kernel = null_vector(tuple(monomials(n, x) for x in points), d)
    require(kernel is not None, "underdetermined quadratic evaluation map")
    linear = tuple(2 * ((kernel >> (i + 1)) & 1) for i in range(n))
    cross = tuple((kernel >> k) & 1 for k in range(n + 1, d))
    require(any(cross), "full affine span excludes affine null polynomials")
    return Phase(2 * (kernel & 1), linear, cross)


def literal_tag(phase: Phase) -> bool:
    """Independent cube-value definition; used only in small finite checks."""
    n = len(phase.linear)
    if n > 4:
        raise ValueError("literal oracle is restricted to at most four axes")
    values = tuple(phase.at(x) for x in range(1 << n))
    for tag in range(1 << n):
        if all(values[x] == (values[0] + 2 * ((tag & x).bit_count() % 2)) % 4
               for x in range(1 << n)):
            return True
    return False


def normalized_phase(columns: tuple[int, ...], offset: int,
                     constant: int, tag: int) -> Phase:
    """Coefficient construction, separate from the oracle membership test."""
    n = len(columns)
    linear = tuple((sum((1 - 2 * ((offset >> j) & 1)) * ((columns[i] >> j) & 1)
                        for j in range(n)) - 1 + 2 * ((tag >> i) & 1)) % 4
                   for i in range(n))
    cross = tuple((columns[i] & columns[j]).bit_count() % 2 for i, j in pairs(n))
    return Phase((constant + offset.bit_count()) % 4, linear, cross)


def check_small_phases() -> int:
    count = 0
    for n in range(1, 4):
        identity = tuple(1 << i for i in range(n))
        for linear in product(range(4), repeat=n):
            for cross in product(range(2), repeat=len(pairs(n))):
                for constant in range(4):
                    phase = Phase(constant, linear, cross)
                    try:
                        c, t = certify(identity, 0, phase.at)
                    except ValueError:
                        accepted = False
                    else:
                        accepted = True
                        require(all(phase.at(x) == (c + 2 * ((t & x).bit_count() % 2)) % 4
                                    for x in range(1 << n)), "returned tag")
                    require(accepted == literal_tag(phase), "literal membership")
                    count += 1
    return count


def check_subsets() -> int:
    count = 0
    for n in range(1, 5):
        d = len(test_points(n))
        for size in range(d):
            for points in combinations(range(1 << n), size):
                phase = adversary(n, points)
                require(all(phase.at(x) == 0 for x in points), "adversary transcript")
                require(not literal_tag(phase), "adversary must be outside tag family")
                count += 1
    return count


def check_constructions() -> int:
    rng = Random(20261028)
    count = 0
    for n in (1, 2, 3, 4, 5, 9, 16, 32, 64):
        for trial in range(4):
            # Upper triangular columns, with all diagonal entries equal to one.
            columns = tuple((1 << i) | rng.randrange(1 << i) for i in range(n))
            offset = rng.randrange(1 << n)
            constant, tag = trial, rng.randrange(1 << n)
            phase = normalized_phase(columns, offset, constant, tag)
            seen: list[int] = []

            def oracle(x: int) -> int:
                seen.append(x)
                return phase.at(x)

            require(certify(columns, offset, oracle) == (constant, tag), "affine construction")
            require(tuple(seen) == test_points(n), "each optimal query used exactly once")
            addresses = range(1 << n) if n <= 5 else test_points(n)
            for x in addresses:
                expected = (affine_value(columns, offset, x).bit_count() - x.bit_count()
                            + constant + 2 * ((tag & x).bit_count() % 2)) % 4
                require(phase.at(x) == expected, "direct weight-phase comparison")
            if n >= 2:
                points = test_points(n)[:-1]
                fake = adversary(n, points)
                require(all(fake.at(x) == 0 for x in points), "large deficient transcript")
                require(any(fake.quadratic), "large full-span counterfeit")
            count += 1
    return count


def check_controls() -> int:
    identity = (1, 2, 4)
    cases = (
        lambda: Phase(0, (), ()),
        lambda: Phase(4, (0,), ()),
        lambda: Phase(0, (True,), ()),
        lambda: Phase(0, (0, 0), (2,)),
        lambda: Phase(0, [0], ()),
        lambda: test_points(65),
        lambda: certify((1, 1), 0, lambda x: 0),
        lambda: certify(identity, 8, lambda x: 0),
        lambda: certify(identity, 0, lambda x: True),
        lambda: certify(identity, 0, lambda x: 4),
        lambda: certify(identity, 0, Phase(0, (1, 0, 0), (0, 0, 0)).at),
        lambda: certify(identity, 0, Phase(0, (0, 0, 0), (1, 0, 0)).at),
        lambda: adversary(3, test_points(3)),
        lambda: adversary(3, (8,)),
    )
    for case in cases:
        try:
            case()
        except ValueError:
            continue
        raise AssertionError("invalid-domain or nonmember control accepted")
    # The polynomial promise is indispensable: a cubic fools every weight-two test.
    require(certify(identity, 0, lambda x: 2 if x == 7 else 0) == (0, 0), "cubic control")
    return len(cases) + 1


def main() -> None:
    results = {
        "status": "PASS_AFFINE_TAG_QUERY_MINIMUM",
        "quadratic_phases_enumerated": check_small_phases(),
        "insufficient_query_subsets_enumerated": check_subsets(),
        "affine_constructions": check_constructions(),
        "controls": check_controls(),
        "nine_axis_queries": len(test_points(9)),
        "implementation_max_axes": MAX_AXES,
    }
    package = Path(__file__).resolve().parent
    names = ("README.md", "PROOF.md", "TASK.json", "SOURCES.json", "VERIFY.json", "verify.py")
    results["package_sha256"] = {
        name: sha256((package / name).read_bytes()).hexdigest() for name in names
    }
    print(json.dumps(results, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
