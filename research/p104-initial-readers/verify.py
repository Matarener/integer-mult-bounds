#!/usr/bin/env python3
"""Count X102's readers from the departures on its initial line.

The archived contact rule reads a source when one of its frames fits a
helper bound. This check builds the compatible edges and does not run the
read-first transfer.
"""

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
WITNESS = ROOT / "research/p104-native-channel/inputs/LOWRANK-WITNESS.json"
CERTIFICATE = ROOT / "research/p104-joint-unit-flags/CERTIFICATE.json"
ARCHIVED = ROOT / "research/p104-pooled-cut-independent/verify.py"
ARCHIVED_RESULT = ROOT / "research/p104-pooled-cut-independent/RESULT.json"
SOURCE = 102
MARKER = "PASS_P104_INITIAL_READERS readers=16 no_new_kappa"


def fail(message):
    raise SystemExit("FAIL_P104_INITIAL_READERS " + message)


def require(condition, message):
    if not condition:
        fail(message)


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def points(basis):
    require(type(basis) is list and len(basis) <= 9, "basis size")
    result = [0]
    for vector in basis:
        require(type(vector) is int and 0 < vector < 512 and vector not in result, "basis vector")
        result += [point ^ vector for point in result]
    return frozenset(result)


def chain(word, name):
    frames = [points(word["initial_frames"][name])]
    for event in word["program"]:
        if event[0] != "transport" or event[1] != name:
            continue
        old, new = points(event[2]), points(event[3])
        require(frames[-1] == old and old < new, "monotone data path")
        require(len(new) == len(old) * 2 ** event[4], "transport rank")
        frames.append(new)
    require(frames[-1] == points(word["final_frames"][name]), "final frame")
    return frames


def contacts(bounds, dimension, paths, kind):
    snapshots = [
        (index, frame)
        for index in range(104)
        for frame in paths[f"{kind}{index}"]
        if len(frame) == 2 ** dimension
    ]
    return [
        sum(1 << index for index, frame in snapshots if low <= frame <= high)
        for low, high in bounds
    ]


def authenticate():
    sources = json.loads((PACKAGE / "SOURCES.json").read_text(encoding="utf-8"))
    pinned = {row["path"]: row for row in sources["files"] if row["usage"] == "input"}
    expected = {
        "research/p104-native-channel/inputs/LOWRANK-WITNESS.json",
        "research/p104-joint-unit-flags/CERTIFICATE.json",
        "research/p104-pooled-cut-independent/verify.py",
        "research/p104-pooled-cut-independent/RESULT.json",
    }
    require(set(pinned) == expected, "input inventory changed")
    for path, row in pinned.items():
        require(sha256(ROOT / path) == row["sha256"], "input drift " + path)


def evaluate():
    authenticate()
    checker = ARCHIVED.read_text(encoding="utf-8")
    require("return [(lines[a // 2], lines[a // 2]) for a, _ in edges]" in checker, "the dimension-1 bound moved")
    require("if len(f) == 2**dimension" in checker, "the snapshot rule moved")
    require("sum(1 << i for i, f in snapshots if low <= f <= high)" in checker, "the contact rule moved")
    word = json.loads(WITNESS.read_text(encoding="utf-8"))
    certificate = json.loads(CERTIFICATE.read_text(encoding="utf-8"))
    require(len(word["program"]) == 4058, "word length")
    require(set(certificate["forms"]) == {"departure", "arrival"}, "cover kinds")
    paths = {f"{kind}{index}": chain(word, f"{kind}{index}") for kind in "XY" for index in range(104)}
    lines = [paths[f"X{index}"][0] for index in range(104)]
    caps = [paths[f"Y{index}"][-1] for index in range(104)]
    departures, arrivals = [], []
    for index in range(104):
        require(len(certificate["forms"]["departure"][index]) == 2, "departure count")
        require(len(certificate["forms"]["arrival"][index]) == 2, "arrival count")
        for vector in certificate["forms"]["departure"][index]:
            line = next(point for point in lines[index] if point)
            departures.append(points([line, vector]))
        for functional in certificate["forms"]["arrival"][index]:
            arrivals.append(frozenset(
                point for point in caps[index] if (point & functional).bit_count() % 2 == 0
            ))
    require(len(departures) == len(arrivals) == 208, "slot count")
    require(all(len(slot) == 4 for slot in departures) and all(len(slot) == 128 for slot in arrivals), "cover dimensions")
    edges = [(departure, arrival) for departure in range(208) for arrival in range(208) if departures[departure] <= arrivals[arrival]]
    require(len(edges) == 2309, "compatible edges")
    line = paths["X102"][0]
    channels = [index for index, frame in enumerate(lines) if frame == line]
    slots = [slot for slot in range(208) if lines[slot // 2] == line]
    compatible = sorted({departure for departure, _ in edges if lines[departure // 2] == line})
    matched = [(departure, arrival) for departure, arrival in edges if lines[departure // 2] == line]
    bounds = {
        1: [(lines[departure // 2], lines[departure // 2]) for departure, _ in edges],
        2: [(departures[departure], departures[departure]) for departure, _ in edges],
        7: [(arrivals[arrival], arrivals[arrival]) for _, arrival in edges],
        8: [(caps[arrival // 2], caps[arrival // 2]) for _, arrival in edges],
    }
    for dimension in range(3, 7):
        bounds[dimension] = [(departures[departure], arrivals[arrival]) for departure, arrival in edges]
    readers = []
    for dimension in range(1, 9):
        reads = contacts(bounds[dimension], dimension, paths, "X")
        readers.append(sum(bool((mask >> SOURCE) & 1) for mask in reads))
    archived = json.loads(ARCHIVED_RESULT.read_text(encoding="utf-8"))
    archived_readers = [row["source102_readers"] for row in archived["layers"]]
    require(archived["edges"] == 2309, "the archived edge count moved")
    require(archived_readers == [16, 0, 0, 0, 0, 0, 0, 0], "the archived reader row moved")
    require(channels == [102] and slots == [204, 205] and compatible == [204, 205], "the departure slots moved")
    require(len(matched) == 16 and readers == archived_readers, "the reader count moved")
    return {
        "source": SOURCE,
        "channels": channels,
        "departure_slots": slots,
        "compatible_slots": compatible,
        "compatible_edges": len(matched),
        "edges": len(edges),
        "readers": readers,
        "no_new_kappa": True,
    }


def main():
    observed = evaluate()
    stored = json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))
    require(observed == stored, "RESULT.json does not match the execution: " + json.dumps(observed, sort_keys=True))
    print(MARKER)


if __name__ == "__main__":
    main()
