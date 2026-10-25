# SPDX-License-Identifier: Apache-2.0
"""Literal encoded execution, semantic oracles and complete Count ownership."""

import json
from contextlib import contextmanager
from hashlib import sha256
from unittest.mock import patch

import reference
from source import require


def serial(plan, inspect):
    return {
        key: value if key == "fits" else inspect(value) for key, value in plan.items()
    }


@contextmanager
def audited_counts():
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
                self.head == 1 and all(x == BLANK for x in self.cells[1:]),
                "closed Count body erased and head restored",
            )
            live.discard(self)

    with (
        patch.object(counts, "Tape", Audited),
        patch.object(cardinality, "Tape", Audited),
    ):
        yield observed, live
    require(not live, "all owned Count roles released")


def plans():
    import strict_selector as selector
    from cardinal_counts import Count
    from check_support import inspect_count, no_decode

    digest, total, fitted, new_domain = sha256(), 0, 0, 0
    with audited_counts() as (observed, live):
        for values in reference.cases():
            e, q, m, r, factor, compatibility, numerator, denominator = values
            if e > 24 and e % 8:
                continue
            profile = selector.Profile(numerator, denominator, m, r, factor)
            original = Count.literal(e)
            before = bytes(original.tape.cells)
            try:
                with no_decode():
                    plan = selector.select(original, q, profile, compatibility)
                actual = serial(plan, inspect_count)
                require(actual == reference.oracle(*values), "exact strict plan")
                require(
                    bytes(original.tape.cells) == before and original.tape.head == 1,
                    "borrowed original bytes and canonical head",
                )
                selector.close_plan(plan)
                require(len(live) == 1, "only borrowed original remains")
                digest.update(json.dumps([values, actual], sort_keys=True).encode())
                total += 1
                fitted += actual["fits"]
                new_domain += actual["fits"] and actual["rows"] < actual["stock"]
            finally:
                original.close()
    return dict(
        cases=total,
        fitted=fitted,
        below_stock=new_domain,
        sha256=digest.hexdigest(),
        **observed,
    )


def thresholds():
    import strict_selector as selector
    from cardinal_counts import Count
    from check_support import inspect_count, no_decode

    total = equalities = bound_cases = sharp_bounds = 0
    with audited_counts() as (observed, live):
        for stock in range(1, 65):
            source = Count.literal(stock)
            before = bytes(source.tape.cells)
            try:
                with no_decode():
                    threshold = selector.strict_threshold(source)
                value = inspect_count(threshold)
                require(value == stock // 2 + 1, "strict integer threshold")
                for rows in range(1, 65):
                    require(
                        (rows >= value) == (2 * rows > stock),
                        "exact strict boundary including equality",
                    )
                    equalities += 2 * rows == stock
                    total += 1
                for q in (2, 3, 5):
                    rows = 1
                    for _ in range(stock.bit_length() + 1):
                        if rows >= value:
                            break
                        rows *= q
                    else:
                        raise ValueError("threshold exponent bound")
                    require(2 * rows <= q * stock, "exact final-power bound")
                    bound_cases += 1
                    sharp_bounds += 2 * rows == q * stock
                threshold.close()
                require(
                    bytes(source.tape.cells) == before and source.tape.head == 1,
                    "borrowed stock preserved",
                )
                require(len(live) == 1, "threshold temporary cleanup")
            finally:
                source.close()
    return dict(
        decisions=total,
        rejected_equalities=equalities,
        final_bound_cases=bound_cases,
        sharp_final_equalities=sharp_bounds,
        **observed,
    )


def large_plan():
    import strict_selector as selector
    from cardinal_counts import Count
    from check_support import inspect_count, no_decode

    e = 1000000
    with audited_counts() as (observed, live):
        original = Count.literal(e)
        before = bytes(original.tape.cells)
        try:
            with no_decode():
                plan = selector.select(original, 2, selector.Profile(0, 1, 2, 1, 1), 1)
            actual = serial(plan, inspect_count)
            initial_stock = 6 ** reference.depth(e, 2, 1)
            candidates = [
                k
                for k in range(initial_stock.bit_length() + 1)
                if 2 * 2**k > 6 ** reference.depth(e - k, 2, 1)
            ]
            require(
                candidates and actual["borrowed"] == candidates[0],
                "large least strict plan",
            )
            require(
                actual["stock"] == 6 ** reference.depth(e - candidates[0], 2, 1)
                and actual["rows"] == 2 ** candidates[0],
                "exact large plan fields",
            )
            require(2 * actual["rows"] <= 2 * initial_stock, "proved final-size bound")
            require(
                bytes(original.tape.cells) == before and original.tape.head == 1,
                "large borrowed input preserved",
            )
            selector.close_plan(plan)
            require(len(live) == 1, "large plan cleanup")
        finally:
            original.close()
    require(observed["maximum_cells"] <= 104, "large trial storage remains capped")
    return dict(
        original=e,
        borrowed=actual["borrowed"],
        depth=actual["depth"],
        final_rows=str(actual["rows"]),
        final_stock=str(actual["stock"]),
        full_upper_power_bits=(e - 1) // 2 + 1,
        **observed,
    )


def rejections():
    import strict_selector as selector
    from cardinal_counts import Count
    from check_support import no_decode

    total = 0
    with audited_counts() as (observed, live):
        original, zero = Count.literal(24), Count.literal(0)
        try:
            calls = (
                lambda: selector.strict_threshold(zero),
                lambda: selector.select(zero, 2),
                lambda: selector.select(original, True),
                lambda: selector.select(original, 2, compatibility=False),
                lambda: selector.select(original, 2, selector.Profile(0, 1, 2, 2)),
                lambda: selector.select(original, 2, selector.Profile(2, 1, 2, 1)),
            )
            for call in calls:
                try:
                    call()
                except ValueError:
                    total += 1
                else:
                    raise ValueError("missing public boundary rejection")
                require(len(live) == 2, "rejection preserves borrowed roles")
            completed = 0
            ordinary_fits = selector.fits

            def fail_second(candidate):
                nonlocal completed
                completed += 1
                if completed == 2:
                    raise ValueError("injected completed-trial failure")
                return ordinary_fits(candidate)

            with no_decode(), patch.object(selector, "fits", fail_second):
                try:
                    selector.select(original, 2, selector.Profile(0, 1, 2, 1, 1), 1)
                except ValueError as error:
                    require(
                        str(error) == "injected completed-trial failure",
                        "expected completed-trial diagnostic",
                    )
                    total += 1
                else:
                    raise ValueError("missing injected failure")
            require(
                completed == 2 and len(live) == 2, "completed-trial failure cleanup"
            )
        finally:
            original.close()
            zero.close()
    return dict(controls=total, **observed)
