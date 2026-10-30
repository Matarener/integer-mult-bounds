#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Exact fibre copy_bits invoice for PR2753 routes.route_cube.

Prepared by Wentao Li with substantial AI assistance.
"""
from __future__ import annotations

from fractions import Fraction
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
VENDOR = ROOT / "research/selected-bit-recursive-caller/predecessor/vendor"

# Expected certificate constants (also recomputed live).
EXPECTED = {
    "formula_cap_gt_1": "(2*d*d*L + 2)*V",
    "formula_cap_eq_1": "2*V",
    "partition_count_cap_gt_1": "d*d*L",
    "partition_count_cap_eq_1": 0,
    "L_identity": "arena.bits",
    "V_identity": "H*F with H=cap**(d*d)",
    "OwV_match": (
        "For M=q^w and L=bit_length(M)+1, fibre writes equal "
        "(2*d*d*L+2)*V when cap>1, hence >= 2*L*V >= 2*(floor(w*log2(q))+1)*V, "
        "matching the stated O_q(wV) charge on this pinned route_cube."
    ),
    "selected_decimal": "0.001672660197076918",
    "source_pr": 2753,
    "source_head": "7dba5452a4071a856a0b11cebdcd2d3b6bcd7659",
    "routes_sha256": "ed7dc3679451696ab1dd841146b215c9515a3eec5e4ff3763f33c315f1696ada",
}


def need(ok, message):
    if not ok:
        raise ValueError(message)


def load_vendor():
    need(VENDOR.is_dir(), "missing PR2753 vendor tree")
    path = str(VENDOR)
    if path not in sys.path:
        sys.path.insert(0, path)
    import bitstream  # noqa: F401
    import routes
    from counts import Count
    from directory import Context
    from records import Tape
    from words import Arena, Ring, ZERO, ONE

    return {
        "bitstream": bitstream,
        "routes": routes,
        "Count": Count,
        "Context": Context,
        "Tape": Tape,
        "Arena": Arena,
        "Ring": Ring,
        "ZERO": ZERO,
        "ONE": ONE,
    }


class Vocab:
    def __init__(self, q, dimension):
        self.q = q
        self.dimension = dimension
        self.bits = 2
        self.limit = 4

    def rank(self, _low):
        return None


def identity_low(dimension):
    return tuple(
        tuple(1 if i == j else 0 for j in range(dimension))
        for i in range(dimension)
    )


def identity_chart(dimension):
    return tuple(
        tuple(Fraction(1 if i == j else 0) for j in range(dimension))
        for i in range(dimension)
    )


def scale_chart(dimension, scale):
    return tuple(
        tuple(Fraction(scale if i == j else 0) for j in range(dimension))
        for i in range(dimension)
    )


def predicted(q, w, dimension, fibre_bits, arena_bits=None):
    need(q >= 3 and q % 2 == 1, "odd prime label q>=3")
    need(w >= 1 and dimension >= 1 and fibre_bits >= 1, "positive extents")
    modulus = q**w
    bits = arena_bits if arena_bits is not None else modulus.bit_length() + 1
    need(bits >= modulus.bit_length() + 1, "arena bits cover modulus margin")
    cap = modulus // q
    highs = cap ** (dimension * dimension)
    volume = highs * fibre_bits
    if cap > 1:
        partitions = dimension * dimension * bits
        writes = (2 * dimension * dimension * bits + 2) * volume
    else:
        partitions = 0
        writes = 2 * volume
    return {
        "q": q,
        "w": w,
        "dimension": dimension,
        "fibre_bits": fibre_bits,
        "modulus": modulus,
        "arena_bits": bits,
        "cap": cap,
        "highs": highs,
        "volume": volume,
        "partition_count": partitions,
        "fibre_copy_writes": writes,
        "OwV_coefficient_lower": (
            None if volume == 0 else writes / (w * volume)
        ),
    }


def measure_route_cube(q, w, dimension, fibre_bits, chart=None, low=None):
    """Run pinned route_cube; count partitions and fibre copy_bits writes."""
    mods = load_vendor()
    routes = mods["routes"]
    bitstream = mods["bitstream"]
    Count = mods["Count"]
    Context = mods["Context"]
    Tape = mods["Tape"]
    Arena = mods["Arena"]
    Ring = mods["Ring"]
    ZERO = mods["ZERO"]
    ONE = mods["ONE"]

    pred = predicted(q, w, dimension, fibre_bits)
    arena = Arena(bits=pred["arena_bits"], capacity=1 << 20)
    modulus_word = arena.input(pred["modulus"])
    ring = Ring(modulus_word)
    vocab = Vocab(q, dimension)
    context = Context(ring, vocab)
    if low is None:
        low = identity_low(dimension)
    if chart is None:
        chart = identity_chart(dimension)
    route = routes.compile_route(low, chart, vocab)

    fibre = Count.literal(fibre_bits)
    source = Tape()
    for index in range(pred["volume"]):
        source.append(ONE if index % 2 else ZERO)
    source.rewind()

    writes = {"n": 0}
    real_copy = bitstream.copy_bits

    def metered_copy(src, target, length):
        before = len(target.cells)
        real_copy(src, target, length)
        writes["n"] += len(target.cells) - before

    bitstream.copy_bits = metered_copy
    routes.copy_bits = metered_copy
    partitions = {"n": 0}
    real_partition = routes.partition

    def counted_partition(*args, **kwargs):
        partitions["n"] += 1
        return real_partition(*args, **kwargs)

    routes.partition = counted_partition
    try:
        output = routes.route_cube(source, route, context, fibre)
        need(partitions["n"] == pred["partition_count"], "partition count")
        need(writes["n"] == pred["fibre_copy_writes"], "fibre copy_bits writes")
        need(len([c for c in output.cells[1:] if c in (ZERO, ONE)]) == pred["volume"],
             "output fibre volume")
        result = {
            **pred,
            "measured_partitions": partitions["n"],
            "measured_fibre_copy_writes": writes["n"],
            "chart_kind": "identity" if chart == identity_chart(dimension) else "scaled",
        }
        output.clear()
        return result
    finally:
        routes.partition = real_partition
        bitstream.copy_bits = real_copy
        routes.copy_bits = real_copy
        source.clear()
        fibre.close()
        context.close()
        ring.close()
        arena.free(modulus_word)


def cursor_pass_count(arena_bits):
    """Word lemma: routes.route_cube one-hot cursor yields exactly arena.bits passes.

    Ring requires bit_length(M)+1 == arena.bits. Pass count depends only on
    arena.bits (one-hot walk to the high margin), not on the modulus value.
    """
    mods = load_vendor()
    Arena = mods["Arena"]
    Ring = mods["Ring"]
    ONE = mods["ONE"]
    ZERO = mods["ZERO"]
    need(arena_bits >= 3, "cursor lemma needs high-bit margin")
    # Canonical odd modulus with exact one high-zero margin for this arena.
    modulus_value = (1 << (arena_bits - 2)) + 1
    need(modulus_value.bit_length() + 1 == arena_bits, "exact margin width")
    arena = Arena(bits=arena_bits, capacity=64)
    modulus = arena.input(modulus_value)
    ring = Ring(modulus)
    one = arena.literal(1)
    cursor = arena.copy(one)
    arena.free(one)
    passes = 0
    try:
        while True:
            passes += 1
            cursor.msb()
            final = cursor.read() == ONE
            cursor.rewind()
            if final:
                break
            shifted = ring.raw.shift_add_bit(cursor, ZERO)
            arena.free(cursor)
            cursor = shifted
        need(passes == arena_bits, "cursor passes equal arena.bits")
        return passes
    finally:
        arena.free(cursor)
        ring.close()
        arena.free(modulus)


FIXTURES = (
    {"q": 3, "w": 1, "dimension": 1, "fibre_bits": 5},
    {"q": 3, "w": 2, "dimension": 1, "fibre_bits": 4},
    {"q": 3, "w": 2, "dimension": 1, "fibre_bits": 3, "scale": 2},
    {"q": 3, "w": 3, "dimension": 1, "fibre_bits": 2},
    {"q": 3, "w": 2, "dimension": 2, "fibre_bits": 1},
    {"q": 5, "w": 2, "dimension": 1, "fibre_bits": 2},
)


def run_suite():
    rows = []
    for fixture in FIXTURES:
        scale = fixture.get("scale")
        chart = None
        if scale is not None:
            chart = scale_chart(fixture["dimension"], scale)
        row = measure_route_cube(
            fixture["q"],
            fixture["w"],
            fixture["dimension"],
            fixture["fibre_bits"],
            chart=chart,
        )
        rows.append(row)
    cursor_checks = {bits: cursor_pass_count(bits) for bits in (3, 5, 6, 8)}
    return rows, cursor_checks
