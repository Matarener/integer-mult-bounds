# SPDX-License-Identifier: Apache-2.0
"""Real encoded planning and complete signed tape endpoints with exact oracles."""

from fractions import Fraction
import atexit
from hashlib import sha256
import json
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace

sys.path.insert(0, str(Path(sys.argv[1]).resolve()))
import cohort

cohort.activate()
sys.path.insert(0, str(Path(sys.argv[1]).resolve()))
# Frozen activation owns four private source directories. Close them before
# weakref finalizers so warnings remain enabled for the actual replay.
for name in ("leaf_sources", "phase_sources", "native_sources", "source"):
    temporary = getattr(sys.modules[name], "_temporary", None)
    if not isinstance(temporary, tempfile.TemporaryDirectory):
        raise ValueError("retained private source directory: " + name)
    atexit.register(temporary.cleanup)
from cardinal_counts import Count
from check_root import body, encode, integer, walsh
from fixture_binding import FixtureBinding
from cover import OrthogonalCover
from macro_code import Code
from ordinary import Ordinary
from outer_layer import OuterLayer
from outer_root_plan import RootPlan
from records import Tape
from root_layer import RootLayer
from session import erase_marker
from word_order import WordOrderBridge
from words import BLANK


def need(ok, message):
    if not ok:
        raise ValueError(message)


def packet(raw):
    tape = Tape()
    for bit in raw:
        tape.append(bit)
    tape.rewind()
    return tape


def consume(tape):
    tape.clear()
    erase_marker(tape)


def msb(values, width):
    return bytes(
        (v >> bit) & 1
        for pair in values
        for v in pair
        for bit in reversed(range(width))
    )


def bridge_checks():
    bridge, inverse = WordOrderBridge(), WordOrderBridge()
    digest = sha256()
    cases = 0
    for width in range(2, 9):
        w, n = Count.literal(width), Count.literal(2)
        for value in range(-(1 << (width - 1)), 1 << (width - 1)):
            values = ((value, -1), (0, (1 << (width - 1)) - 1))
            raw = msb(values, width)
            source = packet(raw)
            out = bridge.run(source, w, n)
            need(body(out) == encode(values, width), "signed value and component order")
            returned = inverse.run(out, w, n)
            need(
                body(returned) == raw and body(source) == raw,
                "bridge involution and borrowed source",
            )
            need(
                source.head == 1 and bridge.closed and not bridge.pool.live,
                "bridge cleanup",
            )
            digest.update(body(out))
            for tape in (returned, out, source):
                consume(tape)
            cases += 1
        w.close()
        n.close()
    return {
        "signed_packets": cases,
        "sha256": digest.hexdigest(),
        "peak_leases": bridge.pool.peak,
    }


def failure_checks():
    bridge = WordOrderBridge()
    w, n = Count.literal(4), Count.literal(1)
    cases = (bytes([0] * 7), bytes([0] * 9), bytes([0, 0, 7, 0, 0, 0, 0, 0]))
    rejected = 0
    for raw in cases:
        source = packet(raw)
        try:
            bridge.run(source, w, n)
        except ValueError:
            rejected += 1
        else:
            raise ValueError("malformed complete packet accepted")
        need(
            body(source) == raw
            and source.head == 1
            and bridge.closed
            and not bridge.pool.live
            and bridge.output.read() == BLANK,
            "failed bridge cleanup",
        )
        consume(source)
    source = packet(bytes([0] * 8))
    out = bridge.run(source, w, n)
    need(body(out) == bytes([0] * 8), "bridge reusable after rejection")
    for tape in (out, source):
        consume(tape)
    w.close()
    n.close()
    return {"malformed_packets_rejected": rejected, "reuse_after_failure": True}


def plan_checks():
    rows = []
    divisor = 66304 * OrthogonalCover(73).size
    for p in (2, 9, (1 << 40) - 1, 1 << 40, (1 << 40) + 1, 1 << 80, 1 << 280):
        plan = RootPlan(73, 48, divisor, guard_exponent=2, dimension_exponent=(1, 40))
        counts = tuple(Count.literal(v) for v in (p, 1, 2, 3, 2, 2, 0))
        snapshots = tuple(bytes(v.tape.cells) for v in counts)
        plan.compute(*counts)
        actual = {name: integer(plan.count(name)) for name in plan.roles}
        d = actual["d"]
        need(d**40 <= p < (d + 1) ** 40, "actual encoded outer dimension law")
        need(
            actual["K"] ** 500 <= d < (actual["K"] + 1) ** 500,
            "actual encoded chunk law",
        )
        need(
            actual["delta"] == 4 * d and actual["work_bits"] == p + 8 * d + 3,
            "guard follows new dimension",
        )
        need(
            actual["gaussians"] == 4 * (1 << (2 + actual["K"] + 3)),
            "whole payload volume",
        )
        need(
            tuple(bytes(v.tape.cells) for v in counts) == snapshots,
            "borrowed plan descriptors",
        )
        need(
            actual["q0"] == actual["depth"] * (divisor - 1).bit_length(),
            "T74 divisor in actual reserve",
        )
        rows.append([p, d, actual["K"], actual["delta"], actual["Q0"]])
        plan.clear()
        need(
            not plan.pool.live and all(t.read() == BLANK for t in plan.roles.values()),
            "plan cleanup",
        )
        for count in counts:
            count.close()
    rejected = invalid_plan_checks()
    return {
        "encoded_plans": rows,
        "T74_divisor_bits": divisor.bit_length(),
        "invalid_exponents_rejected": rejected,
        "old_dimension_rejected": True,
    }


def invalid_plan_checks():
    rejected = 0
    for exponent in ((0, 40), (41, 40), (1, 1001), (True, 40), [1, 40]):
        try:
            RootPlan(73, 48, 66304, dimension_exponent=exponent)
        except ValueError:
            rejected += 1
    need(rejected == 5, "fixed exponent boundary validation")
    plan = RootPlan(73, 48, 66304, guard_exponent=2, dimension_exponent=(1, 40))
    counts = tuple(Count.literal(v) for v in (9, 2, 0, 0, 1, 1, 0))
    try:
        plan.compute(*counts)
    except ValueError as error:
        need("selected width" in str(error), "old dimension cannot leak into new plan")
    else:
        raise ValueError("too many outer axes accepted")
    for count in counts:
        count.close()
    return rejected


def reduced_root():
    binding = FixtureBinding()
    native = Ordinary(
        2,
        SimpleNamespace(codes=SimpleNamespace(q=2)),
        SimpleNamespace(families=0),
        (Code((("unreachable",),), 0),),
        capacity=64,
    )
    plan = RootPlan(2, 1, 4, guard_exponent=2, dimension_exponent=(1, 40))
    return RootLayer(binding, native, binding.catalogue, plan)


def root_checks():
    layer = reduced_root()
    adapter = OuterLayer(layer)
    digest, mismatches = sha256(), 0
    cases = (
        (5, 0, 1, 1, 2, 2, 0),
        (5, 1, 1, 1, 2, 2, 0),
        (7, 1, 0, 2, 3, 2, 0),
        (9, 1, 2, 0, 1, 1, 0),
    )
    for parameters in cases:
        p, selected, left, right, fields, rows, rho = parameters
        size = rows * (1 << (left + selected + right)) * fields
        values = [((i * 7) % 13 - 6, (i * 11) % 17 - 8) for i in range(size)]
        raw = msb(values, p + 2)
        source = packet(raw)
        counts = tuple(Count.literal(v) for v in parameters)
        snapshots = tuple(bytes(value.tape.cells) for value in counts)
        returned = adapter.run(source, *counts)
        expected = msb(
            walsh(values, selected, left, right, 1, rho, fields, rows), p + 2
        )
        need(
            body(returned) == expected,
            "actual root with complete component-order adapters",
        )
        need(
            body(source) == raw
            and source.head == 1
            and tuple(bytes(value.tape.cells) for value in counts) == snapshots,
            "borrowed complete packets",
        )
        need(
            layer.closed
            and not layer.pool.live
            and layer.current.read() == BLANK
            and adapter.closed
            and not adapter.pool.live,
            "joined root cleanup",
        )
        mismatches += int(raw != encode(values, p + 2))
        digest.update(body(returned))
        for tape in (returned, source):
            consume(tape)
        for count in counts:
            count.close()
    need(mismatches == len(cases), "missing entrance reversal changes actual packet")
    return {
        "complete_root_packets": len(cases),
        "missing_bridge_witnesses": mismatches,
        "sha256": digest.hexdigest(),
        "scope": "Retained reduced binding, actual outer exponent, reduced guard",
    }


def wrapper_failure_checks():
    adapter = OuterLayer(reduced_root())
    counts = tuple(Count.literal(v) for v in (5, 1, 0, 0, 1, 1, 0))
    snapshots = tuple(bytes(value.tape.cells) for value in counts)
    source = packet(bytes([0] * 27))
    try:
        adapter.run(source, *counts)
    except ValueError as error:
        need(
            "complete signed bridge component" in str(error), "joined extent rejection"
        )
    else:
        raise ValueError("short joined packet accepted")
    need(
        adapter.closed
        and not adapter.pool.live
        and all(t.read() == BLANK for t in adapter.root.plan.roles.values()),
        "joined failure cleanup",
    )
    need(
        body(source) == bytes([0] * 27)
        and source.head == 1
        and tuple(bytes(value.tape.cells) for value in counts) == snapshots,
        "joined failure preserves caller",
    )
    consume(source)
    source = packet(bytes([0] * 28))
    returned = adapter.run(source, *counts)
    need(body(returned) == bytes([0] * 28), "joined retry endpoint")
    for tape in (source, returned):
        consume(tape)
    for count in counts:
        count.close()
    return {"extent_rejected": True, "complete_retry": True}


def arithmetic_checks():
    epsilon, c, tau = Fraction(1, 40), Fraction(1, 500), Fraction(99830289, 10**8)
    gaps = {
        "spacing": 1 - epsilon * (1 + c),
        "guard": 1 - epsilon,
        "chunk_growth": epsilon * c,
        "retained_outer_bottleneck": epsilon * c * (1 - tau),
    }
    need(all(v > 0 for v in gaps.values()), "strict outer/root geometry gaps")
    need(
        gaps["retained_outer_bottleneck"] == Fraction(169711, 2 * 10**12),
        "no substituted integer exponent",
    )
    return {key: str(value) for key, value in gaps.items()}


if __name__ == "__main__":
    print(
        json.dumps(
            {
                "bridge": bridge_checks(),
                "failures": failure_checks(),
                "plans": plan_checks(),
                "root": root_checks(),
                "wrapper_failure": wrapper_failure_checks(),
                "arithmetic": arithmetic_checks(),
            },
            sort_keys=True,
        )
    )
