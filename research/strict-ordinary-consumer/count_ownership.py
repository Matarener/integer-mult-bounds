"""Track complete Count-tape release through successful and failed calls."""

from contextlib import contextmanager
from unittest.mock import patch

import cardinality
import counts
from records import Tape
from runtime import require
from words import BLANK


@contextmanager
def audited_counts(base=Tape):
    live = set()
    observation = {"peak_roles": 0, "maximum_cells": 0}

    class Audited(base):
        def __init__(self):
            super().__init__()
            live.add(self)
            observation["peak_roles"] = max(observation["peak_roles"], len(live))

        def write(self, value):
            super().write(value)
            observation["maximum_cells"] = max(
                observation["maximum_cells"], len(self.cells)
            )

        def append(self, value):
            super().append(value)
            observation["maximum_cells"] = max(
                observation["maximum_cells"], len(self.cells)
            )

        def clear(self):
            super().clear()
            require(
                self.head == 1 and all(value == BLANK for value in self.cells[1:]),
                "every released Count tape erased and head restored",
            )
            live.discard(self)

    try:
        with (
            patch.object(counts, "Tape", Audited),
            patch.object(cardinality, "Tape", Audited),
        ):
            yield observation
    finally:
        require(not live, "all observed Count tapes released")
