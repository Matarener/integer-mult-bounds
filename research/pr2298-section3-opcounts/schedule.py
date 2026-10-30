"""Exact PR2298 §3 exchange schedules for mixed adjacent axis widths.

Research construction / recursive interface; no new kappa.
Prepared by Wentao Li with substantial AI assistance.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from typing import Iterable


def need(ok, message: str) -> None:
    if not ok:
        raise RuntimeError(message)


@dataclass(frozen=True)
class Op:
    """One completed equal-width interchange or one elementary bit move."""

    kind: str  # "interchange" or "bit_move"
    i: int
    j: int
    width_i: int
    width_j: int

    def as_list(self):
        return [self.kind, self.i, self.j, self.width_i, self.width_j]


def _plan_pair(wi: int, wj: int) -> list[str]:
    """Primitive sequence for exchanging axes of bit-widths wi, wj.

    Matches PR2298 PROOF §3 / docs/nonadjacent-axis-audit.md:
      equal widths: one interchange
      |wi-wj|=1: one interchange + one bit move (order depends on which is longer)
    """
    need(abs(wi - wj) <= 1, f"axis widths must be adjacent: {wi},{wj}")
    if wi == wj:
        return ["interchange"]
    if wi == wj + 1:
        # long field first: e x G y -> e y G x -> y G e x
        return ["interchange", "bit_move"]
    # wi + 1 == wj: long field last: x G e y -> e x G y -> e y G x
    return ["bit_move", "interchange"]


def exchange_ops(widths: list[int], i: int, j: int) -> list[Op]:
    """Emit the primitive ops that exchange positions i and j, then swap widths."""
    need(0 <= i < j < len(widths), f"bad exchange indices {i},{j}")
    wi, wj = widths[i], widths[j]
    kinds = _plan_pair(wi, wj)
    return [Op(kind, i, j, wi, wj) for kind in kinds]


def apply_exchange(widths: list[int], i: int, j: int) -> list[Op]:
    ops = exchange_ops(widths, i, j)
    widths[i], widths[j] = widths[j], widths[i]
    return ops


def reversal_schedule(widths: list[int]) -> dict:
    """Reverse axis order by nonadjacent endpoint exchanges."""
    d = len(widths)
    live = list(widths)
    ops: list[Op] = []
    exchanges = 0
    for k in range(d // 2):
        ops.extend(apply_exchange(live, k, d - 1 - k))
        exchanges += 1
    need(live == list(reversed(widths)), "reversal must invert axis order")
    return {
        "kind": "reversal",
        "d": d,
        "widths_in": list(widths),
        "widths_out": live,
        "exchanges": exchanges,
        "bound_exchanges": d // 2,
        "interchanges": sum(1 for op in ops if op.kind == "interchange"),
        "bit_moves": sum(1 for op in ops if op.kind == "bit_move"),
        "ops": [op.as_list() for op in ops],
    }


def tensor_map_schedule(widths: list[int]) -> dict:
    """Expose each non-innermost axis, then restore: ≤ 2(d-1) exchanges."""
    d = len(widths)
    live = list(widths)
    ops: list[Op] = []
    exchanges = 0
    # Innermost is index d-1. For each axis i < d-1: swap with innermost, then undo.
    for i in range(d - 1):
        ops.extend(apply_exchange(live, i, d - 1))
        exchanges += 1
        # process lines (no exchange cost in this invoice)
        ops.extend(apply_exchange(live, i, d - 1))
        exchanges += 1
    need(live == list(widths), "tensor map must restore widths")
    return {
        "kind": "tensor_map",
        "d": d,
        "widths_in": list(widths),
        "widths_out": live,
        "exchanges": exchanges,
        "bound_exchanges": 2 * max(d - 1, 0),
        "interchanges": sum(1 for op in ops if op.kind == "interchange"),
        "bit_moves": sum(1 for op in ops if op.kind == "bit_move"),
        "ops": [op.as_list() for op in ops],
    }


def one_extra_bit_cases(base: int = 3) -> list[dict]:
    """Unit checks of the two one-extra-bit constructions at a single pair."""
    cases = []
    for wi, wj, label in (
        (base + 1, base, "long_first"),
        (base, base + 1, "long_last"),
        (base, base, "equal"),
    ):
        widths = [wi, wj]
        ops = exchange_ops(widths, 0, 1)
        cases.append(
            {
                "label": label,
                "widths": [wi, wj],
                "ops": [op.as_list() for op in ops],
                "interchanges": sum(1 for op in ops if op.kind == "interchange"),
                "bit_moves": sum(1 for op in ops if op.kind == "bit_move"),
            }
        )
    return cases


def mixed_width_patterns(d: int, short: int = 3, long: int = 4) -> Iterable[tuple[int, ...]]:
    """All 2^d patterns of adjacent bit-widths {short, long} for axis count d."""
    need(long == short + 1, "mixed r/2 and r means adjacent bit widths")
    for bits in product((short, long), repeat=d):
        yield bits


def census(max_d: int = 8, short: int = 3, long: int = 4) -> dict:
    """Exact schedule census for every mixed-width pattern at d=1..max_d."""
    rows = []
    max_rev_ex = 0
    max_tensor_ex = 0
    one_extra_long = 0
    one_extra_equal = 0
    for d in range(1, max_d + 1):
        for widths in mixed_width_patterns(d, short, long):
            rev = reversal_schedule(list(widths))
            ten = tensor_map_schedule(list(widths))
            need(rev["exchanges"] <= rev["bound_exchanges"], "reversal exchange bound")
            need(ten["exchanges"] <= ten["bound_exchanges"], "tensor exchange bound")
            # Every unequal exchange in either schedule uses exactly one bit_move.
            for sched in (rev, ten):
                for kind, _i, _j, wi, wj in sched["ops"]:
                    if wi == wj:
                        need(kind == "interchange", "equal widths use interchange only")
                        one_extra_equal += 1
                    else:
                        need(kind in ("interchange", "bit_move"), "primitive kind")
                        one_extra_long += 1
                # Per exchange pair: unequal ⇒ exactly one interchange and one bit_move.
            # Recount per exchange by walking the schedule in emission order.
            _check_pair_invoice(rev["ops"])
            _check_pair_invoice(ten["ops"])
            max_rev_ex = max(max_rev_ex, rev["exchanges"])
            max_tensor_ex = max(max_tensor_ex, ten["exchanges"])
            rows.append(
                {
                    "d": d,
                    "widths": list(widths),
                    "reversal_exchanges": rev["exchanges"],
                    "reversal_bound": rev["bound_exchanges"],
                    "reversal_interchanges": rev["interchanges"],
                    "reversal_bit_moves": rev["bit_moves"],
                    "tensor_exchanges": ten["exchanges"],
                    "tensor_bound": ten["bound_exchanges"],
                    "tensor_interchanges": ten["interchanges"],
                    "tensor_bit_moves": ten["bit_moves"],
                    "reversal_ops": rev["ops"],
                    "tensor_ops": ten["ops"],
                }
            )
    unit = one_extra_bit_cases()
    for case in unit:
        if case["label"] == "equal":
            need(case["interchanges"] == 1 and case["bit_moves"] == 0, "equal pair invoice")
        else:
            need(case["interchanges"] == 1 and case["bit_moves"] == 1, "one-extra-bit invoice")
    pattern_count = sum(2**d for d in range(1, max_d + 1))
    need(len(rows) == pattern_count, "pattern census size")
    return {
        "max_d": max_d,
        "short_width": short,
        "long_width": long,
        "pattern_count": len(rows),
        "max_reversal_exchanges": max_rev_ex,
        "max_tensor_exchanges": max_tensor_ex,
        "unit_one_extra_bit": unit,
        "rows": rows,
        "bounds": {
            "reversal_exchanges": "floor(d/2)",
            "tensor_exchanges": "2(d-1)",
            "one_extra_bit": "1 interchange + 1 bit_move",
            "equal_pair": "1 interchange",
        },
        "all_reversals_within_bound": all(
            r["reversal_exchanges"] <= r["reversal_bound"] for r in rows
        ),
        "all_tensors_within_bound": all(
            r["tensor_exchanges"] <= r["tensor_bound"] for r in rows
        ),
    }


def _check_pair_invoice(ops: list[tuple]) -> None:
    """Group ops into per-exchange invoices (1 or 2 primitives)."""
    i = 0
    while i < len(ops):
        kind, a, b, wi, wj = ops[i]
        if wi == wj:
            need(kind == "interchange", "equal pair starts with interchange")
            i += 1
            continue
        need(i + 1 < len(ops), "unequal pair needs two primitives")
        kind2, a2, b2, wi2, wj2 = ops[i + 1]
        need((a, b, wi, wj) == (a2, b2, wi2, wj2), "paired primitives share endpoints")
        kinds = {kind, kind2}
        need(kinds == {"interchange", "bit_move"}, "one-extra-bit invoice")
        i += 2


def physical_reversal_ok(widths: list[int], move_address) -> bool:
    """Apply the reversal schedule to a full address space via move_address."""
    d = len(widths)
    total = sum(widths)
    # Build field intervals from MSB (matching physical.py convention).
    live = list(widths)
    space = list(range(1 << total)) if total <= 16 else None
    if space is None:
        # Spot-check random addresses for large spaces.
        import random

        rng = random.Random(2298 + d + sum(widths))
        space = [rng.randrange(1 << total) for _ in range(64)]
        space += [0, (1 << total) - 1]
    # Emit low-level (kind, source, target, width) for physical.move_address.
    low_ops = []
    for k in range(d // 2):
        i, j = k, d - 1 - k
        wi, wj = live[i], live[j]
        left = sum(live[:i])
        right = sum(live[:j])
        if wi == wj:
            low_ops.append(("swap", left, right, wi))
        elif wi == wj + 1:
            low_ops.append(("swap", left + 1, right, wj))
            low_ops.append(("move", left, right - 1, 1))
        else:
            low_ops.append(("move", right, left, 1))
            low_ops.append(("swap", left + 1, right + 1, wi))
        live[i], live[j] = live[j], live[i]
    need(live == list(reversed(widths)), "width track for physical reversal")

    def apply_all(index: int) -> int:
        for op in low_ops:
            index = move_address(index, total, op)
        return index

    # Axis coordinate permutation: reversing field order.
    def decode(index: int, ws: list[int]) -> list[int]:
        # MSB-first fields.
        coords = []
        shift = total
        for w in ws:
            shift -= w
            coords.append((index >> shift) & ((1 << w) - 1))
        return coords

    def encode(coords: list[int], ws: list[int]) -> int:
        index = 0
        for c, w in zip(coords, ws):
            index = (index << w) | c
        return index

    for addr in space:
        coords = decode(addr, list(widths))
        expect = encode(list(reversed(coords)), list(reversed(widths)))
        got = apply_all(addr)
        if got != expect:
            return False
    return True
