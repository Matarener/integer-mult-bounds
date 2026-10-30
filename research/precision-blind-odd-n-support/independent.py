#!/usr/bin/env python3
"""Independent closed-form replay of odd-n dual-scale support classification.

Imports no algebra.py. Checks far/near closed forms, n² exclusivity on a
concrete slice, and illegal-middle emptiness.

Prepared by Wentao Li with substantial AI assistance. Apache-2.0.
"""
from __future__ import annotations

import json
import sys
from itertools import product
from math import gcd
from pathlib import Path

HERE = Path(__file__).resolve().parent


def need(ok, message):
    if not ok:
        raise SystemExit(f"FAIL_INDEPENDENT: {message}")


def reject_duplicate_keys(pairs):
    keys = [k for k, _ in pairs]
    if len(keys) != len(set(keys)):
        raise ValueError("duplicate JSON key")
    return dict(pairs)


def units(M):
    return [x for x in range(M) if gcd(x, M) == 1]


def classify(a, M):
    n = len(a)
    goods = []
    for i, j in product(range(n), repeat=2):
        found = None
        for s in units(M):
            for t in units(M):
                p_h = [((s * a[k]) if k == i else a[k]) % M for k in range(n)]
                p_d = [None] * n
                conflict = False
                for k in range(n):
                    idx = n - 1 - k
                    val = ((a[idx] * pow(t, -1, M)) if k == j else a[idx]) % M
                    if p_d[idx] is None:
                        p_d[idx] = val
                    elif p_d[idx] != val:
                        conflict = True
                        break
                if conflict or p_h != p_d:
                    continue
                p = p_h
                if all((p[k] * p[n - 1 - k]) % M == 1 for k in range(n)):
                    found = (s, t, p)
                    break
            if found:
                break
        if found:
            goods.append((i, j, found))
    return goods


def fa(h, d, a, M):
    n = len(a)
    nh = tuple((a[k] * d[n - 1 - k]) % M for k in range(n))
    nd = tuple(
        (pow(a[n - 1 - k], -1, M) * h[n - 1 - k]) % M for k in range(n)
    )
    return nh, nd


def norm(nh, nd, i, j, s, t, M):
    nh = list(nh)
    nd = list(nd)
    nh[i] = (nh[i] * s) % M
    nd[j] = (nd[j] * t) % M
    return tuple(nh), tuple(nd)


def fa_p(h, d, p, M):
    n = len(p)
    nh = tuple((p[k] * d[n - 1 - k]) % M for k in range(n))
    nd = tuple(
        (pow(p[n - 1 - k], -1, M) * h[n - 1 - k]) % M for k in range(n)
    )
    return nh, nd


def main():
    cert = json.loads(
        (HERE / "CERTIFICATE.json").read_text(), object_pairs_hook=reject_duplicate_keys
    )
    need(cert["no_new_kappa"] is True, "kappa")
    need(cert["boolean_meter_inventory"] is False, "meters")
    need(cert["n2_census_reprinted"] is False, "n2")
    need(cert["n3_grid_reprinted"] is False, "n3")
    need(cert["dimensions"] == [5, 7], "dims")

    # Independent n=5 classification at (3,2), middles (1,1,1).
    M, a0, inv = 9, 4, 7
    a = [a0, 1, 1, 1, 1]
    goods = classify(a, M)
    need(len(goods) == 2, "exactly two")
    keys = {(i, j) for i, j, _ in goods}
    need(keys == {(0, 4), (4, 0)}, "far+near only")
    for i, j, (s, t, p) in goods:
        need(s == inv and t == a0, "scales")
        h = (1, 2, 3, 4, 5)
        d = (6, 7, 8, 0, 1)
        got = norm(*fa(h, d, a, M), i, j, s, t, M)
        want = fa_p(h, d, p, M)
        need(got == want, "bank")
    far = next(g for g in goods if g[0] == 4)
    near = next(g for g in goods if g[0] == 0)
    need(far[2][2] == [4, 1, 1, 1, 7], "far target")
    need(near[2][2] == [1, 1, 1, 1, 1], "near target")

    # Illegal middles: zero supports.
    a_bad = [4, 1, 1, 8, 1]
    need(len(classify(a_bad, M)) == 0, "illegal empty")

    # n=7 far+near closed form spot.
    a7 = [4, 1, 1, 1, 1, 1, 1]
    goods7 = classify(a7, M)
    need({(i, j) for i, j, _ in goods7} == {(0, 6), (6, 0)}, "n7 keys")

    # Certificate rows agree on good_supports==2 / illegal==0.
    for row in cert["rows_n5"] + cert["rows_n7"]:
        need(row["good_supports"] == 2, "cert goods")
        need(row["far_end"]["scale_H"] == row["inv_a0"], "cert far s")
        need(row["near_end"]["target"][0] == 1, "cert near")
        need((row["a0"] * row["inv_a0"]) % row["modulus"] == 1, "reciprocal")
        need(pow(row["a0"], (row["p"] - 1) // 2, row["p"]) == 1, "QR")
    for row in cert["illegal_middle_rows"]:
        need(row["good_supports"] == 0, "cert illegal")

    # n=3 near-end citation without 30-row reprint.
    goods3 = classify([4, 1, 1], M)
    need({(i, j) for i, j, _ in goods3} == {(0, 2), (2, 0)}, "n3 keys")
    need(cert["n3_near_end_citation"]["target"] == [1, 1, 1], "near cite")

    print(
        "PASS_INDEPENDENT_PRECISION_BLIND_ODD_N_SUPPORT "
        f"n5_rows={len(cert['rows_n5'])} n7_rows={len(cert['rows_n7'])} "
        f"goods=far+near illegal_zero={len(cert['illegal_middle_rows'])} "
        f"boolean_meters=false n2_census=false n3_grid=false no_new_kappa"
    )


if __name__ == "__main__":
    main()
