"""Reproduce uniform precision certificates and actual hybrid products.
Dugongue, with substantial OpenAI Codex assistance. Apache-2.0.
"""
from itertools import product
from fractions import Fraction as F
from pathlib import Path
import argparse
import hashlib
import json
from hybrid import (ROOT,need,authenticate,residue_lane,lift,seed_lines,
                    precision_view,certificate,least_precision,multiply,GaussianLine)


def schoolbook(a,b):
    result=[0]*(len(a)+len(b)-1)
    for i,x in enumerate(a):
        for j,y in enumerate(b):result[i+j]+=x*y
    return result


def digest(values):
    return hashlib.sha256(json.dumps(values,separators=(',',':')).encode()).hexdigest()


def run_checks():
    authenticate();lane_cases=0
    arrays=[list(x) for length in range(1,4) for x in product(range(4),repeat=length)]
    for a in arrays:
        for b in arrays:
            expected=schoolbook(a,b)
            for k in (1,2,3):
                actual,bill=residue_lane(a,b,k)
                need(actual==[x%(1 << k) for x in expected],'independent modular convolution')
                need(bill['exact_child_calls']==1,'paid child invoice')
                need(bill['left_child_bits']<=bill['left_child_bound'] and
                     bill['right_child_bits']<=bill['right_child_bound'],'packed child size bound')
                lane_cases+=1
    seeds=seed_lines()
    # Independent source constructor/certifier checks the affine p-transfer.
    for p in (192,208):
        views=precision_view(seeds,p)
        for old,view in zip(seeds,views):
            fresh=GaussianLine(old.s,old.t,old.alpha,precision=p,bits=old.bits)
            fresh.certify_operator()
            need(fresh.uniform_error==view.uniform_error and fresh.operator_error==view.operator_error,
                 'fresh source precision certificate equals affine transfer')
            need(fresh.expansion==view.expansion and fresh.compression==view.compression,
                 'prepared source matrices are independent of p')
    curve=[]
    for k in (0,8,16,24):
        lines,cert=least_precision(seeds,64,k)
        rejected_below=False
        try:certificate(precision_view(seeds,cert['precision']-1),64,k)
        except ValueError:rejected_below=True
        need(rejected_below,'least accepted p in the frozen certificate range')
        d=228;w=2*k+(d-1).bit_length() if k else None
        curve.append({**cert,'one_bit_lower_not_certified':True,
                      'packed_child_bound':k+(d-1)*w if k else 0,
                      'packed_slot_bits':w,'paid_exact_lane_calls':int(k>0)})
    need([r['precision'] for r in curve]==[208,200,192,184],'source-bound precision curve')
    need(F(333,1000)<F(*curve[0]['radius'])<F(334,1000),'ordinary radius display bound')
    need(21834<F(*curve[2]['radius'])<21835,'hybrid radius display bound')
    products=[];line_calls=coefficients=ordinary_ambiguous=0
    for dimension in (1,2,3):
        lines,cert=least_precision(seeds[:dimension],64,16)
        size=1
        for l in lines:size*=l.s
        digits=(size+1)//2;bits=digits*64
        maximum=(1 << bits)-1
        mixed=sum(((j*104729+12345)%(1 << 64)) << (64*j) for j in range(digits))
        for name,a,b in [('zero',0,maximum),('maximal',maximum,maximum),('mixed',mixed,maximum-17)]:
            answer,r=multiply(a,b,lines,64,16,bits)
            # Original-input multiplication occurs ONLY here after the output exists.
            need(answer==a*b,'independent whole product')
            aa=[(a >> (64*j))% (1 << 64) for j in range(digits)]
            bb=[(b >> (64*j))% (1 << 64) for j in range(digits)]
            exact=schoolbook(aa,bb)
            need(r['coefficients']==exact,'every inverse-CRT coefficient independently checked')
            need(r['exact_lane']['strictly_smaller_child_bound'],'proper declared-size child')
            radius=F(*r['actual_radius'])
            if radius>=F(1,2):ordinary_ambiguous+=1
            # The accepted interval is wider than a unit for the stressed rows,
            # but still contains exactly one representative of the correct class.
            need(radius<F(1 << 16,2),'modular separation radius')
            line_calls+=r['gaussian_line_executions'];coefficients+=len(exact)
            products.append({'case':name,'source_axes':dimension,'declared_input_bits':bits,
                             'precision':r['precision'],'actual_radius':r['actual_radius'],
                             'exact_lane':r['exact_lane'],'gaussian_line_executions':r['gaussian_line_executions'],
                             'coefficient_sha256':digest(r['coefficients']),
                             'output_sha256':hashlib.sha256(format(answer,'x').encode()).hexdigest()})
    need(ordinary_ambiguous>=3,'actual products use the wider residue recovery contract')
    return {'status':'PASS_MODULAR_GAUSSIAN_RECOVERY','modular_lane_cases':lane_cases,
            'fresh_precision_constructor_checks':6,'precision_curve':curve,
            'complete_products':products,'gaussian_line_executions':line_calls,
            'recovered_coefficients':coefficients,
            'actual_products_with_radius_at_least_half':ordinary_ambiguous,
            'scope':'Universal lifting/packing proof plus finite uniform Gaussian all-input certificate. No new kappa or physical caller bound.'}


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--write',action='store_true')
    parser.add_argument('--check-inputs',action='store_true');args=parser.parse_args()
    if args.check_inputs:
        authenticate();print('PASS_AUTHENTICATED_INPUTS');return
    result=run_checks();path=ROOT/'RESULT.json'
    if args.write:path.write_text(json.dumps(result,indent=2)+'\n',encoding='utf8')
    else:need(json.loads(path.read_text(encoding='utf8'))==result,'frozen mathematical receipt')
    print(json.dumps({'status':result['status'],'modular_lane_cases':result['modular_lane_cases'],
                      'products':len(result['complete_products']),
                      'gaussian_line_executions':result['gaussian_line_executions'],
                      'recovered_coefficients':result['recovered_coefficients'],
                      'actual_products_with_radius_at_least_half':result['actual_products_with_radius_at_least_half']}))


if __name__=='__main__':main()
