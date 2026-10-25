"""Replay exact equations, rank fixtures and homogeneous bounds. Apache-2.0."""
import argparse
import hashlib
import itertools
import json
from pathlib import Path
import random
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import model as m
import oracle

ROOT = Path(__file__).resolve().parent


def require(ok, message):
    if not ok:
        raise ValueError(message)


def source_hashes():
    names = ('model.py', 'oracle.py', 'verify.py', 'test_package.py', 'PROOF.md',
             'inputs/RETENTION.json', 'inputs/pr3570-PROOF.md',
             'inputs/pr3536-PROOF.md', 'inputs/pr3558-PROOF.md')
    result = {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
              for name in names}
    retained = json.loads((ROOT / 'inputs/RETENTION.json').read_text())
    for row in retained['files']:
        require(result[row['retained_path']] == row['sha256'], 'retained source changed')
    return result


def arithmetic():
    for g, h in itertools.product(range(8), repeat=2):
        require(m.mul(1 << g, 1 << h) == 1 << oracle.group_product(g, h),
                'Hamilton multiplication mismatch')
    for mask in range(256):
        require(m.coordinates(mask) < 256, 'basis coordinate capacity')
        coords = m.coordinates(mask)
        rebuilt = 0
        for k in range(8):
            if coords >> k & 1:
                rebuilt ^= m.BASIS[k]
        require(rebuilt == mask, 'basis inverse')
    cubic = []
    fourth = []
    for labels in itertools.product((1, 2), repeat=3):
        value = 1
        for label in labels:
            value = m.mul(value, 1 ^ (1 << label))
        coords = m.coordinates(value)
        cubic.append(((coords >> 5) ^ (coords >> 6)) & 1)
    require(cubic == [1, 1, 0, 1, 1, 0, 1, 1], 'cubic table')
    for labels in itertools.product((1, 2), repeat=4):
        value = 1
        for label in labels:
            value = m.mul(value, 1 ^ (1 << label))
        require(value in (0, 255), 'fourth coefficient leakage')
        require(m.mul(value, 3) == m.mul(value, 5) == 0, 'fifth leakage')
        fourth.append(value)
    return dict(group_products=64, basis_values=256, cubic=cubic,
                fourth=fourth)


def check_word(roles, word):
    endpoint = m.endpoint(roles, word)
    x, y, ell, ei, ej, h, hp = m.call_matrices(roles, word)
    c = m.bm(m.bm(ei, m.bm(ell, ell)), ej)
    tau = m.bm(m.bm(x, h), y)
    q = m.bm(m.bm(x, m.bx(h, hp)), y)
    cubic = m.bm(m.bm(x, m.bx(m.bm(h, h), c)), y)
    require(tau == m.coefficient(endpoint, 3), 'quadratic chronology')
    require(q == m.coefficient(endpoint, 4), 'cross quadratic chronology')
    actual = m.bx(m.coefficient(endpoint, 5), m.coefficient(endpoint, 6))
    require(cubic == actual, 'mixed cubic chronology')
    for column in range(8 * roles):
        require(oracle.action(roles, word, column)
                == oracle.matrix_action(endpoint, column), 'dirty action mismatch')
    return 8 * roles


def generic_words():
    rng = random.Random(1904)
    words, columns = 0, 0
    for roles in range(1, 6):
        gates = tuple((g, u, v) for g in (1, 2) for u in range(1, 1 << roles)
                      for v in range(1, 1 << roles) if m.parity(u & v))
        for length in range(13):
            for _ in range(3):
                word = tuple(rng.choice(gates) for _ in range(length))
                for swapped in (word, tuple((3 - g, u, v) for g, u, v in word)):
                    columns += check_word(roles, swapped)
                    words += 1
    return dict(words=words, dirty_columns=columns, seed=1904)


def direct_endpoints():
    endpoints, columns, omissions = 0, 0, 0
    for t in range(1, 7):
        for spectators in range(3):
            roles = t + spectators
            for label in (1, 2):
                word = tuple((label, 1 << a, 1 << a)
                             for a in range(t) for _ in range(3))
                actual = m.endpoint(roles, word)
                expected = [[(1 << (label + 4) if a < t else 1) * int(a == b)
                             for b in range(roles)] for a in range(roles)]
                require(actual == expected, 'direct endpoint')
                columns += check_word(roles, word)
                endpoints += 1
                for k in range(len(word)):
                    require(m.endpoint(roles, word[:k] + word[k + 1:]) != expected,
                            'omitted paid factor escaped')
                    omissions += 1
    return dict(endpoints=endpoints, dirty_columns=columns, omissions=omissions)


def rank_lemma():
    fixtures, sharp = 0, 0
    for t in (1, 2):
        for ni in range(t, 4):
            for x in itertools.product(range(1 << ni), repeat=t):
                for y in itertools.product(range(1 << t), repeat=ni):
                    if m.bm(x, y) != m.identity(t):
                        continue
                    for bits in range(1 << (ni * (ni - 1) // 2)):
                        rows, cursor = [], 0
                        for a in range(ni):
                            row = 1 << a
                            for b in range(a):
                                row ^= ((bits >> cursor) & 1) << b
                                cursor += 1
                            rows.append(row)
                        value = m.rank(m.bm(m.bm(x, tuple(rows)), y))
                        require(value >= 2 * t - ni, 'Sylvester block fixture')
                        sharp += int(value == 2 * t - ni)
                        fixtures += 1
    require(sharp > 0, 'missing sharp block fixture')
    zero_products = 0
    for nj in range(5):
        for x, y in itertools.product(range(1 << nj), repeat=2):
            if not m.parity(x & y):
                require(int(bool(x)) + int(bool(y)) <= nj, 'zero-product rank')
                zero_products += 1
    return dict(triangular_sylvester=fixtures, sharp=sharp,
                zero_product_pairs=zero_products)


def count_controls():
    require(m.lower_bound(4) == 10, 'homogeneous eight-call exclusion')
    require(not any(m.allowed_counts(4, ni, 8 - ni) for ni in range(9)),
            'eight-call false positive')
    require([ni for ni in range(11) if m.allowed_counts(4, ni, 10 - ni)] == [6],
            'ten-call label rigidity')
    counts = 0
    for t in range(1, 33):
        for ni, nj in itertools.product(range(3 * t + 1), repeat=2):
            if m.allowed_counts(t, ni, nj):
                require(2 * (ni + nj) >= 5 * t, 'count theorem consequence')
                require((ni + nj - t) % 2 == 0, 'total trace parity')
                counts += 1
        require(m.allowed_counts(t, 3 * t, 0), 'direct upper-bound counts')
    return dict(accepted_count_pairs=counts, target_counts=32,
                homogeneous_four_minimum=[10, 12], ten_call_counts=[6, 4])


def compute():
    return dict(status='PASS_Q8_HOMOGENEOUS_MIXED_FLOOR',
                source_sha256=source_hashes(), arithmetic=arithmetic(),
                generic=generic_words(), direct=direct_endpoints(),
                rank_fixtures=rank_lemma(), count_controls=count_controls(),
                claim='2ni+nj>=4t; 2ni+3nj>=6t; 2n>=5t; homogeneous only',
                independent_acceptance=False, new_kappa=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', type=Path)
    args = parser.parse_args()
    result = compute()
    if args.write:
        with args.write.open('x', encoding='utf-8') as stream:
            stream.write(json.dumps(result, indent=2) + '\n')
    else:
        require(result == json.loads((ROOT / 'RESULT.json').read_text()),
                'receipt mismatch')
    print(json.dumps(result, sort_keys=True))


if __name__ == '__main__':
    main()
