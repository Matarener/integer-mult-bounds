"""Semantic controls for the new binding, independent of source-hash failures.

SPDX-License-Identifier: Apache-2.0
Prepared for yssite with substantial OpenAI Codex assistance.
"""
import json
from pathlib import Path
import shutil
import tempfile
import unittest

from binding import account, sha, validate_rebind
from native_outputs import authenticate_native
from replay import PREDECESSOR


def fixture():
    """Four real provider kinds, reduced to the shared 7/8-width boundary."""
    pids = ["extra-four", "extra", "gauge44", "gauge44-four"]
    registry = {
        p: {"widths": [7 if p.endswith("-four") else 8],
            "actual_paid_profile": {"1": 2 if p.endswith("-four") else 1},
            "orientation_program_sha256": {o: p + ":" + o for o in ("forward", "backward")}}
        for p in pids
    }
    plan = dict(order=[[s, 0] for s in range(4)], provider_registry=registry,
                pairs={"0": 0}, sides={"0": 0},
                windows={"0,0": [16, [0, 1]], "1,0": [16, [2, 3]]},
                provider_calls=[], per_call_widths=[])
    roles, dispatch = [], []
    for t, pid in enumerate(pids):
        ori = "forward" if t % 2 == 0 else "backward"
        plan["provider_calls"].append(dict(stage=t, replica=0, time=t, provider=pid,
                                           orientation=ori, local_program_sha256=pid + ":" + ori))
        plan["per_call_widths"].append(dict(stage=t, replica=0, time=t,
                                           widths=registry[pid]["widths"][:]))
        roles.append(dict(time=t, helper=0, stage=t, replica=0, owner_replica=t // 2,
                          child=0, port=107, family=896 * (t // 2) + 107,
                          copy=112 * (t // 2) + 107, offset=[0, 7, 0, 8][t],
                          width=registry[pid]["widths"][0]))
        dispatch.append([t, 0, pid])
    return plan, roles, dispatch


class CallBindingTests(unittest.TestCase):
    def test_positive_complements_and_row_order(self):
        p, r, d = fixture()
        idle, total = account(p, r, d)
        self.assertEqual(idle, {1: 2, 16: 222})
        self.assertEqual(total, {1: 8, 16: 222})
        self.assertEqual(account(p, r, list(reversed(d))), (idle, total))

    def test_wrong_dispatch_with_coherent_call_metadata(self):
        p, r, d = fixture()
        # Keep counts, programs, per-call widths and row widths coherent, but
        # exchange which call uses FOUR. The old second offset is now illegal.
        d[0][2], d[1][2] = d[1][2], d[0][2]
        for t in (0, 1):
            pid = d[t][2]
            c = p["provider_calls"][t]
            c["provider"] = pid
            c["local_program_sha256"] = pid + ":" + c["orientation"]
            p["per_call_widths"][t]["widths"] = p["provider_registry"][pid]["widths"][:]
            r[t]["width"] = p["provider_registry"][pid]["widths"][0]
        with self.assertRaisesRegex(ValueError, "compact per-call residual prefix"):
            account(p, r, d)

    def test_omitted_provider(self):
        p, r, d = fixture()
        del p["provider_registry"]["gauge44-four"]
        with self.assertRaisesRegex(ValueError, "complete provider usage"):
            account(p, r, d)

    def test_program_binding_even_when_widths_agree(self):
        p, r, d = fixture()
        p["provider_calls"][2]["local_program_sha256"] = "extra:forward"
        with self.assertRaisesRegex(ValueError, "per-call program binding"):
            account(p, r, d)

    def test_averaged_width_or_wrong_orientation(self):
        for field, value, reason in (
            ("width", 8, "actual selected helper width"),
            ("orientation", "backward", "per-call orientation"),
        ):
            p, r, d = fixture()
            if field == "width":
                r[0][field] = value
            else:
                p["provider_calls"][0][field] = value
            with self.assertRaisesRegex(ValueError, reason):
                account(p, r, d)

    def test_capacity_window_hole_and_duplicate(self):
        mutations = [
            (lambda p, r, d: r[0].__setitem__("offset", 1), "compact per-call residual prefix"),
            (lambda p, r, d: p["windows"]["0,0"].__setitem__(0, 14), "compact per-call residual prefix"),
            (lambda p, r, d: p["windows"]["0,0"].__setitem__(1, [1]), "strict inherited window"),
            (lambda p, r, d: d.__setitem__(1, d[0][:]), "dispatch bijection"),
        ]
        for mutate, reason in mutations:
            with self.subTest(reason=reason):
                p, r, d = fixture()
                mutate(p, r, d)
                with self.assertRaisesRegex(ValueError, reason):
                    account(p, r, d)


class RebindContractTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.pkg = Path(self.temp.name)
        (self.pkg / "new").mkdir()
        self.plan, roles, dispatch = fixture()
        idle, total = account(self.plan, roles, dispatch)
        self.plan["profile"] = {str(r): n for r, n in total.items()}
        self.contract = {"providers": {}, "dispatch": list(reversed(dispatch))}
        self.locs = {}

        def put(path, value):
            path.write_text(json.dumps(value))
        self.put = put
        # This reduced fixture tests the binder contract, not native semantics;
        # NativeProductTests uses the real source-bound native products.
        for pid, desc in self.plan["provider_registry"].items():
            word = self.pkg / (pid + ".json")
            value = {"provider": pid}
            put(word, value)
            local = self.pkg / pid
            local.mkdir()
            put(local / "FULL-WORD.json", value)
            import gzip
            (local / "FULL-WORD.json.gz").write_bytes(gzip.compress(json.dumps(value).encode()))
            width = desc["widths"][0]
            canonical = {"R": 1, "frames": [[], [1 << i for i in range(width)]],
                         "start": [0] * 225, "final": [0] * 224 + [1]}
            (local / "CANONICAL-WORD.json.gz").write_bytes(gzip.compress(json.dumps(canonical).encode()))
            put(local / "LOCAL-CHECKS.json",
                {o: {"paid_profile": desc["actual_paid_profile"]} for o in ("forward", "backward")})
            self.contract["providers"][pid] = dict(word=word.name, word_sha256=sha(word),
                                                    widths=desc["widths"], profile=desc["actual_paid_profile"])
            self.locs[pid] = local
        put(self.pkg / "new/MIXED-CONTRACT.json", self.contract)
        put(self.pkg / "DISPATCH.json", dispatch)
        import gzip
        (self.pkg / "OWNERS.json.gz").write_bytes(gzip.compress(json.dumps(roles).encode()))
        put(self.pkg / "CONSTRUCTION.json", {"idle": idle})

    def test_positive_rebind_with_different_table_order(self):
        self.assertEqual(validate_rebind(self.pkg, self.plan, self.locs), {1: 2, 16: 222})

    def test_stale_idle(self):
        self.put(self.pkg / "CONSTRUCTION.json", {"idle": {1: 1, 16: 222}})
        with self.assertRaisesRegex(ValueError, "stale construction idle"):
            validate_rebind(self.pkg, self.plan, self.locs)

    def test_source_change(self):
        (self.pkg / "gauge44-four.json").write_text('{"provider":"different"}')
        with self.assertRaisesRegex(ValueError, "provider source changed"):
            validate_rebind(self.pkg, self.plan, self.locs)

    def test_missing_provider_and_changed_selector(self):
        locs = dict(self.locs)
        del locs["gauge44-four"]
        with self.assertRaisesRegex(ValueError, "complete four-provider binding"):
            validate_rebind(self.pkg, self.plan, locs)
        dispatch = json.loads((self.pkg / "DISPATCH.json").read_text())
        dispatch[0][2], dispatch[1][2] = dispatch[1][2], dispatch[0][2]
        self.put(self.pkg / "DISPATCH.json", dispatch)
        with self.assertRaisesRegex(ValueError, "literal mixed selector"):
            validate_rebind(self.pkg, self.plan, self.locs)


class NativeProductTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = PREDECESSOR / "native-base/native"
        cls.word_sha = json.loads((PREDECESSOR / "native-base/RESULT.json").read_text())["word_sha256"]

    def test_real_retained_positive_control(self):
        self.assertEqual(len(authenticate_native("gauge44", self.word_sha, self.source)), 11)

    def test_phase_change_with_rebound_receipts(self):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "native"
            shutil.copytree(self.source, out)
            path = out / "local/CLIFFORD-RECIPES.json"
            recipe = json.loads(path.read_text())
            recipe["warps"][0]["left"]["phase"] = (recipe["warps"][0]["left"]["phase"] + 1) % 4
            path.write_text(json.dumps(recipe))
            # Rebind both receipt references, so rejection cannot be attributed
            # to a stale raw hash or the intentionally unchanged success flags.
            for name in ("CLIFFORD-REVIEW.json", "WARP-RECIPE-CHECKS.json"):
                receipt = out / "local" / name
                value = json.loads(receipt.read_text())
                value["recipe_sha256"] = sha(path)
                receipt.write_text(json.dumps(value))
            with self.assertRaisesRegex(ValueError, "native scientific output commitment"):
                authenticate_native("gauge44", self.word_sha, out)

    def test_missing_phase_stage(self):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "native"
            shutil.copytree(self.source, out)
            path = out / "STEPS.json"
            path.write_text(json.dumps(json.loads(path.read_text())[:-1]))
            with self.assertRaisesRegex(ValueError, "actual native stage products coverage"):
                authenticate_native("gauge44", self.word_sha, out)

    def test_uncovered_endpoint_claim(self):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "native"
            shutil.copytree(self.source, out)
            path = out / "local/INDEPENDENT-LOCAL-REPLAY.json"
            value = json.loads(path.read_text())
            value["local"]["backward"]["private_work_erased"] = False
            path.write_text(json.dumps(value))
            with self.assertRaisesRegex(ValueError, "native scientific output commitment"):
                authenticate_native("gauge44", self.word_sha, out)


if __name__ == "__main__":
    unittest.main(verbosity=2)
