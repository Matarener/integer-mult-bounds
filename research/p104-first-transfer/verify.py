#!/usr/bin/env python3
"""Apply one dimension-1 read-first transfer to X102's readers.

The 16 dimension-1 readers already hold X102. This check spreads that signal
once along the dimension-1 relation and does not build the dimension-2 relation.
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
MARKER = "PASS_P104_FIRST_TRANSFER reached=16 no_new_kappa"


def fail(message):
    raise SystemExit("FAIL_P104_FIRST_TRANSFER " + message)


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


def bitmap(space):
    return sum(1 << point for point in space)


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


def interval_relation(bounds, dimension):
    masks = [(bitmap(low), bitmap(high)) for low, high in bounds]
    adjacency = [1 << index for index in range(len(bounds))]
    for index, (left, right) in enumerate(masks):
        for earlier in range(index):
            other_left, other_right = masks[earlier]
            if left & other_right != left or other_left & right != other_left:
                continue
            lower = left.bit_count() * other_left.bit_count() // (left & other_left).bit_count()
            if lower <= 2 ** dimension <= (right & other_right).bit_count():
                adjacency[index] |= 1 << earlier
                adjacency[earlier] |= 1 << index
    return adjacency


def transfer(state, reads, adjacency):
    seeded = [held | read for held, read in zip(state, reads, strict=True)]
    result = seeded.copy()
    for index, signal in enumerate(seeded):
        if signal:
            mask = adjacency[index]
            for other in range(len(state)):
                if (mask >> other) & 1:
                    result[other] |= signal
    return result


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


def geometry(word, certificate):
    paths = {f"{kind}{index}": chain(word, f"{kind}{index}") for kind in "XY" for index in range(104)}
    lines = [paths[f"X{index}"][0] for index in range(104)]
    caps = [paths[f"Y{index}"][-1] for index in range(104)]
    departures, arrivals = [], []
    for index in range(104):
        for vector in certificate["forms"]["departure"][index]:
            line = next(point for point in lines[index] if point)
            departures.append(points([line, vector]))
        for functional in certificate["forms"]["arrival"][index]:
            arrivals.append(frozenset(
                point for point in caps[index] if (point & functional).bit_count() % 2 == 0
            ))
    edges = [
        (departure, arrival)
        for departure in range(208)
        for arrival in range(208)
        if departures[departure] <= arrivals[arrival]
    ]
    return paths, lines, edges


def evaluate():
    authenticate()
    checker = ARCHIVED.read_text(encoding="utf-8")
    require("seeded = [s | r for s, r in zip(state, reads, strict=True)]" in checker, "the seeding rule moved")
    require("result[j] |= signal" in checker, "the transfer rule moved")
    require("lower = a.bit_count() * c.bit_count() // (a & c).bit_count()" in checker, "the interval test moved")
    word = json.loads(WITNESS.read_text(encoding="utf-8"))
    certificate = json.loads(CERTIFICATE.read_text(encoding="utf-8"))
    require(len(word["program"]) == 4058, "word length")
    paths, lines, edges = geometry(word, certificate)
    require(len(edges) == 2309, "compatible edges")
    bounds = [(lines[departure // 2], lines[departure // 2]) for departure, _ in edges]
    reads = contacts(bounds, 1, paths, "X")
    adjacency = interval_relation(bounds, 1)
    state = transfer([0] * len(edges), reads, adjacency)
    readers = [index for index, mask in enumerate(reads) if (mask >> SOURCE) & 1]
    reached = [index for index, mask in enumerate(state) if (mask >> SOURCE) & 1]
    require(len(readers) == 16 and reached == readers, "the transfer left the reader set")
    reader_mask = sum(1 << index for index in readers)
    require(all(adjacency[index] == reader_mask for index in readers), "the readers are not a clique")
    archived = json.loads(ARCHIVED_RESULT.read_text(encoding="utf-8"))
    layer = archived["layers"][0]
    require(layer["dimension"] == 1, "the first archived layer moved")
    require(layer["source102_readers"] == 16 and layer["source102_reached"] == 16, "the archived dimension-1 count moved")
    return {
        "source": SOURCE,
        "dimension": 1,
        "edges": len(edges),
        "readers": len(readers),
        "neighbors": adjacency[readers[0]].bit_count(),
        "reached": len(reached),
        "reached_equals_readers": True,
        "no_new_kappa": True,
    }


def main():
    observed = evaluate()
    stored = json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))
    require(observed == stored, "RESULT.json does not match the execution: " + json.dumps(observed, sort_keys=True))
    print(MARKER)


if __name__ == "__main__":
    main()
