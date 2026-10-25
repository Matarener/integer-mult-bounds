"""Separate scalar-coefficient and raw binary-matrix residual replay.

Nick Petalas. Apache-2.0.
"""

import hashlib
import itertools
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def require(ok, message):
    if not ok:
        raise ValueError(message)


def read(name):
    path = HERE / name
    require(
        path.is_file() and not path.is_symlink() and path.stat().st_size <= 262144,
        "regular input",
    )
    return json.loads(path.read_bytes())


def bits(x, width):
    require(type(x) is int and 0 < x < 2**width, "binary vector range")
    return [(x >> j) & 1 for j in range(width)]


def pairing(x, y):
    return sum(a * b for a, b in zip(x, y, strict=True)) % 2


def eliminate(matrix):
    if not matrix:
        return 0
    rows = [r[:] for r in matrix]
    pivot = 0
    for j in range(len(rows[0])):
        candidates = [i for i in range(pivot, len(rows)) if rows[i][j]]
        if not candidates:
            continue
        i = candidates[0]
        rows[pivot], rows[i] = rows[i], rows[pivot]
        for k in range(pivot + 1, len(rows)):
            if rows[k][j]:
                rows[k] = [
                    (a + b) % 2 for a, b in zip(rows[k], rows[pivot], strict=True)
                ]
        pivot += 1
    return pivot


def prepare(row):
    width = row["ambient_dimension"]
    require(type(width) is int and 1 <= width <= 16, "ambient capacity")
    require(1 <= len(row["blocks"]) <= 8, "block capacity")
    blocks = [[bits(x, width) for x in b] for b in row["blocks"]]
    base = [v for b in blocks for v in b]
    require(
        all(1 <= len(b) <= 8 for b in blocks) and len(base) <= width, "block dimensions"
    )
    require(
        all(
            pairing(x, y) == int(i == j)
            for i, x in enumerate(base)
            for j, y in enumerate(base)
        ),
        "block orthonormality",
    )
    require(len(row["groups"]) == 3, "three groups")
    labels, group_indices, closures = [], [], []
    counts = [0] * len(blocks)
    for group in row["groups"]:
        start, used = len(labels), set()
        for part in group["parts"]:
            k = part["block"]
            require(
                type(k) is int and k in range(len(blocks)) and k not in used,
                "distinct blocks",
            )
            vectors = [bits(x, width) for x in part["basis"]]
            require(len(vectors) == len(blocks[k]), "complete basis")
            require(
                all(
                    pairing(x, y) == int(i == j)
                    for i, x in enumerate(vectors)
                    for j, y in enumerate(vectors)
                ),
                "group orthonormality",
            )
            require(eliminate(blocks[k] + vectors) == len(vectors), "block span")
            used.add(k)
            counts[k] += 1
            labels.extend(vectors)
        local = group["cells"]
        size = len(labels) - start
        require(
            1 <= size <= 16 and 1 <= len(local) <= 8 and all(local), "cell capacity"
        )
        indices = [i for c in local for i in c]
        require(
            all(type(i) is int for i in indices)
            and sorted(indices) == list(range(size)),
            "cell partition",
        )
        closures.extend(tuple(start + i for i in c) for c in local)
        group_indices.append(set(range(start, len(labels))))
    require(len(closures) <= 9 and all(counts), "covered blocks and cell capacity")
    n = [
        sum(len(b) for b, c in zip(blocks, counts, strict=True) if c == k)
        for k in (1, 2, 3)
    ]
    return labels, group_indices, closures, n


def coefficient_vectors(groups, closures, assignment, family, *, generic=False):
    length = sum(map(len, groups)) + (2 if generic else 0)
    a, b, c = ([int(i in g) for i in range(length)] for g in groups)
    representatives = {cell[0] for cell in closures}
    a, b, c = (
        [v * int(i in representatives) for i, v in enumerate(x)] for x in (a, b, c)
    )
    parameter = [((i * 7 + 3) if generic else 0) for i in range(length)]
    for cell, v in zip(closures, assignment, strict=True):
        parameter[cell[0]] = (0, 1, -1)[v] if family == "VVV" else v
    queries, readers = [[], [], [], []], [[], [], [], []]
    for x, y, z, v in zip(a, b, c, parameter, strict=True):
        if family == "VVV":
            q, u = (
                (x + y, x + z, y + z, x + y + z),
                (x + y - z - v, x - y + z - v, -x + y + z - v, 2 * v),
            )
        else:
            q, u = (
                (x + y - z, x - y + z, -x + y + z, x + y + z),
                (x + y - v, x + z - v, y + z - v, v),
            )
        for j in range(4):
            queries[j].append(q[j])
            readers[j].append(u[j])
    return (a, b, c), queries, readers


def close(vector, cells):
    return tuple(i for cell in cells if any(vector[j] for j in cell) for i in cell)


def replay(row, family):
    labels, groups, cells, n = prepare(row)
    count = 3 if family == "VVV" else 2
    bound = (n[0] if family == "VVV" else 2 * n[0]) + 3 * n[1] + 3 * n[2]
    digest, histogram, best, witness, cache = hashlib.sha256(), {}, None, None, {}
    for choice in itertools.product(range(count), repeat=len(cells)):
        _, queries, readers = coefficient_vectors(groups, cells, choice, family)
        charges = []
        for q, u in zip(queries, readers, strict=True):
            rows, columns = close(q, cells), close(u, cells)
            key = (rows, columns)
            if key not in cache:
                matrix = [
                    [pairing(labels[i], labels[j]) for j in columns] for i in rows
                ]
                cache[key] = eliminate(matrix)
            charges.append(cache[key])
        bill = sum(charges)
        require(bill >= bound, "residual floor violated")
        histogram[str(bill)] = histogram.get(str(bill), 0) + 1
        digest.update((",".join(map(str, charges)) + "\n").encode())
        if best is None or bill < best:
            best, witness = bill, list(choice)
    return {
        "assignments": count ** len(cells),
        "n": n,
        "original": n[0] + 2 * n[1] + 3 * n[2],
        "bound": bound,
        "minimum": best,
        "minimizer": witness,
        "histogram": histogram,
        "charge_stream_sha256": digest.hexdigest(),
    }


def operators(row):
    _, groups, cells, _ = prepare(row)
    checked = 0
    for family in ("VVV", "MMM"):
        targets, queries, readers = coefficient_vectors(
            groups, cells, [0] * len(cells), family, generic=True
        )
        for i in range(len(queries[0])):
            for j in range(len(queries[0])):
                expected = sum(x[i] * x[j] for x in targets)
                require(
                    sum(readers[t][i] * queries[t][j] for t in range(4))
                    == 2 * expected,
                    "integer actual operator",
                )
                checked += 1
                for prime in (3, 5, 7):
                    scales = (1, 2, 1, 2)
                    value = (
                        sum(
                            readers[t][i]
                            * pow(2 * scales[t], -1, prime)
                            * queries[t][j]
                            * scales[t]
                            for t in range(4)
                        )
                        % prime
                    )
                    require(value == expected % prime, "gauged field actual operator")
                    checked += 1
    return checked


def main():
    fixtures = read("FIXTURES.json")["fixtures"]
    require(1 <= len(fixtures) <= 12, "fixture capacity")
    require(len({r["name"] for r in fixtures}) == len(fixtures), "unique names")
    actual = {
        "schema": 1,
        "fixtures_sha256": hashlib.sha256(
            (HERE / "FIXTURES.json").read_bytes()
        ).hexdigest(),
        "results": {
            r["name"]: {f: replay(r, f) for f in ("VVV", "MMM")} for r in fixtures
        },
    }
    require(actual == read("RESULT.json"), "independent recorded result mismatch")
    total = sum(
        x["assignments"] for r in actual["results"].values() for x in r.values()
    )
    entries = sum(operators(r) for r in fixtures)
    print(
        f"PASS_INDEPENDENT_CELL_CROSSING fixtures={len(fixtures)} "
        f"assignments={total} integer_or_gauged_entries={entries}"
    )


if __name__ == "__main__":
    main()
