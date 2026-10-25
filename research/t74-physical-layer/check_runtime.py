# SPDX-License-Identifier: Apache-2.0
"""Exercise private-Z/warp joins in the recursive physical machine."""
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import sys
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parent))
from predecessor import activate, close_test_imports
activate()
from t74_machine import T74Machine
from check_machine import encode, oracle
from cardinal_counts import Count
from fixture_binding import FixtureBinding
from macro_code import Code
from ordinary import Ordinary
from records import Tape
from selected_binding import Group
from words import BLANK, need


class ZFixture(FixtureBinding):
    private = 2
    centres = 1

    def __init__(self, corrupt=False):
        super().__init__()
        self.corrupt = corrupt

    def group(self, event, subgroup, cover):
        old = super().group(event, subgroup, cover)
        recipes = dict(old.recipes, warp=dict(matrix_rows=[2, 1], offset=1, phase=1,
                                             linear_Z4=[1, 2], quadratic_rows=[2, 1]))
        code = [("zero", -1, 3), ("copy", -1, 3, 0),
                ("monomial", -1, 3, "warp", False), ("monomial", -1, 3, "warp", True)]
        if not self.corrupt:
            code.append(("scalar", -1, 3, 0, ("add", -1, 1)))
        code.append(("release_zero", -1, 3))
        return Group(old.keys, tuple(code) + old.code, recipes)


def fixture(corrupt=False):
    binding = ZFixture(corrupt)
    native = Ordinary(2, SimpleNamespace(codes=SimpleNamespace(q=2)),
                      SimpleNamespace(families=0), (Code((("unreachable",),), 0),), capacity=64)
    visits = Counter()
    machine = T74Machine(binding, native, binding.catalogue,
                         lambda _machine, event: visits.update([event]))
    raw = dict(prefixes=2, rows=4, front=0, compact_bits=0, before=0,
               width=2, after=0, back=0, spacing=1, guard=1, residue=0,
               component_bits=16, coefficients=2, root_width=2)
    desc = {name: Count.literal(value) for name, value in raw.items()}
    descriptors_before = {name: bytes(value.tape.cells) for name, value in desc.items()}
    values = [(64 * ((i * 7) % 11 - 5), 64 * ((i * 3) % 7 - 3)) for i in range(64)]
    payload = encode(values, 16)
    expected = encode(oracle(values, 2, 0, 8, 2), 16)
    source = Tape()
    for bit in payload:
        source.append(bit)
    source.rewind()
    before = tuple(source.cells)
    try:
        try:
            result = machine.run(source, desc)
        except ValueError as error:
            need(corrupt and "zero" in str(error).lower(), "specific nonzero private-release rejection")
            need(tuple(source.cells) == before and machine.closed and
                 all(bytes(value.tape.cells) == descriptors_before[name] for name, value in desc.items()),
                 "rejected root preserves borrowed source and descriptors")
            return dict(rejected=str(error), visits=dict(visits))
        need(not corrupt, "accepted nonzero private release")
        actual = []
        while result.read() != BLANK:
            actual.append(result.read())
            result.step(1)
        result.rewind()
        need(bytes(actual) == expected and tuple(source.cells) == before, "complete recursive endpoint and preserved borrow")
        need(all(bytes(value.tape.cells) == descriptors_before[name] for name, value in desc.items()),
             "preserved complete borrowed descriptors")
        need(machine.closed and visits["enter"] == visits["return"] > 0, "balanced physical child returns")
        need(all(tape.read() == BLANK for tape in machine.private), "all owned private tapes blank")
        result.clear()
        return dict(status="PASS_REDUCED_T74_PRIVATE_Z_RUNTIME", bits=len(payload), visits=dict(visits),
                    sha256=sha256(expected).hexdigest(),
                    scope="Complete reduced geometry with new zero/warp joins; no full T74 payload or production guard.")
    finally:
        source.clear()
        for value in desc.values():
            value.close()


if __name__ == "__main__":
    try:
        print(json.dumps(dict(positive=fixture(), negative=fixture(True)), indent=2, sort_keys=True))
    finally:
        close_test_imports()
