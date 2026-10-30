# SPDX-License-Identifier: Apache-2.0
"""Join an explicitly planned physical root to MSB-first outer packets."""

import cohort

cohort.activate()
from cardinal_counts import Count
from scratch_pool import ScratchPool
from session import OuterScope, erase_marker, sealed_constructors
from word_order import WordOrderBridge
from words import BLANK, need


class OuterLayer:
    """The supplied root retains responsibility for its native construction."""

    def __init__(self, root):
        need(root.plan.dimension_exponent == (1, 40), "explicit outer root plan")
        self.root = root
        self.entrance, self.exit = WordOrderBridge(), WordOrderBridge()
        self.pool = ScratchPool(8)
        self.scope = OuterScope(self.pool)
        self.closed = True

    def run(
        self,
        payload,
        precision,
        selected,
        left,
        right,
        coefficients,
        outer_rows,
        residue,
    ):
        need(
            self.closed and self.root.closed and self.exit.output.read() == BLANK,
            "consumed complete outer layer",
        )
        parameters = (
            precision,
            selected,
            left,
            right,
            coefficients,
            outer_rows,
            residue,
        )
        width = gaussians = entry = result = None
        self.closed = False
        try:
            self.root.plan.compute(*parameters)
            with sealed_constructors(), self.scope.installed():
                width = Count(self.root.plan.count("input_bits"))
                gaussians = Count(self.root.plan.count("gaussians"))
            self.root.plan.clear()
            entry = self.entrance.run(payload, width, gaussians)
            result = self.root.run(entry, *parameters)
            return self.exit.run(result, width, gaussians)
        finally:
            for tape in (result, entry):
                if tape is not None:
                    tape.clear()
                    erase_marker(tape)
            for value in (width, gaussians):
                if value is not None:
                    value.close()
            self.root.plan.clear()
            self.pool.empty()
            self.closed = True
