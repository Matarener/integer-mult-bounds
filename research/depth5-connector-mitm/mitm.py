#!/usr/bin/env python3
"""Exact meet-in-the-middle for the depth-five chain connector with witness extraction.

decide(m, counts) returns, for every residue c whose connector exists with exactly these call counts, one
explicit word (found by backtracking through the stored deduplicated layers); residues absent from the result
have no word with these counts. Words are lists of calls 1..5 applied left to right; the product of
g_l = I + E[l][l-1] must equal I + c E[5][0].
"""
import itertools
import json
import sys
import time

import numpy as np

PAIRS = [(i, j) for i in range(6) for j in range(i)]
IDX = {p: k for k, p in enumerate(PAIRS)}
KEY_COLS = [k for k, p in enumerate(PAIRS) if p != (5, 0)]
C50 = IDX[(5, 0)]


def apply(X, l, sign, m):
    Y = X.astype(np.int16).copy()
    Y[:, IDX[(l, l - 1)]] = (Y[:, IDX[(l, l - 1)]] + sign) % m
    for i in range(l + 1, 6):
        Y[:, IDX[(i, l - 1)]] = (Y[:, IDX[(i, l - 1)]] + sign * X[:, IDX[(i, l)]].astype(np.int16)) % m
    return Y.astype(np.uint8)


def all_layers(cap, length, sign, m):
    out = [{(0,) * 5: np.zeros((1, 15), dtype=np.uint8)}]
    for _ in range(length):
        nxt = {}
        for a, X in out[-1].items():
            for l in range(1, 6):
                if a[l - 1] == cap[l - 1]:
                    continue
                b = list(a)
                b[l - 1] += 1
                nxt.setdefault(tuple(b), []).append(apply(X, l, sign, m))
        out.append({b: np.unique(np.concatenate(v), axis=0) for b, v in nxt.items()})
    return out


def keys(X, m, cols=KEY_COLS):
    w = np.zeros(len(X), dtype=np.int64)
    for k in cols:
        w = w * m + X[:, k].astype(np.int64)
    return w


def member(layer, a, row, m):
    X = layer.get(a)
    if X is None:
        return False
    return bool((X == row).all(axis=1).any())


def backtrack(layers, a, row, sign, m):
    """a word (list of letters, in the order they were appended) reaching `row` with counts a"""
    word = []
    for k in range(sum(a), 0, -1):
        for l in range(1, 6):
            if a[l - 1] == 0:
                continue
            prev = apply(row[None, :], l, -sign, m)[0]        # undo appending l
            b = list(a)
            b[l - 1] -= 1
            b = tuple(b)
            if member(layers[k - 1], b, prev, m):
                word.append(l)
                a, row = b, prev
                break
        else:
            raise AssertionError("backtrack failed")
    return word[::-1]


def product(word, m):
    X = np.zeros((1, 15), dtype=np.uint8)
    for l in word:
        X = apply(X, l, +1, m)
    return {p: int(X[0][IDX[p]]) for p in PAIRS if X[0][IDX[p]]}


def decide(m, counts):
    L = sum(counts)
    split = L // 2
    pre = all_layers(counts, split, +1, m)
    suf = all_layers(counts, L - split, -1, m)
    found = {}
    for a, P in pre[-1].items():
        b = tuple(x - y for x, y in zip(counts, a))
        S = suf[-1].get(b)
        if S is None:
            continue
        kp, ks = keys(P, m), keys(S, m)
        order = np.argsort(ks, kind="stable")
        kss = ks[order]
        pos = np.searchsorted(kss, kp)
        ok = (pos < len(kss)) & (kss[np.minimum(pos, len(kss) - 1)] == kp)
        for i in np.nonzero(ok)[0]:
            j = pos[i]
            while j < len(kss) and kss[j] == kp[i]:
                c = int((int(P[i, C50]) - int(S[order[j], C50])) % m)
                if c and c not in found:
                    left = backtrack(pre, a, P[i], +1, m)
                    right = backtrack(suf, b, S[order[j]], -1, m)   # letters prepended, in prepend order
                    word = left + right[::-1]
                    assert product(word, m) == {(5, 0): c}, "witness replay"
                    found[c] = word
                j += 1
    return found


def last_layer(cap, length, sign, m):
    """current layer only (no history): the decision-only variant used for the recorded exhaustive runs"""
    cur = {(0,) * 5: np.zeros((1, 15), dtype=np.uint8)}
    for _ in range(length):
        nxt = {}
        for a, X in cur.items():
            for l in range(1, 6):
                if a[l - 1] == cap[l - 1]:
                    continue
                b = list(a)
                b[l - 1] += 1
                nxt.setdefault(tuple(b), []).append(apply(X, l, sign, m))
        cur = {b: np.unique(np.concatenate(v), axis=0) for b, v in nxt.items()}
    return cur


def residues(m, counts):
    """sorted residues c != 0 attained by some word with exactly these call counts"""
    L = sum(counts)
    split = L // 2
    pre = last_layer(counts, split, +1, m)
    suf = last_layer(counts, L - split, -1, m)
    found = set()
    for a, P in pre.items():
        b = tuple(x - y for x, y in zip(counts, a))
        S = suf.get(b)
        if S is None:
            continue
        kp, ks = keys(P, m), keys(S, m)
        order = np.argsort(ks, kind="stable")
        kss = ks[order]
        pos = np.searchsorted(kss, kp)
        ok = (pos < len(kss)) & (kss[np.minimum(pos, len(kss) - 1)] == kp)
        for i in np.nonzero(ok)[0]:
            j = pos[i]
            while j < len(kss) and kss[j] == kp[i]:
                found.add(int((int(P[i, C50]) - int(S[order[j], C50])) % m))
                j += 1
    found.discard(0)
    return sorted(found)


if __name__ == "__main__":
    m = int(sys.argv[1])
    counts = tuple(int(x) for x in sys.argv[2].split(","))
    t = time.time()
    if len(sys.argv) > 3 and sys.argv[3] == "--residues":
        print(json.dumps({"m": m, "counts": counts, "residues": residues(m, counts),
                          "seconds": round(time.time() - t, 1)}), flush=True)
        sys.exit(0)
    res = decide(m, counts)
    print(json.dumps({"m": m, "counts": counts, "witnesses": {c: "".join(map(str, w)) for c, w in sorted(res.items())},
                      "seconds": round(time.time() - t, 1)}), flush=True)
