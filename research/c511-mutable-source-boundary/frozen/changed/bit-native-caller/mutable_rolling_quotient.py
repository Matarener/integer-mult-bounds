#!/usr/bin/env python3
"""Common scalar readout rank for the actual raw rolling-word defect.

This is an information bound for ADDRESS-independent scalar source rows,
not a native-query rank or a bound against routed/address-dependent readers.
Apache-2.0. Prepared with substantial OpenAI Codex assistance.
"""
from pathlib import Path
from hashlib import sha256
import argparse
import gzip
import json
from mutable_rolling_boundary import receipt as boundary,mod,mv,need,RAW
from physical_code import actual_routes,bits

HERE=Path(__file__).resolve().parent

def receipt(write=False):
    checked=boundary(False)
    pin=json.loads((HERE/'MUTABLE-SOURCE-FIVE.json').read_bytes());C=pin['C_binary_rows']
    raw=json.loads(gzip.decompress(RAW.read_bytes()));rhos,Ps,_=actual_routes(raw)
    prime=101;m=15;r=[mod(a,prime)for a in rhos];P=[mod(a,prime)for a in Ps]
    basis={};rows=[];summaries=[]
    for j in range(8):
        v=tuple(int(i==j)for i in range(m));mid=[]
        for k in range(111):
            t=mv(P[k],v[:8],prime)+(0,)*7
            h=tuple((a-b)%prime for a,b in zip(v,t))
            mid.append((mv(r[k],h,prime),mv(r[k],t,prime)))
        nonfree=0;support=0
        for p,cp in enumerate(C):
            coeff={}
            t=mv(P[p],v[:8],prime)+(0,)*7
            h=tuple((a-b)%prime for a,b in zip(v,t))
            # Destructive control: setting C0=C1=I must make Phi=N+N=0.
            # The actual routed identity edge is rho_p*rho_p, not an
            # independently chosen or scalar ADDRESS adapter.
            hh,tt=mid[p]
            need(mv(r[p],hh,prime)+mv(r[p],tt,prime)==h+t,
                 'identity-code native impulse control cancels exactly')
            coeff[h+t]=1<<p
            for k in bits(cp):
                h,t=mid[k];at=mv(r[p],h,prime)+mv(r[p],t,prime)
                coeff[at]=coeff.get(at,0)^C[k]
            for at,row in sorted(coeff.items()):
                if not row or not any(at[m:]):continue
                nonfree+=1;support|=row
                witness={'input_HEAD_basis':j,'output_port':p,'output_HEAD':list(at[:m]),'output_TAIL':list(at[m:]),'coefficient_SOURCE_row':row}
                rows.append([j,p,list(at),row])
                z=row
                for pivot,(b,_)in sorted(basis.items(),reverse=True):
                    if(z>>pivot)&1:z^=b
                if z:
                    pivot=z.bit_length()-1;basis[pivot]=(z,witness)
        summaries.append({'input_HEAD_basis':j,'nonfree_coefficient_rows':nonfree,'nonzero_SOURCE_columns':support.bit_count(),'accumulated_rank':len(basis)})
    # Each row is obtained by fixing one common input ADDRESS and projecting
    # one actual output impulse. Any scalar source-readout factorization
    # Phi=sum_i A_i (c_i^T tensor I_ADDRESS), modulo a head/tail-free map,
    # puts every row in span{c_i}, since a free map cannot emit nonzero tail
    # ADDRESS from a tail0 input. Hence t>=the certified binary row rank.
    need(len(basis)==111,'full111 common scalar SOURCE-row rank on actual ADDRESS samples')
    saved=[{'pivot':p,'reduced_row':v[0],'original_row_witness':v[1]}for p,v in sorted(basis.items(),reverse=True)]
    out={'status':'PASS_ACTUAL_ROLLING_COMMON_SCALAR_QUOTIENT_FLOOR','no_new_kappa':True,
         'scientific_pin':pin['scientific_pin'],'C_order':511,'ADDRESS_field':prime,
         'operator':'Phi=N+C1*N*C0, an actual unclosed block of N_global*R3',
         'input_samples':'For each core coordinate j=0..7, all111 source ports carry an arbitrary VALUE coefficient on the same HEAD=e_j,TAIL0 impulse.',
         'projected_outputs':'Every output port/ADDRESS with nonzero TAIL; such an impulse is absent from any admitted head/tail-separate free output map.',
         'sampled_coefficient_row_rank':len(basis),'per_sample':summaries,
         'row_echelon_certificate':saved,'all_nonzero_coefficient_rows':len(rows),
         'complete_coefficient_rows_sha256':sha256(json.dumps(rows,separators=(',',':')).encode()).hexdigest(),
         'identity_code_negative_control':'C0=C1=I gives Phi=N+N=0 on all111*8 sampled impulses, with the actual rho_p*rho_p ADDRESS adapters.',
         'source_receipt_sha256':sha256((HERE/'MUTABLE-SOURCE-FIVE.json').read_bytes()).hexdigest(),
         'bound':'If the correction uses t ADDRESS-independent common scalar source rows c_i, i.e. Phi=H_free+sum_i A_i*(c_i^T tensor I_ADDRESS), every sampled coefficient row lies in span{c_i}; therefore t is at least the displayed exact binary rank.',
         'limits':['No native-query cost follows from this information rank alone.','Routed readouts, ADDRESS-dependent source rows, direct public-input access, extra native source queries and changed coupled words are outside this factorization.','The samples give a lower bound for this actual raw word, not a rank9 code obstruction or all-caller lower bound.'],
         'attribution':'Source code and roots are pinned predecessor data. This lane computes the actual routed operator samples and exact scalar-quotient floor.'}
    out=json.loads(json.dumps(out));p=HERE/'MUTABLE-ROLLING-QUOTIENT.json'
    if write:p.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    else:need(json.loads(p.read_bytes())==out,'saved scalar-quotient certificate differs')
    return out

if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--write',action='store_true');a=ap.parse_args();o=receipt(a.write)
    print(o['status'],'common scalar readouts >=',o['sampled_coefficient_row_rank'])
