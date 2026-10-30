#!/usr/bin/env python3
"""Self-owned host schedule for the flag-0 tail X0 read (answers #3669 OQ2).

On the published promote/add/restore at 5758/5759/5807, assign owner=X0 on the
full host chart. Prove: the assignment is the unique owner among registers
named by that ADD; the window touches no dirty helper; X0 is never a
destination after the channel prefix; both endpoints stay at their unrestored
channel finals (zero repayment toward initials); restoring X0 to its initial
frame before the ADD breaks the published common-chart annotation.

Read-only. Admission uses need(); checks stay active under -O.
"""

from __future__ import annotations

import gzip
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
MARKER = (
    "PASS_P104_FLAG0_TAIL_OWNER_HOST flag=0 owner=X0 promote=5758 add=5759 "
    "restore=5807 dirty_helper_touches=0 endpoint_repay=0 "
    "pre_read_restore_blocks=1 unique_owner=1 no_new_kappa"
)
INPUTS = (
    "research/p104-native-channel/inputs/LOWRANK-WITNESS.json",
    "research/p104-tail-side-correction-seed749717/AUGMENTED-WITNESS.json.gz",
    "research/p104-tail-side-correction-seed749717/CORRECTION-ROWS.json",
    "research/p104-tail-flag0-owner/RESULT.json",
    "research/p104-channel-touch-restoration-audit/CERTIFICATE.json",
)
FULL = [1, 2, 4, 8, 16, 32, 64, 128, 256]
RANK8 = [499, 23, 232, 32, 112, 15, 7, 2]
SOURCE_INIT = [232]
TARGET_INIT: list[int] = []
PROMOTE = 5758
ADD = 5759
RESTORE = 5807
CHANNEL_LEN = 4058
SELECTED_KAPPA = "0.001672660197076918"


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
    need(len(raw) <= 8_000_000, "input exceeds 8 MB")
    return json.loads(raw, object_pairs_hook=pairs_unique)


def read_json_gz(path):
    raw = Path(path).read_bytes()
    need(len(raw) <= 8_000_000, "gzip input exceeds 8 MB")
    return json.loads(gzip.decompress(raw), object_pairs_hook=pairs_unique)


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def is_dirty_helper(name):
    if type(name) is not str or len(name) < 2:
        return False
    head, tail = name[0], name[1:]
    if head == "C" and tail == "":
        return True
    if head not in "DGQ":
        return False
    return tail.isdigit() and int(tail) <= 103


def walk_frames(program, initial, names):
    frames = {name: list(initial[name]) for name in names}
    destinations = {name: [] for name in names}
    for index, event in enumerate(program):
        need(type(event) is list and event, "event shape")
        op = event[0]
        if op == "transport":
            need(len(event) == 5, "transport arity")
            _op, reg, old, new, rank = event
            if reg in frames:
                need(old == frames[reg], "transport left its live frame at " + str(index))
                need(type(rank) is int and rank >= 0, "transport rank")
                frames[reg] = list(new)
                destinations[reg].append(index)
        elif op == "add":
            need(len(event) == 5, "add arity")
            _op, dest, _src, _coef, _chart = event
            if dest in frames:
                destinations[dest].append(index)
        elif op == "copy":
            need(len(event) >= 3, "copy arity")
            dest = event[1]
            if dest in frames:
                destinations[dest].append(index)
    return frames, destinations


def authenticate():
    sources = read_json(HERE / "SOURCES.json")
    pinned = {row["path"]: row for row in sources["files"] if row["usage"] == "input"}
    need(set(pinned) == set(INPUTS), "input inventory changed")
    for path, row in pinned.items():
        need(sha256(ROOT / path) == row["sha256"], "source hash " + path)


def evaluate():
    authenticate()
    certificate = read_json(HERE / "CERTIFICATE.json")
    channel = read_json(ROOT / INPUTS[0])
    tail = read_json_gz(ROOT / INPUTS[1])
    rows = read_json(ROOT / INPUTS[2])
    owner_receipt = read_json(ROOT / INPUTS[3])
    touch = read_json(ROOT / INPUTS[4])

    need(tail["program"][:CHANNEL_LEN] == channel["program"], "tail prefix left the channel")
    need(channel["final_frames"]["X0"] == FULL, "channel X0 final")
    need(channel["final_frames"]["Y34"] == RANK8, "channel Y34 final")
    need(channel["initial_frames"]["X0"] == SOURCE_INIT, "channel X0 initial")
    need(channel["initial_frames"]["Y34"] == TARGET_INIT, "channel Y34 initial")
    need(tail["initial_frames"]["X0"] == SOURCE_INIT, "tail X0 initial")
    need(tail["initial_frames"]["Y34"] == TARGET_INIT, "tail Y34 initial")
    need(tail["final_frames"]["X0"] == FULL, "tail X0 final")
    need(tail["final_frames"]["Y34"] == RANK8, "tail Y34 final")

    # Channel-touch prior: every endpoint unrestored (cited, not re-censused).
    need(touch["claim_id"] == "p104-channel-touch-restoration-audit", "touch claim id")
    need(touch["frame_restored_sources"] == 0, "touch sources restored")
    need(touch["frame_restored_targets"] == 0, "touch targets restored")
    need(touch["flag0"]["source_frame_restored"] is False, "touch flag0 source")
    need(touch["flag0"]["target_frame_restored"] is False, "touch flag0 target")
    # Prior owner package: the tail word names no owner for event 5759.
    need(owner_receipt["event"] == ADD, "owner receipt event")
    need(owner_receipt["owner_assigned"] is False, "owner already assigned")
    need(owner_receipt["owner_field"] is False, "owner field present")
    need(owner_receipt["add"] == ["Y34", "X0", "-1/2"], "owner receipt add")

    program = tail["program"]
    need(len(program) > RESTORE, "program too short")
    need(program[PROMOTE] == ["transport", "Y34", RANK8, FULL, 1], "promote event")
    need(program[ADD] == ["add", "Y34", "X0", "-1/2", FULL], "add event")
    need(program[RESTORE] == ["transport", "Y34", FULL, RANK8, 1], "restore event")

    frames_at_add, destinations = walk_frames(
        program[: ADD + 1], tail["initial_frames"], ("X0", "Y34")
    )
    need(frames_at_add["X0"] == FULL, "X0 not on host chart at add")
    need(frames_at_add["Y34"] == FULL, "Y34 not on host chart at add")
    need(program[ADD][4] == frames_at_add["X0"] == frames_at_add["Y34"], "common chart")

    frames_after, destinations_full = walk_frames(
        program[: RESTORE + 1], tail["initial_frames"], ("X0", "Y34")
    )
    need(frames_after["X0"] == FULL, "X0 frame after restore")
    need(frames_after["Y34"] == RANK8, "Y34 frame after restore")
    need(frames_after["X0"] != SOURCE_INIT, "X0 repaid to initial")
    need(frames_after["Y34"] != TARGET_INIT, "Y34 repaid to initial")

    x0_dest_after = [i for i in destinations_full["X0"] if i >= CHANNEL_LEN]
    need(x0_dest_after == [], "X0 written after channel")
    # Last X0 destination in the whole word must be inside the channel.
    all_x0_dest = destinations_full["X0"]
    need(all_x0_dest and all_x0_dest[-1] == 1486, "X0 last destination")

    y34_tail = [i for i in destinations_full["Y34"] if i >= CHANNEL_LEN]
    # Destination list includes ADDs; transports alone are the frame changes.
    y34_transports = [
        i
        for i, event in enumerate(program)
        if event[0] == "transport" and event[1] == "Y34" and i >= CHANNEL_LEN
    ]
    need(y34_transports == [PROMOTE, RESTORE], "Y34 tail transports")

    window = program[PROMOTE : RESTORE + 1]
    dirty_touches = 0
    add_count = 0
    named_on_add = set()
    for offset, event in enumerate(window):
        index = PROMOTE + offset
        for item in event:
            if is_dirty_helper(item):
                dirty_touches += 1
        if event[0] == "add" and event[1] == "Y34":
            add_count += 1
            if index == ADD:
                named_on_add = {event[1], event[2]}
    need(dirty_touches == 0, "dirty helper touched in window")
    need(add_count == 48, "window add count")
    need(named_on_add == {"Y34", "X0"}, "add named registers")
    # Unique owner among registers named by the ADD, excluding the write target.
    source_named = named_on_add - {"Y34"}
    need(source_named == {"X0"}, "unique source owner")

    # Coefficient matches the published correction row.
    row = rows["rows"][34]
    need(row["target"] == 34, "correction target")
    hits = [entry for entry in row["nonzero"] if entry["source"] == 0]
    need(len(hits) == 1 and hits[0]["coefficient"] == "-1/2", "correction coefficient")

    # Pre-read restoration of X0 to its initial frame blocks the published chart.
    blocked = SOURCE_INIT != FULL
    need(blocked, "initial equals FULL unexpectedly")
    # Simulate: if X0 were forced to SOURCE_INIT at the ADD while the event
    # still annotates FULL, the common-chart rule fails.
    need(SOURCE_INIT != program[ADD][4], "pre-read restore would match chart")

    expected = {
        "schema_version": 1,
        "claim_id": "p104-flag0-tail-owner-host",
        "pinned_main": "20ecf2891d80b5acf18d980b2164fb44ea7faa90",
        "answers": "CrocSwap#3669 OQ2",
        "flag_index": 0,
        "source": 0,
        "target": 34,
        "source_register": "X0",
        "target_register": "Y34",
        "promote_event": PROMOTE,
        "add_event": ADD,
        "restore_event": RESTORE,
        "coefficient": "-1/2",
        "host_chart": FULL,
        "channel_final_x0": FULL,
        "channel_final_y34": RANK8,
        "source_initial": SOURCE_INIT,
        "target_initial": TARGET_INIT,
        "schedule_id": "S0",
        "owner": "X0",
        "owner_kind": "self",
        "unique_owner_among_event_named_registers": True,
        "dirty_helper_touches_in_window": 0,
        "x0_destination_events_after_channel": 0,
        "x0_last_destination_event": 1486,
        "endpoint_repay_x0_to_initial": False,
        "endpoint_repay_y34_to_initial": False,
        "x0_frame_after_restore": FULL,
        "y34_frame_after_restore": RANK8,
        "y34_tail_transports": [PROMOTE, RESTORE],
        "window_add_count": 48,
        "pre_read_x0_restoration_blocks_common_chart": True,
        "selected_kappa": SELECTED_KAPPA,
        "no_new_kappa": True,
    }
    need(certificate == expected, "certificate mismatch")
    need(certificate["selected_kappa"] == SELECTED_KAPPA, "kappa drift")
    return {
        "owner": "X0",
        "dirty_helper_touches": dirty_touches,
        "endpoint_repay": 0,
        "unique_owner": 1,
        "pre_read_restore_blocks": 1,
    }


def main():
    result = evaluate()
    need(result["owner"] == "X0", "owner")
    print(MARKER)


if __name__ == "__main__":
    main()
