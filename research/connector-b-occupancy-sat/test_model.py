"""Behavioral controls for the independent Boolean translation."""

import importlib.util
import itertools
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

from pysat.solvers import Cadical195

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("occupancy_verify", HERE / "verify.py")
V = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(V)
M = V.M
ORIGINAL = (0, 1, 0, 2, 0, 1, 0, 5, 2, 3, 4, 3, 6, 3, 4, 3, 5, 3, 4, 3, 6, 3, 4, 3)
NEGATIVE = (3, 4, 2, 5, 0, 1, 6, 1, 0, 3, 5, 4, 0, 3, 1, 4, 3, 2, 0, 4, 6, 1)


def fixture(original, mapping):
    word = tuple(mapping[label] for label in original)
    boundary = next(i for i in range(len(word)) if word[i] >= 3)
    word = word[boundary + 1 :] + word[: boundary + 1]
    low, fixed, run, high, start = [], [], [], 0, 0
    for label in word:
        if label < 3:
            run.append(label)
            high ^= 1 << label
        else:
            low.append(label - 3)
            fixed.append((start, tuple(run)))
            start, run = high, []
    M.need(not run and high == 0, "literal fixture closes on a low step")
    return word, tuple(low), fixed


def decide(formula):
    with Cadical195(bootstrap_with=formula.clauses) as solver:
        result = solver.solve()
        return result, solver.get_model() if result else None


class EncodingBehavior(unittest.TestCase):
    def test_all_small_cardinality_assignments(self):
        for size in range(1, 6):
            for target in range(size + 1):
                formula = M.Formula()
                literals = [formula.var("x", i) for i in range(size)]
                formula.exactly_count(literals, target, "test")
                with Cadical195(bootstrap_with=formula.clauses) as solver:
                    for bits in itertools.product((False, True), repeat=size):
                        assumptions = [
                            x if bit else -x
                            for x, bit in zip(literals, bits, strict=True)
                        ]
                        self.assertEqual(
                            solver.solve(assumptions=assumptions), sum(bits) == target
                        )

    def test_all_small_exactly_one_assignments(self):
        for size in range(1, 7):
            formula = M.Formula()
            literals = [formula.var("x", i) for i in range(size)]
            formula.exactly_one(literals, "test")
            with Cadical195(bootstrap_with=formula.clauses) as solver:
                for bits in itertools.product((False, True), repeat=size):
                    self.assertEqual(
                        solver.solve(
                            assumptions=[
                                x if bit else -x
                                for x, bit in zip(literals, bits, strict=True)
                            ]
                        ),
                        sum(bits) == 1,
                    )

    def test_ordered_paths_have_their_literal_endpoints(self):
        observed = set()
        for vertices, word in M.paths():
            points, end = M.prefix_points(word)
            self.assertEqual((*points, end), vertices)
            self.assertEqual(len(set(vertices)), len(vertices))
            observed.add(word)
        self.assertEqual(len(observed), 112)
        self.assertIn((1, 0, 2, 0, 1, 0, 2), observed)
        self.assertIn((2, 0, 1, 0, 2, 0, 1), observed)

    def test_fixed_simple24_is_sat_and_decodes(self):
        word, low, fixed = fixture(ORIGINAL, (3, 2, 4, 0, 1, 5, 6))
        formula = M.build(low, (8, 4, 2), fixed=fixed, symmetry=False)
        result, assignment = decide(formula)
        self.assertTrue(result)
        self.assertEqual(tuple(M.word_from(formula, low, assignment)), word)
        self.assertEqual(M.check_word(word, (8, 4, 2), True)["coverage"], 128)

    def test_unfixed_simple24_is_sat_and_checked(self):
        _, low, _ = fixture(ORIGINAL, (3, 2, 4, 0, 1, 5, 6))
        formula = M.build(low, (8, 4, 2), symmetry=False)
        result, assignment = decide(formula)
        self.assertTrue(result)
        M.check_word(M.word_from(formula, low, assignment), (8, 4, 2), True)

    def test_noncover_is_sat_only_without_coverage(self):
        word, low, fixed = fixture(NEGATIVE, (3, 0, 4, 1, 2, 5, 6))
        self.assertEqual(M.check_word(word, (4, 4, 4), False)["coverage"], 126)
        for cover in (False, True):
            formula = M.build(low, cover=cover, fixed=fixed, symmetry=False)
            self.assertEqual(decide(formula)[0], not cover)

    def test_equal_count_first_appearance_symmetry_has_a_positive_word(self):
        _, low, _ = fixture(NEGATIVE, (3, 0, 4, 1, 2, 5, 6))
        formula = M.build(low, cover=False)
        result, assignment = decide(formula)
        self.assertTrue(result)
        word = M.word_from(formula, low, assignment)
        M.check_word(word, (4, 4, 4), False)
        first_occurrences = [word.index(axis) for axis in range(3)]
        self.assertEqual(first_occurrences, sorted(first_occurrences))

    def test_repeated_origin_fails_simplicity_without_coverage(self):
        original = list(ORIGINAL)
        original[7], original[8] = original[8], original[7]
        word, low, fixed = fixture(original, (3, 2, 4, 0, 1, 5, 6))
        points, end = M.prefix_points(word)
        self.assertEqual((len(points), len(set(points)), end), (24, 23, 0))
        self.assertEqual(len({a ^ b for a in points for b in points}), 128)
        self.assertFalse(decide(M.build(low, (8, 4, 2), False, fixed, False))[0])

    def test_wrong_coordinate_total_is_unsat(self):
        _, low, fixed = fixture(ORIGINAL, (3, 2, 4, 0, 1, 5, 6))
        self.assertFalse(decide(M.build(low, (7, 4, 2), False, fixed, False))[0])

    def test_initial_translation_and_invalid_symmetry_rejected(self):
        _, low, fixed = fixture(ORIGINAL, (3, 2, 4, 0, 1, 5, 6))
        with self.assertRaises(ValueError):
            M.build(low, (8, 4, 2), symmetry=True)
        shifted = [(start ^ 1, word) for start, word in fixed]
        with self.assertRaises(ValueError):
            M.build(low, (8, 4, 2), fixed=shifted, symmetry=False)

    def test_incomplete_solver_is_not_an_exclusion(self):
        with tempfile.TemporaryDirectory() as temporary:
            with self.assertRaisesRegex(ValueError, "incomplete"):
                V.solve_one(1, Path(temporary), budget=1)

    def test_native_trace_is_finalized_and_truncation_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            binary = V.compile_checker(directory)
            cnf, proof = directory / "trace.cnf", directory / "trace.drat"
            cnf.write_text("p cnf 2 4\n1 2 0\n1 -2 0\n-1 2 0\n-1 -2 0\n")
            with Cadical195(
                bootstrap_with=[[1, 2], [1, -2], [-1, 2], [-1, -2]], with_proof=True
            ) as solver:
                self.assertFalse(solver.solve())
                V.binary_proof(solver, proof)
            V.check_proof(binary, cnf, proof, directory / "valid.log")
            proof.write_bytes(b"")
            V.check_proof(binary, cnf, proof, directory / "truncated.log", False)

    def test_native_template_ids_match_independent_group_action(self):
        with tempfile.TemporaryDirectory() as temporary:
            binary = Path(temporary) / "native"
            source = V.ROOT / "research/connector-covering-code/cycle_search.cpp"
            subprocess.run(
                [
                    "c++",
                    "-std=c++17",
                    "-O2",
                    "-Wall",
                    "-Wextra",
                    "-Wpedantic",
                    "-Werror",
                    str(source),
                    "-o",
                    str(binary),
                ],
                check=True,
                timeout=60,
                capture_output=True,
            )
            result = subprocess.run(
                [str(binary), "--pattern", "B", "--list-only"],
                capture_output=True,
                text=True,
                check=True,
                timeout=90,
            )
            rows = [json.loads(line) for line in result.stdout.splitlines()]
            lows = [
                (row["template"], tuple(row["low_word"]))
                for row in rows
                if "template" in row
            ]
            self.assertEqual(lows, list(enumerate(M.templates(), 1)))


if __name__ == "__main__":
    unittest.main()
