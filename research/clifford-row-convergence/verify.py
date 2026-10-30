#!/usr/bin/env python3
"""Exact finite corroboration of the Clifford row-sum convergence theorem."""

import hashlib
import itertools
import json
from collections import Counter
from fractions import Fraction
from pathlib import Path


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def rank(columns: tuple[int, ...]) -> int:
    """Binary rank; callers supply at most four columns of at most four bits."""
    require(len(columns) <= 4, "rank census limited to four columns")
    pivots = [0] * 4
    result = 0
    for column in columns:
        require(0 <= column < 16, "binary column outside finite domain")
        value = column
        for bit in range(3, -1, -1):
            if not (value >> bit) & 1:
                continue
            if pivots[bit]:
                value ^= pivots[bit]
            else:
                pivots[bit] = value
                result += 1
                break
    return result


def pairing(u: int, v: int, n: int) -> int:
    mask = (1 << n) - 1
    return (((u & mask) & (v >> n)).bit_count()
            + ((v & mask) & (u >> n)).bit_count()) % 2


def gram(columns: tuple[int, ...], n: int) -> tuple[int, ...]:
    return tuple(sum(pairing(u, v, n) << i
                     for i, u in enumerate(columns)) for v in columns)


def product_factor(n: int, length: int) -> Fraction:
    require(type(n) is int and 1 <= n <= 32, "n outside 1..32")
    require(type(length) is int and 0 <= length <= 64, "invalid length")
    if length > n:
        return Fraction(0)
    answer = Fraction(1)
    for j in range(length):
        answer *= 1 - Fraction(4**j, 4**n)
    return answer


def embedding_count(n: int, k: int, half_rank: int) -> int:
    require(type(k) is int and 0 <= k <= 64, "invalid form dimension")
    require(type(half_rank) is int and 0 <= 2 * half_rank <= k,
            "invalid alternating rank")
    factor = product_factor(n, k - half_rank)
    exponent = 2 * n * k - k * (k - 1) // 2
    answer = Fraction(2)**exponent * factor
    require(answer.denominator == 1, "nonintegral embedding count")
    return answer.numerator


def alternating_forms(k: int) -> list[tuple[int, ...]]:
    require(0 <= k <= 4, "alternating census limited to dimension four")
    pairs = list(itertools.combinations(range(k), 2))
    forms = []
    for code in range(1 << len(pairs)):
        columns = [0] * k
        for bit, (i, j) in enumerate(pairs):
            if (code >> bit) & 1:
                columns[i] |= 1 << j
                columns[j] |= 1 << i
        forms.append(tuple(columns))
    return forms


def check_embeddings() -> dict[str, int]:
    checked = 0
    types = 0
    for n in (1, 2):
        for k in range(1, 2 * n + 1):
            counts: Counter[tuple[int, ...]] = Counter()
            for columns in itertools.product(range(1, 1 << (2 * n)), repeat=k):
                if rank(columns) == k:
                    counts[gram(columns, n)] += 1
                    checked += 1
            for form in alternating_forms(k):
                form_rank = rank(form)
                require(form_rank % 2 == 0, "alternating rank must be even")
                expected = embedding_count(n, k, form_rank // 2)
                require(counts[form] == expected, "embedding product mismatch")
                types += 1
    return {"ordered_embeddings": checked, "alternating_types": types}


def invertible_form_histograms() -> list[Counter[int]]:
    histograms = []
    for k in range(5):
        histogram: Counter[int] = Counter()
        for code in range(1 << (k * k)):
            columns = tuple((code >> (k * j)) & ((1 << k) - 1)
                            for j in range(k))
            if rank(columns) != k:
                continue
            symmetric = tuple(columns[j] ^ sum(
                ((columns[i] >> j) & 1) << i for i in range(k))
                for j in range(k))
            symmetric_rank = rank(symmetric)
            require(symmetric_rank % 2 == 0, "odd symmetrization rank")
            histogram[symmetric_rank // 2] += 1
        histograms.append(histogram)
    return histograms


def symplectic_orders() -> tuple[int, ...]:
    orders = [1]
    for n in range(1, 33):
        orders.append(orders[-1] * 2**(2 * n - 1) * (4**n - 1))
    return tuple(orders)


def fixed_space_counts(n: int, orders: tuple[int, ...]) -> tuple[int, ...]:
    """Rudvalis-Shinoda, recorded by Fulman-Stanton, Theorem 2.3, q=2."""
    require(1 <= n <= 32 and len(orders) == 33, "invalid distribution domain")
    counts = []
    for dimension in range(2 * n + 1):
        k, odd = divmod(dimension, 2)
        probability = sum((Fraction((-1)**i * 2**(i * (i + 1)),
                                    orders[i] * 2**(2 * i * (k + odd)))
                           for i in range(n - k - odd + 1)), Fraction(0))
        probability /= orders[k] * 2**(odd * (2 * k + 1))
        count = orders[n] * probability
        require(count.denominator == 1 and count >= 0, "invalid exact count")
        counts.append(count.numerator)
    require(sum(counts) == orders[n], "fixed-space distribution mass")
    return tuple(counts)


def limit_interval(cutoff: int) -> tuple[Fraction, Fraction]:
    require(type(cutoff) is int and 1 <= cutoff <= 64, "invalid tail cutoff")
    lower = sum((Fraction(1, 2**(k * (k + 1) // 2))
                 for k in range(1, cutoff + 1)), Fraction(0))
    first = Fraction(1, 2**((cutoff + 1) * (cutoff + 2) // 2))
    ratio = Fraction(1, 2**(cutoff + 2))
    return lower, lower + first / (1 - ratio)


def check_gap(n: int, row_sum: Fraction,
              interval: tuple[Fraction, Fraction]) -> None:
    lower, upper = interval
    require(lower < upper, "invalid limit enclosure")
    require(lower - row_sum >= Fraction(1, 2 * 4**n), "lower gap bound")
    require(upper - row_sum <= (4 + lower) / (3 * 4**n), "upper gap bound")


def check_distributions(histograms: list[Counter[int]]) -> dict[str, object]:
    orders = symplectic_orders()
    interval = limit_interval(40)
    rows = []
    normalized_checks = 0
    previous_counts: tuple[int, ...] = ()
    for n in range(1, 33):
        counts = fixed_space_counts(n, orders)
        row_sum = sum((Fraction(counts[2 * n - k], 2**(k * (2 * n + 1)))
                       for k in range(1, 2 * n + 1)), Fraction(0))
        check_gap(n, row_sum, interval)
        if rows:
            require(rows[-1] < row_sum, "strict dimension monotonicity")
        for k in range(1, 5):
            average = sum((multiplicity * product_factor(n, k - half_rank)
                           for half_rank, multiplicity in histograms[k].items()),
                          Fraction(0)) / sum(histograms[k].values())
            count = counts[2 * n - k] if k <= 2 * n else 0
            scale = Fraction(2)**(2 * n * k - k * (k - 1) // 2)
            require(count == scale * average, "normalized residual average")
            normalized_checks += 1
        for k in range(1, 2 * n - 1):
            old = Fraction(previous_counts[2 * n - 2 - k],
                           2**((2 * n - 2) * k - k * (k - 1) // 2))
            new = Fraction(counts[2 * n - k],
                           2**(2 * n * k - k * (k - 1) // 2))
            require(old <= new, "normalized-count monotonicity")
        previous_counts = counts
        rows.append(row_sum)
    return {"axis_counts": len(rows), "residual_average_cases": normalized_checks,
            "first_row_sum": str(rows[0]),
            "row_sums_sha256": hashlib.sha256(
                json.dumps([str(row) for row in rows]).encode()).hexdigest()}


def rejected(function, *arguments) -> None:
    try:
        function(*arguments)
    except ValueError:
        return
    raise ValueError("negative control was accepted")


def check_controls() -> int:
    interval = limit_interval(40)
    rejected(check_gap, 2, interval[0], interval)
    rejected(check_gap, 2, interval[0] - Fraction(2, 16), interval)
    rejected(check_gap, 2, Fraction(1, 2), tuple(reversed(interval)))
    rejected(product_factor, 0, 1)
    rejected(product_factor, 33, 1)
    rejected(product_factor, 2, -1)
    rejected(product_factor, 2, 65)
    rejected(embedding_count, 2, -1, 0)
    rejected(embedding_count, 2, 4, 3)
    rejected(embedding_count, 2, 4, -1)
    rejected(limit_interval, 0)
    rejected(limit_interval, 65)
    # Semantic mutations must differ from the literal embedding counts.
    require(embedding_count(2, 2, 0) != 2**7 * product_factor(2, 1),
            "omitted radical factor accepted")
    require(embedding_count(1, 2, 1) != 2**3 * product_factor(1, 0),
            "omitted hyperbolic factor accepted")
    require(product_factor(1, 2) == 0, "unavailable dimension not zero")
    return 15


def source_hashes() -> dict[str, str]:
    package = Path(__file__).resolve().parent
    names = ("README.md", "TASK.json", "SOURCES.json", "VERIFY.json", "verify.py")
    return {name: hashlib.sha256((package / name).read_bytes()).hexdigest()
            for name in names}


def main() -> None:
    embedding_evidence = check_embeddings()
    histograms = invertible_form_histograms()
    distribution_evidence = check_distributions(histograms)
    controls = check_controls()
    receipt = {"status": "PASS_CLIFFORD_ROW_CONVERGENCE",
               "claim_type": "scoped proof with exact finite corroboration",
               "embeddings": embedding_evidence,
               "invertible_forms": sum(sum(h.values()) for h in histograms),
               "symmetrization_histograms": [dict(sorted(h.items())) for h in histograms],
               "distribution": distribution_evidence,
               "controls": controls, "source_sha256": source_hashes()}
    print(json.dumps(receipt, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
