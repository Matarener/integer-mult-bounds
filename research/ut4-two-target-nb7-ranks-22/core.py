#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Self-contained two-role UT4(F2) profile/key primitives for the n_b=7 (2,2) census.

Reimplements the r=2 formulas of CrocSwap/integer-mult-bounds#1690
(research/ut4-two-target-r2/search.py) needed here: rank-one couplings,
side tables, transport keys, and GL2-minimal zero-sum middle sequences.
Length-7 side-zero keys use a 3+4 meet-in-the-middle. Does not import that
module. Prepared by Wentao Li with substantial AI assistance. Apache-2.0.
"""
import itertools
from collections import defaultdict

PAR = [bin(m).count("1") & 1 for m in range(128)]
SOL = {}
for _u0 in range(128):
    for _u1 in range(128):
        for _e0 in (0, 1):
            for _e1 in (0, 1):
                SOL[(_u0, _u1, _e0, _e1)] = [
                    m for m in range(128)
                    if PAR[_u0 & m] == _e0 and PAR[_u1 & m] == _e1
                ]


def need(ok, message):
    if not ok:
        raise ValueError(message)


def mm(A, B, r=2):
    out = 0
    for i in range(r):
        for j in range(r):
            s = 0
            for k in range(r):
                s ^= (A >> (i * r + k)) & (B >> (k * r + j)) & 1
            out |= s << (i * r + j)
    return out


def rank_one(x, y, r=2):
    return sum(
        1 << (i * r + j)
        for i in range(r)
        for j in range(r)
        if (x >> i) & 1 and (y >> j) & 1
    )


def split(N, r=2):
    rows = [(N >> (i * r)) & ((1 << r) - 1) for i in range(r)]
    y = next(v for v in rows if v)
    x = sum(1 << i for i, v in enumerate(rows) if v)
    need(all(v in (0, y) for v in rows) and rank_one(x, y, r) == N, "not rank one")
    return x, y


def diag(w, r):
    return sum(1 << (i * r + i) for i in range(w))


def couplings(r=2):
    return [(x, y) for x in range(1, 1 << r) for y in range(1, 1 << r)]


def gl(r=2):
    I = diag(r, r)
    inv = {}
    for g in range(1 << (r * r)):
        for h in range(1 << (r * r)):
            if mm(g, h, r) == I:
                inv[g] = h
    return inv


def side_tables(bseq, r=2):
    tab = []
    for j, N in enumerate(bseq):
        L = R = 0
        for i, M in enumerate(bseq):
            if i < j:
                L ^= M
            elif i > j:
                R ^= M
        tab.append([
            mm(p, N, r)
            | mm(N, p, r) << 4
            | mm(mm(p, N, r), p, r) << 8
            | (mm(mm(L, p, r), N, r) ^ mm(mm(N, p, r), R, r)) << 12
            for p in range(16)
        ])
    return tab


def side_coeffs(bseq, P, r=2):
    ab = ba = aba = bab = 0
    for j, (N, p) in enumerate(zip(bseq, P)):
        pn = mm(p, N, r)
        ab ^= pn
        ba ^= mm(N, p, r)
        aba ^= mm(pn, p, r)
        for k in range(j + 1, len(bseq)):
            bab ^= mm(mm(N, P[k] ^ p, r), bseq[k], r)
    return ab, ba, aba, bab


def cross_coeffs(bseq, P, Q, r=2):
    abc = cba = 0
    for N, p, q in zip(bseq, P, Q):
        abc ^= mm(mm(p, N, r), q, r)
        cba ^= mm(mm(q, N, r), p, r)
    return abc, cba


def key(bseq, P):
    U, W = [0, 0], [0, 0]
    for j, (N, p) in enumerate(zip(bseq, P)):
        x, y = split(N)
        for s in range(2):
            u = w = 0
            for k in range(2):
                u ^= (p >> (2 * s + k)) & (x >> k) & 1
                w ^= (y >> k) & (p >> (2 * k + s)) & 1
            U[s] |= u << j
            W[s] |= w << j
    return U[0], U[1], W[0], W[1]


def key_cross(kp, kq):
    abc = cba = 0
    for s in range(2):
        for t in range(2):
            abc |= PAR[kp[s] & kq[2 + t]] << (2 * s + t)
            cba |= PAR[kq[s] & kp[2 + t]] << (2 * s + t)
    return abc, cba


def key_pairs(akeys, ckeys=None, target=(9, 9)):
    ckeys = akeys if ckeys is None else ckeys
    abc = target[0]
    byW = defaultdict(list)
    for k in ckeys:
        byW[k[2:]].append(k)
    for ka in akeys:
        for m0 in SOL[(ka[0], ka[1], abc & 1, abc >> 2 & 1)]:
            for m1 in SOL[(ka[0], ka[1], abc >> 1 & 1, abc >> 3 & 1)]:
                for kc in byW.get((m0, m1), ()):
                    if key_cross(ka, kc) == target:
                        yield ka, kc


def middle_sequences(nb=7, symmetric=True, r=2):
    inv = gl(r)
    R1 = sorted(rank_one(x, y, r) for x, y in couplings(r))
    for bt in itertools.product(R1, repeat=nb):
        tot = 0
        for N in bt:
            tot ^= N
        if tot:
            continue
        if symmetric and any(
            tuple(mm(mm(g, N, r), h, r) for N in bt) < bt for g, h in inv.items()
        ):
            continue
        yield bt


def ranks_XY(bseq, r=2):
    xs, ys = [], []
    for N in bseq:
        x, y = split(N, r)
        xs.append(x)
        ys.append(y)

    def rk(vecs):
        rows = list(vecs)
        rank = 0
        for bit in range(r):
            piv = None
            for i in range(rank, len(rows)):
                if rows[i] >> bit & 1:
                    piv = i
                    break
            if piv is None:
                continue
            rows[rank], rows[piv] = rows[piv], rows[rank]
            for i in range(len(rows)):
                if i != rank and rows[i] >> bit & 1:
                    rows[i] ^= rows[rank]
            rank += 1
        return rank

    return rk(xs), rk(ys)


def side_zero_keys(bseq):
    """Set of transport keys of all side-zero 7-profiles, via 3+4 MITM on keys."""
    need(len(bseq) == 7, "n_b=7 only")
    tab = side_tables(bseq)
    ku0, ku1, kw0, kw1 = [], [], [], []
    for N in bseq:
        x, y = split(N)
        a0, a1, b0, b1 = [], [], [], []
        for p in range(16):
            a0.append(((p >> 0) & 1) & (x & 1) ^ ((p >> 1) & 1) & ((x >> 1) & 1))
            a1.append(((p >> 2) & 1) & (x & 1) ^ ((p >> 3) & 1) & ((x >> 1) & 1))
            b0.append((y & 1) & ((p >> 0) & 1) ^ ((y >> 1) & 1) & ((p >> 2) & 1))
            b1.append((y & 1) & ((p >> 1) & 1) ^ ((y >> 1) & 1) & ((p >> 3) & 1))
        ku0.append(a0)
        ku1.append(a1)
        kw0.append(b0)
        kw1.append(b1)
    left = {}
    for code in range(16 ** 3):
        p0, p1, p2 = code & 15, (code >> 4) & 15, (code >> 8) & 15
        v = tab[0][p0] ^ tab[1][p1] ^ tab[2][p2]
        left.setdefault(v, set()).add((
            ku0[0][p0] | (ku0[1][p1] << 1) | (ku0[2][p2] << 2),
            ku1[0][p0] | (ku1[1][p1] << 1) | (ku1[2][p2] << 2),
            kw0[0][p0] | (kw0[1][p1] << 1) | (kw0[2][p2] << 2),
            kw1[0][p0] | (kw1[1][p1] << 1) | (kw1[2][p2] << 2),
        ))
    keys = set()
    joins = 0
    for code in range(16 ** 4):
        p3 = code & 15
        p4 = (code >> 4) & 15
        p5 = (code >> 8) & 15
        p6 = (code >> 12) & 15
        v = tab[3][p3] ^ tab[4][p4] ^ tab[5][p5] ^ tab[6][p6]
        L = left.get(v)
        if not L:
            continue
        ru0 = ku0[3][p3] | (ku0[4][p4] << 1) | (ku0[5][p5] << 2) | (ku0[6][p6] << 3)
        ru1 = ku1[3][p3] | (ku1[4][p4] << 1) | (ku1[5][p5] << 2) | (ku1[6][p6] << 3)
        rw0 = kw0[3][p3] | (kw0[4][p4] << 1) | (kw0[5][p5] << 2) | (kw0[6][p6] << 3)
        rw1 = kw1[3][p3] | (kw1[4][p4] << 1) | (kw1[5][p5] << 2) | (kw1[6][p6] << 3)
        for u0, u1, w0, w1 in L:
            joins += 1
            # Pack four 7-bit limbs into one int for cheaper set membership.
            keys.add(
                (u0 | (ru0 << 3))
                | ((u1 | (ru1 << 3)) << 7)
                | ((w0 | (rw0 << 3)) << 14)
                | ((w1 | (rw1 << 3)) << 21)
            )
    return keys, joins


def count_key_pairs(keys, target=(9, 9)):
    """Count abc=cba=target key pairs on packed 28-bit keys from side_zero_keys."""
    need(target == (9, 9), "this counter is specialized to I_2")
    byW = defaultdict(list)
    byU = defaultdict(list)
    for p in keys:
        u0, u1 = p & 127, (p >> 7) & 127
        w0, w1 = (p >> 14) & 127, (p >> 21) & 127
        byW[(w0, w1)].append(p)
        byU[(u0, u1)].append(p)
    w_items = list(byW.items())
    n = 0
    for (u0, u1), kas in byU.items():
        cands = []
        for (m0, m1), lst in w_items:
            if (
                PAR[u0 & m0] == 1
                and PAR[u1 & m0] == 0
                and PAR[u0 & m1] == 0
                and PAR[u1 & m1] == 1
            ):
                cands.extend(lst)
        if not cands:
            continue
        for ka in kas:
            kaw0, kaw1 = (ka >> 14) & 127, (ka >> 21) & 127
            for kc in cands:
                kcu0, kcu1 = kc & 127, (kc >> 7) & 127
                cba = (
                    PAR[kcu0 & kaw0]
                    | (PAR[kcu0 & kaw1] << 1)
                    | (PAR[kcu1 & kaw0] << 2)
                    | (PAR[kcu1 & kaw1] << 3)
                )
                if cba == 9:
                    n += 1
    return n
