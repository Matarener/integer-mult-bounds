#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Certify the new entrance maps for the in-place P104 completion.

Clear1nsight, with substantial OpenAI assistance.  The Gaussian Clifford
compiler and the separately written PR3416 checker retain their authorship.
PR3462 supplies the omitted X list; PR3469 supplies the endpoint convention.

The caller authenticates WORD and both executable sources before calling
``synthesize`` and reconciles X_NAMES with its authenticated completion C.
This module neither imports nor rereplays the 1,245 historical native classes.
It certifies 52 singleton-to-empty maps and one empty-to-full map.  These
are exact complex-linear maps; literal integer admission is a separate gate.
"""

import hashlib
import json
from collections import Counter


BITS = 9
SIZE = 1 << BITS
FULL = [256, 128, 64, 32, 16, 8, 4, 2, 1]
X_NAMES = (
    "X0", "X10", "X101", "X102", "X11", "X12", "X15", "X16",
    "X17", "X21", "X24", "X25", "X26", "X30", "X31", "X33",
    "X34", "X37", "X38", "X39", "X41", "X42", "X43", "X47",
    "X5", "X51", "X52", "X53", "X55", "X56", "X57", "X6",
    "X60", "X61", "X62", "X63", "X67", "X68", "X69", "X71",
    "X72", "X73", "X76", "X77", "X78", "X82", "X86", "X90",
    "X91", "X93", "X96", "X97",
)


class NativeError(ValueError):
    """A new-map, frame or native-certificate obligation failed."""


def require(condition, message):
    if not condition:
        raise NativeError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def binary_rank(columns):
    """Independent elimination on the requested map's nine B columns."""
    require(type(columns) in (list, tuple) and len(columns) <= BITS,
            "binary-rank capacity")
    pivots = {}
    for original in columns:
        require(type(original) is int and 0 <= original < SIZE,
                "binary-rank column")
        value = original
        while value:
            bit = value.bit_length() - 1
            if bit in pivots:
                value ^= pivots[bit]
            else:
                pivots[bit] = value
                break
    return len(pivots)


def check_wrapper_shape(record):
    require(type(record) is dict and set(record) == {
        "matrix_rows", "offset", "phase", "linear_Z4", "quadratic_rows"
    }, "wrapper fields")
    for name in ("matrix_rows", "quadratic_rows", "linear_Z4"):
        require(type(record[name]) in (list, tuple)
                and len(record[name]) == BITS, "wrapper vector width")
    for name in ("matrix_rows", "quadratic_rows"):
        require(all(type(x) is int and 0 <= x < SIZE for x in record[name]),
                "wrapper binary coefficients")
    require(all(type(x) is int and 0 <= x < 4 for x in record["linear_Z4"]),
            "wrapper linear phases")
    require(type(record["offset"]) is int and 0 <= record["offset"] < SIZE,
            "wrapper offset")
    require(type(record["phase"]) is int and 0 <= record["phase"] < 4,
            "wrapper scalar phase")
    require(binary_rank(record["matrix_rows"]) == BITS,
            "wrapper invertible address map")
    quadratic = record["quadratic_rows"]
    for j in range(BITS):
        require((record["linear_Z4"][j] & 1) == ((quadratic[j] >> j) & 1),
                "wrapper diagonal parity")
        for k in range(j):
            require(((quadratic[j] >> k) & 1) == ((quadratic[k] >> j) & 1),
                    "wrapper quadratic symmetry")


def wrapper_mapping(record):
    """Enumerate address and phase directly, independently of kernel.wrapper."""
    check_wrapper_shape(record)
    mapping = []
    for source in range(SIZE):
        target = record["offset"]
        for j, row in enumerate(record["matrix_rows"]):
            target ^= ((row & source).bit_count() & 1) << j
        phase = record["phase"]
        active = [j for j in range(BITS) if (source >> j) & 1]
        for j in active:
            phase += record["linear_Z4"][j]
            for k in active:
                if k > j:
                    phase += 2 * ((record["quadratic_rows"][j] >> k) & 1)
        mapping.append((target, phase % 4))
    require({target for target, _ in mapping} == set(range(SIZE)),
            "wrapper address bijection")
    return tuple(mapping)


def wrapper_counts(mapping):
    """Count a direct cycle permutation and then Gaussian unit rotations.

    A cycle of length l uses l-1 direct Gaussian SWAPs.  This counts an
    abstract in-place permutation, not the old l+1 clean-scratch algorithm.
    A physical lowering must pay its actual scalar SWAP/sign implementation.
    """
    require(type(mapping) is tuple and len(mapping) == SIZE,
            "wrapper-map capacity")
    require({target for target, _ in mapping} == set(range(SIZE)),
            "wrapper-map permutation")
    seen, cycles = set(), Counter()
    for start in range(SIZE):
        if start in seen:
            continue
        value, length = start, 0
        while value not in seen:
            seen.add(value)
            length += 1
            value = mapping[value][0]
        require(value == start and length > 0, "closed permutation cycle")
        cycles[length] += 1
    phase = Counter(p for _, p in mapping)
    require(all(type(p) is int and 0 <= p < 4 for p in phase),
            "wrapper-map phases")
    count = sum(cycles.values())
    return {
        "mapping_sha256": digest(mapping),
        "entries": SIZE,
        "cycles": count,
        "cycle_length_histogram": {str(k): cycles[k] for k in sorted(cycles)},
        "direct_gaussian_swaps": SIZE - count,
        "phase_histogram": {str(k): phase[k] for k in range(4)},
        "nontrivial_phase_entries": SIZE - phase[0],
        "phase_real_swaps": phase[1] + phase[3],
        "phase_real_negations": phase[1] + 2 * phase[2] + phase[3],
    }


def certify_record(record, kernel, cache=None):
    """Prove one proposed native map, including its global scalar phase."""
    require(type(record) is dict and set(record) == {"old", "new", "recipe"},
            "new native record fields")
    old, new, recipe = record["old"], record["new"], record["recipe"]
    require(type(old) is list and type(new) is list, "native frame types")
    require(type(recipe) is dict and set(recipe) == {"rank", "left", "right"},
            "native recipe fields")
    require(type(recipe["rank"]) is int and 1 <= recipe["rank"] <= BITS,
            "positive native rank")
    if cache is None:
        cache = {}
    wrappers = {}
    for side in ("right", "left"):
        mapping = wrapper_mapping(recipe[side])
        require(mapping == kernel["wrapper"](recipe[side]),
                "independent wrapper address/phase mismatch")
        wrappers[side] = wrapper_counts(mapping)
    actual = kernel["recipe_program"](recipe)
    expected = kernel["adjoint"](kernel["chart"](old)) + kernel["chart"](new)
    tableau, anchor = kernel["equal_certificate"](actual, expected, cache)
    requested_table = kernel["program_table"](expected, cache)
    require(len(requested_table) == 2 * BITS, "requested signed Pauli width")
    rank = binary_rank([x for _, x, _ in requested_table[BITS:]])
    require(recipe["rank"] == rank, "minimal requested native rank")
    return {
        "old": list(old), "new": list(new), "rank": rank,
        "recipe_sha256": digest(recipe),
        "signed_pauli_sha256": tableau,
        "exact_anchor_sha256": anchor,
        "wrappers": wrappers,
    }


def build_record(old, new, compiler, kernel, cache):
    before = compiler["canonical_frame"](BITS, old)
    after = compiler["canonical_frame"](BITS, new)
    operation = before.then(after.adjoint())
    recipe, _unused_execution = compiler["lower_child"](operation)
    # The compiler's own execution object is deliberately not an oracle.
    recipe = json.loads(canonical(recipe))
    record = {"old": list(old), "new": list(new), "recipe": recipe}
    return record, certify_record(record, kernel, cache)


def aggregate_wrappers(certificates, multiplicities):
    require(set(certificates) == set(multiplicities), "wrapper multiplicities")
    total = Counter()
    phases, cycle_lengths = Counter(), Counter()
    for name, certificate in certificates.items():
        multiplicity = multiplicities[name]
        require(type(multiplicity) is int and 1 <= multiplicity <= 93,
                "positive native multiplicity")
        for record in certificate["wrappers"].values():
            total["wrappers"] += multiplicity
            for key in ("entries", "cycles", "direct_gaussian_swaps",
                        "nontrivial_phase_entries", "phase_real_swaps",
                        "phase_real_negations"):
                total[key] += multiplicity * record[key]
            for key, value in record["phase_histogram"].items():
                phases[key] += multiplicity * value
            for key, value in record["cycle_length_histogram"].items():
                cycle_lengths[key] += multiplicity * value
    total["phase_histogram"] = {str(k): phases[str(k)] for k in range(4)}
    total["cycle_length_histogram"] = {
        key: cycle_lengths[key] for key in sorted(cycle_lengths, key=int)
    }
    require(total["entries"] == total["wrappers"] * SIZE,
            "complete wrapper entry count")
    require(total["direct_gaussian_swaps"] == total["entries"] - total["cycles"],
            "direct wrapper permutation count")
    return dict(total)


def check_word_boundary(word):
    require(type(word) is dict and word.get("chart") ==
            "Delta_W = conjugate(Gamma_W) = Gamma_W^(-T)", "source chart")
    require(type(word.get("program")) is list and len(word["program"]) == 5398,
            "source event count")
    for field in ("initial_frames", "final_frames"):
        require(type(word.get(field)) is dict and len(word[field]) == 358,
                "source public bank count")
    require(len(X_NAMES) == len(set(X_NAMES)) == 52, "frozen omitted X list")
    old_frames = []
    for name in X_NAMES:
        old = word["initial_frames"].get(name)
        require(type(old) is list and len(old) == 1 and type(old[0]) is int
                and 0 < old[0] < SIZE, "actual singleton X entrance")
        require(word["final_frames"].get(name) == FULL, "actual full X endpoint")
        old_frames.append(old[0])
    require(len(set(old_frames)) == 52, "distinct singleton X entrances")
    return old_frames


def synthesize(word, compiler, kernel):
    """Return (x_to_empty, empty_to_full, deterministic new-map receipt).

    Each returned map record has exactly {old, new, recipe}.  The common
    empty-to-full record occurs on the 52 X and the 41 omitted N/G roles in
    the proposed prefix.  The caller binds these roles and executes the
    complete scalar and chronological program separately.
    """
    old_frames = check_word_boundary(word)
    require(type(compiler) is dict and type(kernel) is dict, "engine namespaces")
    require(all(callable(compiler.get(k)) for k in ("canonical_frame", "lower_child")),
            "compiler API")
    require(all(callable(kernel.get(k)) for k in (
        "wrapper", "recipe_program", "adjoint", "chart", "equal_certificate",
        "program_table"
    )), "separate checker API")
    cache, records, certificates = {}, {}, {}
    for name in X_NAMES:
        record, certificate = build_record(word["initial_frames"][name], [],
                                           compiler, kernel, cache)
        require(certificate["rank"] == 1, "singleton-to-empty rank one")
        records[name], certificates[name] = record, certificate
    full_record, full_certificate = build_record([], FULL, compiler, kernel, cache)
    require(full_certificate["rank"] == BITS, "empty-to-full rank nine")
    certificates["empty_to_full"] = full_certificate
    multiplicities = {name: 1 for name in X_NAMES}
    multiplicities["empty_to_full"] = 93
    wrapper_total = aggregate_wrappers(certificates, multiplicities)
    require(wrapper_total["wrappers"] == 290, "new wrapper occurrence count")
    receipt = {
        "schema_version": 1,
        "scope": "53 new exact maps; historical native classes not replayed",
        "x_names": list(X_NAMES),
        "singleton_frames_sha256": digest(old_frames),
        "recipes_sha256": digest({"x_to_empty": records,
                                  "empty_to_full": full_record}),
        "distinct_recipes": len(certificates),
        "signed_paulis_per_recipe": 2 * BITS,
        "exact_anchor_entries_per_recipe": SIZE,
        "monomial_maps_checked_by_separate_kernel": len(cache),
        "proposed_occurrence_profile": {"1": 52, "9": 93},
        "proposed_native_calls": 145,
        "proposed_native_rank_mass": 889,
        "proposed_native_pair_count": 889 * (SIZE // 2),
        "wrapper_occurrence_counts": wrapper_total,
        "certificates": certificates,
    }
    return records, full_record, receipt
