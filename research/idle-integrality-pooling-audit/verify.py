#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Audit global versus per-call idle integrality; no predecessor code is run.

Arham-Tahir64 with substantial OpenAI Codex assistance. See NOTICE.md.
The positive-binomial enclosure is derived in PROOF.md, independently of the
predecessors' logarithm/exponential arithmetic. All verdicts use integers.
"""
import argparse
from collections import Counter, defaultdict
from fractions import Fraction as Q
from functools import lru_cache
import gzip
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SCALE = 10 ** 70
TOLERANCE = 10 ** 25  # enclosure tail < 10^-45 in real units
M = 73
CAP = 51
FAMILIES = 896
STAGES = 9
CENTRE = 64


def require(condition, message):
    if not condition:
        raise ValueError(message)


def ceil_div(n, d):
    require(d > 0, 'positive denominator required')
    return -(-n // d)


@lru_cache(None, typed=True)
def price(rank, saving):
    """Integer enclosure / SCALE of (rank/M) ** (1-saving).

    (1-z)^p = 1 - sum b_k*z^k, b_1=p,
    b_(k+1)=b_k*(k-p)/(k+1); all terms are positive for 0<p<1.
    The next-term geometric bound is valid because term ratios <= z<1.
    """
    require(type(rank) is int and 1 <= rank < M, 'price rank domain')
    saving = Q(saving)
    require(0 < saving < 1, 'price saving domain')
    p = 1 - saving
    pn, pd = p.numerator, p.denominator
    zn = M - rank
    first_n, first_d = pn * zn, pd * M
    term_lo = SCALE * first_n // first_d
    term_hi = ceil_div(SCALE * first_n, first_d)
    sum_lo = sum_hi = 0
    for k in range(1, 30000):
        sum_lo += term_lo
        sum_hi += term_hi
        rn = (k * pd - pn) * zn
        rd = pd * M * (k + 1)
        term_lo = term_lo * rn // rd
        term_hi = ceil_div(term_hi * rn, rd)
        tail_hi = ceil_div(term_hi * M, rank)
        if tail_hi < TOLERANCE:
            lo, hi = SCALE - sum_hi - tail_hi, SCALE - sum_lo
            require(0 < lo <= hi < SCALE, 'invalid price enclosure')
            return lo, hi
    raise ValueError('binomial tail did not converge within declared bound')


def validate(histogram, mass, cap=CAP):
    require(type(mass) is int and mass >= 0, 'mass domain')
    require(type(cap) is int and 1 <= cap < M, 'rank cap domain')
    require(isinstance(histogram, dict), 'histogram must be a mapping')
    require(all(type(r) is int and 1 <= r <= cap and
                type(n) is int and n > 0 for r, n in histogram.items()),
            'integer positive histogram required')
    require(sum(r * n for r, n in histogram.items()) == mass,
            'histogram does not conserve declared mass')


def optimum(mass, cap=CAP):
    """Credited PR1685 concavity theorem, not a newly discovered optimizer."""
    require(type(mass) is int and mass >= 0, 'mass domain')
    require(type(cap) is int and 1 <= cap < M, 'rank cap domain')
    count, residue = divmod(mass, cap)
    out = {cap: count} if count else {}
    if residue:
        out[residue] = 1
    validate(out, mass, cap)
    return out


def moment(local, calls, live, idle, saving):
    require(type(calls) is int and calls > 0 and type(live) is int and live > 0,
            'calls and live must be positive integers')
    require(all(type(r) is int and 1 <= r < M and type(n) is int and n > 0
                for r, n in local.items()), 'local profile domain')
    lo = hi = 0
    for hist, factor in ((local, calls), (idle, 1)):
        for r, n in hist.items():
            lower, upper = price(r, saving)
            lo += factor * n * lower
            hi += factor * n * upper
    return Q(lo, SCALE * live), Q(hi, SCALE * live)


def interval_json(interval, digits=24):
    """Exact fractions plus outward decimal labels; no floating point."""
    lo, hi = interval
    unit = 10 ** digits
    def fixed(value):
        return f'{value // unit}.{value % unit:0{digits}d}'
    return {'lower': str(lo), 'upper': str(hi),
            'decimal_lower': fixed(lo.numerator * unit // lo.denominator),
            'decimal_upper': fixed(ceil_div(hi.numerator * unit, hi.denominator))}


def root_bracket(local, calls, live, idle):
    """Monotone moment root, certified at adjacent 10^-15 grid points."""
    grid = 10 ** 15
    left, right = grid // 1000, grid // 500
    require(moment(local, calls, live, idle, Q(left, grid))[1] < 1,
            'root lower window does not accept')
    require(moment(local, calls, live, idle, Q(right, grid))[0] > 1,
            'root upper window does not reject')
    while right - left > 1:
        middle = (left + right) // 2
        lower, upper = moment(local, calls, live, idle, Q(middle, grid))
        if upper < 1:
            left = middle
        elif lower > 1:
            right = middle
        else:
            raise ValueError('root sign not separated')
    return {'lower': str(Q(left, grid)), 'upper': str(Q(right, grid)),
            'decimal_lower': interval_json((Q(left, grid), Q(right, grid)), 15)['decimal_lower'],
            'decimal_upper': interval_json((Q(left, grid), Q(right, grid)), 15)['decimal_upper'],
            'moment_at_lower': interval_json(moment(local, calls, live, idle, Q(left, grid))),
            'moment_at_upper': interval_json(moment(local, calls, live, idle, Q(right, grid)))}


def authenticate():
    manifest = json.loads((HERE / 'SOURCES.json').read_text())
    for row in manifest['files']:
        if row['usage'] == 'input':
            data = (ROOT / row['path']).read_bytes()
            require(hashlib.sha256(data).hexdigest() == row['sha256'],
                    'source input changed: ' + row['path'])
    upstream = json.loads((HERE / 'UPSTREAM.json').read_text())
    for row in upstream['files']:
        data = (HERE / row['retained_path']).read_bytes()
        require(hashlib.sha256(data).hexdigest() == row['sha256'],
                'retained predecessor changed: ' + row['retained_path'])
        blob = b'blob ' + str(len(data)).encode() + b'\0' + data
        require(hashlib.sha1(blob).hexdigest() == row['git_blob'],
                'retained Git blob mismatch')
    return upstream


def selected():
    rec = json.loads((ROOT / 'certificates/selected-result.json').read_text())
    asm = json.loads((ROOT / rec['certificate']).read_text())
    ind = json.loads((ROOT / 'research/community-frontier1094-audit/INDEPENDENT1094.json').read_text())
    full = {int(r): n for r, n in asm['complex_profile'].items()}
    require(full == {int(r): n for r, n in ind['owner']['profile'].items()},
            'selected profile sources disagree')
    idle = {int(r): n for r, n in ind['owner']['idle'].items()}
    calls, live = ind['price']['calls'], ind['price']['live']
    require((calls, live) == (144, 14336), 'unexpected selected dimensions')
    require(calls % STAGES == 0 and live == FAMILIES * (calls // STAGES),
            'replica dimensions disagree')
    require(sum(r * n for r, n in full.items()) == (M - 1) * live + CENTRE * calls,
            'selected coverage identity failed')
    local = {}
    for r in set(full) | set(idle):
        residual = full.get(r, 0) - idle.get(r, 0)
        require(residual >= 0 and residual % calls == 0, 'local word not uniform')
        if residual:
            local[r] = residual // calls
    require(local == {1: 2412, 2: 418, 3: 432, 4: 142, 5: 82, 8: 8},
            'unexpected local word')
    mass = sum(r * n for r, n in idle.items())
    require(mass == calls * 1646, 'selected idle mass mismatch')
    validate(idle, mass)
    return local, calls, live, mass


def owner_ledger(roles, plan):
    """Recount the literal selected capacity ledger, not a native/phase replay.

    Per the pinned indep16.check_roles, a bin is (owner, child, port), and
    allocations from *all* hosted calls consume its prefix before its one
    remainder is charged. Chronological windows here come from the pinned plan;
    source-event derivation, frame semantics and physical admission are unrun.
    """
    require(len(roles) == 69120, 'owner role inventory')
    groups = defaultdict(list)
    by_call = defaultdict(set)
    for row in roles:
        owner, child, port = row['owner_replica'], row['child'], row['port']
        stage, replica, time = row['stage'], row['replica'], row['time']
        require(0 <= port < 112 and 0 <= owner < 16, 'owner coordinates')
        require(0 <= time < 144 and plan['order'][time] == [stage, replica],
                'owner call identity')
        require(row['helper'] not in by_call[time], 'duplicate helper at call')
        by_call[time].add(row['helper'])
        rank, eligible = plan['windows'][f'{owner},{child}']
        require(time in eligible, 'outside declared window')
        require(row['width'] > 0 and row['offset'] >= 0 and
                row['offset'] + row['width'] <= rank, 'slice capacity')
        require(row['family'] == owner * 896 +
                (2 * plan['pairs'][str(child)] + plan['sides'][str(child)]) * 112 + port,
                'owner family identity')
        groups[owner, child, port].append(row)
    require(set(by_call) == set(range(144)) and
            all(helpers == set(range(480)) for helpers in by_call.values()),
            'complete per-call helper inventory')
    capacities = Counter(rank for rank, _ in plan['windows'].values())
    capacities = {rank: count * 112 for rank, count in capacities.items()}
    require(capacities == {8: 10752, 16: 7168, 32: 7168, 48: 7168},
            'declared bin capacity inventory')
    total_capacity = sum(rank * count for rank, count in capacities.items())
    total_width = sum(row['width'] for row in roles)
    require((total_capacity, total_width) == (774144, 537120),
            'declared capacity/width mass')
    idle = Counter()
    witness_key = (0, 6, 85)
    for label, (rank, _) in plan['windows'].items():
        owner, child = map(int, label.split(','))
        for port in range(112):
            rows = sorted(groups[owner, child, port], key=lambda row: row['offset'])
            used = 0
            for row in rows:
                require(row['offset'] == used, 'slice gap or overlap')
                used += row['width']
            require(used <= rank, 'bin overfull')
            if rank > used:
                idle[rank - used] += 1
    require(dict(idle) == {1: 2276, 3: 377, 7: 7, 48: 4866},
            'literal selected idle profile mismatch')
    shared = Counter(len({row['time'] for row in rows}) for rows in groups.values() if rows)
    require(sum(n for k, n in shared.items() if k > 1) == 17217,
            'shared-bin inventory mismatch')
    witness = sorted(groups[witness_key], key=lambda row: row['offset'])
    require([(r['time'], r['offset'], r['width']) for r in witness]
            == [(9, 0, 9), (11, 9, 4), (13, 13, 9), (15, 22, 9)],
            'shared remainder witness mismatch')
    return {'roles': len(roles), 'used_bins_by_distinct_host_calls': dict(sorted(shared.items())),
            'declared_bins_by_capacity': dict(sorted(capacities.items())),
            'total_capacity': total_capacity, 'allocated_width': total_width,
            'maximum_possible_residual_in_this_bin_recipe': max(capacities),
            'idle': dict(sorted(idle.items())),
            'shared_remainder_witness': {'bin': list(witness_key), 'capacity': 32,
                                         'remainder': 1, 'allocations': witness}}


def audit():
    upstream = authenticate()
    local, calls, live, mass = selected()
    claimed = json.loads((HERE / 'sources/pr3729/RESULT.json').read_text())
    upper = Q(claimed['integer_ceiling']['a_ceiling'])
    lower = Q(claimed['integer_ceiling']['a_witnessed_below'])
    single = optimum(mass // calls)
    require(single == {51: 32, 14: 1}, 'single-call positive control failed')
    require(single == {int(r): n for r, n in
                       claimed['integer_ceiling']['optimal_idle_histogram'].items()},
            'retained claim histogram mismatch')
    repeated = {r: n * calls for r, n in single.items()}
    pooled = optimum(mass)
    require(pooled == {51: 4647, 27: 1}, 'PR1685 aggregate control failed')
    validate(repeated, mass)
    separated = Q('0.001689')
    rows = []
    for saving in (lower, upper, separated):
        per_call = moment(local, calls, live, repeated, saving)
        aggregate = moment(local, calls, live, pooled, saving)
        require(aggregate[1] < per_call[0], 'pooling must strictly reduce cost')
        if saving == lower:
            require(per_call[1] < 1, 'claimed lower bracket positive control failed')
        else:
            require(per_call[0] > 1 and aggregate[1] < 1,
                    'separating moment signs failed')
        rows.append({'saving': str(saving), 'per_call': interval_json(per_call),
                     'pooled': interval_json(aggregate)})
    # An algebraic replica count suffices; no physical template is claimed.
    replicas = 17
    n, w = STAGES * replicas, FAMILIES * replicas
    pooled153 = optimum(1646 * n)
    require(pooled153 == {51: 4938}, 'zero-residue replicated histogram failed')
    require(Q(pooled153[CAP], n) == Q(1646, CAP),
            'replicated integer histogram does not equal fractional relaxation')
    require(sum(r * count for r, count in local.items()) * n + 1646 * n
            == (M - 1) * w + CENTRE * n, 'replicated coverage mismatch')
    fractional_witness = moment(local, n, w, pooled153, separated)
    require(fractional_witness[1] < 1, 'fractional-equality witness must pass')
    # Replicating the selected cohort 17 times also has zero aggregate residue.
    cohort_histogram = optimum(17 * calls * 1646)
    require(cohort_histogram == {51: 79008}, 'selected-cohort replication failed')
    # The two-unpaid lever is a changed law, not a physical construction.
    n2, w2 = STAGES, FAMILIES
    local_mass = sum(r * count for r, count in local.items())
    changed_mass = (M - 2) * w2 + CENTRE * n2 - n2 * local_mass
    require(changed_mass == 13918 and Q(changed_mass, n2).denominator == 9,
            'two-unpaid normalization control failed')
    changed_histogram = optimum(changed_mass)
    require(changed_histogram == {51: 272, 46: 1}, 'changed-law integer witness failed')
    parent = ROOT / 'research/complex-t16-rare-pattern-exchanges/data'
    owners = json.loads(gzip.decompress((parent / 'OWNERS.json.gz').read_bytes()))
    plan = json.loads((parent / 'PLAN.json').read_text())
    physical_ledger = owner_ledger(owners, plan)
    fixed_n_root = root_bracket(local, calls, live, pooled)
    zero_gap_root = root_bracket(local, n, w, pooled153)
    return {'status': 'PASS_IDLE_INTEGRALITY_POOLING_AUDIT',
            'audited_head': upstream['head'],
            'selected': {'calls': calls, 'live': live, 'idle_mass': mass,
                         'local_mass_per_call': local_mass, 'local': local},
            'repeated_per_call_histogram': repeated, 'pooled_histogram': pooled,
            'separating_decisions': rows,
            'fixed_144_call_pooled_ceiling': fixed_n_root,
            'fractional_equality_ceiling': zero_gap_root,
            'zero_gap_replication': {'replicas': replicas, 'calls': n, 'live': w,
                                     'histogram': pooled153,
                                     'moment_at_separating_saving': interval_json(fractional_witness),
                                     'selected_cohort_copies': 17,
                                     'selected_cohort_calls': 17 * calls,
                                     'selected_cohort_histogram': cohort_histogram},
            'two_unpaid_control': {'calls': n2, 'live': w2,
                                   'average_idle_mass': str(Q(changed_mass, n2)),
                                   'integer_total_mass': changed_mass,
                                   'histogram': changed_histogram},
            'literal_selected_owner_ledger': physical_ledger,
            'scope': 'Aggregate rank-mass relaxation only; no owner, hosting, physical packing, supplier or kappa admission.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    result = audit()
    text = json.dumps(result, indent=2, sort_keys=True) + '\n'
    if args.write:
        (HERE / 'RESULT.json').write_text(text)
    else:
        require((HERE / 'RESULT.json').read_text() == text, 'receipt differs; use --write intentionally')
    print(result['status'])


if __name__ == '__main__':
    main()
