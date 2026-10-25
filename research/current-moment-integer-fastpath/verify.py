#!/usr/bin/env python3
"""Exact differential checks against the authenticated Fraction implementation."""
from fractions import Fraction as F
import json
import random
import types
from unittest.mock import patch
import fast_moments as fast
import workload


def need(value, message):
    if not value:
        raise ValueError(message)


def traced(engine):
    calls = []
    original = engine.expbound
    def wrapper(x):
        result = original(x)
        calls.append((x, result))
        return result
    engine.expbound = wrapper
    return calls


def main():
    reference, candidate = fast.load_engine(False), fast.load_engine(True)
    left, right = traced(reference), traced(candidate)
    expected, actual = workload.run(reference), workload.run(candidate)
    need(expected == actual, 'complete pricing workload changed')
    need(left == right, 'exponential invocation/result trace changed')
    trace_count = len(left)
    rng = random.Random(20261025)
    values = {F(0), F(1, 64), F(1, 64)-F(1, 10**70),
              F(1, 64)+F(1, 10**70), F(1, 10**100), F(42), F(100)}
    values.update(F(2**j, 64) for j in range(15))
    values.update(F(rng.randrange(0, 100000), rng.randrange(1, 100000)) for _ in range(40))
    values |= {-x for x in values}
    for x in sorted(values):
        need(reference.expbound(x) == candidate.expbound(x), 'boundary/random exp mismatch')
        reduced = abs(x)
        while reduced > F(1, 64):
            reduced /= 2
        term = total = F(1)
        for j in range(1, 41):
            term *= reduced / j
            total += term
        remainder = term * reduced / 41 / (1-reduced/42)
        n, d, u, v = fast.taylor_parts(reduced.numerator, reduced.denominator)
        need(F(n, d) == total and F(u, v) == total+remainder, 'unrounded Taylor/remainder mismatch')
    for rank in (1, 2, 3, 8, 9, 72, 145):
        for exponent in (F(-3, 2), F(0), F(1, 3), F(1), F(3, 2)):
            need(reference.power(rank, exponent) == candidate.power(rank, exponent), 'signed power mismatch')
    paid, targets = workload.profiles()
    for k, sign in ((F(3027288235, 10**12), 1), (F(302728825, 10**11), -1)):
        margin = candidate.minus(candidate.moment(targets, 1-k), candidate.moment(paid, 1-k))
        need(margin[0] > 0 if sign == 1 else margin[1] < 0, 'selected lower/ceiling bracket changed')
    for action in (lambda: fast.load_engine(), workload.profiles):
        with patch('pathlib.Path.read_bytes', return_value=b'tampered'):
            try:
                action()
            except ValueError:
                pass
            else:
                raise ValueError('missing source/fixture tamper rejection')
    changed = dict(paid); changed[1] -= 1
    e = F(996972711765, 10**12)
    need(candidate.moment(changed, e) != candidate.moment(paid, e), 'omitted charge invisible')
    # Execute actual damaged implementations in memory. Check unrounded
    # parts too: the tiny positive tail often fits below one output grid unit.
    source = fast.SOURCE.parent.parent / 'fast_moments.py'
    raw = source.read_text(encoding='utf-8')
    for old, new in (('range(1, 41)', 'range(1, 40)'),
                     ('factor = 41 *', 'factor = 40 *'),
                     ('upper_num * precision + upper_den - 1', 'upper_num * precision')):
        need(raw.count(old) == 1, 'mutation target changed')
        mutant = types.ModuleType('mutant'); mutant.__file__ = str(source)
        exec(compile(raw.replace(old, new), str(source), 'exec', optimize=0), mutant.__dict__)
        parts = mutant.taylor_parts(1, 64)
        oracle = fast.taylor_parts(1, 64)
        detected = (F(parts[0], parts[1]), F(parts[2], parts[3])) != (F(oracle[0], oracle[1]), F(oracle[2], oracle[3]))
        if not detected:
            detected = mutant.load_engine().expbound(F(1, 64)) != reference.expbound(F(1, 64))
        need(detected, 'damaged kernel went undetected')
    try:
        candidate.logarithm(0)
    except ValueError:
        pass
    else:
        raise ValueError('positive-rank guard lost')
    print(json.dumps({'status': 'PASS_IDENTICAL_RATIONAL_PRICING',
                      'workload_sha256': workload.digest(actual),
                      'workload_exponential_calls': trace_count,
                      'boundary_and_random_values': len(values),
                      'new_kappa': None}, sort_keys=True))


if __name__ == '__main__':
    main()
