#!/usr/bin/env python3
"""Independent exact common-cut normalizer audit and bounded inverse search.

No minimum, routed caller, or kappa claim. All writes stay in this directory.
"""
from pathlib import Path
import hashlib, importlib.util, json, random, sys
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CP = Path('/Users/ross/git/math/integer-mult-bounds/research/kernel92-frame-composition/vendor/pr531/vendor/clifford/clifford_exact.py')

def need(b,m):
    if not b: raise ValueError(m)

def main():
    sp=importlib.util.spec_from_file_location('independent_common_cut_ce',CP)
    ce=importlib.util.module_from_spec(sp);sys.modules[sp.name]=ce;sp.loader.exec_module(ce)
    need(hashlib.sha256(CP.read_bytes()).hexdigest()=='2982ead07721e83358dc67c6f49c2b4c16a236a6bebdfd72f58221be1f5d0962','compiler pin')
    rp=ROOT/'shared-helper-budget/COMMON-FRAME-NORMALIZER.json'
    parent=json.loads(rp.read_text());bus=json.loads((HERE/'D4-BUS-INPUT.json').read_text());n=7
    def same(a,b,m):need(a.tab==b.tab and a.zero_state()==b.zero_state(),m)
    def lower(a):
        r,l=ce.lower_child(a);same(a,l,'exact native phase lowering');return r
    def matmul(a,b):return ce.transpose([ce.mv(a,v)for v in ce.transpose(b,n)],n)
    core=[g[0]for g in bus['groups7']]
    chart=ce.perm(n,ce.inv(ce.transpose(core+[5,53,30,96],n),n))
    D=chart.then(ce.hadamard(n,[3,4])).then(chart.adjoint()).then(ce.Op(n,ce.identity(n),[('phase',3)]))
    VC=D.then(ce.cgate(n,core[0])).then(ce.cgate(n,core[1]));F=ce.fourier(n).then(ce.xgate(n,33))
    def mvcols(cols,v):
        out=0
        while v:
            bit=v&-v;out^=cols[bit.bit_length()-1];v^=bit
        return out
    def mulcols(a,b):return tuple(mvcols(a,v)for v in b)
    def tabcols(a):return tuple(x|(z<<n)for x,z,p in a.tab)
    def pcols(G):
        Gi=ce.inv(G,n);Git=ce.transpose(Gi,n)
        gc=ce.transpose(G,n);gic=ce.transpose(Git,n)
        return tuple(gc[j]|((gc[j]^gic[j])<<n)for j in range(n))+tuple(v<<n for v in gic)
    def brank(cols):return ce.rank([v&127 for v in cols[n:]])
    results=[]
    for j,row in enumerate(parent['rows']):
        p,q=row['p'],row['q'];Cp,Cq=ce.cgate(n,p),ce.cgate(n,q)
        S=Cp.adjoint().then(VC);T=Cp.adjoint().then(Cq.adjoint()).then(F);J=ce.xgate(n,p).then(F)
        G=tuple(row['G']);Gi=ce.inv(G,n);metric=matmul(ce.transpose(Gi,n),Gi);Q=tuple((1<<i)^metric[i]for i in range(n))
        need(tuple(row['Q'])==Q,'independent common-cut quadratic reconstruction')
        pre=ce.perm(n,G).then(ce.diag(n,Q));post=S.adjoint().then(pre.adjoint()).then(T)
        same(pre.then(S).then(post),T,'all-input source normalization with actual global phase')
        need(lower(pre)['rank']==lower(post)['rank']==lower(F.adjoint().then(pre).then(F))['rank']==0,'independent parent two-cut audit')
        need(tabcols(pre)==pcols(G),'independent binary common-pair formula agrees actual Clifford')
        DX=Cp;DY=Cp.adjoint().then(F);A=Cp.then(pre).then(Cp.adjoint())
        need(lower(DX.adjoint().then(A.adjoint()).then(DX))['rank']==lower(DY.adjoint().then(A.adjoint()).then(DY))['rank']==0,'actual forward logical cut audit')
        W=lambda op:ce.nullspace(ce.transpose([op.tab[i][0]^op.tab[n+i][0]for i in range(n)],n),n)
        bt,bs=ce.basis_extend(W(T),n),ce.basis_extend(W(S),n)
        BT,BS=ce.transpose(bt,n),ce.transpose(bs,n);BTi=ce.inv(BT,n)
        kt=tabcols(Cp.adjoint().then(Cq));tt=tabcols(T)
        rng=random.Random(20261018+j);best=None;census={};trials=4096
        allowed=[(a,b)for a in range(n)for b in range(n)if a!=b and(a<5 or b>=5)]
        for k in range(trials):
            H=[1<<a for a in range(n)]
            for _ in range(k%41):
                a,b=rng.choice(allowed);H[a]^=H[b]
            g=matmul(BS,matmul(H,BTi));gi=ce.inv(g,n)
            ki=mulcols(pcols(gi),kt)
            ab=mulcols(tt,mulcols(ki,mulcols(tt,ki)))
            # Inverse has the same B-rank. Conjugate inverse by T exactly.
            abr=ce.transpose(ab,2*n);abi=ce.transpose(ce.inv(abr,2*n),2*n)
            bb=mulcols(tt,mulcols(abi,tt))
            ra,rb=brank(ab),brank(bb);key=(ra+rb,ra,rb)
            census[str((ra,rb))]=census.get(str((ra,rb)),0)+1
            if best is None or key<best['score']:best={'score':key,'G':g,'trial':k}
            if key[0]==0:break
        G=best['G'];Gi=ce.inv(G,n);metric=matmul(ce.transpose(Gi,n),Gi);Q=tuple((1<<a)^metric[a]for a in range(n))
        pre=ce.perm(n,G).then(ce.diag(n,Q));post=S.adjoint().then(pre.adjoint()).then(T)
        same(pre.then(S).then(post),T,'winner exact source normalization')
        need(lower(pre)['rank']==lower(post)['rank']==lower(F.adjoint().then(pre).then(F))['rank']==0,'winner all common-cut ranks zero')
        K=pre.then(J).then(T.adjoint());AB=K.adjoint().then(T.adjoint()).then(K.adjoint()).then(T);BB=T.adjoint().then(AB.adjoint()).then(T)
        need((lower(AB)['rank']+lower(BB)['rank'],lower(AB)['rank'],lower(BB)['rank'])==best['score'],'binary search winner independently exact-phase compiled')
        same(AB.then(T.adjoint()).then(K).then(T.then(T)),K.adjoint().then(T),'winner corrected inverse-B cross')
        same(AB.then(T.adjoint()).then(T.then(T)).then(BB),T,'winner corrected inverse-B source diagonal')
        equal=lambda a,b:a.tab==b.tab and a.zero_state()==b.zero_state()
        controls={
            'omit_source_output_normalizer':not equal(pre.then(S),T),
            'omit_common_cut_quadratic_chirp':lower(F.adjoint().then(ce.perm(n,G)).then(F))['rank']>0,
            'omit_inverse_input_correction':not equal(T.adjoint().then(K).then(T.then(T)),K.adjoint().then(T)),
            'replace_inverse_kernel_by_forward_kernel':not equal(K,K.adjoint()),
        }
        need(all(controls.values()),'each named omission/control must actually change its stated contract')
        logical=Cp.then(K).then(Cq.adjoint())
        need(lower(DX.adjoint().then(logical.adjoint()).then(DX))['rank']==lower(DY.adjoint().then(logical.adjoint()).then(DY))['rank']==0,'winner actual forward logical cuts both monomial')
        results.append(dict(p=p,q=q,trials=k+1,best_ranks=best['score'],winning_trial=best['trial'],G=G,Q=Q,
                            pre_events=pre.circuit,post_events=post.circuit,physical_K_events=K.circuit,
                            pre_native=lower(pre),post_native=lower(post),fullcut_native=lower(F.adjoint().then(pre).then(F)),
                            forward_entry_native=lower(DX.adjoint().then(logical.adjoint()).then(DX)),
                            forward_exit_native=lower(DY.adjoint().then(logical.adjoint()).then(DY)),
                            logical_A_events=logical.circuit,logical_A_native=lower(logical),
                            inverse_input=lower(AB),inverse_output=lower(BB),inverse_input_events=AB.circuit,inverse_output_events=BB.circuit,
                            named_negative_controls=controls,rank_pair_census=census))
    out=dict(status='PASS_INDEPENDENT_COMMON_FRAME_NORMALIZER_AND_BOUNDED_INVERSE_SEARCH',parent_receipt_sha256=hashlib.sha256(rp.read_bytes()).hexdigest(),
             source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),compiler_sha256=hashlib.sha256(CP.read_bytes()).hexdigest(),
             local_profile={'1':8,'2':40,'3':16},local_mass=136,ordinary_helpers=0,private_fields=0,
             rows=results,limits=['The bounded rank census is not a lower bound.','A routed caller, all-size primitive/tape/precision bill and owner restoration remain unproved.'])
    (HERE/'COMMON-FRAME-INVERSE-SEARCH.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    print(out['status']);print([(r['p'],r['best_ranks'])for r in results])

if __name__=='__main__':main()
