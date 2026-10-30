#!/usr/bin/env python3
"""Exact finite corroboration of the connected restored XOR-word floor.

Produced by Nick Petalas. Apache-2.0.
No predecessor executable or external scientific input is imported.
"""

import hashlib
import json
from pathlib import Path
import sys


PACKAGE_FILES = ("PROOF.md", "README.md", "SOURCES.json", "TASK.json", "VERIFY.json", "verify.py")
# Census widths and the largest full word length joined at each width.
CENSUS = ((1, 2), (2, 4), (3, 6), (4, 8), (5, 8))
MAX_STAR_LABELS = 12


def need(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def arcs(n: int) -> tuple[tuple[int, int], ...]:
    need(type(n) is int and 1 <= n <= MAX_STAR_LABELS, "unsupported label count")
    return tuple((s, t) for t in range(n) for s in range(n) if s != t)


def apply(rows: tuple[int, ...], s: int, t: int) -> tuple[int, ...]:
    """X_(s,t): x_t += x_s, acting on the rows of the source frame."""
    need(0 <= s < len(rows) and 0 <= t < len(rows) and s != t, "bad XOR call")
    out = list(rows)
    out[t] ^= rows[s]
    return tuple(out)


def identity(n: int) -> tuple[int, ...]:
    return tuple(1 << i for i in range(n))


def components(n: int, arc_mask: int, table: tuple[tuple[int, int], ...]) -> int:
    parent = list(range(n))

    def root(v: int) -> int:
        for _ in range(n):
            if parent[v] == v:
                return v
            v = parent[v]
        raise ValueError("union-find did not terminate")

    for k, (s, t) in enumerate(table):
        if arc_mask >> k & 1:
            parent[root(s)] = root(t)
    return len({root(v) for v in range(n)})


def endpoint_counts(arc_mask: int, table: tuple[tuple[int, int], ...]) -> tuple[int, int]:
    used = [arc for k, arc in enumerate(table) if arc_mask >> k & 1]
    return len({t for _, t in used}), len({s for s, _ in used})


def half_layers(n: int, depth: int) -> list[dict[tuple[int, ...], set[int]]]:
    """Every (frame matrix, used directed-arc set) reachable in exactly k calls."""
    table = arcs(n)
    layers = [{identity(n): {0}}]
    for _ in range(depth):
        nxt: dict[tuple[int, ...], set[int]] = {}
        for rows, masks in layers[-1].items():
            for k, (s, t) in enumerate(table):
                bucket = nxt.setdefault(apply(rows, s, t), set())
                bucket.update(mask | 1 << k for mask in masks)
        layers.append(nxt)
    return layers


def census(n: int, max_length: int) -> dict[str, object]:
    table = arcs(n)
    layers = half_layers(n, (max_length + 1) // 2)
    rows_out = []
    for length in range(max_length + 1):
        left, right = layers[length // 2], layers[(length + 1) // 2]
        graphs: set[int] = set()
        for rows, masks in left.items():
            for other in right.get(rows, ()):
                graphs.update(mask | other for mask in masks)
        fewest = None
        for mask in graphs:
            c = components(n, mask, table)
            targets, sources = endpoint_counts(mask, table)
            need(length >= targets + sources, "rank lemma L >= |T|+|S| fails")
            need(c >= n - length // 2, "component floor c >= n - floor(L/2) fails")
            fewest = c if fewest is None else min(fewest, c)
        rows_out.append({"length": length, "restored_arc_sets": len(graphs), "fewest_components": fewest})
    first_connected = next((r["length"] for r in rows_out if r["fewest_components"] == 1), None)
    if n == 1:
        need(first_connected == 0, "single label must be connected by the empty word")
    elif max_length >= 2 * (n - 1):
        need(first_connected == 2 * (n - 1), "connected minimum is not 2(n-1)")
    for r in rows_out:
        if r["length"] % 2 == 0 and r["length"] <= 2 * (n - 1):
            need(r["fewest_components"] == n - r["length"] // 2, "even-length floor is not attained")
    return {
        "labels": n,
        "max_length": max_length,
        "half_layer_states": [sum(len(v) for v in layer.values()) for layer in layers],
        "lengths": rows_out,
        "first_connected_length": first_connected,
    }


def run_word(n: int, word: list[tuple[int, int]]) -> tuple[bool, int]:
    rows = identity(n)
    mask = 0
    index = {arc: k for k, arc in enumerate(arcs(n))}
    for s, t in word:
        rows = apply(rows, s, t)
        mask |= 1 << index[(s, t)]
    return rows == identity(n), components(n, mask, arcs(n))


def attaining_words() -> dict[str, object]:
    checked = []
    for n in range(2, MAX_STAR_LABELS + 1):
        star = [(0, i) for i in range(1, n) for _ in range(2)]
        path = [(i, i + 1) for i in range(n - 1) for _ in range(2)]
        for word in (star, path):
            restored, c = run_word(n, word)
            need(restored and c == 1 and len(word) == 2 * (n - 1), "attaining word fails")
        checked.append(n)
    commutator = [(1, 0), (2, 1), (1, 0), (2, 1), (2, 0)]
    restored, c = run_word(3, commutator)
    need(restored and c == 1, "odd commutator identity fails")
    return {"star_and_path_labels": checked, "odd_commutator_length": len(commutator)}


def controls() -> int:
    passed = 0
    restored, c = run_word(3, [(0, 1), (1, 2), (0, 1), (1, 2)])
    need(c == 1 and not restored, "connected nonrestored control")
    passed += 1
    restored, c = run_word(3, [(0, 1), (0, 1)])
    need(restored and c == 2, "restored disconnected control")
    passed += 1
    restored, c = run_word(3, [(0, 1), (1, 2), (2, 0)])
    need(not restored and c == 1, "three-cycle control")
    passed += 1
    for bad in ((0, 0), (0, 3), (-1, 1)):
        try:
            apply(identity(3), *bad)
        except ValueError:
            passed += 1
        else:
            raise ValueError("malformed call accepted")
    return passed


def package_hashes() -> dict[str, str]:
    root = Path(__file__).resolve().parent
    return {name: hashlib.sha256((root / name).read_bytes()).hexdigest() for name in PACKAGE_FILES}


def main() -> int:
    results = [census(n, length) for n, length in CENSUS]
    receipt = {
        "census": results,
        "attaining": attaining_words(),
        "controls_passed": controls(),
        "package_sha256": package_hashes(),
    }
    print("PASS_CONNECTED_XOR_WORD_FLOOR")
    print(json.dumps(receipt, indent=1, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
