#!/usr/bin/env python3
"""Second flag-1 present-head scanner. It does not import verify.py.

Events are first indexed per endpoint register. Literal frames are frozensets;
spans are explicit XOR closures (at most 512 labels), so membership, rank and
nesting are set operations rather than row reduction. The head decomposition
is found by exhaustive subset search. Admission uses need() under -O.
"""

import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
MARKER = (
    "PASS_P104_PRESENT_HEAD_FLAG1_INDEPENDENT flag=1 head=232 "
    "preterminal_hosting=0 preterminal_span_hosting=0 drop_event=591 "
    "arrive_event=3473 source_span_drops=0 head_free_target_updates=6/6 "
    "no_new_kappa"
)
INPUTS = (
    "research/p104-joint-unit-flags/CERTIFICATE.json",
    "research/p104-native-channel/inputs/LOWRANK-WITNESS.json",
    "research/p104-endpoint-geometric-budget/geometry.py",
)
SOURCE_LINE = "sources = [paths[f'X{s}'] for s in range(104)]"
TARGET_LINE = "targets = [paths[f'Y{t}'] for t in range(104)]"
FLAG_INDEX = 1
HIT_FLAGS = (0, 1, 9, 43)


def need(ok, message):
    if not ok:
        raise ValueError(message)


def pairs_unique(pairs):
    value = {}
    for key, item in pairs:
        need(key not in value, "duplicate JSON key")
        value[key] = item
    return value


def read_json(path):
    raw = Path(path).read_bytes()
    need(len(raw) <= 2_000_000, "input exceeds 2 MB")
    return json.loads(raw, object_pairs_hook=pairs_unique)


def frame_set(frame):
    need(type(frame) is list, "frame")
    values = []
    for entry in frame:
        need(type(entry) is int and 0 < entry < 512, "frame entry")
        values.append(entry)
    folded = frozenset(values)
    need(len(folded) == len(values), "duplicate frame vector")
    return folded


def closure(frame):
    """Explicit GF(2) span of an independent frame."""
    span = {0}
    for vector in frame_set(frame):
        span = span | {vector ^ old for old in span}
    need(len(span) == 1 << len(frame), "dependent frame")
    return frozenset(span)


def dimension(frame):
    return len(closure(frame)).bit_length() - 1


def subset_xor(vector, frame):
    found = []
    for mask in range(1 << len(frame)):
        acc = 0
        chosen = []
        for position, entry in enumerate(frame):
            if mask & (1 << position):
                acc ^= entry
                chosen.append(entry)
        if acc == vector:
            found.append(sorted(chosen))
    need(len(found) <= 1, "non-unique decomposition")
    return found[0] if found else None


def index_registers(program, wanted):
    table = {name: [] for name in wanted}
    joint = 0
    for index, event in enumerate(program):
        need(type(event) is list and 1 <= len(event) <= 8, "event shape")
        present = {item for item in event if type(item) is str and item in table}
        if len(present) == len(table):
            joint += 1
        for name in present:
            table[name].append(index)
    return table, joint


def frames_of(event, name):
    if event[0] == "transport" and event[1] == name:
        return [("before", event[2]), ("after", event[3])]
    if event[0] == "add" and name in (event[1], event[2]):
        return [("add", event[-1])]
    return []


def pin_sources():
    manifest = read_json(HERE / "SOURCES.json")
    rows = [row for row in manifest["files"] if row["usage"] == "input"]
    need(tuple(row["path"] for row in rows) == INPUTS, "input inventory")
    pinned = {}
    for row in rows:
        raw = (ROOT / row["path"]).read_bytes()
        need(hashlib.sha256(raw).hexdigest() == row["sha256"], "source hash: " + row["path"])
        pinned[row["path"]] = raw
    return pinned


def evaluate():
    pinned = pin_sources()
    geometry = pinned[
        "research/p104-endpoint-geometric-budget/geometry.py"
    ].decode("utf-8")
    need(SOURCE_LINE in geometry and TARGET_LINE in geometry, "geometry naming")
    helpers = json.loads(
        pinned["research/p104-joint-unit-flags/CERTIFICATE.json"],
        object_pairs_hook=pairs_unique,
    )["helpers"]
    witness = json.loads(
        pinned["research/p104-native-channel/inputs/LOWRANK-WITNESS.json"],
        object_pairs_hook=pairs_unique,
    )
    program = witness["program"]
    need(len(helpers) == 208 and len(program) == 4058, "sizes")
    hits = [
        index
        for index, row in enumerate(helpers)
        if row["basis"][0] in witness["final_frames"][f"Y{row['target']}"]
    ]
    need(hits == list(HIT_FLAGS), "hit-flag census drift")
    need(FLAG_INDEX in hits, "flag 1 left the present-head class")
    helper = helpers[FLAG_INDEX]
    head = helper["basis"][0]
    source = f"X{helper['source']}"
    target = f"Y{helper['target']}"
    table, joint = index_registers(program, (source, target))
    source_indices = table[source]
    target_indices = table[target]
    need(source_indices and target_indices, "endpoint silence")

    source_hits = []
    source_frames = 0
    source_span_frames = 0
    source_span_drops = []
    transports = []
    for index in source_indices:
        event = program[index]
        if event[0] == "transport" and event[1] == source:
            transports.append(event)
        for role, frame in frames_of(event, source):
            literal = frame_set(frame)
            source_frames += 1
            if head in closure(frame):
                source_span_frames += 1
            else:
                source_span_drops.append(index)
            if head in literal:
                source_hits.append(
                    {
                        "event": index,
                        "opcode": event[0],
                        "role": role,
                        "frame": sorted(literal),
                    }
                )

    target_hits = []
    target_span_hits = []
    target_pool = set()
    updates = []
    head_free_updates = 0
    for index in target_indices:
        event = program[index]
        if event[0] == "transport" and event[1] == target:
            transports.append(event)
        if event[0] == "add" and event[1] == target:
            updates.append(index)
            if head not in closure(event[-1]):
                head_free_updates += 1
        for role, frame in frames_of(event, target):
            literal = frame_set(frame)
            target_pool |= literal
            if head in closure(frame):
                target_span_hits.append((index, role))
            if head in literal:
                target_hits.append(
                    {
                        "event": index,
                        "opcode": event[0],
                        "role": role,
                        "frame": sorted(literal),
                    }
                )

    drop = source_indices[0]
    drop_event = program[drop]
    need(drop_event[0] == "transport" and drop_event[1] == source, "first source op")
    drop_before = sorted(frame_set(drop_event[2]))
    drop_after = sorted(frame_set(drop_event[3]))
    need(drop_before == [head], "drop before")
    need(head not in drop_after, "drop after")
    need(len(target_hits) == 1, "unexpected target head hosting count")
    arrive = target_hits[0]
    need(arrive["opcode"] == "transport" and arrive["role"] == "after", "arrive shape")
    need(arrive["event"] == target_indices[-1], "arrive not terminal")
    arrive_event = program[arrive["event"]]
    arrive_before = sorted(frame_set(arrive_event[2]))
    arrive_after = sorted(frame_set(arrive_event[3]))
    need(head not in arrive_before and head in arrive_after, "arrive frames")
    preterminal = [row for row in target_hits if row["event"] < arrive["event"]]
    need(target_span_hits, "no span hosting on target")
    span_open, span_role = target_span_hits[0]
    span_preterminal = [row for row in target_span_hits if row[0] < arrive["event"]]
    after_drop = any(
        row["event"] > drop or (row["event"] == drop and row["role"] == "after")
        for row in source_hits
    )
    nested = all(closure(event[2]) <= closure(event[3]) for event in transports)
    steps = all(
        event[4] == dimension(event[3]) - dimension(event[2]) for event in transports
    )
    source_initial = witness["initial_frames"][source]
    source_final = witness["final_frames"][source]
    target_initial = witness["initial_frames"][target]
    target_final = witness["final_frames"][target]
    finals_with_head = len(
        [name for name, frame in witness["final_frames"].items()
         if name.startswith("Y") and head in frame]
    )
    receipt = {
        "schema_version": 1,
        "claim_id": "p104-present-head-flag1-audit",
        "pinned_main": "6f100d4bb5083f8c35d96fd95a539811c62f245c",
        "flag_index": FLAG_INDEX,
        "source": helper["source"],
        "target": helper["target"],
        "basis_head": head,
        "departure_choice": helper["departure_choice"],
        "arrival_choice": helper["arrival_choice"],
        "basis": helper["basis"],
        "source_register": source,
        "target_register": target,
        "source_initial": source_initial,
        "source_final": source_final,
        "target_initial": target_initial,
        "target_final": target_final,
        "source_initial_is_basis_head": source_initial == [head],
        "target_final_contains_basis_head": head in target_final,
        "source_frame_restored": frame_set(source_initial) == frame_set(source_final),
        "target_frame_restored": frame_set(target_initial) == frame_set(target_final),
        "source_rank_initial": dimension(source_initial),
        "source_rank_final": dimension(source_final),
        "target_rank_initial": dimension(target_initial),
        "target_rank_final": dimension(target_final),
        "source_first_event": source_indices[0],
        "source_last_event": source_indices[-1],
        "target_first_event": target_indices[0],
        "target_last_event": target_indices[-1],
        "source_event_count": len(source_indices),
        "target_event_count": len(target_indices),
        "joint_source_target_events": joint,
        "basis_head_drop_event": drop,
        "basis_head_drop_before": drop_before,
        "basis_head_drop_after": drop_after,
        "basis_head_arrive_event": arrive["event"],
        "basis_head_arrive_before": arrive_before,
        "basis_head_arrive_after": arrive_after,
        "hosting_gap_events": arrive["event"] - drop,
        "source_annotations_containing_basis_head": len(source_hits),
        "target_annotations_containing_basis_head": len(target_hits),
        "target_preterminal_annotations_containing_basis_head": len(preterminal),
        "source_head_annotations": source_hits,
        "target_head_annotations": target_hits,
        "target_annotated_vectors": sorted(target_pool),
        "basis_head_in_any_target_annotation": head in target_pool,
        "basis_head_in_source_after_drop": after_drop,
        "drop_after_span_decomposition_of_head": subset_xor(head, drop_event[3]),
        "drop_transport_span_nested": closure(drop_event[2]) <= closure(drop_event[3]),
        "source_annotation_count": source_frames,
        "source_annotations_span_hosting_basis_head": source_span_frames,
        "source_span_drop_events": source_span_drops,
        "target_span_first_hosting_event": span_open,
        "target_span_first_hosting_role": span_role,
        "target_preterminal_annotations_span_hosting_basis_head": len(span_preterminal),
        "target_arrive_before_span": sorted(closure(arrive_event[2])),
        "target_update_events": updates,
        "target_updates_in_head_free_span": head_free_updates,
        "target_last_update_event": updates[-1],
        "target_events_after_span_cohost_open": len(
            [index for index in target_indices if index > span_open]
        ),
        "source_events_after_span_cohost_open": [
            index for index in source_indices if index > span_open
        ],
        "endpoint_transport_count": len(transports),
        "endpoint_transports_span_nested_upward": nested,
        "endpoint_transport_rank_steps_match": steps,
        "targets_whose_final_contains_basis_head_among_all": finals_with_head,
        "hit_flags_from_census": list(HIT_FLAGS),
        "flag_is_present_head_case": True,
        "obstruction": (
            "published_channel_hosts_basis_head_on_matched_target_only_at_"
            "terminal_transport_literally_and_in_span_after_every_target_update"
        ),
        "no_new_kappa": True,
        "selected_kappa": "0.001672660197076918",
    }
    need(receipt["target_final_contains_basis_head"] is True, "left present-head class")
    need(receipt["target_preterminal_annotations_containing_basis_head"] == 0, "preterminal")
    need(receipt["target_preterminal_annotations_span_hosting_basis_head"] == 0, "span preterminal")
    need(receipt["source_span_drop_events"] == [], "source lost head direction")
    need(receipt["target_updates_in_head_free_span"] == len(updates), "head-hosting update")
    need(receipt["target_events_after_span_cohost_open"] == 0, "target event after cohost")
    need(receipt["basis_head_in_source_after_drop"] is False, "source relisted head")
    need(receipt["joint_source_target_events"] == 0, "joint endpoint event")
    need(nested and steps, "transport semantics")
    return receipt


def main():
    observed = evaluate()
    expected = read_json(HERE / "CERTIFICATE.json")
    need(observed == expected, "certificate mismatch")
    print(MARKER)


if __name__ == "__main__":
    main()
