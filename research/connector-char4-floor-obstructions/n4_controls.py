#!/usr/bin/env python3
"""Bounded standard-library controls for the characteristic-four upper bound."""

from collections import defaultdict
from itertools import combinations, combinations_with_replacement, product
import json
from math import comb
from random import Random

# Each coordinate occupies one nibble. A four-prefix sum has coordinate
# digit at most twelve, so addition cannot carry into another coordinate.
# Bit one of each nibble detects residues two or three modulo four.


def require(condition, message):
    if not condition:
        raise ValueError(message)


def packed_prefixes(word, k):
    require(1 <= k <= 19, "control source range")
    require(len(word) == 4 * k, "control word length")
    require(all(word.count(j) == 4 for j in range(k)), "source multiplicities")
    values = []
    counts = [0] * k
    for symbol in word:
        values.append(sum(count << (4 * j) for j, count in enumerate(counts)))
        counts[symbol] = (counts[symbol] + 1) % 4
    require(all(count == 0 for count in counts), "restoration")
    low_mask = sum(1 << (4 * j) for j in range(k))
    r = 4 * k - len({value & low_mask for value in values})
    return values, r


def cube_cap(k, r):
    small = min(k, r // 2)
    return k + small + (k - small) // 4


def pair_graphs(word, k):
    events = [[] for _ in range(k)]
    y, xy, full = set(), set(), set()
    for b, symbol in enumerate(word[:-1], 1):
        previous = events[symbol]
        if previous:
            full.add((b - 1, b))
        for a in previous:
            y.add((a - 1, b))
            xy.add((a - 1, b))
            xy.add((a, b))
            full.add((a - 1, b))
            full.add((a, b))
        previous.append(b)
    return y, xy, full


def graph_degrees(graph, length):
    degrees = [0] * length
    for a, b in graph:
        degrees[a] += 1
        degrees[b] += 1
    return max(degrees), sum(d * (d - 1) // 2 for d in degrees)


def inspect_graph_cube(word, k, offsets):
    values, r = packed_prefixes(word, k)
    families = pair_graphs(word, k)
    for graph, degree, wedges in zip(families, (6, 9, 10), (22 * k, 70 * k, 108 * k)):
        actual_degree, actual_wedges = graph_degrees(graph, 4 * k)
        require(actual_degree <= degree, "maximum degree")
        require(actual_wedges <= wedges, "rank wedge bound")
    require(len(families[0]) == 6 * k - 3, "Y pair count")
    require(len(families[1]) >= 12 * k - 6 - 2 * r, "XY pair count")
    low = sum(1 << (4 * j) for j in range(k))
    retained, seen = set(), set()
    for index, value in enumerate(values):
        if value & low not in seen:
            retained.add(index)
            seen.add(value & low)
    induced = {(a, b) for a, b in families[2] if a in retained and b in retained}
    require(len(induced) >= 15 * k - 7 - 13 * r, "retained full pair count")
    for offset in offsets:
        actual = sum(not ((value + offset) & (2 * low)) for value in values)
        require(actual <= cube_cap(k, r), "strengthened cyclic cube cap")
    return len(offsets)


def small_graph_cube_controls():
    checked, words = 0, 0
    for k in (2, 3):
        offsets = tuple(sum(x << (4 * j) for j, x in enumerate(v))
                        for v in product(range(4), repeat=k))
        positions = tuple(range(4 * k))
        for zero in combinations(positions, 4):
            rest = tuple(t for t in positions if t not in zero)
            choices = (rest,) if k == 2 else combinations(rest, 4)
            for one in choices:
                word = [2] * (4 * k)
                for t in zero:
                    word[t] = 0
                for t in one:
                    word[t] = 1
                checked += inspect_graph_cube(word, k, offsets)
                words += 1
    return words, checked


def large_graph_cube_controls():
    rng = Random(1020230)
    checked = 0
    for k in (4, 9, 18, 19):
        for _ in range(1000):
            word = [j for j in range(k) for _ in range(4)]
            rng.shuffle(word)
            offsets = tuple(sum(rng.randrange(4) << (4 * j) for j in range(k))
                            for _ in range(100))
            checked += inspect_graph_cube(word, k, offsets)
    return checked


def full_components(full_values, k):
    labels = {}
    count = 0
    for value in full_values:
        if value in labels:
            continue
        queue = [value]
        labels[value] = count
        for _ in range(len(full_values)):
            if not queue:
                break
            current = queue.pop()
            for j in range(k):
                neighbor = current ^ (2 << (4 * j))
                if neighbor in full_values and neighbor not in labels:
                    labels[neighbor] = count
                    queue.append(neighbor)
        require(not queue, "component work bound")
        count += 1
    return labels, count


def triple_classes(values, k):
    low = sum(1 << (4 * j) for j in range(k))
    prefix_parity = {value & low for value in values}
    groups = defaultdict(set)
    triples = []
    for indices in combinations(range(len(values)), 3):
        full = sum(values[t] for t in indices) & (3 * low)
        parity = full & low
        if parity not in prefix_parity:
            groups[parity].add(full)
            triples.append((indices, full))
    full_values = set().union(*groups.values()) if groups else set()
    labels, count = full_components(full_values, k)
    return groups, full_values, labels, count, triples


def axis_colex_controls(k, values, r, labels, count, triples):
    axes = {2 << (4 * j) for j in range(k)}
    deleted = {b for b in range(len(values))
               if any(values[a] ^ values[b] in axes for a in range(b))}
    leaders = {}
    for indices, full in triples:
        encoded = sum(1 << t for t in indices)
        label = labels[full]
        if label not in leaders or encoded < leaders[label]:
            leaders[label] = encoded
    forbidden = sum(1 << t for t in deleted)
    require(all(not leader & forbidden for leader in leaders.values()), "axis colex leader")
    selected = set(sorted(deleted)[:4])
    q = len(selected)
    n = len(values) - q
    edge_lower = max(0, 12 * k - 6 - 2 * r - 9 * q)
    bound = comb(n, 3) - edge_lower * (n - 2) + min(8 * edge_lower, 70 * k)
    require(count <= bound, "axis-deletion component count")


def inspect_incidence(word, k):
    values, r = packed_prefixes(word, k)
    low = sum(1 << (4 * j) for j in range(k))
    groups, full_values, labels, xcomp, triples = triple_classes(values, k)
    cap = cube_cap(k, r)
    incidences = 0
    for parity, group in groups.items():
        components = len({labels[value] for value in group})
        eligible = {t for t, prefix in enumerate(values)
                    if any(not ((prefix + full) & (2 * low)) for full in group)}
        require(len(eligible) <= 3 * len(group) + (cap - 3) * components,
                "free-slab component count")
        require(len(eligible) <= 2 * len(group) + 2 * k - 2, "union component count")
        incidences += len({parity ^ (values[t] & low) for t in eligible})
    upper = (3 * len(full_values) + (2 * k - cap - 1) * xcomp
             + (2 * cap - 2 * k - 2) * len(groups))
    require(incidences <= upper, "merged class incidence")
    prefix_parity = {value & low for value in values}
    pairs = {0} | {a ^ b for a, b in combinations(prefix_parity, 2)}
    masks = set()
    for readout in combinations_with_replacement(values, 4):
        total = sum(readout)
        if not total & (2 * low):
            masks.add(total & low)
    require(4 * len(masks - pairs) <= incidences, "four distinct parity classes")
    axis_colex_controls(k, values, r, labels, xcomp, triples)


def incidence_controls():
    rng = Random(1020230)
    checked = 0
    for k in (5, 6, 9):
        for _ in range(20):
            word = [j for j in range(k) for _ in range(4)]
            rng.shuffle(word)
            inspect_incidence(word, k)
            checked += 1
    return checked


def run_controls():
    words, small = small_graph_cube_controls()
    large = large_graph_cube_controls()
    incidence = incidence_controls()
    return {"small_words": words, "small_translations": small,
            "large_words": 4000, "large_translations": large,
            "incidence_axis_words": incidence, "result": "PASS"}


if __name__ == "__main__":
    print(json.dumps(run_controls(), indent=2, sort_keys=True))
