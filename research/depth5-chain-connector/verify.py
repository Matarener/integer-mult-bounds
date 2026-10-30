#!/usr/bin/env python3
"""Replay the depth-five unsigned chain connector results.

The chain calls are z_l += B_l z_{l-1} for l = 1..5 (z_0 = x immutable,
z_5 = y). A word over {1,...,5} is correct for c in characteristic m when it
restores z_1..z_4 and adds c B_5 B_4 B_3 B_2 B_1 x to y. Equivalently, the
product of the generators I + e_{l,l+1} in UT6(Z/m) is I + c e_{1,6}.

Two kinds of evidence are checked:
* exact minima for small m by breadth-first search over all of UT(K+1, Z/m)
  (depth five at m = 2, 3; depth four at m = 2..5 as a control against #4249);
* witness words with exactly m copies of each call, which meet the 5m floor.
"""
import hashlib
import json
import random
import sys
from pathlib import Path

import numpy as np

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
DEPTH = 5
INPUTS = ("research/universal-connector-boundary/README.md",)
PACKAGE_FILES = ("README.md", "SOURCES.json", "TASK.json", "VERIFY.json",
                 "search_witnesses.c", "verify.py", "witnesses.json")
REPLAY_SEED = 5
REPLAYS_PER_WITNESS = 2
# (depth, m) -> exact shortest length for every nonzero c, by BFS.
EXPECTED_BFS = {(4, 2): 12, (4, 3): 18, (4, 4): 20, (4, 5): 25,
                (5, 2): 16, (5, 3): 24}
# Depth five at m = 4 depends on c. The BFS over all 4^15 elements needs about
# 9 minutes and 20 GB, so it runs only with --exhaustive-m4.
EXPECTED_M4 = {1: 28, 2: 24, 3: 28}
FULL_M_MIN, FULL_M_MAX = 9, 20
EXPECTED_WITNESSES = 173  # 162 full-row pairs for 9 <= m <= 20 plus 11 at m = 5..8


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def bfs_minima(depth: int, modulus: int, chunk: int = 1 << 22) -> dict:
    """Shortest positive word for I + c e_{1,depth+1}, every c, over all of UT."""
    size = depth + 1
    pairs = [(i, j) for i in range(size) for j in range(i + 1, size)]
    idx = {p: t for t, p in enumerate(pairs)}
    weight = modulus ** np.arange(len(pairs), dtype=np.int64)
    seen = np.full(modulus ** len(pairs), 255, dtype=np.uint8)
    seen[0] = 0
    frontier = np.array([0], dtype=np.int64)
    targets = {c: c * int(weight[idx[(0, depth)]]) for c in range(1, modulus)}
    found, dist = {}, 0
    while len(frontier) and len(found) < len(targets):
        dist += 1
        require(dist < 255, "BFS depth overflow")
        grown = []
        for start in range(0, len(frontier), chunk):
            part = frontier[start:start + chunk]
            digits = (part[:, None] // weight[None, :]) % modulus
            for l in range(depth):  # call l+1: column l+1 += column l, (l, l+1) += 1
                delta = np.zeros(len(part), dtype=np.int64)
                for i in range(l + 1):
                    src = digits[:, idx[(i, l)]] if i < l else 1
                    dst = digits[:, idx[(i, l + 1)]]
                    delta += (((dst + src) % modulus) - dst) * weight[idx[(i, l + 1)]]
                new = part + delta
                new = new[seen[new] == 255]
                seen[new] = dist
                grown.append(new)
        frontier = np.unique(np.concatenate(grown))
        for c, t in targets.items():
            if c not in found and seen[t] == dist:
                found[c] = dist
    require(len(found) == len(targets), f"BFS missed a target at {(depth, modulus)}")
    return found


def interval_counts(word: str, modulus: int) -> dict:
    """N[i..j] mod m: scattered occurrences of the subword i(i+1)...j."""
    count = {(i, j): 0 for i in range(1, DEPTH + 1) for j in range(i, DEPTH + 1)}
    for event in word:
        letter = int(event)
        require(1 <= letter <= DEPTH, "unknown letter")
        for i in range(letter, 0, -1):
            gain = 1 if i == letter else count[(i, letter - 1)]
            count[(i, letter)] = (count[(i, letter)] + gain) % modulus
    return count


def counts_correct(word: str, modulus: int, coefficient: int) -> bool:
    count = interval_counts(word, modulus)
    return all(v == (coefficient % modulus if iv == (1, DEPTH) else 0)
               for iv, v in count.items())


def matrix_correct(word: str, modulus: int, coefficient: int) -> bool:
    """Product of I + e_{l,l+1} in UT6(Z/m), by full matrix multiplication."""
    n = DEPTH + 1
    acc = [[int(r == c) for c in range(n)] for r in range(n)]
    for event in word:
        letter = int(event)
        gen = [[int(r == c) for c in range(n)] for r in range(n)]
        gen[letter - 1][letter] = 1
        acc = [[sum(acc[r][k] * gen[k][c] for k in range(n)) % modulus
                for c in range(n)] for r in range(n)]
    want = [[int(r == c) for c in range(n)] for r in range(n)]
    want[0][DEPTH] = coefficient % modulus
    return acc == want


def matmul(a, b, m):
    return [[sum(a[i][k] * b[k][j] for k in range(2)) % m for j in range(2)]
            for i in range(2)]


def matvec(a, v, m):
    return [sum(a[i][k] * v[k] for k in range(2)) % m for i in range(2)]


def literal_replay(word: str, modulus: int, coefficient: int, rng) -> bool:
    """Dirty registers in (Z/m)^2 and random (generally noncommuting) 2x2 maps."""
    maps = [[[rng.randrange(modulus) for _ in range(2)] for _ in range(2)]
            for _ in range(DEPTH)]
    start = [[rng.randrange(modulus) for _ in range(2)] for _ in range(DEPTH + 1)]
    regs = [row[:] for row in start]
    for event in word:
        letter = int(event)
        gain = matvec(maps[letter - 1], regs[letter - 1], modulus)
        regs[letter] = [(u + g) % modulus for u, g in zip(regs[letter], gain)]
    chain = maps[0]
    for b in maps[1:]:
        chain = matmul(b, chain, modulus)
    target = [(u + coefficient * g) % modulus
              for u, g in zip(start[DEPTH], matvec(chain, start[0], modulus))]
    return regs[:DEPTH] == start[:DEPTH] and regs[DEPTH] == target


def load_witnesses() -> dict:
    data = json.loads((PACKAGE / "witnesses.json").read_text(encoding="utf-8"))
    require(data.get("schema_version") == 1, "witness schema")
    table = {}
    for m_text, row in data["witnesses"].items():
        m = int(m_text)
        table[m] = {int(c): w for c, w in row.items()}
        require(all(1 <= c < m for c in table[m]), f"residues at m={m}")
    for m in range(FULL_M_MIN, FULL_M_MAX + 1):
        require(sorted(table.get(m, {})) == list(range(1, m)), f"full row at m={m}")
    m4 = {int(c): w for c, w in data["m4_minimal_words"].items()}
    require(sorted(m4) == sorted(EXPECTED_M4), "m=4 rows")
    return table, m4


def check_m4_words(m4: dict) -> int:
    """Upper-bound words for depth five at m = 4, of the BFS lengths."""
    rng = random.Random(REPLAY_SEED + 4)
    for c, word in sorted(m4.items()):
        require(len(word) == EXPECTED_M4[c], f"m=4 length at c={c}")
        require(counts_correct(word, 4, c), f"m=4 counts at c={c}")
        require(matrix_correct(word, 4, c), f"m=4 UT6 product at c={c}")
        for _ in range(REPLAYS_PER_WITNESS):
            require(literal_replay(word, 4, c, rng), f"m=4 dirty replay at c={c}")
    return len(m4)


def check_witnesses(table: dict) -> int:
    rng = random.Random(REPLAY_SEED)
    checked = 0
    for m, row in sorted(table.items()):
        for c, word in sorted(row.items()):
            require(len(word) == DEPTH * m, f"length at {(m, c)}")
            for letter in "12345":
                require(word.count(letter) == m, f"count of {letter} at {(m, c)}")
            require(counts_correct(word, m, c), f"interval counts at {(m, c)}")
            require(matrix_correct(word, m, c), f"UT6 product at {(m, c)}")
            for _ in range(REPLAYS_PER_WITNESS):
                require(literal_replay(word, m, c, rng), f"dirty replay at {(m, c)}")
            checked += 1
    return checked


def controls(table: dict) -> list:
    """Each mutation of one witness must be rejected by every correctness check."""
    m = 14
    c = 1
    word = table[m][c]
    names = []

    def rejected(name: str, mutated: str, coeff: int = c) -> None:
        require(not counts_correct(mutated, m, coeff), f"control {name}: counts")
        require(not matrix_correct(mutated, m, coeff), f"control {name}: matrix")
        rng = random.Random(name)
        require(not all(literal_replay(mutated, m, coeff, rng) for _ in range(8)),
                f"control {name}: replay")
        names.append(name)

    rejected("wrong_coefficient", word, c + 1)
    rejected("dropped_last_call", word[:-1])
    swap = next(i for i in range(len(word) - 1)
                if abs(int(word[i]) - int(word[i + 1])) == 1)
    rejected("adjacent_noncommuting_swap",
             word[:swap] + word[swap + 1] + word[swap] + word[swap + 2:])
    first = word.index("3")
    rejected("one_call_relabelled", word[:first] + "4" + word[first + 1:])
    rejected("one_extra_call", word + "5")
    return names


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    require(sys.argv[1:] in ([], ["--exhaustive-m4"]), "usage: verify.py [--exhaustive-m4]")
    minima = {}
    for (depth, m), want in sorted(EXPECTED_BFS.items()):
        found = bfs_minima(depth, m)
        require(set(found.values()) == {want}, f"BFS minimum at {(depth, m)}: {found}")
        minima[f"depth{depth}_m{m}"] = want
    if sys.argv[1:] == ["--exhaustive-m4"]:
        found = bfs_minima(DEPTH, 4)
        require(found == EXPECTED_M4, f"BFS minima at (5, 4): {found}")
        minima["depth5_m4"] = {str(c): v for c, v in sorted(found.items())}
    table, m4 = load_witnesses()
    checked = check_witnesses(table)
    require(checked == EXPECTED_WITNESSES, f"witness total {checked}")
    m4_checked = check_m4_words(m4)
    names = controls(table)
    receipt = {
        "schema_version": 1,
        "claim": "depth-five unsigned dirty chain connector: exact minima 16 (m=2) and "
                 "24 (m=3) by exhaustive BFS; explicit m=4 words of lengths 28, 24, 28 "
                 f"(c=1,2,3); the 5m floor attained for every c when {FULL_M_MIN} <= m "
                 f"<= {FULL_M_MAX} and for the listed pairs at m = 5..8",
        "exhaustive_m4": sys.argv[1:] == ["--exhaustive-m4"],
        "m4_words_checked": m4_checked,
        "bfs_exact_minima": minima,
        "witness_pairs": {str(m): sorted(row) for m, row in sorted(table.items())},
        "witnesses_checked": checked,
        "literal_replays": checked * REPLAYS_PER_WITNESS,
        "controls": names,
        "package_sha256": {f: sha256(PACKAGE / f) for f in PACKAGE_FILES},
        "input_sha256": {p: sha256(ROOT / p) for p in INPUTS},
    }
    print(json.dumps(receipt, indent=2, sort_keys=True))
    print(f"PASS_DEPTH5_CHAIN_CONNECTOR bfs_cases={len(minima)} witnesses={checked} "
          f"m4_words={m4_checked}")


if __name__ == "__main__":
    main()
