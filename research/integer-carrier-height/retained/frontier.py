#!/usr/bin/env python3
"""Source-bound carrier certificates, retaining the complete PR5413 invoice.

Apache-2.0. Richard Hoekstra, with substantial OpenAI Codex assistance.
The higher-moment/logarithmic compiler is zxv's; the mixed flow is Jacob
Alan Sussman's. Arithmetic helpers and the outer ledger are authenticated
public sources credited to Chris R/Clear1nsight and their retained lineage.
This module does not independently reimplement those arithmetic helpers.
"""
import copy
import hashlib
import json
from fractions import Fraction as Q
from pathlib import Path

AGENTS = 'swarm-coupled-caller-sol-high-20261024/agents/'
INVOICE = AGENTS+'invoice/'
PRECISION = AGENTS+'precision/'
TEMPLATE = 'carrier-frontier/BASELINE-FUNDING.json'
TEMPLATE_SHA = '70ab7d13548962097ad83ad393b8482f52e827b8996869011ce6d071146bd3eb'
MOMENTS = INVOICE+'exact_moments.py'
MOMENTS_SHA = 'cf7439c9eb4095224126dd5eefc9f1c5dfe1968d6e8eca5b87d4a3897841182d'
OUTER = 'swarm-next-gain-sol-high-20261024/agents/numeric/exact_engine.py'
OUTER_SHA = '9ef7ee4082631566eb7903c3e21e517ef58039dca2a47104a2279c459589eb47'
BASE_K = Q('0.003027288235')
BASE_S = Q('0.003027288245')
CASES = [dict(name='fixed-kappa', k=BASE_K, s=BASE_S, v=1024, c=18, b=21,
              u=Q(1, 10), theta=Q(61, 64), p=322, H=12040700000000000, j=17201)]
for name, k, v, p, H, j in [
    ('saving-003', Q('.003'), 512, 120, 1239850102, 3625),
    ('saving-00275', Q('.00275'), 256, 59, 50859231, 1511),
    ('saving-0025', Q('.0025'), 256, 58, 25258797, 1427),
    ('saving-002', Q('.002'), 256, 55, 11738348, 1292),
]:
    CASES.append(dict(name=name, k=k, s=k+Q(3, 4)*(BASE_S-k), v=v, c=17, b=21,
                      u=Q(1, 10), theta=Q(15, 16), p=p, H=H, j=j))


def need(ok, why):
    if not ok:
        raise ValueError(why)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def encode(value):
    if isinstance(value, Q):
        return str(value)
    if isinstance(value, dict):
        return {str(k): encode(v) for k, v in value.items()}
    if isinstance(value, (tuple, list)):
        return [encode(v) for v in value]
    return value


def load_source(root, relative, digest):
    path = root/relative
    need(sha(path) == digest, 'changed public arithmetic input: '+relative)
    space = {'__name__': '_carrier_public_helper', '__file__': str(path)}
    exec(compile(path.read_bytes(), str(path), 'exec', dont_inherit=True, optimize=0), space)
    return space


def ceilq(x):
    return -((-x.numerator)//x.denominator)


def upper(x):
    scale = 2**192
    return Q(ceilq(x*scale), scale)


def grid(p, gap):
    need(type(p) is int and p > 0 and 0 < gap < Q(1, 16), 'proved positive carrier-grid domain')
    def at(j):
        return ceilq(Q(j)/gap)
    def wins(j):
        return (at(j)+1)**p < 2**j
    low, high = 1, 2
    while not wins(high):
        low, high = high, 2*high
    while high-low > 1:
        mid = (low+high)//2
        if wins(mid):
            high = mid
        else:
            low = mid
    need(wins(high) and not wins(high-1), 'first successful sufficient height grid')
    return at(high), high


def certify(root, case):
    need(sha(root/TEMPLATE) == TEMPLATE_SHA, 'frozen complete source invoice')
    baseline = json.loads((root/TEMPLATE).read_bytes())
    E = load_source(root, MOMENTS, MOMENTS_SHA)
    ledger = load_source(root, OUTER, OUTER_SHA)['ledger']
    power, moment = E['power'], E['moment']
    P, T = ({int(r): n for r, n in baseline[key].items()} for key in ('paid', 'targets'))
    need(sum(P.values()) == 64260 and sum(T.values()) == 10928, 'full source profile')
    k, s, v, c, b, u, theta, p = (case[key] for key in ('k', 's', 'v', 'c', 'b', 'u', 'theta', 'p'))
    t, d = 1-s, (s-k)/7
    target, paid = moment(T, t), moment(P, t)
    alpha = upper(paid[1]/target[0])
    gamma = upper(moment(P, t+u)[1]/(power(c, u)[0]*target[0]))
    delta = upper(Q(b*sum(T.values()))/(power(c, s)[0]*target[0]))
    original_paid = upper(alpha**v)
    higher_tail, completion_tail = upper(2*gamma**v), upper(2*delta**v)
    complete = original_paid+higher_tail+completion_tail
    eta = (1-s)*power(145, -v*s)[0]
    H, j = grid(p, d)
    n, den = theta.numerator, theta.denominator
    predicates = dict(
        ordered_savings=0 < k < s < Q('.0034'), raw_moment=target[0] > paid[1],
        funded_alpha_reserve=alpha < 1-Q(1, 10**12), higher_moment_domain=u >= s,
        positive_partial_block_charges=higher_tail > 0 and completion_tail > 0,
        exact_completed_moment=complete < 1, split=1 < c < b < 145,
        true_exit_exponent=c**den < b**n,
        shifted_exits=2**(den-n)*c**(v*den) <= 145**(v*n),
        eta=eta > theta**p, initial_range=power(145, v*s)[1] < 2**p,
        height=H > 8*v and (H, j) == (case['H'], case['j']))
    need(all(predicates.values()), 'unfunded carrier predicates: '+str(predicates))
    parameters = dict(kappa=k, tested_saving=s, complex_uniform_saving=k+6*d,
                      b=k+5*d, a=k+4*d, q=k+3*d, bit_saving=Q('.0034'),
                      bit_atom=Q('.004'), epsilon=1-d, beta=1-3*d, r0=d/10,
                      stop=d, layout=d, d=d)
    margins, strict, functional = ledger(parameters)
    need(set(strict) == set(baseline['source_predicates']['strict']) and
         set(functional) == set(baseline['source_predicates']['functional']), '54+4 source inventory')
    need(len(strict) == 54 and len(functional) == 4 and
         min(strict.values()) > 0 and min(functional.values()) > 0, 'strict full outer ledger')
    result = copy.deepcopy(baseline)
    for obsolete in ('strict_minimum_rounding_reserve', 'reserve_above_minimum',
                     'reserve_slack', 'preceding_grid_fails'):
        result.pop(obsolete, None)
    result.update(case=case['name'], kappa=k, tested=s, gap=d, H=H, j=j,
        tuple=dict(ambient=145, cutoff=c, floor=b, offset=u, tensor_power=v,
                   theta=theta, logarithm_power=p),
        raw_tested_margin=(target[0]-paid[1], target[1]-paid[0]),
        alpha_upper=alpha, gamma_upper=gamma, delta_upper=delta, eta_lower=eta,
        normalized_paid_upper=complete, original_paid_upper=original_paid,
        higher_tail_upper=higher_tail, completion_tail_upper=completion_tail,
        completion_slack=1-complete, reserve_slack=1-Q(1, 10**12)-alpha,
        predicates=predicates, outer=dict(parameters=parameters, margins=margins,
            strict=strict, functional=functional, minimum_strict=min(strict.values()),
            minimum_functional=min(functional.values())),
        gain_over_comparison=k-Q('.00302728823'),
        charging_model='complete-higher-moment-sum-with-both-partial-block-tails',
        grid_success=True, preceding_grid_fails=True,
        grid_scope='First j on H=ceil(j/gap) for this sufficient logarithmic majorant; no global template minimum.',
        controls={}, possible_gain_type='smaller carrier at unchanged or explicitly weaker exponent saving',
        scope='Source-bound numerical carrier certificate only; changed-tuple precision and physical conjunction are separate checks.')
    return encode(result)


def verify_funding(root, received):
    cases = [c for c in CASES if c['name'] == received.get('case')]
    need(len(cases) == 1 and certify(root, cases[0]) == received,
         'complete changed-tuple funding certificate differs from exact rebuild')
    return True
