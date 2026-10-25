#!/usr/bin/env python3
"""Source-bound exact local tariff allowance for the 0.001745 continuation.

No putative circuit or geometry change is admitted by this budget.  The
retained complete T35 word and full fallback profile are the fixed baseline.
Apache-2.0. Substantial OpenAI assistance under the user's direction.
"""
from decimal import Decimal, localcontext
from fractions import Fraction as Q
from hashlib import sha256
from importlib.util import spec_from_file_location,module_from_spec
from pathlib import Path
import json

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
BASE=ROOT/'research/kappa-next-regime/geometry-search/pool35-word/RESULT.json'
ENGINE=ROOT/'research/native-complex-moment552/engines/moment.py'


def main():
    spec=spec_from_file_location('k1745_budget_moment',ENGINE)
    engine=module_from_spec(spec);spec.loader.exec_module(engine)
    baseline=json.loads(BASE.read_text());profile={int(r):n for r,n in baseline['profile'].items()}
    target=Q('0.001745');rows=[]
    for name,a in [('direct_supplier_parameter',target),('kappa_over_one_minus_kappa',target/(1-target))]:
        low,high=engine.moment(profile,64,31080,a,True)
        ln_low,ln_high=engine.logarithm(Q(64))
        factor_low,factor_high=engine.exponential(a*ln_low,a*ln_high)
        required=((low-1)*64*31080/(315*factor_high),(high-1)*64*31080/(315*factor_low))
        with localcontext() as ctx:
            ctx.prec=60;da=Decimal(a.numerator)/Decimal(a.denominator)
            price=lambda r:(Decimal(r).ln()*(1-da)).exp() if r else Decimal(0)
            mechanisms={'merge_two_rank1':2*price(1)-price(2),
                        'merge_rank1_rank2':price(1)+price(2)-price(3),
                        'merge_two_rank2':2*price(2)-price(4),
                        'merge_rank1_rank7':price(1)+price(7)-price(8),
                        'merge_all_eight_rank1':8*price(1)-price(8),
                        'previous_three_covectors':-(2*price(1)-2*price(2)-3*price(3)+3*price(4)+price(5)-price(6))}
            req=Decimal(required[1].numerator)/Decimal(required[1].denominator)
            screens={k:{'saving':str(v),'minimum_disjoint_instances':int(req//v)+1} for k,v in mechanisms.items()}
        rows.append({'interpretation':name,'parameter':str(a),'parameter_decimal':engine.decimal(a),
                     'complete_moment_minus_one':[engine.decimal(low-1),engine.decimal(high-1)],
                     'local_tariff_reduction_required_interval':[engine.decimal(x) for x in required],
                     'illustrative_unchanged_call_count_screens':screens})
    result={'status':'EXACT_COMPLETE_BASELINE_DEFICIT_BUDGET','baseline_word_content_sha256':baseline['word_content_sha256'],
            'baseline_lower':baseline['bit_endpoint_lower_decimal'],'source_sha256':{str(p.relative_to(ROOT)):sha256(p.read_bytes()).hexdigest() for p in (BASE,ENGINE,Path(__file__))},
            'target':str(target),'rows':rows,
            'scope':'The local reduction interval assumes315 equal local calls, unchanged ownership/idles and unchanged paid-call count. Changed helper widths, owners or number of calls require a complete new invoice. Both parameter conventions are reported; the outer integration chooses the actual obligation. Illustrative mechanism counts are Decimal cost screens, not constructions.'}
    (HERE/'BUDGET.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
    print(json.dumps(result,sort_keys=True,indent=2))


if __name__=='__main__':main()
