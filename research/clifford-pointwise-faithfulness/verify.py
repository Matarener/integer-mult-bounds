"""Replay exact pointwise-theorem checks. This is not a proof kernel.

Ali Romman, with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
from copy import deepcopy
from fractions import Fraction as Q
import json
from pathlib import Path
import random
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import source
import bounds
import census
import native_pointwise
import stabilizer
import certify as exact
import clifford_exact as native
from quadratic import Paths

G, need = exact.G, census.require


def tail_bound(shift, clifford):
    denominator, terms = 1, []
    for k in range(1, 6):
        denominator *= (1 << k)-1
        terms.append(Q(1, (1 << (shift*k))*denominator))
    value = sum(terms[:4])+terms[4]/(1-Q(1, 63*(1 << shift)))
    return value-Q(1, 1 << (shift+1)) if clifford else value


def spec_from_state(state, axes, input_axes):
    support = [x for x, a in enumerate(state) if a]
    offset, basis = support[0], []
    for x in support:
        if census.binary_rank(basis+[x ^ offset]) > len(basis):
            basis.append(x ^ offset)
    need(len(support) == 1 << len(basis), "Complete affine support")
    linear = [(state[offset ^ b]-1) % 4 for b in basis]
    pairs = []
    for i, a in enumerate(basis):
        for j in range(i+1, len(basis)):
            value = (state[offset ^ a ^ basis[j]]-1-linear[i]-linear[j]) % 4
            need(value in (0, 2), "Even quadratic cross term")
            if value:
                pairs.append([i, j])
    return {"input_axes": input_axes, "output_axes": axes-input_axes,
            "offset": offset, "basis": basis, "linear": linear,
            "pairs": pairs, "scale": 1}


def literal_values(state):
    return [G.pair(Q(a), Q(b)) for a, b in (census.UNITS[x] for x in state)]


def positive_definite(matrix):
    """Check Hermitian elimination pivots with exact scalars."""
    a = [row.copy() for row in matrix]
    for j in range(len(a)):
        pivot = a[j][j]
        need(pivot.imag == 0 and pivot.real > 0, "Positive Gram pivot")
        for i in range(j+1, len(a)):
            for k in range(j+1, len(a)):
                a[i][k] -= a[i][j]*a[j][k]/pivot


def source_matrix(n, circuit):
    op, columns = native.Op(n, native.identity(n), circuit), []
    for column in range(1 << n):
        values, denominator = op.zero_state(column)
        columns.append([G.pair(Q(a, 1 << denominator), Q(b, 1 << denominator)) for a, b in values])
    return [list(row) for row in zip(*columns)]


def literal_column(problem, width, input_role, address):
    """Execute one tensor column without the signed-word compiler."""
    n, roles = problem["axes"], problem["roles"]
    need(n == 1, "The literal tensor oracle is bounded to one axis")
    size = 1 << width
    matrices = {name: source_matrix(n, circuit) for name, circuit in problem["operators"].items()}

    def execute(instructions):
        values = [[G(0) for _ in range(size)] for _ in range(roles)]
        values[input_role][address] = G(1)
        for op in instructions:
            d, kind = op["dst"], op["op"]
            s = op.get("src", d)
            if kind == "swap":
                values[s], values[d] = values[d], values[s]
                continue
            if kind == "scale":
                values[d] = [G(op["coefficient"])*x for x in values[d]]
                continue
            image = values[s].copy()
            if kind in ("apply", "query"):
                matrix = matrices[op["symbol"]]
                if op.get("inverse", False):
                    matrix = exact.adjoint(matrix)
                for bit in range(width):
                    step = 1 << bit
                    for x in range(size):
                        if not x & step:
                            a, b = image[x], image[x | step]
                            image[x] = matrix[0][0]*a+matrix[0][1]*b
                            image[x | step] = matrix[1][0]*a+matrix[1][1]*b
            if kind == "apply":
                values[d] = image
            else:
                coefficient = G(op.get("coefficient", 1))
                values[d] = [x+coefficient*y for x, y in zip(values[d], image)]
        return values

    a, b = execute(problem["program"]), execute(problem["reference"])
    return [[x-y for x, y in zip(row, other)] for row, other in zip(a, b)]


def rejected(call, label):
    try:
        call()
    except (ValueError, TypeError, KeyError):
        return label
    raise ValueError("A negative control was accepted: "+label)


def run():
    rng = random.Random(20261024)
    state_sets, state_rows = {}, []
    for n in range(5):
        states = census.stabilizer_states(n)
        state_sets[n] = states
        histogram, zeros = census.state_overlap_histogram(states)
        expected = bounds.overlap_counts(n)
        need(histogram == dict(enumerate(expected)), "Complete stabilizer overlap census")
        order = 1 << n
        for j in range(1, n+1):
            order *= (1 << j)+1
        need(len(states) == order, "Complete stabilizer orbit order")
        state_rows.append({"axes": n, "projective_states": order,
                           "overlap_counts": expected, "zero_overlaps": zeros})

    clifford_sets, clifford_rows = {}, []
    for n in (1, 2):
        states = census.clifford_choi(n)
        clifford_sets[n] = states
        histogram, zeros = census.choi_overlap_histogram(states, n)
        pauli = census.pauli_census(n)
        need(len(states) == pauli["projective_order"], "Literal/Pauli group order")
        need(histogram == pauli["overlaps"] and zeros == pauli["zero_overlaps"], "Independent Pauli trace census")
        need(set(states) <= set(state_sets[2*n]), "Clifford Choi states are stabilizer states")
        upper = bounds.overlap_counts(n, clifford=True)
        need(histogram[1] == upper[1], "Exact first Clifford overlap level")
        need(all(count <= upper[k] for k, count in histogram.items()), "Every Clifford overlap upper bound")
        expected_order = 1 << (n*n+2*n)
        for j in range(1, n+1):
            expected_order *= (1 << (2*j))-1
        need(len(states) == expected_order, "Full projective Clifford order")
        clifford_rows.append({"axes": n, **pauli})

    constants = {"clifford_base": tail_bound(0, True), "stabilizer_base": tail_bound(1, False),
                 "clifford_plus4": tail_bound(2, True), "clifford_plus12": tail_bound(6, True)}
    for name, limit in (("clifford_base", Q(8, 9)), ("stabilizer_base", Q(3, 5)),
                        ("clifford_plus4", Q(3, 20)), ("clifford_plus12", Q(1, 126))):
        need(constants[name] < limit, "Uniform tail: "+name)
    bound_checks = 0
    for n in range(1, 65):
        for shift, limit in ((0, Q(1, 9)), (2, Q(17, 20)), (6, Q(125, 126))):
            lower = bounds.pointwise_bound(n, 4*n+4+2*shift, clifford=True)
            need(lower > limit, "Finite Clifford bound")
            need(bounds.pointwise_bound(n, 4*n+5+2*shift, clifford=True) == lower, "Odd-width safe bound")
            bound_checks += 2
        need(bounds.pointwise_bound(n, 2*n+6) > Q(2, 5), "Finite stabilizer bound")
        bound_checks += 1

    map_checks = pair_checks = prefix_checks = 0
    map_sets = {}
    for n in range(4):
        maps = []
        for state in state_sets[n]:
            op = stabilizer.Map(spec_from_state(state, n, n//2))
            need([op.entry(x) for x in range(1 << n)] == literal_values(state), "Literal affine-quadratic map")
            map_checks += 1 << n
            maps.append(op)
        map_sets[n] = maps
        pairs = [(i, j) for i in range(len(maps)) for j in range(len(maps))] if n <= 2 else [
            (rng.randrange(len(maps)), rng.randrange(len(maps))) for _ in range(200)]
        for i, j in pairs:
            a, b = literal_values(state_sets[n][i]), literal_values(state_sets[n][j])
            expected = sum((exact.conjugate(x)*y for x, y in zip(a, b)), G(0))
            need(stabilizer.inner(maps[i], maps[j]) == expected, "Literal nonunitary Gram entry")
            pair_checks += 1
            if i < 4 and j < 4:
                for length in range(n+1):
                    for mask in range(1 << length):
                        prefix = [(mask >> bit) & 1 for bit in range(length)]
                        expected = sum((exact.conjugate(a[x])*b[x] for x in range(1 << n)
                                        if x % (1 << length) == mask), G(0))
                        need(stabilizer.inner(maps[i], maps[j], prefix) == expected, "Literal prefix Gram entry")
                        prefix_checks += 1

    vectors = [literal_values(s) for s in state_sets[1]]
    norms = [sum(exact.norm2(x) for x in vector) for vector in vectors]
    gram = [[exact.power(sum((exact.conjugate(x)*y for x, y in zip(a, b)), G(0)), 8)/
             (norms[i]*norms[j])**4-G(Q(2, 5) if i == j else 0)
             for j, b in enumerate(vectors)] for i, a in enumerate(vectors)]
    positive_definite(gram)
    vectors = []
    for state in clifford_sets[1]:
        weight = sum(bool(x) for x in state[:2])
        divisor = exact.power(G("1+1i"), weight.bit_length()-1)
        vectors.append([value/divisor for value in literal_values(state)])
    gram = [[exact.power(sum((exact.conjugate(x)*y for x, y in zip(a, b)), G(0))/2, 8)-
             G(Q(1, 9) if i == j else 0) for j, b in enumerate(vectors)] for i, a in enumerate(vectors)]
    positive_definite(gram)

    examples = {}
    for path in sorted((HERE / "examples").glob("native-*-identity.json")):
        result = native_pointwise.decide(json.loads(path.read_text()))
        need(result["equal"], "Complete source native relation")
        examples[path.name] = result
    trap = json.loads((HERE / "examples/native-9-phase-trap.json").read_text())
    result = native_pointwise.decide(trap)
    need([row["equal"] for row in result["decisions"]] == [False, True, False, False], "Native/scalar phase residue")
    examples["native-9-phase-trap.json"] = result
    for residue in range(4):
        phase_test = {"axes": 0, "roles": 2,
                      "operators": {str(j): [["phase", j]] for j in range(4)},
                      "program": [{"op": "query", "src": 0, "dst": 1, "symbol": str(j),
                                   "coefficient": str(exact.power(G("0+1i"), (-residue*j) % 4))}
                                  for j in range(4)], "reference": []}
        decisions = native_pointwise.decide(phase_test)["decisions"]
        need([row["equal"] for row in decisions] == [f % 4 != residue for f in range(1, 5)],
             "Every phase residue is necessary")
    for name, expected in (("projection-correct", True), ("projection-scalar-trap", False)):
        problem = json.loads((HERE / f"examples/{name}.json").read_text())
        result = stabilizer.analyze(problem["maps"], problem["coefficients"], problem["width"])
        need(result["equal_to_zero"] == expected, "Projection scalar inside tensor power")
        examples[name+".json"] = result

    native_columns = 0
    for sign in (-1, 1):
        op, path = native.cgate(9, 173, sign), Paths(9, [["C", 173, sign]])
        for x in range(512):
            vector, denominator = op.zero_state(x)
            for y in (x, x ^ 173, x ^ 1):
                a, b = vector[y]
                need(path.entry(y, x) == G.pair(Q(a, 1 << denominator), Q(b, 1 << denominator)), "Source nine-axis C entry")
            native_columns += 1

    problem = json.loads((HERE / "examples/native-1-identity.json").read_text())
    literal_columns = 0
    for input_role in range(3):
        delta = literal_column(problem, 8, input_role, 0)
        need(all(not x for row in delta for x in row), "Literal complete dirty endpoint")
        literal_columns += 1
    dirty = deepcopy(problem)
    dirty["program"].append({"op": "scale", "dst": 2, "coefficient": 0})
    result = native_pointwise.decide(dirty, 8, witness=True)
    need(not result["equal"], "Missing arbitrary dirty return rejected")
    failure = result["decisions"][0]["failures"][0]
    witness = failure["witness"]
    address = sum(x << j for j, x in enumerate(witness["input_tuple"]))
    output = sum(x << j for j, x in enumerate(witness["output_tuple"]))
    delta = literal_column(dirty, 8, failure["input_role"], address)
    need(delta[failure["output_role"]][output] == G(witness["discrepancy"]) != 0, "Literal witness without word expansion")
    literal_columns += 1

    residual_checks = 0
    for n in range(1, 4):
        width = 2*n+6
        for _ in range(12):
            indices = rng.sample(range(len(map_sets[n])), 3)
            specifications = [map_sets[n][j].specification for j in indices]
            coefficients = [str(rng.choice([-2, -1, 1, 2])) for _ in indices]
            need(not stabilizer.analyze(specifications, coefficients, width)["equal_to_zero"], "Independent projective maps cannot cancel")
            residual_checks += 1

    controls = [rejected(lambda: native_pointwise.decide(problem, 7), "unproved width")]
    for label, mutation in (("Boolean role", {"dst": True}), ("Nonboolean inverse", {"inverse": 1})):
        malformed = deepcopy(problem); malformed["program"][0].update(mutation)
        controls.append(rejected(lambda: native_pointwise.decide(malformed), label))
    malformed = deepcopy(problem); malformed["operators"]["H"] = [["C", 1, 0]]
    controls.append(rejected(lambda: native_pointwise.decide(malformed), "Invalid native sign"))
    base = deepcopy(map_sets[2][-1].specification)
    for label, key, value in (("dependent support", "basis", [1, 1]), ("out-of-range offset", "offset", 4),
                              ("zero native scale", "scale", 0), ("invalid phase", "linear", [4]*len(base["basis"])),
                              ("invalid phase pair", "pairs", [[0, 0]])):
        mutant = deepcopy(base); mutant[key] = value
        controls.append(rejected(lambda mutant=mutant: stabilizer.Map(mutant), label))
    controls.append(rejected(lambda: stabilizer.analyze([base], [1], 9), "unproved stabilizer width"))
    other = deepcopy(base); other["input_axes"], other["output_axes"] = 0, 2
    controls.append(rejected(lambda: stabilizer.analyze([base, other], [1, 1], 10), "incompatible rectangular types"))
    controls.append(rejected(lambda: bounds.row_bound(2, 11), "odd exact row request"))
    return {"status": "PASS_POINTWISE_CLIFFORD_AND_STABILIZER_NO_NEW_KAPPA",
            "stabilizer_censuses": state_rows, "clifford_censuses": clifford_rows,
            "infinite_row_upper_bounds": {key: str(value) for key, value in constants.items()},
            "finite_bound_checks": bound_checks, "literal_map_entries": map_checks,
            "literal_pair_inner_products": pair_checks, "literal_prefix_inner_products": prefix_checks,
            "exact_positive_Gram_sizes": [6, 24], "source_nine_axis_columns": native_columns,
            "literal_complete_tensor_columns": literal_columns, "nonunitary_residual_checks": residual_checks,
            "negative_controls": controls, "examples": examples}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-result", action="store_true")
    args = parser.parse_args()
    result = json.loads(json.dumps(run()))
    path = HERE / "RESULT.json"
    if args.write_result:
        path.write_text(json.dumps(result, indent=2, sort_keys=True)+"\n")
    else:
        need(json.loads(path.read_text()) == result, "Complete result receipt")
    print(result["status"])


if __name__ == "__main__":
    main()
