#!/usr/bin/env python3
"""Tiny independent soundness and rejection controls for the LRAT checker.

The oracle below evaluates every Boolean assignment directly. It does not
implement unit propagation or use a solver. Exhaustive coverage is bounded to
138 formulas over one or two variables and 1,581 proposed empty-clause proofs,
plus 1,034 model-falsified intermediate-clause attacks. The separate
implication-chain fixture uses four variables. These controls do
not certify a general proof kernel or the source CNF's intended encoding.
"""

from __future__ import annotations

from dataclasses import asdict, replace
import gzip
import hashlib
import itertools
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

# Isolated Python (-I) deliberately omits the script directory from sys.path.
# Resolve this one sibling explicitly; there are no non-standard dependencies.
sys.path.insert(0, str(Path(__file__).resolve().parent))
import checker


UNIT_CNF = "p cnf 1 2\n1 0\n-1 0\n"
UNIT_PROOF = "3 0 1 2 0\n"
SPLIT_CNF = "p cnf 2 4\n1 2 0\n-1 2 0\n1 -2 0\n-1 -2 0\n"
SPLIT_PROOF = "5 2 0 1 2 0\n6 0 5 3 4 0\n"


def models(variables: int, clauses: tuple[tuple[int, ...], ...]):
    """Return all models, including the single assignment on zero variables."""
    return [
        values
        for values in itertools.product((False, True), repeat=variables)
        if all(
            any(values[abs(literal) - 1] == (literal > 0) for literal in clause)
            for clause in clauses
        )
    ]


def dimacs(variables: int, clauses: tuple[tuple[int, ...], ...]) -> str:
    return f"p cnf {variables} {len(clauses)}\n" + "".join(
        " ".join(map(str, clause)) + (" " if clause else "") + "0\n"
        for clause in clauses
    )


class CheckerControls(unittest.TestCase):
    def run_check(self, cnf: str | bytes, proof: str | bytes, *, compressed=False,
                  **options):
        cnf_bytes = cnf.encode("ascii") if isinstance(cnf, str) else cnf
        proof_bytes = proof.encode("ascii") if isinstance(proof, str) else proof
        with tempfile.TemporaryDirectory(prefix="gl3-lrat-control-") as directory:
            cnf_path = Path(directory) / "tiny.cnf"
            proof_path = Path(directory) / ("tiny.lrat.gz" if compressed else "tiny.lrat")
            cnf_path.write_bytes(cnf_bytes)
            proof_path.write_bytes(gzip.compress(proof_bytes, mtime=0) if compressed else proof_bytes)
            return checker.check(cnf_path, proof_path, **options)

    def rejects(self, cnf, proof, *, code=None, **options):
        with self.assertRaises(checker.CheckError) as captured:
            self.run_check(cnf, proof, **options)
        if code is not None:
            self.assertEqual(captured.exception.code, code)
        return captured.exception

    def test_boolean_oracle_known_models(self):
        self.assertEqual(models(0, ()), [()])
        self.assertEqual(models(0, ((),)), [])
        self.assertEqual(models(1, ((1,),)), [(True,)])
        self.assertEqual(models(1, ((1,), (-1,))), [])
        self.assertEqual(len(models(2, ((1, -1),))), 4)
        self.assertEqual(models(2, ((1, 2), (-1, 2), (1, -2))), [(True, True)])

    def test_positive_and_negative_unit_conflicts(self):
        for proof in ("3 0 1 2 0\n", "3 0 2 1 0\n"):
            with self.subTest(proof=proof):
                receipt = self.run_check(UNIT_CNF, proof)
                self.assertEqual(receipt.status, "verified_unsat")
                self.assertEqual(receipt.additions, 1)
                self.assertEqual(receipt.hints, 2)
                self.assertEqual(receipt.final_empty_clause, 3)
                self.assertTrue(receipt.final_empty)
                self.assertTrue(receipt.final_empty_live)

    def test_nontrivial_added_clause_uses_negated_assumptions(self):
        clauses = ((1, 2), (-1, 2), (1, -2), (-1, -2))
        self.assertEqual(models(2, clauses), [])
        receipt = self.run_check(SPLIT_CNF, SPLIT_PROOF)
        self.assertEqual(receipt.additions, 2)
        self.assertEqual(receipt.hints, 5)
        # Symmetry exercises a negative assumed literal as the derived clause.
        reflected_cnf = dimacs(2, tuple(tuple(-literal for literal in c) for c in clauses))
        reflected_proof = "5 -2 0 1 2 0\n6 0 5 3 4 0\n"
        self.assertEqual(self.run_check(reflected_cnf, reflected_proof).additions, 2)

    def test_four_variable_implication_chain(self):
        clauses = ((-1, 2), (-2, 3), (-3, 4), (1,), (-4,))
        self.assertEqual(models(4, clauses), [])
        receipt = self.run_check(dimacs(4, clauses), "6 0 4 1 2 3 5 0\n")
        self.assertEqual(receipt.variables, 4)
        self.assertEqual(receipt.hints, 5)
        self.rejects(dimacs(4, clauses), "6 0 4 2 1 3 5 0\n", code="nonunit_hint")

    def test_initial_empty_still_requires_derived_empty(self):
        cnf = "p cnf 0 1\n0\n"
        self.assertEqual(self.run_check(cnf, "2 0 1 0\n").final_empty_clause, 2)
        self.rejects(cnf, "", code="no_empty_clause")
        self.rejects("p cnf 0 0\n", "1 0 0\n", code="missing_conflict")

    def test_duplicate_literals_have_clause_semantics(self):
        receipt = self.run_check("p cnf 1 2\n1 1 0\n-1 -1 0\n", UNIT_PROOF)
        self.assertEqual(receipt.clauses, 2)
        duplicated = "5 2 2 0 1 2 0\n6 0 5 3 4 0\n"
        self.assertEqual(self.run_check(SPLIT_CNF, duplicated).additions, 2)

    def test_initial_tautology_allowed_but_not_a_false_conflict(self):
        cnf = "p cnf 1 3\n1 -1 0\n1 0\n-1 0\n"
        self.assertEqual(self.run_check(cnf, "4 0 2 3 0\n").clauses, 3)
        self.rejects("p cnf 1 1\n1 -1 0\n", "2 0 1 0\n", code="nonunit_hint")
        self.rejects(UNIT_CNF, "3 1 -1 0 1 2 0\n4 0 1 2 0\n", code="tautology")

    def test_hint_order_unit_conflict_and_satisfaction_controls(self):
        bad_proofs = {
            "missing_conflict": "3 0 1 0\n",
            "satisfied_hint": "3 0 1 1 2 0\n",
            "excess_hints": "3 0 1 2 1 0\n",
            "missing_hint": "3 0 1 3 0\n",
        }
        for code, proof in bad_proofs.items():
            with self.subTest(code=code):
                self.rejects(UNIT_CNF, proof, code=code)
        self.rejects(SPLIT_CNF, "5 0 1 2 0\n", code="nonunit_hint")
        # The same false empty clause must not become valid by merely omitting hints.
        self.rejects("p cnf 1 1\n1 0\n", "2 0 0\n", code="missing_conflict")

    def test_id_and_live_database_controls(self):
        cases = (
            ("3 0 1 4 0\n", "missing_hint"),
            ("2 0 1 2 0\n", "addition_id"),
            ("0 0 1 2 0\n", "addition_id"),
            ("2 d 1 0\n3 0 1 2 0\n", "missing_hint"),
            ("2 d 1 0\n2 d 1 0\n", "deletion_target"),
            ("2 d 3 0\n", "deletion_target"),
            ("2 d 1 1 0\n", "deletion_target"),
            ("2 d 0 0\n", "deletion_target"),
            ("3 d 1 0\n", "deletion_label"),
            ("2 d 1 0\n1 0 2 0\n", "addition_id"),
        )
        for proof, code in cases:
            with self.subTest(proof=proof):
                self.rejects(UNIT_CNF, proof, code=code)
        self.rejects(SPLIT_CNF, "5 2 0 1 2 0\n5 0 5 3 4 0\n", code="addition_id")
        self.rejects(SPLIT_CNF, "6 2 0 1 2 0\n5 0 6 3 4 0\n", code="addition_id")

    def test_valid_deletions_and_metadata_do_not_create_clauses(self):
        cnf = "p cnf 2 4\n1 0\n-1 0\n2 0\n-2 0\n"
        receipt = self.run_check(cnf, "4 d 1 2 0\n5 0 3 4 0\n")
        self.assertEqual((receipt.deletions, receipt.deletion_records, receipt.live_clauses), (2, 1, 3))
        receipt = self.run_check(UNIT_CNF, "0 d 0\n" + UNIT_PROOF + "3 d 3 0\n")
        self.assertEqual(receipt.deletion_records, 2)
        self.assertEqual(receipt.deletions, 1)
        self.assertFalse(receipt.final_empty_live)
        self.assertEqual(receipt.final_empty_clause, 3)

    def test_last_addition_must_be_empty(self):
        self.rejects(SPLIT_CNF, "5 2 0 1 2 0\n", code="no_empty_clause")
        self.rejects(UNIT_CNF, UNIT_PROOF + "4 1 0 1 0\n", code="after_empty")
        self.assertTrue(self.run_check(UNIT_CNF, UNIT_PROOF + "c trailing comment\n\n").final_empty)

    def test_dimacs_comments_split_clauses_and_final_line(self):
        cnf = "c preamble\np cnf 1 2\n1\nc between clause literals\n0 -1 0"
        receipt = self.run_check(cnf, "c proof preamble\n\t3\t0\t1 2 0")
        self.assertEqual(receipt.variables, 1)
        self.assertEqual(receipt.clauses, 2)

    def test_malformed_dimacs_is_rejected(self):
        invalid = (
            "", "1 0\n", "p sat 1 2\n1 0 -1 0\n",
            "p cnf 1 2 extra\n1 0 -1 0\n", "p cnf 1 2\np cnf 1 2\n1 0 -1 0\n",
            "p cnf 1 3\n1 0 -1 0\n", "p cnf 1 1\n1 0 -1 0\n",
            "p cnf 1 2\n1 0 -1\n", "p cnf 1 2\n1 0 -1 0 0\n",
            "p cnf 1 2\n2 0 -1 0\n", "p cnf -1 2\n1 0 -1 0\n",
            "p cnf 1 -2\n1 0 -1 0\n", "p cnf 01 2\n1 0 -1 0\n",
            "p cnf 1 2\n+1 0 -1 0\n", "p cnf 1 2\n1 0 -0 -1 0\n",
            "p cnf 1 2\n1 0 word -1 0\n", "p cnf 1 2\n1 0 -1 0 c inline\n",
        )
        for cnf in invalid:
            with self.subTest(cnf=cnf):
                self.rejects(cnf, UNIT_PROOF)
        self.rejects(b"p cnf 1 2\n1 0\n-1 0\n\xff\n", UNIT_PROOF, code="ascii")

    def test_malformed_lrat_and_rat_are_rejected(self):
        invalid = (
            "3 0 1 2\n", "3 0 1 2 0 0\n", "3 1 2 0\n", "3 0\n",
            "3 0 1 0 2 0\n", "3 0 -1 2 0\n", "3 0 +1 2 0\n",
            "3 0 01 2 0\n", "03 0 1 2 0\n", "-3 0 1 2 0\n",
            "3 0 1 x 0\n", "3 2 0 1 2 0\n", "3 0 1 2 0 c inline\n",
            "2 d 1\n", "2 d 1 0 0\n", "2 d -1 0\n",
        )
        for proof in invalid:
            with self.subTest(proof=proof):
                self.rejects(UNIT_CNF, proof)
        self.rejects(UNIT_CNF, b"3 0 1 2 0\n\x00", code="ascii")

    def test_integer_bounds_are_checked_before_large_integer_conversion(self):
        oversized = str(1 << 63)
        for proof in (
            f"{oversized} 0 1 2 0\n", f"3 0 1 {oversized} 0\n",
            f"2 d {oversized} 0\n", "9" * 5000 + " 0 1 2 0\n",
        ):
            with self.subTest(prefix=proof[:40]):
                self.rejects(UNIT_CNF, proof)
        self.rejects("p cnf 1000001 2\n1 0 -1 0\n", UNIT_PROOF, code="integer_bound")

    def test_limits_reject_instead_of_weakening_checks(self):
        cases = (
            (UNIT_CNF, UNIT_PROOF, replace(checker.Limits(), max_hints=1), "hint_limit"),
            (UNIT_CNF, UNIT_PROOF, replace(checker.Limits(), max_live_clauses=2), "clause_limit"),
            (UNIT_CNF, UNIT_PROOF, replace(checker.Limits(), max_clause_id=2), "integer_bound"),
            (SPLIT_CNF, SPLIT_PROOF, replace(checker.Limits(), max_additions=1), "clause_limit"),
            (UNIT_CNF, UNIT_PROOF, replace(checker.Limits(), max_cnf_bytes=10), "byte_limit"),
            (UNIT_CNF, UNIT_PROOF, replace(checker.Limits(), max_proof_bytes=8), "byte_limit"),
            (UNIT_CNF, UNIT_PROOF + " " * 20, replace(checker.Limits(), max_line_bytes=16), "line_limit"),
        )
        for cnf, proof, limits, code in cases:
            with self.subTest(code=code, limits=limits):
                self.rejects(cnf, proof, limits=limits, code=code)
        self.rejects(UNIT_CNF, UNIT_PROOF, limits=replace(checker.Limits(), max_hints=0), code="invalid_limit")
        self.rejects(UNIT_CNF, UNIT_PROOF, limits=replace(checker.Limits(), max_hints=True), code="invalid_limit")

    def test_receipt_binds_exact_plain_and_gzip_bytes(self):
        plain = self.run_check(UNIT_CNF, UNIT_PROOF)
        compressed = self.run_check(UNIT_CNF, UNIT_PROOF, compressed=True)
        self.assertEqual(plain.cnf_sha256, hashlib.sha256(UNIT_CNF.encode()).hexdigest())
        self.assertEqual(plain.lrat_sha256, hashlib.sha256(UNIT_PROOF.encode()).hexdigest())
        self.assertEqual(plain.lrat_payload_sha256, plain.lrat_sha256)
        expected_gzip = gzip.compress(UNIT_PROOF.encode(), mtime=0)
        self.assertEqual(compressed.lrat_sha256, hashlib.sha256(expected_gzip).hexdigest())
        self.assertEqual(compressed.lrat_payload_sha256, plain.lrat_payload_sha256)
        self.assertEqual(compressed.lrat_payload_bytes, len(UNIT_PROOF.encode()))
        self.assertEqual(compressed.lrat_bytes, len(expected_gzip))
        semantic_fields = ("status", "variables", "clauses", "additions", "hints", "final_empty_clause")
        self.assertEqual({key: asdict(plain)[key] for key in semantic_fields},
                         {key: asdict(compressed)[key] for key in semantic_fields})
        self.rejects(UNIT_CNF, UNIT_PROOF, compressed=True, allow_gzip=False, code="gzip_disabled")
        # Its highly compressible comment is over the decompressed cap only.
        payload = "c " + "x" * 500 + "\n" + UNIT_PROOF
        self.rejects(UNIT_CNF, payload, compressed=True,
                     limits=replace(checker.Limits(), max_proof_bytes=100), code="byte_limit")

    def test_unreadable_and_corrupt_input_rejected(self):
        with tempfile.TemporaryDirectory(prefix="gl3-lrat-io-") as directory:
            cnf_path = Path(directory) / "tiny.cnf"
            cnf_path.write_text(UNIT_CNF)
            proof_path = Path(directory) / "bad.lrat.gz"
            proof_path.write_bytes(b"this is not gzip")
            with self.assertRaises(checker.CheckError) as captured:
                checker.check(cnf_path, proof_path)
            self.assertEqual(captured.exception.code, "io_error")
            with self.assertRaises(checker.CheckError) as captured:
                checker.check(Path(directory) / "missing.cnf", proof_path)
            self.assertEqual(captured.exception.code, "io_error")

    def test_cli_rejects_forgery_under_optimized_python(self):
        with tempfile.TemporaryDirectory(prefix="gl3-lrat-optimized-") as directory:
            cnf_path = Path(directory) / "tiny.cnf"
            proof_path = Path(directory) / "tiny.lrat"
            cnf_path.write_text("p cnf 1 1\n1 0\n")
            proof_path.write_text("2 0 1 0\n")
            result = subprocess.run(
                [sys.executable, "-I", "-O", "-W", "error", "-B",
                 str(Path(checker.__file__)), str(cnf_path), str(proof_path)],
                capture_output=True, text=True, check=False,
            )
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn('"status": "rejected"', result.stdout)
            self.assertIn('"code": "missing_conflict"', result.stdout)

    def test_exhaustive_tiny_empty_proof_soundness_against_all_models(self):
        formula_count = proof_count = accepted_count = rejected_count = 0
        with tempfile.TemporaryDirectory(prefix="gl3-lrat-exhaustive-") as directory:
            cnf_path, proof_path = Path(directory) / "tiny.cnf", Path(directory) / "tiny.lrat"
            for variables in (1, 2):
                # A non-tautological clause chooses absent, negative, or positive
                # independently for each variable; this includes the empty clause.
                clauses = tuple(
                    tuple(sign * variable for variable, sign in enumerate(signs, 1) if sign)
                    for signs in itertools.product((-1, 0, 1), repeat=variables)
                )
                for count in range(min(3, len(clauses)) + 1):
                    for formula in itertools.combinations(clauses, count):
                        formula_count += 1
                        satisfying_assignments = models(variables, formula)
                        cnf_path.write_text(dimacs(variables, formula))
                        for length in range(count + 1):
                            for hints in itertools.permutations(range(1, count + 1), length):
                                proof_count += 1
                                hint_text = " ".join(map(str, hints))
                                proof_path.write_text(f"{count + 1} 0 {hint_text} 0\n")
                                try:
                                    receipt = checker.check(cnf_path, proof_path)
                                except checker.CheckError:
                                    rejected_count += 1
                                    continue
                                accepted_count += 1
                                self.assertEqual(receipt.status, "verified_unsat")
                                self.assertEqual(
                                    satisfying_assignments, [],
                                    f"accepted satisfiable formula={formula!r}, hints={hints!r}",
                                )
        self.assertEqual(formula_count, 138)
        self.assertEqual(proof_count, 1581)
        self.assertGreater(accepted_count, 0)
        self.assertGreater(rejected_count, 0)

    def test_model_falsified_intermediate_clause_cannot_forge_unsat(self):
        """A concrete model supplies a final conflict if a false lemma slips in.

        Each input has an explicitly enumerated model fixed by unit clauses.
        Enumerate every nonempty non-tautological clause false in that model,
        and every repetition-free ordering of available first-step hints. A
        forged lemma, if admitted, would conflict with those units in the
        second step. Thus every complete two-step proof must be rejected.
        """
        proof_count = 0
        with tempfile.TemporaryDirectory(prefix="gl3-lrat-model-attack-") as directory:
            cnf_path, proof_path = Path(directory) / "tiny.cnf", Path(directory) / "tiny.lrat"
            for variables in (1, 2):
                nonempty_clauses = tuple(
                    tuple(sign * variable for variable, sign in enumerate(signs, 1) if sign)
                    for signs in itertools.product((-1, 0, 1), repeat=variables)
                    if any(signs)
                )
                for original in ((), *((clause,) for clause in nonempty_clauses)):
                    for values in models(variables, original):
                        units = tuple((variable if value else -variable,)
                                      for variable, value in enumerate(values, 1))
                        formula = original + units
                        self.assertEqual(models(variables, formula), [values])
                        cnf_path.write_text(dimacs(variables, formula))
                        count = len(formula)
                        unit_ids = tuple(range(len(original) + 1, count + 1))
                        for clause in nonempty_clauses:
                            if any(values[abs(literal) - 1] == (literal > 0) for literal in clause):
                                continue
                            clause_text = " ".join(map(str, clause))
                            final_hints = " ".join(map(str, (*unit_ids, count + 1)))
                            for length in range(count + 1):
                                for hints in itertools.permutations(range(1, count + 1), length):
                                    proof_count += 1
                                    hint_text = " ".join(map(str, hints))
                                    proof = (f"{count + 1} {clause_text} 0 {hint_text} 0\n"
                                             f"{count + 2} 0 {final_hints} 0\n")
                                    proof_path.write_text(proof)
                                    with self.assertRaises(
                                        checker.CheckError,
                                        msg=f"accepted model={values!r}, formula={formula!r}, clause={clause!r}, hints={hints!r}",
                                    ):
                                        checker.check(cnf_path, proof_path)
        self.assertEqual(proof_count, 1034)


if __name__ == "__main__":
    unittest.main()
