"""Complete normalized real-Gaussian block with the actual word convolution."""
from expansion_sources import active
active()
from cardinal_counts import Count
from encoded import compare, subtract
from expansion_records import BlockHeader
from fft_arithmetic import Arithmetic
from fft_word_engine import FftWord
from gaussian_convolution import Convolution
from gaussian_page import skip_bits
from records import Tape
from ring_words import Signed, read_signed, scaled, truncate, write_signed
from router_metadata import indices, owned
from scratch_pool import ScratchPool
from session import (OuterScope, borrowed_tape, erase_marker, initialize_marker,
                     sealed_constructors)
from words import BLANK, need


class Block:
    def __init__(self):
        self.word = FftWord(base_bits=4096)
        self.convolution = Convolution(self.word)
        self.pool = ScratchPool(256)
        self.scope = OuterScope(self.pool)
        self.arithmetic = Arithmetic(self.word, self.scope)
        self.output = Tape()
        self.closed = True
        self.calls = 0
        for tape in (*self.pool.tapes, self.output):
            erase_marker(tape)

    def idle(self):
        self.convolution.idle()
        need(self.convolution.closed and not self.convolution.pool.live
             and self.convolution.output.read() == BLANK, "consumed expansion convolution return")

    def norm(self, real, imaginary, header):
        with owned(self.arithmetic.multiply(real, real, header.input_width)) as (first,):
            with owned(self.arithmetic.multiply(imaginary, imaginary, header.input_width)) as (second,):
                first.magnitude.add(second.magnitude)
                need(compare(first.magnitude, header.norm_bound) <= 0, "expansion disk-grid packet")

    def factors(self, page, target, length, header):
        for _ in indices(length):
            with owned(read_signed(page, header.width)) as (value,):
                need(not value.negative and compare(value.magnitude, header.unit) <= 0,
                     "nonnegative normalized expansion coefficient")
                write_signed(value, target, header.width)
        target.rewind()

    def scalar(self, source, a, kernel, b, normalization, destination, header, component):
        weighted = returned = None
        source.rewind()
        a.rewind()
        b.rewind()
        try:
            weighted = self.pool.acquire()
            for _ in indices(header.n):
                with owned(read_signed(source, header.input_width)) as (real,):
                    with owned(read_signed(source, header.input_width)) as (imaginary,):
                        if component == 0:
                            self.norm(real, imaginary, header)
                        with owned(scaled(real if component == 0 else imaginary, header.promote)) as (value,):
                            with owned(read_signed(a, header.width)) as (coefficient,):
                                with owned(self.arithmetic.multiply(value, coefficient, header.width)) as (product,):
                                    with owned(truncate(product, header.P)) as (rounded,):
                                        write_signed(rounded, weighted, header.width)
            need(source.read() == a.read() == BLANK, "complete expansion source window and input factors")
            with owned(subtract(header.nc, header.n), Signed(Count.literal(0))) as (padding, zero):
                for _ in indices(padding):
                    write_signed(zero, weighted, header.width)
            weighted.rewind()
            with self.scope.suspended():
                returned = self.convolution.run(weighted, kernel, header.nc, header.width, header.P)
            with owned(Count.literal(1)) as (one,):
                with owned(subtract(header.n, one)) as (prefix,):
                    with owned(Count.product(prefix, header.width)) as (bits,):
                        skip_bits(returned, bits)
            for _ in indices(header.m):
                with owned(read_signed(returned, header.width)) as (value,):
                    with owned(read_signed(b, header.width)) as (coefficient,):
                        with owned(self.arithmetic.multiply(value, coefficient, header.width)) as (product,):
                            with owned(truncate(product, header.P)) as (post_chirp,):
                                with owned(self.arithmetic.multiply(post_chirp, normalization, header.width)) as (product,):
                                    with owned(truncate(product, header.P)) as (fine_normalized,):
                                        with owned(truncate(fine_normalized, header.extract)) as (final,):
                                            write_signed(final, destination, header.input_width)
            need(returned.read() == b.read() == BLANK, "complete cropped expansion output")
            destination.rewind()
        finally:
            if returned is not None:
                returned.clear()
                erase_marker(returned)
            if weighted is not None:
                weighted.clear()
            for value in (source, a, kernel, b):
                value.rewind()

    def run(self, page, source):
        page, source = borrowed_tape(page), borrowed_tape(source)
        forbidden = (*self.pool.tapes, self.output, *self.convolution.pool.tapes,
                     self.convolution.output, *self.word.pool.tapes, self.word.output,
                     *self.word.canonical)
        need(page is not source and page not in forbidden and source not in forbidden,
             "external expansion block ports")
        need(self.closed and not self.pool.live and self.output.read() == BLANK,
             "consume prior expansion block output")
        self.idle()
        for tape in (*self.pool.tapes, self.output):
            initialize_marker(tape)
        self.closed = False
        header = a = kernel = b = normalization = real = imaginary = None
        succeeded = False
        try:
            with sealed_constructors(), self.scope.installed():
                try:
                    page.rewind()
                    header = BlockHeader(page)
                    a, kernel, b, real, imaginary = (self.pool.acquire() for _ in range(5))
                    self.factors(page, a, header.n, header)
                    self.factors(page, kernel, header.nc, header)
                    self.factors(page, b, header.m, header)
                    normalization = read_signed(page, header.width)
                    with owned(Count(header.unit)) as (quarter,):
                        quarter.divide_small(4)
                        need(not normalization.negative and not normalization.magnitude.zero()
                             and compare(normalization.magnitude, quarter) <= 0,
                             "positive normalized expansion reciprocal alpha")
                    need(page.read() == BLANK, "complete expansion page extent")
                    self.scalar(source, a, kernel, b, normalization, real, header, 0)
                    self.scalar(source, a, kernel, b, normalization, imaginary, header, 1)
                    for _ in indices(header.m):
                        with owned(read_signed(real, header.input_width)) as (first,):
                            with owned(read_signed(imaginary, header.input_width)) as (second,):
                                self.norm(first, second, header)
                                write_signed(first, self.output, header.input_width)
                                write_signed(second, self.output, header.input_width)
                    need(real.read() == imaginary.read() == BLANK, "complete normalized complex expansion block")
                    self.idle()
                    self.calls += 1
                    succeeded = True
                finally:
                    for value in (a, kernel, b, real, imaginary):
                        if value is not None:
                            value.clear()
                    if normalization is not None:
                        normalization.close()
                    if header is not None:
                        header.close()
                    page.rewind()
                    source.rewind()
                    self.pool.empty()
        finally:
            for tape in self.pool.tapes:
                erase_marker(tape)
            self.output.rewind()
            if not succeeded:
                self.output.clear()
                erase_marker(self.output)
            self.closed = True
        return self.output
