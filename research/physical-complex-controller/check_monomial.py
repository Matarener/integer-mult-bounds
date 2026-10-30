# SPDX-License-Identifier: Apache-2.0
"""Finite physical selection/inverse checks with a direct address oracle."""
from hashlib import sha256
import json
from pathlib import Path
import sys
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cohort
cohort.monomial_api()
from cardinal_counts import Count
from macro_code import Code
from monomial_packets import MonomialPackets, identity_literal
from ordinary import Ordinary
from records import Tape
from session import erase_marker
from words import BLANK


def encode(values, width):
    return bytes((v >> j) & 1 for v in values for j in range(width))


def decode(raw):
    value = sum(bit << i for i, bit in enumerate(raw))
    return value - (1 << len(raw)) if raw[-1] else value


def rotate(real, imag, phase):
    return ((real, imag), (-imag, real), (-real, -imag), (imag, -real))[phase % 4]


def oracle(raw, widths, literal, f, h, rows, inverse):
    records = 1 << sum(widths)
    out = bytearray(len(raw))
    for row in range(rows):
        for address in range(records):
            values, remaining = [0] * len(widths), address
            for i in reversed(range(len(widths))):
                values[i] = remaining % (1 << widths[i])
                remaining >>= widths[i]
            changed = list(values)
            phase = f * literal["phase"]
            for column in range(f):
                bits = [(values[2 + i] >> column) & 1 for i in range(2)]
                phase += sum(a * b for a, b in zip(literal["linear_Z4"], bits))
                phase += 2 * bits[0] * bits[1] * ((literal["quadratic_rows"][0] >> 1) & 1)
                for i in range(2):
                    value = ((literal["offset"] >> i) & 1) ^ (
                        sum(((literal["matrix_rows"][i] >> j) & 1) * bits[j] for j in range(2)) % 2)
                    changed[2 + i] = (changed[2 + i] & ~(1 << column)) | (value << column)
            destination = 0
            for value, width in zip(changed, widths):
                destination = (destination << width) + value
            source, target = (destination, address) if inverse else (address, destination)
            start = (row * records + source) * 2 * h
            pair = rotate(decode(raw[start:start + h]), decode(raw[start + h:start + 2 * h]),
                          -phase if inverse else phase)
            start_out = (row * records + target) * 2 * h
            out[start_out:start_out + 2 * h] = encode(pair, h)
    return bytes(out)


def run():
    # This finite q=2 fixture reaches the ordinary elementary branch. It does
    # not instantiate the selected large-prime BIT source or its full cover.
    native = Ordinary(2, SimpleNamespace(codes=SimpleNamespace(q=2)),
                      SimpleNamespace(families=0), (Code((("unreachable",),), 0),), capacity=64)
    names = ("u", "t", "v0", "v1", "b")
    engine = MonomialPackets(names, ("v0", "v1"), native)
    literals = [identity_literal(2),
                dict(matrix_rows=[3, 1], offset=1, phase=1, linear_Z4=[1, 2], quadratic_rows=[2, 0]),
                dict(matrix_rows=[2, 1], offset=2, phase=3, linear_Z4=[3, 1], quadratic_rows=[0, 0])]
    source = Tape()
    digest = sha256()
    cases = 0
    for f in (1, 2):
        widths0 = (f - 1, f - 1, f, f, f - 1)
        widths = tuple(Count.literal(v) for v in widths0)
        args = tuple(Count.literal(v) for v in (f, 1, 1, 0, 8, 1, 2))
        values = [4 * ((i * 5) % 7 - 3) for i in range(4 * (1 << sum(widths0)))]
        raw = encode(values, 8)
        for literal in literals:
            engine.select(literal)
            for inverse in (False, True):
                source.clear()
                for bit in raw:
                    source.append(bit)
                source.rewind()
                expected = oracle(raw, widths0, literal, f, 8, 2, inverse)
                returned = engine.run(source, widths, *args, inverse=inverse)
                actual = bytes(returned.cells[1:]).rstrip(bytes([BLANK]))
                cohort.require(actual == expected, "selected monomial physical endpoint")
                cohort.require(bytes(source.cells[1:]).rstrip(bytes([BLANK])) == raw,
                               "monomial preserves borrowed packet")
                cohort.require(engine.closed and not engine.pool.live and engine.compact.closed,
                               "monomial closes work")
                digest.update(actual)
                returned.clear()
                erase_marker(returned)
                cases += 1
        for value in (*widths, *args):
            value.close()
    source.clear()
    cohort.ready()
    return {"complete_packets": cases, "columns": [1, 2], "outer_rows": 2,
            "sha256": digest.hexdigest(), "peak_leases": engine.pool.peak,
            "scope": "Selectable two-coordinate physical monomials with an elementary q=2 ordinary fixture; no selected full-cover payload execution."}


if __name__ == "__main__":
    print(json.dumps(run(), sort_keys=True, indent=2))
