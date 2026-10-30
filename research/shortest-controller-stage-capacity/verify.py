#!/usr/bin/env python3
"""Check exact controls and complete prices for the written rank-cut proof.

Ali Romman, with substantial OpenAI Codex assistance. Apache-2.0.
The simplex formulas and literal word are due to Cinna Davis.
"""
import argparse
from collections import Counter
from decimal import Decimal, localcontext
from fractions import Fraction
import hashlib
from itertools import combinations, product
import json
from pathlib import Path
from types import ModuleType


PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]


def need(condition, message):
    if not condition:
        raise ValueError(message)


def authenticate():
    manifest = json.loads((PACKAGE / 'SOURCES.json').read_text())
    count = 0
    for row in manifest['files']:
        if row['usage'] != 'input':
            continue
        raw = (ROOT / row['path']).read_bytes()
        need(hashlib.sha256(raw).hexdigest() == row['sha256'],
             'Source SHA256 mismatch: ' + row['path'])
        blob = b'blob ' + str(len(raw)).encode() + b'\0' + raw
        need(hashlib.sha1(blob).hexdigest() == row['git_blob'],
             'Source Git blob mismatch: ' + row['path'])
        count += 1
    return count


def rank(rows):
    pivots = {}
    for value in rows:
        while value:
            p = value.bit_length()-1
            if p not in pivots:
                pivots[p] = value
                break
            value ^= pivots[p]
    return len(pivots)


def eye(n):
    return [1 << i for i in range(n)]


def add(a, b):
    return [x ^ y for x, y in zip(a, b)]


def mul(a, b):
    out = []
    for row in a:
        value = 0
        while row:
            low = row & -row
            value ^= b[low.bit_length()-1]
            row ^= low
        out.append(value)
    return out


def outer(u, v, n):
    return [v if (u >> i) & 1 else 0 for i in range(n)]


def dot(v, u):
    return (u & v).bit_count() % 2


def apply(a, u):
    return sum(dot(row, u) << i for i, row in enumerate(a))


def inverse(a):
    n = len(a)
    rows = [r | (1 << (n+i)) for i, r in enumerate(a)]
    for j in range(n):
        pivot = next((i for i in range(j, n) if (rows[i] >> j) & 1), None)
        need(pivot is not None, 'Singular constant endpoint')
        rows[j], rows[pivot] = rows[pivot], rows[j]
        for i in range(n):
            if i != j and (rows[i] >> j) & 1:
                rows[i] ^= rows[j]
    return [row >> n for row in rows]


def submatrix(a, row_ids, column_ids):
    return [sum(((a[i] >> j) & 1) << t for t, j in enumerate(column_ids))
            for i in row_ids]


def factor_rank_one(a):
    v = next(row for row in a if row)
    need(all(row in (0, v) for row in a), 'Rank-one factor')
    u = sum(bool(row) << i for i, row in enumerate(a))
    need(dot(v, u) == 0, 'Nilpotent factor')
    return u, v


def word(gates, labels, omit_query=None):
    """Multiply sparse group-algebra coefficient matrices directly."""
    n = len(gates[0][1])
    result = {0: eye(n)}
    for i, ((p, r), label) in enumerate(zip(gates, labels)):
        terms = {0: eye(n)} if label is None else {0: add(eye(n), p), label: p}
        if i != omit_query:
            key = 1 if label is None else label ^ 1
            terms[key] = add(terms.get(key, [0]*n), r)
        changed = {}
        for left, a in terms.items():
            for right, b in result.items():
                key = left ^ right
                changed[key] = add(changed.get(key, [0]*n), mul(a, b))
        result = {key: value for key, value in changed.items() if any(value)}
    return result


def endpoint(coefficients):
    n = len(next(iter(coefficients.values())))
    need(all(key & 1 for key in coefficients), 'Missing central query')
    constant = [0]*n
    for value in coefficients.values():
        constant = add(constant, value)
    inv = inverse(constant)
    projections = {key: mul(value, inv) for key, value in coefficients.items()}
    for a, b in product(projections, repeat=2):
        want = projections[a] if a == b else [0]*n
        need(mul(projections[a], projections[b]) == want,
             'Independent coefficient images')
    degrees = Counter()
    for key, value in projections.items():
        degrees[key.bit_count()-1] += rank(value)
    need(sum(degrees.values()) == n, 'All independent fields are retained')
    return dict(sorted(degrees.items()))


def query_frame(gates):
    n = len(gates[0][1])
    tail, undo = eye(n), eye(n)
    us, vs, ps = [], [], []
    for p, nilpotent in reversed(gates):
        r = mul(mul(tail, nilpotent), undo)
        u, v = factor_rank_one(r)
        us.append(u)
        vs.append(v)
        ps.append(mul(mul(tail, p), undo))
        constant = add(eye(n), nilpotent)
        tail = mul(tail, constant)
        undo = mul(constant, undo)
    us.reverse()
    vs.reverse()
    ps.reverse()
    total = [0]*n
    for u, v in zip(us, vs):
        total = add(total, outer(u, v, n))
    need(total == eye(n), 'Whole-word query frame sums to identity')
    gram = [sum(dot(v, u) << j for j, u in enumerate(us)) for v in vs]
    need(mul(gram, gram) == gram and rank(gram) == n, 'Query Gram projection')
    need(all(not ((row >> i) & 1) for i, row in enumerate(gram)), 'Zero Gram diagonal')
    return gram, ps


def operator_controls():
    source = ROOT / 'research/productive-controller-basis-search/algebra.py'
    a = ModuleType('credited_controller_algebra')
    exec(compile(source.read_bytes(), str(source), 'exec'), a.__dict__)
    ids = [7, 0, 39, 832, 384]
    gates = [(a.FULL if (24 >> i) & 1 else a.THIN)[g] for i, g in enumerate(ids)]
    labels = [None, None, None, 16, 32]
    direct = word(gates, labels)
    literal = a.coefficients(a.literal(24, ids))
    need(direct == literal, 'Two literal interpreters agree on the sharp word')
    need(endpoint(direct) == {0: 2, 2: 2}, 'Independent main ranks 1,1,17,17')
    gram, _ = query_frame(gates)
    need(gram == [31 ^ (1 << i) for i in range(5)], 'Sharp shortest-query Gram')
    try:
        endpoint(word(gates, labels, omit_query=1))
    except ValueError:
        pass
    else:
        raise ValueError('Deleted query escaped the endpoint control')
    pairs = [(0, 1), (1, 0), (0, 1), (2, 3), (3, 2), (2, 3)]
    gates = [a.FULL[a.elementary(*pair)] for pair in pairs]
    independent = word(gates, [1 << (i+1) for i in range(6)])
    literal = a.coefficients(a.literal(63, [a.elementary(*p) for p in pairs]))
    need(independent == literal, 'Two literal interpreters agree on the longer word')
    paired = word(gates, [2, 4, 8, 2, 4, 8])
    need(endpoint(paired) == {3: 4}, 'Actual six-call paired-stage endpoint')
    gram, ps = query_frame(gates)
    groups = [(i, i+3) for i in range(3)]
    for group in groups:
        need(rank(submatrix(gram, group, group)) == 0, 'Zero within-pair Gram')
        need(add(ps[group[0]], ps[group[1]]) == eye(4), 'Full pair capacity')
    for s, t in combinations(groups, 2):
        need(rank(submatrix(gram, s, t)) == 2, 'Off-diagonal intersection demand')
    need(4 > 2 + (2 % 2), 'Longer positive control defeats a false shortest extension')
    return {'sharp_five_query_degrees': {'0': 2, '2': 2}, 'sharp_margin_at_linear_tariff': -8,
            'six_query_paired_degrees': {'3': 4}, 'six_query_gram': gram,
            'two_literal_interpreters': True, 'deleted_query_rejected': True}


def simplex_controls():
    pairings = private_tests = 0
    for n in range(2, 65, 2):
        ones = (1 << n)-1
        us = [1 << i for i in range(n)] + [ones]
        vs = [ones ^ (1 << i) for i in range(n)] + [ones]
        gram = [sum(dot(v, u) << j for j, u in enumerate(us)) for v in vs]
        need(gram == [((1 << (n+1))-1) ^ (1 << i) for i in range(n+1)], 'Simplex pairings')
        pairings += (n+1)**2
        for k in range(1, n+2):
            need(rank(submatrix(gram, range(k), range(k))) == k-k % 2,
                 'Every principal-block rank formula')
        projectors, suffixes = {}, {}
        for s in range(1, n):
            u_tail = v_tail = 0
            for j in range(s+1, n+1):
                u_tail ^= us[j]
                v_tail ^= vs[j]
            pairing = [dot(vs[s], us[s]), dot(vs[s], u_tail),
                       dot(v_tail, us[s]), dot(v_tail, u_tail)]
            need(pairing == [0, (n-s) % 2, (n-s) % 2, 0], 'Private-stage pairing')
            if (n-s) % 2 == 0:
                continue
            p = add(outer(us[s], v_tail, n), outer(u_tail, vs[s], n))
            need(rank(p) == 2 and mul(p, p) == p, 'Forced private projector')
            projectors[s], suffixes[s] = p, u_tail
            for boundary, u_extra, v_extra in (
                    (0, us[s] ^ u_tail, vs[s] ^ v_tail), (n, u_tail, v_tail)):
                if (boundary == 0 and s == 1) or (boundary == n and s == n-1):
                    continue
                need(u_extra not in (0, us[boundary]) and v_extra not in (0, vs[boundary]),
                     'Endpoint pairs are independent')
                need(not any(dot(v, u) for v in (vs[boundary], v_extra)
                             for u in (us[boundary], u_extra)), 'Endpoint degeneracy')
                private_tests += 1
        for s, t in combinations(projectors, 2):
            need(apply(projectors[s], us[t]) == suffixes[s] != 0, 'Earlier private projector')
            need(apply(projectors[t], suffixes[s]) == 0 and
                 apply(projectors[t], us[t]) == us[t], 'Private projectors fail to commute')
            private_tests += 1
    for k in range(1, 65):
        n, total = k+1, [0]*(k+1)
        for i in range(1, n):
            p = add(outer(1, 1, n), outer(1 << i, 1 << i, n))
            r = outer(1 | (1 << i), 1 | (1 << i), n)
            need(mul(p, p) == p and mul(p, r) == mul(r, p) == r, 'Local capacity witness')
            total = add(total, p)
        need(mul(total, total) == total and rank(total) == k+k % 2, 'Sharp local reuse capacity')
    return {'max_main_fields': 64, 'simplex_pairings': pairings,
            'private_stage_controls': private_tests, 'sharp_local_capacities': 64}


def rank_cut_controls():
    n, us, vs = 4, [1, 2, 4, 8, 15], [14, 13, 11, 7, 15]
    choices = []
    for u, v in zip(us, vs):
        ps = set()
        for a, b in product(range(16), repeat=2):
            if dot(v, a) and dot(b, u) and not dot(b, a):
                ps.add(tuple(add(outer(u, b, n), outer(a, v, n))))
        need(len(ps) == 16, 'Complete compatible projector alphabet')
        choices.append(sorted(ps))
    counts = {}
    for k in (2, 3):
        passed, ranks = 0, set()
        for terms in product(*choices[:k]):
            e = [0]*n
            for p in terms:
                e = add(e, p)
            if mul(e, e) != e:
                continue
            passed += 1
            ranks.add(rank(e))
            need(rank(e) <= k+k % 2, 'Enumerated repeated-axis cut')
        need(passed > 0 and max(ranks) == k+k % 2, 'Nonvacuous sharp capacity census')
        counts[str(k)] = {'words': 16**k, 'idempotent_sums': passed, 'ranks': sorted(ranks)}
    kernel_cases, factors = 0, []
    for a, b in product(product(range(4), repeat=2), repeat=2):
        e = mul(a, b)
        if mul(e, e) == e:
            need(rank(add(eye(2), mul(b, a))) == 2-rank(e), 'AB/BA kernel identity')
            kernel_cases += 1
            factors.append((a, b, e))
    intersection_cases = 0
    for (a, b, e), (c, d, f) in product(factors, repeat=2):
        if mul(e, f) != mul(f, e):
            continue
        need(rank(mul(b, c)) <= rank(mul(e, f)) + 4-rank(e)-rank(f),
             'Intersection cut with rank deficits')
        intersection_cases += 1
    bad = [2, 0]
    need(mul(bad, bad) != bad and rank(add(eye(2), bad)) != 2-rank(bad),
         'Non-idempotent control must fail the kernel identity')
    return {'simplex_projector_census': counts, 'kernel_identity_cases': kernel_cases,
            'intersection_factor_cases': intersection_cases,
            'non_idempotent_control_rejected': True}


def reusable_filter_controls():
    path = PACKAGE / 'cuts.py'
    module = ModuleType('caller_capacity_cuts')
    exec(compile(path.read_bytes(), str(path), 'exec'), module.__dict__)
    results = {}
    for name in ('shortest-repeat-rejected', 'six-query-positive',
                 'fourteen-query-intersection-rejected'):
        candidate = json.loads((PACKAGE / 'examples' / (name+'.json')).read_text())
        receipt = module.audit(candidate)
        expected = 'PASS_NECESSARY_CUTS_ONLY' if name == 'six-query-positive' else 'REJECT_NECESSARY_CUT'
        need(receipt['status'] == expected, 'Reusable cut filter fixture')
        if name == 'fourteen-query-intersection-rejected':
            need(all(x['target_count'] <= x['capacity'] for x in receipt['single_axis']),
                 'Longer negative passes every separate rank cut')
            need(all(x['kind'] == 'axis_intersection' for x in receipt['failures']),
                 'Joint cut is the discriminating condition')
        results[name] = receipt['status']
    candidate['u'][0] = 0
    try:
        module.audit(candidate)
    except ValueError:
        results['invalid_query_frame'] = 'REJECTED'
    else:
        raise ValueError('Invalid query frame was accepted')
    return results


def incidence_controls():
    records = {}
    for m in range(3, 66):
        n, dp = 2*m-2, {0: 0}
        for _ in range(n):
            new = {}
            for used, value in dp.items():
                for extra in range(min(m-2, 4-used)+1):
                    d, key = 2+extra, used+extra
                    new[key] = max(new.get(key, -1), value+d*(d-1)//2)
            dp = new
        maximum = dp[4]
        need(maximum == {3: 12, 4: 16, 5: 19}.get(m, 2*m+12), 'Exact intersection maximum')
        if m >= 4:
            need(m % 2 == 0 or maximum < m*(m-1), 'Paired-stage saturation rejected')
        if m <= 7:
            records[str(m)] = {'max_intersections': maximum, 'required': m*(m-1),
                               'parity_admissible': bool(m % 2)}
    gl2 = [list(a) for a in product(range(4), repeat=2) if rank(a) == 2]
    for x, z in product(gl2, repeat=2):
        need(mul(inverse(x), x) == eye(2) and rank(mul(x, inverse(z))) == 2,
             'Pair saturation forces full cross-pair rank')
    need(96*7-1040 == -368 and 96*9-1040 == -176, 'Longer complete linear bounds')
    return {'paired_stage_cases': records, 'packing_dp_max_m': 65,
            'gl2_pair_controls': len(gl2)**2, 'n12_all_concave_upper': -368,
            'n16_all_concave_upper': -176}


def block_simplex_controls():
    cases = 0
    for n, q in [(n, q) for n in (4, 6, 12) for q in (2, 3, 7)] + [(4, 104)]:
        blocks = [[(0 if i == j else 1) for j in range(n+1)] for i in range(n+1)]
        gram = [sum(blocks[i][j] << (j*q+a) for j in range(n+1))
                for i in range(n+1) for a in range(q)]
        need(mul(gram, gram) == gram and rank(gram) == n*q, 'Block query Gram projection')
        need(rank(add(eye(q*(n+1)), gram)) == q, 'Rank-q complement')
        for k in range(1, n+2):
            indices = range(q*k)
            need(rank(submatrix(gram, indices, indices)) == q*(k-k % 2),
                 'Block stage-capacity formula')
            cases += 1
    return {'rank_controls': cases, 'includes_port_count_104': True,
            'total_dimension_contract': 'N=q*n and L=n+1'}


def power_interval(r, numerator, denominator, bits=48):
    """Enclose r^(numerator/denominator) with checked integer powers."""
    scale = 1 << bits
    if r == 1:
        return scale, scale
    target = pow(r, numerator) << (bits*denominator)
    low, high = 0, r*scale+1
    while high-low > 1:
        mid = (low+high)//2
        if pow(mid, denominator) <= target:
            low = mid
        else:
            high = mid
    need(pow(low, denominator) <= target < pow(high, denominator), 'Exact integer root bounds')
    return low, high


def moment_interval(coefficients, powers):
    low = high = 0
    for r, coefficient in coefficients.items():
        a, b = powers[r]
        low += coefficient * (a if coefficient >= 0 else b)
        high += coefficient * (b if coefficient >= 0 else a)
    return low, high


def display_interval(pair):
    with localcontext() as context:
        context.prec = 32
        return {'denominator': 1 << 48, 'lower_numerator': pair[0], 'upper_numerator': pair[1],
                'lower_decimal': str(Decimal(pair[0])/(1 << 48)),
                'upper_decimal': str(Decimal(pair[1])/(1 << 48))}


def price_controls():
    paths = {'original_P104': ROOT / 'research/p104-productive-controller/RESULT.json',
             'PR5599_at_09dd0965': ROOT / 'research/p104-helper-subspace-splits/RESULT.json'}
    source = ROOT / 'research/native-equality-cut/cuts.py'
    equality = ModuleType('credited_equality_cuts')
    exec(compile(source.read_bytes(), str(source), 'exec'), equality.__dict__)
    ranks = [*range(1, 10), 17, 25]
    p998 = {r: power_interval(r, 499, 500) for r in ranks}
    p997 = {r: power_interval(r, 997, 1000) for r in ranks}
    results = {}
    for name, path in paths.items():
        source = json.loads(path.read_text())['local']
        paid = {int(r): c for r, c in source['paid'].items()}
        helpers = {int(r): c for r, c in source['helpers'].items()}
        c = {r: paid.get(r, 0)-helpers.get(r, 0) for r in set(paid) | set(helpers)}
        debt = sum(r*count for r, count in c.items())
        need(debt == 1720, 'Complete paid-minus-helper rank mass')
        need(debt-2*8*104 == 56 > 104//2, 'P104 fails the debt design threshold')
        hinges = [sum(count*max(r-j, 0) for r, count in c.items()) for j in range(1, 10)]
        need(all(value <= 0 for value in hinges), 'All-concave local lower bound')
        need([104*(f-1+16*f)-1720*f for f in range(3)] == [-104, -56, -8],
             'Sharp complete shortest upper bounds')
        need(Fraction(3016-1520*3, 3) < -8, 'All f>=3 excluded by decreasing bound')
        costs = {r: -3*count for r, count in c.items()}
        costs[25] = costs.get(25, 0)+208
        need(max(r for r, value in costs.items() if value < 0) <
             min(r for r, value in costs.items() if value > 0), 'Two-field sign separation')
        two = moment_interval(costs, p998)
        need(two[1] < 0, 'Two-field exception excluded at kappa .002')
        longer = {}
        for m in (4, 26):
            coefficients = {r: -2*m*count for r, count in c.items()}
            coefficients.update({17: 104*(2*m-5), 25: 312})
            need(max(r for r, v in coefficients.items() if v < 0) <
                 min(r for r, v in coefficients.items() if v > 0), 'Longer sign separation')
            interval = moment_interval(coefficients, p997)
            need(interval[1] < 0, 'Paired caller size endpoint excluded at kappa .003')
            longer[str(m)] = display_interval(interval)
        relaxed = {r: -14*count for r, count in c.items()}
        relaxed.update({17: 8*104, 25: 4*104})
        need(moment_interval(relaxed, p997)[0] > 0, 'Fourteen-call relaxation passes before joint cut')
        invoice = {'paid': {str(r): 14*count for r, count in paid.items()},
                   'targets': {str(r): 14*count for r, count in helpers.items()}}
        invoice['targets'].update({'17': 8*104, '25': 4*104})
        earlier_cut = equality.audit(invoice)
        need(earlier_cut['status'] == 'PASS_NECESSARY_EQUALITY_CUTS',
             'Earlier equality cuts do not reject the longer relaxation')
        results[name] = {'paid': paid, 'helpers': helpers, 'net_rank_mass': debt,
                         'hinges_at_1_through_9': hinges,
                         'two_field_margin_at_kappa_002': display_interval(two),
                         'paired_margin_at_kappa_003': longer,
                         'n12_previous_equality_cut': earlier_cut,
                         'n12_without_incidence_cut_positive': True}
    return results


def check():
    sources = authenticate()
    return {'status': 'PASS_CALLER_STAGE_CAPACITY_CUTS', 'authenticated_inputs': sources,
            'operator_controls': operator_controls(), 'simplex_controls': simplex_controls(),
            'rank_cut_controls': rank_cut_controls(), 'incidence_controls': incidence_controls(),
            'block_simplex_controls': block_simplex_controls(),
            'reusable_filter_controls': reusable_filter_controls(),
            'complete_prices': price_controls(),
            'limits': {'formal_kernel': False, 'independent_review': False, 'new_kappa': False,
                       'native_word_replay': False,
                       'model': 'Binary constant bases; commuting independent involutive axes; autonomous helpers'}}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write-result', action='store_true')
    args = parser.parse_args()
    result = check()
    serialized = json.dumps(result, indent=2, sort_keys=True)+'\n'
    destination = PACKAGE / 'RESULT.json'
    if args.write_result:
        destination.write_text(serialized)
    else:
        need(destination.read_text() == serialized, 'Committed result differs from replay')
    print(json.dumps(result, sort_keys=True))
