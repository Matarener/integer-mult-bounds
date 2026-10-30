#!/usr/bin/env python3
"""Exact local equality between conjugated factory rank and new progress.
Apache-2.0; substantial OpenAI Codex assistance. Not a bank-network no-go.
"""
from pathlib import Path
import argparse
import hashlib
import json
from native_model import *
from orthogonal_source_normalizer import reflection

HERE=Path(__file__).resolve().parent


def run():
    checks=[]
    for f in(1,2,3):
        z=Model(f,3)
        R,_=reflection(z,3,(0,1,2,4))
        P=mul(R,z.P[1],R)
        T=mul(P,z.N,P.adjoint())
        B=mul(z.N,P,z.N.adjoint())
        progress=mul(z.N,T)
        same(mul(B,P.adjoint()),mul(phase(z.n,2),progress),'actual all-f minus sign in local tradeoff')
        ranks={'P_prime':b.native_rank(P),'T_prime':b.native_rank(T),
               'conjugated_factory':b.native_rank(B),'N_T_prime':b.native_rank(progress),
               'standard_N_N2':b.native_rank(mul(z.N,z.T[1]))}
        need(ranks=={'P_prime':0,'T_prime':2*f,'conjugated_factory':2*f,
                     'N_T_prime':2*f,'standard_N_N2':4*f},'local factory-progress ranks')
        completion=mul(z.N,z.T[1],progress.adjoint())
        old_commutator=mul(P,z.T[0],P.adjoint(),z.T[0].adjoint())
        need(b.native_rank(completion)==4*f,'literal standard-target compensation rank')
        need(b.native_rank(old_commutator)==2*f,'old fresh chart is not preserved')
        checks.append({'f':f,'native_arities':ranks,
                       'exact_standard_target_completion_arity':4*f,
                       'old_N1_frame_commutator_arity':2*f,
                       'actual_Gaussian_minus_sign_verified':True})
    return {'status':'PASS_ALL_F_LOCAL_FACTORY_PROGRESS_TRADEOFF',
            'scientific_pin':PIN,'producer_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'source_pins':[{'path':str(HERE/p),'sha256':hashlib.sha256((HERE/p).read_bytes()).hexdigest()}
                           for p in('native_model.py','orthogonal_source_normalizer.py','conjugated_factory.py')],
            'all_parameter_identity':'For any invertible monomial Clifford P and actual N with N^2=-I, define T=P N P^-1. Then (N P N^-1) P^-1=-N T. This is a literal operator equality, including the global minus sign, for every ambient dimension and f.',
            'all_parameter_rank_equality':'Native Clifford arity is the rank of its binary B block. Right or left multiplication by an invertible monomial Clifford and a global scalar preserves that rank. Therefore arity(Ad_N(P))=arity(N T) exactly. In particular a cheap2f factory conjugate cannot simultaneously supply independent common+new progress of arity4f through this same P and T.',
            'local_compensation_lower_bound':'For Clifford operators A,B, B_(AB)=A_A B_B+B_A D_B, so rank B_(AB)<=rank B_A+rank B_B. Any unary compensation word, with arbitrary monomial Clifford adapters between its native children, increasing a2f operator to actual nativearity4f needs sum additional native arities>=2f. This is a single-field endpoint statement and does not assume the marked-residual bridge grammar.',
            'specific_two_sided_factory':'P_prime=R P2 R, R=ADDRESS(I+vv^T), v=(p0,q0,p1,p2); T_prime=P_prime N0 P_prime^-1. The cheap conjugate of CONJUGATED-FACTORY.json is valid, but N0*T_prime has arity2f, while N0*N2 has arity4f. The literal standard-target correction (N0*N2)(N0*T_prime)^-1 has arity4f. P_prime also changes the oldN1 chart: its commutator with N1 has arity2f.',
            'all_f_lift':'The reflection and P2 are bitwise tensor families, and N_f^2=-I is already an exact all-f identity with one global i per plane. The rank equality and compensation inequality are written dimension-independent proofs. The displayed specific ranks follow by tensor-direct-sum B rank; the actual sign is checked independently at f1/f2/f3. No claim N_f*T_prime,f=(N_1*T_prime,1)^tensor f is made without its global phase.',
            'actual_checks':checks,
            'scope':['The two-sided reflection factory lowering remains a legitimate local native resource.',
                     'A different source/delivery map or a bank-coupled word may change the pair P,T and is not excluded.',
                     'A sum of paths, borrowed inputs, dirty helpers and source reads requires its complete independent-column analysis; the unary rank inequality does not replace that.',
                     'No supplier, stock surplus, precision, all-size or tape conclusion follows.'],
            'no_new_kappa':True}


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--write',action='store_true');args=p.parse_args()
    out=json.loads(json.dumps(run()));path=HERE/'SOURCE-PROGRESS-TRADEOFF.json'
    if args.write:path.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    else:need(json.loads(path.read_text())==out,'saved source progress tradeoff differs')
    print(out['status'])
