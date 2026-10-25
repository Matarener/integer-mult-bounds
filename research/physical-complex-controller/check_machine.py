# SPDX-License-Identifier: Apache-2.0
"""Complete recursive physical fixtures versus an independent Gaussian oracle."""
import argparse
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path
import sys
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cohort
cohort.activate()
from cardinal_counts import Count
from fixture_binding import FixtureBinding
from machine import Machine
from macro_code import Code
from ordinary import Ordinary
from records import Tape
from words import BLANK


def encode(values, bits):
    return bytes((int(x) >> bit) & 1 for pair in values for x in pair for bit in range(bits))


def oracle(values, width, compact, rows, coefficients):
    result = [tuple(map(Q, pair)) for pair in values]
    address_bits = width + 3 * compact
    records = 1 << address_bits
    for axis in range(width):
        bit = 1 << (compact + axis)
        for row in range(rows):
            for address in range(records):
                if address & bit:
                    continue
                for field in range(coefficients):
                    i = (row * records + address) * coefficients + field
                    j = (row * records + address + bit) * coefficients + field
                    a, b = result[i]
                    c, d = result[j]
                    result[i] = ((a - b + c + d) / 2, (a + b - c + d) / 2)
                    result[j] = ((a + b + c - d) / 2, (-a + b + c + d) / 2)
    if any(x.denominator != 1 for pair in result for x in pair):
        raise ValueError("independent fixture grid")
    return result


def run(width):
    binding = FixtureBinding()
    native = Ordinary(2, SimpleNamespace(codes=SimpleNamespace(q=2)),
                      SimpleNamespace(families=0), (Code((("unreachable",),), 0),), capacity=64)
    observations = Counter()

    def observe(machine, event):
        observations[event] += 1
        if machine.pool.live:
            raise ValueError("scratch at a recursive boundary")

    machine = Machine(binding, native, binding.catalogue, observe)
    depth, n = 0, width
    while n >= 2:
        depth += 1
        n //= 2
    rows = 4 ** depth
    prefixes = 2 if width == 3 else 1
    coefficients = 2 if width == 3 else 1
    compact = max(0, width // 2 - 1)
    bits = 12 if width >= 4 else 20
    raw_descriptors = dict(prefixes=prefixes, rows=rows, front=0, compact_bits=compact,
        before=0, width=width, after=0, back=0, spacing=1, guard=1, residue=0,
        component_bits=bits, coefficients=coefficients, root_width=max(1, width))
    descriptors = {name: Count.literal(value) for name, value in raw_descriptors.items()}
    count = prefixes * rows * (1 << (width + 3 * compact)) * coefficients
    scale = 16 if width >= 4 else 256
    values = [(scale * ((i * 7) % 11 - 5), scale * ((i * 3) % 7 - 3)) for i in range(count)]
    raw = encode(values, bits)
    expected = encode(oracle(values, width, compact, prefixes * rows, coefficients), bits)
    source = Tape()
    for bit in raw:
        source.append(bit)
    source.rewind()
    snapshots = {name: bytes(value.tape.cells) for name, value in descriptors.items()}
    returned = machine.run(source, descriptors)
    actual = bytes(returned.cells[1:]).rstrip(bytes([BLANK]))
    cohort.require(actual == expected, "complete recursive Gaussian endpoint")
    cohort.require(bytes(source.cells[1:]).rstrip(bytes([BLANK])) == raw, "prepared root preserves source")
    cohort.require(all(bytes(value.tape.cells) == snapshots[name] for name, value in descriptors.items()),
                   "root preserves encoded descriptors")
    cohort.require(machine.closed and observations["enter"] == observations["return"] and
                   all(t.read() == BLANK for t in machine.parked), "complete recursive root return")
    machine.parking.empty()
    returned.clear()
    source.clear()
    for value in descriptors.values():
        value.close()
    return {"active_width": width, "logical_rows": rows, "outer_prefixes": prefixes,
            "coefficients": coefficients, "Gaussian_values": count, "payload_bits": len(raw),
            "calls_and_returns": dict(observations), "sha256": sha256(actual).hexdigest(),
            "scope": "Complete reduced-geometry recursive C execution; not a selected O73 payload or root-grid admission."}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--width", type=int, default=2)
    args = parser.parse_args()
    print(json.dumps(run(args.width), sort_keys=True, indent=2))
