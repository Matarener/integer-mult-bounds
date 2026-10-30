#!/usr/bin/env python3
"""Portable independent check of fixed public-window moment obstruction.

Only input fixture: source-context/global_k.py, exact historical source.
No producer module is imported or executed. Rational nth-root enclosures
use integer powers; no logarithms, exponentials or floating-point decisions.
The all-parameter proof is WINDOW-REVIEW.md, not this finite computation.
Apache-2.0; substantial OpenAI Codex assistance.
"""
import ast
from collections import Counter
from fractions import Fraction as Q
from functools import lru_cache
import hashlib
import json
from math import comb
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
SOURCE_SHA = '6368196a393ac25bb2918880e4c4bd31ed733b762c27b6873ab391cbc0c5c3c8'
PIN = '20ecf2891d80b5acf18d980b2164fb44ea7faa90'
SOURCE_PATH = 'research/e8-bit-p111-tuned/vendor/pr510/e8-r480-nine-stage/vendor/e8-r715-eleven-stage-whole/code/global_k.py'
H = {1:1322, 2:1342, 3:79, 4:39, 5:102, 6:11, 7:18}
C = sum(r*n for r, n in H.items())
SCALE = 10**18


def need(ok, message):
    if not ok:
        raise RuntimeError(message)


@lru_cache(None)
def root500(x):
    x = Q(x)
    need(x >= 1, 'positive root domain')
    target = x.numerator*pow(SCALE, 500)
    lo, hi = SCALE, 2*SCALE
    while pow(hi, 500)*x.denominator <= target:
        hi *= 2
    while hi-lo > 1:
        mid = (lo+hi)//2
        if pow(mid, 500)*x.denominator <= target:
            lo = mid
        else:
            hi = mid
    need(pow(lo, 500)*x.denominator <= target < pow(hi, 500)*x.denominator,
         'exact rational 500th root enclosure')
    return Q(lo, SCALE), Q(hi, SCALE)


def add(a, b):
    return a[0]+b[0], a[1]+b[1]


def scale(a, c):
    return (a[0]*c, a[1]*c) if c >= 0 else (a[1]*c, a[0]*c)


def local(m):
    out = Q(0), Q(0)
    for r, n in H.items():
        out = add(out, scale(root500(Q(m, r)), r*n))
    return out


def encoded(x):
    return list(map(str, x))


def source_context():
    raw = (HERE/'source-context/global_k.py').read_bytes()
    need(hashlib.sha256(raw).hexdigest() == SOURCE_SHA, 'frozen source SHA256')
    tree = ast.parse(raw)
    names = next(n for n in tree.body if isinstance(n, ast.Assign) and
                 any(isinstance(t, ast.Name) and t.id == 'NAMES' for t in n.targets))
    named_layouts = sorted(ast.literal_eval(names.value))
    need(named_layouts == [5, 7, 9, 11, 13], 'actual named producer layouts')
    # No source execution. These checks bind the three branches reviewed in
    # the all-K written argument to the pinned file, including elif tails.
    rules = [n for n in ast.walk(tree) if isinstance(n, ast.If) and
             ast.unparse(n.test) == 's % 2 == 1 and s <= 2 * K - 3']
    need(len(rules) == 1, 'unique public idle rule')
    first = rules[0]
    second = first.orelse[0]
    third = second.orelse[0]
    need(isinstance(second, ast.If) and
         ast.unparse(second.test) == 's % 2 == 0 and 2 <= s <= 2 * K - 2', 'middle idle rule')
    need(isinstance(third, ast.If) and ast.unparse(third.test) == 's == 2 * K', 'terminal idle rule')
    return {'scientific_pin': PIN, 'repository_path': SOURCE_PATH,
            'sha256': SOURCE_SHA, 'named_layouts': named_layouts,
            'source_execution': False,
            'all_odd_L_domain': 'written mathematical recipe extension; not a claim that the old CLI emits every L'}


def windows(L):
    K = (L-1)//2
    # Explicit enumeration of the three disjoint event families in the
    # source rule: early gaps, one-step gaps, terminal completions.
    early = [7*(s+1) for s in range(1, 2*K-2, 2)]
    middle = [7 for s in range(2, 2*K-1, 2)]
    terminal = [7*(2*K-(2*j+2)) for j in range(K)]
    actual = Counter(r for r in early+middle+terminal if r)
    expected = Counter({7: K-1})
    for j in range(1, K):
        expected[14*j] += 2
    need(+actual == +expected, 'all event families match closed formula')
    need(max(actual, default=0) == 7*(L-3), 'largest public idle rank')
    need(sum(r*n for r, n in actual.items()) == 7*(K-1)*L, 'total source idle rank')
    return dict(sorted(actual.items()))


def endpoint(L):
    m = 7*L+1
    w = Q(111*(L-1), L)
    t = 777*L-714
    qmin = max(Q(0), C-t)
    idle = t-C+qmin
    need(0 <= qmin <= 3484, 'required moved helper progress')
    need(t == 1554+63+777*(L-3), 'coverage from public local, COPY and idle progress')
    if idle == 0:
        # Includes L=3: no public idle window exists, so never divide by R=0.
        out = add(local(m), (-m*w-qmin,)*2)
    else:
        need(m > 22, 'positive public idle capacity')
        out = add(local(m), scale(root500(Q(m, m-22)), idle))
        out = add(out, (-m*w,)*2)
    need(out[0] > 0, 'fixed-window target failure')
    return {'L':L, 'm':m, 'qmin':str(qmin), 'remaining_public_idle_mass':str(idle),
            'max_public_idle_rank':m-22, 'excess':encoded(out)}


def main():
    if '--force-failure' in sys.argv:
        need(False, 'forced explicit window failure')
    need(C == 5101 and C == 1554+3484+63, 'local progress accounting')
    context = source_context()
    controls = {L:windows(L) for L in range(3, 102, 2)}
    cases = [endpoint(L) for L in (3,5,7,9,11,13)]
    b = Q(1,500)
    p = [-Q(111), -Q(777), 7*b*C]
    shifted = [sum(p[j]*comb(j,k)*13**(j-k) for j in range(k,3)) for k in range(3)]
    need(all(c > 0 for c in shifted), 'positive derivative for every real L>=13')
    need(shifted == [Q(928483,500), Q(269941,250), Q(35707,500)], 'independent polynomial values')
    native42 = add(local(64), scale(root500(Q(64,42)),1178))
    native42 = add(native42,(-Q(18944,3),)*2)
    calls = sum(H.values())+Q(1178,42)
    total42 = add(native42,scale(root500(Q(64)),Q(32*64**2,10**16)*calls))
    need(total42[0] > native42[0] > 0, 'rank42 native and fallback lower bounds')
    need(60 > max(map(int, controls[9])), 'rank60 lies outside every old nine-stage public window')
    out = {'status':'PASS_INDEPENDENT_FIXED_WINDOW_ALL_DEPTH_REVIEW',
           'input_context':context, 'b':'1/500', 'H':H, 'local_mass':C,
           'finite_transcription_cases':list(controls), 'nine_stage_idle_multiset':controls[9],
           'endpoint_cases':cases, 'derivative_coefficients_L_minus_13':list(map(str, shifted)),
           'nine_stage_native_excess':encoded(native42),
           'nine_stage_fallback_excess':encoded(total42),
           'rank60_public_window_rejected':True,
           'all_parameter_argument':'WINDOW-REVIEW.md: q minimization, concavity, polynomial derivative and monotonicity in b',
           'scope':'fixed stage/idle chronology, unchanged H and one-unpaid-coordinate coverage, any independent full-progress extra stock; no native admission',
           'arithmetic':'exact integer-power root bisection and Fraction; no floating decisions',
           'no_formal_kernel_proof':True, 'no_new_kappa':True}
    print(json.dumps(out, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
