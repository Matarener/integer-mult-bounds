#!/usr/bin/env python3
"""Exploratory fractional pattern LP for the proposed three-pair controller.

This enforces aggregate stage/width demand and actual window rank capacities.
It does not supply an integer clock, family-injective assignment or theorem.
Apache-2.0; substantial OpenAI Codex assistance.
"""
from collections import Counter
from fractions import Fraction as F
from pathlib import Path
import importlib.util
import json
import numpy as np
from scipy.optimize import linprog
from scipy.sparse import lil_matrix


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
WINDOWS = [(16, (0, 1)), (8, (2,)), (32, (0, 1, 2, 3)),
           (8, (4,)), (32, (3, 4, 5, 6)), (16, (5, 6))]
WIDTHS = tuple(range(4, 10))
DEMAND = {4: 26, 5: 2, 6: 18, 7: 53, 8: 96, 9: 213}


def patterns(cap):
    out = []
    def rec(i, rem, counts):
        if i == len(WIDTHS):
            out.append((tuple(counts), rem))
            return
        for count in range(rem//WIDTHS[i]+1):
            rec(i+1, rem-count*WIDTHS[i], counts+[count])
    rec(0, cap, [])
    return out


def main():
    path = REPO/'research/kappa-global-continuation/invoice-analysis/invoice.py'
    spec = importlib.util.spec_from_file_location('p3_invoice', path)
    I = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(I)
    variables = []
    for group, (cap, stages) in enumerate(WINDOWS):
        variables += [('pattern', group, counts, rem) for counts, rem in patterns(cap)]
        variables += [('supply', group, stage, width) for stage in stages for width in WIDTHS]
    # Rows: group bin counts6; group-width balance36; stage-width demand42.
    A = lil_matrix((84, len(variables)), dtype=float)
    rhs = np.zeros(84)
    rhs[:6] = 224
    for stage in range(7):
        for wi, w in enumerate(WIDTHS):
            rhs[42+6*stage+wi] = DEMAND[w]
    objective = np.zeros(len(variables))
    a = float(I.TARGET)
    for col, item in enumerate(variables):
        if item[0] == 'pattern':
            _, group, counts, rem = item
            A[group, col] = 1
            for wi, count in enumerate(counts):
                A[6+6*group+wi, col] = count
            objective[col] = rem**(1-a)-rem if rem else 0
        else:
            _, group, stage, width = item
            wi = width-4
            A[6+6*group+wi, col] = -1
            A[42+6*stage+wi, col] = 1
    lp = linprog(objective, A_eq=A.tocsr(), b_eq=rhs, bounds=(0, None), method='highs')
    result = {'status': 'P3_FLOATING_PATTERN_LP_OPTIMAL' if lp.success else 'P3_FLOATING_PATTERN_LP_FAILED',
              'windows': [{'rank': c, 'eligible_stages': list(st), 'bins_per_replica': 224} for c, st in WINDOWS],
              'width_demand_per_stage': DEMAND, 'variables': len(variables), 'equations': 84,
              'solver_status': int(lp.status), 'solver_message': lp.message,
              'scope': 'Exploratory floating-point aggregate pattern LP. No actual clock or physical owner assignment. A rational reconstruction is required for a certified feasibility or price statement.'}
    if lp.success:
        reconstructed = [F(float(x)).limit_denominator(10**6) for x in lp.x]
        residual = [F(0) for _ in range(84)]
        for col, item in enumerate(variables):
            x = reconstructed[col]
            if not x:
                continue
            if item[0] == 'pattern':
                _, group, counts, rem = item
                residual[group] += x
                for wi, count in enumerate(counts):
                    residual[6+6*group+wi] += x*count
            else:
                _, group, stage, width = item
                residual[6+6*group+width-4] -= x
                residual[42+6*stage+width-4] += x
        exact_rhs = list(map(lambda x: F(int(x)), rhs))
        feasible = residual == exact_rhs and min(reconstructed) >= 0
        result['rational_primal_equalities_pass'] = feasible
        result['nonzero_variables'] = [{'variable': v, 'count': str(x)} for v, x in zip(variables, reconstructed) if x]
        if feasible:
            idle = Counter()
            for item, x in zip(variables, reconstructed):
                if item[0] == 'pattern' and item[3] and x:
                    idle[item[3]] += x
            h = Counter({r: 7*n for r, n in I.LOCAL.items()})
            h.update(idle)
            I.need(sum(r*n for r, n in idle.items()) == 2142, 'actual remaining idle mass')
            I.need(sum(r*n for r, n in h.items()) == 38080, 'complete proposed raw invoice')
            result['idle_profile'] = {str(r): str(n) for r, n in sorted(idle.items())}
            result['profile_root'] = I.root(h, 57, 672)
            result['target_residual'] = I.interval(*(v-1 for v in I.moment(h, 57, 672, I.TARGET)))
            result['bit_cap_residual'] = I.interval(*(v-1 for v in I.moment(h, 57, 672, I.BIT_ROOT)))
            result['scope'] += ' The reconstructed primal satisfies all84 aggregate equations exactly; its root is rigorously priced. This still proves no actual hosting, and no exact dual optimality is claimed.'
    (HERE/'P3-PATTERN-SCREEN.json').write_text(json.dumps(result, indent=2)+'\n')
    print(result['status'], 'exact primal', result.get('rational_primal_equalities_pass'),
          'root', result.get('profile_root', {}).get('decimal'), 'idle', result.get('idle_profile'))


if __name__ == '__main__':
    main()
