"""Source-bound quotient and small preparation/readout/direct checks.

Clear1nsight, with substantial OpenAI assistance. Apache-2.0.

The inherited PR3467 encoder/decoder and source-bound Gaussian model are
received through the authenticated primary context.  This module does not
execute the 524-event caller.  Its dense checks bind arrays supplied by that
caller; its three small fixtures check preparation, readout formulas, and
both strict direct schedules.  Algebraic index and rank statements concern
observations, not information erasure, physical storage, or operation bounds.
"""

from collections import Counter
from fractions import Fraction
import hashlib
import json


SIZE = 512
D_BANKS = ("D31", "D30", "D29", "D28", "D27")
WORD_KEY = "research/p104-rounded-collector/inputs/WORD.json"
WORD_SHA256 = "cec1fb3fbd0067b500ad5119a62ba60685be718e769374d7ec8abdd2beaa7e50"
TERMINAL_SLOTS = [2, 9, 16, 27, 51]
TERMINAL_SOURCES = ["Y99", "Y100", "Y66", "Y72", "Y80"]
TERMINAL_EVENTS = [1231, 1393, 1459, 1641, 1831]
O_FRAME = [256, 136, 64, 40, 16, 4, 2, 1]


class ObservationError(ValueError):
    """A source, lattice, observation, or retained-output check failed."""


def require(condition, message):
    if not condition:
        raise ObservationError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def digest(value):
    return hashlib.sha256(canonical(value).encode("utf-8")).hexdigest()


def typed_equal(actual, expected):
    if type(actual) is not type(expected):
        return False
    if type(actual) is dict:
        return actual.keys() == expected.keys() and all(
            typed_equal(actual[key], expected[key]) for key in actual)
    if type(actual) in (list, tuple):
        return len(actual) == len(expected) and all(
            typed_equal(a, b) for a, b in zip(actual, expected))
    return actual == expected


def bank_check(values):
    require(type(values) is list and len(values) == SIZE, "512-entry bank required")
    require(all(type(z) is tuple and len(z) == 2
                and all(type(x) is int for x in z) for z in values),
            "Gaussian tuple components must be exact integers, excluding bool")


def parameters_check(parameters):
    require(type(parameters) is list and len(parameters) == 52,
            "52 coefficient banks required")
    require(len({id(values) for values in parameters}) == 52,
            "coefficient bank objects must be distinct")
    for values in parameters:
        bank_check(values)


def zeros():
    return [(0, 0) for _ in range(SIZE)]


def basis(address, scalar=(1, 0)):
    require(type(address) is int and 0 <= address < SIZE, "basis address")
    require(type(scalar) is tuple and len(scalar) == 2
            and all(type(x) is int for x in scalar), "Gaussian basis scalar")
    values = zeros()
    values[address] = scalar
    return values


def plus(left, right):
    return [(a + c, b + d) for (a, b), (c, d) in zip(left, right)]


def minus(left, right):
    return [(a - c, b - d) for (a, b), (c, d) in zip(left, right)]


def total(banks):
    result = zeros()
    for values in banks:
        bank_check(values)
        result = plus(result, values)
    return result


def scaled(values, scalar):
    require(type(scalar) is int, "integer scale required")
    return [(scalar * a, scalar * b) for a, b in values]


def subset_encode(values):
    """Independent finite E_9 formula, without using a codec implementation."""
    bank_check(values)
    powers = [(1, 0)]
    for _ in range(9):
        a, b = powers[-1]
        powers.append((a - b, a + b))
    result = []
    for address in range(SIZE):
        real, imag, subset = 0, 0, address
        while True:
            a, b = values[subset]
            c, d = powers[subset.bit_count()]
            real += a * c - b * d
            imag += a * d + b * c
            if subset == 0:
                break
            subset = (subset - 1) & address
        result.append((real, imag))
    return result


def source_spec(context):
    raw = context["captured"][WORD_KEY]
    require(type(raw) is bytes and hashlib.sha256(raw).hexdigest() == WORD_SHA256,
            "captured WORD hash")
    word = context["word"]
    require(typed_equal(word, json.loads(raw)), "context WORD differs from captured bytes")
    program, structure = word["program"], context["structure"]
    needed, selected = set(D_BANKS) | {"Q7"}, []
    for event in reversed(range(2025)):
        row = program[event]
        if row[1] in needed:
            require(row[0] in ("add", "transport"), "producer opcode")
            selected.append(event)
            if row[0] == "add":
                needed.add(row[2])
    selected.reverse()
    require(len(selected) == 257 and typed_equal(selected, structure["selected"]),
            "actual backward cone binding")
    groups, rows, terminals = [], [], []
    for bank in D_BANKS:
        reads = [event for event in selected if program[event][:2] == ["add", bank]]
        group = []
        for position, event in enumerate(reads):
            literal = program[event]
            require(type(event) is int and literal[3] == "1/4",
                    "actual positive quarter read")
            following = reads[position + 1] if position + 1 < len(reads) else None
            between = [] if following is None else [
                e for e in selected if event < e < following and program[e][1] == bank]
            require(all(program[e][0] == "transport" for e in between)
                    and len(between) <= 1, "actual single-native or empty interval")
            require(not between or type(program[between[0]][4]) is int
                    and program[between[0]][4] == 1, "actual rank-one interval")
            kind = "terminal" if following is None else ("rank_one" if between else "zero")
            actual_path = [e for e in selected if e < event
                           and program[e][:2] == ["transport", bank]]
            source_path = [e for e in selected if e < event
                           and program[e][:2] == ["transport", literal[2]]]
            row = {"bank": bank, "source": literal[2], "event": event,
                   "frame": literal[4], "kind": kind, "next_event": following,
                   "transport_event": between[0] if between else None,
                   "path_to_read": actual_path, "source_path_to_read": source_path}
            inherited = structure["gaps"][len(rows)]
            require(all(typed_equal(inherited[key], value) for key, value in row.items()),
                    "inherited interval differs from actual source")
            group.append(row["source"])
            if following is None:
                terminals.append(len(rows))
            rows.append(row)
        groups.append(group)
        require([row["source"] for row in structure["groups"][bank]] == group,
                "actual source group order")
    require([len(group) for group in groups] == [3, 7, 7, 11, 24], "five group sizes")
    require(len(rows) == 52 and len({row["source"] for row in rows}) == 52,
            "52 disjoint sources")
    require(typed_equal(terminals, TERMINAL_SLOTS), "five terminal slots")
    require([rows[i]["source"] for i in terminals] == TERMINAL_SOURCES,
            "actual terminal source names")
    require([rows[i]["event"] for i in terminals] == TERMINAL_EVENTS,
            "actual terminal read events")
    require(typed_equal(terminals, context["terminal_slots"]), "primary terminal slots")
    return {"groups": groups, "rows": rows, "terminals": terminals,
            "names": [row["source"] for row in rows]}


def check_y(initial_y, spec, model):
    require(type(initial_y) is dict and set(initial_y) == set(spec["names"]),
            "exact 52 Y roles")
    for values in initial_y.values():
        bank_check(values)
        require(model.member(values), "initial Y must be in B9")


def rho5(initial_y, spec, model):
    check_y(initial_y, spec, model)
    result = []
    for group in spec["groups"]:
        summed = total(initial_y[name] for name in group)
        require(all(x % 4 == 0 for z in summed for x in z), "terminal group quarter")
        values = [(a // 4, b // 4) for a, b in summed]
        require(model.member(values), "terminal group quotient must be in B9")
        result.append(values)
    return result


def sigma(readouts, spec, model):
    require(type(readouts) is list and len(readouts) == 5, "five readout banks")
    section = {name: zeros() for name in spec["names"]}
    for slot, values in zip(spec["terminals"], readouts):
        bank_check(values)
        require(model.member(values), "section input must be in B9")
        section[spec["rows"][slot]["source"]] = scaled(values, 4)
    require(rho5(section, spec, model) == readouts, "common strong section identity")
    return section


def decode(context, initial_y):
    return context["admission"].decode_sources(
        context["structure"], context["plans"], context["model"],
        context["source"], context["classifier"], initial_y)


def encode(context, parameters):
    parameters_check(parameters)
    return context["admission"].encode_sources(
        context["structure"], context["plans"], context["model"],
        context["source"], context["classifier"], parameters)


def readout_images(context, dirty, readouts):
    result = {}
    for bank, value in zip(D_BANKS, readouts):
        bank_check(dirty[bank])
        require(context["model"].member(dirty[bank]), "dirty D initial B9 admission")
        path = context["structure"]["cut_paths"][bank]
        result[bank] = context["source"].apply_path(
            plus(dirty[bank], value), path, context["plans"], context["model"])
    return result


def rational_rank(rows):
    matrix = [[Fraction(value) for value in row] for row in rows]
    pivot_row = 0
    for column in range(len(matrix[0])):
        pivot = next((j for j in range(pivot_row, len(matrix))
                      if matrix[j][column]), None)
        if pivot is None:
            continue
        matrix[pivot_row], matrix[pivot] = matrix[pivot], matrix[pivot_row]
        factor = matrix[pivot_row][column]
        matrix[pivot_row] = [x / factor for x in matrix[pivot_row]]
        for row in range(len(matrix)):
            if row != pivot_row and matrix[row][column]:
                factor = matrix[row][column]
                matrix[row] = [a - factor * b for a, b in
                               zip(matrix[row], matrix[pivot_row])]
        pivot_row += 1
        if pivot_row == len(matrix):
            break
    return pivot_row


def quotient_and_rank(context, spec):
    kinds = Counter(row["kind"] for row in spec["rows"])
    require(kinds == {"zero": 32, "rank_one": 15, "terminal": 5},
            "actual interval census")
    profiles = {
        "zero": [max(4 - address.bit_count(), 0) for address in range(SIZE)],
        "rank_one": [max(4 - (address & ~1).bit_count(), 0) for address in range(SIZE)],
        "terminal": [4] * SIZE,
    }
    for kind, exponents in profiles.items():
        inherited = context["classifier"].profile(kind, 9)
        require(typed_equal(exponents, inherited["exponents"]), "retained profile exponents")
    profile_indices = {kind: sum(exponents) for kind, exponents in profiles.items()}
    inherited_index = sum(kinds[kind] * index for kind, index in profile_indices.items())
    strong_index = len(spec["rows"]) * 4 * SIZE
    relative_index = strong_index - inherited_index
    require(profile_indices == {"zero": 187, "rank_one": 280, "terminal": 2048}
            and (inherited_index, strong_index, relative_index) == (20424, 106496, 86072),
            "source-profile and relative indices")
    bank_matrix = [[int(j == slot) for j in range(52)] for slot in spec["terminals"]]
    final_matrix = [[sum(row[column] for row in bank_matrix) for column in range(52)]]
    five_rank, final_rank = rational_rank(bank_matrix), rational_rank(final_matrix)
    require((five_rank, final_rank) == (5, 1), "observable bank ranks")
    diagonal_exponent = sum(address.bit_count() for address in range(SIZE))
    require(diagonal_exponent == 2304, "Newton nonzero triangular diagonal")
    return {
        "interval_counts": dict(sorted(kinds.items())),
        "profile_index_exponents": profile_indices,
        "B52_over_L_index_power_of_2": inherited_index,
        "B52_over_S_index_power_of_2": strong_index,
        "L_over_S_index_power_of_2": relative_index,
        "quotient_statement": "L/S is isomorphic to K/(K intersect S), K=ker(rho5|L), "
                             "via [y] -> [y-sigma(rho5(y))].",
        "rho5_descends_to_L_over_S": False,
        "reason": "rho5(S)=B9^5; the common terminal-source section splits both domains.",
        "E_rank_certificate": "Triangular subset matrix with nonzero diagonal pi^popcount(address).",
        "E_determinant_pi_exponent": diagonal_exponent,
        "five_readout_gaussian_rank": five_rank * SIZE,
        "final_increment_gaussian_rank": final_rank * SIZE,
        "five_readout_coefficient_kernel_gaussian_rank": (52 - five_rank) * SIZE,
        "final_increment_coefficient_kernel_gaussian_rank": (52 - final_rank) * SIZE,
        "returned_coefficient_banks": 52,
        "rank_scope": "Observation maps only; the full restored query shear erases no coefficient data.",
    }


def section_check(context, spec, parameters, initial_y):
    model = context["model"]
    readouts = rho5(initial_y, spec, model)
    expected = [subset_encode(parameters[slot]) for slot in spec["terminals"]]
    require(readouts == expected, "actual group sums differ from E terminal coefficients")
    require(all(model.encode(parameters[slot]) == value
                for slot, value in zip(spec["terminals"], expected)),
            "retained Newton codec differs from subset formula")
    strong = sigma(readouts, spec, model)
    kernel = {name: minus(initial_y[name], strong[name]) for name in spec["names"]}
    require(all(not any(z != (0, 0) for z in value)
                for value in rho5(kernel, spec, model)), "section remainder not in ker rho5")
    require(decode(context, initial_y) == parameters, "original 52 coefficient decode")
    strong_parameters = decode(context, strong)
    expected_strong = [parameters[j][:] if j in spec["terminals"] else zeros()
                       for j in range(52)]
    require(strong_parameters == expected_strong, "strong section coefficient projection")
    return readouts, strong, kernel


def direct_checks(parameters, query, spec, increment, direct_module):
    bank_check(query)
    expected_q = plus(query, increment)
    outputs = []
    for mode in ("zero", "inplace"):
        result = direct_module.run_direct(parameters, query, spec["terminals"], mode)
        require(result["coefficients"] == parameters, "direct schedule erased coefficient data")
        require(result["query"] == expected_q, "direct observation differs from readout formula")
        receipt = result["receipt"]
        require(receipt["status"] == "PASS" and receipt["real_scratch_final"] == 0,
                "direct scratch/result status")
        require(mode != "zero" or receipt["owned_gaussian_scratch_zero_erased"] is True,
                "owned direct scratch zero erasure")
        outputs.append({
            "mode": mode,
            "output_q_sha256": digest(result["query"]),
            "returned_coefficients_sha256": digest(result["coefficients"]),
            "returned_coefficient_banks": 52,
            "observed_primitives": receipt["observed_primitives"],
            "real_scratch_final": 0,
            "instruction_sha256": receipt["instruction_sha256"],
        })
    return outputs


def fixture_parameters(kind):
    parameters = [zeros() for _ in range(52)]
    if kind in ("nonterminal", "mixed"):
        parameters[44] = basis(15)
    if kind == "terminal_difference":
        parameters[2], parameters[9] = basis(0), basis(0, (-1, 0))
    elif kind == "mixed":
        for slot, address, scalar in zip(
                TERMINAL_SLOTS, (0, 1, 2, 4, 8),
                ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1))):
            parameters[slot] = basis(address, scalar)
    else:
        require(kind == "nonterminal", "known discriminating fixture")
    return parameters


def nonterminal_witness(context, spec, initial_y):
    row, following = spec["rows"][44:46]
    require(typed_equal(
        {key: row[key] for key in ("bank", "source", "event", "kind", "frame", "next_event")},
        {"bank": "D27", "source": "Y91", "event": 1817, "kind": "zero",
         "frame": O_FRAME, "next_event": 1819}), "named nonterminal witness source")
    require(following["source"] == "Y90" and following["event"] == 1819
            and typed_equal(following["frame"], O_FRAME), "paired cancellation source")
    p = initial_y["Y91"]
    require(initial_y["Y90"] == scaled(p, -1), "Y91/Y90 opposite sources")
    require({name for name, values in initial_y.items() if any(z != (0, 0) for z in values)}
            == {"Y91", "Y90"}, "nonterminal witness support")
    decoded = context["model"].decode(p)
    witness = next(((address, part, value) for address, z in enumerate(decoded)
                    for part, value in enumerate(z) if value % 4), None)
    require(witness is not None, "p must lie outside 4B9")
    physical = context["source"].apply_path(
        p, row["source_path_to_read"], context["plans"], context["model"])
    d_path_value = context["source"].apply_path(
        p, row["path_to_read"], context["plans"], context["model"])
    expected = [(-4, 0) if address & 15 == 15 else (0, 0) for address in range(SIZE)]
    require(physical == d_path_value == expected, "actual framed nonterminal profile")
    require(all(x % 4 == 0 for z in physical for x in z), "physical quarter exactness")
    quarter = [(a // 4, b // 4) for a, b in physical]
    support = [address for address, value in enumerate(quarter) if value != (0, 0)]
    require(len(support) == 32 and all(quarter[address] == (-1, 0) for address in support),
            "32 negative unit intermediate entries")
    following_physical = context["source"].apply_path(
        initial_y["Y90"], following["source_path_to_read"],
        context["plans"], context["model"])
    require(plus(physical, following_physical) == zeros(), "next quarter cancellation")
    return {
        "source_events": [1817, 1819],
        "coefficient_slot": 44,
        "coefficient_basis_address": 15,
        "prepared_nonzero_sources": ["Y91", "Y90"],
        "actual_Y91_read_path": row["source_path_to_read"],
        "actual_Y90_read_path": following["source_path_to_read"],
        "actual_D27_read_path": row["path_to_read"],
        "source_path_matches_D_path": True,
        "outside_4B9_decoded_coefficient_witness": list(witness),
        "actual_intermediate_quarter_sha256": digest(quarter),
        "negative_unit_intermediate_entries": len(support),
        "intermediate_then_cancelled": True,
    }


def small_fixture(context, spec, direct_module, kind):
    parameters = fixture_parameters(kind)
    initial_y = encode(context, parameters)
    readouts, strong, kernel = section_check(context, spec, parameters, initial_y)
    increment = total(readouts)
    coefficient_sum = total(parameters[slot] for slot in spec["terminals"])
    require(increment == subset_encode(coefficient_sum), "summed readout linearity")
    result = {
        "kind": kind,
        "scope": "Pinned preparation/decoder, readout formula, and strict direct checks; "
                 "no 524-event caller replay.",
        "parameters_sha256": digest(parameters),
        "prepared_Y_sha256": digest(initial_y),
        "strong_section_Y_sha256": digest(strong),
        "section_kernel_remainder_sha256": digest(kernel),
        "five_readouts_sha256": digest(readouts),
        "final_increment_sha256": digest(increment),
        "direct_modes": direct_checks(
            parameters, subset_encode(basis(0)), spec, increment, direct_module),
    }
    if kind == "nonterminal":
        require(readouts == [zeros() for _ in range(5)] and increment == zeros(),
                "nonterminal observation must vanish")
        result["witness"] = nonterminal_witness(context, spec, initial_y)
    elif kind == "terminal_difference":
        value = subset_encode(basis(0))
        require(readouts == [value, scaled(value, -1), zeros(), zeros(), zeros()]
                and increment == zeros(), "terminal difference observation")
        require(initial_y == strong, "terminal difference must already be in strong section")
        result["five_readout_nonzero_banks"] = 2
        result["final_increment_zero"] = True
    else:
        require(kind == "mixed" and initial_y != strong, "mixed kernel must be retained")
        require({name for name, values in strong.items() if any(z != (0, 0) for z in values)}
                == set(TERMINAL_SOURCES), "exact five-active strong section")
        explicit = [
            (1 - ((x >> 0) & 1) - ((x >> 1) & 1) + ((x >> 2) & 1),
             -((x >> 0) & 1) + ((x >> 1) & 1) - ((x >> 2) & 1) + 2 * ((x >> 3) & 1))
            for x in range(SIZE)]
        require(increment == explicit and any(z != (0, 0) for z in increment),
                "mixed nonzero explicit readout")
        require(parameters[44] == basis(15), "nonterminal output remains nonzero")
        result["strong_nonzero_sources"] = TERMINAL_SOURCES[:]
        result["bypassed_coefficient_slot_44_retained"] = True
        result["first_16_increment_entries"] = increment[:16]
    return result


def analyze(primary_result, direct_module):
    """Bind a primary literal result, then check the quotient's small fixtures."""
    require(type(primary_result) is dict, "primary result object")
    context = primary_result["context"]
    spec = source_spec(context)
    parameters = primary_result["parameters"]
    parameters_check(parameters)
    readouts, strong, kernel = section_check(
        context, spec, parameters, primary_result["initial_y"])
    dirty = primary_result["initial_dirty"]
    require(type(dirty) is dict and set(dirty) == set(D_BANKS) | {"Q7"},
            "six separately admitted dirty roles")
    bank_check(dirty["Q7"])
    require(context["model"].member(dirty["Q7"]), "dirty query initial B9 admission")
    cut = primary_result["cut"]
    require(type(cut) is dict and set(cut) == set(D_BANKS) | {"Q7"}, "six supplied cut roles")
    cut_images = readout_images(context, dirty, readouts)
    require(all(typed_equal(cut[bank], values) for bank, values in cut_images.items()),
            "supplied physical cut differs from five readout images")
    expected_q = plus(dirty["Q7"], total(readouts))
    require(typed_equal(primary_result["output_q"], expected_q),
            "supplied literal Q output differs from final observation")
    strong_images = readout_images(context, dirty, rho5(strong, spec, context["model"]))
    require(cut_images == strong_images, "general and strong physical cut readouts differ")
    indices = quotient_and_rank(context, spec)
    fixtures = [small_fixture(context, spec, direct_module, kind) for kind in
                ("nonterminal", "terminal_difference", "mixed")]
    return {
        "status": "PASS_SOURCE_BOUND_OBSERVABILITY",
        "scope": "Dense supplied literal endpoint binding plus three bounded "
                 "preparation/readout/direct fixtures; no caller replay in this module.",
        "WORD_sha256": WORD_SHA256,
        "source_groups": [
            {"bank": bank, "size": len(group), "terminal_slot": slot,
             "terminal_source": spec["rows"][slot]["source"],
             "terminal_event": spec["rows"][slot]["event"]}
            for bank, group, slot in zip(D_BANKS, spec["groups"], spec["terminals"])],
        "quotient_and_rank": indices,
        "dense_primary_binding": {
            "parameters_sha256": digest(parameters),
            "actual_prepared_Y_sha256": digest(primary_result["initial_y"]),
            "strong_section_Y_sha256": digest(strong),
            "kernel_remainder_sha256": digest(kernel),
            "five_readout_sha256": digest(readouts),
            "five_physical_cut_readouts_sha256": digest(cut_images),
            "actual_Q_output_sha256": digest(primary_result["output_q"]),
            "general_and_strong_five_readouts_equal": True,
            "original_52_parameter_decode_checked": True,
            "strong_decode_has_zero_nonterminal_parameters": True,
            "strong_section_is_not_permission_to_erase_original_coefficients": True,
        },
        "fixtures": fixtures,
    }
