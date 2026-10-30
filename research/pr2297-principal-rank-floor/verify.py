#!/usr/bin/env python3
"""Exact principal-rank floor C >= 554 for every scalar decoder of c*I_112 on the
PR2297 five-frame cover (full-port tariff).  Standard library only.

Prepared by Sagar Thakrar (thakrarsagar) with substantial AI assistance from
Claude (Anthropic, Claude Opus 5.5).  Apache-2.0.
"""
import hashlib
import io
import itertools
import json
import random
import sys
import tarfile
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ARCHIVE = 'research/community-frontier1094-audit/selected-replay.tar.gz'
FIXTURE = 'research/kport-group-scalar-endpoint-audit/fixtures/PR2297-CANDIDATE.json'
MEMBER = 'candidate/strict/global/base/work/complex-nine-native/DATA-PHASES.json'
PAYLOAD_SHA = 'c5916ff312678f12aba403847643fbbc29f643acec60bdf836fa56cd3e8251fa'
EXPECTED = dict(groups=23, flats=107, pairs=107 * 107, support=88, floor=554, direct=554, unpaid='4432/9')


class Reject(Exception):
    pass


def need(condition, message):
    if not condition:
        raise Reject(message)


def sources():
    manifest = json.loads((HERE / 'SOURCES.json').read_text())
    bound = {}
    for pin in manifest['files']:
        if pin['usage'] != 'input':
            continue
        raw = (ROOT / pin['path']).read_bytes()
        need(hashlib.sha256(raw).hexdigest() == pin['sha256'], 'source SHA256: ' + pin['path'])
        need(hashlib.sha1(b'blob %d\0' % len(raw) + raw).hexdigest() == pin['git_blob'], 'source blob: ' + pin['path'])
        bound[pin['path']] = raw
    need(set(bound) == {ARCHIVE, FIXTURE}, 'exactly the two pinned inputs')
    with tarfile.open(fileobj=io.BytesIO(bound[ARCHIVE]), mode='r:gz') as archive:
        stream = archive.extractfile(MEMBER)
        need(stream is not None, 'selected member missing')
        payload = stream.read(2_000_001)
    need(len(payload) <= 2_000_000 and hashlib.sha256(payload).hexdigest() == PAYLOAD_SHA, 'selected member SHA256')
    recipes = sorted(json.loads(payload)['recipes'], key=lambda r: r['port'])
    need([r['port'] for r in recipes] == list(range(112)), '112 selected ports')
    labels = [r['q'] for r in recipes]
    need(len(set(labels)) == 112 and all(type(q) is int and 0 < q < 512 for q in labels), 'labels in F2^9')
    candidate = json.loads(bound[FIXTURE])
    candidate = candidate.get('candidate', candidate)
    groups = candidate.get('blocks', candidate.get('groups'))
    need(sorted(p for g in groups for p in g) == list(range(112)), 'port partition')
    return labels, groups


def dot(a, b):
    return (a & b).bit_count() & 1


def reduce_basis(vectors):
    pivots = {}
    for v in vectors:
        while v:
            b = v.bit_length() - 1
            if b not in pivots:
                pivots[b] = v
                break
            v ^= pivots[b]
    return list(pivots.values())


def rref_key(vectors):
    """Canonical reduced echelon basis (a complete invariant of the span)."""
    rows = sorted(reduce_basis(vectors), reverse=True)
    for i, r in enumerate(rows):
        b = r.bit_length() - 1
        for j in range(len(rows)):
            if j != i and rows[j] >> b & 1:
                rows[j] ^= r
    return tuple(sorted(rows))


def members(vectors):
    """Membership mask (bit x set iff x in span) of the F2-span of vectors."""
    elems = [0]
    for v in reduce_basis(vectors):
        elems += [x ^ v for x in elems]
    mask = 0
    for x in elems:
        mask |= 1 << x
    return mask


def elems(mask):
    return [x for x in range(512) if mask >> x & 1]


def dim(mask):
    count = mask.bit_count()
    need(count & (count - 1) == 0, 'not a subspace')
    return count.bit_length() - 1


def rank_packed(rows):
    pivots = {}
    for v in rows:
        while v:
            b = v.bit_length() - 1
            if b not in pivots:
                pivots[b] = v
                break
            v ^= pivots[b]
    return len(pivots)


_BASIS = {}


def basis(mask):
    if mask not in _BASIS:
        _BASIS[mask] = sorted(reduce_basis(elems(mask)))
    return _BASIS[mask]


def rho_elimination(left, right):
    """Method 1: F2 rank of the pairing matrix between bases (bit-packed elimination)."""
    bl, br = basis(left), basis(right)
    return rank_packed([sum(dot(a, b) << j for j, b in enumerate(br)) for a in bl])


_PERP = {}


def rho_counting(left, right):
    """Method 2: dim L - dim(L meet R-perp), by counting vectors of F2^9."""
    if right not in _PERP:
        _PERP[right] = sum(1 << x for x in range(512) if all(dot(x, r) == 0 for r in basis(right)))
    return dim(left) - dim(left & _PERP[right])


def cover(labels, groups):
    spaces = [[labels[p] for p in g] for g in groups]
    need(len(groups) == EXPECTED['groups'] and sorted(map(len, groups)) == [2] + [5] * 22, '22 five-frames and one pair')
    for sp in spaces:
        need(all(dot(a, b) == (i == j) for i, a in enumerate(sp) for j, b in enumerate(sp)), 'orthonormal group')
    gm = [members(sp) for sp in spaces]
    need(all(dim(m) == len(sp) for m, sp in zip(gm, spaces)), 'independent frame')
    # Premise of the principal-rank count: no orthogonal (free) pair anywhere, so K = c I_112.
    for i, j in itertools.combinations(range(len(gm)), 2):
        need(rho_elimination(gm[i], gm[j]) > 0, 'free (orthogonal) group pair %d,%d' % (i, j))
    need(dim(members(labels)) == 9, 'ambient F2^9')
    return spaces, gm


def flats_closure(gm):
    """Method A: breadth-first closure of single-group spans under adding one group."""
    seen = set(gm)
    frontier = list(seen)
    while frontier:
        nxt = []
        for L in frontier:
            for g in gm:
                if g & ~L:
                    M = members(basis(L) + basis(g))
                    if M not in seen:
                        seen.add(M)
                        nxt.append(M)
        frontier = nxt
    return seen


def flats_small_subsets(gm):
    """Method B: spans of all group subsets of size <= 5 (independent enumeration),
    then a check that this family contains every single group and is closed
    under adding any group, hence contains every span of a nonempty group set."""
    gb = [basis(g) for g in gm]
    keys = set()

    def walk(start, vectors, size):
        keys.add(rref_key(vectors))
        if size < 5:
            for g in range(start, len(gb)):
                walk(g + 1, vectors + gb[g], size + 1)

    for g in range(len(gb)):
        walk(g + 1, list(gb[g]), 1)
    for key in list(keys):
        for b in gb:
            need(rref_key(list(key) + b) in keys, 'small-subset family not closed')
    return {members(list(key)) for key in keys}


def closure_sets(flats, gm):
    return {F: frozenset(i for i, g in enumerate(gm) if g & ~F == 0) for F in flats}


def certificate(path=HERE / 'CERTIFICATE.json'):
    data = json.loads(Path(path).read_text())
    den = data['denominator']
    need(type(den) is int and den > 0, 'denominator')
    rows = []
    for row in data['sets']:
        S = frozenset(row['groups'])
        w = row['weight_numerator']
        need(type(w) is int and w > 0 and S and S <= frozenset(range(23)), 'certificate row')
        rows.append((S, w))
    need(len({S for S, _ in rows}) == len(rows), 'distinct sets')
    return den, rows


def check_dual(den, rows, P, rho):
    """Exact dual feasibility over every ordered pair of flats."""
    hits = [[i for i in range(len(P)) if S & P[i]] for S, _ in rows]
    load = [[0] * len(P) for _ in P]
    for (S, w), h in zip(rows, hits):
        hs = set(h)
        for i in h:
            row = load[i]
            for j in hs:
                row[j] += w
    worst = None
    for i in range(len(P)):
        for j in range(len(P)):
            need(load[i][j] <= rho[i][j] * den, 'dual constraint violated at flat pair %d,%d' % (i, j))
            slack = rho[i][j] * den - load[i][j]
            worst = slack if worst is None else min(worst, slack)
    return worst


def objective(den, rows, d):
    return Q(sum(w * sum(d[g] for g in S) for S, w in rows), den)


def random_pairs_check(den, rows, gm, trials, seed):
    """Second check of the closure reduction: arbitrary (non-closed) supports P, Q."""
    rng = random.Random(seed)
    n = len(gm)
    for _ in range(trials):
        P = frozenset(rng.sample(range(n), rng.randint(1, n)))
        Qs = frozenset(rng.sample(range(n), rng.randint(1, 3 if rng.random() < .5 else n)))
        bl = reduce_basis([v for g in P for v in basis(gm[g])])
        br = reduce_basis([v for g in Qs for v in basis(gm[g])])
        rank = rank_packed([sum(dot(a, b) << j for j, b in enumerate(br)) for a in bl])
        lhs = sum(w for S, w in rows if S & P and S & Qs)
        need(lhs <= rank * den, 'non-closed support pair violates the dual')


def exact_instance(spaces, gm, groups, den, rows, seed=2297):
    """End-to-end exact rational instance: a random unit-triangular decoder with
    even denominators, K = A diag(c) B^T = c0 I_112 checked entrywise, then the
    chain C >= sum_S y_S hits(S) >= sum_S y_S f(S)."""
    rng = random.Random(seed)
    n = 112
    group_of = {p: gi for gi, g in enumerate(groups) for p in g}
    A = [[Q(int(i == j)) for j in range(n)] for i in range(n)]
    for _ in range(160):
        i, j = sorted(rng.sample(range(n), 2))
        A[j][i] = Q(rng.choice([1, -1, 3, -3]), rng.choice([1, 2, 4, 8]))
    c = [Q(rng.choice([1, -1, 1, 3]), rng.choice([1, 2, 4])) for _ in range(n)]
    c0 = Q(1, 2)
    inv = [[Q(0)] * n for _ in range(n)]  # A^{-1} by forward substitution
    for col in range(n):
        x = [Q(0)] * n
        for i in range(n):
            x[i] = Q(int(i == col)) - sum((A[i][k] * x[k] for k in range(i) if A[i][k]), Q(0))
        for i in range(n):
            inv[i][col] = x[i]
    Bt = [[c0 * inv[t][j] / c[t] for j in range(n)] for t in range(n)]  # B^T
    for i in range(n):
        Ai = [(t, A[i][t] * c[t]) for t in range(n) if A[i][t]]
        for j in range(n):
            need(sum((a * Bt[t][j] for t, a in Ai), Q(0)) == (c0 if i == j else 0), 'exact identity')
    cost = 0
    hits = {S: 0 for S, _ in rows}
    for t in range(n):
        P = frozenset(group_of[i] for i in range(n) if A[i][t])
        Qs = frozenset(group_of[j] for j in range(n) if Bt[t][j])
        bl = reduce_basis([v for g in P for v in spaces[g]])
        br = reduce_basis([v for g in Qs for v in spaces[g]])
        cost += rank_packed([sum(dot(a, b) << j for j, b in enumerate(br)) for a in bl])
        for S in hits:
            hits[S] += bool(S & P) and bool(S & Qs)
    d = [len(sp) for sp in spaces]
    need(all(hits[S] >= sum(d[g] for g in S) for S in hits), 'principal-rank count on instance')
    need(Q(cost) >= Q(sum(w * hits[S] for S, w in rows), den) >= objective(den, rows, d), 'chain')
    need(cost >= 554, 'instance below floor')
    return cost


def controls(den, rows, P, rho, gm, labels, groups, spaces):
    rejected = []

    def rejects(name, fn):
        try:
            fn()
        except Reject:
            rejected.append(name)
            return
        raise SystemExit('FAIL: negative control was accepted: ' + name)

    rejects('inflated certificate weight', lambda: check_dual(den, [(rows[0][0], rows[0][1] + den)] + rows[1:], P, rho))
    top = max(range(len(P)), key=lambda i: len(P[i]))
    bad = [row[:] for row in rho]
    bad[top][top] = 8
    rejects('ambient pairing pretended degenerate (rho(all,all)=8)', lambda: check_dual(den, rows, P, bad))
    line = [[1 if len(P[i]) == 1 and len(P[j]) == 1 else rho[i][j] for j in range(len(P))] for i in range(len(P))]
    rejects('line-label tariff instead of full-port tariff', lambda: check_dual(den, rows, P, line))
    rejects('doubled certificate (value 1108 > direct cost)', lambda: check_dual(den, [(S, 2 * w) for S, w in rows], P, rho))
    # Method B fed a mutated input (one group dropped) must disagree with method A.
    rejects('method B fed a group list missing one group', lambda: need(
        flats_small_subsets(gm[:-1]) == flats_closure(gm), 'flat mismatch'))
    # Premise check: move the residual pair into E_0-perp, creating an orthogonal (free)
    # group pair; cover() must reject it for exactly that reason.
    perp0 = [x for x in range(1, 512) if dot(x, x) and not any(dot(x, v) for v in spaces[0])]
    a, b = next((a, b) for a, b in itertools.combinations(perp0, 2) if not dot(a, b))
    mutated = list(labels)
    mutated[groups[-1][0]], mutated[groups[-1][1]] = a, b

    def free_pair_cover():
        try:
            cover(mutated, groups)
        except Reject as exc:
            if 'free (orthogonal) group pair' not in str(exc):
                raise SystemExit('FAIL: free-pair control rejected for the wrong reason: %s' % exc)
            raise
    rejects('cover with a free (orthogonal) group pair', free_pair_cover)
    return rejected


def main():
    labels, groups = sources()
    spaces, gm = cover(labels, groups)
    d = [len(sp) for sp in spaces]
    fa = flats_closure(gm)
    fb = flats_small_subsets(gm)
    need(fa == fb and len(fa) == EXPECTED['flats'], 'two flat enumerations agree')
    flats = sorted(fa, key=lambda F: (dim(F), F))
    Pmap = closure_sets(flats, gm)
    P = [Pmap[F] for F in flats]
    rho = [[rho_elimination(L, R) for R in flats] for L in flats]
    need(rho == [[rho_counting(L, R) for R in flats] for L in flats], 'two pairing-rank methods agree')
    need(all(rho[i][j] == rho[j][i] for i in range(len(P)) for j in range(len(P))), 'symmetric tariff')
    den, rows = certificate()
    need(len(rows) == EXPECTED['support'], 'certificate support size')
    slack = check_dual(den, rows, P, rho)
    value = objective(den, rows, d)
    need(553 < value <= 554, 'certificate value in (553, 554]')
    floor = 554  # C is an integer sum of ranks and C >= value > 553
    direct = sum(len(g) * rho_elimination(m, m) for g, m in zip(groups, gm))
    need(direct == EXPECTED['direct'] == floor, 'direct decoder attains the floor')
    unpaid = Q(8, 9) * sum(len(g) * len(g) for g in groups)
    threshold = unpaid.numerator // unpaid.denominator  # largest integer cost with no loss
    need(str(unpaid) == EXPECTED['unpaid'] and threshold == 492 and floor > threshold, 'no saving at the zero-saving threshold')
    random_pairs_check(den, rows, gm, 2000, 554)
    inst = exact_instance(spaces, gm, groups, den, rows)
    rej = controls(den, rows, P, rho, gm, labels, groups, spaces)
    result = dict(status='PASS_PR2297_PRINCIPAL_RANK_FLOOR', flats=len(P), flat_pairs=len(P) ** 2,
                  certificate_sets=len(rows), certificate_denominator=den,
                  certificate_value=str(value), certificate_value_float=float(value), min_slack_numerator=slack,
                  floor=floor, direct_decoder_cost=direct, zero_saving_threshold=threshold, unpaid_budget=str(unpaid),
                  exact_instance_cost=inst, rejected_controls=rej)
    print(json.dumps(result, indent=1))
    print('PASS_PR2297_PRINCIPAL_RANK_FLOOR')


if __name__ == '__main__':
    try:
        main()
    except Reject as exc:
        print('FAIL:', exc)
        sys.exit(1)
