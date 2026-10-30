# SPDX-License-Identifier: Apache-2.0
"""One active complex node and a physical stack of parent continuations.

I adapt PR2809's finite-PC protocol to Count descriptors and Gaussian packets.
The selected binding supplies finite source groups; it never receives payloads.
"""
import cohort
api = cohort.activate()
from bank_packets import BankPackets, skip
from cardinal_counts import Count, positive
from compact_counts import power_two
from encoded import compare, divide, fixed_power, subtract
from monomial_packets import MonomialPackets
from parking import BODY, FiniteFields, Parking, transfer
from records import Tape
from scalar_packets import FullScalarEngine
from scalar_words import require_zero
from scratch_pool import ScratchPool
from session import (OuterScope, borrowed_count, borrowed_tape, erase_marker,
                     initialize_marker, sealed_constructors)
from stream import Counter
from words import BLANK, LEFT, need

INPUTS = ("prefixes", "rows", "front", "compact_bits", "before", "width", "after", "back",
          "spacing", "guard", "residue", "component_bits", "coefficients", "root_width")
DERIVED = ("columns", "unused", "row_bits", "gaussians")
LEAF_NAMES = ("front", "u", "t", "before", "active", "after", "b", "back")


def origin(tape):
    """Rearm an owned marker at a known canonical head, preserving its body."""
    tape.step(-1)
    try:
        need(tape.read() in (LEFT, BLANK), "canonical owned origin")
        if tape.read() == BLANK:
            tape.write(LEFT)
    finally:
        tape.step(1)


def copy_symbols(source, target):
    source = borrowed_tape(source)
    need(source is not target, "distinct preserved-copy ports")
    source.rewind()
    target.clear()
    while source.read() != BLANK:
        symbol = source.read()
        need(symbol in BODY, "dense copied role")
        target.append(symbol)
        source.step(1)
    source.rewind()
    target.rewind()


class Machine:
    def __init__(self, binding, native, catalogue, observe=None):
        self.binding = binding
        self.bank = BankPackets(binding.families, binding.cover.size, binding.slots)
        self.private = tuple(Tape() for _ in range(binding.private))
        self.roles = {name: Tape() for name in ("current", "header", *INPUTS, *DERIVED)}
        self.capsule = {name: Tape() for name in ("current", *INPUTS)}
        self.output = Tape()
        self.pool = ScratchPool(256)
        self.scope = OuterScope(self.pool)
        self.scalar = FullScalarEngine(catalogue)
        self.leaf = api["coefficient_engine"].CoefficientEngine(LEAF_NAMES, "active")
        vectors = tuple("v" + str(i) for i in range(binding.dimension))
        names = ("front", "u0", "u", "t0", "t", "before", *vectors, "after", "b0", "b", "back")
        self.monomial = MonomialPackets(names, vectors, native)
        self.parked = (*self.roles.values(), *self.bank.packets, *self.private)
        self.parking = Parking(self.parked)
        groups = max(1, *(binding.group_count(i) for i in range(len(binding.events))))
        self.header = FiniteFields((2, len(binding.events), groups, binding.cover.size,
                                   65536, binding.slots + binding.private, binding.dimension))
        self.root = True
        self.event = self.subgroup = self.cover_index = self.pc = 0
        self.group = None
        self.mode = "closed"
        self.closed = True
        self.observe = observe  # Checker-only. Its return value never affects execution.

    def c(self, name):
        value = object.__new__(Count)
        value.tape = self.roles[name]
        return value

    def save(self, value, name):
        try:
            transfer(value.tape, self.roles[name])
        finally:
            value.close()

    def packet(self, index):
        need(type(index) is int and 0 <= index < self.binding.slots + self.binding.private,
             "compiled packet role")
        return self.bank.packets[index] if index < self.binding.slots else self.private[index - self.binding.slots]

    def primitive_boundary(self):
        self.pool.empty()
        need(self.scalar.closed and not self.scalar.pool.live and self.scalar.output.read() == BLANK,
             "scalar closes before recursive cut")
        need(self.leaf.closed and not self.leaf.pool.live and self.leaf.output.read() == BLANK,
             "leaf closes before recursive cut")
        need(self.monomial.closed and not self.monomial.pool.live and self.monomial.output.read() == BLANK
             and self.monomial.compact.closed and self.monomial.compact.binary.native.closed,
             "monomial closes before recursive cut")

    def shape(self):
        active = Count.product(self.c("width"), self.c("spacing"))
        bits = Count(self.c("compact_bits"))
        records = row_bits = None
        try:
            bits.multiply_small(3)
            for name in ("front", "before", "after", "back"):
                bits.add(self.c(name))
            bits.add(active)
            records = power_two(bits)
            row_bits = Count.product(records, self.c("coefficients"))
            expanded = Count.product(row_bits, self.c("component_bits"))
            expanded.multiply_small(2)
            self.save(expanded, "row_bits")
        finally:
            for value in (active, bits, records, row_bits):
                if value is not None:
                    value.close()

    def complete_extent(self):
        rows = Count.product(self.c("prefixes"), self.c("rows"))
        try:
            return Count.product(rows, self.c("row_bits"))
        finally:
            rows.close()

    def apply_leaf(self, width, before, after):
        if width.zero():
            return
        active = Count.product(width, self.c("spacing"))
        rows = Count.product(self.c("prefixes"), self.c("rows"))
        widths = tuple(Count(v) for v in (self.c("front"), self.c("compact_bits"), self.c("compact_bits"),
                                        before, active, after, self.c("compact_bits"), self.c("back")))
        try:
            with self.scope.suspended():
                returned = self.leaf.run_leaf(self.roles["current"], tuple(borrowed_count(v) for v in widths),
                    *(borrowed_count(v) for v in (width, self.c("spacing"), self.c("residue"),
                      self.c("component_bits"), self.c("coefficients"), rows)))
            transfer(returned, self.roles["current"])
            erase_marker(returned)
        finally:
            for value in (*widths, active, rows):
                value.close()

    def node(self):
        dimension = Count.literal(self.binding.dimension)
        test = extent = columns = removed = rest = suffix = shift = divisor = unused = remainder = None
        try:
            for name in ("prefixes", "rows", "spacing", "guard", "component_bits", "coefficients", "root_width"):
                positive(self.c(name))
            need(compare(self.c("width"), self.c("root_width")) <= 0, "node within global width")
            self.shape()
            extent = self.complete_extent()
            self.roles["current"].rewind()
            skip(self.roles["current"], extent)
            need(self.roles["current"].read() == BLANK, "complete node input")
            self.roles["current"].rewind()
            if self.c("width").zero() or compare(self.c("width"), dimension) < 0:
                self.apply_leaf(self.c("width"), self.c("before"), self.c("after"))
                self.mode = "return"
                return
            test = fixed_power(self.c("width"), 1000, self.c("root_width"))
            if compare(test, self.c("root_width")) < 0:
                self.apply_leaf(self.c("width"), self.c("before"), self.c("after"))
                self.mode = "return"
                return
            columns = Count(self.c("width"))
            delta = columns.divide_small(self.binding.dimension)
            if delta:
                removed = Count.literal(delta)
                rest = subtract(self.c("width"), removed)
                suffix = Count.product(rest, self.c("spacing"))
                suffix.add(self.c("after"))
                self.apply_leaf(removed, self.c("before"), suffix)
                shift = Count.product(removed, self.c("spacing"))
                shift.add(self.c("before"))
                self.save(shift, "before")
                shift = None
                self.save(rest, "width")
                rest = None
            self.save(columns, "columns")
            columns = None
            divisor = Count.literal(self.binding.families * self.binding.cover.size)
            unused, remainder = divide(self.c("rows"), divisor)
            need(remainder.zero() and not unused.zero(), "complete fresh row divisor at node")
            self.save(unused, "unused")
            unused = None
            local_bits = Count.product(self.c("prefixes"), self.c("unused"))
            local_extent = Count.product(local_bits, self.c("row_bits"))
            local_bits.close()
            divisor2 = Count(self.c("component_bits"))
            divisor2.multiply_small(2)
            gaussian_count, rem2 = divide(local_extent, divisor2)
            try:
                need(rem2.zero(), "complete Gaussian local packet")
                self.save(gaussian_count, "gaussians")
                gaussian_count = None
            finally:
                if gaussian_count is not None:
                    gaussian_count.close()
                local_extent.close()
                divisor2.close()
                rem2.close()
            self.event = self.subgroup = self.cover_index = self.pc = 0
            self.group = None
            self.mode = "group"
        finally:
            for value in (dimension, test, extent, columns, removed, rest, suffix, shift, divisor, unused, remainder):
                if value is not None:
                    value.close()

    def scalar_step(self, target, source, key):
        self.scalar.select(key)
        with self.scope.suspended():
            returned = self.scalar.run(self.packet(target), None if source is None else self.packet(source),
                                       borrowed_count(self.c("component_bits")), borrowed_count(self.c("gaussians")))
        transfer(returned, self.packet(target))
        erase_marker(returned)

    def packet_extent(self):
        extent = Count.product(self.c("gaussians"), self.c("component_bits"))
        extent.multiply_small(2)
        return extent

    def zero_step(self, target):
        need(target >= self.binding.slots, "only compiled private logical CLEAR")
        extent = self.packet_extent()
        remaining = Counter(extent)
        tape = self.packet(target)
        tape.clear()
        try:
            while not remaining.finished:
                tape.append(0)
                remaining.decrement()
        finally:
            tape.rewind()
            remaining.close()
            extent.close()

    def copy_step(self, target, source):
        need(target >= self.binding.slots and target != source, "compiled private COPY")
        extent = self.packet_extent()
        try:
            require_zero(self.packet(target), extent)
            copy_symbols(self.packet(source), self.packet(target))
        finally:
            extent.close()

    def exchange_step(self, x, y):
        self.scalar.select(("scale", -1, 1))
        with self.scope.suspended():
            returned = self.scalar.run(self.packet(x), None, borrowed_count(self.c("component_bits")),
                                       borrowed_count(self.c("gaussians")))
        transfer(self.packet(y), self.packet(x))
        transfer(returned, self.packet(y))
        erase_marker(returned)

    def monomial_step(self, target, key, inverse):
        self.monomial.select(self.group.recipes[key])
        one = Count.literal(1)
        columns = compact = extra = wide = rows = None
        widths = ()
        try:
            columns = subtract(self.c("columns"), one)
            compact = Count.product(columns, self.c("guard"))
            extra = subtract(self.c("compact_bits"), compact)
            wide = Count.product(self.c("columns"), self.c("spacing"))
            rows = Count.product(self.c("prefixes"), self.c("unused"))
            template = (self.c("front"), extra, compact, extra, compact, self.c("before"),
                        *((wide,) * self.binding.dimension), self.c("after"), extra, compact, self.c("back"))
            widths = tuple(Count(value) for value in template)
            with self.scope.suspended():
                returned = self.monomial.run(self.packet(target), tuple(borrowed_count(v) for v in widths),
                    *(borrowed_count(v) for v in (self.c("columns"), self.c("spacing"), self.c("guard"),
                      self.c("residue"), self.c("component_bits"), self.c("coefficients"), rows)), inverse=inverse)
            transfer(returned, self.packet(target))
            erase_marker(returned)
        finally:
            for value in (*widths, one, columns, compact, extra, wide, rows):
                if value is not None:
                    value.close()

    def next_group(self):
        while self.event < len(self.binding.events):
            count = self.binding.group_count(self.event)
            if self.subgroup >= count:
                self.event += 1
                self.subgroup = self.cover_index = 0
                continue
            if self.cover_index >= self.binding.cover.size:
                self.cover_index = 0
                self.subgroup += 1
                continue
            group = self.binding.group(self.event, self.subgroup, self.cover_index)
            need(len(group.code) < 65536, "finite group program-counter bound")
            if not group.code:
                self.cover_index += 1
                continue
            self.group = group
            self.bank.select(group.keys)
            with self.scope.suspended():
                self.bank.gather(self.roles["current"], *(borrowed_count(self.c(name))
                                  for name in ("prefixes", "unused", "row_bits")))
            for tape in self.private:
                origin(tape)
                tape.clear()
            self.pc = 0
            return
        self.mode = "return"

    def finish_group(self):
        extent = self.packet_extent()
        try:
            for tape in self.private:
                if tape.read() != BLANK:
                    require_zero(tape, extent)
                tape.clear()
        finally:
            extent.close()
        with self.scope.suspended():
            self.bank.scatter(self.roles["current"], *(borrowed_count(self.c(name))
                              for name in ("prefixes", "unused", "row_bits")))
            self.bank.commit(self.roles["current"])
        self.group = None
        self.cover_index += 1
        self.pc = 0

    def prepare_child(self, target, rank):
        need(self.group is not None and self.bank.state == "gathered", "child belongs to active group")
        need(type(rank) is int and 0 < rank < self.binding.dimension, "source child rank contracts")
        width = Count(self.c("columns"))
        if rank > 1:
            width.multiply_small(rank)
        tail = Count(self.c("columns"))
        if self.binding.dimension - rank > 1:
            tail.multiply_small(self.binding.dimension - rank)
        after = Count.product(tail, self.c("spacing"))
        try:
            need(not width.zero() and compare(width, self.c("width")) < 0, "strict complex child contraction")
            after.add(self.c("after"))
            copy_symbols(self.packet(target), self.capsule["current"])
            for name in INPUTS:
                value = self.c("unused") if name == "rows" else width if name == "width" else after if name == "after" else self.c(name)
                copy_symbols(value.tape, self.capsule[name])
            self.header.write(self.roles["header"], (int(self.root), self.event, self.subgroup,
                self.cover_index, self.pc + 1, target, rank))
        finally:
            width.close()
            tail.close()
            after.close()

    def enter_child(self):
        self.primitive_boundary()
        for tape in self.parked:
            origin(tape)
        self.parking.park()
        for name, tape in self.capsule.items():
            transfer(tape, self.roles[name])
        self.bank.state = "closed"
        self.bank.source = None
        self.bank.selection = None
        self.group = None
        self.root = False
        self.mode = "node"
        self.event = self.subgroup = self.cover_index = self.pc = 0
        if self.observe:
            self.observe(self, "enter")

    def return_node(self):
        self.primitive_boundary()
        need(self.output.read() == BLANK, "consume preceding complex output")
        origin(self.output)
        transfer(self.roles["current"], self.output)
        for tape in self.parked:
            origin(tape)
            tape.clear()
        self.bank.state = "closed"
        self.bank.source = None
        self.bank.selection = None
        if self.root:
            self.parking.empty()
            self.closed = True
            self.mode = "closed"
            return True
        self.parking.restore()
        root, self.event, self.subgroup, self.cover_index, self.pc, target, rank = self.header.read(self.roles["header"])
        self.roles["header"].clear()
        self.root = bool(root)
        self.group = self.binding.group(self.event, self.subgroup, self.cover_index)
        need(0 < self.pc <= len(self.group.code) and
             self.group.code[self.pc - 1][0] == "child" and
             self.group.code[self.pc - 1][2:] == (target, rank), "return matches exact parent child instruction")
        transfer(self.output, self.packet(target))
        self.bank.selection = {key: slot for slot, key in enumerate(self.group.keys)}
        self.bank.source = self.roles["current"]
        self.bank.state = "gathered"
        self.mode = "group"
        if self.observe:
            self.observe(self, "return")
        return False

    def discard(self):
        for tape in (*self.parked, *self.capsule.values(), self.output, self.bank.output):
            origin(tape)
            tape.clear()
        self.parking.stack.clear()
        self.parking.reverse.clear()
        self.bank.state = "closed"
        self.bank.source = self.bank.selection = None
        self.group = None
        self.mode = "closed"
        self.closed = True

    def run(self, payload, descriptors):
        need(self.closed and self.output.read() == BLANK and set(descriptors) == set(INPUTS),
             "closed prepared complex entry and complete descriptors")
        self.parking.empty()
        source = borrowed_tape(payload)
        need(source not in self.parked and source is not self.output, "borrowed complex input is separate")
        need(all(isinstance(descriptors[name], Count) for name in INPUTS), "encoded prepared descriptor")
        self.root, self.closed, self.mode = True, False, "node"
        self.group = None
        try:
            copy_symbols(source, self.roles["current"])
            for name in INPUTS:
                copy_symbols(descriptors[name].tape, self.roles[name])
            while True:
                child = False
                with sealed_constructors(), self.scope.installed():
                    if self.mode == "node":
                        self.node()
                    elif self.mode == "group":
                        if self.group is None:
                            self.next_group()
                        elif self.pc == len(self.group.code):
                            self.finish_group()
                        else:
                            op = self.group.code[self.pc]
                            kind = op[0]
                            if kind == "scalar":
                                self.scalar_step(*op[2:])
                            elif kind == "zero":
                                self.zero_step(op[2])
                            elif kind == "copy":
                                self.copy_step(*op[2:])
                            elif kind == "monomial":
                                self.monomial_step(*op[2:])
                            elif kind == "exchange":
                                self.exchange_step(*op[2:])
                            elif kind == "child":
                                self.prepare_child(*op[2:])
                                child = True
                            else:
                                need(kind in ("identity", "marker"), "implemented physical instruction")
                            if not child:
                                self.pc += 1
                    else:
                        need(self.mode == "return", "finite complex controller state")
                self.pool.empty()
                if child:
                    self.enter_child()
                elif self.mode == "return" and self.return_node():
                    source.rewind()
                    return self.output
        except BaseException:
            for tape in (*self.roles.values(), *self.capsule.values()):
                tape.rewind()
            self.discard()
            source.rewind()
            raise
