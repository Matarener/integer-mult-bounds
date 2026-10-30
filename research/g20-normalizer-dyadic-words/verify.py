#!/usr/bin/env python3
"""Construct exact dyadic words for the retained G20 port matrices.

ToikY with substantial OpenAI Codex assistance. Apache-2.0.
Ali Romman's frozen port/controller data retain the credit in NOTICE.
RIGHT convention: ADD[i,j,a] is I+a e_i e_j^T, so row[j] += a*row[i].
"""
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import argparse
import json


HERE = Path(__file__).resolve().parent
SOURCE_HASHES = {
    "PORTS.json": "a53a49c938a46c5a9da8c05ffdec4c2ef2dd906dd94c009d6fa451af4ed350e9",
    "CONTROLLER.json": "39ac84fb848b908f7ba051fae4556d507900c421dc5d23501a9c0cb1d61fd08d",
    "CALLS.json": "30dcc37cdade6b2dc05478837eca28b696894d1c4782bac6a1caab5e7f56c9e8",
}


def need(condition, reason):
    if not condition:
        raise ValueError(reason)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def power_two(integer):
    return integer > 0 and integer & (integer - 1) == 0


def dyadic(value):
    return power_two(value.denominator)


def unit(value):
    return dyadic(value) and power_two(abs(value.numerator))


def identity(size):
    return [[Q(i == j) for j in range(size)] for i in range(size)]


def inverse_operation(operation):
    if operation[0] == "ADD":
        return ["ADD", operation[1], operation[2], str(-Q(operation[3]))]
    return ["SCALE", operation[1], str(1 / Q(operation[2]))]


def validate_operation(operation, size):
    opcode, i = operation[:2]
    need(type(i) is int and 0 <= i < size, "word coordinate")
    if opcode == "ADD":
        need(len(operation) == 4, "ADD arity")
        j, value = operation[2], Q(operation[3])
        need(type(j) is int and 0 <= j < size and i != j and value and dyadic(value),
             "nonzero dyadic ADD")
    else:
        need(opcode == "SCALE" and len(operation) == 3 and unit(Q(operation[2])),
             "SCALE is a dyadic unit")


def right_product(word, size):
    result = identity(size)
    for operation in word:
        validate_operation(operation, size)
        i = operation[1]
        if operation[0] == "ADD":
            j, coefficient = operation[2], Q(operation[3])
            for row in result:
                row[j] += coefficient * row[i]
        else:
            coefficient = Q(operation[2])
            for row in result:
                row[i] *= coefficient
    return result


def checked_product(word, expected):
    need(right_product(word, len(expected)) == expected, "exact RIGHT matrix product")


def factor(matrix):
    """Unit-only row reduction, with Euclidean pivots over dyadic integers.

    At each column, unit row scales first clear powers-of-two denominators.
    Euclidean ADDs and explicitly lowered swaps produce its integer gcd. A
    nonunit gcd is a strict stop, never an invitation to divide by an odd part.
    """
    size = len(matrix)
    current = [row[:] for row in matrix]
    reduction = []

    def emit(operation):
        validate_operation(operation, size)
        reduction.append(operation)
        i = operation[1]
        if operation[0] == "ADD":
            j, coefficient = operation[2], Q(operation[3])
            current[i] = [a + coefficient * b for a, b in zip(current[i], current[j])]
        else:
            current[i] = [Q(operation[2]) * a for a in current[i]]

    def swap(i, j):
        if i != j:
            emit(["ADD", i, j, "1"])
            emit(["ADD", j, i, "-1"])
            emit(["ADD", i, j, "1"])
            emit(["SCALE", j, "-1"])

    for column in range(size):
        for row in range(column, size):
            denominator = max(value.denominator for value in current[row])
            need(power_two(denominator), "dyadic source matrix")
            if denominator != 1:
                emit(["SCALE", row, str(denominator)])
        candidates = [row for row in range(column, size) if current[row][column]]
        need(candidates, "invertible source matrix")
        swap(column, min(candidates, key=lambda row: abs(current[row][column])))
        for row in range(column + 1, size):
            while current[row][column]:
                need(current[row][column].denominator == current[column][column].denominator == 1,
                     "integer Euclidean pivot")
                quotient = current[row][column] // current[column][column]
                if quotient:
                    emit(["ADD", row, column, str(-quotient)])
                if current[row][column]:
                    swap(column, row)
        pivot = current[column][column]
        need(unit(pivot), "Euclidean pivot must be a dyadic unit")
        if pivot != 1:
            emit(["SCALE", column, str(1 / pivot)])
        for row in range(size):
            if row != column and current[row][column]:
                emit(["ADD", row, column, str(-current[row][column])])
    need(current == identity(size), "complete unit row reduction")
    # R_m ... R_1 W = I implies W = R_1^-1 ... R_m^-1.
    forward = [inverse_operation(operation) for operation in reduction]
    inverse = [inverse_operation(operation) for operation in reversed(forward)]
    checked_product(forward, matrix)
    return forward, inverse


def authenticated(name, raw):
    need(sha256(raw).hexdigest() == SOURCE_HASHES[name], "source bytes: " + name)
    return json.loads(raw)


def placement(stage, ordinal, stages):
    need(type(ordinal) is int and 0 <= ordinal < len(stages) and stages[ordinal] == stage,
         "stage ordinal binding")
    active = [0] + list(range(1 + 7 * ordinal, 8 + 7 * ordinal))
    need(len(active) == len(set(active)) == 8 and max(active) < 127, "compatible active layout")
    return active


def address(half, row, slot, lane, f):
    size = 127 * f
    return half * size * size + row * size + slot * f + lane


def route_guard(source, destination, active, half, row, lane, f):
    size = 127 * f
    base = half * size * size + row * size
    need(0 <= row < size and 0 <= lane < f and half in (0, 1), "address domain")
    need(source in {base + slot * f + lane for slot in active}
         and destination in {base + slot * f + lane for slot in active},
         "spectator write or wrong row/lane")
    need(half * size * size <= source < (half + 1) * size * size
         and half * size * size <= destination < (half + 1) * size * size,
         "address half boundary")


def layout_checks(stages):
    samples = []
    for f in (1, 2):
        checks = 0
        size = 127 * f
        for ordinal, stage in enumerate(stages):
            active = placement(stage, ordinal, stages)
            spectators = set(range(127)) - set(active)
            need(len(spectators) == 119 and not spectators & set(active), "119 untouched spectators")
            for half in (0, 1):
                for row in range(size):
                    for lane in range(f):
                        addresses = [address(half, row, slot, lane, f) for slot in active]
                        need(len(set(addresses)) == 8, "injective active addresses")
                        for source in addresses:
                            # Every possible target is in the same validated set;
                            # this checks all ADD pairs without allocating a tape.
                            route_guard(source, source, active, half, row, lane, f)
                            checks += 1
        samples.append({"f": f, "N": size, "active_address_checks": checks,
                        "stages": len(stages), "spectator_slots_per_row_lane": 119})
    return samples


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true", help="emit candidate only; never write files")
    args = parser.parse_args()
    raw = {name: (HERE / "inputs" / name).read_bytes() for name in SOURCE_HASHES}
    data = {name: authenticated(name, content) for name, content in raw.items()}
    records = data["PORTS.json"]["port_interfaces"]["ports"]
    controller, calls = data["CONTROLLER.json"], data["CALLS.json"]
    stages = controller["invoice"]["thick_stages"]
    need(stages == [call["stage"] for call in calls] == [0, 1, *range(3, 32, 2), 32],
         "exact retained thick-stage schedule")
    need(controller["ambient_rank"] == 127 and len(stages) == 18, "ambient and stage counts")
    need([record["port"] for record in records] == list(range(111)), "all exact port IDs")
    ports, histograms = [], {"ADD": Counter(), "SCALE": Counter()}
    max_height = max_numerator_bits = max_denominator_bits = 0
    for record in records:
        matrix = [[Q(value) for value in row] for row in record["normalizer"]]
        inverse_matrix = [[Q(value) for value in row] for row in record["inverse"]]
        need(len(matrix) == len(inverse_matrix) == 8
             and all(len(row) == 8 for row in matrix + inverse_matrix), "eight-coordinate source matrices")
        forward, inverse = factor(matrix)
        checked_product(inverse, inverse_matrix)
        checked_product(forward + inverse, identity(8))
        for operation in forward + inverse:
            value = Q(operation[-1])
            histograms[operation[0]][str(value)] += 1
            max_height = max(max_height, abs(value.numerator), value.denominator)
            max_numerator_bits = max(max_numerator_bits, abs(value.numerator).bit_length())
            max_denominator_bits = max(max_denominator_bits, value.denominator.bit_length())
        ports.append({"port": record["port"], "line": record["line"],
                      "complement": record["complement"],
                      "forward_word": forward, "inverse_word": inverse})
    synthetic = [[Q(3), Q(1)], [Q(2), Q(1)]]
    synthetic_word, synthetic_inverse = factor(synthetic)
    checked_product(synthetic_word + synthetic_inverse, identity(2))
    samples = layout_checks(stages)
    controls = []

    def reject(name, expected, operation):
        try:
            operation()
        except ValueError as error:
            need(str(error) == expected, "control wrong failure: " + name)
            controls.append({"name": name, "reason": str(error), "rejected": True})
        else:
            raise ValueError("control accepted: " + name)

    first_matrix = [[Q(value) for value in row] for row in records[0]["normalizer"]]
    reject("omitted_operation", "exact RIGHT matrix product",
           lambda: checked_product(ports[0]["forward_word"][1:], first_matrix))
    witness = next(index for index, port in enumerate(ports)
                   if right_product(list(reversed(port["forward_word"])), 8)
                   != [[Q(value) for value in row] for row in records[index]["normalizer"]])
    reject("wrong_direction", "exact RIGHT matrix product",
           lambda: checked_product(list(reversed(ports[witness]["forward_word"])),
                                   [[Q(value) for value in row] for row in records[witness]["normalizer"]]))
    reject("odd_SCALE", "SCALE is a dyadic unit", lambda: right_product([["SCALE", 0, "3"]], 8))
    reject("source_drift", "source bytes: PORTS.json",
           lambda: authenticated("PORTS.json", raw["PORTS.json"] + b" "))
    active = placement(stages[0], 0, stages)
    spectator = min(set(range(127)) - set(active))
    reject("spectator_write", "spectator write or wrong row/lane",
           lambda: route_guard(address(0, 0, active[0], 0, 1), address(0, 0, spectator, 0, 1),
                               active, 0, 0, 0, 1))
    reject("raw_stage_used_as_ordinal", "stage ordinal binding", lambda: placement(3, 3, stages))
    histogram = {kind: dict(sorted(counts.items(), key=lambda item: Q(item[0])))
                 for kind, counts in histograms.items()}
    # Each coefficient receives its own named primitive cost. Both directions
    # are already included in histogram; two halves and 18 stage placements
    # multiply by 2*18*(127*f)*f. No unit-price replacement is made.
    bill = {kind: {coefficient: 4572 * count for coefficient, count in counts.items()}
            for kind, counts in histogram.items()}
    result = {
        "schema": "g20-normalizer-dyadic-words/1", "ports": ports,
        "source_raw_sha256": SOURCE_HASHES,
        "word_convention": "RIGHT product E1...Em=W; ADD[i,j,a]=I+a*e_i*e_j^T; row[j]+=a*row[i]",
        "ordered_shift": "source=half*N^2+row*N+active[i]*f+lane; target=half*N^2+row*N+active[j]*f+lane",
        "scale": "SCALE[i,u] scales the corresponding active[i] coordinate; u is a dyadic unit",
        "placements": [{"stage": stage, "ordinal": ordinal,
                         "active_indices": placement(stage, ordinal, stages)}
                        for ordinal, stage in enumerate(stages)],
        "layout_scope": "Chosen compatible 127-slot layout; not the retained literal physical head map",
        "sample_layout_checks": samples, "operation_histogram_both_directions": histogram,
        "operation_counts_both_directions": {kind: sum(counts.values()) for kind, counts in histogram.items()},
        "coefficient_height": {"maximum": max_height, "numerator_bits": max_numerator_bits,
                               "denominator_bits": max_denominator_bits},
        "named_primitive_counts_times_f_squared": bill,
        "parametric_bill": "sum over ADD/SCALE coefficients a of counts[a]*f^2*C_kind(a), with positive named primitive costs",
        "bill_scope": "Cartesian catalogue cross-product; not a bijection to retained paid route events or a full caller invoice",
        "call_cross_product_catalogue_count": 111 * 18 * 2 * 2,
        "multiplicity": {"address_halves": 2, "stages": 18, "row_count": "N=127*f",
                         "lanes": "f", "directions": "forward and inverse already counted"},
        "synthetic_nonunit_pivot": {"matrix": [["3", "1"], ["2", "1"]],
                                    "forward_word": synthetic_word, "inverse_word": synthetic_inverse},
        "failure_controls": controls, "wrong_direction_witness_port": witness,
        "remaining": "Full borrow/cache/carry/type commitments, padding, tape and physical ROW ABI implementation; no unit-price bound or supplier/native admission",
    }
    if not args.emit:
        need(canonical(result) == canonical(json.loads((HERE / "RESULT.json").read_text(encoding="utf-8"))),
             "frozen RESULT.json comparison")
    print(json.dumps(result, sort_keys=True, indent=2))
    print("PASS_G20_NORMALIZER_DYADIC_WORDS")


if __name__ == "__main__":
    main()
