#!/usr/bin/env python3
"""Exact remaining complex target budget, with explicitly ideal comparisons.

The arithmetic compares complete bills. The ideal batching and repeated-edit
equivalents are scales only; they do not assert implementable substitutions.
Apache-2.0. Substantial OpenAI assistance.
"""
from decimal import Decimal, localcontext
from fractions import Fraction as Q
import hashlib
import importlib.util
import json
from pathlib import Path
import argparse

HERE=Path(__file__).resolve().parent
REPO=HERE.parents[1]

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--out',type=Path,default=HERE/'TARGET-BUDGET.json')
    a=ap.parse_args()
    engine=HERE/'sources/PR3945/research/staged544-terminal-gap-fill/vendor/rational_price.py'
    spec=importlib.util.spec_from_file_location('budget_price',engine)
    price=importlib.util.module_from_spec(spec);spec.loader.exec_module(price)
    source=HERE/'composed-supplier/invoice/RESULT.json'
    inv=json.loads(source.read_text())
    target=Q('.001745')
    signed={int(k):v for k,v in inv['profile'].items()};signed[73]=-inv['productive_families']
    excess=price.interval(signed,target)
    single=price.interval({1:1,2:1,3:-1},target)
    ideal_batch=price.interval({4:4,16:-1},target)
    hm=price.h_bounds(73,target)
    normalization=(Q(73)/hm[1],Q(73)/hm[0])
    lower=Q(inv['root']['rational'][0])
    assert excess[0]>0 and single[0]>0 and ideal_batch[0]>0
    def interval(xs):
        with localcontext() as c:
            c.prec=60
            return dict(rational=list(map(str,xs)),decimal=[str(Decimal(x.numerator)/Decimal(x.denominator)) for x in xs])
    def ratio(xs,ys):
        return xs[0]/ys[1],xs[1]/ys[0]
    per_call=tuple(x/inv['calls'] for x in excess)
    normalized_excess=(excess[0]*normalization[0],excess[1]*normalization[1])
    result=dict(status='PASS_EXACT_COMPLETE_TARGET_BUDGET',target=str(target),
                price_units='H_r=r^(1-a); excess=sum(n_r H_r)-W H_m',
                current_complex_lower=str(lower),global_paid_excess=interval(excess),
                average_saving_required_per_call=interval(per_call),
                receiver_identity_saving_per_call=interval(single),
                receiver_identity_equivalents=interval(ratio(per_call,single)),
                ideal_four_rank4_to_one_rank16_saving=interval(ideal_batch),
                ideal_batch_equivalents=interval(ratio(per_call,ideal_batch)),
                normalized_moment_units=dict(
                    definition='h_r=r*(r/m)^(-a)=m^a H_r; mW*(moment-1)=m^a*excess',
                    conversion_m_to_a=interval(normalization),global_excess=interval(normalized_excess),
                    per_call_excess=interval(tuple(x/inv['calls'] for x in normalized_excess))),
                complex_supplier_gap=str(target-lower),
                best_retained_bit_gap=str(target-Q('.001738137188329345368427')),
                scope='Complete target excess is exact. Equivalent counts assume independent savings with no interface, routing, buffer, width, owner, or precision cost; they are not candidate constructions.',
                source_pins={str(p.relative_to(REPO)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [source,engine,Path(__file__)]})
    a.out.write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
    print(result['status'],result['average_saving_required_per_call']['decimal'])

if __name__=='__main__':
    main()
