#!/usr/bin/env python3
"""Exact finite corroboration for the written split-tree theorem. Read-only."""
from fractions import Fraction as F
from hashlib import sha256
from itertools import combinations
import json
from math import comb
from pathlib import Path

MAX_N = 256
PACKAGE_FILES = ("README.md", "PROOF.md", "TASK.json", "SOURCES.json", "VERIFY.json", "verify.py")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def parameters(n):
    require(type(n) is int and 1 <= n <= MAX_N, "finite verifier domain is 1..256")
    d = n.bit_length() - 1
    return d, 1 << d, n - (1 << d)


def optimum(n):
    d, q, remaining = parameters(n)
    total = 3 ** d
    for weight in range(d + 1):
        take = min(remaining, comb(d, weight))
        total += 2 * take * (1 << weight)
        remaining -= take
    require(remaining == 0, "binomial capacities exhausted")
    return 3 * q * n - 2 * q * q, total


def minimum_tree(n, bottom=None):
    d, q, k = parameters(n)
    if bottom is None:
        bottom = sorted(range(q), key=lambda i: (i.bit_count(), i))[:k]
    require(len(set(bottom)) == len(bottom) == k, "wrong bottom cardinality")
    require(all(type(i) is int and 0 <= i < q for i in bottom), "bad bottom index")
    internal = {format(i, f"0{level}b") if level else ""
                for level in range(d) for i in range(1 << level)}
    internal.update(format(i, f"0{d}b") if d else "" for i in bottom)
    return frozenset(internal)


def leaves(internal):
    require(len(internal) < MAX_N, "tree too large")
    require(all(set(p) <= {"0", "1"} and len(p) < MAX_N for p in internal), "bad path")
    require(all(not p or p[:-1] in internal for p in internal), "missing ancestor")
    return sorted(({""} | {p + b for p in internal for b in "01"}) - internal)


def statistics(internal):
    paths = leaves(internal)
    return (sum(1 << len(p) for p in paths),
            sum(1 << p.count("1") for p in paths),
            max(map(len, paths)))


def word(internal, orientation=1):
    require(orientation in (-1, 1), "bad orientation")
    paths = leaves(internal)
    labels = {p: i for i, p in enumerate(paths)}
    paid, _, _ = statistics(internal)
    stack = [("", 0, 1, orientation)]
    result = []
    for _ in range(2 * paid):
        if not stack:
            break
        path, source, target, sign = stack.pop()
        if path not in internal:
            result.append((source, target, sign, labels[path]))
            continue
        helper = 2 + len(path)
        left = (path + "0", source, helper)
        right = (path + "1", helper, target)
        phases = ((left, 1), (right, 1), (left, -1), (right, -1))
        if sign == -1:
            phases = ((right, 1), (left, 1), (right, -1), (left, -1))
        stack.extend((*child, child_sign) for child, child_sign in reversed(phases))
    require(not stack and len(result) == paid, "literal expansion incomplete")
    return result


def scalar_observation(gates, roles, orientation):
    endpoint = [[int(i == j) for j in range(roles)] for i in range(roles)]
    for source, target, sign, _ in gates:
        endpoint[target] = [a + sign * b for a, b in zip(endpoint[target], endpoint[source])]
    expected = [[int(i == j) for j in range(roles)] for i in range(roles)]
    expected[1][0] = orientation
    require(endpoint == expected, "arbitrary-dirty-input endpoint failed")
    suffix = [int(i == 1) for i in range(roles)]
    responses = []
    for source, target, sign, _ in reversed(gates):
        responses.append(suffix[target])
        suffix[source] += sign * suffix[target]
    require(all(c in (-1, 0, 1) for c in responses), "nonunit scalar response")
    state = [0] * roles
    for (source, target, sign, _), defect in zip(gates, reversed(responses)):
        state[target] += sign * state[source] + defect
    count = sum(abs(c) for c in responses)
    require(state[1] == count, "independent signed defects did not attain count")
    return count


def all_shapes():
    shapes = [set() for _ in range(11)]
    shapes[1].add(frozenset())
    rows = []
    for n in range(1, 11):
        if n > 1:
            for size in range(1, n):
                for left in shapes[size]:
                    for right in shapes[n - size]:
                        shapes[n].add(frozenset({""} | {"0" + p for p in left}
                                                | {"1" + p for p in right}))
        observations = [statistics(tree) for tree in shapes[n]]
        paid = min(p for p, _, _ in observations)
        error = min(t for p, t, _ in observations if p == paid)
        require((paid, error) == optimum(n), "exhaustive shape minimum disagrees")
        rows.append({"n": n, "shapes": len(observations), "paid": paid, "target": error})
    require(sum(row["shapes"] for row in rows) == 6918, "shape coverage changed")
    return rows


def minimum_tree_words():
    counts = {"trees": 0, "orientations": 0, "paid_gate_occurrences": 0}
    for n in range(1, 17):
        _, q, k = parameters(n)
        for bottom in combinations(range(q), k):
            tree = minimum_tree(n, bottom)
            paid, coefficient, depth = statistics(tree)
            require(paid == optimum(n)[0], "minimum paid count not attained")
            for orientation in (-1, 1):
                gates = word(tree, orientation)
                observed = scalar_observation(gates, depth + 2, orientation)
                require(observed == coefficient, "literal coefficient disagrees")
                counts["orientations"] += 1
                counts["paid_gate_occurrences"] += len(gates)
            counts["trees"] += 1
    require(counts["trees"] == 275, "bottom-subset coverage changed")
    return counts


def add(a, b):
    return tuple(x + y for x, y in zip(a, b))


def scale(a, s):
    return tuple(s * x for x in a)


def mul(a, b):
    return (a[0]*b[0]+a[1]*b[2], a[0]*b[1]+a[1]*b[3],
            a[2]*b[0]+a[3]*b[2], a[2]*b[1]+a[3]*b[3])


def transpose(a):
    return a[0], a[2], a[1], a[3]


def matrix_observation(gates, n, roles, orientation):
    identity, zero = (F(1), F(0), F(0), F(1)), (F(0),) * 4
    alphabet = ((F(0), F(-1), F(1), F(0)), (F(1), F(0), F(0), F(-1)),
                (F(3, 5), F(-4, 5), F(4, 5), F(3, 5)))
    factors = [alphabet[j % len(alphabet)] for j in range(n)]
    require(mul(factors[0], factors[1]) != mul(factors[1], factors[0]), "commuting fixture")
    endpoint = [[identity if i == j else zero for j in range(roles)] for i in range(roles)]
    for source, target, sign, j in gates:
        endpoint[target] = [add(a, scale(mul(factors[j], b), sign))
                            for a, b in zip(endpoint[target], endpoint[source])]
    product = identity
    for factor in factors:
        product = mul(factor, product)
    expected = [[identity if i == j else zero for j in range(roles)] for i in range(roles)]
    expected[1][0] = scale(product, orientation)
    require(endpoint == expected, "noncommuting all-input endpoint failed")
    suffix = [identity if i == 1 else zero for i in range(roles)]
    responses = []
    for source, target, sign, j in reversed(gates):
        response = suffix[target]
        require(response == zero or mul(response, transpose(response)) == identity,
                "response is neither zero nor orthogonal")
        responses.append(response)
        suffix[source] = add(suffix[source], scale(mul(response, factors[j]), sign))
    state = [zero] * roles
    for (source, target, sign, j), response in zip(gates, reversed(responses)):
        state[target] = add(add(state[target], scale(mul(factors[j], state[source]), sign)),
                            transpose(response))
    count = sum(response != zero for response in responses)
    require(state[1] == scale(identity, count), "matrix defect attainment failed")
    return count


def noncommuting_words():
    rows = []
    for n in (3, 5, 9):
        tree = minimum_tree(n)
        paid, coefficient, depth = statistics(tree)
        for orientation in (-1, 1):
            observed = matrix_observation(word(tree, orientation), n, depth + 2, orientation)
            require(observed == coefficient, "matrix coefficient disagrees")
            rows.append({"n": n, "orientation": orientation, "paid": paid, "target": observed})
    return rows


def rejecting_controls():
    rejected = []
    for bad in (0, -1, True, 257, F(3, 2)):
        try:
            optimum(bad)
        except ValueError:
            rejected.append("domain:" + str(bad))
        else:
            raise ValueError("invalid domain accepted")
    probes = (("orphan", frozenset({"01"})), ("alphabet", frozenset({"x"})))
    for name, tree in probes:
        try:
            leaves(tree)
        except ValueError:
            rejected.append(name)
        else:
            raise ValueError("invalid tree accepted")
    for name, gates in (("missing-restoration", word(minimum_tree(3))[:-1]),
                        ("wrong-phase-order", sorted(word(minimum_tree(3))))):
        try:
            scalar_observation(gates, 4, 1)
        except ValueError:
            rejected.append(name)
        else:
            raise ValueError("mutant endpoint accepted")
    expensive = frozenset({"", "0", "00"})
    require(statistics(expensive)[:2] == (22, 7), "unrestricted-tree control changed")
    require(optimum(4) == (16, 9), "minimum-paid control changed")
    rejected.append("lower-target-can-cost-more-calls")
    return rejected


def main():
    rows = all_shapes()
    words = minimum_tree_words()
    matrices = noncommuting_words()
    controls = rejecting_controls()
    comparison = []
    old = [0, 1]
    for n in range(2, MAX_N + 1):
        old.append(old[n // 2] + 2 * old[n - n // 2])
    for n in (3, 5, 9, 31, 63, 64, 127, 255):
        tree = minimum_tree(n)
        paid, target, depth = statistics(tree)
        require((paid, target) == optimum(n), "attaining construction disagrees")
        require(target <= old[n], "new optimum worse than balanced tree")
        comparison.append({"n": n, "paid": paid, "scratch": depth,
                           "balanced_target": old[n], "minimum_target": target})
    root = Path(__file__).resolve().parent
    hashes = {name: sha256((root / name).read_bytes()).hexdigest() for name in PACKAGE_FILES}
    print(json.dumps({"status": "PASS_MINPAID_COMMUTATOR_ERROR", "claim_type": "scoped-proof",
                      "shapes": rows, "literal_words": words, "noncommuting": matrices,
                      "controls": controls, "comparisons": comparison,
                      "file_sha256": hashes}, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
