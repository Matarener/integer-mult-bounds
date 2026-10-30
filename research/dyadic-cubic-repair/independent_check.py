#!/usr/bin/env python3
"""Independent finite audit of dyadic cubic repair, using exact polynomials.

Prepared by apoursh with substantial OpenAI Codex assistance. Apache-2.0.
The chronological interface and rational two-query criterion are credited to
Nick Petalas's PR6200 and its retained predecessors. This checker imports no
primary verifier and does not infer an all-arity theorem from a finite scan.
"""

import json
from fractions import Fraction
from math import gcd, isqrt


def require(condition, message):
    if not condition:
        raise ValueError(message)


# Sparse polynomials in three free variables: entry a, unchanged b, entry y.
ONE = {(0, 0, 0): Fraction(1)}
A = {(1, 0, 0): Fraction(1)}
B = {(0, 1, 0): Fraction(1)}
Y = {(0, 0, 1): Fraction(1)}
CUBIC_MONOMIALS = [(3, 0, 0), (2, 1, 0), (1, 2, 0), (0, 3, 0)]


def plus(left, right):
    answer = dict(left)
    for exponent, coefficient in right.items():
        answer[exponent] = answer.get(exponent, Fraction(0)) + coefficient
    return {exponent: coefficient for exponent, coefficient in answer.items() if coefficient}


def times_scalar(coefficient, polynomial):
    return {exponent: coefficient * value for exponent, value in polynomial.items()
            if coefficient * value}


def times(left, right):
    answer = {}
    for e, u in left.items():
        for f, v in right.items():
            exponent = tuple(x + y for x, y in zip(e, f, strict=True))
            answer[exponent] = answer.get(exponent, Fraction(0)) + u * v
    return {exponent: coefficient for exponent, coefficient in answer.items() if coefficient}


def power(polynomial, exponent):
    answer = ONE
    for _ in range(exponent):
        answer = times(answer, polynomial)
    return answer


def translate_a(polynomial, offset):
    source = plus(A, times_scalar(offset, B))
    answer = {}
    for exponent, coefficient in polynomial.items():
        term = times(times(power(source, exponent[0]), power(B, exponent[1])),
                     power(Y, exponent[2]))
        answer = plus(answer, times_scalar(coefficient, term))
    return answer


def chronological_state(arity):
    # Build sum_{j=0}^{r-1}(a+j*b)^3 by concatenating binary-sized blocks.
    # This executes the reader-before-shift chronology without Faulhaber formulas.
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
    require(offset == arity, "binary ladder consumed the exact arity")
    return {"a": plus(A, times_scalar(arity, B)), "b": B,
            "y": plus(Y, accumulated)}


def target_state(arity):
    return {"a": A, "b": B, "y": plus(Y, times_scalar(arity, power(A, 3)))}


def dyadic(value):
    denominator = Fraction(value).denominator
    return denominator & (denominator - 1) == 0


def execute(state, program, dyadic_only=True):
    state = dict(state)
    for instruction, coefficient in program:
        coefficient = Fraction(coefficient)
        require(not dyadic_only or dyadic(coefficient), "instruction coefficient is not dyadic")
        if instruction == "shift":
            state["a"] = plus(state["a"], times_scalar(coefficient, state["b"]))
        elif instruction == "source_cube":
            state["y"] = plus(state["y"], times_scalar(coefficient, power(state["a"], 3)))
        elif instruction == "b_cube":
            state["y"] = plus(state["y"], times_scalar(coefficient, power(state["b"], 3)))
        else:
            raise ValueError("unknown instruction")
    return state


def solve_weights(target, linear_forms):
    # Independent coefficient fitting by elimination, with all four equations.
    cubes = [power(form, 3) for form in linear_forms]
    rows = [[cube.get(monomial, Fraction(0)) for cube in cubes]
            + [target.get(monomial, Fraction(0))] for monomial in CUBIC_MONOMIALS]
    pivot_rows = []
    for column in range(len(cubes)):
        pivot = next((i for i in range(len(pivot_rows), len(rows)) if rows[i][column]), None)
        if pivot is None:
            return None
        index = len(pivot_rows)
        rows[index], rows[pivot] = rows[pivot], rows[index]
        divisor = rows[index][column]
        rows[index] = [value / divisor for value in rows[index]]
        for i in range(len(rows)):
            if i != index:
                coefficient = rows[i][column]
                rows[i] = [x - coefficient * y
                           for x, y in zip(rows[i], rows[index], strict=True)]
        pivot_rows.append(index)
    if any(all(value == 0 for value in row[:-1]) and row[-1] for row in rows):
        return None
    answer = [rows[index][-1] for index in pivot_rows]
    reconstructed = {}
    for coefficient, cube in zip(answer, cubes, strict=True):
        reconstructed = plus(reconstructed, times_scalar(coefficient, cube))
    require(reconstructed == target, "fitted cubes reproduce every polynomial coefficient")
    return answer


def form(slope):
    return plus(A, times_scalar(slope, B))


def compact(program):
    return [(operation, Fraction(coefficient)) for operation, coefficient in program if coefficient]


def four_program(arity, defect):
    weights = solve_weights(defect, [form(1), form(-1), A, B])
    require(weights is not None and all(value.denominator == 1 for value in weights),
            "universal four-form coefficients are integers")
    program = [("shift", 1 - arity), ("source_cube", -weights[0]),
               ("shift", -2), ("source_cube", -weights[1]),
               ("shift", 1), ("source_cube", -weights[2]), ("b_cube", -weights[3])]
    return compact(program), weights


def three_program(arity, defect):
    require(arity % 3 == 2, "three-form family arity")
    high, low = (arity + 1) // 3, (arity - 2) // 3
    weights = solve_weights(defect, [form(high), form(low), B])
    require(weights is not None and all(value.denominator == 1 for value in weights),
            "three-form coefficients are integers")
    program = [("shift", high - arity), ("source_cube", -weights[0]),
               ("shift", low - high), ("source_cube", -weights[1]),
               ("shift", -low), ("b_cube", -weights[2])]
    return compact(program), weights


def rational_root(value):
    numerator, denominator = value.numerator, value.denominator
    if numerator < 0:
        return None
    p, q = isqrt(numerator), isqrt(denominator)
    return Fraction(p, q) if p * p == numerator and q * q == denominator else None


def two_query_candidate(arity, defect):
    k = rational_root(Fraction(2 * arity * arity - 2 * arity - 1, 3))
    if k is None:
        return None
    n = 2 * arity - 1
    require(k.denominator == 1 and k.numerator % 2 == 1, "integral odd Pell parameter")
    k = k.numerator
    require(n * n - 6 * k * k == 3 and n % 3 == 0, "Pell equation and slope divisibility")
    high, low = (Fraction(n, 3) + k) / 2, (Fraction(n, 3) - k) / 2
    require(high.denominator == low.denominator == 1, "two normalized slopes are integers")
    weights = solve_weights(defect, [form(high), form(low)])
    require(weights is not None and weights[0] == -weights[1], "forced opposite weights")
    s1 = Fraction(defect[(2, 1, 0)], 3)
    require(s1.denominator == 1 and gcd(k, s1.numerator) == 1, "Pell weight coprimality")
    require(weights[0] == s1 / k and weights[0].denominator == k, "forced reduced denominator")
    program = compact([("shift", high - arity), ("source_cube", -weights[0]),
                       ("shift", low - high), ("source_cube", -weights[1]), ("shift", -low)])
    return {"k": k, "weights": weights, "program": program}


def inspect_arity(arity):
    chronological, target = chronological_state(arity), target_state(arity)
    defect = plus(chronological["y"], times_scalar(-1, target["y"]))
    s1, s2 = arity * (arity - 1) // 2, arity * (arity - 1) * (2 * arity - 1) // 6
    expected = {(2, 1, 0): Fraction(3 * s1), (1, 2, 0): Fraction(3 * s2),
                (0, 3, 0): Fraction(s1 * s1)}
    require(defect == expected, "literal ladder agrees with cited defect")
    require((3, 0, 0) not in defect and defect[(2, 1, 0)] != 0,
            "one-cube coefficient obstruction at this arity")
    program, weights = four_program(arity, defect)
    require(execute(chronological, program) == target, "universal four schedule restores a,b,y")
    require(weights == [Fraction(s1 + s2, 2), Fraction(s2 - s1, 2), -s2, s1 * s1 - s1],
            "independently fitted universal coefficients")
    require((s1 - s2) % 2 == 0, "integer parity improvement over merely dyadic coefficients")
    candidate = two_query_candidate(arity, defect)
    two_dyadic = False
    if candidate is not None:
        require(execute(chronological, candidate["program"], False) == target,
                "rational two-cube schedule restores all outputs")
        two_dyadic = all(dyadic(value) for value in candidate["weights"])
        require(two_dyadic == (arity == 2), "dyadic two-query eligibility on checked arities")
    three_count = None
    if arity % 3 == 2:
        program, weights = three_program(arity, defect)
        require(execute(chronological, program) == target, "integer three-form schedule restores all outputs")
        three_count = sum(operation.endswith("cube") for operation, _ in program)
        require(three_count == (2 if arity == 2 else 3), "nonzero query count")
        require(arity == 2 or not two_dyadic, "three-query optimality corroboration")
    return {"rational_two": candidate is not None, "dyadic_two": two_dyadic,
            "three_family": three_count is not None, "three_query": three_count == 3}


def exceptional_three_examples():
    programs = {
        3: [("shift", -1), ("source_cube", -1),
            ("shift", -1), ("source_cube", -1),
            ("shift", -1), ("source_cube", 2)],
        4: [("source_cube", Fraction(-1, 4)), ("shift", -2),
            ("source_cube", Fraction(-5, 2)), ("shift", -2),
            ("source_cube", Fraction(11, 4))],
    }
    for arity, program in programs.items():
        require(sum(operation == "source_cube" for operation, _ in program) == 3,
                "exceptional example uses exactly three cube queries")
        require(execute(chronological_state(arity), program) == target_state(arity),
                "exceptional three-query schedule restores the entire arbitrary-input state")
    return sorted(programs)


def controls():
    arity = 14
    initial, target = chronological_state(arity), target_state(arity)
    program = [("shift", -9), ("source_cube", -91), ("shift", -1),
               ("source_cube", 91), ("shift", -4), ("b_cube", -2730)]
    require(execute(initial, program) == target, "literal r14 integer program")
    no_restore = execute(initial, program[:4] + program[5:])
    require(no_restore["y"] == target["y"] and no_restore["a"] != A and no_restore["b"] == B,
            "missing source restoration remains observable despite correct accumulator")
    wrong_sign = list(program)
    wrong_sign[1] = ("source_cube", 91)
    require(execute(initial, wrong_sign)["y"] != target["y"], "wrong cube sign is detected")
    defect = plus(initial["y"], times_scalar(-1, target["y"]))
    rational = two_query_candidate(arity, defect)
    require(rational["weights"][0] == Fraction(91, 11), "r14 forbidden prime fixture")
    try:
        execute(initial, rational["program"])
    except ValueError as error:
        require(str(error) == "instruction coefficient is not dyadic", "precise coefficient rejection")
    else:
        raise ValueError("forbidden 91/11 rational repair accepted as dyadic")
    gamma, alpha, beta = Fraction(91, 88), Fraction(2), Fraction(20)
    physical = times_scalar(gamma, power(plus(times_scalar(alpha, A), times_scalar(beta, B)), 3))
    normalized = times_scalar(Fraction(91, 11), power(form(10), 3))
    require(physical == normalized, "nonmonic rescaling preserves the forbidden normalized weight")
    require(dyadic(alpha) and dyadic(beta) and not dyadic(gamma)
            and gamma * alpha ** 3 == Fraction(91, 11), "scaled query does not hide the odd prime")
    return ["missing_final_source_restore", "wrong_cube_sign", "forbidden_91_over_11",
            "nonmonic_91_over_88_hidden_denominator"]


def main():
    pell_arities = []
    n, k = 3, 1
    for _ in range(8):
        require(n * n - 6 * k * k == 3, "generated Pell fixture")
        pell_arities.append((n + 1) // 2)
        n, k = 5 * n + 12 * k, 2 * n + 5 * k
    large_arities = [10 ** 6, 10 ** 12 + 1, 2 ** 128 + 1]
    arities = sorted(set(range(2, 129)) | set(pell_arities) | set(large_arities))
    results = {arity: inspect_arity(arity) for arity in arities}
    exceptional = exceptional_three_examples()
    rejected = controls()
    summary = {"status": "finite independent exact polynomial evidence",
               "arity_count": len(arities), "consecutive_arities": "2..128",
               "pell_arities": pell_arities, "large_arities": large_arities,
               "whole_state_four_form_replays": len(results),
               "whole_state_three_family_replays": sum(item["three_family"] for item in results.values()),
               "exact_three_family_cases": sum(item["three_query"] for item in results.values()),
               "exceptional_three_examples": exceptional,
               "rational_two_candidate_replays": sum(item["rational_two"] for item in results.values()),
               "dyadic_two_arities_checked": [arity for arity, item in results.items() if item["dyadic_two"]],
               "controls": rejected, "control_count": len(rejected),
               "formal_kernel_or_all_arity_scan_proof": False}
    print(json.dumps(summary, sort_keys=True))
    print("PASS_INDEPENDENT_DYADIC_CUBIC_REPAIR")


if __name__ == "__main__":
    main()
