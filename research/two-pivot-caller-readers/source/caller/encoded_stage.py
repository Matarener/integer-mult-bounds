#!/usr/bin/env python3
"""One genuine partial-plane encoded stage in the all-pair caller.

The actual native-zero bridge mixes both dirty carrier banks. Its retarded
operator is N^-1 R N, not the physical ADDRESS R. No terminal tariff is
asserted. Exact tensor/phase-polynomial algebra covers every f>=1.
Apache-2.0; substantial OpenAI Codex assistance.
"""
from pathlib import Path
from fractions import Fraction
import argparse,hashlib,json,sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
NATIVE=HERE.parent/'native-frames'
sys.path.insert(0,str(NATIVE))
import lifted_algebra as L
from native_model import ce,mul,need
from nested_prefix import skeleton
from nested_family import retraction


def build(q=3,encode=True,wrong_chart=False,encoder='triangular'):
    need(q>=3,'one nonfinal handoff is required')
    a=L.Algebra(2*q+1);n=2*q+2
    one,N=a.one,a.N;M=a.mat_identity(n);Mi=a.mat_identity(n);events=[];s=0
    def app(B,Bi,event):
        nonlocal M,Mi
        M=a.mat_product(B,M);Mi=a.mat_product(Mi,Bi);events.append(event)
    def add(d,src,c,label):
        if not c:return
        B=a.mat_identity(n);Bi=a.mat_identity(n)
        B[d][src]=a.add(B[d][src],a.scale(c,1));Bi[d][src]=a.add(Bi[d][src],a.scale(c,-1))
        app(B,Bi,{'op':'ADD','dst':d,'src':src,'label':label})
    def scalar(d,src,c,label):add(d,src,a.scale(one,c),label)
    def unary(bank,op,label):app(a.diagonal(n,bank,op),a.diagonal(n,bank,a.adjoint(op)),{'op':'UNARY','bank':bank,'label':label})
    def swap(i,j,label):
        B=a.mat_identity(n);B[i],B[j]=B[j],B[i];app(B,B,{'op':'SWAP','banks':[i,j],'label':label})
    def ec(z):return a.add(a.scale(one,z[0]),a.scale(N,z[1]))
    # Partial-plane source normalizer, bitwise in every tensor coordinate.
    # Typed D^-1 P_A D phases cancel for this 3p/1q support.
    v=sum(1<<j for j in(0,1,2,4));rows=[(1<<j)^(v if v>>j&1 else 0)for j in range(a.m)]
    physicalR=ce.perm(a.m,rows);R=a.lift(physicalR)
    old=a.product(a.product(N,a.T[0]),a.T[1])
    need(a.product(R,R)==one,'actual reflection involution every f')
    need(a.product(R,old)==a.product(old,R),'actual full-three-plane commutation every f')
    logicalR=R if wrong_chart else a.product(a.product(a.adjoint(N),R),N)
    retarded_actual=mul(a.model.prefix(5).adjoint(),physicalR,a.model.prefix(5))
    if not wrong_chart:need(a.lift(retarded_actual)==logicalR,'physical cut5 to literal retarded source chart')
    for r in range(2,q+1):scalar(2*r+1,3,1,'raw c-basis')
    _,ops=skeleton(q,[1]+[0]*(q-1))
    for typ,d,src,z in ops:
        if typ=='a':add(d,src,ec(z),'initial nested bridge')
        elif typ=='s':swap(d,src,'initial nested bank permutation')
        else:
            s+=1;u=retraction(q,s)
            if s==4:
                for j,(aa,bb)in enumerate(u):
                    if j!=src:scalar(j,src,-aa,'query4 scalar entrance')
                break
            for j,z in enumerate(u):
                if j!=src:add(j,src,a.scale(ec(z),-1),f'query{s} retraction entrance')
            add(d,src,N,f'query{s} target cross')
            P=a.P[s-1];P=a.product(N,P)if s==3 else P
            unary(src,P,f'query{s} retained source code')
            for j,z in enumerate(u):
                if j!=src:add(j,src,ec(z),f'query{s} retraction exit')
    for r in range(3,q+1):scalar(0,2*r,-1,'restore raw a')
    scalar(3,0,-1,'held source subtract raw a')
    for r in range(2,q+1):scalar(3,2*r,-1,'held source subtract future raw b')
    for r in range(2,q+1):
        e,o,b,c=2*r,2*r+1,2*r,2*r+1
        unary(1,N,f'query{e} source common');scalar(1,3,-1,'isolate c difference');swap(1,3,'even handoff')
        unary(1,a.product(a.P[e-1],a.adjoint(N)),'even retarded source post');swap(3,c,'finished c move')
        unary(b,N,f'query{o} source common')
        for ell in range(r+1,q+1):scalar(2*ell+1,b,1,'future c first fanout')
        scalar(3,b,1,'odd delivery');swap(b,3,'odd handoff');scalar(2,b,-1,'b accumulator')
        for ell in range(r+1,q+1):scalar(2*ell+1,b,-1,'future raw c restoration')
        unary(b,a.product(a.P[o-1],a.adjoint(N)),'odd retarded source post')
        if r<q:
            if encode and r==2:
                # Actual physical word U-=V; ADDRESS R(V); U+=V at cut5.
                # In the retarded proof the middle unary is Ad_(N^-1)(R).
                if encoder=='triangular':
                    scalar(1,b,-1,'changed free encoder U-=V')
                    unary(b,logicalR,'changed free encoder physical ADDRESS R')
                    scalar(1,b,1,'changed free encoder U+=V')
                else:
                    need(encoder=='balanced','known bounded encoder candidate')
                    plus=a.scale(a.add(one,logicalR),Fraction(1,2))
                    minus=a.scale(a.add(one,a.scale(logicalR,-1)),Fraction(1,2))
                    B=a.mat_identity(n);B[1][1]=B[b][b]=plus;B[1][b]=B[b][1]=minus
                    need(a.mat_product(B,B)==a.mat_identity(n),'balanced router keeps both dirty inputs')
                    app(B,B,{'op':'BALANCED_ROUTER','banks':[1,b],
                             'label':'physical H_bank diag(I,R) H_bank^-1; retarded Rtilde retained'})
            scalar(2,1,1,'retain other carrier in b accumulator');nextc=2*r+3
            for ell in range(r+2,q+1):
                scalar(2*ell+1,nextc,-1,'next c difference');scalar(2*ell+1,1,1,'retain carrier in future c')
            swap(1,nextc,'next raw c move');scalar(1,b,1,'next source preload');unary(b,N,'retained odd continuation')
        swap(b,3,'finished b move')
    unary(0,N,'final raw a common query');scalar(2,0,-1,'final b isolation')
    for r in range(3,q+1):scalar(2*r+1,2*r-1,1,'triangular c decode')
    need(a.mat_product(M,Mi)==a.mat_product(Mi,M)==a.mat_identity(n),'all-column literal inverse both orders')
    public=[i for i in range(n)if i not in(1,3)]
    need(all(M[i]==[N if i==j else{}for j in range(n)]for i in public),'all independent public outputs exact every f')
    return a,M,Mi,events,physicalR


def serialize(a,entry):
    out=[]
    for(kd,kb),coeff in sorted(entry.items(),key=lambda t:str(t[0])):
        out.append({'distinguished_tableau':[list(x)for x in kd],'bulk_tableau':[list(x)for x in kb],
                    'gaussian_coefficients_by_f_mod4':[x.encode()for x in coeff],
                    'native_arity_distinguished':ce.rank(x for x,z,p in kd[a.m:]),
                    'native_arity_bulk':ce.rank(x for x,z,p in kb[a.m:])})
    return out


def prove():
    a,M,Mi,events,R=build(3);_,old,_,_,_=build(3,False);_,wrong,_,_,_=build(3,wrong_chart=True)
    need(M!=old,'free encoded stage changes the full residual matrix')
    need(M!=wrong,'physical ADDRESS cannot replace its retarded conjugate')
    H=[[serialize(a,M[i][j])for j in(1,3)]for i in(1,3)]
    public=[0,2,4,5,6,7]
    readers=[[serialize(a,M[i][j])for j in public]for i in(1,3)]
    correction=[[serialize(a,a.product(Mi[i][j],a.N))for j in range(8)]for i in(1,3)]
    return {'status':'PASS_NATIVE_ZERO_ENCODED_STAGE_ALL_COLUMNS_ALL_F',
            'scientific_pin':'20ecf2891d80b5acf18d980b2164fb44ea7faa90','q':3,'banks':8,'query_stages':7,'ambient_arity':16,
            'public_rows':public,'pivot_rows':[1,3],'H':H,'public_L':readers,'full_pivot_correction_rows':correction,
            'free_encoder':{'physical_cut':'after query5 fresh progress, before source continuation and next-pair scalar encoder',
                            'word':['bank1-=bank4','ADDRESS R onbank4','bank1+=bank4'],
                            'R_support_chunks':[0,1,2,4],'R_address_rows':list(R.circuit[0][1]),
                            'R_phase':'identity; exact typed phases cancel for support3p/1q',
                            'retarded_middle_operator':'N^-1 R N, nativearity2f; the physical word uses literal ADDRESS R, nativearity0',
                            'cross_terms':'U_tilde=U+(R_tilde-I)V, V_tilde=R_tilde V; newu=V_tilde,newv=-U_tilde-N A_next',
                            'inverse':['bank1-=bank4','ADDRESS R^-1 onbank4','bank1+=bank4']},
            'prefix_bill':{'H2':61,'native_rank_mass':122,'stock_if_pivots_finish':128,'D_before_tail':6,'added_native_calls':0,'added_ADD_scans':2,'added_ADDRESS_scans':1,'ordinary_helpers':0,'private_fields':0},
            'all_f_binding':'Exact one-coordinate Clifford/Gaussian tensor algebra with explicit fmod4 phase polynomial; no finite-f extrapolation. Every retarded event is lifted coordinatewise and the physical R cut intertwiner is checked separately.',
            'events':events,
            'negative_controls':['Omit encoded stage: full H/L differs.','Substitute physical R for N^-1 R N: full H/L differs despite unchanged public rows.'],
            'limits':['No cleanup word or favorable terminal tariff is claimed.','Native arities of individual Clifford summands are diagnostic, not the cost of the full operator-valued bank row.','This is a changed public-preserving prefix in a grammar outside the marked-residual floor, not a multiplication supplier.'],
            'source_pins':[{'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}for p in(HERE/'handoff_family.py',HERE/'nested_family.py',NATIVE/'lifted_algebra.py',NATIVE/'native_model.py')],
            'no_new_kappa':True}


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--write',action='store_true');args=ap.parse_args()
    out=prove();out['producer_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest();p=HERE/'ENCODED-STAGE.json'
    if args.write:p.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    else:need(json.loads(p.read_text())==out,'saved encoded-stage receipt differs')
    print(out['status'])
if __name__=='__main__':main()
