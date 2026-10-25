"""Exact finite corroboration of PROOF.md, with a separate dense oracle.
Dugongue, with substantial OpenAI Codex assistance. Apache-2.0.
"""
from fractions import Fraction as F
from itertools import product
from math import factorial, isqrt, prod
from pathlib import Path
import argparse
import hashlib
import json

from expansion import (Interval, cap, line, pi_interval, exp_negative,
                       prepare, require, tensor, window)

ROOT=Path(__file__).resolve().parent


def oracle(s,t,k,u,bits):
    """Independent residue-first enclosure; no prepare_row or tail_bound call.

    Uses the credited interval backend for transcendental enclosures, not an
    independent transcendental implementation. The indexing, radius, grouping,
    accumulation and dense tensor evaluation are separate.
    """
    center=F(s*k,t)
    radius=max(u, isqrt(u*(bits+40))+5)
    lo=center.numerator//center.denominator-radius
    hi=-((-center.numerator)//center.denominator)+radius
    scale=1 << bits
    root=isqrt(u*scale*scale)
    sqrtu=Interval(root,root if root*root==u*scale*scale else root+1,bits)
    pi=pi_interval(bits)
    answer=[]
    for residue in range(s):
        total=Interval.rational(0,bits)
        for j in range(lo,hi+1):
            if (j-residue)%s==0:
                x=pi*((F(j)-center)**2/u)
                total+=exp_negative(x)/(sqrtu*2)
        answer.append((F(total.lo,scale),F(total.hi,scale)))
    a=3*radius*radius//u
    b=3*(2*radius+1)//u
    tail=F(1,1 << a)/(1-F(1,1 << b))
    # The omitted positive mass is at most tail, in total across residues.
    return answer,tail


def vectors(s,p):
    n=1 << p
    compass=[(n,0),(-n,0),(0,n),(0,-n),(n//2,n//2),
             (-n//2,n//2),(n//2,-n//2),(0,0)]
    return [[compass[(3*j+shift)%len(compass)] for j in range(s)]
            for shift in range(8)]+[[(n,0)]*s,[(0,-n)]*s]


def dense_tensor(data,specs,p,bits):
    """One direct Kronecker matrix, without sequential-axis grid rounding."""
    sources=tuple(product(*(range(s) for s,_,_ in specs)))
    targets=tuple(product(*(range(t) for _,t,_ in specs)))
    matrices=[]
    ref_error=F(1)
    ideal_norm=F(1)
    for s,t,u in specs:
        matrix=[];delta=F(0)
        for k in range(t):
            cells,tail=oracle(s,t,k,u,bits)
            matrix.append([(lo+hi)/2 for lo,hi in cells])
            delta=max(delta,tail+sum(hi-lo for lo,hi in cells))
        matrices.append(matrix)
        ref_error*=cap(u)+delta
        ideal_norm*=cap(u)
    out=[]
    for dest in targets:
        real=imag=F(0)
        for src,z in zip(sources,data):
            weight=prod(matrices[i][dest[i]][src[i]] for i in range(len(specs)))
            real+=weight*F(z[0],1 << p)
            imag+=weight*F(z[1],1 << p)
        out.append((real,imag))
    return out,ref_error-ideal_norm


def run():
    require(sum(F(3)**n/factorial(n) for n in range(10))>20,'e^3 lower certificate')
    require(cap(1)==F(21,38) and F(3,5)-cap(1)==F(9,190),'exact headroom')
    require(all(F(1,2)<cap(u)<=F(21,38) for u in range(1,129)), 'parameter caps')
    cases=[(1,2,1,16,56),(2,4,1,20,64),(5,8,4,24,72),
           (7,16,2,24,72),(3,4,10,101,144)]
    rows_count=values_count=0
    receipt=[]
    for s,t,u,p,q in cases:
        rows=prepare(s,t,u,q)
        for k,row in enumerate(rows):
            cells,tail=oracle(s,t,k,u,q+40)
            widths=sum(hi-lo for lo,hi in cells)
            require(all(F(w,1 << q)<=hi+tail for w,(_,hi) in zip(row.weights,cells)),
                    'downward residue coefficient versus oracle')
            require(sum(lo for lo,_ in cells)<=row.mass+row.deficit,'missing mass budget')
            for data in vectors(s,p):
                output=line(data,(row,),p)[0]
                require((output[0]**2+output[1]**2)*cap(u).denominator**2 <=
                        (1 << (2*p))*cap(u).numerator**2,'hard complex disk')
                for component in range(2):
                    endpoints=[]
                    for j,(lo,hi) in enumerate(cells):
                        z=F(data[j][component],1 << p)
                        endpoints.append((min(z*lo,z*hi),max(z*lo,z*hi)))
                    lower=sum(a for a,_ in endpoints)-tail
                    upper=sum(b for _,b in endpoints)+tail
                    actual=F(output[component],1 << p)
                    require(max(abs(actual-lower),abs(actual-upper)) <=
                            row.deficit+F(2,1 << p)+widths+2*tail,
                            'line approximation enclosure')
                values_count+=1
            rows_count+=1
        encoded=[r.weights for r in rows]
        receipt.append({'s':s,'t':t,'u':u,'p':p,'q':q,
                        'max_mass':str(max(r.mass for r in rows)),
                        'deficit_below_grid_units':str(max(r.deficit for r in rows)*(1 << p)),
                        'prepared_terms':sum(r.terms for r in rows),
                        'weights_sha256':hashlib.sha256(json.dumps(encoded,separators=(',',':')).encode()).hexdigest()})
    tensor_cases=[((2,4,1),(3,4,2)),((2,4,1),(2,4,2),(3,4,4))]
    tensor_coordinates=0
    tensor_receipts=[]
    for specs in tensor_cases:
        p,q=20,72
        n=prod(s for s,_,_ in specs)
        data=vectors(n,p)[3]
        before=data.copy()
        result,shape,error,bound=tensor(data,specs,p,q)
        require(data==before,'borrowed source preservation')
        direct,ref_error=dense_tensor(data,specs,p,q+32)
        require(len(result)==prod(t for _,t,_ in specs),'dense tensor cardinality')
        for out,ref in zip(result,direct):
            require(all(abs(F(out[c],1 << p)-ref[c])<=error+ref_error for c in range(2)),
                    'independent dense tensor agreement')
        tensor_coordinates+=len(result)
        tensor_receipts.append({'specs':specs,'shape':shape,'error':str(error),
                                'norm_bound':str(bound),
                                'output_sha256':hashlib.sha256(json.dumps(result).encode()).hexdigest()})
    rows=prepare(3,4,2,64)
    src=(-7,10,29);dst=(101,105,109,113)
    storage={k:v for k,v in zip(src,vectors(3,20)[2])}
    dirt=object();storage[-999]=dirt;storage[1000]={'arbitrary':'dirty exterior'}
    old=storage.copy()
    output=window(storage,src,dst,rows,20)
    require(storage==old and all(output[k] is v for k,v in old.items()),'host frame and input')
    require([output[k] for k in dst]==line([storage[k] for k in src],rows,20),'window values')
    return {'schema_version':1,'status':'PASS_GAUSSIAN_EXPANSION_HEADROOM',
            'rows':rows_count,'complex_line_values':values_count,
            'tensor_coordinates':tensor_coordinates,'uniform_cap':'21/38',
            'chirp_norm_limit':'3/5','margin':'9/190','cases':receipt,
            'tensors':tensor_receipts,'coverage':'Finite exact-rational corroboration; universal proof is PROOF.md; no new kappa or physical implementation.'}


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--emit',action='store_true')
    args=ap.parse_args()
    result=run()
    if args.emit:
        print(json.dumps(result,indent=2,sort_keys=True))
    else:
        expected=json.loads((ROOT/'RESULT.json').read_text(encoding='utf-8'))
        require(json.loads(json.dumps(result))==expected,'committed result receipt changed')
        print(f"PASS_GAUSSIAN_EXPANSION_HEADROOM rows={result['rows']} line_values={result['complex_line_values']} tensor_coordinates={result['tensor_coordinates']} RECEIPT_MATCH")


if __name__=='__main__':
    main()
