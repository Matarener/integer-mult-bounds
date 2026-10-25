# SPDX-License-Identifier: Apache-2.0
"""Controller work in progress: complete full-literal physical packet checks."""
from fractions import Fraction
from hashlib import sha256
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import cohort
from scalar_program import compile_catalogue, inventory
from selected_source import load


def run():
    selected = load()
    catalogue, _ = compile_catalogue(selected["programs"])
    api = cohort.activate()
    from scalar_packets import FullScalarEngine
    from cardinal_counts import Count
    from records import Tape
    from session import erase_marker
    from words import BLANK
    engine = FullScalarEngine(catalogue)
    normalizer = api["normalizer"].Normalizer()
    width, count = Count.literal(48), Count.literal(1)
    left, right = Tape(), Tape()
    x, y = (7 << 16, -5 << 16), (-3 << 16, 2 << 16)

    def encode(values):
        return bytes((value >> bit) & 1 for value in values for bit in range(48))

    def fill(tape, values):
        tape.clear()
        for bit in encode(values):
            tape.append(bit)
        tape.rewind()

    def body(tape):
        return bytes(tape.cells[1:]).rstrip(bytes([BLANK]))

    digest = sha256()
    for key, program in sorted(catalogue.items()):
        fill(left, x)
        fill(right, y)
        engine.select(key)
        returned = engine.run(left, right if program.kind == "add" else None, width, count)
        expected = [Fraction(a) + program.coefficient * b if program.kind == "add"
                    else program.coefficient * a for a, b in zip(x, y)]
        cohort.require(all(a.denominator == 1 for a in expected), "fixture grid")
        cohort.require(body(returned) == encode([int(a) for a in expected]), "full literal physical endpoint")
        cohort.require(body(left) == encode(x) and body(right) == encode(y), "full literal preserves borrows")
        cohort.require(engine.closed and not engine.pool.live and
                       all(t.head == 1 and all(b == BLANK for b in t.cells) for t in engine.pool.tapes),
                       "closed scalar physical work")
        digest.update(str(key).encode() + body(returned))
        returned.clear()
        erase_marker(returned)
    # Interleave two different inherited primitives under the same Count/Tape
    # identities. The expected degree-two normalization is (-i/2)*z.
    fill(left, (8, -4))
    degree = Count.literal(2)
    returned = normalizer.run(left, width, count, degree)
    cohort.require(body(returned) == encode((-2, -4)), "shared-cohort normalization endpoint")
    cohort.require(not normalizer.pool.live and normalizer.closed, "normalizer closed")
    returned.clear()
    erase_marker(returned)
    degree.close()
    for value in (width, count):
        value.close()
    left.clear()
    right.clear()
    cohort.ready()
    return {"catalogue": inventory(selected["programs"]), "physical_literals": len(catalogue),
            "packet_sha256": digest.hexdigest(), "scalar_peak_leases": engine.pool.peak,
            "normalizer_peak_leases": normalizer.pool.peak, "cohort_inputs": len(api["inputs"]),
            "scope": "Full scalar literal packets and shared normalization cohort; complete controller checks run separately."}


if __name__ == "__main__":
    print(json.dumps(run(), sort_keys=True, indent=2))
