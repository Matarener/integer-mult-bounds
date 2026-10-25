"""Every input column at both sealed returns and the complete interchange."""

from unittest.mock import patch

import check_nested_model as model
import scheduler
import strict_selector
from cardinal_counts import Count
from check_support import no_decode
from directory import Context
from engine import StrictRoot
from macro_binding import ToyBinding
from macro_code import compile_node
from physical_words import PhysicalWord
from provenance import Provenance
from records import Tape
from runtime import require
from traffic import measured
from words import BLANK, Arena, Ring, Word


class Binding(ToyBinding):
    def check_stock(self, runtime):
        # Six GL2 rows are exactly one independent remaining field.
        expected = Count.literal(1)
        try:
            require(
                expected.equals(runtime.count("unused")),
                "exact GL2 fresh stock quotient",
            )
        finally:
            expected.close()


def fixture():
    catalogue = model.Catalogue()
    topology = model.Topology(catalogue)
    arena, indices = Arena(3), Arena(10)
    modulus = arena.input(2)
    ring = Ring(modulus)
    context = Context(ring, catalogue.codes)
    plans = model.compile_coefficients(
        catalogue, context, indices, model.UnitIncoming(context)
    )
    binding = Binding(catalogue, plans)
    program = compile_node(topology, binding, 0)
    context.close()
    ring.close()
    arena.free(modulus)
    profile = strict_selector.Profile(
        row_factor=1, dimension=2, child_rank=1, numerator=0, denominator=1
    )
    return StrictRoot(2, binding, topology, (program,), capacity=128, profile=profile)


def body(tape):
    return bytes(tape.cells[1:]).rstrip(bytes([BLANK]))


def reverse(value, width):
    result = 0
    for _ in range(width):
        result = 2 * result + value % 2
        value //= 2
    return result


def root_permutation(length, prefixes, gap, suffix):
    require(length == prefixes * 6 * 8 * gap * 8 * suffix, "literal padded root volume")
    targets = []
    for address in range(length):
        rest, end = divmod(address, suffix)
        rest, second = divmod(rest, 8)
        rest, middle = divmod(rest, gap)
        row, first = divmod(rest, 8)
        target = (
            ((row * 8 + reverse(second, 3)) * gap + middle) * 8 + reverse(first, 3)
        ) * suffix + end
        targets.append(target)
    require(len(set(targets)) == length, "root map is a permutation")
    return targets


def check_endpoint(source, returned, masks, targets, provenance):
    expected, columns = bytearray(len(source)), [0] * len(source)
    for address, target in enumerate(targets):
        expected[target], columns[target] = source[address], masks[address]
    require(body(returned) == expected, "exact Boolean endpoint")
    require(
        provenance.masks(returned, len(source)) == tuple(columns),
        "every independent column endpoint",
    )


def observer(engine, provenance, prefixes, gap, suffix, completed):
    pending = []

    def observe(stage, padded, returned):
        if stage == "before":
            require(not pending, "one completed root at a time")
            saved = body(padded)
            leases = {
                slot: (lease, body(lease.physical), lease.head)
                for slot, lease in engine.pool.live.items()
            }
            pending.append((saved, provenance.masks(padded, len(saved)), leases))
            return
        saved, masks, leases = pending.pop()
        require(
            leases
            == {
                slot: (lease, body(lease.physical), lease.head)
                for slot, lease in engine.pool.live.items()
            },
            "root preserves every outer lease",
        )
        check_endpoint(
            saved,
            returned,
            masks,
            root_permutation(len(saved), prefixes, gap * 4, suffix),
            provenance,
        )
        require(
            body(padded) == saved and padded.head == returned.head == 1,
            "root preserves input and heads",
        )
        completed.append(len(saved))

    return observe, pending


def erased(engine):
    tapes = [
        *engine.pool.tapes,
        *engine.runtime.pool.tapes,
        *engine.runtime.roles.values(),
        *engine.runtime.handoff.values(),
        engine.runtime.output,
    ]
    for bank in (*engine.banks, engine.runtime.arena, engine.runtime.indices):
        require(not bank.live and not bank.initialized, "all numerical banks erased")
        tapes.extend(word.tape for word in (*bank.words, bank.template))
    require(
        all(all(bit == BLANK for bit in tape.cells) for tape in tapes),
        "all owned cells and markers erased",
    )
    require(
        engine.runtime.numerical.machine.tapes == [{}, {}], "parking workspace erased"
    )
    require(
        not engine.pool.live and not engine.runtime.pool.live,
        "all scratch leases released",
    )


def forbidden(*_args, **_kwargs):
    raise ValueError("fixture-only construction or decoding inside physical execution")


def final_endpoint(initial, output, provenance, extent, gap, suffix):
    targets = []
    for address in range(len(initial)):
        rest, end = divmod(address, suffix)
        rest, second = divmod(rest, extent)
        rest, middle = divmod(rest, gap)
        first_prefix, first = divmod(rest, extent)
        targets.append(
            (((first_prefix * extent + second) * gap + middle) * extent + first)
            * suffix
            + end
        )
    check_endpoint(
        initial, output, tuple(1 << i for i in range(len(initial))), targets, provenance
    )


def fixture_input(width, prefix, gap, suffix):
    extent = 2**width
    volume = prefix * extent * gap * extent * suffix
    require(volume <= 8192, "bounded finite fixture")
    payload = Tape()
    for address in range(volume):
        payload.append(((address * 13) ^ (address >> 3) ^ (address >> 7) ^ 0x53) & 1)
    payload.rewind()
    initial = body(payload)
    counts = tuple(Count.literal(value) for value in (width, prefix, gap, suffix))
    preserved = tuple((bytes(c.tape.cells), c.tape.head) for c in counts)
    return payload, initial, counts, preserved


def run_case(engine, width, prefix, gap, suffix, fitted):
    payload, initial, counts, preserved = fixture_input(width, prefix, gap, suffix)
    volume = len(initial)
    provenance, completed = Provenance(volume), []
    provenance.mark(payload)
    engine.observe, pending = observer(
        engine, provenance, prefix, gap, suffix, completed
    )
    before_macros = dict(engine.runtime.counts)
    with (
        no_decode(),
        provenance.installed(),
        patch.object(Word, "__init__", forbidden),
        patch.object(PhysicalWord, "inspect", forbidden),
        patch.object(scheduler.Invocation, "__init__", forbidden),
    ):
        with measured(engine) as traffic:
            output = engine.run(payload, *counts)
        final_endpoint(initial, output, provenance, 2**width, gap, suffix)
        require(
            body(payload) == initial and payload.head == output.head == 1,
            "borrowed original preserved",
        )
        require(
            tuple((bytes(c.tape.cells), c.tape.head) for c in counts) == preserved,
            "borrowed Counts preserved",
        )
        require(
            not pending and len(completed) == (2 if fitted else 0),
            "both returns checked before restriction",
        )
        require(
            engine.closed and engine.runtime.closed and engine.last_fitted == fitted,
            "complete expected physical branch",
        )
        erased(engine)
        output.clear()
    result = {
        "width": width,
        "spectators": [prefix, gap, suffix],
        "original_columns": volume,
        "fitted": fitted,
        "padded_return_columns": completed,
        "macro_counts_delta": {
            key: engine.runtime.counts[key] - value
            for key, value in before_macros.items()
        },
        "traffic": traffic,
        "outer_peak_roles": engine.pool.peak,
        "inner_peak_roles": engine.runtime.pool.peak,
    }
    payload.clear()
    for count in counts:
        count.close()
    return result


def run():
    engine = fixture()
    return [
        run_case(engine, 5, 1, 1, 1, True),
        run_case(engine, 2, 2, 3, 2, False),
        run_case(engine, 5, 1, 1, 1, True),
        run_case(engine, 5, 2, 1, 1, True),
        run_case(engine, 5, 1, 2, 1, True),
        run_case(engine, 5, 1, 1, 2, True),
    ]
