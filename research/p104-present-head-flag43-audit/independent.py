#!/usr/bin/env python3
"""Second flag-43 present-head scanner. It does not import verify.py.

Events are first indexed per endpoint register. Literal frames are frozensets;
spans are explicit XOR closures (at most 512 labels), so membership, rank and
nesting are set operations rather than row reduction. The head decomposition
is found by exhaustive subset search, and the source's live frame at a target
event is read back from the last earlier source transport. Admission uses
need() under -O.
"""

import bisect
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
MARKER = (
    "PASS_P104_PRESENT_HEAD_FLAG43_INDEPENDENT flag=43 head=15 "
    "preterminal_hosting=0 preterminal_span_hosting=0 drop_event=570 "
    "arrive_event=3525 source_span_drops=0 head_free_target_updates=15/15 "
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
PRIORS = (("3451_flag1", (591, 3473, 2882)), ("3443_flag9", (500, 3489, 2989)))


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
    need(FLAG_INDEX in hits, "flag 43 left the present-head class")
    helper = helpers[FLAG_INDEX]
    head = helper["basis"][0]
    tail = list(helper["basis"][1:])
    source = f"X{helper['source']}"
    target = f"Y{helper['target']}"
    table, joint = index_registers(program, (source, target))
    source_indices = table[source]
    target_indices = table[target]
    need(source_indices and target_indices, "endpoint silence")
    non_frame = len(
        [i for i in set(source_indices) | set(target_indices)
         if program[i][0] not in ("add", "transport")]
    )

    source_hits = []
    source_frames = 0
    source_span_frames = 0
    source_span_drops = []
    source_writes = []
    source_reads = set()
    source_transport_at = []
    source_frame_after = []
    transports = []
    for index in source_indices:
        event = program[index]
        if event[0] == "transport" and event[1] == source:
            transports.append(event)
            source_transport_at.append(index)
            source_frame_after.append(list(event[3]))
        if event[0] == "add" and event[1] == source:
            source_writes.append(index)
        if event[0] == "add" and event[2] == source:
            source_reads.add(index)
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
    befores = [program[i][2] for i in source_transport_at]
    previous = [witness["initial_frames"][source]] + source_frame_after[:-1]
    need(
        all(frame_set(a) == frame_set(b) for a, b in zip(befores, previous)),
        "source frame continuity",
    )

    def source_live_at(index):
        position = bisect.bisect_left(source_transport_at, index)
        if position == 0:
            return witness["initial_frames"][source]
        return source_frame_after[position - 1]

    target_hits = []
    target_span_hits = []
    target_tail_hits = []
    target_pool = set()
    updates = []
    head_free_updates = 0
    empty_updates = 0
    tail_updates = []
    tail_detail = []
    steps = []
    for index in target_indices:
        event = program[index]
        if event[0] == "transport" and event[1] == target:
            transports.append(event)
            steps.append(event[4])
        if event[0] == "add" and event[1] == target:
            updates.append(index)
            chart = closure(event[-1])
            if head not in chart:
                head_free_updates += 1
                if not frame_set(event[-1]):
                    empty_updates += 1
                hosted = [vector for vector in tail if vector in chart]
                if hosted:
                    tail_updates.append(index)
                    live = closure(source_live_at(index))
                    tail_detail.append(
                        {
                            "event": index,
                            "target_chart_rank": dimension(event[-1]),
                            "source_live_rank": len(live).bit_length() - 1,
                            "source_live_spans_head": head in live,
                            "tail_cohosted_by_both_endpoints": [
                                vector for vector in hosted if vector in live
                            ],
                        }
                    )
        for role, frame in frames_of(event, target):
            literal = frame_set(frame)
            span = closure(frame)
            target_pool |= literal
            if head in span:
                target_span_hits.append((index, role))
            hosted = [vector for vector in tail if vector in span]
            if hosted:
                target_tail_hits.append({"event": index, "role": role, "tail": hosted})
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
    need(target_tail_hits, "no tail vector on target")
    after_drop = any(
        row["event"] > drop or (row["event"] == drop and row["role"] == "after")
        for row in source_hits
    )
    nested = all(closure(event[2]) <= closure(event[3]) for event in transports)
    rank_steps = all(
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
    before_span = closure(arrive_event[2])
    final_span = closure(target_final)
    gap = arrive["event"] - drop
    chronology = (drop, arrive["event"], gap)
    late_source = [index for index in source_indices if index > span_open]
    receipt = {
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
        "endpoint_non_frame_events": non_frame,
        "basis_head_drop_event": drop,
        "basis_head_drop_before": drop_before,
        "basis_head_drop_after": drop_after,
        "basis_head_arrive_event": arrive["event"],
        "basis_head_arrive_before": arrive_before,
        "basis_head_arrive_after": arrive_after,
        "hosting_gap_events": gap,
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
        "source_row_update_events": source_writes,
        "source_read_event_count": len(source_reads),
        "target_span_first_hosting_event": span_open,
        "target_span_first_hosting_role": span_role,
        "target_preterminal_annotations_span_hosting_basis_head": len(span_preterminal),
        "target_arrive_before_span": sorted(before_span),
        "target_update_events": updates,
        "target_updates_in_head_free_span": head_free_updates,
        "target_updates_in_empty_chart": empty_updates,
        "target_updates_in_nonempty_head_free_chart": head_free_updates - empty_updates,
        "target_last_update_event": updates[-1],
        "target_transport_rank_steps": steps,
        "target_terminal_rank_step": arrive_event[4],
        "basis_tail": tail,
        "target_tail_first_span_event": target_tail_hits[0]["event"],
        "target_tail_first_span_role": target_tail_hits[0]["role"],
        "target_tail_span_annotations": target_tail_hits,
        "target_tail_in_arrive_before_span": [v for v in tail if v in before_span],
        "target_tail_in_final_span": [v for v in tail if v in final_span],
        "target_updates_cohosting_tail_without_head": tail_updates,
        "target_tail_cohosting_update_detail": tail_detail,
        "source_live_final_matches_witness": (
            frame_set(source_live_at(len(program))) == frame_set(source_final)
        ),
        "target_events_after_span_cohost_open": len(
            [index for index in target_indices if index > span_open]
        ),
        "source_events_after_span_cohost_open": late_source,
        "source_events_after_span_cohost_open_are_reads": set(late_source) <= source_reads,
        "endpoint_transport_count": len(transports),
        "endpoint_transports_span_nested_upward": nested,
        "endpoint_transport_rank_steps_match": rank_steps,
        "targets_whose_final_contains_basis_head_among_all": finals_with_head,
        "hit_flags_from_census": list(HIT_FLAGS),
        "flag_is_present_head_case": True,
        "chronology_drop_arrive_gap": list(chronology),
        "published_prior_present_head_tuples": {
            name: list(values) for name, values in PRIORS
        },
        "chronology_distinct_from_published_priors": chronology not in {
            values for _, values in PRIORS
        },
        "obstruction": (
            "published_channel_hosts_basis_head_on_matched_target_only_at_"
            "terminal_transport_literally_and_in_span_after_every_target_update_"
            "while_preterminal_target_charts_already_span_non_head_basis_vectors"
        ),
        "no_new_kappa": True,
        "selected_kappa": "0.001672660197076918",
    }
    need(receipt["target_final_contains_basis_head"] is True, "left present-head class")
    need(receipt["target_preterminal_annotations_containing_basis_head"] == 0, "preterminal")
    need(receipt["target_preterminal_annotations_span_hosting_basis_head"] == 0, "span preterminal")
    need(receipt["chronology_distinct_from_published_priors"] is True, "reprint of a prior")
    need(receipt["source_span_drop_events"] == [], "source lost head direction")
    need(receipt["source_row_update_events"] == [], "source row updated")
    need(receipt["target_updates_in_head_free_span"] == len(updates), "head-hosting update")
    need(
        all(row["source_live_spans_head"] and row["tail_cohosted_by_both_endpoints"]
            for row in tail_detail),
        "tail co-hosting detail",
    )
    need(receipt["target_events_after_span_cohost_open"] == 0, "target event after cohost")
    need(receipt["source_events_after_span_cohost_open_are_reads"] is True, "late source write")
    need(receipt["basis_head_in_source_after_drop"] is False, "source relisted head")
    need(receipt["joint_source_target_events"] == 0, "joint endpoint event")
    need(receipt["endpoint_non_frame_events"] == 0, "endpoint zero/copy/erase event")
    need(nested and rank_steps, "transport semantics")
    return receipt


def main():
    observed = evaluate()
    expected = read_json(HERE / "CERTIFICATE.json")
    need(observed == expected, "certificate mismatch")
    print(MARKER)


if __name__ == "__main__":
    main()
