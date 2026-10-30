"""Bounded residual-readout test; no improved supplier or exponent.

Douglas Colkitt, with OpenAI Codex assistance. Apache-2.0.
"""
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path
import argparse
import importlib.util
import json
import random

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('joint_readout',
    HERE.parent/'joint-readout-design/audit.py')
A = importlib.util.module_from_spec(spec)
spec.loader.exec_module(A)
require, rank, mm, encode = A.require, A.rank, A.mm, A.encode


def setup(h):
    labels, P, _ = A.geometry(h)
    K = [A.sub(A.eye(h), p) for p in P]
    a, b = [Q(1), Q(2)]+[Q(0)]*(h-2), [Q(2), Q(1)]+[Q(0)]*(h-2)
    L = [A.projection([v], h) for v in (a, b)]
    U = [[int(j in t) for j in range(2)] for t in labels]
    return labels, K, L, U


def direct_word(h, copied, binary):
    """Each unconverted source is read at its own frame on each target.

    Copies are dependent scratch, original centers are untouched. The two
    possible orders for targets needing both sources have equal width lists.
    """
    labels, K, L, U = setup(h)
    n, hist = len(labels), Counter()
    centers = [A.unit(n+j, 2*h) for j in range(2)]
    copies = {j: A.move(centers[j], A.partial(L[j])) for j in copied}
    hist[1] += len(copied)
    targets = []
    missing_exit_fails = False
    expected = A.expected(U, K, L, binary)
    for t in range(n):
        y, frame = A.unit(t, 2*h), A.zero(h)
        for j in copied:
            if U[t][j]:
                y = A.plus(y, copies[j], binary=binary)
        for j in range(2):
            if U[t][j] and j not in copied:
                hist[rank(A.sub(L[j], frame))] += 1
                y = A.move(y, mm(A.partial(L[j]), A.partial(frame)))
                frame = L[j]
                y = A.plus(y, centers[j], binary=binary)
        missing_exit_fails |= y != expected[t]
        hist[rank(A.sub(K[t], frame))] += 1
        targets.append(A.move(y, mm(A.partial(K[t]), A.partial(frame))))
    hist.pop(0, None)
    require(targets == expected, 'literal all-input residual map')
    require(missing_exit_fails, 'endpoint alignment cannot be omitted')
    base = n*(h-1)
    common = h-2
    expected_rank = base+len(copied)+2*common*(2-len(copied))
    total = sum(w*c for w, c in hist.items())
    require(total == expected_rank, 'general independent-target rank formula')
    original = {h-1: n+2}
    complete = hist.copy()
    complete[h-2] += 2  # already-paid center peeling, charged in the comparison
    moment = A.B.B.H.moment
    old = moment(original, 3*h, 1, Q(2, 25))
    new = moment(complete, 3*h, 1, Q(2, 25))
    require(new[0] > old[1], 'no direct schedule improves the original moment')
    return dict(h=h, payload='F2' if binary else 'Q', copied_centers=list(copied),
                residual_histogram=dict(sorted(hist.items())), residual_rank=total,
                complete_histogram=dict(sorted(complete.items())),
                moment_increase=(new[0]-old[1], new[1]-old[0]),
                arbitrary_input_map=True, original_centers_untouched=True)


def binary_rank(rows):
    pivots = {}
    for row in rows:
        x = row
        while x:
            j = x.bit_length()-1
            if j in pivots:
                x ^= pivots[j]
            else:
                pivots[j] = x
                break
    return len(pivots)


def operator_obstruction(h):
    """A single parallel bank, one extra transform before OR after it.

    Scalar mixers may be arbitrary, with unlimited dependent copies. This
    is a relaxation of compatible-frame scalar gates, not a topology search.
    """
    labels, K, L, U = setup(h)
    n = len(labels)
    key = A.matrix_key
    bank = [key(A.partial(k)) for k in K]
    baseline = {key(A.eye(2*h)), *bank}
    desired = [[key(mm(A.partial(K[t]), A.partial(L[j]))) if U[t][j] else None
                for j in range(2)] for t in range(n)]
    all_keys = sorted(baseline | {x for row in desired for x in row if x is not None})
    outside = [x for x in all_keys if x not in baseline]
    pos = {x: i for i, x in enumerate(outside)}
    columns = [[int(desired[t][j] == op) for t in range(n) for op in outside]
               for j in range(2)]
    rows = [[int(desired[t][j] == op) for j in range(2) for op in outside]
            for t in range(n)]
    col_bits = [sum(x << i for i, x in enumerate(row)) for row in columns]
    row_bits = [sum(x << i for i, x in enumerate(row)) for row in rows]
    cr, rr = rank(columns), rank(rows)
    require(cr == binary_rank(col_bits) == 2, 'two independent operator-valued columns')
    affected = sum(any(row) for row in U)
    require(rr == binary_rank(row_bits) == affected, 'independent affected output rows')
    exclusive = [next(t for t in range(n) if U[t] == row) for row in ([1, 0], [0, 1])]
    for t, j in zip(exclusive, range(2)):
        require(desired[t][j] not in baseline, 'exclusive desired operator outside bank span')
    # A concrete finite-address witness: distinct matrices in this list
    # send one address to distinct addresses, so their array-permutation
    # operators are linearly independent over BOTH scalar payload fields.
    prime = 1009
    def mod(x):
        x = Q(x)
        return x.numerator*pow(x.denominator, -1, prime) % prime
    matrices = [[[mod(x) for x in row] for row in M] for M in all_keys]
    rng = random.Random(109+h)
    address = None
    for _ in range(200):
        candidate = [rng.randrange(prime) for _ in range(2*h)]
        images = [tuple(sum(a*b for a, b in zip(row, candidate)) % prime for row in M)
                  for M in matrices]
        if len(set(images)) == len(matrices):
            address = candidate
            break
    require(address is not None, 'finite-address independence witness')
    return dict(h=h, targets=n, affected_targets=affected,
                baseline_operator_count=len(baseline), desired_operators_outside_bank=len(outside),
                early_extra_transform_lower_bound=cr, late_extra_transform_lower_bound=rr,
                rational_and_binary_payload_ranks_agree=True,
                exclusive_target_witnesses=[list(labels[t]) for t in exclusive],
                address_prime=prime, separating_address=address,
                distinct_operators=len(all_keys), distinct_images=len(set(images)),
                scope='One parallel bank of the unchanged target operators; '
                      'all extra transforms before OR all after the bank. '
                      'Arbitrary scalar mixers and dependent copies allowed. '
                      'Interleaved target transforms are outside this screen.')


def formula_ledger(h, copies):
    """General width ledger for direct target paths; no large dense replay."""
    from math import comb
    n, exclusive, common = comb(h, 3), comb(h-2, 2), h-2
    unaffected = comb(h-2, 3) if h >= 5 else 0
    hist = Counter({1: copies})
    if copies == 2:
        hist[h-1] += n
    elif copies == 1:
        hist[h-1] += unaffected+exclusive
        hist[1] += exclusive+common
        hist[h-2] += exclusive
        hist[h] += common
    else:
        hist[h-1] += unaffected
        hist[1] += 2*exclusive+common
        hist[h-2] += 2*exclusive
        hist[2] += common
        hist[h] += common
    return dict(sorted(hist.items()))


def audit():
    direct = [direct_word(h, c, b) for h in (5, 6)
              for c in ((), (0,), (1,), (0, 1)) for b in (False, True)]
    for row in direct:
        require(row['residual_histogram'] == formula_ledger(row['h'], len(row['copied_centers'])),
                'symbolic replay agrees with combinatorial ledger')
    return dict(status='Bounded shared-readout test closed without an improved word or kappa.',
                operator_screens=[operator_obstruction(h) for h in (5, 6)],
                direct_words=direct,
                h23_formula_only=[dict(copied_centers=k, residual_histogram=formula_ledger(23, k))
                                  for k in range(3)])


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--write', type=Path)
    parser.add_argument('--check', type=Path)
    args = parser.parse_args()
    result = encode(audit())
    if args.write:
        args.write.write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    if args.check:
        require(result == json.loads(args.check.read_text()), 'saved residual diagnostic')
    print('Residual shared-readout checks passed; no improved word or kappa.')
