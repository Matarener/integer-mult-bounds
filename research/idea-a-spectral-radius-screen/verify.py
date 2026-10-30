#!/usr/bin/env python3
"""Screen the spectral-radius proposal against one exact typed interface."""

from fractions import Fraction as F
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def require(condition, message):
    if not condition:
        raise SystemExit(f"FAIL: {message}")


def matmul(a, b):
    require(len(a[0]) == len(b), "matrix dimensions")
    return [[sum((a[i][k] * b[k][j] for k in range(len(b))), F(0))
             for j in range(len(b[0]))] for i in range(len(a))]


def matvec(a, x):
    require(all(len(row) == len(x) for row in a), "matrix/vector dimensions")
    return [sum((entry * value for entry, value in zip(row, x)), F(0))
            for row in a]


def check_toy_spectral_witness():
    matrix = [[F(0), F(6, 5)], [F(3, 5), F(0)]]
    square = matmul(matrix, matrix)
    require(square == [[F(18, 25), F(0)], [F(0), F(18, 25)]],
            "toy matrix square")

    vector = [F(1), F(7, 10)]
    rho = F(9, 10)
    image = matvec(matrix, vector)
    ceiling = [rho * value for value in vector]
    require(image == [F(21, 25), F(3, 5)], "toy matrix/vector product")
    require(all(left < right for left, right in zip(image, ceiling)),
            "positive rational contraction")
    require(sum(matrix[0]) == F(6, 5) > 1,
            "example must have a supercritical individual row")

    wrong_vector = [F(1), F(1, 2)]
    wrong_image = matvec(matrix, wrong_vector)
    wrong_ceiling = [rho * value for value in wrong_vector]
    require(not all(left <= right for left, right in zip(wrong_image, wrong_ceiling)),
            "bad-weight control escaped")
    return matrix, vector, rho


def check_repository_candidate():
    result = json.loads((ROOT / "research/z4-hetero-two-bank-seedba18/RESULT.json")
                        .read_text(encoding="utf-8"))
    a_count = len(result["types"]["A_blocks"])
    b_count = len(result["types"]["B_blocks"])
    require((a_count, b_count) == (3, 7), "typed source split")
    require(a_count + b_count == 10, "joint child count")
    require(result["separate_calls"]["map"].startswith("PASS"),
            "separate typed map")
    require(result["joint_3_7_two_banks"]["map"].startswith("PASS"),
            "joint typed map")

    separate = result["separate_calls"]["ADD_NEG"]
    joint = result["joint_3_7_two_banks"]["ADD_NEG"]
    phase = result["recurrence"]
    boundary_saving = {
        key: 2 * (phase["g3_ADD_NEG"][key] + phase["g7_ADD_NEG"][key]
                  - phase["g10_ADD_NEG"][key])
        for key in ("ADD", "NEG")
    }
    require(boundary_saving == {"ADD": 144, "NEG": 0},
            "exact 3|7 boundary saving")
    require({key: separate[key] - joint[key] for key in separate}
            == boundary_saving, "complete invoice differs only by boundary")
    require(result["saving"] == {"primitives": 144, "reads": 288},
            "published savings")
    require(result["assumptions_and_limits"] and any(
        "recursive assembly into a selected supplier" in item
        for item in result["assumptions_and_limits"]),
        "selected-supplier transfer must remain unresolved")
    require("No new kappa" in " ".join(result["assumptions_and_limits"]),
            "candidate is not an admitted kappa result")
    return boundary_saving


def check_existing_theorem_and_candidate_boundary():
    theory = (ROOT / "research/kappa-action-theory/volumes/04-analytic.md")
    text = theory.read_text(encoding="utf-8")
    require("### A051 — Theorem: A positive type vector closes a heterogeneous caller recurrence"
            in text, "existing general typed-recursion theorem")
    require("### A052 — Theorem: A two-state primitive has an explicit rational type certificate"
            in text, "existing exact two-state certificate")
    require("### A054 — Theorem: A cyclic sequence of state transitions has constructive weights"
            in text, "existing cycle certificate")

    readme = (ROOT / "research/z4-hetero-two-bank-seedba18/README.md")
    readme_text = readme.read_text(encoding="utf-8")
    require("recursive assembly into a selected supplier" in readme_text,
            "candidate supplier boundary")
    require("No new κ" in readme_text, "candidate kappa boundary")


def main():
    matrix, vector, rho = check_toy_spectral_witness()
    saving = check_repository_candidate()
    check_existing_theorem_and_candidate_boundary()
    require(sum(matrix[0]) > 1 and rho < 1,
            "positive control must demonstrate supercritical row / contraction")
    print("PASS_IDEA_A_SPECTRAL_SCREEN toy_rho_bound=9/10 "
          f"positive_vector={vector[0]},{vector[1]} "
          f"typed_children=3+7 boundary_saving={saving['ADD']} "
          "new_recursive_matrix=not_instantiated selected_kappa_change=none")


if __name__ == "__main__":
    main()
