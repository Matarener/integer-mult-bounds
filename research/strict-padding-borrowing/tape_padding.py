"""Opt-in successor to Jose Manuel's PR2786 compatible-row planner.

Use only with its canonical Count operands and completed row-pointwise callee.
The frozen predecessor module is passed explicitly and is never modified.
Nick Petalas. Apache-2.0.
"""

MAX_COUNT_BITS = 4096


def bounded(count):
    from words import ONE, RIGHT, ZERO, need

    count.rewind()
    try:
        for _ in range(MAX_COUNT_BITS + 1):
            digit = count.read()
            if digit == RIGHT:
                return
            need(digit in (ZERO, ONE), "canonical binary count")
            count.step(1)
        raise ValueError("input count bit capacity exhausted")
    finally:
        count.rewind()


def compare(left, right):
    from words import ONE, RIGHT, ZERO, need

    if left is right or left.tape is right.tape:
        bounded(left)
        return 0
    left.rewind()
    right.rewind()
    order = 0
    try:
        for _ in range(MAX_COUNT_BITS + 2):
            a, b = left.read(), right.read()
            if a == b == RIGHT:
                return order
            need(a in (ZERO, ONE, RIGHT) and b in (ZERO, ONE, RIGHT), "binary counts")
            if a == RIGHT:
                order = -1
            elif b == RIGHT:
                order = 1
            elif a != b:
                order = 1 if a == ONE else -1
            if a != RIGHT:
                left.step(1)
            if b != RIGHT:
                right.step(1)
        raise ValueError("count bit capacity exhausted")
    finally:
        left.rewind()
        right.rewind()


def difference(left, right):
    from cardinal_counts import Count
    from words import RIGHT, ZERO, need

    need(compare(left, right) >= 0, "nonnegative row difference")
    result = Count(left)
    borrow = 0
    right.rewind()
    try:
        for _ in range(MAX_COUNT_BITS + 2):
            if result.read() == RIGHT:
                need(not borrow and right.read() == RIGHT, "complete row difference")
                result.normalize()
                return result
            done = right.read() == RIGHT
            digit = result.read() - (ZERO if done else right.read()) - borrow
            borrow = int(digit < 0)
            result.tape.write(digit + 2 * borrow)
            result.step(1)
            if not done:
                right.step(1)
        raise ValueError("difference bit capacity exhausted")
    except BaseException:
        result.close()
        raise
    finally:
        right.rewind()


def plan_rows(rows, stock, retained):
    """Return owned (padded,added) exactly when ceil(R/S)*S<2R.

    New-domain counts satisfy S/2<R<S. Legacy-domain behavior is delegated to
    the exact retained planner. No cardinality or payload is decoded.
    """
    from cardinal_counts import Count, positive
    from words import need

    positive(rows)
    positive(stock)
    bounded(rows)
    bounded(stock)
    if compare(rows, stock) >= 0:
        return retained.plan_rows(rows, stock)
    twice = Count(rows)
    try:
        twice.multiply_small(2)
        need(compare(stock, twice) < 0, "strict factor-two padding volume")
        added = difference(stock, rows)
        try:
            return Count(stock), added
        except BaseException:
            added.close()
            raise
    finally:
        twice.close()


def complete(source, prefixes, rows, stock, body, callee, retained):
    """Use retained row scans with the wider planner and the same return checks."""
    from cardinal_counts import positive
    from records import Tape
    from words import need

    positive(prefixes)
    positive(body)
    bounded(prefixes)
    bounded(body)
    padded_rows, added = plan_rows(rows, stock, retained)
    padded = returned = None
    try:
        padded = retained.transform(source, prefixes, rows, added, body)
        candidate = callee(padded, padded_rows)
        need(
            candidate is not padded and candidate is not source, "distinct owned output"
        )
        returned = candidate
        need(isinstance(returned, Tape), "callee returns a payload tape")
        need(
            padded.head == returned.head == padded_rows.tape.head == 1,
            "completed callee restores borrowed and output heads",
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
