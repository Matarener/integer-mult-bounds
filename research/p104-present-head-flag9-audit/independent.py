#!/usr/bin/env python3
"""Second flag-9 present-head scanner. It does not import verify.py.

Frames are accumulated as frozensets per register. Drop and late-arrive
detection use transport before/after sets. Admission uses need() under -O.
"""

import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
MARKER = (
    "PASS_P104_PRESENT_HEAD_FLAG9_INDEPENDENT flag=9 head=196 "
    "preterminal_hosting=0 drop_event=500 arrive_event=3489 no_new_kappa"
)
INPUTS = (
    "research/p104-joint-unit-flags/CERTIFICATE.json",
    "research/p104-native-channel/inputs/LOWRANK-WITNESS.json",
    "research/p104-endpoint-geometric-budget/geometry.py",
)
SOURCE_LINE = "sources = [paths[f'X{s}'] for s in range(104)]"
TARGET_LINE = "targets = [paths[f'Y{t}'] for t in range(104)]"
FLAG_INDEX = 9
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


def frame_set(frame):
    need(type(frame) is list, "frame")
    values = []
    for entry in frame:
        need(type(entry) is int, "frame entry")
        values.append(entry)
    folded = frozenset(values)
    need(len(folded) == len(values), "duplicate frame vector")
    return folded


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
    need(len(helpers) == 208 and len(witness["program"]) == 4058, "sizes")
    hits = []
    for index, row in enumerate(helpers):
        if row["basis"][0] in witness["final_frames"][f"Y{row['target']}"]:
            hits.append(index)
    need(hits == list(HIT_FLAGS), "hit-flag census drift")
    need(FLAG_INDEX in hits, "flag 9 left the present-head class")
    helper = helpers[FLAG_INDEX]
    head = helper["basis"][0]
    source = f"X{helper['source']}"
    target = f"Y{helper['target']}"
    source_hits = []
    target_hits = []
    source_indices = []
    target_indices = []
    target_pool = set()
    joint = 0
    drop = None
    drop_before = None
    drop_after = None
    arrive_before = None
    arrive_after = None
    for index, event in enumerate(witness["program"]):
        names = [register_name(item) for item in event]
        names = [name for name in names if name is not None]
        if source in names and target in names:
            joint += 1
        if source in names:
            source_indices.append(index)
            if event[0] == "transport" and event[1] == source:
                before = frame_set(event[2])
                after = frame_set(event[3])
                if drop is None:
                    drop = index
                    drop_before = sorted(before)
                    drop_after = sorted(after)
                if head in before:
                    source_hits.append(
                        {
                            "event": index,
                            "opcode": "transport",
                            "role": "before",
                            "frame": sorted(before),
                        }
                    )
                if head in after:
                    source_hits.append(
                        {
                            "event": index,
                            "opcode": "transport",
                            "role": "after",
                            "frame": sorted(after),
                        }
                    )
            elif event[0] == "add" and source in (event[1], event[2]):
                present = frame_set(event[-1])
                if head in present:
                    source_hits.append(
                        {
                            "event": index,
                            "opcode": "add",
                            "role": "add",
                            "frame": sorted(present),
                        }
                    )
        if target in names:
            target_indices.append(index)
            if event[0] == "transport" and event[1] == target:
                before = frame_set(event[2])
                after = frame_set(event[3])
                target_pool.update(before)
                target_pool.update(after)
                if head in before:
                    target_hits.append(
                        {
                            "event": index,
                            "opcode": "transport",
                            "role": "before",
                            "frame": sorted(before),
                        }
                    )
                if head in after:
                    target_hits.append(
                        {
                            "event": index,
                            "opcode": "transport",
                            "role": "after",
                            "frame": sorted(after),
                        }
                    )
            elif event[0] == "add" and target in (event[1], event[2]):
                present = frame_set(event[-1])
                target_pool.update(present)
                if head in present:
                    target_hits.append(
                        {
                            "event": index,
                            "opcode": "add",
                            "role": "add",
                            "frame": sorted(present),
                        }
                    )
    need(drop is not None, "missing drop")
    need(drop_before == [head], "drop before")
    need(head not in drop_after, "drop after")
    need(len(target_hits) == 1, "unexpected target head hosting count")
    arrive = target_hits[0]
    need(arrive["opcode"] == "transport" and arrive["role"] == "after", "arrive shape")
    need(arrive["event"] == target_indices[-1], "arrive not terminal")
    arrive_event = witness["program"][arrive["event"]]
    arrive_before = sorted(frame_set(arrive_event[2]))
    arrive_after = sorted(frame_set(arrive_event[3]))
    need(head not in arrive_before, "arrive before hosts head")
    need(head in arrive_after, "arrive after missing head")
    preterminal = [row for row in target_hits if row["event"] < arrive["event"]]
    need(preterminal == [], "preterminal target hosting")
    after_drop = any(
        row["event"] > drop or (row["event"] == drop and row["role"] == "after")
        for row in source_hits
    )
    hosting_gap = arrive["event"] - drop
    source_initial = witness["initial_frames"][source]
    source_final = witness["final_frames"][source]
    target_initial = witness["initial_frames"][target]
    target_final = witness["final_frames"][target]
    finals_with_head = sum(
        1 for index in range(104) if head in witness["final_frames"][f"Y{index}"]
    )
    receipt = {
        "schema_version": 1,
        "claim_id": "p104-present-head-flag9-audit",
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
        "hosting_gap_events": hosting_gap,
        "source_annotations_containing_basis_head": len(source_hits),
        "target_annotations_containing_basis_head": len(target_hits),
        "target_preterminal_annotations_containing_basis_head": len(preterminal),
        "source_head_annotations": source_hits,
        "target_head_annotations": target_hits,
        "target_annotated_vectors": sorted(target_pool),
        "basis_head_in_any_target_annotation": head in target_pool,
        "basis_head_in_source_after_drop": after_drop,
        "targets_whose_final_contains_basis_head_among_all": finals_with_head,
        "hit_flags_from_census": list(HIT_FLAGS),
        "flag_is_present_head_case": True,
        "obstruction": (
            "published_channel_hosts_basis_head_on_matched_target_only_at_"
            "terminal_transport_after_source_drop"
        ),
        "no_new_kappa": True,
        "selected_kappa": "0.001672660197076918",
    }
    need(receipt["target_final_contains_basis_head"] is True, "left present-head class")
    need(receipt["target_preterminal_annotations_containing_basis_head"] == 0, "preterminal")
    need(receipt["basis_head_in_source_after_drop"] is False, "source retained head")
    need(receipt["joint_source_target_events"] == 0, "joint endpoint event")
    return receipt


def main():
    observed = evaluate()
    expected = read_json(HERE / "CERTIFICATE.json")
    need(observed == expected, "certificate mismatch")
    print(MARKER)


if __name__ == "__main__":
    main()
