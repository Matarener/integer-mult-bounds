"""Actual Count selection and completed physical-return boundary controls."""

from types import SimpleNamespace

import selector
import source
import strict_rows
import strict_selector
from cardinal_counts import Count
from records import Tape
from runtime import require
from verification import body


def plans():
    profile = strict_selector.Profile(
        row_factor=1, dimension=2, child_rank=1, numerator=0, denominator=1
    )
    original = Count.literal(5)
    expected = {
        "width": 1,
        "borrowed": 2,
        "body": 3,
        "remainder": 0,
        "depth": 1,
        "stock": 6,
        "rows": 4,
    }
    try:
        plan = strict_selector.select(original, 2, profile, 1)
        try:
            require(plan["fits"], "actual strict plan fits")
            for name, value in expected.items():
                count = Count.literal(value)
                try:
                    require(plan[name].equals(count), "exact plan field " + name)
                finally:
                    count.close()
        finally:
            strict_selector.close_plan(plan)
        covering = selector.select(original, 2, profile, 1)
        try:
            require(not covering["fits"], "actual covering selector has no legal fit")
        finally:
            selector.close_plan(covering)
    finally:
        original.close()
    return expected


def completed_return(kind, source_tape, returned):
    def callee(padded, _rows):
        if kind == "padded-alias":
            return padded
        if kind == "source-alias":
            return source_tape
        if kind == "wrong-type":
            return SimpleNamespace()
        output = Tape()
        for value in body(padded):
            output.append(value)
        output.rewind()
        if kind == "bad-head":
            output.step(1)
        returned.append(output)
        return output

    return callee


def return_control(kind):
    _loader, padding, _outer = source.activate()
    source_tape = Tape()
    for value in (0, 1, 1, 0):
        source_tape.append(value)
    source_tape.rewind()
    counts = tuple(
        Count.literal(v) for v in (1, 4, 8 if kind == "strict-boundary" else 6, 1)
    )
    original, returned = body(source_tape), []
    callee = completed_return(kind, source_tape, returned)
    rejected = False
    try:
        try:
            result = strict_rows.complete(source_tape, *counts, callee, padding)
            require(kind == "identity", "invalid completed return accepted")
            require(body(result) == original, "identity padding/restriction control")
            result.clear()
        except ValueError as error:
            require(kind != "identity", "valid completed return rejected")
            require(
                str(error)
                in {
                    "distinct owned output",
                    "callee returns a physical payload tape",
                    "completed callee restores heads",
                    "strict factor-two padding volume",
                },
                "exact intended boundary rejection",
            )
            rejected = True
        require(
            body(source_tape) == original and source_tape.head == 1,
            "control preserves borrowed source",
        )
        require(all(c.tape.head == 1 for c in counts), "control restores Count heads")
        require(
            all(not body(tape) and tape.head == 1 for tape in returned),
            "returned owned output consumed on rejection",
        )
    finally:
        source_tape.clear()
        for count in counts:
            count.close()
    return {"kind": kind, "rejected": rejected}


def run():
    return {
        "actual_strict_plan": plans(),
        "returns": [
            return_control(kind)
            for kind in (
                "identity",
                "padded-alias",
                "source-alias",
                "wrong-type",
                "bad-head",
                "strict-boundary",
            )
        ],
    }
