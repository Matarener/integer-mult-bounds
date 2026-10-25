#!/usr/bin/env python3
"""Read-only basis-head hosting audit for matched flag 2.

Admission uses need() and remains active under python -O. This module does
not import independent.py or any predecessor verifier.
"""

import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
MARKER = (
    "PASS_P104_ABSENT_HEAD_FLAG2 flag=2 head=488 "
    "target_hosting=0 drop_event=494 no_new_kappa"
)
INPUTS = (
    "research/p104-joint-unit-flags/CERTIFICATE.json",
    "research/p104-native-channel/inputs/LOWRANK-WITNESS.json",
    "research/p104-endpoint-geometric-budget/geometry.py",
)
SOURCE_LINE = "sources = [paths[f'X{s}'] for s in range(104)]"
TARGET_LINE = "targets = [paths[f'Y{t}'] for t in range(104)]"
FLAG_INDEX = 2
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


def register_name(item):
    if type(item) is not str or len(item) < 2 or item[0] not in "XY":
        return None
    if not item[1:].isdigit() or int(item[1:]) > 103:
        return None
    return item


def annotated_frames(event, name):
    frames = []
    if event[0] == "transport" and event[1] == name:
        need(type(event[2]) is list and type(event[3]) is list, "transport frames")
        frames.append(("before", list(event[2])))
        frames.append(("after", list(event[3])))
    elif event[0] == "add" and name in (event[1], event[2]):
        need(type(event[-1]) is list, "add frame")
        frames.append(("add", list(event[-1])))
    return frames


def pin_sources():
    manifest = read_json(HERE / "SOURCES.json")
    rows = manifest["files"]
    inputs = [row for row in rows if row["usage"] == "input"]
    need(tuple(row["path"] for row in inputs) == INPUTS, "input inventory")
    pinned = {}
    for row in inputs:
        path = ROOT / row["path"]
        raw = path.read_bytes()
        need(len(raw) <= 2_000_000, "source size")
        digest = hashlib.sha256(raw).hexdigest()
        need(digest == row["sha256"], "source hash: " + row["path"])
        pinned[row["path"]] = raw
    return pinned


def hit_flag_indices(helpers, witness):
    hits = []
    for index, row in enumerate(helpers):
        head = row["basis"][0]
        target = f"Y{row['target']}"
        if head in witness["final_frames"][target]:
            hits.append(index)
    return hits


def build_receipt(witness, helpers):
    need(len(helpers) == 208, "flag count")
    need(len(witness["program"]) == 4058, "word length")
    hits = hit_flag_indices(helpers, witness)
    need(hits == list(HIT_FLAGS), "hit-flag census drift")
    need(FLAG_INDEX not in hits, "flag 2 unexpectedly hosts head in final")
    helper = helpers[FLAG_INDEX]
    head = helper["basis"][0]
    source = f"X{helper['source']}"
    target = f"Y{helper['target']}"
    program = witness["program"]
    source_events = []
    target_events = []
    joint = 0
    source_head = []
    target_head = []
    target_vectors = set()
    for index, event in enumerate(program):
        need(type(event) is list and 1 <= len(event) <= 8, "event shape")
        names = []
        for item in event:
            name = register_name(item)
            if name is not None:
                names.append(name)
        kinds = {name[0] for name in names}
        if "X" in kinds and "Y" in kinds and (source in names or target in names):
            if source in names and target in names:
                joint += 1
        if source in names:
            source_events.append(index)
            for role, frame in annotated_frames(event, source):
                if head in frame:
                    source_head.append(
                        {
                            "event": index,
                            "opcode": event[0],
                            "role": role,
                            "frame": frame,
                        }
                    )
        if target in names:
            target_events.append(index)
            for role, frame in annotated_frames(event, target):
                target_vectors.update(frame)
                if head in frame:
                    target_head.append(
                        {
                            "event": index,
                            "opcode": event[0],
                            "role": role,
                            "frame": frame,
                        }
                    )
    need(source_events and target_events, "endpoint silence")
    drop = source_events[0]
    drop_event = program[drop]
    need(drop_event[0] == "transport" and drop_event[1] == source, "first source op")
    need(drop_event[2] == [head], "drop before-frame")
    need(head not in drop_event[3], "drop after-frame still hosts head")
    after_drop = False
    for row in source_head:
        if row["event"] > drop:
            after_drop = True
        if row["event"] == drop and row["role"] == "after":
            after_drop = True
    finals_with_head = sum(
        1 for index in range(104) if head in witness["final_frames"][f"Y{index}"]
    )
    source_initial = witness["initial_frames"][source]
    source_final = witness["final_frames"][source]
    target_initial = witness["initial_frames"][target]
    target_final = witness["final_frames"][target]
    return {
        "schema_version": 1,
        "claim_id": "p104-absent-head-flag2-audit",
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
        "source_frame_restored": sorted(source_initial) == sorted(source_final),
        "target_frame_restored": sorted(target_initial) == sorted(target_final),
        "source_first_event": source_events[0],
        "source_last_event": source_events[-1],
        "target_first_event": target_events[0],
        "target_last_event": target_events[-1],
        "source_event_count": len(source_events),
        "target_event_count": len(target_events),
        "joint_source_target_events": joint,
        "basis_head_drop_event": drop,
        "basis_head_drop_before": list(drop_event[2]),
        "basis_head_drop_after": list(drop_event[3]),
        "source_annotations_containing_basis_head": len(source_head),
        "target_annotations_containing_basis_head": len(target_head),
        "source_head_annotations": source_head,
        "target_head_annotations": target_head,
        "target_annotated_vectors": sorted(target_vectors),
        "basis_head_in_any_target_annotation": head in target_vectors,
        "basis_head_in_source_after_drop": after_drop,
        "targets_whose_final_contains_basis_head_among_all": finals_with_head,
        "hit_flags_from_census": list(HIT_FLAGS),
        "flag_is_absent_head_case": True,
        "obstruction": "published_channel_never_hosts_basis_head_on_matched_target",
        "no_new_kappa": True,
        "selected_kappa": "0.001672660197076918",
    }


def evaluate():
    pinned = pin_sources()
    geometry = pinned[
        "research/p104-endpoint-geometric-budget/geometry.py"
    ].decode("utf-8")
    need(SOURCE_LINE in geometry, "source naming left the geometry")
    need(TARGET_LINE in geometry, "target naming left the geometry")
    certificate = json.loads(
        pinned["research/p104-joint-unit-flags/CERTIFICATE.json"],
        object_pairs_hook=pairs_unique,
    )
    witness = json.loads(
        pinned["research/p104-native-channel/inputs/LOWRANK-WITNESS.json"],
        object_pairs_hook=pairs_unique,
    )
    receipt = build_receipt(witness, certificate["helpers"])
    need(receipt["target_annotations_containing_basis_head"] == 0, "target hosted head")
    need(receipt["basis_head_in_any_target_annotation"] is False, "target vector set")
    need(receipt["basis_head_in_source_after_drop"] is False, "source retained head")
    need(receipt["joint_source_target_events"] == 0, "joint endpoint event")
    need(receipt["target_final_contains_basis_head"] is False, "final hosts head")
    need(receipt["no_new_kappa"] is True, "kappa claim crept in")
    return receipt


def admit(observed, expected):
    need(observed == expected, "certificate mismatch")


def main():
    observed = evaluate()
    expected = read_json(HERE / "CERTIFICATE.json")
    admit(observed, expected)
    print(MARKER)


if __name__ == "__main__":
    main()
