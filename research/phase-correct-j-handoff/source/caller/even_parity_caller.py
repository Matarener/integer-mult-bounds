#!/usr/bin/env python3
"""Exact J response rederivation and the unresolved current-reader ordering.
Apache-2.0; substantial OpenAI Codex assistance. No supplier/gain claim.
"""
from pathlib import Path
import argparse,hashlib,json,sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
NATIVE=HERE.parent/'native-frames'
sys.path.insert(0,str(NATIVE))
from native_model import Model,ce,mul,same,need
from even_parity_source import kernels,source_chart

def local_handoff():
    # Independent current bank inputs (b1,U,V,finished_b,delta,future_c).
    # Coefficients are pairs a+bJ, with J^2=-1.
    I=[[((1,0)if i==j else(0,0))for j in range(6)]for i in range(6)]
    ops=[('a',0,2,1),('a',5,4,-1),('a',5,2,1),('a',4,1,1),
         ('j',1,0,1),('s',1,4,0),('s',4,2,0),('s',2,3,0)]
    def apply(rows,inverse=False):
        out=[[x for x in row]for row in rows]
        for typ,d,s,c in(reversed(ops)if inverse else ops):
            if typ=='a':
                c=-c if inverse else c
                out[d]=[(x[0]+c*y[0],x[1]+c*y[1])for x,y in zip(out[d],out[s])]
            elif typ=='s':out[d],out[s]=out[s],out[d]
            else:out[d]=[(b,-a)if inverse else(-b,a)for a,b in out[d]]
        return out
    M,Mi=apply(I),apply(I,True)
    expected=[[x for x in row]for row in I]
    expected[0][2]=(1,0)
    expected[1][4]=(1,0)
    expected[2]=I[3]
    expected[3]=[(0,1)if j==1 else(0,0)for j in range(6)]
    expected[4]=I[2]
    expected[5][4]=(-1,0);expected[5][2]=(1,0)
    need(M==expected,'alternative handoff all six arbitrary current columns')
    need(apply(M,True)==apply(Mi)==I,'alternative handoff literal inverse both orders')
    return {'independent_current_columns':6,'native_continuations':1,'native_arity_per_f':2,
            'literal_inverse_orders':2,'scalar_event_count':7,
            'source_continuation_bank':'bank1 holding U, not the old odd-stage V source',
            'matrix_over_Z[J]':M}

def run():
    checks=[]
    recipes=[]
    zsmall=Model(1,3);_,Jsmall=kernels(zsmall)
    for s in(1,2):
        Fsmall=zsmall.prefix(s-1);op=mul(Fsmall,Jsmall,Fsmall.adjoint())
        rec,compiled=ce.lower_child(op);same(op,compiled,'actual source-query native recipe phase')
        need(rec['rank']==2,'direct changed query uses one selected native2 child')
        recipes.append({'stages':'1'if s==1 else'>=2','one_coordinate_circuit':op.circuit,
                        'all_f_phase':'i^(1-f) times the complete one-coordinate operator tensored f times',
                        'selected_native_recipe':rec})
    for f in(1,2):
        z=Model(f,3);_,J=kernels(z);A=mul(z.N.adjoint(),J)
        rank=lambda op:ce.rank(x for x,y,p in op.tab[z.n:])
        same(mul(J,J),mul(z.N,z.N),'actual J square all-f phase fixture')
        for s in(1,2,3):
            Fpast=z.prefix(s-1);Fnew=z.prefix(s)
            Ks=mul(Fpast,J,Fpast.adjoint())
            B=mul(z.P[s-1],A)
            # Literal physical stage: Ks on source; target+=source;
            # S_s on source; fresh N_s on target.
            source=mul(Fnew.adjoint(),z.P[s-1],Ks,Fpast)
            cross=mul(Fnew.adjoint(),z.T[s-1],Ks,Fpast)
            same(source,B,'literal normalized source coefficient')
            same(cross,J,'literal normalized target cross')
            same(mul(B,J),mul(z.P[s-1],z.N),'exact B_s J=P_s N')
            same(mul(J,B.adjoint()),mul(z.N,z.P[s-1].adjoint()),'exact J B_s^-1=N P_s^-1')
            need(rank(Ks)==2*f,'actual changed query rank')
            need(rank(mul(Fnew,J))==2*(s+1)*f,'public F_s J full native endpoint')
            need(rank(mul(z.prefix(3),B.adjoint(),J,z.prefix(3).adjoint()))==(2 if s==1 else 6)*f,
                 'actual required reader rank including completed frame')
            checks.append({'f':f,'stage':s,'physical_query_rank':rank(Ks),
                           'public_endpoint_rank':rank(mul(Fnew,J)),
                           'source_code_rank':rank(B),
                           'required_reader_F_Binv_J_Finv_rank':rank(mul(z.prefix(3),B.adjoint(),J,z.prefix(3).adjoint())),
                           'reversed_cheap_reader_F_J_Binv_Finv_rank':rank(mul(z.prefix(3),J,B.adjoint(),z.prefix(3).adjoint()))})
        need(rank(mul(A,A))==0,'A squared has no native rank, not discarded as identity')
    return {'status':'PASS_EXACT_EVEN_PARITY_CALLER_RESPONSE_AND_READER_GAP',
            'scientific_pin':'20ecf2891d80b5acf18d980b2164fb44ea7faa90','checks':checks,
            'alternative_handoff_all_input_certificate':local_handoff(),
            'direct_query_recipes':recipes,
            'actual_stage':{'query':'K_s=F_(s-1) J F_(s-1)^-1, native2f',
                            'word':['source=K_s source','target+=source','source=S_s source','target=N_s target'],
                            'retarded_box':'[[B_s,0],[J,I]], B_s=P_s A, A=N0^-1 J',
                            'literal_inverse':'[[B_s^-1,0],[-J B_s^-1,I]] in the retarded chart; physically reverse the four saved stage operations'},
            'exact_identities':['J^2=-I','B_s J=P_s N0','J B_s^-1=N0 P_s^-1'],
            'all_f_proof':'The all-q handoff proof requires only generator K^2=-I and arbitrary invertible source codes. It transfers algebraically with K=J and P_s=B_s. Each physical K_s is a bitwise Clifford tensor with the mandatory J once-per-field phase. Its X-character address is identity plus a fixed translation, so conjugating by Fpast changes only affine/linear phases and preserves the rank2 polar form. The literal source and cross equations hold by Fnew=N_s Fpast and [S_s,Fpast]=0. Every source code B_s and every public reader must remain in the transferred formula.',
            'full_public_rank_proof':'On each p or q coordinate in old planes0,1, B(F_s J)=[[1,1],[1,0]], invertible; all remaining completed fresh directions have identity B. Hence F_s J has full native arity2(s+1)f for every s>=1. Its literal right endpoint gauge is not assumed free at a mixed cut.',
            'concrete_gap':'The current-reader inverse uses B_e^-1 J, not the cheap reversed product J B_e^-1. For every e>=2 the exact completed-F conjugate of the required product has nativearity6f, while the reversed product has2f. Uniform J substitution therefore does not reduce the displayed inverse: it introduces nonmonomial source B_e and a more expensive reader. A new encoder or joint inverse must change that equation, not swap its order.',
            'charge_threshold':'The transferred prefix retains H2=n*k+q+2, n=2q+2,k=2q+1 and full stock m*n,m=4q+4; its deficit is2q. A complete cleanup must have native mass c<2q for positive deficit, versus the old2q+8. At q3 a single unchanged required6-arity reader already exhausts the entire margin before all other readers/core are paid. This is a stop gate for that literal inverse, not a global cleanup lower bound.',
            'incoming_anchor_accounting':'The native resource JE fullarity assumes an already paid full E source. The transferred source is generally F_s times a mixed carrier, not isolated E*x. A retired helper retains at most its already credited full endpoint stock; JE preserving it adds no second stock credit. Crossresponse and rightgauges must be rederived before using that boundary.',
            'growing_scan_scope':'Fixed-in-f monomial-word gates do not rule out a fully charged O(f) or larger cleanup under a changed outer transfer. No source theorem expressly excluding all such scan growth is proved here; that transfer question remains unresolved.',
            'limits':['No full cheaper J cleanup or positive moment is constructed.','The reader rank is a specific unary requirement of the displayed current inverse, not an arbitrary joint-tail lower bound.','No input right gauge, paid full anchor or helper stock is omitted.','No BIT, owner, precision or finite-tape contract is supplied.'],
            'source_pins':[{'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}for p in
                           (NATIVE/'EVEN-PARITY-SOURCE.json',NATIVE/'even_parity_source.py',NATIVE/'native_model.py',HERE/'HANDOFF-FAMILY-PROOF.md')],
            'producer_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'no_new_kappa':True}

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--write',action='store_true');args=ap.parse_args()
    out=json.loads(json.dumps(run()));p=HERE/'EVEN-PARITY-CALLER.json'
    if args.write:p.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    else:need(json.loads(p.read_text())==out,'saved J caller check differs')
    print(out['status'])
if __name__=='__main__':main()
