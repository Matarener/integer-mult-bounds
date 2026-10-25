"""Separate explicit-coordinate enumeration and remaining-mask cover search.

This module deliberately imports no production verifier code.
"""

import argparse
import json
from hashlib import sha256
from itertools import combinations
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
LIMIT = 1_000_000


def check(value, message):
    if not value:
        raise ValueError(message)


def group_masks(vectors):
    n = len(vectors)
    check(0 <= n <= 32 and all(len(v) == 9 for v in vectors), "vector shape")
    check(all(x in (0, 1) for v in vectors for x in v), "binary coordinates")
    check(all(sum(x * x for x in v) % 2 == 1 for v in vectors), "unit vectors")
    check(len({tuple(v) for v in vectors}) == n, "distinct vectors")
    orthogonal = [
        [sum(a * b for a, b in zip(x, y, strict=True)) % 2 == 0 for y in vectors]
        for x in vectors
    ]
    stack = [((), tuple(range(n)))]
    result = []
    for _ in range(LIMIT):
        if not stack:
            return result
        chosen, candidates = stack.pop()
        if chosen and len(chosen) % 2 == 0:
            result.append(sum(1 << j for j in chosen))
            check(len(result) <= 8192, "independent group capacity")
        if len(chosen) < 8:
            for k, vertex in enumerate(candidates):
                remaining = tuple(
                    j for j in candidates[k + 1 :] if orthogonal[vertex][j]
                )
                stack.append(((*chosen, vertex), remaining))
        check(len(stack) <= 100_000, "independent enumeration stack")
    raise ValueError("independent enumeration exhausted")


def cover_masks(groups, n, slots, budget=LIMIT):
    check(
        0 <= n <= 32 and 0 <= slots <= 16 and 1 <= budget <= LIMIT,
        "independent search boundary",
    )
    check(len(groups) <= 8192 and len(set(groups)) == len(groups), "group count")
    check(
        all(0 < g < 1 << n and g.bit_count() in (2, 4, 6, 8) for g in groups),
        "independent mask boundary",
    )
    group_set = set(groups)
    by_vertex = [[g for g in groups if g >> i & 1] for i in range(n)]
    order = sorted(range(n), key=lambda i: len(by_vertex[i]))
    work = [((1 << n) - 1, slots)]
    seen = set()
    nodes = 0
    for _ in range(budget):
        if not work:
            return False, nodes, len(seen)
        remaining, left = work.pop()
        nodes += 1
        if remaining == 0:
            return True, nodes, len(seen)
        if left == 0 or remaining.bit_count() > 8 * left:
            continue
        if remaining in group_set:
            return True, nodes, len(seen)
        if left == 1 or (remaining, left) in seen:
            continue
        seen.add((remaining, left))
        vertex = next(i for i in order if remaining >> i & 1)
        minimum = remaining.bit_count() - 8 * (left - 1)
        for group in by_vertex[vertex]:
            if group & remaining == group and group.bit_count() >= minimum:
                rest = remaining ^ group
                if left == 2:
                    if rest in group_set:
                        return True, nodes, len(seen)
                else:
                    work.append((rest, left - 1))
        check(len(work) <= 100_000, "independent search stack")
    raise ValueError("independent search exhausted")


def run():
    primary = json.loads((HERE / "RESULT.json").read_bytes())
    check(
        len(primary["cases"]) == primary["case_count"] == 286, "primary case inventory"
    )
    rows = json.loads(
        (
            ROOT / "research/adaptive-kernel-demotion/inputs/DATA-PHASES.json"
        ).read_bytes()
    )["recipes"]
    check(
        len(rows) == 112 and sorted(r["port"] for r in rows) == list(range(112)),
        "independent source ports",
    )
    vectors = [
        [r["q"] >> j & 1 for j in range(9)]
        for r in sorted(rows, key=lambda r: r["port"])
    ]
    old = json.loads((HERE / "PREDECESSOR13.json").read_bytes())["orthonormal_groups"]
    check([len(g) for g in old] == [8] * 13 + [2] * 4, "independent old shape")
    check(
        sorted(v for g in old for v in g) == list(range(112)), "independent partition"
    )
    tail = [v for g in old[13:] for v in g]
    receipt = []
    for index, removed in enumerate(combinations(range(13), 3)):
        ports = sorted(tail + [v for i in removed for v in old[i]])
        groups = group_masks([vectors[v] for v in ports])
        reference = primary["cases"][index]
        check(reference["removed"] == list(removed), "case order")
        digest = sha256(json.dumps(sorted(groups)).encode()).hexdigest()
        check(
            digest == reference["group_masks_sha256"], "complete group census differs"
        )
        exists, nodes, states = cover_masks(groups, 32, 5)
        check(
            not exists and reference["five_cover_exists"] is False,
            "independent repair found",
        )
        receipt.append({"removed": list(removed), "nodes": nodes, "states": states})
    return {"cases": receipt, "case_count": 286, "five_cover_exists": False}


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
    if args.write:
        write_receipt(HERE / "INDEPENDENT.json", result)
    else:
        expected = json.loads((HERE / "INDEPENDENT.json").read_bytes())
        check(result == expected, "independent full receipt mismatch")
    print("PASS_P112_THREE_FRAME_INDEPENDENT cases=286 five_cover=false")


if __name__ == "__main__":
    main()
