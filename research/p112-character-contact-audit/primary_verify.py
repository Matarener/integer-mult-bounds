"""Independent projector/character audit of the frozen isolated contacts.

No predecessor checker/compiler is imported. Native recipes are compared
as typed records, not executed as a native controller or physical program.
"""
import argparse
from collections import Counter
import gzip
from hashlib import sha256
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE_SHA = "353220f1edf3a3afda11cd5073c5e55446c23c242969b16a361fa53b8e45dd7e"
N, SIZE = 9, 512
UNITS = tuple(1 << j for j in range(N))
PREV = tuple(x & (x-1) for x in range(SIZE))
BIT = tuple((x ^ PREV[x]).bit_length()-1 for x in range(SIZE))
ZERO, ONE = (0, 0), (1, 0)


def need(ok, message):
    if not ok:
        raise ValueError(message)


def dot(left, right):
    return (left & right).bit_count() & 1


def rank(columns):
    basis = [0]*N
    result = 0
    for value in columns:
        while value:
            pivot = value.bit_length()-1
            if basis[pivot]:
                value ^= basis[pivot]
            else:
                basis[pivot] = value
                result += 1
                break
    return result


def apply(columns, value):
    result = 0
    while value:
        bit = value & -value
        result ^= columns[bit.bit_length()-1]
        value ^= bit
    return result


def projector(basis):
    return tuple(sumxor(vector for vector in basis if dot(vector, unit)) for unit in UNITS)


def sumxor(values):
    result = 0
    for value in values:
        result ^= value
    return result


def cap(normal):
    return tuple(unit ^ (normal if dot(normal, unit) else 0) for unit in UNITS)


def phase_from_columns(columns):
    images = [0]*SIZE
    values = bytearray(SIZE)
    for x in range(1, SIZE):
        images[x] = images[PREV[x]] ^ columns[BIT[x]]
        values[x] = images[x].bit_count() & 3
    return bytes(values)


def descriptor(values):
    constant = values[0]
    linear = [(values[unit]-constant) & 3 for unit in UNITS]
    rows = []
    for a in UNITS:
        row = 0
        for j, b in enumerate(UNITS):
            delta = (values[a ^ b]-values[a]-values[b]+constant) & 3
            need(delta in (0, 2), "Z4 quadratic polar must be even")
            if delta:
                row |= b
        rows.append(row)
    return dict(constant_Z4=constant, linear_Z4=linear, quadratic_rows=rows,
                native_rank=rank(rows), sha256=sha256(values).hexdigest())


def rotate(value, exponent):
    a, b = value
    exponent &= 3
    if exponent == 0:
        return a, b
    if exponent == 1:
        return -b, a
    if exponent == 2:
        return -a, -b
    return b, -a


def execute(case, exponents, sign, mutation=None):
    p, q, common, source, target = exponents
    rows = [[ONE, ZERO, ZERO], [ZERO, ONE, ZERO], [ZERO, ZERO, ONE]]

    def add(destination, origin, scalar):
        rows[destination] = [(a+scalar*c, b+scalar*d)
                             for (a, b), (c, d) in zip(rows[destination], rows[origin])]

    def turn(field, exponent):
        rows[field] = [rotate(value, exponent) for value in rows[field]]

    if case == 1:
        add(1, 0, sign)
        turn(0, source-p+(1 if mutation == "global_i" else 0))
        turn(1, target-q)
    else:
        if mutation != "omit_precompensation":
            add(1, 2, -sign)
        turn(0, common-p)
        turn(1, common-q)
        turn(2, common-q)
        add(2, 0, 1)
        add(1, 2, -sign if mutation == "wrong_delivery" else sign)
        add(2, 0, -1)
        if mutation != "omit_helper_return":
            turn(2, q-common)
        turn(0, source-common+(1 if mutation == "global_i" else 0))
        turn(1, target-common)
    return tuple(tuple(row) for row in rows)


def expected(exponents, sign):
    p, q, common, source, target = exponents
    delivered = rotate(ONE, target-p)
    return ((rotate(ONE, source-p), ZERO, ZERO),
            ((sign*delivered[0], sign*delivered[1]), rotate(ONE, target-q), ZERO),
            (ZERO, ZERO, ONE))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=HERE/"source/PR4204-GEOMETRY.json.gz")
    parser.add_argument("--expected", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    raw = args.source.read_bytes()
    need(sha256(raw).hexdigest() == SOURCE_SHA, "immutable phase geometry input")
    data = json.loads(gzip.decompress(raw))
    ports, partners = data["ports"], data["partners"]
    inventory = data["phase_operators"]
    need(data["dimension"] == N and len(ports) == len(partners) == 112
         and len(inventory) == 8880, "exact source sizes")
    need(all(type(v) is int and 0 < v < SIZE and dot(v, v) == 1 for v in ports+partners),
         "odd norm-one encoded source/partner vectors")
    need(all(dot(p, q) == 0 for p, q in zip(ports, partners)), "each provided source/partner pair perpendicular")
    projector_cache, transitions, generated, generated_columns, checked_inventory = {}, {}, {}, {}, set()

    def remember(values, columns):
        key = sha256(values).hexdigest()
        previous = generated.setdefault(key, values)
        need(previous == values, "phase hash collision or inconsistent reconstruction")
        prior_columns = generated_columns.setdefault(key, columns)
        need(prior_columns == columns, "equal complete phases must have the same quadratic polar")
        if key in inventory and key not in checked_inventory:
            got = descriptor(values)
            need(got == inventory[key], "complete independent phase descriptor")
            need(got["quadratic_rows"] == list(columns), "phase polar equals direct projector difference")
            checked_inventory.add(key)
        return key, values, columns

    def frame(columns):
        if columns not in projector_cache:
            projector_cache[columns] = remember(phase_from_columns(columns), columns)
        return projector_cache[columns]

    def difference(after, before):
        cache_key = (after[0], before[0])
        if cache_key not in transitions:
            values = bytes((a-b) & 3 for a, b in zip(after[1], before[1]))
            columns = tuple(a ^ b for a, b in zip(after[2], before[2]))
            transitions[cache_key] = remember(values, columns)
        return transitions[cache_key]

    cases = data["edge_witnesses"]
    legal = {(i, j) for i, p in enumerate(ports) for j, other in enumerate(ports) if not dot(p, other)}
    need(len(cases) == len(legal) == 5824, "complete legal edge count")
    seen_edges = set()
    rank_counts, typed_native_counts = Counter(), Counter()
    word_cache = {}
    character_cases = 0
    typed_operations = 0
    cache_occurrences = Counter()
    first_by_rank = {}
    phase_families = []
    for edge in cases:
        source_index, target_index = edge["source"], edge["target"]
        need((source_index, target_index) in legal and (source_index, target_index) not in seen_edges,
             "unique actually legal source/target edge")
        seen_edges.add((source_index, target_index))
        p, qs, pt, qt = ports[source_index], partners[source_index], ports[target_index], partners[target_index]
        basis = edge["frame"]
        f = len(basis)
        minimal = 1 if p == qt else 2 if not dot(p, qt) else 3
        need(f == edge["minimal_rank"] == minimal, "actual minimal contact case")
        need(all(type(u) is int and 0 < u < SIZE for u in basis), "binary contact basis")
        need(all(dot(u, v) == (i == j) for i, u in enumerate(basis) for j, v in enumerate(basis)),
             "contact basis orthonormal")
        need(all(not dot(u, qs) and not dot(u, pt) for u in basis), "contact basis in both public caps")
        common_columns = projector(basis)
        need(rank(common_columns) == f and apply(common_columns, p) == p
             and apply(common_columns, qt) == qt, "contact rank and required line containment")
        P, Q, L, S, T = (frame(projector((p,))), frame(projector((qt,))), frame(common_columns),
                          frame(cap(qs)), frame(cap(pt)))
        need(rank(S[2]) == rank(T[2]) == 8, "norm-one caps have rank eight")
        required = (P, Q, L, S, T, difference(S, P), difference(T, Q), difference(T, P))
        need([op[0] for op in required] == edge["phase_ids"], "all eight source phase ids bound to explicit projectors")
        source_prepare, target_prepare = difference(L, P), difference(L, Q)
        helper_return = difference(Q, L)
        source_exit, target_exit = difference(S, L), difference(T, L)
        if f == 1:
            need(P[1] == Q[1] == L[1], "rank-one common exact phase")
            native = [(0, "source_exit", difference(S, P)), (1, "target_exit", difference(T, Q))]
            specified = [{"add": [1, 0, 1]}]
            for field, role, operator in native:
                specified.append(dict(field=field, native=role, phase_sha256=operator[0], rank=rank(operator[2])))
        else:
            native = [(0, "source_prepare", source_prepare), (1, "target_prepare", target_prepare),
                      (2, "helper_prepare", target_prepare), (2, "helper_return", helper_return),
                      (0, "source_exit", source_exit), (1, "target_exit", target_exit)]
            def record(item):
                field, role, operator = item
                return dict(field=field, native=role, phase_sha256=operator[0], rank=rank(operator[2]))
            specified = [{"add": [1, 2, -1]}] + [record(x) for x in native[:3]]
            specified += [{"add": [2, 0, 1]}, {"add": [1, 2, 1]}, {"add": [2, 0, -1]}]
            specified += [record(x) for x in native[3:]]
        need(specified == edge["operations_coefficient_plus_one"], "complete ordered typed plus-one word")
        hist = Counter(rank(op[2]) for field, role, op in native)
        want_hist = {7: 2} if f == 1 else {f-1: 4, 8-f: 2}
        need(dict(hist) == want_hist and {str(k): v for k, v in hist.items()} == edge["native_histogram"],
             "complete native occurrence histogram")
        adds = 1 if f == 1 else 4
        need(edge["whole_field_signed_adds"] == adds and edge["rank_mass"] == sum(k*v for k, v in hist.items())
             and edge["both_coefficients"] == [-1, 1] and edge["physical_helper_return"] is True,
             "source invoice agrees with reconstructed word")
        typed_operations += len(specified)
        typed_native_counts[f] += len(native)
        rank_counts[f] += 1
        first_by_rank.setdefault(f, (source_index, target_index, (P, Q, L, S, T)))
        phase_families.append((f, source_index, target_index, (P, Q, L, S, T)))
        for x in range(SIZE):
            exponents = tuple(op[1][x] for op in (P, Q, L, S, T))
            for sign in (-1, 1):
                key = (f, exponents, sign)
                if key not in word_cache:
                    actual = execute(f, exponents, sign)
                    wanted = expected(exponents, sign)
                    word_cache[key] = actual, wanted
                actual, wanted = word_cache[key]
                need(actual == wanted, "all-three-raw-column contact boundary")
                cache_occurrences[f] += 1
                character_cases += 1
    need(seen_edges == legal and dict(rank_counts) == {1: 104, 2: 2912, 3: 2808}, "all actual contact cases")
    need(checked_inventory == set(inventory), "every phase inventory record independently regenerated")
    serialized_phase_union = set(inventory) | {
        operation["phase_sha256"] for edge in cases for operation in edge["operations_coefficient_plus_one"]
        if "phase_sha256" in operation}
    need(serialized_phase_union <= set(generated), "every serialized native phase is explicitly recomputed")
    auxiliary_keys = set(generated)-serialized_phase_union
    need(auxiliary_keys == {sha256(bytes(SIZE)).hexdigest()}, "only auxiliary phase is the rank-one unused identity preparation")
    # Explicit Gaussian witness columns, not merely exceptions or Boolean
    # helpers. Search the complete actual edge/character family deterministically.
    controls = []
    for mutation in ("omit_helper_return", "omit_precompensation", "wrong_delivery", "global_i"):
        found = None
        for f, source_index, target_index, ops in phase_families:
            if f == 1 and mutation != "global_i":
                continue
            for x in range(SIZE):
                exponents = tuple(op[1][x] for op in ops)
                actual, wanted = execute(f, exponents, 1, mutation), expected(exponents, 1)
                if actual != wanted:
                    row, column = next((i, j) for i in range(3) for j in range(3) if actual[i][j] != wanted[i][j])
                    found = dict(mutation=mutation, source=source_index, target=target_index,
                                 contact_rank=f, character=x, input_column=column, input_Gaussian=[1, 0],
                                 raw_input="chi_character(z)=(-1)^(character dot z) in input_column; other raw fields zero",
                                 observed_raw_address=0,
                                 output_field=row, actual_Gaussian=list(actual[row][column]),
                                 expected_Gaussian=list(wanted[row][column]))
                    break
            if found is not None:
                break
        need(found is not None, "mutation needs actual nonzero Gaussian witness")
        controls.append(found)
    sample = next(iter(generated.values()))
    shifted = bytes((value+1) & 3 for value in sample)
    ordinary, changed = descriptor(sample), descriptor(shifted)
    need(ordinary["quadratic_rows"] == changed["quadratic_rows"]
         and ordinary["native_rank"] == changed["native_rank"]
         and ordinary["linear_Z4"] == changed["linear_Z4"]
         and ordinary["constant_Z4"] != changed["constant_Z4"], "polar/rank cannot detect uniform i")
    result = {"status": "PASS_INDEPENDENT_P112_PROJECTOR_PHASE_AND_ISOLATED_DIRTY_WORD_NO_NEW_KAPPA",
              "source_sha256": SOURCE_SHA, "checker_sha256": sha256(Path(__file__).read_bytes()).hexdigest(),
              "dimension": N, "characters": SIZE, "edges": len(cases),
              "contact_rank_counts": dict(sorted(rank_counts.items())),
              "inventory_records_reconstructed": len(checked_inventory),
              "inventory_character_exponents": len(checked_inventory)*SIZE,
              "distinct_generated_phase_arrays_including_transition_only": len(generated),
              "serialized_inventory_and_native_phase_union": len(serialized_phase_union),
              "auxiliary_identity_preparation_phase_arrays": len(auxiliary_keys),
              "projector_cache_size": len(projector_cache), "transition_cache_size": len(transitions),
              "ordered_typed_plus_one_operations_checked": typed_operations,
              "native_occurrences_by_case": dict(sorted(typed_native_counts.items())),
              "both_sign_edge_character_cases": character_cases,
              "three_raw_input_column_cases": character_cases*3,
              "Gaussian_scalar_word_cache_entries": len(word_cache),
              "cache_occurrences_by_case": dict(sorted(cache_occurrences.items())),
              "cache_dependency_key": "(contact-rank case, P/QT/L/source-cap/target-cap Z4 exponents at the actual character, sign). Every frame transition is exactly an exponent difference; word and expected map use no other data. All actual edges/characters/signs are visited.",
              "controls": controls, "uniform_i_polar_rank_blindness_checked": True,
              "scope": "Provided geometry only: all phase IDs/records, projector ranks, ordered plus-one recipes and specified isolated +/- words on all raw columns/all characters. No original port reconstruction, native compiler, B4, DP, shared caller, physical tape/precision or new kappa replay."}
    payload = json.dumps(result, indent=2, sort_keys=True)+"\n"
    if args.expected is not None:
        need(json.loads(payload) == json.loads(args.expected.read_bytes()), "frozen primary receipt equality")
    if args.output is not None:
        args.output.write_text(payload)
    print(result["status"])


if __name__ == "__main__":
    main()
