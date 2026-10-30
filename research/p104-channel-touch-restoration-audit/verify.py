#!/usr/bin/env python3
"""Read-only chronology and frame-restoration audit of the published P104 word.

This module does not import the #3242 or #3259 verifiers. Admission uses
need(); those checks stay active when Python is started with -O.
"""

import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
MARKER = (
    "PASS_P104_CHANNEL_TOUCH_RESTORATION events=4058 flags=208 "
    "restored=0 no_new_kappa"
)
INPUTS = (
    "research/p104-joint-unit-flags/CERTIFICATE.json",
    "research/p104-native-channel/inputs/LOWRANK-WITNESS.json",
    "research/p104-endpoint-geometric-budget/geometry.py",
    "research/p104-flag-channel-schedule/RESULT.json",
)
AUDITED = "research/p104-flag-channel-schedule/RESULT.json"
COORDINATE_BASIS = (1, 2, 4, 8, 16, 32, 64, 128, 256)
SOURCE_LINE = "sources = [paths[f'X{s}'] for s in range(104)]"
TARGET_LINE = "targets = [paths[f'Y{t}'] for t in range(104)]"


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
    tail = item[1:]
    if not tail.isdigit():
        return None
    index = int(tail)
    if index > 103:
        return None
    return item


def canonical_frame(frame):
    need(type(frame) is list, "frame")
    seen = []
    for entry in frame:
        need(type(entry) is int, "frame entry")
        need(entry not in seen, "duplicate frame vector")
        seen.append(entry)
    return tuple(sorted(seen))


def forward_touches(program):
    first = {}
    last = {}
    present = {}
    joint = 0
    for index, event in enumerate(program):
        need(type(event) is list and 1 <= len(event) <= 8, "event shape")
        names = []
        for item in event:
            name = register_name(item)
            if name is not None:
                names.append(name)
        kinds = {name[0] for name in names}
        if "X" in kinds and "Y" in kinds:
            joint += 1
        for name in names:
            if name not in first:
                first[name] = index
                present[name] = set()
            last[name] = index
            present[name].add(index)
    return first, last, present, joint


def add_coefficients(program, name):
    found = []
    for event in program:
        if event[0] != "add":
            continue
        slots = (register_name(event[1]), register_name(event[2]))
        if name not in slots:
            continue
        need(type(event[3]) in {str, int}, "add coefficient")
        text = str(event[3])
        if text not in found:
            found.append(text)
    found.sort()
    return found


def pin_sources():
    manifest = read_json(HERE / "SOURCES.json")
    rows = manifest["files"]
    inputs = [row for row in rows if row["usage"] == "input"]
    need(tuple(row["path"] for row in inputs) == INPUTS, "input inventory")
    need(any(row["path"] == AUDITED for row in inputs), "audited claim")
    pinned = {}
    for row in inputs:
        path = ROOT / row["path"]
        raw = path.read_bytes()
        need(len(raw) <= 2_000_000, "source size")
        digest = hashlib.sha256(raw).hexdigest()
        need(digest == row["sha256"], "source hash: " + row["path"])
        pinned[row["path"]] = raw
    return pinned


def build_receipt(witness, helpers):
    program = witness["program"]
    need(len(program) == 4058, "word length")
    need(len(helpers) == 208, "flag count")
    first, last, present, joint = forward_touches(program)
    sources = [f"X{i}" for i in range(104)]
    targets = [f"Y{i}" for i in range(104)]
    need(all(name in first for name in sources + targets), "missing register")
    source_first = min(first[name] for name in sources)
    target_last_first = max(first[name] for name in targets)
    earliest = sorted(name for name in sources if first[name] == source_first)
    latest = sorted(name for name in targets if first[name] == target_last_first)
    pairs = []
    head_hits = []
    restored_pairs = 0
    starts_at_head = 0
    meetings = 0
    for index, row in enumerate(helpers):
        need(type(row["source"]) is int and type(row["target"]) is int, "endpoint")
        source = f"X{row['source']}"
        target = f"Y{row['target']}"
        need(source in first and target in first, "matched register")
        gap = first[source] - first[target]
        pairs.append((gap, row["source"], row["target"], first[target], first[source]))
        if present[source] & present[target]:
            meetings += 1
        head = row["basis"][0]
        initial = witness["initial_frames"][source]
        if initial == [head]:
            starts_at_head += 1
        if head in witness["final_frames"][target]:
            head_hits.append(
                {
                    "flag_index": index,
                    "source": row["source"],
                    "target": row["target"],
                    "basis_head": head,
                }
            )
        source_back = canonical_frame(initial) == canonical_frame(
            witness["final_frames"][source]
        )
        target_back = canonical_frame(witness["initial_frames"][target]) == canonical_frame(
            witness["final_frames"][target]
        )
        if source_back or target_back:
            restored_pairs += 1
    source_ranks = {}
    final_basis = 0
    restored_sources = 0
    for index in range(104):
        initial = canonical_frame(witness["initial_frames"][f"X{index}"])
        final = canonical_frame(witness["final_frames"][f"X{index}"])
        source_ranks[str(len(initial))] = source_ranks.get(str(len(initial)), 0) + 1
        if final == COORDINATE_BASIS:
            final_basis += 1
        if initial == final:
            restored_sources += 1
    empty_targets = 0
    target_ranks = {}
    restored_targets = 0
    for index in range(104):
        initial = canonical_frame(witness["initial_frames"][f"Y{index}"])
        final = canonical_frame(witness["final_frames"][f"Y{index}"])
        if initial == ():
            empty_targets += 1
        target_ranks[str(len(final))] = target_ranks.get(str(len(final)), 0) + 1
        if initial == final:
            restored_targets += 1
    gap, source, target, target_first, source_at = min(pairs)
    flag = helpers[0]
    return {
        "schema_version": 1,
        "claim_id": "p104-channel-touch-restoration-audit",
        "pinned_main": "6f100d4bb5083f8c35d96fd95a539811c62f245c",
        "flags": 208,
        "unique_source_target_pairs": len({(row["source"], row["target"]) for row in helpers}),
        "program_events": 4058,
        "joint_source_target_events": joint,
        "matched_pairs_target_before_source": sum(1 for item in pairs if item[0] > 0),
        "matched_pairs_cooccurring": meetings,
        "matched_same_first_event": sum(1 for item in pairs if item[0] == 0),
        "latest_target_first_event": target_last_first,
        "latest_target_firsts": latest,
        "earliest_source_event": source_first,
        "earliest_sources": earliest,
        "population_gap": source_first - target_last_first,
        "minimum_matched_first_touch_gap": gap,
        "minimum_matched_pair": {
            "source": source,
            "target": target,
            "target_first": target_first,
            "source_first": source_at,
        },
        "source_initial_ranks": source_ranks,
        "source_final_equals_coordinate_basis": final_basis,
        "target_initial_empty": empty_targets,
        "target_final_ranks": target_ranks,
        "frame_restored_sources": restored_sources,
        "frame_restored_targets": restored_targets,
        "matched_pairs_with_either_endpoint_frame_restored": restored_pairs,
        "sources_starting_at_basis_head": starts_at_head,
        "targets_whose_final_contains_basis_head": len(head_hits),
        "basis_head_in_target_final": head_hits,
        "flag0": {
            "source": flag["source"],
            "target": flag["target"],
            "basis_head": flag["basis"][0],
            "source_events": [first["X0"], last["X0"]],
            "target_events": [first["Y34"], last["Y34"]],
            "source_coefficients": add_coefficients(program, "X0"),
            "target_coefficients": add_coefficients(program, "Y34"),
            "source_initial": witness["initial_frames"]["X0"],
            "source_frame_restored": canonical_frame(witness["initial_frames"]["X0"])
            == canonical_frame(witness["final_frames"]["X0"]),
            "target_frame_restored": canonical_frame(witness["initial_frames"]["Y34"])
            == canonical_frame(witness["final_frames"]["Y34"]),
            "target_final_contains_basis_head": flag["basis"][0]
            in witness["final_frames"]["Y34"],
        },
        "author_3242_fields_match": True,
        "no_new_kappa": True,
    }


def agree_with_author(receipt, author, witness):
    flag = receipt["flag0"]
    need(author["flags"] == 208, "discrepancy with #3242 flags")
    need(author["program_events"] == 4058, "discrepancy with #3242 events")
    need(author["joint_source_target_events"] == 0, "discrepancy with #3242 joint events")
    need(
        author["matched_pairs_with_target_first"] == 208,
        "discrepancy with #3242 matched order",
    )
    need(author["earliest_source_event"] == receipt["earliest_source_event"], "discrepancy with #3242 earliest source")
    need(
        author["latest_target_first_event"] == receipt["latest_target_first_event"],
        "discrepancy with #3242 latest target",
    )
    need(author["matched_same_first_event"] == 0, "discrepancy with #3242 same first")
    recorded = author["flag0"]
    need(recorded["source"] == 0 and recorded["target"] == 34, "discrepancy with #3242 flag 0")
    need(recorded["basis_head"] == flag["basis_head"], "discrepancy with #3242 basis head")
    need(recorded["source_events"] == flag["source_events"], "discrepancy with #3242 X0 span")
    need(recorded["target_events"] == flag["target_events"], "discrepancy with #3242 Y34 span")
    need(set(recorded["source_coefficients"]) == set(flag["source_coefficients"]), "discrepancy with #3242 X0 coefficients")
    need(set(recorded["target_coefficients"]) == set(flag["target_coefficients"]), "discrepancy with #3242 Y34 coefficients")
    need(recorded["source_initial"] == witness["initial_frames"]["X0"], "discrepancy with #3242 X0 initial")
    need(recorded["restored"] is False, "discrepancy with #3242 restored flag")
    need(recorded["target_final_contains_basis_head"] is True, "discrepancy with #3242 Y34 head")
    need(author["no_new_kappa"] is True, "discrepancy with #3242 kappa flag")


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
    author = json.loads(
        pinned[AUDITED],
        object_pairs_hook=pairs_unique,
    )
    receipt = build_receipt(witness, certificate["helpers"])
    agree_with_author(receipt, author, witness)
    need(receipt["joint_source_target_events"] == 0, "joint event survived")
    need(receipt["matched_pairs_cooccurring"] == 0, "cooccurrence encoding")
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
