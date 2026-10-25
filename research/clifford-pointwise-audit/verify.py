"""Independent exact-matrix audit of PR5526's core theorem, not a proof kernel.

DLamdata, with substantial OpenAI Codex assistance. Apache-2.0.
No predecessor scientific code is imported. --emit prints a receipt;
ordinary replay compares the complete receipt and never writes files.
"""
from collections import Counter, deque
from fractions import Fraction as F
from pathlib import Path
import argparse
import hashlib
import json

HERE = Path(__file__).resolve().parent


def need(condition, message):
    if not condition:
        raise ValueError(message)


def reduced(exponent, entries):
    """Entries (a+ib)/2**exponent, retaining the global phase."""
    while exponent and all(x % 2 == 0 for x in entries):
        exponent -= 1
        entries = tuple(x // 2 for x in entries)
    return exponent, tuple(entries)


def identity(n):
    d = 1 << n
    return 0, tuple(v for r in range(d) for c in range(d)
                    for v in (int(r == c), 0))


def rotate(matrix, power=1):
    e, a = matrix
    for _ in range(power % 4):
        a = tuple(v for j in range(0, len(a), 2) for v in (-a[j+1], a[j]))
    return e, a


def projective(matrix):
    return min(rotate(matrix, j) for j in range(4))


def gate(matrix, n, name, axis, other=0):
    e, a = matrix
    d = 1 << n
    out = list(a)
    if name == 'H':
        # H'=(1+i)/2 [[1,1],[1,-1]], so (H')**2=iI, not I.
        for r in range(d):
            if r & (1 << axis):
                continue
            s = r | (1 << axis)
            for c in range(d):
                j, k = 2*(r*d+c), 2*(s*d+c)
                x, y = a[j]+a[k], a[j+1]+a[k+1]
                u, v = a[j]-a[k], a[j+1]-a[k+1]
                out[j:j+2] = x-y, x+y
                out[k:k+2] = u-v, u+v
        return reduced(e+1, out)
    if name == 'S':
        for r in range(d):
            if r & (1 << axis):
                for c in range(d):
                    j = 2*(r*d+c)
                    out[j:j+2] = -a[j+1], a[j]
    elif name == 'CX':
        for r in range(d):
            s = r ^ (((r >> axis) & 1) << other)
            out[2*r*d:2*(r+1)*d] = a[2*s*d:2*(s+1)*d]
    else:
        raise ValueError('Unknown gate')
    return e, tuple(out)


def exact_group(n, omit_h=False):
    alphabet = [(kind, j, 0) for j in range(n)
                for kind in (('S',) if omit_h else ('H', 'S'))]
    alphabet += [('CX', j, k) for j in range(n) for k in range(n) if j != k]
    start = identity(n)
    found, queue = {start}, deque([start])
    while queue:
        m = queue.popleft()
        for name, j, k in alphabet:
            out = gate(m, n, name, j, k)
            if out not in found:
                found.add(out)
                queue.append(out)
        need(len(found) <= 46080, 'Finite-domain guard')
    return sorted(found), len(alphabet)*len(found)


def inner(a, b):
    """Unnormalized Hilbert--Schmidt inner product, exact in Q(i)."""
    ea, aa = a
    eb, bb = b
    re = sum(aa[j]*bb[j]+aa[j+1]*bb[j+1] for j in range(0, len(aa), 2))
    im = sum(aa[j]*bb[j+1]-aa[j+1]*bb[j] for j in range(0, len(aa), 2))
    return F(re, 1 << (ea+eb)), F(im, 1 << (ea+eb))


def unitary(matrix, d):
    e, a = matrix
    for r in range(d):
        for s in range(d):
            real = imag = 0
            for c in range(d):
                j, k = 2*(r*d+c), 2*(s*d+c)
                real += a[j]*a[k]+a[j+1]*a[k+1]
                imag += a[j+1]*a[k]-a[j]*a[k+1]
            need(real == ((1 << (2*e)) if r == s else 0) and imag == 0,
                 'Literal unitary identity')


def mul(a, b):
    return a[0]*b[0]-a[1]*b[1], a[0]*b[1]+a[1]*b[0]


def sub(a, b):
    return a[0]-b[0], a[1]-b[1]


def div(a, b):
    den = b[0]*b[0]+b[1]*b[1]
    need(den != 0, 'Nonzero Gaussian divisor')
    return (a[0]*b[0]+a[1]*b[1])/den, (a[1]*b[0]-a[0]*b[1])/den


def power(a, n):
    result = (F(1), F(0))
    while n:
        if n & 1:
            result = mul(result, a)
        a = mul(a, a)
        n //= 2
    return result


def rank(matrix):
    a = [row.copy() for row in matrix]
    pivot = 0
    for j in range(len(a[0])):
        found = next((i for i in range(pivot, len(a)) if a[i][j] != (0, 0)), None)
        if found is None:
            continue
        a[pivot], a[found] = a[found], a[pivot]
        for i in range(pivot+1, len(a)):
            if a[i][j] == (0, 0):
                continue
            factor = div(a[i][j], a[pivot][j])
            for k in range(j, len(a[0])):
                a[i][k] = sub(a[i][k], mul(factor, a[pivot][k]))
        pivot += 1
        if pivot == len(a):
            break
    return pivot


def gram(matrices, n, width):
    d = 1 << n
    return [[power(tuple(x/d for x in inner(a, b)), width) for b in matrices]
            for a in matrices]


def positive(matrix):
    """Exact Hermitian Schur complements; no floating eigenvalue routine."""
    a = [row.copy() for row in matrix]
    for j in range(len(a)):
        need(a[j][j][1] == 0 and a[j][j][0] > 0, 'Strictly positive Hermitian pivot')
        for r in range(j+1, len(a)):
            factor = div(a[r][j], a[j][j])
            for c in range(j+1, len(a)):
                a[r][c] = sub(a[r][c], mul(factor, a[j][c]))


def spectral_checks(matrices):
    for width in range(8, 12):
        g = gram(matrices, 1, width)
        low = [[sub(g[r][c], (F(int(r == c), 9), F(0))) for c in range(24)]
               for r in range(24)]
        high = [[sub((F(17*int(r == c), 9), F(0)), g[r][c]) for c in range(24)]
                for r in range(24)]
        positive(low)
        positive(high)
    return {'axes': 1, 'widths': [8, 9, 10, 11],
            'strict_lower': '1/9', 'strict_upper': '17/9', 'positive_pivots': 192}


def group_receipt(n):
    group, edges = exact_group(n)
    expected_projective = (1 << (n*n+2*n))
    for j in range(1, n+1):
        expected_projective *= (1 << (2*j))-1
    need(len(group) == 4*expected_projective, 'Complete exact Clifford group size')
    fibers = Counter(projective(m) for m in group)
    need(set(fibers.values()) == {4}, 'Four exact Gaussian phase lifts')
    hist = Counter()
    for m in fibers:
        unitary(m, 1 << n)
        real, imag = inner(identity(n), m)
        hist[(real*real+imag*imag)/(1 << (2*n))] += 1
    need(hist[F(1, 2)] == 2*((1 << (2*n))-1), 'First Clifford overlap count')
    need(hist[F(1)] == 1, 'Only identity projective class has unit trace overlap')
    width = 4*n+4
    row_sum = sum(count*q**(width//2) for q, count in hist.items() if q != 1)
    need(row_sum < F(8, 9), 'Literal finite Gram row budget')
    return {'axes': n, 'exact_matrices': len(group), 'projective_classes': len(fibers),
            'generator_edges': edges, 'phase_fiber_size': 4,
            'width': width, 'absolute_gram_row_sum': str(row_sum),
            'normalized_trace_squared_histogram': {str(k): v for k, v in sorted(hist.items())}}, sorted(fibers)


def phase_and_gram_checks(one_axis):
    ranks = {str(f): rank(gram(one_axis, 1, f)) for f in range(1, 12)}
    need(all(ranks[str(f)] == 24 for f in range(8, 12)), 'Four-width positive fixture')
    need(ranks['1'] < 24, 'Small-width independence must fail')
    i = (F(0), F(1))
    phase_controls = []
    for omitted in range(4):
        values = []
        for f in range(8, 12):
            terms = [power(i, ((f-omitted)*j) % 4) for j in range(4)]
            value = tuple(sum(t[k] for t in terms) for k in range(2))
            need(value == ((F(4), F(0)) if f % 4 == omitted else (F(0), F(0))),
                 'Missing-residue false acceptance control')
            values.append([str(x) for x in value])
        phase_controls.append({'omitted_residue': omitted, 'widths_8_to_11': values})
    h = gate(identity(1), 1, 'H', 0)
    need(gate(h, 1, 'H', 0) == rotate(identity(1)), 'H-prime square retains i')
    duplicate = [identity(1), rotate(identity(1))]
    need(all(rank(gram(duplicate, 1, f)) == 1 for f in range(1, 9)),
         'Scalar copies must be combined pointwise')
    smaller, _ = exact_group(1, omit_h=True)
    need(len(smaller) != 96, 'Omitted Hadamard must not certify the full group')
    need(mul((F(2), F(0)), power(i, 2)) != power(mul((F(2), F(0)), i), 2),
         'Exterior scalar differs from tensor-lifted scalar')
    for f in range(1, 13):
        c = tuple(-x for x in power(i, (-f) % 4))
        need(mul(c, power(i, f)) == (-F(1), F(0)),
             'Width-dependent formal residual vanishes pointwise')
        need(c != (0, 0), 'Width-dependent coefficient vector is nonzero')
    # P(x)=product_(j=0..3)(x-2**(8+j)); coefficient c_k multiplies [2**k I].
    coeffs = [1]
    for f in range(8, 12):
        out = [0]*(len(coeffs)+1)
        for k, c in enumerate(coeffs):
            out[k] -= (1 << f)*c
            out[k+1] += c
        coeffs = out
    values = [sum(c*(1 << (k*f)) for k, c in enumerate(coeffs)) for f in range(8, 13)]
    need(values[:4] == [0]*4 and values[4] != 0,
         'Arbitrary nonunitary scales do not have a four-width test')
    return {'one_axis_gram_ranks': ranks, 'omitted_residue_controls': phase_controls,
            'nonunitary_scale_counterexample_coefficients': coeffs,
            'nonunitary_scale_values_at_widths_8_to_12': values,
            'other_controls': ['small_width', 'H_prime_square_phase', 'duplicate_phase_classes',
                               'omitted_H_generator', 'exterior_scalar_placement',
                               'width_dependent_coefficients', 'arbitrary_nonunitary_scales']}


def source_checks():
    rows = json.loads((HERE/'SOURCE-RECEIPT.json').read_text())['files']
    result = []
    for row in rows:
        data = (HERE/row['local_path']).read_bytes()
        sha = hashlib.sha256(data).hexdigest()
        blob = hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
        need(sha == row['sha256'] and blob == row['git_blob'], 'Frozen source byte mismatch')
        result.append({'path': row['local_path'], 'sha256': sha, 'git_blob': blob})
    return result


def calculate():
    sources = source_checks()
    one, matrices = group_receipt(1)
    two, _ = group_receipt(2)
    return {'schema': 'clifford-pointwise-independent-matrix-audit/v1',
            'scope': 'Finite exact corroboration only; universal claims require AUDIT.md',
            'sources': sources, 'groups': [one, two], 'phase_and_gram': phase_and_gram_checks(matrices),
            'spectral_check': spectral_checks(matrices)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--emit', action='store_true')
    args = parser.parse_args()
    result = calculate()
    if args.emit:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        need(result == json.loads((HERE/'MATRIX-RESULT.json').read_text()), 'Matrix receipt mismatch')
        print('PASS_CLIFFORD_POINTWISE_MATRIX_AUDIT: 46176 exact matrices; complete receipt matched')


if __name__ == '__main__':
    main()
