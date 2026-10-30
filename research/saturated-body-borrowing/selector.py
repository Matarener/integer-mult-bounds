# SPDX-License-Identifier: Apache-2.0
"""Covering-constrained borrowing with stock-capped trial radix powers.

Nick Petalas. Count setup follows Hiroki Kumazaki's PR3502 and Jose Manuel's
PR2899 arithmetic. The new cap and final-size argument are in PROOF.md.
"""

from contextlib import contextmanager
from dataclasses import dataclass

import count_math as encoded
from cardinal_counts import Count, positive
from words import LEFT, ONE, ZERO, need


@dataclass(frozen=True)
class Profile:
    numerator: int = 17
    denominator: int = 10000
    dimension: int = 64
    child_rank: int = 42
    row_factor: int = 28416


class Owned:
    """A fixed inventory of named roles; each loop replaces its existing slot."""

    def __init__(self):
        self.values = {}

    def put(self, name, value):
        need(name not in self.values, "unused setup role")
        self.values[name] = value
        return value

    def replace(self, name, value):
        self.drop(name)
        return self.put(name, value)

    def get(self, name):
        return self.values[name]

    def take(self, name):
        return self.values.pop(name)

    def drop(self, name):
        self.take(name).close()

    def __enter__(self):
        return self

    def __exit__(self, *_exception):
        for value in self.values.values():
            value.close()
        self.values.clear()


def capped_product(left, right, cap):
    """Positive operands and cap; raw product has at most twice cap's length."""
    if encoded.compare(left, cap) >= 0 or encoded.compare(right, cap) >= 0:
        return Count(cap)
    result = Count.product(left, right)
    if encoded.compare(result, cap) > 0:
        result.close()
        return Count(cap)
    return result


def power(base, exponent, cap=None):
    """Return base**exponent, or min(base**exponent,cap), preserving inputs.

    base and cap are positive canonical Counts; exponent is nonnegative.
    Every exponent-dependent branch reads its tape. No value is decoded.
    """
    positive(base)
    need(
        isinstance(exponent, Count) and exponent.tape is not base.tape,
        "distinct canonical exponent tape",
    )
    if cap is not None:
        positive(cap)
        need(exponent.tape is not cap.tape, "cap distinct from exponent")
    with Owned() as work:
        work.put("value", Count.literal(1))
        exponent.msb()
        try:
            while exponent.read() != LEFT:
                bit = exponent.read()
                need(bit in (ZERO, ONE), "binary setup exponent")
                value = work.get("value")
                following = (
                    Count.product(value, value)
                    if cap is None
                    else capped_product(value, value, cap)
                )
                work.replace("value", following)
                if bit == ONE:
                    value = work.get("value")
                    following = (
                        Count.product(value, base)
                        if cap is None
                        else capped_product(value, base, cap)
                    )
                    work.replace("value", following)
                exponent.step(-1)
            return work.take("value")
        finally:
            if exponent.read() == LEFT:
                exponent.step(1)
            exponent.rewind()


@contextmanager
def trial(original, width, borrowed, dimension, level, radix, profile, compatibility):
    """Exact stock and geometry; rows is only min(q**k,stock) until accepted."""
    with Owned() as work:
        remaining = work.put("remaining", encoded.subtract(original, borrowed))
        body, remainder = encoded.divide(remaining, width)
        work.put("body", body)
        work.put("remainder", remainder)
        work.drop("remaining")
        cursor = work.put("cursor", Count(body))
        depth = work.put("depth", Count.literal(0))
        while encoded.compare(cursor, dimension) >= 0:
            cursor.divide_small(profile.dimension)
            if profile.child_rank != 1:
                cursor.multiply_small(profile.child_rank)
            depth.increment()
        work.drop("cursor")
        stock = work.put("stock", power(level, depth))
        if not depth.zero() and compatibility != 1:
            stock.multiply_small(compatibility)
        work.put("rows", power(radix, borrowed, stock))
        yield work


def fits(candidate):
    return encoded.compare(candidate.get("rows"), candidate.get("stock")) == 0


def no_fit(work):
    result = {}
    for name in ("depth", "borrowed", "body", "remainder"):
        result[name] = work.put("fallback_" + name, Count.literal(0))
    for name in ("stock", "rows"):
        result[name] = work.put("fallback_" + name, Count.literal(1))
    for name in result:
        work.take("fallback_" + name)
    result["width"] = work.take("width")
    result["fits"] = False
    return result


def materialize(work, candidate, borrowed_name):
    """The successful minimum has O(w log(e))-bit exact q**k; prove before use."""
    candidate.replace("rows", power(work.get("radix"), work.get(borrowed_name)))
    need(
        encoded.compare(candidate.get("rows"), candidate.get("stock")) >= 0,
        "exact admitted final rows",
    )
    result = {
        name: candidate.take(name)
        for name in ("depth", "stock", "rows", "body", "remainder")
    }
    result["width"] = work.take("width")
    result["borrowed"] = work.take(borrowed_name)
    result["fits"] = True
    return result


def bounds(work, original, profile):
    work.put("dimension", Count.literal(profile.dimension))
    one = work.put("one", Count.literal(1))
    minimum = work.put("minimum", Count(work.get("width")))
    minimum.multiply_small(profile.dimension)
    if encoded.compare(original, minimum) < 0:
        return False
    strict = work.put("strict", encoded.subtract(original, one))
    strict.divide_small(2)
    body_limit = work.put("body_limit", encoded.subtract(original, minimum))
    work.drop("minimum")
    chosen, other = (
        ("strict", "body_limit")
        if encoded.compare(strict, body_limit) <= 0
        else ("body_limit", "strict")
    )
    work.put("upper", work.take(chosen))
    work.drop(other)
    work.put("lower", Count.literal(0))
    return True


def make_level(work, q, profile):
    order = 1
    for position in range(profile.dimension):
        order *= q**profile.dimension - q**position
    atom = work.put("atom", Count.literal(q ** (profile.dimension**2)))
    exponent = work.put(
        "exponent", encoded.subtract(work.get("width"), work.get("one"))
    )
    level = work.put("level", power(atom, exponent))
    level.multiply_small(profile.row_factor * order)
    work.drop("atom")
    work.drop("exponent")
    work.put("radix", Count.literal(q))


def search(original, work, profile, compatibility):
    arguments = (
        original,
        work.get("width"),
        work.get("dimension"),
        work.get("level"),
        work.get("radix"),
        profile,
        compatibility,
    )

    def candidate(borrowed):
        return trial(arguments[0], arguments[1], borrowed, *arguments[2:])

    with candidate(work.get("lower")) as current:
        if fits(current):
            return materialize(work, current, "lower")
    with candidate(work.get("upper")) as current:
        if not fits(current):
            return no_fit(work)
    # P(lower) is false, P(upper) true. The gap halves each iteration.
    while True:
        gap = work.put("gap", encoded.subtract(work.get("upper"), work.get("lower")))
        adjacent = encoded.compare(gap, work.get("one")) == 0
        work.drop("gap")
        if adjacent:
            break
        middle = work.put("middle", Count(work.get("lower")))
        middle.add(work.get("upper"))
        middle.divide_small(2)
        with candidate(middle) as current:
            destination = "upper" if fits(current) else "lower"
        work.replace(destination, work.take("middle"))
    with candidate(work.get("upper")) as current:
        need(fits(current), "admitted capped final trial")
        return materialize(work, current, "upper")


def select(original, q, profile=None, compatibility=9475):
    """Return seven owned plan Counts and a Boolean fit flag.

    The covering contract remains q**k>=S_D(floor((e-k)/w)), 2*k<e and
    floor((e-k)/w)>=m. Only rejected-trial representation changes.
    """
    if profile is None:
        profile = Profile()
    need(type(q) is int and q >= 2, "compiled radix at least two")
    need(
        type(compatibility) is int and compatibility >= 1,
        "positive compiled compatibility",
    )
    need(isinstance(profile, Profile), "compiled selector profile")
    fields = (
        profile.row_factor,
        profile.dimension,
        profile.child_rank,
        profile.numerator,
        profile.denominator,
    )
    need(all(type(value) is int for value in fields), "integer compiled profile")
    need(
        profile.row_factor >= 1 and 1 <= profile.child_rank < profile.dimension,
        "positive contracting compiled profile",
    )
    need(
        profile.denominator > 0 and 0 <= profile.numerator <= profile.denominator,
        "compiled width exponent between zero and one",
    )
    positive(original)
    with Owned() as work:
        work.put(
            "width",
            encoded.atom_width(original, profile.numerator, profile.denominator),
        )
        if not bounds(work, original, profile):
            return no_fit(work)
        make_level(work, q, profile)
        return search(original, work, profile, compatibility)


def close_plan(plan):
    for key, value in plan.items():
        if key != "fits":
            value.close()
