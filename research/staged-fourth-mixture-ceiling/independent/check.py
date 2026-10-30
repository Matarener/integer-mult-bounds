"""Independent exact pooled-bin lower bound for the PR4088 frozen interface.

OpenAI GPT-6.1 Sol, substantial AI assistance, 2026-10-19.  Apache-2.0.
This imports neither the source pricing engine nor any solver.  The candidate
symbolic dual was supplied by the owner-allocation specialist; its coverage and
all numerical signs are checked here independently.
"""
from __future__ import annotations

import argparse
import ast
from collections import Counter
from fractions import Fraction as Q
from functools import lru_cache
import gzip
import hashlib
import json
from pathlib import Path

SCALE = 10**90
CALLS = 3240
STOCK = 896 * 360
THREE = {1: 2487, 2: 713, 3: 224, 4: 102, 5: 20, 8: 8}
LOCAL_DELTA = {1: 2, 3: 3, 4: -3}
WIDTHS = (5, 6, 7, 8, 9)
CAPACITIES = (8, 16, 32, 48)


def need(test, message):
    if not test:
        raise ValueError(message)


def read(path):
    data = path.read_bytes()
    return json.loads(gzip.decompress(data) if path.suffix == '.gz' else data)


def rank(vectors):
    """GF(2) column rank, with no subspace library or source-code imports."""
    rows = {}
    for v in vectors:
        need(type(v) is int and 0 <= v < 512, 'invalid binary vector')
        while v:
            pivot = v.bit_length() - 1
            if pivot in rows:
                v ^= rows[pivot]
            else:
                rows[pivot] = v
                break
    return len(rows)


def source_accounting(source):
    """Scan actual final/entry subspaces and all distinct original child ports."""
    paths = ['owner/TEMPLATE.json.gz', 'owner/ORDER.json', 'vendor/exact_root.py', 'price.py', 'RESULT.json']
    order = read(source / 'owner/ORDER.json')
    seen = {tuple(call): t for t, call in enumerate(order)}
    need(len(order) == len(seen) == CALLS, 'actual unique call count')
    stages = {s for s, _ in seen}
    replicas = {r for _, r in seen}
    need(stages == set(range(9)) and replicas == set(range(360)), 'actual T360 order domain')
    need(set(seen) == {(s, r) for s in stages for r in replicas}, 'all source call pairs')
    need(all(seen[s, r] < seen[s + 1, r] for r in replicas for s in range(8)), 'per-replica source order')
    # Only historical *capacity* records are used below. Old embedded template
    # replica/call/stock fields (including its replicas=37) are deliberately unused.
    engine = ast.parse((source / 'vendor/exact_root.py').read_text())
    constants = {}
    for statement in engine.body:
        if isinstance(statement, ast.Assign):
            for target in statement.targets:
                if isinstance(target, ast.Name) and target.id in ('COPIES', 'REPLICAS'):
                    constants[target.id] = ast.literal_eval(statement.value)
    need(constants == {'COPIES': CALLS, 'REPLICAS': len(replicas)}, 'source moment replication constants')
    signed = [statement for statement in engine.body if isinstance(statement, ast.FunctionDef) and statement.name == 'signed']
    expected_signed = ast.parse('def signed(profile): return {**profile, 73: -896*REPLICAS}').body[0]
    need(len(signed) == 1 and ast.dump(signed[0], include_attributes=False) == ast.dump(expected_signed, include_attributes=False), 'source ambient width and stock convention')
    inventories = {}
    changed = {}
    for tag in ('base', 'extra'):
        words = {}
        for variant in ('THREE', 'FOUR'):
            rel = f'inputs/{variant}-{tag}.json.gz'
            paths.append(rel)
            word = read(source / rel)
            live_helpers = sorted(set(range(224, 704)) - set(word['removed']))
            need(len(live_helpers) == 408, 'actual helper count')
            widths = {}
            for helper in live_helpers:
                terminal = word['helper_final'].get(str(helper), [1 << j for j in range(9)])
                entry = word['start_extra'].get(str(helper), [])
                need(rank(terminal + entry) == rank(terminal), 'entry not contained in terminal')
                widths[helper] = rank(terminal) - rank(entry)
            inv = dict(sorted(Counter(widths.values()).items()))
            need(inv == {int(k): v for k, v in word['report']['width_inventory'].items()}, 'declared width inventory')
            profile = {int(k): v for k, v in word['report']['local_profile'].items()}
            expected = dict(THREE)
            if variant == 'FOUR':
                for r, n in LOCAL_DELTA.items():
                    expected[r] = expected.get(r, 0) + n
            need(profile == expected, 'local profile differs from stipulated source invoice')
            inventories[f'{variant}-{tag}'] = inv
            words[variant] = widths
        need(set(words['THREE']) == set(words['FOUR']), 'changed helper identities')
        changed[tag] = {str(h): [words['THREE'][h], words['FOUR'][h]]
                        for h in words['THREE'] if words['THREE'][h] != words['FOUR'][h]}
        need(changed[tag] == {'601': [8, 7]}, 'unexpected width change')
    need(inventories['THREE-base'] == inventories['THREE-extra'] == {5: 28, 6: 18, 7: 56, 8: 93, 9: 213}, 'three inventory')
    need(inventories['FOUR-base'] == inventories['FOUR-extra'] == {5: 28, 6: 18, 7: 57, 8: 92, 9: 213}, 'four inventory')

    template = read(source / 'owner/TEMPLATE.json.gz')
    bins_by_port = {}
    for child in template['idle_children']:
        key = (child['child'], child['port'])
        need(key not in bins_by_port, 'duplicate original child port')
        bins_by_port[key] = child['rank']
    need(set(bins_by_port) == {(c, p) for c in range(18) for p in range(112)}, 'all original child ports')
    need(all(bins_by_port[c, p] == bins_by_port[c, 0] for c in range(18) for p in range(112)), 'port-dependent capacities')
    bins = Counter()
    for capacity in bins_by_port.values():
        bins[capacity] += len(replicas)
    bins = dict(sorted(bins.items()))
    need(bins == {8: 241920, 16: 161280, 32: 161280, 48: 161280}, 'bin inventory')
    demands = {w: CALLS * n for w, n in inventories['THREE-base'].items()}
    local = {r: CALLS * n for r, n in THREE.items()}
    capacity_mass = sum(c * n for c, n in bins.items())
    width_mass = sum(w * n for w, n in demands.items())
    local_mass = sum(r * n for r, n in local.items())
    need((capacity_mass, width_mass, local_mass) == (17418240, 10695240, 16708680), 'mass accounting')
    need(local_mass + capacity_mass - width_mass == 65088 * 360, 'complete paid rank mass')
    hashes = {rel: hashlib.sha256((source / rel).read_bytes()).hexdigest() for rel in paths}
    return bins, demands, local, {'helper_inventories': inventories, 'changed_helper': changed,
        'bins': bins, 'demands_at_x0': demands, 'capacity_mass': capacity_mass,
        'hosted_width_mass': '10695240 - x', 'local_rank_mass': '16708680 - x',
        'residual_rank_mass': '6723000 + x', 'complete_rank_mass': 23431680,
        'source_calls': len(order), 'source_replicas': len(replicas),
        'stock': STOCK, 'ambient_width': 73,
        'historical_template_replication_fields': 'unused; only distinct (child,port,rank) capacity records are used',
        'source_sha256': hashes}


@lru_cache(None)
def log_enclosure(r):
    """Bounds scaled by SCALE; exact positive atanh series and geometric tail."""
    need(type(r) is int and r >= 1, 'log argument')
    if r == 1:
        return (0, 0)

    def log_unit(y):
        need(1 <= y <= 2, 'range reduction')
        t = (y - 1) / (y + 1)
        term = t
        partial = Q(0)
        count = 108
        for j in range(count):
            partial += term / (2 * j + 1)
            term *= t * t
        lower = 2 * partial
        upper = lower + 2 * term / ((2 * count + 1) * (1 - t * t))
        return lower, upper

    exponent = r.bit_length() - 1
    yl, yh = log_unit(Q(r, 1 << exponent))
    tl, th = log_unit(Q(2))
    lower, upper = yl + exponent * tl, yh + exponent * th
    return ((lower * SCALE).numerator // (lower * SCALE).denominator,
            -(-(upper * SCALE).numerator // (upper * SCALE).denominator))


def ceil_div(n, d):
    return -(-n // d)


def exp_neg_enclosure(zlo, zhi):
    """Exact fixed-point interval Taylor arithmetic for exp(-z), 0<=z<=1.

    Each positive term is propagated outwards.  Partial sum through degree 64
    is an upper bound, and subtracting the interval upper degree-65 term gives
    a lower bound by the alternating-series theorem.
    """
    need(0 <= zlo <= zhi <= SCALE, 'exponential range')
    tlo = thi = SCALE
    slo = shi = SCALE
    for j in range(1, 65):
        tlo = tlo * zlo // (SCALE * j)
        thi = ceil_div(thi * zhi, SCALE * j)
        if j % 2:
            slo -= thi
            shi -= tlo
        else:
            slo += tlo
            shi += thi
    next_hi = ceil_div(thi * zhi, SCALE * 65)
    return slo - next_hi, shi


def power_enclosure(r, k):
    """Enclose r^(1-k) on the SCALE lattice.  No floating-point functions."""
    need(0 <= k <= Q(1, 100), 'checked k domain is [0,0.01]')
    if r == 0:
        return (0, 0)
    if r == 1 or k == 0:
        return (r * SCALE, r * SCALE)
    ll, lh = log_enclosure(r)
    zlo = ll * k.numerator // k.denominator
    zhi = ceil_div(lh * k.numerator, k.denominator)
    lo, hi = exp_neg_enclosure(zlo, zhi)
    return r * lo, r * hi


def vec(*terms):
    out = Counter()
    for coefficient, source in terms:
        for rank_, value in source.items():
            out[rank_] += Q(coefficient) * value
    return {r: v for r, v in out.items() if v}


def h(r):
    return {r: Q(1)} if r else {}


def dual_vectors():
    """Nominated owner dual, reconstructed as exact sparse linear forms in H_r."""
    d = dict(LOCAL_DELTA)
    v9 = vec((Q(1, 5), h(3)), (-Q(1, 5), h(48)))
    v7 = vec((Q(1, 2), v9), (-Q(1, 2), h(5)))
    v8 = vec((1, v7), (1, d))
    v6 = vec((1, v7), (-1, d))
    v5 = vec((-1, h(5)))
    u8 = vec((-1, v8))
    u16 = vec((-1, v7), (-1, v9))
    u32 = vec((1, h(5)), (-3, v9))
    return {8: u8, 16: u16, 32: u32, 48: h(48)}, {5: v5, 6: v6, 7: v7, 8: v8, 9: v9}


def patterns(capacity):
    """Exhaust all five nonnegative integer counts, including the empty pattern."""
    def walk(index, room, counts):
        if index == len(WIDTHS):
            yield tuple(counts), room
            return
        w = WIDTHS[index]
        for count in range(room // w + 1):
            yield from walk(index + 1, room - count * w, counts + [count])
    yield from walk(0, capacity, [])


def eval_vec(form, power):
    lower = upper = Q(0)
    for r, coefficient in form.items():
        lo, hi = power[r]
        if coefficient > 0:
            lower += coefficient * lo
            upper += coefficient * hi
        else:
            lower += coefficient * hi
            upper += coefficient * lo
    return lower / SCALE, upper / SCALE


def check_dual(bins, demands, local, k, *, tamper=None):
    power = {r: power_enclosure(r, k) for r in range(74)}
    u, v = dual_vectors()
    if tamper == 'wrong_bin_sign':
        u[8] = vec((-1, u[8]))
    if tamper == 'raise_u48':
        u[48] = vec((1, u[48]), (Q(1, 10**12), h(1)))
    need(vec((1, LOCAL_DELTA), (1, v[7]), (-1, v[8])) == {}, 'global x cancellation')
    total_patterns = 0
    exact_ties = 0
    pattern_counts = {}
    minimum = None
    minimum_pattern = None
    ties = {}
    for capacity in CAPACITIES:
        patterns_here = list(patterns(capacity))
        pattern_counts[capacity] = len(patterns_here)
        ties[capacity] = []
        for counts, remainder in patterns_here:
            slack = vec((1, h(remainder)), (-1, u[capacity]),
                        *((-n, v[w]) for w, n in zip(WIDTHS, counts)))
            total_patterns += 1
            if not slack:
                exact_ties += 1
                ties[capacity].append(list(counts))
            else:
                lo, hi = eval_vec(slack, power)
                need(lo > 0, f'dual pattern not strictly feasible: c={capacity}, n={counts}, slack=[{lo},{hi}]')
                if minimum is None or lo < minimum:
                    minimum = lo
                    minimum_pattern = [capacity, list(counts), remainder]
    need(total_patterns == 841, 'incomplete integer-pattern coverage')
    bound_form = vec((1, local), *((n, u[c]) for c, n in bins.items()),
                     *((n, v[w]) for w, n in demands.items()))
    ideal = dict(local)
    for r, n in LOCAL_DELTA.items():
        ideal[r] = ideal.get(r, 0) + 1080 * n
    for r, n in {3: 22788, 5: 1620, 48: 138492}.items():
        ideal[r] = ideal.get(r, 0) + n
    need(all(0 < r < 73 and n > 0 for r, n in ideal.items()), 'strict normalized-moment monotonicity premises')
    need(bound_form == {r: Q(n) for r, n in ideal.items()}, 'dual does not equal nominated ideal histogram')
    bound_minus_stock = vec((1, bound_form), (-STOCK, h(73)))
    lo, hi = eval_vec(bound_minus_stock, power)
    return {'target_k': str(k), 'pattern_counts': pattern_counts, 'total_patterns': total_patterns,
            'exact_ties': exact_ties, 'active_count_vectors_widths5to9': ties,
            'minimum_nonidentity_slack_lower': str(minimum), 'minimum_pattern': minimum_pattern,
            'ideal_profile': ideal, 'lower_bound_minus_stock_interval': [str(lo), str(hi)],
            'lower_bound_minus_stock_decimal': [decimal_str(lo), decimal_str(hi)],
            'strict_all_x_rejection': lo > 0}


def decimal_str(x, digits=30):
    negative = x < 0
    x = abs(Q(x))
    scale = 10**digits
    q = x.numerator * scale // x.denominator
    whole, part = divmod(q, scale)
    return ('-' if negative else '') + str(whole) + '.' + str(part).zfill(digits)


def check_majorization():
    difference = {3: -3, 5: 5, 16: 1, 32: 2, 48: -2}
    sums = {t: sum(n * min(r, t) for r, n in difference.items()) for t in sorted(difference)}
    need(sums == {3: 9, 5: 21, 16: 32, 32: 32, 48: 0}, 'literal versus ideal truncated masses')
    need(sum(r * n for r, n in difference.items()) == 0, 'comparison rank masses differ')
    return {'literal_minus_ideal': difference, 'truncated_rank_sums': sums,
            'conclusion': 'literal moment strictly exceeds ideal moment for every 0 < k < 1'}


def check_primal(bins, demands):
    """An exact integral pooled witness, with chronology/family conditions erased."""
    rows = [
        (8, (0, 0, 0, 1, 0), 241920),
        (16, (0, 0, 1, 0, 1), 161280),
        (32, (0, 0, 0, 0, 3), 1620),
        (32, (0, 0, 2, 0, 2), 10620),
        (32, (0, 1, 0, 1, 2), 58320),
        (32, (1, 0, 0, 0, 3), 90720),
        (48, (0, 0, 0, 0, 0), 138492),
        (48, (0, 0, 0, 0, 5), 22788),
    ]
    observed_bins = Counter()
    observed_demands = Counter()
    idle = Counter()
    u, v = dual_vectors()
    for capacity, counts, multiplicity in rows:
        need(type(multiplicity) is int and multiplicity >= 0, 'primal multiplicity')
        remainder = capacity - sum(w * n for w, n in zip(WIDTHS, counts))
        need(remainder >= 0, 'primal capacity')
        need(vec((1, h(remainder)), (-1, u[capacity]),
                 *((-n, v[w]) for w, n in zip(WIDTHS, counts))) == {}, 'primal pattern not symbolically tight')
        observed_bins[capacity] += multiplicity
        for w, n in zip(WIDTHS, counts):
            observed_demands[w] += multiplicity * n
        if remainder:
            idle[remainder] += multiplicity
    need(dict(observed_bins) == bins, 'primal bin counts')
    expected_demands = dict(demands)
    expected_demands[7] += 1080
    expected_demands[8] -= 1080
    need(dict(observed_demands) == expected_demands, 'primal item counts')
    need(dict(idle) == {3: 22788, 5: 1620, 48: 138492}, 'primal idle invoice')
    # With all nonidentity pattern slacks strict, every optimizer uses precisely
    # the eight active patterns. The cap8 patterns consume B8 width8s; width6
    # demand forces the only other width8 pattern count. Thus x is unique.
    forced_x = demands[8] - bins[8] - demands[6]
    need(forced_x == 1080, 'stationary mixture not forced by tight patterns')
    return {'x': 1080, 'rows': [[c, list(n), z] for c, n, z in rows], 'idle': dict(idle),
        'forced_x_identity': 'x = N8(0) - B8 - N6 = 1080',
        'scope': 'Integral pooled patterns only; chronology, family constraints and helper identities erased.'}


def check_literal_root(source, local):
    record = read(source / 'RESULT.json')
    literal = {int(r): n for r, n in record['profile'].items()}
    expected = dict(local)
    for r, n in LOCAL_DELTA.items():
        expected[r] = expected.get(r, 0) + 1080 * n
    for r, n in {3: 22785, 5: 1625, 16: 1, 32: 2, 48: 138490}.items():
        expected[r] = expected.get(r, 0) + n
    need(literal == expected, 'literal source result invoice')
    difference = vec((1, literal), (-STOCK, h(73)))
    lower, upper = Q(record['root_lower']), Q(record['root_upper'])
    lower_sign = eval_vec(difference, {r: power_enclosure(r, lower) for r in difference})
    upper_sign = eval_vec(difference, {r: power_enclosure(r, upper) for r in difference})
    need(lower_sign[1] < 0 and upper_sign[0] > 0, 'literal source root bracket not independently certified')
    ideal_lower = Q('0.001730980255989036959962')
    ideal_upper = Q('0.001730980255989036959963')
    return {'literal_root': [str(lower), str(upper)],
        'independent_literal_endpoint_sign_intervals': [[str(x) for x in z] for z in (lower_sign, upper_sign)],
        'pooled_ceiling_minus_literal_root': [str(ideal_lower - upper), str(ideal_upper - lower)],
        'pooled_ceiling_minus_literal_root_decimal': [decimal_str(ideal_lower - upper), decimal_str(ideal_upper - lower)],
        'limits': 'A bound on the retained complete-moment root; no all-size construction or outer transfer established.'}


def check_dual_over_root_bracket():
    lower = Q('0.001730980255989036959962')
    upper = Q('0.001730980255989036959963')
    # H_r(k)=r*exp(-k log r) decreases in k, with r=0,1 constant.
    power = {r: (power_enclosure(r, upper)[0], power_enclosure(r, lower)[1]) for r in range(49)}
    u, v = dual_vectors()
    ties = strict = 0
    minimum = None
    for capacity in CAPACITIES:
        for counts, remainder in patterns(capacity):
            slack = vec((1, h(remainder)), (-1, u[capacity]),
                        *((-n, v[w]) for w, n in zip(WIDTHS, counts)))
            if not slack:
                ties += 1
            else:
                lo, _ = eval_vec(slack, power)
                need(lo > 0, 'uniform bracket dual feasibility')
                strict += 1
                minimum = lo if minimum is None else min(minimum, lo)
    need((ties, strict) == (8, 833), 'uniform bracket pattern count')
    return {'k_interval': [str(lower), str(upper)], 'identities': ties, 'strict_patterns': strict,
            'minimum_nonidentity_slack_lower': str(minimum),
            'conclusion': 'The pooled optimum profile and unique mix x=1080 hold throughout this entire root bracket.'}


def controls(bins, demands, local, k):
    rejected = []
    for name in ('wrong_bin_sign', 'raise_u48'):
        try:
            check_dual(bins, demands, local, k, tamper=name)
        except ValueError:
            rejected.append(name)
        else:
            raise ValueError('control not rejected: ' + name)
    bad = dict(bins)
    bad[48] -= 1
    try:
        check_dual(bad, demands, local, k)
    except ValueError:
        rejected.append('missing_capacity48_bin')
    else:
        raise ValueError('missing bin control not rejected')
    need(power_enclosure(0, Q(0)) == (0, 0), 'zero power')
    need(all(power_enclosure(r, Q(0)) == (r * SCALE, r * SCALE) for r in range(74)), 'k=0 exact powers')
    # A nonzero logarithm/exponential control with an exactly known result:
    # (2^100)^(1-1/100)=2^99. This exercises the full nontrivial enclosure path.
    lo, hi = power_enclosure(2**100, Q(1, 100))
    need(lo <= (2**99) * SCALE <= hi, 'nontrivial perfect-power enclosure')
    return rejected + ['exact_integer_powers_at_k0', 'nontrivial_perfect_power',
                       'symbolic_x_cancellation', 'all_empty_patterns_included']


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', type=Path, default=Path(__file__).resolve().parent.parent / 'source4088')
    parser.add_argument('--target-k', type=Q)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--controls', action='store_true')
    args = parser.parse_args()
    bins, demands, local, accounts = source_accounting(args.source)
    bracket_lower = check_dual(bins, demands, local, Q('0.001730980255989036959962'))
    bracket_upper = check_dual(bins, demands, local, Q('0.001730980255989036959963'))
    need(Q(bracket_lower['lower_bound_minus_stock_interval'][1]) < 0 < Q(bracket_upper['lower_bound_minus_stock_interval'][0]), 'strict independent pooled root bracket')
    result = {'status': 'PASS_INDEPENDENT_POOLED_CEILING', 'source': str(args.source),
              'accounting': accounts, 'majorization': check_majorization(),
              'pooled_primal': check_primal(bins, demands),
              'comparison': check_literal_root(args.source, local),
              'uniform_root_bracket': check_dual_over_root_bracket(),
              'bracket_checks': {'lower': bracket_lower, 'upper': bracket_upper}}
    if args.target_k is not None:
        result['dual'] = check_dual(bins, demands, local, args.target_k)
    if args.controls:
        result['controls'] = controls(bins, demands, local, args.target_k or Q('0.001730980255989036959963'))
    if args.output:
        args.output.write_text(json.dumps(result, sort_keys=True, indent=2) + '\n')
    print(json.dumps({'status': result['status'], 'pooled_optimal_mix': 1080,
        'root_bracket': ['0.001730980255989036959962', '0.001730980255989036959963'],
        'patterns': 841,
        **({'dual': {k: v for k, v in result['dual'].items() if k not in ('active_count_vectors_widths5to9',)}} if 'dual' in result else {})}, sort_keys=True))


if __name__ == '__main__':
    main()
