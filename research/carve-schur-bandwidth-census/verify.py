#!/usr/bin/env python3
"""Exhaustive independent check of #4373's separated-carve Schur bandwidth theorem.

For a bandwidth-b path matrix on 0..n-1 and ANY eliminated set E, the generic Schur complement onto the
survivors, written in boundary order, has bandwidth

    bw(E) = max( max over components C of E in the band graph of  #{survivors in [min C - b, max C + b]} - 1,
                 max over survivor pairs u < v with v - u <= b of their boundary-order distance ).

(Fill-path lemma: a survivor pair fills iff both ends touch one eliminated component.) The verifier checks
this formula against an actual Schur complement with random entries over a 61-bit prime field, for every
subset E of every path n <= NMAX and b = 1, 2, 3. It then reads off #4373's claims: with at least b
survivors between consecutive interiors the bandwidth is at most 2b - 1, attained exactly when some
interior has b survivors on both sides; separators of b - 1 survivors grow without bound.
Separately written; imports nothing from #4373.
Ryanson Jonathan with Claude Code (Claude Opus 5.5) assistance. Apache-2.0.
"""
from fractions import Fraction as Q
import json
import random
import sys

PRIME = 2**61 - 1
NMAX = 15
rng = random.Random(4373)


def need(condition, message):
    if not condition:
        raise AssertionError(message)


def runs(elim):
    """maximal runs of consecutive eliminated indices, as (L, R)"""
    out, cur = [], None
    for i in sorted(elim):
        if cur and i == cur[1] + 1:
            cur[1] = i
        else:
            cur = [i, i]
            out.append(cur)
    return [tuple(r) for r in out]


def formula(n, b, elim):
    surv = [i for i in range(n) if i not in elim]
    pos = {v: k for k, v in enumerate(surv)}
    best = 0
    # components of elim in the band graph: consecutive eliminated indices at distance <= b
    comps, cur = [], None
    for i in sorted(elim):
        if cur and i - cur[1] <= b:
            cur[1] = i
        else:
            cur = [i, i]
            comps.append(cur)
    for lo, hi in comps:
        rim = [v for v in surv if lo - b <= v <= hi + b]
        if rim:
            best = max(best, pos[rim[-1]] - pos[rim[0]])
    for u in surv:
        for v in surv:
            if u < v <= u + b:
                best = max(best, pos[v] - pos[u])
    return best


def schur_bandwidth(n, b, elim):
    """eliminate elim (in index order) from a random band matrix mod PRIME; boundary-order bandwidth"""
    while True:
        a = [[rng.randrange(1, PRIME) if abs(i - j) <= b else 0 for j in range(n)] for i in range(n)]
        ok = True
        for e in sorted(elim):
            piv = a[e][e]
            if piv == 0:
                ok = False
                break
            inv = pow(piv, PRIME - 2, PRIME)
            col = [a[i][e] for i in range(n)]
            row = a[e]
            for i in range(n):
                if i != e and col[i]:
                    f = col[i] * inv % PRIME
                    ai = a[i]
                    for j in range(n):
                        if row[j]:
                            ai[j] = (ai[j] - f * row[j]) % PRIME
            for i in range(n):
                a[i][e] = a[e][i] = 0
        if ok:
            break
    surv = [i for i in range(n) if i not in elim]
    best = 0
    for x, u in enumerate(surv):
        for y, v in enumerate(surv):
            if a[u][v]:
                best = max(best, abs(x - y))
    return best


def separated(n, b, elim):
    """at least b survivors between successive interiors"""
    rs = runs(elim)
    return all(rs[k + 1][0] - rs[k][1] - 1 >= b for k in range(len(rs) - 1))


def two_sided(n, b, elim):
    return any(L >= b and R <= n - 1 - b for L, R in runs(elim))


def witness_4285():
    """7x7 bandwidth-2 host, unit diagonal, off-diagonal -1/8, eliminate {2,3,4}"""
    n, b, elim = 7, 2, (2, 3, 4)
    a = [[Q(1) if i == j else (Q(-1, 8) if abs(i - j) <= b else Q(0)) for j in range(n)] for i in range(n)]
    for e in elim:
        piv = a[e][e]
        for i in range(n):
            if i != e and a[i][e]:
                f = a[i][e] / piv
                a[i] = [x - f * y for x, y in zip(a[i], a[e])]
    surv = [i for i in range(n) if i not in elim]
    far = a[surv[0]][surv[-1]]
    bw = max(abs(x - y) for x, u in enumerate(surv) for y, v in enumerate(surv) if a[u][v] != 0)
    s = [[a[u][v] for v in surv] for u in surv]
    k = len(s)
    w = [row[:] + [Q(int(i == j)) for j in range(k)] for i, row in enumerate(s)]
    for c in range(k):
        w[c] = [x / w[c][c] for x in w[c]]
        for r in range(k):
            if r != c:
                f = w[r][c]
                w[r] = [x - f * y for x, y in zip(w[r], w[c])]
    inv = [row[k:] for row in w]
    inf = max(sum(abs(x) for x in row) for row in inv)
    one = max(sum(abs(inv[i][j]) for i in range(k)) for j in range(k))
    return far, bw, inf, one


def main():
    total = cap_cases = sharp = 0
    for b in (1, 2, 3):
        for n in range(1, NMAX + 1):
            for mask in range(1, 2 ** n):
                elim = {i for i in range(n) if mask >> i & 1}
                if len(elim) == n:
                    continue
                f = formula(n, b, elim)
                s = schur_bandwidth(n, b, elim)
                need(s == f, f"formula = generic Schur bandwidth at n={n}, b={b}, E={sorted(elim)}")
                total += 1
                if separated(n, b, elim):
                    cap_cases += 1
                    need(f <= 2 * b - 1, "#4373: separated carve has bandwidth <= 2b-1")
                    need((f == 2 * b - 1) == two_sided(n, b, elim) or b == 1 and f == 1,
                         "sharp exactly at a two-sided interior")
                    sharp += f == 2 * b - 1
    # necessity: singleton interiors separated by b-1 survivors on a long path
    growth = {}
    for b in (2, 3):
        for k in range(1, 9):
            n = b + k * b + b                          # b ends, k singletons spaced by b-1 survivors
            elim = {b + j * b for j in range(k)}
            f = formula(n, b, elim)
            need(f == schur_bandwidth(n, b, elim), "chain: formula = Schur")
            growth.setdefault(b, []).append(f)
        need(growth[b][-1] > 2 * b - 1 and growth[b] == sorted(growth[b]), "under-separation grows")
        need(growth[b] == [2 * b - 1 + (k - 1) * (b - 1) for k in range(1, 9)], "chain: bandwidth formula in k")
    # #4373's own chain: b = 2, one survivor at each end and between singletons -> bandwidth = count
    for k in range(1, 9):
        elim = {1 + 2 * j for j in range(k)}
        n = 2 * k + 1
        need(formula(n, 2, elim) == schur_bandwidth(n, 2, elim) == k, "#4373 chain: bandwidth = interior count")
    far, bw, inf, one = witness_4285()
    need(far == Q(-1, 432) and bw == 3, "#4285 witness: far entry -1/432, bandwidth 3 = 2b-1")
    need(inf == one == Q(488, 389), "#4285 witness: both inverse norms 488/389")
    print(json.dumps({
        "status": "PASS_CARVE_SCHUR_BANDWIDTH_CENSUS",
        "layouts_checked": total, "paths": f"n = 1..{NMAX}", "bandwidths": [1, 2, 3],
        "separated_layouts": cap_cases, "separated_attaining_2b_minus_1": sharp,
        "under_separated_chain_bandwidths": growth,
        "witness_4285": {"far_entry": str(far), "bandwidth": bw},
        "new_kappa_claimed": False,
    }, indent=1))


if __name__ == "__main__":
    sys.exit(main())
