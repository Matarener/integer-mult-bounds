"""Host-integer specifications, independent of the Count-tape implementation.

The linear scan evaluates every geometrically legal borrowing in increasing
order. The second specification instead inverts the child-depth thresholds.
Neither imports the selector, its tape runtime, or its generated receipt.
Hiroki Kumazaki with substantial OpenAI Codex assistance. Apache-2.0.
"""

import itertools
import json
from hashlib import sha256


def require(condition, message):
    if not condition:
        raise ValueError(message)


def parameters(e, q, dimension, child_rank, row_factor, compatibility,
               numerator=0, denominator=1):
    values = (e, q, dimension, child_rank, row_factor, compatibility,
              numerator, denominator)
    require(all(type(value) is int for value in values), "integer parameters")
    require(e >= 1 and q >= 2 and 1 <= child_rank < dimension,
            "positive width, radix, and contracting depth")
    require(row_factor >= 1 and compatibility >= 1,
            "positive stock factors")
    require(denominator > 0 and 0 <= numerator <= denominator,
            "width exponent in [0,1]")
    width = 1
    target = e ** numerator
    while width ** denominator < target:
        width += 1
    group_order = 1
    for column in range(dimension):
        group_order *= q ** dimension - q ** column
    level = row_factor * group_order * q ** (dimension * dimension * (width - 1))
    return width, level


def depth(body, dimension, child_rank):
    result = 0
    while body >= dimension:
        body = child_rank * (body // dimension)
        result += 1
    return result


def plan_at(e, q, width, dimension, child_rank, level, compatibility, borrowed):
    body, remainder = divmod(e - borrowed, width)
    actual_depth = depth(body, dimension, child_rank)
    stock = 1 if actual_depth == 0 else compatibility * level ** actual_depth
    return dict(fits=2 * borrowed < e and body >= dimension and q ** borrowed >= stock,
                width=width, depth=actual_depth, stock=stock, rows=q ** borrowed,
                borrowed=borrowed, body=body, remainder=remainder)


def specification(e, q, dimension, child_rank, row_factor, compatibility,
                  numerator=0, denominator=1):
    """Return the first admitted plan or canonical fallback, by linear scan."""
    width, level = parameters(e, q, dimension, child_rank, row_factor,
                              compatibility, numerator, denominator)
    for borrowed in range((e - 1) // 2 + 1):
        candidate = plan_at(e, q, width, dimension, child_rank, level,
                            compatibility, borrowed)
        if candidate["fits"]:
            return candidate
    return fallback(width)


def fallback(width):
    return dict(fits=False, width=width, depth=0, stock=1, rows=1,
                borrowed=0, body=0, remainder=0)


def slab_specification(e, q, dimension, child_rank, row_factor, compatibility,
                       numerator=0, denominator=1):
    """Minimize inverse-depth intervals, with no forward depth recurrence."""
    width, level = parameters(e, q, dimension, child_rank, row_factor,
                              compatibility, numerator, denominator)
    threshold = dimension
    stock = compatibility
    exponent, rows, level_number = 0, 1, 0
    candidates = []
    while threshold <= e // width:
        level_number += 1
        stock *= level
        while rows < stock:
            exponent += 1
            rows *= q
        following = dimension * ((threshold + child_rank - 1) // child_rank)
        lower = max(0, exponent, e - width * following + 1)
        upper = min((e - 1) // 2, e - width * threshold)
        if lower <= upper:
            body, remainder = divmod(e - lower, width)
            candidates.append(dict(fits=True, width=width, depth=level_number,
                                   stock=stock, rows=q ** lower, borrowed=lower,
                                   body=body, remainder=remainder))
        threshold = following
    return min(candidates, key=lambda candidate: candidate["borrowed"]) if candidates else fallback(width)


def padded_guards(plan, q, dimension, row_factor, compatibility):
    """Check every literal child quotient and Q guard for a selected plan."""
    require(plan["fits"], "admitted plan")
    group_order = 1
    for i in range(dimension):
        group_order *= q ** dimension - q ** i
    level = row_factor * group_order * q ** (dimension ** 2 * (plan["width"] - 1))
    stock, genuine = plan["stock"], plan["rows"]
    padded = ((genuine + stock - 1) // stock) * stock
    require(genuine <= padded < 2 * genuine, "strict padding envelope")
    remaining = padded
    quotients = []
    for _ in range(plan["depth"]):
        remaining, residue = divmod(remaining, level)
        require(residue == 0, "complete local stock quotient")
        require(remaining % compatibility == 0, "compatibility guard")
        quotients.append(remaining)
    return dict(padded=padded, quotients=quotients)


def check():
    """Bounded arithmetic evidence; it is not an encoded runtime replay."""
    records = []
    accepted = 0
    for q, (dimension, child_rank), row_factor, compatibility, exponent in itertools.product(
            (2, 3), ((2, 1), (3, 1), (3, 2)), (1, 2), (1, 2, 5), ((0, 1), (1, 3))):
        for e in range(1, 81):
            args = (e, q, dimension, child_rank, row_factor, compatibility, *exponent)
            forward = specification(*args)
            inverse = slab_specification(*args)
            require(forward == inverse, "forward scan equals inverse-depth slabs")
            if forward["fits"]:
                padded_guards(forward, q, dimension, row_factor, compatibility)
                accepted += 1
            records.append([list(args), forward])
    serial = json.dumps(records, sort_keys=True, separators=(",", ":"))
    return dict(cases=len(records), accepted=accepted, rejected=len(records) - accepted,
                records_sha256=sha256(serial.encode()).hexdigest())


if __name__ == "__main__":
    print("PASS_INDEPENDENT_BODY_DEPTH", json.dumps(check(), sort_keys=True))
