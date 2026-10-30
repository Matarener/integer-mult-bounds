"""Four-term literal triple floor. Nick Petalas. Apache-2.0."""

import argparse
import hashlib
import itertools as it
import json
from collections import Counter
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).absolute().parent
ROOT = HERE.parents[1]
PREFIX = "research/"
AFFINE = PREFIX + "p112-nonfano-affine-reader/"
CLASSIFY = PREFIX + "p112-five-term-reader-floor/"
DATA = PREFIX + "adaptive-kernel-demotion/inputs/DATA-PHASES.json"
POINTS = ((1, 0, 0), (0, 1, 0), (0, 0, 1), (1, 1, 0), (1, 0, 1), (0, 1, 1), (1, 1, 1))
LINES = (11, 21, 97, 38, 82, 76)
MARKS = ((0, 1, 2), (0, 1, 4), (0, 3, 4), (3, 4, 5))
TRANSFERS = {
    (0, 1, 4): ((1, 0, 1), (1, 1, 0), (1, 1, 1), (0, 1, 1)),
    (0, 3, 4): ((1, 1, 0), (1, 0, 1), (0, 1, 1), (1, 1, 1)),
}


def need(condition, message):
    if not condition:
        raise ValueError(message)


def unique_object(pairs):
    answer = {}
    for key, value in pairs:
        need(key not in answer, "duplicate JSON key")
        answer[key] = value
    return answer


def read_json(path):
    need(path.absolute() == path.resolve() and path.is_file(), "regular source path")
    with path.open("rb") as stream:
        raw = stream.read(1048577)
    need(len(raw) <= 1048576, "source capacity")
    return json.loads(raw, object_pairs_hook=unique_object)


def authenticate():
    manifest = read_json(HERE / "SOURCES.json")
    rows = [r for r in manifest["files"] if r["usage"] == "input"]
    need(len(rows) == 9 and len({r["path"] for r in rows}) == 9, "source closure")
    for row in rows:
        path = ROOT / row["path"]
        need(
            path.is_relative_to(ROOT)
            and path.absolute() == path.resolve()
            and path.is_file(),
            "source alias",
        )
        with path.open("rb") as stream:
            raw = stream.read(1048577)
        need(len(raw) <= 1048576, "source capacity")
        need(hashlib.sha256(raw).hexdigest() == row["sha256"], "source drift")
    return rows


def field_mul(a, b):
    answer = 0
    for _ in range(4):
        if b & 1:
            answer ^= a
        a, b = a << 1, b >> 1
        if a & 16:
            a ^= 19
    return answer


def rank16(columns):
    need(len(columns) <= 7 and all(len(c) == 3 for c in columns), "rank shape")
    need(
        all(type(x) is int and 0 <= x < 16 for c in columns for x in c), "field domain"
    )
    rows = [list(c) for c in columns]
    count = 0
    for col in range(3):
        pivot = next((i for i in range(count, len(rows)) if rows[i][col]), None)
        if pivot is None:
            continue
        rows[count], rows[pivot] = rows[pivot], rows[count]
        inv = next(x for x in range(1, 16) if field_mul(x, rows[count][col]) == 1)
        rows[count] = [field_mul(x, inv) for x in rows[count]]
        for i in range(len(rows)):
            if i != count:
                scale = rows[i][col]
                rows[i] = [
                    a ^ field_mul(scale, b)
                    for a, b in zip(rows[i], rows[count], strict=True)
                ]
        count += 1
    return count


def incidence_rank(mask, lines=LINES):
    if mask.bit_count() <= 1:
        return mask.bit_count()
    if mask.bit_count() == 2 or any(mask & line == mask for line in lines):
        return 2
    return 3


def normalized(marks, query):
    rows = [
        [Fraction(POINTS[marks[j]][i]) for j in range(3)] + [Fraction(POINTS[query][i])]
        for i in range(3)
    ]
    for col in range(3):
        pivot = next(i for i in range(col, 3) if rows[i][col])
        rows[col], rows[pivot] = rows[pivot], rows[col]
        scale = rows[col][col]
        rows[col] = [x / scale for x in rows[col]]
        for i in range(3):
            if i != col:
                scale = rows[i][col]
                rows[i] = [
                    a - scale * b for a, b in zip(rows[i], rows[col], strict=True)
                ]
    return tuple(row[3] for row in rows)


def marked_classes():
    autos = [
        p
        for p in it.permutations(range(7))
        if {sum(1 << p[i] for i in range(7) if line >> i & 1) for line in LINES}
        == set(LINES)
    ]
    need(len(autos) == 24, "automorphism group")
    orbits = [{tuple(sorted(p[i] for i in mark)) for p in autos} for mark in MARKS]
    independent = {
        m
        for m in it.combinations(range(7), 3)
        if incidence_rank(sum(1 << i for i in m)) == 3
    }
    need([len(o) for o in orbits] == [4, 12, 12, 1], "marked orbit sizes")
    need(
        set.union(*orbits) == independent and sum(map(len, orbits)) == 29,
        "independent marked triple coverage",
    )
    checks, rows = 0, []
    for marks, new in TRANSFERS.items():
        queries = [i for i in range(7) if i not in marks]
        old = [normalized(marks, q) for q in queries]
        need(
            all(
                all(not x or y for x, y in zip(n, o, strict=True))
                for n, o in zip(new, old, strict=True)
            ),
            "source support inclusion",
        )
        true_requests = 0
        for bits in range(16):
            selected = [new[i] for i in range(4) if bits >> i & 1]
            mask = sum(1 << q for i, q in enumerate(queries) if bits >> i & 1)
            for j, target in enumerate(marks):
                if incidence_rank(mask | (1 << target)) == incidence_rank(mask):
                    need(
                        rank16([*selected, POINTS[j]]) == rank16(selected),
                        "reader span implication",
                    )
                    true_requests += 1
                checks += 1
        rows.append(
            {
                "marks": list(marks),
                "queries": queries,
                "old": [[str(x) for x in c] for c in old],
                "new": [list(c) for c in new],
                "true_reader_requests": true_requests,
            }
        )
    return {
        "automorphisms": 24,
        "independent_triples": 29,
        "orbit_sizes": [4, 12, 12, 1],
        "candidate_reader_requests": checks,
        "binary_transfers": rows,
    }


def inherited_templates():
    data = read_json(ROOT / (CLASSIFY + "TEMPLATES.json"))
    need(data["polynomial"] == 19 and len(data["types"]) == 23, "template inventory")
    checked = 0
    for row in data["types"]:
        if row["kind"] == "non-Fano":
            continue
        need(row["kind"] == "GF16" and len(row["points"]) == 7, "template type")
        for mask in range(128):
            columns = [row["points"][i] for i in range(7) if mask >> i & 1]
            need(
                rank16(columns) == incidence_rank(mask, row["lines"]),
                "inherited full-subset representation",
            )
            checked += 1
    need(checked == 2816, "template check coverage")
    affine = read_json(ROOT / (AFFINE + "RESULT.json"))
    need(len(affine["classes"]) == 800 and affine["triples"] == 4960, "VVV coverage")
    need(all(r["minimum"] >= r["original"] for r in affine["classes"]), "VVV floor")
    return {
        "represented_subset_ranks": checked,
        "VVV_stream_sha256": affine["stream_sha256"],
        "VVV_replayed_states": affine["evaluated_states"],
    }


def binary_basis(values):
    pivots = [0] * 9
    for value in values:
        need(type(value) is int and 0 <= value < 512, "binary label value")
        for bit in range(8, -1, -1):
            if value >> bit & 1:
                if pivots[bit]:
                    value ^= pivots[bit]
                else:
                    pivots[bit] = value
                    break
    return tuple(x for x in pivots if x)


def geometry():
    data = read_json(ROOT / DATA)
    retained = read_json(ROOT / (AFFINE + "RETAINED-RANK32.json"))
    need([r["port"] for r in data["recipes"]] == list(range(112)), "port order")
    labels = tuple(r["q"] for r in data["recipes"])
    groups = retained["orthonormal_groups"]
    need(
        len(groups) == 16 and sorted(p for g in groups for p in g) == list(range(112)),
        "literal partition",
    )
    planes, targets, sizes = [()] * 112, [], []
    for group in groups:
        need(0 < len(group) <= 8 and len(group) % 2 == 0, "even group")
        need(
            all(
                (labels[p] & labels[q]).bit_count() % 2 == int(p == q)
                for p in group
                for q in group
            ),
            "Gram-I group",
        )
        for i in range(0, len(group), 2):
            for p in group[i : i + 2]:
                planes[p] = tuple(group[i : i + 2])
        for side in range(2):
            targets.append(tuple(group[side::2]))
            sizes.append(len(group))
    return labels, planes, targets, sizes


def dense_costs(triple, labels, planes, targets):
    ports = sum((targets[t] for t in triple), ())
    need(len(ports) <= 12 and len(set(ports)) == len(ports), "port capacity")
    source = binary_basis([labels[p] for t in ports for p in planes[t]])
    columns = [
        tuple(
            sum(((v & labels[p]).bit_count() % 2) << j for j, v in enumerate(source))
            for p in planes[t]
        )
        for t in ports
    ]
    bases, costs = [()], [0] * (1 << len(ports))
    for mask in range(1, len(costs)):
        bit = mask & -mask
        new = binary_basis((*bases[mask ^ bit], *columns[bit.bit_length() - 1]))
        bases.append(new)
        costs[mask] = len(new)
    return costs


def solve(triple, labels, planes, targets, sizes):
    costs = dense_costs(triple, labels, planes, targets)
    lengths = [len(targets[t]) for t in triple]
    a, b, c = [((1 << n) - 1) << sum(lengths[:j]) for j, n in enumerate(lengths)]
    best, witness = 100, -1
    for w in range(len(costs)):
        bill = costs[(a | b) ^ w] + costs[(a | c) ^ w] + costs[(b | c) ^ w] + costs[w]
        if bill < best:
            best, witness = bill, w
    original = sum(sizes[t] for t in triple)
    need(best >= original and witness >= 0, "MMM literal floor")
    return {
        "targets": list(triple),
        "original": original,
        "minimum": best,
        "states": len(costs),
        "w_bits": witness,
    }


def canonical(triple):
    groups = [t // 2 for t in triple]
    return tuple(
        2 * g + int(i > 0 and groups[i - 1] == g) for i, g in enumerate(groups)
    )


def summarize(records):
    cache = {tuple(r["targets"]): r for r in records}
    need(len(cache) == 800, "dense class coverage")
    stream, histogram, states, equalities = hashlib.sha256(), Counter(), 0, []
    for triple in it.combinations(range(32), 3):
        r = cache[canonical(triple)]
        row = [*triple, r["original"], r["minimum"], r["w_bits"]]
        stream.update((json.dumps(row, separators=(",", ":")) + "\n").encode())
        histogram[r["minimum"] - r["original"]] += 1
        states += r["states"]
        if r["minimum"] == r["original"]:
            equalities.append(list(triple))
    return {
        "triples": 4960,
        "classes": records,
        "evaluated_states": sum(r["states"] for r in records),
        "expanded_states": states,
        "stream_sha256": stream.hexdigest(),
        "minimum_excess_histogram": {str(k): v for k, v in sorted(histogram.items())},
        "equalities": equalities,
    }


def identity_controls():
    # Include duplicated target types and a spectator with cancelling readers.
    axes = ((1, 0, 0), (1, 0, 0), (0, 1, 0), (0, 0, 1), (0, 0, 0))
    queries = [(a + b - c, a - b + c, -a + b + c, a + b + c) for a, b, c in axes]
    count = 0
    for i, (a, b, c) in enumerate(axes):
        for w in (0, 1, -1, 2, 7):
            readers2 = (a + b - 2 * w, a + c - 2 * w, b + c - 2 * w, 2 * w)
            for j, q in enumerate(queries):
                need(
                    sum(x * y for x, y in zip(readers2, q, strict=True))
                    == 2 * sum(x * y for x, y in zip(axes[i], axes[j], strict=True)),
                    "dense affine operator identity",
                )
                count += 1
    return count


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    authenticate()
    labels, planes, targets, sizes = geometry()
    triples = sorted({canonical(t) for t in it.combinations(range(32), 3)})
    result = {
        "marked_classification": marked_classes(),
        "inherited": inherited_templates(),
        "identity_checks": identity_controls(),
        "MMM": summarize([solve(t, labels, planes, targets, sizes) for t in triples]),
    }
    if args.write:
        (HERE / "RESULT.json").write_text(json.dumps(result, indent=2) + "\n")
    else:
        need(result == read_json(HERE / "RESULT.json"), "result mismatch")
    small = dict(result["MMM"])
    del small["classes"]
    del small["equalities"]
    print("PASS_P112_FOUR_TERM_TRIPLE", json.dumps(small, sort_keys=True))


if __name__ == "__main__":
    main()
