#!/usr/bin/env python3
"""Exact nonmaximal Schur-commutator rank profiles for d=2 over F2.

Nick Petalas. Apache-2.0. Standard library only.

For every A,B in GL_2(F2) and H in M_2(F2) this script
1. enumerates every sector choice I_j >= im T_j, N_j <= ker T_j and records
   the least ambient dimension for each Schur-commutator rank;
2. checks the closed law n_min(rho)=max(n0+rho-rho0, nmax-2(2d-rho)) on the
   feasible interval [rho0, 2d], and the rank identities rank R=2d-a,
   rank L=2d-b on every enumerated choice;
3. builds a literal commuting idempotent pair for every (triple, rank) at the
   claimed least dimension and recomputes its Schur commutator from scratch.
Seeded controls must be rejected. Exit status 0 means every check passed.
"""
from __future__ import annotations

import hashlib
import itertools
import json
import sys

D = 2
SECTORS = ("10", "01", "11")


# ---- dense F2 matrices as lists of 0/1 rows -------------------------------

def mul(x, y):
    cols = len(y[0])
    return [[sum(x[i][k] & y[k][j] for k in range(len(y))) & 1
             for j in range(cols)] for i in range(len(x))]


def add(x, y):
    return [[(a ^ b) for a, b in zip(r, s)] for r, s in zip(x, y)]


def eye(n):
    return [[int(i == j) for j in range(n)] for i in range(n)]


def zeros(r, c):
    return [[0] * c for _ in range(r)]


def rows_to_masks(x):
    return [sum(bit << j for j, bit in enumerate(row)) for row in x]


def mask_rank(masks):
    basis = []
    for v in masks:
        for b in basis:
            v = min(v, v ^ b)
        if v:
            basis.append(v)
    return len(basis)


def rank(x):
    return mask_rank(rows_to_masks(x)) if x and x[0] else 0


def transpose(x):
    return [list(c) for c in zip(*x)]


def inverse(x):
    n = len(x)
    a = [row[:] + e for row, e in zip(x, eye(n))]
    for c in range(n):
        piv = next((r for r in range(c, n) if a[r][c]), None)
        if piv is None:
            raise ValueError("singular")
        a[c], a[piv] = a[piv], a[c]
        for r in range(n):
            if r != c and a[r][c]:
                a[r] = [u ^ v for u, v in zip(a[r], a[c])]
    return [row[n:] for row in a]


def block(rows):
    out = []
    for brow in rows:
        for i in range(len(brow[0])):
            out.append(sum((b[i] for b in brow), []))
    return out


def sub_block(x, r0, r1, c0, c1):
    return [row[c0:c1] for row in x[r0:r1]]


# ---- subspaces of F2^2 as frozensets of vector tuples -----------------------

VECS = [tuple(v) for v in itertools.product((0, 1), repeat=D)]


def span(vs):
    out = {tuple([0] * D)}
    for v in vs:
        out |= {tuple(a ^ b for a, b in zip(s, v)) for s in out}
    return frozenset(out)


SUBSPACES = sorted({span(c) for k in range(D + 1)
                    for c in itertools.combinations(VECS, k)},
                   key=lambda s: (len(s), sorted(s)))


def dim(s):
    return len(s).bit_length() - 1


def basis(s, start=()):
    """Basis of s extending the independent list start (vectors in s)."""
    out = list(start)
    for v in sorted(s):
        if span(out) != span(out + [v]):
            out.append(v)
    return out[len(start):]


def image(t):
    return span([tuple(c) for c in transpose(t)])


def kernel(t):
    return frozenset(v for v in VECS
                     if all(sum(a & b for a, b in zip(row, v)) & 1 == 0 for row in t))


# ---- the reduction ----------------------------------------------------------

def compressed(a, b, h):
    i2 = eye(D)
    return {"00": add(add(add(i2, a), b), h), "10": add(a, h),
            "01": add(b, h), "11": h}


def factor_maps(a, b, h):
    """G: U^2 -> U^3 and G': U^3 -> U^2 with L=Y G and R=G' X (PROOF.md)."""
    ai, bi = inverse(a), inverse(b)
    z = zeros(D, D)
    bih, hbi = mul(bi, h), mul(h, bi)
    g = block([[z, ai], [bih, bi], [add(eye(D), bih), add(ai, bi)]])
    gp = block([[ai, bi, add(ai, bi)], [z, hbi, add(hbi, eye(D))]])
    return g, gp


def embed(j, v):
    out = [0] * (3 * D)
    out[D * j:D * j + D] = v
    return out


def profile(a, b, h, check_identities=True):
    t = compressed(a, b, h)
    g, gp = factor_maps(a, b, h)
    m = mul(g, gp)
    im = {s: image(t[s]) for s in SECTORS}
    ker = {s: kernel(t[s]) for s in SECTORS}
    ich = [[s for s in SUBSPACES if im[j] <= s] for j in SECTORS]
    nch = [[s for s in SUBSPACES if s <= ker[j]] for j in SECTORS]
    gt = transpose(g)
    best = {}
    witness = {}
    for ichoice in itertools.product(*ich):
        cols = [embed(k, list(v)) for k, s in enumerate(ichoice) for v in basis(s)]
        mi = rows_to_masks([[sum(row[q] & c[q] for q in range(3 * D)) & 1
                             for row in m] for c in cols])
        a_def = sum(D - dim(s) for s in ichoice)
        rank_r = mask_rank(rows_to_masks([[sum(row[q] & c[q] for q in range(3 * D)) & 1
                                           for row in gp] for c in cols]))
        for nchoice in itertools.product(*nch):
            nb = rows_to_masks([embed(k, list(v)) for k, s in enumerate(nchoice)
                                for v in basis(s)])
            f = mask_rank(mi + nb) - len(nb)
            b_def = len(nb)
            if check_identities:
                # rank L = 2d - b: rank of U^2 -> U^3/N, i.e. rank[G | N] - dim N.
                rank_l = mask_rank(rows_to_masks(gt) + nb) - len(nb)
                if rank_r != 2 * D - a_def or rank_l != 2 * D - b_def:
                    raise AssertionError("rank R/L identity fails")
                if not (2 * D - a_def - b_def <= f <= 2 * D - max(a_def, b_def)):
                    raise AssertionError("Sylvester sandwich fails")
            cost = sum(dim(s) for s in ichoice) - b_def
            if cost < best.get(f, 10 ** 9):
                best[f] = cost
                witness[f] = (ichoice, nchoice)
    base = rank(t["00"]) + sum(D - rank(t[j]) for j in SECTORS)
    nmin = {f: base + c for f, c in best.items()}
    tt = block([[t[s] if s == r else zeros(D, D) for s in SECTORS] for r in SECTORS])
    rho0 = rank(mul(mul(tt, m), tt))
    return t, nmin, witness, rho0


def law(t, rho0):
    n0 = rank(t["00"]) + sum(rank(t[j]) for j in SECTORS)
    nmax = 3 * D + rank(t["00"]) + sum(D - rank(t[j]) for j in SECTORS)
    return {r: max(n0 + r - rho0, nmax - 2 * (2 * D - r))
            for r in range(rho0, 2 * D + 1)}, n0, nmax


# ---- literal witness ---------------------------------------------------------

def sector_factors(tj, ij, nj):
    """X (d x r), Y (r x d) with XY=tj, im X=ij, ker Y=nj, r minimal."""
    imt = image(tj)
    sigma = basis(imt)
    phi_cols = []
    for col in transpose(tj):  # coordinates of each column in basis sigma
        for coeffs in itertools.product((0, 1), repeat=len(sigma)):
            vec = tuple(sum(c & s[q] for c, s in zip(coeffs, sigma)) & 1 for q in range(D))
            if vec == tuple(col):
                phi_cols.append(list(coeffs))
                break
    phi = transpose(phi_cols) if sigma else []
    nbas = basis(nj)
    kbas = basis(kernel(tj), nbas)
    wbas = basis(frozenset(VECS), nbas + kbas)
    full = nbas + kbas + wbas  # basis of U; psi reads the kbas coordinates
    coords = inverse(transpose([list(v) for v in full]))
    psi = [coords[len(nbas) + q] for q in range(len(kbas))]
    tau = basis(ij, sigma)
    y = [row[:] for row in phi] + psi + [[0] * D for _ in tau]
    x_cols = [list(s) for s in sigma] + [[0] * D for _ in psi] + [list(v) for v in tau]
    x = transpose(x_cols) if x_cols else [[] for _ in range(D)]
    return x, y


def build_pair(a, b, h, ichoice, nchoice):
    t = compressed(a, b, h)
    sel = {"00": (image(t["00"]), kernel(t["00"]))}
    for k, j in enumerate(SECTORS):
        sel[j] = (ichoice[k], nchoice[k])
    xs, ys, p0d, q0d = [], [], [], []
    for j in ("00",) + SECTORS:
        x, y = sector_factors(t[j], *sel[j])
        xs.append(x)
        ys += y
        p0d += [int(j[0] == "1")] * len(y)
        q0d += [int(j[1] == "1")] * len(y)
    n = len(ys)
    pi = [sum((x[r] for x in xs), []) for r in range(D)]
    inc = ys
    if mul(pi, inc) != eye(D):
        raise AssertionError("pi i != I")
    # basis of ker pi
    kerpi = []
    for v in itertools.product((0, 1), repeat=n):
        if len(kerpi) == n - D:
            break
        if any(sum(pi[r][q] & v[q] for q in range(n)) & 1 for r in range(D)):
            continue
        if mask_rank(rows_to_masks(kerpi + [list(v)])) == len(kerpi) + 1:
            kerpi.append(list(v))
    mm = transpose(transpose(inc) + kerpi)
    mi = inverse(mm)
    p0 = [[int(i == j) * p0d[i] for j in range(n)] for i in range(n)]
    q0 = [[int(i == j) * q0d[i] for j in range(n)] for i in range(n)]
    return mul(mul(mi, p0), mm), mul(mul(mi, q0), mm)


def literal_rank(a, b, h, p, q):
    n = len(p)
    if mul(p, p) != p or mul(q, q) != q or mul(p, q) != mul(q, p):
        raise AssertionError("not commuting idempotents")
    if sub_block(p, 0, D, 0, D) != a or sub_block(q, 0, D, 0, D) != b \
            or sub_block(mul(p, q), 0, D, 0, D) != h:
        raise AssertionError("prescribed blocks fail")
    if n == D:
        return 0
    ai, bi = inverse(a), inverse(b)
    s = add(sub_block(p, D, n, D, n),
            mul(mul(sub_block(p, D, n, 0, D), ai), sub_block(p, 0, D, D, n)))
    z = add(sub_block(q, D, n, D, n),
            mul(mul(sub_block(q, D, n, 0, D), bi), sub_block(q, 0, D, D, n)))
    return rank(add(mul(s, z), mul(z, s)))


# ---- driver -------------------------------------------------------------------

def triples():
    mats = [[[w, x], [y, z]] for w, x, y, z in itertools.product((0, 1), repeat=4)]
    gl = [m for m in mats if (m[0][0] & m[1][1]) ^ (m[0][1] & m[1][0])]
    return [(a, b, h) for a in gl for b in gl for h in mats]


def run():
    rows = []
    witnesses = 0
    for a, b, h in triples():
        t, nmin, wit, rho0 = profile(a, b, h)
        predicted, n0, nmax = law(t, rho0)
        if nmin != predicted:
            raise AssertionError(f"law fails at {a},{b},{h}: {nmin} vs {predicted}")
        for r, (ich, nch) in wit.items():
            p, q = build_pair(a, b, h, ich, nch)
            if len(p) != nmin[r] or literal_rank(a, b, h, p, q) != r:
                raise AssertionError("literal witness fails")
            witnesses += 1
        rows.append({"A": a, "B": b, "H": h, "noncommuting": mul(a, b) != mul(b, a),
                     "n0": n0, "rho0": rho0, "nmax": nmax,
                     "n_min": [nmin[r] for r in range(rho0, 2 * D + 1)]})
    return rows, witnesses


def controls():
    """Each seeded mutation must be rejected by the same checks."""
    a, b, h = eye(D), eye(D), eye(D)  # A=B=H=I: slope-two profile 2,4,6,8,10
    t, nmin, wit, rho0 = profile(a, b, h)
    predicted, _, _ = law(t, rho0)
    rejected = 0
    # 1. slope-one-only law (drop the 2(2d-rho) branch)
    n0 = rank(t["00"]) + sum(rank(t[j]) for j in SECTORS)
    rejected += {r: n0 + r - rho0 for r in predicted} != nmin
    # 2. #5128 formula alone for every rank
    rejected += any(nmin[r] != predicted[2 * D] for r in nmin) is True
    # 3. corrupted witness: flip one entry of P
    ich, nch = wit[2]
    p, q = build_pair(a, b, h, ich, nch)
    p[-1][-1] ^= 1
    try:
        literal_rank(a, b, h, p, q)
    except AssertionError:
        rejected += 1
    # 4. wrong prescribed H
    p, q = build_pair(a, b, h, ich, nch)
    try:
        literal_rank(a, b, zeros(D, D), p, q)
    except AssertionError:
        rejected += 1
    return rejected


def main():
    rows, witnesses = run()
    rejected = controls()
    profiles = {}
    for r in rows:
        key = (r["rho0"], tuple(r["n_min"]))
        profiles[key] = profiles.get(key, 0) + 1
    summary = {
        "triples": len(rows),
        "noncommuting_triples": sum(r["noncommuting"] for r in rows),
        "literal_witnesses": witnesses,
        "distinct_profiles": len(profiles),
        "rho0_counts": {str(k): sum(1 for r in rows if r["rho0"] == k) for k in range(5)},
        "controls_rejected": rejected,
        "rows_sha256": hashlib.sha256(json.dumps(rows, sort_keys=True).encode()).hexdigest(),
    }
    expected = {"triples": 576, "noncommuting_triples": 288, "controls_rejected": 4}
    ok = all(summary[k] == v for k, v in expected.items())
    print(json.dumps(summary, indent=1, sort_keys=True))
    if not ok:
        print("FAIL", file=sys.stderr)
        return 1
    print("PASS_SCHUR_INTERMEDIATE_RANKS_D2_F2")
    return 0


if __name__ == "__main__":
    sys.exit(main())
