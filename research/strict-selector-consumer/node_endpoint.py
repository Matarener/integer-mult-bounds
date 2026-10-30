"""Retained PR2753 Node/Driver receives geometry from the actual Count plan."""

from contextlib import contextmanager

from binding_source import require
from cardinal_counts import Count
from check_nested_model import Catalogue, Topology
from directory import Context
from model import Consumer, Incoming
from node import Node
from records import Tape


@contextmanager
def completed(fixture, shape):
    catalogue = Catalogue()
    indices, size = shape.atoms.arena, shape.atoms
    context = Context(shape.ring, catalogue.codes)
    depth = indices.zero()
    program = object()
    incoming = Incoming(context, indices, (1, 1, 1))
    consumer = Consumer(context, indices, program, size, depth, catalogue, incoming)
    node = Node(
        context, indices, program, size, depth, Topology(catalogue), consumer, incoming
    )
    old, one = Tape(), Count.literal(1)
    preserved = (size, depth, incoming.tape, old)
    before = tuple(bytes(value.cells) for value in preserved)

    def call(source, rows):
        return node.run(
            source, old, fixture.counts[0], rows, one, shape.gap, shape.suffix
        )

    fixture.factory = call
    try:
        yield fixture.callee
        require(
            tuple(bytes(value.cells) for value in preserved) == before,
            "source metadata preserved",
        )
        require(
            all(value.head == 1 for value in preserved),
            "source metadata heads restored",
        )
        require(consumer.calls == {"MOVE": 24}, "both actual source residuals")
        require(
            consumer.children == {"enter": 240, "return": 240},
            "all actual source children return",
        )
    finally:
        fixture.factory = None
        old.clear()
        one.close()
        incoming.close()
        indices.free(depth)
        context.close()
