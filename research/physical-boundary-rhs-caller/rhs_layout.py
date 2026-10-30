"""Physical two-component Gaussian RHS layout. JoyboyBrian / Codex; Apache-2.0."""
from cardinal_counts import Count, positive
from encoded import compare
from boundary_pages import ceiling_division
from router_metadata import indices, owned
from session import borrowed_tape
from words import BLANK, need


def bit_scan(source, width, destination=None, zero=False):
    for _ in indices(width):
        value = source.read()
        need(value in (0, 1) and (not zero or value == 0), 'literal RHS bits and zero padding')
        if destination is not None:
            destination.append(value)
        source.step(1)


def zeros(destination, width):
    for _ in indices(width):
        destination.append(0)


def validate(ports, metadata):
    physical = [borrowed_tape(t) for t in ports]
    need(len({id(t) for t in physical}) == len(physical), 'distinct layout payload ports')
    need(all(t.head == 1 for t in physical), 'canonical layout entry heads')
    need(all(borrowed_tape(c.tape) not in physical for c in metadata), 'separate layout metadata')
    for c in metadata:
        positive(c)
    return physical


def pack(real, imaginary, rows, block, width, pool):
    """Borrow two n-record streams; return one owned padded batch stream."""
    sources = validate((real, imaginary), (rows, block, width))
    output = pool.acquire()
    success = False
    try:
        with owned(Count.literal(2), ceiling_division(rows, block)) as (two, blocks):
            with owned(ceiling_division(two, block), Count.product(blocks, block)) as (batches, padded):
                for batch in indices(batches):
                    for source in sources:
                        source.rewind()
                    with owned(Count.product(batch, block)) as (start,):
                        for row in indices(padded):
                            for offset in indices(block):
                                with owned(Count(start)) as (column,):
                                    column.add(offset)
                                    if compare(row, rows) < 0 and compare(column, two) < 0:
                                        bit_scan(sources[0] if column.zero() else sources[1], width, output)
                                    else:
                                        zeros(output, width)
                    # At B=1 the unselected component still needs a complete extent check.
                    for source in sources:
                        source.rewind()
                        for _ in indices(rows):
                            bit_scan(source, width)
                        need(source.read() == BLANK, 'complete component RHS extent')
                        source.rewind()
        output.rewind()
        success = True
        return output
    finally:
        for source in sources:
            source.rewind()
        if not success:
            output.clear()


def unpack(source, rows, block, width, pool):
    """Borrow a protected return; recover two owned scalar RHS streams."""
    source, = validate((source,), (rows, block, width))
    outputs = []
    success = False
    try:
        outputs.append(pool.acquire())
        outputs.append(pool.acquire())
        source.rewind()
        with owned(Count.literal(2), ceiling_division(rows, block)) as (two, blocks):
            with owned(ceiling_division(two, block), Count.product(blocks, block)) as (batches, padded):
                for batch in indices(batches):
                    with owned(Count.product(batch, block)) as (start,):
                        for row in indices(padded):
                            for offset in indices(block):
                                with owned(Count(start)) as (column,):
                                    column.add(offset)
                                    if compare(row, rows) < 0 and compare(column, two) < 0:
                                        bit_scan(source, width, outputs[0] if column.zero() else outputs[1])
                                    else:
                                        bit_scan(source, width, zero=True)
        need(source.read() == BLANK, 'complete padded RHS return extent')
        for out in outputs:
            out.rewind()
        success = True
        return tuple(outputs)
    finally:
        source.rewind()
        if not success:
            for out in outputs:
                out.clear()
