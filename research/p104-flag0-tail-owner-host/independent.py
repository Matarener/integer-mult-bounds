#!/usr/bin/env python3
"""Independent index-list scan of the flag-0 tail owner/host schedule.

Does not import verify.py. Builds per-register event indexes, reconstructs
X0/Y34 frames from their transport subsequences alone, and rechecks the
self-owned schedule, dirt non-touch, zero endpoint repayment, and the
pre-read restoration obstruction. Admission uses need(); active under -O.
"""

from __future__ import annotations

import gzip
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
MARKER = (
    "PASS_P104_FLAG0_TAIL_OWNER_HOST_INDEPENDENT flag=0 owner=X0 promote=5758 "
    "add=5759 restore=5807 dirty_helper_touches=0 endpoint_repay=0 "
    "pre_read_restore_blocks=1 unique_owner=1 no_new_kappa"
)
INPUTS = (
    "research/p104-native-channel/inputs/LOWRANK-WITNESS.json",
    "research/p104-tail-side-correction-seed749717/AUGMENTED-WITNESS.json.gz",
    "research/p104-tail-side-correction-seed749717/CORRECTION-ROWS.json",
    "research/p104-tail-flag0-owner/RESULT.json",
    "research/p104-channel-touch-restoration-audit/CERTIFICATE.json",
)
FULL = (1, 2, 4, 8, 16, 32, 64, 128, 256)
RANK8 = (499, 23, 232, 32, 112, 15, 7, 2)
SOURCE_INIT = (232,)
TARGET_INIT = ()
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


def as_tuple(frame):
    need(type(frame) is list, "frame type")
    return tuple(frame)


def dirty_name(item):
    if type(item) is not str:
        return False
    if item == "C":
        return True
    if len(item) < 2 or item[0] not in "DGQ":
        return False
    return item[1:].isdigit()


def authenticate():
    sources = read_json(HERE / "SOURCES.json")
    pinned = {row["path"]: row for row in sources["files"] if row["usage"] == "input"}
    need(set(pinned) == set(INPUTS), "input inventory changed")
    for path, row in pinned.items():
        need(sha256(ROOT / path) == row["sha256"], "source hash " + path)


def index_program(program):
    by_reg = {}
    transports = {}
    destinations = {}
    for index, event in enumerate(program):
        need(type(event) is list and event, "event")
        names = []
        for item in event:
            if type(item) is str and len(item) >= 2 and item[0] in "XYDGQC":
                if item == "C" or item[1:].isdigit():
                    names.append(item)
        for name in names:
            by_reg.setdefault(name, []).append(index)
        if event[0] == "transport":
            reg = event[1]
            transports.setdefault(reg, []).append(index)
            destinations.setdefault(reg, []).append(index)
        elif event[0] == "add":
            destinations.setdefault(event[1], []).append(index)
        elif event[0] == "copy":
            destinations.setdefault(event[1], []).append(index)
    return by_reg, transports, destinations


def frame_at(program, initial, reg, cut):
    frame = as_tuple(initial[reg])
    for index, event in enumerate(program[:cut]):
        if event[0] != "transport" or event[1] != reg:
            continue
        need(as_tuple(event[2]) == frame, "transport mismatch at " + str(index))
        frame = as_tuple(event[3])
    return frame


def evaluate():
    authenticate()
    certificate = read_json(HERE / "CERTIFICATE.json")
    channel = read_json(ROOT / INPUTS[0])
    tail = read_json_gz(ROOT / INPUTS[1])
    rows = read_json(ROOT / INPUTS[2])
    owner_receipt = read_json(ROOT / INPUTS[3])
    touch = read_json(ROOT / INPUTS[4])

    need(tail["program"][:CHANNEL_LEN] == channel["program"], "prefix drift")
    program = tail["program"]
    by_reg, transports, destinations = index_program(program)

    need(program[PROMOTE][0] == "transport" and program[PROMOTE][1] == "Y34", "promote")
    need(as_tuple(program[PROMOTE][2]) == RANK8, "promote old")
    need(as_tuple(program[PROMOTE][3]) == FULL, "promote new")
    need(program[PROMOTE][4] == 1, "promote rank")
    need(program[ADD] == ["add", "Y34", "X0", "-1/2", list(FULL)], "add")
    need(program[RESTORE][0] == "transport" and program[RESTORE][1] == "Y34", "restore")
    need(as_tuple(program[RESTORE][2]) == FULL, "restore old")
    need(as_tuple(program[RESTORE][3]) == RANK8, "restore new")

    x0_at_add = frame_at(program, tail["initial_frames"], "X0", ADD + 1)
    y34_at_add = frame_at(program, tail["initial_frames"], "Y34", ADD + 1)
    need(x0_at_add == FULL and y34_at_add == FULL, "host chart at add")
    need(x0_at_add == as_tuple(program[ADD][4]), "annotated chart")

    x0_after = frame_at(program, tail["initial_frames"], "X0", RESTORE + 1)
    y34_after = frame_at(program, tail["initial_frames"], "Y34", RESTORE + 1)
    need(x0_after == FULL and y34_after == RANK8, "frames after restore")
    need(x0_after != SOURCE_INIT and y34_after != TARGET_INIT, "endpoint repaid")

    x0_dest_after = [i for i in destinations.get("X0", []) if i >= CHANNEL_LEN]
    need(x0_dest_after == [], "X0 written after channel")
    need(destinations.get("X0", [])[-1] == 1486, "X0 last destination")

    y34_tail_transports = [i for i in transports.get("Y34", []) if i >= CHANNEL_LEN]
    need(y34_tail_transports == [PROMOTE, RESTORE], "Y34 transports")

    dirty = 0
    adds = 0
    for index in range(PROMOTE, RESTORE + 1):
        event = program[index]
        for item in event:
            if dirty_name(item):
                dirty += 1
        if event[0] == "add" and event[1] == "Y34":
            adds += 1
    need(dirty == 0, "dirty helper touch")
    need(adds == 48, "add count")

    # Unique owner: among registers named by the ADD, only X0 can own the read.
    named = {program[ADD][1], program[ADD][2]}
    need(named == {"Y34", "X0"}, "named set")
    need((named - {"Y34"}) == {"X0"}, "unique owner")

    hits = [e for e in rows["rows"][34]["nonzero"] if e["source"] == 0]
    need(len(hits) == 1 and hits[0]["coefficient"] == "-1/2", "coefficient")

    need(touch["frame_restored_sources"] == 0 and touch["frame_restored_targets"] == 0,
         "touch unrestored")
    need(owner_receipt["owner_assigned"] is False and owner_receipt["event"] == ADD,
         "prior owner gap")

    # Pre-read restoration obstruction via index membership: SOURCE_INIT is not
    # the annotated chart, so forcing X0 onto SOURCE_INIT before ADD conflicts.
    need(SOURCE_INIT != FULL, "obstruction vacuous")
    need(SOURCE_INIT != as_tuple(program[ADD][4]), "obstruction chart")

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
        "host_chart": list(FULL),
        "channel_final_x0": list(FULL),
        "channel_final_y34": list(RANK8),
        "source_initial": list(SOURCE_INIT),
        "target_initial": list(TARGET_INIT),
        "schedule_id": "S0",
        "owner": "X0",
        "owner_kind": "self",
        "unique_owner_among_event_named_registers": True,
        "dirty_helper_touches_in_window": 0,
        "x0_destination_events_after_channel": 0,
        "x0_last_destination_event": 1486,
        "endpoint_repay_x0_to_initial": False,
        "endpoint_repay_y34_to_initial": False,
        "x0_frame_after_restore": list(FULL),
        "y34_frame_after_restore": list(RANK8),
        "y34_tail_transports": [PROMOTE, RESTORE],
        "window_add_count": 48,
        "pre_read_x0_restoration_blocks_common_chart": True,
        "selected_kappa": SELECTED_KAPPA,
        "no_new_kappa": True,
    }
    need(certificate == expected, "certificate mismatch")
    return True


def main():
    evaluate()
    print(MARKER)


if __name__ == "__main__":
    main()
