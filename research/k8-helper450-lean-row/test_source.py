#!/usr/bin/env python3
"""Independent scalar semantics and source-binding controls.

Copyright 2026 Sagar Thakrar. Substantial OpenAI Codex assistance.
SPDX-License-Identifier: Apache-2.0
"""

from copy import deepcopy
from fractions import Fraction
from pathlib import Path
import tempfile
import unittest
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))

import source


def literal_row(events, output=450):
    """Reverse covector multiplication; COPY/CLEAR are not inverse execution."""
    row = {output: Fraction(1)}
    for event in reversed(events):
        kind, target = event[:2]
        if kind == "relabel":
            continue
        value = row.get(target, Fraction(0))
        if kind == "add":
            _, _, operand, numerator, denominator = event
            row[operand] = row.get(operand, Fraction(0)) + value * Fraction(numerator, denominator)
        elif kind == "scale":
            row[target] = value * Fraction(event[2], event[3])
        elif kind == "copy":
            row.pop(target, None)
            row[event[2]] = row.get(event[2], Fraction(0)) + value
        elif kind == "clear":
            row.pop(target, None)
        else:
            raise ValueError("unknown literal constructor")
        row = {key: value for key, value in row.items() if value}
    return row


class SourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.inputs = source.authenticate()
        cls.translator, _ = source.retained_modules(cls.inputs)
        cls.events, cls.start, cls.indices, cls.receipt = source._translate(cls.inputs)[:4]

    def test_complete_source_and_independent_endpoint(self):
        self.assertEqual((len(self.events), len(self.start), len(self.indices)), (24757, 712, 24757))
        self.assertEqual(self.receipt["serialized_events"], 24767)
        self.assertEqual(self.receipt["omitted_phase_markers"], 10)
        self.assertEqual(self.receipt["constructors"],
                         {"add": 18962, "scale": 707, "copy": 8, "clear": 16, "relabel": 5064})
        self.assertEqual(literal_row(self.events), {450: Fraction(1)})

    def test_active_gate_mutants_fail_independent_row(self):
        mutants = {}
        changed = deepcopy(self.events)
        changed[source.FIRST][-2] = -1
        mutants["sign"] = changed
        changed = deepcopy(self.events)
        changed[source.SECOND][1] = 451
        mutants["target"] = changed
        changed = deepcopy(self.events)
        del changed[source.FIRST]
        mutants["omitted"] = changed
        changed = deepcopy(self.events)
        changed[source.SECOND][2] = 231
        mutants["partner"] = changed
        for name, events in mutants.items():
            with self.subTest(name=name):
                self.assertNotEqual(literal_row(events), {450: Fraction(1)})
                with self.assertRaises(ValueError):
                    source.row_schedule(events)

    def test_inactive_block_target_mutant(self):
        changed = deepcopy(self.events)
        changed[source.FIRST + 1] = ["scale", 230, 2, 1]
        self.assertNotEqual(literal_row(changed), {450: Fraction(1)})
        with self.assertRaisesRegex(ValueError, "protected row target"):
            source.row_schedule(changed)

    def test_copy_and_clear_have_distinct_semantics(self):
        copy = ["copy", 704, 450, 0]
        clear = ["clear", 704, 0]
        add = ["add", 450, 704, 1, 1]
        self.assertEqual(literal_row([copy, add]), {450: Fraction(2)})
        self.assertEqual(literal_row([copy, clear, add]), {450: Fraction(1)})
        self.assertEqual(literal_row([clear, add]), {450: Fraction(1)})
        self.assertEqual(literal_row([add]), {450: Fraction(1), 704: Fraction(1)})
        self.assertEqual(literal_row([copy], 704), {450: Fraction(1)})
        self.assertEqual(literal_row([clear], 704), {})

    def test_retained_parser_rejects_malformed_scalars(self):
        bad = [["mystery", ["L", 0]], ["scale", ["L", 0], 1, 0],
               ["scale", ["L", 0], True, 1], ["scale", ["L", 0], 0.5, 1],
               ["add", ["L", 0], ["L", 0], 1, 1],
               ["copy", ["C", 8], ["L", 0]], ["clear", ["L", 704]]]
        for operation in bad:
            with self.subTest(operation=operation), self.assertRaises(ValueError):
                self.translator.scalar(operation, 0)
        with self.assertRaises(ValueError):
            self.translator.translate_event({}, ["unknown_event", 0])
        self.assertEqual(self.translator.scalar(["scale", ["C", 0], 2, -4], 0),
                         ["scale", 704, -1, 2])

    def test_source_corruption_precedes_execution(self):
        rows = source.decoded((source.HERE / "SOURCES.json").read_bytes())["files"]
        first = next(row for row in rows if row["usage"] == "input")
        with tempfile.TemporaryDirectory(prefix="helper450-source-control-") as directory:
            path = Path(directory) / first["path"]
            path.parent.mkdir(parents=True)
            path.write_bytes(self.inputs[first["path"]] + b"\n")
            with self.assertRaisesRegex(ValueError, "Input changed"):
                source.authenticate(Path(directory))

    def test_unchanged_generator_matches_retained_kernel_sources(self):
        with tempfile.TemporaryDirectory(prefix="helper450-generation-control-") as directory:
            paths, receipt = source.emit_existing(directory)
            self.assertEqual(len(paths), 14)
            self.assertEqual(len(receipt["generated_sha256"]), 14)
            root = next(path for path in paths if path.name == "ForwardResult.lean")
            self.assertIn("namespace K8.Forward", root.read_text())
            self.assertIn("def events := blocks.flatten", root.read_text())


if __name__ == "__main__":
    unittest.main()
