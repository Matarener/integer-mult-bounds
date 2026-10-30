# SPDX-License-Identifier: Apache-2.0
"""Exact least strict-volume borrowing on literal Count tapes.

Nick Petalas. Uses PR3518's Count arithmetic and saturation, Hiroki Kumazaki's
PR3502 selection, Jose Manuel's PR2899 arithmetic and PR3503 strict padding.
"""

from contextlib import contextmanager

import count_math as encoded
from cardinal_counts import Count, positive
from selector import Owned, Profile, bounds, close_plan, make_level, no_fit, power
from words import need

# Public release operation is inherited unchanged.
__all__ = ["Profile", "select", "close_plan"]


def strict_threshold(stock):
    positive(stock)
    threshold = Count(stock)
    threshold.divide_small(2)
    threshold.increment()
    return threshold


@contextmanager
def trial(original, width, borrowed, dimension, level, radix, profile, compatibility):
    with Owned() as work:
        remaining = work.put("remaining", encoded.subtract(original, borrowed))
        body, remainder = encoded.divide(remaining, width)
        work.put("body", body)
        work.put("remainder", remainder)
        work.drop("remaining")
        cursor = work.put("cursor", Count(body))
        depth = work.put("depth", Count.literal(0))
        # Each step contracts by at least profile.child_rank/profile.dimension.
        while encoded.compare(cursor, dimension) >= 0:
            cursor.divide_small(profile.dimension)
            if profile.child_rank != 1:
                cursor.multiply_small(profile.child_rank)
            depth.increment()
        work.drop("cursor")
        stock = work.put("stock", power(level, depth))
        if not depth.zero() and compatibility != 1:
            stock.multiply_small(compatibility)
        threshold = work.put("threshold", strict_threshold(stock))
        work.put("rows", power(radix, borrowed, threshold))
        yield work


def fits(candidate):
    return encoded.compare(candidate.get("rows"), candidate.get("threshold")) == 0


def materialize(work, candidate, borrowed_name):
    candidate.replace("rows", power(work.get("radix"), work.get(borrowed_name)))
    need(
        encoded.compare(candidate.get("rows"), candidate.get("threshold")) >= 0,
        "exact strict-volume final rows",
    )
    result = {
        name: candidate.take(name)
        for name in ("depth", "stock", "rows", "body", "remainder")
    }
    result["width"] = work.take("width")
    result["borrowed"] = work.take(borrowed_name)
    result["fits"] = True
    return result


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
    # False lower and true upper; the positive gap halves on each iteration.
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
        need(fits(current), "admitted capped final strict trial")
        return materialize(work, current, "upper")


def select(original, q, profile=None, compatibility=9475):
    """Return seven owned Counts and fits; no input-dependent integer decoding.

    Admission is 2*q**k > S_D(floor((e-k)/w)), 2*k<e and body>=m.
    This changes the covering contract. It installs no ordinary callback.
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
