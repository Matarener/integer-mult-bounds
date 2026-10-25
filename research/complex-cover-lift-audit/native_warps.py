#!/usr/bin/env python3
"""Every native warp of the four PR4088 words is a Z4-monomial matrix.

A warp event of operator k moving a lender from frame U to frame E executes
Z = T_E K_G^(+-1) T_U^-1 on the lender's 9 hosted axes.  Here K_G is the
phase-corrected permutation |x> -> i^(q(Gx)) |Gx>, with q the Z4 form of
M = I + G^-T G^-1, and T_U = K_c (C on |U| axes) K_c^-1 with K_c the change of
basis onto U.  These definitions are read from PR4088's native bw_gauss.py;
nothing is imported from it.

For every warp edge class (sign, op, from, to) of the four canonical words,
the script checks that Z has exactly one nonzero entry per row and column,
each in {1, i, -1, -i} (global phase included).  It also binds each
canonical word to its literal input word by B position, G columns and frame
spans.  Controls: the plain permutation P_G in place of K_G is not monomial
for any tested class, and some swapped-frame products are not monomial.
"""
import gzip
import json
from pathlib import Path

import numpy as np

PKG = Path(__file__).resolve().parent
MIXED = PKG.parents[1] / "research" / "staged544-mixed-fourth-entry"
PAIRS = [("FOUR-base", "NATIVE-CANONICAL-base"), ("FOUR-extra", "NATIVE-CANONICAL-extra"),
         ("THREE-base", "THREE-CANONICAL-base"), ("THREE-extra", "THREE-CANONICAL-extra")]
H = 9
NN = 1 << H
C1 = np.array([[1 + 1j, 1 - 1j], [1 - 1j, 1 + 1j]]) / 2
UNITS = np.array([1, 1j, -1, -1j])


def lin(cols, x):
    out = 0
    for i, c in enumerate(cols):
        if x >> i & 1:
            out ^= c
    return out


def inverse_cols(cols):
    back = [0] * NN
    for x in range(NN):
        back[lin(cols, x)] = x
    assert sorted(back) == list(range(NN)), "singular G"
    return [back[1 << i] for i in range(H)]


def f2rank(vs):
    basis = {}
    for x in vs:
        while x:
            t = x.bit_length()
            if t not in basis:
                basis[t] = x
                break
            x ^= basis[t]
    return len(basis)


def extend(xs):
    out = list(xs)
    for i in range(H):
        if f2rank(out + [1 << i]) > len(out):
            out.append(1 << i)
    assert len(out) == H
    return out


def change(src, dst):
    a, b = extend(src), extend(dst)
    return [lin(b, x) for x in inverse_cols(a)]


def K_of(cols, phases=True):
    gi = inverse_cols(cols)
    git = [sum(((gi[j] >> i) & 1) << j for j in range(H)) for i in range(H)]
    M = [(1 << j) ^ lin(git, gi[j]) for j in range(H)]
    K = np.zeros((NN, NN), complex)
    for x in range(NN):
        y = lin(cols, x)
        q = sum(((M[i] >> i) & 1) * (y >> i & 1) for i in range(H))
        q += 2 * sum(((M[j] >> i) & 1) * (y >> i & 1) * (y >> j & 1)
                     for i in range(H) for j in range(i + 1, H))
        K[y, x] = 1j ** (q % 4) if phases else 1
    return K


def C_on(k):
    m = np.array([[1]], complex)
    for j in range(H):
        m = np.kron(C1 if j < k else np.eye(2), m)
    return m


def frame_op(U):
    Kc = K_of(change([1 << i for i in range(len(U))], U))
    return Kc @ C_on(len(U)) @ Kc.conj().T


def is_z4_monomial(Z):
    nz = np.abs(Z) > 1e-9
    if not (np.all(nz.sum(0) == 1) and np.all(nz.sum(1) == 1)):
        return False
    return bool(np.all(np.min(np.abs(Z[nz][:, None] - UNITS[None, :]), axis=1) < 1e-9))


def span(b):
    s = {0}
    for x in b:
        s |= {t ^ x for t in s}
    return frozenset(s)


def main():
    total = 0
    for lit, can in PAIRS:
        with gzip.open(MIXED / "inputs" / f"{lit}.json.gz") as fh:
            a = json.load(fh)
        with gzip.open(MIXED / "evidence" / f"{can}.json.gz") as fh:
            c = json.load(fh)
        A = {(w[0], tuple(w[2])): (span(w[3]), span(w[4])) for w in a["warps"]}
        Cn = {(w["B_pos"], tuple(w["G_columns"])):
              (span(c["frames"][w["from_frame"]]), span(c["frames"][w["to_frame"]]))
              for w in c["warps"]}
        assert A == Cn and len(a["warps"]) == len(c["warps"]) == 72, lit
        G = {w["op"]: w["G_columns"] for w in c["warps"]}
        T = {}
        ok = 0
        for sign, op, f0, f1 in c["warp_edges"]:
            for f in (f0, f1):
                if f not in T:
                    T[f] = frame_op(c["frames"][f])
            K = K_of(G[op])
            K = K if sign > 0 else K.conj().T
            ok += is_z4_monomial(T[f1] @ K @ T[f0].conj().T)
        assert ok == len(c["warp_edges"]), (can, ok)
        total += ok
        print(f"PASS {lit} ({can}): bound to the literal word; {ok} warp classes, "
              f"all Z4-monomial", flush=True)
        if lit == "FOUR-base":
            bad_perm = sum(not is_z4_monomial(T[f1] @ (K_of(G[op], False) if s > 0 else
                                                        K_of(G[op], False).T) @ T[f0].conj().T)
                           for s, op, f0, f1 in c["warp_edges"][:40])
            bad_swap = sum(not is_z4_monomial(T[f0] @ (K_of(G[op]) if s > 0 else
                                                       K_of(G[op]).conj().T) @ T[f1].conj().T)
                           for s, op, f0, f1 in c["warp_edges"] if f0 != f1)
            assert bad_perm == 40 and bad_swap > 0
            print(f"PASS controls: plain permutation P_G non-monomial on 40/40 classes; "
                  f"swapped frames non-monomial on {bad_swap} classes", flush=True)
    print(f"PASS_NATIVE_WARPS_Z4_MONOMIAL {total}")


if __name__ == "__main__":
    main()
