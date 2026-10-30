"""Source-bound exact cover check of the 286 three-frame P112 repairs."""

import argparse
import json
from collections import Counter
from hashlib import sha1, sha256
from itertools import combinations
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
INPUT = "research/adaptive-kernel-demotion/inputs/DATA-PHASES.json"
MAX_GROUPS = 8192
MAX_STATES = 1_000_000
MAX_STACK = 100_000


def need(condition, message):
    if not condition:
        raise ValueError(message)


def read_json(path, limit=1_048_576):
    need(path.is_file() and path.stat().st_size <= limit, "file size or existence")
    return json.loads(path.read_bytes())


def authenticate(raw, pin):
    need(sha256(raw).hexdigest() == pin["sha256"], "source SHA256")
    blob = b"blob " + str(len(raw)).encode() + b"\0" + raw
    need(sha1(blob).hexdigest() == pin["git_blob"], "source Git blob")


def partition(labels, groups, count):
    need(type(groups) is list and len(groups) == count, "partition group count")
    need(
        all(type(g) is list and len(g) in (2, 4, 6, 8) for g in groups),
        "nonempty even group sizes",
    )
    need(all(type(v) is int for g in groups for v in g), "integer ports")
    need(
        sorted(v for g in groups for v in g) == list(range(112)),
        "complete disjoint port partition",
    )
    need(
        all(
            (labels[i] & labels[j]).bit_count() % 2 == int(i == j)
            for g in groups
            for i in g
            for j in g
        ),
        "partition Gram identity",
    )


def inputs():
    meta = read_json(HERE / "SOURCES.json", 65536)
    pins = [row for row in meta["files"] if row["usage"] == "input"]
    need(len(pins) == 1 and pins[0]["path"] == INPUT, "live input inventory")
    rows = read_json(ROOT / INPUT)["recipes"]
    authenticate((ROOT / INPUT).read_bytes(), pins[0])
    need(type(rows) is list and len(rows) == 112, "112 selected recipes")
    need(all(type(row["port"]) is int for row in rows), "integer source ports")
    need(sorted(row["port"] for row in rows) == list(range(112)), "source ports")
    labels = [row["q"] for row in sorted(rows, key=lambda row: row["port"])]
    need(
        all(type(q) is int and 0 < q < 512 and q.bit_count() % 2 for q in labels),
        "unit nine-bit labels",
    )
    need(len(set(labels)) == 112, "distinct selected labels")
    exports = read_json(HERE / "SOURCE-EXPORT.json", 65536)["files"]
    need(
        len(exports) == 2
        and {row["local_path"] for row in exports}
        == {"PREDECESSOR13.json", "UPPER16.json"},
        "retained source inventory",
    )
    for row in exports:
        raw = (HERE / row["local_path"]).read_bytes()
        need(len(raw) <= 65536, "retained source size")
        authenticate(raw, row)
    old = read_json(HERE / "PREDECESSOR13.json", 65536)["orthonormal_groups"]
    upper = read_json(HERE / "UPPER16.json", 65536)["orthonormal_groups"]
    partition(labels, old, 17)
    partition(labels, upper, 16)
    need([len(g) for g in old] == [8] * 13 + [2] * 4, "predecessor shape")
    retained = sum(sorted(g) in [sorted(h) for h in old[:13]] for g in upper)
    need(retained >= 10, "upper witness retains at least ten originals")
    return labels, old, upper


def even_groups(labels):
    n = len(labels)
    need(0 <= n <= 32, "at most 32 repair labels")
    need(
        all(type(q) is int and 0 < q < 512 and q.bit_count() % 2 for q in labels),
        "unit nine-bit repair labels",
    )
    need(len(set(labels)) == n, "distinct repair labels")
    adjacency = [
        sum(
            1 << j
            for j in range(i + 1, n)
            if (labels[i] & labels[j]).bit_count() % 2 == 0
        )
        for i in range(n)
    ]
    groups = []
    stack = [(0, (1 << n) - 1, 0)]
    for _ in range(MAX_STATES):
        if not stack:
            return groups
        mask, candidates, size = stack.pop()
        if size and size % 2 == 0:
            groups.append(mask)
            need(len(groups) <= MAX_GROUPS, "group capacity exhausted")
        if size == 8:
            continue
        for _ in range(n):
            if not candidates:
                break
            bit = candidates & -candidates
            candidates ^= bit
            vertex = bit.bit_length() - 1
            stack.append((mask | bit, candidates & adjacency[vertex], size + 1))
        need(len(stack) <= MAX_STACK, "enumeration stack capacity exhausted")
    raise ValueError("group enumeration budget exhausted")


def cover_index(groups, n):
    need(
        len(groups) <= MAX_GROUPS and len(set(groups)) == len(groups),
        "distinct bounded group inventory",
    )
    need(
        all(
            type(g) is int and 0 < g < 1 << n and g.bit_count() in (2, 4, 6, 8)
            for g in groups
        ),
        "legal group masks",
    )
    by_vertex = [0] * n
    by_min_size = [0] * 9
    for k, group in enumerate(groups):
        for j in range(n):
            if group >> j & 1:
                by_vertex[j] |= 1 << k
        for size in range(9):
            if group.bit_count() >= size:
                by_min_size[size] |= 1 << k
    conflicts = []
    for group in groups:
        mask = 0
        for j in range(n):
            if group >> j & 1:
                mask |= by_vertex[j]
        conflicts.append(mask)
    return by_vertex, by_min_size, conflicts


def choices(rem, available, by_vertex):
    best, count = 0, MAX_GROUPS + 1
    for j, rows in enumerate(by_vertex):
        if rem >> j & 1:
            hits = rows & available
            if hits.bit_count() < count:
                best, count = hits, hits.bit_count()
            if count == 0:
                break
    return best


def cover(groups, n, slots, budget=MAX_STATES):
    need(type(n) is int and 0 <= n <= 32, "cover width")
    need(type(slots) is int and 0 <= slots <= 16, "cover slots")
    need(type(budget) is int and 1 <= budget <= MAX_STATES, "cover budget")
    by_vertex, by_min_size, conflicts = cover_index(groups, n)
    stack = [((1 << n) - 1, (1 << len(groups)) - 1, slots)]
    seen = set()
    nodes = 0
    for _ in range(budget):
        if not stack:
            return False, nodes, len(seen)
        rem, available, left = stack.pop()
        nodes += 1
        if not rem:
            return True, nodes, len(seen)
        if left == 0 or rem.bit_count() > 8 * left:
            continue
        key = rem, left
        if key in seen:
            continue
        seen.add(key)
        minimum = max(2, rem.bit_count() - 8 * (left - 1))
        available &= by_min_size[minimum]
        options = choices(rem, available, by_vertex)
        for _ in range(MAX_GROUPS):
            if not options:
                break
            bit = options & -options
            options ^= bit
            k = bit.bit_length() - 1
            stack.append((rem ^ groups[k], available & ~conflicts[k], left - 1))
        need(len(stack) <= MAX_STACK, "cover stack capacity exhausted")
    raise ValueError("cover search budget exhausted")


def run():
    labels, old, _ = inputs()
    tail = [v for group in old[13:] for v in group]
    cases = []
    for removed in combinations(range(13), 3):
        vertices = sorted(tail + [v for k in removed for v in old[k]])
        need(len(vertices) == len(set(vertices)) == 32, "complete repair domain")
        groups = even_groups([labels[v] for v in vertices])
        exists, nodes, states = cover(groups, 32, 5)
        need(not exists, "fifteen-group repair exists")
        cases.append(
            {
                "removed": list(removed),
                "group_sizes": dict(
                    sorted(Counter(g.bit_count() for g in groups).items())
                ),
                "group_masks_sha256": sha256(
                    json.dumps(sorted(groups)).encode()
                ).hexdigest(),
                "nodes": nodes,
                "states": states,
                "five_cover_exists": exists,
            }
        )
    need(len(cases) == 286, "all predecessor frame triples")
    return {
        "cases": cases,
        "case_count": 286,
        "minimum_groups_retaining_10": 16,
        "minimum_changed_original_frames_for_15": 4,
        "unrestricted_fifteen_group_attainment": "open",
        "no_new_kappa": True,
    }


def write_receipt(path, result):
    fields = []
    for key, value in result.items():
        if key == "cases":
            rows = ("    " + json.dumps(row, sort_keys=True) for row in value)
            encoded = "[\n" + ",\n".join(rows) + "\n  ]"
        else:
            encoded = json.dumps(value)
        fields.append("  " + json.dumps(key) + ": " + encoded)
    path.write_text("{\n" + ",\n".join(fields) + "\n}\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    result = run()
    canonical = json.loads(json.dumps(result))
    if args.write:
        write_receipt(HERE / "RESULT.json", result)
    else:
        need(
            read_json(HERE / "RESULT.json") == canonical,
            "complete result receipt mismatch",
        )
    print("PASS_P112_THREE_FRAME_PRIMARY cases=286 retain10_min=16 global15=open")


if __name__ == "__main__":
    main()
