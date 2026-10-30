# SPDX-License-Identifier: Apache-2.0
"""Encoded signed guard insertion and final truncation toward zero.

I implement PR2287's root grid boundary on the shared tape framework. The
integer truncation convention is retained from selected-conservative-outer.
"""
import cohort
cohort.activate()
from cardinal_counts import Count, positive
from encoded import compare, subtract
from records import Tape
from scratch_pool import ScratchPool
from session import (OuterScope, borrowed_tape, erase_marker, initialize_marker,
                     sealed_constructors)
from stream import Counter
from words import BLANK, LEFT, need


class GridDomainError(ValueError):
    pass


class GridBoundary:
    def __init__(self):
        self.pool = ScratchPool(16)
        self.scope = OuterScope(self.pool)
        self.output = Tape()
        for tape in (*self.pool.tapes, self.output):
            erase_marker(tape)
        self.closed = True

    def _rearm(self):
        need(self.closed and self.output.read() == BLANK and not self.pool.live, "consumed grid boundary")
        self.output.step(-1)
        try:
            need(self.output.read() in (LEFT, BLANK), "grid return origin")
            if self.output.read() == BLANK:
                self.output.write(LEFT)
        finally:
            self.output.step(1)
        for tape in self.pool.tapes:
            initialize_marker(tape)
        self.closed = False

    @staticmethod
    def _digit(source):
        bit = source.read()
        need(bit in (0, 1), "complete signed root word")
        source.step(1)
        return bit

    def _repeat(self, bit, count):
        remaining = Counter(count)
        try:
            while not remaining.finished:
                self.output.append(bit)
                remaining.decrement()
        finally:
            remaining.close()

    def _expanded_component(self, source, width, low, high):
        self._repeat(0, low)
        remaining = Counter(width)
        sign = 0
        try:
            while not remaining.finished:
                sign = self._digit(source)
                self.output.append(sign)
                remaining.decrement()
        finally:
            remaining.close()
        self._repeat(sign, high)

    def _truncated_component(self, source, width, low, result_width, kept, buffer):
        remaining = Counter(low)
        sticky = False
        try:
            while not remaining.finished:
                sticky = bool(self._digit(source)) or sticky
                remaining.decrement()
        finally:
            remaining.close()
        remaining = Counter(kept)
        sign = 0
        try:
            while not remaining.finished:
                sign = self._digit(source)
                buffer.append(sign)
                remaining.decrement()
        finally:
            remaining.close()
        buffer.rewind()
        if sign and sticky:
            remaining = Counter(kept)
            carry = 1
            try:
                while not remaining.finished:
                    bit = buffer.read()
                    need(bit in (0, 1), "complete signed quotient")
                    total = bit + carry
                    buffer.write(total & 1)
                    carry = total >> 1
                    buffer.step(1)
                    remaining.decrement()
                need(buffer.read() == BLANK, "exact signed quotient width")
            finally:
                remaining.close()
                buffer.rewind()
        incoming, outgoing = Counter(kept), Counter(result_width)
        output_sign = sign = 0
        try:
            while not incoming.finished:
                sign = buffer.read()
                need(sign in (0, 1), "rounded quotient digit")
                if not outgoing.finished:
                    self.output.append(sign)
                    output_sign = sign
                    outgoing.decrement()
                elif sign != output_sign:
                    raise GridDomainError("truncated root signed headroom")
                buffer.step(1)
                incoming.decrement()
            need(buffer.read() == BLANK, "complete rounded quotient")
            while not outgoing.finished:
                self.output.append(sign)
                outgoing.decrement()
        finally:
            incoming.close()
            outgoing.close()
            borrowed_tape(buffer).clear()

    def _run(self, payload, width, low, final_parameter, gaussians, truncate):
        for value in (width, gaussians):
            positive(value)
        need(isinstance(low, Count) and isinstance(final_parameter, Count), "encoded root grid parameters")
        source = borrowed_tape(payload)
        need(source is not self.output and source not in self.pool.tapes, "borrowed grid input")
        self._rearm()
        two = components = remaining = kept = None
        buffer = None
        failure = None
        source.rewind()
        try:
            with sealed_constructors(), self.scope.installed():
                try:
                    two = Count.literal(2)
                    need(compare(width, two) >= 0, "signed root input width")
                    if truncate:
                        need(compare(final_parameter, two) >= 0 and compare(low, width) < 0,
                             "signed root output and retained sign")
                        kept = subtract(width, low)
                        buffer = self.pool.acquire()
                    components = Count(gaussians)
                    components.multiply_small(2)
                    remaining = Counter(components)
                    while not remaining.finished:
                        if truncate:
                            self._truncated_component(source, width, low, final_parameter, kept, buffer)
                        else:
                            self._expanded_component(source, width, low, final_parameter)
                        remaining.decrement()
                    need(source.read() == BLANK, "complete root grid packet")
                finally:
                    if buffer is not None:
                        buffer.clear()
                    for value in (two, components, remaining, kept):
                        if value is not None:
                            value.close()
                    self.pool.empty()
        except ValueError as error:
            failure = error
        finally:
            source.rewind()
            for tape in self.pool.tapes:
                erase_marker(tape)
            self.output.rewind()
            self.closed = True
        if failure is not None:
            self.output.clear()
            erase_marker(self.output)
            raise failure
        return self.output

    def expand(self, payload, width, low_zeros, high_signs, gaussians):
        return self._run(payload, width, low_zeros, high_signs, gaussians, False)

    def truncate(self, payload, width, discarded_bits, output_bits, gaussians):
        return self._run(payload, width, discarded_bits, output_bits, gaussians, True)
