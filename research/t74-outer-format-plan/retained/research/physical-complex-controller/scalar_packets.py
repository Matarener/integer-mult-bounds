# SPDX-License-Identifier: Apache-2.0
"""Use the credited physical scalar transducer with the full compiled catalogue.

The module name differs from the unchanged predecessor scalar_engine.
"""
import cohort
inherited = cohort.activate()["scalar_engine"]
from records import Tape
from scratch_pool import ScratchPool
from session import OuterScope, erase_marker
from scalar_program import ScalarProgram


class FullScalarEngine(inherited.ScalarEngine):
    def __init__(self, catalogue):
        cohort.require(type(catalogue) is dict and 0 < len(catalogue) <= 349 and
                       all(isinstance(value, ScalarProgram) and key == value.key
                           for key, value in catalogue.items()), "compiled full-word catalogue")
        self.recipes = dict(catalogue)
        self.recipe = next(iter(self.recipes.values()))
        self.pool = ScratchPool(128)
        self.scope = OuterScope(self.pool)
        self.output = Tape()
        for tape in (*self.pool.tapes, self.output):
            erase_marker(tape)
        self.closed = True
