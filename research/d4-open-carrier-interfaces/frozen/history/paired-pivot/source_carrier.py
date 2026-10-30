#!/usr/bin/env python3
"""No-helper source-carrier buses and exact normalized star F/B interfaces."""
from collections import Counter
from pathlib import Path
import hashlib,importlib.util,json,sys
sys.dont_write_bytecode=True
from d4_geometry import dot,need
HERE=Path(__file__).resolve().parent
REPO=Path('/Users/ross/git/math/integer-mult-bounds')
def main():
    cp=REPO/'research/kernel92-frame-composition/vendor/pr531/vendor/clifford/clifford_exact.py'
    sha=hashlib.sha256(cp.read_bytes()).hexdigest();need(sha=='2982ead07721e83358dc67c6f49c2b4c16a236a6bebdfd72f58221be1f5d0962','compiler pin')
    sp=importlib.util.spec_from_file_location('carrier_actual_clifford',cp);ce=importlib.util.module_from_spec(sp);sys.modules[sp.name]=ce;sp.loader.exec_module(ce)
    bp=HERE/'D4-BUS-INPUT.json';bus=json.loads(bp.read_text());n=7;G=bus['groups7'];core=[g[0]for g in G];R=[5,53];dual=[30,96];columns=core+R+dual
    P=ce.perm(n,ce.inv(ce.transpose(columns,n),n));D=P.then(ce.hadamard(n,[3,4])).then(P.adjoint()).then(ce.Op(n,ce.identity(n),[('phase',3)]))
    E=[D.then(ce.cgate(n,a))for a in core];VB=E[0].then(ce.cgate(n,core[2]));VC=E[0].then(ce.cgate(n,core[1]))
    F=ce.ident(n)
    for a in core:F=F.then(ce.cgate(n,a))
    for a,b in zip(R,dual):F=F.then(ce.cgate(n,a)).then(ce.cgate(n,b)).then(ce.cgate(n,a^b).adjoint())
    def same(a,b,msg):need(a.tab==b.tab and a.zero_state()==b.zero_state(),msg)
    def lower(op):
        rec,lit=ce.lower_child(op);same(op,lit,'actual native lowering full phase');return rec
    same(F,ce.fourier(n).then(ce.xgate(n,33)),'exact invariant full gauge')
    # A physical source-A field is itself the carrier. Every original source
    # and target column is independent; no ordinary helper value is present.
    rows=[[int(i==j)for j in range(24)]for i in range(24)]
    def swap(a,b):rows[a],rows[b]=rows[b],rows[a]
    def add(a,b):rows[a]=[x+y for x,y in zip(rows[a],rows[b])]
    for j in range(4):add(12+j,j);swap(j,4+j)
    for j in range(4):add(16+j,j);swap(j,8+j)
    for j in range(4):add(20+j,j)
    for g in range(3):
        for j in range(4):need(rows[4*g+j]==[int(k==4*((g+2)%3)+j)for k in range(24)],'source carrier gives exact3cycle')
    for j in range(12):need(rows[12+j]==[int(k==j)+int(k==12+j)for k in range(24)],'complete arbitrary target responseI')
    cleanup=[]
    for j in range(4):
        swap(j,8+j);cleanup.append([j,8+j]);swap(j,4+j);cleanup.append([j,4+j])
    for j in range(12):need(rows[j]==[int(k==j)for k in range(24)],'raw fixed family ID cleanup carries actual frames')
    profiles={};endpoints=[]
    for name in('closed','open'):
        hist=Counter();queries=[]
        for g in range(3):
            for j,p in enumerate(G[g]):
                q=G[(g+1)%3][j];out=ce.cgate(n,q).adjoint().then(F)
                if g==0:
                    ops=[ce.cgate(n,p),E[0],E[1],E[2]]
                    if name=='closed':ops.extend([E[0],out])
                    else:ops.extend([VB,VC])
                else:ops=[ce.cgate(n,p),E[g],out]
                path=[lower(a.adjoint().then(b))for a,b in zip(ops,ops[1:])]
                expected=([2,2,2,2,3]if name=='closed'else[2,2,2,1,2])if g==0 else[2,3]
                need([x['rank']for x in path]==expected,'actual source carrier native query path')
                for x in path:hist[x['rank']]+=1
                t_ops=[ce.cgate(n,q),E[(g+1)%3]]
                if name=='open'and g==2:t_ops.append(VC)
                t_ops.append(ce.cgate(n,p).adjoint().then(F))
                tp=[lower(a.adjoint().then(b))for a,b in zip(t_ops,t_ops[1:])]
                need([x['rank']for x in tp]==([2,1,2]if name=='open'and g==2 else[2,3]),'actual sourcecarrier target contact')
                for x in tp:hist[x['rank']]+=1
                queries.append({'group':g,'coordinate':j,'source_ranks':[x['rank']for x in path],'target_ranks':[x['rank']for x in tp]})
        need(hist==(Counter({2:36,3:24})if name=='closed'else Counter({1:8,2:40,3:16})),'complete nohelper query histogram')
        profiles[name]={'histogram':hist,'rank_mass':sum(r*c for r,c in hist.items()),'rows':queries}
    for g in range(3):
        for j,p in enumerate(G[g]):
            q=G[(g+1)%3][j];r=G[(g+2)%3][j];T=ce.cgate(n,p).adjoint().then(ce.cgate(n,q).adjoint()).then(F);J=ce.xgate(n,p).then(F)
            S=ce.cgate(n,p).adjoint().then(ce.cgate(n,r).adjoint()).then(F)
            # Orthogonal transposition q<->r fixes p and the invariant qform.
            w=q^r;rowsR=tuple((1<<i)^(w if w>>i&1 else 0)for i in range(n));star=ce.perm(n,rowsR)
            same(star.then(star),ce.ident(n),'star transposition involutive')
            same(star.adjoint().then(F).then(star),F,'actual invariant full gate commutes each portstar')
            same(star.then(S).then(star.adjoint()),T,'two-sided source normalization is exactly old paired diagonal')
            Kold=ce.cgate(n,p).adjoint().then(ce.cgate(n,q));Kstar=star.then(Kold)
            same(star.then(J).then(T.adjoint()),Kstar,'new physical cross kernel is Kold Rstar')
            need(lower(star)['rank']==0,'all source normalizers are literal monomial')
            # Literal inverse of normalized F, bank-role swap, and ONLY
            # address translations produce the genuine inverse-star B.
            X=T.then(T);wantX=ce.xgate(n,127^p^q);same(X,wantX,'T squared is explicit address translation')
            A=ce.xgate(n,p^q)
            inverse_word_cross=A.then(T.adjoint()).then(Kstar).then(X)
            desired_B_cross=Kstar.adjoint().then(T)
            same(inverse_word_cross,desired_B_cross,'actual inverse-star B obtained with same inverse query ranks and Pauli wrappers')
            same(A.then(T.adjoint()).then(X).then(A),T,'source diagonal of inverse B is restored to T')
            same(T.adjoint().then(X),T,'target diagonal of inverse B is restored to T')
            # Corner invariant for independent two-sided monomial charts.
            corner=T.then(J.adjoint()).then(S);want=ce.cgate(n,q).adjoint().then(ce.cgate(n,r).adjoint()).then(F)
            same(corner,want,'closed corner identity exactphase')
            corner_rank=lower(corner)['rank'];need(corner_rank==5,'closed corner rank5')
            clean_corner=T.then(J.adjoint()).then(T);need(lower(clean_corner)['rank']==7,'old clean paired corner rank7')
            openS=S if g<2 else ce.cgate(n,p).adjoint().then(VC)
            open_corner=T.then(J.adjoint()).then(openS);orank=lower(open_corner)['rank'];need(orank==(5 if g<2 else 3),'open sourceC corner rank3 retained')
            need(lower(openS)['rank']==5,'all open moved source channels have actual width5')
            endpoints.append({'group':g,'coordinate':j,'p':p,'q':q,'r':r,'source_normalizer_rows':rowsR,'source_normalizer_events':star.circuit,
                'closed_star_kernel_events':Kstar.circuit,'closed_star_kernel_native_rank':lower(Kstar)['rank'],
                'inverse_B_output_translation':127^p^q,'inverse_B_source_input_and_output_translation':p^q,
                'closed_corner_rank':corner_rank,'open_corner_rank':orank,
                'open_actual_endpoint_events':(ce.cgate(n,r).adjoint().then(F)if g<2 else VC).circuit})
    out={'status':'PASS_ZERO_HELPER_SOURCE_CARRIER_AND_EXACT_STAR_F_INVERSE_B','source_bus_sha256':hashlib.sha256(bp.read_bytes()).hexdigest(),'compiler_sha256':sha,
        'arbitrary_input_columns':24,'ordinary_helpers':0,'private_fields':0,'canonical_source_map':'(A,B,C)->(C,A,B)','canonical_target_map':'Y+=originalX',
        'fixed_family_cleanup_raw_SWAPS':cleanup,'scalar_word_before_cleanup':{'complex_ADDs':36,'complex_negations':8,'whole_source_SWAPs':8},
        'raw_family_cleanup_cost':{'whole_field_SWAPs':8,'signed_complex_ADDs':24,'complex_negations':8},
        'profiles':profiles,'native_source_and_target_widths':{'closed':[5]*24,'open':[5]*24},'normalized_star_rows':endpoints,
        'closed_normalized_F':'[[T,0],[T Kstar,T]], Kstar=Cq Cp^-1 R(q<->r). All12 source channels use independent actual monomial pre/post wrappers.',
        'available_inverse_B':'Literal inverse of normalizedF, swap bankroles; postapply X=T^2 on both outputs, and conjugate the source wire by A=X_(p+q). Result [[T,-T Kstar^-1],[0,T]]. All operations are explicit monomial/wire permutations besides reversed original queries; native inverse query ranks equal original ranks.',
        'corner_lemma':'Under Snew=Lx S Rx, Jnew=Ly J Rx,Tnew=Ly T Ry, the corner Snew Jnew^-1 Tnew=Lx(S J^-1 T)Ry. Its Bruhat Fourier rank is invariant under arbitrary independent two-sided monomial charts. Closedrank5 and openC rank3 differ from oldcleanpairedrank7, so restoring the oldcrossJ aswell is impossible by such charts alone.',
        'limits':['This provides complete changed local F/inverse-B boundaries, not a closed global star-Coxeter caller.','Open sourceC is noncirculant; the simple star conjugation normalizes only the closed bus and openA/B.','Every scalar ADD, raw SWAP, monomial scan, phase and physical access remains paid; zeroordinaryhelpers does not mean zero source work.','No all-size owner, precision, tape, jointsupplier or positive kappa claim.']}
    (HERE/'SOURCE-CARRIER.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    print(out['status']);print(json.dumps({'profiles':{k:{j:v[j]for j in('histogram','rank_mass')}for k,v in profiles.items()},'star_rows':len(endpoints),'corner_ranks':sorted({r['open_corner_rank']for r in endpoints})}))

if __name__=='__main__':main()
