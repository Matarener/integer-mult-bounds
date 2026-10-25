# SPDX-License-Identifier: Apache-2.0
"""Complete owner-packet acquisition and replacement on one sequential bank.

I extend PR3106's bank access to a finite selected packet set and arbitrary
encoded outer prefixes. The predecessor tape/count operations retain credit.
"""
import cohort
cohort.activate()
from cardinal_counts import Count, positive
from compact_counts import append_bits, copy_bits
from records import Tape
from scratch_pool import ScratchPool
from session import (OuterScope, borrowed_tape, erase_marker, initialize_marker,
                     sealed_constructors)
from stream import Counter
from words import BLANK, LEFT, need


def arm_empty(tape):
    need(tape.read() == BLANK, "empty owned packet port")
    tape.step(-1)
    try:
        need(tape.read() in (LEFT, BLANK), "owned packet origin")
        if tape.read() == BLANK:
            tape.write(LEFT)
    finally:
        tape.step(1)


def skip(source, extent):
    remaining = Counter(extent)
    try:
        while not remaining.finished:
            need(source.read() in (0, 1), "complete skipped packet")
            source.step(1)
            remaining.decrement()
    finally:
        remaining.close()


class BankPackets:
    """Layout: prefix, family, cover, unused row, complete within-row packet.

Family/cover alphabets and slot count are fixed before input. Prefix count,
unused rows and within-row extent remain encoded Counts. No numerical array
index, decoded length or per-row tape allocation appears in the scans.
"""
    def __init__(self, families, covers, slots):
        need(type(families) is int and families > 0 and type(covers) is int and covers > 0
             and type(slots) is int and 0 < slots <= families * covers,
             "fixed finite bank alphabet")
        self.families, self.covers, self.slots = families, covers, slots
        self.packets = tuple(Tape() for _ in range(slots))
        self.output = Tape()
        self.pool = ScratchPool(16)
        self.scope = OuterScope(self.pool)
        for tape in (*self.packets, self.output, *self.pool.tapes):
            erase_marker(tape)
        self.selection = None
        self.source = None
        self.state = "closed"

    def select(self, keys):
        need(self.state == "closed" and not self.pool.live and
             all(t.read() == BLANK for t in (*self.packets, self.output)), "closed bank selection")
        need(type(keys) is tuple and 0 < len(keys) <= self.slots and len(set(keys)) == len(keys),
             "distinct compiled owner slots")
        need(all(type(key) is tuple and len(key) == 2 and
                 type(key[0]) is int and 0 <= key[0] < self.families and
                 type(key[1]) is int and 0 <= key[1] < self.covers for key in keys),
             "owner keys in fixed alphabet")
        self.selection = {key: slot for slot, key in enumerate(keys)}

    def _start_scratch(self):
        need(not self.pool.live, "empty packet scratch")
        for tape in self.pool.tapes:
            initialize_marker(tape)

    def _close_scratch(self):
        self.pool.empty()
        for tape in self.pool.tapes:
            erase_marker(tape)

    def gather(self, bank, prefixes, unused_rows, row_bits):
        need(self.state == "closed" and self.selection is not None, "compiled acquisition boundary")
        for count in (prefixes, unused_rows, row_bits):
            positive(count)
        source = borrowed_tape(bank)
        need(source not in (*self.packets, self.output, *self.pool.tapes), "distinct borrowed bank")
        for tape in self.packets:
            arm_empty(tape)
        self._start_scratch()
        extent = remaining = None
        self.source = source
        source.rewind()
        try:
            with sealed_constructors(), self.scope.installed():
                try:
                    extent = Count.product(unused_rows, row_bits)
                    remaining = Counter(prefixes)
                    while not remaining.finished:
                        for family in range(self.families):
                            for cover in range(self.covers):
                                slot = self.selection.get((family, cover))
                                if slot is None:
                                    skip(source, extent)
                                else:
                                    copy_bits(source, self.packets[slot], extent)
                        remaining.decrement()
                    need(source.read() == BLANK, "complete acquisition bank")
                finally:
                    for value in (extent, remaining):
                        if value is not None:
                            value.close()
            for tape in self.packets:
                tape.rewind()
            self.state = "gathered"
            return self.packets
        except BaseException:
            for tape in self.packets:
                tape.clear()
                erase_marker(tape)
            self.source = None
            raise
        finally:
            source.rewind()
            self._close_scratch()

    def scatter(self, bank, prefixes, unused_rows, row_bits):
        source = borrowed_tape(bank)
        need(self.state == "gathered" and source is self.source,
             "replace the acquired current bank")
        for count in (prefixes, unused_rows, row_bits):
            positive(count)
        need(self.output.read() == BLANK, "consume earlier replacement")
        arm_empty(self.output)
        self._start_scratch()
        extent = remaining = None
        source.rewind()
        for tape in self.packets:
            tape.rewind()
        try:
            with sealed_constructors(), self.scope.installed():
                try:
                    extent = Count.product(unused_rows, row_bits)
                    remaining = Counter(prefixes)
                    while not remaining.finished:
                        for family in range(self.families):
                            for cover in range(self.covers):
                                slot = self.selection.get((family, cover))
                                if slot is None:
                                    copy_bits(source, self.output, extent)
                                else:
                                    skip(source, extent)
                                    copy_bits(self.packets[slot], self.output, extent)
                        remaining.decrement()
                    need(source.read() == BLANK and all(t.read() == BLANK for t in self.packets),
                         "complete replacement and local packet extents")
                finally:
                    for value in (extent, remaining):
                        if value is not None:
                            value.close()
            self.output.rewind()
            self.state = "returned"
            return self.output
        except BaseException:
            self.output.clear()
            erase_marker(self.output)
            raise
        finally:
            source.rewind()
            for tape in self.packets:
                tape.rewind()
            self._close_scratch()

    def commit(self, bank):
        """Caller authorizes destructive replacement of its owned current bank."""
        target = borrowed_tape(bank)
        need(self.state == "returned" and target is self.source and self.output.read() in (0, 1),
             "complete current-bank return before commit")
        target.clear()
        append_bits(self.output, target)
        target.rewind()
        self.output.clear()
        erase_marker(self.output)
        self.release()

    def release(self):
        need(self.output.read() == BLANK and not self.pool.live, "consume bank return before release")
        for tape in self.packets:
            tape.clear()
            erase_marker(tape)
        self.source = None
        self.state = "closed"
