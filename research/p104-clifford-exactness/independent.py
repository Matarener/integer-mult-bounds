#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Independent Gaussian/Mobius and literal-collector checker.

Clear1nsight, with substantial OpenAI assistance. No primary implementation
or predecessor executable is imported. The authenticated lifting source fixes
the native signed-floor convention; the rational and integer arithmetic below
were independently implemented from that convention and its closed matrix.
"""

import argparse
import gzip
import hashlib
import json
from pathlib import Path


ZERO = (0, 0)
ONE = (1, 0)
I = (0, 1)
PI = (1, 1)
INPUTS = {
    "WORD.json": "cec1fb3fbd0067b500ad5119a62ba60685be718e769374d7ec8abdd2beaa7e50",
    "NATIVE.json.gz": "ab91c78835c3e10cf3b2cb8a5d4e0b7cfc3df1ae5a811298d27842f2193e1e3d",
    "lifting.py": "9424ee08f22b717f6d58f7cc46f189c5549fa86778afcd0c0762ab2daf591160",
}
SOURCE_SIZES = {"WORD.json": 288482, "NATIVE.json.gz": 49610, "lifting.py": 8567}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def add(a, b):
    return a[0] + b[0], a[1] + b[1]


def sub(a, b):
    return a[0] - b[0], a[1] - b[1]


def multiply(a, b):
    return a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0]


def phase(z, power):
    a, b = z
    return ((a, b), (-b, a), (-a, -b), (b, -a))[power % 4]


def pi_divide(z):
    a, b = z
    require((a + b) % 2 == 0, "Newton coefficient not divisible by pi")
    return (a + b) // 2, (b - a) // 2


def dimension(values):
    n = len(values)
    require(n > 0 and n & (n - 1) == 0, "binary cube array")
    require(all(len(z) == 2 and all(type(a) is int for a in z) for z in values),
            "Gaussian integer array")
    return n.bit_length() - 1


def newton(values):
    """Boolean Mobius inversion, independently of tensor encoder sweeps."""
    r = dimension(values)
    coefficients = list(values)
    for bit in range(r):
        step = 1 << bit
        for mask in range(len(values)):
            if mask & step:
                coefficients[mask] = sub(coefficients[mask], coefficients[mask ^ step])
    return coefficients


def decode(values):
    coefficients = newton(values)
    for mask, value in enumerate(coefficients):
        for _ in range(mask.bit_count()):
            value = pi_divide(value)
        coefficients[mask] = value
    return coefficients


def encode(coefficients):
    """Weight each Newton coefficient, then Boolean zeta transform."""
    r = dimension(coefficients)
    values = []
    for mask, value in enumerate(coefficients):
        for _ in range(mask.bit_count()):
            value = multiply(PI, value)
        values.append(value)
    for bit in range(r):
        step = 1 << bit
        for mask in range(len(values)):
            if mask & step:
                values[mask] = add(values[mask], values[mask ^ step])
    return values


def belongs(values):
    try:
        decode(values)
    except ValueError as error:
        require(str(error) == "Newton coefficient not divisible by pi", "membership diagnostic")
        return False
    return True


def rational_pair_numerators(a, b, direction=1):
    """The two exact C outputs, with common denominator two."""
    require(direction in (1, -1), "C direction")
    total = add(a, b)
    difference = sub(a, b)
    rotated = -direction * difference[1], direction * difference[0]
    return add(total, rotated), sub(total, rotated)


def literal_pair(a, b, direction=1):
    """Closed component formula for the literal signed-floor pair."""
    require(direction in (1, -1), "literal C direction")
    dr, di = a[0] - b[0], a[1] - b[1]
    qr, qi = -direction * di, direction * dr
    br = b[0] + dr // 2 - qr // 2
    bi = b[1] + di // 2 - qi // 2
    return (br + qr, bi + qi), (br, bi)


def coordinate(values, bit, mode="literal", direction=1):
    require(0 <= bit < dimension(values), "coordinate bit")
    result = list(values)
    for x in range(len(values)):
        if x & (1 << bit):
            continue
        y = x | (1 << bit)
        numerator = rational_pair_numerators(values[x], values[y], direction)
        if mode == "numerator":
            result[x], result[y] = numerator
        else:
            require(mode == "literal", "coordinate mode")
            first, second = literal_pair(values[x], values[y], direction)
            require(tuple(2 * a for a in first) == numerator[0]
                    and tuple(2 * a for a in second) == numerator[1],
                    "literal pair rounding defect")
            result[x], result[y] = first, second
    return result


def wrapper_plan(record):
    require(set(record) == {"matrix_rows", "offset", "linear_Z4", "quadratic_rows", "phase"},
            "literal wrapper fields")
    rows, linear, quadratic = [record[k] for k in ("matrix_rows", "linear_Z4", "quadratic_rows")]
    require(len(rows) == len(linear) == len(quadratic) == 9, "nine-bit wrapper")
    require(all(type(x) is int and 0 <= x < 512 for x in rows + quadratic), "wrapper binary words")
    require(all(type(x) is int and 0 <= x < 4 for x in linear), "wrapper linear phase")
    require(type(record["offset"]) is int and 0 <= record["offset"] < 512
            and type(record["phase"]) is int and 0 <= record["phase"] < 4, "wrapper constants")
    plan = []
    for x in range(512):
        destination = record["offset"] ^ sum(((row & x).bit_count() % 2) << j
                                             for j, row in enumerate(rows))
        exponent = record["phase"]
        for j in range(9):
            if x & (1 << j):
                exponent += linear[j]
                exponent += 2 * (quadratic[j] & x & ~((1 << (j + 1)) - 1)).bit_count()
        plan.append((destination, exponent % 4))
    require(len({destination for destination, _ in plan}) == 512, "wrapper affine bijection")
    return plan


def wrapper(values, plan):
    require(len(values) == len(plan), "wrapper address count")
    out = [ZERO] * len(values)
    for x, (destination, exponent) in enumerate(plan):
        out[destination] = phase(values[x], exponent)
    return out


def permutation_cycles(plan):
    unseen = set(range(len(plan)))
    lengths = []
    while unseen:
        start = min(unseen)
        address, length = start, 0
        while address in unseen:
            unseen.remove(address)
            length += 1
            address = plan[address][0]
        require(address == start, "complete disjoint wrapper cycles")
        lengths.append(length)
    return lengths


def transform(values, recipe, mode="literal", check_prefixes=False):
    current = wrapper(values, recipe["right_plan"])
    if check_prefixes:
        decode(current)
    for bit in range(recipe["rank"]):
        current = coordinate(current, bit, mode)
        if check_prefixes:
            decode(current)
    current = wrapper(current, recipe["left_plan"])
    if check_prefixes:
        decode(current)
    return current


def digest_object(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def read_sources(word_path, native_path, lifting_path):
    blobs = {}
    for name, path in [("WORD.json", word_path), ("NATIVE.json.gz", native_path), ("lifting.py", lifting_path)]:
        path = Path(path)
        require(path.is_file() and not path.is_symlink(), "regular authenticated input " + name)
        with path.open("rb") as stream:
            data = stream.read(SOURCE_SIZES[name] + 1)
        require(len(data) == SOURCE_SIZES[name], "bounded authenticated input size " + name)
        require(hashlib.sha256(data).hexdigest() == INPUTS[name], "authenticated input " + name)
        blobs[name] = data
    word = json.loads(blobs["WORD.json"])
    native = json.loads(gzip.decompress(blobs["NATIVE.json.gz"]))
    require(word["schema_version"] == native["schema_version"] == 1
            and word["chart"] == native["chart"], "source chart and schema")
    require(len(word["program"]) == 5398 and len(native["transports"]) == 1245, "source event inventory")
    frame = [256, 136, 64, 40, 16, 4, 2, 1]
    sources = ["D31", "D30", "D29", "D28", "D27"]
    expected = [["zero", "C", frame]]
    expected += [["add", "C", source, 1, frame] for source in sources]
    expected += [["transport", "C", frame, [364], 7], ["add", "Q7", "C", "1", [364]],
                 ["transport", "C", [364], frame, 7]]
    expected += [["add", "C", source, "-1", frame] for source in reversed(sources)]
    expected += [["erase", "C", frame]]
    events = word["program"][2025:2040]
    require(events == expected, "exact fifteen-event collector occurrence")
    recipes = {}
    for event in (2031, 2033):
        hits = [entry for entry in native["transports"] if event in entry["events"]]
        require(len(hits) == 1 and hits[0]["events"] == [event], "unique literal transport occurrence")
        record = hits[0]
        gate = word["program"][event]
        require(record["old"] == gate[2] and record["new"] == gate[3], "transport frame binding")
        recipe = record["recipe"]
        require(set(recipe) == {"left", "right", "rank"} and recipe["rank"] == gate[4] == 7,
                "rank-seven literal recipe")
        recipes[event] = {"rank": 7, "left_plan": wrapper_plan(recipe["left"]),
                          "right_plan": wrapper_plan(recipe["right"]),
                          "source_recipe": recipe}
    return events, recipes


def must_reject(function, expected):
    try:
        function()
    except ValueError as error:
        require(str(error) == expected, "control failed at wrong obligation: " + str(error))
        return expected
    raise ValueError("negative control unexpectedly accepted: " + expected)


def check_generators():
    def matrix(r, operation):
        columns = []
        for index in range(1 << r):
            coefficients = [ZERO] * (1 << r)
            coefficients[index] = ONE
            columns.append(decode(operation(encode(coefficients))))
        return [list(row) for row in zip(*columns)]

    zero, one, imag, minus, pi, negbar = ZERO, ONE, I, (-1, 0), PI, (-1, 1)
    expected = {
        "C": [[one, one], [zero, imag]],
        "C_inverse": [[one, imag], [zero, (0, -1)]],
        "S": [[one, zero], [imag, imag]],
        "X": [[one, pi], [zero, minus]],
        "CNOT_0_to_1": [[one, zero, zero, zero], [zero, one, one, pi],
                         [zero, zero, one, zero], [zero, zero, negbar, minus]],
        "CZ": [[one, zero, zero, zero], [zero, one, zero, zero],
               [zero, zero, one, zero], [imag, negbar, negbar, minus]],
    }
    operations = {
        "C": (1, lambda v: coordinate(v, 0)),
        "C_inverse": (1, lambda v: coordinate(v, 0, direction=-1)),
        "S": (1, lambda v: [v[0], phase(v[1], 1)]),
        "X": (1, lambda v: [v[1], v[0]]),
        "CNOT_0_to_1": (2, lambda v: [v[x ^ ((x & 1) << 1)] for x in range(4)]),
        "CZ": (2, lambda v: [phase(z, 2 if x == 3 else 0) for x, z in enumerate(v)]),
    }
    found = {name: matrix(r, operation) for name, (r, operation) in operations.items()}
    require(found == expected, "independent exact generator intertwiners")
    for name, order in [("C", 4), ("S", 4), ("X", 2), ("CNOT_0_to_1", 2), ("CZ", 2)]:
        r, operation = operations[name]
        for index in range(1 << r):
            coefficients = [ZERO] * (1 << r)
            coefficients[index] = ONE
            value = initial = encode(coefficients)
            for _ in range(order):
                value = operation(value)
                decode(value)
            require(value == initial, "generator inverse preserves lattice")
    return found


def check_parity_and_boundaries():
    cases = 0
    for direction in (1, -1):
        for real in range(-7, 8):
            for imag in range(-7, 8):
                a, b = (-5, 8), (-5 - real, 8 - imag)
                actual = literal_pair(a, b, direction)
                ideal = rational_pair_numerators(a, b, direction)
                exact = all(tuple(2 * t for t in z) == w for z, w in zip(actual, ideal))
                require(exact == ((real - imag) % 2 == 0), "signed-floor parity equivalence")
                cases += 1
    single_gate = [ZERO, ZERO, ZERO, PI]
    require(not belongs(single_gate), "single-gate example lies outside B2")
    first = coordinate(single_gate, 0)
    require(first == [ZERO, ZERO, ONE, I], "first C is exactly integral outside maximal module")
    other_single = coordinate(single_gate, 1)
    require(other_single == [ZERO, ONE, ZERO, I], "other single C is exactly integral outside maximal module")
    bad_prefix = must_reject(lambda: coordinate(first, 1), "literal pair rounding defect")
    phase_witness = [ONE, I]
    require(decode(phase_witness) == [ONE, I] and coordinate(phase_witness, 0) == [PI, ZERO],
            "old phase witness now has exact phase-complete entrance")
    quarter_source, quarter = [(4, 0), ZERO], [ONE, ZERO]
    require(belongs(quarter_source) and not belongs(quarter), "integral quarter leaves B1")
    must_reject(lambda: coordinate(quarter, 0), "literal pair rounding defect")
    e0 = [ONE, ZERO]
    ce = coordinate(encode(e0), 0)
    ec_num = encode(coordinate(e0, 0, mode="numerator"))
    require([tuple(2 * t for t in z) for z in ce] != ec_num, "CE is not EC")
    cubic_phase = [phase(ONE, 2 if x == 7 else 0) for x in range(8)]
    require(not belongs(cubic_phase), "cubic phase is outside quadratic wrapper contract")
    return {"signed_floor_cases": cases,
            "single_gate_outside_B2": single_gate, "first_exact_C0": first,
            "individual_exact_C1": other_single,
            "second_C1_rejection": bad_prefix,
            "phase_witness": phase_witness, "phase_witness_coefficients": decode(phase_witness),
            "quarter_source_in_B1": quarter_source, "integral_quarter_outside_B1": quarter,
            "CE_e0": ce, "two_times_EC_e0": ec_num,
            "cubic_phase_outside_B3": cubic_phase}


def check_complete_columns(recipes):
    forward, backward = recipes[2031], recipes[2033]
    column_hash = hashlib.sha256()
    lattice_hash = hashlib.sha256()
    for index in range(512):
        column = [ZERO] * 512
        column[index] = ONE
        sent = transform(column, forward, "numerator")
        returned = transform(sent, backward, "numerator")
        require(returned == [(16384, 0) if j == index else ZERO for j in range(512)],
                "actual archived V times U identity on complete complex basis")
        column_hash.update(json.dumps(sent, separators=(",", ":")).encode() + b"\n")
        for component in range(2):
            coefficients = [ZERO] * 512
            sign = -1 if (index + component) % 2 else 1
            coefficients[index] = (sign, 0) if component == 0 else (0, sign)
            value = encode(coefficients)
            require(decode(value) == coefficients, "complete signed encoder basis round trip")
            actual_sent = transform(value, forward)
            decode(actual_sent)
            actual_returned = transform(actual_sent, backward)
            require(actual_returned == value, "literal U V on complete signed Gaussian module basis")
            lattice_hash.update(json.dumps(actual_sent, separators=(",", ":")).encode() + b"\n")
    return {"ideal_complex_columns": 512, "ideal_U_numerator_denominator": 128,
            "VU_numerator_denominator": 16384, "ideal_U_columns_sha256": column_hash.hexdigest(),
            "signed_Z_basis_columns": 1024, "literal_U_basis_sha256": lattice_hash.hexdigest(),
            "literal_basis_pair_obligations": 1024 * 2 * 7 * 256}


def collector(events, recipes, sources, initial_query, check_prefixes=True):
    require(len(sources) == 5 and all(len(v) == 512 for v in sources)
            and len(initial_query) == 512, "collector entrance shape")
    for value in sources + [initial_query]:
        decode(value)
    source_names = ["D31", "D30", "D29", "D28", "D27"]
    values = dict(zip(source_names, sources))
    values["Q7"] = list(initial_query)
    frozen = [list(source) for source in sources]
    checkpoints = {}
    for index, event in enumerate(events, 2025):
        operation = event[0]
        if operation == "zero":
            require(event[1] not in values, "fresh private C")
            values[event[1]] = [ZERO] * 512
        elif operation == "add":
            target, source, coefficient = event[1], event[2], int(event[3])
            require(coefficient in (-1, 1), "unit collector ADD")
            values[target] = [add(a, b) if coefficient == 1 else sub(a, b)
                              for a, b in zip(values[target], values[source])]
        elif operation == "transport":
            values[event[1]] = transform(values[event[1]], recipes[index], check_prefixes=check_prefixes)
        else:
            require(operation == "erase", "literal collector operation")
            require(values[event[1]] == [ZERO] * 512, "private C erases exactly")
            checkpoints["private_C"] = digest_object(values[event[1]])
            del values[event[1]]
        if operation != "erase":
            decode(values[event[1]])
        if index in (2030, 2031, 2033):
            checkpoints[str(index)] = digest_object(values["C"])
    require([values[name] for name in source_names] == frozen, "all borrowed source arrays unchanged")
    total = [ZERO] * 512
    for source in sources:
        total = [add(a, b) for a, b in zip(total, source)]
    numerator = transform(total, recipes[2031], "numerator")
    require(all(t % 128 == 0 for z in numerator for t in z), "exact source collector target")
    expected = [add(q, (z[0] // 128, z[1] // 128)) for q, z in zip(initial_query, numerator)]
    require(values["Q7"] == expected, "dirty query plus exact archived U source sum")
    return {"query_sha256": digest_object(values["Q7"]), "checkpoints": checkpoints,
            "sources_sha256": digest_object(sources), "initial_query_sha256": digest_object(initial_query)}


def check_collectors(events, recipes):
    fixtures = []
    retained = None
    for seed in range(3):
        coefficient_arrays = [[(((mask * (2 * role + 3) + 5 * seed) % 17) - 8,
                                ((mask * (role + 5) + 7 * seed + role) % 19) - 9)
                               for mask in range(512)] for role in range(6)]
        arrays = [encode(coefficients) for coefficients in coefficient_arrays]
        require(all(any(a < 0 or b < 0 for a, b in value) for value in arrays), "signed dense entrances")
        fixtures.append(collector(events, recipes, arrays[:5], arrays[5]))
        if seed == 0:
            retained = arrays
    require(retained is not None, "nonvacuous collector controls")
    corrupted = {key: dict(value) for key, value in recipes.items()}
    corrupted[2033]["left_plan"] = [(destination, (exponent + 1) % 4)
                                   for destination, exponent in recipes[2033]["left_plan"]]
    wrong_phase = must_reject(lambda: collector(events, corrupted, retained[:5], retained[5], False),
                              "private C erases exactly")
    wrong_return = dict(recipes)
    wrong_return[2033] = recipes[2031]
    wrong_return_rejection = must_reject(lambda: collector(events, wrong_return, retained[:5], retained[5], False),
                                         "private C erases exactly")
    return {"dense_signed_fixtures": fixtures, "actual_return_phase_control": wrong_phase,
            "forward_used_as_return_control": wrong_return_rejection,
            "literal_events": 15, "unit_array_ADDs": 11, "transport_calls": 2,
            "literal_wrapper_invocations": 4, "literal_pair_invocations_per_collector": 3584}


def verify_independent(word_path, native_path, lifting_path):
    events, recipes = read_sources(word_path, native_path, lifting_path)
    generators = check_generators()
    boundaries = check_parity_and_boundaries()
    columns = check_complete_columns(recipes)
    collectors = check_collectors(events, recipes)
    wrappers = {}
    for event, recipe in recipes.items():
        for side in ("left", "right"):
            plan = recipe[side + "_plan"]
            inverse = [None] * 512
            for x, (destination, exponent) in enumerate(plan):
                inverse[destination] = (x, -exponent % 4)
            values = [(x - 257, 3 * x - 911) for x in range(512)]
            require(wrapper(wrapper(values, plan), inverse) == values, "literal wrapper inverse on all addresses")
            lengths = permutation_cycles(plan)
            wrappers[str(event) + ":" + side] = {
                "addresses": 512, "phase_histogram": [sum(exponent == k for _, exponent in plan) for k in range(4)],
                "plan_sha256": digest_object(plan), "source_record_sha256": digest_object(recipe["source_recipe"][side]),
                "permutation_cycles": len(lengths), "cycle_length_histogram": {
                    str(length): lengths.count(length) for length in sorted(set(lengths))},
                "one_scratch_cycle_swaps": 512 + len(lengths)}
    collectors["actual_wrapper_cycles"] = sum(item["permutation_cycles"] for item in wrappers.values())
    collectors["actual_one_scratch_wrapper_swaps"] = sum(item["one_scratch_cycle_swaps"] for item in wrappers.values())
    return {"status": "PASS_INDEPENDENT_P104_PHASE_COMPLETE_DOMAIN", "schema_version": 1,
            "source_sha256": dict(INPUTS), "source_byte_sizes": dict(SOURCE_SIZES),
            "collector_event_range_inclusive": [2025, 2039],
            "collector_events_sha256": digest_object(events), "generator_intertwiners": generators,
            "boundary_controls": boundaries, "complete_columns": columns,
            "literal_wrappers": wrappers, "collector": collectors,
            "scope": "Exact restricted-entrance local collector and Gaussian module; no caller supply, physical owner, recursive cost or frontier admission."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    inputs = args.repo / "research/p104-rounded-collector/inputs"
    receipt = verify_independent(inputs / "WORD.json", inputs / "NATIVE.json.gz",
                                 args.repo / "research/p104-reversible-lifting/lifting.py")
    print(json.dumps(receipt, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
