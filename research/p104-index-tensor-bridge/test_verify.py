#!/usr/bin/env python3
"""Failure controls for the index-to-tensor bridge. Standard library only."""
from __future__ import annotations

import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import verify


def require(condition, message):
    if not condition:
        raise SystemExit("FAIL: " + message)


def test_wrong_column_convention():
    operator = verify.witness(verify.N)
    state = verify.state_from(verify.N, 4)
    fiber = verify.axis1_broadcast(operator, state)
    omitted_transpose = verify.matmul(state, operator)
    gaps = verify.compare(fiber, omitted_transpose)
    require(gaps > 0, "omitting K^t must disagree on the non-symmetric witness")


def test_mutated_coefficient_breaks_square():
    b2, _gram = verify.load_b2()
    mutated = [row[:] for row in b2]
    mutated[0][0] += 1
    try:
        verify.check_geometry(mutated)
    except SystemExit as exc:
        require(str(exc).startswith("FAIL:"), "mutation must fail closed")
        return
    raise SystemExit("FAIL: mutated B2 was accepted")


def test_receipt_shape():
    b2, gram = verify.load_b2()
    require(gram[0][0] == 8 and len(b2) == 8 and len(b2[0]) == 96, "fixture shape")
    require(verify.factored_frobenius_square([(1, [[1]], [[1]])]) == 1, "one-cell contraction")


def main():
    test_wrong_column_convention()
    test_mutated_coefficient_breaks_square()
    test_receipt_shape()
    print("PASS_P104_INDEX_TENSOR_BRIDGE_TESTS " + json.dumps({
        "groups": 3, "new_kappa": False}, sort_keys=True))


if __name__ == "__main__":
    main()
