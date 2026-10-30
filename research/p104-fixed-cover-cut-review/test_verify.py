#!/usr/bin/env python3
"""Negative controls: each deliberate defect must make verify.py fail."""

import unittest
from pathlib import Path
from unittest import mock

import runpy

V = runpy.run_path(str(Path(__file__).resolve().parent / "verify.py"))


_CACHE = []


def result():
    if not _CACHE:
        _CACHE.append(V["p104"]())
    return _CACHE[0]


def fails(why, fn, *args):
    """True when fn stops with the FAIL message that names `why`."""
    try:
        fn(*args)
    except SystemExit as exc:
        return str(exc).startswith("FAIL: " + why)
    return False


class Controls(unittest.TestCase):
    def test_tampered_input_hash(self):
        bad = {k: "0" * 64 for k in V["INPUTS"]}
        with mock.patch.dict(V["load"].__globals__["INPUTS"], bad):
            self.assertTrue(fails("input hash", V["load"]))

    def test_oracle_rejects_an_unsound_test(self):
        # A test that grants only shared snapshots misses helper paths.
        g = V["oracle"].__globals__
        with mock.patch.dict(g, {"small_sharp": lambda inst: {
                (t, s) for s, xc in enumerate(inst[1])
                for t, yc in enumerate(inst[2]) if set(xc) & set(yc)}}):
            self.assertTrue(fails("oracle: exhaustive untimed support differs",
                                  V["oracle"], 7, ((3, 400),), 120))

    def test_oracle_rejects_a_too_tight_exhaustive_search(self):
        # An exhaustive search that never switches helper type misses the
        # legal two-type relay of the unpooled F_2^4 example.
        g = V["unpooled_relay_example"].__globals__
        with mock.patch.dict(g, {"small_exact": lambda inst: (
                V["small_sharp"](inst), {})}):
            self.assertTrue(fails("pooling is needed",
                                  V["unpooled_relay_example"]))

    def test_dropping_shared_type_breaks_pr3427_masks(self):
        # Pairing a source snapshot and a target snapshot that are each
        # admitted by some helper type, not necessarily the same one.
        g = V["sharp_by_frames"].__globals__
        r = result()
        loose = [0] * 104
        geo, paths = r["geo"], r["paths"]
        masks = V["endpoint_masks"](geo)
        frames = {f for k in "XY" for i in range(104)
                  for f in paths[k + str(i)]}
        adm = {f: V["admit_mask"](geo, masks, f) for f in frames}
        for t in range(104):
            for s in range(104):
                if any(adm[v] and adm[w] for v in paths["X%d" % s]
                       for w in paths["Y%d" % t]):
                    loose[t] |= 1 << s
        got = [sum(1 << t for t in range(104) if loose[t] >> s & 1)
               for s in range(4)]
        self.assertNotEqual(tuple(got), g["PR3427_SOURCE_MASKS"])

    def test_dropping_containment_loses_exactness_in_principle(self):
        # Containment V <= W is not decisive at P104 (verify.py checks this),
        # but without it the test over-grants: it stays sound, not exact.
        # F_2^4, one pooled type with line <e1> and hyperplane <e1,e2,e3>:
        # X0 passes the admitted plane <e1,e2>, Y0 the admitted plane
        # <e1,e3>, and no path joins them.
        key = V["key"]
        full = key([1, 2, 4, 8])
        ty = {0: (), 1: key([1]), 3: key([1, 2, 4]), 4: full}
        inst = (4, [[key([2]), key([1, 2]), full]],
                [[(), key([1, 4]), key([1, 4, 8])]], [ty])
        v, w = key([1, 2]), key([1, 4])
        self.assertTrue(V["small_admit"](ty, v) and V["small_admit"](ty, w))
        self.assertNotIn((0, 0), V["small_exact"](inst)[0])
        self.assertNotIn((0, 0), V["small_sharp"](inst))
        # The containment-free variant grants the unreachable pair (0,0).
        self.assertFalse(V["le"](v, w))
        self.assertIn((0, 0), V["small_sharp"](inst, nested=False))

    def test_wrong_rank_block_is_rejected(self):
        # The block is a maximum independent set, so any added port meets a
        # supported pair; a shrunk block fails the size-23 check.
        g = V["rank_consequence"].__globals__
        r = result()
        for bad, why in ((g["MIS_BLOCK"] + (45,), "principal block"),
                         (g["MIS_BLOCK"][1:], "maximum independent set")):
            with mock.patch.dict(g, {"MIS_BLOCK": bad}):
                self.assertTrue(fails(why, V["rank_consequence"], r))

    def test_y_relay_counterexample_is_a_real_escape(self):
        self.assertEqual(V["y_relay_counterexample"](), (1, True))


if __name__ == "__main__":
    unittest.main()
