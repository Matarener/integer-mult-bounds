#!/usr/bin/env python3
"""Independent Gaussian-Gram screen for the cut58 response alphabet.

Apache-2.0; Ross Richardson with substantial OpenAI Codex assistance.
No source constructor imports; this is an exact finite check, not a supplier.
"""
import argparse
from collections import Counter, deque
import hashlib
import gzip
import json
from pathlib import Path


def need(ok, message):
    if not ok:
        raise ValueError(message)


def rank_mod(rows, prime):
    rows = [list(row) for row in rows]
    if not rows:
        return 0
    pivot = 0
    for col in range(len(rows[0])):
        hit = next((i for i in range(pivot, len(rows)) if rows[i][col] % prime), None)
        if hit is None:
            continue
        rows[pivot], rows[hit] = rows[hit], rows[pivot]
        inv = pow(rows[pivot][col] % prime, -1, prime)
        rows[pivot] = [(x * inv) % prime for x in rows[pivot]]
        for i in range(pivot + 1, len(rows)):
            c = rows[i][col] % prime
            if c:
                rows[i] = [(x - c * y) % prime for x, y in zip(rows[i], rows[pivot])]
        pivot += 1
        if pivot == len(rows):
            break
    return pivot


def decode_old(data):
    n = len(data['rows'])
    need(n == 12, 'actual source ambient arity')
    need(data['rows'][4:] == [1 << j for j in range(4, 12)], 'old spectator address')
    need(not any(data['alpha'][4:]) and not any(data['quad'][4:]), 'old spectator phases')
    need(data['offset'] < 16 and not any(q >> 4 for q in data['quad']), 'old support')
    perm, phase = [], []
    for x in range(16):
        perm.append(sum(((r & x).bit_count() % 2) << j for j, r in enumerate(data['rows'][:4])) ^ data['offset'])
        q = data['constant'] + sum(data['alpha'][j] for j in range(4) if x >> j & 1)
        q += 2 * sum((data['quad'][j] & x).bit_count() % 2 for j in range(4) if x >> j & 1)
        phase.append(q % 4)
    return tuple(perm), tuple(phase), data['global_phase'] % 4


def compose(a, b):
    pa, qa, ga = a
    pb, qb, gb = b
    return tuple(pa[pb[x]] for x in range(16)), tuple((qb[x] + qa[pb[x]]) % 4 for x in range(16)), (ga + gb) % 4


def polar_rank(g):
    q = g[1]
    alpha = [(q[1 << j] - q[0]) % 4 for j in range(4)]
    b = [[0] * 4 for _ in range(4)]
    for j in range(4):
        b[j][j] = alpha[j] % 2
        for k in range(j + 1, 4):
            value = (q[(1 << j) | (1 << k)] - q[0] - alpha[j] - alpha[k]) % 4
            need(value % 2 == 0, 'quadratic phase cross term')
            b[j][k] = b[k][j] = value // 2
    for x in range(16):
        value = q[0] + sum(alpha[j] for j in range(4) if x >> j & 1)
        value += 2 * sum(b[j][k] for j in range(4) for k in range(j + 1, 4) if (x >> j & 1) and (x >> k & 1))
        need(value % 4 == q[x], 'full phase truth table is quadratic')
    return rank_mod(b, 2)


def projective(g):
    return g[0], g[1], g[2] % 2


def verify_tags(elements, tags, k, w):
    for g, tag in elements.items():
        need(tags[projective(g)] == tag, 'projective tag agrees with its Cayley word')
        for generator, bit in ((k, (1, 0)), (w, (0, 1))):
            h = compose(generator, g)
            need(tags[projective(h)] == tuple(a ^ b for a, b in zip(tag, bit)),
                 'projective tag satisfies each generator edge')


def gram(reps, tensor_power, prime=101, imag=10):
    need((imag * imag + 1) % prime == 0, 'Gaussian integer homomorphism')
    out = []
    for a in reps:
        row = []
        for b in reps:
            trace = sum(pow(imag, (b[1][x] - a[1][x]) % 4, prime)
                        for x in range(16) if a[0][x] == b[0][x]) % prime
            row.append(pow(trace, tensor_power, prime))
        out.append(row)
    return out


def produce(source):
    raw = gzip.decompress(source.read_bytes()) if source.suffix == ".gz" else source.read_bytes()
    need(hashlib.sha256(raw).hexdigest() == '7553ec4f63272cd4b8efb16b2ec01183240be248e36a5dc45df32f9ebd24de58', 'frozen cut58 source')
    data = json.loads(raw)
    k, w = (decode_old(data['operators'][name]) for name in ('K', 'W'))
    identity = tuple(range(16)), (0,) * 16, 0
    negative_identity = identity[0], identity[1], 2
    need(compose(k, k) == negative_identity, 'all-f K square')
    elements, queue = {identity: (0, 0)}, deque([identity])
    while queue:
        g = queue.popleft()
        for generator, bit in ((k, (1, 0)), (w, (0, 1))):
            h = compose(generator, g)
            tag = tuple(a ^ b for a, b in zip(elements[g], bit))
            if h in elements:
                need(elements[h] == tag, 'all-f word parity consistency')
            else:
                elements[h] = tag
                queue.append(h)
        need(len(elements) <= 128, 'finite old response group cap')
    need(len(elements) == 128, 'complete group cardinality')
    need({g for g in elements if g[0] == identity[0] and len(set(g[1])) == 1}
         == {identity, negative_identity}, 'only scalar families are literal +/- identity')
    reps, tags = [], {}
    census = Counter()
    for g, (pk, pw) in elements.items():
        r = polar_rank(g)
        need(r >= 2 * (pw + (pk ^ pw)), 'complete group native tariff')
        census[f'{pk}{pw}:rank{r}'] += 1
        h = projective(g)
        if h not in tags:
            tags[h] = (pk, pw)
            reps.append(h)
        else:
            need(tags[h] == (pk, pw), 'projective parity consistency')
    need(len(reps) == 64, 'projective response cardinality')
    verify_tags(elements, tags, k, w)
    ranks = [rank_mod(gram(reps, f), 101) for f in (1, 2)]
    need(ranks == [54, 64], 'exact one- and two-fold Gram ranks')
    # The tensor-square Gram is positive definite over C: its Gaussian integer
    # determinant has a nonzero image in F101. Schur product with the one-fold
    # positive semidefinite Gram (strict positive diagonal) preserves positive
    # definiteness at every later tensor power. This is a written proof step.
    need(2 * (1 + 4 + 6) == 22 and 54 + 22 == 76 > 72, 'full unchanged-prefix native budget')
    bad_reps = reps[:-1] + [reps[0]]
    need(rank_mod(gram(bad_reps, 2), 101) < 64, 'duplicate-ray control')
    bad_tags = dict(tags)
    bad_tags[projective(k)] = (0, 0)
    need(bad_tags[projective(k)] != elements[k], 'K parity mutation is nontrivial')
    try:
        verify_tags(elements, bad_tags, k, w)
    except ValueError as exc:
        need('tag' in str(exc), 'K tag control fails at its intended condition')
    else:
        raise ValueError('K tag mutation was accepted')
    return {
        'status': 'PASS_CUT58_SEPARABLE_QUERY_TARIFF',
        'source_sha256': hashlib.sha256(raw).hexdigest(),
        'group_elements': len(elements), 'projective_rays': len(reps),
        'rank_census': dict(sorted(census.items())),
        'prime': 101, 'imaginary_unit_image': 10,
        'one_fold_gram_rank': ranks[0], 'two_fold_gram_rank': ranks[1],
        'covered_tensor_sizes': 'all f>=2 by the written Schur-product argument',
        'target_defect_ranks_per_field': {'W_parity': 1, 'K_plus_W_parity': 4, 'fresh_T_parity': 6},
        'rank_claim_scope': 'The three target-defect ranks are proved in the written block-kernel derivation; they are not inferred from this finite group census.',
        'sharp_native_mass_per_f': 22, 'whole_mass_per_f': 76, 'fixed_stock_per_f': 72,
        'limits': ['Only separable <K,W> times T-parity unary alphabet.', 'Scalar bank GL and restored same-volume dirty helpers allowed.', 'No claim at f=1 from W parity.', 'No new supplier, unrestricted native alphabet lower bound, or kappa.'],
        'controls': ['Duplicated projective ray loses two-fold rank.', 'Wrong K tag is rejected by the actual Cayley-edge predicate.'],
    }


def main():
    parser = argparse.ArgumentParser()
    here = Path(__file__).resolve().parent
    parser.add_argument('--source', type=Path, default=here / 'source' / 'CUT58.json.gz')
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    result = produce(args.source)
    expected = here / 'CERTIFICATE.json'
    if args.write:
        expected.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    else:
        need(json.loads(expected.read_text()) == json.loads(json.dumps(result)), 'fixed certificate matches exact current computation')
    print(result['status'], 'group128 rays64 f1rank54 f2rank64; no_new_kappa')


if __name__ == '__main__':
    main()
