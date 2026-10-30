"""Actual Core first-pass binding; no replacement of its old boundary solver."""
from cardinal_counts import Count
from encoded import compare
from gaussian_page import Header, Cell, skip_bits
from router_metadata import indices, owned
from words import BLANK, need


def first_pass_pair(core, page, source):
    """Inside core.scope: return two owned RHS streams and their live Header."""
    header = None
    outputs = []
    success = False
    try:
        page.rewind()
        header = Header(page)
        for component in (0, 1):
            header.repeat(page)
            selected, rhs = core.pool.acquire(), core.pool.acquire()
            outputs.append(rhs)
            try:
                core.gather(source, page, selected, header, component)
                with owned(Count.literal(0), Count.literal(0)) as (rows, boundaries):
                    for _ in indices(header.cell_count):
                        with owned(Cell(page, header)) as (cell,):
                            core.first_cell(selected, page, rhs, cell, header)
                            rows.add(cell.length)
                            boundaries.add(cell.boundary)
                    need(compare(rows, header.m) == 0
                         and compare(boundaries, header.boundary_length) == 0
                         and selected.read() == BLANK, 'complete actual Core first pass')
                skip_bits(page, header.lower_bits)
                skip_bits(page, header.upper_bits)
                need(page.read() == BLANK, 'complete original Core page')
                rhs.rewind()
            finally:
                selected.clear()
        success = True
        return tuple(outputs), header
    finally:
        page.rewind()
        source.rewind()
        if not success:
            for out in outputs:
                out.clear()
            if header is not None:
                header.close()
