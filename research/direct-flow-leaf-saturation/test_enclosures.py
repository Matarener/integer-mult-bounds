#!/usr/bin/env python3
"""Exact independent enclosure checks and discriminating remainder mutations.

The logarithm oracle uses -log(1-q)=sum(q**k/k), rather than the primary
atanh series. After n=2**e*u, 1<=u<2, both log(2) and log(u) have q<=1/2.
For K=256 the positive remainder is at most
q**(K+1)/((K+1)*(1-q)).

The exponential oracle sums through degree 82. Its first omitted term is
x**83/83!, and every subsequent term ratio is at most x/84<=5/84, so a
geometric series bounds its tail. This does not use the primary Lagrange
bound exp(x)<3**5. Both implementations still share the ordinary exponential
series and Python's exact Fraction arithmetic; these finite checks are not a
formal proof of either series or of all future inputs.

Every successful log/exp argument in the primary parameters and controls is
checked. The domain is collected from that execution, not independently
inferred. Three mutations use smaller, explicitly named discriminating
fixtures; they do not rerun a mutated scientific certificate.

Prepared for DLamdata with substantial OpenAI Codex assistance. Apache-2.0.
"""
from fractions import Fraction
from functools import lru_cache
from pathlib import Path
import hashlib
import json

HERE = Path(__file__).resolve().parent
PRODUCTION = HERE / 'verify.py'
Q = Fraction


def need(ok, message):
    if not ok:
        raise ValueError(message)


def load(source):
    """Compile the actual source bytes, with no import bytecode-cache reuse."""
    namespace = {'__name__': 'enclosure_test_subject', '__file__': str(PRODUCTION)}
    exec(compile(source, str(PRODUCTION), 'exec'), namespace)
    return namespace


@lru_cache(None)
def log_oracle(n):
    need(isinstance(n, int) and n >= 1, 'oracle positive integer log input')
    e = n.bit_length() - 1
    u = Q(n, 1 << e)

    def minus_log_one_minus(q):
        need(0 <= q <= Q(1, 2), 'oracle log range reduction')
        term = Q(1)
        lower = Q(0)
        for k in range(1, 257):
            term *= q
            lower += term / k
        remainder = term * q / (257 * (1 - q))
        return lower, lower + remainder

    lo2, hi2 = minus_log_one_minus(Q(1, 2))
    lou, hiu = minus_log_one_minus(1 - 1 / u)
    return e * lo2 + lou, e * hi2 + hiu


@lru_cache(None)
def exp_oracle(x):
    need(isinstance(x, Q) and 0 <= x <= 5, 'oracle rational exp domain [0,5]')
    term = lower = Q(1)
    for k in range(1, 83):
        term *= x / k
        lower += term
    first_omitted = term * x / 83
    upper = lower + first_omitted / (1 - x / 84)
    return lower, upper


def check_enclosure(kind, argument, production_interval, oracle_interval):
    lo, hi = production_interval
    oracle_lo, oracle_hi = oracle_interval
    need(all(isinstance(x, Q) for x in (lo, hi, oracle_lo, oracle_hi)),
         kind + ' arithmetic must remain exact Fraction')
    need(lo <= oracle_lo <= oracle_hi <= hi,
         kind + ' enclosure fails exact independent containment')


def actual_arguments(subject):
    logs, exponentials = set(), set()
    original_log, original_exp = subject['log_bounds'], subject['exp_point']

    def track_log(n):
        value = original_log(n)
        logs.add(n)
        return value

    def track_exp(x):
        value = original_exp(x)
        exponentials.add(x)
        return value

    subject['log_bounds'], subject['exp_point'] = track_log, track_exp
    P, W, M = subject['bindings']()
    subject['parameters'](P, W, M)
    subject['controls']()
    # The full verifier's remaining finite_law function uses integer products
    # and counts only; it makes no log_bounds or exp_point calls.
    need(logs and exponentials, 'empty production argument coverage')
    return logs, exponentials, original_log, original_exp


def reject_mutation(source, name, old, new, kind, argument):
    need(source.count(old) == 1, 'mutation source anchor changed: ' + name)
    mutated = load(source.replace(old, new))
    function = mutated['log_bounds' if kind == 'log' else 'exp_point']
    oracle = log_oracle if kind == 'log' else exp_oracle
    try:
        check_enclosure(kind, argument, function(argument), oracle(argument))
    except ValueError as error:
        need(str(error) == kind + ' enclosure fails exact independent containment',
             'mutation rejected for an unrelated reason: ' + name)
        return name
    raise ValueError('remainder mutation escaped independent check: ' + name)


def main():
    source = PRODUCTION.read_text(encoding='utf-8')
    subject = load(source)
    logs, exponentials, production_log, production_exp = actual_arguments(subject)
    for n in sorted(logs):
        check_enclosure('log', n, production_log(n), log_oracle(n))
    for x in sorted(exponentials):
        check_enclosure('exp', x, production_exp(x), exp_oracle(x))
    # Known exact endpoints also guard the oracle's zero cases.
    need(log_oracle(1) == (Q(0), Q(0)) and exp_oracle(Q(0)) == (Q(1), Q(1)),
         'independent oracle identity fixtures')
    mutations = [
        reject_mutation(source, 'zero_log_tail_at_log2',
                        '        return total, total + tail',
                        '        return total, total', 'log', 2),
        reject_mutation(source, 'zero_exp_tail_at_exp1',
                        'tail = Q(3 ** 5) * term * x / 81',
                        'tail = Q(0)', 'exp', Q(1)),
        reject_mutation(source, 'invalid_exp_majorant_one_at_exp1',
                        'tail = Q(3 ** 5) * term * x / 81',
                        'tail = Q(1) * term * x / 81', 'exp', Q(1)),
    ]
    need(max(exponentials) < Q(479, 100), 'actual exp argument ceiling changed')
    # A deterministic domain digest records exact argument coverage without
    # printing the large rational numerators/denominators.
    domain = json.dumps({'log': sorted(logs),
                         'exp': [[str(x.numerator), str(x.denominator)]
                                 for x in sorted(exponentials)]},
                        sort_keys=True, separators=(',', ':')).encode()
    print(json.dumps({
        'status': 'PASS_INDEPENDENT_RATIONAL_ENCLOSURES',
        'production_source_sha256': hashlib.sha256(source.encode('utf-8')).hexdigest(),
        'log_integer_arguments': sorted(logs),
        'distinct_exp_rational_arguments': len(exponentials),
        'all_exp_arguments_below': '479/100',
        'domain_sha256': hashlib.sha256(domain).hexdigest(),
        'log_oracle': '256-term -log(1-q) series; exact positive geometric tail',
        'exp_oracle': 'degree-82 positive series; exact ratio-bounded geometric tail',
        'mutations_rejected': mutations,
        'scope': 'Exact containment at every argument captured from current parameters and controls; finite mutation discrimination, not a formal verifier or an all-input enclosure proof.'
    }, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
