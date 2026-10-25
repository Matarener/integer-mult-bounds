# SPDX-License-Identifier: Apache-2.0
"""Check normalized root return through the changed private-Z machine."""
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import sys
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parent))
from predecessor import activate, close_test_imports
activate()
from check_runtime import ZFixture
from t74_root import T74RootLayer
from check_root import OneCover, ReducedPlan, body, encode, walsh
from cardinal_counts import Count
from macro_code import Code
from ordinary import Ordinary
from records import Tape
from root_plan import RootPlan
from session import erase_marker
from words import BLANK, need


def run(fast):
    binding = ZFixture()
    if fast:
        binding.cover = OneCover()
    native = Ordinary(2, SimpleNamespace(codes=SimpleNamespace(q=2)),
                      SimpleNamespace(families=0), (Code((("unreachable",),), 0),), capacity=64)
    visits = Counter()
    plan_type = ReducedPlan if fast else RootPlan
    plan = plan_type(2, 1, 2 if fast else 4, guard_exponent=2)
    layer = T74RootLayer(binding, native, binding.catalogue, plan,
                         lambda _machine, event: visits.update([event]))
    cases = [(9, 8, 0, 0, 1, 1, 0)] if fast else [
        (5, 0, 1, 1, 2, 2, 0), (5, 1, 1, 1, 2, 2, 0),
        (5, 2, 1, 0, 2, 1, 0), (6, 3, 0, 1, 1, 1, 0)]
    digest = sha256()
    for parameters in cases:
        p, width, left, right, fields, rows, _residue = parameters
        count = rows * (1 << (left + width + right)) * fields
        values = [((i * 7) % 13 - 6, (i * 11) % 17 - 8) for i in range(count)]
        raw = encode(values, p + 2)
        expected = encode(walsh(values, width, left, right, 1, 0, fields, rows), p + 2)
        source = Tape()
        for bit in raw:
            source.append(bit)
        source.rewind()
        counts = tuple(Count.literal(value) for value in parameters)
        before = tuple(bytes(value.tape.cells) for value in counts)
        try:
            result = layer.run(source, *counts)
            need(body(result) == expected and body(source) == raw, "normalized T74 machine root and preserved input")
            need(tuple(bytes(value.tape.cells) for value in counts) == before, "preserved root descriptors")
            need(layer.closed and layer.machine.closed and not layer.pool.live and
                 layer.current.read() == BLANK and all(t.read() == BLANK for t in plan.roles.values()),
                 "complete root-owned state return")
            digest.update(body(result))
            result.clear()
            erase_marker(result)
        finally:
            source.clear()
            for value in counts:
                value.close()
    need(visits["enter"] == visits["return"] and (not fast or visits["enter"] > 0), "balanced normalized child returns")
    return dict(status="PASS_T74_NORMALIZED_ROOT_FIXTURE", packets=len(cases), visits=dict(visits),
                sha256=digest.hexdigest(),
                scope="Reduced fast reservations" if fast else "Retained root formulas with reduced fixed guard",
                limitation="Neither fixture executes the full T74/O73 payload, native GL64 factory or production guard width.")


if __name__ == "__main__":
    try:
        print(json.dumps(dict(direct=run(False), fast=run(True)), sort_keys=True, indent=2))
    finally:
        close_test_imports()
