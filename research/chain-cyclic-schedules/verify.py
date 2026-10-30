#!/usr/bin/env python3
"""Read-only exact replay. No network, Git, numpy or assertions required."""
import hashlib
import json
from math import comb, gcd
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from periods import (check_unit_row, divisors, fixed_count, period_row,
                     repeated_counts, require, unit_repeated_count)
from oracle import (chronological_counts, literal_census, matrix_counts,
                    residue_dp, words)


def check_sources():
    sources = json.loads((HERE / "SOURCES.json").read_text(encoding="utf-8"))
    checked = 0
    for row in sources["files"]:
        if "vendored_as" in row:
            payload = (HERE / row["vendored_as"]).read_bytes()
            require(hashlib.sha256(payload).hexdigest() == row["sha256"], "source SHA256 mismatch")
            checked += 1
    return checked


def source_rows():
    data = json.loads((HERE / "source/6037-RESULT.json").read_text(encoding="utf-8"))
    rows = {int(k): [int(x) for x in v] for k, v in data["balanced_counts"].items()}
    require(set(rows) == set(range(2, 25)), "source census domain")
    for m, row in rows.items():
        require(len(row) == m and all(x >= 0 for x in row), "source census shape")
    rows[1] = [6]
    return rows


def all_period_rows(rows):
    answer, unit_cases = {}, 0
    for m in range(1, 25):
        answer[str(m)] = []
        for c in range(m):
            row = period_row(m, c, rows)
            row["target"] = c
            if m >= 2 and gcd(c, m) == 1:
                row["unit_repeated_words"] = check_unit_row(m, c, rows, row)
                unit_cases += 1
            answer[str(m)].append(row)
    return answer, unit_cases


def check_literal(rows, table):
    stats = dict(words=0, rotations=0, scalar_matrix_comparisons=0, cases=0)
    for m in range(1, 6):
        found = literal_census(m)
        require(found["counts"] == rows[m], "literal W does not match source")
        for c in range(m):
            row = table[str(m)][c]
            require(found["orbits"][c] == row["cyclic_orbits"], "literal cyclic orbit mismatch")
            for d in divisors(m):
                require(found["fixed"][d][c] == row["fixed"][str(d)], "literal fixed-point mismatch")
                require(found["exact"][c][d] == row["exact_repetitions"][str(d)],
                        "literal least-period mismatch")
            stats["cases"] += 1
        stats["words"] += found["total"]
        stats["rotations"] += found["rotations"]
        stats["scalar_matrix_comparisons"] += found["matrix_checks"]
    return stats


def check_repetition():
    tests = restored = 0
    for n in range(1, 5):
        for word, (a, b, t) in words(n):
            for d in range(1, 9):
                m = n * d
                predicted = repeated_counts(n, d, a, b, t)
                actual = chronological_counts(word * d)
                require(predicted == actual, "integer repetition identity")
                if n <= 2:
                    require(matrix_counts(word * d) == actual, "repetition matrix identity")
                pair_ok = actual[0] % m == actual[1] % m == 0
                gate = (d % 2 == 1 or n % 2 == 0) and a % n == b % n == 0
                require(pair_ok == gate, "repetition pair gate")
                if pair_ok:
                    target = (d * t + comb(d, 3) * n**3) % m
                    require(actual[2] % m == target, "repetition target shift")
                    restored += 1
                tests += 1
    return dict(cases=tests, restored_pair_cases=restored, max_modulus=32)


def check_controls(rows, table):
    controls = {
        "naive_total_over_length": rows[3][1] % 9 != 0,
        "missing_even_odd_pair_gate": fixed_count(2, 0, 2, rows) == 0 and rows[1][0] == 6,
        "missing_cubic_shift": fixed_count(3, 1, 3, rows) == 6 and 1 % 3 != 0,
        "wrong_cubic_shift_sign": fixed_count(3, 1, 3, rows) != fixed_count(3, 2, 3, rows),
        "missing_target_divisibility": fixed_count(3, 0, 3, rows) == 0 and rows[1][0] > 0,
        "all_unit_words_primitive": unit_repeated_count(3, 1, rows) == 6,
        "allow_unit_repetition_at_nine": unit_repeated_count(9, 1, rows) == 0,
        "missing_totient_weight": table["5"][0]["cyclic_orbits"] * 15 != rows[5][0] + 6,
        "mobius_sign_reversed": table["4"][0]["primitive_words"] != rows[4][0] + 42,
        "nonunit_repetition_three_only": table["4"][0]["exact_repetitions"]["2"] == 42,
        "larger_unit_exception": unit_repeated_count(15, 8, rows) == 5340,
        "small_existence_exception_six": unit_repeated_count(6, 5, rows) == 0,
        "small_existence_exception_twelve": unit_repeated_count(12, 1, rows) == 0
                                          and unit_repeated_count(12, 7, rows) == 216,
    }
    for name, passed in controls.items():
        require(passed, "negative control: " + name)
    return list(controls)


def build():
    source_checks = check_sources()
    rows = source_rows()
    table, unit_cases = all_period_rows(rows)
    literal = check_literal(rows, table)
    for m in range(1, 9):
        require(residue_dp(m) == rows[m], "independent DP/source mismatch")
    repetition = check_repetition()
    controls = check_controls(rows, table)
    return dict(schema_version=1, status="PASS_CHAIN_CYCLIC_SCHEDULES",
                source_files_checked=source_checks, literal=literal,
                dp_moduli=list(range(1, 9)), repetition=repetition,
                unit_cases=unit_cases, controls=controls,
                derived_from_source_counts_through=24, period_counts=table)


def main():
    result = build()
    expected = json.loads((HERE / "EXPECTED.json").read_text(encoding="utf-8"))
    require(result == expected, "EXPECTED result mismatch")
    receipt = {"result": result, "files": {}}
    for path in sorted(HERE.rglob("*")):
        if path.is_file() and "__pycache__" not in path.parts:
            receipt["files"][path.relative_to(HERE).as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
    print(json.dumps(receipt, sort_keys=True))


if __name__ == "__main__":
    main()
