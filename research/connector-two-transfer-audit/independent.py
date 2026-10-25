"""Brute port/reader oracle for the reduction. Nick Petalas. Apache-2.0."""

import sys
from itertools import combinations, product
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import census
from verify import read_json


def direct_words(n, triple):
    """Unrestricted labelled words, filtered after generation."""
    length = 2 * n + int(triple)
    expected = [2] * n
    expected[0] += int(triple)
    result = []
    for word in product(range(n), repeat=length):
        if [word.count(i) for i in range(n)] != expected:
            continue
        ordinary = range(1, n) if triple else range(n)
        first = [word.index(i) for i in ordinary]
        if first == sorted(first):
            result.append(word)
    return result


def literal(word, cut, ports, n, destination):
    """Set-valued full rows; no moving-frame or restoration shortcut."""
    roots = [frozenset((n,)), frozenset((n + 1,))]
    observations = set(roots)
    roots[destination] ^= roots[1 - destination]
    observations.update(roots)
    for i in range(len(word) + 1):
        if i == cut:
            roots[destination] ^= roots[1 - destination]
            observations.update(roots)
        if i < len(word):
            port = ((ports >> i) & 1) ^ destination
            roots[port] ^= frozenset((word[i],))
            observations.update(roots)
    restored = roots == [frozenset((n,)), frozenset((n + 1,))]
    return restored, observations


def read_masks(observations, n):
    result = []
    for length in (2, 3):
        masks = set()
        for reads in combinations(observations, length):
            value = frozenset()
            for row in reads:
                value ^= row
            if all(i < n for i in value):
                masks.add(sum(1 << i for i in value))
        result.append(masks)
    return result


def compare_group(word, cut, ports, n, observations):
    expected = set()
    for dirt, bits in enumerate(census.queries(word, cut, ports, n)):
        for value in census.values(bits):
            expected.add(
                frozenset(i for i in range(n + 2) if (value | (dirt << n)) & (1 << i))
            )
    census.require(expected == observations, "query-set reduction disagrees")
    pair, triple = read_masks(observations, n)
    pair.add(0)
    covered = census.paired_masks(census.queries(word, cut, ports, n))
    census.require(pair == set(census.values(covered)), "paired reader disagreement")
    groups = census.queries(word, cut, ports, n)
    computed = {i for i in range(1 << n) if census.three_read(groups, i)}
    census.require(computed == triple, "three-reader disagreement")


def run():
    rows = []
    for n, triple in product((2, 3), (False, True)):
        words = direct_words(n, triple)
        census.require(
            set(words) == set(census.source_words(n, triple)),
            "source-word generator disagreement",
        )
        restored_count = 0
        attempted = 0
        for word in words:
            for cut in range(len(word) + 1):
                accepted = []
                for ports in range(1 << len(word)):
                    attempted += 1
                    ok, observations = literal(word, cut, ports, n, 0)
                    swapped, _ = literal(word, cut, ports, n, 1)
                    census.require(ok == swapped, "root-exchange restoration")
                    if ok:
                        accepted.append(ports)
                        compare_group(word, cut, ports, n, observations)
                        restored_count += 1
                census.require(
                    accepted == sorted(census.restoring_ports(word, cut, n, triple)),
                    "restoration port generator incomplete",
                )
        rows.append(
            {
                "sources": n,
                "triple": triple,
                "attempted": attempted,
                "restored": restored_count,
                "source_words": len(words),
            }
        )
    return rows


if __name__ == "__main__":
    import json

    observed = {"status": "PASS_BRUTE_PHASE_ORACLE", "domains": run()}
    expected = read_json(Path(__file__).resolve().parent / "CHECKS.json")[
        "brute_oracle"
    ]
    census.require(observed == expected, "brute oracle receipt mismatch")
    print(json.dumps(observed, indent=2, sort_keys=True))
