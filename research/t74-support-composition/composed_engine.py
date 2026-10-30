"""Execute complete support exposure, one normalized root and inverse exposure."""

from composed_sources import active
active()
from active_root import ActiveWidthRoot
from cardinal_counts import Count, positive
from compact_counts import append_bits, copy_bits, power_two, shifted
from composed_plan import ExposurePlan, Positions
from encoded import compare, subtract
from grid_boundary import GridBoundary
from records import Tape
from retuned_native import build_native
from router_engine import Router
from router_metadata import indices, owned
from scratch_pool import ScratchPool
from session import (OuterScope, borrowed_count, borrowed_tape, erase_marker,
                     initialize_marker, sealed_constructors)
from words import BLANK, LEFT, need


class ComposedRoot:
    def __init__(self, router, root, policy="standard"):
        need(isinstance(router, Router) and isinstance(root, ActiveWidthRoot), "shared authenticated owners")
        need(policy in ("standard", "fixture-ell1"), "compiled composition policy")
        need(router.output is not root.output, "distinct physical owner returns")
        self.router, self.root, self.policy = router, root, policy
        self.grid = GridBoundary()
        self.pool = ScratchPool(256)
        self.scope = OuterScope(self.pool)
        self.output = Tape()
        self.current = None
        self.closed = True
        self.last_mode = None
        self.calls = dict(swaps=0, routes=0, roots=0, lifts=0, truncations=0)
        for tape in (*self.pool.tapes, self.output):
            erase_marker(tape)

    def idle(self):
        self.router.idle_child()
        need(self.router.closed and self.router.output.read() == BLANK and not self.router.pool.live
             and self.root.closed and self.root.output.read() == BLANK
             and self.root.current.read() == BLANK and not self.root.pool.live
             and self.grid.closed and self.grid.output.read() == BLANK,
             "consumed and closed composition children")

    def rearm(self):
        need(self.closed and self.current is None and self.output.read() == BLANK,
             "consume prior composed output")
        self.idle()
        self.output.step(-1)
        need(self.output.read() in (LEFT, BLANK), "composed output origin")
        if self.output.read() == BLANK:
            self.output.write(LEFT)
        self.output.step(1)
        for tape in self.pool.tapes:
            initialize_marker(tape)
        self.closed = False

    def accept(self, returned):
        following = self.pool.acquire()
        try:
            append_bits(returned, following)
            following.rewind()
        except BaseException:
            following.clear()
            raise
        finally:
            returned.clear()
            erase_marker(returned)
        self.current.clear()
        self.current = following

    def suffix_swap(self, n, R, C, start, width):
        positive(width)
        need(compare(width, start) <= 0, "disjoint persistent suffix blocks")
        with owned(Count(start)) as (end,):
            end.add(width)
            need(compare(end, n) <= 0, "complete persistent suffix source")
            with owned(subtract(n, end), subtract(start, width)) as (before_bits, gap_bits):
                with owned(power_two(before_bits), power_two(gap_bits)) as (before, gap):
                    with owned(Count.product(C, before)) as (prefixes,):
                        self.idle()
                        with self.scope.suspended():
                            returned = self.router.binary.run(
                                borrowed_tape(self.current),
                                *(borrowed_count(v) for v in (width, prefixes, gap, R)))
                        self.accept(returned)
        self.calls["swaps"] += 1

    def route(self, plan, descriptor, R, C):
        self.idle()
        with self.scope.suspended():
            returned = self.router.run(
                borrowed_tape(self.current), borrowed_tape(descriptor),
                *(borrowed_count(v) for v in (plan.N, plan.p, plan.count, plan.prefix_width, R, C)))
        self.accept(returned)
        self.calls["routes"] += 1

    def transform(self, p, g, left, right, coefficients, C):
        self.idle()
        with owned(Count.literal(0)) as (zero,):
            with self.scope.suspended():
                returned = self.root.run(
                    borrowed_tape(self.current),
                    *(borrowed_count(v) for v in (p, g, left, right, coefficients, C, zero)))
            self.accept(returned)
        self.calls["roots"] += 1

    def literal(self, plan, selected, coefficients, C, gaussians, h):
        # Every intermediate H0 prefix is exact on this lifted grid.
        with owned(Count(plan.p), Count(h), Count.literal(0), Count.literal(1)) as (P, wide, zero, one):
            P.add(plan.g)
            wide.add(plan.g)
            self.idle()
            with self.scope.suspended():
                returned = self.grid.expand(borrowed_tape(self.current),
                    *(borrowed_count(v) for v in (h, plan.g, zero, gaussians)))
            self.accept(returned)
            self.calls["lifts"] += 1
            with owned(subtract(plan.n, one)) as (last,):
                for index in indices(plan.g):
                    with selected.at(index) as right, owned(subtract(last, right)) as (left,):
                        self.transform(P, one, left, right, coefficients, C)
            self.idle()
            with self.scope.suspended():
                returned = self.grid.truncate(borrowed_tape(self.current),
                    *(borrowed_count(v) for v in (wide, plan.g, h, gaussians)))
            self.accept(returned)
            self.calls["truncations"] += 1

    def composed(self, plan, coefficients, C, R):
        self.suffix_swap(plan.n, R, C, plan.U, plan.ell)
        with owned(shifted(coefficients, plan.ell), shifted(R, plan.ell), Count.literal(0)) as (fields, wide_R, zero):
            self.route(plan, plan.forward, wide_R, C)
            self.transform(plan.p, plan.g, plan.left, zero, fields, C)
            self.route(plan, plan.inverse, wide_R, C)
        self.suffix_swap(plan.n, R, C, plan.U, plan.ell)

    def run(self, payload, positions, n, p, g, width, coefficients, outer_rows):
        source, selected = borrowed_tape(payload), borrowed_tape(positions)
        need(source is not selected and source is not self.output and selected is not self.output,
             "distinct borrowed composed payload and selected descriptor")
        positive(coefficients)
        positive(outer_rows)
        self.rearm()
        plan = None
        source.rewind()
        with sealed_constructors(), self.scope.installed():
            try:
                plan = ExposurePlan(n, p, g, width, self.pool.acquire, self.policy)
                plan.compile(selected)
                self.last_mode = plan.mode
                with owned(Count(p), power_two(n)) as (h, addresses):
                    h.increment()
                    h.increment()
                    with owned(Count.product(addresses, coefficients), Count.product(h, coefficients)) as (row_fields, R):
                        R.multiply_small(2)
                        with owned(Count.product(row_fields, outer_rows)) as (gaussians,):
                            with owned(Count.product(gaussians, h)) as (total,):
                                total.multiply_small(2)
                                self.current = self.pool.acquire()
                                copy_bits(source, self.current, total)
                            need(source.read() == BLANK, "complete composed Gaussian packet")
                            self.current.rewind()
                            if plan.mode == "composed":
                                self.composed(plan, coefficients, outer_rows, R)
                            elif plan.mode == "literal":
                                self.literal(plan, Positions(selected, g, width), coefficients, outer_rows, gaussians, h)
                            else:
                                need(plan.mode == "identity", "complete composed plan mode")
                self.idle()
                append_bits(self.current, self.output)
            finally:
                source.rewind()
                selected.rewind()
                if self.current is not None:
                    self.current.clear()
                    self.current = None
                if plan is not None:
                    plan.close()
            self.pool.empty()
        for tape in self.pool.tapes:
            erase_marker(tape)
        self.output.rewind()
        self.closed = True
        return self.output


def production_layer():
    """Compile two fresh production natives in the one authenticated cohort."""
    state = active().root
    binding = state.t74_binding.T74Binding(state.prepared)
    router = Router(build_native())
    root = ActiveWidthRoot(binding, build_native(), binding.catalogue)
    return ComposedRoot(router, root)
