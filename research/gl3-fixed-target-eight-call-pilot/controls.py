"""Semantic, independent-replay, and solver calibration controls."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import time

import exact_checker as independent
from model import Algebra, ID, LABELS, PAIRS, TARGET, build, multiply, extract_word, support_masks

ALIAS_WORD = [(2, 3, 0, 2), (1, 3, 2, 1), (1, 1, 1, 2),
              (3, 1, 0, 1), (1, 1, 2, 1), (1, 1, 1, 0), (1, 3, 0, 1)]
ALIAS_TARGET = (140, 279, ID)


def row_tuple(n):
    return tuple((n >> (3 * r)) & 7 for r in range(3))


def main(output):
    import z3
    start = time.perf_counter()
    a = Algebra()
    passed = []
    assert set(map(row_tuple, a.group)) == set(independent.group())
    assert Counter(map(len, a.paths.values())) == {0: 1, 1: 6, 2: 24, 3: 51, 4: 60, 5: 24, 6: 2}
    passed.append("independent_group_enumeration_and_direct_distance_layers")
    for x in a.group:
        for y in a.group:
            assert row_tuple(multiply(x, y)) == independent.product(row_tuple(x), row_tuple(y))
    passed.append("all_28224_group_products_independent")
    unit = a.endpoint((ID, ID, ID))
    for gate in a.generators:
        assert a.step(a.step(unit, gate), gate) == unit
        for role in range(3):
            actual = independent.column([gate], role)
            packed = a.step(unit, gate)
            for r in range(3):
                expected = {row_tuple(g) for k, g in enumerate(a.group)
                            if packed[3 * r + role] & (1 << k)}
                assert actual[r] == expected
    passed.append("all_168_paid_factors_independent_and_involutions")
    # Exhaustively compare every two-factor formal product with independent
    # coefficient sets (three identity-address inputs determine all coefficients).
    for first in a.generators:
        prefix = a.step(unit, first)
        for second in a.generators:
            packed = a.step(prefix, second)
            for role in range(3):
                actual = independent.column([first, second], role)
                for r in range(3):
                    bits = sum(1 << a.index[sum(row << (3 * k) for k, row in enumerate(g))]
                               for g in actual[r])
                    assert bits == packed[3 * r + role]
    passed.append("all_28224_two_factor_products_independent")
    direct = a.direct_word()
    assert len(direct) == 9 and [len(a.paths[g]) for g in TARGET] == [4, 5, 0]
    direct_report = independent.check(direct)
    assert direct_report["accepted"]
    passed.append("direct_nine_all_504_regular_basis_columns")
    tampered = [direct[:k] + direct[k + 1:] for k in range(9)]
    tampered += [[(u, v, j, i) for u, v, i, j in direct], list(reversed(direct))]
    changed = list(direct)
    u, v, i, j = changed[0]
    replacement = next(pair for pair in PAIRS if pair != (i, j))
    changed[0] = (u, v, *replacement)
    tampered.append(changed)
    for word in tampered:
        assert not independent.check(word, all_columns=False)["accepted"]
    passed.append("12_omission_transposition_reversal_changed_label_rejections")
    dirty_word = direct + [(4, 4, 0, 1)]
    dirty_report = independent.check(dirty_word)
    assert dirty_report["failing_columns"] == 168
    assert all(independent.column(dirty_word, role) == independent.column(direct, role)
               for role in (0, 1))
    passed.append("dirty_third_restoration_only_failure_rejected")
    alias_target = tuple(map(row_tuple, ALIAS_TARGET))
    assert independent.natural_rows(ALIAS_WORD) == independent.natural_target(alias_target)
    alias_report = independent.check(ALIAS_WORD, alias_target)
    assert not alias_report["accepted"] and alias_report["failing_columns"] > 0
    passed.append("known_seven_call_natural_alias_rejected_formally")
    try:
        independent.validate_word([(1, 2, 0, 1)])
        raise AssertionError("nilpotent mask accepted")
    except ValueError:
        pass
    passed.append("nilpotent_rank_one_excluded")
    # All rank-one idempotents are the scalar conjugates of coordinate projector.
    projector = 1
    conjugates = set()
    for m in a.group:
        inverse = next(n for n in a.group if multiply(m, n) == ID)
        conjugates.add(multiply(multiply(m, projector), inverse))
    outer_products = {sum(((u >> r) & (v >> c) & 1) << (3 * r + c)
                          for r in range(3) for c in range(3))
                      for u, v, _, _ in a.generators}
    assert len(outer_products) == 28 and conjugates == outer_products
    passed.append("all_28_scalar_conjugates_exactly_equal_paid_projectors")
    calibration = []
    cases = [
        ("fixed_direct_nine", 9, TARGET, direct, z3.sat),
        ("fixed_natural_alias", 7, ALIAS_TARGET, ALIAS_WORD, z3.unsat),
        ("fixed_missing_last_call", 8, TARGET, direct[:-1], z3.unsat),
        ("fixed_dirty_restoration_failure", 10, TARGET, dirty_word, z3.unsat),
        ("unrestricted_one_call_identity", 1, (ID, ID, ID), None, z3.unsat),
        ("unrestricted_two_call_identity", 2, (ID, ID, ID), None, z3.sat),
    ]
    for name, length, target, fixed, expected in cases:
        solver, controls, _ = build(length, target, fixed)
        solver.set(timeout=30000, max_memory=2048)
        then = time.perf_counter()
        result = solver.check()
        assert result == expected, (name, str(result), solver.reason_unknown())
        if result == z3.sat:
            decoded = extract_word(solver.model(), controls)
            assert independent.check(decoded, tuple(map(row_tuple, target)))["accepted"]
        calibration.append({"name": name, "result": str(result),
                            "elapsed_seconds": time.perf_counter() - then})
    passed.append("six_solver_calibration_cases")
    for gate in a.generators:
        solver, _, _ = build(1, fixed_word=[gate], expected_state=a.step(unit, gate))
        solver.set(timeout=5000, max_memory=2048)
        assert solver.check() == z3.sat
    passed.append("all_168_symbolic_single_factor_encodings")
    for name, length, target, fixed, expected in cases:
        solver, controls, _ = build(length, target, fixed, support_bounds=True)
        solver.set(timeout=30000, max_memory=2048)
        assert solver.check() == expected, ("support_bound", name)
        if expected == z3.sat:
            assert independent.check(extract_word(solver.model(), controls),
                                     tuple(map(row_tuple, target)))["accepted"]
    passed.append("six_support_bounded_solver_calibrations")
    masks = support_masks(a, 9)
    state = unit
    for t in range(10):
        for r in range(3):
            for c in range(3):
                assert state[3 * r + c] & ~masks[t][c] == 0
        if t < 9:
            state = a.step(state, direct[t])
    passed.append("direct_nine_every_prefix_obeys_forward_backward_support")
    tactic_calibration = []
    for name, length, target, fixed, expected in cases:
        solver, controls, _ = build(length, target, fixed, support_bounds=True,
                                    engine="bitblast")
        solver.set(timeout=30000, max_memory=2048, threads=1, random_seed=0)
        then = time.perf_counter()
        result = solver.check()
        assert result == expected, ("bitblast", name, str(result))
        if result == z3.sat:
            assert independent.check(extract_word(solver.model(), controls),
                                     tuple(map(row_tuple, target)))["accepted"]
        tactic_calibration.append({"name": name, "result": str(result),
                                   "elapsed_seconds": time.perf_counter() - then})
    passed.append("six_explicit_bitblast_solver_calibrations")
    report = {"status": "PASS", "checks": passed, "check_count": len(passed),
              "direct_word_uvij": direct, "direct_report": direct_report,
              "alias_report": alias_report, "dirty_restoration_report": dirty_report,
              "solver_calibrations": calibration, "z3_version": z3.get_version_string(),
              "explicit_bitblast_calibrations": tactic_calibration,
              "elapsed_seconds": time.perf_counter() - start}
    Path(output).write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2), flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="CONTROLS.json")
    main(parser.parse_args().output)
