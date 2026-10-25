"""Paid two-active-column refinement of the physical inverse-block product.

JoyboyBrian, substantial OpenAI Codex assistance; Apache-2.0.
The original BoundaryPages owner, rounding and pass order remain inherited.
"""
from boundary_pages import BoundaryPages
from cardinal_counts import Count
from compact_counts import copy_bits
from encoded import compare
from ring_words import Signed, add, read_signed, write_signed
from router_metadata import indices, owned
from session import borrowed_tape
from words import BLANK, need


class PairBoundaryPages(BoundaryPages):
    def active_transpose(self, source, destination, block, width, active):
        for column in indices(active):
            source.rewind()
            for _ in indices(block):
                for j in indices(block):
                    with owned(read_signed(source, width)) as (value,):
                        if compare(j, active) >= 0:
                            need(value.magnitude.zero(), 'inactive product columns are zero')
                        if compare(j, column) == 0:
                            write_signed(value, destination, width)
            need(source.read() == BLANK, 'complete two-column matrix')
        source.rewind()
        destination.rewind()

    def product(self, first, second, destination, block, width, wide):
        transposed, row = self.pool.acquire(), self.pool.acquire()
        try:
            with owned(Count.literal(2)) as (two,):
                if compare(block, two) <= 0:
                    # The inherited kernel is already full-width for B=1 or B=2.
                    transposed.clear(); row.clear()
                    return super().product(first, second, destination, block, width, wide)
                self.active_transpose(second, transposed, block, width, two)
                first.rewind()
                for _ in indices(block):
                    with owned(Count.product(block, width)) as (row_bits,):
                        copy_bits(first, row, row_bits)
                    row.rewind()
                    transposed.rewind()
                    for column in indices(block):
                        total = Signed(Count.literal(0))
                        try:
                            if compare(column, two) < 0:
                                for _ in indices(block):
                                    with owned(read_signed(row, width), read_signed(transposed, width)) as (a,b):
                                        with owned(self.arithmetic.multiply(a,b,width)) as (term,):
                                            following = add(total,term)
                                    total.close()
                                    total = following
                                need(row.read() == BLANK, 'complete active scalar row')
                            write_signed(total, destination, wide)
                        finally:
                            total.close()
                            row.rewind()
                    need(transposed.read() == BLANK, 'complete active transpose')
                    borrowed_tape(row).clear()
                need(first.read() == BLANK, 'complete first product matrix')
                self.products += 1
        finally:
            transposed.clear(); row.clear()
            first.rewind(); second.rewind(); destination.rewind()
