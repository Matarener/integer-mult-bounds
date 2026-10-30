#!/usr/bin/env python3
"""Exact helper-free reverse carrier: source full7, target5, zero excess."""
from collections import Counter
from pathlib import Path
import hashlib,importlib.util,json,sys
sys.dont_write_bytecode=True
from d4_geometry import need
HERE=Path(__file__).resolve().parent
REPO=Path('/Users/ross/git/math/integer-mult-bounds')
def main():
    cp=REPO/'research/kernel92-frame-composition/vendor/pr531/vendor/clifford/clifford_exact.py'
    sha=hashlib.sha256(cp.read_bytes()).hexdigest();need(sha=='2982ead07721e83358dc67c6f49c2b4c16a236a6bebdfd72f58221be1f5d0962','actual compiler pin')
    sp=importlib.util.spec_from_file_location('reverse_carrier_clifford',cp);ce=importlib.util.module_from_spec(sp);sys.modules[sp.name]=ce;sp.loader.exec_module(ce)
    bp=HERE/'D4-BUS-INPUT.json';bus=json.loads(bp.read_text());n=7;G=bus['groups7'];core=[g[0]for g in G];P=ce.perm(n,ce.inv(ce.transpose(core+[5,53,30,96],n),n))
    D=P.then(ce.hadamard(n,[3,4])).then(P.adjoint()).then(ce.Op(n,ce.identity(n),[('phase',3)]))
    E=[D.then(ce.cgate(n,a))for a in core];VA=E[1].then(ce.cgate(n,core[2]));VB=E[0].then(ce.cgate(n,core[2]));VC=E[0].then(ce.cgate(n,core[1]));F=ce.fourier(n).then(ce.xgate(n,33))
    def same(a,b,msg):need(a.tab==b.tab and a.zero_state()==b.zero_state(),msg)
    def lower(op):
        rec,lit=ce.lower_child(op);same(op,lit,'reverse query exact phase');return rec
    rows=[[int(i==j)for j in range(24)]for i in range(24)]
    def swap(a,b):rows[a],rows[b]=rows[b],rows[a]
    def add(a,b):rows[a]=[x+y for x,y in zip(rows[a],rows[b])]
    for j in range(4):add(12+j,j);swap(j,8+j)
    for j in range(4):add(20+j,j);swap(j,4+j)
    for j in range(4):add(16+j,j)
    for g in range(3):
        for j in range(4):need(rows[4*g+j]==[int(k==4*((g+1)%3)+j)for k in range(24)],'reverse source permutation exact')
    for j in range(12):need(rows[12+j]==[int(k==j)+int(k==12+j)for k in range(24)],'all24 arbitrary columns targetI')
    cleanup=[]
    for j in range(4):swap(j,4+j);cleanup.append([j,4+j]);swap(j,8+j);cleanup.append([j,8+j])
    for j in range(12):need(rows[j]==[int(k==j)for k in range(24)],'fixed physical family IDs restore with transported native frames')
    profiles={};native_rows=[]
    for mode in('full_source_caps','partial_carrier_VB'):
        hist=Counter();paths=[]
        for g in range(3):
            for j,p in enumerate(G[g]):
                q=G[(g+1)%3][j];out=ce.cgate(n,q).adjoint().then(F)
                if g==0:
                    ops=[ce.cgate(n,p),E[0],VA,VC,VB]
                    if mode=='full_source_caps':ops.append(out)
                elif g==1:ops=[ce.cgate(n,p),E[1],VC,out]
                else:ops=[ce.cgate(n,p),E[2],VA,out]
                spath=[lower(a.adjoint().then(b))for a,b in zip(ops,ops[1:])]
                expected=([2,3,2,2,2]if mode=='full_source_caps'else[2,3,2,2])if g==0 else[2,1,2]
                need([x['rank']for x in spath]==expected,'exact reverse source carrier query path')
                target_contact=(VA,VB,VC)[g]
                t_ops=[ce.cgate(n,q),E[(g+1)%3],target_contact,ce.cgate(n,p).adjoint().then(F)]
                tp=[lower(a.adjoint().then(b))for a,b in zip(t_ops,t_ops[1:])]
                need([x['rank']for x in tp]==[2,1,2],'all reverse targets have actual nested delivery contacts')
                for x in spath+tp:hist[x['rank']]+=1
                paths.append({'group':g,'coordinate':j,'source_ranks':[x['rank']for x in spath],'target_ranks':[x['rank']for x in tp]})
        want=Counter({1:20,2:56,3:4})if mode=='full_source_caps'else Counter({1:20,2:52,3:4})
        need(hist==want,'complete reverse histogram')
        profiles[mode]={'histogram':hist,'native_rank_mass':sum(r*c for r,c in hist.items()),'actual_paths':paths}
    for g in range(3):
        for j,p in enumerate(G[g]):
            q=G[(g+1)%3][j];destination=(g+2)%3
            destcap=ce.cgate(n,p).adjoint().then(F)
            S=ce.cgate(n,p).adjoint().then(destcap);J=ce.xgate(n,p).then(F);same(S,J,'every moved source value has full nativeF Xp, exactphase')
            T=ce.cgate(n,p).adjoint().then(ce.cgate(n,q).adjoint()).then(F)
            need(lower(S)['rank']==7 and lower(T)['rank']==5,'extra2 native source progress is real')
            K=ce.cgate(n,p).adjoint().then(ce.cgate(n,q));same(J.then(T.adjoint()),K,'forward normalized asymmetric kernelKold')
            # With literal flipped source/target entry p<->q, the same reverse
            # carrier on partnerO^-1 supplies sourceJq and kernelKold^-1.
            Jq=ce.xgate(n,q).then(F);same(Jq.then(T.adjoint()),K.adjoint(),'paired flipped backward inversekernel exactphase')
            native_rows.append({'group':g,'coordinate':j,'input_port':p,'source_destination_before_raw_cleanup':destination,
                'source_native_rank':7,'target_native_rank':5,'source_channel_events':S.circuit,'target_channel_events':T.circuit,
                'target_cross_events':J.circuit,'forward_kernel_events':K.circuit,'flipped_backward_kernel_events':K.adjoint().circuit})
    need(profiles['full_source_caps']['native_rank_mass']==12*7+12*5,'zero excess complete native coverage')
    out={'status':'PASS_REVERSE_ZERO_HELPER_SOURCE_FULL7_TARGET5_ZERO_EXCESS','compiler_sha256':sha,'source_bus_sha256':hashlib.sha256(bp.read_bytes()).hexdigest(),
        'arbitrary_input_columns':24,'ordinary_helpers':0,'private_fields':0,'canonical_source_map':'(A,B,C)->(B,C,A)','canonical_target_map':'Y+=originalX','profiles':profiles,
        'full_source_cap_native_histogram':{'7':12,'5':12},'full_source_cap_coverage':144,'uncovered_native_mass':0,'actual_native_rows':native_rows,
        'forward_raw_boundary':'[[Jp,0],[Jp,Tp]]=Tp[[Kp,0],[Kp,1]], Kp=Cq Cp^-1','flipped_backward_raw_boundary':'With sourceentryq,targetentryp and partnerO^-1: [[Tp,-Jq],[0,Jq]]=Tp[[1,-Kp^-1],[0,Kp^-1]]. Same mirrored query rank profile; negative target ADDs.',
        'raw_fixed_family_cleanup_SWAPS':cleanup,'scalar_word_before_cleanup':{'complex_ADDs':36,'complex_negations':8},'raw_cleanup_cost':{'whole_field_SWAPs':8,'complex_ADDs':24,'complex_negations':8},
        'limits':['The full7 source channel must be retained as a resource. It is not the old rank5 equal-residual native boundary.','This is a complete local all-input identity with exact phases and zero native uncovered mass, not a complete changed global caller.','Terminal progress may fill a specific missing native2 only after an actual source/owner matching and global operator identity are supplied.','Every monomial, scalar primitive, raw SWAP, access, prefix, rounding and physical-tape obligation remains charged. No kappa claim.']}
    (HERE/'REVERSE-CARRIER.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    print(out['status']);print(json.dumps({k:{j:v[j]for j in('histogram','native_rank_mass')}for k,v in profiles.items()}))

if __name__=='__main__':main()
