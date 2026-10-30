"""Join actual-width planning and the retuned machine to the retained root."""

from active_sources import active
active()
import root_layer as retained
from t74_root import T74RootLayer
from active_plan import ActiveWidthPlan
from retuned_machine import RetunedMachine
from retuned_native import build_native


class ActiveWidthRoot(T74RootLayer):
    def __init__(self, binding, native, catalogue, plan=None, observe=None):
        self.plan = plan if plan is not None else ActiveWidthPlan(
            binding.dimension, binding.maximum_rank, binding.families * binding.cover.size)
        self.machine = RetunedMachine(binding, native, catalogue, observe)
        self.grid = retained.GridBoundary()
        self.phase = retained.PhaseSweep()
        self.padding = retained.RowPadding()
        self.normalizer = retained.api["normalizer"].Normalizer()
        self.leaf = retained.api["coefficient_engine"].CoefficientEngine(("left", "active", "right"), "active")
        self.pool = retained.ScratchPool(32)
        self.scope = retained.OuterScope(self.pool)
        self.current, self.output = retained.Tape(), retained.Tape()
        self.closed = True


def production_layer():
    """Construct the retained finite source; no production-size execution claim."""
    state = active()
    binding = state.t74_binding.T74Binding(state.prepared)
    return ActiveWidthRoot(binding, build_native(), binding.catalogue)
