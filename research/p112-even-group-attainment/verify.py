"""Exact two-frame repair obstruction on the literal selected P112 labels."""

import json
from collections import Counter
from hashlib import sha1, sha256
from itertools import combinations
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
INPUT = "research/adaptive-kernel-demotion/inputs/DATA-PHASES.json"
MAX_GROUPS = 4096
MAX_UNIONS = 1_000_000


def need(condition, message):
    if not condition:
        raise ValueError(message)


def read_json(path, limit):
    need(path.stat().st_size <= limit, "input byte limit: " + str(path))
    return json.loads(path.read_bytes())


def authenticate(raw, row):
    need(sha256(raw).hexdigest() == row["sha256"], "source SHA256")
    blob = b"blob " + str(len(raw)).encode() + b"\0" + raw
    need(sha1(blob).hexdigest() == row["git_blob"], "source Git blob")


def inputs():
    meta = read_json(HERE / "SOURCES.json", 65536)
    live = [row for row in meta["files"] if row["usage"] == "input"]
    need(len(live) == 1 and live[0]["path"] == INPUT, "live input inventory")
    need((ROOT / INPUT).stat().st_size <= 1_048_576, "selected payload byte limit")
    raw = (ROOT / INPUT).read_bytes()
    authenticate(raw, live[0])
    rows = json.loads(raw)["recipes"]
    need(type(rows) is list and len(rows) == 112, "112 selected recipes")
    need(all(type(row["port"]) is int for row in rows), "integer port IDs")
    need(sorted(row["port"] for row in rows) == list(range(112)), "port inventory")
    labels = [row["q"] for row in sorted(rows, key=lambda row: row["port"])]
    need(all(type(q) is int and 0 < q < 512 for q in labels), "nine-bit labels")
    need(len(set(labels)) == 112, "distinct labels")
    need(all(q.bit_count() % 2 == 1 for q in labels), "unit label norms")
    exports = read_json(HERE / "SOURCE-EXPORT.json", 65536)
    need(len(exports["files"]) == 2, "retained certificate inventory")
    need(
        {row["local_path"] for row in exports["files"]}
        == {"PREDECESSOR13.json", "UPPER16.json"},
        "complete retained certificate names",
    )
    for row in exports["files"]:
        need(
            row["local_path"] in ("PREDECESSOR13.json", "UPPER16.json"),
            "retained certificate spelling",
        )
        path = HERE / row["local_path"]
        need(path.stat().st_size <= 65536, "retained certificate byte limit")
        authenticate(path.read_bytes(), row)
    old = read_json(HERE / "PREDECESSOR13.json", 65536)["orthonormal_groups"]
    upper = read_json(HERE / "UPPER16.json", 65536)["orthonormal_groups"]
    validate_partition(labels, old, 17)
    validate_partition(labels, upper, 16)
    need([len(g) for g in old] == [8] * 13 + [2] * 4, "predecessor shape")
    retained = sum(sorted(g) in [sorted(h) for h in old[:13]] for g in upper)
    need(retained == 11, "upper witness retains eleven source frames")
    return labels, old, upper


def validate_partition(labels, groups, count):
    need(type(groups) is list and len(groups) == count, "group count")
    need(
        all(type(g) is list and len(g) in (2, 4, 6, 8) for g in groups),
        "nonempty even group sizes",
    )
    need(all(type(v) is int for g in groups for v in g), "integer group ports")
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
        "group Gram identity",
    )


def even_groups(labels):
    n = len(labels)
    need(0 <= n <= 24, "repair domain at most 24 ports")
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
    for _ in range(1 << n):
        if not stack:
            return groups
        mask, candidates, size = stack.pop()
        if size and size % 2 == 0:
            groups.append(mask)
            need(len(groups) <= MAX_GROUPS, "even group capacity")
        if size == 8:
            continue
        for _ in range(n):
            if not candidates:
                break
            bit = candidates & -candidates
            candidates ^= bit
            vertex = bit.bit_length() - 1
            stack.append((mask | bit, candidates & adjacency[vertex], size + 1))
    need(not stack, "subset enumeration exhausted")
    return groups


def two_group_unions(groups):
    need(len(groups) <= MAX_GROUPS, "union input capacity")
    unions = {0, *groups}
    for i, group in enumerate(groups):
        for j in range(i + 1, len(groups)):
            other = groups[j]
            if group & other == 0:
                unions.add(group | other)
        need(len(unions) <= MAX_UNIONS, "two-group union capacity")
    return unions


def four_cover(labels):
    groups = even_groups(labels)
    unions = two_group_unions(groups)
    full = (1 << len(labels)) - 1
    exists = any((full ^ mask) in unions for mask in unions)
    return exists, groups, len(unions)


def run():
    labels, old, _ = inputs()
    tail = [v for group in old[13:] for v in group]
    cases = []
    for removed in combinations(range(13), 2):
        vertices = sorted(tail + [v for k in removed for v in old[k]])
        need(len(vertices) == len(set(vertices)) == 24, "complete repair domain")
        exists, groups, unions = four_cover([labels[v] for v in vertices])
        need(not exists, "fifteen-group repair found")
        cases.append(
            {
                "removed": list(removed),
                "groups": dict(sorted(Counter(g.bit_count() for g in groups).items())),
                "unions": unions,
                "four_cover_exists": exists,
            }
        )
    need(len(cases) == 78, "all predecessor frame pairs")
    return {
        "cases": cases,
        "case_count": 78,
        "minimum_groups_retaining_11": 16,
        "minimum_changed_original_frames_for_15": 3,
        "unrestricted_fifteen_group_attainment": "open",
        "no_new_kappa": True,
    }


def main():
    result = run()
    expected = read_json(HERE / "RESULT.json", 65536)
    need(json.loads(json.dumps(result)) == expected, "exact result receipt")
    print("PASS_P112_TWO_FRAME_OBSTRUCTION cases=78 minimum_groups=16 scope=retain11")


if __name__ == "__main__":
    main()
