"""Authenticated structure and exact execution of the first P104 producer cone.

Clear1nsight, with substantial OpenAI assistance. Apache-2.0.
The frozen word, native recipes and Gaussian model retain their named authors.
Only the selected dependency cone is executed, not the omitted prefix events.
"""

import gzip
import hashlib
import json
from collections import Counter
from fractions import Fraction
from pathlib import Path
from types import ModuleType


PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
SIZE = 512
CUT = 2025
D_BANKS = ("D31", "D30", "D29", "D28", "D27")
TARGETS = D_BANKS + ("Q7",)
YS = tuple("Y" + str(j) for j in list(range(22, 33)) + list(range(63, 104)))
SOURCE_HASHES = {
    "word": "cec1fb3fbd0067b500ad5119a62ba60685be718e769374d7ec8abdd2beaa7e50",
    "native": "ab91c78835c3e10cf3b2cb8a5d4e0b7cfc3df1ae5a811298d27842f2193e1e3d",
    "model": "74c83367887dd885137b222155c86389fe0be9f1293a6f0e5fdb51d71f435fdd",
}


class SourceError(ValueError):
    """A source binding, execution or finite-domain condition failed."""


def require(condition, message):
    if not condition:
        raise SourceError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def read_pinned(path, label):
    path = Path(path)
    require(path.is_file() and not path.is_symlink(), "regular input required: " + label)
    with path.open("rb") as handle:
        data = handle.read(32 * 1024 * 1024 + 1)
    require(len(data) <= 32 * 1024 * 1024, "bounded source size")
    require(hashlib.sha256(data).hexdigest() == SOURCE_HASHES[label],
            "source digest mismatch: " + label)
    return data


def load_inputs(root=ROOT):
    root = Path(root)
    word = json.loads(read_pinned(root / "research/p104-rounded-collector/inputs/WORD.json", "word"))
    raw_native = read_pinned(root / "research/p104-rounded-collector/inputs/NATIVE.json.gz", "native")
    native = json.loads(gzip.decompress(raw_native))
    model_path = PACKAGE / "inputs/pr3382_model.py"
    model_bytes = read_pinned(model_path, "model")
    model = ModuleType("p104_pinned_newton_model")
    exec(compile(model_bytes, str(model_path), "exec"), model.__dict__)
    return word, native, model


def occurrence_map(native):
    result = {}
    for item in native["transports"]:
        for event in item["events"]:
            require(type(event) is int and event not in result, "unique native occurrence")
            result[event] = item
    require(len(native["transports"]) == 1245 and len(result) == 2070,
            "frozen native archive dimensions")
    return result


def structure(word, native):
    program = word["program"]
    require(len(program) == 5398, "frozen word length")
    needed = set(TARGETS)
    selected = []
    for event in reversed(range(CUT)):
        record = program[event]
        if record[1] in needed:
            require(record[0] in ("transport", "add"), "producer opcode")
            selected.append(event)
            if record[0] == "add":
                needed.add(record[2])
    selected.reverse()
    require(needed == set(TARGETS) | set(YS), "exact initial dependencies")
    require(len(selected) == 257, "exact producer event count")
    require(Counter(program[e][0] for e in selected) == {"transport": 200, "add": 57},
            "producer event profile")
    require(all(word["initial_frames"][name] == [] for name in needed), "empty initial frames")
    occurrences = occurrence_map(native)
    frames = {name: [] for name in needed}
    paths = {name: [] for name in needed}
    groups = {name: [] for name in D_BANKS}
    q_reads = []
    rank_mass = 0
    for event in selected:
        record = program[event]
        opcode, bank = record[:2]
        if opcode == "transport":
            old, new, rank = record[2:]
            item = occurrences[event]
            require((item["old"], item["new"], item["recipe"]["rank"]) ==
                    (old, new, rank), "native old/new/rank binding")
            require(frames[bank] == old, "actual transport frame chronology")
            frames[bank] = new[:]
            paths[bank].append(event)
            rank_mass += rank
        else:
            source, coefficient, frame = record[2:]
            require(frames[bank] == frames[source] == frame, "common ADD frame")
            coefficient = Fraction(str(coefficient))
            if bank == "Q7":
                require(source in D_BANKS and coefficient == -1 and not groups[source],
                        "Q reads only initial dirty D before quarters")
                q_reads.append([event, source])
            else:
                require(bank in D_BANKS and source in YS and coefficient == Fraction(1, 4),
                        "positive quarter into D")
                groups[bank].append({
                    "bank": bank, "source": source, "event": event,
                    "frame": frames[bank][:], "path_to_read": paths[bank][:],
                    "source_path_to_read": paths[source][:],
                })
    require(rank_mass == 354, "producer native rank mass")
    require(sorted(source for _, source in q_reads) == sorted(D_BANKS), "five dirty Q reads")
    require([len(groups[d]) for d in D_BANKS] == [3, 7, 7, 11, 24], "source group sizes")
    require(sorted(g["source"] for rows in groups.values() for g in rows) == sorted(YS),
            "disjoint source groups exhaust52 Y")
    gaps = []
    for bank in D_BANKS:
        rows = groups[bank]
        for index, row in enumerate(rows):
            gap = dict(row)
            if index + 1 == len(rows):
                gap.update(kind="terminal", next_event=None, transport_event=None)
            else:
                next_event = rows[index + 1]["event"]
                between = [e for e in selected if row["event"] < e < next_event
                           and program[e][1] == bank]
                require(all(program[e][0] == "transport" for e in between), "pure read gap")
                require(len(between) <= 1, "at most one native in each nonterminal gap")
                if between:
                    require(program[between[0]][4] == 1, "one rank-one native per nonempty gap")
                gap.update(kind="rank_one" if between else "zero", next_event=next_event,
                           transport_event=between[0] if between else None)
            gaps.append(gap)
    require(Counter(g["kind"] for g in gaps) == {"zero": 32, "rank_one": 15, "terminal": 5},
            "complete interval profile")
    return {
        "selected": selected, "dependencies": sorted(needed), "groups": groups, "gaps": gaps,
        "q_reads": q_reads, "cut_frames": {name: frames[name] for name in TARGETS},
        "cut_paths": {name: paths[name] for name in TARGETS},
        "native_count": 200, "native_rank_mass": rank_mass,
    }


def native_plans(word, native, selected, model):
    occurrences = occurrence_map(native)
    plans = {}
    for event in selected:
        record = word["program"][event]
        if record[0] != "transport":
            continue
        item = occurrences[event]
        require((item["old"], item["new"], item["recipe"]["rank"]) ==
                (record[2], record[3], record[4]), "recipe binding")
        recipe = item["recipe"]
        plans[event] = {"rank": recipe["rank"],
                        "left": model.wrapper_plan(recipe["left"]),
                        "right": model.wrapper_plan(recipe["right"])}
    return plans


def apply_wrapper(values, plan, model, inverse=False):
    require(len(values) == len(plan) == SIZE, "wrapper dimensions")
    out = [(0, 0)] * SIZE
    for source, (target, phase) in enumerate(plan):
        if inverse:
            out[source] = model.rot(values[target], -phase)
        else:
            out[target] = model.rot(values[source], phase)
    return out


def apply_native(values, event, plans, model, inverse=False, literal=False):
    plan = plans[event]
    out = apply_wrapper(values, plan["left" if inverse else "right"], model, inverse)
    bits = range(plan["rank"] - 1, -1, -1) if inverse else range(plan["rank"])
    for bit in bits:
        out = model.stage(out, bit, inverse=inverse, literal=literal)
    return apply_wrapper(out, plan["right" if inverse else "left"], model, inverse)


def apply_path(values, path, plans, model, inverse=False):
    out = values[:]
    for event in reversed(path) if inverse else path:
        out = apply_native(out, event, plans, model, inverse=inverse)
    return out


def trace_cone(word, structure_record, plans, model, initial):
    require(set(initial) == set(structure_record["dependencies"]), "initial execution roles")
    require(all(model.member(value) for value in initial.values()), "initial execution B domain")
    state = {name: values[:] for name, values in initial.items()}
    pairs = 0
    max_component = max(abs(x) for values in state.values() for value in values for x in value)
    first_non_b = None
    for event in structure_record["selected"]:
        record = word["program"][event]
        opcode, bank = record[:2]
        if opcode == "transport":
            plan = plans[event]
            out = apply_wrapper(state[bank], plan["right"], model)
            for bit in range(plan["rank"]):
                step = 1 << bit
                for address in range(SIZE):
                    if address & step:
                        continue
                    other = address | step
                    a, b = out[address], out[other]
                    numerators = model.ideal_pair_numerators(a, b)
                    if any(x % 2 for value in numerators for x in value):
                        return {"ok": False, "failure": {"event": event, "bank": bank,
                                "kind": "nonintegral_ideal_pair", "bit": bit,
                                "address": address, "inputs": [a, b],
                                "twice_ideal": numerators}, "pairs_checked": pairs}
                    ideal = tuple((a // 2, b // 2) for a, b in numerators)
                    actual = model.lift_pair(a, b)
                    require(actual == ideal, "signed-floor versus ideal pair equality")
                    out[address], out[other] = actual
                    pairs += 1
            state[bank] = apply_wrapper(out, plan["left"], model)
        else:
            source, coefficient = record[2:4]
            factor = Fraction(str(coefficient))
            p, q = factor.numerator, factor.denominator
            values = state[source]
            bad = next(((j, component, x) for j, value in enumerate(values)
                        for component, x in enumerate(value) if p * x % q), None)
            if bad is not None:
                return {"ok": False, "failure": {"event": event, "bank": bank,
                        "source": source, "kind": "nonintegral_fractional_add",
                        "coordinate": bad[0], "component": bad[1], "value": bad[2],
                        "numerator": p, "denominator": q}, "pairs_checked": pairs}
            state[bank] = [model.add(a, (p * b[0] // q, p * b[1] // q))
                           for a, b in zip(state[bank], values)]
        max_component = max(max_component, *(abs(x) for value in state[bank] for x in value))
        if first_non_b is None and not model.member(state[bank]):
            first_non_b = {"event": event, "bank": bank}
    cut = {name: state[name] for name in TARGETS}
    return {"ok": True, "pairs_checked": pairs, "first_non_b": first_non_b,
            "max_state_component": max_component, "cut_sha256": digest(cut),
            "cut_in_b": {name: model.member(value) for name, value in cut.items()}, "cut": cut}


def coefficient_fixture(slot):
    require(type(slot) is int and 0 <= slot < 58, "fixture slot")
    return [(((37 * slot + 17 * k + 3 * k.bit_count()) % 11) - 5,
             ((19 * slot + 29 * k + 5 * k.bit_count()) % 13) - 6) for k in range(SIZE)]
