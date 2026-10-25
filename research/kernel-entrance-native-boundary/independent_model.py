"""Exact model for the fixed PR589 kernel-entrance composition.

Prepared by Clear1nsight with substantial OpenAI assistance. Apache-2.0.
No predecessor implementation, exporter, or native checker is imported.
This module checks finite F2 semantics and rational frame geometry; it does
not implement physical address operators, owner allocation, or bank hosting.
"""

import copy
import hashlib
import json
from collections import Counter
from fractions import Fraction
from math import gcd


PIVOT = 444
PARTNER = 470
ENTRANCE = 79
WIDTH = 8
PORTS = 111
HELPERS = 439
PERSISTENT = 2 * PORTS + HELPERS
SELECTION = [{"a": PIVOT, "partners": [PARTNER],
              "new_frame_id": ENTRANCE, "E_dimension": 1}]


class ModelError(ValueError):
    """A checked premise of this fixed finite model did not hold."""


def require(condition, message):
    if not condition:
        raise ModelError(message)


def canonical(value):
    """JSON bytes distinguish integers from Booleans and floats."""
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      allow_nan=False).encode("utf-8")


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def normalise(word):
    """Independent occurrence-parity implementation of the fixed domain."""
    require(type(word) is dict, "word must be an object")
    require(all(type(word.get(key)) is int for key in ("h", "v", "R")),
            "integer word dimensions")
    require((word["h"], word["v"], word["R"]) ==
            (WIDTH, PORTS, HELPERS), "fixed word dimensions")
    retained, rows = word.get("ret"), word.get("scatter")
    require(type(retained) is list and len(retained) in (9, 10),
            "fixed retained-slot contract")
    require(canonical(retained[:9]) == canonical(list(range(472, 481))),
            "original retained helper identities")
    require(len(retained) == 9 or type(retained[9]) is int and retained[9] == 472,
            "additional slot must alias helper 472")
    require(type(rows) is list and len(rows) == PORTS, "complete scatter rows")
    total = 0
    result = copy.deepcopy(word)
    result["scatter"] = []
    for row in rows:
        require(type(row) is list and len(row) <= 4096,
                "bounded occurrence row")
        total += len(row)
        require(total <= 65536, "bounded total scatter occurrences")
        require(all(type(slot) is int and 0 <= slot < len(retained)
                    for slot in row), "valid retained-slot indices")
        counts = Counter(row)
        result["scatter"].append(sorted(slot for slot, count in counts.items()
                                        if count % 2))
    return result


def gauge(word):
    """Reconstruct the exact archived transformation without importing it."""
    result = copy.deepcopy(word)
    result["start"][PIVOT] = ENTRANCE
    for gate in result["D"]:
        gate[2] = [source for source in gate[2] if source != PIVOT]
    result["A"].insert(0, [ENTRANCE, PARTNER, [PIVOT]])
    result["C"].append([1, PARTNER, [PIVOT]])
    return result


def validate_selection(selection, candidate_word):
    """Bind the exact nonempty declaration to the finite entrance contract.

    The complete source-word equality is checked by analyse_case. This local
    guard checks its selection and the particular entrance/shear footprint;
    an empty physical source-owner/donor inventory is not made nonempty here.
    """
    require(canonical(selection) == canonical(SELECTION),
            "selection does not name the fixed kernel entrance")
    require(type(candidate_word) is dict, "candidate must be an object")
    require(type(candidate_word.get("start")) is list and
            len(candidate_word["start"]) == PERSISTENT,
            "complete candidate start map")
    require(type(candidate_word["start"][PIVOT]) is int and
            candidate_word["start"][PIVOT] == ENTRANCE,
            "selection is not bound to the pivot entrance")
    require(type(candidate_word.get("A")) is list and candidate_word["A"] and
            canonical(candidate_word["A"][0]) ==
            canonical([ENTRANCE, PARTNER, [PIVOT]]),
            "selection is not bound to the entrance shear")
    require(type(candidate_word.get("C")) is list and candidate_word["C"] and
            canonical(candidate_word["C"][-1]) ==
            canonical([1, PARTNER, [PIVOT]]),
            "selection is not bound to the exit shear")
    require(all(PIVOT not in gate[2] for gate in candidate_word["D"]),
            "pivot remains in the zero-frame compensation")
    return True


def reduced_rows(rows, width=WIDTH):
    """Gauss-Jordan elimination over Q, independent of exported dimensions."""
    matrix = [[Fraction(value) for value in row] for row in rows]
    require(all(len(row) == width for row in matrix), "rational row width")
    pivots = []
    for column in range(width):
        position = len(pivots)
        selected = next((index for index in range(position, len(matrix))
                         if matrix[index][column]), None)
        if selected is None:
            continue
        matrix[position], matrix[selected] = matrix[selected], matrix[position]
        coefficient = matrix[position][column]
        matrix[position] = [value / coefficient for value in matrix[position]]
        for index in range(len(matrix)):
            if index != position and matrix[index][column]:
                coefficient = matrix[index][column]
                matrix[index] = [left - coefficient * right for left, right
                                 in zip(matrix[index], matrix[position])]
        pivots.append(column)
    return matrix[:len(pivots)], pivots


def primitive_integer_row(row):
    denominator = 1
    for value in row:
        denominator = denominator * value.denominator // gcd(
            denominator, value.denominator)
    integers = [int(value * denominator) for value in row]
    divisor = 0
    for value in integers:
        divisor = gcd(divisor, abs(value))
    require(divisor != 0, "zero annihilator row")
    return [value // divisor for value in integers]


def geometry(word):
    labels = word["lines"]
    require(all(type(row) is list and len(row) == WIDTH and
                all(type(value) is int for value in row) for row in labels),
            "integer source label rows")
    bases = []
    for frame in word["frames"]:
        require(all(type(index) is int and 0 <= index < len(labels)
                    for index in frame), "valid frame label indices")
        bases.append(reduced_rows([labels[index] for index in frame])[0])
    ranks = list(map(len, bases))
    entrance_basis, pivots = reduced_rows(
        [labels[index] for index in word["frames"][ENTRANCE]])
    annihilator = []
    for free in range(WIDTH):
        if free in pivots:
            continue
        row = [Fraction(int(index == free)) for index in range(WIDTH)]
        for basis, pivot in zip(entrance_basis, pivots):
            row[pivot] = -basis[free]
        annihilator.append(primitive_integer_row(row))
    require(ranks[ENTRANCE] == 1, "entrance has rational rank one")
    require(len(reduced_rows(annihilator)[0]) == WIDTH - ranks[ENTRANCE],
            "complete independent entrance annihilator")
    require(all(sum(left * right for left, right in zip(a, b)) == 0
                for a in annihilator for b in entrance_basis),
            "entrance basis/annihilator orthogonality")
    containment_cache = {}

    def contained(left, right):
        pair = left, right
        if pair not in containment_cache:
            containment_cache[pair] = (len(reduced_rows(
                bases[left] + bases[right])[0]) == ranks[right])
        return containment_cache[pair]

    witness = {
        "frame": ENTRANCE,
        "label_indices": word["frames"][ENTRANCE],
        "integer_label_rows": [labels[index]
                               for index in word["frames"][ENTRANCE]],
        "rational_rank": ranks[ENTRANCE],
        "annihilator_integer_rows": annihilator,
        "annihilator_rational_rank": len(reduced_rows(annihilator)[0]),
        "basis_annihilator_product_is_zero": True,
    }
    return ranks, contained, witness


def events(word, sections=("D", "A", "scatter", "B", "C")):
    result = []
    for section in sections:
        if section == "scatter":
            for slot, helper in enumerate(word["ret"]):
                result.append(("copy", PERSISTENT, helper))
                for target, row in enumerate(word["scatter"]):
                    # Occurrences, not membership: normalization is a separate
                    # checked implication before the exporter is used.
                    for occurrence in row:
                        if occurrence == slot:
                            result.append(("add", PORTS + target, PERSISTENT))
                result.append(("erase", PERSISTENT, helper))
        else:
            for frame, destination, sources in word[section]:
                require(type(destination) is int and
                        0 <= destination < PERSISTENT and
                        all(type(source) is int and 0 <= source < PERSISTENT
                            for source in sources), "scalar gate roles")
                require(len(set([destination, *sources])) == len(sources) + 1,
                        "distinct scalar gate operands")
                result.extend(("add", destination, source) for source in sources)
    return result


def scalar_state(word, sections=("D", "A", "scatter", "B", "C"),
                 reverse=False):
    """All formal F2 columns, with a separate clean singleton COPY slot."""
    state = [1 << register for register in range(PERSISTENT)] + [0]
    live = None
    saved = None
    count = Counter()
    sequence = events(word, sections)
    if reverse:
        sequence = [("erase" if kind == "copy" else
                     "copy" if kind == "erase" else kind, target, source)
                    for kind, target, source in reversed(sequence)]
    for kind, target, source in sequence:
        if kind == "add":
            require(target != PERSISTENT and (live is None or target != live),
                    "a live snapshot or its center was mutated")
            require(source != PERSISTENT or live is not None,
                    "reading inactive COPY workspace")
            state[target] ^= state[source]
        elif kind == "copy":
            require(live is None and state[PERSISTENT] == 0,
                    "COPY requires inactive clean workspace")
            state[PERSISTENT] = state[source]
            live, saved = source, state[source]
        elif kind == "erase":
            require(live == source and state[PERSISTENT] == saved == state[source],
                    "ERASE must restore its exact original snapshot")
            state[PERSISTENT] = 0
            live = saved = None
        else:
            raise ModelError("unknown scalar event")
        count[kind] += 1
    require(live is None and state[PERSISTENT] == 0, "COPY workspace restored")
    return state, dict(sorted(count.items()))


def expected_decoder():
    return [(1 << register) ^ (1 << (register - PORTS))
            if PORTS <= register < 2 * PORTS else 1 << register
            for register in range(PERSISTENT)] + [0]


def support(bits):
    return [register for register in range(PERSISTENT) if bits >> register & 1]


def endpoint_differences(actual, expected):
    return [{"output": register, "inputs": support(left ^ right)}
            for register, (left, right) in enumerate(zip(actual, expected))
            if left != right]


def invoice(word, ranks, contained):
    """Source-word geometry and telescoping, never native record recounting."""
    initial, final = word["start"], word["final"]
    require(len(initial) == len(final) == PERSISTENT,
            "complete frame endpoints")
    require(all(type(frame) is int and 0 <= frame < len(ranks)
                for frame in initial + final), "valid frame endpoints")
    current = list(initial)
    move_histogram = Counter()
    move_count = 0
    copy_slots = []
    non_scatter_adds = 0

    def climb(register, frame):
        nonlocal move_count
        old = current[register]
        if old == frame:
            return
        require(ranks[old] < ranks[frame] and contained(old, frame),
                "source word contains an illegal rational frame advance")
        move_histogram[ranks[frame] - ranks[old]] += 1
        move_count += 1
        current[register] = frame

    for section in ("D", "A", "scatter", "B", "C"):
        if section == "scatter":
            require(all(ranks[current[PORTS + target]] == 0
                        for target in range(PORTS)), "scatter target frames")
            copy_slots = [{"slot": slot, "helper": helper,
                           "frame": current[helper],
                           "rank": ranks[current[helper]]}
                          for slot, helper in enumerate(word["ret"])]
        else:
            for frame, destination, sources in word[section]:
                require(type(frame) is int and 0 <= frame < len(ranks),
                        "valid gate frame")
                for register in [destination, *sources]:
                    climb(register, frame)
                non_scatter_adds += len(sources)
    for register, frame in enumerate(final):
        climb(register, frame)
    initial_sum = sum(ranks[frame] for frame in initial)
    final_sum = sum(ranks[frame] for frame in final)
    move_mass = final_sum - initial_sum
    require(move_mass == sum(rank * count for rank, count in move_histogram.items()),
            "telescoping and direct source-frame invoice disagree")
    copy_mass = sum(row["rank"] for row in copy_slots)
    scatter_adds = sum(len(row) for row in word["scatter"])
    histogram = move_histogram + Counter(row["rank"] for row in copy_slots)
    return {
        "status": "COMPUTED_EXACT_KERNEL_ENTRANCE_WORD_INVOICE",
        "frame_count": len(ranks),
        "initial_frame_rank_sum": initial_sum,
        "final_frame_rank_sum": final_sum,
        "move_rank_mass": move_mass,
        "nested_moves": move_count,
        "move_histogram": {str(rank): count for rank, count
                           in sorted(move_histogram.items())},
        "retained_slots": copy_slots,
        "copies": len(copy_slots),
        "copy_rank_mass": copy_mass,
        "raw_rank_mass": move_mass + copy_mass,
        "paid_histogram": {str(rank): count for rank, count
                           in sorted(histogram.items())},
        "non_scatter_adds": non_scatter_adds,
        "normalised_scatter_adds": scatter_adds,
        "total_scalar_adds": non_scatter_adds + scatter_adds,
        "records": move_count + non_scatter_adds + scatter_adds + 2 * len(copy_slots),
        "rank_method": "exact rational source labels and telescoping dimensions",
    }


def analyse_case(input_word, normalised_word, candidate_word):
    """Check one fixed baseline/active-alias composition and return evidence."""
    expected_normal = normalise(input_word)
    require(canonical(normalised_word) == canonical(expected_normal),
            "public normalization differs from independent parity model")
    require(canonical(normalise(normalised_word)) == canonical(normalised_word),
            "normal form is not idempotent")
    expected_candidate = gauge(normalised_word)
    require(canonical(candidate_word) == canonical(expected_candidate),
            "candidate differs from the exact source-derived gauge")
    require(canonical(normalise(gauge(input_word))) ==
            canonical(gauge(normalise(input_word))),
            "normalization and kernel gauge do not commute")
    validate_selection(SELECTION, candidate_word)

    raw, _ = scalar_state(normalised_word, ("A", "scatter", "B"))
    dirt_mask = ((1 << HELPERS) - 1) << (2 * PORTS)
    source_mask = (1 << PORTS) - 1
    target_mask = source_mask << PORTS
    compensation, _ = scalar_state(normalised_word, ("D",))
    for target in range(PORTS):
        require(raw[PORTS + target] & source_mask == 1 << target,
                "raw source-to-target map differs from identity")
        require(raw[PORTS + target] & target_mask == 1 << (PORTS + target),
                "raw target map differs from identity")
        require(compensation[PORTS + target] ^ (1 << (PORTS + target)) ==
                raw[PORTS + target] & dirt_mask,
                "D does not equal the source-derived raw helper response")
    require(all(raw[register] & target_mask == 0
                for register in range(PERSISTENT)
                if not PORTS <= register < 2 * PORTS),
            "raw source/helper output depends on targets")
    kernel_support = {
        str(helper): [target for target in range(PORTS)
                      if raw[PORTS + target] >> helper & 1]
        for helper in (PIVOT, PARTNER)
    }
    require(kernel_support[str(PIVOT)] == kernel_support[str(PARTNER)],
            "the actual raw word does not have the declared kernel pair")
    require(len(kernel_support[str(PIVOT)]) == 55,
            "fixed kernel response weight")

    ranks, contained, frame_witness = geometry(normalised_word)
    first = {}
    for frame, destination, sources in normalised_word["A"] + normalised_word["B"]:
        for register in [destination, *sources]:
            if register in (PIVOT, PARTNER):
                first.setdefault(register, frame)
    require(first == {PIVOT: ENTRANCE, PARTNER: ENTRANCE},
            "declared pair does not share its first raw contact frame")
    frame_witness["first_raw_contacts"] = [
        {"helper": helper, "frame": first[helper],
         "entrance_contained": contained(ENTRANCE, first[helper])}
        for helper in (PIVOT, PARTNER)]

    expected = expected_decoder()
    original_state, original_events = scalar_state(normalised_word)
    candidate_state, candidate_events = scalar_state(candidate_word)
    reverse_state, reverse_events = scalar_state(candidate_word, reverse=True)
    occurrence_state, _ = scalar_state(gauge(input_word))
    require(original_state == candidate_state == reverse_state == occurrence_state == expected,
            "finite all-column decoder or restored dirt differs")
    candidate_raw, _ = scalar_state(candidate_word, ("A", "scatter", "B"))
    require(all(not (candidate_raw[PORTS + target] >> PIVOT & 1)
                for target in range(PORTS)), "gauged pivot response is nonzero")
    original_invoice = invoice(normalised_word, ranks, contained)
    candidate_invoice = invoice(candidate_word, ranks, contained)
    require(candidate_invoice["total_scalar_adds"] == candidate_events["add"],
            "source-word ADD invoice and independent scalar events differ")

    missing_exit = copy.deepcopy(candidate_word)
    removed_exit = missing_exit["C"].pop()
    bad_state, _ = scalar_state(missing_exit)
    missing_exit_witness = endpoint_differences(bad_state, expected)
    require(missing_exit_witness == [{"output": PARTNER, "inputs": [PIVOT]}],
            "missing-exit dirty-state witness differs")
    wrong_selection = copy.deepcopy(SELECTION)
    wrong_selection[0]["partners"] = [223]
    wrong_partner_support = [target for target in range(PORTS)
                             if raw[PORTS + target] >> 223 & 1]
    wrong_partner_differences = sorted(set(kernel_support[str(PIVOT)]) ^
                                       set(wrong_partner_support))
    require(wrong_partner_differences,
            "wrong-partner control must violate the actual raw kernel relation")
    first_bad_target = wrong_partner_differences[0]
    try:
        validate_selection(wrong_selection, candidate_word)
    except ModelError as error:
        wrong_selection_reason = str(error)
    else:
        raise ModelError("wrong declared partner was accepted")

    return {
        "status": "PASS_INDEPENDENT_KERNEL_ENTRANCE_MODEL",
        "input_word_sha256": digest(input_word),
        "normalised_word_sha256": digest(normalised_word),
        "candidate_word_sha256": digest(candidate_word),
        "normalisation": {
            "input_occurrences": sum(map(len, input_word["scatter"])),
            "normalised_terms": sum(map(len, normalised_word["scatter"])),
            "retained_slots_preserved": True,
            "idempotent": True,
            "gauge_commutes": True,
            "slot_use_counts": [sum(row.count(slot) for row in normalised_word["scatter"])
                                for slot in range(len(normalised_word["ret"]))],
        },
        "kernel": {
            "pivot": PIVOT, "partner": PARTNER,
            "raw_target_supports": kernel_support,
            "equal_response_weight": len(kernel_support[str(PIVOT)]),
            "raw_compensation_matches_all_D_columns": True,
            "raw_source_to_target_identity": True,
            "raw_target_to_target_identity": True,
            "raw_z_has_no_target_dependence": True,
            "gauged_pivot_target_column_is_zero": True,
        },
        "entrance_geometry": frame_witness,
        "selection": copy.deepcopy(SELECTION),
        "scalar": {
            "persistent_columns": PERSISTENT,
            "arbitrary_dirty_helper_columns": HELPERS,
            "fresh_copy_slots": 1,
            "original_events": original_events,
            "candidate_events": candidate_events,
            "reverse_events": reverse_events,
            "all_persistent_outputs_match_decoder": True,
            "every_erase_matches_its_snapshot": True,
            "workspace_zero_at_end": True,
            "occurrence_and_normal_form_outputs_equal": True,
            "reverse_scope": "F2 scalar word only; no physical inverse-frame compiler",
        },
        "baseline_invoice": original_invoice,
        "invoice": candidate_invoice,
        "delta": {
            key: candidate_invoice[key] - original_invoice[key]
            for key in ("initial_frame_rank_sum", "final_frame_rank_sum",
                        "move_rank_mass", "nested_moves", "copy_rank_mass",
                        "raw_rank_mass", "non_scatter_adds",
                        "normalised_scatter_adds", "total_scalar_adds", "records")
        },
        "controls": {
            "missing_exit_shear": {
                "removed_gate": removed_exit,
                "endpoint_differences": missing_exit_witness,
            },
            "wrong_declared_partner": {
                "selection": wrong_selection,
                "model_rejected": True,
                "reason": wrong_selection_reason,
                "declared_partner_response_support": wrong_partner_support,
                "kernel_relation_failing_target_indices": wrong_partner_differences,
                "first_kernel_failure": {
                    "target_index": first_bad_target,
                    "target_register": PORTS + first_bad_target,
                    "pivot_input_coefficient":
                        (raw[PORTS + first_bad_target] >> PIVOT) & 1,
                    "declared_partner_input_coefficient":
                        (raw[PORTS + first_bad_target] >> 223) & 1,
                },
                "native_acceptance": "must be tested separately on the unchanged valid stream",
            },
        },
        "scope": {
            "physical_source_owner_map_supplied": False,
            "physical_donor_map_supplied": False,
            "physical_bank_or_hosting_admission": False,
            "selected_zero_entrance_H2_admission": False,
            "native_execution_performed_by_this_model": False,
            "new_kernel_census_or_saving_claimed": False,
        },
    }
