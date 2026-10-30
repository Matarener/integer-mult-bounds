#!/usr/bin/env python3
"""Exact dual check for complex mixed-width packing over changed clocks.

SciPy proposes dual helper prices. The certificate then rounds those prices
to rationals and independently checks every integer slot pattern with exact
rational transcendental lower bounds. No numerical solver status is trusted
as a lower-bound certificate. Chronological eligibility and physical axes
are omitted, making this a favorable relaxation of every named controller.

Apache-2.0. Substantial OpenAI assistance. The local word and width inventory
are the frozen receiver-sharing/staged544 lineage, credited by the root.
"""
from argparse import ArgumentParser
from collections import Counter
from fractions import Fraction as Q
from functools import lru_cache
from hashlib import sha256
from itertools import combinations_with_replacement
from pathlib import Path
import importlib.util
import json
import math

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
PRICE = REPO/'research/kappa-next-regime/width-search/review_invoice_outer.py'
SOURCE = HERE.parent/'complex/TARGET-BUDGET.json'
WIDTHS = (4,5,6,7,8,9)
INVENTORY = (26,2,18,53,96,213)
spec = importlib.util.spec_from_file_location('clock_complex_rational_price',PRICE)
price = importlib.util.module_from_spec(spec); spec.loader.exec_module(price)


@lru_cache(None)
def patterns(capacity,index=0):
    if index == len(WIDTHS):
        return ((),)
    width = WIDTHS[index]
    return tuple((count,)+rest for count in range(capacity//width+1)
                 for rest in patterns(capacity-count*width,index+1))


def decimal(value):
    s = '-' if value < 0 else ''
    n = abs(value*10**30).__floor__()
    return s+str(n//10**30)+'.'+str(n%10**30).zfill(30)


def main():
    import numpy as np
    from scipy.optimize import linprog
    ap = ArgumentParser(description=__doc__)
    ap.add_argument('--parameter',default='.001745')
    ap.add_argument('--output',type=Path,default=HERE/'COMPLEX-CLOCK-PACKING.json')
    args = ap.parse_args(); exponent = Q(args.parameter)
    source = json.loads(SOURCE.read_text())
    local = {int(r):n for r,n in source['baseline_local_profile'].items()}
    assert local == {1:2439,2:724,3:225,4:102,5:20,8:8}
    assert sum(w*n for w,n in zip(WIDTHS,INVENTORY)) == 3278
    assert sum(r*n for r,n in local.items()) == 5134
    demand = tuple(9*n for n in INVENTORY)
    tariff = {0:(Q(0),Q(0))}
    for r in range(1,49):
        lo,hi = price.log_interval(Q(73,r)); lo,hi = price.exp_interval(exponent*lo,exponent*hi)
        tariff[r] = (r*lo,r*hi)
    local_lower = 9*sum(n*tariff[r][0] for r,n in local.items())
    catalogue = []
    for delta in range(1,7):
        for row in patterns(8*delta):
            remainder = 8*delta-sum(w*n for w,n in zip(WIDTHS,row))
            catalogue.append((delta,row,remainder))
    costs = np.array([float(tariff[r][0]) for _,_,r in catalogue])
    columns = np.array([list(row)+[int(delta == d) for d in range(1,7)] for delta,row,_ in catalogue]).T
    partitions = [ds for ds in combinations_with_replacement(range(1,7),9) if sum(ds) == 27]
    rows = []
    for index,ds in enumerate(partitions):
        counts = Counter(ds)
        rhs = np.array(list(demand)+[224*counts[d] for d in range(1,7)])
        sol = linprog(costs,A_eq=columns,b_eq=rhs,bounds=(0,None),method='highs')
        assert sol.success, ('LP relaxation infeasible or solver incomplete',ds,sol.message)
        helper_dual = tuple(Q(str(float(y))).limit_denominator(10**9) for y in sol.eqlin.marginals[:6])
        # Reset each slot dual to the exact maximal value compatible with all
        # its listed integer patterns. This repairs every floating error.
        slot_dual = {delta:min(tariff[r][0]-sum(n*y for n,y in zip(row,helper_dual))
                              for d,row,r in catalogue if d == delta)
                     for delta in range(1,7)}
        idle_lower = sum(n*y for n,y in zip(demand,helper_dual))+224*sum(slot_dual[d] for d in ds)
        minimum = (local_lower+idle_lower)/(73*896)
        row = {'partition':list(ds),'slot_counts_per_replica':{8*d:224*n for d,n in sorted(counts.items())},
               'solver_cost_heuristic':float(sol.fun),'helper_dual':list(map(str,helper_dual)),
               'slot_dual':{str(d):str(y) for d,y in slot_dual.items()},
               'idle_tariff_lower':str(idle_lower),'normalized_moment_lower':str(minimum),
               'normalized_moment_minus_one_lower':str(minimum-1),'decimal_margin':decimal(minimum-1)}
        rows.append(row)
        if index % 10 == 0:
            print(index,ds,row['decimal_margin'],flush=True)
    rows.sort(key=lambda row:Q(row['normalized_moment_lower']))
    result = {'status':'EXACT_DUAL_LOWER_BOUNDS_OVER_ALL_88_NINE_SEGMENT_PARTITIONS',
              'parameter':str(exponent),'parameter_decimal':decimal(exponent),'m':73,'W_per_replica':896,
              'width_inventory':dict(zip(WIDTHS,INVENTORY)),'local_profile':local,
              'patterns_per_slot':{8*d:len(patterns(8*d)) for d in range(1,7)},
              'all_pattern_constraints_checked':len(catalogue)*len(rows),'partitions':len(rows),
              'best_lower_bound_row':rows[0],'all_partitions_reject_target':all(Q(row['normalized_moment_lower'])>1 for row in rows),
              'rows':rows,'scope':'Nine nonzero idle segments with Delta1..6 and total27, 224 copies each, fully pooled fractional pattern counts, unchanged local word and helper-width inventory. No physical construction or integer-lift claim. More segments are dominated by merging two smallest advances until nine remain, since subadditivity cannot increase residual tariff.',
              'source_sha256':{str(p.relative_to(REPO)):sha256(p.read_bytes()).hexdigest() for p in (SOURCE,PRICE,Path(__file__))}}
    args.output.write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
    print(json.dumps({'status':result['status'],'rejects':result['all_partitions_reject_target'],
                      'best_partition':rows[0]['partition'],'best_margin':rows[0]['decimal_margin']}),flush=True)


if __name__ == '__main__':
    main()
