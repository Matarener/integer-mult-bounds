#!/usr/bin/env python3
"""Unrestricted actual-width pattern screen for generalized paired chains.

Column generation uses an exact integer knapsack state space and floating
dual prices. Emitted primal coefficients are reconstructed as rationals and
checked exactly; no floating dual is represented as a proof of optimality.
With --guard actual, remainder children satisfy the true strict condition
2r^2<m^2. With --guard native, all native remainders are granted unsplit,
an optimistic relaxation that can also bound every permitted splitting.
Apache-2.0; substantial OpenAI assistance. See README for source credit.
"""
from argparse import ArgumentParser
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import json
import math
import numpy as np
from scipy.optimize import linprog

WIDTHS = (4, 5, 6, 7, 8, 9)
DEMAND = (26, 2, 18, 53, 96, 213)
LOCAL = {1:2440, 2:725, 3:224, 4:102, 5:20, 8:8}


def split(left, cap):
    return [cap]*(left//cap)+([left % cap] if left % cap else [])


def price(left, cap, a):
    return sum(r**(1-a) for r in split(left, cap))


def knapsack(dual, maximum):
    values = [-math.inf]*(maximum+1)
    counts = [None]*(maximum+1)
    values[0], counts[0] = 0., (0,)*6
    for used in range(1, maximum+1):
        for wi, width in enumerate(WIDTHS):
            if used >= width and counts[used-width] is not None:
                candidate = values[used-width]+dual[wi]
                if candidate > values[used]:
                    value = list(counts[used-width])
                    value[wi] += 1
                    values[used], counts[used] = candidate, tuple(value)
    return values, counts


def floating_root(profile, m, fields):
    lo, hi = 0., .01
    for _ in range(70):
        a = (lo+hi)/2
        if sum(float(n)*(r/m)**(1-a) for r, n in profile.items()) < fields:
            lo = a
        else:
            hi = a
    return [lo, hi]


def solve(pairs, a, out, guard='native'):
    m, calls, fields = 16*pairs+9, 2*pairs+1, 224*pairs
    bins = {8:224*(pairs-1)} | {16*q:448 for q in range(1, pairs)}
    actual_cap = math.isqrt((m*m-1)//2)
    cap = max(bins) if guard == 'native' else actual_cap
    ranks = sorted(bins)
    demand = [calls*n for n in DEMAND]
    rhs = np.array([bins[r] for r in ranks]+demand, dtype=float)
    stock = sum(r*n for r, n in bins.items())
    credit = sum(w*n for w, n in zip(WIDTHS, demand))
    result = dict(pairs=pairs, dimension=m, calls=calls, productive_fields=fields,
                  priced_child_rank_cap=cap, actual_permitted_child_rank_cap=actual_cap,
                  rank_guard_relaxation=guard, native_idle_histogram=bins,
                  native_idle_mass=stock, helper_credit=credit,
                  remainder_mass=stock-credit, nominal_raw_deficit=96*pairs-64,
                  local_profile=LOCAL, helper_width_inventory=dict(zip(WIDTHS, DEMAND)),
                  scope='Unrestricted bin-pattern relaxation; no stage-window, chronological owner, family injection, or complete outer admission is claimed.')
    if stock < credit:
        result.update(status='EXACT_RAW_HELPER_CAPACITY_OBSTRUCTION', exact_shortfall=credit-stock)
        return result
    columns, seen = [], set()
    def add(rank, counts):
        item = (rank, counts)
        if item not in seen:
            columns.append(item)
            seen.add(item)
    for r in ranks:
        add(r, (0,)*6)
        for wi, width in enumerate(WIDTHS):
            counts = [0]*6
            counts[wi] = r//width
            add(r, tuple(counts))
    convergence = []
    final = None
    for iteration in range(300):
        # Artificial unmet-demand variables make the initial master feasible.
        # Their large cost is a search device; they must all vanish at admission.
        A = np.zeros((len(rhs), len(columns)+6), dtype=float)
        costs = np.full(len(columns)+6, 1e6)
        for j, (r, counts) in enumerate(columns):
            A[ranks.index(r), j] = 1
            A[len(ranks):, j] = counts
            left = r-sum(w*n for w, n in zip(WIDTHS, counts))
            costs[j] = price(left, cap, a)
        for wi in range(6):
            A[len(ranks)+wi, len(columns)+wi] = 1
        lp = linprog(costs, A_eq=A, b_eq=rhs, bounds=(0, None), method='highs')
        if not lp.success:
            raise ValueError('restricted master failed: '+lp.message)
        dual = lp.eqlin.marginals
        values, options = knapsack(dual[len(ranks):], max(ranks))
        added, reduced = 0, []
        for ri, r in enumerate(ranks):
            candidate = min((price(r-used, cap, a)-values[used]-dual[ri], used)
                            for used in range(r+1) if options[used] is not None)
            reduced.append(candidate[0])
            if candidate[0] < -1e-8 and (r, options[candidate[1]]) not in seen:
                add(r, options[candidate[1]])
                added += 1
        convergence.append(dict(iteration=iteration, columns=len(columns), added=added,
                                artificial_sum=float(sum(lp.x[-6:])), minimum_reduced_cost=min(reduced)))
        if not added:
            final = lp
            break
    if final is None:
        raise ValueError('column-generation iteration cap')
    result.update(column_generation_iterations=len(convergence), column_count=len(columns),
                  floating_minimum_reduced_cost=convergence[-1]['minimum_reduced_cost'],
                  floating_artificial_sum=convergence[-1]['artificial_sum'],
                  floating_dual=list(map(float, final.eqlin.marginals)))
    if max(final.x[-6:]) > 1e-7:
        result.update(status='FLOATING_PATTERN_CAPACITY_FAILURE', convergence=convergence)
        return result
    rational = [Q(float(x)).limit_denominator(10**7) for x in final.x[:len(columns)]]
    obtained = [Q(0)]*len(rhs)
    idle = Counter()
    selection = []
    for (r, counts), n in zip(columns, rational):
        if not n:
            continue
        obtained[ranks.index(r)] += n
        for wi, count in enumerate(counts):
            obtained[len(ranks)+wi] += n*count
        left = r-sum(w*k for w, k in zip(WIDTHS, counts))
        for child in split(left, cap):
            idle[child] += n
        selection.append(dict(rank=r, counts=counts, count=str(n), unsplit_remainder=left,
                              priced_remainder_children=split(left, cap)))
    exact = obtained == list(map(lambda x:Q(int(x)), rhs)) and min(rational) >= 0
    if not exact:
        result.update(status='FLOATING_PRIMAL_RATIONAL_RECONSTRUCTION_FAILED', selection=selection)
        return result
    profile = Counter({r:calls*n for r, n in LOCAL.items()})
    profile.update(idle)
    if sum(r*n for r,n in idle.items()) != stock-credit:
        raise ValueError('exact residue mass')
    if m*fields-sum(r*n for r,n in profile.items()) != 96*pairs-64:
        raise ValueError('exact complete raw deficit')
    result.update(status='EXACT_RATIONAL_UNRESTRICTED_PATTERN_PRIMAL',
                  rational_primal_equations_pass=True, pattern_selection=selection,
                  idle_profile={r:str(n) for r,n in sorted(idle.items())},
                  complete_profile={r:str(n) for r,n in sorted(profile.items())},
                  floating_profile_root=floating_root(profile,m,fields),
                  floating_residual_at_endpoint=sum(float(n)*(r/m)**(1-a) for r,n in profile.items())/fields-1,
                  convergence=convergence)
    return result


def main():
    parser=ArgumentParser(description=__doc__)
    parser.add_argument('--pairs', type=int, nargs='+', default=list(range(2,9)))
    parser.add_argument('--endpoint', type=float, default=0.0017305784372662468)
    parser.add_argument('--guard', choices=['native','actual'], default='native')
    parser.add_argument('--out', type=Path, default=Path(__file__).resolve().parent/'pair-count-nominations')
    args=parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    rows=[]
    for pairs in args.pairs:
        result=solve(pairs,args.endpoint,args.out,args.guard)
        result['generator_sha256']=sha256(Path(__file__).read_bytes()).hexdigest()
        (args.out/f'PAIRS-{pairs}.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
        brief={k:v for k,v in result.items() if k in ('status','pairs','dimension','productive_fields',
               'priced_child_rank_cap','actual_permitted_child_rank_cap','remainder_mass','floating_profile_root','floating_residual_at_endpoint',
               'exact_shortfall','column_count')}
        rows.append(brief)
        print(json.dumps(brief,sort_keys=True),flush=True)
    (args.out/'CENSUS.json').write_text(json.dumps(rows,indent=2,sort_keys=True)+'\n')


if __name__=='__main__':
    main()
