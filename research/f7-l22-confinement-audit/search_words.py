#!/usr/bin/env python3
"""Stochastic word-level search in the PR943 singleton prefix-walk model.

Fixed multiset of positive even label counts; moves are transpositions;
objective is the number of masks of F2^n realised as XOR of a contiguous
subword, i.e. |P + P|.  The search is a heuristic: it certifies nothing it does
not print, and a rerun need not reproduce the same best coverage.  Its purpose
in this package is the positive control at length 24, where a universal word is
known to exist.
"""

import argparse
import sys
from itertools import combinations_with_replacement

N = 7
FULL = (1 << N) - 1


def coverage(digits):
    q = 0
    states = [0]
    for d in digits:
        q ^= 1 << d
        states.append(q)
    return len({a ^ b for a in states for b in states})


class Lcg:
    def __init__(self, seed):
        self.s = seed & ((1 << 64) - 1)

    def next(self):
        self.s = (self.s * 6364136223846793005 + 1442695040888963407) & ((1 << 64) - 1)
        return self.s >> 16

    def randrange(self, n):
        return self.next() % n


def search(counts, seconds, seed, report=print):
    import time
    rng = Lcg(seed)
    length = sum(counts)
    best, bestw = -1, None
    deadline = time.time() + seconds
    runs = 0
    while time.time() < deadline:
        runs += 1
        word = []
        for i, c in enumerate(counts):
            word += [i] * c
        for i in range(length - 1, 0, -1):
            j = rng.randrange(i + 1)
            word[i], word[j] = word[j], word[i]
        cur = coverage(word)
        stall = 0
        while stall < 4000 and time.time() < deadline:
            i, j = rng.randrange(length), rng.randrange(length)
            if i == j:
                continue
            word[i], word[j] = word[j], word[i]
            new = coverage(word)
            if new >= cur:
                if new > cur:
                    cur, stall = new, 0
                else:
                    stall += 1
                if new > best:
                    best, bestw = new, list(word)
                    report(f"best={new} word={''.join(map(str, word))}")
            else:
                word[i], word[j] = word[j], word[i]
                stall += 1
    return best, bestw, runs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seconds", type=float, default=60.0, help="budget per pattern")
    ap.add_argument("--length", type=int, default=24, choices=(18, 20, 22, 24))
    ap.add_argument("--seed", type=int, default=20261018)
    args = ap.parse_args()
    patterns = [c for c in combinations_with_replacement(range(2, args.length + 1, 2), N)
                if sum(c) == args.length]
    print(f"length {args.length}: {len(patterns)} multiplicity patterns")
    for k, counts in enumerate(patterns):
        best, word, runs = search(list(counts), args.seconds, args.seed + k)
        print(f"pattern {counts}: best={best}/128 restarts={runs} "
              f"word={''.join(map(str, word)) if word else None}", flush=True)


if __name__ == "__main__":
    sys.exit(main())
