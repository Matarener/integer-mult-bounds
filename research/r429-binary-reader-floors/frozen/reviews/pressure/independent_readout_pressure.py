#!/usr/bin/env python3
"""Independent B08 audit: source columns, parabolic counts, partitions, pressure.

Standard-library exact arithmetic. Does not import or execute historical producers.
Apache-2.0; prepared with substantial OpenAI Codex assistance.
"""
from collections import Counter
from fractions import Fraction as F
from hashlib import sha256
from itertools import combinations, product
import gzip
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
BASE = Path('/Users/ross/git/math')
OLD = BASE / '.research-automation/runs/kappa-changed-endpoints-20261019T0153Z'
RAW = BASE / 'integer-mult-bounds/research/bit-r438-transport-rehost/words/r438-t154.json.gz'
COMP = BASE / '.research-automation/runs/kappa-major-20261018T1330Z/bit-endpoint/BIT-FULL-COMPENSATION.json'
PRESSURE = OLD / 'budgets/OVERCOMPLETE-PRESSURE.json'
READOUT = OLD / 'bit-native-caller/READOUT-FLOOR.json'
CAP = (0, 1, 3, 6, 12, 20, 36, 63, 120)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def inverse(matrix):
    n = len(matrix)
    a = [[F(x) for x in row] + [F(i == j) for j in range(n)]
         for i, row in enumerate(matrix)]
    for j in range(n):
        k = next(k for k in range(j, n) if a[k][j])
        a[k], a[j] = a[j], a[k]
        pivot = a[j][j]
        a[j] = [x / pivot for x in a[j]]
        for k in range(n):
            if k != j:
                ratio = a[k][j]
                a[k] = [x - ratio * y for x, y in zip(a[k], a[j])]
    return [row[n:] for row in a]


def e8_capacities():
    # Doubled usual E8 coordinates, independently generated from two root types.
    roots = []
    for i, j in combinations(range(8), 2):
        for s, t in product((-2, 2), repeat=2):
            v = [0] * 8
            v[i], v[j] = s, t
            roots.append(tuple(v))
    roots.extend(v for v in product((-1, 1), repeat=8) if v.count(-1) % 2 == 0)
    require(len(roots) == len(set(roots)) == 240, '240 distinct E8 roots')
    simple = [(1, -1, -1, -1, -1, -1, -1, 1),
              (2, 2, 0, 0, 0, 0, 0, 0),
              (-2, 2, 0, 0, 0, 0, 0, 0)]
    for i in range(1, 6):
        row = [0] * 8
        row[i], row[i + 1] = -2, 2
        simple.append(tuple(row))
    inv = inverse(simple)
    supports = []
    for root in roots:
        coeff = [sum(F(root[j]) * inv[j][i] for j in range(8)) for i in range(8)]
        require(all(x.denominator == 1 for x in coeff), 'integral simple coordinates')
        require(all(x >= 0 for x in coeff) or all(x <= 0 for x in coeff),
                'simple-system positivity')
        supports.append(sum(1 << i for i, x in enumerate(coeff) if x))
    maxima = [0] * 9
    witnesses = [[] for _ in range(9)]
    for subset in range(256):
        positive_count = sum(s & ~subset == 0 for s in supports) // 2
        d = subset.bit_count()
        if positive_count > maxima[d]:
            maxima[d], witnesses[d] = positive_count, [subset]
        elif positive_count == maxima[d]:
            witnesses[d].append(subset)
    require(tuple(maxima) == CAP, 'all 256 standard parabolic capacities')
    return {'signed_roots': 240, 'standard_parabolics': 256,
            'capacities': maxima, 'maximizing_simple_subset_masks': witnesses}


def partitions_exact(total, minimum=1):
    # Enumerate by total and least part, not by rank multiplicities as the producer does.
    if total == 0:
        yield ()
    for first in range(minimum, min(8, total) + 1):
        for rest in partitions_exact(total - first, first):
            yield (first,) + rest


def screen(bounds):
    counts = []
    survivors = []
    rejected = Counter()
    digest = sha256()
    for total in range(53):
        count = 0
        for ranks in partitions_exact(total):
            count += 1
            digest.update(bytes((total, len(ranks), *ranks)))
            t = len(ranks)
            if t < 9:
                rejected['fewer_than_nine'] += 1
                continue
            for k in range(1, 10):
                if sum(CAP[r] for r in ranks[:t - 9 + k]) < bounds[k]:
                    rejected[str(k)] += 1
                    break
            else:
                survivors.append(list(ranks))
        counts.append(count)
    # A second count method: coefficients of product (1-x^r)^(-1), r=1..8.
    dp = [1] + [0] * 52
    for rank in range(1, 9):
        for total in range(rank, 53):
            dp[total] += dp[total - rank]
    require(counts == dp, 'exact-total counts agree with generating-function DP')
    return {'partition_counts_by_exact_cost': counts, 'total': sum(counts),
            'first_failed_constraint': dict(sorted(rejected.items())),
            'survivors': survivors, 'ordered_partition_sha256': digest.hexdigest()}


def log_lower(x, terms):
    require(x > 1, 'positive log argument')
    z = (x - 1) / (x + 1)
    power = z
    result = F(0)
    for denominator in range(1, 2 * terms, 2):
        result += 2 * power / denominator
        power *= z * z
    return result


def main():
    source_hashes = {str(p): sha256(p.read_bytes()).hexdigest()
                     for p in (RAW, COMP, PRESSURE, READOUT)}
    require(source_hashes[str(RAW)] == 'a353999bceac4ac957f540adfd3e5f8768297138b27132eeb83332e2ea4b1022', 'raw pin')
    require(source_hashes[str(COMP)] == '1ee06005d3b82ff592640d9aa4be2021b6de0a0b27fba5723aa06c36a6adbd20', 'compensation pin')
    raw = json.loads(gzip.decompress(RAW.read_bytes()))
    old = json.loads(PRESSURE.read_bytes())
    comp = json.loads(COMP.read_bytes())
    readout = json.loads(READOUT.read_bytes())
    operations = raw['D'] + raw['A']
    require(all(dst not in srcs and len(srcs) == len(set(srcs))
                for _, dst, srcs in operations), 'unambiguous source-column propagation')
    # Propagate each scalar source coordinate separately through 660 bit cells.
    reconstructed = [0] * 9
    for p in range(111):
        state = [0] * 660
        state[p] = 1
        for _, dst, sources in operations:
            state[dst] ^= sum(state[s] for s in sources) % 2
        for j, h in enumerate(raw['ret']):
            reconstructed[j] |= state[h] << p
    require(reconstructed == old['R'] == readout['R'] == comp['R'], 'independent source-column R')
    K = [sum(1 << j for j in indices) for indices in raw['scatter']]
    require(K == old['K'] == readout['K'] == comp['K'], 'source K')
    # Enumerate all nine-bit coefficients independently, without recursive span expansion.
    code = []
    image_K = []
    for mask in range(512):
        value = 0
        for j in range(9):
            if mask >> j & 1:
                value ^= reconstructed[j]
        code.append(value)
        image_K.append(sum(((row & mask).bit_count() % 2) << i for i, row in enumerate(K)))
    require(len(set(code)) == len(set(image_K)) == 512, 'R and K rank nine')
    weights = Counter(v.bit_count() for v in code[1:])
    support = sum(any(row >> p & 1 for row in reconstructed) for p in range(111))
    require(min(weights) == 48 and support == 111, 'distance and active coordinate count')
    require({str(k): v for k, v in sorted(weights.items())} == old['code_weights'], 'weight census')
    bounds = [0] + [(48 * (2 ** k - 1) + 2 ** (k - 1) - 1) // 2 ** (k - 1)
                    for k in range(1, 9)] + [111]
    require(bounds == old['generalized_support_lower_bounds'], 'generalized support bounds')
    census = screen(bounds)
    require(census['total'] == 340260 and census['survivors'] == [[4] * 13], 'independent full census')
    require(6 * CAP[4] == bounds[2] and 13 * CAP[4] > 111, 'survivor equality contradiction')
    weak_bounds = [0] + [(44 * (2 ** k - 1) + 2 ** (k - 1) - 1) // 2 ** (k - 1)
                         for k in range(1, 9)] + [111]
    weakened = screen(weak_bounds)
    require(weakened['survivors'] != census['survivors'], 'distance sensitivity')
    bulk = {int(k): v for k, v in comp['forward']['profile'].items()}
    bulk[1] -= 111
    require(bulk == {1: 1295, 2: 1342, 3: 79, 4: 44, 5: 93, 6: 11, 7: 9}, 'literal bulk profile')
    mass = sum(r * c for r, c in bulk.items())
    require(mass == 4986 == 14 * 111 + 8 * 429, 'literal bulk mass')
    per_rank = {str(r): str(F(3, 500) * r * c * log_lower(F(22, r), 32))
                for r, c in bulk.items()}
    lower = sum(map(F, per_rank.values()), F(0))
    require(lower == F(old['seed_consequence']['pressure_strict_lower']), 'independent rational pressure')
    require(lower > F('72.34417105') > 63, 'strict rational threshold')
    require(lower < 222 - 3 * 49 == 75, 'old floor does not supply this witness')
    exact_claims = {'status': 'PASS_INDEPENDENT_B08_SOURCE_ONLY_53_AND_FIXED_PRESSURE',
                    'scientific_pin': '20ecf2891d80b5acf18d980b2164fb44ea7faa90',
                    'sources': source_hashes, 'source_R': reconstructed,
                    'code_weights': dict(sorted(weights.items())), 'code_dimension': 9,
                    'active_coordinates': support, 'distance': min(weights),
                    'e8_parabolics': e8_capacities(), 'support_bounds': bounds,
                    'partition_census': census, 'distance44_control_survivors': len(weakened['survivors']),
                    'survivor_disjoint_union_required': 156,
                    'bulk_profile': bulk, 'bulk_mass': mass,
                    'pressure_per_rank_lower': per_rank, 'pressure_lower_exact': str(lower),
                    'pressure_lower_decimal_floor_8_places': '{}.{:08d}'.format(*divmod(lower.numerator * 10**8 // lower.denominator, 10**8)),
                    'fixed_credit_after_reader_floor': 63,
                    'scope': 'Binary separate materialized readers and a fixed complete-invoice deficit premise; no native supplier impossibility, no attainment, no new kappa.'}
    (HERE / 'INDEPENDENT-RESULT.json').write_text(json.dumps(exact_claims, indent=2, sort_keys=True) + '\n')
    print(exact_claims['status'])
    print('340260 partitions, sole relaxed survivor 13 rank4; 256 parabolics; pressure > 72.34417105 > 63')


if __name__ == '__main__':
    main()
