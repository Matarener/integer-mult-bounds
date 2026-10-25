# SPDX-License-Identifier: Apache-2.0
"""Actual-body borrowing on the retained fixed-role Count-tape vocabulary.

Hiroki Kumazaki, with substantial OpenAI Codex assistance.
The threshold theorem is Nick Petalas's PR3486; Count arithmetic and the
ordinary consumer are the credited PR2899/3264 predecessor interfaces.
"""

from contextlib import contextmanager

import encoded
from cardinal_counts import Count, positive
from words import LEFT, ONE, ZERO, need


class _Owned:
    """Ownership bookkeeping for a fixed set of literal operand names.

    The dictionary is host bookkeeping, not an integer tape or a data table.
    Every call site uses a fixed name; loop iterations replace those slots.
    """

    def __init__(self):
        self.values = {}

    def put(self, name, value):
        need(name not in self.values, "unused setup operand role")
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
        while self.values:
            self.values.popitem()[1].close()


def _power(base, exponent):
    """Encoded nonnegative exponent, scanned MSB first; preserve both inputs."""
    with _Owned() as work:
        work.put("value", Count.literal(1))
        exponent.msb()
        try:
            while exponent.read() != LEFT:
                bit = exponent.read()
                need(bit in (ZERO, ONE), "binary setup exponent")
                value = work.get("value")
                work.replace("value", Count.product(value, value))
                if bit == ONE:
                    work.replace("value", Count.product(work.get("value"), base))
                exponent.step(-1)
            return work.take("value")
        finally:
            if exponent.read() == LEFT:
                exponent.step(1)
            exponent.rewind()


@contextmanager
def _trial(original, width, borrowed, dimension, level, radix, profile,
           compatibility):
    """Compute the complete trial plan from the candidate borrowing tape."""
    with _Owned() as work:
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
        stock = work.put("stock", _power(level, depth))
        if not depth.zero() and compatibility != 1:
            stock.multiply_small(compatibility)
        work.put("rows", _power(radix, borrowed))
        yield work


def _fits(trial):
    return encoded.compare(trial.get("rows"), trial.get("stock")) >= 0


def _plan(work, trial, borrowed_name):
    """Transfer owned results out of the two bounded temporary scopes."""
    result = {name: trial.take(name)
              for name in ("depth", "stock", "rows", "body", "remainder")}
    result["width"] = work.take("width")
    result["borrowed"] = work.take(borrowed_name)
    result["fits"] = True
    return result


def _no_fit(work):
    """Return a documented nonadmitted sentinel, never stale trial fields."""
    for name in ("depth", "borrowed", "body", "remainder"):
        work.put("fallback_" + name, Count.literal(0))
    for name in ("stock", "rows"):
        work.put("fallback_" + name, Count.literal(1))
    result = {name: work.take("fallback_" + name)
              for name in ("depth", "borrowed", "body", "remainder", "stock", "rows")}
    result["width"] = work.take("width")
    result["fits"] = False
    return result


def select_body_stock(original, q, profile=encoded.Profile(row_factor=28416),
                      compatibility=9475):
    """Return the least admitted actual-body borrowing, using Count tapes.

    The radix and profile are compiled constants. The caller retains
    ``original`` and owns every returned Count. Successful plans satisfy
    2*k<e, n=floor((e-k)/w)>=m and q**k>=Q*b**D(n), with fixed
    w=ceil(e**(numerator/denominator)) and
    b=W*|GL_m(F_q)|*q**(m*m*(w-1)).

    A no-fit plan has the true width, zero depth/borrowed/body/remainder and
    unit stock/rows. Its fields are a sentinel, not an admitted invocation.
    This function does not change a backend callback or execute a payload.
    """
    need(type(q) is int and q >= 2, "compiled radix at least two")
    need(type(compatibility) is int and compatibility >= 1,
         "positive compiled compatibility factor")
    need(type(profile.row_factor) is int and profile.row_factor >= 1,
         "positive compiled live-family factor")
    need(type(profile.dimension) is int and type(profile.child_rank) is int
         and 1 <= profile.child_rank < profile.dimension,
         "contracting compiled depth profile")
    need(type(profile.numerator) is int and type(profile.denominator) is int
         and profile.denominator > 0
         and 0 <= profile.numerator <= profile.denominator,
         "compiled width exponent between zero and one")
    positive(original)
    with _Owned() as work:
        width = work.put("width", encoded.atom_width(
            original, profile.numerator, profile.denominator))
        dimension = work.put("dimension", Count.literal(profile.dimension))
        one = work.put("one", Count.literal(1))
        minimum_body = work.put("minimum_body", Count(width))
        minimum_body.multiply_small(profile.dimension)
        if encoded.compare(original, minimum_body) < 0:
            return _no_fit(work)

        strict = work.put("strict", encoded.subtract(original, one))
        strict.divide_small(2)
        body_limit = work.put("body_limit", encoded.subtract(original, minimum_body))
        work.drop("minimum_body")
        if encoded.compare(strict, body_limit) <= 0:
            work.put("upper", work.take("strict"))
            work.drop("body_limit")
        else:
            work.put("upper", work.take("body_limit"))
            work.drop("strict")

        # Only compiled source constants use host arithmetic. Width-dependent
        # high-field multiplicities and every trial reserve remain encoded.
        order = 1
        for position in range(profile.dimension):
            order *= q ** profile.dimension - q ** position
        atom = work.put("atom", Count.literal(q ** (profile.dimension ** 2)))
        exponent = work.put("exponent", encoded.subtract(width, one))
        level = work.put("level", _power(atom, exponent))
        level.multiply_small(profile.row_factor * order)
        work.drop("atom")
        work.drop("exponent")
        radix = work.put("radix", Count.literal(q))
        work.put("lower", Count.literal(0))

        with _trial(original, width, work.get("lower"), dimension, level, radix,
                    profile, compatibility) as trial:
            if _fits(trial):
                return _plan(work, trial, "lower")
        with _trial(original, width, work.get("upper"), dimension, level, radix,
                    profile, compatibility) as trial:
            if not _fits(trial):
                return _no_fit(work)

        # The lower endpoint is false and the upper endpoint is true. A
        # nonnegative encoded interval avoids a negative sentinel tape.
        while True:
            gap = work.put("gap", encoded.subtract(work.get("upper"), work.get("lower")))
            adjacent = encoded.compare(gap, one) == 0
            work.drop("gap")
            if adjacent:
                break
            middle = work.put("middle", Count(work.get("lower")))
            middle.add(work.get("upper"))
            middle.divide_small(2)
            with _trial(original, width, middle, dimension, level, radix,
                        profile, compatibility) as trial:
                destination = "upper" if _fits(trial) else "lower"
            work.replace(destination, work.take("middle"))

        with _trial(original, width, work.get("upper"), dimension, level, radix,
                    profile, compatibility) as trial:
            need(_fits(trial), "admitted final stock")
            return _plan(work, trial, "upper")


def close_plan(plan):
    """Release all seven owned Count results, including no-fit sentinels."""
    for key, value in plan.items():
        if key != "fits":
            value.close()
