#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Construct exact contraction or noncontraction witnesses for A >= 0.

Classical nonsingular M-matrix alternative and sign-preserving elimination.
Project precedents: window-comparison-barrier and coupled-comparison-barrier.
Prepared for Ali Romman with substantial OpenAI Codex assistance.
"""
import argparse
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path
import re
import sys
from compare_recursive_invoices import _pairs, _integer, _not_integer, require


def rational(x):
    require(type(x) is int or type(x) is str and len(x) <= 4096
            and re.fullmatch(r'-?[0-9]+(?:/[1-9][0-9]*)?', x, re.ASCII), 'Use integer or rational strings')
    return Q(x)


def encode_rational(q):
    require(max(abs(q.numerator).bit_length(), q.denominator.bit_length()) <= 6000,
            'Exact certificate exceeds the 6000-bit rational budget')
    return str(q)


def read(path):
    with Path(path).open('rb') as f: raw = f.read(2*1024**2+1)
    require(len(raw) <= 2*1024**2, 'Input exceeds 2 MiB')
    return json.loads(raw, object_pairs_hook=_pairs, parse_int=_integer,
                      parse_float=_not_integer, parse_constant=_not_integer), sha256(raw).hexdigest()


def validate(value):
    require(type(value) is dict and value.keys() == {'schema', 'matrix', 'forcing'}
            and value['schema'] == 'coupled-recurrence/v1', 'Invalid recurrence problem')
    matrix, forcing = value['matrix'], value['forcing']
    require(type(matrix) is list and 1 <= len(matrix) <= 64, 'Use 1..64 types')
    n = len(matrix)
    require(all(type(row) is list and len(row) == n for row in matrix), 'Matrix must be square')
    require(type(forcing) is list and len(forcing) == n, 'Wrong forcing size')
    a = [[rational(x) for x in row] for row in matrix]; b = [rational(x) for x in forcing]
    require(all(0 <= x and x.numerator <= 10**12 and x.denominator <= 10**12
                for row in a+[b] for x in row), 'Coefficients must be nonnegative bounded rationals')
    return a, b


def product(a, v): return [sum((x*y for x,y in zip(row,v)), Q(0)) for row in a]


def backsolve(rows, rhs, size):
    x = [Q(0)]*size
    for i in reversed(range(size)):
        x[i] = (rhs[i]-sum((rows[i][j]*x[j] for j in range(i+1,size)), Q(0)))/rows[i][i]
    return x


def certify(value):
    a, b = validate(value); n = len(a)
    rows = [[Q(i == j)-a[i][j] for j in range(n)]+[Q(1),b[i]] for i in range(n)]
    for k in range(n):
        if rows[k][k] <= 0:
            v = backsolve(rows, [-rows[i][k] for i in range(k)], k)+[Q(1)]+[Q(0)]*(n-k-1)
            result = {'schema': 'coupled-recurrence-certificate/v1', 'status': 'noncontracting',
                      'witness': list(map(encode_rational,v))}
            verify(value,result); return result
        for i in range(k+1,n):
            factor = rows[i][k]/rows[k][k]
            for j in range(k,n+2): rows[i][j] -= factor*rows[k][j]
    w = backsolve(rows,[row[n] for row in rows],n)
    total = backsolve(rows,[row[n+1] for row in rows],n)
    aw = product(a,w); ratio = max(x/y for x,y in zip(aw,w))
    result = {'schema': 'coupled-recurrence-certificate/v1', 'status': 'contracting',
              'weights': list(map(encode_rational,w)), 'ratio': encode_rational(ratio), 'total': list(map(encode_rational,total))}
    verify(value,result); return result


def verify(value, result):
    """Check only exact matrix-vector inequalities and the fixed-point equation."""
    a, b = validate(value); n = len(a)
    require(type(result) is dict and result.get('schema') == 'coupled-recurrence-certificate/v1', 'Invalid certificate')
    def vector(name):
        raw = result.get(name)
        require(type(raw) is list and len(raw) == n, 'Invalid '+name+' vector')
        return [rational(x) for x in raw]
    if result.get('status') == 'noncontracting':
        v = vector('witness')
        require(all(x >= 0 for x in v) and any(v), 'Witness must be nonzero and nonnegative')
        require(all(x >= y for x,y in zip(product(a,v),v)), 'No noncontraction witness')
        return True
    require(result.get('status') == 'contracting', 'Invalid status')
    w, total = vector('weights'), vector('total'); q = rational(result.get('ratio'))
    require(all(x > 0 for x in w) and 0 <= q < 1, 'Invalid positive weights or ratio')
    require(all(x <= q*y for x,y in zip(product(a,w),w)), 'False contraction bound')
    require(all(x >= 0 for x in total)
            and all(x == y+z for x,y,z in zip(total, product(a,total),b)), 'Wrong total work vector')
    return True


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument('problem'); parser.add_argument('--check')
    args = parser.parse_args(argv)
    try:
        value,digest = read(args.problem)
        if args.check:
            result,_ = read(args.check)
            require(type(result) is dict and result.get('input_sha256') == digest, 'Problem bytes changed')
            verify(value,result); print('PASS_COUPLED_RECURRENCE_CERTIFICATE')
        else:
            result=certify(value);result['input_sha256']=digest;print(json.dumps(result,indent=2,sort_keys=True))
    except (OSError,ValueError,TypeError,KeyError,RecursionError,ZeroDivisionError) as exc:
        print(str(exc),file=sys.stderr);return 2
    return 0


if __name__ == '__main__':raise SystemExit(main())
