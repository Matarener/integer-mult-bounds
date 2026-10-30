#!/usr/bin/env python3
"""Verify the bounded-depth block capacity bound for the unsigned connector.

Claim (README): a depth-d block on k sources in characteristic c >= 2, i.e. a
word using each source exactly c times in which every nonzero binary mask is a
sum of at most d prefix-count vectors modulo c, satisfies

    2^k - 1 <= k * min(k, c) * binom(k*c + d - 2, d - 1).

The proof is the weight identity: boundary t has coordinate sum t, so the read
boundaries of a mask m sum to |m| modulo c.  This script checks the identity
and the per-weight candidate count on literal words (an exhaustive census of
small words and independently rebuilt reflected-Gray blocks), evaluates the
explicit capacity tables, and rejects mutation controls.  Finite checks support
the written proof; they do not replace it.  Standard library only.

JosieElliston (Claude Code session 40, Anthropic Claude assistance). Apache-2.0.
"""

from __future__ import annotations

import hashlib
import itertools
import json
import math
from fractions import Fraction
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent.parent


class Fail(Exception):
    pass


def need(cond: bool, msg: str) -> None:
    if not cond:
        raise Fail(msg)


# ---------------------------------------------------------------- sources

def check_sources() -> int:
    data = json.loads((HERE / "SOURCES.json").read_text(encoding="utf-8"))
    n = 0
    for row in data["files"]:
        if row["usage"] != "input":
            continue
        raw = (ROOT / row["path"]).read_bytes()
        need(hashlib.sha256(raw).hexdigest() == row["sha256"],
             f"source hash mismatch: {row['path']}")
        n += 1
    return n


# ---------------------------------------------------------------- words

def validate_word(word, k, c):
    need(len(word) == k * c, "word length must be k*c")
    counts = [0] * k
    for s in word:
        need(0 <= s < k, "source label out of range")
        counts[s] += 1
    need(all(x == c for x in counts), "every source must occur exactly c times")


def prefixes(word, k):
    """Integer prefix-count vectors q_0..q_{kc} as tuples."""
    q = [0] * k
    out = [tuple(q)]
    for s in word:
        q[s] += 1
        out.append(tuple(q))
    return out


def mask_of(vec, c):
    """Return the binary mask (as int) if vec is binary mod c, else None."""
    m = 0
    for j, x in enumerate(vec):
        r = x % c
        if r == 1:
            m |= 1 << j
        elif r != 0:
            return None
    return m


def cover(word, k, c, d, audit=True):
    """Nonzero masks represented by multisets of <= d boundaries in [0, kc-1].

    Boundary kc has prefix c*1 == 0 = q_0 mod c, so it is never needed.
    With audit=True, every representing multiset is checked against the
    weight identity sum(a_i) == |m| (mod c), and for every (d'-1)-prefix
    multiset and weight w the number of admissible last boundaries is <= k.
    Returns (set_of_masks, number_of_identity_checks).
    """
    validate_word(word, k, c)
    q = prefixes(word, k)
    T = k * c
    masks = set()
    checks = 0
    for e in range(1, d + 1):
        for head in itertools.combinations_with_replacement(range(T), e - 1):
            base = [0] * k
            for a in head:
                for j in range(k):
                    base[j] += q[a][j]
            lo = head[-1] if head else 0
            per_weight = {}
            for a in range(lo, T):
                vec = [base[j] + q[a][j] for j in range(k)]
                m = mask_of(vec, c)
                if m is None or m == 0:
                    continue
                masks.add(m)
                if audit:
                    w = bin(m).count("1")
                    need((sum(head) + a - w) % c == 0,
                         f"weight identity fails: word={word} reads={head + (a,)}")
                    per_weight[w] = per_weight.get(w, 0) + 1
                    checks += 1
            for w, cnt in per_weight.items():
                need(cnt <= k, "more than k last-read candidates for one weight")
    return masks, checks


def multiset_words(k, c):
    """All words with each of k labels exactly c times (lexicographic)."""
    counts = [c] * k
    word = []

    def rec():
        if len(word) == k * c:
            yield tuple(word)
            return
        for s in range(k):
            if counts[s]:
                counts[s] -= 1
                word.append(s)
                yield from rec()
                word.pop()
                counts[s] += 1

    yield from rec()


# ---------------------------------------------------------------- bounds

def cap_rhs(k, c, d):
    return k * min(k, c) * math.comb(k * c + d - 2, d - 1)


def trivial_rhs(k, c, d):
    # multisets of exactly d boundaries among the kc residue-distinct ones
    return math.comb(k * c + d - 1, d)


def first_fail(c, d, rhs):
    k = 1
    while (1 << k) - 1 <= rhs(k, c, d):
        k += 1
    return k


def gray_lower(c):
    b = 1 + (c.bit_length() - 1)
    return b * (c // 2) + 2 * (c % 2)


# ---------------------------------------------------------------- Gray blocks
# Independent rebuild of the PR6071 construction from its README statement:
# upward labels A, nonnegative middle fill, reversed downward labels B.

def gray_block(k, c):
    labels = []
    g = 0
    up = []
    down = []
    for i in range(1, 1 << k):
        j = (i & -i).bit_length() - 1
        labels.append(j)
        if (g >> j) & 1:
            down.append(j)
        else:
            up.append(j)
        g ^= 1 << j
    flips = [labels.count(j) for j in range(k)]
    need(max(flips) <= c, "Gray block needs c >= 2^(k-1)")
    middle = [j for j in range(k) for _ in range(c - flips[j])]
    return tuple(up + middle + list(reversed(down)))


# ---------------------------------------------------------------- controls

def run_controls():
    rejected = 0
    # 1. word with one source short
    try:
        validate_word((0, 0, 1), 2, 2)
    except Fail:
        rejected += 1
    # 2. weight identity with the wrong modulus is not an invariant
    w = gray_block(3, 4)
    q = prefixes(w, 3)
    bad = False
    for a in range(12):
        for s in range(a, 12):
            vec = [q[a][j] + q[s][j] for j in range(3)]
            m = mask_of(vec, 4)
            if m and (a + s - bin(m).count("1")) % 5 != 0:
                bad = True
    if bad:
        rejected += 1
    # 3. the Gray block with its downward suffix not reversed loses depth two
    k, c = 4, 8
    up, down, g = [], [], 0
    for i in range(1, 1 << k):
        j = (i & -i).bit_length() - 1
        (down if (g >> j) & 1 else up).append(j)
        g ^= 1 << j
    flips = [up.count(j) + down.count(j) for j in range(k)]
    mid = [j for j in range(k) for _ in range(c - flips[j])]
    wrong = tuple(up + mid + down)
    got, _ = cover(wrong, k, c, 2, audit=True)
    if len(got) < (1 << k) - 1:
        rejected += 1
    # 4. depth one cannot cover three sources (PR4248 Lemma C) at c=3
    best = max(len(cover(wd, 3, 3, 1, audit=True)[0]) for wd in multiset_words(3, 3))
    if best < 7:
        rejected += 1
    return rejected


# ---------------------------------------------------------------- main

def main() -> int:
    n_src = check_sources()

    # Exhaustive census of small words: identity + per-weight candidate count
    census = {}
    total_checks = 0
    for (k, c) in [(2, 2), (2, 3), (2, 4), (2, 5), (3, 2), (3, 3), (3, 4), (4, 2)]:
        words = 0
        best = {1: 0, 2: 0, 3: 0}
        for wd in multiset_words(k, c):
            words += 1
            for d in (1, 2, 3):
                if d == 3 and k * c > 9:
                    continue
                got, chk = cover(wd, k, c, d)
                total_checks += chk
                need(len(got) <= cap_rhs(k, c, d), "cap violated on a literal word")
                best[d] = max(best[d], len(got))
        census[f"k={k},c={c}"] = {"words": words, "max_cover_d1": best[1],
                                  "max_cover_d2": best[2],
                                  "max_cover_d3": best[3] if k * c <= 9 else None}
    expected_words = {"k=2,c=2": 6, "k=2,c=3": 20, "k=2,c=4": 70, "k=2,c=5": 252,
                      "k=3,c=2": 90, "k=3,c=3": 1680, "k=3,c=4": 34650,
                      "k=4,c=2": 2520}
    for key, n in expected_words.items():
        need(census[key]["words"] == n, f"census size {key}")
    # depth one carries at most two sources (PR4248 Lemma C): no k=3 word has depth one
    for key in ("k=3,c=2", "k=3,c=3", "k=3,c=4"):
        need(census[key]["max_cover_d1"] < 7, "unexpected depth-one three-source word")

    # Gray blocks: depth two on literal words, identity audited
    gray = 0
    gray_masks = 0
    for k in range(1, 8):
        base = max(2, 1 << (k - 1))
        for c in (base, base + 1, base + 3):
            got, chk = cover(gray_block(k, c), k, c, 2)
            need(len(got) == (1 << k) - 1, f"Gray block k={k} c={c} not depth two")
            need((1 << k) - 1 <= cap_rhs(k, c, 2), "Gray block above cap")
            total_checks += chk
            gray += 1
            gray_masks += len(got)

    # Capacity tables
    table = []
    exact_ratios = []
    for e in list(range(1, 21)) + [24, 32, 40, 48, 64, 96, 128, 256, 1024, 4096]:
        c = 1 << e
        k2 = first_fail(c, 2, cap_rhs) - 1
        t2 = first_fail(c, 2, trivial_rhs) - 1
        k3 = first_fail(c, 3, cap_rhs) - 1
        k4 = first_fail(c, 4, cap_rhs) - 1
        g = 1 + e  # Gray block size at c = 2^e
        # explicit closed form: 2^(k-1) <= k^3 c  =>  k <= 1 + log2 c + 3 log2 k
        need(k2 <= 1 + e + 3 * math.log2(k2) + 1e-9, "closed form fails")
        need(g <= k2, "Gray block exceeds the cap (impossible)")
        # n <= c * max(2, K_2/2) for depth<=2 concatenations; ratios exact
        upper_ratio = Fraction(max(4, k2), 2 * e)
        lower_ratio = Fraction(gray_lower(c), c * e)
        exact_ratios.append((lower_ratio, upper_ratio))
        table.append({"c": f"2^{e}", "gray_k": g, "cap_k_d2": k2,
                      "trivial_k_d2": t2, "cap_k_d3": k3, "cap_k_d4": k4,
                      "N_le2_lower_over_clog2c": str(round(lower_ratio, 6)),
                      "N_le2_upper_over_clog2c": str(round(upper_ratio, 6))})
    # sanity of the asymptotic message at the largest entry
    last = table[-1]
    need(exact_ratios[-1][1] < Fraction(506, 1000), "depth<=2 upper ratio not near 1/2")
    need(exact_ratios[-1][0] > Fraction(49, 100), "Gray ratio not near 1/2")
    need(last["trivial_k_d2"] > 1.99 * 4096, "trivial depth-two count should be ~2 log2 c")
    # the cap is strictly better than trivial pair counting from c = 2^7 on
    crossover = min(int(r["c"][2:]) for r in table if r["cap_k_d2"] < r["trivial_k_d2"])

    controls = run_controls()
    need(controls == 4, f"only {controls}/4 controls rejected")

    digest = hashlib.sha256(json.dumps({"census": census, "table": table},
                                       sort_keys=True).encode()).hexdigest()
    if "--table" in sys.argv:
        print(json.dumps({"census": census, "table": table}, indent=1))
    print(f"PASS_CONNECTOR_BOUNDED_DEPTH_CAP sources={n_src} census_cases={len(census)} "
          f"identity_checks={total_checks} gray_blocks={gray} gray_masks={gray_masks} "
          f"cap_beats_trivial_from=2^{crossover} controls={controls} sha256={digest[:16]}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Fail as exc:
        print(f"FAIL {exc}")
        sys.exit(1)
