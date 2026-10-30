#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Replace paid jobs with scaled recursive invoices and explicit fee accounting.

One matching inner target is consumed for each replaced outer job. Other
targets remain credits. This is declared accounting, not physical composition.
Ali Romman with OpenAI Codex assistance; retain the invoice predecessor credits.
"""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import re
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
try:
    from compare_recursive_invoices import load_invoice, validate_invoice, require, MAX_COUNT
    from combine_recursive_invoices import combine_invoices
finally:
    sys.path.pop(0)


def substitute(outer, inner, fees, replacements):
    outer=validate_invoice(outer, 'outer');inner=validate_invoice(inner, 'inner')
    fees=validate_invoice(fees, 'fees')
    require(fees['contract']==outer['contract'] and not fees['targets'],
            'fees need the outer contract and no target credits')
    for key in ('model','rank_semantics','boundary'):
        require(outer['contract'][key]==inner['contract'][key], 'declared inner and outer contracts differ')
    ambient=inner['contract']['ambient_rank']
    require(inner['targets'].get(str(ambient),0)>=1, 'inner needs a target at its ambient rank')
    require(all(int(r)<ambient for r in inner['paid']), 'inner paid children must have strictly smaller ranks')
    require(type(replacements) is list and 1<=len(replacements)<=128, 'provide 1..128 replacements')
    demand={}
    for rank,count in replacements:
        require(type(rank) is int and 1<=rank<=outer['contract']['ambient_rank'], 'invalid replacement rank')
        require(type(count) is int and 1<=count<=MAX_COUNT, 'invalid replacement count')
        demand[rank]=demand.get(rank,0)+count
    for rank,count in demand.items():
        require(rank%ambient==0, 'replacement rank must be an integer multiple of inner ambient rank')
        require(count<=outer['paid'].get(str(rank),0), 'replacement exceeds available outer paid jobs')
    result={**outer,'paid':dict(outer['paid']),'targets':dict(outer['targets'])}
    steps=[]
    for rank,count in sorted(demand.items()):
        scale=rank//ambient
        result['paid'][str(rank)]-=count
        for side in ('paid','targets'):
            for r,n in inner[side].items():
                amount=n-(side=='targets' and int(r)==ambient)
                key=str(int(r)*scale)
                result[side][key]=result[side].get(key,0)+count*amount
        steps.append({'outer_rank':rank,'copies':count,'rank_scale':scale,
                      'consumed_inner_target_rank':ambient})
    result=combine_invoices([(1,validate_invoice(result,'substituted invoice')),(1,fees)])
    return result,steps


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('outer');parser.add_argument('inner');parser.add_argument('fees')
    parser.add_argument('--replace',nargs=2,action='append',required=True,metavar=('COUNT','RANK'))
    args=parser.parse_args(argv)
    try:
        require(len(args.replace)<=128,'provide at most 128 replacements')
        replacements=[]
        for count,rank in args.replace:
            require(re.fullmatch(r'[1-9][0-9]{0,60}',count) is not None and
                    re.fullmatch(r'[1-9][0-9]{0,9}',rank) is not None,'use positive decimal counts and ranks')
            replacements.append((int(rank),int(count)))
        invoices=[];pins={}
        for name in ('outer','inner','fees'):
            value,pin=load_invoice(getattr(args,name));invoices.append(value);pins[name]=pin
        result,steps=substitute(*invoices,replacements)
        payload=(json.dumps(result,indent=2,sort_keys=True)+'\n').encode('utf-8')
        receipt={'schema':'integer-mult-invoice-substitution/v1','inputs':pins,'replacements':steps,
                 'output_sha256':sha256(payload).hexdigest(),'output_bytes':len(payload),
                 'identity':'F_new(t) = F_outer(t) + sum copies * scale^t * F_inner(t) + F_fees(t)',
                 'scope':'Declared histogram substitution only. Matched target ownership, coproduct '
                         'independence, physical scale lifting and complete fees require source proofs.'}
    except (OSError,ValueError,TypeError,RecursionError) as exc:
        print(json.dumps({'status':'INVALID_INVOICE_SUBSTITUTION','error':str(exc)}),file=sys.stderr)
        return 2
    sys.stdout.buffer.write(payload);sys.stdout.buffer.flush()
    print(json.dumps(receipt,sort_keys=True),file=sys.stderr)
    return 0


if __name__=='__main__':raise SystemExit(main())
