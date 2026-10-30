#!/usr/bin/env python3
"""Certify the numerical gates of PROOF.md, without replaying predecessors.

Produced by Nick Petalas. Apache-2.0.
"""
import ast
import hashlib
import json
from fractions import Fraction as F
from itertools import product
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
GRID = 1 << 128


def need(condition, message):
    if not condition:
        raise ValueError(message)


def rounded(lo, hi):
    need(lo <= hi, 'reversed interval')
    return (F(lo.numerator * GRID // lo.denominator, GRID),
            F(-((-hi.numerator * GRID) // hi.denominator), GRID))


def add(x, y):
    return rounded(x[0] + y[0], x[1] + y[1])


def mul(x, y):
    bounds = [a * b for a in x for b in y]
    return rounded(min(bounds), max(bounds))


def div(x, y):
    need(y[0] > 0, 'nonpositive denominator interval')
    return mul(x, (1 / y[1], 1 / y[0]))


def point(x):
    return (F(x), F(x))


def log_unit(x):
    need(F(1) <= x <= 2, 'log reduction domain')
    z = (x - 1) / (x + 1)
    total = sum((2 * z ** (2 * j + 1) / (2 * j + 1)
                 for j in range(48)), F(0))
    tail = 2 * z ** 97 / (97 * (1 - z * z))
    return rounded(total, total + tail)


def log_integer(n):
    need(type(n) is int and 1 <= n <= 121, 'log integer domain')
    k = n.bit_length() - 1
    return add(log_unit(F(n, 1 << k)), mul(point(k), log_unit(F(2))))


def exp_scalar(x):
    need(F(0) <= x <= 5, 'exp domain')
    y = x / 16
    term = F(1)
    total = F(1)
    for j in range(1, 33):
        term *= y / j
        total += term
    next_term = term * y / 33
    tail = next_term / (1 - y / 34)
    result = rounded(total, total + tail)
    for _ in range(4):
        result = mul(result, result)
    return result


def exp_interval(x):
    return exp_scalar(x[0])[0], exp_scalar(x[1])[1]


def authenticate(data, record):
    need(hashlib.sha256(data).hexdigest() == record['sha256'],
         'source hash mismatch: ' + record['path'])


def inputs():
    manifest = json.loads((PACKAGE / 'SOURCES.json').read_text())
    need(len(manifest['files']) == 4, 'source inventory')
    payloads = {}
    for entry in manifest['files']:
        path = entry['path']
        need(path in {'certificates/selected-result.json',
                      'docs/research/agent-task-catalog.json',
                      'research/direct-flow-leaf-walk/README.md',
                      'research/direct-flow-leaf-walk/verify.py'}, 'source path')
        if entry['usage'] == 'provenance':
            continue
        data = (ROOT / path).read_bytes()
        need(len(data) <= 1_000_000, 'source capacity')
        authenticate(data, entry)
        payloads[path] = data
    tree = ast.parse(payloads['research/direct-flow-leaf-walk/verify.py'])
    laws = {}
    need(len(tree.body) <= 100, 'source AST capacity')
    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1:
            target = node.targets[0]
            if isinstance(target, ast.Name) and target.id in {'P', 'W'}:
                laws[target.id] = ast.literal_eval(node.value)
    need(set(laws) == {'P', 'W'}, 'missing law')
    for law in laws.values():
        need(len(law) == 9, 'law support')
        need(all(type(r) is int and 1 <= r <= 121 and type(c) is int
                 and 1 <= c <= 100000 for r, c in law.items()), 'law domain')
    return laws, manifest


def moments(law, exponent, logs):
    result = [point(0), point(0), point(0)]
    for r, count in law.items():
        weight = mul(point(count), exp_interval(mul(exponent, logs[r])))
        result[0] = add(result[0], weight)
        result[1] = add(result[1], mul(weight, logs[r]))
        result[2] = add(result[2], mul(weight, mul(logs[r], logs[r])))
    return result


def minus(x, y):
    return rounded(x[0] - y[1], x[1] - y[0])


def numerical_gates(laws):
    logs = {r: log_integer(r) for r in sorted(set(laws['P']) | set(laws['W']))}
    t = F(9973, 10000), F(9974, 10000)
    alpha = F(9898, 10000), F(9899, 10000)
    a = logs[5]
    signs = []
    for endpoint in t:
        wm = moments(laws['W'], point(endpoint), logs)
        pm = moments(laws['P'], point(endpoint), logs)
        signs.append(minus(wm[0], pm[0]))
    need(signs[0][1] < 0 < signs[1][0], 'invoice endpoint signs')
    wm = moments(laws['W'], t, logs)
    pm = moments(laws['P'], t, logs)
    need(wm[1][0] > pm[1][1], 'invoice derivative')
    means = []
    for endpoint in alpha:
        z, first, _ = moments(laws['P'], point(endpoint), logs)
        means.append(div(first, z))
    need(means[0][1] < a[0] and means[1][0] > a[1], 'tilt endpoint signs')
    z, first, second = moments(laws['P'], alpha, logs)
    mean = div(first, z)
    variance = minus(div(second, z), mul(mean, mean))
    need(F(49, 25) < variance[0] and variance[1] < F(9, 4), 'variance gate')
    lam = minus(t, alpha)
    need(F(7, 1000) < lam[0] and lam[1] < F(8, 1000), 'lambda gate')
    need(a[1] < 2, 'offset gate')
    for r in laws['P']:
        centered = minus(logs[r], a)
        need(-F(5, 2) < centered[0] <= centered[1] < F(5, 2), 'support radius')
    # e^(1/2)<5/3 and e>5/2 imply both elementary exponential gates.
    need(exp_scalar(F(1, 2))[1] < F(5, 3), 'normal window density')
    need(exp_scalar(F(1))[0] > F(5, 2), 'window integral')
    return {'t': t, 'alpha': alpha, 'lambda': lam, 'variance': variance,
            'invoice_signs': signs, 'tilt_means': means}


def constants(depth=11000, factor=5, sigma_low=F(7, 5), be=F(14, 25)):
    need(depth >= 0 and factor > 0 and sigma_low > 0 and be > 0, 'gate domain')
    b_upper = be * F(5, 2) / sigma_low
    lower = F(1, 4) * F(3, 5) ** 2 * F(1000, 8) - 2 * b_upper
    upper = F(2, 7) * F(1000, 7) + 2 * b_upper
    threshold = ((2 + F(1000, 7)) / sigma_low) ** 2
    need(F(depth) >= threshold, 'depth window')
    need(lower > 0, 'positive denominator')
    need(upper <= factor * lower, 'tail constant')
    return {'depth': depth, 'factor': factor, 'b_upper': b_upper,
            'denominator_lower': lower, 'numerator_upper': upper,
            'threshold_upper': threshold, 'ratio_upper': upper / lower}


def finite_tilt_fixtures():
    count = 0
    # Integer-valued X with q=(1/2,1/2), p=(1/3,2/3), exp(lambda)=2.
    # These exact fixtures check the finite ratio and clipping identities.
    for g in range(1, 9):
        sums = [sum(word) for word in product((0, 1), repeat=g)]
        for barrier in range(g + 1):
            chosen = [s for s in sums if s <= barrier]
            pweights = [F(2 ** s, 3 ** g) for s in chosen]
            qweights = [F(2 ** s, 2 ** (g + barrier)) for s in chosen]
            for cut in range(barrier + 2):
                direct = sum((w for s, w in zip(chosen, pweights)
                              if barrier - s >= cut), F(0)) / sum(pweights)
                tilted = sum((w for s, w in zip(chosen, qweights)
                              if barrier - s >= cut), F(0)) / sum(qweights)
                need(direct == tilted, 'finite tilt factorization')
                clipped = sum((max(barrier - s - cut, 0) * w
                               for s, w in zip(chosen, pweights)), F(0))
                tail = sum(((barrier - s) * w
                            for s, w in zip(chosen, pweights)
                            if barrier - s >= cut), F(0))
                need(tail == cut * direct * sum(pweights) + clipped,
                     'clipping identity at atoms')
                count += 1
    return count


def controls(manifest):
    failures = 0
    trials = ({'depth': 10000}, {'factor': 4}, {'sigma_low': F(1)},
              {'be': F(2)}, {'depth': -1})
    for trial in trials:
        try:
            constants(**trial)
        except ValueError:
            failures += 1
        else:
            raise ValueError('invalid numerical certificate accepted')
    entry = next(e for e in manifest['files'] if e['usage'] == 'input')
    try:
        authenticate(b'changed scientific input', entry)
    except ValueError:
        failures += 1
    else:
        raise ValueError('changed source accepted')
    need(failures == 6, 'control coverage')
    return failures


def serialize(value):
    if isinstance(value, F):
        return str(value)
    raise TypeError('unsupported receipt value')


def main():
    laws, manifest = inputs()
    gates = numerical_gates(laws)
    bound = constants()
    fixtures = finite_tilt_fixtures()
    rejected = controls(manifest)
    names = ['PROOF.md', 'README.md', 'TASK.json', 'SOURCES.json',
             'VERIFY.json', 'verify.py']
    hashes = {name: hashlib.sha256((PACKAGE / name).read_bytes()).hexdigest()
              for name in names}
    print(json.dumps({'status': 'PASS_DIRECT_FLOW_FINITE_TAIL',
                      'gates': gates, 'bound': bound, 'finite_fixtures': fixtures,
                      'rejection_controls': rejected, 'package_sha256': hashes},
                     default=serialize, sort_keys=True, indent=2))


if __name__ == '__main__':
    main()
