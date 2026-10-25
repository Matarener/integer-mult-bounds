"""Streamed leaf/XOR ownership under an already installed canonical pool.

Prepared for commdata2338 with substantial OpenAI Codex assistance. Apache-2.0.
The executed producer/consumer bytecode is JoyboyBrian's #5055; ScratchPool
and the canonical commit are Jose Manuel's retained physical-caller work.
"""

import importlib.util
from pathlib import Path
from types import FunctionType

import records
from records import Tape
from scratch_pool import ScratchPool
from words import BLANK, LEFT, need

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location(
    "r437_canonical_predecessor", ROOT / "research/r437-streaming-directory/streaming.py"
)
source = importlib.util.module_from_spec(spec)
spec.loader.exec_module(source)


def capacity(q):
    """Conditional on #5187's inherited source-call-graph reserve."""
    need(type(q) is int and q >= 2, "compiled radix at least two")
    return q * q + 141


def empty_role(tape):
    # The source Tape contract supplies contiguous bodies and blank tails.
    need(tape.read() == BLANK, "empty persistent body")
    tape.step(-1)
    need(tape.read() == LEFT, "persistent head after LEFT")
    tape.step(1)


def preserve(pool, residents):
    """A finite role-identity guard; it does not inspect a payload or a Word."""
    need(pool.live == residents and all(lease.active for lease in residents.values()),
         "consumer preserves exactly the producer leases")
    for slot, tape in enumerate(pool.tapes):
        if slot not in residents:
            empty_role(tape)


def run_into(source_packet, target_packet, events, layout, old, old_fields,
             old_count, code, context, coefficient, *, pool, roles,
             observe=None, boundary_observer=None):
    """Borrow four persistent roles: output, saved prefix, prefix, reader.

    The caller installs `pool` exactly once, before this call. All four roles
    must be ordinary tapes, separate from scratch and explicit borrowed inputs.
    On successful return only output is nonblank; every scratch lease is closed.
    There is no exception rollback or general recursive-dispatch installation.
    """
    need(isinstance(pool, ScratchPool) and records.Tape == pool.acquire,
         "canonical pool already installed")
    need(not pool.live, "empty canonical pool at macro entry")
    need(len(pool.tapes) >= capacity(layout.q), "canonical stream role reserve")
    need(len(roles) == 4 and all(type(tape) is Tape for tape in roles),
         "four persistent physical roles")
    borrowed = (source_packet, target_packet, old, old_count.tape, context.highs.tape)
    need(len({id(tape) for tape in roles}) == 4 and
         all(tape is not other for tape in roles for other in (*borrowed, *pool.tapes)),
         "persistent roles disjoint from borrows and scratch")
    for tape in roles:
        empty_role(tape)
    output, saved, prefix_role, reader = roles
    in_consumer = False
    output_taken = False
    producer_slots = iter((saved, prefix_role, reader))
    producer_allocations = 0

    def producer_tape():
        nonlocal producer_allocations
        producer_allocations += 1
        need(producer_allocations <= 3, "three fixed producer roles")
        return next(producer_slots)

    producer = FunctionType(source.visit.__code__,
                            dict(source.visit.__globals__, Tape=producer_tape))

    def allocate():
        nonlocal output_taken
        if in_consumer:
            return pool.acquire()
        need(not output_taken, "one supplied full output")
        output_taken = True
        return output

    def visit(old, fields, count, source_code, ctx, callback):
        def consume(prefix):
            nonlocal in_consumer
            need(not in_consumer, "nonreentrant leaf consumer")
            residents = dict(pool.live)
            need(len(residents) == 5, "five persistent producer Counts")
            if boundary_observer is not None:
                boundary_observer("entry", pool, residents, prefix)
            in_consumer = True
            try:
                callback(prefix)
            finally:
                in_consumer = False
            preserve(pool, residents)
            if boundary_observer is not None:
                boundary_observer("exit", pool, residents, prefix)
        return producer(old, fields, count, source_code, ctx, consume)

    run = FunctionType(source.run.__code__,
                       dict(source.run.__globals__, Tape=allocate, visit=visit))
    result = run(source_packet, target_packet, events, layout, old, old_fields,
                 old_count, code, context, coefficient, observe)
    need(result is output and output_taken and producer_allocations == 3,
         "complete supplied-role execution")
    pool.empty()
    for tape in roles[1:]:
        empty_role(tape)
    return result
