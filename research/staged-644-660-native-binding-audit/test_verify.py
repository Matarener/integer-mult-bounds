# SPDX-License-Identifier: Apache-2.0
"""Semantic failures at the emitted 644/660 wrapper, climb, exit and recipe boundaries.

Adapted from research/rank7-group-d-native-widths-audit/test_verify.py (Wentao Li).
"""

import copy
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import native
from common import (COMPILER, DONORS, ENTRANCE, FULL, HELPERS, KERNEL, PACKAGE,
                    PARENT_ENTRANCE, ROOT, authenticate, consumer_name, decode, module,
                    recorded_receipts, staged_name)


class BoundaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.blobs = authenticate()
        cls.result = decode((PACKAGE / "RESULT.json").read_bytes())
        cls.row = cls.result["native"]["providers"]["base"]
        cls.kernel = module(cls.blobs[KERNEL], "staged_pair_test_kernel")
        cls.compiler = module(cls.blobs[COMPILER], "staged_pair_test_compiler")
        cls.tmp = tempfile.TemporaryDirectory(prefix="staged-pair-tests-")
        raw = cls.blobs[staged_name("base")]
        cls.word = decode(raw, True)
        cls.canonical, cls.programs, cls.checks = native.generate(
            cls.blobs, raw, Path(cls.tmp.name) / "staged")
        cls.r = cls.row["bindings"]["644"]["forward"]["compact_helper"]
        cls.recipe = cls.row["residuals"]["137"]["recipe"]
        cls.parent_recipe = cls.row["parent_residual"]["recipe"]
        cls.adapters = native.adapter_file(cls.compiler, cls.canonical)
        raw = cls.blobs[consumer_name("RETIMED644-660", "base")]
        cls.retimed = decode(raw, True)
        cls.retimed_canonical, cls.retimed_programs, cls.retimed_checks = native.generate(
            cls.blobs, raw, Path(cls.tmp.name) / "retimed")

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def stream(self):
        return copy.deepcopy(self.programs["forward"])

    def bind(self, stream, word=None, helper=644, backward=False):
        return native.emitted_binding(word or self.word, self.canonical, stream, helper, backward)

    def assertRejects(self, action, message=""):
        with self.assertRaises((ValueError, AssertionError)) as caught:
            action()
        self.assertIn(message, str(caught.exception))

    def index(self, stream, kind, *head):
        return next(i for i, e in enumerate(stream)
                    if e[0] == kind and e[1:1 + len(head)] == list(head))

    def test_positive_and_receipt(self):
        self.assertEqual(self.checks, self.row["local_checks_sha256"])
        for orientation in ("forward", "backward"):
            for h in (644, 660):
                binding = self.bind(self.programs[orientation], helper=h,
                                    backward=orientation == "backward")
                self.assertEqual(binding, self.row["bindings"][str(h)][orientation])
        self.assertEqual(native.check_recipe(self.kernel, self.recipe, ENTRANCE, FULL)["rank"], 7)
        self.assertEqual(native.check_recipe(self.kernel, self.parent_recipe,
                                             PARENT_ENTRANCE, FULL)["rank"], 8)

    def test_wrapper_corruptions(self):
        s = self.stream(); del s[self.index(s, "residual_adapter", "post", self.r)]
        self.assertRejects(lambda: self.bind(s))
        s = self.stream(); i = self.index(s, "residual_adapter", "pre", self.r)
        s[i] = s[i][:3] + [self.canonical["start"][self.r] - 1]
        self.assertRejects(lambda: self.bind(s))
        s = self.stream(); i = self.index(s, "residual_adapter", "pre", self.r)
        s[i] = s[i] + [1]  # A restored-helper terminal field on a FULL helper.
        self.assertRejects(lambda: self.bind(s))

    def test_climb_and_exit_corruptions(self):
        s = self.stream(); del s[self.index(s, "climb", "B", self.r)]
        self.assertRejects(lambda: self.bind(s))
        s = self.stream(); i = self.index(s, "climb", "B", self.r); s[i][5] += 1
        self.assertRejects(lambda: self.bind(s))
        s = self.stream(); i = self.index(s, "adapter", "new_to_old", self.r)
        s[i] = ["adapter", "old_to_new", self.r, s[i][3]]
        self.assertRejects(lambda: self.bind(s))
        s = self.stream(); i = self.index(s, "adapter", "new_to_old", self.r)
        event = s.pop(i)
        s.insert(self.index(s, "zero_buffer", "free", self.canonical["zero_buffers"][-1]), event)
        self.assertRejects(lambda: self.bind(s))
        s = self.stream(); s.insert(self.index(s, "phase", "full_frame_cleanup") + 1,
                                    ["zero_buffer", "alloc", self.r])
        self.assertRejects(lambda: self.bind(s))

    def test_scalar_and_orientation_corruptions(self):
        s = self.stream()
        i = next(i for i, e in enumerate(s) if e[0] == "scalar" and e[1][0] == "add" and
                 ["L", self.r] in e[1][1:3])
        s[i][1][3] = -s[i][1][3]
        self.assertRejects(lambda: self.bind(s))
        self.assertRejects(lambda: self.bind(self.programs["forward"], backward=True))
        word = copy.deepcopy(self.word); word["start_extra"]["644"] = list(PARENT_ENTRANCE)
        self.assertRejects(lambda: self.bind(self.programs["forward"], word=word))
        word = copy.deepcopy(self.word); word["helper_final"]["644"] = list(FULL)
        self.assertRejects(lambda: self.bind(self.programs["forward"], word=word))

    def test_recipe_corruptions(self):
        check = lambda rec, e=ENTRANCE: native.check_recipe(self.kernel, rec, e, FULL)
        bad = copy.deepcopy(self.recipe); bad["left"], bad["right"] = bad["right"], bad["left"]
        self.assertRejects(lambda: check(bad))
        bad = copy.deepcopy(self.recipe); bad["right"] = None
        self.assertRejects(lambda: check(bad))
        bad = copy.deepcopy(self.recipe); bad["left"]["offset"] ^= 1
        self.assertRejects(lambda: check(bad))
        bad = copy.deepcopy(self.recipe); bad["rank"] = 8
        self.assertRejects(lambda: check(bad))
        # A different plane through the parent line 30 (430 is not in span(429,30)).
        self.assertRejects(lambda: check(self.recipe, [430, 30]))

    def compare(self, adapters=None, canonical=None, forward=None):
        bindings = {str(h): {"forward": self.bind(self.programs["forward"], helper=h)}
                    for h in HELPERS}
        staged = (self.word, self.canonical, self.programs, adapters or self.adapters, bindings)
        programs = dict(self.retimed_programs, forward=forward or self.retimed_programs["forward"])
        return native.compare(staged, self.retimed, canonical or self.retimed_canonical,
                              programs, self.compiler, self.kernel, {})

    def test_consumer_positive_and_receipt(self):
        row = self.result["native"]["consumers"]["RETIMED644-660"]["base"]
        self.assertEqual(self.retimed_checks, recorded_receipts()["RETIMED644-660"]["base"])
        self.assertEqual(self.retimed_checks, row["local_checks_sha256"])
        self.assertEqual(self.compare(), {k: v for k, v in row.items()
                                          if k not in ("word_sha256", "local_checks_sha256")})
        for h in HELPERS:  # The retimed word does not describe the STAGED program either.
            self.assertRejects(lambda: native.emitted_binding(
                self.retimed, self.canonical, self.programs["forward"], h),
                "source-to-emission direct scalar/climb clocks")

    def test_consumer_corruptions(self):
        adapters = copy.deepcopy(self.adapters)
        adapters["recipes"]["137"]["left"]["phase"] ^= 1
        self.assertRejects(lambda: self.compare(adapters=adapters),
                           "unchanged serialized residual adapters")
        # Moving the span(429,30) entrance from 644 to its donor 640 keeps the recipe set.
        canonical = copy.deepcopy(self.retimed_canonical)
        kept = [r for r in range(704) if r not in self.retimed["removed"]]
        a, b = kept.index(644), kept.index(DONORS[0])
        canonical["start"][a], canonical["start"][b] = canonical["start"][b], canonical["start"][a]
        self.assertRejects(lambda: self.compare(canonical=canonical),
                           "unchanged entrance/terminal pairs")
        # An extra changed climb chain outside the donors.
        s = copy.deepcopy(self.retimed_programs["forward"])
        del s[next(i for i, e in enumerate(s) if e[0] == "climb" and
                   kept[e[2]] not in (*HELPERS, *DONORS))]
        self.assertRejects(lambda: self.compare(forward=s), "only the donors' climb chains change")
        # The donor stops at its old intermediate frame span(429,30) instead of one merged climb.
        s = copy.deepcopy(self.retimed_programs["forward"])
        i = next(i for i, e in enumerate(s) if e[0] == "climb" and kept[e[2]] == DONORS[0])
        s[i][4:6] = [self.retimed_canonical["frames"].index(ENTRANCE), 1]
        self.assertRejects(lambda: self.compare(forward=s), "one merged donor climb")

    def test_source_pin_corruption(self):
        with tempfile.TemporaryDirectory(prefix="staged-pair-pins-") as work:
            root = Path(work)
            for name in self.blobs:
                (root / name).parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / name, root / name)
            self.assertEqual(authenticate(root), self.blobs)
            for target in (root / staged_name("extra"), root / consumer_name("DELAYED", "base")):
                good = target.read_bytes()
                raw = bytearray(good); raw[-5] ^= 1; target.write_bytes(bytes(raw))
                self.assertRejects(lambda: authenticate(root))
                target.write_bytes(good)


if __name__ == "__main__":
    unittest.main()
