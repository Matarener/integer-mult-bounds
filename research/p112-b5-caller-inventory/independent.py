"""Separate count-vector/filter and small-first assignment reconstruction.

Imports no primary or predecessor executable. Apache-2.0; Codex assistance.
"""
from pathlib import Path
from itertools import combinations, product
import hashlib
import json

HERE = Path(__file__).resolve().parent
CAP = (2, 4, 8, 12, 20, 36)
TIGHT = (2, 4, 8, 12, 20, 32)


def check(condition, message):
    if not condition:
        raise ValueError(message)


def subsets(items, k):
    return combinations(items, k)


def vectors(n, k=6):
    if k == 1:
        yield (n,)
    else:
        for first in range(n + 1):
            for tail in vectors(n - first, k - 1):
                yield (first,) + tail


def accepts(xs):
    n = len(xs)
    if sum(xs) >= 30:
        return False
    for d, threshold in enumerate((53, 78, 92, 100, 106), 1):
        ys = xs[:n - 5 + d]
        total = sum(CAP[x] for x in ys)
        special = sum(TIGHT[x] for x in ys)
        if d <= 2:
            if special < threshold and total < (73 if d == 1 else 82):
                return False
        elif total < threshold:
            return False
    small = xs[:n - 5]
    if sum(CAP[x] for x in small) >= 53:
        return True
    weights = [x + 2 for x in small]
    if sum(weights) <= 7:
        return False
    sums = {0}
    for w in weights:
        sums |= {s + w for s in tuple(sums)}
    return not any(s <= 6 and sum(weights) - s <= 6 for s in sums)


def applications(xs, name):
    n = len(xs)
    indices = set(range(n))
    results = []
    minima = []
    if name in ('rank6_29', 'rank5_47', 'six_support20_30'):
        endpoint_n = 6 if name.startswith('six') else 3
        maximum = 3 if name == 'rank5_47' else 4
        cut = {'rank6_29': 29, 'rank5_47': 47, 'six_support20_30': 30}[name]
        for small in subsets(range(n), n - 6):
            cost = sum(CAP[xs[i]] for i in small)
            available = sorted(indices.difference(small))
            for endpoints in subsets(available, endpoint_n):
                if max(xs[i] for i in endpoints) > maximum:
                    continue
                minima.append(cost)
                if cost <= cut:
                    results.append(dict(small=list(small), endpoints=list(endpoints), deleted=sorted(indices.difference(small).difference(endpoints)), common_cap=cost, surviving_code_dimension=5 - (6 - endpoint_n)))
    else:
        for basis in subsets(range(n), n - 5):
            cost = sum(CAP[xs[i]] for i in basis)
            minima.append(cost)
            if cost >= 53:
                continue
            if name.startswith('common'):
                if cost <= {'common23': 23, 'common24': 24}[name]:
                    results.append(dict(basis=list(basis), common_cap=cost, quotient_dimension=n - 5, required_directions=5))
            else:
                for cut_n in range(len(basis) + 1):
                    for cut_set in subsets(basis, cut_n):
                        cut_cost = sum(CAP[xs[i]] for i in cut_set)
                        if cut_cost > 2:
                            continue
                        rest = sorted(set(basis).difference(cut_set))
                        for a_n in range(len(rest) + 1):
                            for a in subsets(rest, a_n):
                                b = set(rest).difference(a)
                                if sum(xs[i] + 2 for i in a) > 6 or sum(xs[i] + 2 for i in b) > 6:
                                    continue
                                roles = [2 if i in cut_set else 0 if i in a else 1 for i in basis]
                                results.append(dict(basis=list(basis), roles=roles, basis_cap=cost, cut_cap=cut_cost, required_directions=5, span_bound=4))
    return results, min(minima, default=None)


def main():
    receipt = json.loads((HERE / 'RESULT.json').read_text())
    source = (HERE / 'SOURCES.json').read_bytes()
    check(hashlib.sha256(source).hexdigest() == receipt['source_manifest_sha256'], 'source binding differs')
    attempts = 0
    for cell in receipt['cells']:
        t = cell['cell'][1]
        candidates = []
        for n in range(5, 6 + t):
            for counts in vectors(n):
                candidates.append(tuple(x for x, count in enumerate(counts) for _ in range(count)))
        survivors = sorted(xs for xs in candidates if accepts(xs))
        recorded = sorted(tuple(w - 2 for w in row['weights']) for row in cell['rows'])
        check(survivors == recorded, 'full historical domain mismatch')
        check(len(candidates) == cell['domain_multisets'], 'domain count differs')
        for row in cell['rows']:
            xs = tuple(w - 2 for w in row['weights'])
            check(row['strict_excess_deficit'] == 30 - sum(xs), 'strict deficit differs')
            found = []
            for name, expected in row['attempts'].items():
                results, minimum = applications(xs, name)
                check(len(results) == expected['successful_assignments'], 'assignment count: ' + name)
                check(minimum == expected['minimum_capacity_sum'], 'capacity minimum: ' + name)
                check(expected['witness'] in results if results else expected['witness'] is None, 'literal witness: ' + name)
                if results:
                    found.append(name)
                attempts += 1
            check(row['primary'] == (found[0] if found else None), 'primary attribution differs')
        check(cell['certified'] == sum(row['primary'] is not None for row in cell['rows']), 'coverage count differs')
    interface = receipt['remaining_interface']
    costs = sorted(sum(CAP[interface['weights'][i] - 2] for i in B) for B in combinations(range(11), 6))
    check(len(costs) == 462 and costs[0] == 30, 'remaining caller basis minimum')
    check(30 < 53 and 11 - 6 == 5, 'remaining caller quotient')
    check(receipt['cells'][0]['uncertified'] == [] and receipt['cells'][1]['uncertified'] == [interface['weights']], 'remaining rows differ')
    print('PASS_P112_B5_INDEPENDENT', attempts, 'rule/row combinations; 462 basis subsets')


if __name__ == '__main__':
    main()
