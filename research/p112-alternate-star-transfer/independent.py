"""Separate integer-minor and GF4-annihilator implementation."""

import argparse
import hashlib
import json
from itertools import combinations, permutations, product
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent.parent
TABLE = ((0, 0, 0, 0), (0, 1, 2, 3), (0, 2, 3, 1), (0, 3, 1, 2))


def need(condition, message):
    if not condition:
        raise ValueError(message)


def read(path):
    need(
        path.is_file() and not path.is_symlink() and path.stat().st_size <= 65536,
        "regular bounded input",
    )
    return json.loads(path.read_text())


def dot(a, b):
    value = 0
    for x, y in zip(a, b, strict=True):
        value ^= TABLE[x][y]
    return value


def determinant(matrix):
    size = len(matrix)
    total = 0
    for order in permutations(range(size)):
        value = (-1) ** sum(
            order[i] > order[j] for i in range(size) for j in range(i + 1, size)
        )
        for i in range(size):
            value *= matrix[i][order[i]]
        total += value
    return total


def rational_rank(columns):
    for size in range(min(4, len(columns)), 0, -1):
        for chosen in combinations(columns, size):
            for coordinates in combinations(range(4), size):
                if determinant([[c[i] for i in coordinates] for c in chosen]):
                    return size
    return 0


def old_contains(columns, mark):
    return rational_rank(columns) == rational_rank([*columns, mark])


def new_contains(columns, mark):
    for normal in product(range(4), repeat=4):
        if all(dot(normal, c) == 0 for c in columns) and dot(normal, mark):
            return False
    return True


def check(q, nq, marks):
    readers, sources, failures = [[], []], [[], []], []
    for mask in range(64):
        a = [c for i, c in enumerate(q) if mask >> i & 1]
        b = [c for i, c in enumerate(nq) if mask >> i & 1]
        for j in (0, 1):
            if old_contains(a, marks[j]):
                readers[j].append(mask)
                if not new_contains(b, marks[j]):
                    failures.append([mask, j, "reader"])
            if not old_contains([*a, marks[1 - j]], marks[j]):
                sources[j].append(mask)
                if new_contains([*b, marks[1 - j]], marks[j]):
                    failures.append([mask, j, "source"])
    extrema = [
        {
            "minimal_readers": [
                a
                for a in readers[j]
                if not any(b != a and a & b == b for b in readers[j])
            ],
            "maximal_sources": [
                a
                for a in sources[j]
                if not any(b != a and a & b == a for b in sources[j])
            ],
        }
        for j in (0, 1)
    ]
    return failures, extrema


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", type=Path, default=ROOT)
    data = parser.parse_args().data_dir
    origin = read(data / "ORIGINS.json")["retained_pending_sources"][0]
    need(
        hashlib.sha256((data / "PREDECESSOR-WITNESS.json").read_bytes()).hexdigest()
        == origin["sha256"],
        "predecessor hash",
    )
    for row in read(data / "SOURCES.json")["files"]:
        if row["usage"] == "input":
            need(
                hashlib.sha256((REPO / row["path"]).read_bytes()).hexdigest()
                == row["sha256"],
                "proof hash",
            )
    old, mapped, expected = (
        read(data / "PREDECESSOR-WITNESS.json"),
        read(data / "MAP.json"),
        read(data / "RESULT.json"),
    )
    q, nq, marks = old["queries"], mapped["queries"], mapped["marks"]
    need(
        marks == [[1, 0, 0, 0], [0, 1, 0, 0]]
        and mapped["gf4_polynomial"] == 7
        and mapped["parameter"] == 2,
        "parameters",
    )
    need(len(q) == len(nq) == 6 and all(len(c) == 4 for c in q + nq), "shape")
    need(all(type(x) is int and 0 <= x < 4 for c in nq for x in c), "field values")
    failures, extrema = check(q, nq, marks)
    need(
        not failures and extrema == expected["extremal_premises"],
        "alternate transfer and exact premises",
    )
    binary = [list(c) for c in nq]
    binary[0][1] = 1
    failures, _ = check(q, binary, marks)
    need(
        failures
        == expected["binary_degeneracy"]
        == [[43, 0, "reader"], [43, 1, "reader"]],
        "binary degeneration",
    )
    print("PASS_INDEPENDENT_ALTERNATE_STAR")
    print(
        json.dumps(
            {
                "star_subsets": 64,
                "alternate_failures": [],
                "extremal_premises": extrema,
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
