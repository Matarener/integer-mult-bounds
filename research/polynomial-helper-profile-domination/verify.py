"""Exact finite corroboration; --record writes a generated receipt outside package."""
import argparse
import hashlib
import json
from dataclasses import replace
from fractions import Fraction as Q
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from compiler import Gate, Program, evaluate, inverse, linearize, profile, require, validate

MAX_TERMS = 512
MAX_TOTAL_DEGREE = 16
SOURCE_FILES = ("README.md", "PROOF.md", "compiler.py", "verify.py", "TASK.json",
                "SOURCES.json", "VERIFY.json")


def scale(poly, coefficient):
    return {m: c * coefficient for m, c in poly.items() if c * coefficient}


def add(left, right):
    require(len(left) <= MAX_TERMS and len(right) <= MAX_TERMS, "term input limit")
    result = dict(left)
    for monomial, coefficient in right.items():
        value = result.get(monomial, Q(0)) + coefficient
        if value:
            result[monomial] = value
        else:
            result.pop(monomial, None)
    require(len(result) <= MAX_TERMS, "term output limit")
    return result


def multiply(left, right):
    require(len(left) <= MAX_TERMS and len(right) <= MAX_TERMS, "product input limit")
    result = {}
    for a, x in left.items():
        for b, y in right.items():
            monomial = tuple(i + j for i, j in zip(a, b))
            require(sum(monomial) <= MAX_TOTAL_DEGREE, "symbolic degree limit")
            result[monomial] = result.get(monomial, Q(0)) + x * y
            require(len(result) <= MAX_TERMS, "product term limit")
    return {m: c for m, c in result.items() if c}


def substitution(poly, coefficients, variables):
    one = {(0,) * variables: Q(1)}
    power = one
    result = {}
    for exponent, coefficient in enumerate(coefficients):
        if exponent:
            power = multiply(power, poly)
        result = add(result, scale(power, coefficient))
    return result


def symbolic(program, clean=()):
    validate(program)
    variables = program.roles * program.width
    initial = [{tuple(int(i == j) for i in range(variables)): Q(1)}
               if j // program.width not in clean else {}
               for j in range(variables)]
    state = list(initial)
    for gate in program.gates:
        start = gate.source * program.width
        source = state[start:start + program.width]
        if gate.placement == "before":
            source = [substitution(p, gate.polynomial, variables) for p in source]
        increment = []
        for row in gate.operator:
            value = {}
            for coefficient, poly in zip(row, source):
                value = add(value, scale(poly, coefficient))
            increment.append(value)
        if gate.placement == "after":
            increment = [substitution(p, gate.polynomial, variables) for p in increment]
        for i, value in enumerate(increment):
            index = gate.target * program.width + i
            state[index] = add(state[index], value)
    return initial, state


def linear_part(state):
    return [{m: c for m, c in poly.items() if sum(m) == 1} for poly in state]


def dual_run(program, direction):
    """Independent nilpotent arithmetic; no symbolic or extraction routines."""
    state = [(Q(0), c) for c in direction]
    for gate in program.gates:
        start = gate.source * program.width
        values = state[start:start + program.width]
        if gate.placement == "before":
            values = [dual_polynomial(gate.polynomial, v) for v in values]
        image = [(sum((a * v[0] for a, v in zip(row, values)), Q(0)),
                  sum((a * v[1] for a, v in zip(row, values)), Q(0)))
                 for row in gate.operator]
        if gate.placement == "after":
            image = [dual_polynomial(gate.polynomial, v) for v in image]
        for i, value in enumerate(image):
            index = gate.target * program.width + i
            old = state[index]
            state[index] = (old[0] + value[0], old[1] + value[1])
    require(all(value == 0 for value, _ in state), "zero trajectory invariant")
    return tuple(tangent for _, tangent in state)


def dual_polynomial(coefficients, value):
    answer = (Q(0), Q(0))
    for coefficient in reversed(coefficients):
        a, b = answer
        c, d = value
        answer = (a * c + coefficient, a * d + b * c)
    return answer


def operator(rows):
    return tuple(tuple(Q(c) for c in row) for row in rows)


def fixtures():
    operators = (operator(((1,),)), operator(((1, 1), (1, -1))),
                 operator(((0, Q(1, 2)), (1, 0))),
                 operator(((1, 2), (0, 0))))
    cases = []
    for matrix in operators:
        for placement in ("before", "after"):
            for a in (Q(-1), Q(0), Q(1, 2), Q(1)):
                for tail in ((Q(1),), (Q(-1), Q(1)), (Q(0), Q(1), Q(2))):
                    p = (Q(0), a) + tail
                    q = (Q(0), Q(1) - a) + tuple(-c for c in tail)
                    gates = (Gate(0, 1, matrix, p, placement, "paid"),
                             Gate(0, 1, matrix, q, placement, "paid"))
                    expected = Program(2, len(matrix),
                                       (replace(gates[0], polynomial=(Q(0), Q(1))),))
                    cases.append(("pair", Program(2, len(matrix), gates), expected, ()))
    for matrix in operators:
        for placement in ("before", "after"):
            for a in (Q(0), Q(1, 2), Q(-1)):
                cases.append(echo_fixture(matrix, placement, a, ()))
                cases.append(echo_fixture(matrix, placement, a, (1,)))
    require(len(cases) == 144, "fixture family count")
    return cases


def echo_fixture(matrix, placement, a, clean):
    width = len(matrix)
    identity = operator(tuple(tuple(int(i == j) for j in range(width))
                              for i in range(width)))
    p = (Q(0), a, Q(1), Q(-1))
    u = Gate(0, 1, matrix, p, placement, "T")
    v = Gate(1, 2, identity, (Q(0), Q(1)), "after", "read")
    gates = (u, v, replace(u, polynomial=tuple(-c for c in p)),
             replace(v, polynomial=(Q(0), Q(-1))),
             Gate(0, 2, matrix, (Q(0), Q(0), Q(-1), Q(1)), placement, "T"))
    expected = Program(3, width, (Gate(0, 2, matrix, (Q(0), a),
                                      placement, "T"),))
    return "echo", Program(3, width, gates), expected, clean


def check_fixture(program, expected, clean):
    initial, full = symbolic(program, clean)
    _, target = symbolic(expected, clean)
    require(full == target, "claimed linear endpoint is false")
    extracted = linearize(program)
    _, tangent = symbolic(extracted, clean)
    require(tangent == target == linear_part(full), "extracted endpoint")
    before, after = profile(program), profile(extracted)
    require(all(count <= before.get(label, 0) for label, count in after.items()),
            "profile increased")
    double = Program(program.roles, program.width, program.gates + inverse(program).gates)
    require(symbolic(double, clean)[1] == initial, "arbitrary-dirt inverse")
    n = program.roles * program.width
    directions = [tuple(Q(int(i == j)) for i in range(n)) for j in range(n)]
    directions += [tuple(Q((i + shift) % 3 - 1) for i in range(n))
                   for shift in range(3)]
    for vector in directions:
        vector = tuple(Q(0) if i // program.width in clean else v
                       for i, v in enumerate(vector))
        require(dual_run(program, vector) == evaluate(extracted, vector),
                "independent dual-number extraction")
        require(evaluate(program, vector) == evaluate(expected, vector),
                "literal arbitrary-input evaluation")
    return len(directions)


def controls():
    matrix = operator(((1,),))
    base = Gate(0, 1, matrix, (Q(0), Q(1), Q(1)), "after", "paid")
    mutants = (replace(base, source=1), replace(base, source=-1),
               replace(base, polynomial=(Q(1), Q(1))),
               replace(base, polynomial=(Q(0),) * 6),
               replace(base, operator=()), replace(base, placement="somewhere"),
               replace(base, label=""), replace(base, polynomial=(Q(0), Q(1025))))
    rejected = 0
    for gate in mutants:
        try:
            linearize(Program(2, 1, (gate,)))
        except ValueError:
            rejected += 1
    require(rejected == len(mutants), "invalid gate accepted")
    nonlinear = Program(2, 1, (base,))
    full = symbolic(nonlinear)[1]
    require(full != symbolic(linearize(nonlinear))[1], "endpoint premise lost")
    trap = Program(2, 1, (replace(base, polynomial=(Q(0), Q(-1), Q(1))),))
    for value in ((Q(0), Q(0)), (Q(1), Q(0)), (Q(0), Q(1))):
        require(evaluate(trap, value) == value, "basis trap fixture")
    require(evaluate(trap, (Q(2), Q(0))) != (Q(2), Q(0)), "basis-only trap lost")
    require(linearize(Program(2, 1, (replace(base, polynomial=(Q(0), Q(0), Q(1))),)))
            .gates == (), "zero derivative not deleted")
    require(all((x * x) % 2 == x for x in range(2)), "finite-field boundary")
    for x in range(-3, 4):
        require((x + 1) ** 2 - x ** 2 - 1 == 2 * x,
                "linear endpoint with nonzero-constant trajectory")
    mixing = operator(((1, 1), (0, 1)))
    square = Gate(0, 1, mixing, (Q(0), Q(0), Q(1)), "after", "T")
    require(evaluate(Program(2, 2, (square,)), (Q(1), Q(1), Q(0), Q(0)))
            == (Q(1), Q(1), Q(4), Q(1)), "polynomial after operator")
    require(evaluate(Program(2, 2, (replace(square, placement="before"),)),
                     (Q(1), Q(1), Q(0), Q(0)))
            == (Q(1), Q(1), Q(2), Q(1)), "polynomial before operator")
    # A noncommuting two-block fixture checks source changes between blocks.
    a = echo_fixture(operator(((1, 1), (0, 1))), "after", Q(1), ())
    b = echo_fixture(operator(((0, 1), (1, 0))), "before", Q(1), ())
    remapped = tuple(replace(g, source=2 - g.source, target=2 - g.target)
                     for g in b[1].gates)
    expected_b = tuple(replace(g, source=2 - g.source, target=2 - g.target)
                       for g in b[2].gates)
    combined = Program(3, 2, a[1].gates + remapped)
    expected = Program(3, 2, a[2].gates + expected_b)
    return rejected + 6, check_fixture(combined, expected, ())


def report():
    dual_cases = 0
    cases = fixtures()
    for _, program, expected, clean in cases:
        dual_cases += check_fixture(program, expected, clean)
    rejected, extra = controls()
    hashes = {}
    for name in SOURCE_FILES:
        path = ROOT / name
        require(path.stat().st_size <= 4 * 1024 * 1024, "source size limit")
        hashes[name] = hashlib.sha256(path.read_bytes()).hexdigest()
    sample = echo_fixture(operator(((1, 1), (0, 1))), "after", Q(1), ())
    return {"status": "PASS_POLYNOMIAL_HELPER_PROFILE_DOMINATION",
            "claim_type": "scoped proof with finite exact corroboration",
            "linear_endpoint_fixtures": len(cases) + 1,
            "dual_and_numeric_directions_each": dual_cases + extra,
            "controls": rejected,
            "dirty_echo_profile": {"before": profile(sample[1]),
                                    "after": profile(linearize(sample[1]))},
            "source_sha256": hashes}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--record", type=Path)
    args = parser.parse_args()
    result = report()
    if args.record:
        destination = args.record.resolve()
        require(not destination.is_relative_to(ROOT), "record outside package")
        with destination.open("x", encoding="utf-8") as stream:
            stream.write(json.dumps(result, indent=2, sort_keys=True) + "\n")
    else:
        path = ROOT / "RESULT.json"
        require(path.stat().st_size <= 1024 * 1024, "receipt size limit")
        require(result == json.loads(path.read_text()), "receipt mismatch")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
