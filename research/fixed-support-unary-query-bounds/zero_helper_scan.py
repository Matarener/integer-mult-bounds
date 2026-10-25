#!/usr/bin/env python3
"""Exact zero-native-query Fourier word with a linear-in-f scan tariff.

Both field arrays are arbitrary independent dirty public inputs. Every
coefficient is Gaussian dyadic; the complete per-bit ADD loop is counted.
Apache-2.0; substantial OpenAI Codex assistance.
"""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
from fractions import Fraction as F
import argparse,json
HERE=Path(__file__).resolve().parent
Z=(F(0),F(0));I=(F(1),F(0));alpha=(F(1,2),F(1,2));beta=(F(1,2),F(-1,2))
def need(b,m):
    if not b:raise ValueError(m)
def add(a,b):return (a[0]+b[0],a[1]+b[1])
def neg(a):return (-a[0],-a[1])
def mul(a,b):return (a[0]*b[0]-a[1]*b[1],a[0]*b[1]+a[1]*b[0])
def independent(D):return [[[I if k==b*D+j else Z for k in range(2*D)] for j in range(D)] for b in range(2)]
def apply(state,op):
    typ=op[0]
    if typ=='ADD':
        _,dst,src,c,mask=op
        state[dst]=[[add(x,mul(c,y)) for x,y in zip(row,state[src][j^mask])] for j,row in enumerate(state[dst])]
    elif typ=='SWAP':state[0],state[1]=state[1],state[0]
    elif typ=='ADDRESS_FIRST':state[0]=[state[0][j^op[1]][:] for j in range(len(state[0]))]
    else:state[0]=[[neg(c) for c in row] for row in state[0]]
def inverse(op):return (op[0],op[1],op[2],neg(op[3]),op[4]) if op[0]=='ADD' else op
def word(bits):
    ops=[]
    for j in range(bits):
        x=1<<j
        ops.extend([('ADD',0,1,alpha,0),('ADD',0,1,beta,x),
                    ('ADD',1,0,neg(beta),0),('ADD',1,0,neg(alpha),x),
                    ('ADD',0,1,alpha,0),('ADD',0,1,beta,x),('SWAP',),('SIGN_FIRST',)])
    return ops
def target(bits,both_forward=False):
    D=1<<bits;out=[[[Z for _ in range(2*D)] for _ in range(D)] for _ in range(2)]
    for b in range(2):
        same,different=(beta,alpha) if b==0 and not both_forward else (alpha,beta)
        for y in range(D):
            for x in range(D):
                c=I
                for j in range(bits):c=mul(c,different if ((x^y)>>j)&1 else same)
                out[b][y][b*D+x]=c
    return out
def case(m,f):
    bits=m*f;D=1<<bits;ops=word(bits);state=independent(D)
    for op in ops:apply(state,op)
    expected=target(bits);need(state==expected,'every arbitrary dirty-input coefficient has the full tensor chirp target')
    # C_total^2=X_all; one further ADDRESS permutation changes the inverse
    # first output to the same forward orientation as the second output.
    orientation=('ADDRESS_FIRST',D-1);apply(state,orientation);ops.append(orientation)
    expected=target(bits,True);need(state==expected,'both full native outputs in the same forward orientation')
    need(all(c!=Z for b in range(2) for row in state[b] for c in row[b*D:(b+1)*D]),'full row support on both independent public fields')
    for op in reversed(ops):apply(state,inverse(op))
    need(state==independent(D),'literal inverse restores both arbitrary input arrays')
    bad=independent(D)
    for op in ops[1:]:apply(bad,op)
    need(bad!=expected,'one omitted scalar ADD is detected')
    return {'m':m,'f':f,'address_bits':bits,'cells_per_field':D,'independent_input_columns':2*D,
            'all_coefficients':True,'literal_inverse':True,'omitted_ADD_detected':True,
            'native_queries':0,'initialized_or_helper_fields':0,
            'field_array_ADDs':6*bits,'field_array_SWAPS':bits,'field_array_sign_scans':bits,
            'final_ADDRESS_orientation_scans':1,
            'native_rank_mass':0,'full_native_output_rank_mass':2*m}
def receipt():
    need(add(alpha,beta)==I and mul(alpha,alpha)==(F(0),F(1,2)),'exact Gaussian dyadic chirp coefficients')
    return {'status':'PASS_ZERO_HELPER_SCAN_COUNTEREXAMPLE_NO_KAPPA',
            'scientific_pin':'20ecf2891d80b5acf18d980b2164fb44ea7faa90',
            'cases':[case(m,f) for m,f in ((1,1),(1,2),(1,3),(2,2))],
            'all_f_identity':'For every internal bit j, C_j=alpha I+beta X_j, C_j^-1=beta I+alpha X_j, alpha=(1+i)/2,beta=(1-i)/2. The three operator shears a+=C_j b; b-=C_j^-1 a; a+=C_j b, followed by swap and sign on first field, yield (C_j^-1 a_old,C_j b_old). Each shear expands into two scalar/ADDRESS ADDs. Different bit factors commute, giving full tensor chirps on both independent arrays for all m,f>=1.',
            'cost_boundary':'There are exactly6mf complete field-array ADD scans,mf field-array swaps,mf sign scans andone final ADDRESS orientation scan, before controller/address/head costs. This is O(mf) scans, not a constant number independent of f. In the ideal array arithmetic model it costs O(mf*2^(mf)) operations; actual fixed-tape routing can only add cost.',
            'logical_consequence':'No universal native-rank-mass floor sum r>=mn follows from zero-helper arbitrary dirty linear algebra alone: native mass0 produces2 full-native m outputs. A valid lower bound needs a quantitative primitive scan/access/conditioning premise. This counterexample does not satisfy the desired constant-scan local cost and gives no kappa gain.',
            'scope':'Allowed monomials are explicitly ADDRESS bit flips, scalar Gaussian dyadics, bank swap and sign. No initialized ancilla, cross-input correlation, hidden Fourier ADD, or unpriced f loop is used.',
            'no_new_kappa':True}
def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--write',action='store_true');a=ap.parse_args()
    out=receipt();p=HERE/'ZERO-HELPER-SCAN-COUNTEREXAMPLE.json'
    if a.write:p.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    else:need(json.loads(p.read_bytes())==out,'saved zero-helper scan counterexample differs')
    print(out['status']);print('Arbitrary dirty coefficients and literal inverse; zero native queries, exactly6mf ADD scans, no constant-scan or kappa claim.')
if __name__=='__main__':main()
