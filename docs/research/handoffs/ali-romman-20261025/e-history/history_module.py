"""Screen retained paid values in the published small E caller.

This uses the group algebra of four coordinate Gaussians and axis
permutations. It does not replace the actual 112^3-owner native word.
"""
import hashlib
import argparse
import itertools
import json
import time
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
MOD = 65521
PERMS = list(itertools.permutations(range(4)))
PID = {p: i for i, p in enumerate(PERMS)}
ID = PID[(0, 1, 2, 3)]
COMPOSE = [[PID[tuple(a[b[k]] for k in range(4))] for b in PERMS]
           for a in PERMS]


def scalar(num, den=1):
    return num*pow(den, -1, MOD) % MOD if MOD else Fraction(num, den)


def norm(value):
    return value % MOD if MOD else value


def move(e, p):
    out = 0
    for i in range(4):
        out |= ((e >> (2*i)) & 3) << (2*p[i])
    return out


MOVED = [[move(e, p) for e in range(256)] for p in PERMS]


def plus_exp(a, b):
    return sum((((a >> (2*i)) + (b >> (2*i))) & 3) << (2*i)
               for i in range(4))


def atom(src, e, p):
    return (src*256+e)*24+p


def unpack(k):
    q, p = divmod(k, 24)
    src, e = divmod(q, 256)
    return src, e, p


def left(row, e, p):
    out = {}
    for k, c in row.items():
        src, f, q = unpack(k)
        z = atom(src, plus_exp(e, MOVED[p][f]), COMPOSE[p][q])
        out[z] = norm(out.get(z, 0)+c)
    return {k: c for k, c in out.items() if c}


def linear(a, b, c):
    out = dict(a)
    for k, v in b.items():
        out[k] = norm(out.get(k, 0)+c*v)
        if not out[k]:
            del out[k]
    return out


def operator(name):
    if name.startswith('X'):
        q, s = map(int, name[1:].split('_'))
        return 2*((q & 1) | ((q >> 1) << (2*s))), ID
    if name.startswith('P'):
        s = int(name[1:]); p = list(range(4)); p[0], p[s] = p[s], p[0]
        return 0, PID[tuple(p)]
    if name.startswith('C0'):
        return 1, ID
    if name.startswith('C1'):
        return 1 << (2*int(name[2:])), ID
    if name.startswith('R'):
        return 1+(1 << (2*int(name[1:]))), ID
    if name.startswith('I'):
        return 0, ID
    raise ValueError(name)


def source(program=None):
    data = (HERE/'N3-PROGRAM.json').read_bytes() if program is None else json.dumps(program).encode()
    program = json.loads(data)
    fields = ['X0', 'X1', 'Y0', 'Y1']
    vals = {f: {atom(i, 0, ID): 1} for i, f in enumerate(fields)}
    history = [('input_'+f, vals[f]) for f in fields]
    for j, e in enumerate(program):
        op = e[0]
        if op == 'OWN_ZERO':
            vals[e[1]] = {}
        elif op == 'COPY':
            vals[e[1]] = dict(vals[e[2]])
        elif op == 'CLEAR':
            vals[e[1]] = {}
        elif op == 'SWAP':
            vals[e[1]], vals[e[2]] = vals[e[2]], vals[e[1]]
        elif op == 'SCALE':
            c = scalar(e[2], e[3])
            vals[e[1]] = {k: norm(v*c) for k, v in vals[e[1]].items() if norm(v*c)}
        elif op == 'ADD':
            c = scalar(e[3], e[4])
            vals[e[1]] = linear(vals[e[1]], left(vals[e[2]], *operator(e[5])), c)
        else:
            assert op in ('PAID', 'MONO')
            vals[e[1]] = left(vals[e[1]], *operator(e[2]))
            if op == 'PAID':
                history.append((f'paid_{j}_{e[1]}_{e[2]}', dict(vals[e[1]])))
    targets = [{atom(src, 85, ID): 1} for src in range(4)]
    for src, f in enumerate(fields[2:], start=2):
        if vals[f] != targets[src]:
            raise ValueError('The positive endpoint does not replay in the group algebra')
    return history, targets, hashlib.sha256(data).hexdigest()


def project(row, chi, perm):
    out = {}
    for k, v in row.items():
        src, e, p = unpack(k)
        e = MOVED[perm][e]
        r = sum(((e >> (2*i)) & 1) << i for i in range(4))
        t = sum(((e >> (2*i+1)) & 1) << i for i in range(4))
        z = (src*16+r)*24+COMPOSE[perm][p]
        if (chi & t).bit_count() % 2:
            v = -v
        out[z] = norm(out.get(z, 0)+v)
    return {k: v for k, v in out.items() if v}


def insert(row, pivots):
    row = dict(row)
    while row:
        k = min(row)
        if k not in pivots:
            inv = pow(row[k], -1, MOD) if MOD else Fraction(1)/row[k]
            pivots[k] = {j: norm(v*inv) for j, v in row.items()}
            return True
        row = linear(row, pivots[k], -row[k])
    return False


def residue(row, pivots):
    row = dict(row)
    while row:
        k = min(row)
        if k not in pivots:
            break
        row = linear(row, pivots[k], -row[k])
    return row


def main():
    global MOD
    ap = argparse.ArgumentParser()
    ap.add_argument('--exact', action='store_true')
    args = ap.parse_args()
    if args.exact:
        MOD = None
    start = time.monotonic()
    history, targets, sha = source()
    results = []
    for weight in range(5):
        chi = (1 << weight)-1
        pivots = {}
        for name, row in history:
            for p in range(24):
                insert(project(row, chi, p), pivots)
        residuals = [residue(project(t, chi, ID), pivots) for t in targets]
        if any(residuals[2:]):
            raise ValueError('The already decoded positive targets must be in the history module')
        control = dict(pivots)
        for t in targets[:2]:
            for p in range(24):
                insert(project(t, chi, p), control)
        if any(residue(project(t, chi, ID), control) for t in targets):
            raise ValueError('The added full-Gaussian positive control failed')
        one_axis = dict(pivots)
        for name, row in history:
            for axis in range(4):
                query = left(row, 1 << (2*axis), ID)
                for p in range(24):
                    insert(project(query, chi, p), one_axis)
        one_axis_targets = dict(one_axis)
        for t in targets[:2]:
            for p in range(24):
                insert(project(t, chi, p), one_axis_targets)
        rec = {'translation_character_weight': weight, 'projected_rank': len(pivots),
               'target_in_span': [not r for r in residuals],
               'residual_term_counts': list(map(len, residuals)),
               'full_Gaussian_control_rank': len(control),
               'all_one_axis_query_rank': len(one_axis),
               'one_axis_plus_target_rank': len(one_axis_targets),
               'one_axis_query_target_in_span': [not residue(project(t, chi, ID), one_axis)
                                                  for t in targets]}
        results.append(rec)
        print(json.dumps(rec), flush=True)
    result = {'status': 'EXACT_RATIONAL_HISTORY_SCREEN' if args.exact else 'MODULAR_HISTORY_SCREEN', 'prime': MOD,
              'source_pr': 5464, 'source_head': '56ba6d7d609124d71c067d6a380caed573963f8f',
              'source_program_sha256': sha, 'saved_rows': len(history),
              'max_row_terms': max(map(lambda x: len(x[1]), history)),
              'results': results, 'seconds': time.monotonic()-start,
              'scope': 'Small four-axis, four-input fixture in the specified group algebra. Every paid result and original input is retained. The left ordinary alphabet is translations and axis permutations. No actual large E8 caller, general physical lower bound, paid improvement, or kappa claim.'}
    name = 'history_module_exact.json' if args.exact else 'history_module.json'
    (HERE/name).write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps({k: v for k, v in result.items() if k != 'results'}), flush=True)


if __name__ == '__main__':
    main()
