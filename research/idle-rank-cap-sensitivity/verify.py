#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Exact idle rank-cap sensitivity of the selected complex word's optimal packing.

Recomputes the selected endpoint and the packing ceiling with an independently written
rational enclosure chain (enclosures.py: atanh logarithms, positive Taylor exponential,
directed rounding to 2^-200), then certifies the endpoint of the optimal integer idle
packing for every legal cap of the idle rank.

usage: verify.py [--write]
Nick Petalas, with AI assistance. Apache-2.0.
"""
import json
import sys
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
import enclosures as E  # noqa: E402

M, N, W, CENTRE = 73, 144, 14336, 64
LOCAL = {1: 2412, 2: 418, 3: 432, 4: 142, 5: 82, 8: 8}
LOCAL_MASS = sum(r * n for r, n in LOCAL.items())
IDLE_MASS = (M - 1) * W + CENTRE * N - N * LOCAL_MASS
GUARD_R = 51
BITS = 50
CAPS = (51, 50, 49, 48, 47, 46, 45, 44, 42, 40, 36, 32, 28, 24, 16, 12, 8, 4, 3, 2, 1)
PUB_CEILING_LO = Q(52814190909, 31250000000000)   # complex-local-word-ceiling RESULT.json
PUB_CEILING_HI = Q(1690054109089, 10 ** 15)       # a_relaxation_achievable / a_ceiling
PUB_CEILING = PUB_CEILING_HI
PUB_CEILING_KAPPA = Q(1687202646, 10 ** 12)    # README of the same package


def require(ok, why):
    if not ok:
        raise ValueError(why)


def frac(text):
    return Q(*map(int, text.split('/')))


def merge(*dicts):
    out = {}
    for d in dicts:
        for r, n in d.items():
            out[r] = out.get(r, 0) + n
    return out


def load_sources():
    """Selected profile, idle histogram, endpoint and kappa from the pinned sources."""
    asm = json.loads((ROOT / 'research/community-frontier1094-audit/ASSEMBLY.json').read_text())
    ind = json.loads((ROOT / 'research/community-frontier1094-audit/INDEPENDENT1094.json').read_text())
    rec = json.loads((ROOT / 'certificates/selected-result.json').read_text())
    profile = {int(r): n for r, n in ind['owner']['profile'].items()}
    idle = {int(r): n for r, n in ind['owner']['idle'].items()}
    require(profile == {int(r): n for r, n in asm['complex_profile'].items()},
            'certificate and independent profile differ')
    require(ind['price']['live'] == W and ind['price']['calls'] == N, 'selected price stock differs')
    require(ind['price']['rank_mass'] == sum(r * n for r, n in profile.items()),
            'selected rank mass differs')
    require(sum(r * n for r, n in profile.items()) == (M - 1) * W + CENTRE * N,
            'coverage identity mass = 72W + 64N fails')
    require(max(idle) == ind['price']['max_child'] == 48, 'selected idle max rank differs')
    require(sum(r * n for r, n in idle.items()) == IDLE_MASS, 'selected idle mass differs')
    local_agg = {r: n * N for r, n in LOCAL.items()}
    require(merge(local_agg, idle) == profile, 'selected word is not local word plus idle histogram')
    a_c, kappa = frac(asm['complex_lower']), frac(rec['kappa'])
    exact = E.kappa(a_c)
    require(0 < exact - kappa < Q(1, 10 ** 18),
            'selected kappa is not the truncated 18-digit decimal of a/(1+a)')
    return dict(profile=profile, idle=idle, local_agg=local_agg, a_c=a_c, kappa=kappa,
                kappa_exact=str(exact), kappa_exact_decimal=f'{float(exact):.18g}')


def pack_fractional(base, R):
    """Ideal relay-like relaxation: the whole idle mass in (fractional) rank-R children."""
    return merge(base, {R: Q(IDLE_MASS, R)})


def pack_integer(base, R):
    """Aggregate integer optimum: whole rank-R children, residue in one child of its own rank."""
    q, s = divmod(IDLE_MASS, R)
    return merge(base, {R: q}, {s: 1} if s else {})


def pack_integer_container(base, R):
    """As above, but the residue is carried by rank-1 children instead of one small child."""
    q, s = divmod(IDLE_MASS, R)
    return merge(base, {R: q}, {1: s} if s else {})


def pack_integer_per_call(base, R):
    """The same optimum required independently inside each call (no pooling across calls)."""
    per = IDLE_MASS // N
    q, s = divmod(per, R)
    return merge(base, {R: q * N}, {s: N} if s else {})


def rank_gain(lo, hi, a_c, kappa):
    """Certified lower bounds on the relative gain over the selected endpoint."""
    return dict(a_lo=str(lo), a_hi=str(hi), a_decimal=f'{float(lo):.15g}',
                a_gain_percent_lower=f'{100 * (lo / a_c - 1):.6g}',
                kappa_lo=f'{float(E.kappa(lo)):.12g}',
                kappa_gain_percent_lower=f'{100 * (E.kappa(lo) / kappa - 1):.6g}')


def table(src):
    out = {'fractional_relaxation': {}, 'integer_aggregate': {}, 'integer_per_call': {},
           'integer_container_residue': {}}
    for R in CAPS:
        for name, H in (('fractional_relaxation', pack_fractional(src['local_agg'], R)),
                        ('integer_aggregate', pack_integer(src['local_agg'], R)),
                        ('integer_per_call', pack_integer_per_call(src['local_agg'], R)),
                        ('integer_container_residue', pack_integer_container(src['local_agg'], R))):
            lo, hi = E.endpoint(H, M, W, bits=BITS)
            out[name][str(R)] = rank_gain(lo, hi, src['a_c'], src['kappa'])
    return out


def controls(src, tbl, ev):
    out = {}
    base, a_c = src['local_agg'], src['a_c']
    # 1. the outer halving guard is why 51 is legal and 52 is not
    require(2 * GUARD_R * GUARD_R < M * M, 'guard cap 51 violates the halving guard')
    require(2 * 52 * 52 > M * M, 'guard cap 52 does not violate the halving guard')
    out['halving_guard_admits_51_rejects_52'] = 'yes'
    # 2. the selected histogram itself exceeds one at the published ceiling
    ml, mh = E.moment_bounds(src['profile'], M, W, PUB_CEILING)
    require(ml > 1 and mh > 1, 'selected word does not exceed one at the published ceiling')
    out['selected_word_above_one_at_published_ceiling'] = 'yes'
    # 3. the published ceiling interval and the independent bracket overlap, and the
    #    published kappa cap is not below the independently certified value
    lo, hi = E.endpoint(pack_fractional(base, GUARD_R), M, W, bits=BITS)
    require(max(lo, PUB_CEILING_LO) <= min(hi, PUB_CEILING_HI),
            'published and independent ceiling brackets do not overlap')
    require(E.kappa(lo) <= PUB_CEILING_KAPPA, 'published kappa cap below the independent value')
    out['published_ceiling_bracket_overlaps_independent'] = 'yes'
    # 4. the published endpoint is a truncation of the root: its exact moment is strictly
    #    below one, and within 1e-23 of one
    require(Q(ev['selected_root_lo']) <= a_c <= Q(ev['selected_root_hi']),
            'published endpoint outside the certified grid bracket')
    ml, mh = E.moment_bounds(src['profile'], M, W, a_c)
    require(mh < 1 and ml > 1 - Q(1, 10 ** 23),
            'published endpoint is not a sub-1e-23 truncation of the root')
    out['published_endpoint_is_truncated_root'] = 'yes'
    # 5. monotonicity of the integer optimum in the rank cap
    vals = [(R, Q(tbl['integer_aggregate'][str(R)]['a_lo'])) for R in CAPS]
    require(all(vals[i][1] <= vals[i - 1][1] for i in range(1, len(vals))),
            'integer optimum not monotone in the rank cap')
    out['integer_optimum_monotone_in_cap'] = 'yes'
    # 6. rank dominance: the same mass at rank 1 prices strictly worse than at the cap
    shifted = merge(pack_integer(base, GUARD_R), {GUARD_R: -1, 1: 51})
    require(E.endpoint(shifted, M, W, bits=BITS)[1] < Q(tbl['integer_aggregate']['51']['a_lo']),
            'rank dominance fails')
    out['same_mass_at_rank_1_prices_worse'] = 'yes'
    # 7. pooling matters: the aggregate optimum strictly beats the per-call optimum at the cap
    require(Q(tbl['integer_aggregate']['51']['a_lo']) >
            Q(tbl['integer_per_call']['51']['a_hi']),
            'aggregate optimum does not beat the per-call optimum')
    out['aggregate_optimum_strictly_above_per_call_optimum'] = 'yes'
    # 8. refused inputs: a rank above the cap, a wrong idle mass, a negative count
    for name in ('idle_rank_52_above_cap', 'idle_mass_plus_one', 'negative_count'):
        try:
            if name == 'idle_rank_52_above_cap':
                bad = {52: 1}
            elif name == 'idle_mass_plus_one':
                bad = merge(base, {1: IDLE_MASS + 1})
            else:
                bad = merge(base, {1: -3})
            require(max(bad) <= GUARD_R, 'idle rank above the guard cap')
            E.moment_bounds(bad, M, W, Q(1, 1000))
            require(sum(r * n for r, n in bad.items()) == (M - 1) * W + CENTRE * N,
                    'coverage mass mismatch')
            require(all(n >= 0 for n in bad.values()), 'negative count')
            out[name] = 'ACCEPTED'
        except ValueError as exc:
            out[name] = 'rejected: ' + str(exc)
    require(all(v.startswith('rejected') or v == 'yes' for v in out.values()),
            'control failure: ' + json.dumps(out))
    return out


def build():
    src = load_sources()
    tbl = table(src)
    lo, hi = E.endpoint(src['profile'], M, W, bits=BITS)
    ml, mh = E.moment_bounds(src['profile'], M, W, src['a_c'])
    ev = dict(selected_root_lo=str(lo), selected_root_hi=str(hi),
              selected_root_lo_decimal=f'{float(lo):.20g}',
              selected_root_hi_decimal=f'{float(hi):.20g}',
              moment_minus_one_at_published_endpoint=[f'{float(ml - 1):.6g}', f'{float(mh - 1):.6g}'],
              published_kappa_cap='1687202646/1000000000000',
              published_ceiling_bracket=[str(PUB_CEILING_LO), str(PUB_CEILING_HI)])
    return dict(
        status='PASS_IDLE_RANK_CAP_SENSITIVITY',
        model=dict(m=M, calls=N, live=W, centre_per_call=CENTRE,
                   local_profile_per_call={str(r): n for r, n in sorted(LOCAL.items())},
                   local_mass_per_call=LOCAL_MASS, idle_mass=IDLE_MASS,
                   coverage='rank mass = 72 W + 64 N (checked on the selected profile)',
                   idle_rank_cap=GUARD_R, halving_guard='2 R^2 < m^2 admits 51 and rejects 52',
                   grid='2^-%d' % BITS),
        selected=dict(profile={str(r): n for r, n in sorted(src['profile'].items())},
                      idle_histogram={str(r): n for r, n in sorted(src['idle'].items())},
                      a_endpoint=str(src['a_c']), kappa=str(src['kappa']),
                      kappa_exact_at_endpoint=src['kappa_exact'],
                      kappa_exact_decimal=src['kappa_exact_decimal'],
                      truncation_evidence=ev),
        endpoints=tbl,
        controls=controls(src, tbl, ev),
        scope='Per-call uniform local word of the selected complex supplier, 144 calls, 14336 live '
              'data families, the PR1012 coverage law and the outer halving guard. Endpoints are for '
              'the exact moment (1/W) sum_r n_r (r/m)^(1-a) = 1. Fractional and integer idle packings '
              'are pricing models: no physical hosting, owner-family or restoration cost is claimed.')


def main():
    out = build()
    text = json.dumps(out, indent=1, sort_keys=True) + '\n'
    if sys.argv[1:] == ['--write']:
        (HERE / 'RESULT.json').write_text(text)
    else:
        require((HERE / 'RESULT.json').read_text() == text, 'RESULT.json differs')
    e = out['endpoints']
    print(out['status'],
          'selected', e['integer_aggregate']['51']['a_decimal'],
          'R51_gain', e['integer_aggregate']['51']['a_gain_percent_lower'],
          'R48_gain', e['integer_aggregate']['48']['a_gain_percent_lower'])


if __name__ == '__main__':
    try:
        main()
    except ValueError as exc:
        print('FAIL:', exc)
        sys.exit(1)
