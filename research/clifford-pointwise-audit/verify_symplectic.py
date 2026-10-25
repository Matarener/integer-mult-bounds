#!/usr/bin/env python3
"""Independent finite evidence for PR5526 Sections 3--5; standard library only.

Prepared for DLamdata with substantial OpenAI Codex assistance, Apache-2.0.
No predecessor executable is imported. Enumerates every binary matrix on <=4
coordinates, rather than generating Clifford gates/tableaux or Choi states.
Finite evidence does not replace the all-dimension proof review.
"""

from collections import Counter, defaultdict
from fractions import Fraction
from itertools import product
import json


def require(condition, message):
    if not condition:
        raise ValueError(message)


def omega(x, y, n):
    mask = (1 << n) - 1
    return (((x & mask) & (y >> n)).bit_count()
            + ((x >> n) & (y & mask)).bit_count()) % 2


def apply(columns, v):
    out = 0
    for j, column in enumerate(columns):
        if (v >> j) & 1:
            out ^= column
    return out


def binary_rank(columns):
    pivots = {}
    for column in columns:
        while column:
            p = column.bit_length() - 1
            if p in pivots:
                column ^= pivots[p]
            else:
                pivots[p] = column
                break
    return len(pivots)


def symplectic(columns, n):
    return all(omega(columns[i], columns[j], n) == omega(1 << i, 1 << j, n)
               for i in range(2*n) for j in range(i + 1, 2*n))


def transvections(n):
    return {
        tuple((1 << j) ^ (a if omega(1 << j, a, n) else 0)
              for j in range(2*n))
        for a in range(1, 1 << (2*n))
    }


def gaussian_binomial(n, k):
    if k < 0 or k > n:
        return 0
    rows = [1] + [0] * k
    for dim in range(1, n + 1):
        rows = [1] + [rows[j] + (1 << (dim-j)) * rows[j-1]
                      if j <= dim else 0 for j in range(1, k+1)]
    return rows[k]


def state_overlap_bound(naxes, k):
    return gaussian_binomial(naxes, k) * (1 << (k*(k+3)//2))


def census(n):
    m, q = 2*n, 1 << (2*n)
    hist = Counter()
    lifted = Counter()
    rank_one = set()
    residual_keys = set()
    per_subspace = Counter()
    character_sums = 0
    residual_pairs = 0
    candidates = 0
    for columns in product(range(q), repeat=m):
        candidates += 1
        if not symplectic(columns, n):
            continue
        images = tuple(apply(columns, v) for v in range(q))
        require(len(set(images)) == q, 'noninvertible-preserver')
        displacement = tuple(columns[j] ^ (1 << j) for j in range(m))
        k = binary_rank(displacement)
        fixed = tuple(v for v in range(q) if images[v] == v)
        require(len(fixed) == 1 << (m-k), 'fixed-rank-disagreement')
        image = tuple(sorted({images[v] ^ v for v in range(q)}))
        require(len(image) == 1 << k, 'image-rank-disagreement')
        hist[k] += 1
        if k == 1:
            rank_one.add(columns)

        # Restrict every Pauli commutation character to the actual fixed space.
        # An arbitrary base sign character translates this multiset, so the
        # count is independent of which Clifford lift is chosen first.
        sums = [sum(1 if omega(p, v, n) == 0 else -1 for v in fixed)
                for p in range(q)]
        character_sums += q
        require(set(sums) <= {0, len(fixed)}, 'character-not-orthogonal')
        positive = sum(s != 0 for s in sums)
        require(positive == 1 << k, 'wrong-nonzero-lift-count')
        lifted[k] += positive

        # Compute B from actual preimages; no formula enumeration is used.
        preimages = defaultdict(list)
        for x in range(q):
            preimages[images[x] ^ x].append(x)
        table = []
        for u in image:
            row = []
            for w in image:
                values = {omega(x, w, n) for x in preimages[u]}
                require(len(values) == 1, 'residual-not-well-defined')
                row.append(values.pop())
            table.append(tuple(row))
        require(all(u == 0 or any(table[i]) for i, u in enumerate(image)),
                'residual-left-degenerate')
        for i, u in enumerate(image):
            for j, v in enumerate(image):
                require(table[i][j] ^ table[j][i] == omega(u, v, n),
                        'wrong-residual-symmetrization')
                residual_pairs += 1
        key = (image, tuple(table))
        require(key not in residual_keys, 'residual-not-injective')
        residual_keys.add(key)
        per_subspace[image] += 1

    require(candidates == 1 << (m*m), 'incomplete-matrix-domain')
    require(rank_one == transvections(n), 'rank-one-transvection-mismatch')
    for image, count in per_subspace.items():
        k = len(image).bit_length() - 1
        require(count <= 1 << (k*(k+1)//2), 'too-many-residual-forms')
    require(lifted[0] == 1, 'identity-overlap-count')
    require(lifted[1] == 2*(q-1), 'first-overlap-count')
    for k in range(m+1):
        require(lifted[k] <= state_overlap_bound(m, k), 'general-overlap-bound')
    require(sum(hist.values()) == (6 if n == 1 else 720), 'group-size-fixture')
    return {
        'axes': n, 'binary_matrices_tested': candidates,
        'symplectic_matrices': sum(hist.values()),
        'displacement_rank_histogram': dict(sorted(hist.items())),
        'nonzero_trace_lift_histogram': dict(sorted(lifted.items())),
        'character_sums': character_sums,
        'residual_symmetrization_pairs': residual_pairs,
        'distinct_residual_forms': len(residual_keys),
    }


def dk(k):
    out = 1
    for j in range(1, k+1):
        out *= (1 << j) - 1
    return out


def bound_and_phases():
    # Independent rational series: retain four terms and dominate k>=5 by
    # the geometric ratio first encountered after k=5 (1/63, scaled by 2^-s).
    def clifford_tail(s):
        initial = Fraction(1, 1 << (s+1))
        finite = sum((Fraction(1, (1 << (s*k))*dk(k)) for k in range(2, 5)),
                     Fraction())
        tail = Fraction(1, (1 << (5*s))*dk(5)) / (1-Fraction(1, (1 << s)*63))
        return initial + finite + tail

    c0, c2, c6 = (clifford_tail(s) for s in (0, 2, 6))
    require(c0 < Fraction(8, 9), 'clifford-uniform-tail')
    require(c2 < Fraction(3, 20), 'clifford-later-tail-s2')
    require(c6 < Fraction(1, 126), 'clifford-later-tail-s6')
    st = sum((Fraction(1, (1 << k)*dk(k)) for k in range(1, 5)), Fraction())
    st += Fraction(1, (1 << 5)*dk(5)) / (1-Fraction(1, 126))
    require(st < Fraction(3, 5), 'stabilizer-uniform-tail')

    # Independent finite rational check of the subspace-count domination,
    # including all actual k, for an explicit bounded 1<=N<=32 domain.
    finite_terms = 0
    for axes in range(1, 33):
        for k in range(1, axes+1):
            term = Fraction(state_overlap_bound(axes, k), 1 << (k*(axes+2)))
            require(term <= Fraction(1, dk(k)), 'finite-subspace-term')
            finite_terms += 1

    # Gaussian integers represented as pairs; no floating complex arithmetic.
    roots = ((1, 0), (0, 1), (-1, 0), (0, -1))
    def add(xs):
        return (sum(x[0] for x in xs), sum(x[1] for x in xs))
    # Fourier orthogonality simultaneously checks inversion and each missing
    # residue witness. The four exact operators i^j I are kept separate.
    fourier = []
    for r in range(4):
        row = [add([roots[((f-r)*j) % 4] for j in range(4)]) for f in range(4)]
        require(row == [(4, 0) if f == r else (0, 0) for f in range(4)],
                'phase-fourier-orthogonality')
        fourier.append(row)
    return {
        'clifford_row_sum_majorants': {'s0': str(c0), 's2': str(c2), 's6': str(c6)},
        'stabilizer_row_sum_majorant': str(st),
        'finite_subspace_terms': finite_terms,
        'four_residue_witness_values': fourier,
    }


def controls():
    # Direct domain controls: reject invertible matrices that fail the actual
    # alternating form, and reject singular matrices even if a few pairs agree.
    identity = (1, 2, 4, 8)
    require(symplectic(identity, 2), 'identity-positive-control')
    bad = (1, 3, 4, 8)
    require(binary_rank(bad) == 4 and not symplectic(bad, 2),
            'invertible-is-not-symplectic-control')
    require(not symplectic((1, 2, 4, 4), 2), 'singular-control')
    require(omega(1, 4, 2) == 1 and omega(1, 2, 2) == 0,
            'pairing-coordinate-control')
    # Explicit failure of phase deletion: [I]-[iI] is zero at f=4 and nonzero
    # at f=1; three residue tests miss their complementary Fourier witness.
    roots = ((1, 0), (0, 1), (-1, 0), (0, -1))
    def identity_minus_phase(f):
        phase = roots[f % 4]
        return (1-phase[0], -phase[1])
    require(identity_minus_phase(4) == (0, 0)
            and identity_minus_phase(1) != (0, 0), 'phase-deletion-control')
    # Dropping the half factor in the first overlap estimate destroys the
    # claimed 8/9 universal row budget even before the remaining positive tail.
    require(Fraction(1) + Fraction(1, 3) > Fraction(8, 9),
            'first-overlap-half-is-essential')
    return ['identity-positive', 'invertible-nonsymplectic', 'singular',
            'pairing-coordinates', 'phase-deletion', 'first-overlap-half']


def main():
    result = {'scope': 'PR5526 Sections 3--5 independent direct binary-matrix audit',
              'censuses': [census(1), census(2)],
              'bounds_and_phases': bound_and_phases(), 'controls': controls()}
    print(json.dumps(result, indent=2, sort_keys=True))
    print('PASS_INDEPENDENT_SYMPLECTIC_OVERLAP_AUDIT')


if __name__ == '__main__':
    main()
