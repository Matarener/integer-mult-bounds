#!/usr/bin/env python3
"""Literal source controls; small matrix witnesses specify composition order.

Copyright 2026 Sagar Thakrar. Substantial OpenAI Codex assistance.
SPDX-License-Identifier: Apache-2.0
"""

from copy import deepcopy
from fractions import Fraction
import gzip
import json
from pathlib import Path
import sys
import tarfile
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import source


def literal_assets():
    """Read original records directly, without either retained translator."""
    archive = HERE.parents[1] / "research/community-frontier1094-audit/selected-replay.tar.gz"
    prefix = "candidate/strict/global/base/providers/gauge44/"
    values = []
    with tarfile.open(archive, "r:gz") as stream:
        for name in ("CANONICAL-WORD.json.gz", "LOCAL-PROGRAMS.json.gz",
                     "CLIFFORD-RECIPES.json", "RESIDUAL-ADAPTERS.json"):
            data = stream.extractfile(prefix + name).read()
            values.append(json.loads(gzip.decompress(data) if name.endswith(".gz") else data))
    return values


def literal_recipe(event, recipes, residual):
    """Resolve raw record literals, never Nat labels or generated token IDs."""
    kind = event[0]
    if kind in ("climb", "center"):
        old, new, rank = event[-3:]
        index, record = next((i, r) for i, r in enumerate(recipes["children"])
                             if (r["old"], r["new"]) == (old, new))
        return ["child", index, rank, record["left"], record["right"]]
    if kind == "adapter":
        _, direction, register, _ = event
        role = "source" if direction == "old_to_new" and register < 112 else (
            "target" if direction == "new_to_old" and 112 <= register < 224 else None)
        if role is None:
            return ["identity"]
        port = register if role == "source" else register - 112
        record = next(r for r in recipes["endpoint_adapters"]
                      if (r["role"], r["port"]) == (role, port))
        return [role, record["left"]]
    _, side, _, entrance, *terminal = event
    key = str(entrance) if not terminal else f"{entrance}:{terminal[0]}"
    return [side, residual["recipes"][key]["right" if side == "pre" else "left"]]


def resolve_tokens(recipe, tables):
    if recipe[0] == "identity":
        return recipe
    if recipe[0] == "child":
        return recipe[:3] + [tables["monomials"][i] for i in recipe[3:]]
    return [recipe[0], tables["monomials"][recipe[1]]]


def address(record, value):
    """Literal monomial address permutation; no Clifford multiplication."""
    return record["offset"] ^ sum(((row & value).bit_count() & 1) << i
                                  for i, row in enumerate(record["matrix_rows"]))


def product(a, b):
    return tuple(tuple(sum(a[i][k] * b[k][j] for k in range(2)) for j in range(2))
                 for i in range(2))


def inverse(a):
    determinant = a[0][0] * a[1][1] - a[0][1] * a[1][0]
    return ((Fraction(a[1][1], determinant), Fraction(-a[0][1], determinant)),
            (Fraction(-a[1][0], determinant), Fraction(a[0][0], determinant)))


class DispatchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = source.load()
        cls.canonical, programs, cls.recipes, cls.residual = literal_assets()
        cls.raw = programs["forward"]
        cls.tables = cls.data["tables"]
        cls.rows = cls.data["occurrences"]

    def test_every_descriptor_matches_original_record_literals(self):
        semantic = 0
        expected = []
        for index, event in enumerate(self.raw):
            if event[0] == "phase":
                continue
            if event[0] != "scalar":
                register = 704 + event[1] if event[0] == "center" else event[2]
                expected.append((index, semantic, register, event))
            semantic += 1
        self.assertEqual((semantic, len(expected)), (24757, 5064))
        for row, (index, position, register, event) in zip(self.rows, expected, strict=True):
            self.assertEqual(row[:3], [index, position, register])
            self.assertEqual(resolve_tokens(row[5], self.tables),
                             literal_recipe(event, self.recipes, self.residual))
        centres = [row[2] for row in self.rows if self.raw[row[0]][0] == "center"]
        self.assertEqual(sorted(centres), list(range(704, 712)))
        used = {row[5][1] for row in self.rows if row[5][0] == "child"}
        missing = [(r["old"], r["new"], r["rank"])
                   for i, r in enumerate(self.recipes["children"]) if i not in used]
        self.assertEqual(len(used), 2888)
        self.assertEqual(missing, [(0, i, 8) for i in range(415, 423)])

    def test_tag_stride_is_712_not_typed_capacity_1024(self):
        wrapped = next(row for row in self.rows if row[2] == 450 and row[5][0] == "pre")
        self.assertEqual(wrapped[3:5], [2 + 1004 * (1 + 450 + 2 * 712), 2])
        self.assertEqual(source.decode_label(wrapped[3]), ("prew", 450, 2))
        self.assertEqual(self.data["receipt"]["typed_register_capacity"], 1024)
        with self.assertRaises(ValueError):
            source.dispatch(wrapped[3], wrapped[4], self.tables, stride=1024)
        for bad in (True, -1, 1.0, 1004 * (1 + 4 * 712), 1004 * (1 + 704)):
            with self.subTest(label=bad), self.assertRaises(ValueError):
                source.decode_label(bad)

    def test_centre_identity_and_duplicate_occurrences_cannot_disappear(self):
        centre = next(row for row in self.rows if self.raw[row[0]][0] == "center")
        identity = next(row for row in self.rows if row[5] == ["identity"])
        for row in (centre, identity):
            events, indices = deepcopy(self.data["events"]), self.data["indices"][:]
            del events[row[1]]
            del indices[row[1]]
            with self.assertRaisesRegex(ValueError, "complete source index order"):
                source.occurrences(self.raw, self.canonical, self.tables, events, indices)
        events, indices = deepcopy(self.data["events"]), self.data["indices"][:]
        events.insert(centre[1], events[centre[1]])
        indices.insert(centre[1], indices[centre[1]])
        with self.assertRaisesRegex(ValueError, "complete source index order"):
            source.occurrences(self.raw, self.canonical, self.tables, events, indices)

    def test_reversed_source_target_and_wrapper_orientation_fail(self):
        for kind in ("source", "target", "pre", "post"):
            row = next(r for r in self.rows if r[5][0] == kind)
            with self.subTest(kind=kind), self.assertRaises(ValueError):
                source.dispatch(row[4], row[3], self.tables)
        pre = next(row for row in self.rows if row[2] == 450 and row[5][0] == "pre")
        raw = deepcopy(self.raw)
        raw[pre[0]][1] = "post"
        with self.assertRaisesRegex(ValueError, "raw/label dispatch disagreement"):
            source.occurrences(raw, self.canonical, self.tables,
                               self.data["events"], self.data["indices"])

    def test_helper450_uses_literal_2_999_and_both_correct_sides(self):
        pre = next(row for row in self.rows if row[2] == 450 and row[5][0] == "pre")
        post = next(row for row in self.rows if row[2] == 450 and row[5][0] == "post")
        actual = self.residual["recipes"]["2:999"]
        full = self.residual["recipes"]["2"]
        self.assertEqual((pre[0], post[0]), (7852, 24562))
        self.assertEqual(resolve_tokens(pre[5], self.tables), ["pre", actual["right"]])
        self.assertEqual(resolve_tokens(post[5], self.tables), ["post", actual["left"]])
        self.assertEqual((address(actual["right"], 0), address(full["right"], 0)), (511, 241))
        self.assertEqual((address(actual["left"], 2), address(full["left"], 2)), (12, 18))
        raw = self.raw[pre[0]][:-1]
        with self.assertRaisesRegex(ValueError, "raw wrapper endpoint"):
            source.raw_descriptor(raw, self.canonical, self.tables)
        bad = deepcopy(self.tables)
        bad["residual"]["2:999"]["right"] = bad["residual"]["2"]["right"]
        wrong = source.dispatch(pre[3], pre[4], bad)
        self.assertNotEqual(resolve_tokens(wrong, bad), ["pre", actual["right"]])

    def test_child_rank_and_left_right_tokens_bind_to_raw_record(self):
        row = next(r for r in self.rows if r[5][0] == "child" and r[5][3] != r[5][4])
        raw = self.raw[row[0]][:]
        raw[-1] += 1
        with self.assertRaisesRegex(ValueError, "child rank mismatch"):
            source.raw_descriptor(raw, self.canonical, self.tables)
        for rank in (None, True):
            raw = self.raw[row[0]][:]
            raw[-1] = rank
            with self.subTest(rank=rank), self.assertRaisesRegex(ValueError, "raw child rank"):
                source.raw_descriptor(raw, self.canonical, self.tables)
        original = literal_recipe(self.raw[row[0]], self.recipes, self.residual)
        self.assertEqual(resolve_tokens(source.dispatch(row[3], row[4], self.tables), self.tables),
                         original)
        bad = deepcopy(self.tables)
        child = bad["children"][row[5][1]]
        child["left"], child["right"] = child["right"], child["left"]
        self.assertNotEqual(resolve_tokens(source.dispatch(row[3], row[4], bad), bad), original)

    def test_noncommuting_operator_order_specification_witnesses(self):
        # These independent witnesses specify the algebra; Lean checks the production definitions.
        frame, mono = ((1, 1), (0, 1)), ((1, 0), (1, 1))
        identity = ((1, 0), (0, 1))
        pre_tag = product(inverse(mono), frame)
        self.assertEqual(product(frame, inverse(pre_tag)), mono)
        self.assertNotEqual(product(frame, inverse(product(frame, inverse(mono)))), mono)
        self.assertNotEqual(mono, inverse(mono))
        self.assertEqual(product(pre_tag, inverse(frame)), inverse(mono))
        wrapper_tag = product(mono, frame)
        self.assertEqual(product(frame, inverse(wrapper_tag)), inverse(mono))
        self.assertNotEqual(product(frame, inverse(product(frame, mono))), inverse(mono))
        self.assertEqual(product(frame, inverse(frame)), identity)
        core = ((2, 0), (0, Fraction(1, 2)))
        self.assertNotEqual(product(frame, product(core, mono)),
                            product(mono, product(core, frame)))

    def test_changed_source_bytes_fail_before_record_execution(self):
        manifest = json.loads((HERE / "SOURCES.json").read_text())
        row = next(r for r in manifest["files"] if r["usage"] == "input")
        target = (source.ROOT / row["path"]).resolve()
        original = Path.read_bytes

        def changed(path):
            value = original(path)
            return value + b"\n" if path.resolve() == target else value

        with patch.object(Path, "read_bytes", changed):
            with self.assertRaisesRegex(ValueError, "Input changed"):
                source.authenticate()


if __name__ == "__main__":
    unittest.main()
