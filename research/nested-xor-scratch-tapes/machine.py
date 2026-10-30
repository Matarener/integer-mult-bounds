"""Nested XOR swaps, using the two-tape record ABI of Dugongue's PR3879.

The R0/L0/W transition templates below reimplement that credited ABI.
The nested visit schedule and its complete invoice are produced by Nick Petalas.
Apache-2.0.
"""

from dataclasses import dataclass

ZERO, ONE, SEP, BLANK = range(4)
MAX_H = 9
MAX_TABLE_ENTRIES = 250_000


def need(condition, message):
    if not condition:
        raise ValueError(message)


def parameters(h, delta):
    """Bound executable evidence; the written theorem has unrestricted h."""
    need(type(h) is int and 0 <= h <= MAX_H, "dimension outside 0..9")
    need(type(delta) is int and 0 <= delta < 1 << h, "invalid XOR mask")
    n = 1 << h
    m = 1 << (delta.bit_length() - 1) if delta else 0
    return n, m, delta - m


def visits(h, delta):
    n, _, _ = parameters(h, delta)
    if not delta:
        return ()
    roots = tuple(a for a in range(n) if a < (a ^ delta))
    closing = tuple(v for a in reversed(roots) for v in (a ^ delta, a))
    need(len(roots) == n // 2, "fixed-point-free involution")
    return roots + closing


def invoice(h, delta, width):
    n, m, low = parameters(h, delta)
    need(type(width) is int and width >= 0, "invalid record width")
    if delta:
        travel = n * m + 2 * (n // (2 * m) - 1) * (low + 1)
        serial = (n - 2) * m + 2 * n - 2  # PR3879, Theorem B
        swaps = 3 * n // 2
    else:
        travel = serial = swaps = 0
    return {
        "records": n, "mask": delta, "width": width,
        "record_swaps": swaps, "record_crossings": travel,
        "serial_record_crossings": serial,
        "saved_record_crossings": serial - travel,
        "steps": swaps * (2 * width + 3) + travel * (width + 2),
        "saved_steps": (serial - travel) * (width + 2),
        "states_including_halt": 3 * swaps + 2 * travel + 1,
        "table_entries": 11 * swaps + 16 * travel,
    }


@dataclass(frozen=True)
class Machine:
    operations: tuple
    table: dict
    halt: int


def template(table, state, op):
    """Literal four-symbol templates from PR3879, not an online macro oracle."""
    need(op in ("R0", "L0", "W"), "unknown macro")
    following = state + (3 if op == "W" else 2)
    scan, rewind = state + 1, state + 2
    for a in range(4):
        for b in range(4):
            if op == "W":
                if a == b == SEP:
                    table[state, a, b] = (scan, None, None, 1, 1)
                    table[scan, a, b] = (rewind, None, None, -1, -1)
                    table[rewind, a, b] = (following, None, None, 0, 0)
                elif a in (ZERO, ONE) and b in (ZERO, ONE):
                    table[scan, a, b] = (scan, b, a, 1, 1)
                    table[rewind, a, b] = (rewind, None, None, -1, -1)
            else:
                direction = 1 if op == "R0" else -1
                if a == SEP:
                    table[state, a, b] = (scan, None, None, direction, 0)
                    table[scan, a, b] = (following, None, None, 0, 0)
                elif a in (ZERO, ONE):
                    table[scan, a, b] = (scan, None, None, direction, 0)
    return following


def compile_visits(h, delta, order, *, return_head=True):
    """Also accepts bounded wrong orders for executable rejection controls."""
    n, _, _ = parameters(h, delta)
    need(type(order) is tuple and len(order) <= 3 * n, "visit capacity")
    need(all(type(a) is int and 0 <= a < n for a in order), "visit address")
    position = 0
    travel = 0
    for address in order:
        travel += abs(address - position)
        position = address
    travel += position if return_head else 0
    entries = 16 * travel + 11 * len(order)
    need(entries <= MAX_TABLE_ENTRIES, "literal table capacity exceeded")
    operations = []
    position = 0
    for address in order:
        step = address - position
        operations.extend(("R0" if step > 0 else "L0",) * abs(step))
        operations.append("W")
        position = address
    if return_head:
        operations.extend(("L0",) * position)
    table = {}
    state = 0
    for op in operations:
        state = template(table, state, op)
    need(len(table) == entries, "transition-template inventory")
    need(state == 2 * travel + 3 * len(order), "state inventory")
    return Machine(tuple(operations), table, state)


def compile_machine(h, delta):
    machine = compile_visits(h, delta, visits(h, delta))
    bill = invoice(h, delta, 0)
    need(len(machine.table) == bill["table_entries"], "closed table bill")
    need(machine.halt + 1 == bill["states_including_halt"], "closed state bill")
    return machine
