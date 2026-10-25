#!/usr/bin/env python3
"""Exact factory endpoints of the proposed diagonal J handoff recurrence.
Apache-2.0; substantial OpenAI Codex assistance. Not a complete J caller.
"""
from pathlib import Path
import argparse
import hashlib
import json
from native_model import *
from even_parity_source import kernels

HERE=Path(__file__).resolve().parent


def run():
    checks=[]
    for q in range(2,9):
        for f in(1,2):
            z=Model(f,2*q+1);_,J=kernels(z);A=mul(z.N.adjoint(),J)
            De,Dv=z.I,z.I
            for r in range(2,q+1):
                De=mul(z.P[2*r-1],A,De)
                Dv=mul(z.P[2*r],z.N,Dv)
            Dv=mul(phase(z.n,2*(q-2)),Dv)
            Du=mul(De,z.P[2],z.N)
            F=z.prefix(2*q+1);E=mul(z.N,F)
            arities={'Ninv_J':b.native_rank(A),'D_even':b.native_rank(De),
                     'D_u_with_base_P3N':b.native_rank(Du),'D_v':b.native_rank(Dv),
                     'F_D_u':b.native_rank(mul(F,Du)),'F_D_v':b.native_rank(mul(F,Dv)),
                     'u_correction_to_E':b.native_rank(mul(E,Du.adjoint(),F.adjoint())),
                     'v_correction_to_E':b.native_rank(mul(E,Dv.adjoint(),F.adjoint()))}
            need(arities=={'Ninv_J':4*f,'D_even':4*f,'D_u_with_base_P3N':6*f,
                            'D_v':2*(q-1)*f,'F_D_u':4*q*f,'F_D_v':(2*q+4)*f,
                            'u_correction_to_E':8*f,'v_correction_to_E':2*q*f},
                 'exact proposed diagonal recurrence native arities')
            n,k,m=2*q+2,2*q+1,4*q+4
            prefix=2*(n*k+q+2)
            helper_threshold=prefix-(n-2)*m
            endpoint_total=6*q+4
            need(helper_threshold==6*q+8 and endpoint_total-helper_threshold==-4,
                 'complete rank-mass threshold includes publicstock and basefactor')
            checks.append({'q':q,'f':f,'native_arities':arities,
                           'prefix_rank_mass_per_f':prefix,'full_public_stock_per_f':(n-2)*m,
                           'helper_arity_needed_for_positive_D_per_f':f'>{helper_threshold}',
                           'exposed_factory_endpoint_arity_per_f':endpoint_total,
                           'factory_endpoint_shortfall_before_core_readers_per_f':4})
    return {'status':'PASS_ALL_Q_DIAGONAL_J_FACTORY_ENDPOINT_GATE',
            'scientific_pin':PIN,'producer_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'source_pins':[{'path':str(HERE/p),'sha256':hashlib.sha256((HERE/p).read_bytes()).hexdigest()}
                           for p in('native_model.py','even_parity_source.py','EVEN-PARITY-SOURCE.json')],
            'conditional_caller_interface':'Assume the changed handoff u_next=B_e u,v_next=-B_o J v plus its stated affinepublicreaders is physicallybound. B_s=P_s N0^-1 J. The transferredbasehasu1=B3 J*(core_row2)=P3 N0*(core_row2), v1=core_row1. This file proves the resulting homogeneousfactories, not the entirepublicreader/callerword.',
            'factories':'D_even=product descendingr(q..2)[P_(2r) A], A=N0^-1 J; D_u=D_even P3 N0; D_v=(-1)^(q-2) product descendingr(q..2)[P_(2r+1) N0]. FullprefixF=productfresh1..2q+1.',
            'all_q_star_proof':'On each p orq half, A hasB block e0 e1T+e1 e0T+e1 e1T. Moving the whole-planepermutations totheright makes D_even a star X-chirp with anchorplane1 andleafsum on evenfresh4,6,..,2q, plus (q-1 mod2) e1e1T. Eachhalfrank is2 forq>=2, soD_evenarity4f. Addingthisstar to the fullfreshF block gives aninvertiblefreshmatrix: itsanchor Schurcomplementis1+(q-1)+(q-1)=1. Thus F D_even isfullonallfresh andstillmissescommon0. P3 N=N3 P3; fresh3 isdisjointfromthe star, so thebasefactorcancelsfresh3 and arity(FD_u)=4q f. D_v hasdistinctodd-freshnativeplanes5,7,..,2q+1, soarity(FD_v)=(2q+4)f.',
            'specified_direct_correction_arities':'For targetE=N0 F, E D_u^-1 F^-1 hasarity8f and E D_v^-1 F^-1 hasarity2qf. Inbinaryform Ad_E fixes these shear/permutationfactories; actualphasecommutators arePaulifactorsanddonotchangearity. u has disjointstar4f,fresh3 2f,andcommon0 2f; v hasq-1odd-freshplanespluscommon0. Thus thisseparatefactory-firstcompletionalreadyneedsnative mass2q+8, exceedingprefixD2q beforecore/publicreaderwork. No joint-tail lowerboundis claimed.',
            'partial_endpoint_gate':'If thefactorieswere exposed as independentownerendpoints, theircombinedarity is(6q+4)f. The stipulatedprefixmass minus n-2 fullpublicstock is(6q+8)f, so thatpartialretirement missesby4f evenbefore anycostforremovingcoreorpublicreaders. A differentfactorization/ownercontract may differ; no rawcoupledH rankiscredited.',
            'checks':checks,
            'evidence_domain':'Written all-q star/Schur proof with actual all-f tensor families; independent binaryClifford rankchecks q2..8,f1/f2. MandatoryJ andN globalphases are retained in theconstructedoperators; this is anarity/costgate, not a literalcompletecalleridentity or a formal-kernel proof.',
            'limits':['The caller lane owns the proposed affinepublicreader reencoding and any completephysical trace.',
                      'A genuinely jointcore/factory/readerword orcoupled-ownerboundary is notexcluded.',
                      'No positive moment, all-size supplier, ownerallocation, precision or tape claim ismade.'],
            'no_new_kappa':True}


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--write',action='store_true');args=p.parse_args()
    out=json.loads(json.dumps(run()));path=HERE/'DIAGONAL-J-FACTORY-GATE.json'
    if args.write:path.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    else:need(json.loads(path.read_text())==out,'saved diagonalJ factory gate differs')
    print(out['status'])
