#!/usr/bin/env python3
"""Apply the dimension-3 read-first transfer to X102's 25-edge state.

Dimension 2 has already left X102 on 25 edges. This check spreads that state
once along the dimension-3 interval relation and does not build dimension 4.
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
MARKER = "PASS_P104_THIRD_TRANSFER reached=52 no_new_kappa"


def fail(message):
    raise SystemExit("FAIL_P104_THIRD_TRANSFER " + message)


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
    return paths, lines, departures, arrivals, edges


def holding(state):
    return [index for index, mask in enumerate(state) if (mask >> SOURCE) & 1]


def slot_counts(edges, chosen):
    counts = {}
    for index in chosen:
        slot = edges[index][0]
        counts[slot] = counts.get(slot, 0) + 1
    return [[slot, counts[slot]] for slot in sorted(counts)]


def evaluate():
    authenticate()
    checker = ARCHIVED.read_text(encoding="utf-8")
    require("seeded = [s | r for s, r in zip(state, reads, strict=True)]" in checker, "the seeding rule moved")
    require("return [(departures[a], arrivals[b]) for a, b in edges]" in checker, "the interval bound moved")
    word = json.loads(WITNESS.read_text(encoding="utf-8"))
    certificate = json.loads(CERTIFICATE.read_text(encoding="utf-8"))
    require(len(word["program"]) == 4058, "word length")
    paths, lines, departures, arrivals, edges = geometry(word, certificate)
    require(len(edges) == 2309, "compatible edges")
    line_bounds = [(lines[departure // 2], lines[departure // 2]) for departure, _ in edges]
    state = transfer([0] * len(edges), contacts(line_bounds, 1, paths, "X"), interval_relation(line_bounds, 1))
    plane_bounds = [(departures[departure], departures[departure]) for departure, _ in edges]
    state = transfer(state, contacts(plane_bounds, 2, paths, "X"), interval_relation(plane_bounds, 2))
    incoming = holding(state)
    require(slot_counts(edges, incoming) == [[165, 9], [204, 7], [205, 9]], "the incoming state moved")
    interval_bounds = [(departures[departure], arrivals[arrival]) for departure, arrival in edges]
    fresh = contacts(interval_bounds, 3, paths, "X")
    require(sum(bool((mask >> SOURCE) & 1) for mask in fresh) == 0, "dimension 3 read X102")
    state = transfer(state, fresh, interval_relation(interval_bounds, 3))
    reached = holding(state)
    added = [index for index in reached if index not in set(incoming)]
    added_counts = slot_counts(edges, added)
    require(len(reached) == 52 and len(added) == 27, "the reached count left 52")
    require(sum(count for _, count in added_counts) == 27, "the added edges moved")
    archived = json.loads(ARCHIVED_RESULT.read_text(encoding="utf-8"))
    layer = archived["layers"][2]
    require(layer["dimension"] == 3, "the archived dimension moved")
    require(layer["source102_readers"] == 0 and layer["source102_reached"] == 52, "the archived count moved")
    return {
        "source": SOURCE,
        "dimension": 3,
        "edges": len(edges),
        "incoming": len(incoming),
        "fresh_readers": 0,
        "reached": len(reached),
        "added_edges": len(added),
        "added_slots": added_counts,
        "no_new_kappa": True,
    }


def main():
    observed = evaluate()
    stored = json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))
    require(observed == stored, "RESULT.json does not match the execution: " + json.dumps(observed, sort_keys=True))
    print(MARKER)


if __name__ == "__main__":
    main()
