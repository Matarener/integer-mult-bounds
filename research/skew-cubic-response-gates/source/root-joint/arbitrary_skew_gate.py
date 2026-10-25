#!/usr/bin/env python3
"""Exact wider-support checks for a proposed general skew-interface gate.
Apache-2.0; substantial OpenAI Codex assistance. No supplier admission.
"""
from pathlib import Path
import hashlib,importlib.util,json,random,sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;R=HERE.parent
SOURCE=R/'general-clifford-retiming/kernel-search/kernel_exact.py'
spec=importlib.util.spec_from_file_location('frozen_kernel_exact_wider_test',SOURCE)
k=importlib.util.module_from_spec(spec);spec.loader.exec_module(k)
qc=k.qc

def embed(j,m):
    d=len(j.rows)
    return qc.Mono(j.rows+tuple(1<<i for i in range(d,m)),j.offset,
        j.alpha+(0,)*(m-d),j.quad+(0,)*(m-d),j.constant,j.global_phase)

def cases():
    d=12;rng=random.Random(202610191422)
    original=k.j_operator(d)
    odd=qc.Mono((3,2)+tuple(1<<i for i in range(2,d)),0,(2,1)+(0,)*(d-2),(0,)*d,0,1)
    for t in range(12):
        rows=list(qc.identity(d).rows)
        for _ in range(24):
            i,j=rng.sample(range(d),2);rows[i]^=rows[j]
        P=qc.Mono(tuple(rows),0,(0,)*d,(0,)*d)
        seed=original if t%2==0 else odd
        # Conjugation by an actual physical linear address map preserves
        # the skew square, while spreading the response across fresh planes.
        yield f'wide-address-conjugate-{t}',P@seed@P.inv()
    # More general X-character Clifford conjugates change native response ranks.
    for t in range(6):
        W=qc.Mono(qc.identity(d).rows,0,tuple(rng.randrange(4)for _ in range(d)),
                  tuple(sum(rng.randrange(2)<<j for j in range(i+1,d))for i in range(d)))
        yield f'wide-quadratic-conjugate-{t}',W@odd@W.inv()

def main():
    fixtures=json.loads((R/'folded-fusion/SIMPLIFIED-FUSIONS.json').read_text())['fixtures']
    rows=[]
    for name,j in cases():
        minus=qc.Mono(qc.identity(12).rows,0,(0,)*12,(0,)*12,0,2)
        k.need(k.mono(j@j)==k.mono(minus),'exact all-f skew square')
        k.J=lambda m,j=j:embed(j,m)
        for f in fixtures:
            q=f['q'];n=2*q+2;kk=2*q+1;m=2*(kk+1);jj=embed(j,m)
            default=k.build(f);changed=k.isolate(default)
            J=lambda s:k.FF(m,s)@jj@k.FF(m,s).inv()
            T=k.P(m,4)@J(3)
            for r in range(3,q+1):T=k.P(m,2*r)@J(2*r-1)@k.N(m,2*r-1)@T
            k.need(k.serial(k.mono(T))==changed['isolated_forward_column_entry'],'wider exact transport including phase')
            L=qc.Mono(qc.identity(m).rows,0,(0,)*m,(0,)*m,0,2)
            for s in range(3,2*q+1):L=k.N(m,s)@L
            k.need(k.serial(k.mono(L))==changed['L'],'wider exact closed L')
            F=k.FF(m,kk);Q=jj@k.P(m,1)@k.N(m,0).inv();W=F@Q.inv()@F.inv()
            k.need(k.mono(W@(F@jj))==k.mono(F@k.N(m,0)@k.P(m,1)),'global Q-target product')
            arities={s:qc.rank(J(s).polar())for s in range(kk+1)}
            parent=default['parent_arity'];d=parent-2*kk
            k.need(all(a>=d for a in arities.values()),'all chronological J lower bounds')
            selected=[arities[2*r-1]for r in range(2,q+1)]
            k.need(changed['R_rank']<=sum(selected)+2*(q-2),'general transport triangle')
            jcounts={s:0 for s in range(kk+1)}
            for e in f['full_events']:
                fam=e.get('native_family')
                if fam and fam.get('kind')=='J':jcounts[fam['completed']]+=1
                elif e.get('native_recipe_id')=='tail-J':jcounts[kk]+=1
            k.need(sum(jcounts.values())==3*q+2,'complete J query count')
            for r in range(2,q+1):
                k.need(jcounts[2*r-1]>0,'each transport J has a paid source occurrence')
                jcounts[2*r-1]-=1
            k.need(sum(jcounts.values())==n+1,'uncancelled J counts')
            lower=n*(2*kk-1)+2*q+sum(c*arities[s]for s,c in jcounts.items())+default['Q_rank']
            k.need(changed['mass']>=lower>=n*parent,'complete mass is at least stock')
            rows.append(dict(case=name,q=q,J=j.data(),chronological_arities=arities,
                remaining_J_multiplicity=jcounts,L_rank=changed['L_rank'],R_rank=changed['R_rank'],
                Q_rank=default['Q_rank'],parent_rank=parent,complete_mass=changed['mass'],
                intermediary_lower_bound=lower,stock=n*parent,all_original_columns=n,
                literal_inverse_orders=2))
        print('PASS_WIDER_SKEW',name,flush=True)
    out=dict(status='PASS_WIDER_SKEW_FINITE_BINDINGS',fixtures=rows,
        source_sha256=hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        producer_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        no_new_kappa=True,scope='Exact finite q2/q3 bindings; separate all-q interface proof required.')
    target=HERE/'ARBITRARY-SKEW-GATE.json'
    target.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')

if __name__=='__main__':main()
