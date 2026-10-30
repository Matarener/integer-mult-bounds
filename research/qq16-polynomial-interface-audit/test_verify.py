"""Independent rational primitive and source-bound controls. Apache-2.0.

OpenAI Codex assistance. No predecessor executable or envelope is imported.
"""

import contextlib
import copy
from fractions import Fraction as Q
import io
import itertools
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
import verify  # noqa: E402 - explicit local package under isolated Python.


def complex_add(a, b):
    return a[0] + b[0], a[1] + b[1]


def quarter_turn(a, sign):
    return -sign * a[1], sign * a[0]


def literal_pair(a, b, sign):
    """The pair-first formula on actual rational components, not envelopes."""
    s = complex_add(a, b)
    d = a[0] - b[0], a[1] - b[1]
    u = complex_add(s, quarter_turn(d, sign))
    v = complex_add(s, quarter_turn(d, -sign))
    return (s, d), (u, v), tuple((x / 2, y / 2) for x, y in (u, v))


def evaluate(value, depth):
    polynomial, lines = value
    t = depth - 1
    z = 1 << t
    bound = sum(c * z ** j for j, c in enumerate(polynomial))
    grid = max((s * t + g for s, g in lines), default=0)
    return bound, grid


def fits(value, width, quantum):
    integer = value / quantum
    return integer.denominator == 1 and -(1 << (width - 1)) <= integer < 1 << (width - 1)


class PrimitiveControls(unittest.TestCase):
    def test_native_delta_has_the_exact_quarter_turn_sign(self):
        for sign in (-1, 1):
            _, _, output = literal_pair((Q(1), Q(0)), (Q(0), Q(0)), sign)
            self.assertEqual(output, ((Q(1, 2), Q(sign, 2)),
                                      (Q(1, 2), Q(-sign, 2))))

    def assert_components(self, vectors, value, depth, h):
        bound, grid = evaluate(value, depth)
        quantum = h * Q(2) ** -grid
        for vector in vectors:
            for component in vector:
                self.assertLessEqual(abs(component), h * bound)
                self.assertEqual((component / quantum).denominator, 1)

    def test_literal_gaussian_components_and_tensor_interiors(self):
        cases = 0
        h = Q(1, 4)
        for components in itertools.product((-1, 0, 1), repeat=4):
            base = tuple((Q(components[j]) * h, Q(components[j + 1]) * h)
                         for j in (0, 2))
            for sign in (-1, 1):
                for depth in range(1, 5):
                    vector = [quarter_turn(base[j % 2], -1 if j.bit_count() % 2 else 1)
                              for j in range(1 << depth)]
                    bounds = verify.gaussian(verify.UNIT)
                    for axis in range(depth):
                        stride = 1 << axis
                        for start in range(0, len(vector), 2 * stride):
                            for offset in range(stride):
                                a, b = start + offset, start + offset + stride
                                pair, cross, output = literal_pair(vector[a], vector[b], sign)
                                for actual, bound in zip((pair, cross, output), bounds):
                                    self.assert_components(actual, bound, depth, h)
                                vector[a], vector[b] = output
                        cases += 1
                    self.assert_components(vector, bounds[2], depth, h)
        self.assertEqual(cases, 1620)

    def test_native_cross_numerator_can_overflow_a_fitting_endpoint(self):
        pair, cross, output = literal_pair((Q(1), Q(-1)), (Q(1), Q(1)), 1)
        self.assertEqual(max(abs(x) for z in cross for x in z), 4)
        self.assertEqual(max(abs(x) for z in output for x in z), 2)
        quantum = Q(1, 2)
        self.assertTrue(all(fits(x, 4, quantum) for z in output for x in z))
        self.assertFalse(all(fits(x, 4, quantum) for z in cross for x in z))
        self.assertTrue(all(fits(x, 5, quantum) for z in cross for x in z))
        identity = {"matrix_rows": [1 << j for j in range(9)],
                    "quadratic_rows": [0] * 9, "linear_Z4": [0] * 9,
                    "offset": 0, "phase": 0}
        audit = verify.Audit()
        audit.recipe(verify.UNIT, {"rank": 1, "left": identity, "right": identity})
        self.assertEqual(audit.max_sum, 4)
        self.assertEqual(audit.max_location[1], "tensor-cross-interiors")
        self.assertEqual(audit.cost["native_gaussian_lines"], 1)

    def test_signed_dyadic_products_and_shifted_partials(self):
        for coefficient in (Q(-3, 8), Q(5, 2), Q(-6), Q(8)):
            audit = verify.Audit()
            result = audit.multiply(verify.UNIT, coefficient)
            self.assertEqual(audit.count, 3)
            self.assertGreaterEqual(audit.max_sum, abs(coefficient.numerator))
            bound, grid = evaluate(result, 3)
            for integer in range(-8, 9):
                actual = Q(integer, 8) * coefficient
                self.assertLessEqual(abs(actual), bound)
                self.assertEqual((actual / (Q(1, 8) * Q(2) ** -grid)).denominator, 1)
        audit = verify.Audit()
        self.assertEqual(audit.multiply(verify.UNIT, Q(-6))[1], ((0, -1),))
        self.assertEqual(audit.grid_forms, ((0, 0),))

    def test_affine_grid_domain_and_zero(self):
        forms = ((0, 7), (3, -4), (1, 2), (2, -9), (0, -1))
        result = verify.frontier(forms)
        self.assertIn((0, 7), result)
        self.assertIn((3, -4), result)
        for t in (0, 1, 2, 7, 99):
            self.assertEqual(max(s * t + g for s, g in forms),
                             max(s * t + g for s, g in result))
        self.assertEqual(verify.gaussian(verify.ZERO), (verify.ZERO,) * 3)
        self.assertEqual(verify.scale(verify.UNIT, 0), verify.ZERO)
        self.assertEqual(verify.scale(verify.ZERO, Q(-3, 2)), verify.ZERO)
        with self.assertRaisesRegex(ValueError, "dyadic"):
            verify.scale(verify.UNIT, Q(1, 3))
        with self.assertRaisesRegex(ValueError, "nonnegative"):
            verify.Audit().observe(((Q(-1),), ((0, 0),)), "invalid")
        for token in (["L", True], ["C", 8], ["L", -1]):
            with self.assertRaises(ValueError):
                verify.index(token)

    def test_monomial_and_owner_permutation_guards(self):
        columns = [1 << j for j in range(73)]
        self.assertEqual(verify.inverse_binary(columns), columns)
        columns[1] = columns[0]
        with self.assertRaisesRegex(ValueError, "singular"):
            verify.inverse_binary(columns)
        broken = {"matrix_rows": [0] * 9, "quadratic_rows": [0] * 9,
                  "linear_Z4": [0] * 9, "offset": 0, "phase": 0}
        with self.assertRaisesRegex(ValueError, "permutation"):
            verify.monomial_check(broken)
        with self.assertRaisesRegex(ValueError, "rank"):
            verify.Audit().recipe(verify.UNIT, {"rank": True})
        with self.assertRaisesRegex(ValueError, "duplicate"):
            verify.decode('{"x":1,"x":2}')


class SourceAndClaimControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.packet, cls.recipes, cls.residuals, cls.claimed = verify.load()
        cls.envelope, cls.stages, cls.maps = verify.run(cls.packet, cls.recipes, cls.residuals)
        cls.result = verify.certify(cls.envelope, cls.stages, cls.maps, cls.claimed)

    def test_actual_carried_state_reset_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "F0-to-B1 state carry"):
            verify.run(self.packet, self.recipes, self.residuals, reset_at_b1=True)

    def test_literal_sweep_omission_is_rejected(self):
        program = self.packet["programs"]["F_0"]
        location = next(j for j, event in enumerate(program)
                        if event[0] in ("private_sweep", "cover_sweep"))
        original = program[location]
        replacement = copy.deepcopy(original)
        replacement[2].pop()
        program[location] = replacement
        try:
            with self.assertRaisesRegex(ValueError, "stage length"):
                verify.expand(self.packet, "F_0")
        finally:
            program[location] = original

    def test_claim_type_coefficient_scope_and_tariff_mutants(self):
        mutants = (("grid_slope", True), ("signed_width_slope", 37),
                   ("storage_words_per_N", 1425), ("supplier_admission", True))
        for field, value in mutants:
            with self.subTest(field=field):
                changed = copy.deepcopy(self.claimed)
                changed[field] = value
                with self.assertRaises(ValueError):
                    verify.certify(self.envelope, self.stages, self.maps, changed)
        changed = copy.deepcopy(self.claimed)
        changed["direct_cost_at_one"]["native_real_additions"] -= 512
        with self.assertRaisesRegex(ValueError, "tariff"):
            verify.certify(self.envelope, self.stages, self.maps, changed)
        changed = copy.deepcopy(self.stages)
        changed["B_1_2"]["event_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "event expansion"):
            verify.certify(self.envelope, changed, self.maps, self.claimed)

    def private_inputs(self, root):
        package = root / "research/qq16-polynomial-interface-audit"
        package.mkdir(parents=True)
        shutil.copyfile(verify.HERE / "SOURCES.json", package / "SOURCES.json")
        for path in verify.INPUT_PATHS:
            destination = root / path
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(verify.ROOT / path, destination)
        return package

    def test_private_source_bytes_and_pin_usage_mutants(self):
        with tempfile.TemporaryDirectory(prefix="qq16-polynomial-source-controls-") as work:
            root = Path(work)
            package = self.private_inputs(root)
            certificate = root / verify.CERT
            original = certificate.read_bytes()
            certificate.write_bytes(original + b"changed")
            with mock.patch.object(verify, "HERE", package):
                with self.assertRaisesRegex(ValueError, "source SHA256"):
                    verify.load(root)
            certificate.write_bytes(original)
            manifest_path = package / "SOURCES.json"
            manifest = json.loads(manifest_path.read_text())
            row = next(r for r in manifest["files"] if r["usage"] == "input")
            row["usage"] = "provenance"
            manifest_path.write_text(json.dumps(manifest))
            with mock.patch.object(verify, "HERE", package):
                with self.assertRaisesRegex(ValueError, "input inventory"):
                    verify.load(root)

    def test_receipt_type_mutation_and_exclusive_write(self):
        with tempfile.TemporaryDirectory(prefix="qq16-polynomial-receipt-controls-") as work:
            package = Path(work)
            receipt = copy.deepcopy(self.result)
            receipt["maximum_polynomial_degree"] = True
            (package / "RESULT.json").write_text(json.dumps(receipt))
            with mock.patch.object(verify, "audit", return_value=self.result):
                with mock.patch.object(verify, "HERE", package), mock.patch.object(sys, "argv", ["verify.py"]):
                    with self.assertRaisesRegex(ValueError, "receipt mismatch"):
                        verify.main()
                output = package / "new.json"
                with mock.patch.object(sys, "argv", ["verify.py", "--write", str(output)]):
                    with contextlib.redirect_stdout(io.StringIO()):
                        verify.main()
                    self.assertEqual(json.loads(output.read_text())["status"], self.result["status"])
                    with self.assertRaises(FileExistsError):
                        verify.main()


if __name__ == "__main__":
    unittest.main(verbosity=2)
