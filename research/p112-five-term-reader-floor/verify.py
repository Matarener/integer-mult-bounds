"""Seven-point classification and five-term pair lemma. Nick Petalas. Apache-2.0."""

import itertools as it
import json
from hashlib import sha1, sha256
from pathlib import Path

HERE = Path(__file__).resolve().parent
OLD_LINES = (11, 21, 97, 38, 82, 76)


def need(condition, message):
    if not condition:
        raise ValueError(message)


def read_json(name):
    with (HERE / name).open("rb") as stream:
        raw = stream.read(131073)
    need(len(raw) <= 131072, "input capacity")
    return json.loads(raw)


def mul(a, b):
    answer = 0
    for _ in range(4):
        if b & 1:
            answer ^= a
        b >>= 1
        a <<= 1
        if a & 16:
            a ^= 19
    return answer


def rank(points):
    need(len(points) <= 7, "point capacity")
    need(all(len(p) == 3 for p in points), "point shape")
    need(all(type(x) is int and 0 <= x < 16 for p in points for x in p), "field value")
    rows = [list(p) for p in points]
    pivots = 0
    for col in range(3):
        found = next((j for j in range(pivots, len(rows)) if rows[j][col]), None)
        if found is None:
            continue
        rows[pivots], rows[found] = rows[found], rows[pivots]
        inverse = next(x for x in range(1, 16) if mul(x, rows[pivots][col]) == 1)
        rows[pivots] = [mul(x, inverse) for x in rows[pivots]]
        for j in range(len(rows)):
            if j != pivots:
                scale = rows[j][col]
                rows[j] = [
                    x ^ mul(scale, y)
                    for x, y in zip(rows[j], rows[pivots], strict=True)
                ]
        pivots += 1
    return pivots


def old_rank(mask, lines):
    if mask.bit_count() <= 1:
        return mask.bit_count()
    if mask.bit_count() == 2 or any(mask & line == mask for line in lines):
        return 2
    return 3


def canonical(lines, n):
    signatures = [
        tuple(sorted(x.bit_count() for x in lines if x >> i & 1)) for i in range(n)
    ]
    groups = [
        [i for i in range(n) if signatures[i] == s] for s in sorted(set(signatures))
    ]
    best = None
    for pieces in it.product(*(it.permutations(g) for g in groups)):
        order = tuple(i for piece in pieces for i in piece)
        new = tuple(
            sorted(
                sum(1 << j for j, i in enumerate(order) if x >> i & 1) for x in lines
            )
        )
        if best is None or new < best:
            best = new
    need(best is not None, "canonical result")
    return best


def extensions(lines, n):
    covered = {
        sum(1 << i for i in pair)
        for x in lines
        for pair in it.combinations(range(n), 2)
        if all(x >> i & 1 for i in pair)
    }
    pairs = [
        (1 << a) | (1 << b)
        for a, b in it.combinations(range(n), 2)
        if ((1 << a) | (1 << b)) not in covered
    ]
    blocks = list(lines) + pairs
    answer = {canonical(lines, n + 1)}
    for size in range(1, n // 2 + 1):
        for chosen in it.combinations(blocks, size):
            union = 0
            for block in chosen:
                union |= block
            if union.bit_count() != sum(block.bit_count() for block in chosen):
                continue
            new = [x for x in lines if x not in chosen] + [x | (1 << n) for x in chosen]
            answer.add(canonical(new, n + 1))
    return answer


def classify(data):
    types = {()}
    counts = []
    for n in range(1, 8):
        types = set().union(*(extensions(lines, n - 1) for lines in types))
        counts.append(len(types))
    need(
        counts == data["counts_by_size"] == [1, 1, 2, 3, 5, 10, 24],
        "classification counts",
    )
    rows = data["types"]
    need(len(rows) == 23, "rank-three template count")
    need(
        {tuple(row["lines"]) for row in rows} | {(127,)} == types,
        "classification coverage",
    )
    nonfano = canonical(OLD_LINES, 7)
    need(
        [tuple(row["lines"]) for row in rows if row["kind"] == "non-Fano"] == [nonfano],
        "unique exception",
    )
    subset_checks = 0
    for row in rows:
        if row["kind"] == "non-Fano":
            continue
        need(row["kind"] == "GF16", "template kind")
        points = row["points"]
        need(len(points) == 7 and rank(points) == 3, "template dimension")
        for mask in range(128):
            actual = rank([points[i] for i in range(7) if mask >> i & 1])
            need(actual == old_rank(mask, row["lines"]), "template subset rank")
            subset_checks += 1
    return counts, subset_checks


def nonfano(data):
    retained = read_json("PREDECESSOR-TEMPLATES.json")
    need(retained["polynomial"] == 7, "GF4 polynomial")
    pairs, templates = retained["representative_pairs"], retained["points"]
    need(pairs == [[0, 1], [0, 3], [3, 4]] and len(templates) == 3, "marked orbits")
    autos = [
        p
        for p in it.permutations(range(7))
        if {sum(1 << p[i] for i in range(7) if line >> i & 1) for line in OLD_LINES}
        == set(OLD_LINES)
    ]
    need(len(autos) == 24, "quadrangle automorphisms")
    counts = [0, 0]
    for a, b in it.combinations(range(7), 2):
        orbit, perm = next(
            (j, p)
            for j, pair in enumerate(pairs)
            for p in autos
            if {p[i] for i in pair} == {a, b}
        )
        points = [None] * 7
        for i in range(7):
            points[perm[i]] = [[0, 1, 6, 7][x] for x in templates[orbit][i]]
        ranks = [
            rank([points[i] for i in range(7) if mask >> i & 1]) for mask in range(128)
        ]
        need(ranks[(1 << a) | (1 << b)] == 2, "marked independence")
        queries = [i for i in range(7) if i not in (a, b)]
        for bits in range(32):
            mask = sum(1 << q for j, q in enumerate(queries) if bits >> j & 1)
            for target, other in ((a, b), (b, a)):
                base = mask | (1 << other)
                if old_rank(base | (1 << target), OLD_LINES) > old_rank(
                    base, OLD_LINES
                ):
                    need(
                        ranks[base | (1 << target)] > ranks[base], "source implication"
                    )
                    counts[0] += 1
                if old_rank(mask | (1 << target), OLD_LINES) == old_rank(
                    mask, OLD_LINES
                ):
                    need(
                        ranks[mask | (1 << target)] == ranks[mask], "reader implication"
                    )
                    counts[1] += 1
    need(counts == [288, 672], "selective premise counts")
    need(data["polynomial"] == 19 and mul(6, 6) ^ 6 ^ 1 == 0, "field embedding")
    return counts


def retained_sources():
    rows = read_json("SOURCE-CLOSURE.json")
    need(len(rows) == 2, "retained source count")
    need(
        {row["local_path"] for row in rows}
        == {"PREDECESSOR-PROOF.md", "PREDECESSOR-TEMPLATES.json"},
        "retained source names",
    )
    for row in rows:
        path = HERE / row["local_path"]
        need(path.parent == HERE and not path.is_symlink(), "retained source path")
        with path.open("rb") as stream:
            raw = stream.read(131073)
        need(len(raw) <= 131072, "retained capacity")
        need(sha256(raw).hexdigest() == row["sha256"], "retained SHA256")
        blob = b"blob " + str(len(raw)).encode() + b"\0" + raw
        need(
            sha1(blob, usedforsecurity=False).hexdigest() == row["git_blob"],
            "retained Git blob",
        )


def main():
    retained_sources()
    data = read_json("TEMPLATES.json")
    counts, subsets = classify(data)
    premises = nonfano(data)
    result = {
        "types_by_size": counts,
        "rank3_types": 23,
        "GF16_types": 22,
        "subset_ranks": subsets,
        "nonfano_pairs": 21,
        "source_premises": premises[0],
        "reader_premises": premises[1],
    }
    need(result == read_json("RESULT.json")["primary"], "result receipt")
    print("PASS_FIVE_TERM_PAIR " + json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
