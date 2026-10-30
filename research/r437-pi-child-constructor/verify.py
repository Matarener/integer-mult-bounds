#!/usr/bin/env python3
"""Exact program-tape invoice for children.extend, one term inside Pi_v.

The counting argument is in PROOF.md. This file executes the pinned
constructor and checks that argument, including the entry-head hypothesis
and the empty selected stock gate.
"""
import ast
import sys
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[2]
VENDOR = ROOT / "research/selected-bit-physical-caller/inputs/pr2753/predecessor/vendor"
BINDING = ROOT / "research/selected-bit-physical-caller/macro_binding.py"
sys.path.insert(0, str(VENDOR))

from children import extend  # noqa: E402
from records import FINITE_BITS, Program, ROOT, STEP  # noqa: E402
from words import LEFT, Arena, Unsigned  # noqa: E402


def need(condition, message):
    if not condition:
        raise SystemExit("FAIL_R437_PI_CHILD_CONSTRUCTOR " + message)


def tape_counts(index_bits, residue_bits, code_bits, steps):
    """Program-tape meters of extend. Parent tape enters already rewound."""
    step = code_bits + 2 * index_bits + 5 * FINITE_BITS + 10
    root = 2 * index_bits + residue_bits + 5
    copied = steps * step
    child = root + (steps + 1) * step
    parent = (2 * root + 3 * copied + 3, 0, 2 * root + 2 * copied + 4)
    produced = (2 * child + 1, child, 2 * child + 2)
    return parent, produced, child


def meter(tape):
    return (tape.meter.reads, tape.meter.writes, tape.meter.moves)


def plus(raw):
    def add(left, right):
        out, carry = raw.add(left, right)
        need(not carry, "index addition left the fixed width")
        return out
    return add


def execute(index_bits, residue_bits, code_bits, steps, kind, rank, half, root_value):
    indices = Arena(index_bits, 64)
    residues = Arena(residue_bits, 16)
    events = []
    current = root_value
    for _ in range(steps):
        quotient = current // 64
        if kind == "good":
            current = rank * quotient
        elif half:
            current = quotient // 2
        else:
            current = quotient
        need(current > 0, "fixture history collapsed")
        events.append(({"good": 0, "pair": 1, "unit": 2}[kind], 1, rank, 0, 0, int(half)))
    program = Program.fixture(indices, residues, root_value, 1, events, code_bits=code_bits)
    need(program.tape.head == 1, "fixture did not rewind the parent")
    raw = Unsigned(indices)
    before_parent = meter(program.tape)
    before_index = indices.meter.reads
    incoming = SimpleNamespace(
        program=program,
        index=indices,
        residue=residues,
        raw=raw,
        specifications={1: SimpleNamespace(template=SimpleNamespace(rank=rank))},
        current_code=1,
        final_size=indices.input(current),
        sixty_four=indices.literal(64),
        two_index=indices.literal(2),
        one_index=indices.literal(1),
        depth=indices.input(steps),
        root_size=indices.input(root_value),
        root_unit=residues.input(1),
        plus=plus(raw),
    )
    request = SimpleNamespace(
        child_kind=kind, coordinate=indices.input(0), field=0, reverse=False, half=half)
    produced = extend(incoming, request)
    parent = tuple(after - before for after, before in zip(meter(program.tape), before_parent))
    return parent, meter(produced.tape), produced, indices.meter.reads - before_index


def selected_stock_gate_is_empty():
    tree = ast.parse(BINDING.read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == "SelectedBinding":
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and item.name == "check_stock":
                    return len(item.body) == 1 and isinstance(item.body[0], ast.Pass)
    return False


def main():
    need(FINITE_BITS == 16, "pinned finite vocabulary width changed")
    need("prefix" not in extend.__code__.co_names, "extend names a prefix tape")
    need(selected_stock_gate_is_empty(), "SelectedBinding.check_stock is no longer empty")
    cases = []
    for index_bits in (8, 10, 12):
        for residue_bits in (2, 5):
            for code_bits in (1, 16):
                for steps in (0, 1, 4):
                    cases.append((index_bits, residue_bits, code_bits, steps, "good", 64, False, 64))
    cases.extend((
        (10, 4, 16, 0, "good", 2, False, 128),
        (10, 4, 16, 0, "unit", 3, False, 64),
        (10, 4, 16, 0, "pair", 3, False, 64),
        (12, 4, 8, 0, "unit", 4, True, 128),
    ))
    index_growth = []
    for case in cases:
        expected_parent, expected_child, symbols = tape_counts(*case[:4])
        parent, child, produced, index_reads = execute(*case)
        need(parent == expected_parent, "parent meter " + str(case) + " " + str(parent))
        need(child == expected_child, "child meter " + str(case) + " " + str(child))
        need(len(produced.tape.cells) == symbols + 1, "child length " + str(case))
        need(produced.tape.head == 1 and produced.tape.cells[0] == LEFT, "child not rewound")
        body = list(produced.tape.cells)
        need(body.count(ROOT) == 1 and body.count(STEP) == case[3] + 1, "record census " + str(case))
        need(child[1] == symbols and symbols > 0, "production writes vanished")
        index_growth.append(index_reads)
    need(any(value > 0 for value in index_growth), "index arena was idle during extend")
    # A parent head that is not the rewind postcondition is outside the formula.
    shifted = execute(10, 4, 16, 2, "good", 64, False, 64)
    # Re-run with the head moved after the fixture rewind, through a local copy of execute's setup.
    indices = Arena(10, 64)
    residues = Arena(4, 16)
    events = []
    current = 64
    for _ in range(2):
        current = 64 * (current // 64)
        events.append((0, 1, 64, 0, 0, 0))
    program = Program.fixture(indices, residues, 64, 1, events, code_bits=16)
    program.tape.step(1)
    raw = Unsigned(indices)
    before = meter(program.tape)
    incoming = SimpleNamespace(
        program=program, index=indices, residue=residues, raw=raw,
        specifications={1: SimpleNamespace(template=SimpleNamespace(rank=64))},
        current_code=1, final_size=indices.input(64), sixty_four=indices.literal(64),
        two_index=indices.literal(2), one_index=indices.literal(1),
        depth=indices.input(2), root_size=indices.input(64), root_unit=residues.input(1),
        plus=plus(raw))
    produced = extend(incoming, SimpleNamespace(
        child_kind="good", coordinate=indices.input(0), field=0, reverse=False, half=False))
    shifted_parent = tuple(a - b for a, b in zip(meter(program.tape), before))
    expected_parent, _, _ = tape_counts(10, 4, 16, 2)
    need(shifted_parent != expected_parent, "unrewound entry matched the rewound formula")
    need(meter(produced.tape)[1] > 0, "shifted entry produced an empty child")
    # Dropping one parent read per copied step is the nearby false invoice.
    false_reads = expected_parent[0] - 2 * (16 + 20 + 5 * FINITE_BITS + 10)
    need(shifted[0] == expected_parent, "control case drifted")
    need(shifted[0][0] != false_reads, "one-read-per-symbol invoice also matched")
    print(
        "PASS_R437_PI_CHILD_CONSTRUCTOR"
        " cases=%d finite_bits=%d stock_gate=pass prefix_in_extend=false"
        " index_reads_seen=%s no_new_kappa"
        % (len(cases), FINITE_BITS, max(index_growth)))


if __name__ == "__main__":
    main()
