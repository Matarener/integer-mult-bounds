# SPDX-License-Identifier: Apache-2.0
"""Complete root phase sweeps and one-time row padding on encoded streams."""
import cohort
cohort.monomial_api()
from cardinal_counts import Count, positive
from compact_counts import append_bits, copy_bits
from compact_layout import Layout
from encoded import compare, subtract
from grid_boundary import GridDomainError
from phase_recipe import Recipe
from records import Tape
from scratch_pool import ScratchPool
from session import (OuterScope, borrowed_tape, erase_marker, initialize_marker,
                     sealed_constructors)
from signed_phase import scan
from stream import Counter
from words import BLANK, LEFT, need


class OutputEngine:
    def __init__(self, slots):
        self.pool = ScratchPool(slots)
        self.scope = OuterScope(self.pool)
        self.output = Tape()
        for tape in (*self.pool.tapes, self.output):
            erase_marker(tape)
        self.closed = True

    def rearm(self):
        need(self.closed and self.output.read() == BLANK and not self.pool.live, "consumed root stream output")
        self.output.step(-1)
        try:
            need(self.output.read() in (LEFT, BLANK), "root stream origin")
            if self.output.read() == BLANK:
                self.output.write(LEFT)
        finally:
            self.output.step(1)
        for tape in self.pool.tapes:
            initialize_marker(tape)
        self.closed = False

    def finish(self, failure):
        self.pool.empty()
        for tape in self.pool.tapes:
            erase_marker(tape)
        self.output.rewind()
        self.closed = True
        if failure is not None:
            self.output.clear()
            erase_marker(self.output)
            raise failure
        return self.output


class PhaseSweep(OutputEngine):
    def __init__(self):
        super().__init__(96)
        self.recipe = Recipe(dict(matrix_rows=[1], offset=0, phase=0,
                                  linear_Z4=[1], quadratic_rows=[0]), ("active",))

    def run(self, payload, left, selected, right, spacing, residue, width, coefficients, outer_rows):
        source = borrowed_tape(payload)
        need(source is not self.output, "distinct root phase input")
        for value in (spacing, width, coefficients, outer_rows):
            positive(value)
        self.rearm()
        active = record_bits = total = plan = current = result = None
        failure = None
        with sealed_constructors(), self.scope.installed():
            try:
                need(compare(residue, spacing) < 0, "root phase selected residue")
                active = Count.product(selected, spacing)
                record_bits = Count.product(width, coefficients)
                record_bits.multiply_small(2)
                plan = Layout(("left", "active", "right"), (left, active, right), record_bits)
                total = Count.product(plan.row_bits, outer_rows)
                current = self.pool.acquire()
                source.rewind()
                copy_bits(source, current, total)
                need(source.read() == BLANK, "complete root phase packet")
                current.rewind()
                result = scan(current, plan, self.recipe, selected, spacing, residue,
                              width, coefficients, outer_rows, self.pool.acquire)
                current = None
                append_bits(result, self.output)
            except ValueError as error:
                failure = error
            finally:
                source.rewind()
                for value in (current, result, active, record_bits, total):
                    if value is not None:
                        value.close() if isinstance(value, Count) else value.clear()
                if plan is not None:
                    plan.close()
        return self.finish(failure)


class RowPadding(OutputEngine):
    def __init__(self):
        super().__init__(16)

    def run(self, payload, prefixes, original_rows, padded_rows, row_bits, remove=False):
        need(type(remove) is bool, "compiled row-padding direction")
        for value in (prefixes, original_rows, padded_rows, row_bits):
            positive(value)
        source = borrowed_tape(payload)
        need(source is not self.output, "distinct row-padding input")
        self.rearm()
        extra = kept_bits = extra_bits = remaining = skipped = None
        failure = None
        with sealed_constructors(), self.scope.installed():
            try:
                need(compare(original_rows, padded_rows) <= 0, "row padding does not shrink")
                extra = subtract(padded_rows, original_rows)
                kept_bits = Count.product(original_rows, row_bits)
                extra_bits = Count.product(extra, row_bits)
                remaining = Counter(prefixes)
                source.rewind()
                while not remaining.finished:
                    copy_bits(source, self.output, kept_bits)
                    skipped = Counter(extra_bits)
                    while not skipped.finished:
                        if remove:
                            if source.read() != 0:
                                raise GridDomainError("nonzero padded row returned")
                            source.step(1)
                        else:
                            self.output.append(0)
                        skipped.decrement()
                    skipped.close()
                    skipped = None
                    remaining.decrement()
                need(source.read() == BLANK, "complete row padding input")
            except ValueError as error:
                failure = error
            finally:
                source.rewind()
                for value in (extra, kept_bits, extra_bits, remaining, skipped):
                    if value is not None:
                        value.close()
        return self.finish(failure)
