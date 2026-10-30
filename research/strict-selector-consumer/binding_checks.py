"""Changed-boundary controls and nonpayload geometry observations."""

from unittest.mock import patch

import cardinality
import checks
import endpoints
import outer
import plan_geometry
import strict_call
import strict_selector
from binding_source import require
from cardinal_counts import Count
from check_runtime import Tracker
from check_support import no_decode
from count_ownership import audited_counts


def oracle(e, q, numerator, denominator):
    w = next(i for i in range(1, e + 1) if i**denominator >= e**numerator)
    level = (q * q - 1) * (q * q - q) * q ** (4 * (w - 1))
    for k in range(min((e - 1) // 2, e - 2 * w) + 1):
        n, ell = divmod(e - k, w)
        cursor, depth = n, 0
        for _ in range(e.bit_length()):
            if cursor < 2:
                break
            cursor //= 2
            depth += 1
        else:
            raise ValueError("bounded independent depth")
        stock = level**depth
        if 2 * q**k > stock:
            return dict(
                width=w,
                borrowed=k,
                body=n,
                remainder=ell,
                depth=depth,
                rows=q**k,
                stock=stock,
                fits=True,
            )
    return None


def observe(plan, shape, expected, q):
    # Read-only oracle observations never control the caller.
    require(expected is not None, "admitted independent plan")
    actual = {
        key: value if key == "fits" else checks.decode(value)
        for key, value in plan.items()
    }
    require(actual == expected, "all exact selected fields")
    require(
        checks.decode(shape.atoms) == expected["body"],
        "encoded body copied",
    )
    require(
        checks.decode(shape.ring.modulus) == q ** expected["width"],
        "encoded atom ring",
    )
    require(
        checks.decode(shape.high.modulus) == expected["rows"],
        "exact genuine high field",
    )
    residual = q ** expected["remainder"]
    require(
        (shape.remainder is None) == (residual == 1),
        "zero residual omission",
    )
    if shape.remainder is not None:
        require(
            checks.decode(shape.remainder.modulus) == residual,
            "encoded residual ring",
        )
    require(
        checks.decode(shape.gap) == residual * 2 * expected["rows"],
        "genuine spectator gap",
    )
    require(
        checks.decode(shape.suffix) == residual * 2,
        "complete residual suffix",
    )
    return actual


def geometries():
    cases = (
        (5, 2, 0, 1),
        (13, 2, 1, 8),
        (28, 2, 1, 8),
        (29, 2, 1, 8),
        (21, 3, 0, 1),
        (45, 3, 1, 8),
        (47, 3, 1, 8),
    )
    rows = []
    with audited_counts(cardinality.Tape) as observation:
        for e, q, numerator, denominator in cases:
            original, z, t = (Count.literal(value) for value in (e, 2, 2))
            plan = None
            try:
                with no_decode():
                    plan = strict_selector.select(
                        original,
                        q,
                        strict_selector.Profile(numerator, denominator, 2, 1, 1),
                        1,
                    )
                    snapshots = {
                        key: bytes(value.tape.cells)
                        for key, value in plan.items()
                        if key != "fits"
                    }
                    with plan_geometry.fitted(plan, q, z, t) as shape:
                        actual = observe(
                            plan, shape, oracle(e, q, numerator, denominator), q
                        )
                    require(
                        all(
                            bytes(plan[key].tape.cells) == raw
                            and plan[key].tape.head == 1
                            for key, raw in snapshots.items()
                        ),
                        "geometry preserves every plan Count",
                    )
                rows.append(dict(original=e, q=q, **actual))
            finally:
                if plan is not None:
                    strict_selector.close_plan(plan)
                for value in (original, z, t):
                    value.close()
    return dict(cases=rows, count_ownership=observation)


def fallback_endpoint(result, volume, extent, z, t):
    for address in range(volume):
        rest, tail = divmod(address, t)
        rest, d = divmod(rest, extent)
        rest, spectator = divmod(rest, z)
        prefix, h = divmod(rest, extent)
        target = (((prefix * extent + d) * z + spectator) * extent + h) * t + tail
        require(result.origins.get(target + 1) == 1 << address, "full no-fit endpoint")


def fallback(e, p, z, t):
    profile = strict_selector.Profile(0, 1, 2, 1, 1)
    require(oracle(e, 2, 0, 1) is None, "independent no-fit")
    tracker, meter = Tracker(), dict(callee=False, ADD=0, sign=0, chunk_swap=0)
    extent = 2**e
    volume = p * extent * z * extent * t
    source = tracker.source(volume)
    saved = bytes(source.cells)
    counts = tuple(Count.literal(value) for value in (e, p, z, t))
    snapshots = [bytes(value.tape.cells) for value in counts]
    result = None

    def forbidden(_shape):
        raise ValueError("no-fit must never construct a callee")

    try:
        with (
            checks.observed(tracker, meter),
            audited_counts(cardinality.Tape) as observation,
        ):
            result = strict_call.run(
                source, counts[0], 2, *counts[1:], forbidden, profile
            )
        fallback_endpoint(result, volume, extent, z, t)
        require(
            bytes(source.cells) == saved and source.head == result.head == 1,
            "no-fit borrowed source",
        )
        require(
            all(
                bytes(value.tape.cells) == raw and value.tape.head == 1
                for value, raw in zip(counts, snapshots, strict=True)
            ),
            "no-fit borrowed Counts",
        )
        require(tracker.live == {source, result}, "no-fit payload cleanup")
        require(
            meter == dict(callee=False, ADD=0, sign=0, chunk_swap=1),
            "one complete fallback swap",
        )
        return dict(
            original=e,
            prefixes=p,
            spectators=z,
            suffix=t,
            columns=volume,
            count_ownership=observation,
        )
    finally:
        if result is not None:
            result.clear()
        source.clear()
        for value in counts:
            value.close()
        require(not tracker.live, "fallback final teardown")


def controls():
    with patch.object(strict_call.strict_outer, "interchange", outer.interchange):
        try:
            endpoints.one()
        except ValueError as error:
            require(
                "row capacity must cover at least one stock group" in str(error),
                "old covering contract rejects strict plan",
            )
        else:
            raise ValueError("old covering consumer unexpectedly admitted R<S")
    failures = [endpoints.one(fail_at=call) for call in (1, 2)]
    return dict(old_covering_rejected=True, callee_failures=failures)
