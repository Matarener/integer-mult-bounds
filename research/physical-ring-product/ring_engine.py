"""Complete physical normalized Gaussian polynomial products via DIF/DIT FFTs."""

from ring_sources import active
active()
from cardinal_counts import Count
from compact_counts import append_bits, copy_bits
from encoded import compare, subtract
from fft_arithmetic import Arithmetic
from product_plan import ProductPlan
from records import Tape
from ring_words import difference, nearest, read_signed, truncate, write_signed
from router_metadata import indices, owned
from scratch_pool import ScratchPool
from session import (OuterScope, borrowed_count, borrowed_tape, erase_marker,
                     initialize_marker, sealed_constructors)
from twiddle_setup import Twiddles
from word_product import WordProduct
from words import BLANK, need


class RingProduct:
    def __init__(self):
        self.word = WordProduct()
        self.twiddles = Twiddles()
        self.pool = ScratchPool(256)
        self.scope = OuterScope(self.pool)
        self.arithmetic = Arithmetic(self.word, self.scope)
        self.output = Tape()
        self.a = self.b = self.current = None
        self.closed = True
        self.calls = dict(stages=0, tables=0, pointwise=0, recoveries=0)
        for item in (*self.pool.tapes, self.output):
            erase_marker(item)

    def idle(self):
        need(self.word.closed and not self.word.pool.live and self.word.output.read() == BLANK
             and all(t.read() == BLANK for t in self.word.canonical)
             and self.twiddles.closed and not self.twiddles.pool.live
             and self.twiddles.output.read() == BLANK, "closed product arithmetic children")

    def rearm(self):
        need(self.closed and self.a is self.b is self.current is None and not self.pool.live
             and self.output.read() == BLANK, "consume prior normalized-product output")
        self.idle()
        for item in (*self.pool.tapes, self.output):
            initialize_marker(item)
        self.closed = False

    def table(self, plan, length, opposite):
        self.idle()
        with self.scope.suspended():
            returned = self.twiddles.run(borrowed_count(plan.Q), borrowed_count(length), opposite)
        result = self.pool.acquire()
        try:
            append_bits(returned, result)
            result.rewind()
            self.calls["tables"] += 1
            return result
        except BaseException:
            result.clear()
            raise
        finally:
            returned.clear()
            erase_marker(returned)

    def lift_and_pad(self, source, plan):
        output = self.pool.acquire()
        source.rewind()
        try:
            for _ in indices(plan.records):
                for _ in indices(plan.r):
                    for _ in range(2):
                        for _ in indices(plan.lift):
                            output.append(0)
                        copy_bits(source, output, plan.small)
                with owned(Count.product(plan.r, plan.wide)) as (zeros,):
                    zeros.multiply_small(2)
                    for _ in indices(zeros):
                        output.append(0)
            need(source.read() == BLANK, "complete normalized-product input packet")
            output.rewind()
            return output
        except BaseException:
            output.clear()
            raise
        finally:
            source.rewind()

    def stage(self, source, table, plan, length, opposite):
        output, left, top, bottom = (self.pool.acquire() for _ in range(4))
        half, groups = Count(length), Count(plan.N)
        half.divide_small(2)
        with owned(Count(length)) as (divisor,):
            while not divisor.zero():
                remainder = divisor.divide_small(2)
                if divisor.zero():
                    need(remainder == 1, "dyadic FFT group length")
                    break
                need(remainder == 0, "dyadic FFT group length")
                groups.divide_small(2)
        source.rewind()
        try:
            with owned(Count.product(half, plan.wide)) as (half_bits,):
                half_bits.multiply_small(2)
                for _ in indices(plan.records):
                    for _ in indices(groups):
                        copy_bits(source, left, half_bits)
                        left.rewind()
                        table.rewind()
                        for _ in indices(half):
                            with owned(read_signed(left, plan.wide), read_signed(left, plan.wide),
                                       read_signed(source, plan.wide), read_signed(source, plan.wide),
                                       read_signed(table, plan.wide), read_signed(table, plan.wide)) as values:
                                results = (self.arithmetic.dit(*values, plan) if opposite
                                           else self.arithmetic.dif(*values, plan))
                                try:
                                    write_signed(results[0], top, plan.wide)
                                    write_signed(results[1], top, plan.wide)
                                    write_signed(results[2], bottom, plan.wide)
                                    write_signed(results[3], bottom, plan.wide)
                                finally:
                                    for value in results:
                                        value.close()
                        need(left.read() == table.read() == BLANK, "complete FFT half and twiddle table")
                        append_bits(top, output)
                        append_bits(bottom, output)
                        for buffer in (left, top, bottom):
                            borrowed_tape(buffer).clear()
                need(source.read() == BLANK, "complete sequential FFT packet")
            source.clear()
            output.rewind()
            self.calls["stages"] += 1
            return output
        except BaseException:
            output.clear()
            raise
        finally:
            for buffer in (left, top, bottom):
                buffer.clear()
            half.close()
            groups.close()
            table.rewind()

    def fft(self, source, plan, opposite):
        current = source
        length = Count.literal(2) if opposite else Count(plan.N)
        try:
            for _ in indices(plan.m):
                table = self.table(plan, length, opposite)
                try:
                    current = self.stage(current, table, plan, length, opposite)
                finally:
                    table.clear()
                if opposite:
                    length.multiply_small(2)
                else:
                    length.divide_small(2)
            return current
        except BaseException:
            current.clear()
            raise
        finally:
            length.close()

    def pointwise(self, first, second, plan):
        output = self.pool.acquire()
        first.rewind()
        second.rewind()
        try:
            for _ in indices(plan.fft_gaussians):
                with owned(read_signed(first, plan.wide), read_signed(first, plan.wide),
                           read_signed(second, plan.wide), read_signed(second, plan.wide)) as values:
                    with owned(*self.arithmetic.pointwise(*values, plan)) as result:
                        for value in result:
                            write_signed(value, output, plan.wide)
            need(first.read() == second.read() == BLANK, "matching complete frequency packets")
            first.clear()
            second.clear()
            output.rewind()
            self.calls["pointwise"] += 1
            return output
        except BaseException:
            output.clear()
            raise

    def recover(self, source, plan):
        output, low = self.pool.acquire(), self.pool.acquire()
        source.rewind()
        try:
            with owned(Count.literal(1)) as (one,):
                with owned(subtract(plan.r, one)) as (last,):
                    for _ in indices(plan.records):
                        for _ in indices(plan.r):
                            for _ in range(2):
                                with owned(read_signed(source, plan.wide)) as (value,):
                                    with owned(nearest(value, plan.recovery_shift)) as (integer,):
                                        write_signed(integer, low, plan.integer_width)
                        low.rewind()
                        for index in indices(plan.r):
                            for _ in range(2):
                                with owned(read_signed(source, plan.wide),
                                           read_signed(low, plan.integer_width)) as (value, lower):
                                    with owned(nearest(value, plan.recovery_shift)) as (upper,):
                                        if compare(index, last) == 0:
                                            need(upper.magnitude.zero(), "zero final ordinary-convolution coefficient")
                                        with owned(difference(lower, upper)) as (wrapped,):
                                            with owned(truncate(wrapped, plan.product_shift)) as (result,):
                                                write_signed(result, output, plan.small)
                        need(low.read() == BLANK, "complete recovered lower polynomial half")
                        borrowed_tape(low).clear()
            need(source.read() == BLANK, "complete integer recovery packet")
            source.clear()
            output.rewind()
            self.calls["recoveries"] += 1
            return output
        except BaseException:
            output.clear()
            raise
        finally:
            low.clear()

    def run(self, first, second, dimension, precision, ell, rows):
        first, second = borrowed_tape(first), borrowed_tape(second)
        need(first is not second and first is not self.output and second is not self.output,
             "distinct borrowed normalized-product packets")
        self.rearm()
        plan = None
        succeeded = False
        try:
            with sealed_constructors(), self.scope.installed():
                try:
                    plan = ProductPlan(dimension, precision, ell, rows)
                    plan.compile()
                    self.a = self.lift_and_pad(first, plan)
                    self.b = self.lift_and_pad(second, plan)
                    self.a = self.fft(self.a, plan, False)
                    self.b = self.fft(self.b, plan, False)
                    self.current = self.pointwise(self.a, self.b, plan)
                    self.a = self.b = None
                    self.current = self.fft(self.current, plan, True)
                    self.current = self.recover(self.current, plan)
                    self.idle()
                    append_bits(self.current, self.output)
                    succeeded = True
                finally:
                    first.rewind()
                    second.rewind()
                    for value in (dimension, precision, ell, rows):
                        value.rewind()
                    for value in (self.a, self.b, self.current):
                        if value is not None:
                            value.clear()
                    self.a = self.b = self.current = None
                    if plan is not None:
                        plan.close()
                    self.pool.empty()
        finally:
            for item in self.pool.tapes:
                erase_marker(item)
            self.output.rewind()
            if not succeeded:
                self.output.clear()
                erase_marker(self.output)
            self.closed = True
        return self.output
