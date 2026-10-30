#!/usr/bin/env python3
"""Two exact mechanism admission tests at kappa=1/256. Apache-2.0.

Douglas Colkitt, with OpenAI Codex assistance. No supplier is constructed.
"""
import argparse
from collections import Counter
from fractions import Fraction as Q
import hashlib
import importlib.util
from itertools import combinations
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]


def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    result=importlib.util.module_from_spec(spec); spec.loader.exec_module(result)
    return result


H=module('eighth_rank_tools',HERE.parent/'higher-rank-sixteenth/screen.py')
B=module('eighth_budget_tools',HERE.parent/'shared-core-blocks/audit.py')


def inverse(matrix):
    n=len(matrix)
    rows=[[Q(x) for x in row]+[Q(i==j) for j in range(n)]
          for i,row in enumerate(matrix)]
    for j in range(n):
        pivot=next(i for i in range(j,n) if rows[i][j])
        rows[j],rows[pivot]=rows[pivot],rows[j]
        value=rows[j][j]; rows[j]=[x/value for x in rows[j]]
        for i in range(n):
            if i!=j:
                value=rows[i][j]
                rows[i]=[x-value*y for x,y in zip(rows[i],rows[j])]
    result=[row[n:] for row in rows]
    assert H.mm(matrix,result)==[[int(i==j) for j in range(n)] for i in range(n)]
    return result


def extend(basis,vector,p=101):
    row=[x%p for x in vector]
    for pivot,b in basis:
        value=row[pivot]
        if value:row=[(x-value*y)%p for x,y in zip(row,b)]
    pivot=next((i for i,x in enumerate(row) if x),None)
    if pivot is None:return basis
    scale=pow(row[pivot],-1,p)
    return tuple(sorted(basis+((pivot,tuple(x*scale%p for x in row)),)))


def folded_geometry():
    n=16; generators=(1,2,4,8,15)
    adjacency=[{i^g for g in generators} for i in range(n)]
    C=[[int(i==j or j in adjacency[i]) for j in range(n)] for i in range(n)]
    binary_rows=[sum(x<<j for j,x in enumerate(row)) for row in C]
    assert H.binary_rank(binary_rows)==6 and H.rank(C)==16
    # Twice a Gram matrix: diagonal 2, zero on edges, one on nonedges.
    G=[[2 if i==j else 0 if j in adjacency[i] else 1 for j in range(n)] for i in range(n)]
    assert H.rank(G)==6
    selected=[0,1,2,3,4,8]
    form=inverse([[G[i][j] for j in selected] for i in selected])
    vectors=[tuple(G[i][j] for i in selected) for j in range(n)]
    reconstructed=H.mm(H.mm(vectors,form),list(map(list,zip(*vectors))))
    assert reconstructed==G
    projectors=[]
    for u in vectors:
        dual=H.mm([u],form)[0]
        P=[[Q(x*y,2) for y in dual] for x in u]
        assert H.rank(P)==1 and H.mm(P,P)==P
        projectors.append(P)
    zero=[[0]*6 for _ in range(6)]
    for i in range(n):
        for j in adjacency[i]:
            assert H.mm(projectors[i],projectors[j])==zero
    assert any(H.mm(projectors[i],projectors[j])!=H.mm(projectors[j],projectors[i])
               for i in range(n) for j in range(i))
    return C,G,vectors,form,projectors


def span_capacities(vectors):
    # If a rational support has rank <=r, its rank modulo 101 is <=r.
    # Every such modular span has a basis of <=r input vectors; enumerate
    # all these bases, then their closures. This gives safe rational caps.
    maximum={}; witnesses={}; enumerated=0
    for size in range(6):
        for subset in combinations(range(16),size):
            basis=()
            for j in subset:basis=extend(basis,vectors[j])
            closure=[j for j,v in enumerate(vectors) if len(extend(basis,v))==len(basis)]
            r=len(basis); enumerated+=1
            if len(closure)>maximum.get(r,-1):
                maximum[r]=len(closure);witnesses[r]=closure
    assert enumerated==6885
    assert maximum=={0:0,1:1,2:2,3:4,4:6,5:10}
    # Rational witnesses attain each modular upper bound: the capacities
    # are exact for these rational labels, not just finite-field guesses.
    for r,ids in witnesses.items():
        if r:assert H.rank([vectors[i] for i in ids])==r
    maximum[6]=16; witnesses[6]=list(range(16))
    assert all(4*maximum[r]<=9*r-5 for r in range(1,6))
    # Independent integer partition control of the source-coverage bound.
    best=-1;best_counts=None;feasible=0
    def visit(r,remaining,counts):
        nonlocal best,best_counts,feasible
        if r==7:
            if sum(counts)>=6:
                feasible+=1
                covered=sum(count*maximum[k] for k,count in enumerate(counts,1))
                if covered>best:best=covered;best_counts=counts
            return
        for count in range(remaining//r+1):visit(r+1,remaining-r*count,counts+[count])
    visit(1,10,[])
    assert best==15
    return dict(modulus=101, subsets_enumerated=enumerated,
                maximum_support_by_rank=maximum, rational_witness_supports=witnesses,
                budget_ten_with_at_least_six_channels=dict(maximum_total_support=best,
                    rank_multiplicities=best_counts,partitions_checked=feasible))


def audit():
    saving=Q(9,2000)
    # This weaker exponent is below even the necessary admitted threshold
    # 1/255. Failure here cannot be rescued by tightening our 0.0045 budget.
    tensor=H.block_budget(110,5,Q(1,256),Q(0))
    assert tensor['moment_interval'][0]>1
    assert tensor['added_role_moment_interval'][0]>1
    C,G,vectors,form,projectors=folded_geometry()
    optimistic=B.ideal_budget(6,1,saving,Q(6,16),Q(6,16*6))
    assert optimistic['moment_interval'][1]<1
    loss_nine=B.ideal_budget(6,1,saving,Q(6,16),Q(9,16*6))
    loss_ten=B.ideal_budget(6,1,saving,Q(6,16),Q(10,16*6))
    assert loss_nine['moment_interval'][1]<1<loss_ten['moment_interval'][0]
    spans=span_capacities(vectors)
    # Any scalar factor C=AB needs >=6 nonzero channels. Every source
    # occurs since C has unit diagonal. Span cost <=10 covers at most15
    # sources, so the conservative copied-center loss is at least11.
    minimum_loss=11
    deficit_upper=2*16-3*minimum_loss
    assert deficit_upper==-1
    sources=[HERE.parent/'higher-rank-sixteenth/screen.py',
             HERE.parent/'shared-core-blocks/audit.py',HERE/'budget.json']
    return H.encode(dict(
        status='Two scoped candidates rejected; no new supplier or kappa.',
        target='1/256', illustrative_primitive_saving=saving,
        fractional_cycle_tensor=dict(d=110,r=5,**{'two_axis_zero_auxiliary_screen':tensor},
            decision='Still excluded at 1/256 in the stated two-axis ledger, even with no auxiliary roles or central loss.'),
        folded_five_cube=dict(v=16,d=6,r=1,binary_scalar_rank=6,rational_scalar_rank=16,
            scalar_matrix=C,gram_matrix=G,label_vectors=vectors,common_form=form,
            projectors=projectors,optimistic_budget=optimistic,span_capacity_certificate=spans,
            loss_nine_relaxation=loss_nine,loss_ten_relaxation=loss_ten,
            largest_integer_loss_admitted_by_minimum_stock_relaxation=9,
            minimum_copied_source_loss=minimum_loss,deficit_upper_bound=deficit_upper,
            decision='Valid noncommuting geometry and optimistic numerical pass; no positive deficit with the tested conservative copied-source compiler, including overcomplete scalar factorizations.'),
        scope='The tensor compiler and the folded-cube labels/source-copy contract are fixed. Other geometries and producer interfaces are not excluded.',
        next_requirement='A concrete operation changing paid source collection/readout or recursive boundaries; no automatic larger search or reopening of the retired inventory.',
        source_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--write',action='store_true');args=parser.parse_args()
    result=audit();dest=HERE/'repricing.json'
    if args.write:dest.write_text(json.dumps(result,indent=2)+'\n')
    else:assert json.loads(dest.read_text())==result,'certificate drift'
    tensor=result['fractional_cycle_tensor']['two_axis_zero_auxiliary_screen']
    folded=result['folded_five_cube']
    print(json.dumps(dict(status=result['status'],
        tensor_moment_interval=[float(Q(x)) for x in tensor['moment_interval']],
        folded_optimistic_interval=[float(Q(x)) for x in folded['optimistic_budget']['moment_interval']],
        folded_loss_at_least=folded['minimum_copied_source_loss'],
        folded_deficit_at_most=folded['deficit_upper_bound']),indent=2))
