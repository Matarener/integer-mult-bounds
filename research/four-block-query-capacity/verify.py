"""Exact finite controls for the four-query capacity proof. Apache-2.0."""

from hashlib import sha256
import json
from pathlib import Path
import sys


MAX_RANK = 24
MAX_DIM = 64


def need(condition, message):
    if not condition:
        raise ValueError(message)


def eye(n):
    return tuple(1 << i for i in range(n))


def add(a, b):
    return tuple(x ^ y for x, y in zip(a, b, strict=True))


def mul(a, b):
    out = []
    for row in a:
        value = 0
        for j in range(len(b)):
            if row >> j & 1:
                value ^= b[j]
        out.append(value)
    return tuple(out)


def independent_indices(rows, width):
    pivots = [0] * width
    indices = []
    for index, row in enumerate(rows):
        value = row
        for bit in range(width - 1, -1, -1):
            if value >> bit & 1:
                if pivots[bit]:
                    value ^= pivots[bit]
                else:
                    pivots[bit] = value
                    indices.append(index)
                    break
    return indices


def rank(rows, width):
    return len(independent_indices(rows, width))


def inverse(rows):
    n = len(rows)
    work = [row | (1 << (n + i)) for i, row in enumerate(rows)]
    for col in range(n):
        pivot = next((i for i in range(col, n) if work[i] >> col & 1), None)
        need(pivot is not None, "singular constant basis")
        work[col], work[pivot] = work[pivot], work[col]
        for i in range(n):
            if i != col and work[i] >> col & 1:
                work[i] ^= work[col]
    result = tuple(row >> n for row in work)
    need(mul(rows, result) == eye(n), "inverse invariant")
    return result


def factor(rows, width):
    """Return a full-rank factorization A B of a binary rectangular matrix."""
    columns = tuple(sum(((row >> j) & 1) << i for i, row in enumerate(rows))
                    for j in range(width))
    selected = independent_indices(columns, len(rows))
    r = len(selected)
    left = tuple(sum(((row >> j) & 1) << k for k, j in enumerate(selected))
                 for row in rows)
    pivots = independent_indices(left, r)
    right = mul(inverse(tuple(left[i] for i in pivots)),
                tuple(rows[i] for i in pivots))
    need(mul(left, right) == rows, "rank factorization invariant")
    return left, right


def construct(r, n):
    need(1 <= r <= MAX_RANK, "rank outside finite constructor range")
    need(2 <= n <= MAX_DIM and n % 2 == 0, "dimension must be positive and even")
    need(n <= 2 * (4 * r // 3), "four-query capacity exceeded")
    layers = [[0] * n for _ in range(4)]
    for pair in range(n // 2):
        active = [i for i in range(4) if i != pair % 4]
        a, b = 2 * pair, 2 * pair + 1
        layers[active[0]][a] = 1 << b
        layers[active[1]][b] = 1 << a
        layers[active[2]][a] = 1 << b
    return tuple(tuple(layer) for layer in layers), tuple(1 << (i ^ 1) for i in range(n))


def quotient_check(layers, final, r):
    """Replay in F2[Q]/(Q^2-1), keeping both coefficients separately."""
    n = len(final)
    constant, odd = eye(n), (0,) * n
    for nilpotent in layers:
        need(mul(nilpotent, nilpotent) == (0,) * n, "paid matrix is not square-zero")
        need(rank(nilpotent, n) <= r, "paid rank cap exceeded")
        constant, odd = add(constant, mul(nilpotent, odd)), add(odd, mul(nilpotent, constant))
    endpoint = mul(final, constant), mul(final, odd)
    need(endpoint == ((0,) * n, eye(n)), "endpoint is not Q times identity")
    return endpoint


def lifted_check(layers, final):
    """Independently replay every original coefficient bit as a 2n-bit map."""
    n = len(final)
    rows = [1 << i for i in range(2 * n)]
    for nilpotent in layers:
        old = tuple(rows)
        for i in range(n):
            for j in range(n):
                if nilpotent[i] >> j & 1:
                    rows[i] ^= old[n + j]
                    rows[n + i] ^= old[j]
    old = tuple(rows)
    result = []
    for half in range(2):
        for row in final:
            value = 0
            for j in range(n):
                if row >> j & 1:
                    value ^= old[half * n + j]
            result.append(value)
    expected = tuple(1 << (n + i) for i in range(n)) + eye(n)
    need(tuple(result) == expected, "lifted input-column endpoint failed")


def normalized_queries(layers, final):
    n = len(final)
    suffix = final
    queries = []
    for nilpotent in reversed(layers):
        query = mul(mul(suffix, nilpotent), inverse(suffix))
        queries.append(query)
        suffix = mul(suffix, add(eye(n), nilpotent))
    need(suffix == eye(n), "constant endpoint is not identity")
    total = (0,) * n
    for query in queries:
        need(mul(query, query) == (0,) * n, "normalized square-zero invariant")
        total = add(total, query)
    need(total == eye(n), "normalized queries do not sum to identity")
    return tuple(queries)


def gram_check(queries, r):
    n = len(queries[0])
    factors = [factor(query, n) for query in queries]
    ranks = [len(right) for _, right in factors]
    s = sum(ranks)
    u = [0] * n
    v = []
    offset = 0
    for (left, right), ri in zip(factors, ranks, strict=True):
        need(mul(right, left) == (0,) * ri, "nilpotent factor pairing")
        u = [row ^ (part << offset) for row, part in zip(u, left, strict=True)]
        v.extend(right)
        offset += ri
    u, v = tuple(u), tuple(v)
    need(mul(u, v) == eye(n), "UV must be identity")
    k = mul(v, u)
    cmat = add(eye(s), k)
    need(mul(k, k) == k and rank(cmat, s) == s - n, "Gram complement invariant")
    a, b = factor(cmat, s)
    c = len(b)
    need(mul(b, a) == eye(c), "complement factor pairing")
    total_e, total_f = (0,) * c, (0,) * c
    offset = 0
    for ri in ranks:
        ai = a[offset:offset + ri]
        bi = tuple((row >> offset) & ((1 << ri) - 1) for row in b)
        need(mul(ai, bi) == eye(ri), "complement diagonal block")
        e = mul(bi, ai)
        f = add(eye(c), e)
        need(mul(e, e) == e and rank(e, c) == ri, "block idempotent rank")
        need(rank(f, c) == c - ri, "complementary block rank")
        total_e, total_f = add(total_e, e), add(total_f, f)
        offset += ri
    need(total_e == eye(c) and total_f == eye(c), "four-block complementary sum")
    need(3 * n <= 2 * s <= 8 * r, "sharp rank inequalities")
    return s, c


def exhaustive_square_zero():
    summaries = []
    for n in (2, 3, 4):
        by_rank = [[] for _ in range(n // 2 + 1)]
        mask = (1 << n) - 1
        for encoded in range(1 << (n * n)):
            rows = tuple((encoded >> (i * n)) & mask for i in range(n))
            if mul(rows, rows) == (0,) * n:
                ri = rank(rows, n)
                need(ri <= n // 2, "square-zero half-rank bound")
                by_rank[ri].append(encoded)
        target = sum(1 << (i * n + i) for i in range(n))
        feasible = []
        for r in range(1, n // 2 + 1):
            choices = [x for part in by_rank[:r + 1] for x in part]
            pair_sums = {a ^ b for a in choices for b in choices}
            found = any((target ^ pair) in pair_sums for pair in pair_sums)
            need(found == (n % 2 == 0 and n <= 2 * (4 * r // 3)), "exhaustive capacity mismatch")
            feasible.append(found)
        summaries.append({"dimension": n, "square_zero_counts_by_rank": [len(x) for x in by_rank],
                          "four_summand_feasible_by_cap": feasible})
    return summaries


def controls():
    count = 0
    for r, n in ((0, 2), (25, 2), (1, 0), (1, 3), (1, 4), (2, 6), (24, 66)):
        try:
            construct(r, n)
        except ValueError:
            count += 1
        else:
            raise ValueError("invalid constructor request accepted")
    layers, final = construct(3, 8)
    for kind in range(3):
        bad = list(layers)
        if kind == 0:
            bad[0] = (0,) * 8
        elif kind == 1:
            bad[0] = eye(8)
        try:
            quotient_check(tuple(bad), final, 2 if kind == 2 else 3)
        except ValueError:
            count += 1
        else:
            raise ValueError("mutated word accepted")
    return count


def finite_constructions():
    fixtures = gram_fixtures = input_columns = 0
    examples = []
    for r in range(1, MAX_RANK + 1):
        cap = 2 * (4 * r // 3)
        for n in range(2, cap + 1, 2):
            layers, final = construct(r, n)
            quotient_check(layers, final, r)
            lifted_check(layers, final)
            input_columns += 2 * n
            fixtures += 1
            if n <= 16:
                s, c = gram_check(normalized_queries(layers, final), r)
                need(s == 3 * n // 2 and c == n // 2, "attaining total rank")
                gram_fixtures += 1
        if r <= 6:
            examples.append({"rank_cap": r, "maximum_dimension": cap})
    for r in range(1, 5):
        n = 2 * (4 * r // 3)
        layers, final = construct(r, n)
        basis = list(eye(n))
        for i in range(n - 1):
            basis[i] ^= basis[i + 1]
        basis, inv = tuple(basis), inverse(tuple(basis))
        mixed = tuple(mul(mul(basis, x), inv) for x in layers)
        mixed_final = mul(mul(basis, final), inv)
        quotient_check(mixed, mixed_final, r)
        lifted_check(mixed, mixed_final)
        gram_check(normalized_queries(mixed, mixed_final), r)
    return {"construction_fixtures": fixtures, "original_coefficient_columns": input_columns,
            "gram_fixtures": gram_fixtures, "mixed_basis_fixtures": 4, "examples": examples}


def main():
    need(sys.version_info >= (3, 12), "CPython 3.12 or newer required")
    need(len(sys.argv) == 1, "no command-line arguments accepted")
    receipt = finite_constructions()
    receipt["exhaustive_square_zero"] = exhaustive_square_zero()
    receipt["rejecting_controls"] = controls()
    package = Path(__file__).resolve().parent
    files = sorted(package.iterdir())
    need(len(files) <= 16, "unexpected package size")
    receipt["sha256"] = {p.name: sha256(p.read_bytes()).hexdigest()
                         for p in files if p.is_file()}
    receipt["status"] = "PASS_FOUR_BLOCK_QUERY_CAPACITY"
    print(json.dumps(receipt, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
