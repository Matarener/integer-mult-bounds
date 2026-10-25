#!/usr/bin/env python3
"""Exact mixed pair-query tariff census. @CubeJerry, Codex-assisted; Apache-2.0."""

import argparse
from collections import Counter
from hashlib import sha1, sha256
from itertools import combinations
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
INPUT = "research/adaptive-kernel-demotion/inputs/DATA-PHASES.json"


def need(ok, message):
    if not ok:
        raise ValueError(message)


def authenticate(raw, pin):
    need(sha256(raw).hexdigest() == pin["sha256"], "source SHA256 mismatch")
    need(sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
         == pin["git_blob"], "source Git blob mismatch")


def load(root=ROOT, here=HERE):
    sources = json.loads((here / "SOURCES.json").read_text())
    pins = [p for p in sources["files"] if p["usage"] == "input"]
    need(len(pins) == 1 and pins[0]["path"] == INPUT, "input inventory")
    raw = (root / INPUT).read_bytes()
    authenticate(raw, pins[0])
    rows = json.loads(raw)["recipes"]
    need(sorted(r["port"] for r in rows) == list(range(112)), "port inventory")
    labels = [r["q"] for r in sorted(rows, key=lambda r: r["port"])]
    raw = (here / "RETAINED-RANK32.json").read_bytes()
    authenticate(raw, sources["retained_rank32"])
    groups = json.loads(raw)["orthonormal_groups"]
    validate_geometry(labels, groups)
    return labels, groups


def validate_geometry(labels, groups):
    need(len(labels) == 112 and len(set(labels)) == 112, "distinct labels")
    need(all(type(x) is int and 0 < x < 512 for x in labels), "nine-bit labels")
    need(len(groups) == 16 and sorted(map(len, groups)) == [4]*3+[6]*2+[8]*11,
         "group sizes")
    need(sorted(p for g in groups for p in g) == list(range(112)), "partition")
    for g in groups:
        need(all((labels[p] & labels[q]).bit_count() % 2 == (p == q)
                 for p in g for q in g), "orthonormal group")


def rank(columns):
    pivots = {}
    for value in columns:
        while value:
            bit = value.bit_length() - 1
            if bit in pivots:
                value ^= pivots[bit]
            else:
                pivots[bit] = value
                break
    return len(pivots)


def costs(labels, source, planes):
    blocks = [[sum(((labels[p] & labels[q]).bit_count() & 1) << i
                   for i, p in enumerate(source)) for q in plane]
              for plane in planes]
    return [rank(v for j, block in enumerate(blocks) if mask >> j & 1 for v in block)
            for mask in range(1 << len(planes))]


def masks(state, k, na):
    """Ternary digits: 0 correct axis, 1 wrong axis, 2 neither axis."""
    a = b = level1 = level2 = 0
    for i in range(k):
        state, digit = divmod(state, 3)
        bit = 1 << i
        if digit:
            level1 |= bit
        if digit == 2:
            level2 |= bit
        elif (i < na) == (digit == 0):
            a |= bit
        else:
            b |= bit
    return a, b, level1, level2


def pair_census(labels, ga, gb, indices):
    planes = [g[j:j+2] for g in (ga, gb) for j in range(0, len(g), 2)]
    k, na = len(planes), len(ga)//2
    ca, cb, cd = [costs(labels, source, planes) for source in (ga, gb, ga+gb)]
    floor = len(ga) + len(gb)
    histogram = Counter()
    equal = 0
    first_equal_mixed = None
    for state in range(3**k):
        a, b, s1, s2 = masks(state, k, na)
        bill = ca[a] + cb[b] + cd[s1] + cd[s2]
        need(bill >= floor, f"pair floor failed: {indices}, state {state}, bill {bill}")
        histogram[bill-floor] += 1
        if bill == floor:
            equal += 1
            if s2 and a and b and first_equal_mixed is None:
                first_equal_mixed = state
    need(ca[(1 << na)-1] + cb[((1 << k)-1)^((1 << na)-1)] == floor,
         "literal axis attainment")
    need(equal > 0, "sharp minimum")
    return {"groups": list(indices), "sizes": [len(ga), len(gb)],
            "states": 3**k, "minimum": floor, "equality_states": equal,
            "first_equal_four_direction_state": first_equal_mixed,
            "gap_histogram": {str(gap): count for gap, count in sorted(histogram.items())},
            "rank_tables_sha256": sha256(json.dumps([ca, cb, cd], separators=(",", ":")).encode()).hexdigest()}


def check_operator(labels, groups, ga_index, gb_index, state, parity=(0, 0), outside=False):
    """Actual four-direction rational fixture; checks every 112x112 entry."""
    ga, gb = groups[ga_index], groups[gb_index]
    a, b = ga[parity[0]::2], gb[parity[1]::2]
    target = a+b
    na = len(a)
    supports = masks(state, len(target), na)
    directions = [(1, 0), (0, 1), (1, 1), (1, 2)]
    readers = [[0]*112 for _ in directions]
    remaining = state
    for i, port in enumerate(target):
        remaining, digit = divmod(remaining, 3)
        axis = int(i >= na)
        if digit == 0:
            readers[axis][port] = 1
        elif digit == 1:
            readers[1-axis][port] = -1
            readers[2][port] = 1
        else:
            readers[2][port] = 2 if axis == 0 else -1
            readers[3][port] = -1 if axis == 0 else 1
    if outside:
        port = next(p for p in range(112) if p not in target)
        # q0 + q1 - q2 = 0 outside the target; deleting this row preserves the map.
        for i, value in enumerate((1, 1, -1)):
            readers[i][port] = value
    av, bv = [int(p in a) for p in range(112)], [int(p in b) for p in range(112)]
    queries = [[x*av[p]+y*bv[p] for p in range(112)] for x, y in directions]
    for p in range(112):
        for q in range(112):
            need(sum(readers[i][p]*queries[i][q] for i in range(4))
                 == av[p]*av[q]+bv[p]*bv[q], "four-direction operator identity")
    owners = {p: g[j:j+2] for g in groups for j in range(0, len(g), 2) for p in g[j:j+2]}
    def closure(vector):
        return sorted({v for p, coefficient in enumerate(vector) if coefficient for v in owners[p]})
    invoice = []
    for u, q in zip(readers, queries):
        source, reader = closure(q), closure(u)
        invoice.append(rank(sum(((labels[p]&labels[t]).bit_count() & 1) << j
                                for j, p in enumerate(source)) for t in reader))
    need(sum(invoice) >= len(ga)+len(gb), "actual fixture invoice")
    if not outside:
        planes = [g[j:j+2] for g in (ga, gb) for j in range(0, len(g), 2)]
        tables = [costs(labels, source, planes) for source in (ga, gb, ga+gb, ga+gb)]
        need(invoice == [table[mask] for table, mask in zip(tables, supports)],
             "normal-form invoice agrees with actual supports")
    return invoice


def receipt(labels, groups):
    pairs = [pair_census(labels, groups[i], groups[j], (i, j))
             for i, j in combinations(range(16), 2)]
    # Seed 25 fixes only the fixture traversal, never the exhaustive census.
    fixtures = 0
    for number, pair in enumerate(pairs):
        i, j = pair["groups"]
        state = (25*104729 + number*7919) % pair["states"]
        check_operator(labels, groups, i, j, state,
                       parity=(number % 2, (number//2) % 2), outside=number % 3 == 0)
        fixtures += 1
    return {"schema_version": 1, "result": "sharp mixed-pair actual-reader floor",
            "field_scope": "every field; coefficient arithmetic is not reduced modulo two",
            "distinct_group_pairs": 120, "indicator_pairs_covered": 496,
            "ternary_states": sum(p["states"] for p in pairs),
            "same_group_pairs": 16, "same_group_argument": "two directions per plane",
            "literal_total_tariff": 2*sum(map(len, groups)),
            "rational_operator_fixtures": fixtures,
            "operator_entries_checked": fixtures*112*112,
            "pairs": pairs}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--write-receipt", action="store_true")
    args = parser.parse_args()
    labels, groups = load(args.root)
    result = receipt(labels, groups)
    path = HERE / "RESULT.json"
    if args.write_receipt:
        path.write_text(json.dumps(result, indent=2)+"\n")
    else:
        need(json.loads(path.read_text()) == result, "complete receipt mismatch")
    print(f"PASS_MIXED_QUERY_READER_FLOOR pairs=496 states={result['ternary_states']} tariff=224")


if __name__ == "__main__":
    main()
