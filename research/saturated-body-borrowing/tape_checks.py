# SPDX-License-Identifier: Apache-2.0
"""Literal Count execution versus direct arithmetic, with ownership checks."""

import json
from contextlib import contextmanager
from hashlib import sha256
from unittest.mock import patch

import science
from runtime import require


def serial(plan, inspect_count):
    return {
        key: value if key == "fits" else inspect_count(value)
        for key, value in plan.items()
    }


@contextmanager
def audited_counts():
    """Observe actual runtime tape allocation, writes, erasure and maximum extent."""
    import cardinality
    import counts
    from records import Tape
    from words import BLANK

    live = set()
    observed = dict(peak_roles=0, maximum_cells=0)

    class Audited(Tape):
        def __init__(self):
            super().__init__()
            live.add(self)
            observed["peak_roles"] = max(observed["peak_roles"], len(live))

        def write(self, value):
            super().write(value)
            observed["maximum_cells"] = max(observed["maximum_cells"], len(self.cells))

        def clear(self):
            super().clear()
            require(
                self.head == 1 and all(value == BLANK for value in self.cells[1:]),
                "closed Count tape erased",
            )
            live.discard(self)

    with (
        patch.object(counts, "Tape", Audited),
        patch.object(cardinality, "Tape", Audited),
    ):
        yield observed, live
    require(not live, "all Count roles released")


def powers():
    import selector
    from cardinal_counts import Count
    from check_support import inspect_count, no_decode

    digest = sha256()
    total = 0
    with audited_counts() as (observed, live):
        for base in (1, 2, 3, 7):
            for exponent in (0, 1, 2, 3, 8, 31):
                for cap in (1, 2, 5, 16, 65):
                    inputs = [Count.literal(x) for x in (base, exponent, cap)]
                    before = [bytes(x.tape.cells) for x in inputs]
                    try:
                        with no_decode():
                            output = selector.power(*inputs)
                        expected = min(base**exponent, cap)
                        require(inspect_count(output) == expected, "exact capped power")
                        require(
                            all(x.tape.head == 1 for x in inputs),
                            "borrowed power heads",
                        )
                        require(
                            [bytes(x.tape.cells) for x in inputs] == before,
                            "borrowed power values",
                        )
                        output.close()
                        require(len(live) == 3, "only three borrowed power roles")
                        digest.update(f"{base},{exponent},{cap}:{expected};".encode())
                        total += 1
                    finally:
                        for value in inputs:
                            value.close()
    return dict(cases=total, sha256=digest.hexdigest(), **observed)


def plans():
    import selector
    from cardinal_counts import Count
    from check_support import inspect_count, no_decode

    digest, total, fitted = sha256(), 0, 0
    with audited_counts() as (observed, live):
        for values in science.cases():
            e, q, m, r, factor, compatibility, numerator, denominator = values
            # The complete integer census covers all 1536 cases. Literal
            # coverage uses every fourth width plus all small/boundary widths.
            if e > 16 and e % 4 != 0 and e not in (23, 25):
                continue
            profile = selector.Profile(numerator, denominator, m, r, factor)
            original = Count.literal(e)
            before = bytes(original.tape.cells)
            try:
                with no_decode():
                    plan = selector.select(original, q, profile, compatibility)
                actual = serial(plan, inspect_count)
                expected = science.oracle(*values)
                require(actual == expected, "complete least-borrowing plan")
                require(
                    bytes(original.tape.cells) == before and original.tape.head == 1,
                    "borrowed original preserved",
                )
                selector.close_plan(plan)
                require(len(live) == 1, "only borrowed original remains")
                digest.update(json.dumps([values, actual], sort_keys=True).encode())
                total += 1
                fitted += actual["fits"]
            finally:
                original.close()
    return dict(cases=total, fitted=fitted, sha256=digest.hexdigest(), **observed)


def large_trial():
    """A genuinely oversized candidate exponent, observed through actual tapes."""
    import selector
    from cardinal_counts import Count
    from check_support import inspect_count, no_decode

    with audited_counts() as (observed, live):
        base, exponent, cap = (Count.literal(v) for v in (2, 1000000, 97))
        try:
            with no_decode():
                output = selector.power(base, exponent, cap)
            require(inspect_count(output) == 97, "large exponent saturates exactly")
            output.close()
            require(len(live) == 3, "large trial temporary cleanup")
        finally:
            for value in (base, exponent, cap):
                value.close()
    require(observed["maximum_cells"] <= 24, "bounded literal capped intermediate")
    return dict(
        base=2,
        exponent=1000000,
        cap=97,
        uncapped_power_bits=1000001,
        capped_power_bits=7,
        **observed,
    )


def large_plan():
    import selector
    from cardinal_counts import Count
    from check_support import inspect_count, no_decode

    e = 1000000
    with audited_counts() as (observed, live):
        original = Count.literal(e)
        try:
            with no_decode():
                plan = selector.select(original, 2, selector.Profile(0, 1, 2, 1, 1), 1)
            actual = serial(plan, inspect_count)
            # Compute the oracle by threshold candidates, not a million
            # exhaustive large powers. k <= ceil(log2(initial_stock)).
            initial_stock = 6 ** science.depth(e, 2, 1)
            limit = (initial_stock - 1).bit_length()
            answers = []
            for k in range(limit + 1):
                stock = 6 ** science.depth(e - k, 2, 1)
                if 2**k >= stock:
                    answers.append((k, stock))
            require(
                answers
                and actual["borrowed"] == answers[0][0]
                and actual["stock"] == answers[0][1]
                and actual["rows"] == 2 ** actual["borrowed"],
                "large least plan and exact final radix materialization",
            )
            require(actual["rows"] < 2 * initial_stock, "final-size theorem witness")
            selector.close_plan(plan)
            require(len(live) == 1, "large plan temporary cleanup")
        finally:
            original.close()
    require(observed["maximum_cells"] <= 104, "full selector capped intermediate bound")
    return dict(
        original=e,
        borrowed=actual["borrowed"],
        depth=actual["depth"],
        final_rows=str(actual["rows"]),
        final_stock=str(actual["stock"]),
        uncapped_upper_trial_power_bits=(e - 1) // 2 + 1,
        **observed,
    )


def rejections():
    import selector
    from cardinal_counts import Count
    from check_support import no_decode

    total = 0
    with audited_counts() as (observed, live):
        original, base, exponent, zero = (Count.literal(v) for v in (24, 2, 3, 0))
        try:
            bad = (
                (lambda: selector.power(base, exponent, zero)),
                (lambda: selector.power(base, exponent, False)),
                (lambda: selector.power(base, base, exponent)),
                (lambda: selector.power(base, exponent, exponent)),
                (lambda: selector.select(zero, 2)),
                (lambda: selector.select(original, True)),
                (lambda: selector.select(original, 2, compatibility=0)),
                (lambda: selector.select(original, 2, selector.Profile(0, 1, 2, 2, 1))),
                (lambda: selector.select(original, 2, selector.Profile(2, 1, 2, 1, 1))),
            )
            for call in bad:
                try:
                    call()
                except ValueError:
                    total += 1
                else:
                    raise ValueError("missing public boundary rejection")
                require(len(live) == 4, "failed boundary preserves borrowed roles")
            calls = 0
            ordinary_fits = selector.fits

            def fail_second(candidate):
                nonlocal calls
                calls += 1
                if calls == 2:
                    raise ValueError("injected completed-trial failure")
                return ordinary_fits(candidate)

            with no_decode(), patch.object(selector, "fits", fail_second):
                try:
                    selector.select(original, 2, selector.Profile(0, 1, 2, 1, 1), 1)
                except ValueError as error:
                    require(
                        str(error) == "injected completed-trial failure",
                        "expected injected failure",
                    )
                    total += 1
                else:
                    raise ValueError("missing injected failure")
            require(
                len(live) == 4 and calls == 2,
                "failed completed trial releases setup roles",
            )
        finally:
            for value in (original, base, exponent, zero):
                value.close()
    return dict(controls=total, **observed)
