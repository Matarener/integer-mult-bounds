#!/usr/bin/env python3
"""Exact target deficit and optimistic changed-geometry economic bounds.

Uses the previous independent review's rational logarithm/exponential tails,
not the construction optimizer. All changed helper shapes below are declared
hypotheses, not emitted words. Whole-residual packing is relaxed across all
replicas and all stage windows. No source files are modified.

Apache-2.0; substantial OpenAI assistance. Width7 packing retains Sagar
Thakrar's bit589-width-packing and bit-partial-width7-optimum lineage.
"""
from argparse import ArgumentParser
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from itertools import combinations_with_replacement
from pathlib import Path
import importlib.util
import json

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
OLD = REPO/'research/kappa-next-regime'
PRICE = OLD/'width-search/review_invoice_outer.py'
spec = importlib.util.spec_from_file_location('independent_rational_price',PRICE)
price = importlib.util.module_from_spec(spec)
spec.loader.exec_module(price)


def interval(a,b):
    return [str(a),str(b)]


def decimal(value,places=32):
    sign = '-' if value < 0 else ''
    n = abs(value*10**places).__floor__()
    return sign+str(n//10**places)+'.'+str(n%10**places).zfill(places)


def tariff(rank,exponent):
    if not rank:
        return Q(0),Q(0)
    low,high = price.log_interval(Q(64,rank))
    low,high = price.exp_interval(exponent*low,exponent*high)
    return rank*low,rank*high


def combine(profile,exponent):
    lower = upper = Q(0)
    for rank,count in profile.items():
        lo,hi = tariff(rank,exponent)
        if count >= 0:
            lower += count*lo; upper += count*hi
        else:
            lower += count*hi; upper += count*lo
    return lower,upper


def mixed_profile(local,k,optimistic=True):
    changed = Counter(local)
    if optimistic:
        changed[1] -= k
    else:
        # A rank8 child is not present in this source word: this is only the
        # universal worst location for a unit trim among possible widths <=8.
        changed[8] -= k; changed[7] += k
    idle = {7:Q(666-9*k),6:Q(444),4:Q(444),
            2:Q(444)-Q(63+9*k,5),42:Q(63+9*k,5)}
    result = Counter({r:9*n for r,n in changed.items()})
    result.update(idle)
    return dict(sorted((r,n) for r,n in result.items() if n))


def recipe_relaxation(local,exponent):
    """Rigorous dual for all 9 segments, sum Delta=27, 1<=Delta<=6."""
    # A rational Lagrange multiplier is valid even when not exactly the true
    # analytic equality multiplier. It is deliberately rounded down here.
    lo42,hi42 = tariff(42,exponent)
    lo2,hi2 = tariff(2,exponent)
    lam = Q(((lo42-hi2)/5*10**60).__floor__(),10**60)
    per_segment = {}
    for delta in range(1,7):
        r = 7*delta
        per_segment[delta] = min(tariff(r-8*k,exponent)[0]+lam*k for k in range(r//8+1))
    rows = []
    for ds in combinations_with_replacement(range(1,7),9):
        if sum(ds) == 27:
            cost = 222*sum(per_segment[d] for d in ds)-lam*(9*437)
            rows.append((cost,ds))
    rows.sort()
    local_price = combine(local,exponent)[0]
    minimum = (9*local_price+rows[0][0])/(64*888)
    return {'parameter':str(exponent),'parameter_decimal':decimal(exponent),
            'partition_count':len(rows),'best_partition':list(rows[0][1]),
            'dual_multiplier':str(lam),'dual_segment_lower_prices':{str(d):str(c) for d,c in per_segment.items()},
            'minimum_normalized_moment_lower':str(minimum),
            'minimum_normalized_moment_minus_one_lower':str(minimum-1),
            'decimal_margin':decimal(minimum-1),
            'fallback_charged':0,
            'scope':'Lower bound on cost, ignoring stage eligibility and physical axes, for nine nonzero idle advances of Delta1..6, all width8 residuals, pooled over all replicas. Dropping fallback favors the relaxation.'}


def main():
    ap = ArgumentParser(description=__doc__)
    ap.add_argument('--output',type=Path,default=HERE/'GEOMETRY-BUDGET.json')
    args = ap.parse_args()
    invoice_path = OLD/'COMPLETE-WORD-INVOICE.json'
    invoice = json.loads(invoice_path.read_text())
    local = {int(r):n for r,n in invoice['local']['forward']['profile'].items()}
    full = {int(r):n for r,n in invoice['profile'].items()}
    assert local == {1:1322,2:1342,3:74,4:46,5:103,6:10,7:18}
    assert sum(r*n for r,n in local.items()) == 5113
    a = Q('.001745')
    f_low,f_high = price.moment(full,64,31080,a,invoice['fallback_total'])
    factor_low,factor_high = tariff(1,a)
    required_low = (f_low-1)*64*31080/(315*factor_high)
    required_high = (f_high-1)*64*31080/(315*factor_low)
    widths = []
    for k in range(8):
        p = mixed_profile(local,k)
        assert sum(r*n for r,n in p.items()) == 64*888-321
        E = sum(p.values())
        lo,hi = price.moment(p,64,888,a,32*64*64*E)
        widths.append({'width7_helpers_per_call':k,'profile_per_replica':{r:str(n) for r,n in p.items()},
                       'paid_requests_per_replica':str(E),'moment_minus_one':interval(lo-1,hi-1),
                       'decimal_upper_margin':decimal(hi-1),'passes_optimistic_economics':hi<1})
    # Conservative target upper bound; the best relaxed concrete profile's
    # numerical root is near .0017401561948, but this rounded rejection alone
    # is the rigorous ceiling recorded here.
    cap = Q('.001740157')
    relaxed_target = recipe_relaxation(local,a)
    relaxed_cap = recipe_relaxation(local,cap)
    assert Q(relaxed_cap['minimum_normalized_moment_lower']) > 1
    first = next(row['width7_helpers_per_call'] for row in widths if row['passes_optimistic_economics'])
    assert first == 6
    result = {'status':'EXACT_TARGET_BUDGET_AND_CONDITIONAL_CLOCK_GEOMETRY_CEILING',
              'target':str(a),'baseline_lower':invoice['bit_lower'],
              'baseline_complete_moment_minus_one':interval(f_low-1,f_high-1),
              'required_local_r_to_1_minus_a_tariff_saving':interval(required_low,required_high),
              'required_local_tariff_saving_decimal':interval(decimal(required_low),decimal(required_high)),
              'mixed_width7_optimistic_first_passing_count':first,'mixed_width7_rows':widths,
              'mixed_width7_hypothesis':'Each of k converted helpers starts at an admissible rank1 frame, removes exactly one paid rank1 local move, and needs no adapters or new captures. Place each width7 role alone in a rank7 slot; concentrate released width8 places into rank42 slots. This is a tariff relaxation, not a literal word.',
              'arbitrary_nine_segment_target':relaxed_target,
              'arbitrary_nine_segment_strict_ceiling':relaxed_cap,
              'strict_ceiling':str(cap),'strict_ceiling_decimal':decimal(cap),
              'ceiling_conditional_on':'A valid controller has at least nine nonzero idle segments and no idle advance exceeding six stages. The packing bound itself does not assert those controller premises.',
              'source_sha256':{str(p.relative_to(REPO)):sha256(p.read_bytes()).hexdigest() for p in (invoice_path,PRICE,Path(__file__))}}
    args.output.write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
    print(json.dumps({'status':result['status'],'width7_threshold':first,'strict_ceiling':decimal(cap),
                      'target_margin':relaxed_target['decimal_margin'],'ceiling_margin':relaxed_cap['decimal_margin']}))


if __name__ == '__main__':
    main()
