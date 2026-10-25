#!/usr/bin/env python3
"""Compare the frames at the flag-0 tail add with the channel's final frames.

X0 stays on the channel's full final frame. Y34 is promoted to that frame one
event earlier and restored after its 48 tail adds. This walk follows listed
bases. It does not import either package's verifier.
"""

import gzip
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
TAIL = ROOT / "research/p104-tail-side-correction-seed749717"
CHANNEL = ROOT / "research/p104-native-channel"
MARKER = "PASS_P104_TAIL_FLAG0_FRAMES promotion=5758 add=5759 restored=5807 no_new_kappa"
FULL = [1, 2, 4, 8, 16, 32, 64, 128, 256]
RANK8 = [499, 23, 232, 32, 112, 15, 7, 2]


def fail(message):
    raise SystemExit("FAIL_P104_TAIL_FLAG0_FRAMES " + message)


def require(condition, message):
    if not condition:
        fail(message)


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def span(vectors):
    out = {0}
    for vector in vectors:
        out |= {item ^ vector for item in tuple(out)}
    return tuple(sorted(out))


def walk(program, initial):
    frames = {name: list(basis) for name, basis in initial.items() if name in ("X0", "Y34")}
    transports = {"X0": [], "Y34": []}
    for index, event in enumerate(program):
        if event[0] != "transport" or event[1] not in frames:
            continue
        _op, reg, old, new, rank = event
        require(old == frames[reg], "a listed transport left its current frame at " + str(index))
        frames[reg] = list(new)
        transports[reg].append(index)
    return frames, transports


def authenticate():
    sources = json.loads((PACKAGE / "SOURCES.json").read_text(encoding="utf-8"))
    pinned = {row["path"]: row for row in sources["files"] if row["usage"] == "input"}
    expected = {
        "research/p104-native-channel/inputs/LOWRANK-WITNESS.json",
        "research/p104-tail-side-correction-seed749717/AUGMENTED-WITNESS.json.gz",
    }
    require(set(pinned) == expected, "input inventory changed")
    for path, row in pinned.items():
        require(sha256(ROOT / path) == row["sha256"], "input drift " + path)


def evaluate():
    authenticate()
    channel = json.loads((CHANNEL / "inputs/LOWRANK-WITNESS.json").read_text(encoding="utf-8"))
    tail = json.loads(gzip.decompress((TAIL / "AUGMENTED-WITNESS.json.gz").read_bytes()))
    require(tail["program"][:4058] == channel["program"], "the tail prefix left the channel word")
    require(channel["final_frames"]["X0"] == FULL, "the channel left a different X0 frame")
    require(channel["final_frames"]["Y34"] == RANK8, "the channel left a different Y34 frame")
    require(tail["final_frames"]["X0"] == FULL and tail["final_frames"]["Y34"] == RANK8, "the tail ends on different frames")
    _frames, channel_moves = walk(channel["program"], channel["initial_frames"])
    require(channel_moves["X0"][-1] < 4058 and channel_moves["Y34"][-1] < 4058, "a channel transport sits past the prefix")
    frames, moves = walk(tail["program"][:4058], tail["initial_frames"])
    require(frames["X0"] == FULL and frames["Y34"] == RANK8, "the prefix ends on different frames")
    later_x0 = [index for index in moves["X0"] if index >= 4058]
    later_y34 = [index for index in walk(tail["program"], tail["initial_frames"])[1]["Y34"] if index >= 4058]
    require(later_x0 == [], "a tail transport writes X0")
    require(later_y34 == [5758, 5807], "the Y34 tail transports moved")
    promotion = tail["program"][5758]
    addition = tail["program"][5759]
    restoration = tail["program"][5807]
    require(promotion == ["transport", "Y34", RANK8, FULL, 1], "the promotion changed")
    require(addition == ["add", "Y34", "X0", "-1/2", FULL], "the flag-0 add changed")
    require(restoration == ["transport", "Y34", FULL, RANK8, 1], "the restoration changed")
    window = [
        index for index, event in enumerate(tail["program"])
        if 5758 < index < 5807 and event[0] == "add" and event[1] == "Y34"
    ]
    require(window[0] == 5759 and window[-1] == 5806 and len(window) == 48, "the promoted add window changed")
    old_span = span(RANK8)
    full_span = span(FULL)
    require(len(old_span) == 256 and len(full_span) == 512 and set(old_span) <= set(full_span), "the rank-8 span left the full span")
    x0_writes = [
        index for index, event in enumerate(tail["program"])
        if index >= 4058 and event[1] == "X0"
    ]
    require(x0_writes == [], "a tail event writes X0")
    return {
        "channel_final": {"X0": FULL, "Y34": RANK8},
        "prefix_end_matches_channel_final": True,
        "x0_writes_after_prefix": 0,
        "promotion": {"event": 5758, "rank": 1, "from": RANK8, "to": FULL},
        "add": {"event": 5759, "frame": FULL, "x0_frame": FULL, "y34_frame": FULL},
        "restoration": {"event": 5807, "rank": 1, "to": RANK8},
        "promoted_adds": 48,
        "rank8_span_inside_full_span": True,
        "no_new_kappa": True,
    }


def main():
    observed = evaluate()
    stored = json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))
    require(observed == stored, "RESULT.json does not match the execution: " + json.dumps(observed, sort_keys=True))
    print(MARKER)


if __name__ == "__main__":
    main()
