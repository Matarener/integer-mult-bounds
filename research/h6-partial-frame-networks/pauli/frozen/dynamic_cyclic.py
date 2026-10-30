#!/usr/bin/env python3
"""Mutable cyclic readers: exact input transport and dirty cleanup.

Each reader accumulates successive source groups at nested frames, then
delivers once to the excluded group. Actual E8 cases r=2..7 only. No full
H6 arc network or improved kappa is inferred from conditional tariffs.
"""
from fractions import Fraction as F
from pathlib import Path
import importlib.util
import json

HERE = Path(__file__).resolve().parent


def load(name, file):
    spec = importlib.util.spec_from_file_location(name, HERE/file)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


c = load('dynamic_static_cyclic', 'cyclic_mixed.py')
m = c.m
b = load('dynamic_exact_budget', 'optimistic_budget.py')
need = m.need


def fixture(r):
    fix = c.fixture(r)
    n = fix['N']
    k = [[F(q) for q in row] for row in fix['K']]
    planes = [tuple(p) for p in fix['planes']]
    arc = {(g, depth): tuple(fix['arcs'][str(g)+':'+str(depth)])
           for g in range(r) for depth in range(1, r)}
    # L is now the cyclic all-but-excluded prefix accumulation. R sends
    # each final packet to only that excluded target pair.
    ell = [[F(0)]*n for _ in range(n)]
    decoder = [[F(0)]*n for _ in range(n)]
    for g in range(r):
        for depth in range(r-1):
            source = (g+depth) % r
            ell[2*g][2*source] = ell[2*g][2*source+1] = 1
            ell[2*g+1][2*source] = 1
            ell[2*g+1][2*source+1] = -1
        t = (g-1) % r
        for z in range(2):
            decoder[2*t+z][2*g] = -F(1, 8)
            decoder[2*t+z][2*g+1] = F(3 if z else -3, 16)
    need(all(sum(decoder[i][g]*ell[g][j] for g in range(n))
             == F(fix['C'][i][j]) for i in range(n) for j in range(n)),
         'dynamic exact coefficient identity C=R L')
    events = []

    def add(dst, src, q, tag):
        if q:
            events.append({'op': 'add', 'dst': dst, 'src': src,
                           'q': str(q), 'tag': tag})

    def climb(reg, frame, tag):
        events.append({'op': 'climb', 'register': reg,
                       'frame': list(frame), 'tag': tag})

    for t in range(n):
        for j in range(n):
            add(f'y{t}', f'h{j}', -decoder[t][j], 'comp_prefix')
            add(f'y{t}', f'c{j}', -k[t][j], 'K_prefix')
    # At depth0 each source pair and its reader pair meet at U_g.
    # At depth d>0 source group j visits F(j-d,d+1), including itself.
    # Its previous visit F(j-d+1,d) is a subspace of this new arc.
    for depth in range(r-1):
        for g in range(r):
            source = (g+depth) % r
            frame = arc[g, depth+1]
            for z in range(2):
                climb(f'x{2*source+z}', frame, 'source_read_arc')
                climb(f'h{2*g+z}', frame, 'mutable_reader_arc')
            for z in range(2):
                add(f'h{2*g}', f'x{2*source+z}', F(1), 'mutable_read')
                add(f'h{2*g+1}', f'x{2*source+z}', F(1 if z == 0 else -1), 'mutable_read')
    for i in range(n):
        climb(f'x{i}', m.FULL, 'source_full')
        climb(f'c{i}', m.FULL, 'K_center_full')
        add(f'c{i}', f'x{i}', F(1), 'K_gather')
    for j in range(n):
        events.append({'op': 'private', 'center': f'c{j}',
                       'targets': [[f'y{i}', str(k[i][j])] for i in range(n) if k[i][j]],
                       'tag': 'K_private'})
    for i in range(n):
        add(f'c{i}', f'x{i}', -F(1), 'K_restore')
    for g in range(r):
        t = (g-1) % r
        for z in range(2):
            climb(f'y{2*t+z}', arc[g, r-1], 'target_final_arc')
            for channel in range(2):
                add(f'y{2*t+z}', f'h{2*g+channel}',
                    decoder[2*t+z][2*g+channel], 'comp_scatter')
            climb(f'y{2*t+z}', tuple(fix['ends'][f'y{2*t+z}']), 'target_cap')
    for j in range(n):
        climb(f'h{j}', m.FULL, 'reader_restore_full')
        for i in range(n):
            add(f'h{j}', f'x{i}', -ell[j][i], 'comp_restore')
    fix.update(L=[[str(q) for q in row] for row in ell],
               R=[[str(q) for q in row] for row in decoder], events=events,
               mechanism='mutable cyclic prefix readers; one final delivery')
    return fix


def conditional_tariffs():
    rows = []
    for r in range(2, 8):
        source = [1]*(r-1)+[17-r]
        target = [r, 16-r]
        helper = [2]+[1]*(r-2)+[17-r]
        for L in range(3, 34, 2):
            row = b.model(L, source, target, helper, b.N)
            rows.append({'r': r, 'L': L, 'm': row['m'], 'q': row['q'],
                         'pad': row['pad'], 'source': source, 'target': target,
                         'helper': helper, 'R': b.N, 'stock_W': str(row['W']),
                         'K_ordinary_roles': b.KC, 'K_private_C': b.KBILL,
                         'coverage_deficit': row['D'],
                         'rank_histogram': {r: str(n) for r, n in sorted(row['H'].items())},
                         'targets': [dict(b.target_row(row, k),
                                          helper_boundary=b.helper_boundary(row, k))
                                     for k in map(F, ('.002', '.003', '.005'))]})
    return rows


def main():
    cases, controls = [], []
    for r in range(2, 8):
        fix = fixture(r)
        n = fix['N']
        forward, dual = m.replay(fix), m.replay(fix, True)
        need(forward['rank_mass'] == dual['rank_mass'] == 83*n,
             'whole dynamic word rank mass')
        need(forward['scalar_primitives_before_real_doubling'] == n*(54*r-1),
             'whole dynamic forward primitive bound')
        need(dual['scalar_primitives_before_real_doubling'] == n*(54*r+2),
             'whole dynamic dual primitive bound')
        independent = c.matrix_check(fix)
        for tag in ('mutable_read', 'comp_prefix', 'comp_scatter',
                    'comp_restore', 'K_private', 'source_read_arc',
                    'mutable_reader_arc', 'target_final_arc'):
            for inverse in (False, True):
                try:
                    m.replay(fix, inverse, tag)
                except ValueError as err:
                    controls.append({'r': r, 'omit': tag, 'dual': inverse,
                                     'gate': str(err)})
                else:
                    raise ValueError('meaningful dynamic defect accepted '+tag)
        cases.append({'r': r, 'N': n, 'C_rank': n, 'restricted_K_rank': n,
                      'ordinary_mutable_readers': n, 'compensation_private_rank': 0,
                      'source_path': [1]*(r-1)+[17-r],
                      'target_path': [r, 16-r],
                      'helper_path': [2]+[1]*(r-2)+[17-r],
                      'forward': forward, 'dual': dual,
                      'independent_operator_entries': independent, 'fixture': fix})
    tariffs = conditional_tariffs()
    out = {'status': 'PASS_ACTUAL_MUTABLE_CYCLIC_H6_READERS_NO_NEW_KAPPA',
           'source_pin': b.PIN, 'cases': cases, 'controls': controls,
           'conditional_full_H6_tariffs': tariffs,
           'limits': 'Actual E8 examples r=2..7,N=4..14. Sources really traverse the declared nested read arcs; targets stayZERO through K and have one final arc visit. Full subfamily K is rankN with private C=17N, so standalone coverage fails for every L. Full-domain tariff assumes an unconstructed common-frame incidence network using N such channels and the unchanged816-center full K. Pure-block couplings, whole H6 geometry, physical allocation, approximate-child precision and outer BIT closure remain unproved. Tariff passing is not a kappa claim.'}
    (HERE/'DYNAMIC-CYCLIC-RESULT.json').write_text(json.dumps(out, indent=2, sort_keys=True)+'\n')
    print(out['status']+' cases=6 controls='+str(len(controls)))
    for case in cases:
        print('r', case['r'], 'N', case['N'], 'rank', case['forward']['rank_mass'],
              'primitives', case['forward']['scalar_primitives_before_real_doubling'],
              case['dual']['scalar_primitives_before_real_doubling'])
    for r in (3, 7):
        candidates = [row for row in tariffs if row['r'] == r]
        for k in ('1/500', '3/1000', '1/200'):
            best = max(candidates,
                       key=lambda row: F(next(t for t in row['targets'] if t['target'] == k)['raw_slack']['lower']))
            t = next(t for t in best['targets'] if t['target'] == k)
            print('conditional r', r, 'target', k, 'bestL', best['L'],
                  'maxR', t['helper_boundary']['largest_nonnegative_R'],
                  'M', t['normalized_moment']['lo'])


if __name__ == '__main__':
    main()
