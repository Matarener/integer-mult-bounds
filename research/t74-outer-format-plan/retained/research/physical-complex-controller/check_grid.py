# SPDX-License-Identifier: Apache-2.0
"""Complete small signed root boundaries and independent integer controls."""
from hashlib import sha256
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cohort
cohort.activate()
from cardinal_counts import Count
from grid_boundary import GridBoundary, GridDomainError
from records import Tape
from session import erase_marker
from words import BLANK


def encode(values, width):
    return bytes((value >> bit) & 1 for value in values for bit in range(width))


def fill(tape, raw):
    tape.clear()
    for bit in raw:
        tape.append(bit)
    tape.rewind()


def body(tape):
    return bytes(tape.cells[1:]).rstrip(bytes([BLANK]))


def run():
    engine = GridBoundary()
    source = Tape()
    digest = sha256()
    cases = rejects = expansions = 0
    count = Count.literal(1)
    for h in range(2, 7):
        width = Count.literal(h)
        for g in range(h):
            low = Count.literal(g)
            for out in range(2, 7):
                out_count = Count.literal(out)
                for x in range(-(1 << (h - 1)), 1 << (h - 1)):
                    values = (x, -1)
                    raw = encode(values, h)
                    fill(source, raw)
                    expected = tuple(-((-v) >> g) if v < 0 else v >> g for v in values)
                    admitted = all(-(1 << (out - 1)) <= v < 1 << (out - 1) for v in expected)
                    try:
                        returned = engine.truncate(source, width, low, out_count, count)
                    except GridDomainError:
                        if admitted:
                            raise
                        rejects += 1
                    else:
                        cohort.require(admitted and body(returned) == encode(expected, out), "rounded signed root endpoint")
                        digest.update(body(returned))
                        returned.clear()
                        erase_marker(returned)
                    cohort.require(body(source) == raw and engine.closed and not engine.pool.live,
                                   "grid preserves borrowed source and closes work")
                    cases += 1
                out_count.close()
            high = Count.literal(3)
            for x in (-(1 << (h - 1)), -1, 0, (1 << (h - 1)) - 1):
                raw = encode((x, -1), h)
                fill(source, raw)
                returned = engine.expand(source, width, low, high, count)
                cohort.require(body(returned) == encode((x << g, -1 << g), h + g + 3), "signed guard embedding")
                returned.clear()
                erase_marker(returned)
                expansions += 1
            high.close()
            low.close()
        width.close()
    # -9/2 truncates to -4, which fits3 bits, although floor(-9/2)=-5 does not.
    width, low, out = (Count.literal(v) for v in (5, 1, 3))
    fill(source, encode((-9, -1), 5))
    returned = engine.truncate(source, width, low, out, count)
    cohort.require(body(returned) == encode((-4, 0), 3), "capacity follows correction")
    returned.clear()
    erase_marker(returned)
    for value in (width, low, out, count):
        value.close()
    source.clear()
    return {"signed_truncations": cases, "expected_headroom_rejections": rejects,
            "guard_embeddings": expansions, "negative_capacity_control": True,
            "peak_leases": engine.pool.peak, "sha256": digest.hexdigest()}


if __name__ == "__main__":
    print(json.dumps(run(), sort_keys=True, indent=2))
