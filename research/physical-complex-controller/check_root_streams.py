# SPDX-License-Identifier: Apache-2.0
"""Independent finite root phase/padding oracles with complete outer prefixes."""
from hashlib import sha256
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cohort
cohort.activate()
from cardinal_counts import Count
from grid_boundary import GridDomainError
from records import Tape
from root_streams import PhaseSweep, RowPadding
from session import erase_marker
from words import BLANK


def body(tape):
    return bytes(tape.cells[1:]).rstrip(bytes([BLANK]))


def fill(tape, data):
    tape.clear()
    for bit in data:
        tape.append(bit)
    tape.rewind()


def encode(values, width):
    return bytes((v >> bit) & 1 for pair in values for v in pair for bit in range(width))


def run():
    phase = PhaseSweep()
    pad = RowPadding()
    source = Tape()
    copied = Tape()
    digest = sha256()
    for D, K, rho in ((0, 1, 0), (1, 1, 0), (2, 2, 1), (3, 1, 0)):
        address_bits = 2 + D * K
        records = 1 << address_bits
        values = [(i % 7 - 3, (i * 3) % 5 - 2) for i in range(2 * records)]
        expected = []
        for row in range(2):
            for address in range(records):
                selected_value = (address >> 1) & ((1 << (D * K)) - 1)
                turn = sum((selected_value >> (rho + j * K)) & 1 for j in range(D)) % 4
                a, b = values[row * records + address]
                expected.append(((a, b), (-b, a), (-a, -b), (b, -a))[turn])
        args = tuple(Count.literal(v) for v in (1, D, 1, K, rho, 8, 1, 2))
        raw = encode(values, 8)
        fill(source, raw)
        returned = phase.run(source, *args)
        cohort.require(body(returned) == encode(expected, 8) and body(source) == raw, "complete root phase sweep")
        digest.update(body(returned))
        returned.clear()
        erase_marker(returned)
        for value in args:
            value.close()
    for P, R, T, B in ((1, 1, 1, 3), (2, 3, 4, 7), (3, 5, 8, 11)):
        args = tuple(Count.literal(v) for v in (P, R, T, B))
        raw = bytes((i * i // 3) & 1 for i in range(P * R * B))
        fill(source, raw)
        returned = pad.run(source, *args)
        expected = b"".join(raw[p * R * B:(p + 1) * R * B] + bytes((T - R) * B) for p in range(P))
        cohort.require(body(returned) == expected and body(source) == raw, "complete prefix row padding")
        fill(copied, body(returned))
        returned.clear()
        erase_marker(returned)
        returned = pad.run(copied, *args, remove=True)
        cohort.require(body(returned) == raw and body(copied) == expected, "exact zero-row removal")
        returned.clear()
        erase_marker(returned)
        if T > R:
            mutant = bytearray(expected)
            mutant[R * B] = 1
            fill(copied, mutant)
            try:
                pad.run(copied, *args, remove=True)
            except GridDomainError:
                pass
            else:
                raise ValueError("nonzero padded output accepted")
            cohort.require(body(copied) == mutant and pad.closed and not pad.pool.live, "padding rejection preserves source")
        digest.update(expected)
        for value in args:
            value.close()
    source.clear()
    copied.clear()
    return {"phase_packets": 4, "padding_round_trips": 3, "nonzero_padding_rejections": 2,
            "sha256": digest.hexdigest(), "phase_peak": phase.pool.peak, "padding_peak": pad.pool.peak}


if __name__ == "__main__":
    print(json.dumps(run(), sort_keys=True, indent=2))
