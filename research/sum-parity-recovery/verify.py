"""Bounded exact corroboration of PROOF.md; writes nothing.

Produced by Nick Petalas. Apache-2.0. Standard library only.
"""

from fractions import Fraction as F
from hashlib import sha256
from itertools import combinations, product
from pathlib import Path
import json
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from recovery import decode, require, sketch

HERE = Path(__file__).resolve().parent
PACKAGE_FILES = ("README.md", "PROOF.md", "TASK.json", "SOURCES.json",
                 "VERIFY.json", "recovery.py", "verify.py")


def row_spaces(dimension):
    """Every reduced binary row space once; used only for 2 <= N <= 6."""
    require(2 <= dimension <= 6, "Exhaustive dimension outside 2..6")
    for rank in range(dimension + 1):
        for pivots in combinations(range(dimension), rank):
            free = [(i, j) for i, pivot in enumerate(pivots)
                    for j in range(pivot + 1, dimension) if j not in pivots]
            for assignment in range(1 << len(free)):
                rows = [1 << pivot for pivot in pivots]
                for bit, (i, j) in enumerate(free):
                    rows[i] |= ((assignment >> bit) & 1) << j
                yield tuple(rows)


def subspace_count(dimension):
    answer = 0
    for rank in range(dimension + 1):
        numerator = denominator = 1
        for i in range(rank):
            numerator *= (1 << dimension) - (1 << i)
            denominator *= (1 << rank) - (1 << i)
        require(numerator % denominator == 0, "Gaussian binomial integrality")
        answer += numerator // denominator
    return answer


def span_is_full(rows, dimension):
    """Independent bounded span enumeration, without decoder elimination."""
    span = {0}
    for row in [*rows, (1 << dimension) - 1]:
        span |= {x ^ row for x in tuple(span)}
    return len(span) == 1 << dimension


def boolean_collision(rows, dimension):
    """Direct observation oracle on every binary vector and its exact sum."""
    seen = {}
    for mask in range(1 << dimension):
        values = tuple((mask >> i) & 1 for i in range(dimension))
        key = (sum(values), sketch(values, rows))
        if key in seen:
            return seen[key], values
        seen[key] = values
    return None


def exhaustive_sketches():
    census = []
    failed = admitted = collision_checks = decoder_checks = 0
    for dimension in range(2, 7):
        spaces = list(row_spaces(dimension))
        require(len(set(spaces)) == len(spaces) == subspace_count(dimension),
                "Complete distinct row-space inventory")
        census.append([dimension, len(spaces)])
        for rows in spaces:
            full = span_is_full(rows, dimension)
            collision = boolean_collision(rows, dimension)
            require(full == (collision is None), "Rank criterion versus direct oracle")
            if collision is not None:
                left, right = collision
                midpoint = tuple(F(a + b, 2) for a, b in zip(left, right))
                require(left != right and sum(left) == sum(right), "Distinct equal sums")
                require(sketch(left, rows) == sketch(right, rows), "Equal sketches")
                require(all(abs(y - a) <= F(1, 2) and abs(y - b) <= F(1, 2)
                            for y, a, b in zip(midpoint, left, right)),
                        "Actual half-unit ambiguity")
                failed += 1
                collision_checks += 1
                continue
            admitted += 1
            for mask in range(1 << dimension):
                values = tuple(((mask >> i) & 1) * 7 - 3 for i in range(dimension))
                for radius in (F(1, 2), F(999, 1000)):
                    noise = tuple(radius * (-1 if (mask >> i) & 1 else 1)
                                  for i in range(dimension))
                    observed = tuple(a + e for a, e in zip(values, noise))
                    require(decode(observed, rows, sketch(values, rows),
                                   sum(values), radius) == values,
                            "Constructive decoder at closed error boundary")
                    decoder_checks += 1
    return dict(row_spaces=census, admitted_sketches=admitted,
                excluded_sketches=failed, explicit_ambiguities=collision_checks,
                boundary_decodes=decoder_checks)


def expect_rejection(call, phrase):
    try:
        call()
    except ValueError as error:
        require(phrase in str(error), "Rejection had an unexpected cause")
    else:
        raise ValueError("Invalid contract accepted: " + phrase)


def boundary_controls():
    low_noise = 0
    for dimension in range(2, 7):
        for values in product((-1, 0, 1), repeat=dimension):
            observed = tuple(F(x) + F(499, 1000) * (-1 if i & 1 else 1)
                             for i, x in enumerate(values))
            require(decode(observed, (), (), sum(values), F(499, 1000)) == values,
                    "Sub-half-unit recovery with no sketch")
            low_noise += 1
    omissions = 0
    for dimension in range(2, 13):
        optimal = tuple(1 << i for i in range(dimension - 1))
        require(span_is_full(optimal, dimension), "N-1 attaining construction")
        for removed in range(dimension - 1):
            rows = optimal[:removed] + optimal[removed + 1:]
            left = tuple(int(i == removed) for i in range(dimension))
            right = tuple(int(i == dimension - 1) for i in range(dimension))
            require(sketch(left, rows) == sketch(right, rows), "Omitted check ambiguity")
            observed = tuple(F(a + b, 2) for a, b in zip(left, right))
            expect_rejection(lambda: decode(observed, rows, sketch(left, rows),
                                            1, F(1, 2)), "determine all parities")
            omissions += 1
    unit_ambiguities = 0
    for dimension in range(2, 65):
        left = (0, 2) + (0,) * (dimension - 2)
        right = (2, 0) + (0,) * (dimension - 2)
        rows = tuple(1 << i for i in range(dimension))
        require(sum(left) == sum(right) and sketch(left, rows) == sketch(right, rows),
                "Radius-one ambiguity")
        require(max(abs(F(a + b, 2) - a) for a, b in zip(left, right)) == 1,
                "Exact unit error")
        unit_ambiguities += 1
    return dict(sub_half_decodes=low_noise, indispensable_check_controls=omissions,
                unit_radius_ambiguities=unit_ambiguities)


def invalid_controls():
    valid = dict(observations=(F(1, 2), F(1, 2)), rows=(1,), tags=(0,), total=1, radius=F(1, 2))
    controls = [
        ({"observations": (F(0),)}, "Dimension"),
        ({"observations": (F(0),) * 65}, "Dimension"),
        ({"rows": (1,) * 65, "tags": (0,) * 65}, "Sketch size"),
        ({"tags": ()}, "Sketch size"), ({"tags": (True,)}, "Tags"),
        ({"tags": (2,)}, "Tags"), ({"rows": (-1,)}, "Row outside"),
        ({"rows": (4,)}, "Row outside"), ({"rows": (True,)}, "must be an integer"),
        ({"radius": 1}, "Radius outside"), ({"radius": F(-1)}, "Radius outside"),
        ({"radius": 0.5}, "must be exact"), ({"total": True}, "must be an integer"),
        ({"total": 1 << 4096}, "bit limit"),
        ({"observations": (0.5, F(1, 2))}, "must be exact"),
        ({"observations": (F(1, 1 << 4096), F(0))}, "bit limit"),
        ({"observations": (F(0), F(0)), "total": 2, "radius": F(0)}, "sum disagrees"),
        ({"observations": (F(0), F(0)), "total": 0, "tags": (1,), "radius": F(0)}, "sketch disagrees"),
        ({"observations": (F(1, 2), F(1, 2)), "radius": F(0)}, "radius promise"),
        ({"rows": (1, 1), "tags": (0, 1)}, "Inconsistent parity"),
    ]
    for changes, phrase in controls:
        arguments = dict(valid, **changes)
        expect_rejection(lambda: decode(**arguments), phrase)
    huge = (1 << 4000, -(1 << 4000) + 1)
    require(decode(tuple(F(x) + F(3, 4) for x in huge), (1,), (0,), 1, F(3, 4)) == huge,
            "Large signed integer fixture")
    return dict(invalid_contract_rejections=len(controls), large_integer_decodes=1)


def main():
    require(len(sys.argv) == 1, "No command-line options are supported")
    result = dict(schema="sum-parity-recovery/1", claim_type="scoped proof with finite corroboration")
    result.update(exhaustive_sketches())
    result.update(boundary_controls())
    result.update(invalid_controls())
    result["package_sha256"] = {name: sha256((HERE / name).read_bytes()).hexdigest()
                                for name in PACKAGE_FILES}
    print(json.dumps(result, indent=2, sort_keys=True))
    print("PASS_SUM_PARITY_RECOVERY")


if __name__ == "__main__":
    main()
