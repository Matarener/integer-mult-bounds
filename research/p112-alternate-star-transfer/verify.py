"""Exact Gaussian check of the alternate shared-port transfer."""

import argparse
import hashlib
import json
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent.parent


def require(condition, message):
    if not condition:
        raise ValueError(message)


def load(path):
    require(path.is_file() and not path.is_symlink(), "regular input")
    require(path.stat().st_size <= 65536, "input capacity")
    return json.loads(path.read_text())


def mul(a, b):
    value = 0
    for _ in range(2):
        if b & 1:
            value ^= a
        b >>= 1
        a <<= 1
        if a & 4:
            a ^= 7
    return value


def rank(columns, field):
    require(len(columns) <= 9, "column capacity")
    if not columns:
        return 0
    require(all(len(c) == len(columns[0]) <= 4 for c in columns), "dimension")
    rows = [list(c) if field == 4 else list(map(Fraction, c)) for c in columns]
    count = 0
    for j in range(len(rows[0])):
        pivot = next((i for i in range(count, len(rows)) if rows[i][j]), None)
        if pivot is None:
            continue
        rows[count], rows[pivot] = rows[pivot], rows[count]
        value = rows[count][j]
        inverse = (
            next(x for x in (1, 2, 3) if mul(value, x) == 1)
            if field == 4
            else 1 / value
        )
        rows[count] = [
            mul(x, inverse) if field == 4 else x * inverse for x in rows[count]
        ]
        for i in range(count + 1, len(rows)):
            scale = rows[i][j]
            rows[i] = [
                x ^ mul(scale, y) if field == 4 else x - scale * y
                for x, y in zip(rows[i], rows[count], strict=True)
            ]
        count += 1
        if count == len(rows):
            break
    return count


def contains(columns, vector, field):
    return rank(columns, field) == rank([*columns, vector], field)


def audit(q, m, nq, nm):
    require(len(q) == len(nq) <= 6 and len(m) == len(nm) == 2, "configuration shape")
    failures = []
    for mask in range(1 << len(q)):
        old = [c for i, c in enumerate(q) if mask >> i & 1]
        new = [c for i, c in enumerate(nq) if mask >> i & 1]
        for j in (0, 1):
            if not contains([*old, m[1 - j]], m[j], 0) and contains(
                [*new, nm[1 - j]], nm[j], 4
            ):
                failures.append([mask, j, "source"])
            if contains(old, m[j], 0) and not contains(new, nm[j], 4):
                failures.append([mask, j, "reader"])
    return failures


def extremal_premises(q, m):
    result = []
    for j in (0, 1):
        readers, sources = [], []
        for mask in range(64):
            chosen = [c for i, c in enumerate(q) if mask >> i & 1]
            if contains(chosen, m[j], 0):
                readers.append(mask)
            if not contains([*chosen, m[1 - j]], m[j], 0):
                sources.append(mask)
        result.append(
            {
                "minimal_readers": [
                    a
                    for a in readers
                    if not any(b != a and b & a == b for b in readers)
                ],
                "maximal_sources": [
                    a
                    for a in sources
                    if not any(b != a and b & a == a for b in sources)
                ],
            }
        )
    return result


def identities(data):
    origin = load(data / "ORIGINS.json")["retained_pending_sources"][0]
    require(
        hashlib.sha256((data / "PREDECESSOR-WITNESS.json").read_bytes()).hexdigest()
        == origin["sha256"],
        "retained predecessor hash",
    )
    for row in load(data / "SOURCES.json")["files"]:
        if row["usage"] == "input":
            require(
                hashlib.sha256((REPO / row["path"]).read_bytes()).hexdigest()
                == row["sha256"],
                "live proof source hash",
            )


def compute(data):
    identities(data)
    old, mapped = load(data / "PREDECESSOR-WITNESS.json"), load(data / "MAP.json")
    q, nq = old["queries"], mapped["queries"]
    marks = [[1, 0, 0, 0], [0, 1, 0, 0]]
    require(
        mapped["marks"] == marks
        and mapped["gf4_polynomial"] == 7
        and mapped["parameter"] == 2,
        "map parameters",
    )
    require(len(q) == len(nq) == 6 and all(len(c) == 4 for c in q + nq), "map shape")
    require(all(type(x) is int and 0 <= x < 4 for c in nq for x in c), "map values")
    require(not audit(q, marks, nq, marks), "alternate star transfer")
    binary = [list(c) for c in nq]
    binary[0][1] = 1
    require(
        audit(q, marks, binary, marks) == [[43, 0, "reader"], [43, 1, "reader"]],
        "binary degeneration",
    )
    base = [[0, 0, 1], [1, 1, 0], [1, 0, 1], [0, 1, 1], [1, 1, 1]]
    image = [list(c) for c in base]
    image[1] = [1, 2, 0]
    short_marks = [c[:3] for c in marks]
    require(not audit(base, short_marks, image, short_marks), "new base transfer")
    reduced = [q[i][:3] for i in (0, 1, 2)] + [[0, -1, 0]]
    reduced_new = [nq[i][:3] for i in (0, 1, 2)] + [[0, 1, 0]]
    require(
        not audit(reduced, short_marks, reduced_new, short_marks), "difference transfer"
    )
    return {
        "star_subsets": 64,
        "star_implications": 256,
        "base_subsets": 32,
        "difference_subsets": 16,
        "alternate_failures": [],
        "binary_degeneracy": [[43, 0, "reader"], [43, 1, "reader"]],
        "extremal_premises": extremal_premises(q, marks),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", type=Path, default=ROOT)
    args = parser.parse_args()
    result = compute(args.data_dir)
    require(result == load(args.data_dir / "RESULT.json"), "scientific result")
    print("PASS_ALTERNATE_STAR_TRANSFER")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
