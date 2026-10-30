#!/usr/bin/env python3
"""Exact source/parameter/finite-law checks; does not mechanically prove the LLT.
DLamdata with substantial OpenAI Codex assistance. Apache-2.0.
"""
from fractions import Fraction as Q
from functools import lru_cache
from pathlib import Path
import argparse
import ast
import hashlib
import itertools
import json
import math
import runpy

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def need(ok, message):
    if not ok:
        raise ValueError(message)


# Rational intervals. No machine floating-point arithmetic in certification.
def add(a, b):
    return a[0] + b[0], a[1] + b[1]


def neg(a):
    return -a[1], -a[0]


def mul(a, b):
    v = [x * y for x in a for y in b]
    return min(v), max(v)


def div(a, b):
    need(b[0] > 0, 'positive denominator required')
    return mul(a, (1 / b[1], 1 / b[0]))


def pt(x):
    return Q(x), Q(x)


@lru_cache(None)
def log_bounds(n):
    """log(n) via 2 atanh(z), |z|<=1/3, with geometric tail."""
    need(isinstance(n, int) and n >= 1, 'positive integer log input')
    if n == 1:
        return pt(0)
    e = n.bit_length() - 1
    u = Q(n, 2 ** e)

    def series(z):
        total = sum((2 * z ** (2 * k + 1) / (2 * k + 1) for k in range(48)), Q(0))
        tail = 2 * z ** 97 / (97 * (1 - z * z))
        return total, total + tail

    return add(mul(pt(e), series(Q(1, 3))), series((u - 1) / (u + 1)))


@lru_cache(None)
def exp_point(x):
    """Taylor enclosure for 0<=x<=5; exp(x)<=3^5 bounds remainder."""
    need(0 <= x <= 5, 'exp domain [0,5]')
    term = total = Q(1)
    for k in range(1, 81):
        term = term * x / k
        total += term
    tail = Q(3 ** 5) * term * x / 81
    return total, total + tail


def exp_bounds(x):
    return exp_point(x[0])[0], exp_point(x[1])[1]


def power(n, t):
    return exp_bounds(mul(log_bounds(n), pt(t)))


def moment(hist, t, derivative=False):
    out = pt(0)
    for rank, count in hist.items():
        term = mul(pt(count), power(rank, t))
        if derivative:
            term = mul(term, log_bounds(rank))
        out = add(out, term)
    return out


def mean(hist, t):
    return div(moment(hist, t, True), moment(hist, t))


def rounded(a, places=12):
    scale = 10 ** places
    lo = a[0].numerator * scale // a[0].denominator
    hi = -((-a[1].numerator * scale) // a[1].denominator)
    def fmt(k):
        sign = '-' if k < 0 else ''
        k = abs(k)
        return f'{sign}{k // scale}.{k % scale:0{places}d}'
    return [fmt(lo), fmt(hi)]


def bindings():
    source = json.loads((HERE / 'SOURCES.json').read_text())
    for row in source['files']:
        if row['usage'] == 'input':
            need(hashlib.sha256((ROOT / row['path']).read_bytes()).hexdigest() == row['sha256'],
                 'source mismatch: ' + row['path'])
    path = ROOT / 'research/direct-flow-leaf-walk/verify.py'
    constants = {}
    for node in ast.parse(path.read_text()).body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            if node.targets[0].id in ('P', 'W', 'M'):
                constants[node.targets[0].id] = ast.literal_eval(node.value)
    need(set(constants) == {'P', 'W', 'M'}, 'source constants missing')
    return constants['P'], constants['W'], constants['M']


def parameters(P, W, M):
    t = (Q('0.99731351095114'), Q('0.99731351095116'))
    alpha = (Q('0.98981438244597'), Q('0.98981438244599'))
    # Positive derivative on the full source bisection interval identifies its root.
    f_lo = add(moment(W, t[0]), neg(moment(P, t[0])))
    f_hi = add(moment(W, t[1]), neg(moment(P, t[1])))
    derivative = add(moment(W, Q('0.99'), True), neg(moment(P, Q(1), True)))
    need(f_lo[1] < 0 < f_hi[0] and derivative[0] > 0, 'invoice root bracket')
    a = log_bounds(5)
    need(mean(P, alpha[0])[1] < a[0] and mean(P, alpha[1])[0] > a[1], 'tilt mean bracket')
    mu = mean(P, t[0])[0], mean(P, t[1])[1]  # mean strictly increases: derivative=variance>0.
    drift = add(mu, neg(a))
    need(drift[0] > 0, 'positive drift')
    need(all(P.get(k, 0) > 0 for k in (1, 2, 3)), 'nonlattice support witness 1,2,3')
    lam = add(t, neg(alpha))
    inverse = div(pt(1), lam)
    depth = add(add(log_bounds(M), neg(mu)), inverse)
    return {'t_star': rounded(t, 14), 'alpha': rounded(alpha, 14),
            'lambda': rounded(lam, 14), 'mean_log_rank': rounded(mu),
            'invoice_derivative_lower_bound_interval_0_99_to_1': rounded(derivative, 6),
            'drift_above_log5': rounded(drift), 'mean_deficit_limit': rounded(inverse, 8),
            'mean_leaf_depth_limit': rounded(depth, 8),
            'method': 'exact Fraction arithmetic, log atanh48 and exp Taylor80 with positive remainder bounds'}


def finite_law(P, W, M):
    # Independent ordered-word enumeration vs the predecessor's whole-flow X-BX.
    flow = runpy.run_path(str(ROOT / 'research/direct-flow-leaf-walk/diagnostics/overlap_flow.py'))['flow']
    count = 0
    terminal_cut_distinguishing_fixtures = 0
    for G in range(4):
        for N in (M * 5 ** G, M * 5 ** G + M * 5 ** G // 2):
            got = flow(N, W, P)
            need(got['G'] == G, 'flow depth')
            prefixes = {}
            for word in itertools.product(P, repeat=G):
                rho = math.prod(word)
                if M * rho <= N:
                    prefixes[rho] = prefixes.get(rho, 0) + math.prod(P[r] for r in word)
            leaves, wrong = {}, {}
            for rho, multiplicity in prefixes.items():
                for r, pr in P.items():
                    e = rho * r
                    leaves[e] = leaves.get(e, 0) + multiplicity * pr
                    if M * e <= N:
                        wrong[e] = wrong.get(e, 0) + multiplicity * pr
            actual = {e: c - got['BX'].get(e, 0) for e, c in got['X'].items() if c != got['BX'].get(e, 0)}
            need(actual == leaves, 'ordered words disagree with actual leaf exits')
            # This checks fixture sensitivity, not an additional source identity.
            # Source coverage is the complete actual==leaves comparison above.
            terminal_cut_distinguishing_fixtures += wrong != leaves
            count += 1
    need(terminal_cut_distinguishing_fixtures > 0, 'no fixture distinguishes terminal truncation')
    return {'whole_flow_fixtures': count, 'ordered_word_max_depth': 3,
            'terminal_cut_distinguishing_fixtures': terminal_cut_distinguishing_fixtures,
            'source_check': 'complete actual X-BX histogram equals ordered-word enumeration'}


def controls():
    # Lattice countermodel: X in {0,log2}, p(X=log2)=2/3, barrier n log2/2.
    # At even n the limiting gap/log2 is geometric with mean 1, whereas
    # the nonlattice formula would give mean gap=1 (lambda=1).
    means = []
    for n in (40, 400):
        denominator = sum(math.comb(n, k) * 2 ** k for k in range(n // 2 + 1))
        numerator = sum((n // 2 - k) * math.comb(n, k) * 2 ** k for k in range(n // 2 + 1))
        means.append(Q(numerator, denominator))
    need(0 < means[0] < means[1] < 1, 'lattice geometric control')
    need(mul(pt(means[1]), log_bounds(2))[1] < Q(7, 10), 'lattice mean must differ from exponential mean 1')
    rejected = 0
    for f in (lambda: div(pt(1), (-Q(1), Q(1))), lambda: exp_point(Q(-1)), lambda: log_bounds(0)):
        try:
            f()
        except ValueError:
            rejected += 1
    need(rejected == 3, 'interval domain controls')
    # Elementary exact enclosure controls include endpoint exp0/log1 identities.
    need(log_bounds(1) == pt(0) and exp_point(Q(0)) == pt(1), 'identity fixtures')
    need(log_bounds(2)[0] > Q(69, 100) and log_bounds(2)[1] < Q(7, 10), 'log2 fixture')
    return {'lattice_countermodel': 'geometric mean gap/log2 tends to 1; finite n=400 gap<0.7, not exponential mean1',
            'interval_domain_rejections': rejected}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--expect', type=Path)
    args = parser.parse_args()
    P, W, M = bindings()
    result = {'status': 'PASS_DIRECT_FLOW_LEAF_SATURATION_CHECKS', 'parameters': parameters(P, W, M),
              'finite_law': finite_law(P, W, M), 'controls': controls(),
              'scope': 'Source identity, rigorous numerical hypotheses and finite controls only; see PROOF.md for classical-LLT-based theorem. No finite-depth rate, total-flow ceiling or new kappa.'}
    if args.expect:
        need(result == json.loads(args.expect.read_text()), 'expected receipt mismatch')
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
