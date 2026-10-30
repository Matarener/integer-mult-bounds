#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Independent n_b=7 ranks-(2,2) key-pair census (does not import verify.py).

Rebuilds side-zero transport keys by enumerating 3+4 profile halves as
base-16 integers and assembling keys via per-position bit lists, then pairs
keys for abc=cba=I. Prepared by Wentao Li with substantial AI assistance.
Apache-2.0.
"""
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor
import itertools
import json
import multiprocessing
from pathlib import Path

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

HERE = Path(__file__).resolve().parent
PASS = "PASS_UT4_TWO_TARGET_NO_NB7_RANKS_22_INDEPENDENT"


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
    return x, y


def diag(w, r):
    return sum(1 << (i * r + i) for i in range(w))


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


def gl_inv(r=2):
    I = diag(r, r)
    return {
        g: h
        for g in range(1 << (r * r))
        for h in range(1 << (r * r))
        if mm(g, h, r) == I
    }


def canonical_middles(nb=7, r=2):
    inv = gl_inv(r)
    R1 = sorted(
        rank_one(x, y, r)
        for x in range(1, 1 << r)
        for y in range(1, 1 << r)
    )
    out = []
    for bt in itertools.product(R1, repeat=nb):
        tot = 0
        for N in bt:
            tot ^= N
        if tot:
            continue
        if any(tuple(mm(mm(g, N, r), h, r) for N in bt) < bt for g, h in inv.items()):
            continue
        out.append(bt)
    return out


def keys_for_middle(bseq):
    """Enumerate profile halves as base-16 integers (3+4 MITM, list-built keys)."""
    need(len(bseq) == 7, "n_b=7 only")
    tab = side_tables(bseq)
    kcontrib = []
    for N in bseq:
        x, y = split(N)
        row = []
        for p in range(16):
            bits = [0, 0, 0, 0]
            for s in range(2):
                u = w = 0
                for k in range(2):
                    u ^= (p >> (2 * s + k)) & (x >> k) & 1
                    w ^= (y >> k) & (p >> (2 * k + s)) & 1
                bits[s] = u
                bits[2 + s] = w
            row.append(bits)
        kcontrib.append(row)
    left = {}
    for code in range(16 ** 3):
        p0, p1, p2 = code & 15, (code >> 4) & 15, (code >> 8) & 15
        v = tab[0][p0] ^ tab[1][p1] ^ tab[2][p2]
        partial = [0, 0, 0, 0]
        for t in range(4):
            partial[t] = (
                kcontrib[0][p0][t]
                | (kcontrib[1][p1][t] << 1)
                | (kcontrib[2][p2][t] << 2)
            )
        left.setdefault(v, set()).add(tuple(partial))
    keys = set()
    joins = 0
    for code in range(16 ** 4):
        p3, p4, p5, p6 = (
            code & 15,
            (code >> 4) & 15,
            (code >> 8) & 15,
            (code >> 12) & 15,
        )
        v = tab[3][p3] ^ tab[4][p4] ^ tab[5][p5] ^ tab[6][p6]
        L = left.get(v)
        if not L:
            continue
        right = [0, 0, 0, 0]
        for t in range(4):
            right[t] = (
                kcontrib[3][p3][t]
                | (kcontrib[4][p4][t] << 1)
                | (kcontrib[5][p5][t] << 2)
                | (kcontrib[6][p6][t] << 3)
            )
        for partial in L:
            joins += 1
            u0 = partial[0] | (right[0] << 3)
            u1 = partial[1] | (right[1] << 3)
            w0 = partial[2] | (right[2] << 3)
            w1 = partial[3] | (right[3] << 3)
            keys.add(u0 | (u1 << 7) | (w0 << 14) | (w1 << 21))
    return keys, joins


def count_pairs(keys):
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


def worker(bt):
    keys, joins = keys_for_middle(bt)
    return joins, len(keys), count_pairs(keys)


def read_json(path):
    def pairs(items):
        obj = {}
        for k, v in items:
            need(k not in obj, "duplicate JSON key: " + k)
            obj[k] = v
        return obj

    return json.loads(path.read_text(), object_pairs_hook=pairs)


def main():
    need("verify" not in globals(), "must not bind verify")
    cert = read_json(HERE / "CERTIFICATE.json")
    all_m = canonical_middles()
    good = [bt for bt in all_m if ranks_XY(bt) == (2, 2)]
    need(len(all_m) == cert["canonical_zero_sum_middles"], "canonical count")
    need(len(good) == cert["rank_XY_exactly_2_2"], "rank filter count")
    tot_join = tot_keys = tot_kp = 0
    max_keys = 0
    ctx = multiprocessing.get_context("fork")
    with ProcessPoolExecutor(max_workers=4, mp_context=ctx) as pool:
        for joins, nk, kp in pool.map(worker, good, chunksize=64):
            tot_join += joins
            tot_keys += nk
            tot_kp += kp
            max_keys = max(max_keys, nk)
    need(tot_kp == 0, "independent census found an I-pair")
    need(tot_keys == cert["keys_sum"], "keys_sum mismatch")
    need(tot_join == cert["side_zero_key_joins"], "join count mismatch")
    need(max_keys == cert["max_keys_per_middle"], "max keys mismatch")
    need(cert["key_pairs_abc_cba_I"] == 0, "certificate claims pairs")
    print(PASS, "key_pairs=0", "keys_sum=" + str(tot_keys))


if __name__ == "__main__":
    main()
