#!/usr/bin/env python3
"""Stdlib verifier: contamination-charge construction + exact 3+3 twisted-exit decision + controls.

PASS line: PASS_TWISTED_FEEDBACK_CONTAMINATION_LEMMA
"""
import os
import random
import sys
from collections import deque

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lemma import apply, identity, simulate  # noqa: E402
import independent33  # noqa: E402


def bfs(n, gens):
    start = tuple(identity(n))
    dist, par, queue = {start: 0}, {start: None}, deque([start])
    while queue:
        x = queue.popleft()
        for d, s in gens:
            y = list(x)
            y[d] ^= y[s]
            y = tuple(y)
            if y not in dist:
                dist[y], par[y] = dist[x] + 1, (x, (d, s))
                queue.append(y)
    return dist, par


def word_to(par, x):
    w = []
    while par[x] is not None:
        x, g = par[x]
        w.append(g)
    return w[::-1]


def mul(A, B):
    out = []
    for a in A:
        v, k = 0, 0
        while a:
            if a & 1:
                v ^= B[k]
            a >>= 1
            k += 1
        out.append(v)
    return out


def elim_word(G, n):
    """A word w with apply(w, I) == G (Gaussian elimination; every op is an involution)."""
    A, ops = list(G), []
    for c in range(n):
        p = next(r for r in range(c, n) if A[r] >> c & 1)
        if p != c:
            A[c] ^= A[p]
            ops.append((c, p))
        for r in range(n):
            if r != c and A[r] >> c & 1:
                A[r] ^= A[c]
                ops.append((r, c))
    assert A == identity(n)
    return ops[::-1]


def invertible(rows, n):
    A = list(rows)
    for c in range(n):
        p = next((r for r in range(c, n) if A[r] >> c & 1), None)
        if p is None:
            return False
        A[c], A[p] = A[p], A[c]
        for r in range(n):
            if r != c and A[r] >> c & 1:
                A[r] ^= A[c]
    return True


def tally(totals, led):
    totals["singular"] += led["singular_reads"] > 0
    totals["swaps"] += led["relabel_swaps"] > 0
    totals["contaminated"] += led["contaminated_reads"] > 0


def check_lemma():
    totals = dict(exhaustive_words=0, random_words=0, free_words=0, singular=0, swaps=0, contaminated=0)
    rng = random.Random(20261019)
    for n in (2, 3, 4):                       # every element of every parabolic, n <= 4
        full = [(d, s) for d in range(n) for s in range(n) if d != s]
        Df, Pf = bfs(n, full)
        assert len(Df) == {2: 6, 3: 168, 4: 20160}[n]
        for H in range(1, n):
            Y = n - H
            Dr, _ = bfs(n, [(d, s) for d, s in full if not (d < H <= s)])
            for X in Dr:
                detour = [rng.choice(full) for _ in range(rng.randrange(1, 12))]
                inv = apply(list(reversed(detour)), identity(n))
                for w in (word_to(Pf, X), detour + word_to(Pf, tuple(mul(list(X), inv)))):
                    assert apply(w, identity(n)) == list(X)
                    out, led = simulate(w, H, Y)
                    assert apply(out, identity(n)) == list(X) and Dr[X] <= len(out)
                    totals["exhaustive_words"] += 1
                    tally(totals, led)
    for n in range(2, 9):                     # random words ending in P, n <= 8, every split
        full = [(d, s) for d in range(n) for s in range(n) if d != s]
        for H in range(1, n):
            Y = n - H
            for trial in range(300):
                while True:
                    X = [rng.getrandbits(H) for _ in range(H)] + [rng.getrandbits(n) for _ in range(Y)]
                    if trial % 2:             # exact twisted exit [[T,0],[K,I]]
                        X = X[:H] + [(X[H + j] & ((1 << H) - 1)) | 1 << (H + j) for j in range(Y)]
                    if invertible(X, n):
                        break
                u = [rng.choice(full) for _ in range(rng.randrange(0, 3 * n))]
                w = u + elim_word(mul(X, apply(list(reversed(u)), identity(n))), n)
                assert apply(w, identity(n)) == X
                out, led = simulate(w, H, Y)
                assert led["final_in_P"] and apply(out, identity(n)) == X
                totals["random_words"] += 1
                tally(totals, led)
            for _ in range(100):              # arbitrary endpoints: per-gate frame invariant only
                simulate([rng.choice(full) for _ in range(rng.randrange(1, 40))], H, Y)
                totals["free_words"] += 1
    assert totals["singular"] > 0 and totals["swaps"] > 0 and totals["contaminated"] > 0
    return totals


def controls():
    """Each control exercises a way the claim could be wrong and must fail in the stated way."""
    passed = 0
    # 1. The invertibility gap is real: after h^=y; y^=h the target block is 0, so no
    #    frame read off M's target block exists there; the construction still covers the word (two swaps = I).
    w = [(0, 1), (1, 0), (0, 1), (0, 1), (1, 0), (0, 1)]
    assert (apply(w[:2], identity(2))[1] >> 1) & 1 == 0, "control 1: target block must be singular"
    out, led = simulate(w, 1, 1)
    assert led["singular_reads"] == 2 and apply(out, identity(2)) == identity(2)
    passed += 1
    # 2. Deleting feedback is wrong at a contaminated read: h^=y0; y1^=h; h^=y0 (H=1, Y=2).
    w = [(0, 1), (2, 0), (0, 1)]
    target = apply(w, identity(3))
    naive = apply([g for g in w if not (g[0] < 1 <= g[1])], identity(3))
    assert naive != target, "control 2: naive deletion must fail"
    out, led = simulate(w, 1, 2)
    assert apply(out, identity(3)) == target and led["charge"] == 1 and len(out) == 2
    passed += 1
    # 3. The charge is necessary: L - f = 1 < d_P(target) = 2 for that word.
    full = [(d, s) for d in range(3) for s in range(3) if d != s]
    Dr, _ = bfs(3, [(d, s) for d, s in full if not (d < 1 <= s)])
    assert Dr[tuple(target)] == 2 > len(w) - led["virtual_feedback"], "control 3"
    passed += 1
    # 4. A forged extra gate is detected by replay.
    try:
        assert apply(out + [(1, 2)], identity(3)) == target, "forged word"
    except AssertionError as exc:
        assert "forged word" in str(exc)
        passed += 1
    # 5. A self XOR is rejected.
    try:
        simulate([(1, 1)], 1, 1)
    except ValueError:
        passed += 1
    return passed


def main():
    totals = check_lemma()
    print("lemma", totals, flush=True)
    exits, classes, twisted, adv, hist = independent33.main()
    assert (exits, classes, twisted, adv) == (86016, 3478, 85504, 0)
    assert hist == [(1, 6), (2, 96), (3, 744), (4, 3594), (5, 11463), (6, 23948), (7, 29259), (8, 15438), (9, 956)]
    n_controls = controls()
    assert n_controls == 5
    print(f"PASS_TWISTED_FEEDBACK_CONTAMINATION_LEMMA exits33={exits} twisted={twisted} classes={classes} "
          f"strict_feedback_advantage={adv} max_restricted_min={max(d for d, _ in hist)} "
          f"lemma_words={totals['exhaustive_words'] + totals['random_words']} controls={n_controls}")


if __name__ == "__main__":
    main()
