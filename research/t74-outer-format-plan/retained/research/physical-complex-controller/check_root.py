# SPDX-License-Identifier: Apache-2.0
"""Complete root outputs against an independent rational Walsh oracle."""
import argparse
from collections import Counter
from fractions import Fraction
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
from macro_code import Code
from machine import copy_symbols
from ordinary import Ordinary
from records import Tape
from root_layer import RootLayer
from root_plan import RootPlan
from session import erase_marker
from words import BLANK, RIGHT


def integer(count):
    count.rewind()
    value, power = 0, 1
    while count.read() != RIGHT:
        value += power * count.read()
        power *= 2
        count.step(1)
    count.rewind()
    return value


class OneCover:
    size = 1

    @staticmethod
    def unrank(index):
        cohort.require(index == 0, "single reduced cover")
        return (1, 2)


class ReducedPlan(RootPlan):
    """One explicit small fast-branch plan, outside the production p-parameter law."""
    def compute(self, precision, selected, left, right, coefficients, outer_rows, residue):
        cohort.require(tuple(map(integer, (precision, selected, left, right, coefficients, outer_rows, residue)))
                       == (9, 8, 0, 0, 1, 1, 0), "fixed reduced root fixture")
        values = dict(precision=9, selected=8, left=0, right=0, coefficients=1, outer_rows=1,
                      residue=0, zero=0, d=8, K=1, G=1, H=1, depth=3, q0=3, qF=2, qB=1,
                      Q0=6, delta=32, input_bits=11, work_bits=76, gaussians=256, prefixes=1,
                      original_rows=8, padded_rows=8, stock=8, row_bits=4864,
                      core_width=2, core_front=0, core_back=0)
        self.clear()
        for name, value in values.items():
            count = Count.literal(value)
            copy_symbols(count.tape, self.roles[name])
            count.close()
        self.fast = True
        return self


def encode(values, width):
    return bytes((int(value) >> bit) & 1 for pair in values for value in pair for bit in range(width))


def body(tape):
    return bytes(tape.cells[1:]).rstrip(bytes([BLANK]))


def walsh(values, selected, left, right, spacing, residue, coefficients, rows):
    addresses = 1 << (left + selected * spacing + right)
    masks = [1 << (right + index * spacing + residue) for index in range(selected)]
    result = []
    for row in range(rows):
        for address in range(addresses):
            fixed = address
            for mask in masks:
                fixed &= ~mask
            for field in range(coefficients):
                sums = [0, 0]
                for subset in range(1 << selected):
                    source, sign = fixed, 1
                    for index, mask in enumerate(masks):
                        if subset >> index & 1:
                            source |= mask
                            if address & mask:
                                sign = -sign
                    pair = values[(row * addresses + source) * coefficients + field]
                    for component in range(2):
                        sums[component] += sign * pair[component]
                result.append(tuple(int(Fraction(value, 1 << selected)) for value in sums))
    return result


def run(fast=False):
    binding = FixtureBinding()
    if fast:
        binding.cover = OneCover()
    native = Ordinary(2, SimpleNamespace(codes=SimpleNamespace(q=2)), SimpleNamespace(families=0),
                      (Code((("unreachable",),), 0),), capacity=64)
    observations = Counter()

    def observe(machine, event):
        observations[event] += 1
        cohort.require(not machine.pool.live and not layer.pool.live, "closed pools at root child cut")

    plan_type = ReducedPlan if fast else RootPlan
    plan = plan_type(2, 1, 2 if fast else 4, guard_exponent=2)
    layer = RootLayer(binding, native, binding.catalogue, plan, observe)
    cases = [(9, 8, 0, 0, 1, 1, 0)] if fast else [
        (5, 0, 1, 1, 2, 2, 0), (5, 1, 1, 1, 2, 2, 0),
        (5, 2, 1, 0, 2, 1, 0), (6, 3, 0, 1, 1, 1, 0)]
    digest = sha256()
    packets = 0
    for parameters in cases:
        p, D, left, right, fields, rows, rho = parameters
        count = rows * (1 << (left + D + right)) * fields
        # Components <= 1/4, hence every input lies in the unit disk.
        values = [((i * 7) % 13 - 6, (i * 11) % 17 - 8) for i in range(count)]
        raw = encode(values, p + 2)
        expected = encode(walsh(values, D, left, right, 1, rho, fields, rows), p + 2)
        source = Tape()
        for bit in raw:
            source.append(bit)
        source.rewind()
        counts = tuple(Count.literal(value) for value in parameters)
        snapshots = tuple(bytes(value.tape.cells) for value in counts)
        result = layer.run(source, *counts)
        cohort.require(body(result) == expected, "complete physical H0 root endpoint")
        cohort.require(body(source) == raw and tuple(bytes(v.tape.cells) for v in counts) == snapshots,
                       "complete root preserves payload and descriptors")
        cohort.require(layer.closed and not layer.pool.live and layer.current.read() == BLANK and
                       all(t.read() == BLANK for t in plan.roles.values()), "closed root-owned state")
        digest.update(body(result))
        result.clear()
        erase_marker(result)
        source.clear()
        for value in counts:
            value.close()
        packets += 1
    return dict(packets=packets, recursive_events=dict(observations), sha256=digest.hexdigest(),
                scope="Reduced fast reservations" if fast else "Production root formulas with reduced guard constant",
                limitation="Neither fixture executes the selected O73/GL64 payload or production guard width.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--fast", action="store_true")
    print(json.dumps(run(parser.parse_args().fast), sort_keys=True, indent=2))
