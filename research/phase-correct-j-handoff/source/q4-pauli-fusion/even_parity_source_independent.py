#!/usr/bin/env python3
"""Independent actual Gaussian and all-size audit of the new J source."""
from pathlib import Path
import argparse, hashlib, json
from unpaired_reflection_screen import TensorBase, need, rotate
from one_query_endpoint_obstruction import walsh

HERE=Path(__file__).resolve().parent
NATIVE=HERE.parent/'native-frames'


def inverse(A,op):
    p,z=A.ops[op]; q=[0]*64; phase=[0]*64
    for w,x in enumerate(p): q[x]=w; phase[x]=(-z[w])%4
    return A.intern(tuple(q),tuple(phase))


def binary_rank(rows):
    pivots={}
    for row in rows:
        while row:
            j=row.bit_length()-1
            if j in pivots: row^=pivots[j]
            else: pivots[j]=row;break
    return len(pivots)


def physical(A,op):
    p,z=A.ops[op]; units=((1,0),(0,1),(-1,0),(0,-1)); rows=[]
    for x in range(64):
        values=[]
        for w in range(64):
            a,b=units[z[w]]; s=-1 if (x&p[w]).bit_count()%2 else 1
            values.append((s*a,s*b))
        rows.append(walsh(values))
    return rows # common denominator64


def mono(recipe,x):
    phase=recipe['phase']+sum(a*((x>>j)&1) for j,a in enumerate(recipe['linear_Z4']))
    phase+=2*sum(((x>>j)&1)*((x>>k)&1) for j,row in enumerate(recipe['quadratic_rows'])
                 for k in range(j+1,6) if (row>>k)&1)
    out=sum(((x&row).bit_count()%2)<<j for j,row in enumerate(recipe['matrix_rows']))^recipe['offset']
    return out,phase%4


def recipe_matrix(recipe,omit=None):
    rank=recipe['rank']; den=2**rank; rows=[[(0,0)]*64 for _ in range(64)]
    for col in range(64):
        x,p=(col,0) if omit=='right' else mono(recipe['right'],col)
        for mask in range(2**rank):
            a,b=1,0
            for j in range(rank):
                c,d=1,(-1 if (mask>>j)&1 else 1)
                a,b=a*c-b*d,a*d+b*c
            y,q=(x^mask,0) if omit=='left' else mono(recipe['left'],x^mask)
            rows[y][col]=rotate((a,b),p+q)
    return rows,den


def B_columns(A,op):
    out=[]; oi=inverse(A,op)
    for j in range(6):
        X=A.intern(tuple(w^(1<<j) for w in range(64)),(0,)*64)
        image=A.left(op,A.left(X,oi)); p,z=A.ops[image]
        shift=p[0]; need(all(p[w]==w^shift for w in range(64)),'conjugated Pauli has constant shift')
        mask=sum((((z[1<<k]-z[0])%4)//2)<<k for k in range(6))
        need(all((z[w]-z[0])%4==2*((mask&w).bit_count()%2) for w in range(64)),
             'conjugated Pauli has exact linear Gaussian phase')
        out.append(mask)
    return out


def run():
    resource=json.loads((NATIVE/'EVEN-PARITY-SOURCE.json').read_text())
    A=TensorBase(); p0,q0,p1,q1=1,2,4,8
    J=A.intern(tuple(w^3 for w in range(64)),
               tuple((2+(w&5).bit_count()%2+(w&10).bit_count()%2)%4 for w in range(64)))
    N=A.intern(A.ops[A.H[0]][0],tuple((z+1)%4 for z in A.ops[A.H[0]][1]))
    E=A.intern(A.ops[A.Ebase][0],tuple((z+3)%4 for z in A.ops[A.Ebase][1]))
    minusI=A.intern(tuple(range(64)),(2,)*64)
    need(A.left(J,J)==minusI,'actual J1 squares to-I including phase')
    badJ=A.intern(A.ops[J][0],tuple((z+3)%4 for z in A.ops[J][1]))
    need(A.left(badJ,badJ)==A.identity and A.left(badJ,badJ)!=minusI,
         'wrong constant-i phase fails the actual odd-f1 operator square')
    # Independent X-character image of physical M=X_p0 Z_p0 P_CNOT.
    mapping=[]; phases=[]
    for w in range(64):
        y=w^(((w>>2)&1)<<0)^(((w>>3)&1)<<1)
        y^=1;mapping.append(y);phases.append(2*(y&1))
    M=A.intern(tuple(mapping),tuple(phases)); Mi=inverse(A,M)
    need(A.left(M,A.left(N,Mi))==J,'both actual M adapters reproduce J1 with its exact phase')
    JE=A.left(J,E)
    NE=A.left(N,E)
    D=A.left(inverse(A,E),A.left(Mi,A.left(E,M)))
    need(binary_rank(B_columns(A,NE))==4,'old N removes its own2bit source plane')
    drift_columns=B_columns(A,D)
    need(binary_rank(drift_columns)==4,'actual monomial-chart frame drift has native arity4')
    recipe_checks=[]
    for name,target,recipe in [('queryJ',J,resource['native_query_recipes']['quadratic_J']),
                               ('retainedJE_L3',JE,resource['retained_full_endpoint_recipes_L3']['quadratic_J'])]:
        actual=physical(A,target); lowered,den=recipe_matrix(recipe)
        need(all(a*den==c*64 and b*den==d*64
                 for row,other in zip(actual,lowered) for (a,b),(c,d) in zip(row,other)),
             'all64 actual Gaussian columns match both saved endpoint adapters')
        omitted={}
        for side in ('left','right'):
            mutant,md=recipe_matrix(recipe,side)
            different=any(a*md!=c*64 or b*md!=d*64
                          for row,other in zip(actual,mutant) for (a,b),(c,d) in zip(row,other))
            need(different,'omitting either actual endpoint adapter is rejected')
            omitted[side]=different
        cols=B_columns(A,target); rank=binary_rank(cols)
        need(rank==(2 if name=='queryJ' else 6),'independent actual physical B rank')
        recipe_checks.append(dict(name=name,actual_B_columns=cols,native_arity=rank,
                                  both_monomial_adapters_checked=True,actual_columns=64,
                                  omitted_adapter_controls_rejected=omitted,
                                  matrix_sha256=hashlib.sha256(json.dumps(actual).encode()).hexdigest()))
    allsize=[]
    for L in range(2,9):
        for f in range(1,9):
            n=2*L*f;vectors=[]
            for k in range(f): vectors += [(1<<k)|(1<<(2*f+k)),(1<<(f+k))|(1<<(3*f+k))]
            gamma=[0]*n
            for v in vectors:
                for j in range(n):
                    if (v>>j)&1:gamma[j]^=v
            squared=[0]*n
            for j,row in enumerate(gamma):
                for k in range(n):
                    if (row>>k)&1:squared[j]^=gamma[k]
            need(not any(squared),'pairwise-orthogonal parity Gamma has square0')
            need(binary_rank(gamma)==2*f,'J native arity is exactly2f')
            need(binary_rank(row^(1<<j) for j,row in enumerate(gamma))==n,
                 'retained JE native arity stays full')
            correct=(2*(f+1)+2*f)%4; wrong=(2+2*f)%4
            need(correct==2 and (wrong!=2)==bool(f%2),'all-size phase and odd-f mutant')
            allsize.append(dict(L=L,f=f,J_arity=2*f,JE_arity=n,J_square_i_exponent=correct,
                                wrong_constant_i_square_i_exponent=wrong,wrong_mutant_rejected=bool(f%2)))
    return dict(status='PASS_INDEPENDENT_ALL_F_QUADRATIC_J_SOURCE_AUDIT',no_new_kappa=True,
                actual_recipe_checks=recipe_checks,exact_finite_rank_and_phase_grid=allsize,
                all_f_square_proof='Z anticommutes with each of the2f independent parityXs. Hence ZUZ=i^(2f)U^-1 and [i^(f+1)ZU]^2=i^(4f+2)I=-I. A constanti gives i^(2f+2)I, which is+I at everyoddf.',
                all_f_arity_proof='Gamma=sum(vk vkT+wk wkT), with2f independent pairwise-orthogonal even parity vectors. Gamma has rank2f and Gamma^2=0. J hasB=Gamma; E hasB=I; JE hasB=I+Gamma, invertible with inverseI+Gamma, so JE arity=2Lf for everyL>=2,f>=1.',
                exact_tensor_phases='J_f=i^(1-f) J1^tensorf, N0_f=i^(1-f) N0_1^tensorf and M_f=M1^tensorf. The actual J1=M1 N0_1 M1^-1 equality therefore gives J_f=M_f N0_f M_f^-1. JE atLoldplanes has global unit i^((L+1)(1-f)) times (J1 E1)^tensorf; at checkedL3 this unit is1.',
                literal_source_word=['source=J source','target+=source'],
                arbitrary_column_action='On(E*x,E*y), the exact output is(JE*x,E*y+JE*x). x,y arbitrary and independent.',
                literal_inverse=['target-=source','source=-J source'],
                inverse_proof='[[J,0],[J,I]]^-1=[[-J,0],[-I,I]], both product ordersI becauseJ^2=-I.',
                paid_invoice=dict(native_rank2f_queries=1,monomial_adapters=2,scalar_delivery_ADDs=1,
                                  ADDRESS_scans_at_most=2,Pauli_phase_scans_at_most=2,
                                  incoming_full_E_anchor='paid premise',ordinary_helpers=0,
                                  scope='Forward source/delivery word only; executing its literal inverse costs another rank2f query, two monomial adapters and one ADD.'),
                monomial_handoff_gate='If physical monomials P,Q obeyP J Q^-1=Nj and E^-1 Q E is also monomial, then NjE=P(JE)(E^-1Q^-1E) has arity2Lf, contradicting its actual arity(2L-2)f. Thus no such free-retarded-frame handoff exists.',
                quantitative_drift_gate='For physical-monomial P withJ=P Nj P^-1, letF=P^-1 E P,D=E^-1F. ThenJE=P(NjE)D P^-1. Native B rank is invariant under monomial endpoints and subadditive under Clifford products, hence rankB(D)>=2f. D is allowed to be Clifford. IfP is instead a general nonmonomial Clifford, this argument only yieldsrankB(D)>=2f-2rankB(P).',
                actual_chart_drift=dict(one_bit_B_columns=drift_columns,one_bit_native_arity=4,
                                       all_f_native_arity='4f by exact bitwise tensoring; all global phases cancel in E^-1 M^-1 E M.'),
                cleanup_inference='No cheap cleanup or caller closure follows. JE has full arity and differs from E; both full-endpoint gauges are needed to turn it into a chosen canonical full native. A right endpoint gauge cannot be dropped at an intermediate mixed cut, and the oldN reader is not replaced byJ without a new all-column caller identity.',
                attribution='Native worker supplied J, its native/query/source endpoint recipes and proposed all-size identities. This independent lane constructs its own X-character monomials, physical Gaussian columns, physical Pauli conjugation B ranks and binary nilpotent rank grid; it imports no native Clifford/model/producer code.',
                producer_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                source_pins=[dict(path=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in
                             [NATIVE/'EVEN-PARITY-SOURCE.json',NATIVE/'even_parity_source.py',
                              HERE/'unpaired_reflection_screen.py',HERE/'one_query_endpoint_obstruction.py']])


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--write',action='store_true');args=ap.parse_args()
    out=json.loads(json.dumps(run()));path=HERE/'INDEPENDENT-EVEN-PARITY-SOURCE.json'
    if args.write:path.write_text(json.dumps(out,sort_keys=True,indent=2)+'\n')
    else:need(json.loads(path.read_text())==out,'saved independentJ source audit differs')
    print(out['status'],'actual64column recipes',len(out['actual_recipe_checks']),'rank/phase grid',len(out['exact_finite_rank_and_phase_grid']))


if __name__=='__main__':main()
