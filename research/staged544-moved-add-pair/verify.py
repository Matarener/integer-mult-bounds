#!/usr/bin/env python3
"""No commuting moved-ADD pair retargets a staged544 line onto a disjoint line.

The scalar program of the crossed-line pattern is unchanged and its child
histogram delta is zero. Selected kappa is not changed.
"""
import gzip
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "vendor"))
import retiming as R  # noqa: E402

SHA256 = {
    "inputs/BORROW-WORD-43base.json.gz":
        "5ca4be99851f8878cbfe0fd6c454df926b11218f17feefa1664721cf03156699",
    "inputs/BORROW-WORD-43extra.json.gz":
        "965268a9be73d3f62e7ef680d18f108cf064bfe1f44b82157baa61443232904e",
    "vendor/retiming.py":
        "591d7278541ac4de9e9b6fc1e17aba23b205ac4b6c81824a28fc08294658ef0d",
}


def need(ok, message):
    if not ok:
        raise SystemExit(message)


def crosses(g, h):
    """Independent copy of the scalar commutation normal form."""
    if h[0] == "add":
        return g[1] != h[2] and h[1] != g[2]
    return h[0] == "scale" and h[2] != 0


def authenticate():
    for name, digest in SHA256.items():
        blob = (ROOT / name).read_bytes()
        need(hashlib.sha256(blob).hexdigest() == digest, "sha256 mismatch: " + name)
    need(SHA256["inputs/BORROW-WORD-43base.json.gz"]
         != SHA256["inputs/BORROW-WORD-43extra.json.gz"], "providers identical")


def load(name):
    with gzip.open(ROOT / name, "rt", encoding="utf-8") as handle:
        return json.load(handle)


def witness(word):
    """One forcing operand for every rank-1 ADD, or None when the line is free."""
    nodes, where, _bill = R.tracing(word)
    rows = []
    for section in ("A", "B", "restore"):
        gates = word[section]
        for index, gate in enumerate(gates):
            if gate[0] != "add" or not gate[-1]:
                continue
            old = R.span(tuple(gate[-1]))
            if R.rank(old) != 1:
                continue
            found = None
            for register in R.touched(gate):
                sequence = nodes[register]
                position = where[((section, index), register)]
                incoming = sequence[position][2]
                if R.rank(incoming) == 0 or not R.contained(incoming, old):
                    continue
                intro = None
                for cursor in range(position - 1, -1, -1):
                    if (R.contained(incoming, sequence[cursor][3])
                            and not R.contained(incoming, sequence[cursor][2])):
                        intro = sequence[cursor]
                        break
                if intro is None:
                    found = {"kind": "entrance", "section": section, "index": index,
                             "register": register}
                    break
                address = intro[0]
                if not (isinstance(address, tuple) and address[0] == section
                        and gates[address[1]][0] == "add"):
                    found = {"kind": "map", "section": section, "index": index,
                             "register": register, "event": intro[1],
                             "source": address if isinstance(address, tuple) else None}
                    break
                producer = address[1]
                forward = crosses(gates[producer], gate)
                backward = crosses(gate, gates[producer])
                need(forward == R.crosses(gates[producer], gate)
                     and backward == R.crosses(gate, gates[producer]),
                     "commutation normal form diverged")
                if forward and backward:
                    continue
                found = {"kind": "dependence", "section": section,
                         "producer": producer, "index": index, "register": register,
                         "producer_rank": R.rank(R.span(tuple(gates[producer][-1])))}
                break
            rows.append(found)
    return rows


def check_windows(word, rows):
    """Finite hypotheses for the persistence argument.

    From the witness source through the consumer, every recorded frame contains
    the original line. Entrance and dependence windows contain no map, so no
    warp on that register sits in the interval. A map window starts at the
    witness warp and contains no later map.
    """
    nodes, where, _bill = R.tracing(word)
    for row in rows:
        section, index, register = row["section"], row["index"], row["register"]
        old = R.span(tuple(word[section][index][-1]))
        sequence = nodes[register]
        position = where[((section, index), register)]
        prior = sequence[:position]
        intro_at = None
        for cursor in range(len(prior) - 1, -1, -1):
            outgoing = prior[cursor][3]
            incoming = prior[cursor][2]
            if R.contained(old, outgoing) and not R.contained(old, incoming):
                intro_at = cursor
                break
        window = prior if intro_at is None else prior[intro_at:]
        for event in window:
            need(R.contained(old, event[3]), "witness window drops the original line")
        maps = [event for event in window if event[1] == "map"]
        if row["kind"] == "entrance":
            start = window[0][2] if window else sequence[position][2]
            need(R.contained(old, start), "entrance start misses the original line")
            need(maps == [], "entrance window contains a map")
        elif row["kind"] == "dependence":
            need(window and window[0][0] == (section, row["producer"]),
                 "dependence window does not start at the producer")
            need(maps == [], "dependence window contains a map")
        else:
            need(len(maps) == 1 and maps[0][0] == row["source"],
                 "map window is not exactly the witness warp")
            need(window[0][1] == "map", "map window does not start at the warp")


def check_provider(name):
    word = load(name)
    rows = witness(word)
    need(all(row is not None for row in rows), name + " has a free rank-1 ADD")
    check_windows(word, rows)
    counts = {}
    for row in rows:
        counts[row["kind"]] = counts.get(row["kind"], 0) + 1
    need(counts == {"entrance": 653, "map": 70, "dependence": 12},
         name + " witness counts " + str(counts))
    dependence = [row for row in rows if row["kind"] == "dependence"]
    for row in dependence:
        gates = word[row["section"]]
        consumer = gates[row["index"]]
        producer = gates[row["producer"]]
        need(row["producer"] < row["index"], "producer is not earlier")
        need(row["producer_rank"] == 1, "dependence producer is not rank 1")
        need(not crosses(producer, consumer) and not crosses(consumer, producer),
             "dependence pair commutes")
        need(consumer[2] == producer[1] or producer[2] == consumer[1],
             "dependence pair has no read-after-write")
        need(row["section"] == "A", "dependence pair is not in section A")
    order = {"A": 0, "B": 1, "restore": 2}
    maps = [row for row in rows if row["kind"] == "map"]
    need({row["event"] for row in maps} == {"map"}, "map witness is not a map event")
    for row in maps:
        source = row["source"]
        need(isinstance(source, tuple) and isinstance(source[0], str)
             and source[0].startswith("map-"), "map witness has no gate")
        warp_section = source[0].split("-", 1)[1]
        warp = word[warp_section][source[1]]
        need(warp[0] == "warp", "map witness is not a warp gate")
        consumer = word[row["section"]][row["index"]]
        need(not crosses(consumer, warp) and not R.crosses(consumer, warp),
             "an ADD can cross its map witness")
        if warp_section == row["section"]:
            need(source[1] < row["index"], "map witness is not earlier in the section")
        else:
            need(order[warp_section] < order[row["section"]],
                 "map witness is not in an earlier section")
    return counts, [(row["section"], row["producer"], row["index"], row["register"])
                    for row in dependence]


def local_children(frames):
    """Rank climbs on the two helper registers, without the target epilogue."""
    start = {0}
    end = {0, 1, 2, 3}

    def span(vectors):
        points = {0}
        for vector in vectors:
            points |= {point ^ vector for point in points}
        return points

    def rank(points):
        return (len(points).bit_length() - 1)

    bill = [0] * 10
    current = {300: set(start), 301: set(start)}
    for frame in frames:
        image = span(frame)
        for register in (300, 301):
            before = current[register]
            need(before <= image, "independent intermediate accepted a bad nest")
            bill[rank(image) - rank(before)] += 1
            current[register] = image
    for register in (300, 301):
        before = current[register]
        need(before <= end, "terminal frame does not contain the line")
        bill[rank(end) - rank(before)] += 1
    bill[0] = 0
    return bill


def check_toy():
    old = local_children(([1], [1]))
    new = local_children(([2], [2]))
    need(old == new == [0, 4] + [0] * 8, "toy helper bill " + str((old, new)))
    for frames in (([2], [1]), ([1], [2])):
        try:
            local_children(frames)
        except SystemExit:
            continue
        raise SystemExit("toy intermediate was legal")
    keep = set(range(112, 224)) | {300, 301}
    removed = [register for register in range(704) if register not in keep]

    def programmed(frames):
        return {
            "A": [["add", 300, 301, 1, 1, list(frame)] for frame in frames],
            "B": [], "restore": [], "removed": removed, "ports": [1] * 112,
            "start_extra": {}, "helper_final": {"300": [1, 2], "301": [1, 2]},
            "target_levels": {}, "centers": [], "center_frames": [], "cut": [],
            "prelude_events": 0, "warps": [], "cleanup": [],
        }

    original = programmed(([1], [1]))
    retargeted = programmed(([2], [2]))
    scalar = lambda word: [(gate[0], gate[1], gate[2], gate[3], gate[4]) for gate in word["A"]]
    need(scalar(original) == scalar(retargeted), "scalar program changed")
    bill_old = R.tracing(original)[2]
    bill_new = R.tracing(retargeted)[2]
    need(bill_old == bill_new, "tracer bill changed: " + str((bill_old, bill_new)))
    for frames in (([2], [1]), ([1], [2])):
        try:
            R.tracing(programmed(frames))
        except ValueError:
            continue
        raise SystemExit("tracer accepted a one-edit intermediate")


def main():
    authenticate()
    reports = {}
    pairs = None
    for name in ("inputs/BORROW-WORD-43base.json.gz",
                 "inputs/BORROW-WORD-43extra.json.gz"):
        counts, dependence = check_provider(name)
        reports[name] = counts
        if pairs is None:
            pairs = dependence
        else:
            need(dependence == pairs, "providers disagree on the dependence pairs")
    check_toy()
    print("PASS_MOVED_ADD_PAIR",
          "providers=2",
          "rank1=735",
          "entrance=653",
          "map=70",
          "dependence=12",
          "disjoint_line_moves=0",
          "toy_helper_bill=4xrank1",
          "toy_delta=0",
          "no_new_kappa")


if __name__ == "__main__":
    main()
