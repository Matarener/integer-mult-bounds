#!/usr/bin/env python3
"""Search for a balanced depth-four witness for one (m, c); not part of the replay.

Simulated annealing over words with exactly m copies of each call, moving by
swapping two different calls. The objective is the circular distance of the
six non-diagonal interval counts from (0, 0, 0, 0, 0, c) mod m. This is how
witnesses.json was produced; verify.py checks the words themselves, so any
other search method would serve equally. Usage: search_witnesses.py M C
"""
import math
import random
import sys

DEPTH = 4
SWEEPS = 400_000


def interval_residues(word: list, m: int) -> tuple:
    n1 = n2 = n3 = n12 = n23 = n34 = n13 = n24 = n14 = 0
    for letter in word:
        if letter == 1:
            n1 += 1
        elif letter == 2:
            n12 += n1
            n2 += 1
        elif letter == 3:
            n13 += n12
            n23 += n2
            n3 += 1
        else:
            n14 += n13
            n24 += n23
            n34 += n3
    return (n12 % m, n23 % m, n34 % m, n13 % m, n24 % m, n14 % m)


def distance(residues: tuple, m: int, c: int) -> int:
    target = (0, 0, 0, 0, 0, c)
    return sum(min((a - b) % m, (b - a) % m) for a, b in zip(residues, target))


def anneal(m: int, c: int, rng: random.Random):
    word = [l for l in range(1, DEPTH + 1) for _ in range(m)]
    rng.shuffle(word)
    cost = distance(interval_residues(word, m), m, c)
    temperature = 2.0
    for _ in range(SWEEPS):
        if cost == 0:
            return word
        i, j = rng.randrange(len(word)), rng.randrange(len(word))
        if word[i] == word[j]:
            continue
        word[i], word[j] = word[j], word[i]
        new = distance(interval_residues(word, m), m, c)
        if new <= cost or rng.random() < math.exp((cost - new) / temperature):
            cost = new
        else:
            word[i], word[j] = word[j], word[i]
        temperature = max(0.3, temperature * 0.99995)
    return None


def main() -> None:
    if len(sys.argv) != 3:
        raise SystemExit("usage: search_witnesses.py M C")
    m, c = int(sys.argv[1]), int(sys.argv[2])
    if not (2 <= m and 1 <= c < m):
        raise SystemExit("need m >= 2 and 1 <= c < m")
    rng = random.Random(1000 * m + c)
    for attempt in range(1, 101):
        word = anneal(m, c, rng)
        if word is not None:
            assert interval_residues(word, m) == (0, 0, 0, 0, 0, c)
            print(m, c, attempt, "".join(map(str, word)))
            return
    raise SystemExit(f"no witness for (m, c) = ({m}, {c}) in 100 restarts")


if __name__ == "__main__":
    main()
