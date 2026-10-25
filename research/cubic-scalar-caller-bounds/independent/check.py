#!/usr/bin/env python3
"""Separate rational-matrix audit; imports no candidate/source arithmetic."""
import argparse
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path

HISTORICAL_SHA='2050478b6fc2082775bc2eead709ee2f771c1fd2eca26a8cca4ad25eff142029'

def need(ok,why):
    if not ok:raise ValueError(why)
def eye(n):return [[Q(i==j) for j in range(n)] for i in range(n)]
def zero(n,m=None):return [[Q(0) for _ in range(n if m is None else m)] for _ in range(n)]
def add(A,B):return [[a+b for a,b in zip(x,y)] for x,y in zip(A,B)]
def neg(A):return [[-a for a in x] for x in A]
def sub(A,B):return add(A,neg(B))
def scale(A,c):return [[c*a for a in x] for x in A]
def mul(A,B):return [[sum(A[i][k]*B[k][j] for k in range(len(B))) for j in range(len(B[0]))] for i in range(len(A))]
def power(A,k):
    R=eye(len(A))
    for _ in range(k):R=mul(A,R)
    return R
def inv(A):
    n=len(A);M=[list(x)+y for x,y in zip(A,eye(n))]
    for j in range(n):
        q=next((q for q in range(j,n) if M[q][j]),None)
        need(q is not None,'nonsingular rational matrix')
        M[j],M[q]=M[q],M[j];v=M[j][j];M[j]=[x/v for x in M[j]]
        for i in range(n):
            if i!=j:
                v=M[i][j];M[i]=[x-v*y for x,y in zip(M[i],M[j])]
    return [r[n:] for r in M]
def kron(A,B):
    return [[A[i][j]*B[a][b] for j in range(len(A[0])) for b in range(len(B[0]))]
            for i in range(len(A)) for a in range(len(B))]
def diagblocks(blocks):
    n=sum(len(b) for b in blocks);M=zero(n);r=0
    for b in blocks:
        for i,row in enumerate(b):
            for j,v in enumerate(row):M[r+i][r+j]=v
        r+=len(b)
    return M
def trace(A):return sum(A[i][i] for i in range(len(A)))
def serial(x):
    if isinstance(x,Q):return str(x)
    if isinstance(x,dict):return {str(k):serial(v) for k,v in x.items()}
    if isinstance(x,(list,tuple)):return [serial(v) for v in x]
    return x
def equal(A,B,label,deleted=()):
    if label not in deleted:need(A==B,label)
def control(name,label,fn):
    try:fn(())
    except ValueError as exc:need(str(exc)==label,'unintended independent control failure')
    else:raise ValueError('independent mutant survived: '+name)
    fn((label,))
    return {'name':name,'rejected':label,'same_guard_deletion':'accept'}
def liftfull(poly):
    # C is the full 3-cycle, so 1,C,C² are linearly independent operators.
    C=[[Q(0),Q(0),Q(1)],[Q(1),Q(0),Q(0)],[Q(0),Q(1),Q(0)]]
    out=zero(3*len(poly));powers=[eye(3),C,power(C,2)]
    for i,row in enumerate(poly):
        for j,coefficient in enumerate(row):
            for k,c in enumerate(coefficient):
                for a in range(3):
                    for b in range(3):out[3*i+a][3*j+b]+=Q(c)*powers[k][a][b]
    return out

def audit(source):
    controls=[];fixtures=[]
    C=[[Q(0),Q(0),Q(1)],[Q(1),Q(0),Q(0)],[Q(0),Q(1),Q(0)]]
    for j,fixture in enumerate(source['normalization_fixtures']):
        W=eye(9);B=eye(3);P=eye(9);prefixes=[]
        for event in fixture['word']:
            if event['op']=='FREE':
                F=[[Q(v) for v in r] for r in event['matrix']]
                W=mul(kron(F,eye(3)),W);B=mul(F,B)
            else:
                R=zero(3);R[event['dst']][event['src']]=Q(event['sign'])
                e=event.get('power',1)
                direction=mul(mul(inv(B),R),B)
                P=mul(add(eye(9),kron(direction,sub(power(C,e),eye(3)))),P)
                W=mul(add(eye(9),kron(R,power(C,e))),W)
                B=mul(add(eye(3),R),B)
            normalized=mul(kron(inv(B),eye(3)),W)
            equal(P,normalized,'chronological augmentation identity')
            prefixes.append(P)
        expected=liftfull(fixture['normalized_full_ring_matrix'])
        equal(P,expected,'all full-ring normalization columns')
        controls.append(control('omit_augmentation_'+str(j),'all full-ring normalization columns',
            lambda deleted,W=W,expected=expected:equal(W,expected,'all full-ring normalization columns',deleted)))
        fixtures.append({'all_prefixes':prefixes,'final_full_regular_operator':P,'augmentation':B})

    def product(matrices):
        result=eye(9)
        for matrix in matrices:result=mul(matrix,result)
        return result
    excluded=[liftfull(T) for T in source['controls']['excluded_N_dependent_four_factor_word']]
    for T in excluded:equal(power(sub(T,eye(9)),2),zero(9),'excluded factor square-zero perturbation')
    target=kron(eye(3),C)
    excluded_product=product(excluded)
    equal(excluded_product,target,'full-ring excluded-word endpoint')
    inverse_word=product([sub(scale(eye(9),2),T) for T in reversed(excluded)])
    equal(mul(inverse_word,excluded_product),eye(9),'excluded literal inverse')
    controls.append(control('omit_excluded_factor','full-ring excluded-word endpoint',
        lambda d:equal(product(excluded[1:]),target,'full-ring excluded-word endpoint',d)))
    false_primitive=add(add(eye(9),scale(target,2)),power(target,2))
    controls.append(control('discard_augmentation_component','full-ring excluded-word endpoint',
        lambda d:equal(false_primitive,target,'full-ring excluded-word endpoint',d)))

    # This ordinary 2x2 rational representation is used ONLY for the necessary
    # primitive specialization. It is not confused with the full 3-cycle above.
    J=[[Q(0),Q(-1)],[Q(1),Q(-1)]]
    equal(add(add(power(J,2),J),eye(2)),zero(2),'primitive relation')
    t=sub(J,eye(2));t2=sub(power(J,2),eye(2))
    A=[[Q(0),Q(1),Q(0)],[Q(0),Q(0),Q(0)],[Q(0),Q(0),Q(0)]]
    B=[[Q(0),Q(0),Q(0)],[Q(-1),Q(0),Q(0)],[Q(0),Q(0),Q(0)]]
    C0=[[Q(0),Q(0),Q(0)],[Q(0),Q(0),Q(1)],[Q(0),Q(0),Q(0)]]
    D=[[Q(0),Q(0),Q(0)],[Q(0),Q(0),Q(0)],[Q(0),Q(1),Q(0)]]
    for M in (A,B,C0,D):equal(mul(M,M),zero(3),'square-zero layer')
    I=eye(3);I6=eye(6)
    left=mul(add(I6,kron(D,t2)),add(I6,kron(C0,t)))
    right=mul(kron(I,J),mul(sub(I6,kron(A,t)),sub(I6,kron(B,t2))))
    G=add(add(scale(A,2),B),scale(mul(A,B),3))
    q0=add(sub(sub(I,C0),scale(D,2)),scale(mul(D,C0),3))
    q1=sub(C0,D)
    equal(left,add(kron(q0,eye(2)),kron(q1,J)),'left pair coefficients')
    equal(right,add(kron(sub(A,B),eye(2)),kron(add(I,G),J)),'right inverse coefficients')
    e=sub(q0,sub(A,B));f=sub(q1,add(I,G))
    lhs=sub(mul(D,G),add(A,mul(A,B)))
    rhs=scale(sub(add(e,f),scale(mul(D,f),3)),Q(1,3))
    equal(lhs,rhs,'noncentral pure-layer defect identity')
    controls.append(control('delete_target_defect','noncentral pure-layer defect identity',
        lambda d:equal(lhs,zero(3),'noncentral pure-layer defect identity',d)))
    controls.append(control('wrong_cross_sign','left pair coefficients',
        lambda d:equal(left,add(kron(q0,eye(2)),kron(add(C0,D),J)),'left pair coefficients',d)))
    pair=mul(add(I,B),add(I,A));literal=mul(sub(I,A),sub(I,B))
    equal(mul(pair,literal),I,'literal two-layer inverse')
    need(trace(pair)==trace(literal),'reciprocal pair trace')
    controls.append(control('reverse_inverse_order','literal two-layer inverse',
        lambda d:equal(mul(pair,mul(sub(I,B),sub(I,A))),I,'literal two-layer inverse',d)))

    projections=[]
    for label,M,sign in [('upper',[[-1,1,2,0],[0,-1,0,3],[0,0,0,0],[0,0,0,0]],1),
                         ('lower',[[0,0,0,0],[0,0,0,0],[1,0,1,0],[0,2,1,1]],-1)]:
        M=[[Q(x) for x in r] for r in M];base=add(eye(4),scale(M,sign));P=sub(eye(4),power(base,4))
        def projection(QP,deleted=(),M=M):
            ok=mul(QP,QP)==QP and mul(QP,M)==M and mul(M,QP)==M
            equal(ok,True,'spectral projector equations',deleted)
        projection(P)
        wrong=sub(eye(4),base)
        controls.append(control('truncate_'+label,'spectral projector equations',lambda d,wrong=wrong,projection=projection:projection(wrong,d)))
        projections.append({'kind':label,'matrix':M,'projector':P})

    # Reconstruct chronological interaction with ordinary 10x10 rational blocks.
    n,k=3,5;U=zero(n,k);V=zero(k,n)
    for q in range(k):
        j=q%n;U[j][q]=1;U[(j+1)%n][q]=q+1;V[q][(j+2)%n]=(-1)**q
    interaction=mul(V,U);L=[[interaction[i][j] if i>j else Q(0) for j in range(k)] for i in range(k)]
    upper=[[interaction[i][j] if i<j else Q(0) for j in range(k)] for i in range(k)]
    alphas=[t if q%2==0 else t2 for q in range(k)]
    Ginv=sub(diagblocks([inv(a) for a in alphas]),kron(L,eye(2)));Gbig=inv(Ginv)
    Ub=kron(U,eye(2));Vb=kron(V,eye(2));W=eye(2*n)
    for q in range(k):
        direction=[[U[i][q]*V[q][j] for j in range(n)] for i in range(n)]
        W=mul(add(eye(2*n),kron(direction,alphas[q])),W)
    equal(W,add(eye(2*n),mul(mul(Ub,Gbig),Vb)),'interaction resolvent')
    Cbig=sub(kron(interaction,eye(2)),mul(kron(eye(k),t),Ginv))
    Ac=[r[:] for r in upper];Hc=[r[:] for r in L]
    for q in range(k):
        if q%2==0:Ac[q][q]=-1
        else:Hc[q][q]=1
    equal(Cbig,add(kron(Ac,eye(2)),kron(Hc,J)),'triangular split')
    defect=sub(W,kron(eye(n),J));actual=mul(mul(Ub,Gbig),Cbig)
    equal(actual,mul(defect,Ub),'interaction target defect')
    controls.append(control('erase_interaction_defect','interaction target defect',
        lambda d:equal(actual,zero(2*n,2*k),'interaction target defect',d)))
    need(len(controls)==12,'independent control coverage')
    return {'status':'PASS_INDEPENDENT_RATIONAL_MATRIX_AUDIT','source_sha256':HISTORICAL_SHA,
        'full_regular_basis_order':[[r,g] for r in range(3) for g in range(3)],
        'normalization_fixtures':fixtures,'primitive_generator':J,
        'excluded_word':{'literal_factors':excluded,'full_operator':excluded_product,'literal_inverse':inverse_word},
        'primitive_only_false_target_full_operator':false_primitive,
        'pure_layer':{'left':left,'right':right,'e':e,'f':f,'lhs':lhs,'rhs':rhs},
        'projectors':projections,'interaction':{'U':U,'V':V,'G_inverse':Ginv,'G':Gbig,
            'C':Cbig,'A':Ac,'H':Hc,'W':W,'target_defect':defect,'full_defect_identity':actual},
        'two_layer':{'pair':pair,'literal_inverse':literal},'controls':controls,
        'scope':'independent finite algebra checks and sensitivity; all-word proof reviewed separately'}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--historical-receipt',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args()
    raw=a.historical_receipt.read_bytes();need(hashlib.sha256(raw).hexdigest()==HISTORICAL_SHA,'historical input authentication')
    need(a.output.is_absolute() and not a.output.exists() and not a.output.is_symlink(),'new absolute output')
    for root in (Path(__file__).resolve().parent,a.historical_receipt.resolve().parent):
        need(not a.output.resolve().is_relative_to(root),'external independent output')
    data=serial(audit(json.loads(raw)))
    with a.output.open('x') as out:out.write(json.dumps(data,sort_keys=True,indent=2)+'\n')
    print('PASS independent full-ring and primitive rational matrices; 12 defects and deletions')
if __name__=='__main__':main()
