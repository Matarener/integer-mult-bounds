"""Strict row return adapter with a stable nominal Tape type.

The physical factory scope changes records.Tape into an allocation function.
Capture its nominal type before that scope, as the physical OuterScope does.
The Count planner and both physical scans remain the exact predecessors.
"""

import tape_padding
from cardinal_counts import positive
from records import Tape
from words import need


def complete(source, prefixes, rows, stock, body, callee, retained):
    positive(prefixes)
    positive(body)
    tape_padding.bounded(prefixes)
    tape_padding.bounded(body)
    padded_rows, added = tape_padding.plan_rows(rows, stock, retained)
    padded = returned = None
    try:
        padded = retained.transform(source, prefixes, rows, added, body)
        candidate = callee(padded, padded_rows)
        need(
            candidate is not padded and candidate is not source, "distinct owned output"
        )
        returned = candidate
        need(isinstance(returned, Tape), "callee returns a physical payload tape")
        need(
            padded.head == returned.head == padded_rows.tape.head == 1,
            "completed callee restores heads",
        )
        padded.clear()
        padded = None
        return retained.transform(
            returned, prefixes, rows, added, body, restricting=True
        )
    finally:
        if returned is not None and isinstance(returned, Tape):
            returned.clear()
        if padded is not None:
            padded.clear()
        padded_rows.close()
        added.close()
