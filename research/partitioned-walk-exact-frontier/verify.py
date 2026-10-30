#!/usr/bin/env python3
"""Exact checks for the complete five-source partitioned readout frontier.

New checker by apoursh with substantial OpenAI Codex assistance, Apache-2.0.
The even-per-port model, path tariff and Q7--Q9 values retain Wentao Li
(PR2779), Nick Petalas (PR6036) and their credited predecessor lineage.
The all-size result rests on PROOF.md; these finite checks corroborate it.
"""
from __future__ import annotations

from collections import Counter
from itertools import combinations
from math import comb
from pathlib import Path
from types import ModuleType
import hashlib
import json

INF = 10 ** 6
BASIS = (0, 1, 2, 4, 8, 16)
EXPECTED_HISTOGRAMS = {
    8: {20: 90, 22: 160, 25: 75},
    9: {21: 60, 22: 60, 23: 810, 25: 660, 27: 750, 28: 260},
}
WITNESSES = {
    7: ((0, 1), (0, 2, 4, 8, 16)),
    8: ((0, 10), (0, 22, 5, 31, 24, 20)),
    9: ((0, 3), (0, 18, 1, 5, 11, 20, 27)),
    10: ((0, 7), (0, 1, 2, 4, 8, 16, 30, 31)),
    11: ((0, 7), (0, 1, 2, 4, 8, 16, 29, 30, 31)),
    12: ((0, 1), (0, 1, 2, 4, 8, 16, 3, 5, 6, 31)),
}
FRONTIER = {7: 112, 8: 92, 9: 80, 10: 72, 11: 66, 12: 62}


def need(condition, message):
    if not condition:
        raise ValueError(message)


def span(values):
    result = {0}
    for value in values:
        result |= {x ^ value for x in result}
    return result


def pair_counts(points):
    return Counter(a ^ b for a, b in combinations(points, 2) if a != b)


def kernel_words(points):
    """Literal dependencies of nonzero columns; no Gaussian elimination."""
    words = []
    for bits in range(1 << len(points)):
        value = 0
        for i, point in enumerate(points):
            if bits >> i & 1:
                value ^= point
        if value == 0:
            words.append(bits)
    return words


def normalized_census(n, basis=BASIS):
    need(len(basis) == 6 and basis[0] == 0 and len(span(basis)) == 32,
         "normalization must retain zero and a full five-dimensional basis")
    need(n in (8, 9), "normalized census outside declared domains")
    candidates = tuple(x for x in range(32) if x not in basis)
    histogram = Counter()
    multiplicity_cases = Counter()
    for extra in combinations(candidates, n - 6):
        points = basis + extra
        counts = pair_counts(points)
        histogram[len(counts)] += 1
        quadruples = sum(a ^ b ^ c ^ d == 0
                         for a, b, c, d in combinations(points, 4))
        need(sum(comb(m, 2) for m in counts.values()) == 3 * quadruples,
             "pair-collision/parallelogram identity failed")
        code = kernel_words(tuple(point | 32 for point in points))
        need(len(code) == 1 << (n - 6), "affine kernel dimension changed")
        need(all(word.bit_count() >= 4 and word.bit_count() % 2 == 0
                 for word in code[1:]), "affine kernel has forbidden weight")
        need(sum(word.bit_count() for word in code) <= n * (1 << (n - 7)),
             "affine-code total-weight bound failed")
        need(sum(word.bit_count() == 4 for word in code) == quadruples,
             "affine weight-four words do not count parallelograms")
        if n == 8:
            need(quadruples >= 1 and len(counts) <= 25, "eight-point cap failed")
        else:
            largest = max(counts.values())
            if largest >= 3:
                multiplicity_cases["three_pairs"] += 1
                difference = next(d for d, m in counts.items() if m >= 3)
                pairs = [(a, b) for a, b in combinations(points, 2)
                         if a ^ b == difference][:3]
                six = tuple(x for pair in pairs for x in pair)
                need(len(set(six)) == 6 and len(pair_counts(six)) <= 7,
                     "three translated pairs violate their seven-difference cap")
            else:
                multiplicity_cases["at_most_two_pairs"] += 1
                need(quadruples >= 3 and 36 - len(counts) == 3 * quadruples,
                     "nine-point low-multiplicity argument failed")
            need(len(counts) <= 28, "nine-point cap failed")
    need(sum(histogram.values()) == comb(26, n - 6), "incomplete basis census")
    need(dict(histogram) == EXPECTED_HISTOGRAMS[n], "normalized histogram changed")
    return {"representatives": sum(histogram.values()),
            "histogram": dict(sorted(histogram.items())),
            "proof_cases": dict(sorted(multiplicity_cases.items()))}


def parity_tables(slots):
    """Chronological include/exclude DP, with separate parity in this port."""
    table = [[INF] * 32 for _ in range(2)]
    table[0][0] = 0
    for point in slots:
        nxt = [row[:] for row in table]
        for parity in range(2):
            for mask, cost in enumerate(table[parity]):
                nxt[parity ^ 1][mask ^ point] = min(
                    nxt[parity ^ 1][mask ^ point], cost + 1)
        table = nxt
    return table


def subset_oracle(slots):
    """Every subset, visited in Gray order; independent of the DP recurrence."""
    out = [INF] * 32
    out[0] = 0
    mask = weight = 0
    for i in range(1, 1 << len(slots)):
        bit = i & -i
        mask ^= slots[bit.bit_length() - 1]
        gray = i ^ (i >> 1)
        weight += 1 if gray & bit else -1
        if weight % 2 == 0 and weight < out[mask]:
            out[mask] = weight
    return out


def convolve(tables):
    acc = [INF] * 32
    acc[0] = 0
    for table in tables:
        nxt = [INF] * 32
        for a, ca in enumerate(acc):
            for b, cb in enumerate(table):
                nxt[a ^ b] = min(nxt[a ^ b], ca + cb)
        acc = nxt
    return acc


def pair_port_oracle(left, right):
    """Literal two-port minimization, not the chronological convolution."""
    return [min(left[a] + right[a ^ target] for a in range(32))
            for target in range(32)]


def valid_walk(slots):
    return (isinstance(slots, tuple) and len(slots) >= 2 and slots[0] == 0
            and all(type(x) is int and 0 <= x < 32 for x in slots)
            and all(a != b for a, b in zip(slots, slots[1:] + (0,))))


def witness_receipt(q, walks, expected_r, brute=True):
    need(len(walks) >= 2 and sum(map(len, walks)) == q, "witness partition")
    need(all(valid_walk(walk) for walk in walks), "zero edge or invalid walk")
    tables = [parity_tables(walk)[0] for walk in walks]
    if brute:
        direct = [subset_oracle(walk) for walk in walks]
        need(tables == direct, "literal even-subset oracle disagrees with DP")
        need(convolve(tables) == pair_port_oracle(*direct),
             "independent port minimization disagrees")
    values = convolve(tables)
    need(all(value < INF for value in values), "witness does not cover")
    r = sum(values[1:])
    need(r == expected_r, f"wrong readout: Q={q}, actual={r}, claimed={expected_r}")
    pairs = set().union(*(pair_counts(walk) for walk in walks))
    need({m for m in range(1, 32) if values[m] == 2} == pairs,
         "cost-two union differs from literal readout")
    x = sum(2 * ((a ^ b).bit_count() - 1) for walk in walks
            for a, b in zip(walk, walk[1:] + (0,)))
    return {"walks": walks, "R": r, "path_X": x, "tariff": 38 * q + 2 * r + 2 * x,
            "readout_histogram": dict(sorted(Counter(values[1:]).items()))}


def partitions(total, cap=None):
    if cap is None:
        cap = total
    if total == 0:
        yield ()
    for first in range(min(total, cap), 1, -1):
        for rest in partitions(total - first, first):
            yield (first,) + rest


def difference_cap(n):
    if n == 8:
        return 25
    if n == 9:
        return 28
    return min(31, comb(n, 2))


def partition_receipts():
    result = {}
    for q in range(4, 13):
        rows = [parts for parts in partitions(q) if len(parts) >= 2]
        covering = [parts for parts in rows if sum(n - 1 for n in parts) >= 5]
        if q < 7:
            need(not covering, "below-seven cover violates dimension bound")
            result[q] = {"partitions": len(rows), "covering_by_rank": 0}
            continue
        cap = max(min(31, sum(difference_cap(n) for n in parts)) for parts in covering)
        pair_floor = max(62, 124 - 2 * cap)
        if q == 7:
            need(set(covering) == {(5, 2), (4, 3)}, "Q7 rank-tight partitions changed")
            for parts in covering:
                # A covering Q7 word has five independent nonzero labels in
                # disjoint port spans. GL normalization sends them to this basis.
                start = 0
                walks = []
                for n in parts:
                    walks.append((0,) + tuple(1 << i for i in range(start, start + n - 1)))
                    start += n - 1
                need(sum(convolve([parity_tables(w)[0] for w in walks])[1:]) == 112,
                     "rank-tight Q7 structural identity")
                need(sum(16 * n for n in parts) == 112, "Q7 binomial weight identity")
        else:
            need(pair_floor == FRONTIER[q], "partition floor disagrees with sharp frontier")
        result[q] = {"partitions": len(rows), "covering_by_rank": len(covering),
                     "pair_sum_cap": cap, "pair_floor": pair_floor,
                     "sharp_R": FRONTIER[q]}
    return result


def rejected(action):
    try:
        action()
    except ValueError:
        return True
    return False


def controls(censuses):
    damaged = dict(EXPECTED_HISTOGRAMS[8])
    damaged[25] -= 1
    controls = {
        "corrupted_histogram": rejected(lambda: need(
            censuses[8]["histogram"] == damaged, "forged histogram")),
        "dropped_basis_axis": rejected(lambda: normalized_census(8, BASIS[:-1])),
        "false_Q10_readout_66": rejected(lambda: witness_receipt(10, WITNESSES[10], 66, False)),
        "false_Q11_readout_62": rejected(lambda: witness_receipt(11, WITNESSES[11], 62, False)),
        "zero_edge_padding": rejected(lambda: witness_receipt(
            13, ((0, 1, 1), WITNESSES[12][1]), 62, False)),
        "changed_witness": rejected(lambda: witness_receipt(
            10, ((0, 1), WITNESSES[10][1]), 72, False)),
    }
    relaxed = []
    for walk in WITNESSES[7]:
        even, odd = parity_tables(walk)
        relaxed.append([min(a, b) for a, b in zip(even, odd)])
    need(sum(convolve(relaxed)[1:]) != 112, "odd-parity control failed to discriminate")
    controls["odd_parity_mixing"] = rejected(lambda: need(
        sum(convolve(relaxed)[1:]) == 112, "independent port dirt not restored"))
    need(len(controls) == 7 and all(controls.values()), "one failure control did not reject")
    return controls


def main():
    censuses = {n: normalized_census(n) for n in (8, 9)}
    # Source-load the checked sibling, including under -I/-B/-O, so stale pyc
    # files and the caller's module search path cannot replace the oracle.
    path = Path(__file__).with_name("oracle.py")
    module = ModuleType("partitioned_walk_kernel_oracle")
    exec(compile(path.read_bytes(), str(path), "exec"), module.__dict__)
    oracle = module.run_oracle()
    need(oracle["maxima"] == {"8": 25, "9": 28}, "kernel-code maxima disagree")
    witnesses = {q: witness_receipt(q, ws, FRONTIER[q]) for q, ws in WITNESSES.items()}
    padding = {}
    long = WITNESSES[12][1]
    for q in range(13, 33):
        # Insert an existing support label unequal to both ends of the first
        # edge. This is the proof's padding rule, with no zero edge or new point.
        inserted = 1 if long[1] != 1 else 2
        long = (0, inserted) + long[1:]
        need(set(long) == set(WITNESSES[12][1]), "padding changed support")
        padding[q] = witness_receipt(q, ((0, 1), long), 62, brute=False)
    report = {"normalized_censuses": censuses, "kernel_oracle": oracle,
              "partitions": partition_receipts(), "witnesses": witnesses,
              "padding_witnesses": padding, "controls": controls(censuses),
              "scope": "finite corroboration of the written all-Q proof; no new kappa"}
    print(json.dumps(report, sort_keys=True))
    canonical = json.dumps(report, sort_keys=True, separators=(",", ":")).encode("utf-8")
    print("RESULT_SHA256=" + hashlib.sha256(canonical).hexdigest())
    print("PASS_PARTITIONED_WALK_EXACT_FRONTIER normalized_supports=2925"
          " witnesses=26 controls=7 Q10_R=72 Q11_R=66 Q_ge_12_R=62 no_new_kappa")


if __name__ == "__main__":
    main()
