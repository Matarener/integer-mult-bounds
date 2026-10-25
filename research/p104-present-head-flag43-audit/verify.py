#!/usr/bin/env python3
"""Read-only present-head dirty-restoration audit for matched flag 43.

Flag 43 is one of the four published flags whose target final contains the
basis head. Frames are binary subspaces of the nine-dimensional label space,
so hosting is checked both as literal frame membership and as membership in
the GF(2) span of the frame. The target side is also scanned for the flag's
non-head basis vectors. Admission uses need() and remains active under
python -O. This module does not import independent.py or any predecessor
verifier.
"""

import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
MARKER = (
    "PASS_P104_PRESENT_HEAD_FLAG43 flag=43 head=15 preterminal_hosting=0 "
    "preterminal_span_hosting=0 drop_event=570 arrive_event=3525 "
    "source_span_drops=0 head_free_target_updates=15/15 "
    "tail_cohosting_updates=2 no_new_kappa"
)
INPUTS = (
    "research/p104-joint-unit-flags/CERTIFICATE.json",
    "research/p104-native-channel/inputs/LOWRANK-WITNESS.json",
    "research/p104-endpoint-geometric-budget/geometry.py",
)
SOURCE_LINE = "sources = [paths[f'X{s}'] for s in range(104)]"
TARGET_LINE = "targets = [paths[f'Y{t}'] for t in range(104)]"
FLAG_INDEX = 43
HIT_FLAGS = (0, 1, 9, 43)
LABEL_BITS = 9
# (drop, arrive, gap) as published by open #3451 (flag 1) and #3443 (flag 9).
PRIOR_TUPLES = {"3451_flag1": [591, 3473, 2882], "3443_flag9": [500, 3489, 2989]}


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


def echelon(frame):
    """Pivot-indexed GF(2) row echelon form; each row tracks its frame subset."""
    rows = {}
    for vector in frame:
        need(type(vector) is int and 0 < vector < (1 << LABEL_BITS), "label range")
        value = vector
        combo = 1 << frame.index(vector)
        while value:
            pivot = value.bit_length() - 1
            if pivot not in rows:
                rows[pivot] = (value, combo)
                break
            value ^= rows[pivot][0]
            combo ^= rows[pivot][1]
        need(value != 0, "dependent frame vector")
    return rows


def span_combination(vector, frame):
    """Return the frame subset whose XOR is vector, or None if outside the span."""
    rows = echelon(frame)
    value = vector
    combo = 0
    while value:
        pivot = value.bit_length() - 1
        if pivot not in rows:
            return None
        value ^= rows[pivot][0]
        combo ^= rows[pivot][1]
    return sorted(frame[i] for i in range(len(frame)) if combo >> i & 1)


def in_span(vector, frame):
    return span_combination(vector, frame) is not None


def rank(frame):
    return len(echelon(frame))


def span_elements(frame):
    rows = [row for row, _ in echelon(frame).values()]
    out = []
    for mask in range(1 << len(rows)):
        value = 0
        for i, row in enumerate(rows):
            if mask >> i & 1:
                value ^= row
        out.append(value)
    return sorted(out)


def span_contains(big, small):
    return all(in_span(vector, big) for vector in small)


def tail_in_span(tail, frame):
    return [vector for vector in tail if in_span(vector, frame)]


def pin_sources(root=ROOT, here=HERE):
    manifest = read_json(here / "SOURCES.json")
    rows = manifest["files"]
    inputs = [row for row in rows if row["usage"] == "input"]
    need(tuple(row["path"] for row in inputs) == INPUTS, "input inventory")
    pinned = {}
    for row in inputs:
        path = root / row["path"]
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
    need(FLAG_INDEX in hits, "flag 43 left the present-head class")
    helper = helpers[FLAG_INDEX]
    head = helper["basis"][0]
    tail = list(helper["basis"][1:])
    source = f"X{helper['source']}"
    target = f"Y{helper['target']}"
    program = witness["program"]
    source_events = []
    target_events = []
    joint = 0
    source_head = []
    target_head = []
    target_vectors = set()
    source_frames = 0
    source_span_frames = 0
    source_span_drops = []
    source_row_updates = []
    source_reads = []
    target_span_head = []
    target_span_tail = []
    target_updates = []
    target_updates_head_free = []
    target_updates_empty_chart = []
    target_updates_tail_cohosting = []
    tail_cohosting_detail = []
    target_transport_steps = []
    endpoint_non_frame_events = 0
    transports = []
    source_live = list(witness["initial_frames"][source])
    for index, event in enumerate(program):
        need(type(event) is list and 1 <= len(event) <= 8, "event shape")
        names = []
        for item in event:
            name = register_name(item)
            if name is not None:
                names.append(name)
        if source in names and target in names:
            joint += 1
        if (source in names or target in names) and event[0] not in ("add", "transport"):
            endpoint_non_frame_events += 1
        if source in names:
            source_events.append(index)
            for role, frame in annotated_frames(event, source):
                source_frames += 1
                if in_span(head, frame):
                    source_span_frames += 1
                else:
                    source_span_drops.append(index)
                if head in frame:
                    source_head.append(
                        {
                            "event": index,
                            "opcode": event[0],
                            "role": role,
                            "frame": sorted(frame),
                        }
                    )
            if event[0] == "transport" and event[1] == source:
                transports.append(event)
                need(sorted(event[2]) == sorted(source_live), "source frame continuity")
                source_live = list(event[3])
            if event[0] == "add" and event[1] == source:
                source_row_updates.append(index)
            if event[0] == "add" and event[2] == source:
                source_reads.append(index)
        if target in names:
            target_events.append(index)
            for role, frame in annotated_frames(event, target):
                target_vectors.update(frame)
                if in_span(head, frame):
                    target_span_head.append({"event": index, "role": role})
                hosted_tail = tail_in_span(tail, frame)
                if hosted_tail:
                    target_span_tail.append(
                        {"event": index, "role": role, "tail": hosted_tail}
                    )
                if head in frame:
                    target_head.append(
                        {
                            "event": index,
                            "opcode": event[0],
                            "role": role,
                            "frame": sorted(frame),
                        }
                    )
            if event[0] == "add" and event[1] == target:
                target_updates.append(index)
                chart = event[-1]
                if not in_span(head, chart):
                    target_updates_head_free.append(index)
                    if chart == []:
                        target_updates_empty_chart.append(index)
                    if tail_in_span(tail, chart):
                        target_updates_tail_cohosting.append(index)
                        tail_cohosting_detail.append(
                            {
                                "event": index,
                                "target_chart_rank": rank(chart),
                                "source_live_rank": rank(source_live),
                                "source_live_spans_head": in_span(head, source_live),
                                "tail_cohosted_by_both_endpoints": [
                                    vector
                                    for vector in tail_in_span(tail, chart)
                                    if in_span(vector, source_live)
                                ],
                            }
                        )
            if event[0] == "transport" and event[1] == target:
                transports.append(event)
                target_transport_steps.append(event[4])
    need(source_events and target_events, "endpoint silence")
    drop = source_events[0]
    drop_event = program[drop]
    need(drop_event[0] == "transport" and drop_event[1] == source, "first source op")
    need(drop_event[2] == [head], "drop before-frame")
    need(head not in drop_event[3], "drop after-frame still lists head")
    after_drop = False
    for row in source_head:
        if row["event"] > drop:
            after_drop = True
        if row["event"] == drop and row["role"] == "after":
            after_drop = True
    need(len(target_head) == 1, "unexpected target head hosting count")
    arrive = target_head[0]
    need(arrive["opcode"] == "transport", "arrive opcode")
    need(arrive["role"] == "after", "arrive role")
    need(arrive["event"] == target_events[-1], "arrive is not terminal target event")
    preterminal = [row for row in target_head if row["event"] < arrive["event"]]
    need(preterminal == [], "preterminal target hosting")
    arrive_event = program[arrive["event"]]
    need(arrive_event[0] == "transport" and arrive_event[1] == target, "arrive transport")
    need(head not in arrive_event[2], "arrive before-frame already lists head")
    need(head in arrive_event[3], "arrive after-frame missing head")
    hosting_gap = arrive["event"] - drop
    need(hosting_gap > 0, "arrive precedes drop")
    need(target_span_head, "target never span-hosts head")
    span_arrive = target_span_head[0]
    span_preterminal = [
        row for row in target_span_head if row["event"] < arrive["event"]
    ]
    need(target_span_tail, "target never spans a tail vector")
    tail_open = target_span_tail[0]
    nested = all(span_contains(event[3], event[2]) for event in transports)
    rank_steps = all(
        event[4] == rank(event[3]) - rank(event[2]) for event in transports
    )
    decomposition = span_combination(head, list(drop_event[3]))
    finals_with_head = sum(
        1 for index in range(104) if head in witness["final_frames"][f"Y{index}"]
    )
    source_initial = witness["initial_frames"][source]
    source_final = witness["final_frames"][source]
    target_initial = witness["initial_frames"][target]
    target_final = witness["final_frames"][target]
    cohost_open = span_arrive["event"]
    chronology = [drop, arrive["event"], hosting_gap]
    return {
        "schema_version": 1,
        "claim_id": "p104-present-head-flag43-audit",
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
        "source_rank_initial": rank(source_initial),
        "source_rank_final": rank(source_final),
        "target_rank_initial": rank(target_initial),
        "target_rank_final": rank(target_final),
        "source_first_event": source_events[0],
        "source_last_event": source_events[-1],
        "target_first_event": target_events[0],
        "target_last_event": target_events[-1],
        "source_event_count": len(source_events),
        "target_event_count": len(target_events),
        "joint_source_target_events": joint,
        "endpoint_non_frame_events": endpoint_non_frame_events,
        "basis_head_drop_event": drop,
        "basis_head_drop_before": sorted(drop_event[2]),
        "basis_head_drop_after": sorted(drop_event[3]),
        "basis_head_arrive_event": arrive["event"],
        "basis_head_arrive_before": sorted(arrive_event[2]),
        "basis_head_arrive_after": sorted(arrive_event[3]),
        "hosting_gap_events": hosting_gap,
        "source_annotations_containing_basis_head": len(source_head),
        "target_annotations_containing_basis_head": len(target_head),
        "target_preterminal_annotations_containing_basis_head": len(preterminal),
        "source_head_annotations": source_head,
        "target_head_annotations": target_head,
        "target_annotated_vectors": sorted(target_vectors),
        "basis_head_in_any_target_annotation": head in target_vectors,
        "basis_head_in_source_after_drop": after_drop,
        "drop_after_span_decomposition_of_head": decomposition,
        "drop_transport_span_nested": span_contains(drop_event[3], drop_event[2]),
        "source_annotation_count": source_frames,
        "source_annotations_span_hosting_basis_head": source_span_frames,
        "source_span_drop_events": source_span_drops,
        "source_row_update_events": source_row_updates,
        "source_read_event_count": len(source_reads),
        "target_span_first_hosting_event": span_arrive["event"],
        "target_span_first_hosting_role": span_arrive["role"],
        "target_preterminal_annotations_span_hosting_basis_head": len(span_preterminal),
        "target_arrive_before_span": span_elements(list(arrive_event[2])),
        "target_update_events": target_updates,
        "target_updates_in_head_free_span": len(target_updates_head_free),
        "target_updates_in_empty_chart": len(target_updates_empty_chart),
        "target_updates_in_nonempty_head_free_chart": (
            len(target_updates_head_free) - len(target_updates_empty_chart)
        ),
        "target_last_update_event": target_updates[-1],
        "target_transport_rank_steps": target_transport_steps,
        "target_terminal_rank_step": arrive_event[4],
        "basis_tail": tail,
        "target_tail_first_span_event": tail_open["event"],
        "target_tail_first_span_role": tail_open["role"],
        "target_tail_span_annotations": target_span_tail,
        "target_tail_in_arrive_before_span": tail_in_span(tail, list(arrive_event[2])),
        "target_tail_in_final_span": tail_in_span(tail, list(target_final)),
        "target_updates_cohosting_tail_without_head": target_updates_tail_cohosting,
        "target_tail_cohosting_update_detail": tail_cohosting_detail,
        "source_live_final_matches_witness": sorted(source_live) == sorted(source_final),
        "target_events_after_span_cohost_open": sum(
            1 for index in target_events if index > cohost_open
        ),
        "source_events_after_span_cohost_open": [
            index for index in source_events if index > cohost_open
        ],
        "source_events_after_span_cohost_open_are_reads": all(
            index in source_reads for index in source_events if index > cohost_open
        ),
        "endpoint_transport_count": len(transports),
        "endpoint_transports_span_nested_upward": nested,
        "endpoint_transport_rank_steps_match": rank_steps,
        "targets_whose_final_contains_basis_head_among_all": finals_with_head,
        "hit_flags_from_census": list(HIT_FLAGS),
        "flag_is_present_head_case": True,
        "chronology_drop_arrive_gap": chronology,
        "published_prior_present_head_tuples": PRIOR_TUPLES,
        "chronology_distinct_from_published_priors": all(
            chronology != prior for prior in PRIOR_TUPLES.values()
        ),
        "obstruction": (
            "published_channel_hosts_basis_head_on_matched_target_only_at_"
            "terminal_transport_literally_and_in_span_after_every_target_update_"
            "while_preterminal_target_charts_already_span_non_head_basis_vectors"
        ),
        "no_new_kappa": True,
        "selected_kappa": "0.001672660197076918",
    }


def evaluate(root=ROOT, here=HERE):
    pinned = pin_sources(root, here)
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
    need(receipt["target_final_contains_basis_head"] is True, "left present-head class")
    need(receipt["target_preterminal_annotations_containing_basis_head"] == 0, "preterminal")
    need(receipt["target_annotations_containing_basis_head"] == 1, "target hosting count")
    need(receipt["basis_head_drop_event"] == 570, "drop event drift")
    need(receipt["basis_head_arrive_event"] == 3525, "arrive event drift")
    need(receipt["hosting_gap_events"] == 2955, "gap drift")
    need(receipt["chronology_distinct_from_published_priors"] is True, "reprint of a prior")
    need(receipt["basis_head_in_source_after_drop"] is False, "source relisted head")
    need(receipt["joint_source_target_events"] == 0, "joint endpoint event")
    need(receipt["endpoint_non_frame_events"] == 0, "endpoint zero/copy/erase event")
    need(receipt["source_frame_restored"] is False, "source restored")
    need(receipt["target_frame_restored"] is False, "target restored")
    need(receipt["source_span_drop_events"] == [], "source lost head direction")
    need(
        receipt["source_annotations_span_hosting_basis_head"]
        == receipt["source_annotation_count"],
        "source span hosting gap",
    )
    need(receipt["source_row_update_events"] == [], "source row updated")
    need(receipt["target_span_first_hosting_event"] == 3525, "span arrive drift")
    need(receipt["target_span_first_hosting_role"] == "after", "span arrive role")
    need(
        receipt["target_preterminal_annotations_span_hosting_basis_head"] == 0,
        "preterminal span hosting",
    )
    need(
        receipt["target_updates_in_head_free_span"]
        == len(receipt["target_update_events"])
        == 15,
        "target update in head-hosting chart",
    )
    need(receipt["target_updates_in_empty_chart"] == 10, "empty-chart update count")
    need(
        receipt["target_updates_cohosting_tail_without_head"] == [3231, 3364],
        "tail co-hosting updates",
    )
    need(receipt["target_tail_in_arrive_before_span"] == [6, 18, 32], "preterminal tail")
    need(receipt["source_live_final_matches_witness"] is True, "source frame replay")
    need(
        [row["tail_cohosted_by_both_endpoints"]
         for row in receipt["target_tail_cohosting_update_detail"]]
        == [[32], [6, 18, 32]],
        "tail co-hosted by both endpoints",
    )
    need(
        all(row["source_live_spans_head"]
            for row in receipt["target_tail_cohosting_update_detail"]),
        "source lost head at a tail co-hosting update",
    )
    need(receipt["target_events_after_span_cohost_open"] == 0, "target event after cohost")
    need(
        receipt["source_events_after_span_cohost_open_are_reads"] is True,
        "source written after cohost",
    )
    need(receipt["endpoint_transports_span_nested_upward"] is True, "non-nested transport")
    need(receipt["endpoint_transport_rank_steps_match"] is True, "rank step mismatch")
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
