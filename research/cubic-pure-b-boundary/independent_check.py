#!/usr/bin/env python3
"""Independent quotient-ring and symbolic-state audit of the pure-b boundary.

Prepared by apoursh with substantial OpenAI Codex assistance. Apache-2.0.
Retains Nick Petalas's chronological interface and the predecessor credits
recorded in README.md. No imports from the primary checker; no file writes.
"""

import itertools
import json
from fractions import Fraction


def need(condition, message):
    if not condition:
        raise ValueError(message)


# Free entry variables (a,b,y), represented by sparse exact polynomials.
ONE = {(0, 0, 0): Fraction(1)}
A = {(1, 0, 0): Fraction(1)}
B = {(0, 1, 0): Fraction(1)}
Y = {(0, 0, 1): Fraction(1)}
CUBICS = [(3, 0, 0), (2, 1, 0), (1, 2, 0), (0, 3, 0)]
LOW_RESIDUES = {3, 4, 6, 7}


def plus(left, right):
    answer = dict(left)
    for exponent, coefficient in right.items():
        answer[exponent] = answer.get(exponent, Fraction(0)) + coefficient
    return {exponent: coefficient for exponent, coefficient in answer.items() if coefficient}


def scaled(coefficient, polynomial):
    return {exponent: coefficient * value for exponent, value in polynomial.items()
            if coefficient * value}


def times(left, right):
    answer = {}
    for left_power, left_value in left.items():
        for right_power, right_value in right.items():
            exponent = tuple(x + y for x, y in zip(left_power, right_power, strict=True))
            answer[exponent] = answer.get(exponent, Fraction(0)) + left_value * right_value
    return {exponent: coefficient for exponent, coefficient in answer.items() if coefficient}


def power(polynomial, exponent):
    answer = ONE
    for _ in range(exponent):
        answer = times(answer, polynomial)
    return answer


def line(slope):
    return plus(A, scaled(slope, B))


def translate_a(polynomial, offset):
    answer = {}
    for exponent, coefficient in polynomial.items():
        term = times(times(power(line(offset), exponent[0]), power(B, exponent[1])),
                     power(Y, exponent[2]))
        answer = plus(answer, scaled(coefficient, term))
    return answer


def entry_after_ladder(arity):
    # Concatenate literal reader-before-shift blocks by binary doubling.
    # No closed-form sums or primary fixed-coefficient routines are used.
    remaining, width, offset = arity, 1, 0
    block, accumulated = power(A, 3), {}
    while remaining:
        if remaining & 1:
            accumulated = plus(accumulated, translate_a(block, offset))
            offset += width
        remaining //= 2
        if remaining:
            block = plus(block, translate_a(block, width))
            width *= 2
    need(offset == arity, "literal ladder consumes its exact arity")
    return {"a": line(arity), "b": B, "y": plus(Y, accumulated)}


def desired_state(arity):
    return {"a": A, "b": B, "y": plus(Y, scaled(arity, power(A, 3)))}


def defect_for(arity):
    initial = entry_after_ladder(arity)
    desired = desired_state(arity)
    return plus(initial["y"], scaled(-1, desired["y"]))


def dyadic(value):
    denominator = Fraction(value).denominator
    return denominator & (denominator - 1) == 0


def dyadic_unit(value):
    value = Fraction(value)
    numerator = abs(value.numerator)
    return dyadic(value) and numerator > 0 and numerator & (numerator - 1) == 0


def inverse_frame(matrix):
    a, b, c, d = matrix
    determinant = a * d - b * c
    need(dyadic_unit(determinant), "source frame determinant must be a dyadic unit")
    return tuple(Fraction(value, determinant) for value in (d, -b, -c, a))


def entry_b_line(polynomial):
    return set(polynomial) == {(0, 1, 0)} and polynomial[(0, 1, 0)] != 0


def execute(initial, program):
    state = dict(initial)
    reads = pure_b_reads = shifts = frames = 0
    for operation, argument in program:
        if operation == "frame":
            a, b, c, d = map(Fraction, argument)
            need(all(dyadic(value) for value in (a, b, c, d)), "dyadic frame entries")
            need(dyadic_unit(a * d - b * c), "source frame determinant must be a dyadic unit")
            old_a, old_b = state["a"], state["b"]
            state["a"] = plus(scaled(a, old_a), scaled(b, old_b))
            state["b"] = plus(scaled(c, old_a), scaled(d, old_b))
            frames += 1
            continue
        coefficient = Fraction(argument)
        need(dyadic(coefficient), "dyadic shear or query coefficient")
        if operation == "shift":
            state["a"] = plus(state["a"], scaled(coefficient, state["b"]))
            shifts += 1
        elif operation in {"read_a", "read_b"}:
            source = state["a"] if operation == "read_a" else state["b"]
            state["y"] = plus(state["y"], scaled(coefficient, power(source, 3)))
            if coefficient:
                reads += 1
                pure_b_reads += int(entry_b_line(source))
        else:
            raise ValueError("unknown instruction")
    return state, {"queries": reads, "entry_b_queries": pure_b_reads,
                   "shears": shifts, "frames": frames}


def fit_weights(defect, forms):
    cubes = [power(form, 3) for form in forms]
    rows = [[cube.get(monomial, Fraction(0)) for cube in cubes]
            + [defect.get(monomial, Fraction(0))] for monomial in CUBICS]
    pivots = []
    for column in range(len(cubes)):
        pivot = next((i for i in range(len(pivots), len(rows)) if rows[i][column]), None)
        need(pivot is not None, "independent query forms")
        index = len(pivots)
        rows[index], rows[pivot] = rows[pivot], rows[index]
        divisor = rows[index][column]
        rows[index] = [value / divisor for value in rows[index]]
        for i in range(len(rows)):
            if i != index:
                coefficient = rows[i][column]
                rows[i] = [x - coefficient * y
                           for x, y in zip(rows[i], rows[index], strict=True)]
        pivots.append(index)
    need(not any(all(value == 0 for value in row[:-1]) and row[-1] for row in rows),
         "all four cubic equations are consistent")
    weights = [rows[index][-1] for index in pivots]
    reconstructed = {}
    for weight, cube in zip(weights, cubes, strict=True):
        reconstructed = plus(reconstructed, scaled(weight, cube))
    need(reconstructed == defect, "independently fitted full cubic identity")
    need(all(weight.denominator == 1 and weight != 0 for weight in weights),
         "all displayed query weights are nonzero integers")
    return weights


def restoration_program(arity, defect):
    if arity % 3 == 2:
        high, low = (arity + 1) // 3, (arity - 2) // 3
        weights = fit_weights(defect, [line(high), line(low), B])
        return [("shift", high - arity), ("read_a", -weights[0]),
                ("shift", low - high), ("read_a", -weights[1]),
                ("shift", -low), ("read_b", -weights[2])], "old_three"
    if arity % 9 in {0, 1}:
        epsilon = -1 if arity % 9 == 0 else 1
        q = arity // 3
        primitive = plus(scaled(3, A), scaled(3 * q + epsilon, B))
        weights = fit_weights(defect, [line(q), primitive, B])
        matrix = (3, epsilon, 1, 0)
        return [("shift", q - arity), ("read_a", -weights[0]),
                ("frame", matrix), ("read_a", -weights[1]),
                ("frame", inverse_frame(matrix)), ("shift", -q),
                ("read_b", -weights[2])], "nonmonic_three"
    weights = fit_weights(defect, [line(1), line(-1), A, B])
    return [("shift", 1 - arity), ("read_a", -weights[0]),
            ("shift", -2), ("read_a", -weights[1]),
            ("shift", 1), ("read_a", -weights[2]), ("read_b", -weights[3])], "four"


def quotient_ring_certificate():
    modulus = 9
    tensors = set()
    parameter_count = 0
    for gamma, alpha, beta in itertools.product(range(modulus), repeat=3):
        tensors.add((gamma * alpha ** 3 % modulus, 3 * gamma * alpha ** 2 * beta % modulus,
                     3 * gamma * alpha * beta ** 2 % modulus, gamma * beta ** 3 % modulus))
        parameter_count += 1
    projections = {tensor[:3] for tensor in tensors}
    pair_sums = {tuple((x + y) % modulus for x, y in zip(left, right, strict=True))
                 for left in projections for right in projections}
    need(parameter_count == 729 and len(tensors) == 33 and len(projections) == 21,
         "complete physical-coefficient residue enumeration")
    need(len(pair_sums) == 57, "all projected two-cube sums")
    need(not any(first == second == 0 and third != 0 for first, second, third in pair_sums),
         "two cubes cannot have only a nonzero ab-squared projected coefficient")
    excluded, targets = [], {}
    for residue in range(modulus):
        defect = defect_for(residue + modulus)
        target = tuple(defect.get(monomial, Fraction(0)) for monomial in CUBICS[:3])
        need(all(coefficient.denominator == 1 for coefficient in target), "integral quotient-ring target")
        projected = tuple(coefficient.numerator % modulus for coefficient in target)
        targets[str(residue)] = projected
        if projected not in pair_sums:
            excluded.append(residue)
    need(set(excluded) == LOW_RESIDUES, "exact pure-b obstruction residue classes")
    return {"modulus": modulus, "physical_parameter_triples": parameter_count,
            "weighted_cube_tensors": len(tensors), "projected_tensors": len(projections),
            "ordered_projected_pairs": len(projections) ** 2, "distinct_pair_sums": len(pair_sums),
            "excluded_residues": excluded, "target_projections": targets}


def verify_arity(arity):
    defect = defect_for(arity)
    need(defect.get((3, 0, 0), 0) == 0 and defect[(2, 1, 0)] != 0,
         "one mixed cube plus pure-b reads cannot supply the coefficient pattern")
    program, family = restoration_program(arity, defect)
    final, counts = execute(entry_after_ladder(arity), program)
    need(final == desired_state(arity), "full arbitrary-input source and accumulator restoration")
    expected = 4 if arity % 9 in LOW_RESIDUES else 3
    need(counts["queries"] == expected and counts["entry_b_queries"] >= 1,
         "nonzero entry-b read and stated query count")
    if family == "nonmonic_three":
        need(counts["frames"] == 2 and counts["shears"] == 2, "declared nonmonic source-frame schedule")
    return family


def controls():
    arity = 10
    initial, desired = entry_after_ladder(arity), desired_state(arity)
    program, family = restoration_program(arity, defect_for(arity))
    need(family == "nonmonic_three", "nonmonic mutation fixture")
    no_restore, _ = execute(initial, program[:5] + program[6:])
    need(no_restore["y"] == desired["y"] and no_restore["a"] != A,
         "a correct accumulator cannot mask an unrestored source")
    early_b = program[:4] + [program[-1]] + program[4:-1]
    wrong_source, counts = execute(initial, early_b)
    need(wrong_source["a"] == A and wrong_source["b"] == B
         and wrong_source["y"] != desired["y"] and counts["entry_b_queries"] == 0,
         "temporary second slot is not the entry-b line")
    wrong_sign = list(program)
    wrong_sign[1] = ("read_a", -wrong_sign[1][1])
    need(execute(initial, wrong_sign)[0]["y"] != desired["y"], "wrong query sign is observable")
    try:
        execute(initial, [("frame", (3, 0, 0, 1))])
    except ValueError as error:
        need(str(error) == "source frame determinant must be a dyadic unit", "specific nonunit-frame rejection")
    else:
        raise ValueError("a frame requiring division by three was accepted")
    unrestricted = [("shift", -1), ("read_a", -1), ("shift", -1),
                    ("read_a", -1), ("shift", -1), ("read_a", 2)]
    final, counts = execute(entry_after_ladder(3), unrestricted)
    need(final == desired_state(3) and counts["queries"] == 3 and counts["entry_b_queries"] == 0,
         "r3 has an unrestricted three-query repair outside the pure-b contract")
    return {"negative": ["missing_source_restore", "reading_temporary_b_slot",
                         "wrong_query_sign", "nonunit_source_frame"],
            "positive_scope": ["r3_three_queries_without_entry_b_read"]}


def main():
    quotient = quotient_ring_certificate()
    large_arities = [9 * 2 ** 80 + residue for residue in range(9)]
    arities = sorted(set(range(3, 129)) | set(large_arities))
    families = {"old_three": 0, "nonmonic_three": 0, "four": 0}
    for arity in arities:
        families[verify_arity(arity)] += 1
    control_results = controls()
    result = {"claim_type": "exact finite quotient-ring certificate and symbolic schedule checks",
              "quotient_ring": quotient, "consecutive_arities": "3..128",
              "large_arities": large_arities, "whole_state_schedule_checks": len(arities),
              "schedule_families": families, "negative_controls": len(control_results["negative"]),
              "positive_scope_controls": len(control_results["positive_scope"]),
              "controls": control_results, "formal_kernel_or_full_supplier_proof": False}
    print(json.dumps(result, sort_keys=True))
    print("PASS_INDEPENDENT_CUBIC_PURE_B_BOUNDARY")


if __name__ == "__main__":
    main()
