"""Actual rounded-block return through the unchanged Gaussian second pass.
JoyboyBrian, substantial OpenAI Codex assistance; Apache-2.0.
"""
from cardinal_counts import Count
from encoded import compare
from gaussian_core import Core
from gaussian_page import Header, Cell, skip_bits
from pair_kernel import PairBoundaryPages
from rhs_layout import pack, unpack
from ring_words import read_signed, write_signed
from router_metadata import indices, owned
from session import borrowed_tape, initialize_marker, erase_marker, sealed_constructors
from words import BLANK, need


class BlockCore(Core):
    def __init__(self, retain=True):
        super().__init__()
        self.blocks = PairBoundaryPages()
        self.retain = retain  # Fixed public schedule, never decoded payload.

    def run(self, page, source, factor_pages, block):
        page, source = borrowed_tape(page), borrowed_tape(source)
        pages = tuple(borrowed_tape(t) for t in factor_pages)
        ports = (page, source, *pages)
        owners = (self, self.interior, self.interior.convolution, self.boundary,
                  self.word, self.blocks, self.blocks.word)
        forbidden = tuple(t for owner in owners for t in (*owner.pool.tapes, owner.output))
        need(len(pages) == 4 and len({id(t) for t in ports}) == 6
             and all(t not in forbidden and t not in self.word.canonical
                     and t not in self.blocks.word.canonical for t in ports)
             and borrowed_tape(block.tape) not in ports
             and all(t.head == 1 for t in ports), 'canonical external block Core ports')
        need(self.closed and not self.pool.live and self.output.read() == BLANK,
             'consume prior block Core output')
        self.idle(); self.blocks.idle()
        for t in (*self.pool.tapes, self.output): initialize_marker(t)
        self.closed = False
        header = packed = returned = None
        selecteds, rhs, solutions, results = [], [], [], []
        succeeded = False
        try:
            with sealed_constructors(), self.scope.installed():
                try:
                    header = Header(page)
                    for component in (0, 1):
                        header.repeat(page)
                        selecteds.append(self.pool.acquire()); rhs.append(self.pool.acquire())
                        self.gather(source, page, selecteds[-1], header, component)
                        with owned(Count.literal(0), Count.literal(0)) as (rows, boundaries):
                            for _ in indices(header.cell_count):
                                with owned(Cell(page, header)) as (cell,):
                                    self.first_cell(selecteds[-1], page, rhs[-1], cell, header)
                                    rows.add(cell.length); boundaries.add(cell.boundary)
                            need(compare(rows, header.m) == 0 and compare(boundaries, header.boundary_length) == 0
                                 and selecteds[-1].read() == BLANK, 'complete first block Core cell pass')
                        skip_bits(page, header.lower_bits); skip_bits(page, header.upper_bits)
                        need(page.read() == BLANK, 'complete first block Core page')
                        selecteds[-1].rewind(); rhs[-1].rewind()
                        if not self.retain: selecteds.pop().clear()
                    packed = pack(*rhs, header.boundary_length, block, header.width, self.pool)
                    with owned(Count.literal(2)) as (two,):
                        with self.scope.suspended():
                            returned = self.blocks.run(*pages, packed, header.boundary_length,
                                                       two, block, header.width, header.P)
                    solutions.extend(unpack(returned, header.boundary_length, block, header.width, self.pool))
                    returned.clear(); erase_marker(returned); returned = None
                    packed.clear(); packed = None
                    for t in rhs: t.clear()
                    rhs.clear()
                    for component in (0, 1):
                        header.repeat(page)
                        if self.retain:
                            selected = selecteds[component]
                            header.skip_selection(page)
                        else:
                            selected = self.pool.acquire(); selecteds.append(selected)
                            self.gather(source, page, selected, header, component)
                        results.append(self.pool.acquire())
                        with owned(Count.literal(0), Count.literal(0)) as (position, emitted):
                            for _ in indices(header.cell_count):
                                with owned(Cell(page, header)) as (cell,):
                                    self.second_cell(selected, solutions[component], page, results[-1],
                                                     position, emitted, cell, header)
                            need(compare(position, header.m) == 0 and compare(emitted, header.core_length) == 0
                                 and selected.read() == solutions[component].read() == BLANK,
                                 'complete second block Core pass and crop')
                        skip_bits(page, header.lower_bits); skip_bits(page, header.upper_bits)
                        need(page.read() == BLANK, 'complete second block Core page')
                        results[-1].rewind()
                        selected.clear(); solutions[component].clear()
                    for _ in indices(header.core_length):
                        with owned(read_signed(results[0], header.input_width),
                                   read_signed(results[1], header.input_width)) as (real, imaginary):
                            self.norm(real, imaginary, header)
                            write_signed(real, self.output, header.input_width)
                            write_signed(imaginary, self.output, header.input_width)
                    need(all(t.read() == BLANK for t in results), 'complete normalized complex block return')
                    self.idle(); self.blocks.idle()
                    self.calls += 1; succeeded = True
                finally:
                    if returned is not None: returned.clear(); erase_marker(returned)
                    for t in (*selecteds, *rhs, *solutions, *results): t.clear()
                    if packed is not None: packed.clear()
                    if header is not None: header.close()
                    for t in ports: t.rewind()
                    self.pool.empty()
        finally:
            for t in self.pool.tapes: erase_marker(t)
            self.output.rewind()
            if not succeeded: self.output.clear(); erase_marker(self.output)
            self.closed = True
        return self.output
