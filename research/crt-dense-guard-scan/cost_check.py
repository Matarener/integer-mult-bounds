"""Independent cost/ownership checker; imports the literal kernel, not its verifier.

Written with substantial OpenAI Codex assistance. Apache-2.0.
Finite checks corroborate the separately written quantified cost derivation.
"""
import argparse
import ast
import hashlib
import json
from pathlib import Path
import sys
import types


def need(condition, message):
    if not condition:
        raise ValueError(message)


def load_kernel(path):
    data = path.read_bytes()
    module = types.ModuleType("_independent_literal_guard_cost")
    module.__file__ = str(path)
    sys.modules[module.__name__] = module
    exec(compile(data, str(path), "exec"), module.__dict__)
    return module, data


def inspect_program(data):
    """A structural guardrail, not a complete finite-state formalization."""
    tree = ast.parse(data)
    functions = {node.name: node for node in tree.body if isinstance(node, ast.FunctionDef)}
    names = ("rewind", "compare_flag", "predicate", "increment_and_return", "erase_counter", "transduce")
    forbidden_attributes = {"head", "cells", "actions", "reads", "writes", "moves"}
    forbidden_calls = {"len", "range", "enumerate", "int", "sum", "any", "all", "zip"}
    for name in names:
        need(name in functions, "missing literal program function: " + name)
        for node in ast.walk(functions[name]):
            if isinstance(node, ast.Attribute):
                need(node.attr not in forbidden_attributes, "literal program reads simulator observer: " + node.attr)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                need(node.func.id not in forbidden_calls, "literal program uses host iteration/index helper: " + node.func.id)
    return {"functions_inspected": list(names), "observer_accesses": 0,
            "scope": "AST guardrail plus manual finite-control review, not a complete program proof"}


def run(machine, cells, expected):
    stencil = machine.Tape([machine.LEFT] + list(cells) + [machine.END])
    original = list(stencil.cells)
    counter, mask = machine.transduce(stencil)
    length = len(cells)
    records = 1 << length
    need(stencil.cells == original, "protected stencil changed")
    need(stencil.head == counter.head == mask.head == 0, "head return contract")
    need(counter.cells == [machine.LEFT] + [machine.BLANK] * (length + 1), "private blank erasure including end marker")
    need(mask.cells == [machine.LEFT] + list(expected) + [machine.END], "complete owned mask/markers")
    actual = {"reads": sum(t.reads for t in (stencil, counter, mask)),
              "writes": sum(t.writes for t in (stencil, counter, mask)),
              "moves": sum(t.moves for t in (stencil, counter, mask))}
    wanted = {"reads": (4 * length + 6) * records + 5 * length + 9,
              "writes": 3 * records + 2 * length + 1,
              "moves": (4 * length + 6) * records + 6 * length + 8}
    need(actual == wanted, "independently derived read/write/move invoice")
    visited = sum(len(t.cells) for t in (stencil, counter, mask))
    need(visited == records + 2 * length + 6, "exact complete visited space")
    return {"L": length, "M": records, **actual,
            "actions": sum(actual.values()), "visited_cells": visited,
            "mask_sha256": hashlib.sha256(expected.encode()).hexdigest()}


def undercharged_read_control(machine):
    """Observer-ledger fault: omit one charged READ while preserving semantics."""
    base = machine.Tape
    changed = [False]

    class UnderchargedTape(base):
        def read(self):
            value = super().read()
            if not changed[0]:
                self.reads -= 1
                changed[0] = True
            return value

    machine.Tape = UnderchargedTape
    try:
        try:
            run(machine, [machine.SKIP], "00")
        except ValueError as error:
            need(str(error) == "independently derived read/write/move invoice", "tariff mutant failed for another reason")
            return {"name": "one READ omitted from observer tariff; mask and ownership preserved", "detected_by": str(error)}
        raise ValueError("undercharged read accepted")
    finally:
        machine.Tape = base


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--machine", type=Path, default=Path(__file__).resolve().with_name("machine.py"))
    args = parser.parse_args()
    machine, data = load_kernel(args.machine)
    structural = inspect_program(data)
    rows = []
    for length in range(1, 11):
        rows.append({"name": "all_skip", **run(machine, [machine.SKIP] * length, "0" * (1 << length))})
    rows.append({"name": "single_cell_digit", **run(machine, [("D", True, True, "0", "0")], "01")})
    rows.append({"name": "single_cell_guard", **run(machine, [("G", True, True, "0", "1")], "01")})
    rows.append({"name": "two_adjacent_single_cell_digits", **run(machine, [("D", True, True, "0", "0")] * 2, "0111")})
    rows.append({"name": "two_cell_MSB_guard", **run(machine, [("G", True, False, "0", "1"), ("G", False, True, "1", "1")], "1001")})
    report = {"result": "PASS_INDEPENDENT_LITERAL_GUARD_COST",
              "kernel_sha256": hashlib.sha256(data).hexdigest(),
              "cases": len(rows), "complete_addresses": sum(r["M"] for r in rows),
              "rows": rows, "structural_guardrail": structural,
              "cost_fault_controls": [undercharged_read_control(machine)],
              "scope": "Admitted fixed-alphabet stencil only; no construction/admission/E/payload tariff"}
    print(json.dumps(report, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
