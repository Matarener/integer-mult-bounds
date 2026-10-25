#!/usr/bin/env python3
"""Independent literal replay of the restored first-collector caller.

Clear1nsight, with substantial OpenAI assistance. Apache-2.0.
Gaussian arithmetic and the Y-path coefficient construction are adapted from
our independently written PR3467 independent.py, frozen at 4e4b08c689242f7f.
This file imports no predecessor or primary executable. The new source scan,
selective return schedule, full-array endpoint checks and controls are local.
The predecessor's universal module and native-covariance proofs are inherited;
their historical basis suites are not rerun here.
"""

import argparse
from collections import Counter
from fractions import Fraction
import gzip
import hashlib
import io
import json
from pathlib import Path


WORD_SHA256 = "cec1fb3fbd0067b500ad5119a62ba60685be718e769374d7ec8abdd2beaa7e50"
NATIVE_SHA256 = "ab91c78835c3e10cf3b2cb8a5d4e0b7cfc3df1ae5a811298d27842f2193e1e3d"
SIZE = 512
RANK = 9
D_BANKS = ("D31", "D30", "D29", "D28", "D27")
DIRTY = (*D_BANKS, "Q7")
O_FRAME = (256, 136, 64, 40, 16, 4, 2, 1)
P_FRAME = (364,)
ZERO = (0, 0)
PI = ((1, 0), (1, 1), (0, 2), (-2, 2), (-4, 0))


class ReplayFailure(ValueError):
    """A precisely located arithmetic, lifetime or endpoint rejection."""

    def __init__(self, record):
        super().__init__(record["kind"])
        self.record = record


def need(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def digest(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def strict_json(raw):
    def pairs(items):
        out = {}
        for key, value in items:
            need(key not in out, "duplicate source JSON key")
            out[key] = value
        return out
    def forbidden(value):
        raise ValueError("noninteger JSON number: " + value)
    return json.loads(raw, object_pairs_hook=pairs,
                      parse_float=forbidden, parse_constant=forbidden)


def read_pinned(path, expected):
    path = Path(path)
    need(path.is_file() and not path.is_symlink(), "regular scientific input required")
    with path.open("rb") as handle:
        raw = handle.read(1048577)
    need(len(raw) <= 1048576, "scientific input capacity")
    need(hashlib.sha256(raw).hexdigest() == expected, "scientific source SHA256 mismatch")
    return raw


def read_inputs(word_path, native_path):
    word = strict_json(read_pinned(word_path, WORD_SHA256))
    compressed = read_pinned(native_path, NATIVE_SHA256)
    with gzip.GzipFile(fileobj=io.BytesIO(compressed)) as handle:
        raw = handle.read(8388609)
    need(len(raw) <= 8388608, "native expansion capacity")
    return word, strict_json(raw)


def native_bindings(word, archive):
    need(len(word["program"]) == 5398, "frozen word length")
    need(len(word["initial_frames"]) == 358, "frozen public role count")
    need(len(archive["transports"]) == 1245, "frozen native class count")
    need(word["chart"] == archive["chart"], "native chart binding")
    bound = {}
    for record in archive["transports"]:
        recipe = record["recipe"]
        need(type(recipe["rank"]) is int and 1 <= recipe["rank"] <= RANK, "native rank")
        for event in record["events"]:
            need(type(event) is int and 0 <= event < 5398 and event not in bound,
                 "unique native occurrence")
            literal = word["program"][event]
            need(literal[0] == "transport", "native occurrence opcode")
            need(literal[2:] == [record["old"], record["new"], recipe["rank"]],
                 "native occurrence/frame/rank binding")
            bound[event] = recipe
    expected = {i for i, event in enumerate(word["program"]) if event[0] == "transport"}
    need(set(bound) == expected and len(bound) == 2070, "all native occurrences bound")
    return bound


def select_source(word):
    program, needed, selected = word["program"], set(DIRTY), []
    for event in reversed(range(2025)):
        row = program[event]
        if row[1] in needed:
            need(row[0] in ("add", "transport"), "producer operation alphabet")
            selected.append(event)
            if row[0] == "add":
                needed.add(row[2])
    selected.reverse()
    ys = {"Y" + str(i) for i in (*range(22, 33), *range(63, 104))}
    need(needed == ys | set(DIRTY) and len(selected) == 257, "exact producer cone")
    need(all(word["initial_frames"][bank] == [] for bank in needed), "empty caller frames")
    groups, slots = source_slots(program, selected)
    compensation = [i for i in selected if program[i][:2] == ["add", "Q7"]]
    need(compensation == [908, 910, 912, 914, 916], "five initial dirty compensations")
    need([program[i][2] for i in compensation] == list(D_BANKS), "dirty compensation order")
    need(all(Fraction(str(program[i][3])) == -1 and program[i][4] == []
             for i in compensation), "dirty compensation coefficients and frame")
    need([i for i in selected if program[i][:2] == ["transport", "Q7"]] == [972],
         "single Q frame map")
    reverse = [(i, True) for i in reversed(selected) if i not in compensation]
    need(len(reverse) == 252, "selective return count")
    check_collector(program)
    return {"cone": selected, "roles": sorted(needed), "groups": groups, "slots": slots,
            "compensation": compensation, "reverse": reverse}


def source_slots(program, selected):
    paths = {bank: [] for bank in (*DIRTY, *("Y" + str(i) for i in range(104)))}
    groups = {bank: [] for bank in D_BANKS}
    for event in selected:
        row = program[event]
        if row[0] == "transport":
            paths[row[1]].append(event)
        elif row[1] in groups:
            need(str(row[3]) == "1/4" and row[2].startswith("Y"), "group quarter read")
            groups[row[1]].append({"event": event, "source": row[2], "bank": row[1],
                                   "source_path": paths[row[2]][:], "frame": row[4]})
    need([len(groups[bank]) for bank in D_BANKS] == [3, 7, 7, 11, 24], "group lengths")
    slots = []
    for bank in D_BANKS:
        rows = groups[bank]
        for index, row in enumerate(rows):
            following = rows[index + 1]["event"] if index + 1 < len(rows) else None
            between = [] if following is None else [i for i in selected
                if row["event"] < i < following and program[i][1] == bank]
            need(all(program[i][0] == "transport" for i in between), "pure native gap")
            need(len(between) <= 1, "single native per nonterminal gap")
            if between:
                need(program[between[0]][4] == 1, "rank-one interval")
            kind = "terminal" if following is None else ("rank_one" if between else "zero")
            slots.append({**row, "kind": kind, "next_event": following,
                          "transport_event": between[0] if between else None})
    need(len({slot["source"] for slot in slots}) == 52, "disjoint source groups")
    need(Counter(slot["kind"] for slot in slots) == {"zero": 32, "rank_one": 15, "terminal": 5},
         "inherited interval census")
    return groups, slots


def check_collector(program):
    actual = program[2025:2040]
    need(actual[0] == ["zero", "C", list(O_FRAME)], "literal collector allocation")
    need(actual[6] == ["transport", "C", list(O_FRAME), list(P_FRAME), 7], "actual U event")
    need(actual[8] == ["transport", "C", list(P_FRAME), list(O_FRAME), 7], "actual V event")
    need(actual[-1] == ["erase", "C", list(O_FRAME)], "literal collector erasure")
    for offset, bank in enumerate(D_BANKS, 1):
        row = actual[offset]
        need(row[:3] == ["add", "C", bank] and Fraction(str(row[3])) == 1
             and row[4] == list(O_FRAME), "collector gather order")
    for offset, bank in enumerate(reversed(D_BANKS), 9):
        row = actual[offset]
        need(row[:3] == ["add", "C", bank] and Fraction(str(row[3])) == -1
             and row[4] == list(O_FRAME), "collector cleanup order")
    need(actual[7][:3] == ["add", "Q7", "C"] and Fraction(str(actual[7][3])) == 1
         and actual[7][4] == list(P_FRAME), "collector readout")


def add(a, b):
    return a[0] + b[0], a[1] + b[1]


def subtract(a, b):
    return a[0] - b[0], a[1] - b[1]


def multiply(a, b):
    return a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0]


def rotate(value, phase):
    a, b = value
    return ((a, b), (-b, a), (-a, -b), (b, -a))[phase % 4]


def vector_check(value):
    need(type(value) is list and len(value) == SIZE, "Gaussian vector shape")
    need(all(type(z) in (list, tuple) and len(z) == 2 and all(type(x) is int for x in z)
             for z in value), "Gaussian integer components")


def encode(coefficients):
    vector_check(coefficients)
    out = [tuple(z) for z in coefficients]
    for bit in range(RANK):
        step = 1 << bit
        for address in range(SIZE):
            if not address & step:
                out[address | step] = add(out[address], multiply(PI[1], out[address | step]))
    return out


def divide_pi(value):
    a, b = value
    need((a + b) % 2 == 0, "unavailable exact Gaussian division")
    return (a + b) // 2, (b - a) // 2


def decode(values):
    out = [tuple(z) for z in values]
    for bit in reversed(range(RANK)):
        step = 1 << bit
        for address in range(SIZE):
            if not address & step:
                out[address | step] = divide_pi(subtract(out[address | step], out[address]))
    return out


def pair(a, b, inverse, event, bit, address):
    dr, di = subtract(a, b)
    sign = -1 if inverse else 1
    ar, ai = add(a, b)
    nums = ((ar - sign * di, ai + sign * dr), (ar + sign * di, ai - sign * dr))
    if any(x % 2 for z in nums for x in z):
        raise ReplayFailure({"kind": "nonintegral_ideal_pair", "event": event,
                             "inverse": inverse, "bit": bit, "address": address})
    ideal = tuple((r // 2, i // 2) for r, i in nums)
    middle = add(b, (dr // 2, di // 2))
    turned = (di, -dr) if inverse else (-di, dr)
    second = subtract(middle, (turned[0] // 2, turned[1] // 2))
    literal = (add(second, turned), second)
    need(literal == ideal, "completed signed-floor pair differs from ideal")
    return literal


def wrapper_plan(record):
    rows, linear, quadratic = (record[k] for k in ("matrix_rows", "linear_Z4", "quadratic_rows"))
    need(len(rows) == len(linear) == len(quadratic) == RANK, "wrapper dimensions")
    need(all(type(x) is int and 0 <= x < SIZE for x in rows + quadratic), "binary rows")
    need(all(type(x) is int and 0 <= x < 4 for x in linear), "linear phases")
    need(type(record["offset"]) is int and 0 <= record["offset"] < SIZE, "affine offset")
    need(type(record["phase"]) is int and 0 <= record["phase"] < 4, "global phase")
    mapping = []
    for address in range(SIZE):
        target = record["offset"] ^ sum(((address & row).bit_count() % 2) << bit
                                         for bit, row in enumerate(rows))
        phase = record["phase"]
        for bit in range(RANK):
            if address & (1 << bit):
                phase += linear[bit]
                upper = quadratic[bit] & ~((1 << (bit + 1)) - 1)
                phase += 2 * (upper & address).bit_count()
        mapping.append((target, phase % 4))
    need({target for target, _ in mapping} == set(range(SIZE)), "wrapper bijection")
    return mapping


def wrapper(values, mapping, inverse=False):
    out = [ZERO] * SIZE
    for source, (target, phase) in enumerate(mapping):
        if inverse:
            out[source] = rotate(values[target], -phase)
        else:
            out[target] = rotate(values[source], phase)
    return out


class Arithmetic:
    def __init__(self, bound):
        self.bound = bound
        self.plans = {}

    def plan(self, raw):
        key = canonical(raw)
        if key not in self.plans:
            need(len(self.plans) < 2500, "wrapper plan capacity")
            self.plans[key] = wrapper_plan(raw)
        return self.plans[key]

    def native(self, values, event, inverse=False, counts=None):
        recipe = self.bound[event]
        first, last = ("left", "right") if inverse else ("right", "left")
        out = wrapper(values, self.plan(recipe[first]), inverse)
        bits = reversed(range(recipe["rank"])) if inverse else range(recipe["rank"])
        for bit in bits:
            step = 1 << bit
            for address in range(SIZE):
                if not address & step:
                    out[address], out[address | step] = pair(
                        out[address], out[address | step], inverse, event, bit, address)
                    if counts is not None:
                        counts["completed_literal_pairs"] += 1
        if counts is not None:
            counts["native_occurrences"] += 1
            counts["native_rank_mass"] += recipe["rank"]
            counts["inverse_native_occurrences"] += int(inverse)
            counts["wrappers"] += 2
        return wrapper(out, self.plan(recipe[last]), inverse)

    def path(self, values, path, inverse=False):
        out = list(values)
        for event in reversed(path) if inverse else path:
            out = self.native(out, event, inverse)
        return out


def exponents(kind):
    return [max(4 - (mask & ~1 if kind == "rank_one" else mask).bit_count(), 0)
            for mask in range(SIZE)]


def prepare(parameters, slots, arithmetic):
    need(type(parameters) is list and len(parameters) == 52, "52 coefficient banks")
    initial, previous, bank = {}, [ZERO] * SIZE, None
    for slot, coefficients in zip(slots, parameters, strict=True):
        vector_check(coefficients)
        if bank != slot["bank"]:
            previous, bank = [ZERO] * SIZE, slot["bank"]
        if slot["kind"] == "terminal":
            partial = [(4 * r, 4 * i) for r, i in encode(coefficients)]
        else:
            weighted = [multiply(PI[e], value) for e, value in
                        zip(exponents(slot["kind"]), coefficients, strict=True)]
            partial = encode(weighted)
            if slot["kind"] == "rank_one":
                right = arithmetic.bound[slot["transport_event"]]["right"]
                partial = wrapper(partial, arithmetic.plan(right), inverse=True)
            partial = arithmetic.path(partial, slot["source_path"], inverse=True)
        initial[slot["source"]] = [subtract(new, old) for new, old in
                                   zip(partial, previous, strict=True)]
        previous = partial
    need(len(initial) == 52, "all prepared sources")
    for values in initial.values():
        decode(values)
    return initial


def recover(initial_y, slots, arithmetic):
    recovered, total, bank = [], [ZERO] * SIZE, None
    for slot in slots:
        if bank != slot["bank"]:
            total, bank = [ZERO] * SIZE, slot["bank"]
        total = [add(a, b) for a, b in zip(total, initial_y[slot["source"]], strict=True)]
        if slot["kind"] == "terminal":
            values = decode(total)
            need(all(x % 4 == 0 for z in values for x in z), "terminal exact division")
            coefficients = [(r // 4, i // 4) for r, i in values]
        else:
            values = arithmetic.path(total, slot["source_path"])
            if slot["kind"] == "rank_one":
                right = arithmetic.bound[slot["transport_event"]]["right"]
                values = wrapper(values, arithmetic.plan(right))
            coefficients = decode(values)
            for index, exponent in enumerate(exponents(slot["kind"])):
                for _ in range(exponent):
                    coefficients[index] = divide_pi(coefficients[index])
        recovered.append(coefficients)
    return recovered


def clone_state(state):
    return {bank: list(values) for bank, values in state.items()}


def increment(values, coefficient, event):
    numerator, denominator = coefficient.as_integer_ratio()
    need(abs(numerator) == 1 and denominator in (1, 4), "caller scalar alphabet")
    for address, value in enumerate(values):
        if any(numerator * x % denominator for x in value):
            raise ReplayFailure({"kind": "nonintegral_addend", "event": event,
                                 "address": address, "coefficient": str(coefficient)})
    return [(numerator * r // denominator, numerator * i // denominator) for r, i in values]


def run_steps(state, frames, steps, word, arithmetic, mutation=None):
    counts = Counter()
    for event, inverse in steps:
        if mutation == "omit_q_return" and event == 972 and inverse:
            continue
        row = word["program"][event]
        op, target = row[:2]
        counts["events"] += 1
        if op == "transport":
            old, new = (row[3], row[2]) if inverse else (row[2], row[3])
            need(frames[target] == tuple(old), "actual native entrance frame")
            state[target] = arithmetic.native(state[target], event, inverse, counts)
            frames[target] = tuple(new)
            if mutation == "extra_native_phase" and event == 2031:
                state[target] = [rotate(z, 1) for z in state[target]]
        elif op == "add":
            source = row[2]
            need(frames[target] == frames[source] == tuple(row[4]), "common ADD frame")
            coefficient = Fraction(str(row[3])) * (-1 if inverse else 1)
            if mutation == "wrong_query_sign" and event == 2032:
                coefficient = -coefficient
            values = increment(state[source], coefficient, event)
            state[target] = [add(a, b) for a, b in zip(state[target], values, strict=True)]
            counts["weighted_adds"] += 1
            counts["quarter_adds"] += int(coefficient.denominator == 4)
        elif op == "zero":
            need(not inverse and target not in state, "private allocation")
            state[target], frames[target] = [ZERO] * SIZE, tuple(row[2])
            counts["private_zero"] += 1
        else:
            need(op == "erase" and not inverse and frames[target] == tuple(row[2]), "erase frame")
            bad = next((i for i, z in enumerate(state[target]) if z != ZERO), None)
            if bad is not None:
                raise ReplayFailure({"kind": "private_not_zero", "event": event,
                                     "bank": target, "address": bad, "value": state[target][bad]})
            del state[target]
            del frames[target]
            counts["private_erase"] += 1
    return counts


def summed(vectors):
    out = [ZERO] * SIZE
    for vector in vectors:
        out = [add(a, b) for a, b in zip(out, vector, strict=True)]
    return out


def endpoint(state, frames, initial, expected_q):
    need(set(state) == set(initial) and "C" not in state, "returned public role set")
    for bank in sorted(frames):
        if frames[bank] != ():
            raise ReplayFailure({"kind": "return_frame", "bank": bank,
                                 "actual": list(frames[bank]), "expected": []})
    for bank in sorted(initial):
        expected = expected_q if bank == "Q7" else initial[bank]
        if state[bank] != expected:
            first = next(i for i in range(SIZE) if state[bank][i] != expected[i])
            raise ReplayFailure({"kind": "query_endpoint" if bank == "Q7" else "source_return",
                                 "bank": bank, "address": first,
                                 "actual": state[bank][first], "expected": expected[first]})


def rejection(operation, kind):
    try:
        operation()
    except ReplayFailure as error:
        need(error.record["kind"] == kind, "control failed at wrong boundary")
        return error.record
    raise ValueError("incorrect caller control was accepted: " + kind)


def control_full_inverse(after, after_frames, spec, word, arithmetic, initial, expected_q):
    state, frames = clone_state(after), dict(after_frames)
    steps = [(event, True) for event in reversed(spec["cone"])]
    run_steps(state, frames, steps, word, arithmetic)
    dirty_sum = summed(initial[bank] for bank in D_BANKS)
    wrong = [add(a, b) for a, b in zip(expected_q, dirty_sum, strict=True)]
    need(any(z != ZERO for z in dirty_sum), "nonzero dirty-sum control")
    need(state["Q7"] == wrong, "complete wrong-inverse dirty contamination formula")
    failure = rejection(lambda: endpoint(state, frames, initial, expected_q), "query_endpoint")
    return {"failure": failure, "dirty_sum_sha256": digest(dirty_sum),
            "wrong_q_sha256": digest(wrong), "formula_checked_on_all_coordinates": True}


def control_collector(cut, cut_frames, spec, word, arithmetic, initial, expected_q, mutation):
    state, frames = clone_state(cut), dict(cut_frames)
    collector = [(event, False) for event in range(2025, 2040)]
    if mutation == "extra_native_phase":
        failure = rejection(lambda: run_steps(state, frames, collector, word, arithmetic, mutation),
                            "private_not_zero")
        need(failure["event"] == 2039, "wrong native phase must fail literal private erasure")
        return failure
    need(mutation == "wrong_query_sign", "named collector control")
    run_steps(state, frames, collector, word, arithmetic, mutation)
    run_steps(state, frames, spec["reverse"], word, arithmetic)
    failure = rejection(lambda: endpoint(state, frames, initial, expected_q), "query_endpoint")
    need(failure["bank"] == "Q7", "readout sign controls query")
    return failure


def control_return(after, after_frames, spec, word, arithmetic, initial, expected_q):
    state, frames = clone_state(after), dict(after_frames)
    run_steps(state, frames, spec["reverse"], word, arithmetic, "omit_q_return")
    failure = rejection(lambda: endpoint(state, frames, initial, expected_q), "return_frame")
    need(failure["bank"] == "Q7" and failure["actual"] == list(P_FRAME), "named Q return gap")
    return failure


def execute_closed(initial, spec, word, arithmetic):
    state = clone_state(initial)
    frames = {bank: () for bank in state}
    counts = run_steps(state, frames, [(i, False) for i in spec["cone"]], word, arithmetic)
    need(all(frames[bank] == O_FRAME for bank in D_BANKS) and frames["Q7"] == P_FRAME,
         "actual cut frame contract")
    for bank in DIRTY:
        decode(state[bank])
    cut, cut_frames = clone_state(state), dict(frames)
    collector = [(i, False) for i in range(2025, 2040)]
    counts.update(run_steps(state, frames, collector, word, arithmetic))
    after, after_frames = clone_state(state), dict(frames)
    counts.update(run_steps(state, frames, spec["reverse"], word, arithmetic))
    return state, frames, counts, cut, cut_frames, after, after_frames


def fixture_coefficients(slot):
    return [(((37 * slot + 17 * k + 3 * k.bit_count()) % 11) - 5,
             ((19 * slot + 29 * k + 5 * k.bit_count()) % 13) - 6) for k in range(SIZE)]


def run_controls(cut, cut_frames, after, after_frames, spec, word, arithmetic, initial, expected_q):
    return {
        "full_producer_inverse": control_full_inverse(
            after, after_frames, spec, word, arithmetic, initial, expected_q),
        "extra_phase_after_native2031": control_collector(
            cut, cut_frames, spec, word, arithmetic, initial, expected_q, "extra_native_phase"),
        "omitted_q_inverse972": control_return(
            after, after_frames, spec, word, arithmetic, initial, expected_q),
        "query2032_wrong_sign": control_collector(
            cut, cut_frames, spec, word, arithmetic, initial, expected_q, "wrong_query_sign")}


def analyze(word, native, parameters, initial_dirty, *, run_negative_controls=False):
    """Return full arrays for root comparison and a compact deterministic receipt.

    parameters:52 arbitrary Gaussian coefficient vectors, ordered by the five
    source groups. initial_dirty:six B9 vectors named D31,D30,D29,D28,D27,Q7.
    Source-byte authentication belongs to the caller; standalone mode pins it.
    Negative controls are optional because they require nonzero witnesses;
    enable them for the named dense fixture, not arbitrary zero/kernel inputs.
    """
    bound = native_bindings(word, native)
    spec = select_source(word)
    arithmetic = Arithmetic(bound)
    need(set(initial_dirty) == set(DIRTY), "six dirty input roles")
    dirty = {bank: [tuple(z) for z in values] for bank, values in initial_dirty.items()}
    for values in dirty.values():
        vector_check(values)
        decode(values)
    initial_y = prepare(parameters, spec["slots"], arithmetic)
    initial = {**initial_y, **dirty}
    expected_parameters = [[tuple(z) for z in vector] for vector in parameters]
    terminal = [index for index, slot in enumerate(spec["slots"]) if slot["kind"] == "terminal"]
    need(terminal == [2, 9, 16, 27, 51], "five terminal coefficient slots")
    query = encode(summed(parameters[index] for index in terminal))
    expected_q = [add(a, b) for a, b in zip(dirty["Q7"], query, strict=True)]
    state, frames, counts, cut, cut_frames, after, after_frames = execute_closed(
        initial, spec, word, arithmetic)
    endpoint(state, frames, initial, expected_q)
    recovered = recover({bank: state[bank] for bank in initial_y}, spec["slots"], arithmetic)
    need(recovered == expected_parameters, "all52 full coefficient arrays restored")
    wanted = {"events": 524, "native_occurrences": 402, "native_rank_mass": 722,
              "completed_literal_pairs": 184832, "inverse_native_occurrences": 200,
              "wrappers": 804, "weighted_adds": 120, "quarter_adds": 104,
              "private_zero": 1, "private_erase": 1}
    need(dict(counts) == wanted, "complete literal caller inventory")
    controls = (run_controls(cut, cut_frames, after, after_frames, spec, word, arithmetic,
                             initial, expected_q) if run_negative_controls else {})
    receipt = make_receipt(spec, parameters, initial, state, recovered, counts, controls)
    return {"receipt": receipt, "initial_y": initial_y,
            "returned_y": {bank: state[bank] for bank in initial_y},
            "returned_coefficients": recovered,
            "returned_dirty": {bank: state[bank] for bank in D_BANKS},
            "output_q": state["Q7"], "cut": {bank: cut[bank] for bank in DIRTY}}


def make_receipt(spec, parameters, initial, state, recovered, counts, controls):
    steps = ([(i, False) for i in spec["cone"]]
             + [(i, False) for i in range(2025, 2040)] + spec["reverse"])
    terminal = [i for i, slot in enumerate(spec["slots"]) if slot["kind"] == "terminal"]
    return {"status": "PASS_INDEPENDENT_RESTORED_QUERY",
            "scope": "524-event changed closed caller; omitted original histories unclaimed",
            "source_sha256": {"WORD.json": WORD_SHA256, "NATIVE.json.gz": NATIVE_SHA256},
            "cone_events_sha256": digest(spec["cone"]), "closed_steps_sha256": digest(steps),
            "excluded_q_compensation_inverses": spec["compensation"],
            "terminal_slots": terminal,
            "terminal_sources": [spec["slots"][i]["source"] for i in terminal],
            "literal_counts": dict(counts), "parameters_sha256": digest(parameters),
            "initial_all_banks_sha256": digest(initial), "output_q_sha256": digest(state["Q7"]),
            "returned_coefficients_sha256": digest(recovered),
            "full_array_checks": {"returned_coefficient_banks": 52, "returned_prepared_y_banks": 52,
                                  "returned_dirty_d_banks": 5, "query_coordinates": SIZE,
                                  "all58_public_return_frames_empty": True,
                                  "private_C_erased_zero": True},
            "negative_controls_executed": bool(controls),
            "controls": controls,
            "inherited": ["PR3467 complete entrance and codec theorem",
                          "PR3416 native covariance with phase",
                          "PR3382 Newton invariance; PR3025/3068 literal gate lineage"]}


def verify_independent(word_path, native_path):
    word, native = read_inputs(word_path, native_path)
    parameters = [fixture_coefficients(index) for index in range(52)]
    dirty = {bank: encode(fixture_coefficients(index)) for index, bank in enumerate(DIRTY, 52)}
    return analyze(word, native, parameters, dirty, run_negative_controls=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    inputs = args.repo / "research/p104-rounded-collector/inputs"
    result = verify_independent(inputs / "WORD.json", inputs / "NATIVE.json.gz")["receipt"]
    rendered = canonical(result) + "\n"
    if args.output:
        with args.output.open("x", encoding="utf-8") as handle:
            handle.write(rendered)
    else:
        print(rendered, end="")


if __name__ == "__main__":
    main()
