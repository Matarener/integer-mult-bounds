"""Encoded readout controls and a two-center residual contract.

Douglas Colkitt, with OpenAI Codex assistance. Apache-2.0.
No cheaper word, supplier, or multiplication exponent is certified.
"""
from collections import Counter
from fractions import Fraction as Q
from itertools import combinations
from pathlib import Path
import argparse
import importlib.util
import json
import math

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('boundary_readout_tools',
    HERE.parent/'boundary-readout-sixteenth/audit.py')
B = importlib.util.module_from_spec(spec)
spec.loader.exec_module(B)
require, encode, rank, mm = B.require, B.encode, B.rank, B.mm
eye, zero, sub, projection, partial = B.eye, B.zero, B.sub, B.projection, B.partial


def geometry(h):
    require(h >= 5 and h != 9, 'nondegenerate triple geometry')
    labels = list(combinations(range(h), 3))
    vectors = [[Q(i in t) for i in range(h)] for t in labels]
    P = [projection([v], h) for v in vectors]
    R = [projection([v for v, t in zip(vectors, labels) if j in t], h)
         for j in range(h)]
    require(all(rank(x) == h-1 for x in R), 'central source span')
    for t, p in zip(labels, P):
        for j in t:
            require(mm(p, R[j]) == mm(R[j], p) == p, 'incidence nesting')
    return labels, P, R


def matrix_key(A):
    return tuple(tuple(row) for row in A)


def unit(role, dim):
    return {(role, matrix_key(eye(dim))): 1}


def move(value, A):
    return {(role, matrix_key(mm(A, M))): c for (role, M), c in value.items()}


def plus(x, y, sign=1, binary=False):
    z = dict(x)
    for k, v in y.items():
        z[k] = z.get(k, 0)+sign*v
    if binary:
        z = {k: v % 2 for k, v in z.items()}
    return {k: v for k, v in z.items() if v}


def expected(U, K, R, binary):
    n, h = len(K), len(K[0])
    out = []
    for t in range(n):
        value = unit(t, 2*h)
        for j, c in enumerate(U[t]):
            if c:
                value = plus(value, move(unit(n+j, 2*h), partial(R[j])), c, binary)
        out.append(move(value, partial(K[t])))
    return out


def discrepancy(P, R, U):
    """Nonzero target rows of the rational broadcast endpoint discrepancy."""
    n, k, h = len(P), len(R), len(P[0])
    K = [sub(eye(h), p) for p in P]
    out = [[Q(0)]*((n+k)*h) for _ in range(n*h)]
    quotient = [[Q(0)]*(k*h) for _ in range(n*h)]
    for t in range(n):
        for a in range(h):
            out[t*h+a][t*h:(t+1)*h] = K[t][a]
        for j in range(k):
            block = [[U[t][j]*x for x in row] for row in sub(K[t], R[j])]
            qblock = [[U[t][j]*x for x in row] for row in mm(P[t], R[j])]
            for a in range(h):
                out[t*h+a][(n+j)*h:(n+j+1)*h] = block[a]
                quotient[t*h+a][j*h:(j+1)*h] = qblock[a]
    return out, quotient


def target_pivot(h=5, binary=False):
    labels, P_all, R_all = geometry(h)
    P = [p for t, p in zip(labels, P_all) if 0 in t]
    R, n = R_all[0], len(P)
    K = [sub(eye(h), p) for p in P]
    targets = [unit(t, 2*h) for t in range(n)]
    center = unit(n, 2*h)
    # Encode all other targets against the original pivot at common frame 0.
    for t in range(1, n):
        targets[t] = plus(targets[t], targets[0], -1, binary)
    targets[0] = plus(move(targets[0], partial(R)), center, 1, binary)
    # One dependent copy of the updated pivot supplies every decoder input.
    copied = move(targets[0], partial(R))
    undecoded = [move(targets[t], partial(K[t])) for t in range(1, n)]
    require(undecoded != expected([[1]]*n, K, [R], binary)[1:],
            'target decoder is required for arbitrary dirty inputs')
    for t in range(1, n):
        targets[t] = plus(targets[t], copied, 1, binary)
        targets[t] = move(targets[t], partial(K[t]))
    targets[0] = move(targets[0], mm(partial(K[0]), partial(R)))
    require(targets == expected([[1]]*n, K, [R], binary),
            'pivot readout on all arbitrary targets and center')
    baseline = Counter({h-1: n+1})
    changed = Counter({h-1: n+1})  # initial pivot move, copy, n-1 other endpoints
    changed[rank(sub(K[0], R))] += 1
    D, Qblock = discrepancy(P, [R], [[1]]*n)
    base = n*(h-1)
    require(rank(Qblock) == h-1, 'single-center quotient saturates copied rank')
    require(rank(D) == base+h-1, 'full discrepancy agrees with quotient formula')
    require(sum(t*c for t, c in baseline.items()) == rank(D),
            'existing copy attains the rational-lift lower bound')
    return dict(h=h, targets=n, payload='F2' if binary else 'Q',
                baseline_histogram=dict(baseline), candidate_histogram=dict(changed),
                baseline_rank=base+h-1, candidate_rank=sum(t*c for t, c in changed.items()),
                rank_lower_bound=rank(D), exact_arbitrary_inputs=True,
                scope='Isolated arbitrary-center broadcast; rational-realizable '
                      'encoding/decoding graphs, full-volume rank charges.')


def center_pair(h=5, binary=False):
    labels, P, Rs = geometry(h)
    R, n = Rs[:2], len(P)
    K = [sub(eye(h), p) for p in P]
    U = [[int(j in t) for j in range(2)] for t in labels]
    V = [[Q(i in t) for i in range(h)] for t in labels if 0 in t and 1 in t]
    intersection = projection(V, h)
    require(rank(intersection) == h-2, 'central intersection dimension')
    candidates = {'zero': zero(h), 'intersection': intersection,
                  'first_center': R[0], 'second_center': R[1], 'full': eye(h)}
    reports = {}
    for name, M in candidates.items():
        z = [move(unit(n+j, 2*h), mm(partial(M), partial(R[j]))) for j in range(2)]
        z[0] = plus(z[0], z[1], 1, binary)
        copies = [move(x, partial(M)) for x in z]
        target = []
        for t in range(n):
            y = unit(t, 2*h)
            # Original z0=w0-w1 and z1=w1, so transformed readout is U L^-1.
            y = plus(y, copies[0], U[t][0], binary)
            y = plus(y, copies[1], U[t][1]-U[t][0], binary)
            target.append(move(y, partial(K[t])))
        unclean = [move(x, mm(partial(R[j]), partial(M))) for j, x in enumerate(z)]
        require(unclean != [unit(n+j, 2*h) for j in range(2)], 'center decoder is mandatory')
        z[0] = plus(z[0], z[1], -1, binary)
        z = [move(x, mm(partial(R[j]), partial(M))) for j, x in enumerate(z)]
        require(z == [unit(n+j, 2*h) for j in range(2)], 'arbitrary centers restored')
        require(target == expected(U, K, R, binary), 'pair encoder and decoder exact')
        hist = Counter({h-1: n})
        for j in range(2):
            hist[rank(sub(M, R[j]))] += 2
        hist[rank(M)] += 2
        hist.pop(0, None)
        reports[name] = dict(histogram=dict(sorted(hist.items())),
                             rank=sum(t*c for t, c in hist.items()))
    floor = n*(h-1)+2*(h-1)+2
    require(reports['intersection']['rank'] == floor, 'sharp three-point median bound')
    require(all(x['rank'] >= floor for x in reports.values()), 'common-frame coding floor')
    return dict(h=h, payload='F2' if binary else 'Q', baseline_rank=n*(h-1)+2*(h-1),
                all_common_frame_rank_floor=floor, exact_arbitrary_inputs=True,
                evaluated_frames=reports,
                scope='Two restored centers encoded and decoded at one common '
                      'frame, two independent encoded readouts at frame zero.')


def joint_quotient(h, dense=False):
    labels = list(combinations(range(h), 3))
    pair_columns = list(combinations(range(h), 2))
    inclusion = [[int(i in t and j in t) for i, j in pair_columns] for t in labels]
    # Scale all covectors by six: 6 phi_T[l] = 3*1_(l in T)-1.
    rows = [[int(j in t)*(3*int(l in t)-1) for j in range(h) for l in range(h)]
            for t in labels]
    require(rank(rows) == rank(inclusion) == math.comb(h, 2), 'pair-incidence quotient rank')
    # Check both linear span identities, rather than inferring a formula from ranks.
    for t, row in zip(labels, rows):
        for j, l in pair_columns:
            require(row[j*h+l]+Q(row[j*h+j], 2) == 3*int(j in t and l in t),
                    'recover pair feature')
        for j in range(h):
            require(sum(int(j in t and l in t) for l in range(h) if l != j)
                    == 2*int(j in t), 'recover singleton feature')
    result = dict(h=h, targets=len(labels), target_floor=len(labels)*(h-1),
                  separate_copy_rank=h*(h-1), joint_discrepancy_excess=rank(rows),
                  status='Lower-bound gap only; no implementing word.')
    if dense:
        labels, P, R = geometry(h)
        U = [[int(j in t) for j in range(h)] for t in labels]
        D, q = discrepancy(P, R, U)
        require(rank(D) == result['target_floor']+rank(rows), 'dense full discrepancy')
        require(rank(q) == rank(rows), 'dense vs compressed quotient')
        require(rank(U) == h, 'actual scalar center signals remain independent')
        result.update(full_discrepancy_rank=rank(D), scalar_broadcast_rank=rank(U))
    return result


def residual_pair(h=5):
    labels, P, Rs = geometry(h)
    R = Rs[:2]
    a = [Q(1), Q(2)]+[Q(0)]*(h-2)
    b = [Q(2), Q(1)]+[Q(0)]*(h-2)
    L = [projection([v], h) for v in (a, b)]
    for j in range(2):
        require(mm(R[j], L[j]) == mm(L[j], R[j]) == L[j], 'residual line nested in center')
        require(rank(sub(R[j], L[j])) == h-2, 'paid peeling width')
    U = [[int(j in t) for j in range(2)] for t in labels]
    D, quotient = discrepancy(P, L, U)
    base = len(labels)*(h-1)
    require(rank(quotient) == 1 and rank(D) == base+1, 'one-rank residual discrepancy')
    groups = Counter(tuple(row) for row in U)
    for t, p in zip(labels, P):
        if 0 in t and 1 not in t:
            require(mm(p, L[0]) == zero(h), 'first-only target contains first residual line')
        if 1 in t and 0 not in t:
            require(mm(p, L[1]) == zero(h), 'second-only target contains second residual line')
        if 0 in t and 1 in t:
            require(mm(p, [[x-y] for x, y in zip(a, b)]) == [[Q(0)] for _ in range(h)],
                    'difference direction lies in all common target caps')
    # The pair kernel is an address-label relation, not a scalar relation
    # between arbitrary arrays. Explicitly retain rank(U)=2.
    kernel = a+[-x for x in b]
    require(mm(quotient, [[x] for x in kernel]) == [[Q(0)] for _ in quotient],
            'explicit pair address-kernel vector')
    require(rank(U) == 2, 'no free scalar channel deletion')
    return dict(h=h, targets=len(labels), residual_vectors=[a, b],
                group_counts={str(k): v for k, v in groups.items()},
                peeling_children={h-2: 2}, existing_remaining_copies={1: 2},
                target_floor=base, residual_discrepancy_floor=base+1,
                baseline_complete_rank=base+2*(h-1),
                optimistic_complete_rank=base+2*(h-2)+1,
                status='Exact residual contract and lower bound; one-child '
                       'realization is missing. Copied inputs add no role volume.')


def residual_budget(h):
    saving = Q(2, 25)
    def moment(rows):
        return B.B.H.moment(rows, 3*h, 1, saving)
    old = moment({h-1: 2})
    ideal = moment({h-2: 2, 1: 1})
    gain = (old[0]-ideal[1], old[1]-ideal[0])
    split = moment({1: 1, h-2: 1})
    whole = moment({h-1: 1})
    penalty = (split[0]-whole[1], split[1]-whole[0])
    one = moment({1: 1})
    require(gain[0] > 0 and gain[1] < one[0], 'positive but sub-singleton moment budget')
    count = int(gain[0]/penalty[1])
    require(count == int(gain[1]/penalty[0]), 'stable split allowance')
    direct_targets = 2*math.comb(h-2, 2)
    require(direct_targets > count, 'all exclusive targets split too many times')
    return dict(h=h, saving=saving, normalization='Sum of (width/(3h))^(1-saving); '
                'common role normalization omitted from both sides.',
                ideal_moment_gain=gain, per_target_split_penalty=penalty,
                maximum_such_splits=count, exclusive_targets=direct_targets,
                scope='Conditional on the unimplemented one-rank residual word. '
                      'Every other changed child still has to be charged.')


def audit():
    return dict(status='Two encoders rejected; a joint residual contract remains '
                       'open. No improved supplier or kappa.',
                target_pivot=[target_pivot(binary=b) for b in (False, True)],
                center_pair=[center_pair(h, b) for h in (5, 6) for b in (False, True)],
                joint_quotients=[joint_quotient(h, dense=(h == 5)) for h in (5, 6, 7, 8)],
                residual_pairs=[residual_pair(h) for h in (5, 6)],
                residual_moment_budgets=[residual_budget(h) for h in (5, 6, 23)],
                h23_formula_only=dict(h=23, target_count=1771,
                    separate_copy_rank=506, joint_discrepancy_excess=253,
                    scope='General pair-incidence proof; not a dense replay or construction.'))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--write', type=Path)
    parser.add_argument('--check', type=Path)
    args = parser.parse_args()
    value = encode(audit())
    if args.write:
        args.write.write_text(json.dumps(value, indent=2, sort_keys=True)+'\n')
    if args.check:
        require(value == json.loads(args.check.read_text()), 'saved joint readout diagnostic')
    print('Joint readout design checks passed; no cheaper readout word or kappa.')
