#!/usr/bin/env python3
"""Exact optimistic budget for refining PR5599's thirteen H9 helpers.

Prepared by OpenAI Codex for Charan; substantial AI assistance. Apache-2.0.
No predecessor executable or floating-point power routine is imported.
"""
import argparse
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
PINS = {
    'source-result.json': '1d92e587915052110dfb3aca8890df5afdaf496164efa5a4a52e69ceeb3c70f3',
    'source-proof.md': 'f4c68acf9373e34d88e14e1a7791b4b739c8b5297a1ae4c0121f579a02fde04e',
    'source-selected.json': '2a0220e866417774606e0f991e41b9c1d26b1f43b97857238cf478dbc7d330b5',
}
CAP = Q(17, 5000)


def require(ok, message):
    if not ok:
        raise ValueError(message)


def authenticate(name, data):
    require(sha256(data).hexdigest() == PINS[name], 'source hash: ' + name)


def log_interval(r, terms=128):
    # ln(r) = 2 atanh((r-1)/(r+1)); positive geometric tail majorant.
    z = Q(r-1, r+1)
    lo = 2*sum((z**(2*k+1)/Q(2*k+1) for k in range(terms)), Q(0))
    return lo, lo + 2*z**(2*terms+1)/(Q(2*terms+1)*(1-z*z))


def exp_minus(x, n):
    require(0 <= x < 1, 'alternating-series domain')
    term = total = Q(1)
    for k in range(1, n+1):
        term *= -x/Q(k)
        total += term
    return total


def power_interval(r, saving=CAP):
    require(isinstance(r, int) and r >= 1, 'positive integral rank')
    require(0 <= saving <= CAP, 'saving outside certified interval')
    lo, hi = log_interval(r)
    return r*exp_minus(saving*hi, 17), r*exp_minus(saving*lo, 16)


def enclosure(lo, hi, digits=12):
    scale = 10**digits
    return [str(Q((lo*scale).__floor__(), scale)),
            str(Q((hi*scale).__ceil__(), scale))]


def partitions(total, minimum=1):
    if total == 0:
        yield ()
    for first in range(minimum, total+1):
        for tail in partitions(total-first, first):
            yield (first,) + tail


def validate_delta(delta, old_count, new_count):
    require(sum(r*n for r,n in delta.items()) == 0, 'rank mass changed')
    require(sum(delta.values()) == new_count-old_count, 'independent field count')
    require(delta.get(9) == -old_count, 'surrendered H9 targets missing')


def gain_interval(delta, powers):
    lo = hi = Q(0)
    for r, count in delta.items():
        a,b = powers[r]
        lo += count*(a if count >= 0 else b)
        hi += count*(b if count >= 0 else a)
    return lo,hi


def first_count(gain):
    lo,hi = gain
    n = 1//lo + 1
    require((n-1)*hi < 1 < n*lo, 'threshold not separated')
    return n


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    for name in PINS:
        authenticate(name, (HERE/name).read_bytes())
    source = json.loads((HERE/'source-result.json').read_text())
    selected = json.loads((HERE/'source-selected.json').read_text())
    require(selected['source_certificate_sha256'] == PINS['source-result.json'], 'selection binding')
    require(selected['audited_source_head'] == '09dd0965711ca7eeb169057a420abab1c9052137', 'source head')
    splits = source['splits']
    require(len(splits) == 13, 'thirteen source splits')
    delta = Counter()
    for split in splits:
        require(sum(split['ranks']) == 9 and len(split['ranks']) == 2, 'H9 source split')
        delta.update(split['ranks'])
        delta[9] -= 1
    require(dict(sorted(delta.items())) == {int(k):v for k,v in source['local_helper_delta'].items()}, 'source target delta')
    validate_delta(delta, 13, 26)
    cost = source['complete_cost']
    require(Q(cost['ordinary_BIT']['admitted']) == CAP, 'frozen BIT interval')
    require(cost['full_forward_calls'] == 18, 'replica count')
    require(sum(cost['paid'].values()) == 66726 and sum(cost['targets'].values()) == 13048, 'full counts')
    require(sum(int(r)*n for r,n in cost['targets'].items()) -
            sum(int(r)*n for r,n in cost['paid'].items()) == 760, 'full rank surplus')
    require(source['physical_caller']['new_paid_jobs'] == 0, 'source adds no paid job')

    powers = {r:power_interval(r) for r in range(1,10)}
    p9lo,p9hi = powers[9]
    single = (9-p9hi, 9-p9lo)
    best = tuple(13*x for x in single)
    require(best[1] < 1, 'thirteen-source exclusion')
    require(14*single[1] < 1 < 15*single[0], 'sharp relaxed source count')
    # A second implementation checks the outward-rounded power endpoints by
    # integer exponentiation, independent of the logarithm/exp series.
    pl,ph = map(Q, enclosure(p9lo,p9hi))
    exponent = 1-CAP
    rhs = 9**exponent.numerator
    require(pl.numerator**exponent.denominator < rhs*pl.denominator**exponent.denominator,
            'independent lower power bound')
    require(ph.numerator**exponent.denominator > rhs*ph.denominator**exponent.denominator,
            'independent upper power bound')

    rows = []
    for part in partitions(9):
        d = Counter(part)
        d[9] -= 1
        lo,hi = gain_interval(d,powers)
        require(sum(part) == 9 and len(part) <= 9, 'partition integrity')
        if part != (1,)*9:
            require(hi < single[0], 'strict best-partition separation')
        rows.append({'parts':list(part), 'gain_at_cap':enclosure(lo,hi)})
    require(len(rows) == 30, 'complete partition census')
    binary = gain_interval({4:1,5:1,9:-1},powers)
    for part in partitions(9):
        if len(part) == 2 and part != (4,5):
            d = Counter(part); d[9] -= 1
            require(gain_interval(d,powers)[1] < binary[0], 'best binary partition')
    actual = gain_interval(delta,powers)
    require(0 < actual[0] < actual[1] < best[0], 'actual split positive control')

    controls = []
    for label, bad, old, new in [
        ('omitted_original_target_debit', {1:117}, 13,117),
        ('extra_rank_mass', {1:118,9:-13}, 13,118),
        ('duplicate_independent_field_credit', {1:117,9:-13},13,118),
    ]:
        try:
            validate_delta(bad,old,new)
        except ValueError:
            controls.append(label)
        else:
            raise ValueError('control accepted: '+label)
    try:
        authenticate('source-result.json', (HERE/'source-result.json').read_bytes()+b' ')
    except ValueError:
        controls.append('changed_source_bytes')
    else:
        raise ValueError('hash control accepted')
    try:
        power_interval(9,Q(1,100))
    except ValueError:
        controls.append('unlicensed_exponent_range')
    else:
        raise ValueError('range control accepted')
    result = {
        'status':'PASS_HELPER_REFINEMENT_BUDGET_S29',
        'saving_interval':['0',str(CAP)],
        'maximum_gain_13_sources_at_cap':enclosure(*best),
        'minimum_loss_with_one_added_H1_at_cap':enclosure(1-best[1],1-best[0]),
        'actual_13_binary_splits_gain_at_cap':enclosure(*actual),
        'global_18_calls_maximum_gain_at_cap':enclosure(*(18*x for x in best)),
        'first_relaxed_source_count_paying_one_H1':first_count(single),
        'first_binary_source_count_paying_one_H1':first_count(binary),
        'partitions_of_nine':rows,
        'negative_controls':controls,
        'positive_controls':['actual_no_added_paid_job_gain','15_fully_refined_sources_can_pay_H1_at_cap'],
        'independent_integer_power_checks':2,
        'scope':'Optimistic target refinement only; fixed other targets and paid jobs; no supplier admission or new kappa.',
    }
    encoded = json.dumps(result,indent=2,sort_keys=True)+'\n'
    if args.write:
        (HERE/'RESULT.json').write_text(encoded)
    else:
        require((HERE/'RESULT.json').read_text() == encoded, 'result differs from committed certificate')
    print(result['status']+' partitions=30 controls=5 independent_power_checks=2')


if __name__ == '__main__':
    main()
