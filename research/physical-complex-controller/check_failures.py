# SPDX-License-Identifier: Apache-2.0
"""Named preparation failures preserve borrowed input and permit machine reuse."""
import json
from pathlib import Path
import sys
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cohort
cohort.activate()
from cardinal_counts import Count
from fixture_binding import FixtureBinding
from macro_code import Code
from machine import Machine
from ordinary import Ordinary
from records import Tape
from session import erase_marker
from words import BLANK


def run():
    binding = FixtureBinding()
    native = Ordinary(2, SimpleNamespace(codes=SimpleNamespace(q=2)), SimpleNamespace(families=0),
                      (Code((("unreachable",),), 0),), capacity=64)
    machine = Machine(binding, native, binding.catalogue)
    observations = []
    for rows, cut, expected in ((3, False, "complete fresh row divisor at node"),
                                (4, True, "complete skipped packet"), (4, False, None)):
        raw = bytes(2 * 8 * rows * 4 - int(cut))
        source = Tape()
        for bit in raw:
            source.append(bit)
        source.rewind()
        parameters = dict(prefixes=1, rows=rows, front=0, compact_bits=0, before=0, width=2,
                          after=0, back=0, spacing=1, guard=1, residue=0, component_bits=8,
                          coefficients=1, root_width=2)
        descriptors = {name: Count.literal(value) for name, value in parameters.items()}
        snapshots = {name: bytes(value.tape.cells) for name, value in descriptors.items()}
        try:
            result = machine.run(source, descriptors)
        except ValueError as error:
            cohort.require(expected is not None and str(error) == expected, "exact preparation rejection")
            observations.append(str(error))
        else:
            cohort.require(expected is None, "missing preparation rejection")
            cohort.require(bytes(result.cells[1:]).rstrip(bytes([BLANK])) == raw, "valid retry endpoint")
            result.clear()
            erase_marker(result)
        cohort.require(bytes(source.cells[1:]).rstrip(bytes([BLANK])) == raw, "failure preserves borrowed packet")
        cohort.require(all(bytes(value.tape.cells) == snapshots[name] for name, value in descriptors.items()),
                       "failure preserves encoded descriptors")
        cohort.require(machine.closed and not machine.pool.live and all(t.read() == BLANK for t in machine.parked),
                       "failure closes machine state")
        machine.parking.empty()
        for value in descriptors.values():
            value.close()
        source.clear()
    return dict(rejections=observations, complete_reuse=True,
                scope="Prepared descriptor/extent failures; inherited arithmetic errors have their own source checks.")


if __name__ == "__main__":
    print(json.dumps(run(), sort_keys=True, indent=2))
