"""Changed-boundary failure controls, with explicit cleanup observations."""

from unittest.mock import patch

import outer
import padding
from cardinal_counts import Count
from fixtures import Fixture, Parameters, case
from runtime import require


def rejected(action, expected):
    try:
        action()
    except ValueError as error:
        require(str(error) == expected, "named strict control: " + str(error))
    else:
        raise ValueError("strict semantic mutant accepted")


def boundary():
    fixture = Fixture(Parameters(n=1, stock_value=6), None, None)
    try:
        with patch.object(
            fixture.source,
            "read",
            side_effect=ValueError("payload read before admission"),
        ):
            rejected(fixture.run, "strict factor-two padding volume")
        require(not fixture.calls, "equality rejects before callee")
        require(fixture.tracker.live == {fixture.source}, "equality cleanup")
        require(
            bytes(fixture.source.cells) == fixture.saved, "equality source preserved"
        )
        require(
            all(
                bytes(c.tape.cells) == old and c.tape.head == 1
                for c, old in zip(fixture.counts, fixture.snapshots, strict=True)
            ),
            "equality counts preserved",
        )
    finally:
        fixture.close()


def covering_rejects():
    rows, stock = Count.literal(3), Count.literal(5)
    before = bytes(rows.tape.cells), bytes(stock.tape.cells)
    try:
        rejected(
            lambda: padding.plan_rows(rows, stock),
            "row capacity must cover at least one stock group",
        )
        require(
            before == (bytes(rows.tape.cells), bytes(stock.tape.cells))
            and rows.tape.head == stock.tape.head == 1,
            "old guard preserves borrowed row counts",
        )
    finally:
        rows.close()
        stock.close()


def delayed_restriction():
    original = padding.transform

    def retain_rows(source, prefixes, rows, added, body, restricting=False):
        if not restricting:
            return original(source, prefixes, rows, added, body)
        expanded, zero = Count(rows), Count.literal(0)
        try:
            expanded.add(added)
            return original(source, prefixes, expanded, zero, body)
        finally:
            expanded.close()
            zero.close()

    with patch.object(padding, "transform", retain_rows):
        rejected(lambda: case(n=1), "immediate genuine restriction")


def genuine_gap():
    original = outer.borrowing_shape

    from contextlib import contextmanager

    @contextmanager
    def altered(*args):
        with original(*args) as shape:
            shape.actual_gap.multiply_small(2)
            yield shape

    with patch.object(outer, "borrowing_shape", altered):
        # The first ADD now expects a nonexistent full second high field.
        rejected(lambda: case(n=1), "genuine other high field in body gap")


def run_controls():
    boundary()
    covering_rejects()
    delayed_restriction()
    genuine_gap()
    names = [
        "strict_equality_before_payload",
        "old_covering_guard_rejects_new_domain",
        "delayed_restriction",
        "fabricated_second_high_field",
    ]
    for position in (1, 2):
        result = case(n=1, fail_at=position)
        require(
            result["failed_at"] == position, "actual strict callee failure propagated"
        )
        names.append(f"strict_callee_failure_{position}_cleanup")
    return names
