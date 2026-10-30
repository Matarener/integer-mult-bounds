"""Compact typed free-operator certificates. Apache-2.0; Nick Petalas.

Extends zxv's PR5235 dependency-state construction to rectangular maps.
The compiler is shared with the checker and belongs to the trusted surface.
"""

import argparse
from fractions import Fraction as Q
import json
from pathlib import Path


def require(condition, message):
    if not condition:
        raise ValueError(message)


def scalar(value, certificate=False):
    require(type(value) in (int, str), "scalar must be an integer or fraction string")
    require(len(str(value)) <= (4096 if certificate else 160), "scalar encoding too long")
    require("." not in str(value) and "e" not in str(value).lower(), "use explicit fractions")
    result = Q(value)
    require(max(abs(result.numerator).bit_length(), result.denominator.bit_length()) <=
            (8192 if certificate else 512),
            "scalar too large")
    return result


def validate(problem):
    require(type(problem) is dict, "problem must be an object")
    require(set(problem) == {"roles", "arrows", "left", "right"}, "unexpected problem keys")
    roles, arrows = problem["roles"], problem["arrows"]
    require(type(roles) is list and 1 <= len(roles) <= 16, "role count must be 1..16")
    require(all(type(t) is str and 1 <= len(t) <= 32 for t in roles), "invalid role type")
    require(len(set(roles)) <= 8, "at most eight types")
    require(type(arrows) is dict and len(arrows) <= 16, "at most sixteen arrows")
    for name, ends in arrows.items():
        require(type(name) is str and 1 <= len(name) <= 32, "invalid arrow name")
        require(type(ends) is list and len(ends) == 2 and all(t in roles for t in ends),
                "arrow endpoints must be declared role types")
    for side in ("left", "right"):
        program = problem[side]
        require(type(program) is list and len(program) <= 128, "at most 128 instructions per side")
        for ins in program:
            validate_instruction(ins, roles, arrows)
    return problem


def validate_instruction(ins, roles, arrows):
    require(type(ins) is dict and "op" in ins, "instruction must have an op")
    op = ins["op"]
    keys = {"add": {"op", "src", "dst", "c"}, "scale": {"op", "dst", "c"},
            "swap": {"op", "src", "dst"}, "query": {"op", "src", "dst", "arrow", "c"},
            "apply": {"op", "dst", "arrow"}}
    require(type(op) is str and op in keys and set(ins) == keys[op], "invalid instruction keys")
    for key in ("src", "dst"):
        if key in ins:
            require(type(ins[key]) is int and 0 <= ins[key] < len(roles), "invalid register")
    if "c" in ins:
        scalar(ins["c"])
    if op in ("add", "swap"):
        require(roles[ins["src"]] == roles[ins["dst"]], "scalar operation crosses types")
    if op in ("query", "apply"):
        require(type(ins["arrow"]) is str and ins["arrow"] in arrows, "unknown arrow")
        src = ins.get("src", ins["dst"])
        require(arrows[ins["arrow"]] == [roles[src], roles[ins["dst"]]], "ill-typed arrow")


def combine(x, y, c=Q(1)):
    return [a + c * b for a, b in zip(x, y, strict=True)]


def compile_side(problem, side):
    r = len(problem["roles"])
    n = r + sum(ins["op"] in ("query", "apply") for ins in problem[side])
    registers = [[Q(i == j) for j in range(n)] for i in range(r)]
    atoms = list(problem["roles"])
    transitions = {a: [] for a in problem["arrows"]}
    cursor = r
    for ins in problem[side]:
        op, dst = ins["op"], ins["dst"]
        if op == "add":
            registers[dst] = combine(registers[dst], registers[ins["src"]], scalar(ins["c"]))
        elif op == "scale":
            registers[dst] = [scalar(ins["c"]) * v for v in registers[dst]]
        elif op == "swap":
            src = ins["src"]
            registers[src], registers[dst] = registers[dst], registers[src]
        else:
            source = ins.get("src", dst)
            transitions[ins["arrow"]].append((cursor, registers[source][:]))
            atoms.append(problem["roles"][dst])
            unit = [Q(j == cursor) for j in range(n)]
            registers[dst] = unit if op == "apply" else combine(registers[dst], unit, scalar(ins["c"]))
            cursor += 1
    assert cursor == n and len(atoms) == n
    return registers, transitions, atoms


def compile_problem(problem):
    validate(problem)
    u, t, types_left = compile_side(problem, "left")
    v, s, types_right = compile_side(problem, "right")
    n, m = len(types_left), len(types_right)
    output = [x + [-a for a in y] for x, y in zip(u, v, strict=True)]
    transitions = {}
    for arrow in t:
        transitions[arrow] = [(j, row + [Q(0)] * m) for j, row in t[arrow]]
        transitions[arrow] += [(n + j, [Q(0)] * n + row) for j, row in s[arrow]]
    return {"output": output, "transitions": transitions, "types": types_left + types_right,
            "right_offset": n, "roles": problem["roles"], "arrows": problem["arrows"]}


def advance(model, row, arrow):
    result = [Q(0)] * len(row)
    for j, dependency in model["transitions"][arrow]:
        if row[j]:
            result = combine(result, dependency, row[j])
    return result


def projection(model, row):
    offset = model["right_offset"]
    return [row[i] + row[offset + i] for i in range(len(model["roles"]))]


def path_row(model, output, word):
    require(type(output) is int and 0 <= output < len(model["roles"]), "invalid output")
    require(type(word) is list and len(word) < len(model["types"]), "invalid path length")
    row = model["output"][output][:]
    current = model["roles"][output]
    for arrow in word:
        require(type(arrow) is str and arrow in model["arrows"], "unknown path arrow")
        source, target = model["arrows"][arrow]
        require(current == target, "noncomposable certificate path")
        row = advance(model, row, arrow)
        current = source
    return row, current


def reduce_row(row, echelon):
    rest = row[:]
    coefficients = [Q(0)] * len(row)
    for pivot, normal, coordinates in echelon:
        c = rest[pivot]
        if c:
            rest = combine(rest, normal, -c)
            coefficients = combine(coefficients, coordinates, c)
    return rest, coefficients


def extend_basis(row, description, basis, paths, echelon):
    rest, coefficients = reduce_row(row, echelon)
    if not any(rest):
        return
    pivot = next(i for i, v in enumerate(rest) if v)
    gain = rest[pivot]
    normal = [v / gain for v in rest]
    coordinates = [-v / gain for v in coefficients]
    coordinates[len(basis)] += 1 / gain
    echelon.append((pivot, normal, coordinates))
    basis.append(row)
    paths.append(description)


def coordinates(row, echelon, size):
    rest, result = reduce_row(row, echelon)
    require(not any(rest), "closure construction failed")
    encoded = [str(c) for c in result[:size]]
    for value in encoded:
        scalar(value, certificate=True)
    return encoded


def decide(problem):
    model = compile_problem(problem)
    basis, paths, echelon = [], [], []
    for i, row in enumerate(model["output"]):
        extend_basis(row, {"output": i, "word": []}, basis, paths, echelon)
    d = len(model["types"])
    for cursor in range(d):
        if cursor == len(basis):
            break
        row, path = basis[cursor], paths[cursor]
        image = projection(model, row)
        if any(image):
            i = next(i for i, c in enumerate(image) if c)
            scalar(str(image[i]), certificate=True)
            return {"equal": False, **path, "input": i, "coefficient": str(image[i])}
        _, current = path_row(model, path["output"], path["word"])
        for a, (_, target) in model["arrows"].items():
            if target == current:
                extend_basis(advance(model, row, a),
                             {"output": path["output"], "word": path["word"] + [a]},
                             basis, paths, echelon)
        assert len(basis) <= d
    return {"equal": True, "basis": paths,
            "initial": [coordinates(row, echelon, len(basis)) for row in model["output"]],
            "closure": {a: [coordinates(advance(model, row, a), echelon, len(basis))
                            for row in basis] for a in model["arrows"]}}


def witness(problem, certificate):
    model = compile_problem(problem)
    row, current = path_row(model, certificate["output"], certificate["word"])
    i = certificate["input"]
    require(type(i) is int and 0 <= i < len(model["roles"]), "invalid input")
    require(current == model["roles"][i], "witness input has wrong type")
    c = projection(model, row)[i]
    require(c != 0 and c == scalar(certificate["coefficient"], certificate=True), "false discrepancy")
    visits = [model["roles"][certificate["output"]]]
    for a in certificate["word"]:
        visits.append(model["arrows"][a][0])
    positions = {t: [j for j, v in enumerate(visits) if v == t] for t in set(model["roles"])}
    matrices = {}
    for a, (src, dst) in model["arrows"].items():
        matrix = [[0] * len(positions[src]) for _ in positions[dst]]
        for j, letter in enumerate(certificate["word"]):
            if letter == a:
                matrix[positions[dst].index(j)][positions[src].index(j + 1)] = 1
        matrices[a] = matrix
    return {"dimensions": {t: len(p) for t, p in positions.items()}, "matrices": matrices,
            "input_coordinate": positions[current].index(len(visits) - 1),
            "output_coordinate": positions[visits[0]].index(0), "coefficient": str(c)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("problem", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    require(args.problem.stat().st_size <= 1_000_000, "problem file too large")
    result = decide(json.loads(args.problem.read_text()))
    encoded = json.dumps(result, indent=2, sort_keys=True) + "\n"
    require(len(encoded.encode()) <= 16_000_000, "certificate file too large")
    with args.output.open("x") as stream:
        require(stream.write(encoded) == len(encoded), "short certificate write")
    print("EQUAL" if result["equal"] else "DIFFERENT")


if __name__ == "__main__":
    main()
