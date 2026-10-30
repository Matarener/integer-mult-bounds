#!/usr/bin/env python3
"""Exact checks for the four-term address-twist classification.

V = M_m(F2) is stored as an m*m-bit integer (entry (r, c) at bit r*m+c).
A two-sided transport z -> L z R is stored as the tuple of images of the
basis matrices. Sym^2(V) is the degree-two part of F2[t_0, ..., t_(N-1)],
squares retained, as in PR5490 equation (1).

Nick Petalas. Apache-2.0. Standard library only; no predecessor code imported.
"""
from itertools import product
from pathlib import Path
import hashlib
import json
import random

PASS = 'PASS_FOUR_TERM_TWIST_ESCAPE'


def need(ok, why):
    if not ok:
        raise SystemExit('FAIL: ' + why)


# --- matrices over F2 -----------------------------------------------------

def mat_mul(a, b, m):
    out = 0
    for r in range(m):
        for c in range(m):
            v = 0
            for k in range(m):
                v ^= (a >> (r*m+k)) & (b >> (k*m+c)) & 1
            out |= v << (r*m+c)
    return out


def mat_rank(a, m):
    rows = [(a >> (r*m)) & ((1 << m)-1) for r in range(m)]
    return vec_rank(rows)


def vec_rank(vectors):
    pivots = {}
    for x in vectors:
        while x:
            k = x.bit_length()-1
            if k not in pivots:
                pivots[k] = x
                break
            x ^= pivots[k]
    return len(pivots)


def identity(m):
    return sum(1 << (r*m+r) for r in range(m))


def general_linear(m):
    return [a for a in range(1 << (m*m)) if mat_rank(a, m) == m]


def mat_inv(a, m):
    one = identity(m)
    power = a
    while True:  # finite group: some power of a is the identity
        nxt = mat_mul(power, a, m)
        if nxt == one:
            return power
        power = nxt


# --- transports on V ------------------------------------------------------

def transport(left, right, m):
    return tuple(mat_mul(mat_mul(left, 1 << k, m), right, m)
                 for k in range(m*m))


def apply(u, x):
    y = 0
    k = 0
    while x:
        if x & 1:
            y ^= u[k]
        x >>= 1
        k += 1
    return y


def map_sum(maps):
    return tuple(_xor_all(column) for column in zip(*maps))


def _xor_all(values):
    y = 0
    for v in values:
        y ^= v
    return y


def map_rank(u):
    return vec_rank(list(u))


# --- Sym^2 condition, written two independent ways --------------------------

def sym2_product(a, w, n):
    """Coefficients of the product of linear forms a and w in Sym^2(V)."""
    coeff = {}
    for p in range(n):
        if not (a >> p) & 1:
            continue
        for q in range(n):
            if (w >> q) & 1:
                key = (min(p, q), max(p, q))
                coeff[key] = coeff.get(key, 0) ^ 1
    return {k for k, v in coeff.items() if v}


def degree_one_residue(frames, maps, n):
    """Return (sum a_i, [sum_i a_i*(U_i e_t) for every basis e_t])."""
    constant = _xor_all(frames)
    residues = []
    for t in range(n):
        total = set()
        for a, u in zip(frames, maps):
            total ^= sym2_product(a, u[t], n)
        residues.append(total)
    return constant, residues


def survives(frames, maps, n):
    constant, residues = degree_one_residue(frames, maps, n)
    return constant == 0 and all(not r for r in residues)


def kernel_basis(equations, nvars):
    pivots = {}
    for e in equations:
        for k, v in pivots.items():
            if (e >> k) & 1:
                e ^= v
        if e:
            k = e.bit_length()-1
            for kk in list(pivots):
                if (pivots[kk] >> k) & 1:
                    pivots[kk] ^= e
            pivots[k] = e
    basis = []
    for f in range(nvars):
        if f in pivots:
            continue
        x = 1 << f
        for k, v in pivots.items():
            if (v >> f) & 1:
                x |= 1 << k
        basis.append(x)
    return basis


def solution_space(maps, n):
    """Basis of all (a_1..a_k) with sum a_i = 0 and the degree-two identity.

    Variables are a_1..a_(k-1); a_k is their sum. The identity says that
    the matrix sum_i a_i (U_i e_t)^T is alternating (symmetric, zero diagonal).
    """
    k = len(maps)
    last = maps[-1]
    equations = []
    for t in range(n):
        for p in range(n):
            for q in range(p, n):
                e = 0
                cells = [(p, q)] if p == q else [(p, q), (q, p)]
                for j in range(k-1):
                    for row, col in cells:
                        if ((maps[j][t] ^ last[t]) >> col) & 1:
                            e ^= 1 << (j*n+row)
                equations.append(e)
    basis = []
    mask = (1 << n)-1
    for x in kernel_basis(equations, (k-1)*n):
        frames = [(x >> (j*n)) & mask for j in range(k-1)]
        frames.append(_xor_all(frames))
        basis.append(frames)
    return basis


def residue_beta(frames, inverse_maps):
    return _xor_all(apply(v, a) for v, a in zip(inverse_maps, frames))


# --- checks ---------------------------------------------------------------

def all_transports(m):
    gl = general_linear(m)
    pairs = {}
    for left, right in product(gl, repeat=2):
        pairs.setdefault(transport(left, right, m), (left, right))
    return pairs


def check_m2_exhaustive():
    m, n = 2, 4
    pairs = all_transports(m)
    maps = sorted(pairs)
    need(len(maps) == 36, 'GL2(F2) two-sided transports')
    ident = tuple(1 << k for k in range(n))
    for u, v in product(maps, repeat=2):
        if u != v:
            need(map_rank(map_sum([u, v])) >= m, 'rank distance m=2')
    inverse = {u: transport(mat_inv(l, m), mat_inv(r, m), m)
               for u, (l, r) in pairs.items()}
    need(all(apply(inverse[u], apply(u, x)) == x
             for u in maps for x in range(1 << n)), 'inverse transports')
    dims = {}
    tuples = 0
    for triple in product(maps, repeat=3):
        quad = list(triple)+[ident]
        inv = [inverse[u] for u in quad]
        basis = solution_space(quad, n)
        dims[len(basis)] = dims.get(len(basis), 0)+1
        for frames in basis:
            need(survives(frames, quad, n), 'kernel solves (1)')
            need(residue_beta(frames, inv) == 0, 'm=2 four-term residue')
        tuples += 1
    need(tuples == 36**3, 'm=2 tuple count')
    return tuples, dict(sorted(dims.items()))


def check_m2_normalization_spot():
    """Spot-check U_4 = id normalization: beta transforms by U_4."""
    m, n = 2, 4
    pairs = all_transports(m)
    maps = sorted(pairs)
    inverse = {u: transport(mat_inv(l, m), mat_inv(r, m), m)
               for u, (l, r) in pairs.items()}
    rng = random.Random(5490)
    for _ in range(200):
        quad = [rng.choice(maps) for _ in range(4)]
        for frames in solution_space(quad, n):
            need(residue_beta(frames, [inverse[u] for u in quad]) == 0,
                 'm=2 unnormalized four-term residue')


def field_multiplication(m, poly):
    """Matrices of multiplication by every element of F2[x]/(poly)."""
    def mulmod(a, b):
        r = 0
        while b:
            if b & 1:
                r ^= a
            b >>= 1
            a <<= 1
            if (a >> m) & 1:
                a ^= poly
        return r
    mats = {}
    for c in range(1 << m):
        cols = [mulmod(c, 1 << j) for j in range(m)]
        mats[c] = sum(((cols[j] >> i) & 1) << (i*m+j)
                      for i in range(m) for j in range(m))
    return mats, mulmod


IRREDUCIBLE = {3: 0b1011, 4: 0b10011, 5: 0b100101, 6: 0b1000011}


def field_inverse(c, m, mulmod):
    for d in range(1, 1 << m):
        if mulmod(c, d) == 1:
            return d
    raise SystemExit('FAIL: zero has no inverse')


def check_witness(m):
    n = m*m
    mats, mulmod = field_multiplication(m, IRREDUCIBLE[m])
    need(all(mat_rank(mats[c], m) == m for c in range(1, 1 << m)),
         'irreducible modulus for m=%d' % m)
    a, b = 1, 0b10  # b = x is outside F4 for m >= 3
    need(mulmod(b, b) ^ b ^ 1 != 0, 'b^2+b+1 nonzero')
    q, q2 = 1, 0b10
    p = q ^ q2
    lefts = [a, b, a ^ b, a ^ b]
    rights = [p, p, q, q2]
    need(all(v != 0 for v in lefts+rights), 'nonzero field elements')
    maps = [transport(mats[l], mats[r], m) for l, r in zip(lefts, rights)]
    need(len(set(maps)) == 4, 'four distinct transports')
    for i in range(4):
        for j in range(i+1, 4):
            need(map_rank(map_sum([maps[i], maps[j]])) >= m,
                 'witness rank distance')
    need(all(c == 0 for c in map_sum(maps)), 'transport relation sum U_i = 0')
    x = 1  # E_00, rank one
    frames = [x]*4
    need(survives(frames, maps, n), 'witness satisfies (1) for m=%d' % m)
    inverse = [transport(mats[field_inverse(l, m, mulmod)],
                         mats[field_inverse(r, m, mulmod)], m)
               for l, r in zip(lefts, rights)]
    for u, v in zip(maps, inverse):
        need(all(apply(v, apply(u, 1 << k)) == 1 << k for k in range(n)),
             'witness inverse')
    beta = residue_beta(frames, inverse)
    need(mat_rank(beta, m) == 2, 'witness residue rank 2 for m=%d' % m)
    # A perturbed control: changing one frame breaks the identity.
    need(not survives([x, x, x, x ^ (1 << 1)], maps, n), 'negative control')
    return beta


def check_m3_random_triples(samples):
    """Random m=3 tuples: generic transports admit only beta = 0."""
    m, n = 3, 9
    gl = general_linear(m)
    need(len(gl) == 168, '|GL3(F2)|')
    rng = random.Random(1022)
    ident = tuple(1 << k for k in range(n))
    nonzero = 0
    for _ in range(samples):
        pairs = [(rng.choice(gl), rng.choice(gl)) for _ in range(3)]
        quad = [transport(l, r, m) for l, r in pairs]+[ident]
        inv = [transport(mat_inv(l, m), mat_inv(r, m), m) for l, r in pairs]
        inv.append(ident)
        rel = all(c == 0 for c in map_sum(quad))
        for frames in solution_space(quad, n):
            if residue_beta(frames, inv):
                need(rel and len(set(frames)) == 1, 'escape outside the form')
                nonzero += 1
    return nonzero


def check_three_term_control():
    """Positive control: three terms at m=2 are rigid (PR5490 lemma)."""
    m, n = 2, 4
    pairs = all_transports(m)
    maps = sorted(pairs)
    inverse = {u: transport(mat_inv(l, m), mat_inv(r, m), m)
               for u, (l, r) in pairs.items()}
    ident = tuple(1 << k for k in range(n))
    for u, v in product(maps, repeat=2):
        triple = [u, v, ident]
        for frames in solution_space(triple, n):
            need(residue_beta(frames, [inverse[w] for w in triple]) == 0,
                 'three-term control')


def check_pinned_sources():
    package = Path(__file__).resolve().parent
    root = package.parents[1]
    rows = json.loads((package / 'SOURCES.json').read_text())['files']
    live = [r for r in rows if r['usage'] == 'input']
    need(live, 'live input pins')
    for row in live:
        data = (root / row['path']).read_bytes()
        need(hashlib.sha256(data).hexdigest() == row['sha256'],
             'pinned bytes for ' + row['path'])
    proof = (root / live[0]['path']).read_text()
    need('## 2. Three-term quadratic rigidity' in proof,
         'PR5490 three-term lemma present')


def main():
    check_pinned_sources()
    tuples, dims = check_m2_exhaustive()
    check_m2_normalization_spot()
    check_three_term_control()
    witnesses = {m: check_witness(m) for m in (3, 4, 5, 6)}
    escapes = check_m3_random_triples(300)
    need(escapes == 0, 'random m=3 triples should not hit a relation')
    print('m=2 exhaustive four-term tuples (U_4 = id):', tuples)
    print('m=2 solution-space dimension histogram:', dims)
    print('rank-2 witnesses, residue bitmasks:',
          {m: hex(b) for m, b in witnesses.items()})
    print(PASS)


if __name__ == '__main__':
    main()
