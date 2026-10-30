"""Exact finite corroboration of the shared-column minor theorem. Apache-2.0."""

from fractions import Fraction
from hashlib import sha256
from itertools import permutations, product
import json
from math import prod
from pathlib import Path
import sys


def require(condition, message):
    if not condition:
        raise ValueError(message)


def add(a, b, q):
    return a ^ b if q == 4 else (a + b) % q


def multiply(a, b, q):
    if q != 4:
        return a * b % q
    value = 0
    for bit in range(2):
        if b & (1 << bit):
            value ^= a << bit
    if value & 4:
        value ^= 7  # F_2[x]/(x^2+x+1).
    return value


def inverse(a, q):
    require(0 < a < q and q in (2, 3, 4), "invalid inverse input")
    for b in range(1, q):
        if multiply(a, b, q) == 1:
            return b
    raise ValueError("not a field element")


def dot(a, b, q):
    value = 0
    for x, y in zip(a, b, strict=True):
        value = add(value, multiply(x, y, q), q)
    return value


def matrix_rank(rows, q):
    work = [list(row) for row in rows]
    height, width = len(work), len(work[0])
    pivot = 0
    for column in range(width):
        found = next((i for i in range(pivot, height) if work[i][column]), None)
        if found is None:
            continue
        work[pivot], work[found] = work[found], work[pivot]
        scale = inverse(work[pivot][column], q)
        work[pivot] = [multiply(x, scale, q) for x in work[pivot]]
        for i in range(height):
            if i != pivot:
                factor = work[i][column]
                for j in range(width):
                    term = multiply(factor, work[pivot][j], q)
                    work[i][j] = add(work[i][j], term if q == 4 else -term, q)
        pivot += 1
        if pivot == height:
            break
    return pivot


def determinant(rows, q):
    size = len(rows)
    value = 0
    for perm in permutations(range(size)):
        term = 1
        for i in range(size):
            term = multiply(term, rows[i][perm[i]], q)
        inversions = sum(perm[j] > perm[i] for i in range(size) for j in range(i))
        if inversions % 2 and q != 4:
            term = -term
        value = add(value, term, q)
    return value


def projective_vectors(q, dimension):
    points = []
    for vector in product(range(q), repeat=dimension):
        first = next((a for a in vector if a), None)
        if first == 1:
            points.append(vector)
    require(len(points) == (q**dimension - 1) // (q - 1), "projective coverage")
    return tuple(points)


def predicted(q, m, k, budget):
    require(q in (2, 3, 4) and 1 <= k < m <= 8, "unsupported formula domain")
    require(1 <= budget <= q + 2, "invalid choice budget")
    t = m - k + 1
    total = prod(q**m - q**j for j in range(k))
    prefix = prod(q**k - q**j for j in range(k - 1))
    coefficient = Fraction(prefix * q ** (k * t - 2) * (q - 1), total)
    return 1 - coefficient * max(0, q + 1 - budget)


def bad_mask(rows, q, points):
    k = len(rows)
    mask = 0
    for index, vector in enumerate(points):
        minor = [tuple(row[: k - 1]) + (dot(row[k - 1 :], vector, q),) for row in rows]
        if determinant(minor, q) == 0:
            mask |= 1 << index
    return mask


def family_counts(frequencies, number):
    counts = [0] * (1 << number)
    for family in range(1, 1 << number):
        counts[family] = sum(count for mask, count in enumerate(frequencies) if mask & family)
    return counts


def check_families(counts, points, q, m, k, total):
    maxima = {}
    witnesses = {}
    for budget in range(1, len(points) + 1):
        eligible = [i for i in range(1, len(counts)) if i.bit_count() <= budget]
        maximum = max(counts[i] for i in eligible)
        require(Fraction(maximum, total) == predicted(q, m, k, min(budget, q + 2)),
                "wrong sharp higher-rank frontier")
        maxima[str(budget)] = maximum
        witnesses[str(budget)] = next(i for i in eligible if counts[i] == maximum)
    return maxima, witnesses


def row_census(q, m, k):
    points = projective_vectors(q, m - k + 1)
    frequencies = [0] * (1 << len(points))
    prefix_deficient = 0
    total = 0
    for entries in product(range(q), repeat=k * m):
        rows = tuple(entries[i * m : (i + 1) * m] for i in range(k))
        if matrix_rank(rows, q) != k:
            continue
        total += 1
        mask = bad_mask(rows, q, points)
        frequencies[mask] += 1
        if matrix_rank(tuple(row[: k - 1] for row in rows), q) < k - 1:
            prefix_deficient += 1
            require(mask == len(frequencies) - 1, "deficient prefix must fail every test")
    require(total == prod(q**m - q**j for j in range(k)), "full-row-rank count")
    t = m - k + 1
    good_prefix = prod(q**k - q**j for j in range(k - 1)) * q ** ((k - 1) * t) * (q**t - 1)
    require(total - prefix_deficient == good_prefix, "prefix-deficiency count")
    counts = family_counts(frequencies, len(points))
    maxima, witnesses = check_families(counts, points, q, m, k, total)
    return {"q": q, "m": m, "k": k, "matrices": total,
            "prefix_deficient": prefix_deficient, "families": len(counts) - 1,
            "max_bad_counts": maxima, "witness_family_masks": witnesses,
            "frequency_sha256": sha256(json.dumps(frequencies).encode()).hexdigest()}, frequencies


def gl_census(q, expected_frequencies):
    m, k = 3, 2
    points = projective_vectors(q, 2)
    frequencies = [0] * (1 << len(points))
    for entries in product(range(q), repeat=9):
        rows = tuple(entries[3 * i : 3 * i + 3] for i in range(3))
        if determinant(rows, q) == 0:
            continue
        require(matrix_rank(rows, q) == 3, "GL determinant/rank disagreement")
        frequencies[bad_mask(rows[:k], q, points)] += 1
    completions = q**3 - q**2
    require(frequencies == [completions * x for x in expected_frequencies],
            "literal GL fibers are not equal")
    return {"q": q, "dimension": m, "matrices": sum(frequencies),
            "completions_per_top_frame": completions}


def controls():
    rejected = 0
    for args in ((1, 3, 2, 1), (6, 3, 2, 1), (2, 2, 2, 1),
                 (2, 3, 0, 1), (2, 9, 2, 1), (2, 3, 2, 0), (2, 3, 2, 5)):
        try:
            predicted(*args)
        except ValueError:
            rejected += 1
        else:
            raise ValueError("out-of-domain formula accepted")
    require(multiply(2, 2, 4) == 3 and multiply(2, 3, 4) == 1, "F4 is not Z/4")
    require(determinant(((1, 2), (3, 1)), 4) == 0, "F4 determinant control")
    require(predicted(2, 3, 2, 1) == Fraction(3, 7), "one-choice boundary")
    require(predicted(2, 3, 2, 2) == Fraction(5, 7), "two-choice boundary")
    require(predicted(2, 3, 2, 3) == predicted(2, 3, 2, 4) == 1, "saturation")
    require(predicted(2, 3, 2, 2) != Fraction(2, 3), "shared deficiency cannot be omitted")
    require(predicted(2, 3, 2, 2) != 2 * predicted(2, 3, 2, 1), "union bound not sharp")
    return {"invalid_domains_rejected": rejected, "semantic_comparisons": 7}


def main():
    require(len(sys.argv) == 1, "this fixed verifier accepts no arguments")
    cases = []
    gl_cases = []
    for q, m, k in ((2, 3, 2), (3, 3, 2), (4, 3, 2), (2, 4, 2), (2, 4, 3)):
        result, frequencies = row_census(q, m, k)
        cases.append(result)
        if m == 3 and q in (2, 3):
            gl_cases.append(gl_census(q, frequencies))
    receipt = {"status": "PASS_COMMON_PREFIX_MINOR_FRONTIER", "claim_type": "scoped proof",
               "row_censuses": cases, "literal_GL_censuses": gl_cases, "controls": controls(),
               "python": sys.version, "no_new_kappa": True}
    package = Path(__file__).resolve().parent
    receipt["sha256"] = {}
    for name in ("README.md", "PROOF.md", "TASK.json", "SOURCES.json", "VERIFY.json", "verify.py"):
        with (package / name).open("rb") as handle:
            data = handle.read(262145)
        require(len(data) <= 262144, "package file exceeds read bound")
        receipt["sha256"][name] = sha256(data).hexdigest()
    print(json.dumps(receipt, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
