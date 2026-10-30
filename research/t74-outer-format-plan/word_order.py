# SPDX-License-Identifier: Apache-2.0
"""Reverse each complete signed component using the retained tape cohort."""

import cohort

cohort.activate()
from cardinal_counts import Count, positive
from encoded import compare
from records import Tape
from scratch_pool import ScratchPool
from session import (
    OuterScope,
    borrowed_tape,
    erase_marker,
    initialize_marker,
    sealed_constructors,
)
from stream import Counter
from words import BLANK, LEFT, need


class WordOrderBridge:
    """Borrow a complete Gaussian packet and return its per-word reversal."""

    def __init__(self):
        self.pool = ScratchPool(8)
        self.scope = OuterScope(self.pool)
        self.output = Tape()
        for tape in (*self.pool.tapes, self.output):
            erase_marker(tape)
        self.closed = True

    def _component(self, source, buffer, width):
        remaining = Counter(width)
        try:
            while not remaining.finished:
                bit = source.read()
                need(bit in (0, 1), "complete signed bridge component")
                buffer.append(bit)
                source.step(1)
                remaining.decrement()
        finally:
            remaining.close()
        remaining = Counter(width)
        try:
            while not remaining.finished:
                buffer.step(-1)
                bit = buffer.read()
                need(bit in (0, 1), "bridge reverse buffer")
                self.output.append(bit)
                remaining.decrement()
        finally:
            remaining.close()
            borrowed_tape(buffer).clear()

    def run(self, payload, width, gaussians):
        positive(width)
        positive(gaussians)
        source = borrowed_tape(payload)
        need(
            source is not self.output and source not in self.pool.tapes,
            "borrowed bridge input",
        )
        need(
            self.closed and self.output.read() == BLANK and not self.pool.live,
            "consumed bridge output",
        )
        self.output.step(-1)
        need(self.output.read() in (LEFT, BLANK), "bridge return origin")
        self.output.write(LEFT)
        self.output.step(1)
        for tape in self.pool.tapes:
            initialize_marker(tape)
        self.closed = False
        source.rewind()
        two = components = remaining = buffer = None
        succeeded = False
        try:
            with sealed_constructors(), self.scope.installed():
                two = Count.literal(2)
                need(compare(width, two) >= 0, "signed bridge width")
                components = Count(gaussians)
                components.multiply_small(2)
                remaining = Counter(components)
                buffer = self.pool.acquire()
                while not remaining.finished:
                    self._component(source, buffer, width)
                    remaining.decrement()
                need(source.read() == BLANK, "complete bridge packet")
            succeeded = True
            return self.output
        finally:
            if buffer is not None:
                buffer.clear()
            for value in (two, components, remaining):
                if value is not None:
                    value.close()
            self.pool.empty()
            source.rewind()
            for tape in self.pool.tapes:
                erase_marker(tape)
            self.output.rewind()
            if not succeeded:
                self.output.clear()
                erase_marker(self.output)
            self.closed = True
