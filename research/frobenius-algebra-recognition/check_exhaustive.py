#!/usr/bin/env python3
"""Independent tiny-field and target-orbit checks for recognize.py.

The oracle uses F2 bitsets and complete vector-space enumeration, not the
recognizer's Gaussian elimination or Frobenius filtration implementation.
It is a finite regression certificate; the iff theorem is proved separately.
"""

import argparse
import importlib.util
import json
from itertools import product
from pathlib import Path


def load_recognizer():
    path = Path(__file__).with_name("recognize.py")
    spec = importlib.util.spec_from_file_location("recognize_oracle_target", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.recognize


recognize = load_recognizer()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def multiply_bits(left, right, table):
    """F2 bilinear multiplication in an independently encoded table."""
    result = 0
    for i, row in enumerate(table):
        if (left >> i) & 1:
            for j, value in enumerate(row):
                if (right >> j) & 1:
                    result ^= value
    return result


def power_bits(value, exponent, table):
    result = 1  # Every oracle table has its unit in coordinate zero.
    for _ in range(exponent):
        result = multiply_bits(result, value, table)
    return result


def span_bits(vectors):
    values = {0}
    for vector in vectors:
        values |= {value ^ vector for value in values}
    return values


def associative_bits(table):
    n = len(table)
    return all(
        multiply_bits(table[i][j], 1 << k, table)
        == multiply_bits(1 << i, table[j][k], table)
        for i, j, k in product(range(n), repeat=3)
    )


def coefficient_table(table):
    n = len(table)
    return [
        [[(value >> k) & 1 for k in range(n)] for value in row]
        for row in table
    ]


def vector_bits(vector, n):
    require(isinstance(vector, list) and len(vector) == n, "bad witness vector")
    require(all(type(value) is int and value in (0, 1) for value in vector),
            "witness coefficients are not canonical F2 elements")
    return sum(value << i for i, value in enumerate(vector))


def check_witness_bits(table, witness, expected_heights):
    """Check the supplied transporter without importing production checks."""
    n = len(table)
    require(witness.get("status") == "accepted", "positive oracle case rejected")
    require(witness.get("n") == n, "wrong witness dimension")
    heights = witness.get("heights")
    require(heights == expected_heights, "wrong canonical height sequence")
    require(vector_bits(witness.get("unit"), n) == 1, "wrong unit")
    generators = [vector_bits(vector, n) for vector in witness.get("generators", [])]
    require(len(generators) == len(heights), "wrong generator count")
    for generator, height in zip(generators, heights):
        require(power_bits(generator, 2 ** height, table) == 0,
                "generator nilpotence relation fails")
    exponents = list(product(*(range(2 ** height) for height in heights)))
    require(witness.get("monomial_exponents") == [list(powers) for powers in exponents],
            "wrong monomial exponent order")
    columns = [vector_bits(vector, n) for vector in witness.get("transporter", [])]
    require(len(columns) == n == len(exponents), "wrong transporter size")
    for column, powers in zip(columns, exponents):
        value = 1
        for generator, exponent in zip(generators, powers):
            value = multiply_bits(value, power_bits(generator, exponent, table), table)
        require(column == value, "transporter column is not its declared monomial")
    require(len(span_bits(columns)) == 2 ** n, "transporter is singular")
    # Check every product in the alleged truncated-polynomial basis.
    position = {powers: i for i, powers in enumerate(exponents)}
    for i, j in product(range(n), repeat=2):
        powers = tuple(a + b for a, b in zip(exponents[i], exponents[j]))
        expected = 0 if any(a >= 2 ** e for a, e in zip(powers, heights)) else columns[position[powers]]
        require(multiply_bits(columns[i], columns[j], table) == expected,
                "transporter does not intertwine multiplication")
    inverse = witness.get("inverse")
    require(isinstance(inverse, list) and len(inverse) == n, "wrong inverse size")
    for i, row in enumerate(inverse):
        row_bits = vector_bits(row, n)
        for j, column in enumerate(columns):
            require((row_bits & column).bit_count() % 2 == int(i == j),
                    "reported inverse does not invert transporter")


def check_dimension_two():
    accepted = 0
    for square in range(4):
        table = [[1, 2], [2, square]]
        require(associative_bits(table), "unexpected nonassociative 2D oracle table")
        witness = recognize(2, coefficient_table(table))
        # An element other than zero is square-zero exactly for square=0 or 1.
        nilpotents = [value for value in range(1, 4) if multiply_bits(value, value, table) == 0]
        expected = len(nilpotents) == 1
        require((witness.get("status") == "accepted") == expected,
                "2D exhaustive oracle disagrees")
        if expected:
            accepted += 1
            check_witness_bits(table, witness, [1])
    require(accepted == 2, "unexpected 2D orbit count")
    return {"fixed_unit_tables": 4, "associative": 4, "accepted": accepted}


def check_dimension_three():
    counts = {"nonassociative": 0, "nilradical_dimension_0": 0,
              "nilradical_dimension_1": 0, "nilradical_dimension_2": 0}
    for xx, xy, yy in product(range(8), repeat=3):
        table = [[1, 2, 4], [2, xx, xy], [4, xy, yy]]
        if not associative_bits(table):
            counts["nonassociative"] += 1
        else:
            nilpotents = [value for value in range(8) if power_bits(value, 4, table) == 0]
            # These are all nilpotents: nilpotence index is at most dimension 3.
            require(len(nilpotents) in (1, 2, 4), "unexpected nilradical size")
            require(span_bits(nilpotents) == set(nilpotents), "nilpotents fail linearity")
            counts[f"nilradical_dimension_{len(nilpotents).bit_length() - 1}"] += 1
        result = recognize(2, coefficient_table(table))
        require(result.get("status") == "rejected", "3D F2 table cannot be a p-group target")
    require(counts == {"nonassociative": 448, "nilradical_dimension_0": 24,
                       "nilradical_dimension_1": 24, "nilradical_dimension_2": 16},
            "independent 3D enumeration counts changed")
    return {"fixed_unit_tables": 512, "accepted": 0, **counts}


def unit_fixing_bases_four():
    for second in range(2, 16):
        span_two = span_bits([1, second])
        for third in range(1, 16):
            if third in span_two:
                continue
            span_three = span_bits([1, second, third])
            for fourth in range(1, 16):
                if fourth not in span_three:
                    yield (1, second, third, fourth)


def transport_table(table, basis):
    inverse = {}
    for coordinates in range(16):
        value = 0
        for i, column in enumerate(basis):
            if (coordinates >> i) & 1:
                value ^= column
        require(value not in inverse, "oracle basis is singular")
        inverse[value] = coordinates
    return tuple(tuple(inverse[multiply_bits(left, right, table)] for right in basis)
                 for left in basis)


def check_dimension_four_orbits():
    # Independently written standard multiplication tables in monomial bases.
    cyclic = [[1, 2, 4, 8], [2, 4, 8, 0], [4, 8, 0, 0], [8, 0, 0, 0]]
    elementary = [[1, 2, 4, 8], [2, 0, 8, 0], [4, 8, 0, 0], [8, 0, 0, 0]]
    bases = list(unit_fixing_bases_four())
    require(len(bases) == 1344, "wrong unit-fixing GL4 stabilizer size")
    orbits = []
    report = {"unit_fixing_bases": len(bases)}
    for name, table, heights, count in (
        ("cyclic", cyclic, [2], 336),
        ("elementary", elementary, [1, 1], 56),
    ):
        orbit = {transport_table(table, basis) for basis in bases}
        require(len(orbit) == count, "wrong independently generated target orbit size")
        for changed_table in sorted(orbit):
            require(associative_bits(changed_table), "transported target lost associativity")
            result = recognize(2, coefficient_table(changed_table))
            check_witness_bits(changed_table, result, heights)
        orbits.append(orbit)
        report[f"{name}_distinct_tables"] = len(orbit)
    require(not orbits[0].intersection(orbits[1]), "nonisomorphic target orbits intersect")
    report["accepted_distinct_tables"] = sum(map(len, orbits))
    # Completeness here is for the two positive isomorphism orbits, not for all
    # 2^24 fixed-unit commutative multiplication tables of dimension four.
    report["scope"] = "complete unit-fixing positive target orbits only"
    return report


def check_dimension_two_f3():
    for a, b in product(range(3), repeat=2):
        table = [[[1, 0], [0, 1]], [[0, 1], [a, b]]]
        result = recognize(3, table)
        require(result.get("status") == "rejected", "2D F3 table cannot be a p-group target")
    return {"fixed_unit_tables": 9, "accepted": 0}


def run_checks():
    return {
        "status": "passed",
        "f2_dimension_two": check_dimension_two(),
        "f2_dimension_three": check_dimension_three(),
        "f2_dimension_four": check_dimension_four_orbits(),
        "f3_dimension_two": check_dimension_two_f3(),
        "independent_method": "F2 bitsets, complete finite spans, target basis orbits",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="emit the deterministic verification report")
    args = parser.parse_args()
    report = run_checks()
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print("PASS: all 525 tiny fixed-unit tables and 392 positive 4D target presentations")


if __name__ == "__main__":
    main()
