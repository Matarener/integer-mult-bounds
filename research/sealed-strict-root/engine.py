"""The strict encoded plan enters a preallocated, sealed physical root."""

from contextlib import ExitStack
from unittest.mock import patch

import strict_outer
import strict_rows
import strict_selector
from cardinal_counts import Count
from ordinary import Ordinary, ring_from_count, unit_program
from runtime import require
from session import borrowed_count, borrowed_tape


class StrictRoot(Ordinary):
    def run(self, payload, original, prefixes, gap, suffix):
        require(self.q == 2 and self.binding.cutoff == 2, "reduced GL2 grammar only")
        require(
            self.profile
            == strict_selector.Profile(
                row_factor=1, dimension=2, child_rank=1, numerator=0, denominator=1
            ),
            "exact reduced stock profile",
        )

        def plan():
            # Called inside execute_plan's sealed outer pool scope.
            two, five = Count.literal(2), Count.literal(5)
            try:
                require(
                    original.equals(two) or original.equals(five),
                    "only proved reduced widths two and five",
                )
            finally:
                two.close()
                five.close()
            return strict_selector.select(original, self.q, self.profile, 1)

        return self.execute_plan(
            payload,
            original,
            prefixes,
            gap,
            suffix,
            plan,
        )

    def setup(self, plan, cleanup):
        radix = Count.literal(self.q)
        cleanup.callback(radix.close)
        modulus = strict_selector.power(radix, plan["width"])
        remainder = strict_selector.power(radix, plan["remainder"])
        one = Count.literal(1)
        for value in (modulus, remainder, one):
            cleanup.callback(value.close)
        ring = ring_from_count(self.banks[0], modulus, cleanup)
        high = ring_from_count(self.banks[1], plan["rows"], cleanup)
        tail = (
            None
            if plan["remainder"].zero()
            else ring_from_count(self.banks[2], remainder, cleanup)
        )
        maximum = Count(plan["body"])
        cleanup.callback(maximum.close)
        maximum.increment()
        maximum.multiply_small(128)
        indices = self.banks[3]
        indices.prepare(maximum)
        size, depth = indices.load(plan["body"]), indices.zero()
        cleanup.callback(indices.free_many, size, depth)
        self.runtime.arena.prepare(modulus)
        self.runtime.indices.prepare(maximum)
        program = unit_program(indices, ring, size, depth, self.binding.codes.bits)
        directory = self.pool.acquire()
        cleanup.callback(program.tape.clear)
        cleanup.callback(directory.clear)
        return ring, high, tail, remainder, one, size, depth, program, directory

    def fitted(self, payload, plan, prefixes, gap, suffix):
        with ExitStack() as cleanup:
            ring, high, tail, remainder, one, size, depth, program, directory = (
                self.setup(plan, cleanup)
            )
            partial = Count.product(remainder, gap)
            cleanup.callback(partial.close)
            actual_gap = Count.product(partial, plan["rows"])
            actual_suffix = Count.product(remainder, suffix)
            cleanup.callback(actual_gap.close)
            cleanup.callback(actual_suffix.close)

            def callee(padded, rows):
                if self.observe is not None:
                    self.observe("before", borrowed_tape(padded), None)
                with self.scope.suspended():
                    returned = self.runtime.run(
                        borrowed_tape(padded),
                        borrowed_tape(directory),
                        borrowed_tape(program.tape),
                        ring.modulus,
                        size,
                        depth,
                        borrowed_count(prefixes),
                        borrowed_count(rows),
                        borrowed_count(one),
                        borrowed_count(actual_gap),
                        borrowed_count(actual_suffix),
                    )
                if self.observe is not None:
                    self.observe("after", borrowed_tape(padded), returned)
                return returned

            with patch.object(
                strict_outer.tape_padding, "complete", strict_rows.complete
            ):
                return strict_outer.interchange(
                    payload,
                    size,
                    ring,
                    high,
                    self.q,
                    prefixes,
                    gap,
                    suffix,
                    plan["stock"],
                    callee,
                    remainder_ring=tail,
                )
