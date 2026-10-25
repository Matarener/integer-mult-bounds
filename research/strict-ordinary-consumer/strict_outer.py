"""Opt-in ordinary consumer of strict compatible-row padding.

Retains PR2808's ordered passes and PR3503's exact Count adapter.
No predecessor module or default callback is changed.
"""

from contextlib import ExitStack

import outer
import padding
import tape_padding
from cardinal_counts import Count, positive
from cardinality import multiply_atom_power
from words import need


def admit(rows, stock):
    """Reject S>=2R before any payload operation; preserve borrowed Counts."""
    positive(rows)
    positive(stock)
    tape_padding.bounded(rows)
    tape_padding.bounded(stock)
    twice = Count(rows)
    try:
        twice.multiply_small(2)
        need(tape_padding.compare(stock, twice) < 0, "strict factor-two padding volume")
    finally:
        twice.close()


def body(source, atoms, ring, q, prefixes, rows, stock, gap, suffix, callee):
    """Each completed call returns through restriction before another pass."""
    current = source
    with ExitStack() as work:
        before = Count.product(prefixes, rows)
        work.callback(before.close)
        extent = Count.product(gap, suffix)
        work.callback(extent.close)
        multiply_atom_power(extent, atoms, ring, q)
        multiply_atom_power(extent, atoms, ring, q)
        try:
            current = outer.body_pass(
                current, atoms, ring, q, before, gap, suffix, negative=True
            )
            for second in (False, True):
                following = tape_padding.complete(
                    current, prefixes, rows, stock, extent, callee, padding
                )
                current = outer.replace(current, following, source)
                if not second:
                    following = outer.body_pass(
                        current, atoms, ring, q, before, gap, suffix
                    )
                    current = outer.replace(current, following, source)
            following = outer.body_pass(
                current, atoms, ring, q, before, gap, suffix, sign=True
            )
            current = outer.replace(current, following, source)
            following = outer.body_pass(current, atoms, ring, q, before, gap, suffix)
            current = outer.replace(current, following, source)
            result, current = current, None
            return result
        finally:
            if current is not None and current is not source:
                current.clear()


def interchange(
    source,
    atoms,
    ring,
    high_ring,
    q,
    prefixes,
    spectators,
    suffix,
    stock,
    callee,
    remainder_ring=None,
):
    """Full ordinary chunk interchange, with genuine R in every spectator gap."""
    current = source
    with outer.borrowing_shape(
        atoms, ring, high_ring, q, prefixes, spectators, suffix, stock, remainder_ring
    ) as shape:
        admit(shape.rows, stock)
        try:
            if remainder_ring is not None:
                current = outer.swap_remainder(
                    current, remainder_ring, q, prefixes, shape, suffix
                )
            following = body(
                current,
                atoms,
                ring,
                q,
                prefixes,
                shape.rows,
                stock,
                shape.actual_gap,
                shape.actual_suffix,
                callee,
            )
            current = outer.replace(current, following, source)
            following = outer.swap_chunks(
                current, high_ring, q, prefixes, shape.high_gap, shape.high_suffix
            )
            current = outer.replace(current, following, source)
            result, current = current, None
            return result
        finally:
            if current is not None and current is not source:
                current.clear()
