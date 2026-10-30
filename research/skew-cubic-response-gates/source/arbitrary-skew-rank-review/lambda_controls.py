#!/usr/bin/env python3
"""Exact small controls for the two-sided support-length lemma.
Apache-2.0; substantial OpenAI Codex assistance. No circuit search.
"""
from fractions import Fraction as F
from pathlib import Path
import argparse,json
HERE=Path(__file__).resolve().parent
def need(c,m):
    if not c:raise ValueError(m)
def mm(A,B):return [[sum(A[i][k]*B[k][j]for k in range(len(A)))for j in range(len(A))]for i in range(len(A))]
def adj(A):return [list(x)for x in zip(*A)]
def support(A):return max(max(sum(x!=0 for x in row)for row in A),max(sum(x!=0 for x in col)for col in zip(*A)))
def run():
    I=[[F(1),F(0)],[F(0),F(1)]];H=[[F(3,5),F(4,5)],[F(4,5),F(-3,5)]]
    S=[[F(0),F(1)],[F(1),F(0)]];Z=[[F(1),F(0)],[F(0),F(-1)]];V=[[F(3,5),F(4,5)],[F(-4,5),F(3,5)]]
    mats=[I,H,S,Z,V]
    for A in mats:need(mm(A,adj(A))==I==mm(adj(A),A)and support(A)==support(adj(A)),'orthogonal inverse and two-sided support')
    for A in mats:
        for B in mats:need(support(mm(A,B))<=support(A)*support(B),'product row/column union bound')
        for P in(S,Z):need(support(mm(A,P))==support(A)==support(mm(P,A)),'weighted monomial invariance')
    need(mm(H,H)==I and support(H)==2 and support(mm(H,H))==1,'cancellation does not invalidate upper union bound')
    # J=iH is a non-Clifford unitary skew response; the scalar phase does not
    # affect support and J^2=-H^2=-I. No native implementation is asserted.
    return dict(status='PASS_EXACT_TWO_SIDED_SUPPORT_CONTROLS',orthogonal_matrices=5,product_pairs=25,non_clifford_skew_example='i times [[3/5,4/5],[4/5,-3/5]]',cancellation_control=True,scope='Finite corroboration only; written union-bound proof supplies the arbitrary-dimension lemma.',no_native_implementation_claim=True)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');args=p.parse_args();out=run();path=HERE/'LAMBDA-CONTROLS.json'
    if args.write:path.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    else:need(json.loads(path.read_text())==out,'saved support controls')
    print(out['status'])
