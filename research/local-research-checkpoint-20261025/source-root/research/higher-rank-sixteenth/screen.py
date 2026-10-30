"""Two exact higher-rank geometry screens; no supplier/algorithm certificate.

Douglas Colkitt, with OpenAI Codex assistance. Apache-2.0.
Uses an explicitly hypothetical two-axis block ledger. Its failures do not
exclude different compilers, terminal contracts, or recurrence profiles.
"""
from collections import Counter
from fractions import Fraction as Q
from itertools import combinations
from pathlib import Path
import argparse
import hashlib
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def require(ok, message):
    if not ok:
        raise ValueError(message)


def encode(value):
    if isinstance(value, Q):
        return str(value)
    if isinstance(value, dict):
        return {str(k): encode(v) for k, v in value.items()}
    if isinstance(value, (tuple, list)):
        return [encode(v) for v in value]
    return value


def power_interval(x, p, q, scale=10**24):
    """Positive rational x**(p/q), certified by integer powers."""
    x = Q(x)
    require(x > 0 and p > 0 and q > 0, 'positive power input')
    y = x**p
    lo, hi = 0, scale
    rhs = y.numerator * scale**q
    while hi**q * y.denominator < rhs:
        hi *= 2
    while hi-lo > 1:
        mid = (hi+lo)//2
        if mid**q * y.denominator <= rhs:
            lo = mid
        else:
            hi = mid
    require(lo**q*y.denominator <= rhs <= hi**q*y.denominator,
            'power enclosure')
    return Q(lo, scale), Q(hi, scale)


def moment(rows, m, W, saving):
    exponent = 1-saving
    lo = hi = Q(0)
    for width, count in rows.items():
        require(0 < width < m and count >= 0, 'valid child')
        a, b = power_interval(Q(width, m), exponent.numerator,
                              exponent.denominator)
        lo += count*a/W
        hi += count*b/W
    return lo, hi


def block_budget(d, r, saving, rho):
    """Equal-axis hypothetical copied ledger with central loss erased.

    rho = auxiliary independent roles per label per axis. The rho=1 floor
    applies ONLY to retained transparent identity factorization JLV=I_n.
    No physical block-copy theorem or compiler is asserted by these rows.
    """
    require(0 < r < d and rho >= 0, 'block parameters')
    m, W = d*d, 2+2*rho
    rows = Counter()
    rows[(d-r)**2] += 2
    rows[r*r] += 1
    rows[r*(d-r)] += 4
    rows[d*r] += 2*rho
    rows[m-d*r] += 2*rho
    lo, hi = moment(rows, m, W, saving)
    role = moment(Counter([d*r, m-d*r]), m, 1, saving)
    require(role[0] > 1, 'extra role contribution exceeds unit volume')
    mass = sum(t*n for t, n in rows.items())
    require(W*m-mass == r*r, 'gross block deficit accounting')
    return dict(d=d, r=r, m=m, role_ratio=rho, W_per_pair=W,
                saving=saving, rows=dict(sorted(rows.items())),
                rank_deficit_per_pair=r*r, moment_interval=[lo, hi],
                added_role_moment_interval=role, excluded=lo > 1,
                scope='Hypothetical two-axis block ledger; zero central loss; '
                      'ideal within-macro batching; no compiler supplied.')


def mm(a, b):
    return [[sum(x*y for x, y in zip(row, col)) for col in zip(*b)]
            for row in a]


def rank(a):
    a = [list(map(Q, row)) for row in a]
    pivot = 0
    for j in range(len(a[0])):
        i = next((i for i in range(pivot, len(a)) if a[i][j]), None)
        if i is None:
            continue
        a[pivot], a[i] = a[i], a[pivot]
        z = a[pivot][j]
        a[pivot] = [x/z for x in a[pivot]]
        for i in range(pivot+1, len(a)):
            z = a[i][j]
            if z:
                a[i] = [x-z*y for x, y in zip(a[i], a[pivot])]
        pivot += 1
        if pivot == len(a):
            break
    return pivot


def binary_rank(rows):
    basis = {}
    for x in rows:
        while x:
            j = x.bit_length()-1
            if j not in basis:
                basis[j] = x
                break
            x ^= basis[j]
    return len(basis)


def line_projector(h, triple):
    # P = x (x^T G)/2, G=I-J/9, x^T G x=2.
    return [[Q((int(j in triple)-Q(1, 3))*int(i in triple), 2)
             for j in range(h)] for i in range(h)]


def packet_projector(h, triples):
    matrices = [line_projector(h, t) for t in triples]
    return [[sum(p[i][j] for p in matrices) for j in range(h)]
            for i in range(h)]


def sunflower_control():
    r, h = 5, 11
    left = [(0, i, i+1) for i in range(1, 11, 2)]
    right = [(0, 2, 3), (0, 4, 5), (0, 6, 7), (0, 8, 9), (0, 10, 1)]
    p, q = packet_projector(h, left), packet_projector(h, right)
    require(mm(p, p) == p and mm(q, q) == q, 'packet idempotence')
    require(rank(p) == rank(q) == r, 'packet ranks')
    require(any(any(row) for row in mm(p, q)), 'nonorthogonal packets')
    require(mm(p, q) != mm(q, p), 'genuinely noncommuting control')
    # Exhaustively check the necessary condition for ALL triple lines versus
    # a packet. The proof in REPORT extends it to every maximal packet.
    counts = Counter()
    for t in combinations(range(h), 3):
        total = sum(len(set(t)&set(s)) for s in left)
        require(total == 3+(r-1)*int(0 in t), 'intersection-sum identity')
        counts[total] += 1
        require(total != r, 'no triple annihilates all packet lines')
    require(rank([[Q(i == j)-Q(1, 9) for j in range(h)]
                  for i in range(h)]) == h, 'nondegenerate common form')
    return dict(rank=r, dimension=h, left=left, right=right,
                projector_left=p, projector_right=q,
                possible_intersection_sums=dict(counts),
                theoretical_required_sum=r,
                obstruction='For r>=5, h=2r+1, every maximal sunflower '
                            'packet is nonorthogonal to every triple line. '
                            'Thus distinct packets cannot annihilate. The '
                            'compatible diagonal-one binary central map is I.',
                scalar_compatibility='No nontrivial central interaction in '
                                     'this packet/annihilation template.')


def tensor_cycle_control():
    h, r, q = 10, 5, 11
    triples = list(combinations(range(h), 3))
    sets = [set((i+2*j) % q for j in range(r)) for i in range(q)]
    # Factorwise checks certify every one of the 1320 block labels and every
    # required product without constructing a dense 145200-square block matrix.
    core = []
    for s in triples:
        row = 0
        require(Q(len(s)-1, 2) == 1, 'core diagonal normalization')
        for j, t in enumerate(triples):
            z = len(set(s)&set(t))
            if z % 2:
                row |= 1 << j
                require(s == t or z-1 == 0, 'core annihilation')
        core.append(row)
    cycle = []
    for i, s in enumerate(sets):
        row = 0
        require(len(s) == r, 'cycle rank')
        for j, t in enumerate(sets):
            adjacent = (i-j) % q in (1, q-1)
            require((not s&t) == adjacent, 'cycle orthogonality graph')
            if i == j or adjacent:
                row |= 1 << j
        cycle.append(row)
    require(binary_rank(core) == h and binary_rank(cycle) == q,
            'exact central factor ranks')
    # The triple core is noncommuting; the tensor family retains this property
    # at the same cycle label. It is not a disguised coordinate-coloring family.
    p = line_projector(h, (0, 1, 2))
    u = line_projector(h, (0, 1, 3))
    require(mm(p, p) == p and rank(p) == 1, 'core projector')
    require(mm(p, u) != mm(u, p), 'noncommuting tensor core')
    return dict(core_ground_size=h, core_labels=len(triples),
                cycle_length=q, cycle_supports=[sorted(s) for s in sets],
                block_label_count=len(triples)*q, label_rank=r,
                ambient_dimension=h*q,
                binary_central_rank=binary_rank(core)*binary_rank(cycle),
                core_product_checks=len(triples)**2, cycle_product_checks=q*q,
                core_matrix_sha256=hashlib.sha256(b''.join(
                    x.to_bytes((len(triples)+7)//8, 'little') for x in core)).hexdigest(),
                exact_contract='P_(S,i)=P_S tensor Q_i; C=C_core tensor '
                               '(I+Adj(C11)). Rank(P)=5; P^2=P; '
                               'C_uv=1,u!=v implies P_u P_v=P_v P_u=0.',
                scope='Valid rational block-label/binary-core geometry only; '
                      'no all-role circuit or complex supplier.')


def audit():
    targets = (Q(2, 25), Q(3, 40))
    cases = {}
    for name, d, r in [('sunflower_packet', 11, 5),
                       ('tensor_cycle', 110, 5),
                       ('cycle_alone_control', 11, 5),
                       ('half_rank_control', 2, 1)]:
        cases[name] = {str(s): {str(rho): block_budget(d, r, s, rho)
                               for rho in (Q(0), Q(1))} for s in targets}
    for s in targets:
        require(not cases['sunflower_packet'][str(s)]['0']['excluded'],
                'packet bare budget passes')
        require(cases['sunflower_packet'][str(s)]['1']['excluded'],
                'packet paid-port floor fails')
        require(cases['tensor_cycle'][str(s)]['0']['excluded'],
                'tensor budget fails even before roles')
        require(cases['half_rank_control'][str(s)]['1']['excluded'],
                'half-rank control still pays too much for source ports')
    files = ['research/kappa-nine/block_fano_obstruction.py',
             'research/kappa-nine/ASSESSMENT.md',
             'research/mechanism-prep/REPORT.md',
             'docs/research/kappa-sixteenth-preparation.md']
    return dict(status='TWO SCOPED REJECTIONS; NO NEW SUPPLIER OR KAPPA',
                sources={f: hashlib.sha256((ROOT/f).read_bytes()).hexdigest()
                         for f in files},
                sunflower=sunflower_control(), tensor_cycle=tensor_cycle_control(),
                budgets=cases, survivors=[],
                paid_fragment_attempts='None: neither candidate survives the '
                                       'optimistic budget and compatibility gates.',
                complex_companion='Not constructed. Both complex target '
                                  'scores fail in the assumed ledger already.',
                exclusions='These ledger screens do not prove lower bounds '
                           'for other circuits or block compilation methods.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path)
    parser.add_argument('--check', type=Path)
    args = parser.parse_args()
    result = encode(audit())
    if args.check:
        require(result == json.loads(args.check.read_text()), 'receipt mismatch')
    if args.output:
        args.output.write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    print('PASS two exact geometry controls and scoped target-budget rejections')
