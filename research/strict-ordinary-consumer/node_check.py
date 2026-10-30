"""Complete retained GL2(F2) source execution on fewer genuine rows than stock.

David Arias's PR2753 Node/Driver, through Nick Petalas's PR2808 fixture.
This is a toy supplier, outside the selected odd-prime GL64 domain.
"""

from cardinal_counts import Count
from check_nested_model import Catalogue, Topology
from check_support import audit
from directory import Context
from fixtures import case
from model import Consumer, Incoming
from node import Node
from records import Tape
from runtime import require
from words import Arena, Ring


def borrowing_table():
    result = []
    for k in range(3):
        body, depth = 5 - k, 0
        cursor = body
        for _ in range(3):
            if cursor < 2:
                break
            cursor //= 2
            depth += 1
        else:
            raise ValueError("fixed toy depth bound")
        rows, stock = 2**k, 6**depth
        result.append([k, body, depth, rows, stock, rows >= stock, 2 * rows > stock])
    require(
        result
        == [
            [0, 5, 2, 1, 36, False, False],
            [1, 4, 2, 2, 36, False, False],
            [2, 3, 1, 4, 6, False, True],
        ],
        "newly admitted exact toy borrowing profile",
    )
    return result


def run_node(n):
    require(n in (2, 3), "bounded source toy body")
    arena, indices = Arena(3), Arena(8)
    modulus = arena.input(2)
    ring = Ring(modulus)
    catalogue = Catalogue()
    context = Context(ring, catalogue.codes)
    size, depth = indices.input(n), indices.input(0)
    program = object()
    incoming = Incoming(context, indices, (1,) * n)
    consumer = Consumer(context, indices, program, size, depth, catalogue, incoming)
    node = Node(
        context, indices, program, size, depth, Topology(catalogue), consumer, incoming
    )
    old, one, gap = Tape(), Count.literal(1), Count.literal(4)
    before = tuple(bytes(value.cells) for value in (size, depth, incoming.tape, old))

    def callee(source, rows):
        return node.run(source, old, one, rows, one, gap, one)

    try:
        result = case(q=2, n=n, k=2, stock_value=6, callee_factory=callee)
        after = tuple(bytes(value.cells) for value in (size, depth, incoming.tape, old))
        require(before == after, "frozen source metadata unchanged")
        require(
            all(value.head == 1 for value in (size, depth, incoming.tape, old)),
            "frozen source metadata heads restored",
        )
        require(
            consumer.children["enter"] == consumer.children["return"],
            "every actual source child returns before restriction",
        )
        result.update(
            domain="one-family GL2(F2) toy, not selected GL64",
            residuals=dict(consumer.calls),
            children=dict(consumer.children),
        )
        if n == 3:
            result["borrowing_table_e5"] = borrowing_table()
        return result
    finally:
        old.clear()
        one.close()
        gap.close()
        incoming.close()
        indices.free_many(size, depth)
        context.close()
        ring.close()
        arena.free(modulus)
        audit(arena)
        audit(indices)
