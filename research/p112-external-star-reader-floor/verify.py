"""External-star support transfer. Nick Petalas. Apache-2.0."""

import argparse
import itertools
import json
from fractions import Fraction as F
from hashlib import sha1, sha256
from pathlib import Path

HERE = Path(__file__).resolve().parent
INPUT = "research/adaptive-kernel-demotion/inputs/DATA-PHASES.json"


def need(condition, message):
    if not condition:
        raise ValueError(message)


def read(path, limit=1_048_576):
    with path.open("rb") as stream:
        raw = stream.read(limit + 1)
    need(len(raw) <= limit, "input capacity")
    return raw


def authenticate(raw, pin):
    need(sha256(raw).hexdigest() == pin["sha256"], "source SHA256")
    header = b"blob " + str(len(raw)).encode() + b"\0"
    need(sha1(header + raw, usedforsecurity=False).hexdigest() == pin["git_blob"],
         "source blob")


def dot(a, b):
    return (a & b).bit_count() % 2


def rank(rows, width):
    pivots = [0] * width
    for row in rows:
        for bit in range(width - 1, -1, -1):
            if row >> bit & 1:
                if pivots[bit]:
                    row ^= pivots[bit]
                else:
                    pivots[bit] = row
                    break
    return sum(bool(p) for p in pivots)


def load():
    meta = json.loads(read(HERE / "SOURCES.json", 32768))
    pins = [x for x in meta["files"] if x["usage"] == "input"]
    need(len(pins) == 1 and pins[0]["path"] == INPUT, "input inventory")
    raw = read(HERE.parents[1] / INPUT)
    authenticate(raw, pins[0])
    rows = json.loads(raw)["recipes"]
    need(len(rows) == 112, "112 recipes")
    need(sorted(r["port"] for r in rows) == list(range(112)), "port IDs")
    labels = [r["q"] for r in sorted(rows, key=lambda r: r["port"])]
    need(all(type(q) is int and 0 < q < 512 for q in labels), "binary labels")
    need(len(set(labels)) == 112, "distinct labels")
    raw = read(HERE / "RETAINED-RANK32.json", 32768)
    authenticate(raw, meta["retained_rank32"])
    groups = json.loads(raw)["orthonormal_groups"]
    need(len(groups) == 16, "sixteen groups")
    need(all(len(g) in (4, 6, 8) for g in groups), "group sizes")
    need(sorted(p for g in groups for p in g) == list(range(112)), "partition")
    for g in groups:
        need(all(dot(labels[p], labels[q]) == int(p == q) for p in g for q in g),
             "orthonormal group")
    owners = {p: g[i:i + 2] for g in groups for i in range(0, len(g), 2)
              for p in g[i:i + 2]}
    indicators = [g[side::2] for g in groups for side in range(2)]
    return labels, groups, owners, indicators


def closure(support, owners):
    return sorted({q for p in support for q in owners[p]})


def cost(labels, source, reader):
    rows = [sum(dot(labels[p], labels[q]) << j for j, q in enumerate(reader))
            for p in source]
    return rank(rows, len(reader))


def gf4_mul(a, b):
    value = 0
    for _ in range(2):
        if b & 1:
            value ^= a
        a <<= 1
        if a & 4:
            a ^= 7
        b >>= 1
    return value


def transfer_value(value, active_alpha):
    """At this port only its target arm can have a nonzero literal entry."""
    if value == 0:
        return 0
    if active_alpha != 0 and 1 + active_alpha * value == 0:
        return 1
    return 2


def local_truth_tables():
    need(gf4_mul(2, 2) == 3, "GF4 defining polynomial")
    need(all(any(gf4_mul(a, b) == 1 for b in range(1, 4)) for a in range(1, 4)),
         "GF4 inverses")
    checked = 0
    for prime in (2, 3, 5, 7):
        for alpha in itertools.product(range(prime), repeat=3):
            for target, value in itertools.product(range(-1, 3), range(prime)):
                active = alpha[target] if target >= 0 else 0
                image = 0 if value == 0 else 1 if active and (
                    1 + active * value) % prime == 0 else 2
                for j in range(3):
                    old = (int(j == target) + alpha[j] * value) % prime
                    new = int(j == target) ^ gf4_mul(int(alpha[j] != 0), image)
                    need(bool(old) == bool(new), "prime-field query support")
                need(bool(value) == bool(image), "seed support")
                checked += 1
    return checked


def expanded_identity(labels, owners, indicators):
    index = {p: j for j, row in enumerate(indicators) for p in row}
    entries = 0
    for p, q in itertools.product(range(112), repeat=2):
        for j, k in itertools.product(range(2), repeat=2):
            value = int(index[p] == index[q]) * dot(
                labels[owners[p][j]], labels[owners[q][k]])
            need(value == int(p == q and j == k), "expanded I224")
            entries += 1
    return entries


def fixture(indicators, selected, offset):
    alpha = [F((-2, 0, 3, 1)[(j + offset) % 4]) for j in range(len(selected))]
    target = {p: j for j, index in enumerate(selected) for p in indicators[index]}
    c = []
    for p in range(112):
        j = target.get(p, -1)
        a = alpha[j] if j >= 0 else F(0)
        kind = (p + offset) % 3
        c.append(F(0) if kind == 0 else -1 / a if kind == 1 and a else F(2))
    return alpha, target, c


def check_star(labels, owners, indicators, selected, offset):
    alpha, target, c = fixture(indicators, selected, offset)
    if len(selected) == 3:
        need(any(c[p] for p in range(112) if p not in target), "external triple seed")
    images = [transfer_value(c[p], alpha[target[p]] if p in target else F(0))
              for p in range(112)]
    bill = new_bill = baseline = 0
    for j, index in enumerate(selected):
        source = [p for p in range(112) if int(target.get(p) == j) + alpha[j] * c[p]]
        new = [p for p in range(112) if int(target.get(p) == j) ^
               gf4_mul(int(alpha[j] != 0), images[p])]
        need(source == new, "rational query support")
        reader = closure(indicators[index], owners)
        bill += cost(labels, closure(source, owners), reader)
        new_bill += cost(labels, closure(new, owners), reader)
        baseline += len(reader)
    reader = closure([p for p, j in target.items() if alpha[j]], owners)
    source = closure([p for p in range(112) if c[p]], owners)
    bill += cost(labels, source, reader)
    new_bill += cost(labels, closure([p for p in range(112) if images[p]], owners), reader)
    need(bill == new_bill and bill >= baseline, "external-star tariff floor")
    return bill - baseline


def exact_operator_control(indicators):
    selected = [0, 2, 4]
    alpha, target, c = fixture(indicators, selected, 0)
    images = [transfer_value(c[p], alpha[target[p]] if p in target else F(0))
              for p in range(112)]
    checked = 0
    for p, q in itertools.product(range(112), repeat=2):
        expected = int(p in target and target.get(p) == target.get(q))
        rational = sum(F(target.get(p) == j) * (
            F(target.get(q) == j) + alpha[j] * c[q]) for j in range(3))
        rational -= (alpha[target[p]] if p in target else F(0)) * c[q]
        value = 0
        for j in range(3):
            query = int(target.get(q) == j) ^ gf4_mul(int(alpha[j] != 0), images[q])
            value ^= gf4_mul(int(target.get(p) == j), query)
        value ^= gf4_mul(int(p in target and alpha[target[p]] != 0), images[q])
        need(rational == expected and value == expected, "exact star operator")
        checked += 1
    return checked


def sharpness(labels, owners, indicators):
    selected = [indicators[j] for j in (0, 2, 4)]
    a, b, d = selected
    need(len(a) >= 2, "nonconstant seed fixture")
    supports = [a[1:], b, d, a[:1]]
    need(all(supports) and len(set(p for s in supports for p in s)) ==
         sum(len(s) for s in supports), "four independent disjoint query supports")
    readers = [a, b, d, a]
    bill = sum(cost(labels, closure(q, owners), closure(u, owners))
               for q, u in zip(supports, readers))
    baseline = sum(len(closure(s, owners)) for s in selected)
    need(bill == baseline, "external sharpness witness")
    return {"query_dimension": len(supports), "actual_bill": bill, "baseline": baseline}


def run():
    labels, groups, owners, indicators = load()
    entries = expanded_identity(labels, owners, indicators)
    local = local_truth_tables()
    excess = [check_star(labels, owners, indicators, selected, i)
              for i, selected in enumerate(itertools.combinations(range(32), 3))]
    for count in range(1, 33):
        check_star(labels, owners, indicators, list(range(count)), count)
    return {"status": "PASS_P112_EXTERNAL_STAR_FLOOR", "errors": 0,
            "expanded_identity_entries": entries, "finite_field_local_states": local,
            "literal_triple_fixtures": len(excess), "all_k_fixtures": 32,
            "rational_and_GF4_operator_entries": exact_operator_control(indicators),
            "triple_excess_min": min(excess), "triple_excess_max": max(excess),
            "whole_literal_tariff": sum(2 * len(g) for g in groups),
            "external_sharpness": sharpness(labels, owners, indicators)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    result = run()
    if args.write:
        (HERE / "RESULT.json").write_text(json.dumps(result, indent=2) + "\n")
    else:
        need(json.loads(read(HERE / "RESULT.json", 32768)) == result, "RESULT mismatch")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
