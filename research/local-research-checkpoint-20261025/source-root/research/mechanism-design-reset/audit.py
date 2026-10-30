"""Design admission checks, not a new framed supplier.

Douglas Colkitt, with OpenAI Codex assistance. Apache-2.0.
"""
from fractions import Fraction as Q
from itertools import combinations
from pathlib import Path
import argparse
import importlib.util
import json

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('design_budget', HERE.parent/'shared-core-blocks/audit.py')
H = importlib.util.module_from_spec(spec)
spec.loader.exec_module(H)
require, encode = H.require, H.encode


class Field:
    def __init__(self, binary):
        self.binary = binary

    def q(self, x):
        return int(x) % 2 if self.binary else Q(x)

    def eye(self, n):
        return [[self.q(i == j) for j in range(n)] for i in range(n)]

    def zero(self, n, m=None):
        return [[self.q(0)]*(n if m is None else m) for _ in range(n)]

    def add(self, a, b, scale=1):
        return [[self.q(x+scale*y) for x, y in zip(r, s)] for r, s in zip(a, b)]

    def mm(self, a, b):
        bt = list(zip(*b))
        return [[self.q(sum(x*y for x, y in zip(row, col))) for col in bt] for row in a]

    def inverse(self, a):
        n = len(a)
        rows = [list(r)+e for r, e in zip(a, self.eye(n))]
        for j in range(n):
            pivot = next(i for i in range(j, n) if rows[i][j])
            rows[j], rows[pivot] = rows[pivot], rows[j]
            divisor = rows[j][j]
            rows[j] = [self.q(x/divisor) if not self.binary else x for x in rows[j]]
            for i in range(n):
                if i != j and rows[i][j]:
                    c = rows[i][j]
                    rows[i] = [self.q(x-c*y) for x, y in zip(rows[i], rows[j])]
        result = [r[n:] for r in rows]
        require(self.mm(a, result) == self.mm(result, a) == self.eye(n), 'two-sided inverse')
        return result

    def blocks(self, a, b, c, d):
        return [x+y for x, y in zip(a, b)]+[x+y for x, y in zip(c, d)]

    def double(self, a):
        z = self.zero(len(a), len(a[0]))
        return self.blocks(a, z, z, a)


def factor(h, binary):
    f = Field(binary)
    triples = list(combinations(range(h), 3))
    V = [[f.q(i in t) for t in triples] for i in range(h)]
    if binary:
        a, b = V, [list(row) for row in zip(*V)]
    else:
        # Dyadic rank-h factor of (|S intersect T|-1)/2. Replace the
        # last incidence row by the all-ones row; sum(V rows)=3*ones.
        a = V[:-1]+[[Q(1)]*len(triples)]
        b = [[(V[i][t]-V[-1][t])/2 for i in range(h-1)]
             +[(3*V[-1][t]-1)/2] for t in range(len(triples))]
    c = f.mm(b, a)
    expected = [[f.q(len(set(s)&set(t))) if binary else Q(len(set(s)&set(t))-1, 2)
                 for t in triples] for s in triples]
    require(c == expected and all(c[i][i] == 1 for i in range(len(c))), 'central factor and diagonal')
    return f, triples, a, b, c


def terminal_decoder(h, binary, omit_workspace_normalization=False):
    f, triples, a, b, c = factor(h, binary)
    n, k = len(c), len(a)
    i, z = f.eye(n), f.zero(n)
    s = f.add(i, c, -1)
    s2, s3 = f.mm(s, s), f.mm(f.mm(s, s), s)
    diagonal = f.add(i, s2, -1)
    lower = f.add(f.add(s, s), s3, -1)
    negs = f.add(z, s, -1)
    side_word = f.blocks(diagonal, negs, lower, diagonal)
    exchange = f.blocks(z, f.add(z, i, -1), i, z)
    # D times the side-only three-shear word equals the desired exchange.
    decoder = f.blocks(lower, f.add(z, diagonal, -1), diagonal, s)
    require(f.mm(decoder, side_word) == exchange, 'complete scalar endpoint')
    q = f.mm(a, b)
    q2, ik = f.mm(q, q), f.eye(k)
    upper_left = f.add(f.add(ik, q, -3), q2)
    upper_right = f.add(q, ik, -2)
    lower_left = f.add(f.add(ik, ik), q, -1)
    kernel = f.blocks(upper_left, upper_right, lower_left, f.add(f.zero(k), ik, -1))
    aa, bb = f.double(a), f.double(b)
    bp = f.mm(bb, kernel)
    require(f.add(f.eye(2*n), f.mm(bp, aa)) == decoder, 'two-summary-bank correction')
    small = f.add(f.eye(2*k), f.mm(aa, bp))
    invsmall = f.inverse(small)
    backward = f.mm(invsmall, aa)
    # Execute five matrix phases on every independent data/dirty column.
    data = [row+[f.q(0)]*(2*k) for row in f.eye(2*n)]
    dirty = [[f.q(0)]*(2*n)+row for row in f.eye(2*k)]
    dirty = f.add(dirty, f.mm(aa, data))
    data = f.add(data, f.mm(bp, dirty))
    dirty = f.add(dirty, f.mm(backward, data), -1)
    if not omit_workspace_normalization:
        dirty = f.mm(small, dirty)
    data = f.add(data, f.mm(bp, dirty), -1)
    expected_data = [row+[f.q(0)]*(2*k) for row in decoder]
    expected_dirty = [[f.q(0)]*(2*n)+row for row in f.eye(2*k)]
    exact = data == expected_data and dirty == expected_dirty
    if not omit_workspace_normalization:
        require(exact, 'arbitrary dirty workspace restored by full decoder')
    def nnz(m):
        return sum(bool(x) for row in m for x in row)
    dyadic = all(Q(x).denominator & (Q(x).denominator-1) == 0
                 for m in (aa, bp, small, invsmall, backward) for row in m for x in row)
    require(dyadic, 'no non-dyadic coefficients in tested scalar decoder')
    return dict(h=h, field='F2' if binary else 'Q', ports=n, central_channels=k,
                terminal_workspace_channels=2*k, full_data_channels=2*n,
                central_square_zero=f.mm(c, c) == z,
                side_involutory=s2 == i, exact_dirty_endpoint=exact,
                decoder_matrix_rank=H.H.rank(decoder) if not binary else None,
                nonzero_phase_coefficients=dict(injection=nnz(aa), read=nnz(bp),
                    backward_injection=nnz(backward), workspace_normalization=nnz(small)),
                old_three_central_routines_nonzero_coefficients=6*(nnz(a)+nnz(b)),
                new_decoder_nonzero_coefficients=nnz(aa)+2*nnz(bp)+nnz(backward)+nnz(small),
                tested_coefficients_dyadic=dyadic,
                scope='Scalar identity and arbitrary-input restoration only. '
                      'Frames, recursive children, stock and complex phases not priced.')


def field_rank(matrix, binary):
    if not binary:
        return H.H.rank(matrix)
    pivots = {}
    for row in matrix:
        value = sum((int(x) % 2) << i for i, x in enumerate(row))
        while value:
            bit = value.bit_length()-1
            if bit in pivots:
                value ^= pivots[bit]
            else:
                pivots[bit] = value
                break
    return len(pivots)


def unequal_stage_control(h, binary):
    f, triples, a, b, _ = factor(h, binary)
    n, k = len(triples), len(a)
    permutations = [list(range(n)) for _ in range(3)]
    permutations[1][:4] = [1, 3, 0, 2]
    permutations[2][:5] = [2, 4, 1, 0, 3]
    aa = [[[row[j] for j in p] for row in a] for p in permutations]
    bb = [[b[j] for j in p] for p in permutations]
    side = [f.add(f.eye(n), f.mm(bi, ai), -1) for ai, bi in zip(aa, bb)]
    s1, s2, s3 = side
    require(f.mm(s1, s2) != f.mm(s2, s1), 'genuinely unequal noncommuting stage control')
    i, z = f.eye(n), f.zero(n)
    word = f.blocks(f.add(i, f.mm(s2, s1), -1), f.add(z, s2, -1),
                    f.add(f.add(s1, s3), f.mm(s3, f.mm(s2, s1)), -1),
                    f.add(i, f.mm(s3, s2), -1))
    decoder = f.blocks(f.add(f.add(s1, s3), f.mm(s1, f.mm(s2, s3)), -1),
                       f.add(f.mm(s1, s2), i, -1),
                       f.add(i, f.mm(s2, s3), -1), s2)
    require(f.mm(decoder, word) == f.blocks(z, f.add(z, i, -1), i, z),
            'noncommutative three-stage decoder')
    s1_squared = f.mm(s1, s1)
    same_decoder = f.blocks(f.add(f.add(s1, s1), f.mm(s1_squared, s1), -1),
                            f.add(s1_squared, i, -1), f.add(i, s1_squared, -1), s1)
    require(f.mm(same_decoder, word) != f.blocks(z, f.add(z, i, -1), i, z),
            'using the aligned-stage decoder on unequal stages must fail')
    q12, q13, q23 = f.mm(aa[0], bb[1]), f.mm(aa[0], bb[2]), f.mm(aa[1], bb[2])
    iz, zz = f.eye(k), f.zero(k)
    def neg(m):
        return [[f.q(-x) for x in row] for row in m]
    block_rows = [[neg(q12), f.add(f.mm(q12, q23), q13, -1), neg(iz), q12],
                  [iz, neg(q23), zz, neg(iz)],
                  [iz, neg(q23), zz, neg(iz)],
                  [zz, iz, zz, zz]]
    kernel = [sum((block[row] for block in blocks), []) for blocks in block_rows for row in range(k)]
    az = f.zero(k, n)
    injection = [r+s for left, right in ((aa[1], az), (aa[2], az), (az, aa[0]), (az, aa[1]))
                 for r, s in zip(left, right)]
    bz = f.zero(n, k)
    out = [r+s+t+u for r, s, t, u in zip(bb[0], bb[1], bz, bz)]
    out += [r+s+t+u for r, s, t, u in zip(bz, bz, bb[1], bb[2])]
    read = f.mm(out, kernel)
    require(f.add(f.eye(2*n), f.mm(read, injection)) == decoder, 'four-summary-bank factor')
    small = f.add(f.eye(4*k), f.mm(injection, read))
    backward = f.mm(f.inverse(small), injection)
    data = [row+[f.q(0)]*(4*k) for row in f.eye(2*n)]
    dirty = [[f.q(0)]*(2*n)+row for row in f.eye(4*k)]
    dirty = f.add(dirty, f.mm(injection, data))
    data = f.add(data, f.mm(read, dirty))
    dirty = f.add(dirty, f.mm(backward, data), -1)
    dirty = f.mm(small, dirty)
    data = f.add(data, f.mm(read, dirty), -1)
    require(data == [row+[f.q(0)]*(4*k) for row in decoder], 'unequal decoded data')
    require(dirty == [[f.q(0)]*(2*n)+row for row in f.eye(4*k)], 'unequal dirty restoration')
    summary_ranks = [field_rank(aa[1]+aa[2], binary), field_rank(aa[0]+aa[1], binary)]
    return dict(h=h, field='F2' if binary else 'Q', ports=n, channels_per_stage=k,
                uncompressed_workspace=4*k, joint_input_summary_ranks=summary_ranks,
                algebraic_summary_dimension=sum(summary_ranks), exact_dirty_endpoint=True,
                noncommuting_stages=True,
                scope='Toy column-permuted stage maps, NOT production cover routing. '
                      'Rank compression is not a free framed implementation.')


def nilpotent_controls():
    out = []
    for h in (5, 6, 7, 8, 10):
        f, triples, a, b, c = factor(h, True)
        gram = f.mm(a, b)
        expected = [[int((h-1)*(h-2)//2 if i == j else h-2) % 2
                     for j in range(h)] for i in range(h)]
        require(gram == expected, 'exact incidence Gram')
        require((gram == f.zero(h)) == (h % 4 == 2), 'nilpotent sufficient family')
        out.append(dict(h=h, ports=len(triples), gram_zero=gram == f.zero(h)))
    # Complex involutory side S=I-C would require C^2=2C and hence rank(C)=v/2.
    # Under copied source spans L>=vr/2. Grant zero stock and test the relaxed
    # moment on t=r/d in [0,1/2]. Concavity reduces rejection to endpoints.
    saving = Q(3, 40)
    at_zero = H.power(Q(1, 3), saving)
    at_zero = (3*at_zero[0], 3*at_zero[1])
    # d=2,r=1, rho=0, lambda=t/2=1/4, only an optimistic arithmetic relaxation.
    half = H.ideal_budget(2, 1, saving, rho=Q(0), loss_ratio=Q(1, 4))['moment_interval']
    require(at_zero[0] > 1 and half[0] > 1, 'complex involution copied-center screen')
    return dict(binary_gram_controls=out, complex_relaxed_endpoint_moments=[at_zero, half],
                scope='Simple involutory side-map shortcut only; not the general terminal decoder.')


def tensor_lift_control():
    # Start with an exact annihilating pair P0,P1 in dimension three.
    # Diagonal entries of C remain one in a tensor scalar factor C tensor C.
    # Therefore pairs (0,0),(0,1) remain adjacent whenever C_01 is nonzero.
    d, p0, p1 = 3, [1, 0, 0], [0, 1, 0]
    def label(p, q, kind):
        if kind == 'intersection':
            return [a*b for a in p for b in q]
        if kind == 'union':
            return [a+b-a*b for a in p for b in q]
        return [a+b-2*a*b for a in p for b in q]
    out = {}
    for kind in ('intersection', 'union', 'parity'):
        x, y = label(p0, p0, kind), label(p0, p1, kind)
        out[kind] = dict(dimension=d*d, rank=sum(x),
                         required_edge_product_rank=sum(a*b for a, b in zip(x, y)))
    require(out['intersection']['required_edge_product_rank'] == 0, 'ordinary tensor preserves edge')
    require(all(out[k]['required_edge_product_rank'] > 0 for k in ('union', 'parity')),
            'rank-boosting labels violate an inherited scalar tensor edge')
    return dict(exact_coordinate_counterexample=out,
                scope='These literal tensor/union/parity lifts with unchanged tensor scalar support only.')


def orbit_difference_control(n=5):
    upper = list(combinations(range(n), 2))
    lower = sorted(upper, key=lambda x: (x[1], x[0]))
    q = len(upper)
    permutation = [lower.index(pair) for pair in upper]
    require(permutation != list(range(q)), 'nontrivial triangular-order permutation')
    # Coefficient vectors expose every independent upper/lower payload.
    f = Field(False)
    a = [row+[Q(0)]*q for row in f.eye(q)]
    b = [[Q(0)]*q+row for row in f.eye(q)]
    tb = [b[j] for j in permutation]
    delta = f.add(a, tb, -1)
    out_upper = f.add(a, delta, -1)
    inverse = [permutation.index(j) for j in range(q)]
    out_lower = f.add(b, [delta[j] for j in inverse])
    require(out_upper == tb and out_lower == [a[j] for j in inverse], 'packed-difference endpoint')
    require(out_lower != f.add(b, delta), 'inverse alignment cannot be omitted')
    return dict(n=n, moved_addresses=2*q, each_packed_stream=q,
                paid_alignments=['lower-to-upper triangular order', 'upper-to-lower triangular order'],
                total_aligned_volume=2*q,
                scope='Two half-volume alignments equal full movable volume; '
                      'no fixed-tape cost bound or faster typed recurrence.')


def audit():
    controls = [terminal_decoder(6, True), terminal_decoder(5, False)]
    require(not terminal_decoder(5, False, True)['exact_dirty_endpoint'], 'normalization adverse control')
    return dict(status='Design comparison; general coupled terminal decoder selected for one pricing test.',
                terminal_decoder=controls, nilpotent_special_case=nilpotent_controls(),
                unequal_stages=[unequal_stage_control(6, True), unequal_stage_control(5, False)],
                tensor_lift=tensor_lift_control(), orbit_difference=orbit_difference_control())


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--write', type=Path)
    parser.add_argument('--check', type=Path)
    args = parser.parse_args()
    value = encode(audit())
    if args.write:
        args.write.write_text(json.dumps(value, indent=2, sort_keys=True)+'\n')
    if args.check:
        require(value == json.loads(args.check.read_text()), 'saved design comparison')
    print('Mechanism design checks passed; no framed implementation or stronger kappa.')
