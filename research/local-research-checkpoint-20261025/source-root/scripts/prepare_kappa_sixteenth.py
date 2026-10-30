#!/usr/bin/env python3
"""Exact research screens for kappa=1/16; never accepts a new multiplier.

Douglas Colkitt, with OpenAI Codex assistance. Apache-2.0.
"""
import argparse
from fractions import Fraction as Q
from functools import lru_cache
import json
from pathlib import Path

import audit_assembly_domain as domain

TARGET = Q(1, 16)
OLD = Q(384599, 10**10)


@lru_cache(None)
def enclosure_tools():
    name = domain.PACKAGE + 'arithmetic/interval_moment.py'
    namespace = {}
    exec(compile(domain.pinned_bytes(domain.ROOT / name, domain.PINS[name]),
                 name, 'exec'), namespace)
    return namespace


def extended_exp(lo, hi):
    """Research-only range reduction; positive squaring preserves enclosure."""
    domain.require(type(lo) is Q and type(hi) is Q and 0 <= lo <= hi,
                   'Expected exact nonnegative interval')
    tools = enclosure_tools()
    squarings = 0
    while hi >= Q(1, 4):
        lo /= 2
        hi /= 2
        squarings += 1
    lo, hi = tools['exp_interval'](lo, hi)
    for _ in range(squarings):
        lo, hi = tools['lower'](lo * lo), tools['upper'](hi * hi)
    return lo, hi


def moment_screen(profile, saving):
    """Raw histogram only: a passing moment is NOT a construction certificate.

    Independent integer-power checks validate each rational-power enclosure.
    The bit wrapper's additional nonnegative costs are omitted, so failure
    already excludes the profile but success would require further checks.
    """
    domain.require(type(saving) is Q and 0 <= saving < 1, 'Exact saving in [0,1) required')
    m, W = profile['m'], Q(profile['W_per_vertex'])
    raw = profile['child_histogram']
    hist = {int(t): n for t, n in raw.items()}
    domain.require(type(m) is int and m > 1 and W > 0, 'Invalid dimensions')
    domain.require(hist and len(hist) == len(raw) and
                   all(0 < t < m and type(n) is int and n > 0 for t, n in hist.items()),
                   'Invalid histogram')
    mass = sum(t * n for t, n in hist.items())
    domain.require(mass == Q(profile['rank_per_vertex']) ==
                   W * m - Q(profile['deficit_per_vertex']), 'Rank ledger mismatch')
    domain.require(max(hist) == profile['maxchild'], 'Maximum child mismatch')
    low = high = Q(0)
    for t, n in sorted(hist.items()):
        ratio = Q(m, t)
        L, U = enclosure_tools()['log_interval'](ratio)
        E, F = extended_exp(saving * L, saving * U)
        domain.require(E**saving.denominator <= ratio**saving.numerator <=
                       F**saving.denominator, 'Independent rational-power check failed')
        weight = Q(t * n) / (W * m)
        low += weight * E
        high += weight * F
    return dict(saving=str(saving), moment_lower=str(low), moment_upper=str(high),
                excluded_by_raw_moment=low > 1, independent_power_checks=len(hist),
                required_normalized_moment_reduction_lower=str(max(Q(0), 1 - 1 / low)),
                scope='Raw histogram screen only; no endpoint, wrapper or bridge certification')


def prepare():
    name = domain.PACKAGE + 'certificate.json'
    certificate = json.loads(domain.pinned_bytes(domain.ROOT / name, domain.PINS[name]))
    necessary = TARGET / (1 - TARGET)
    coarse_threshold = necessary * (1 - OLD) / (1 - necessary)
    coarse, atom, admitted, complex_saving = Q(2, 25), Q(3, 40), Q(7, 100), Q(3, 40)
    effective = (1 - atom) * coarse + atom * OLD
    domain.require(admitted < effective < atom < 1 - effective, 'Wrapper budget failed')
    arithmetic = domain.diagnostic_case(admitted, complex_saving, TARGET,
                                       beta=Q(1, 100), backoff=Q(1, 10**6))
    domain.require(set(arithmetic['failed_slacks']) == {'b_below_one_over32'},
                   'Unexpected assembly obstacle')
    # Fixed complex ledger, even allowing deletion of every auxiliary role.
    p = certificate['complex']['profile']
    minimum_W = 2 * p['v']
    minimum_mass_fraction = 1 - Q(p['deficit_per_vertex'], minimum_W * p['m'])
    ratio = Q(p['m'], p['maxchild'])
    rejection = minimum_mass_fraction**necessary.denominator * ratio**necessary.numerator
    domain.require(rejection > 1, 'Fixed-ledger exclusion failed')
    return dict(
        status='PREPARATION ONLY; no new kappa or supplier certified',
        source_sha256=domain.PINS,
        target=dict(kappa=str(TARGET), log_exponent=str(1 - TARGET),
                    admitted_bit_saving_strictly_above=str(necessary),
                    coarse_bit_saving_strictly_above=str(coarse_threshold),
                    published_kappa_multiplier=str(TARGET / Q(certificate['kappa']))),
        illustrative_supplier_budget=dict(coarse_bit=str(coarse), atom=str(atom),
            ordinary_leaf=str(OLD), effective_bit=str(effective), admitted_bit=str(admitted),
            complex=str(complex_saving), status='Missing suppliers and extended-domain proof'),
        assembly_diagnostic=arithmetic,
        retained_profile_screens=dict(bit=moment_screen(certificate['bit']['profile'], coarse),
                                     complex=moment_screen(p, complex_saving)),
        fixed_complex_ledger_screen=dict(minimum_roles=minimum_W,
            minimum_mass_fraction=str(minimum_mass_fraction), maxchild_ratio=str(ratio),
            tested_saving=str(necessary), powered_moment_lower=str(rejection),
            excluded=rejection > 1,
            scope='Only fixed deficit, dimension, maxchild and two disjoint data banks; not a universal barrier'),
        published_control=domain.published_control())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--write', type=Path)
    group.add_argument('--check', type=Path)
    args = parser.parse_args()
    report = prepare()
    if args.check:
        domain.require(json.loads(args.check.read_text()) == report, 'Preparation receipt differs')
        print('PASS exact sixteenth preparation screens; no new bound certified')
    elif args.write:
        args.write.write_text(json.dumps(report, indent=2) + '\n')
    else:
        print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
