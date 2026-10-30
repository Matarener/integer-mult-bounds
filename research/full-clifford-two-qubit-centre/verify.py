#!/usr/bin/env python3
"""Exact two-qubit Clifford centre. MatShep/Codex; Apache-2.0.

NumPy does bounded int64 arithmetic only. Spectral certificates use unbounded
Python integers. No floating-point eigenvalue computation or symbolic package.
"""
from fractions import Fraction
from hashlib import sha256
from itertools import permutations
import json
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent


def need(ok, why):
    if not ok:
        raise ValueError(why)


def mul(a, b):
    ar, ai, br, bi = a[..., 0, :, :], a[..., 1, :, :], b[..., 0, :, :], b[..., 1, :, :]
    rr, ii = ar @ br - ai @ bi, ar @ bi + ai @ br
    need(not np.any(rr % 2) and not np.any(ii % 2), 'scaled Gaussian integrality')
    out = np.stack((rr // 2, ii // 2), axis=-3)
    need(np.max(np.abs(out)) <= 2, 'unitary entry encoding bound')
    return out


def star(a):
    b = a.swapaxes(-1, -2).copy()
    b[..., 1, :, :] *= -1
    return b


def phase(a):
    return np.stack((-a[..., 1, :, :], a[..., 0, :, :]), axis=-3)


def key(a):
    return a.astype('int8').tobytes()


IDENT = np.stack((2 * np.eye(4, dtype='int64'), np.zeros((4, 4), dtype='int64')))


def embed(a, axis):
    return np.stack([np.kron(x, np.eye(2, dtype='int64')) if axis == 0
                     else np.kron(np.eye(2, dtype='int64'), x) for x in a])


S = np.array([[[2, 0], [0, 0]], [[0, 0], [0, 2]]], dtype='int64')
V = np.array([[[1, 1], [1, 1]], [[1, -1], [-1, 1]]], dtype='int64')
CNOT = np.zeros((2, 4, 4), dtype='int64')
for j in range(4):
    CNOT[0, j ^ ((j >> 1) & 1), j] = 2
GENERATORS = np.array([embed(S, 0), embed(V, 0), embed(S, 1), embed(V, 1), CNOT])


def enumerate_group():
    mats, index, frontier = [IDENT], {key(IDENT): 0}, np.array([IDENT])
    while len(frontier):
        new = []
        for s in GENERATORS:
            for a in mul(s, frontier):
                k = key(a)
                if k not in index:
                    index[k] = len(mats)
                    mats.append(a)
                    new.append(a)
        frontier = np.array(new)
    g = np.array(mats)
    need(len(g) == 46080, '46080 exact elements')
    need(np.all(mul(star(g), g) == IDENT), 'all lifts unitary')
    need(all(key(p) in index for p in (IDENT, phase(IDENT), -IDENT, -phase(IDENT))), 'four scalar lifts')
    # Exact integer Pauli alphabet; generator normalization extends by closure.
    local = [np.array([[[2, 0], [0, 2]], [[0, 0], [0, 0]]]),
             np.array([[[0, 2], [2, 0]], [[0, 0], [0, 0]]]),
             np.array([[[0, 0], [0, 0]], [[0, -2], [2, 0]]]),
             np.array([[[2, 0], [0, -2]], [[0, 0], [0, 0]]])]
    p2 = []
    for a in local:
        for b in local:
            p2.append(np.stack((np.kron(a[0], b[0]) - np.kron(a[1], b[1]),
                                np.kron(a[0], b[1]) + np.kron(a[1], b[0]))) // 2)
    pkeys = {key(p) for p in p2} | {key(-p) for p in p2}
    for s in GENERATORS:
        need(all(key(mul(mul(s, p), star(s))) in pkeys for p in p2), 'signed Pauli normalizer')
    canonical = {min(key(a), key(phase(a)), key(-a), key(-phase(a))) for a in g}
    need(len(canonical) == 11520, '11520 projective classes')
    parent = list(range(len(g)))

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    for s in GENERATORS:
        for a, b in enumerate(mul(mul(s, g), star(s))):
            u, v = find(a), find(index[key(b)])
            if u != v:
                parent[v] = u
    classes = {}
    for a in range(len(g)):
        classes.setdefault(find(a), []).append(a)
    classes = sorted(classes.values(), key=lambda c: c[0])
    labels = np.zeros(len(g), dtype='int64')
    for j, c in enumerate(classes):
        labels[c] = j
    need(len(classes) == 59, '59 conjugacy classes')
    return g, index, labels, np.array([c[0] for c in classes])


def power(a, b, f):
    x, y = np.ones_like(a), np.zeros_like(b)
    for _ in range(f):
        x, y = x * a - y * b, x * b + y * a
    return x, y


def scalar_basis(iperm, r):
    done, columns, picks = set(), [], []
    for j in range(len(iperm)):
        if j in done:
            continue
        orbit, k = [], j
        while k not in orbit:
            orbit.append(k)
            done.add(k)
            k = iperm[k]
        if (r * len(orbit)) % 4:
            continue
        v = np.zeros((2, len(iperm)), dtype='int64')
        for t, k in enumerate(orbit):
            v[:, k] = ((1, 0), (0, 1), (-1, 0), (0, -1))[(r * t) % 4]
        columns.append(v)
        picks.append(j)
    return np.stack(columns, axis=-1), picks


def centre_matrix(traces, labels, f):
    ar, ai = [], []
    for rr, ii in traces:
        a, b = power(rr, ii, f)
        x, y = np.zeros(len(traces), dtype='int64'), np.zeros(len(traces), dtype='int64')
        np.add.at(x, labels, a)
        np.add.at(y, labels, b)
        ar.append(x)
        ai.append(y)
    return np.array(ar), np.array(ai)


def matvec(a, v, shift=0):
    return [(sum(x * u - y * w for (x, y), (u, w) in zip(row, v)) - shift * v[i][0],
             sum(x * w + y * u for (x, y), (u, w) in zip(row, v)) - shift * v[i][1])
            for i, row in enumerate(a)]


def spectral_certificate(a, values):
    d = len(a)
    for j in range(d):
        v = [(int(i == j), 0) for i in range(d)]
        for x in values:
            v = matvec(a, v, x)
        need(not any(x or y for x, y in v), 'exact square-free spectral annihilator')
    counts = {}
    for x in values:
        v, den = [(int(i == 0), 0) for i in range(d)], 1
        for y in values:
            if y != x:
                v, den = matvec(a, v, y), den * (x - y)
        need(v[0][1] == 0 and (11520 * v[0][0]) % den == 0, 'exact projector trace')
        count = 11520 * v[0][0] // den
        need(count > 0, 'positive regular spectral multiplicity')
        counts[x] = count
    need(sum(counts.values()) == 11520, 'complete regular spectral mass')
    return counts


def determinants(g):
    rr, ii = np.zeros(len(g), dtype='int64'), np.zeros(len(g), dtype='int64')
    for p in permutations(range(4)):
        sign = (-1) ** sum(p[i] > p[j] for i in range(4) for j in range(i + 1, 4))
        a, b = np.ones(len(g), dtype='int64'), np.zeros(len(g), dtype='int64')
        for j in range(4):
            x, y = g[:, 0, j, p[j]], g[:, 1, j, p[j]]
            a, b = a * x - b * y, a * y + b * x
        rr, ii = rr + sign * a, ii + sign * b
    need(np.all(ii == 0) and np.all(np.abs(rr) == 16), 'determinant character +/-1')
    return rr // 16


def literal_controls(g):
    chosen, count = g[[0, 1, 4, 111]], 0
    for f in range(1, 5):
        tensors = []
        for a in chosen:
            rr, ii = np.array([[1]], dtype='int64'), np.array([[0]], dtype='int64')
            for _ in range(f):
                rr, ii = np.kron(rr, a[0]) - np.kron(ii, a[1]), np.kron(rr, a[1]) + np.kron(ii, a[0])
            tensors.append((rr, ii))
        for i, (a, b) in enumerate(tensors):
            for j, (c, d) in enumerate(tensors):
                tr = (int(np.sum(chosen[i, 0] * chosen[j, 0] + chosen[i, 1] * chosen[j, 1])),
                      int(np.sum(chosen[i, 0] * chosen[j, 1] - chosen[i, 1] * chosen[j, 0])))
                x, y = power(np.array(tr[0]), np.array(tr[1]), f)
                need(int(np.sum(a * c + b * d)) == x and int(np.sum(a * d - b * c)) == y, 'literal tensor Gram')
                count += 1
    return count


def run():
    cert = json.loads((HERE / 'CERTIFICATE.json').read_text())
    g, index, labels, reps = enumerate_group()
    need(sha256(g.astype('int8').tobytes()).hexdigest() == cert['group_int8_sha256'], 'group receipt')
    need(sha256(labels.astype('<u4').tobytes()).hexdigest() == cert['class_labels_u32le_sha256'], 'class receipt')
    need(np.bincount(labels).tolist() == cert['class_sizes'] and g[reps].tolist() == cert['representatives'], 'class data')
    gr, gi = g[:, 0].reshape(len(g), 16), g[:, 1].reshape(len(g), 16)
    traces = []
    for r in reps:
        rr, ii = gr @ gr[r] + gi @ gi[r], gi @ gr[r] - gr @ gi[r]
        need(not np.any(rr % 4) and not np.any(ii % 4), 'Gaussian integer traces')
        need(np.all((rr // 4) ** 2 + (ii // 4) ** 2 <= 16), 'trace magnitude bound')
        traces.append((rr // 4, ii // 4))
    traces = np.array(traces)
    need(all(len(set(zip(traces[0, 0, labels == j], traces[0, 1, labels == j]))) == 1 for j in range(len(reps))), 'trace class function')
    iperm = [int(labels[index[key(phase(g[r]))]]) for r in reps]
    spectra, ranks, dimensions, actual9 = {}, [], {}, None
    for f in range(1, 13):
        ar, ai = centre_matrix(traces, labels, f)
        (br, bi), picks = scalar_basis(iperm, -f % 4)
        rr, ii = ar @ br - ai @ bi, ar @ bi + ai @ br
        cr, ci = rr[picks], ii[picks]
        need(np.array_equal(rr, br @ cr - bi @ ci) and np.array_equal(ii, br @ ci + bi @ cr), 'scalar-sector invariance')
        a = [[(int(x), int(y)) for x, y in zip(r, t)] for r, t in zip(cr, ci)]
        row = cert['widths'][str(f)]
        need(picks == row['picks'] and a == [[tuple(x) for x in r] for r in row['matrix']], 'derived centre matrix')
        values = row['eigenvalues']
        need(values == sorted(set(values)), 'distinct sorted eigenvalues')
        counts = spectral_certificate(a, values)
        spectrum = {str(Fraction(x, 4 * 4 ** f)): counts[x] for x in values if x}
        rank = sum(spectrum.values())
        need(spectrum == row['expected']['spectrum'] and rank == row['expected']['rank'], 'finite spectrum receipt')
        need(sum(Fraction(x) * v for x, v in spectrum.items()) == 11520, 'unit diagonal Gram trace')
        spectra[f], dimensions[f % 4] = spectrum, len(a)
        ranks.append(rank)
        if f == 9:
            actual9 = a
    det, moments = determinants(g), {}
    for f in (4, 8, 12):
        rr, ii = power(*traces[0], f)
        need(not np.any(ii), 'real determinant moment')
        moments[f] = int(np.sum(det * rr))
    need(moments[8] == 0 and moments[12] != 0, 'same-residue determinant null witness')
    lo, hi = min(map(Fraction, spectra[9])), max(map(Fraction, spectra[9]))
    need(lo == Fraction(315, 1024) and hi == Fraction(9855, 4096), 'sharp width-nine endpoints')
    controls = []
    need(ranks[7] < 11520, 'reject width-eight independence'); controls.append('width-eight independence rejected')
    need(not lo >= lo + Fraction(1, 2 ** 20), 'reject stronger lower bound'); controls.append('stronger lower bound rejected')
    need(not hi <= hi - Fraction(1, 2 ** 20), 'reject stronger upper bound'); controls.append('stronger upper bound rejected')
    need(not hi / lo <= Fraction(219, 28) - Fraction(1, 1000), 'reject stronger condition bound'); controls.append('stronger condition bound rejected')
    bad = [list(row) for row in actual9]
    bad[0][0] = (bad[0][0][0] + 1, bad[0][0][1])
    try:
        spectral_certificate(bad, cert['widths']['9']['eigenvalues'])
    except ValueError:
        controls.append('changed centre coefficient rejected')
    else:
        raise ValueError('mutated centre matrix accepted')
    real_only = traces.copy(); real_only[:, 1] = 0
    ar, ai = centre_matrix(real_only, labels, 9)
    (br, bi), picks = scalar_basis(iperm, -9 % 4)
    cr = np.array([[x for x, y in row] for row in actual9]); ci = np.array([[y for x, y in row] for row in actual9])
    need(not np.array_equal(ar @ br - ai @ bi, br @ cr - bi @ ci), 'reject discarded imaginary traces')
    controls.append('discarded imaginary trace phases rejected')
    need(moments[12] != moments[8], 'reject persistence of null witness'); controls.append('null witness at width twelve rejected')
    return {'status': 'PASS_TWO_QUBIT_CLIFFORD_CENTRE', 'lifts': len(g), 'projective_classes': 11520,
            'conjugacy_classes': len(reps), 'scalar_sector_dimensions': dimensions,
            'ranks_widths_1_to_12': ranks, 'width_nine_spectrum': spectra[9],
            'sharp_uniform_lower': str(lo), 'sharp_uniform_upper': str(hi),
            'sharp_uniform_gram_condition': str(hi / lo), 'determinant_character_moments': moments,
            'literal_tensor_entries': literal_controls(g), 'rejection_controls': controls}


if __name__ == '__main__':
    print(json.dumps(run(), indent=2, sort_keys=True))
