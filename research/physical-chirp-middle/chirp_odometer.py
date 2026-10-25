"""Physical lowering of Chafik Boukhalfa's PR479 adjacent-axis schedule."""

from chirp_sources import active
active()
from cardinal_counts import Count, positive
from chirp_packets import validate
from compact_counts import append_bits, bit_at, read_fixed, write_fixed
from encoded import compare, subtract
from parking import Parking
from records import Tape
from ring_words import power_two
from router_metadata import indices, owned
from session import erase_marker, initialize_marker
from words import BLANK, need


def modular_add(left, right, modulus):
    result = Count(left)
    try:
        result.add(right)
        if compare(result, modulus) >= 0:
            following = subtract(result, modulus)
            result.close()
            result = following
        return result
    except BaseException:
        result.close()
        raise


def modular_subtract(left, right, modulus):
    if compare(left, right) >= 0:
        return subtract(left, right)
    with owned(subtract(right, left)) as (difference,):
        return subtract(modulus, difference)


class Odometer:
    """Caller-owned state and a fixed number of borrowed-scope Count leases."""
    def __init__(self):
        self.state, self.row = Tape(), Tape()
        self.parking = Parking((self.row,))
        self.canonical = (self.state, self.row, self.parking.stack, self.parking.reverse)
        self.phase = self.extent = self.plan = None
        self.visits = self.wraps = 0
        for value in self.canonical:
            erase_marker(value)

    def open(self, sources, plan):
        need(self.phase is self.extent is self.plan is None, "closed chirp odometer")
        validate(sources, plan.source_bits, "chirp source packet")
        for value in self.canonical:
            need(value.read() == BLANK, "empty chirp odometer tape")
            initialize_marker(value)
        self.plan = plan
        self.phase, self.extent = Count.literal(0), Count.literal(0)
        sources.rewind()
        plan.flags.rewind()
        try:
            with owned(Count.literal(0), Count.literal(1)) as (zero, one):
                for index in indices(plan.dimensions):
                    last = compare(index, plan.axes) == 0
                    flag = 1 if last else plan.flags.read()
                    need(flag in (0, 1), "complete chirp axis flags")
                    if not last:
                        plan.flags.step(1)
                    with owned(Count(plan.ell) if flag else subtract(plan.ell, one)) as (length,):
                        with owned(power_two(length), read_fixed(sources, plan.ell)) as (radix, source):
                            positive(source)
                            need(compare(source, radix) < 0 and bit_at(source, zero) == 1,
                                 "odd positive chirp source below its radix")
                            if not flag:
                                source.multiply_small(2)
                            with owned(subtract(plan.modulus, source)) as (coefficient,):
                                for value in (radix, zero, zero, coefficient, coefficient):
                                    write_fixed(value, self.row, plan.key_width)
                    self.row.rewind()
                    self.parking.park()
                need(sources.read() == plan.flags.read() == BLANK,
                     "exact chirp source and flag descriptor extents")
                for _ in indices(plan.dimensions):
                    self.parking.restore()
                    append_bits(self.row, self.state)
                    self.row.clear()
                    self.extent.add(plan.state_row_bits)
            self.parking.empty()
            self.state.rewind()
        finally:
            sources.rewind()
            plan.flags.rewind()

    def replace_phase(self, value):
        self.phase.close()
        self.phase = value

    def advance(self):
        need(self.plan is not None and self.phase is not None, "open chirp odometer")
        plan = self.plan
        while self.state.read() != BLANK:
            with owned(*(read_fixed(self.state, plan.key_width) for _ in range(5))) as values:
                radix, index, value, difference, coefficient = values
                self.visits += 1
                index.increment()
                wrapped = compare(index, radix) == 0
                if wrapped:
                    self.replace_phase(modular_subtract(self.phase, value, plan.modulus))
                    following = (Count.literal(0), Count.literal(0), Count(coefficient))
                    self.wraps += 1
                else:
                    need(compare(index, radix) < 0, "chirp coordinate stays within radix")
                    self.replace_phase(modular_add(self.phase, difference, plan.modulus))
                    with owned(modular_add(difference, coefficient, plan.modulus)) as (once,):
                        following = (Count(index), modular_add(value, difference, plan.modulus),
                                     modular_add(once, coefficient, plan.modulus))
                try:
                    # Clear only this fixed-width record, then overwrite it.
                    for _ in indices(plan.state_row_bits):
                        self.state.step(-1)
                        self.state.write(BLANK)
                    for item in (radix, *following, coefficient):
                        write_fixed(item, self.state, plan.key_width)
                finally:
                    for item in following:
                        item.close()
            if not wrapped:
                # Fastest axis is first; this crosses only the visited prefix.
                self.state.rewind()
                return True
        need(self.phase.zero(), "complete chirp rollover restores the global phase")
        self.state.rewind()
        return False

    def close(self):
        if self.plan is None:
            need(self.phase is self.extent is None, "closed chirp odometer leases")
            return
        if self.extent is not None:
            self.state.rewind()
            for _ in indices(self.extent):
                self.state.write(BLANK)
                self.state.step(1)
            self.state.rewind()
            self.extent.close()
        if self.phase is not None:
            self.phase.close()
        self.phase = self.extent = self.plan = None
        for value in self.canonical:
            value.clear()
            erase_marker(value)
