#!/usr/bin/env python3
"""Replay the depth-four unsigned chain connector witnesses.

The chain calls are z_l += B_l z_{l-1} for l = 1..4 (z_0 = x immutable,
z_4 = y). A word over {1,2,3,4} is correct for c in characteristic m when it
restores z_1, z_2, z_3 and adds c B_4 B_3 B_2 B_1 x to y. Each witness uses
every call exactly m times, which is the floor (README, Lemma 1), so each
witness proves that the shortest word for (m, c) has exactly 4m calls.
"""
import hashlib
import json
import random
import sys
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
DEPTH = 4
M_MIN, M_MAX = 6, 32
INPUTS = ("research/universal-connector-boundary/README.md",)
PACKAGE_FILES = ("README.md", "SOURCES.json", "TASK.json", "VERIFY.json",
                 "search_witnesses.py", "verify.py", "witnesses.json")
REPLAY_SEED = 4
REPLAYS_PER_WITNESS = 2


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


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


def unitriangular_product(word: str, modulus: int) -> list:
    """Product of I + e_{l,l+1} in UT5(Z/m), computed by matrix multiplication."""
    n = DEPTH + 1
    acc = [[int(r == c) for c in range(n)] for r in range(n)]
    for event in word:
        letter = int(event)
        gen = [[int(r == c) for c in range(n)] for r in range(n)]
        gen[letter - 1][letter] = 1
        acc = [[sum(acc[r][k] * gen[k][c] for k in range(n)) % modulus
                for c in range(n)] for r in range(n)]
    return acc


def matrix_correct(word: str, modulus: int, coefficient: int) -> bool:
    n = DEPTH + 1
    want = [[int(r == c) for c in range(n)] for r in range(n)]
    want[0][DEPTH] = coefficient % modulus
    return unitriangular_product(word, modulus) == want


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
    require(sorted(table) == list(range(M_MIN, M_MAX + 1)), "modulus range")
    for m, row in table.items():
        require(sorted(row) == list(range(1, m)), f"residues at m={m}")
    return table


def check_witnesses(table: dict) -> int:
    rng = random.Random(REPLAY_SEED)
    checked = 0
    for m, row in sorted(table.items()):
        for c, word in sorted(row.items()):
            require(len(word) == DEPTH * m, f"length at {(m, c)}")
            for letter in "1234":
                require(word.count(letter) == m, f"count of {letter} at {(m, c)}")
            require(counts_correct(word, m, c), f"interval counts at {(m, c)}")
            require(matrix_correct(word, m, c), f"UT5 product at {(m, c)}")
            for _ in range(REPLAYS_PER_WITNESS):
                require(literal_replay(word, m, c, rng), f"dirty replay at {(m, c)}")
            checked += 1
    return checked


def floor_predicate(word: str, modulus: int) -> bool:
    """Lemma 1 as a predicate: a correct word uses each call a positive multiple of m times."""
    return all(word.count(l) % modulus == 0 and word.count(l) > 0 for l in "1234")


def controls(table: dict) -> list:
    """Each mutation must be rejected by every correctness check."""
    m, c = 7, 3
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
    rejected("reversed_word", word[::-1])
    rejected("one_extra_call", word + "4")
    # The floor predicate rejects any count that is not a positive multiple of m.
    require(floor_predicate(word, m) and not floor_predicate(word[:-1], m),
            "control floor predicate")
    names.append("floor_predicate")
    return names


def interleavings(word: str) -> tuple:
    """x_j, y_k, z_l: number of calls l-1 before the j-th call l, for l = 2, 3, 4."""
    out = []
    for low, high in (("1", "2"), ("2", "3"), ("3", "4")):
        seen, seq = 0, []
        for event in word:
            if event == low:
                seen += 1
            elif event == high:
                seq.append(seen)
        out.append(seq)
    return tuple(out)


def interleaving_counts(word: str) -> dict:
    """README Lemma 2: the six non-diagonal counts from x, y, z alone (exact integers)."""
    x, y, z = interleavings(word)
    big_x = [sum(x[:s]) for s in range(len(x) + 1)]
    big_y = [sum(y[:s]) for s in range(len(y) + 1)]
    f = [sum(big_x[v] for v in y[:s]) for s in range(len(y) + 1)]
    return {(1, 2): sum(x), (2, 3): sum(y), (3, 4): sum(z),
            (1, 3): sum(big_x[v] for v in y), (2, 4): sum(big_y[v] for v in z),
            (1, 4): sum(f[s] for s in z)}


def check_lemma2(trials: int = 2000) -> int:
    rng = random.Random(REPLAY_SEED + 1)
    for _ in range(trials):
        m = rng.randrange(1, 12)
        letters = [l for l in "1234" for _ in range(m)]
        rng.shuffle(letters)
        word = "".join(letters)
        exact = interval_counts(word, 10 ** 12)
        require(all(exact[iv] == v for iv, v in interleaving_counts(word).items()),
                "Lemma 2 mismatch")
    return trials


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    require(sys.argv[1:] == [], "usage: verify.py")
    table = load_witnesses()
    checked = check_witnesses(table)
    require(checked == sum(m - 1 for m in range(M_MIN, M_MAX + 1)), "witness total")
    names = controls(table)
    lemma2 = check_lemma2()
    receipt = {
        "schema_version": 1,
        "claim": "shortest unsigned depth-four dirty chain connector = 4m calls "
                 f"for every m in [{M_MIN}, {M_MAX}] and every nonzero c (mod m)",
        "witnesses_checked": checked,
        "literal_replays": checked * REPLAYS_PER_WITNESS,
        "controls": names,
        "lemma2_random_balanced_words": lemma2,
        "package_sha256": {f: sha256(PACKAGE / f) for f in PACKAGE_FILES},
        "input_sha256": {p: sha256(ROOT / p) for p in INPUTS},
    }
    print(json.dumps(receipt, indent=2, sort_keys=True))
    print(f"PASS_DEPTH4_CHAIN_CONNECTOR moduli={M_MAX - M_MIN + 1} witnesses={checked}")


if __name__ == "__main__":
    main()
