#!/usr/bin/env python3
"""Paid even-parity native responses preserve an already-full source endpoint.
Apache-2.0; substantial OpenAI Codex assistance. Changed kernel, no free anchor.
"""
from pathlib import Path
import argparse
import hashlib
import json
from native_model import *
from conjugated_reflection import tensor_monomial
from lifted_algebra import Algebra

HERE=Path(__file__).resolve().parent


def parity_query(z,chunks):
    out=z.I
    for k in range(z.f):
        q=sum(1<<(j*z.f+k)for j in chunks)
        out=mul(ce.cgate(z.n,q),out)
    return out


def kernels(z):
    C=parity_query(z,(0,1))
    U=mul(parity_query(z,(0,2)),parity_query(z,(1,3)))
    Z=pauli(z.n,z=(1<<(2*z.f))-1)
    J=mul(phase(z.n,z.f+1),Z,U)
    return C,J


def source_chart(z):
    # A is bitwise CNOT p0->p1 and q0->q1. M=X_p0 Z_p0 P_A.
    rows=[1<<j for j in range(z.n)]
    for k in range(z.f):
        rows[2*z.f+k]^=1<<k
        rows[3*z.f+k]^=1<<(z.f+k)
    p=(1<<z.f)-1
    return mul(pauli(z.n,x=p,z=p),ce.perm(z.n,rows))


def run():
    z1=Model(1,2)
    C1,J1=kernels(z1)
    E1=mul(z1.N,*z1.T)
    recipes={}
    endpoint_recipes={}
    for name,K in(('even_C',C1),('quadratic_J',J1)):
        rec,compiled=ce.lower_child(K);same(K,compiled,'actual one-bit response lowering')
        recipes[name]=rec
        wr,wc=ce.lower_child(mul(K,E1));same(mul(K,E1),wc,'actual one-bit full endpoint lowering')
        need(wr['rank']==z1.n,'source endpoint fully native')
        endpoint_recipes[name]=wr
    checks=[]
    phase_mutants=[]
    for f in(1,2,3):
        z=Model(f,2);C,J=kernels(z);E=mul(z.N,*z.T)
        chart=source_chart(z)
        need(b.native_rank(chart)==0,'explicit source chart is monomial')
        same(mul(chart,z.N,chart.adjoint()),J,'actual old-N to source-preserving-J chart phase')
        Xtag=ce.xgate(z.n,(1<<(2*f))-1)
        same(mul(C,C),Xtag,'evenC square is a literal ADDRESS translation')
        same(mul(J,J),phase(z.n,2),'quadraticJ square exact minus identity allf')
        bad=mul(phase(z.n,-f),J)
        same(mul(bad,bad),phase(z.n,2*(f+1)),'wrong constant-i mutant has its predicted phase')
        if f%2:
            need(b.sparse_column(mul(bad,bad))!=b.sparse_column(phase(z.n,2)),
                 'constant-i mutant is rejected on oddf')
        phase_mutants.append({'f':f,'wrong_constant_i_square_i_exponent':(2*(f+1))%4,
                              'wrong_constant_i_rejected':bool(f%2)})
        Zall=pauli(z.n,z=(1<<z.n)-1)
        same(mul(C,Zall),mul(Zall,C),'evenC commutes physicalZall')
        same(mul(J,Zall),mul(Zall,J),'quadraticJ commutes physicalZall')
        for name,K,exponent,arity in(('even_C',C,0,1),('quadratic_J',J,1,2)):
            rec=recipes[name]
            literal=mul(phase(z.n,exponent*(1-f)),tensor_monomial(rec['left'],f),
                        ce.fourier(z.n,range(arity*f)),tensor_monomial(rec['right'],f))
            same(K,literal,'native response tensor recipe actual phase')
            W=mul(K,E)
            need(b.native_rank(K)==arity*f and b.native_rank(W)==z.n,'query and retainedfullsource arities')
            phase_checked=False
            if f<=2:
                wr=endpoint_recipes[name]
                lowered=mul(phase(z.n,(3+exponent)*(1-f)),tensor_monomial(wr['left'],f),
                            ce.fourier(z.n),tensor_monomial(wr['right'],f))
                same(W,lowered,'retained full endpoint literal tensor gauge phase')
                phase_checked=True
            checks.append({'f':f,'kernel':name,'query_native_arity':arity*f,
                           'retained_source_native_arity':z.n,
                           'query_recipe_actual_phase':True,
                           'full_endpoint_recipe_actual_phase_checked':phase_checked})

    # Independently preserve both original fields and literal inverse in
    # the full tensor-family algebra, with actual global f phases retained.
    a=Algebra(2);E=a.product(a.product(a.N,a.T[0]),a.T[1])
    source_records=[]
    for name,K1,exponent in(('even_C',C1,0),('quadratic_J',J1,1)):
        K=a.lift(K1,exponent=exponent);Ki=a.adjoint(K)
        query=a.diagonal(2,0,K)
        add=a.mat_identity(2);add[1][0]=a.one
        sub=a.mat_identity(2);sub[1][0]=a.scale(a.one,-1)
        W=a.mat_product(add,query)
        Wi=a.mat_product(a.diagonal(2,0,Ki),sub)
        entrance=[[E,{}],[{},E]]
        expected=[[a.product(K,E),{}],[a.product(K,E),E]]
        need(a.mat_product(W,entrance)==expected,'all original source and dirty target columns')
        need(a.mat_product(W,Wi)==a.mat_product(Wi,W)==a.mat_identity(2),'literal source word inverse bothorders')
        source_records.append({'kernel':name,'all_f_input_columns':2,'literal_inverse_orders':2})
    return {'status':'PASS_ALL_F_EVEN_PARITY_AND_QUADRATIC_FULL_SOURCE_RESPONSES',
            'scientific_pin':PIN,'producer_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'source_pins':[{'path':str(HERE/p),'sha256':hashlib.sha256((HERE/p).read_bytes()).hexdigest()}
                           for p in('native_model.py','conjugated_reflection.py','lifted_algebra.py')],
            'incoming_anchor':'The source already equals E*x for arbitrary x, E=product_i N_i fullnative on L>=2 oldplanes. This fullnative anchor is an incoming paid caller premise; no free preparation is claimed. The checked fixture has L=3.',
            'rankf_kernel':'C_even,f=product_k C_(p0k+q0k), with C_q=((1+i)I+(1-i)X_q)/2. Each parity vector has evenweight, and they are independent. Thus nativearityf. Its exact square is X_all_commonp+commonq, a paid ADDRESS translation, not a discarded residual.',
            'quadratic_kernel':'Let v_k=p0k+p1k,w_k=q0k+q1k, U=product_k C_v_k C_w_k, Z=Z_all_p0 Z_all_q0, and J_f=i^(f+1) Z U. For each anticommtingparity, Z C_v Z=i C_v^-1; hence ZUZ=i^(2f) U^-1 and J_f^2=i^(2f+2) i^(2f)=-I for everyf. The f-dependentGaussianunit is mandatory. This has exact nativearity2f and is a changed literalJ response, nottheold N0 response.',
            'explicit_old_native_source_chart':'Let A be bitwise CNOT p0->p1 and q0->q1, and M_f=X_all_p0 Z_all_p0 P_A. Then J_f=M_f N0 M_f^-1 exactly. ADDRESSconjugation sends theoldnativeC directions to v,w; Z_p0 reverses the v parities with the mandatory i^f factor, and X_p0 supplies the remaining (-1)^f. Thus the phase is i^(f+1). M has oneaffineADDRESS plus onePauliZ scan; applying M^-1,N0,M exposes the sameJ nativequery with bothmonomialadapters paid. This is a source-frame change relative to the retainedincomingE, not a new abstract quadraticalgebra.',
            'full_source_rank_proof':'The fullold E has binary symplecticA=D=I,B=I,C=0. A C_even query has B=Gamma=sum qk qkT. All selectedparities in each kernel are pairwiseorthogonal, so Gamma^2=0 and I+Gamma is invertible, inverseI+Gamma. A PauliZ leftfactor doesnotchangeB. Hence both C_even E andJ E have fullnativearity2Lf, for everyL>=2,f>=1. This is a rank/admission statement, not equality of the endpoint withE.',
            'all_f_phase_and_recipe_proof':'C_even,f=C_even,1^tensor f. J_f=i^(1-f)J_1^tensor f. E_f=i^(L*(1-f))E_1^tensor f. Therefore each source endpoint K_f E_f=i^((L+exponentK)*(1-f)) (K_1 E_1)^tensor f. Tensor the saved actualonebitnativeandmonomialrecipes, with the displayedleftglobalunit. This proves full actual phases and endpoint adapters for everyf without f1 tableau extrapolation.',
            'native_query_recipes':recipes,'retained_full_endpoint_recipes_L3':endpoint_recipes,
            'chronological_word':['source=K source','target+=source'],
            'complete_actual_matrix':'On entrance(E*x,E*y), output(K E*x,E*y+K E*x); bothoriginalfields arbitrary. Source remains an isolatedfullnativeoperatorK E on its ownx. No helperor cleanfield is used.',
            'literal_inverse':['target-=source','source=K^-1 source'],
            'rankf_query_invoice':{'H1':1,'native_rank_mass':1,'delivery_ADD_scans':1,
                                   'native_monomial_adapters':2,'ADDRESS_scans_at_most':2,
                                   'Gaussian_quadratic_phase_scans_at_most':2,
                                   'ordinary_helpers':0,'private_fields':0},
            'quadratic_query_invoice':{'H2':1,'native_rank_mass':2,'delivery_ADD_scans':1,
                                       'native_monomial_adapters':2,'ADDRESS_scans_at_most':2,
                                       'Gaussian_quadratic_phase_scans_at_most':2,
                                       'ordinary_helpers':0,'private_fields':0},
            'endpoint_gauge_obligation':'The fullendpointK E=L C_full R has explicitmonomialleft/rightgauges, bothpaidifused. It isnotexactE. A completecaller whoseindependentoutputsareK_i E may compose the appropriateinputrightgaugesandoutputleftgauges after proving allcolumns. The rightgaugecannotbe dropped at an intermediate mixedcut orassumedto preserve a desiredN response. A dirtyhelper owner mustpriceits actual entrance/terminalresidual; fullarityaloneisnotanownercontract.',
            'even_only_limitation':'Every evenparityC_q commutes physicalZ_all andphysicalX_all. BinaryorthogonalA fixes1; itscorrectedtagz hasz.dot1=0 because itsphaseat1 equals1. Thus R_A=P_A Z_z also commutesbothglobalPaulis. Anybankword usingonlythoseevenqueriesandorthogonalcorrectedcontrollerscommutesdiag(Z_all), whereas afullnativeClifford with invertibleB cannotfix nonzeroZ_all. An odd/nativeanchor or a controlleroutside thatrestrictedcommutant is necessary. GeneralADDRESS adapters outside theorthogonalgroup are notcoveredbythisno-even-onlyclaim. IncomingE isexactlysuch analreadypaidanchor.',
            'actual_checks':checks,'all_f_two_column_checks':source_records,
            'wrong_constant_i_phase_controls':phase_mutants,
            'limits':['No currentpublicreaderN isreplacedbyJ orC_even withouta newall-columnidentity.',
                      'No stockor exponentgain isclaimed: thepaid incominganchor, sourceCOPY/readscans, endpointgauges, ownerbinding, precisionandphysicaltapecontract remainrequired.',
                      'The fullsourceendpointgauge fixturescoverL3; the writtenrankandphaseidentitiesholdallL>=2.'],
            'no_new_kappa':True}


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--write',action='store_true');args=p.parse_args()
    out=json.loads(json.dumps(run()));path=HERE/'EVEN-PARITY-SOURCE.json'
    if args.write:path.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    else:need(json.loads(path.read_text())==out,'saved even parity source differs')
    print(out['status'])
