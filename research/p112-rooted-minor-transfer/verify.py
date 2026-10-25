"""Exact bounded quotient checks for terminal-rooted K3,2 certificates."""

import hashlib
import json
import math
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PAIRS = ((0, 3), (3, 1), (3, 2), (0, 4), (4, 1), (4, 2))


def require(condition, message):
    if not condition:
        raise ValueError(message)


def load(name):
    path = ROOT / name
    require(path.stat().st_size <= 1_000_000, "input exceeds byte bound")
    return json.loads(path.read_text())


def unit(index, width):
    return tuple(int(j == index) for j in range(width))


def subtract(left, right):
    require(len(left) == len(right), "vector width mismatch")
    return tuple(a - b for a, b in zip(left, right))


def rank(vectors, prime=None):
    """Integer row elimination, or separate modular Gaussian elimination."""
    require(len(vectors) <= 64, "rank row bound")
    if not vectors:
        return 0
    width = len(vectors[0])
    require(width <= 24 and all(len(v) == width for v in vectors), "rank width")
    rows = [list(v) for v in vectors]
    pivot = 0
    for col in range(width):
        choices = [
            i
            for i in range(pivot, len(rows))
            if (rows[i][col] % prime if prime else rows[i][col])
        ]
        if not choices:
            continue
        chosen = choices[0]
        rows[pivot], rows[chosen] = rows[chosen], rows[pivot]
        top = rows[pivot]
        for i in range(pivot + 1, len(rows)):
            if prime:
                factor = rows[i][col] * pow(top[col], -1, prime) % prime
                rows[i] = [(a - factor * b) % prime for a, b in zip(rows[i], top)]
            else:
                new = [top[col] * a - rows[i][col] * b for a, b in zip(rows[i], top)]
                divisor = math.gcd(*new)
                rows[i] = [a // divisor for a in new] if divisor else new
        pivot += 1
        if pivot == len(rows):
            break
    return pivot


def contains(vectors, target, prime=None):
    return rank(vectors, prime) == rank(vectors + [target], prime)


def validate_case(case):
    vertices, edges = case["vertices"], case["edges"]
    groups, links = case["branch_sets"], case["links"]
    require(5 <= len(vertices) <= 20, "vertex bound")
    require(
        all(isinstance(v, str) and 1 <= len(v) <= 32 for v in vertices), "vertex name"
    )
    require(len(set(vertices)) == len(vertices), "duplicate vertex")
    require(6 <= len(edges) <= 40, "edge bound")
    require(
        all(len(e) == 2 and set(e) <= set(vertices) for e in edges), "edge endpoints"
    )
    require(len(groups) == 5 and all(groups), "five nonempty branch sets required")
    flat = [v for group in groups for v in group]
    require(
        len(set(flat)) == len(flat) and set(flat) <= set(vertices),
        "disjoint branch sets",
    )
    require(
        all(root in groups[i] for i, root in enumerate(("0", "a", "b"))),
        "root placement",
    )
    require(len(links) == 6 and len(set(links)) == 6, "six distinct links required")
    require(all(type(i) is int and 0 <= i < len(edges) for i in links), "link index")
    owners = {v: i for i, group in enumerate(groups) for v in group}
    signs = []
    for edge_index, pair in zip(links, PAIRS):
        u, v = edges[edge_index]
        ends = (owners.get(u), owners.get(v))
        require(
            ends == pair or ends == pair[::-1],
            "link does not join required branch sets",
        )
        signs.append(1 if ends == pair else -1)
    contracted = []
    for group in groups:
        reached = {group[0]}
        for _ in range(len(group) - 1):
            choices = [
                (i, v if u in reached else u)
                for i, (u, v) in enumerate(edges)
                if u in group and v in group and ((u in reached) != (v in reached))
            ]
            require(bool(choices), "disconnected branch set")
            index, vertex = choices[0]
            contracted.append(index)
            reached.add(vertex)
        require(reached == set(group), "incomplete branch tree")
    return owners, contracted, signs


def geometry(case):
    owners, contracted, signs = validate_case(case)
    internal = [v for v in case["vertices"] if v not in ("0", "a", "b")]
    width = 3 + len(internal)
    e, f, g = [unit(i, width) for i in range(3)]
    potentials = {
        "0": (0,) * width,
        "a": tuple(a + b for a, b in zip(e, g)),
        "b": tuple(a + b for a, b in zip(f, g)),
    }
    potentials.update({v: unit(3 + i, width) for i, v in enumerate(internal)})
    edge_vectors = [subtract(potentials[v], potentials[u]) for u, v in case["edges"]]
    contracted_vectors = [edge_vectors[i] for i in contracted]
    representatives = [
        g,
        tuple(a + b for a, b in zip(e, f)),
        tuple(a + b + z for a, b, z in zip(e, f, g)),
    ]
    representatives += [
        tuple(sign * x for x in edge_vectors[i])
        for i, sign in zip(case["links"], signs)
    ]
    return owners, contracted_vectors, representatives, [e, f], internal


def projection(owners, internal):
    unused = [v for v in internal if v not in owners]
    width = 5 + len(unused)
    e, f, g, h, k = [unit(i, width) for i in range(5)]
    branch_images = [
        (0,) * width,
        tuple(a + b for a, b in zip(e, g)),
        tuple(a + b for a, b in zip(f, g)),
        h,
        k,
    ]
    images = [e, f, g]
    for vertex in internal:
        images.append(
            branch_images[owners[vertex]]
            if vertex in owners
            else unit(5 + unused.index(vertex), width)
        )
    return images


def apply(images, vector):
    return tuple(
        sum(c * image[j] for c, image in zip(vector, images))
        for j in range(len(images[0]))
    )


def check_source_witness(queries, marks, names, mark, support, values):
    functional = [Fraction(a) for a in values]
    require(all(a.denominator == 1 for a in functional), "integral separator")
    require(sum(a * b for a, b in zip(functional, marks[mark])) == 1, "separator mark")
    vanish = [marks[1 - mark]] + [queries[names.index(c)] for c in support]
    require(
        all(sum(a * b for a, b in zip(functional, q)) == 0 for q in vanish),
        "separator zero",
    )


def check_reader_witness(queries, marks, names, mark, support, values):
    coefficients = [Fraction(a) for a in values]
    require(all(a.denominator in (1, 2) for a in coefficients), "reader denominator")
    require(
        all(not a or names[i] in support for i, a in enumerate(coefficients)),
        "reader support",
    )
    value = [sum(a * q[j] for a, q in zip(coefficients, queries)) for j in range(5)]
    require(value == marks[mark], "reader identity")


def check_predecessor():
    origins = load("ORIGINS.json")
    for row in origins["files"]:
        raw = (ROOT / row["retained_path"]).read_bytes()
        require(
            hashlib.sha256(raw).hexdigest() == row["sha256"], "retained source hash"
        )
    config, witness = load("predecessor/CONFIG.json"), load("predecessor/WITNESS.json")
    names, queries, marks = config["query_names"], config["queries"], config["marks"]
    require(names == "gdthxykzw" and len(queries) == 9, "predecessor query indexing")
    require(
        len(witness["rows"])
        == len(witness["functionals"])
        == len(witness["readers"])
        == 21,
        "21 certificate rows",
    )
    seen = {"source": [], "reader": []}
    for (kind, mark, support), phi, reader in zip(
        witness["rows"], witness["functionals"], witness["readers"]
    ):
        seen[kind].append([mark, support])
        if kind == "source":
            check_source_witness(queries, marks, names, mark, support, phi)
        else:
            check_reader_witness(queries, marks, names, mark, support, reader)
    require(
        all(sorted(seen[k]) == sorted(config["premises"][k]) for k in seen),
        "21 premises",
    )
    return config


def check_predicates(c, reps, marks, config):
    stream = []
    for mask in range(512):
        indices = [i for i in range(9) if mask >> i & 1]
        small = [config["queries"][i] for i in indices]
        lifted = c + [reps[i] for i in indices]
        for mark in range(2):
            for prime in (None, 2, 3):
                reader = contains(lifted, marks[mark], prime)
                expected_reader = contains(small, config["marks"][mark], prime)
                source = not contains(lifted + [marks[1 - mark]], marks[mark], prime)
                expected_source = not contains(
                    small + [config["marks"][1 - mark]], config["marks"][mark], prime
                )
                require(
                    (reader, source) == (expected_reader, expected_source),
                    "subset quotient predicate",
                )
                stream.append([mask, mark, prime, reader, source])
    digest = hashlib.sha256(
        json.dumps(stream, separators=(",", ":")).encode()
    ).hexdigest()
    return len(stream), digest


def check_case(case, config):
    owners, c, reps, marks, internal = geometry(case)
    images = projection(owners, internal)
    width = len(marks[0])
    projected = [apply(images, q) for q in reps]
    expected = [tuple(q) + (0,) * (len(images[0]) - 5) for q in config["queries"]]
    require(projected == expected, "projected K3,2 queries")
    require(all(not any(apply(images, q)) for q in c), "contraction kernel inclusion")
    for prime in (None, 2, 3, 5):
        require(rank(c, prime) + rank(images, prime) == width, "kernel dimension")
        require(
            rank(c + marks, prime) == rank(c, prime) + 2, "independent quotient marks"
        )
    count, digest = check_predicates(c, reps, marks, config)
    return {
        "name": case["name"],
        "vertices": len(case["vertices"]),
        "edges": len(case["edges"]),
        "contraction_rank": len(c),
        "predicate_pairs": count,
        "predicate_sha256": digest,
    }


def main():
    config = check_predecessor()
    cases = load("CASES.json")
    require(isinstance(cases, list) and 1 <= len(cases) <= 16, "case count bound")
    results = [check_case(case, config) for case in cases]
    require(results == load("RESULT.json")["cases"], "result receipt mismatch")
    print(
        "PASS_ROOTED_MINOR_TRANSFER "
        + json.dumps(
            {
                "cases": len(results),
                "predicate_pairs": sum(r["predicate_pairs"] for r in results),
                "old_universal_premises": 21,
                "no_new_kappa": True,
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
