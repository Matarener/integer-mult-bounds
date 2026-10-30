#!/usr/bin/env python3
"""Deterministic complete-call words; exact checks use the standard library."""

import hashlib
import itertools
import json
import math
from pathlib import Path
import random


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digits(value, c, n):
    result = []
    for _ in range(n):
        result.append(value % c)
        value //= c
    require(value == 0, "coefficient row out of range")
    return result


def torus_cycle(c, labels):
    """A directed Hamilton cycle, using only positive unit increments."""
    word = []
    for j in labels:
        if not word:
            word = [j] * c
        else:
            word = (word[:-1] + [j]) * c
    return word


def source_bound(c, n):
    a, r = divmod(n, c)
    return r * c if a == 0 else (c + (c - 1) * r) * c**a


def compile_word(c, n):
    require(2 <= c <= 8 and 1 <= n <= 12, "unsupported finite replay case")
    require(c**n <= 100_000, "finite replay row capacity exceeded")
    a, r = divmod(n, c)
    sizes = [a + (i < r) for i in range(c)]
    blocks, source = [], []
    start = 0
    for size in sizes:
        labels = list(range(start, start + size))
        blocks.append(labels)
        source.extend(torus_cycle(c, labels))
        start += size
    require(len(source) == source_bound(c, n), "source invoice")
    powers = [c**j for j in range(n)]
    first, q = {}, [0] * n
    for t, j in enumerate(source):
        first.setdefault(sum(q[k] * powers[k] for k in range(n)), t)
        q[j] = (q[j] + 1) % c
    require(q == [0] * n, "unrestored source path")
    reads = [[] for _ in range(len(source))]
    for v in range(1, c**n):
        row = digits(v, c, n)
        for block in blocks:
            projection = sum(row[j] * powers[j] for j in block)
            reads[first[projection]].append(v)
    word = []
    for t, j in enumerate(source):
        word.extend(("A", v) for v in reads[t])
        word.append(("B", j))
    require(len(word) == len(source) + c * (c**n - 1), "complete invoice")
    return word, source, blocks


def check_ledger(c, n, word, modulus=None):
    """Track formal A_v z_dirty and A_v B_j x_j, without commuting maps."""
    modulus = c if modulus is None else modulus
    z = [1] + [0] * n
    outputs = [[0] * (n + 1) for _ in range(c**n)]
    for kind, index in word:
        if kind == "B":
            require(0 <= index < n, "source index")
            z[index + 1] = (z[index + 1] + 1) % modulus
        else:
            require(kind == "A" and 1 <= index < c**n, "readout index")
            row = outputs[index]
            for j in range(n + 1):
                row[j] = (row[j] + z[j]) % modulus
    require(z == [1] + [0] * n, "connector dirt or source restoration")
    for v in range(1, c**n):
        require(outputs[v] == [0] + digits(v, c, n), "output coefficient ledger")


def matvec(matrix, vector, c):
    return [sum(a * b for a, b in zip(row, vector)) % c for row in matrix]


def random_matrices(rng, count, dimension, c):
    return [[[rng.randrange(c) for _ in range(dimension)] for _ in range(dimension)]
            for _ in range(count)]


def dense_case(c, n, dimension, seed):
    word, _, _ = compile_word(c, n)
    rng = random.Random(seed)
    bmaps = random_matrices(rng, n, dimension, c)
    amaps = random_matrices(rng, c**n, dimension, c)
    # Singular, noncommuting maps are present even over composite rings.
    bmaps[0] = [[int(i == 0 and j == 1) for j in range(dimension)]
                for i in range(dimension)]
    bmaps[1] = [[int(i == 1 and j == 0) for j in range(dimension)]
                for i in range(dimension)]
    sources = [[rng.randrange(c) for _ in range(dimension)] for _ in range(n)]
    saved_sources = [row[:] for row in sources]
    injected = [matvec(bmaps[j], sources[j], c) for j in range(n)]
    z = [rng.randrange(c) for _ in range(dimension)]
    initial_z = z[:]
    outputs = [[rng.randrange(c) for _ in range(dimension)] for _ in range(c**n)]
    expected = [row[:] for row in outputs]
    for v in range(1, c**n):
        row = digits(v, c, n)
        total = [sum(row[j] * injected[j][k] for j in range(n)) % c
                 for k in range(dimension)]
        delta = matvec(amaps[v], total, c)
        expected[v] = [(x + y) % c for x, y in zip(expected[v], delta)]
    for kind, index in word:
        if kind == "B":
            delta = matvec(bmaps[index], sources[index], c)
            z = [(x + y) % c for x, y in zip(z, delta)]
        else:
            delta = matvec(amaps[index], z, c)
            outputs[index] = [(x + y) % c for x, y in zip(outputs[index], delta)]
    require(z == initial_z and sources == saved_sources, "dense restoration")
    require(outputs == expected, "dense noncommuting action")


def capacity(c, length):
    return math.comb(length + c - 1, c) - length


def counting_lower(c, n):
    """Minimum of the all-word relaxed invoice, with no floating roots."""
    m = c**n - 1
    lengths = range(c * n, source_bound(c, n) + 1, c)
    threshold = next(length for length in lengths if capacity(c, length) >= m)
    invoice = min(length + c * max(0, m - capacity(c, length)) for length in lengths)
    require(invoice == threshold, "counting threshold reduction")
    require(math.factorial(c) * m <= (threshold + c - 1)**c, "root lower bound")
    return c * m + threshold


def check_cycles():
    cases = 0
    for c in range(2, 9):
        for b in range(1, 5):
            if c**b > 5000:
                continue
            word = torus_cycle(c, list(range(b)))
            q, seen = [0] * b, set()
            for j in word:
                require(tuple(q) not in seen, "Hamilton cycle repeats early")
                seen.add(tuple(q))
                q[j] = (q[j] + 1) % c
            require(len(seen) == c**b and q == [0] * b, "Hamilton coverage")
            cases += 1
    return cases


def check_multisets():
    examined = 0
    for c, n in ((2, 2), (3, 3), (3, 4), (4, 3)):
        _, source, _ = compile_word(c, n)
        q, prefixes = [0] * n, []
        for j in source:
            prefixes.append(tuple(q))
            q[j] = (q[j] + 1) % c
        sums, pure = set(), 0
        for indices in itertools.combinations_with_replacement(range(len(source)), c):
            total = tuple(sum(prefixes[t][j] for t in indices) % c for j in range(n))
            if indices[0] == indices[-1]:
                require(not any(total), "pure repeated prefix must vanish")
                pure += 1
            if any(total):
                sums.add(total)
            examined += 1
        require(pure == len(source), "pure multiset count")
        require(len(sums) <= capacity(c, len(source)), "nonzero multiset capacity")
        require(len(sums) == c**n - 1, "small construction has full coverage")
    return examined


def check_controls():
    word, _, _ = compile_word(3, 4)
    bpos = next(i for i, op in enumerate(word) if op[0] == "B")
    apos = next(i for i, op in enumerate(word) if op[0] == "A")
    relabelled = [(kind, (index + 1) % 4 if kind == "B" else index)
                 for kind, index in word]
    misrouted = word[:]
    misrouted[apos] = ("A", 1 + misrouted[apos][1] % 80)
    controls = [word[:bpos] + word[bpos + 1:], word[:apos] + word[apos + 1:],
                relabelled, misrouted, word + [("B", 0)]]
    for control in controls:
        try:
            check_ledger(3, 4, control)
        except ValueError:
            continue
        raise ValueError("invalid literal word accepted")
    try:
        check_ledger(3, 4, word, modulus=6)
    except ValueError:
        return len(controls) + 1
    raise ValueError("wrong characteristic accepted")


def check_partitions():
    cases = 0
    # Enumerate all weak compositions in small cases, rather than sampling them.
    for c in range(2, 6):
        for n in range(1, 7):
            best = None
            for cuts in itertools.combinations(range(n + c - 1), c - 1):
                bounds = (-1,) + cuts + (n + c - 1,)
                sizes = [bounds[i + 1] - bounds[i] - 1 for i in range(c)]
                cost = sum(c**b for b in sizes if b)
                best = cost if best is None else min(best, cost)
                cases += 1
            require(best == source_bound(c, n), "balanced palette minimum")
    return cases


def main():
    totals = {"cycle_cases": check_cycles(), "partition_cases": check_partitions(),
              "multisets": check_multisets(), "negative_controls": check_controls(),
              "literal_words": 0, "outputs": 0, "calls": 0, "dense_cases": 0}
    for c, maximum in ((2, 9), (3, 8), (4, 6), (5, 5), (6, 5), (7, 4), (8, 4)):
        for n in range(1, maximum + 1):
            word, source, _ = compile_word(c, n)
            check_ledger(c, n, word)
            require(counting_lower(c, n) <= len(word), "lower bound exceeds witness")
            require(sum(op[0] == "B" for op in word) == len(source), "source call count")
            totals["literal_words"] += 1
            totals["outputs"] += c**n - 1
            totals["calls"] += len(word)
    for c in (3, 4, 6):
        for n in (3, 4):
            for dimension in (2, 3):
                dense_case(c, n, dimension, 1000 * c + 10 * n + dimension)
                totals["dense_cases"] += 1
    table = []
    for n in range(5, 9):
        length = source_bound(3, n)
        table.append({"c": 3, "n": n, "source_calls": length,
                      "readouts": 3 * (3**n - 1),
                      "calls": length + 3 * (3**n - 1),
                      "counting_lower": counting_lower(3, n)})
    package = Path(__file__).resolve().parent
    names = ("README.md", "SOURCES.json", "TASK.json", "VERIFY.json", "verify.py")
    hashes = {name: hashlib.sha256((package / name).read_bytes()).hexdigest()
              for name in names}
    receipt = {"schema_version": 1, "files_sha256": hashes, "counts": totals,
               "ternary_examples": table}
    print("PASS_FULL_COEFFICIENT_CONNECTOR " + json.dumps(totals, sort_keys=True))
    print(json.dumps(receipt, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
