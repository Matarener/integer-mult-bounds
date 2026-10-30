#!/usr/bin/env python3
"""Flag 0 relay window on the published channel word.

X0 must still hold the basis head when a one-register relay can reach Y34.
This checker reads the witness and the flag certificate. It does not import
the schedule package.
"""

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
MARKER = "PASS_P104_FLAG0_RELAY forward_relays=0 no_new_kappa"


def fail(message):
    raise SystemExit("FAIL_P104_FLAG0_RELAY " + message)


def require(condition, message):
    if not condition:
        fail(message)


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def authenticate():
    sources = json.loads((PACKAGE / "SOURCES.json").read_text(encoding="utf-8"))
    pinned = {row["path"]: row for row in sources["files"] if row["usage"] == "input"}
    expected = {
        "research/p104-native-channel/inputs/LOWRANK-WITNESS.json",
        "research/p104-joint-unit-flags/CERTIFICATE.json",
        "research/p104-flag-channel-schedule/README.md",
    }
    require(set(pinned) == expected, "input inventory changed")
    for path, row in pinned.items():
        require(sha256(ROOT / path) == row["sha256"], "input drift " + path)


def named(event):
    return [
        item
        for item in event
        if isinstance(item, str) and len(item) > 1 and item[0].isalpha() and item[1:].isdigit()
    ]


def meetings(program, name):
    found = {}
    for index, event in enumerate(program):
        names = named(event)
        if name in names:
            for other in names:
                if other != name:
                    found.setdefault(other, []).append(index)
    return found


def forward_relays(source_hits, target_hits):
    count = 0
    for register, source_events in source_hits.items():
        for target_index in target_hits.get(register, []):
            count += sum(1 for source_index in source_events if source_index < target_index)
    return count


def frame_at(program, name, index):
    frame = None
    for cursor, event in enumerate(program):
        if cursor > index:
            break
        if event[0] == "transport" and named(event) == [name]:
            frame = list(event[3])
    return frame


def evaluate():
    authenticate()
    note = (ROOT / "research/p104-flag-channel-schedule/README.md").read_text(encoding="utf-8")
    require(
        "A relay through another register could still carry a coefficient from `X0`\n"
        "after index 591 into `Y34`." in note,
        "the relay question moved",
    )
    certificate = json.loads(
        (ROOT / "research/p104-joint-unit-flags/CERTIFICATE.json").read_text(encoding="utf-8")
    )
    witness = json.loads(
        (ROOT / "research/p104-native-channel/inputs/LOWRANK-WITNESS.json").read_text(encoding="utf-8")
    )
    flag = certificate["helpers"][0]
    require(flag["source"] == 0 and flag["target"] == 34 and flag["basis"][0] == 232, "flag 0 changed")
    program = witness["program"]
    require(witness["initial_frames"]["X0"] == [232], "X0 does not start on the basis head")
    source_hits = meetings(program, "X0")
    target_hits = meetings(program, "Y34")
    require(all("Y34" not in hits for hits in source_hits.values()), "an event names both registers")
    shared = sorted(set(source_hits) & set(target_hits))
    require(shared == ["Q3", "Q4", "Q6"], "the shared relay registers changed")
    relays = [
        {
            "register": register,
            "source_events": source_hits[register],
            "target_events": target_hits[register],
        }
        for register in shared
    ]
    source_leave = next(
        index
        for index, event in enumerate(program)
        if event[0] == "transport" and named(event) == ["X0"] and event[2] == [232]
    )
    target_gain = next(
        index
        for index, event in enumerate(program)
        if event[0] == "transport" and named(event) == ["Y34"] and 232 in event[3]
    )
    source_frame = frame_at(program, "X0", target_gain)
    require(source_leave == 591 and target_gain == 3500, "the head window moved")
    require(232 not in source_frame, "X0 still holds the basis head")
    require(forward_relays(source_hits, target_hits) == 0, "a forward relay exists")
    return {
        "flag": 0,
        "basis_head": 232,
        "source_leaves_head": source_leave,
        "target_gains_head": target_gain,
        "source_frame_at_gain": source_frame,
        "head_window_open": False,
        "shared_relays": relays,
        "forward_relays": 0,
        "no_new_kappa": True,
    }


def main():
    observed = evaluate()
    expected = json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))
    require(observed == expected, "RESULT.json does not match the execution")
    print(MARKER)


if __name__ == "__main__":
    main()
