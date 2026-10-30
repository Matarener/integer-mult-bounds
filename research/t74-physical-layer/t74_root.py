# SPDX-License-Identifier: Apache-2.0
"""Join the T74 machine to the retained normalized physical root."""
from predecessor import activate
activate()
import root_layer as retained
from t74_machine import T74Machine


class T74RootLayer(retained.RootLayer):
    def __init__(self, binding, native, catalogue, plan=None, observe=None):
        self.plan = plan if plan is not None else retained.RootPlan(
            binding.dimension, binding.maximum_rank, binding.families * binding.cover.size)
        self.machine = T74Machine(binding, native, catalogue, observe)
        self.grid = retained.GridBoundary()
        self.phase = retained.PhaseSweep()
        self.padding = retained.RowPadding()
        self.normalizer = retained.api["normalizer"].Normalizer()
        self.leaf = retained.api["coefficient_engine"].CoefficientEngine(("left", "active", "right"), "active")
        self.pool = retained.ScratchPool(32)
        self.scope = retained.OuterScope(self.pool)
        self.current, self.output = retained.Tape(), retained.Tape()
        self.closed = True


def production_layer(prepared):
    """Fixed source construction; the native GL64 factory has impractical size."""
    from binding import T74Binding
    from production_native import PRIME, build_native
    binding = T74Binding(prepared)
    return T74RootLayer(binding, build_native(PRIME), binding.catalogue)
