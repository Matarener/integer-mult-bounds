"""Independent source and literal-arithmetic checks for the 257-event cone.

Clear1nsight, with substantial OpenAI assistance. Apache-2.0.
No predecessor or primary executable is imported. This bounded checker uses
actual Y-source paths as its empty-to-read maps; the primary construction uses
D paths. Their identification inherits the separately pinned native covariance
theorem. Numerical execution below is the dependency cone, not the whole prefix.
"""

import argparse
import gzip
import hashlib
import io
import json
from collections import Counter
from pathlib import Path


WORD_SHA256 = "cec1fb3fbd0067b500ad5119a62ba60685be718e769374d7ec8abdd2beaa7e50"
NATIVE_SHA256 = "ab91c78835c3e10cf3b2cb8a5d4e0b7cfc3df1ae5a811298d27842f2193e1e3d"
SIZE = 512
RANK = 9
CUT = 2025
ZERO = (0, 0)
BANKS = ("D31", "D30", "D29", "D28", "D27")
DIRTY = (*BANKS, "Q7")
PI = ((1, 0), (1, 1), (0, 2), (-2, 2), (-4, 0))


class IndependentError(ValueError):
    """A source, arithmetic, or finite-reference contract failed."""


class ArithmeticFailure(IndependentError):
    """The first ideal stage that has no exact Gaussian realization."""

    def __init__(self, record):
        super().__init__(record["kind"])
        self.record = record


def need(condition, message):
    if not condition:
        raise IndependentError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def digest(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def unique_object(items):
    out = {}
    for key, value in items:
        need(key not in out, "duplicate JSON key")
        out[key] = value
    return out


def json_load(data):
    def forbidden(value):
        raise IndependentError("noninteger JSON number: " + value)
    return json.loads(data, object_pairs_hook=unique_object,
                      parse_float=forbidden, parse_constant=forbidden)


def authenticated(path, expected):
    path = Path(path)
    need(path.is_file() and not path.is_symlink(), "regular scientific source required")
    need(path.stat().st_size <= 1048576, "scientific source capacity")
    data = path.read_bytes()
    need(hashlib.sha256(data).hexdigest() == expected, "scientific source SHA256 mismatch")
    return data


def source_inputs(word_path, native_path):
    word = json_load(authenticated(word_path, WORD_SHA256))
    compressed = authenticated(native_path, NATIVE_SHA256)
    with gzip.GzipFile(fileobj=io.BytesIO(compressed)) as handle:
        raw = handle.read(8388609)
    need(len(raw) <= 8388608, "decompressed native source capacity")
    native = json_load(raw)
    need(len(word["program"]) == 5398, "literal word event count")
    need(len(word["initial_frames"]) == 358, "literal initial role count")
    need(len(native["transports"]) == 1245, "native recipe count")
    bound = bind_native(word, native)
    check_frames(word)
    return word, bound


def bind_native(word, native):
    bound = {}
    for record in native["transports"]:
        recipe = record["recipe"]
        need(type(recipe["rank"]) is int and 1 <= recipe["rank"] <= RANK,
             "positive bounded native rank")
        for event in record["events"]:
            need(type(event) is int and 0 <= event < len(word["program"]), "native event")
            need(event not in bound, "duplicate native occurrence")
            literal = word["program"][event]
            need(literal[0] == "transport", "native occurrence opcode")
            need(literal[2:] == [record["old"], record["new"], recipe["rank"]],
                 "native occurrence/frame/rank binding")
            bound[event] = recipe
    actual = {i for i, e in enumerate(word["program"]) if e[0] == "transport"}
    need(set(bound) == actual and len(bound) == 2070, "complete occurrence binding")
    return bound


def check_frames(word):
    frames = {role: tuple(frame) for role, frame in word["initial_frames"].items()}
    for event in word["program"]:
        op, target = event[:2]
        if op == "transport":
            need(frames[target] == tuple(event[2]), "chronological native old frame")
            frames[target] = tuple(event[3])
        elif op == "add":
            need(frames[target] == frames[event[2]] == tuple(event[4]), "common ADD frame")
        elif op == "sign":
            need(event[2] == "-1" and frames[target] == tuple(event[3]), "signed frame")
        elif op == "zero":
            need(target not in frames, "private role already live")
            frames[target] = tuple(event[2])
        else:
            need(op == "erase" and frames[target] == tuple(event[2]), "private erase frame")
            del frames[target]
    need(frames == {r: tuple(f) for r, f in word["final_frames"].items()}, "terminal frames")


def extract_cone(word):
    live, selected = set(DIRTY), []
    for index in range(CUT - 1, -1, -1):
        event = word["program"][index]
        if event[1] not in live:
            continue
        need(event[0] in ("transport", "add"), "unexpected producer cone operation")
        selected.append(index)
        if event[0] == "add":
            live.add(event[2])
    selected.reverse()
    need(len(selected) == 257 and len(live) == 58, "producer dependency cone")
    need(all(word["initial_frames"][role] == [] for role in live), "empty producer inputs")
    groups = extract_groups(word, selected)
    slots = extract_slots(word, selected, groups)
    return selected, live, groups, slots


def extract_groups(word, cone):
    groups = []
    for bank in BANKS:
        reads = []
        for index in cone:
            event = word["program"][index]
            if event[0] == "add" and event[1] == bank:
                need(str(event[3]) == "1/4" and event[2].startswith("Y"), "producer quarter")
                reads.append({"source": event[2], "event": index})
        groups.append({"bank": bank, "reads": reads})
    names = [read["source"] for group in groups for read in group["reads"]]
    need(len(names) == len(set(names)) == 52, "disjoint Y source groups")
    need([len(g["reads"]) for g in groups] == [3, 7, 7, 11, 24], "source group lengths")
    return groups


def path_to_source_read(word, cone, source, read):
    path = []
    for index in cone:
        if index >= read:
            break
        event = word["program"][index]
        if event[1] == source:
            need(event[0] == "transport", "Y source has a nontransport producer")
            path.append(index)
    return path


def extract_slots(word, cone, groups):
    slots = []
    for group in groups:
        reads = group["reads"]
        for offset, read in enumerate(reads):
            following = reads[offset + 1]["event"] if offset + 1 < len(reads) else None
            transports = [] if following is None else [i for i in cone
                if read["event"] < i < following and word["program"][i][0] == "transport"
                and word["program"][i][1] == group["bank"]]
            need(len(transports) <= 1, "at most one intervening native occurrence")
            if transports:
                need(word["program"][transports[0]][4] == 1, "rank-one interval")
            kind = "terminal" if following is None else ("rank_one" if transports else "zero")
            slots.append({"bank": group["bank"], **read, "next_event": following,
                          "kind": kind, "transport_event": transports[0] if transports else None,
                          "source_path": path_to_source_read(word, cone, read["source"], read["event"]),
                          "frame": word["program"][read["event"]][4]})
    need(Counter(s["kind"] for s in slots) == {"zero": 32, "rank_one": 15, "terminal": 5},
         "source interval census")
    return slots


def add(left, right):
    return left[0] + right[0], left[1] + right[1]


def sub(left, right):
    return left[0] - right[0], left[1] - right[1]


def multiply(left, right):
    return left[0] * right[0] - left[1] * right[1], left[0] * right[1] + left[1] * right[0]


def rotate(value, phase):
    real, imag = value
    return ((real, imag), (-imag, real), (-real, -imag), (imag, -real))[phase % 4]


def encode(coefficients):
    need(len(coefficients) == SIZE, "rank-nine coefficients")
    out = list(coefficients)
    for bit in range(RANK):
        step = 1 << bit
        for address in range(SIZE):
            if not address & step:
                out[address | step] = add(out[address], multiply(PI[1], out[address | step]))
    return out


def decode(values):
    need(len(values) == SIZE, "rank-nine values")
    out = list(values)
    for bit in reversed(range(RANK)):
        step = 1 << bit
        for address in range(SIZE):
            if not address & step:
                real, imag = sub(out[address | step], out[address])
                need((real + imag) % 2 == 0, "outside Gaussian Newton lattice")
                out[address | step] = ((real + imag) // 2, (imag - real) // 2)
    return out


def belongs(values):
    try:
        decode(values)
    except IndependentError:
        return False
    return True


def literal_pair(a, b, inverse=False):
    real, imag = sub(a, b)
    center = add(b, (real // 2, imag // 2))
    turned = (imag, -real) if inverse else (-imag, real)
    second = sub(center, (turned[0] // 2, turned[1] // 2))
    return add(second, turned), second


def ideal_pair(a, b, inverse=False):
    sign = -1 if inverse else 1
    real, imag = sub(a, b)
    total_real, total_imag = add(a, b)
    nums = ((total_real - sign * imag, total_imag + sign * real),
            (total_real + sign * imag, total_imag - sign * real))
    if any(component % 2 for pair in nums for component in pair):
        return None, nums
    return tuple((real // 2, imag // 2) for real, imag in nums), nums


def stage(values, bit, inverse=False, event=None):
    out = list(values)
    step = 1 << bit
    for address in range(SIZE):
        if address & step:
            continue
        other = address | step
        literal = literal_pair(out[address], out[other], inverse)
        ideal, nums = ideal_pair(out[address], out[other], inverse)
        if ideal is None:
            raise ArithmeticFailure({"kind": "nonintegral_native_pair", "event": event,
                                     "bit": bit, "address": address, "numerators": nums,
                                     "inputs": [out[address], out[other]], "literal": literal})
        need(literal == ideal, "literal/ideal pair disagreement on integral ideal input")
        out[address], out[other] = literal
    return out


def wrapper_plan(record):
    rows, linear, quadratic = (record[k] for k in ("matrix_rows", "linear_Z4", "quadratic_rows"))
    need(len(rows) == len(linear) == len(quadratic) == RANK, "wrapper shape")
    permutation, phases = [], []
    for address in range(SIZE):
        target = sum(((address & row).bit_count() % 2) << bit for bit, row in enumerate(rows))
        permutation.append(target ^ record["offset"])
        phase = record["phase"]
        for bit in range(RANK):
            if address & (1 << bit):
                phase += linear[bit]
                for other in range(bit + 1, RANK):
                    if address & (1 << other) and quadratic[bit] & (1 << other):
                        phase += 2
        phases.append(phase % 4)
    need(set(permutation) == set(range(SIZE)), "bijective monomial wrapper")
    return tuple(permutation), tuple(phases)


def wrapper(values, plan, inverse=False):
    permutation, phases = plan
    out = [ZERO] * SIZE
    for source, target in enumerate(permutation):
        if inverse:
            out[source] = rotate(values[target], -phases[source])
        else:
            out[target] = rotate(values[source], phases[source])
    return out


class Native:
    """Independent bounded monomial tables and direct Gaussian arithmetic."""

    def __init__(self, bound):
        self.bound = bound
        self.plans = {}

    def plan(self, record):
        key = canonical(record)
        if key not in self.plans:
            need(len(self.plans) < 2500, "monomial table capacity")
            self.plans[key] = wrapper_plan(record)
        return self.plans[key]

    def apply(self, values, event, inverse=False):
        recipe = self.bound[event]
        if not any(value != ZERO for value in values):
            return list(values)
        first, last = ("left", "right") if inverse else ("right", "left")
        out = wrapper(values, self.plan(recipe[first]), inverse)
        bits = reversed(range(recipe["rank"])) if inverse else range(recipe["rank"])
        for bit in bits:
            out = stage(out, bit, inverse, event)
        return wrapper(out, self.plan(recipe[last]), inverse)

    def path(self, values, events, inverse=False):
        out = list(values)
        for event in reversed(events) if inverse else events:
            out = self.apply(out, event, inverse)
        return out


def exponent_profile(kind):
    if kind == "terminal":
        return [4] * SIZE
    need(kind in ("zero", "rank_one"), "known interval profile")
    return [max(4 - (mask & ~1 if kind == "rank_one" else mask).bit_count(), 0)
            for mask in range(SIZE)]


def is_four_grid(values):
    return all(real % 4 == 0 and imag % 4 == 0 for real, imag in values)


def core_admits(values, kind):
    if not is_four_grid(values):
        return False
    return kind == "zero" or is_four_grid(stage(values, 0))


def independent_profiles():
    result = {}
    for kind in ("zero", "rank_one"):
        observed, sharp = [], 0
        for mask in range(SIZE):
            power = (1, 0)
            for _ in range(mask.bit_count()):
                power = multiply(power, PI[1])
            for exponent in range(5):
                value = multiply(power, PI[exponent])
                column = [value if address & mask == mask else ZERO for address in range(SIZE)]
                if core_admits(column, kind):
                    observed.append(exponent)
                    sharp += exponent > 0
                    break
            else:
                raise IndependentError("four-B core generator rejected")
        need(observed == exponent_profile(kind), "derived minimal diagonal profile")
        result[kind] = {"exponents": observed, "counts": dict(Counter(observed)),
                        "index_log2": sum(observed), "minimal_basis_checks": SIZE,
                        "strict_preceding_exponent_rejections": sharp}
    need(result["zero"]["index_log2"] == 187, "zero-gap index")
    need(result["rank_one"]["index_log2"] == 280, "rank-one-gap index")
    result["terminal"] = {"counts": {4: SIZE}, "index_log2": 2048}
    profile = Counter({0: 0})
    for kind, multiplicity in (("zero", 32), ("rank_one", 15), ("terminal", 5)):
        for exponent, count in result[kind]["counts"].items():
            profile[exponent] += multiplicity * count
    need(sum(profile.values()) == 52 * SIZE, "whole-module Gaussian rank")
    result["whole"] = {"counts": dict(profile), "index_log2": sum(e * n for e, n in profile.items())}
    need(result["whole"]["index_log2"] == 20424, "whole-module exact index")
    return result


def fixture_coefficients(slot):
    return [(((37 * slot + 17 * k + 3 * k.bit_count()) % 11) - 5,
             ((19 * slot + 29 * k + 5 * k.bit_count()) % 13) - 6) for k in range(SIZE)]


def partial_sum_fixture(slot, index, native):
    coefficients = fixture_coefficients(index)
    if slot["kind"] == "terminal":
        return [(4 * real, 4 * imag) for real, imag in encode(coefficients)]
    values = encode([multiply(PI[exponent], value) for exponent, value in
                     zip(exponent_profile(slot["kind"]), coefficients, strict=True)])
    if slot["kind"] == "rank_one":
        record = native.bound[slot["transport_event"]]["right"]
        values = wrapper(values, native.plan(record), inverse=True)
    return native.path(values, slot["source_path"], inverse=True)


def generated_initial(slots, native):
    initial, partials = {}, {}
    previous = [ZERO] * SIZE
    bank = None
    for index, slot in enumerate(slots):
        if bank != slot["bank"]:
            previous, bank = [ZERO] * SIZE, slot["bank"]
        partial = partial_sum_fixture(slot, index, native)
        need(belongs(partial), "constructed partial sum outside initial B")
        initial[slot["source"]] = [sub(new, old) for new, old in zip(partial, previous, strict=True)]
        partials[slot["event"]] = partial
        previous = partial
    for offset, role in enumerate(DIRTY, 52):
        initial[role] = encode(fixture_coefficients(offset))
    need(len(initial) == 58 and all(belongs(v) for v in initial.values()), "generated B inputs")
    return initial, partials


def read_exact_quarter(values, event, source):
    for address, value in enumerate(values):
        if value[0] % 4 or value[1] % 4:
            raise ArithmeticFailure({"kind": "nonintegral_quarter", "event": event,
                                     "source": source, "address": address, "value": value})
    return [(real // 4, imag // 4) for real, imag in values]


def replay_cone(initial, word, cone, native):
    states = {role: list(values) for role, values in initial.items()}
    counts = Counter()
    active, first_non_b = [], None
    for index in cone:
        event = word["program"][index]
        op, target = event[:2]
        if op == "transport":
            counts["native_occurrences"] += 1
            if any(z != ZERO for z in states[target]):
                active.append(index)
                counts["literal_pair_comparisons"] += native.bound[index]["rank"] * (SIZE // 2)
            states[target] = native.apply(states[target], index)
        else:
            source, coefficient = event[2:4]
            counts["additions"] += 1
            if str(coefficient) == "1/4":
                increment = read_exact_quarter(states[source], index, source)
                counts["quarter_reads"] += 1
            else:
                need(coefficient == -1, "initial D-to-Q subtraction")
                increment = [(-real, -imag) for real, imag in states[source]]
            states[target] = [add(a, b) for a, b in zip(states[target], increment, strict=True)]
        if first_non_b is None and not belongs(states[target]):
            first_non_b = {"event": index, "bank": target}
    cut = {role: states[role] for role in DIRTY}
    need(all(belongs(values) for values in cut.values()), "six final-cut B outputs")
    return {"initial_sha256": digest(initial), "cut_sha256": digest(cut),
            "cut_bank_sha256": {role: digest(values) for role, values in cut.items()},
            "counts": dict(counts), "active_native_events": active,
            "first_non_B": first_non_b}, cut


def expected_cut(initial, groups, word, cone, native):
    result = {}
    for group in groups:
        total = [ZERO] * SIZE
        for read in group["reads"]:
            total = [add(a, b) for a, b in zip(total, initial[read["source"]], strict=True)]
        quarter = read_exact_quarter(total, None, "complete initial source group")
        bank = group["bank"]
        value = [add(a, b) for a, b in zip(initial[bank], quarter, strict=True)]
        path = [i for i in cone if word["program"][i][:2] == ["transport", bank]]
        result[bank] = native.path(value, path)
    value = list(initial["Q7"])
    for bank in BANKS:
        value = [sub(a, b) for a, b in zip(value, initial[bank], strict=True)]
    path = [i for i in cone if word["program"][i][:2] == ["transport", "Q7"]]
    result["Q7"] = native.path(value, path)
    return result


def validate_partial_fixture(partials, slots, native):
    for slot in slots:
        partial = partials[slot["event"]]
        if slot["kind"] == "terminal":
            need(all(r % 4 == 0 and i % 4 == 0 for r, i in decode(partial)), "terminal 4B sum")
            continue
        physical = native.path(partial, slot["source_path"])
        need(is_four_grid(physical), "post-read partial sum grid")
        if slot["kind"] == "rank_one":
            record = native.bound[slot["transport_event"]]
            at_pair = wrapper(physical, native.plan(record["right"]))
            need(is_four_grid(at_pair), "right wrapper preserves four grid")
            need(is_four_grid(stage(at_pair, 0)), "complete intervening C stage four grid")
    return {"checked_partial_sums": len(slots), "actual_source_paths": True}


def zero_initial(roles):
    return {role: [ZERO] * SIZE for role in roles}


def ideal_cancellation_control(slots, native, roles, kind):
    slot = min((s for s in slots if s["kind"] == "rank_one"), key=lambda s: s["event"])
    following = next(s for s in slots if s["event"] == slot["next_event"])
    if kind == "quarter":
        physical = [(1, 0)] * SIZE
    else:
        need(kind == "pair", "control kind")
        physical = [(-4, 0) if address & 1 else ZERO for address in range(SIZE)]
        need(belongs(physical) and is_four_grid(physical), "valid rank-one sharp core witness")
        record = native.bound[slot["transport_event"]]["right"]
        physical = wrapper(physical, native.plan(record), inverse=True)
    first = native.path(physical, slot["source_path"], inverse=True)
    initial = zero_initial(roles)
    initial[slot["source"]] = first
    initial[following["source"]] = [(-real, -imag) for real, imag in first]
    need(all(belongs(v) for v in initial.values()), "control initial B admission")
    for bank in BANKS:
        total = [ZERO] * SIZE
        for item in slots:
            if item["bank"] == bank:
                total = [add(a, b) for a, b in zip(total, initial[item["source"]], strict=True)]
        need(all(value == ZERO for value in total), "control ideal final group cancellation")
    return initial, slot, following


def rejected_control(initial, word, cone, native, expected_kind, expected_event):
    try:
        replay_cone(initial, word, cone, native)
    except ArithmeticFailure as error:
        need(error.record["kind"] == expected_kind and error.record["event"] == expected_event,
             "control failed at the wrong boundary")
        return {"initial_sha256": digest(initial), "first_failure": error.record,
                "initial_B": True, "ideal_group_sums_zero": True}
    raise IndependentError("nonexact control accepted")


def controls(word, cone, roles, slots, native):
    quarter, gap, _ = ideal_cancellation_control(slots, native, roles, "quarter")
    pair, pair_gap, _ = ideal_cancellation_control(slots, native, roles, "pair")
    need(gap["event"] == 1087 and pair_gap["transport_event"] == 1089, "earliest actual interval")
    first = rejected_control(quarter, word, cone, native, "nonintegral_quarter", 1087)
    second = rejected_control(pair, word, cone, native, "nonintegral_native_pair", 1089)
    initial = zero_initial(roles)
    initial["Y27"][0], initial["Y26"][0] = (64, 0), (-64, 0)
    need(all(belongs(v) for v in initial.values()), "retained paired initial B")
    paired, cut = replay_cone(initial, word, cone, native)
    need(all(z == ZERO for values in cut.values() for z in values), "paired literal zero cut")
    need(paired["first_non_B"] == {"event": 1090, "bank": "D31"}, "retained strict separation")
    return {"first_quarter": first, "post_native": second, "known_paired64": paired}


def verify_independent(word_path, native_path):
    word, bound = source_inputs(word_path, native_path)
    cone, roles, groups, slots = extract_cone(word)
    native = Native(bound)
    profiles = independent_profiles()
    initial, partials = generated_initial(slots, native)
    validation = validate_partial_fixture(partials, slots, native)
    fixture, cut = replay_cone(initial, word, cone, native)
    need(cut == expected_cut(initial, groups, word, cone, native), "actual six-bank ideal cut formula")
    fixture["full_array_cut_formula_checks"] = len(DIRTY)
    need(fixture["counts"]["native_occurrences"] == 200, "generated native occurrence count")
    need(fixture["counts"]["quarter_reads"] == 52, "generated quarter count")
    return {"status": "PASS_INDEPENDENT_STAGEWISE_ENTRANCE",
            "inputs": {"WORD.json": WORD_SHA256, "NATIVE.json.gz": NATIVE_SHA256},
            "scope": "257-event dependency cone; full-word frame binding is structural only",
            "cone": {"events": cone, "events_sha256": digest(cone), "count": len(cone),
                     "initial_count": len(roles), "initial_roles": sorted(roles),
                     "native_rank_sum": sum(bound[i]["rank"] for i in cone if i in bound)},
            "groups": groups, "slots": slots, "profiles": profiles,
            "generated_fixture": {**fixture, **validation},
            "controls": controls(word, cone, roles, slots, native)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    inputs = args.repo / "research/p104-rounded-collector/inputs"
    result = verify_independent(inputs / "WORD.json", inputs / "NATIVE.json.gz")
    rendered = canonical(result) + "\n"
    if args.output:
        with args.output.open("x", encoding="utf-8") as handle:
            handle.write(rendered)
    else:
        print(rendered, end="")


if __name__ == "__main__":
    main()
