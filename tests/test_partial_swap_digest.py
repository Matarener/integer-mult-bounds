#!/usr/bin/env python3
"""Focused controls for the partial-swap verify digest tooling package."""
from __future__ import annotations

from hashlib import sha256
import importlib.util
import json
import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "research" / "partial-swap-digest"
sys.path.insert(0, str(ROOT / "scripts"))

from partial_swap import shared as production  # noqa: E402
from partial_swap.graph import graph  # noqa: E402

ORIGINAL_SHA256 = "81e9af92cdf38243a540cdcff2062778e449467848d444da37a9553c12ca4c34"
OPTIMIZED_SHA256 = "5a0646a50b9f3e8ea55168620a78e8853b0ab810517cefc8cfb8696aedee278a"


def load_baseline():
    spec = importlib.util.spec_from_file_location("baseline_pspc_test", PACKAGE / "baseline.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class PartialSwapDigestTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.baseline = load_baseline()

    def test_baseline_matches_base_commit_bytes(self):
        import subprocess

        original = subprocess.check_output(
            ["git", "show", "0b1cccf86e2f5132ed286a26ef0a681a495740ea:scripts/partial_swap/shared.py"],
            cwd=ROOT,
        )
        self.assertEqual((PACKAGE / "baseline.py").read_bytes(), original)
        self.assertEqual(sha256(original).hexdigest(), ORIGINAL_SHA256)

    def test_encoding_matches_json_dumps(self):
        samples = [
            (1, None, None),
            (5, (1, 2), (0, 3)),
            (9, None, None),
            (100, (8, 7), (2, 4)),
        ]
        for node, edge, prov in samples:
            old = json.dumps((node, edge, prov), separators=(",", ":")) + "\n"
            if edge is None:
                new = f"[{node},null,null]\n"
            else:
                a, b = edge
                common, local = prov
                new = f"[{node},[{a},{b}],[{common},{local}]]\n"
            self.assertEqual(old, new)
        out_old = json.dumps((0, (0, 1, 2), 22), separators=(",", ":")) + "\n"
        self.assertEqual(out_old, "[0,[0,1,2],22]\n")

    def test_none_mutant_differs(self):
        self.assertNotEqual(
            "[0,None,None]\n",
            json.dumps((0, None, None), separators=(",", ":")) + "\n",
        )

    def test_small_circuit_receipts_match(self):
        for h in (6, 8, 10):
            circuit = production.SharedPointCircuit(h)
            self.assertEqual(
                self.baseline.SharedPointCircuit.verify(circuit),
                circuit.verify(),
            )

    def test_retained_total_receipts_match(self):
        # graph() adds an empty-exclusion local output, lifted to (common,).
        for h in (6, 8, 10, 25):
            with self.subTest(h=h):
                circuit = graph(h)
                self.assertEqual(sum(len(t) == 1 for _, t in circuit.outputs), h)
                receipt = circuit.verify()
                self.assertEqual(self.baseline.SharedPointCircuit.verify(circuit), receipt)
                if h == 25:
                    frozen = json.loads((ROOT / "research/copied-fixed-reversed/producer-input-25.json").read_text())
                    self.assertEqual(receipt, frozen["scalar"])

    def test_wrong_retained_total_rejected(self):
        circuit = graph(8)
        key = next(key for key in circuit.outputs if len(key[1]) == 1)
        common = key[0]
        # A proper excluded-pair sum cannot replace the full retained total.
        circuit.outputs[key] = next(node for (c, t), node in circuit.outputs.items()
                                    if c == common and len(t) == 3)
        with self.assertRaises(AssertionError):
            circuit.verify()
        with self.assertRaises(AssertionError):
            self.baseline.SharedPointCircuit.verify(circuit)

    def test_support_rejection_preserved(self):
        circuit = production.SharedPointCircuit(8)
        node = next(n for n in circuit.active if circuit.args[n])
        a, _b = circuit.args[node]
        circuit.core[node] = circuit.core[a]
        with self.assertRaises(AssertionError):
            circuit.verify()
        with self.assertRaises(AssertionError):
            self.baseline.SharedPointCircuit.verify(circuit)

    def test_production_digest_pin(self):
        self.assertEqual(
            sha256((ROOT / "scripts/partial_swap/shared.py").read_bytes()).hexdigest(),
            OPTIMIZED_SHA256,
        )

    def test_certificate_pin_only(self):
        import subprocess
        from copy import deepcopy

        base = json.loads(
            subprocess.check_output(
                [
                    "git",
                    "show",
                    "0b1cccf86e2f5132ed286a26ef0a681a495740ea:certificates/partial-swap-network.json",
                ],
                cwd=ROOT,
            )
        )
        live = json.loads((ROOT / "certificates/partial-swap-network.json").read_text(encoding="utf-8"))
        self.assertEqual(base["source_sha256"]["scripts/partial_swap/shared.py"], ORIGINAL_SHA256)
        self.assertEqual(live["source_sha256"]["scripts/partial_swap/shared.py"], OPTIMIZED_SHA256)
        restored = deepcopy(live)
        restored["source_sha256"]["scripts/partial_swap/shared.py"] = ORIGINAL_SHA256
        self.assertEqual(restored, base)


if __name__ == "__main__":
    unittest.main()
