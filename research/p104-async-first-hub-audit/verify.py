#!/usr/bin/env python3
"""Independent data-only audit of PR5786's first temporal helper split.

ToikY with substantial OpenAI Codex assistance. Apache-2.0.
The retained word and plan are Ali Romman's work; NOTICE preserves predecessors.
No predecessor Python code is imported or executed by this checker.
"""
from collections import Counter
from copy import deepcopy
from fractions import Fraction
from hashlib import sha256
from pathlib import Path
import argparse
import gzip
import json


HERE = Path(__file__).resolve().parent
WORD_RAW = "7c393444fa5b9a6941471d02047beb2aa8285e5614bb052fb85458b69236a38a"
WORD_CANONICAL = "75f429fc0c8b206f4439bfbda4b621fc62ea892e6e3008c17409f2d3ee0981bb"
PLAN_RAW = "2c4878f78dc393339f8cccf24441d9bfb50257784459c2f253ebcb27c964211c"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def rational_map(value):
    return {int(k): Fraction(v) for k, v in value.items() if Fraction(v)}


def encoded(vector):
    return {str(k): str(v) for k, v in sorted(vector.items())}


def accumulate(destination, source, coefficient):
    for key, value in source.items():
        new = destination.get(key, 0) + coefficient * value
        if new:
            destination[key] = new
        else:
            destination.pop(key, None)


def frame_spaces(word):
    spaces = []
    for basis in word["frames"]:
        values = {0}
        for vector in basis:
            require(type(vector) is int and 0 < vector < 512 and vector not in values,
                    "independent nine-bit frame basis")
            values.update({old ^ vector for old in values})
        spaces.append(frozenset(values))
    return spaces


def forward_history(word, plan, spaces):
    """Propagate every public and dirty-owned input, recording physical contacts."""
    public = word["public"]
    size = public + word["owned_fields"]
    rows = [{j: Fraction(1)} for j in range(size)]
    frames = word["initial"][:] + [None] * word["owned_fields"]
    live_owned = set()
    wanted = {(item["time2"], item["role"])
              for kind in ("collection", "injection") for item in plan[kind]}
    wanted.add((plan["time2"], plan["pivot"]))
    snapshots = {}
    lifetimes = peak = 0

    def observe(time, middle=None):
        for contact_time, role in wanted:
            if contact_time != time:
                continue
            frame = plan["frame"] if middle and role == middle[1] else frames[role]
            snapshots[time, role] = {
                "row": rows[role].copy(), "frame": frame,
                "owned_live": role in live_owned,
            }

    for index, event in enumerate(word["program"]):
        observe(2 * index)
        opcode, target = event[:2]
        require(type(target) is int and 0 <= target < size, "source target role")
        if opcode == "MOVE":
            _, _, entrance, exit_frame, private = event
            require(frames[target] == entrance and (target in live_owned) == private,
                    "source MOVE frame and owned lifetime")
            require(spaces[exit_frame] < spaces[entrance] if private
                    else spaces[entrance] < spaces[exit_frame], "source nested MOVE")
            observe(2 * index + 1, event)
            frames[target] = exit_frame
        elif opcode == "INIT":
            require(target >= public and target not in live_owned,
                    "source owned initialization")
            live_owned.add(target)
            lifetimes += 1
            peak = max(peak, len(live_owned))
            rows[target] = {}
            frames[target] = event[2]
        elif opcode == "CLEAR":
            require(target in live_owned and frames[target] == event[2],
                    "source owned erasure frame")
            # This models the predecessor's charged erasure operation. It does
            # not assume the buffer was zero before CLEAR.
            rows[target] = {}
            frames[target] = None
            live_owned.remove(target)
        else:
            coefficient = Fraction(event[-2])
            require(coefficient and frames[target] == event[-1],
                    "source scalar destination frame")
            if opcode == "SCALE":
                rows[target] = {key: coefficient * value
                                for key, value in rows[target].items()}
            else:
                require(opcode in ("ADD", "COPY"), "source scalar opcode")
                source = event[2]
                require(source != target and 0 <= source < size
                        and frames[source] == frames[target], "source common scalar frame")
                if opcode == "COPY":
                    require(target in live_owned and not rows[target],
                            "source COPY into cleared owned field")
                    rows[target] = {}
                accumulate(rows[target], rows[source], coefficient)
    observe(2 * len(word["program"]))
    require(not live_owned and frames[:public] == word["final"]
            and frames[public:] == [None] * word["owned_fields"], "source boundary frames")
    live = set(word["live"])
    for output, row in enumerate(rows):
        expected = {output: Fraction(1)} if output < public else {}
        if output - 112 in live:
            expected[output - 112] = Fraction(1)
        require(row == expected, "source full arbitrary-input endpoint")
    return snapshots, {
        "input_columns": size, "output_rows": size,
        "coefficient_positions_checked": size * size,
        "endpoint": "I + sum e_(r+112) e_r^T on public coordinates; zero owned outputs",
        "endpoint_sha256": sha256(canonical([encoded(row) for row in rows])).hexdigest(),
        "owned_lifetimes": lifetimes, "peak_live_owned": peak,
    }


def suffix_columns(word, plan):
    """Reverse-mode delivery propagation, independent of the forward row table."""
    size = word["public"] + word["owned_fields"]
    effects = [{j: Fraction(1)} for j in range(size)]
    wanted = {(item["time2"], item["role"]) for item in plan["injection"]}
    snapshots = {}

    def observe(time):
        for contact_time, role in wanted:
            if contact_time == time:
                snapshots[time, role] = effects[role].copy()

    observe(2 * len(word["program"]))
    for index in range(len(word["program"]) - 1, -1, -1):
        event = word["program"][index]
        opcode, target = event[:2]
        if opcode in ("INIT", "CLEAR"):
            effects[target] = {}
        elif opcode == "SCALE":
            coefficient = Fraction(event[-2])
            effects[target] = {key: coefficient * value
                               for key, value in effects[target].items()}
        elif opcode in ("ADD", "COPY"):
            accumulate(effects[event[2]], effects[target], Fraction(event[-2]))
            if opcode == "COPY":
                effects[target] = {}
        else:
            require(opcode == "MOVE", "reverse source opcode")
        observe(2 * index)
        if opcode == "MOVE":
            observe(2 * index + 1)
    return snapshots


def audit_plan(word, plan, spaces, prefixes, suffixes):
    require(plan["source_sha256"] == WORD_CANONICAL, "step source binding")
    frame, cut = plan["frame"], plan["time2"]
    queries = plan["queries"]
    require(len(queries) == len(set(queries)), "distinct paid queries")
    for kind in ("collection", "injection"):
        for item in plan[kind]:
            time, role = item["time2"], item["role"]
            require(type(time) is int and 0 <= time <= 2 * len(word["program"]),
                    "contact time range")
            require(type(role) is int and 0 <= role < word["public"] + word["owned_fields"]
                    and Fraction(item["coefficient"]), "contact operand")
            require(time <= cut if kind == "collection" else cut <= time,
                    "causal collection/cut/injection order")
            require(time % 2 == 0 or time // 2 in queries, "unpaid interior contact")
            require(prefixes[time, role]["frame"] == frame, "actual contact frame")
    require([word["program"][index] for index in sorted(queries)] == plan["query_events"],
            "exact paid query binding")
    require(prefixes[cut, plan["pivot"]]["frame"] == frame, "physical pivot at cut")
    query_receipts = []
    delta = Counter()
    for index in sorted(queries):
        event = word["program"][index]
        require(event[0] == "MOVE", "paid contact subdivides MOVE")
        _, role, entrance, exit_frame, private = event
        require(spaces[exit_frame] < spaces[frame] < spaces[entrance] if private
                else spaces[entrance] < spaces[frame] < spaces[exit_frame],
                "strict actual intermediate GF2 frame")
        a, middle, b = (len(word["frames"][j]) for j in (entrance, frame, exit_frame))
        ranks = [abs(a - middle), abs(middle - b)]
        delta.update(ranks)
        delta[abs(a - b)] -= 1
        query_receipts.append({"index": index, "event": event,
                               "frame_dimensions": [a, middle, b],
                               "replacement_ranks": ranks, "replaced_rank": abs(a - b)})
    collection, delivery = {}, {}
    for item in plan["collection"]:
        accumulate(collection, prefixes[item["time2"], item["role"]]["row"],
                   Fraction(item["coefficient"]))
    for item in plan["injection"]:
        accumulate(delivery, suffixes[item["time2"], item["role"]],
                   Fraction(item["coefficient"]))
    require(collection == rational_map(plan["input"]), "complete temporal collection row")
    require(delivery == rational_map(plan["output"]), "complete temporal delivery column")
    main = set(word["live"]) | {role + 112 for role in word["live"]}
    eligible = {role for role in range(word["public"]) if role not in main
                and word["initial"][role] == 3 and word["final"][role] == 127}
    require(set(collection) | set(delivery) <= eligible, "actual independent full-boundary helpers")
    pairing = sum(value * delivery.get(role, 0) for role, value in collection.items())
    require(pairing == 1 and delivery.get(plan["pivot"]), "unit pairing and physical pivot")
    return {
        "collection_row": encoded(collection), "delivery_column": encoded(delivery),
        "pairing": str(pairing), "eligible_full_boundary_helpers": len(eligible),
        "helper_133_is_eligible": 133 in eligible,
        "paid_access": query_receipts,
        "paid_access_delta": {str(rank): count for rank, count in sorted(delta.items()) if count},
    }


def split_replay(word, plan, spaces, omit_clear=False, omit_swap_scale=False):
    """Emit and replay the first split on an independent formal label namespace."""
    original_size = word["public"] + word["owned_fields"]
    fresh, buffer = original_size, original_size + 1
    size = original_size + 2
    pivot, frame, cut = plan["pivot"], plan["frame"], plan["time2"]
    delivery = rational_map(plan["output"])
    require(rational_map(plan["input"]) == {pivot: Fraction(1)}
            and delivery[pivot] == 1, "specialized first-step boundary basis")
    basis = [(role, coefficient) for role, coefficient in sorted(delivery.items())
             if role != pivot]
    events = [["ADD", role, pivot, str(coefficient), 3] for role, coefficient in basis]
    first = min(item["time2"] for item in plan["collection"])
    last = max(item["time2"] for item in plan["injection"])

    def renamed(event, time):
        result = event[:]
        for position in ((1, 2) if event[0] in ("ADD", "COPY") else (1,)):
            if time >= cut and result[position] == pivot:
                result[position] = fresh
        return result

    def swap(left, right, first_swap=False):
        events.extend([["ADD", left, right, "1", frame],
                       ["ADD", right, left, "-1", frame],
                       ["ADD", left, right, "1", frame]])
        if not (first_swap and omit_swap_scale):
            events.append(["SCALE", right, "-1", frame])

    def contact(time):
        if time == first:
            events.append(["INIT", buffer, frame])
        for item in plan["collection"]:
            if item["time2"] == time:
                events.append(["ADD", buffer, item["role"], item["coefficient"], frame])
        if time == cut:
            swap(pivot, buffer, first_swap=True)
            swap(fresh, buffer)
            events.append(["ADD", buffer, pivot, "-1", frame])
        for item in plan["injection"]:
            if item["time2"] == time:
                role = fresh if item["role"] == pivot else item["role"]
                events.append(["ADD", role, buffer, item["coefficient"], frame])
        if time == last and not omit_clear:
            events.append(["CLEAR", buffer, frame])

    for index, event in enumerate(word["program"]):
        contact(2 * index)
        if index in plan["queries"]:
            _, role, entrance, exit_frame, private = event
            events.append(renamed(["MOVE", role, entrance, frame, private], 2 * index))
            contact(2 * index + 1)
            events.append(renamed(["MOVE", role, frame, exit_frame, private], 2 * index + 1))
        else:
            events.append(renamed(event, 2 * index))
    contact(2 * len(word["program"]))
    events.extend([["ADD", role, fresh, str(-coefficient), 127]
                   for role, coefficient in reversed(basis)])

    rows = [{role: Fraction(1)} for role in range(size)]
    frames = word["initial"][:] + [None] * word["owned_fields"] + [frame, None]
    owned = set(range(word["public"], original_size)) | {buffer}
    live_owned = set()
    lifetimes = peak = buffer_inits = buffer_clears = 0
    before_clear = None
    for event in events:
        opcode, target = event[:2]
        require(type(target) is int and 0 <= target < size, "split target role")
        if opcode == "INIT":
            require(target in owned and target not in live_owned,
                    "split owned initialization")
            live_owned.add(target)
            lifetimes += 1
            peak = max(peak, len(live_owned))
            buffer_inits += int(target == buffer)
            rows[target] = {}
            frames[target] = event[2]
        elif opcode == "CLEAR":
            require(target in live_owned and frames[target] == event[2],
                    "split owned erasure frame")
            if target == buffer:
                before_clear = rows[target].copy()
                buffer_clears += 1
            rows[target] = {}
            frames[target] = None
            live_owned.remove(target)
        elif opcode == "MOVE":
            _, _, entrance, exit_frame, private = event
            require(frames[target] == entrance and (target in live_owned) == private,
                    "split MOVE frame and ownership")
            require(spaces[exit_frame] < spaces[entrance] if private
                    else spaces[entrance] < spaces[exit_frame], "split strict nested MOVE")
            frames[target] = exit_frame
        else:
            coefficient = Fraction(event[-2])
            require(coefficient and frames[target] == event[-1],
                    "split scalar destination frame")
            if opcode == "SCALE":
                rows[target] = {key: coefficient * value
                                for key, value in rows[target].items()}
            else:
                require(opcode in ("ADD", "COPY"), "split scalar opcode")
                source = event[2]
                require(source != target and 0 <= source < size
                        and frames[source] == frames[target], "split common scalar frame")
                if opcode == "COPY":
                    require(target in live_owned and not rows[target],
                            "split COPY into cleared owned field")
                    rows[target] = {}
                accumulate(rows[target], rows[source], coefficient)
    live = set(word["live"])
    for role, row in enumerate(rows):
        expected = {role: Fraction(1)} if role < word["public"] or role == fresh else {}
        if role - 112 in live:
            expected[role - 112] = Fraction(1)
        require(row == expected, "split arbitrary-input endpoint at role " + str(role))
    expected_frames = word["final"][:] + [None] * word["owned_fields"] + [127, None]
    expected_frames[pivot] = frame
    require(frames == expected_frames and not live_owned, "split final frames and owned closure")
    require(before_clear == {fresh: Fraction(1), pivot: Fraction(-1)},
            "split retained buffer before charged erasure")
    require(buffer_inits == buffer_clears == 1 and lifetimes == 25 and peak <= 13,
            "split charged owned lifetime census")
    return {
        "formal_input_axes": size, "coefficient_positions_checked": size * size,
        "fresh_public_label": fresh, "new_owned_buffer_label": buffer,
        "retired_pivot_final_frame": frame, "fresh_final_frame": 127,
        "program_events": len(events), "owned_lifetimes": lifetimes,
        "peak_live_owned": peak, "new_buffer_init_count": buffer_inits,
        "new_buffer_clear_count": buffer_clears, "before_clear_row": encoded(before_clear),
        "endpoint_sha256": sha256(canonical([encoded(row) for row in rows])).hexdigest(),
        "event_stream_sha256": sha256(canonical(events)).hexdigest(),
        "label_scope": "Independent namespace; not a byte-identity claim for the author's emitted word",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true",
                        help="emit a candidate result without comparing RESULT.json; never writes files")
    args = parser.parse_args()
    raw = (HERE / "inputs/WORD.json.gz").read_bytes()
    plan_bytes = (HERE / "inputs/PLAN.json").read_bytes()
    require(sha256(raw).hexdigest() == WORD_RAW, "raw source WORD authentication")
    require(sha256(plan_bytes).hexdigest() == PLAN_RAW, "raw PLAN authentication")
    word, plans = json.loads(gzip.decompress(raw)), json.loads(plan_bytes)
    require(sha256(canonical(word)).hexdigest() == WORD_CANONICAL,
            "canonical source WORD authentication")
    require(plans["source_canonical_sha256"] == WORD_CANONICAL, "PLAN source binding")
    require(word["public"] == 767 and word["owned_fields"] == 22
            and len(word["program"]) == 25882, "fixed source dimensions")
    plan = plans["steps"][0]
    require((plan["pivot"], plan["frame"], plan["time2"]) == (696, 1031, 27044),
            "fixed first-step contact")
    spaces = frame_spaces(word)
    prefixes, endpoint = forward_history(word, plan, spaces)
    suffixes = suffix_columns(word, plan)
    result = audit_plan(word, plan, spaces, prefixes, suffixes)
    require(result["collection_row"] == {"696": "1"}, "first-step exact input")
    require(result["delivery_column"] == {"133": "2", "696": "1", "697": "1",
                                           "699": "1", "709": "1", "733": "1"},
            "first-step exact output including helper hole")
    require(result["paid_access_delta"] == {"3": 1, "4": 1, "7": -1},
            "first-step actual paid subdivision")
    require(prefixes[27501, 770]["owned_live"], "owned injection is in its live interval")
    controls = []
    changes = [
        ("omitted_collection", "complete temporal collection row",
         lambda p: p.update(collection=[])),
        ("omitted_owned_injection", "complete temporal delivery column",
         lambda p: p["injection"].pop(2)),
        ("injection_before_cut", "causal collection/cut/injection order",
         lambda p: p["injection"][0].update(time2=27042)),
        ("wrong_source", "step source binding",
         lambda p: p.update(source_sha256="0" * 64)),
        ("unpaid_owned_interior_query", "unpaid interior contact",
         lambda p: p.update(queries=[])),
    ]
    for name, expected, change in changes:
        bad = deepcopy(plan)
        change(bad)
        try:
            audit_plan(word, bad, spaces, prefixes, suffixes)
        except ValueError as error:
            require(str(error) == expected, "control rejected for unintended reason: " + name)
            controls.append({"name": name, "rejected": True, "reason": str(error)})
        else:
            raise ValueError("control accepted: " + name)
    split = split_replay(word, plan, spaces)
    for name, options in (("omitted_new_buffer_CLEAR", {"omit_clear": True}),
                          ("omitted_first_swap_SCALE", {"omit_swap_scale": True})):
        try:
            split_replay(word, plan, spaces, **options)
        except ValueError as error:
            require(str(error).startswith("split arbitrary-input endpoint at role "),
                    "split control rejected for unintended reason: " + name)
            controls.append({"name": name, "rejected": True, "reason": str(error)})
        else:
            raise ValueError("split control accepted: " + name)
    contacts = []
    for kind in ("collection", "injection"):
        for item in plan[kind]:
            physical = prefixes[item["time2"], item["role"]]
            contacts.append({"kind": kind, **item, "actual_frame": physical["frame"],
                             "owned_live": physical["owned_live"]})
    output = {
        "schema": "p104-async-first-hub-audit/1",
        "scope": "Finite exact first-step temporal contacts and literal scalar/frame restoration; no native phase, full caller or kappa admission",
        "source_raw_sha256": WORD_RAW, "source_canonical_sha256": WORD_CANONICAL,
        "plan_raw_sha256": PLAN_RAW, "source_endpoint": endpoint,
        "pivot": plan["pivot"], "frame": plan["frame"], "cut_time2": plan["time2"],
        "contacts": contacts, **result, "literal_first_split": split,
        "failure_controls": controls,
        "erasure_scope": "INIT/CLEAR use the predecessor's charged owned-erasure semantics",
    }
    if not args.emit:
        require(canonical(output) == canonical(json.loads(
            (HERE / "RESULT.json").read_text(encoding="utf-8"))),
            "frozen RESULT.json mismatch")
    print(json.dumps(output, sort_keys=True, indent=2))
    print("PASS_P104_ASYNC_FIRST_HUB_AUDIT")


if __name__ == "__main__":
    main()
