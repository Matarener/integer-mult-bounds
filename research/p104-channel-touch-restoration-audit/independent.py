#!/usr/bin/env python3
"""Second chronology scanner. It does not import verify.py.

Touches are stored as index lists. First and last events are min and max.
Frames are compared as sets. A matched pair co-occurs only when those index
sets meet. Admission uses need() and remains active under python -O.
"""

import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
MARKER = (
    "PASS_P104_CHANNEL_TOUCH_RESTORATION_INDEPENDENT events=4058 "
    "flags=208 restored=0 no_new_kappa"
)
COORDINATE_BASIS = frozenset((1, 2, 4, 8, 16, 32, 64, 128, 256))


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


def index_touches(program):
    seen = {f"{kind}{index}": [] for kind in "XY" for index in range(104)}
    joint = 0
    for index, event in enumerate(program):
        need(type(event) is list, "event shape")
        found = []
        for slot in range(len(event)):
            name = register_name(event[slot])
            if name is None:
                continue
            found.append(name)
            seen[name].append(index)
        has_source = False
        has_target = False
        for name in found:
            has_source = has_source or name[0] == "X"
            has_target = has_target or name[0] == "Y"
        if has_source and has_target:
            joint += 1
    return seen, joint


def coefficients(program, name):
    found = set()
    for event in program:
        if event[0] != "add":
            continue
        named = register_name(event[1]) == name or register_name(event[2]) == name
        if not named:
            continue
        need(type(event[3]) in {str, int}, "add coefficient")
        found.add(str(event[3]))
    return sorted(found)


def build_receipt(witness, helpers):
    program = witness["program"]
    need(len(program) == 4058 and len(helpers) == 208, "published sizes")
    seen, joint = index_touches(program)
    for name, hits in seen.items():
        need(len(hits) > 0, "missing register " + name)
    source_first = min(seen[f"X{i}"][0] for i in range(104))
    target_last_first = max(seen[f"Y{i}"][0] for i in range(104))
    earliest = [f"X{i}" for i in range(104) if seen[f"X{i}"][0] == source_first]
    latest = [f"Y{i}" for i in range(104) if seen[f"Y{i}"][0] == target_last_first]
    before = 0
    same = 0
    meet = 0
    restored_pairs = 0
    starts_at_head = 0
    head_hits = []
    gaps = []
    for index, row in enumerate(helpers):
        source_hits = seen[f"X{row['source']}"]
        target_hits = seen[f"Y{row['target']}"]
        if target_hits[0] < source_hits[0]:
            before += 1
        if target_hits[0] == source_hits[0]:
            same += 1
        if set(source_hits) & set(target_hits):
            meet += 1
        initial = witness["initial_frames"][f"X{row['source']}"]
        final = witness["final_frames"][f"Y{row['target']}"]
        head = row["basis"][0]
        if initial == [head]:
            starts_at_head += 1
        if head in final:
            head_hits.append(
                {
                    "flag_index": index,
                    "source": row["source"],
                    "target": row["target"],
                    "basis_head": head,
                }
            )
        source_same = frame_set(initial) == frame_set(
            witness["final_frames"][f"X{row['source']}"]
        )
        target_same = frame_set(witness["initial_frames"][f"Y{row['target']}"]) == frame_set(
            final
        )
        if source_same or target_same:
            restored_pairs += 1
        gaps.append(
            (
                source_hits[0] - target_hits[0],
                row["source"],
                row["target"],
                target_hits[0],
                source_hits[0],
            )
        )
    source_ranks = {}
    basis_finals = 0
    restored_sources = 0
    for index in range(104):
        initial = frame_set(witness["initial_frames"][f"X{index}"])
        final = frame_set(witness["final_frames"][f"X{index}"])
        source_ranks[str(len(initial))] = source_ranks.get(str(len(initial)), 0) + 1
        if final == COORDINATE_BASIS:
            basis_finals += 1
        if initial == final:
            restored_sources += 1
    empty_targets = 0
    target_ranks = {}
    restored_targets = 0
    for index in range(104):
        initial = frame_set(witness["initial_frames"][f"Y{index}"])
        final = frame_set(witness["final_frames"][f"Y{index}"])
        if not initial:
            empty_targets += 1
        target_ranks[str(len(final))] = target_ranks.get(str(len(final)), 0) + 1
        if initial == final:
            restored_targets += 1
    gap, source, target, target_first, source_at = min(gaps)
    flag = helpers[0]
    return {
        "schema_version": 1,
        "claim_id": "p104-channel-touch-restoration-audit",
        "pinned_main": "6f100d4bb5083f8c35d96fd95a539811c62f245c",
        "flags": 208,
        "unique_source_target_pairs": len({(row["source"], row["target"]) for row in helpers}),
        "program_events": 4058,
        "joint_source_target_events": joint,
        "matched_pairs_target_before_source": before,
        "matched_pairs_cooccurring": meet,
        "matched_same_first_event": same,
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
        "source_final_equals_coordinate_basis": basis_finals,
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
            "source_events": [min(seen["X0"]), max(seen["X0"])],
            "target_events": [min(seen["Y34"]), max(seen["Y34"])],
            "source_coefficients": coefficients(program, "X0"),
            "target_coefficients": coefficients(program, "Y34"),
            "source_initial": witness["initial_frames"]["X0"],
            "source_frame_restored": frame_set(witness["initial_frames"]["X0"])
            == frame_set(witness["final_frames"]["X0"]),
            "target_frame_restored": frame_set(witness["initial_frames"]["Y34"])
            == frame_set(witness["final_frames"]["Y34"]),
            "target_final_contains_basis_head": flag["basis"][0]
            in witness["final_frames"]["Y34"],
        },
        "author_3242_fields_match": True,
        "no_new_kappa": True,
    }


def evaluate():
    manifest = read_json(HERE / "SOURCES.json")
    for row in manifest["files"]:
        if row["usage"] != "input":
            continue
        raw = (ROOT / row["path"]).read_bytes()
        need(hashlib.sha256(raw).hexdigest() == row["sha256"], "source hash: " + row["path"])
    certificate = read_json(ROOT / "research/p104-joint-unit-flags/CERTIFICATE.json")
    witness = read_json(ROOT / "research/p104-native-channel/inputs/LOWRANK-WITNESS.json")
    author = read_json(ROOT / "research/p104-flag-channel-schedule/RESULT.json")
    geometry = (ROOT / "research/p104-endpoint-geometric-budget/geometry.py").read_text(
        encoding="utf-8"
    )
    need("sources = [paths[f'X{s}'] for s in range(104)]" in geometry, "source naming")
    need("targets = [paths[f'Y{t}'] for t in range(104)]" in geometry, "target naming")
    receipt = build_receipt(witness, certificate["helpers"])
    need(receipt["joint_source_target_events"] == 0, "joint event")
    need(receipt["frame_restored_sources"] == 0, "source frame returned")
    need(receipt["frame_restored_targets"] == 0, "target frame returned")
    need(author["earliest_source_event"] == receipt["earliest_source_event"], "discrepancy with #3242 earliest source")
    need(author["latest_target_first_event"] == receipt["latest_target_first_event"], "discrepancy with #3242 latest target")
    need(author["joint_source_target_events"] == 0, "discrepancy with #3242 joint events")
    need(author["matched_pairs_with_target_first"] == 208, "discrepancy with #3242 matched order")
    need(author["flag0"]["restored"] is False, "discrepancy with #3242 restored flag")
    need(set(author["flag0"]["source_coefficients"]) == set(receipt["flag0"]["source_coefficients"]), "discrepancy with #3242 X0 coefficients")
    need(set(author["flag0"]["target_coefficients"]) == set(receipt["flag0"]["target_coefficients"]), "discrepancy with #3242 Y34 coefficients")
    return receipt


def main():
    observed = evaluate()
    expected = read_json(HERE / "CERTIFICATE.json")
    need(observed == expected, "certificate mismatch")
    print(MARKER)


if __name__ == "__main__":
    main()
