#!/usr/bin/env python3
"""Source-bound p6 native BIT controller with ordinary saving 0.00312.

Retains the complete PR589/PR4359 local word and its owned copied centers.
Every p6 polynomial coefficient, helper owner and whole idle is regenerated.
The p3 utility is an authenticated dependency for rational arithmetic and
the original local port audit. Apache-2.0; source authors credited in proof.
"""
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import argparse, json, sys

sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import bit_tensor_extension as BASE
if sha256(Path(BASE.__file__).read_bytes()).hexdigest()!='7ac72da26df21a0bef1ed15cb500468cf94b328e86efd1ed60a7a0016db415c0':
    raise ValueError('Authenticated p3 arithmetic and original source-replay dependency')

PAIRS=6
KEEP=25279
STAGES=13
AMBIENT=92
T={8:5707,22:444,36:444,50:222,92:222}
P={1:17199,2:17446,3:1027,4:572,5:1326,6:143,7:1357,14:444,28:444,42:222}
TESTED=Q('0.00314')
UNIFORM=Q('0.003135')
COVERED=Q('0.00313')
ADMITTED=Q('0.00312')
POWER=6000
need=BASE.need

def source_replay(root):
    baseline=BASE.source_replay(root)
    import mixed_productive_bit as B
    import bit_native_binding as N
    folder=root/'research/kappa-rebuild/bit'
    word,streams,local=B.audit_local(folder/'sources/pr589-regenerated/WORD.json.gz')
    ports=N.run()
    need(ports['status']=='PASS_FIXED_RATIONAL_PORTS_AND_PHYSICAL_ENDPOINTS',
         'Original exact 15-coordinate rational port charts')
    coefficient,events,idle=B.physical_controller(PAIRS,KEEP)
    factor=B.simultaneous_monomial_factor(coefficient)
    need(factor is not None,'Every p6 coefficient factors over the exact source ring')
    expected=[15,15,63,63,255,255,14337,14337,15873,15873,16383,16383]
    need(factor['diagonal_monomials']==expected,'All twelve complete p6 physical monomials')
    decoded=B.explicit_unbanked_scalar_replay(PAIRS,streams)
    need(decoded['all_arbitrary_columns']==7039 and decoded['independent_dirty_helpers']==5707,
         'Every main and native helper input remains arbitrary and distinct')
    need(decoded['COPY_episodes']==117 and decoded['private_COPY_closed'],
         'All copied-center episodes remain charged and restored')
    scalar=(decoded['unit_ADDs_before_new_boundary_adapters']+
            B.V*factor['boundary_unit_ADDs_per_port']+3*PAIRS*B.V)
    need(scalar==326621,'Complete scalar word including both boundaries and final swaps')
    need(AMBIENT==8+7*(STAGES-1),'Exact expanded rational carrier')
    embeddings=[]
    occupied=set(range(8))
    for stage in range(1,STAGES):
        fresh=list(range(8+7*(stage-1),8+7*stage))
        axes=list(range(8))+fresh
        need(len(axes)==len(set(axes))==15 and max(axes)<AMBIENT,
             'Exact coordinate injection for the original local rational chart')
        need(not (occupied&set(fresh)),'Fresh seven-dimensional stage blocks are disjoint')
        occupied.update(fresh)
        embeddings.append(dict(stage=stage,chart_axes=axes,
                               spectator_axes=[a for a in range(AMBIENT) if a not in axes]))
    need(occupied==set(range(AMBIENT)),'All ambient axes accounted for')
    # If E is the displayed coordinate injection, Gamma=I-EE^t+E rho E^t.
    # E^t E=I15 and rho^2=I15 were checked above; hence Gamma^2=I92.
    # Its active projection identity is the same 15x15 equality on image E,
    # and identity on the displayed spectator axes. No dimension-dependent
    # numerical assertion is used here.
    need(len(ports['ports'])==111 and all(len(p['chart_15'])==15 for p in ports['ports']),
         'Every data port has its exact original rational chart')
    targets=Counter({8:STAGES*B.R})
    endpoints=[]
    for role,mon in enumerate(factor['diagonal_monomials']):
        selected=[s for s in range(STAGES) if mon>>(s+1)&1]
        need(mon&1==1,'Every p6 main role keeps exactly one central rank')
        rank=1+7*len(selected)
        targets[rank]+=B.V
        endpoints.append(dict(role=role,central_q=True,stages=selected,rank=rank))
    paid=Counter({rank:STAGES*count for rank,count in B.LOCAL.items()})
    windows=[]
    for row in idle:
        if row['retained']:
            need(row['rank']==7*len(row['stages']), 'Whole idle is the sum of its orthogonal stage projectors')
            paid[row['rank']]+=2*B.V
            windows.append(row)
    need(dict(targets)==T and dict(paid)==P,'Complete p6 target and paid histograms')
    need(len(windows)==10 and sum(len(w['stages']) for w in windows)==23,
         'All complete idle windows are present once')
    need(sum(T.values())==7039,'No scratch endpoint receives target credit')
    helper_owners=[dict(stage=s,first=2*PAIRS*B.V+s*B.R,
                       last_exclusive=2*PAIRS*B.V+(s+1)*B.R) for s in range(STAGES)]
    need(helper_owners[0]['first']==1332 and helper_owners[-1]['last_exclusive']==7039,
         'Fresh helper owners partition all helper input columns')
    return dict(status='PASS_P6_EXACT_NATIVE_PORTS_ARBITRARY_COLUMNS_AND_WHOLE_IDLES',
                pairs=PAIRS,keep=KEEP,stages=STAGES,ambient_rank=AMBIENT,
                local_audit=local['status'],original_p3_audit=baseline['native_audit'],
                all_arbitrary_columns=7039,independent_dirty_helpers=5707,
                owned_COPY_episodes=117,COPY_or_ERASE_records=234,
                scalar_ADD_allowance=scalar,helper_owners=helper_owners,
                exact_factorization=factor,main_endpoints=endpoints,
                whole_idle_windows=windows,stage_chart_embeddings=embeddings,
                nonidentity_port_routes_including_inverses=(STAGES-1)*111*2*2,
                targets=dict(sorted(targets.items())),paid=dict(sorted(paid.items())),
                source_sha256=BASE.SOURCE_HASHES,
                source_generator_sha256=sha256(Path(B.__file__).read_bytes()).hexdigest(),
                source_port_audit_sha256=sha256(Path(N.__file__).read_bytes()).hexdigest(),
                local_all_f_lift=ports['all_f_lift'],
                expanded_chart_identity='Gamma=I-EE^t+E rho E^t; Gamma^2=I92, active identity on im(E), identity on its orthogonal complement',
                common_weight_contract='All original port charts and every product/compiler matcher are fixed rational right routes in one final cover. No intermediate covered child is lowered.')

def arithmetic():
    tlo,thi=BASE.moment(T,TESTED);plo,phi=BASE.moment(P,TESTED)
    T1=sum(rank*count for rank,count in T.items())
    P1=sum(rank*count for rank,count in P.items())
    need((T1,P1)==(102932,102419),'Exact complete rank masses')
    alpha=phi/tlo
    gamma=Q(P1)/(BASE.powers(7,TESTED)[0]*tlo)
    need(alpha<1-Q(1,100000),'Certified strict tested mixed moment')
    need(gamma<Q(999,1000),'Certified independent rank-one tail estimate')
    need(Q(999,1000)**1000<Q(1,2),'Exact rank-one tail decay block')
    bound=Q(1,1+Q(POWER,100000))+2*Q(1,2)**(POWER//1000)
    need(bound==Q(1653,1696)<1,'Complete finite paid moment with every split tail')
    need(7**16<8**15 and AMBIENT<2**7 and 7<2**3,'Exact separation and ambient bounds')
    t,z=1-TESTED,1-UNIFORM
    z0=(t+z)/2;delta=z0-t;h=Q(1,16)
    exit_bound=(3+7*h)*POWER
    debt=1+7*POWER*(1-z0)
    H0=((exit_bound*delta+debt)/(h*delta)).__ceil__()
    H1=(H0*(1-z0)/(z-z0)).__floor__()+1
    need((H0,H1)==(850090000,1066862950001),'Explicit complete uniform compiler parameters')
    need(H0>=7*POWER and H1*(z-z0)>H0*(1-z0),'Uniform compiler strict moment')
    gap=UNIFORM-COVERED
    cover_bound=(1+gap/4)/(1+gap/2)
    need(gap==Q(1,200000) and cover_bound<1,'Complete delayed good and fallback cover')
    atom=Q('0.0032');old=Q(384599,10**10)
    ordinary=(1-atom)*COVERED+atom*old
    need(ordinary==Q(9750334599,3125000000000),'Exact ordinary conversion')
    need(atom>ordinary>ADMITTED and atom<1-ordinary,'Ordinary adapter and borrowed stock exponents')
    need(BASE.moment(T,Q('.00315'))[1]<BASE.moment(P,Q('.00315'))[0],
         'Reject an unsupported raw saving of .00315')
    return dict(status='PASS_EXACT_P6_BIT_TENSOR_AND_ORDINARY_ARITHMETIC',
                tested_saving=TESTED,compiled_uniform_saving=UNIFORM,
                covered_saving=COVERED,ordinary_saving=ordinary,admitted_BIT_saving=ADMITTED,
                targets=T,paid=P,target_rank_mass=T1,paid_rank_mass=P1,positive_rank_surplus=T1-P1,
                alpha_upper=1-Q(1,100000),gamma_upper=Q(999,1000),
                tensor_power=POWER,cutoff_encoding='7^'+str(POWER),
                complete_normalized_paid_moment_upper=bound,
                strictification_margin=1-bound,
                uniform_compiler=dict(H0=H0,H1=H1,N_encoding='2^'+str(H1),
                                      theta_upper=Q(15,16),h=h,delta=delta,
                                      exit_log2_upper=exit_bound,negative_log2_eta_upper=debt),
                cover=dict(prime_coefficient_times_N5=256/gap,gap=gap,complete_moment_upper=cover_bound),
                ordinary=dict(atom_power=atom,old_saving=old,linear_adapter_gap=atom-ordinary,
                              stock_absorption_gap=1-ordinary-atom,admission_gap=ordinary-ADMITTED),
                materialized_tensor_or_uniform_word=False)

def run(source_root=None):
    out=arithmetic()
    out['native_source']=(source_replay(Path(source_root).resolve()) if source_root is not None
                          else {'status':'NOT_REPLAYED_ARITHMETIC_ONLY'})
    out['verifier_sha256']=sha256(Path(__file__).read_bytes()).hexdigest()
    out['arithmetic_dependency_sha256']=sha256(Path(BASE.__file__).read_bytes()).hexdigest()
    return out

if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--source-root',type=Path);a.add_argument('--out',type=Path)
    args=a.parse_args();data=run(args.source_root)
    payload=json.dumps(BASE.encode(data),indent=2,sort_keys=True)+'\n'
    if args.out:args.out.write_text(payload)
    print(payload,end='')
