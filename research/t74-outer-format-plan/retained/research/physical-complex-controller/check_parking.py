# SPDX-License-Identifier: Apache-2.0
"""Physical nested continuation tests; expected snapshots are checker-only."""
from hashlib import sha256
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cohort
cohort.activate()
from cardinal_counts import Count
from parking import BODY, FiniteFields, Parking, transfer
from records import Tape
from words import BLANK


def body(tape):
    return bytes(tape.cells[1:]).rstrip(bytes([BLANK]))


def run():
    roles = tuple(Tape() for _ in range(7))
    parking = Parking(roles)
    header = FiniteFields((2, 3, 31756, 712))
    saved = []
    for depth in range(96):
        header.write(roles[0], (int(depth == 0), depth % 3, (depth * 307) % 31756, depth % 712))
        count = Count.literal((1 << (depth + 1)) + depth)
        transfer(count.tape, roles[1])
        count.close()
        for i in range(2, len(roles)):
            for j in range((depth * i + i) % 29):
                roles[i].append(BODY[(depth + j + i) % len(BODY)])
            roles[i].rewind()
        saved.append(tuple(body(t) for t in roles))
        parking.park()
        cohort.require(all(t.head == 1 and t.read() == BLANK for t in roles), "parent roles empty for child")
    digest = sha256()
    for depth in reversed(range(96)):
        parking.restore()
        cohort.require(tuple(body(t) for t in roles) == saved[depth], "exact parent continuation restoration")
        cohort.require(header.read(roles[0]) ==
                       (int(depth == 0), depth % 3, (depth * 307) % 31756, depth % 712), "finite continuation fields")
        for tape in roles:
            digest.update(body(tape))
            tape.clear()
    parking.empty()
    # A live child cannot overwrite its parked parent by returning early.
    roles[0].append(1)
    roles[0].rewind()
    parking.park()
    roles[0].append(0)
    roles[0].rewind()
    try:
        parking.restore()
    except ValueError as error:
        cohort.require(str(error) == "child closes roles before restoration", "live-child rejection")
    else:
        raise ValueError("live child restoration accepted")
    roles[0].clear()
    parking.restore()
    cohort.require(body(roles[0]) == b"\x01", "parent survives rejected early return")
    roles[0].clear()
    parking.empty()
    return {"nested_frames": 96, "roles_per_frame": 7, "finite_header_fields": 4,
            "sha256": digest.hexdigest(), "live_child_rejected": True,
            "scope": "Physical Count/payload continuation primitive; complete-controller checks run separately."}


if __name__ == "__main__":
    print(json.dumps(run(), sort_keys=True, indent=2))
