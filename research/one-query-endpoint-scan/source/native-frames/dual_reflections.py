#!/usr/bin/env python3
"""Exact dual unpaired ADDRESS reflections and all18 one-child conjugates.
Apache-2.0; substantial OpenAI Codex assistance. Local native admission only.
"""
from pathlib import Path
import argparse
import hashlib
import json
from native_model import *
from orthogonal_source_normalizer import reflection
from conjugated_reflection import tensor_monomial
from lifted_algebra import Algebra

HERE=Path(__file__).resolve().parent


def role_duality(model):
    rows=[1<<j for j in range(model.n)]
    for plane in range(3):
        for k in range(model.f):
            p,q=2*plane*model.f+k,(2*plane+1)*model.f+k
            rows[p],rows[q]=rows[q],rows[p]
    Z=pauli(model.n,z=(1<<(6*model.f))-1)
    return mul(Z,ce.perm(model.n,rows))


def support(family,j):
    return (0,2,4,2*j+1)if family=='primal'else(1,3,5,2*j)


def run():
    z1=Model(1,3)
    M1=role_duality(z1)
    recipes={}
    for family in('primal','dual'):
        for j in range(3):
            R,_=reflection(z1,3,support(family,j))
            for i,Ni in enumerate([z1.N,z1.T[0],z1.T[1]]):
                A=mul(Ni,R,Ni.adjoint())
                rec,compiled=ce.lower_child(A)
                need(rec['rank']==2,'every primal/dual old-plane conjugate is native2')
                same(A,compiled,'explicit primal/dual actual one-bit lowering')
                recipes[f'{family}_reflection{j}_conjugating_plane{i}']=rec
    checks=[]
    for f in(1,2,3):
        z=Model(f,3);M=role_duality(z)
        same(mul(M,M),z.I,'role duality literal involution')
        need(b.native_rank(M)==0,'role duality monomial')
        native=[z.N,z.T[0],z.T[1]]
        for i,Ni in enumerate(native):same(mul(M,Ni,M),Ni,'role duality actual Ni phase')
        for j in range(3):
            R,_=reflection(z,3,support('primal',j))
            S,srows=reflection(z,3,support('dual',j))
            same(S,ce.perm(z.n,srows),'dual reflection literally bare ADDRESS')
            same(mul(M,R,M),S,'primal-to-dual literal phase')
            for family,op in(('primal',R),('dual',S)):
                for i,Ni in enumerate(native):
                    A=mul(Ni,op,Ni.adjoint())
                    rec=recipes[f'{family}_reflection{j}_conjugating_plane{i}']
                    literal=mul(tensor_monomial(rec['left'],f),ce.fourier(z.n,range(2*f)),
                                tensor_monomial(rec['right'],f))
                    same(A,literal,'all18 tensor native recipes actual phase')
                    need(b.native_rank(A)==2*f,'primal/dual conjugate rank2f')
                    same(mul(A,A),z.I,'primal/dual conjugate involution')
        checks.append({'f':f,'role_duality_native_arity':0,'all3_native_commutations_phase_exact':True,
                       'all3_primal_dual_intertwiners_phase_exact':True,
                       'all18_native_recipes_phase_exact':True,'each_conjugate_arity':2*f})
    # Independent exact tensor-family algebra keeps the global N_f phase.
    a=Algebra(3);M=a.lift(M1)
    for Ni in[a.N,a.T[0],a.T[1]]:
        need(a.product(a.product(M,Ni),M)==Ni,'all-f duality tensor phase polynomial')
    return {'status':'PASS_ALL_F_DUAL_UNPAIRED_REFLECTIONS_AND_18_NATIVE_RECIPES',
            'scientific_pin':PIN,'producer_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'source_pins':[{'path':str(HERE/p),'sha256':hashlib.sha256((HERE/p).read_bytes()).hexdigest()}
                           for p in('native_model.py','orthogonal_source_normalizer.py','conjugated_reflection.py','lifted_algebra.py')],
            'primal_supports':[list(support('primal',j))for j in range(3)],
            'dual_supports':[list(support('dual',j))for j in range(3)],
            'all_f_bare_phase_proof':'For any even-weight support v, put c=sum_p v-sum_q v and d_v=sum_selected_p x-sum_selected_q x. On v.x=1, D^-1 P_(I+vvT) D has phase i^(2d_v-c)=-i^-c. For threep+oneq c=2, or onep+threeq c=-2, this phase is+1. Hence all6 reflections are bare ADDRESS for every f, bitwise. Each is orthogonal/involutive and normalizes the complete oldthreeplane product.',
            'role_duality':'M=product_i[Z_all_p_i Z_all_q_i SWAP(p_i,q_i)]. The exact typed identities are Z_all Hp_f Z_all=(-i)^f Hq_f and Z_all Hq_f Z_all=i^f Hp_f. Their scalars cancel inside each plane, giving M Ni M=Ni with its one global i retained. M^2=I. Swapping everyp/q exchanges primal anddual supports; Z_all_old commutes these even-weight orthogonal maps, so M R_j M=S_j with no residual scalar or Pauli.',
            'conjugate_duality':'Ad_Ni(S_j)=M Ad_Ni(R_j) M. Thus duals have the same native2f tariff. M can be composed into the existing left/right monomial adapters, not treated as an unpriced operation. The separately saved recipes directly lower all18 cases.',
            'one_bit_selected_native_recipes':recipes,
            'all_f_native_recipe_proof':'Each A_i,j family is a bitwise tensor of its actual one-bit operator: the global scalar of Ni cancels in conjugation. Tensor each saved monomial/native/monomial equality, including f times each monomial globalphase, to obtain one selected native2f child. The binary B block is a direct sum of f rank2 blocks. The f1/f2/f3 compiled recipe comparisons additionally check actual Gaussian phase.',
            'per_reflection_source_invoice':{'native_H2':2,'native_rank_mass':4,
                                             'new_reflection_ADDRESS_scans':2,'new_reflection_phase_scans':0,
                                             'delivery_ADD_scans':1,'source_Pj_ADDRESS_scans':1,
                                             'ordinary_helpers':0,'private_fields':0},
            'per_conjugate_unary_invoice':{'native_H2':1,'native_rank_mass':2,
                                          'monomial_adapters':2,'ADDRESS_scans_at_most':2,
                                          'Gaussian_quadratic_phase_scans_at_most':2,
                                          'ordinary_helpers':0,'private_fields':0},
            'role_duality_standalone_invoice':{'ADDRESS_scans':1,'Pauli_Z_scans':1,'native_queries':0},
            'actual_checks':checks,
            'source_binding':'Any of the6 reflections can be inserted with its inverse around delivery at a source full-old cut containing its3planes. The complete arbitrary-source/target matrix and literal inverse are those of UNPAIRED-SOURCE-WORD.json by the same full-old commutation identity; sourcePj and freshcoverage remain unchanged. This does not make reflection a free outgoing source code change.',
            'limits':['No five-query complete diag(E3,E3) factorization or improved tail is claimed here.',
                      'Scalar, conditional-routing, bank ADD, source-copy, address, phase, precision and tape work remain caller obligations.',
                      'The global duality restricted to old3planes need not commute a future whole-plane source swap; do not silently push it through a later sourcePj.'],
            'no_new_kappa':True}


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--write',action='store_true');args=p.parse_args()
    out=json.loads(json.dumps(run()));path=HERE/'DUAL-REFLECTIONS.json'
    if args.write:path.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    else:need(json.loads(path.read_text())==out,'saved dual reflections differ')
    print(out['status'])
