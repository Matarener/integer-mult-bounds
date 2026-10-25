#!/usr/bin/env python3
"""Apply the dimension-2 read-first transfer to X102's 16-edge state.

Dimension 1 has already left X102 on 16 edges. This check spreads that state
once along the dimension-2 relation and does not build the dimension-3 relation.
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
MARKER = "PASS_P104_PLANE_TRANSFER reached=25 no_new_kappa"


def fail(message):
    raise SystemExit("FAIL_P104_PLANE_TRANSFER " + message)


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
    return paths, lines, departures, edges


def holding(state):
    return [index for index, mask in enumerate(state) if (mask >> SOURCE) & 1]


def evaluate():
    authenticate()
    checker = ARCHIVED.read_text(encoding="utf-8")
    require("seeded = [s | r for s, r in zip(state, reads, strict=True)]" in checker, "the seeding rule moved")
    require("return [(departures[a], departures[a]) for a, _ in edges]" in checker, "the dimension-2 bound moved")
    word = json.loads(WITNESS.read_text(encoding="utf-8"))
    certificate = json.loads(CERTIFICATE.read_text(encoding="utf-8"))
    require(len(word["program"]) == 4058, "word length")
    paths, lines, departures, edges = geometry(word, certificate)
    require(len(edges) == 2309, "compatible edges")
    bounds = [(lines[departure // 2], lines[departure // 2]) for departure, _ in edges]
    incoming = transfer([0] * len(edges), contacts(bounds, 1, paths, "X"), interval_relation(bounds, 1))
    incoming_edges = holding(incoming)
    require(len(incoming_edges) == 16, "the incoming state left 16")
    plane_bounds = [(departures[departure], departures[departure]) for departure, _ in edges]
    fresh = contacts(plane_bounds, 2, paths, "X")
    require(sum(bool((mask >> SOURCE) & 1) for mask in fresh) == 0, "dimension 2 read X102")
    state = transfer(incoming, fresh, interval_relation(plane_bounds, 2))
    reached = holding(state)
    added = [index for index in reached if index not in set(incoming_edges)]
    added_slots = sorted({edges[index][0] for index in added})
    require(added_slots == [165], "the added departure moved")
    require(departures[165] == departures[205] and departures[165] != departures[204], "the shared plane moved")
    counts = {
        slot: sum(departure == slot for departure, _ in edges)
        for slot in (165, 204, 205)
    }
    require(counts == {165: 9, 204: 7, 205: 9}, "the plane edge counts moved")
    require(len(reached) == 25, "the reached count left 25")
    archived = json.loads(ARCHIVED_RESULT.read_text(encoding="utf-8"))
    layer = archived["layers"][1]
    require(layer["dimension"] == 2, "the archived dimension moved")
    require(layer["source102_readers"] == 0 and layer["source102_reached"] == 25, "the archived count moved")
    return {
        "source": SOURCE,
        "dimension": 2,
        "edges": len(edges),
        "incoming": len(incoming_edges),
        "fresh_readers": 0,
        "reached": len(reached),
        "held_slot": 204,
        "held_edges": counts[204],
        "shared_slot": 205,
        "shared_edges": counts[205],
        "added_slot": 165,
        "added_channel": 165 // 2,
        "added_edges": counts[165],
        "no_new_kappa": True,
    }


def main():
    observed = evaluate()
    stored = json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))
    require(observed == stored, "RESULT.json does not match the execution: " + json.dumps(observed, sort_keys=True))
    print(MARKER)


if __name__ == "__main__":
    main()
