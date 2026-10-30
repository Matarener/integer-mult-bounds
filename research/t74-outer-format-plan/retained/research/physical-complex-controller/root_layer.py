# SPDX-License-Identifier: Apache-2.0
"""Physical root execution of b**D S_D C_D S_D with one final rounding."""
import cohort
api = cohort.activate()
from cardinal_counts import Count
from encoded import subtract
from grid_boundary import GridBoundary
from machine import Machine, origin
from parking import transfer
from records import Tape
from root_plan import RootPlan
from root_streams import PhaseSweep, RowPadding
from scratch_pool import ScratchPool
from session import OuterScope, borrowed_count, borrowed_tape, erase_marker, sealed_constructors
from words import BLANK, need


class RootLayer:
    def __init__(self, binding, native, catalogue, plan=None, observe=None):
        self.plan = plan if plan is not None else RootPlan(
            binding.dimension, binding.maximum_rank, binding.families * binding.cover.size)
        self.machine = Machine(binding, native, catalogue, observe)
        self.grid = GridBoundary()
        self.phase = PhaseSweep()
        self.padding = RowPadding()
        self.normalizer = api["normalizer"].Normalizer()
        self.leaf = api["coefficient_engine"].CoefficientEngine(("left", "active", "right"), "active")
        self.pool = ScratchPool(32)
        self.scope = OuterScope(self.pool)
        self.current, self.output = Tape(), Tape()
        self.closed = True

    def c(self, name):
        return self.plan.count(name)

    def accept(self, returned):
        transfer(returned, self.current)
        erase_marker(returned)

    def apply_phase(self):
        self.accept(self.phase.run(self.current, *(self.c(name) for name in
            ("left", "selected", "right", "K", "residue", "work_bits", "coefficients", "outer_rows"))))

    def apply_leaf(self, left, width, right):
        if width.zero():
            return
        active = Count.product(width, self.c("K"))
        try:
            with self.scope.suspended():
                returned = self.leaf.run_leaf(self.current,
                    tuple(borrowed_count(v) for v in (left, active, right)),
                    *(borrowed_count(v) for v in (width, self.c("K"), self.c("residue"),
                      self.c("work_bits"), self.c("coefficients"), self.c("outer_rows"))))
            self.accept(returned)
        finally:
            active.close()

    def reserved_leaves(self):
        prefix = tail = suffix = left = None
        try:
            prefix = Count(self.c("q0"))
            prefix.add(self.c("qF"))
            tail = subtract(self.c("selected"), prefix)
            suffix = Count.product(tail, self.c("K"))
            suffix.add(self.c("right"))
            self.apply_leaf(self.c("left"), prefix, suffix)
            tail.close()
            tail = subtract(self.c("selected"), self.c("qB"))
            left = Count.product(tail, self.c("K"))
            left.add(self.c("left"))
            self.apply_leaf(left, self.c("qB"), self.c("right"))
        finally:
            for value in (prefix, tail, suffix, left):
                if value is not None:
                    value.close()

    def fast_core(self):
        # Root scratch has closed before the recursive machine owns execution.
        self.pool.empty()
        self.accept(self.padding.run(self.current, *(self.c(name) for name in
            ("prefixes", "original_rows", "padded_rows", "row_bits"))))
        names = dict(prefixes="prefixes", rows="padded_rows", front="core_front", compact_bits="H",
                     before="zero", width="core_width", after="zero", back="core_back", spacing="K",
                     guard="G", residue="residue", component_bits="work_bits", coefficients="coefficients",
                     root_width="d")
        self.accept(self.machine.run(self.current, {name: self.c(source) for name, source in names.items()}))
        self.accept(self.padding.run(self.current, *(self.c(name) for name in
            ("prefixes", "original_rows", "padded_rows", "row_bits")), remove=True))

    def run(self, payload, precision, selected, left, right, coefficients, outer_rows, residue):
        """Borrow p-grid Gaussian records and encoded descriptors; return p-grid records.

        The selected production plan fixes the source constants. Checkers may
        inject an explicitly labelled reduced plan to exercise the same branch.
        The theorem assumes the input unit disk and the native source contracts.
        """
        need(self.closed and self.output.read() == BLANK and self.current.read() == BLANK,
             "consume previous complete root output")
        source = borrowed_tape(payload)
        need(source not in (self.current, self.output), "distinct borrowed root input")
        origin(self.output)
        self.closed = False
        high = None
        try:
            self.plan.compute(precision, selected, left, right, coefficients, outer_rows, residue)
            with sealed_constructors(), self.scope.installed():
                high = Count(self.c("delta"))
                high.increment()
                with self.scope.suspended():
                    returned = self.grid.expand(source, self.c("input_bits"), self.c("delta"),
                                                borrowed_count(high), self.c("gaussians"))
                self.accept(returned)
                high.close()
                high = None
            self.pool.empty()
            self.apply_phase()
            with sealed_constructors(), self.scope.installed():
                if self.plan.fast:
                    self.reserved_leaves()
                else:
                    self.apply_leaf(self.c("left"), self.c("selected"), self.c("right"))
            self.pool.empty()
            if self.plan.fast:
                self.fast_core()
            self.apply_phase()
            self.accept(self.normalizer.run(self.current, self.c("work_bits"),
                                           self.c("gaussians"), self.c("selected")))
            returned = self.grid.truncate(self.current, self.c("work_bits"), self.c("delta"),
                                          self.c("input_bits"), self.c("gaussians"))
            transfer(returned, self.output)
            erase_marker(returned)
            self.current.clear()
            return self.output
        except BaseException:
            self.current.clear()
            self.output.clear()
            raise
        finally:
            if high is not None:
                high.close()
            self.pool.empty()
            self.plan.clear()
            source.rewind()
            self.closed = True


def selected_layer(q=None):
    """Compile the selected source-relative construction for an admissible fixed q.

    Full selected finite compilation is intentionally not a local fixture.
    Its q/GL64-scale objects are finite constants in the source construction.
    """
    from production_native import PRIME, build_native
    from scalar_program import compile_catalogue
    from selected_binding import SelectedBinding
    from selected_source import load
    data = load()
    binding = SelectedBinding(data)
    catalogue, _ = compile_catalogue(data["programs"])
    return RootLayer(binding, build_native(PRIME if q is None else q), catalogue)
