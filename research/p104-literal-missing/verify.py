#!/usr/bin/env python3
"""List the required pairs missed by the literal quotient recurrence.

Every source is accumulated through dimensions 1 through 8. Edges share a
signal when one reduced quotient frame of the departure inside the arrival
occurs on both edges. Each literal relation is compared with the interval
relation and with the archived layer digest. The backward cone is not rebuilt.
"""

import hashlib
import json
from itertools import combinations, product
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
WITNESS = ROOT / "research/p104-native-channel/inputs/LOWRANK-WITNESS.json"
CERTIFICATE = ROOT / "research/p104-joint-unit-flags/CERTIFICATE.json"
FIXTURE = ROOT / "research/p104-native-channel/inputs/P104-FIXTURE.json"
ARCHIVED = ROOT / "research/p104-pooled-cut-independent/verify.py"
ARCHIVED_RESULT = ROOT / "research/p104-pooled-cut-independent/RESULT.json"
MARKER = "PASS_P104_LITERAL_MISSING missing=1 no_new_kappa"


def fail(message):
    raise SystemExit("FAIL_P104_LITERAL_MISSING " + message)


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


def quotient_subspaces():
    """Reduced subspaces of the five-dimensional quotient, grouped by dimension."""
    grouped = [[] for _ in range(6)]
    for size in range(6):
        for pivots in combinations(range(5), size):
            free = [
                (row, column)
                for row, pivot in enumerate(pivots)
                for column in range(pivot + 1, 5)
                if column not in pivots
            ]
            for code in range(1 << len(free)):
                basis = [1 << pivot for pivot in pivots]
                for bit, (row, column) in enumerate(free):
                    if (code >> bit) & 1:
                        basis[row] |= 1 << column
                grouped[size].append(points(basis))
    require([len(group) for group in grouped] == [1, 31, 155, 155, 31, 1], "quotient census")
    require(all(len(set(group)) == len(group) for group in grouped), "duplicate quotient")
    return grouped


def literal_choices(low, high, dimension, quotients):
    if low == high:
        return [bitmap(low)]
    basis = []
    generated = set(low)
    for vector in sorted(high):
        if vector not in generated:
            basis.append(vector)
            generated |= {point ^ vector for point in tuple(generated)}
    require(len(basis) == 5 and generated == high, "five-dimensional quotient")
    cosets = []
    for code in range(32):
        shift = 0
        for index in range(5):
            if (code >> index) & 1:
                shift ^= basis[index]
        cosets.append(bitmap(frozenset(point ^ shift for point in low)))
    frames = []
    for quotient in quotients[dimension - 2]:
        frame = 0
        for point in quotient:
            frame |= cosets[point]
        frames.append(frame)
    return frames


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


def layer_digest(adjacency):
    width = (len(adjacency) + 7) // 8
    payload = b"".join(mask.to_bytes(width, "little") for mask in adjacency)
    return hashlib.sha256(payload).hexdigest()


def literal_relation(bounds, dimension, quotients):
    choices = [literal_choices(low, high, dimension, quotients) for low, high in bounds]
    hosts = {}
    for index, frames in enumerate(choices):
        for frame in frames:
            hosts[frame] = hosts.get(frame, 0) | (1 << index)
    adjacency = []
    for frames in choices:
        neighbors = 0
        for frame in frames:
            neighbors |= hosts[frame]
        adjacency.append(neighbors)
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


def bounds_at(dimension, lines, departures, arrivals, caps, edges):
    if dimension == 1:
        return [(lines[departure // 2], lines[departure // 2]) for departure, _ in edges]
    if dimension == 2:
        return [(departures[departure], departures[departure]) for departure, _ in edges]
    if dimension == 7:
        return [(arrivals[arrival], arrivals[arrival]) for _, arrival in edges]
    if dimension == 8:
        return [(caps[arrival // 2], caps[arrival // 2]) for _, arrival in edges]
    require(3 <= dimension <= 6, "layer dimension")
    return [(departures[departure], arrivals[arrival]) for departure, arrival in edges]


def ports_of(fixture):
    removed = fixture["section4_explicit_P104"]
    roots = []
    for i, j in combinations(range(8), 2):
        for sign in (-1, 1):
            row = [0] * 8
            row[i], row[j] = 2, 2 * sign
            roots.append(tuple(row))
    roots += [(1, *signs) for signs in product((-1, 1), repeat=7) if signs.count(-1) % 2 == 0]
    ports = sorted(set(roots) - {tuple(vector) for vector in removed["F0"] + removed["C"]})
    require(len(roots) == 120 and len(ports) == 104, "P104 roots")
    return ports


def entry(ports, target, source):
    return 8 * int(target == source) - sum(
        left * right for left, right in zip(ports[source], ports[target], strict=True)
    )


def pair_is_missing(output, value, source):
    return value != 0 and (output >> source) & 1 == 0


def absent(outputs, ports):
    missing = []
    required = 0
    for target in range(104):
        for source in range(104):
            value = entry(ports, target, source)
            if value == 0:
                continue
            required += 1
            if pair_is_missing(outputs[target], value, source):
                missing.append([target, source])
    return required, missing


def authenticate():
    sources = json.loads((PACKAGE / "SOURCES.json").read_text(encoding="utf-8"))
    pinned = {row["path"]: row for row in sources["files"] if row["usage"] == "input"}
    expected = {
        "research/p104-native-channel/inputs/LOWRANK-WITNESS.json",
        "research/p104-native-channel/inputs/P104-FIXTURE.json",
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
    return paths, lines, departures, arrivals, caps, edges


def evaluate():
    authenticate()
    checker = ARCHIVED.read_text(encoding="utf-8")
    require("def literal_relation(" in checker, "the literal relation moved")
    require("quotients[dimension - 2]" in checker, "the quotient index moved")
    require("hosts[frame] = hosts.get(frame, 0) | (1 << i)" in checker, "the shared-frame rule moved")
    require("def interval_relation(" in checker, "the interval relation moved")
    word = json.loads(WITNESS.read_text(encoding="utf-8"))
    certificate = json.loads(CERTIFICATE.read_text(encoding="utf-8"))
    fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
    require(len(word["program"]) == 4058, "word length")
    paths, lines, departures, arrivals, caps, edges = geometry(word, certificate)
    require(len(edges) == 2309, "compatible edges")
    archived = json.loads(ARCHIVED_RESULT.read_text(encoding="utf-8"))
    require(archived["required"] == 4992 and archived["missing"] == [[71, 102]], "the archived gap moved")
    require(len(archived["layers"]) == 8, "archived layer count")
    quotients = quotient_subspaces()
    outputs = [
        sum(1 << source for source in range(104) if set(paths[f"X{source}"]) & set(paths[f"Y{target}"]))
        for target in range(104)
    ]
    state = [0] * len(edges)
    for dimension in range(1, 9):
        bounds = bounds_at(dimension, lines, departures, arrivals, caps, edges)
        reads = contacts(bounds, dimension, paths, "X")
        writes = contacts(bounds, dimension, paths, "Y")
        literal = literal_relation(bounds, dimension, quotients)
        require(literal == interval_relation(bounds, dimension), "relations differ at dimension " + str(dimension))
        require(
            layer_digest(literal) == archived["layers"][dimension - 1]["relation_sha256"],
            "archived digest differs at dimension " + str(dimension),
        )
        state = transfer(state, reads, literal)
        for index, targets in enumerate(writes):
            for target in range(104):
                if (targets >> target) & 1:
                    outputs[target] |= state[index]
    ports = ports_of(fixture)
    required, missing = absent(outputs, ports)
    value = entry(ports, 71, 102)
    require(
        required == 4992 and missing == [[71, 102]] and value == -4,
        "the literal gap moved: " + json.dumps({"required": required, "missing": missing, "entry": value}),
    )
    return {
        "required_pairs": required,
        "reached_pairs": required - len(missing),
        "missing": missing,
        "entry": str(value),
        "coefficient": "-1/2",
        "relations_equal": True,
        "no_new_kappa": True,
    }


def main():
    observed = evaluate()
    stored = json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))
    require(observed == stored, "RESULT.json does not match the execution: " + json.dumps(observed, sort_keys=True))
    print(MARKER)


if __name__ == "__main__":
    main()
