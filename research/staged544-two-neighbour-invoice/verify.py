#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Long first-ADD retiming invoices on the two pinned staged544 providers.

The first-move price depends only on dimension. Every legal cut that crosses
at least two scalar neighbours is certified nonnegative for every feasible
common-frame dimension. One changed-frame witness is then continued through
every single-ADD retiming of the edited word.
"""
import gzip
import hashlib
import json
from importlib.machinery import SourceFileLoader
from pathlib import Path

P = Path(__file__).resolve().parent
HASHES = {
    "vendor/retiming.py": "591d7278541ac4de9e9b6fc1e17aba23b205ac4b6c81824a28fc08294658ef0d",
    "vendor/audit_core.py": "888679ca8502cdcb100420fe5382a052529a494bf76cb332928b86e62612b951",
    "inputs/BORROW-WORD-43base.json.gz": "5ca4be99851f8878cbfe0fd6c454df926b11218f17feefa1664721cf03156699",
    "inputs/BORROW-WORD-43extra.json.gz": "965268a9be73d3f62e7ef680d18f108cf064bfe1f44b82157baa61443232904e",
}
WITNESS = {
    "provider": "base",
    "section": "A",
    "index": 595,
    "cut": 1214,
    "frame": [85],
    "gate_head": ["add", 459, 510, -1, 1],
    "original_frame": [],
    "crossed": 618,
    "first_delta": [0, 3, 0, -1, 0, 0, 0, 0, 0, 0],
    "first_caps": [2, 1, 0, 0, 0, 0, 0, 0, 0],
    "second_candidates": 1767681,
    "edited_profile": {1: 2443, 2: 725, 3: 223, 4: 102, 5: 20, 8: 8},
    "original_profile": {1: 2440, 2: 725, 3: 224, 4: 102, 5: 20, 8: 8},
}
# Dimension-complete long-first censuses. Locked after the source-bound run.
EXPECTED = {
    "base": {"adds": 5501, "long_gates": 4979, "cases": 1761760, "nonzero": 239103, "neutral": 1522657, "improving": 0},
    "extra": {"adds": 5501, "long_gates": 4979, "cases": 1761760, "nonzero": 239103, "neutral": 1522657, "improving": 0},
}


def need(ok, message):
    if not ok:
        raise SystemExit(message)


def load(name, path):
    return SourceFileLoader(name, str(path)).load_module()


def authenticate():
    for rel, digest in HASHES.items():
        raw = (P / rel).read_bytes()
        need(hashlib.sha256(raw).hexdigest() == digest, "sha256 mismatch: " + rel)


def load_word(tag):
    return json.loads(gzip.decompress((P / "inputs" / f"BORROW-WORD-43{tag}.json.gz").read_bytes()))


def segment_bounds(R, word, section, index):
    for lo, hi in R.segments(word, section):
        if lo <= index < hi:
            return lo, hi
    raise SystemExit("index outside every segment")


def long_cuts(R, gates, lo, hi, index):
    gate = gates[index]
    lower, upper = index, index + 1
    while lower > lo and R.crosses(gate, gates[lower - 1]):
        lower -= 1
    while upper < hi and R.crosses(gate, gates[upper]):
        upper += 1
    cuts = []
    for cut in range(lower, upper + 1):
        if cut == index + 1:
            continue
        crossed = gates[index + 1:cut] if cut > index else gates[cut:index]
        if len(crossed) >= 2:
            cuts.append(cut)
    return cuts


def removal_histogram(R, word, nodes, where, section, index):
    gate = word[section][index]
    delta = [0] * 10
    for register in R.touched(gate):
        seq = nodes[register]
        pos = where[((section, index), register)]
        _, _, before, frame = seq[pos]
        need(seq[pos + 1][1] != "map", "missing successor")
        after = seq[pos + 1][3]
        delta[R.rank(frame) - R.rank(before)] -= 1
        delta[R.rank(after) - R.rank(frame)] -= 1
        delta[R.rank(after) - R.rank(before)] += 1
    return delta


def cut_bounds(R, gates, occurrences, entries, exits, index, cut):
    bounds = []
    for register in R.touched(gates[index]):
        indices = [x for x in occurrences[register] if x != index]
        j = 0
        while j < len(indices) and indices[j] < cut:
            j += 1
        before = R.span(tuple(gates[indices[j - 1]][-1])) if j else entries[register]
        after = R.span(tuple(gates[indices[j]][-1])) if j < len(indices) else exits[register]
        bounds.append((before, after))
    low = R.join(bounds[0][0], bounds[1][0])
    high = bounds[0][1] & bounds[1][1]
    return low, high, bounds


def insertion_delta(removal, dims, dimension):
    delta = removal.copy()
    for before, after in dims:
        delta[after - before] -= 1
        delta[dimension - before] += 1
        delta[after - dimension] += 1
    delta[0] = 0
    return delta


def long_first_census(R, word):
    nodes, where, traced = R.tracing(word)
    counts = {"adds": 0, "long_gates": 0, "cases": 0, "nonzero": 0, "neutral": 0, "improving": 0}
    for section in ("A", "B", "restore"):
        gates = word[section]
        for lo, hi in R.segments(word, section):
            occurrences = {}
            for index in range(lo, hi):
                for register in R.touched(gates[index]):
                    occurrences.setdefault(register, []).append(index)
            entries, exits = {}, {}
            for register, indices in occurrences.items():
                entries[register] = nodes[register][where[((section, indices[0]), register)]][2]
                last = where[((section, indices[-1]), register)]
                need(nodes[register][last + 1][1] != "map", "missing exit")
                exits[register] = nodes[register][last + 1][3]
            for index in range(lo, hi):
                if gates[index][0] != "add":
                    continue
                counts["adds"] += 1
                cuts = long_cuts(R, gates, lo, hi, index)
                if not cuts:
                    continue
                counts["long_gates"] += 1
                removal = removal_histogram(R, word, nodes, where, section, index)
                for cut in cuts:
                    low, high, bounds = cut_bounds(R, gates, occurrences, entries, exits, index, cut)
                    if not R.contained(low, high):
                        continue
                    dims = [(R.rank(before), R.rank(after)) for before, after in bounds]
                    for dimension in range(R.rank(low), R.rank(high) + 1):
                        delta = insertion_delta(removal, dims, dimension)
                        need(sum(rank * count for rank, count in enumerate(delta)) == 0, "rank mass drift")
                        counts["cases"] += 1
                        if any(delta):
                            counts["nonzero"] += 1
                        else:
                            counts["neutral"] += 1
                        if not R.all_power_nonnegative(delta):
                            counts["improving"] += 1
    need(traced == {int(rank): count for rank, count in word["report"]["local_profile"].items()}
         or traced == word["report"]["local_profile"], "trace/profile disagreement")
    # local_profile keys may already be ints
    profile = {int(rank): count for rank, count in word["report"]["local_profile"].items()}
    need(traced == profile, "trace bill differs from declared profile")
    return counts, nodes, where


def witness_invoice(R, C, word):
    section = WITNESS["section"]
    index = WITNESS["index"]
    cut = WITNESS["cut"]
    gates = word[section]
    gate = gates[index]
    need(gate[:5] == WITNESS["gate_head"], "witness gate changed")
    need(gate[-1] == WITNESS["original_frame"], "witness original frame changed")
    crossed = gates[index + 1:cut]
    need(len(crossed) == WITNESS["crossed"], "witness crossing length changed")
    need(any(item[0] == "add" for item in crossed) and any(item[0] == "scale" for item in crossed),
         "witness must cross both an ADD and a SCALE")
    nodes, where, _ = R.tracing(word)
    lo, hi = segment_bounds(R, word, section, index)
    occurrences = {}
    for cursor in range(lo, hi):
        for register in R.touched(gates[cursor]):
            occurrences.setdefault(register, []).append(cursor)
    entries, exits = {}, {}
    for register, indices in occurrences.items():
        entries[register] = nodes[register][where[((section, indices[0]), register)]][2]
        last = where[((section, indices[-1]), register)]
        exits[register] = nodes[register][last + 1][3]
    low, high, bounds = cut_bounds(R, gates, occurrences, entries, exits, index, cut)
    need(R.contained(low, high), "witness interval empty")
    need(R.basis(high) == tuple(WITNESS["frame"]), "witness frame is not the unique upper line")
    need(not R.contained(R.span((1,)), high), "control vector 1 must lie outside the witness line")
    dims = [(R.rank(before), R.rank(after)) for before, after in bounds]
    removal = removal_histogram(R, word, nodes, where, section, index)
    delta = insertion_delta(removal, dims, 1)
    need(delta == WITNESS["first_delta"], "witness first delta changed: " + str(delta))
    need(R.caps(delta) == WITNESS["first_caps"], "witness caps changed")
    need(R.all_power_nonnegative(delta), "witness first move lost its certificate")
    edited = R.apply_move(word, section, index, cut, WITNESS["frame"])
    C.hygiene(edited)
    edited["cleanup"] = C.derive_cleanup(edited)
    C.hygiene(edited)
    original_bill, _widths, *_rest = C.frame_bill(word)
    edited_bill, _widths, *_rest = C.frame_bill(edited)
    need(original_bill == WITNESS["original_profile"], "original frame bill changed")
    need(edited_bill == WITNESS["edited_profile"], "edited frame bill changed")
    traced = R.tracing(edited)[2]
    need(traced == edited_bill, "edited trace disagrees with frame bill")
    second = R.census(edited)
    need(second["candidates"] == WITNESS["second_candidates"], "second-move count changed")
    first = WITNESS["first_delta"]
    for row in second["deltas"]:
        combined = first.copy()
        for rank, count in row["delta"].items():
            combined[int(rank)] += count
        need(sum(rank * count for rank, count in enumerate(combined)) == 0, "combined rank mass")
        need(R.all_power_nonnegative(combined), "combined continuation improves: " + str(combined))
    return second["candidates"]


def failure_controls(R):
    losing = [0, -1, 0, 0, 0, 0, 0, 0, 0, 0]
    need(not R.all_power_nonnegative(losing), "negative control was certified")
    neutral = [0] * 10
    need(R.all_power_nonnegative(neutral), "zero delta must be neutral")
    need(R.rank(R.span(())) == 0, "empty frame rank")


def main():
    authenticate()
    R = load("staged544_retiming", P / "vendor" / "retiming.py")
    C = load("staged544_audit_core", P / "vendor" / "audit_core.py")
    failure_controls(R)
    summary = {}
    for tag in ("base", "extra"):
        word = load_word(tag)
        counts, _nodes, _where = long_first_census(R, word)
        need(counts["improving"] == 0, tag + " has an improving long first move")
        need(counts["cases"] == counts["nonzero"] + counts["neutral"], tag + " case split")
        expected = EXPECTED[tag]
        if expected is not None:
            need(counts == expected, tag + " counts changed: " + str(counts))
        summary[tag] = counts
        if tag == WITNESS["provider"]:
            witness_invoice(R, C, word)
    print("PASS_STAGED544_TWO_NEIGHBOUR_INVOICE "
          + " ".join(f"{tag}_cases={summary[tag]['cases']}" for tag in summary)
          + f" witness_second={WITNESS['second_candidates']} improving=0 no_new_kappa")


if __name__ == "__main__":
    main()
