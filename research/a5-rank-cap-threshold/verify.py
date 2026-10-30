"""Exact, bounded corroboration of the A5 paid-rank threshold. Apache-2.0."""

import hashlib
import itertools
import json
from fractions import Fraction
from pathlib import Path


IDENTITY = (0, 1, 2, 3, 4)
X = (1, 0, 3, 2, 4)
Y = (2, 1, 4, 3, 0)


def need(condition, message):
    if not condition:
        raise ValueError(message)


def compose(g, h):
    return tuple(g[h[i]] for i in range(5))


def reduce_value(value, prime):
    return value % prime if prime else value


def zero(n):
    return ((0,) * n,) * n


def eye(n):
    return tuple(tuple(int(i == j) for j in range(n)) for i in range(n))


def add(a, b, prime, sign=1):
    n = len(a)
    return tuple(tuple(reduce_value(a[i][j] + sign * b[i][j], prime)
                       for j in range(n)) for i in range(n))


def multiply(a, b, prime):
    n = len(a)
    return tuple(tuple(reduce_value(sum(a[i][k] * b[k][j] for k in range(n)), prime)
                       for j in range(n)) for i in range(n))


def rank(a, prime):
    n = len(a)
    rows = [list(row) for row in a]
    pivot = 0
    for j in range(n):
        candidates = [i for i in range(pivot, n) if rows[i][j]]
        if not candidates:
            continue
        k = candidates[0]
        rows[pivot], rows[k] = rows[k], rows[pivot]
        inv = pow(rows[pivot][j], -1, prime) if prime else Fraction(1, rows[pivot][j])
        rows[pivot] = [reduce_value(v * inv, prime) for v in rows[pivot]]
        for i in range(pivot + 1, n):
            scalar = rows[i][j]
            rows[i] = [reduce_value(rows[i][k] - scalar * rows[pivot][k], prime)
                       for k in range(n)]
        pivot += 1
    return pivot


def append_factor(state, label, coupling, prime):
    """Multiply on the right by (I-N) + [label]N, keeping every coefficient."""
    n = len(coupling)
    result = {}
    for group, coefficient in state.items():
        active = multiply(coefficient, coupling, prime)
        passive = add(coefficient, active, prime, -1)
        for destination, matrix in ((group, passive), (compose(group, label), active)):
            result[destination] = add(result.get(destination, zero(n)), matrix, prime)
    return {g: a for g, a in result.items() if a != zero(n)}


def word_endpoint(word, prime, n):
    state = {IDENTITY: eye(n)}
    for label, coupling in word:
        state = append_factor(state, label, coupling, prime)
    return state


def target(p, q, prime):
    residual = add(add(eye(len(p)), p, prime, -1), q, prime, -1)
    result = {IDENTITY: residual, compose(X, Y): p, compose(Y, X): q}
    return {g: a for g, a in result.items() if a != zero(len(p))}


def valid_pair(p, q, prime):
    n = len(p)
    need(2 <= n <= 8 and len(q) == n, "role domain")
    need(all(len(row) == n for row in p + q), "square projectors")
    need(multiply(p, p, prime) == p and multiply(q, q, prime) == q, "idempotents")
    need(multiply(p, q, prime) == zero(n) and multiply(q, p, prime) == zero(n),
         "orthogonal projectors")
    r, s = rank(p, prime), rank(q, prime)
    need(r > 0 and s > 0, "nonzero targets")
    return r, s


def minimum(p, q, cap, prime):
    r, s = valid_pair(p, q, prime)
    need(type(cap) is int and cap >= max(r, s), "cap domain")
    return 3 if cap >= r + s else 4


def three_word(p, q, prime):
    return ((X, p), (Y, add(p, q, prime)), (X, q))


def four_word(p, q):
    return ((X, p), (Y, p), (Y, q), (X, q))


def support_check():
    """Independent ordered-subsequence expansion of all short label words."""
    hits = []
    for length in range(4):
        for labels in itertools.product((X, Y), repeat=length):
            support = set()
            for mask in range(1 << length):
                g = IDENTITY
                for i in range(length):
                    if mask >> i & 1:
                        g = compose(g, labels[i])
                support.add(g)
            if {compose(X, Y), compose(Y, X)} <= support:
                hits.append(labels)
    need(hits == [(X, Y, X), (Y, X, Y)], "short support patterns")
    return {"short_label_words": 15, "admissible_support_patterns": 2}


def idempotents_two(prime):
    result = []
    for entries in itertools.product(range(prime), repeat=4):
        matrix = (entries[:2], entries[2:])
        if multiply(matrix, matrix, prime) == matrix:
            result.append(matrix)
    need(len(result) == prime * (prime + 1) + 2, "idempotent inventory")
    return result


def census(prime):
    """Full endpoint oracle; it does not use the middle-coupling argument."""
    matrices = idempotents_two(prime)
    targets = {}
    for p in matrices:
        if rank(p, prime) == 1:
            q = add(eye(2), p, prime, -1)
            targets[tuple(sorted(target(p, q, prime).items()))] = (p, q)
    hits = []
    words = 0
    for labels in itertools.product((X, Y), repeat=3):
        for couplings in itertools.product(matrices, repeat=3):
            state = word_endpoint(tuple(zip(labels, couplings)), prime, 2)
            key = tuple(sorted(state.items()))
            words += 1
            if key in targets:
                p, q = targets[key]
                need(couplings[1] == eye(2), "attaining middle rank")
                expected = (p, eye(2), q) if labels == (X, Y, X) else (q, eye(2), p)
                need(couplings == expected, "complete attaining triple")
                hits.append((labels, couplings))
    need(len(hits) == 2 * prime * (prime + 1), "attainment count")
    return {"field": prime, "idempotents": len(matrices), "words": words,
            "targets": len(targets), "three_call_hits": len(hits)}


def conjugated_pair(n, r, s, prime):
    """Explicit oblique projectors, with no enumeration or random choices."""
    p = tuple(tuple(int(i == j and i < r) for j in range(n)) for i in range(n))
    q = tuple(tuple(int(i == j and r <= i < r + s) for j in range(n))
              for i in range(n))
    for k in range(2 * n):
        i, j = k % n, (k + 1) % n
        amount = (k + 1) if prime else Fraction(k + 1, k + 2)
        e = tuple(tuple(amount if (a, b) == (i, j) else 0 for b in range(n))
                  for a in range(n))
        forward, inverse = add(eye(n), e, prime), add(eye(n), e, prime, -1)
        need(multiply(forward, inverse, prime) == eye(n), "conjugator inverse")
        p = multiply(multiply(forward, p, prime), inverse, prime)
        q = multiply(multiply(forward, q, prime), inverse, prime)
    return p, q


def endpoint_fixtures():
    count, controls = 0, 0
    for prime in (0, 2, 3, 5, 7):
        for n, r, s in ((2, 1, 1), (3, 1, 1), (4, 1, 2), (5, 2, 2),
                        (6, 2, 3), (8, 3, 4)):
            p, q = conjugated_pair(n, r, s, prime)
            expected = target(p, q, prime)
            for word in (three_word(p, q, prime), four_word(p, q)):
                need(word_endpoint(word, prime, n) == expected, "full dirty endpoint")
                count += 1
                for index in range(len(word)):
                    mutant = word[:index] + word[index + 1:]
                    need(word_endpoint(mutant, prime, n) != expected, "omission control")
                    controls += 1
            need(minimum(p, q, r + s, prime) == 3, "rank threshold upper side")
            need(minimum(p, q, max(r, s), prime) == 4, "rank threshold lower side")
            need(rank(add(p, q, prime), prime) == r + s, "rank additivity")
    return {"complete_endpoints": count, "omission_controls": controls,
            "oblique_pairs": count // 2}


def regular_action_check():
    """Act directly on all regular-module basis columns, without formal products."""
    group = []
    for g in itertools.permutations(range(5)):
        inversions = sum(g[i] > g[j] for i in range(5) for j in range(i + 1, 5))
        if inversions % 2 == 0:
            group.append(g)
    need(len(group) == 60, "even permutation group")
    n = 4
    p, q = conjugated_pair(n, 1, 2, 3)
    endpoint = target(p, q, 3)
    columns = 0
    for word in (three_word(p, q, 3), four_word(p, q)):
        for source in range(n):
            for address in group:
                values = {(source, address): 1}
                for label, coupling in reversed(word):
                    updated = dict(values)
                    for (j, g), value in values.items():
                        for i in range(n):
                            coefficient = value * coupling[i][j]
                            for dest, sign in ((g, -1), (compose(label, g), 1)):
                                key = (i, dest)
                                updated[key] = (updated.get(key, 0) + sign * coefficient) % 3
                    values = {key: v for key, v in updated.items() if v}
                expected = {}
                for g, coefficient in endpoint.items():
                    for i in range(n):
                        if coefficient[i][source]:
                            expected[i, compose(g, address)] = coefficient[i][source]
                need(values == expected, "literal regular-action column")
                columns += 1
    return {"regular_action_basis_columns": columns}


def invalid_controls():
    p = ((1, 0), (0, 0))
    q = ((0, 0), (0, 1))
    tests = ((p, q, 0), (p, q, True), (p, p, 2), (zero(2), q, 2),
             (((0, 1), (0, 0)), q, 2), (p, ((1,),), 2))
    for a, b, cap in tests:
        try:
            minimum(a, b, cap, 3)
        except ValueError:
            continue
        raise ValueError("invalid input was accepted")
    p3 = ((1, 0, 0), (0, 0, 0), (0, 0, 0))
    q3 = ((0, 0, 0), (0, 1, 0), (0, 0, 0))
    h3 = ((0, 0, 0), (0, 0, 0), (0, 0, 1))
    bad = three_word(p3, q3, 3) + ((X, h3),)
    need(word_endpoint(bad, 3, 3) != target(p3, q3, 3), "dirty spectator control")
    return {"invalid_input_controls": len(tests), "spectator_control": 1}


def main():
    evidence = {"support": support_check(), "censuses": [census(p) for p in (3, 5)],
                "fixtures": endpoint_fixtures(), "regular": regular_action_check(),
                "controls": invalid_controls()}
    root = Path(__file__).resolve().parent
    names = ("README.md", "PROOF.md", "TASK.json", "SOURCES.json", "VERIFY.json", "verify.py")
    hashes = {name: hashlib.sha256((root / name).read_bytes()).hexdigest() for name in names}
    print("PASS_A5_RANK_CAP_THRESHOLD " + json.dumps({"evidence": evidence, "sha256": hashes},
                                                    sort_keys=True))


if __name__ == "__main__":
    main()
