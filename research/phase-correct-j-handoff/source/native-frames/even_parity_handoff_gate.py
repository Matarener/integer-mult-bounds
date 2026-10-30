#!/usr/bin/env python3
"""Source-bound limitation on transporting the new J through an old full E.
Apache-2.0; substantial OpenAI Codex assistance. Coupled banks are outside.
"""
from pathlib import Path
import argparse
import hashlib
import json
from native_model import *
from even_parity_source import kernels,source_chart

HERE=Path(__file__).resolve().parent


def run():
    checks=[]
    for f in(1,2,3):
        z=Model(f,2);_,J=kernels(z);P=source_chart(z);E=mul(z.N,*z.T)
        F=mul(P.adjoint(),E,P);D=mul(E.adjoint(),F)
        same(mul(P,z.N,P.adjoint()),J,'actual source intertwiner phase')
        arities={'J_E':b.native_rank(mul(J,E)),'N_E':b.native_rank(mul(z.N,E)),
                 'N_F':b.native_rank(mul(z.N,F)),'frame_drift_D':b.native_rank(D),
                 'conjugated_M':b.native_rank(mul(E.adjoint(),P,E))}
        need(arities=={'J_E':6*f,'N_E':4*f,'N_F':6*f,'frame_drift_D':4*f,
                       'conjugated_M':4*f},'actual handoff geometry and drift ranks')
        checks.append({'f':f,'native_arities':arities,'universal_drift_lower_bound':2*f})
    return {'status':'PASS_SOURCE_BOUND_J_HANDOFF_GATE_AND_FRAME_DRIFT',
            'scientific_pin':PIN,'producer_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'source_pins':[{'path':str(HERE/p),'sha256':hashlib.sha256((HERE/p).read_bytes()).hexdigest()}
                           for p in('native_model.py','even_parity_source.py','EVEN-PARITY-SOURCE.json')],
            'free_warp_gate':'Let E befullnative on theambient includingJ andNj. Our actualJ hasarity(JE)=m f, whilearity(Nj E)=(m-2)f. If monomialP,Q obey P J Q^-1=Nj and E^-1 Q E ismonomial, then Nj E=P (JE)(E^-1 Q^-1 E), a monomialdoublecoset ofJE. Row and column monomial multiplication preserves everyrowsupportcount, contradiction:2^(mf) versus2^((m-2)f). This excludes arbitrary invertiblemonomialoperators, notonlyCliffords, wheneverthe statedfreewarp condition holds. CommutingoldsourceS withP=Q is a specialcase.',
            'orthogonal_centralizer_specialization':'At thebinarysymplecticlevel E=[[I,I],[0,I]]. A monomialCliffordP=[[A,0],[C,A^-T]] commutingE musthaveC=0 andA=A^-T, henceAorthogonal. OurJ hasGamma_J^2=0, whileNj hasnonzeroidempotentGamma_Nj. Orthogonalconjugationpreservesthese squares, so it cannotmapone to theother. This isonlya necessarybinarygate; thefreewarp rowsupportargument alreadykeepsfullactualoperators.',
            'quantitative_single_bank_Clifford_gate':'AssumePmonomialCliffordandJ=P Nj P^-1. Put F=P^-1 E P andD=E^-1 F. Monomialconjugation givesarity(Nj F)=arity(JE)=m f. SinceF=E D, B-ranksubadditivity givesm f<=arity(Nj E)+arity(D)=(m-2)f+arity(D), hencearity(D)>=2f. Anyunarynativeword repairingthatdriftmustpayatleast2f rankmass. TheexplicitM sourcechart actuallyhasdriftarity4f.',
            'outside_old_support':'IfNj is outside the transformedold supportof apartialE, a commuting monomialClifford mustpreserve itsactiveold Fourier subspace; it cannotexport an activeoldJ to that untouchedfresh plane. The full-E gate above is statedseparatelyanddoesnotpretendpartialEisfull.',
            'actual_checks':checks,
            'limits':['No lowerboundforcoupled-bankencoders, cross-cut cancellations oraccepting a genuinelychangedfutureframe isclaimed.',
                      'The onequeryJsource/fullarityresource remainsvalid; this gate says oldfreeS transportdoesnotcomealongwithit.',
                      'No helperowner, sourceCOPY, precision, tape or exponent obligation isdischarged.'],
            'no_new_kappa':True}


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--write',action='store_true');args=p.parse_args()
    out=json.loads(json.dumps(run()));path=HERE/'EVEN-PARITY-HANDOFF-GATE.json'
    if args.write:path.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    else:need(json.loads(path.read_text())==out,'saved J handoff gate differs')
    print(out['status'])
