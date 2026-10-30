#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Certify best-candidate regions for common-base recursive invoices.

Use the existing exact polynomial and Sturm tools. Retain their credits.
Ali Romman with OpenAI Codex assistance. Unresolved boxes remain explicit.
"""
import argparse
from fractions import Fraction as Q
import json
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parent))
try:
    import compare_power_polynomial as P
finally:
    sys.path.pop(0)
require=P.require


def difference(a,b):
    return P.trim((a[i] if i<len(a) else 0)-(b[i] if i<len(b) else 0)
                  for i in range(max(len(a),len(b))))


def root_tower(poly):
    """Build one square-free Sturm sequence per level of the multiplicity tower."""
    current=P.primitive(poly);tower=[]
    while len(current)>1:
        common=P.poly_gcd(current,P.derivative(current))
        square,remainder=P.divide(current,common)
        require(not remainder,'inexact square-free division')
        square=P.primitive(square);sequence=[square,P.derivative(square)]
        while len(sequence[-1])>1:
            remainder=P.divide(sequence[-2],sequence[-1])[1]
            require(bool(remainder),'unexpected repeated Sturm root')
            sequence.append(P.primitive(-c for c in remainder))
        tower.append(sequence);current=common
    return tower


def roots(tower,left,right):
    counts=[]
    for sequence in tower:
        # Omitting zeros gives the right-hand variation at a square-free root.
        # Subtract a right-endpoint root to count the open interval (left,right).
        count=P.variations(sequence,left)-P.variations(sequence,right)-int(P.value(sequence[0],right)==0)
        require(count>=0,'negative open root count');counts.append(count)
    distinct=counts[0] if counts else 0
    odd=sum((-1)**i*n for i,n in enumerate(counts))
    require(0<=odd<=distinct,'invalid odd root count')
    return distinct,odd


def prepare(candidates):
    require(type(candidates) is list and 2<=len(candidates)<=8,'provide 2..8 candidates')
    names=[];invoices=[]
    for item in candidates:
        require(type(item) in (list,tuple) and len(item)==2,'candidate needs a name and invoice')
        name,invoice=item
        require(type(name) is str and 0<len(name)<=128 and name not in names,'candidate names must be unique')
        names.append(name);invoices.append(P.INVOICES['validate_invoice'](invoice,name))
    deltas=[P.INVOICES['compare_invoices'](invoices[0],v)['signed_net_delta'] for v in invoices]
    base,exponents=P.common_base(sorted({int(r) for delta in deltas for r in delta}))
    polynomials=[]
    for delta in deltas:
        poly=[0]*(max(exponents.values(),default=0)+1)
        for rank,count in delta.items():poly[exponents[int(rank)]]=count
        polynomials.append(P.trim(poly))
    pairs={}
    for i in range(len(names)):
        for j in range(i+1,len(names)):
            poly=difference(polynomials[j],polynomials[i])
            pairs[i,j]=(poly,root_tower(poly))
    return names,invoices[0]['contract'],base,polynomials,pairs


def compare(candidates,max_nodes=255,max_depth=24):
    require(type(max_nodes) is int and 1<=max_nodes<=4095,'max_nodes must be in 1..4095')
    require(type(max_depth) is int and 0<=max_depth<=40,'max_depth must be in 0..40')
    names,contract,base,polynomials,pairs=prepare(candidates)
    def minima(x):
        values=[P.value(p,x) for p in polynomials];best=min(values)
        return [i for i,v in enumerate(values) if v==best]
    def certificate(winner,left,right):
        comparisons=[]
        for j in range(len(names)):
            if j==winner:continue
            i,k=sorted((j,winner));poly,tower=pairs[i,k]
            if not poly:
                comparisons.append({'other':names[j],'relation':'identical'});continue
            distinct,odd=roots(tower,left,right)
            if odd:return None
            sign=1 if winner==i else -1
            for denominator in range(2,len(poly)+2):
                sample=left+(right-left)/denominator
                value=sign*P.value(poly,sample)
                if value:break
            require(bool(value),'nonzero sample not found')
            if value<0:return None
            comparisons.append({'other':names[j],'relation':'nonnegative','distinct_equalities':distinct,
                                'odd_roots':odd,'sample_x':str(sample),'sample_value':str(value)})
        return comparisons
    pending=[(Q(1),Q(base),0)];allocated=1;cells=[]
    while pending:
        left,right,depth=pending.pop();sample=(left+right)/2
        middle=minima(sample);proofs={}
        for winner in middle:
            proof=certificate(winner,left,right)
            if proof is not None:proofs[names[winner]]=proof
        if proofs:
            cells.append({'left':str(left),'right':str(right),'classification':'certified',
                          'uniform_minimizers':list(proofs),'comparisons':proofs})
        elif depth<max_depth and allocated+2<=max_nodes:
            allocated+=2;pending.extend(((sample,right,depth+1),(left,sample,depth+1)))
        else:
            cells.append({'left':str(left),'right':str(right),'classification':'unresolved',
                          'sample_x':str(sample),'sample_minimizers':[names[i] for i in middle],
                          'reason':'node_or_depth_limit'})
    cells.sort(key=lambda row:Q(row['left']))
    boundaries=sorted({Q(row[k]) for row in cells for k in ('left','right')})
    return {'schema':'integer-mult-candidate-power-regions/v1','contract':contract,'base':base,
            'substitution':'x=base^t; open domain 1<x<base corresponds to 0<t<1',
            'relative_polynomials':{name:list(poly) for name,poly in zip(names,polynomials)},
            'reference_candidate':names[0],'cells':cells,'allocated_nodes':allocated,
            'unresolved_cells':sum(row['classification']=='unresolved' for row in cells),
            'boundaries':[{'x':str(x),'minimizers':[names[i] for i in minima(x)],
                           'in_open_domain':1<x<base} for x in boundaries],
            'scope':'Exact arithmetic on the declared common-base differences. Certified cells '
                    'are open intervals. Additional isolated ties are counted in comparisons, '
                    'not located. Unresolved cells have no certified winner. No source legality '
                    'or complete kappa admission is proved.'}


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--candidate',nargs=2,action='append',required=True,metavar=('NAME','INVOICE'))
    parser.add_argument('--max-nodes',type=int,default=255);parser.add_argument('--max-depth',type=int,default=24)
    args=parser.parse_args(argv)
    try:
        require(2<=len(args.candidate)<=8,'provide 2..8 candidates')
        candidates=[];inputs=[]
        for name,path in args.candidate:
            invoice,pin=P.INVOICES['load_invoice'](path);candidates.append((name,invoice));inputs.append({'name':name,**pin})
        result=compare(candidates,args.max_nodes,args.max_depth);result['inputs']=inputs
    except (OSError,ValueError,TypeError,RecursionError) as exc:
        print(json.dumps({'status':'INVALID_CANDIDATE_COMPARISON','error':str(exc)}),file=sys.stderr);return 2
    print(json.dumps(result,indent=2,sort_keys=True));return 0


if __name__=='__main__':raise SystemExit(main())
