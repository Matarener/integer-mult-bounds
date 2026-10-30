#!/usr/bin/env python3
"""Exact complete-call floor for the 98 seven-source masks of weight <= 4.

Standard-library replay.  It recomputes the projection ceilings that exclude
every restored source word of length <= 18 and the profiles (8,2^6), (6,4,2^5)
at length 20, checks every witness, and cross-checks the native census in
CENSUS.json against closed-form word counts and against the Python censuses
that are cheap enough to rerun here.  The (4,4,4,2^4) length-20 exclusion and
the exact maxima at lengths 16 and 18 come from census.c; see README.md.

Nick Petalas, with AI assistance.  Apache-2.0.
"""
from __future__ import annotations

import json
import math
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
N_SRC, W_MAX = 7, 4


def targets(n: int, w: int) -> int:
    return sum(1 << m for m in range(1, 1 << n) if m.bit_count() <= w)


def restored(word: list[int]) -> bool:
    return all(c % 2 == 0 for c in Counter(word).values())


def covered(word: list[int]) -> int:
    """Bitmask of q_a ^ q_b over the source-call boundaries of a restored word."""
    assert restored(word), "a word that does not restore the connector is not admissible"
    q, states, cov = 0, [0], 0
    for x in word[:-1]:
        q ^= 1 << x
        for p in states:
            cov |= 1 << (q ^ p)
        states.append(q)
    return cov


def census(profile: tuple[int, ...], n: int, w: int) -> Counter:
    """Coverage histogram over relabelling classes of words with this profile.

    Letters are named by first occurrence; a new letter picks its multiplicity
    from the unassigned multiset.  Written independently of census.c and of the
    audited package's double-occurrence enumerator.
    """
    tgt, length = targets(n, w), sum(profile)
    free = Counter(profile)
    owed = [0] * n
    states = [0] * length
    hist: Counter = Counter()

    def dfs(t: int, labels: int, cov: int) -> None:
        if t == length - 1:  # last letter is forced and returns to state 0
            hist[(cov & tgt).bit_count()] += 1
            return
        for letter in range(min(labels + 1, n)):
            options = sorted(free) if letter == labels else [None]
            for mult in options:
                if mult is not None:
                    if not free[mult]:
                        continue
                    free[mult] -= 1
                    owed[letter] = mult
                elif not owed[letter]:
                    continue
                owed[letter] -= 1
                s = states[t] ^ (1 << letter)
                states[t + 1] = s
                ncov = cov
                for a in range(t + 1):
                    ncov |= 1 << (s ^ states[a])
                dfs(t + 1, labels + (mult is not None), ncov)
                owed[letter] += 1
                if mult is not None:
                    free[mult] += 1
                    owed[letter] = 0

    dfs(0, 0, 0)
    return hist


def class_count(profile: tuple[int, ...]) -> int:
    """Relabelling classes: labelled words / n!, since every letter occurs."""
    n = len(profile)
    assignments = math.factorial(n) // math.prod(math.factorial(k) for k in Counter(profile).values())
    words = math.factorial(sum(profile)) // math.prod(math.factorial(c) for c in profile)
    labelled = assignments * words
    assert labelled % math.factorial(n) == 0
    return labelled // math.factorial(n)


def profiles(n: int, length: int) -> list[tuple[int, ...]]:
    """Nonincreasing even multiplicities >= 2 for n sources summing to length."""
    out = []

    def rec(left: int, k: int, cap: int, acc: tuple[int, ...]) -> None:
        if k == 0:
            if left == 0:
                out.append(acc)
            return
        for c in range(min(cap, left - 2 * (k - 1)), 1, -1):
            if c % 2 == 0:
                rec(left - c, k - 1, c, acc + (c,))

    rec(length, n, length, ())
    return out


def words(text: str) -> list[int]:
    return [int(x) for x in text.split()]


def main() -> None:
    record = json.loads((HERE / "CENSUS.json").read_text())
    runs = {tuple(r["profile"]) if r["n"] == N_SRC else ("6src",) + tuple(r["profile"]): r
            for r in record["runs"] if r["W"] == W_MAX}
    T7, T6 = targets(7, 4), targets(6, 4)
    n_t7, n_t6 = T7.bit_count(), T6.bit_count()
    assert (n_t7, n_t6) == (98, 56)
    with_bit = n_t7 - n_t6  # 42 masks of weight <= 4 that contain a given source

    # 1. Every native census row has the closed-form class count and a
    #    histogram that sums to it; its first maximiser attains the maximum.
    for r in record["runs"]:
        prof = tuple(r["profile"])
        hist = {int(k): v for k, v in r["histogram"].items()}
        assert r["canonical_words"] == class_count(prof) == sum(hist.values()), prof
        assert max(hist) == r["max_coverage"] and hist[max(hist)] == r["words_at_max"]
        w = words(r["first_word_at_max"])
        assert sorted(Counter(w).values(), reverse=True) == sorted(prof, reverse=True)
        assert (covered(w) & targets(r["n"], r["W"])).bit_count() == r["max_coverage"], prof

    # 2. Python reruns of the cheaper censuses must match the native
    #    histograms exactly (second implementation of the same enumeration).
    ceiling = {}
    for key, prof, n in [(("6src", 2, 2, 2, 2, 2, 2), (2,) * 6, 6),
                         (("6src", 4, 2, 2, 2, 2, 2), (4,) + (2,) * 5, 6),
                         ((2,) * 7, (2,) * 7, 7)]:
        hist = census(prof, n, W_MAX)
        native = {int(k): v for k, v in runs[key]["histogram"].items()}
        assert dict(hist) == native, key
        ceiling[prof] = max(hist)
    assert ceiling[(2,) * 6] == 48 and ceiling[(4,) + (2,) * 5] == 54
    assert ceiling[(2,) * 7] == 70

    # 3. Projection: deleting source s maps every covered mask avoiding s to a
    #    covered mask of the projected word, so cov <= ceiling(rest) + 42.
    six_ceiling = {(2,) * 6: 48, (4,) + (2,) * 5: 54}
    lift_444 = runs[("6src", 4, 4, 2, 2, 2, 2)]
    assert lift_444["lift_k"] == 4 and lift_444["lift_targets"] == 98
    assert lift_444["full_coverage_6source_words"] == lift_444["words_at_max"]
    assert lift_444["words_at_max"] * math.comb(20, 4) == lift_444["lifts"]
    assert lift_444["lift_max_coverage"] == 95
    w = words(lift_444["first_lift_at_max"])
    assert (covered(w) & T7).bit_count() == 95
    bound = {}
    for length in range(14, 21, 2):
        for prof in profiles(N_SRC, length):
            best = n_t7
            for i in range(N_SRC):
                rest = tuple(sorted(prof[:i] + prof[i + 1:], reverse=True))
                if rest in six_ceiling:
                    best = min(best, six_ceiling[rest] + with_bit)
            if prof == (4, 4, 4, 2, 2, 2, 2):
                # A full cover projects (deleting a 4-source) onto one of the
                # full-56 (4,4,2^4) words; all their lifts reach at most 95.
                best = min(best, n_t7 - 1)
            assert best < n_t7, f"profile {prof} not excluded"
            bound[prof] = best
    assert sorted(bound) == sorted(p for L in range(14, 21, 2) for p in profiles(7, L))
    assert len(bound) == 7

    # 4. Exact maxima at lengths 16 and 18 (native census; witnesses rechecked).
    exact = {p: runs[p]["max_coverage"] for p in [(4,) + (2,) * 6, (6,) + (2,) * 6, (4, 4) + (2,) * 5]}
    assert exact == {(4,) + (2,) * 6: 79, (6,) + (2,) * 6: 85, (4, 4) + (2,) * 5: 91}

    # 5. Length-22 cover attains 218 complete calls.
    w22 = words(record["length22_full_cover"])
    assert len(w22) == 22 and restored(w22) and (covered(w22) & T7) == T7
    assert sorted(Counter(w22).values(), reverse=True) == [6, 6, 2, 2, 2, 2, 2]

    # 6. Complete-call floor with any even number of readouts per mask: a mask
    #    with exactly two readouts lies in D(w); otherwise it needs at least four.
    def floor_at(length: int, max_cov: int) -> int:
        return length + 2 * n_t7 + 2 * (n_t7 - max_cov)

    worst = {L: max(bound[p] for p in profiles(7, L)) for L in range(14, 21, 2)}
    floors = {L: floor_at(L, worst[L]) for L in worst}
    assert min(floors.values()) >= 218 and floor_at(22, n_t7) == 218
    assert 22 + 2 * n_t7 == 218

    # Controls.
    assert class_count((2,) * 7) == 135135 and class_count((4,) + (2,) * 6) == 18918900
    assert class_count((4, 4) + (2,) * 5) == 1447295850  # PR #3780 published domain size
    pr2397 = words("0 1 2 3 1 0 4 2 0 5 1 4 1 6 5 0 3 6")  # 144-call weight-<=3 cover
    assert (covered(pr2397) & targets(7, 3)) == targets(7, 3)
    assert (covered(pr2397) & T7).bit_count() < n_t7
    try:
        covered(w22[:-1])
    except AssertionError:
        pass
    else:
        raise AssertionError("unrestored word accepted")
    broken = list(w22)
    broken[0], broken[1] = broken[1], broken[0]  # swap first two calls
    assert (covered(broken) & T7) != T7  # the cover depends on the exact order
    assert record["length22_full_cover"] == runs[("6src", 6, 2, 2, 2, 2, 2)]["first_lift_at_max"]

    print("PASS_SEVEN_SOURCE_WEIGHT4_EXACT_FLOOR L<=20_excluded floor=218 attained_L22=218 "
          "max16=79 max18_62=85 max18_44=91 lift20_444_max=95")


if __name__ == "__main__":
    main()
