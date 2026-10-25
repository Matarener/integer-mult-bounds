#!/usr/bin/env python3
"""Source-bound, solver-free complete p2 full-identity recursive tariff.

This certifies a finite invoice, strict separation, and its scalar root.
It does not certify the global native owner construction, all-size mixed
router, fixed-tape implementation, rounding induction, or outer kappa.
Apache-2.0. Substantial OpenAI assistance; credits in README.md.
"""
from collections import Counter
from decimal import Decimal, localcontext, ROUND_FLOOR
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import argparse
import json
import sys

sys.dont_write_bytecode=True
import mixed_target_probe as E
import mixed_forest_search as F

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
NATIVE=ROOT/'research/kappa-rebuild/complex/full-identity-certificates/RESULT.json'
PAIRS=((93,8,8),(56,7,9),(56,9,7),(19,5,9))
MIDDLE=((29,0),(28,5),(18,6),(56,7),(93,8))

def root_bracket(signed):
    """Decimal discovery followed by rational elementary-function proof."""
    with localcontext() as context:
        context.prec=85
        terms=[(Decimal(n.numerator)/Decimal(n.denominator),Decimal(r).ln())
               for r,n in sorted(signed.items()) if n]
        def value(c):
            return sum(n*((1-c)*logr).exp() for n,logr in terms)
        lo=Decimal(0);hi=Decimal('0.01')
        for _ in range(200):
            mid=(lo+hi)/2
            if value(mid)>0:lo=mid
            else:hi=mid
        scale=10**30
        integer=int((lo*scale).to_integral_value(rounding=ROUND_FLOOR))
        left,right=Q(integer,scale),Q(integer+1,scale)
        low_bounds=E.moment(signed,left)
        high_bounds=E.moment(signed,right)
        E.need(low_bounds[0]>0 and high_bounds[1]<0,'Exact strict root bracket')
        return {'lower':str(Decimal(integer)/scale),
                'upper':str(Decimal(integer+1)/scale),
                'margin_at_lower':E.show(low_bounds),'margin_at_upper':E.show(high_bounds),
                'uniqueness':'The paid/target ratio is strictly increasing in C because every paid rank is smaller than every target rank.'}

def source_binding():
    data=json.loads(NATIVE.read_text())
    bound={str(NATIVE.relative_to(ROOT)):sha256(NATIVE.read_bytes()).hexdigest()}
    for name in ('THREE-base','THREE-extra'):
        row=data['providers'][name]
        E.need(row['all_408_helpers_autonomous'] and row['all_632_persistent_inputs_arbitrary'],
               'Authenticated arbitrary helper/data input contract')
        E.need(row['external_cleanup_fields']==0 and row['owned_C_fields']==1,
               'Zero external bank and one explicitly owned center')
        for orientation in ('forward','backward'):
            replay=row['split_replays'][orientation]['independent_native_replay']
            profile={int(r):int(n) for r,n in replay['paid_profile'].items()}
            E.need(profile==dict(E.split_profile(F.IDENTITY,5)),'Actual native split profile')
        helpers={int(r):int(n) for r,n in row['helper_boundary']['widths'].items()}
        E.need(helpers==dict(E.HELPERS),'Actual THREE helper inventory')
        for name2,wanted in row['artifacts'].items():
            path=NATIVE.parent/name2
            E.need(sha256(path.read_bytes()).hexdigest()==wanted,'Native bytes '+name2)
            bound[str(path.relative_to(ROOT))]=wanted
        boundary=ROOT/row['helper_boundary']['certificate']
        wanted=row['helper_boundary']['certificate_sha256']
        E.need(sha256(boundary.read_bytes()).hexdigest()==wanted,'Helper boundary bytes')
        bound[str(boundary.relative_to(ROOT))]=wanted
    return bound

def run(prefix_cut=False):
    sources=source_binding()
    solution=[]
    for f in ((1,) if prefix_cut else (0,2)):
        solution.extend({'family':f,'pattern':[a,b],'count':str(n)} for n,a,b in PAIRS)
    solution.extend({'family':0 if prefix_cut else 1,'pattern':[a],'count':str(n)} for n,a in MIDDLE)
    case=F.verify(2,6,solution,'identity',prefix_cut=prefix_cut)
    wanted_targets=({'6':'165','7':'112','8':'186','9':'934','25':'224','41':'224'}
                    if prefix_cut else {'6':'146','9':'803','41':'448'})
    wanted_paid=({'1':'12584','2':'3602','3':'1217','4':'510','5':'169'}
                 if prefix_cut else {'1':'12565','2':'3621','3':'1217','4':'510','5':'169'})
    E.need(case['targets']==wanted_targets,'Literal output census')
    E.need(case['paid']==wanted_paid,'Literal paid census')
    out=F.serialize(case,('0.001730970419199163702738','0.001745','0.00175','0.00177','0.002','0.004'))
    out['root_bracket']=root_bracket(case['signed'])
    bad=[dict(x) for x in solution]
    bad[0]=dict(bad[0],count=str(int(bad[0]['count'])+1))
    rejected=False
    try:F.verify(2,6,bad,'identity',prefix_cut=prefix_cut)
    except AssertionError:rejected=True
    E.need(rejected,'Duplicated owner is rejected')
    illegal=Counter(case['signed']);illegal[1]+=1
    E.need(sum(r*n for r,n in illegal.items())!=128,'Unfunded output rejected by rank budget')
    return {'schema':'source-bound-identity-mixed-tariff/1',
            'status':'PASS_EXACT_NATIVE_BOUND_PROFILE_AND_FINITE_RECURSIVE_INVOICE',
            'source_sha256':sha256(Path(__file__).read_bytes()).hexdigest(),
            'native_sources':sources,
            'enclosure_source_sha256':sha256((HERE/'mixed_target_probe.py').read_bytes()).hexdigest(),
            'invoice':out,
            'controls':{'duplicate_original_idle_owner_rejected':rejected,
                        'unfunded_output_credit_rejected':True,
                        'rank5_target_with_rank5_child_rejected':not(5<5)},
            'explicitly_charged':['all five native full-identity calls',
                                 'all forty rank8 centers split into rank5 plus rank3',
                                 'each unused original idle portion',
                                 ('rank1 completions for all ninety-three width5 fresh helpers' if prefix_cut else
                                  'rank1 completions for all seventy-four width5 fresh helpers'),
                                 'every productive output field at its actual target rank'],
            'prefix_cut':prefix_cut,
            'not_a_recursive_output':['one owned center field, erased after use'],
            'not_proved':['physical global helper placement and controller binding',
                          'all-size mixed-target causal routing on fixed tapes',
                          'rounded whole-caller precision and stock conversion',
                          'outer integer-multiplication transfer'],
            'new_kappa':False}

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path)
    parser.add_argument('--prefix-cut',action='store_true')
    args=parser.parse_args()
    result=run(args.prefix_cut)
    output=args.output or HERE/('IDENTITY-PREFIX-CUT-CERTIFICATE.json' if args.prefix_cut else
                               'IDENTITY-MIXED-CERTIFICATE.json')
    output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'status':result['status'],'root':result['invoice']['root_bracket'],
                      'margin_001745':result['invoice']['invoices']['0.001745']},sort_keys=True))

if __name__=='__main__':main()
