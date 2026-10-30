"""Check exact tariff bounds from the pinned P104 inventory.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
"""
from fractions import Fraction
from functools import lru_cache
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


@lru_cache(None)
def power_interval(rank, numerator, denominator, bits=42):
    scale = 1 << bits
    target = pow(rank, numerator) << (bits*denominator)
    low, high = 0, rank*scale+1
    while high-low > 1:
        mid = (low+high)//2
        if pow(mid, denominator) <= target:
            low = mid
        else:
            high = mid
    upper = low if pow(low, denominator) == target else low+1
    return Fraction(low, scale), Fraction(upper, scale)


def interval_sum(profile, saving):
    power = 1-saving
    low = high = Fraction(0)
    for rank, count in profile.items():
        a, b = power_interval(rank, power.numerator, power.denominator)
        low += count*(a if count > 0 else b)
        high += count*(b if count > 0 else a)
    return low, high


def profile(source, leaves, thin_per_port):
    counts = {int(r): -2*leaves*v for r, v in source['paid'].items()}
    for r, v in source['helpers'].items():
        counts[int(r)] = counts.get(int(r), 0)+2*leaves*v
    counts[8*leaves+1] = counts.get(8*leaves+1, 0)+208
    counts[9] = counts.get(9, 0)+208*leaves
    counts[1] -= 104*thin_per_port
    return {r: c for r, c in sorted(counts.items()) if c}


def run():
    source = json.loads((ROOT/'sources/p104-result.json').read_text())['local']
    require(sum(int(r)*n for r, n in source['paid'].items())
            - sum(int(r)*n for r, n in source['helpers'].items()) == 1720,
            'retained net rank mass')
    saving = Fraction(8, 3125)
    t = 1-saving
    c_profile = {int(r): -2*n for r, n in source['paid'].items()}
    for r, n in source['helpers'].items():
        c_profile[int(r)] = c_profile.get(int(r), 0)+2*n
    c_profile[9] = c_profile.get(9, 0)+208
    c_low, c_high = interval_sum(c_profile, saving)
    z_low, z_high = power_interval(257, t.numerator, t.denominator)
    z_low, z_high = z_low/257, z_high/257
    slope = (1664*t*z_low+c_low-Fraction(104, 3),
             1664*t*z_high+c_high-Fraction(104, 3))
    intercept = (208*z_low*(1+256*saving)-Fraction(1040, 3),
                 208*z_high*(1+256*saving)-Fraction(1040, 3))
    require(slope[1] < 0 and intercept[1] < -7, 'uniform negative tangent')
    bound31 = profile(source, 31, 14)
    bound127 = profile(source, 127, 88)
    complete31 = profile(source, 31, 64)
    short_margins = {g: sum(r*c for r, c in profile(source, g, 4).items()) for g in (1, 2)}
    require(short_margins == {1: -112, 2: -16}, 'short caller linear losses')
    require(sum(r*c for r, c in complete31.items()) == -3472, 'complete word linear loss')
    require(min(r for r, c in complete31.items() if c > 0) >= 8, 'positive rank floor')
    require(max(r for r, c in complete31.items() if c < 0) <= 7, 'negative rank ceiling')
    # These signs hold per g. They transfer rejection to larger savings.
    require(all((r >= 8 if c > 0 else r <= 7) for r, c in c_profile.items() if c),
            'uniform separated ranks')
    candidates = []
    for g, q, thin, alpha in ((13, 8, 5, Fraction(17, 5000)),
                               (31, 26, 5, Fraction(7, 2000))):
        lower_rank = 4*q+2*((g-2+2)//3)
        require(thin*q >= lower_rank, 'candidate rank budget')
        low, high = interval_sum(profile(source, g, thin), alpha)
        require(low > 0, 'candidate optimistic margin')
        candidates.append({'leaves': g, 'coupled_ports': q, 'thin_maps': thin,
                           'rank_per_thin_map': q, 'minimum_thin_rank': lower_rank,
                           'saving': str(alpha), 'margin': [str(low), str(high)],
                           'status': 'UNCONSTRUCTED; COMMUTING FULL PROJECTORS EXCLUDED'})
    return {'net_rank_mass_per_full_call': 1720,
            'requested_31_leaf': {'ports': 2, 'requested_thin_rank': 10,
                                  'minimum_thin_rank': 28,
                                  'minimum_with_arbitrary_nonzero_stage_splits': 20,
                                  'minimum_H1_calls_at_104_ports': 1456,
                                  'optimistic_signed_profile': bound31},
            'old_127_leaf': {'ports': 1, 'requested_thin_rank': 10,
                             'minimum_thin_rank': 88,
                             'optimistic_signed_profile': bound127},
            'uniform_one_or_two_port_ceiling': {
                'saving_rejected': str(saving), 'tangent_leaves': 32,
                'slope_interval': [str(x) for x in slope],
                'intercept_interval': [str(x) for x in intercept],
                'all_integer_leaves_at_least_three': True,
                'short_caller_linear_margins': short_margins,
                'all_positive_leaf_counts_rejected': True,
                'all_larger_savings_rejected': True},
            'complete_binary_word31': {'full_calls': 62, 'thin_maps': 16,
                                       'rank_per_thin_map': 8, 'binary_blocks': 52,
                                       'H1_thin_calls_at_104_ports': 6656,
                                       'signed_profile': complete31,
                                       'linear_margin': -3472,
                                       'all_concave_moments_rejected': True},
            'unconstructed_targets': candidates}


def require(ok, message):
    if not ok:
        raise ValueError(message)
