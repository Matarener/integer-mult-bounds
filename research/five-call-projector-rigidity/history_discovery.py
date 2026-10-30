"""Test exact Gaussian extraction from all completed caller prefixes.

Each saved prefix is owned work. Only the original n independent inputs
can receive productive target credit. This is a local algebraic screen.
"""
import argparse
import json
from pathlib import Path
import time
import sympy as s
from exact_replay import canonical


def advance(word, p, t):
    old = [t*x for x in word]
    complement = s.eye(p.rows)-p
    return [complement*old[0]] + [complement*old[i]+p*old[i-1]
                                  for i in range(1, len(old))] + [p*old[-1]]


def search(path):
    started = time.monotonic()
    data = json.loads(path.read_text())
    n = data['n']
    ps = [s.Matrix([[s.Rational(x) for x in row] for row in p]) for p in data['projectors']]
    ps = [ps[0]] + ps + [ps[-1]]
    ts = [s.Matrix(t) for t in canonical(n)[2]]
    ident = s.eye(n)
    if advance([ident], ident, ident) != [s.zeros(n), ident]:
        raise ValueError('The stage variable control fails: a full stage is z I')
    plus, minus = [ident], [ident]
    records = [(plus.copy(), minus.copy())]
    for p, t in zip(ps, ts):
        plus, minus = advance(plus, p, ident), advance(minus, p, t)
        records.append((plus, minus))
    degree = max(i for i, a in enumerate(plus) if a != s.zeros(n))
    rows = []
    for plus, minus in records:
        both = [plus + [s.zeros(n)]*(degree+1-len(plus)),
                minus + [s.zeros(n)]*(degree+1-len(minus))]
        for row in range(n):
            rows.append([x for sign in [1, -1] for i in range(degree+1)
                         for x in (both[0][i]+sign*both[1][i]).row(row)])
    histories = s.Matrix(rows)
    spaces = []
    for e in range(degree+1):
        good = list(range((degree+1+e)*n, (degree+2+e)*n))
        bad = [j for j in range(histories.cols) if j not in good]
        ordered = histories[:, bad+good]
        reduced, _ = ordered.rref()
        vectors = [row[-n:] for row in reduced.tolist()
                   if not any(row[:-n]) and any(row[-n:])]
        spaces.append({'degree': e, 'dimension': len(vectors),
                       'basis': [[str(x) for x in row] for row in vectors]})
        print(json.dumps({'n': n, 'degree': e, 'dimension': len(vectors)}), flush=True)
    if n == 6 and [x['dimension'] for x in spaces] != [0, 0, 2, 0, 0, 0]:
        raise ValueError('The fixed six-field history control fails')
    return {'n': n, 'full_calls': n//2+2, 'thin_calls': n//2-1,
            'coefficient_variable': 'z',
            'saved_history_rows': histories.rows, 'spaces': spaces,
            'seconds': time.monotonic()-started, 'new_kappa': False}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--projectors', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    result = search(args.projectors)
    args.output.write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps({k: v for k, v in result.items() if k != 'spaces'}), flush=True)
