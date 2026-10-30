#!/usr/bin/env python3
"""Joint header law for arbitrary rank-one requests. Produced by Nick Petalas. Apache-2.0."""

import argparse
from collections import Counter
from fractions import Fraction
import hashlib
from itertools import product
import json
import random
from pathlib import Path


PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
LOCAL_FILES = ("README.md", "SOURCES.json", "TASK.json", "VERIFY.json", "verify.py")
FIELDS = (2, 3, 4, 5)
PAIR_CASES = ((2, 2), (2, 3), (2, 4), (3, 2), (3, 3), (4, 2), (4, 3), (5, 2))
HEADER_CASES = ((2, 2), (2, 3), (3, 2), (4, 2))
FAMILY_CASES = ((2, 3, 3), (2, 4, 3), (2, 4, 4), (3, 3, 3), (3, 4, 3),
                (3, 4, 4), (4, 3, 3), (5, 3, 3))
FAMILIES_PER_CASE = 40
SEED = 4239
TYPES = ("equal", "same_image", "same_kernel", "orthogonal",
         "one_sided", "generic", "degenerate")


def need(condition, message):
    if not condition:
        raise ValueError(message)


def field(q):
    """F4 is F2[x]/(x^2+x+1), encoded by two coefficient bits."""
    need(q in FIELDS, "unsupported executable field")
    add = tuple(tuple((a ^ b) if q == 4 else (a + b) % q
                      for b in range(q)) for a in range(q))
    rows = []
    for a in range(q):
        row = []
        for b in range(q):
            if q == 4:
                value = (a if b & 1 else 0) ^ ((a << 1) if b & 2 else 0)
                value ^= 7 if value & 4 else 0
            else:
                value = a * b % q
            row.append(value)
        rows.append(tuple(row))
    mul = tuple(rows)
    neg = tuple(next(b for b in range(q) if add[a][b] == 0) for a in range(q))
    inv = (0,) + tuple(next(b for b in range(1, q) if mul[a][b] == 1)
                       for a in range(1, q))
    for a, b, c in product(range(q), repeat=3):
        need(mul[a][add[b][c]] == add[mul[a][b]][mul[a][c]], "distributivity")
        need(mul[a][mul[b][c]] == mul[mul[a][b]][c], "associativity")
    return add, mul, neg, inv


def dot(x, y, tables):
    add, mul = tables[0], tables[1]
    total = 0
    for a, b in zip(x, y):
        total = add[total][mul[a][b]]
    return total


def rank(rows, tables):
    add, mul, neg, inv = tables
    work = [list(row) for row in rows]
    found = 0
    width = len(work[0]) if work else 0
    for column in range(width):
        pivot = next((i for i in range(found, len(work)) if work[i][column]), None)
        if pivot is None:
            continue
        work[found], work[pivot] = work[pivot], work[found]
        scale = inv[work[found][column]]
        work[found] = [mul[scale][x] for x in work[found]]
        for i in range(len(work)):
            factor = work[i][column]
            if i != found and factor:
                work[i] = [add[x][neg[mul[factor][y]]]
                           for x, y in zip(work[i], work[found])]
        found += 1
    return found


def subsets(k):
    return tuple(tuple(i for i in range(k) if mask >> i & 1) for mask in range(1 << k))


def formula_count(q, m, us, vs, tables):
    """Section 2 of the README: inclusion-exclusion over vanishing guards."""
    need(len(us) == len(vs) and all(dot(v, u, tables) == 1 for u, v in zip(us, vs)),
         "normalized rank-one requests")
    total = 0
    for s in subsets(len(us)):
        r_u = rank([us[i] for i in s], tables)
        for t in subsets(len(us)):
            r_v = rank([vs[j] for j in t], tables)
            gram = [[dot(vs[j], us[i], tables) for i in s] for j in t]
            mu = rank(gram, tables) if s and t else 0
            sign = (-1) ** (len(s) + len(t))
            total += sign * (Fraction(q ** (2 * m - 1), q ** (r_u + r_v))
                             - Fraction(q ** (m - 1), q ** mu))
    need(Fraction(total).denominator == 1, "integral count")
    return int(total)


def closed_pair(kind, q, m):
    """Section 3 of the README: the seven simultaneous types of two requests."""
    need(m >= 2 and (kind != "degenerate" or m >= 3), "pair type domain")
    y = q - 1
    numerator = {
        "equal": y * q ** (m - 1) * (y * q ** (m - 1) + 1),
        "same_image": y * q ** (m - 1) * (y * y * q ** (m - 2) + 1),
        "same_kernel": y * q ** (m - 1) * (y * y * q ** (m - 2) + 1),
        "orthogonal": y * y * q ** (m - 2) * (y * y * q ** (m - 2) - 1),
        "one_sided": y * q ** (m - 2) * (y ** 3 * q ** (m - 2) + 1),
        "generic": y * q ** (m - 2) * (y ** 3 * q ** (m - 2) + q + 1),
        "degenerate": y * q ** (m - 1) * (y ** 3 * q ** (m - 3) + 1),
    }[kind]
    need(numerator % q == 0, "integral closed count")
    return numerator // q


def vectors(q, m):
    return tuple(product(range(q), repeat=m))


def scalar_pairs(q, m, tables):
    return tuple((a, b) for a in vectors(q, m) for b in vectors(q, m)
                 if dot(a, b, tables) == 1)


def idempotents(q, m, tables):
    """One normalized (u, v) per rank-one idempotent: first nonzero u entry is 1."""
    out = []
    for u in vectors(q, m):
        lead = next((x for x in u if x), 0)
        if lead == 1:
            out.extend((u, v) for v in vectors(q, m) if dot(v, u, tables) == 1)
    need(len(out) == q ** (m - 1) * (q ** m - 1) // (q - 1), "idempotent inventory")
    return tuple(out)


def classify(p, r, tables):
    (u1, v1), (u2, v2) = p, r
    same_image = rank([u1, u2], tables) == 1
    same_kernel = rank([v1, v2], tables) == 1
    if same_image and same_kernel:
        return "equal"
    if same_image or same_kernel:
        return "same_image" if same_image else "same_kernel"
    c, d = dot(v1, u2, tables), dot(v2, u1, tables)
    if not c and not d:
        return "orthogonal"
    if not c or not d:
        return "one_sided"
    return "degenerate" if tables[1][c][d] == 1 else "generic"


def good_masks(reps, guards):
    """Bit h of mask i is set when request i passes guard h."""
    masks = [0] * len(reps)
    for h, passes in enumerate(guards):
        for i in passes:
            masks[i] |= 1 << h
    return masks


def pair_census(q, m, tables):
    """Every ordered pair of rank-one idempotents against every scalar pair."""
    reps = idempotents(q, m, tables)
    masks = good_masks(reps, ([i for i, (u, v) in enumerate(reps)
                               if dot(a, u, tables) and dot(v, b, tables)]
                              for a, b in scalar_pairs(q, m, tables)))
    tally = Counter()
    for i, p in enumerate(reps):
        for j, r in enumerate(reps):
            kind = classify(p, r, tables)
            count = (masks[i] & masks[j]).bit_count()
            need(count == closed_pair(kind, q, m), "closed pair law")
            tally[kind, count] += 1
    witnesses = {}
    for i, p in enumerate(reps):
        for j, r in enumerate(reps):
            witnesses.setdefault(classify(p, r, tables), (p, r))
    for kind, (p, r) in witnesses.items():
        need(formula_count(q, m, (p[0], r[0]), (p[1], r[1]), tables)
             == closed_pair(kind, q, m), "general law on a pair type")
    return {"q": q, "m": m, "idempotents": len(reps),
            "scalar_pairs": (q ** m - 1) * q ** (m - 1),
            "types": {kind: [{"count": count, "ordered_pairs": n}
                             for (k, count), n in sorted(tally.items()) if k == kind]
                      for kind in TYPES if any(k == kind for k, _ in tally)}}


def invert(matrix, tables):
    add, mul, neg, inv = tables
    m = len(matrix)
    work = [list(row) + [int(i == j) for j in range(m)] for i, row in enumerate(matrix)]
    for column in range(m):
        pivot = next((i for i in range(column, m) if work[i][column]), None)
        if pivot is None:
            return None
        work[column], work[pivot] = work[pivot], work[column]
        scale = inv[work[column][column]]
        work[column] = [mul[scale][x] for x in work[column]]
        for i in range(m):
            factor = work[i][column]
            if i != column and factor:
                work[i] = [add[x][neg[mul[factor][y]]]
                           for x, y in zip(work[i], work[column])]
    return [row[m:] for row in work]


def matmul(x, y, tables):
    columns = list(zip(*y))
    return [[dot(row, column, tables) for column in columns] for row in x]


def header_census(q, m, tables):
    """Conjugate every rank-one idempotent by every invertible header."""
    reps = idempotents(q, m, tables)
    matrices = [[[tables[1][u[i]][v[j]] for j in range(m)] for i in range(m)]
                for u, v in reps]
    guards = []
    for flat in product(range(q), repeat=m * m):
        g = [list(flat[i * m:(i + 1) * m]) for i in range(m)]
        gi = invert(g, tables)
        if gi is not None:
            guards.append([i for i, p in enumerate(matrices)
                           if matmul(matmul(g, p, tables), gi, tables)[0][0]])
    headers = len(guards)
    masks = good_masks(reps, guards)
    fiber = headers // ((q ** m - 1) * q ** (m - 1))
    need(fiber * (q ** m - 1) * q ** (m - 1) == headers, "equal pair fibers")
    for i, p in enumerate(reps):
        for j, r in enumerate(reps):
            need((masks[i] & masks[j]).bit_count() == fiber * closed_pair(classify(p, r, tables), q, m),
                 "complete header census")
    return {"q": q, "m": m, "headers": headers, "fiber": fiber,
            "ordered_pairs": len(reps) ** 2}


def random_request(q, m, rng, tables):
    while True:
        u = tuple(rng.randrange(q) for _ in range(m))
        v = tuple(rng.randrange(q) for _ in range(m))
        if dot(v, u, tables) == 1:
            return u, v


def structured_request(q, m, rng, base, tables):
    """Reuse an earlier image or kernel so degenerate rank data are sampled."""
    u0, v0 = base
    for _ in range(1000):
        u, v = random_request(q, m, rng, tables)
        candidate = (u0, v) if rng.randrange(2) else (u, v0)
        if dot(candidate[1], candidate[0], tables) == 1:
            return candidate
    raise ValueError("structured request search exhausted")


def family_census(q, m, k, rng, tables):
    pairs = scalar_pairs(q, m, tables)
    signatures = Counter()
    for index in range(FAMILIES_PER_CASE):
        family = [random_request(q, m, rng, tables)]
        while len(family) < k:
            if index % 2:
                family.append(structured_request(q, m, rng, rng.choice(family), tables))
            else:
                family.append(random_request(q, m, rng, tables))
        us, vs = [p[0] for p in family], [p[1] for p in family]
        direct = sum(all(dot(a, u, tables) and dot(v, b, tables) for u, v in family)
                     for a, b in pairs)
        need(direct == formula_count(q, m, us, vs, tables), "general family law")
        signatures[rank(us, tables), rank(vs, tables), direct] += 1
    return {"q": q, "m": m, "k": k, "families": FAMILIES_PER_CASE,
            "distinct_signatures": len(signatures)}


def controls(tables):
    """Each control must disagree with an exact census value."""
    t3, t2 = tables[3], tables[2]
    rows = 0
    d3 = (3 ** 3 - 1) * 3 ** 2
    single = closed_pair("equal", 3, 3)
    need(Fraction(closed_pair("generic", 3, 3), d3) != Fraction(single, d3) ** 2,
         "independence must fail on a generic pair")
    rows += 1
    need(closed_pair("same_image", 3, 3) != closed_pair("degenerate", 3, 3),
         "tr(PQ)=1 alone must not determine the law")
    rows += 1
    need(closed_pair("one_sided", 3, 3) != closed_pair("orthogonal", 3, 3),
         "one vanishing product must differ from orthogonality")
    rows += 1
    us, vs = ((1, 0, 0), (0, 1, 0)), ((1, 1, 0), (0, 1, 1))
    exact = formula_count(3, 3, us, vs, t3)
    pairs = scalar_pairs(3, 3, t3)
    direct = sum(all(dot(a, u, t3) and dot(v, b, t3) for u, v in zip(us, vs))
                 for a, b in pairs)
    need(exact == direct, "control base")
    need(exact != direct + 1, "corrupted count must be rejected")
    rows += 1
    integer_mod4 = sum(all((sum(x * y for x, y in zip(a, u)) % 4) and
                           (sum(x * y for x, y in zip(v, b)) % 4)
                           for u, v in (((1, 0), (1, 1)), ((1, 1), (0, 1))))
                       for a in product(range(4), repeat=2) for b in product(range(4), repeat=2)
                       if sum(x * y for x, y in zip(a, b)) % 4 == 1)
    need(integer_mod4 != closed_pair("one_sided", 4, 2), "F4 is not Z/4")
    rows += 1
    need(not any(classify(p, r, t2) == "generic" for p in idempotents(2, 3, t2)
                 for r in idempotents(2, 3, t2)), "F2 has no generic pair")
    need(closed_pair("orthogonal", 2, 2) == 0, "binary exceptional orthogonal pair")
    rows += 1
    return rows


def scientific_result():
    tables = {q: field(q) for q in FIELDS}
    rng = random.Random(SEED)
    return {"pair_cases": [pair_census(q, m, tables[q]) for q, m in PAIR_CASES],
            "header_cases": [header_census(q, m, tables[q]) for q, m in HEADER_CASES],
            "family_cases": [family_census(q, m, k, rng, tables[q])
                             for q, m, k in FAMILY_CASES],
            "controls": controls(tables)}


def digest(path):
    need(path.is_file() and path.stat().st_size <= 1000000, "bounded regular input")
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source_hashes():
    sources = json.loads((PACKAGE / "SOURCES.json").read_text())
    live = [row for row in sources["files"] if row["usage"] == "input"]
    need(len(live) == 2, "exact source inventory")
    result = {}
    for row in live:
        value = digest(ROOT / row["path"])
        need(value == row["sha256"], "changed live source: " + row["path"])
        result[row["path"]] = value
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-receipt", type=Path,
                        help="create one new receipt outside the checkout")
    args = parser.parse_args()
    inputs = source_hashes()
    result = scientific_result()
    receipt = {"schema_version": 1, "claim_type": "scoped counting proof with finite corroboration",
               "inputs": inputs, "files": {name: digest(PACKAGE / name) for name in LOCAL_FILES},
               "result": result}
    if args.write_receipt:
        destination = args.write_receipt.resolve()
        need(not destination.is_relative_to(ROOT), "receipt output must be outside checkout")
        with destination.open("x", encoding="utf-8") as output:
            output.write(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    else:
        expected = json.loads((PACKAGE / "RESULT.json").read_text())
        need(receipt == expected, "receipt does not match exact bytes and recomputed counts")
    print("PASS_PROJECTOR_PAIR_HEADER_LAW " + json.dumps({
        "ordered_pairs": sum(row["idempotents"] ** 2 for row in result["pair_cases"]),
        "headers": sum(row["headers"] for row in result["header_cases"]),
        "families": sum(row["families"] for row in result["family_cases"]),
        "controls": result["controls"]}, sort_keys=True))


if __name__ == "__main__":
    main()
