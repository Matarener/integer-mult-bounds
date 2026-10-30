"""Independent exact signed-Pauli audit. Hiroki KUMAZAKI / OpenAI Codex.

Apache-2.0. No source verifier imports. Matrices are unnormalized integer
projector numerators; complex Pauli phases are represented modulo four.
"""
from collections import Counter
from fractions import Fraction
from itertools import product


def require(ok, message):
    if not ok:
        raise ValueError(message)


def multiply(a, b):
    p, x, z = a
    q, y, w = b
    return ((p + q + 2 * (z & y).bit_count()) % 4, x ^ y, z ^ w)


def commute(a, b):
    return ((a[1] & b[2]).bit_count() + (a[2] & b[1]).bit_count()) % 2 == 0


def subgroup(frame):
    result = [(0, 0, 0)]
    for generator in frame:
        result += [multiply(old, generator) for old in result]
    return result


def valid_frame(frame, n):
    if len(frame) != n:
        return False
    if any(multiply(p, p) != (0, 0, 0) for p in frame):
        return False
    if any(not commute(p, q) for p in frame for q in frame):
        return False
    return len({(x, z) for _, x, z in subgroup(frame)}) == 2**n


def gf2rank(values):
    pivots = {}
    for v in values:
        while v:
            bit = v.bit_length() - 1
            if bit in pivots:
                v ^= pivots[bit]
            else:
                pivots[bit] = v
                break
    return len(pivots)


def matrix_rank(matrix):
    a = [[Fraction(v) for v in row] for row in matrix]
    rank = 0
    for col in range(len(a[0])):
        pivot = next((i for i in range(rank, len(a)) if a[i][col]), None)
        if pivot is None:
            continue
        a[rank], a[pivot] = a[pivot], a[rank]
        for i in range(rank + 1, len(a)):
            if a[i][col]:
                ratio = a[i][col] / a[rank][col]
                for j in range(col, len(a[0])):
                    a[i][j] -= ratio * a[rank][j]
        rank += 1
    return rank


def doubled_projector_numerator(group, n):
    d = 2**n
    result = [[0] * (d*d) for _ in range(d*d)]
    for p, x, z in group:
        for a, b in product(range(d), repeat=2):
            sign = (-1) ** ((p + (z & a).bit_count() + (z & b).bit_count()) % 2)
            result[(a ^ x)*d + (b ^ x)][a*d + b] += sign
    return result


def check_projector(a, scale, expected_rank):
    size = len(a)
    require(all(a[i][j] == a[j][i] for i in range(size) for j in range(size)), 'Hermitian numerator')
    require(all(sum(a[i][k]*a[k][j] for k in range(size)) == scale*a[i][j]
                for i in range(size) for j in range(size)), 'projector idempotence')
    require(sum(a[i][i] for i in range(size)) == scale*expected_rank, 'projector trace')
    require(matrix_rank(a) == expected_rank, 'independent rational rank')


def census(n):
    d = 2**n
    labels = [((x & z).bit_count() % 4, x, z)
              for x, z in product(range(d), repeat=2) if x or z]
    seen = set()
    signed_frames = 0
    rank_counts = Counter()
    nontrivial_phase_frames = 0
    checked_projectors = 0
    for base in product(labels, repeat=n):
        if not valid_frame(base, n):
            continue
        r = gf2rank([p[1] for p in base])
        common_labels = frozenset((p[1], p[2]) for p in subgroup(base))
        base_numerator = doubled_projector_numerator(subgroup(base), n)
        # Every choice of generator signs is a different character, and every
        # one must give the same doubled projector. No sign is discarded first.
        for signs in product((0, 2), repeat=n):
            frame = [((p + sign) % 4, x, z) for (p, x, z), sign in zip(base, signs)]
            group = subgroup(frame)
            require(valid_frame(frame, n), 'signed frame is valid')
            require((2, 0, 0) not in group, 'single-copy group has no negative identity')
            diagonal = [p for p in group if p[1] == 0]
            require(len(diagonal) == 2**(n-r), 'signed diagonal intersection size')
            require(all(p[0] % 2 == 0 for p in diagonal), 'diagonal Hermitian phases are real')
            numerator = doubled_projector_numerator(group, n)
            require(numerator == base_numerator, 'sign cancellation in literal tensor matrices')
            signed_frames += 1
            rank_counts[str(r)] += 1
            nontrivial_phase_frames += int(any(p[0] % 2 for p in group))
        # The same image subgroup may have several ordered bases. Check its
        # literal matrix once, while all ordered signed frames were checked above.
        if common_labels in seen:
            continue
        seen.add(common_labels)
        a = base_numerator
        eq = [i*d+i for i in range(d)]
        neq = [i for i in range(d*d) if i not in eq]
        require(all(a[i][j] == 0 for i in eq for j in neq), 'equality projector commutation')
        check_projector(a, d, d)
        intersection = [[a[i][j] for j in eq] for i in eq]
        outside = [[a[i][j] for j in neq] for i in neq]
        check_projector(intersection, d, 2**(n-r))
        check_projector(outside, d, d-2**(n-r))
        checked_projectors += 3
    expected_frames = {1: 6, 2: 360}[n]
    expected_groups = {1: 3, 2: 15}[n]
    require(signed_frames == expected_frames, 'exhaustive signed frame cardinality')
    require(len(seen) == expected_groups, 'exhaustive image subgroup cardinality')
    return {'signed_ordered_frames': signed_frames, 'image_subgroups': len(seen),
            'fourier_rank_counts': dict(sorted(rank_counts.items())),
            'frames_with_imaginary_Pauli_entries': nontrivial_phase_frames,
            'literal_projectors': checked_projectors}


def tensor(a, b):
    return [[x*y for x in ar for y in br] for ar in a for br in b]


def signed_matrix_controls():
    # Gaussian integers (real, imaginary); all denominators stay explicit.
    def mul(a, b):
        return (a[0]*b[0]-a[1]*b[1], a[0]*b[1]+a[1]*b[0])

    def conjugate(a):
        return (a[0], -a[1])

    def mm(a, b):
        return [[tuple(sum(mul(a[i][k], b[k][j])[component]
                           for k in range(len(b))) for component in (0, 1))
                 for j in range(len(b[0]))] for i in range(len(a))]

    def adjoint(a):
        return [[conjugate(a[j][i]) for j in range(len(a))]
                for i in range(len(a[0]))]

    def kt(a, b):
        return [[mul(x, y) for x in ar for y in br] for ar in a for br in b]

    # C = exp(-i*pi*X/4) up to a scalar phase; C Z C* = -Y.
    # c is 2C and u is 4(C tensor C).
    c = [[(1,1), (1,-1)], [(1,-1), (1,1)]]
    require(mm(adjoint(c), c) == [[(4,0),(0,0)],[(0,0),(4,0)]], 'literal Clifford unitarity')
    z = [[(1,0),(0,0)],[(0,0),(-1,0)]]
    require(mm(mm(c, z), adjoint(c)) == [[(0,0),(0,4)],[(0,-4),(0,0)]], 'literal signed Y image')
    u = kt(c, c)
    other = kt(c, [[conjugate(v) for v in row] for row in c])
    eq = (0,3)
    def intersection_num(v):
        cols = [[row[j] for j in eq] for row in v]
        f = mm(cols, adjoint(cols))  # 16F
        return [[f[i][j] for j in eq] for i in eq]
    same = intersection_num(u)
    conjugated = intersection_num(other)
    require(same == [[(8,0),(-8,0)],[(-8,0),(8,0)]], 'same-factor Bell-minus intersection')
    require(conjugated == [[(8,0),(8,0)],[(8,0),(8,0)]], 'conjugated-factor Bell-plus intersection')
    # A unitary monomial on the complete two-column field need not preserve E.
    # Left CNOT exchanges output rows 2 and 3. Its cut Gram is I/2.
    routed = [u[i] for i in (0,1,3,2)]
    block = [[routed[i][j] for j in eq] for i in (1,2)]
    require(mm(adjoint(block), block) == [[(8,0),(0,0)],[(0,0),(8,0)]],
            'non-cut-preserving endpoint invalidates the partial-isometry step')
    return {'same_factor_intersection': 'Bell minus',
            'conjugated_factor_intersection': 'Bell plus',
            'noncolumnwise_unitary_endpoint_cut_gram': 'I/2',
            'exact_Gaussian_integer_controls': 3}


def controls():
    # Same symplectic label but a sign change in only the second tensor factor:
    # F=(I-Z tensor Z)/2 has no intersection with E=(I+Z tensor Z)/2.
    wrong = [[0]*4 for _ in range(4)]
    wrong[1][1] = wrong[2][2] = 2
    require(matrix_rank(wrong) == 2 and wrong[0][0] + wrong[3][3] == 0,
            'mismatched tensor factors invalidate r=0 tariff')
    require(not valid_frame([(0,1,0),(0,0,1)], 2), 'reject anticommuting images')
    require(not valid_frame([(0,1,0),(0,1,0)], 2), 'reject dependent images')
    require(not valid_frame([(1,1,0)], 1), 'reject anti-Hermitian image')
    # Two paired blocks and one unrestricted column: test the product factors
    # using the literal r=1 projector F=(I+X tensor X)/2.
    pair = doubled_projector_numerator([(0,0,0),(0,1,0)], 1)
    four = tensor(pair, pair)
    # Pairwise row index ordering is (a,b,c,d), E imposes a=b and c=d.
    eq = [i for i in range(16) if ((i>>3)&1)==((i>>2)&1) and ((i>>1)&1)==(i&1)]
    neq = [i for i in range(16) if i not in eq]
    cross_gram = [[four[i][j] for j in neq] for i in neq]
    check_projector(cross_gram, 4, 3)
    five = tensor(cross_gram, [[1,0],[0,1]])
    check_projector(five, 4, 6)
    return {'rejected_frame_controls': 3, 'mismatched_factor_control': 1,
            'k2_f4_cut_rank': 3, 'k2_f5_cut_rank': 6}


def run():
    return {'n1': census(1), 'n2': census(2), 'controls': controls(),
            'signed_matrix_controls': signed_matrix_controls()}


if __name__ == '__main__':
    import json
    print(json.dumps(run(), indent=2, sort_keys=True))
