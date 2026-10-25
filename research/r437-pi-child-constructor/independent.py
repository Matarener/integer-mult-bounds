#!/usr/bin/env python3
"""Second invoice for children.extend. Does not import verify.py."""
import sys
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "research/selected-bit-physical-caller/inputs/pr2753/predecessor/vendor"))

from children import extend  # noqa: E402
from records import FINITE_BITS, Program  # noqa: E402
from words import Arena, Unsigned  # noqa: E402


def need(condition, message):
    if not condition:
        raise SystemExit("FAIL_R437_PI_CHILD_INDEPENDENT " + message)


def invoice(index_bits, residue_bits, code_bits, steps, finite_bits):
    step_symbols = 1 + (code_bits + 1) + 5 * (finite_bits + 1) + 2 * (index_bits + 1) + 1
    root_symbols = 1 + 2 * (index_bits + 1) + (residue_bits + 1) + 1
    child_symbols = root_symbols + (steps + 1) * step_symbols
    copied = steps * step_symbols
    parent_reads = 1 + root_symbols + (2 * copied + 1) + (root_symbols + copied + 1)
    parent_moves = 2 + root_symbols + copied + (root_symbols + copied + 2)
    return (parent_reads, 0, parent_moves), (2 * child_symbols + 1, child_symbols, 2 * child_symbols + 2)


def run(index_bits, residue_bits, code_bits, steps):
    indices, residues = Arena(index_bits, 32), Arena(residue_bits, 8)
    events = [(0, 1, 64, 0, 0, 0) for _ in range(steps)]
    program = Program.fixture(indices, residues, 64, 1, events, code_bits=code_bits)
    raw = Unsigned(indices)
    before = (program.tape.meter.reads, program.tape.meter.writes, program.tape.meter.moves)

    def add(left, right):
        out, carry = raw.add(left, right)
        need(not carry, "carry")
        return out

    incoming = SimpleNamespace(
        program=program, index=indices, residue=residues, raw=raw,
        specifications={1: SimpleNamespace(template=SimpleNamespace(rank=64))},
        current_code=1, final_size=indices.input(64), sixty_four=indices.literal(64),
        two_index=indices.literal(2), one_index=indices.literal(1),
        depth=indices.input(steps), root_size=indices.input(64), root_unit=residues.input(1),
        plus=add)
    produced = extend(incoming, SimpleNamespace(
        child_kind="good", coordinate=indices.input(0), field=0, reverse=False, half=False))
    after = (program.tape.meter.reads, program.tape.meter.writes, program.tape.meter.moves)
    parent = tuple(a - b for a, b in zip(after, before))
    child = (produced.tape.meter.reads, produced.tape.meter.writes, produced.tape.meter.moves)
    return parent, child


def main():
    need(FINITE_BITS == 16, "finite width")
    total = 0
    for index_bits, residue_bits, code_bits, steps in (
            (8, 2, 1, 0), (10, 4, 16, 3), (12, 6, 8, 5)):
        parent, child = run(index_bits, residue_bits, code_bits, steps)
        expected_parent, expected_child = invoice(index_bits, residue_bits, code_bits, steps, FINITE_BITS)
        need(parent == expected_parent and child == expected_child, str((parent, child)))
        total += 1
    print("PASS_R437_PI_CHILD_INDEPENDENT cases=%d no_new_kappa" % total)


if __name__ == "__main__":
    main()
