#!/usr/bin/env python3
"""Finite paired vacancy decoder; explicit obstruction to four-term lift.

The operator-shear identity is all-size. Cheap shear expansion is NOT.
Apache-2.0. Substantial OpenAI Codex assistance.
"""
import argparse
from fractions import Fraction as Q
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
def need(b,m):
    if not b:raise ValueError(m)
def plus(a,b):
    z=dict(a)
    for x,(r,i)in b.items():
        u,v=z.get(x,(Q(0),Q(0)));z[x]=(u+r,v+i)
        if z[x]==(0,0):del z[x]
    return z
def scale(a,c):return{x:(r*c,i*c)for x,(r,i)in a.items()if c}
def times(a,b):
    z={}
    for x,(r,i)in a.items():
        for y,(u,v)in b.items():z=plus(z,{x^y:(r*u-i*v,r*v+i*u)})
    return z
ONE={0:(Q(1),Q(0))}
def gate(v,sgn):return {0:(Q(1,2),Q(sgn,2)),v:(Q(1,2),Q(-sgn,2))}
def vacancy(k):
    a=ONE;b=ONE;squared=0
    for j in range(k):
        q,r=1<<(2*j),1<<(2*j+1);squared^=q^r
        a=times(a,times(gate(q,-1),gate(r,-1)))
        b=times(b,times(gate(q,1),gate(r,1)))
    need(times(a,b)==ONE and times(a,a)=={squared:(Q(1),Q(0))},'tensor vacancy inverse and monomial square')
    return a,b,squared
def serial(a):return[[x,str(r),str(i)]for x,(r,i)in sorted(a.items())]
def rows_serial(z):return[[serial(v)for v in row]for row in z]

def witness(k):
    A,B,squared=vacancy(k)
    # Two arbitrary independent input fields; each polynomial coefficient
    # acts on its own complete 2^(2k)-dimensional translation module.
    z=[[A,{}],[{},A]]
    z[1]=[times({squared:(Q(1),Q(0))},v)for v in z[1]]
    need(z==[[A,{}],[{},B]],'second vacancy turned into its inverse by monomial')
    z=[list(map(lambda v:scale(v,-1),z[1])),z[0]]
    z[0]=[plus(x,times(B,y))for x,y in zip(z[0],z[1])]
    z[1]=[plus(y,scale(times(A,x),-1))for x,y in zip(z[0],z[1])]
    z[0]=[plus(x,times(B,y))for x,y in zip(z[0],z[1])]
    need(z==[[ONE,{}],[{},ONE]],'entire paired decoder all independent data columns')
    return {'k':k,'scalar_input_columns':2*(1<<(2*k)),'vacancy_kernel':serial(A),
        'inverse_kernel':serial(B),'square_translation':squared,
        'each_operator_shear_translation_terms':len(A),
        'three_operator_shear_scalar_ADDs':3*len(A),
        'coefficient_absolute_sum_exact':'2^k',
        'endpoint_operator_rows':rows_serial(z)}

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--write',action='store_true');a=ap.parse_args()
    cases=[witness(k)for k in(1,2,3)]
    A2,_,_=vacancy(2);A1,_,_=vacancy(1)
    need(len(A1)==4 and len(A2)==16 and A1!=A2,'wrong constant four-term lift rejected')
    out={'status':'PASS_FINITE_PAIR_DECODER_NO_CHEAP_ALL_SIZE_BINDING',
        'scientific_pin':'20ecf2891d80b5acf18d980b2164fb44ea7faa90',
        'all_size_operator_identity':'For ANY invertible A with A^2 monomial, inputs(Au,Av) become(Au,A^-1v) after that monomial on field2. SignedSWAP(-y,x), x+=A^-1y, y-=Ax, x+=A^-1y then give(u,v). These are operator shears, not native-free operations by themselves.',
        'native_vacancy':'A_k=(C_q^-1 C_r^-1)^tensor k, A_k^2 is the tensor Pauli/address monomial.',
        'finite_cases':cases,
        'finite_k1_expansion':'A_1=(-i I + X_q + X_r + i X_(q+r))/2; inverse conjugates i. Four primitive translation ADDs implement one shear only at k1.',
        'paid_changes':['Finite k1: three operator shears expand12 signed dyadic complex ADDs; signedSWAP uses3 ordinary ADDs and one sign (or a separately paid physical signed field swap).','Every translation source prepare/unprepare, dyadic scalar multiplication/ADD, phase/sign and physical scan is paid; no private or ordinary auxiliary field is used.','At general k direct expansion requires3*4^k scalar translation ADDs, plus source prepare/unprepare and signedSWAP.','Sequential tensor-factor lowering uses O(k) complete-field scans for source prepare/unprepare, not a fixed number of scalar primitives. Precision/amplification may grow with k.'],
        'actual_frames':'For finite common vacancy frame F A, address translations commute F A and preserve common field representatives; the expanded shears have matching framed operands. This does not make A_k itself a constant-cost primitive for unbounded k.',
        'negative_control':'Reuse k1 four-term kernel at k2: support4 versus exactsupport16 and actual operator mismatch. Rejected.',
        'remaining_obligation':'Provide an explicit all-k fixed-poly(m) paid operator-shear implementation or a true native frame cancellation. Neither is supplied. No query-saving all-size caller or favorable exponent follows.',
        'attribution':'This lane proposed paired complementary defects and emitted exact group-algebra decoder. Recursive/complex lanes identified and checked the critical tensor-lift support/scan cost. The initial unconditional zero-query extrapolation is retracted.',
        'claim':'Finite exact algebra and an explicit failed cost lift; no new kappa.'}
    out=json.loads(json.dumps(out));p=HERE/'PAIR-DECODER.json'
    if a.write:p.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    else:need(json.loads(p.read_bytes())==out,'stored pair decoder differs')
    print(out['status']);print([(v['k'],v['each_operator_shear_translation_terms'])for v in cases])

if __name__=='__main__':main()
