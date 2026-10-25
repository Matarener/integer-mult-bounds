#!/usr/bin/env python3
"""Read-only final-word verification and genuine changed-word controls.
Apache-2.0. Substantial OpenAI Codex assistance. No new kappa.
"""
from pathlib import Path
from collections import Counter
import json, hashlib, sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(HERE/'inputs'))
from joint_algebra import *
from joint_prefix import check_literal_family
from literal_events import inverse_events
from fixture_schema import SCHEMA,REMOVED_SOURCE_FIELDS,CURRENT_FIXTURE_FIELDS,verify_event_metadata


def canonical(x):return json.loads(json.dumps(x))


def validate_scientific_metadata(f):
    q,n,m=f['q'],f['banks'],f['ambient_arity'];P,T,E=f['prefix_events'],f['tail_events'],f['events']
    need(f['schema']==SCHEMA,'explicit current-word schema')
    need(set(f)==CURRENT_FIXTURE_FIELDS,'current fixture field allowlist')
    need(not any(key in f for key in REMOVED_SOURCE_FIELDS),'no inherited source scientific fields')
    need(E==P+T==f['full_events'],'current partitions and full word agree')
    need(f['inverse_events']==canonical(inverse_events(E,m)),'serialized reverse inverse includes current metadata')
    hist=Counter(e['rank_per_f']for e in E if e['kind']=='NATIVE')
    phist=Counter(e['rank_per_f']for e in P if e['kind']=='NATIVE');thist=Counter(e['rank_per_f']for e in T if e['kind']=='NATIVE')
    need(f['histogram']==canonical(dict(hist)),'current complete histogram metadata')
    need(f['prefix_histogram']==canonical(dict(phist)),'current prefix histogram metadata')
    need(f['tail_histogram']==canonical(dict(thist)),'current tail histogram metadata')
    mass=sum(r*c for r,c in hist.items());pmass=sum(r*c for r,c in phist.items())
    need(f['prefix_native_mass']==pmass and f['prefix_D']==n*m-pmass,'current prefix mass and margin metadata')
    need(f['native_mass']==mass and f['stock']==n*m and f['D']==n*m-mass,'current complete cost metadata')
    need(f['tail_native_mass']==mass-pmass,'current tail cost metadata')
    Pi=qc.replay(inverse_events(P,m),n,m);G=mono(prefix(m,2*q+1)@j_operator(m));C=product(G,Pi[1][3])
    need(f['original_t_current_V_correction']==canonical(serial(C)),'current serialized tV correction metadata')
    need(f['original_t_current_V_arity_per_f']==qc.rank(next(iter(C)).polar()),'current tV arity metadata')
    need(f['original_t_current_U_correction']==canonical(serial(product(G,Pi[1][1]))),'current tU correction metadata')
    owners={str(i):{str(j):serial(product(G,Pi[i][j]))for j in(1,3)}for i in(1,3)}
    need(f['current_original_owner_inverse_coefficients']==canonical(owners),'all four current owner inverse coefficients')
    need(f['event_kind_counts']==dict(Counter(e['kind']for e in E)),'current event kind count metadata')
    used={e['native_recipe_id']for e in E+f['inverse_events']if e['kind']=='NATIVE'}
    need(set(f['native_recipe_pool'])==used,'no unused inherited recipe definitions')
    need(f['recipe_reference_validation']==verify_event_metadata(E+f['inverse_events'],f['native_recipe_pool'],m),
         'all current family, rank, phase and recipe references revalidate')


def run():
    out=[]
    original=json.loads((HERE/'inputs/DUAL-CORE.json').read_text())
    for name in('SIMPLIFIED-FUSIONS.json','THREE-FUSIONS.json'):
        raw=(HERE/name).read_bytes();doc=json.loads(raw)
        for f in doc['fixtures']:
            validate_scientific_metadata(f)
            q,n,m=f['q'],f['banks'],f['ambient_arity'];E=f['events'];P=f['prefix_events'];G=mono(prefix(m,2*q+1)@j_operator(m))
            target=[[G if i==j else{}for j in range(n)]for i in range(n)]
            A=qc.replay(E,n,m);Ai=qc.replay(inverse_events(E,m),n,m)
            need(A==target,'literal original outputs are exactly F_k J, including their right gauge')
            need(mm(A,Ai)==mm(Ai,A)==eye(n,m),'complete reverse inverse in both orders')
            phasechecks=0
            for e in E+inverse_events(E,m):
                if e['kind']not in('ADD','BANK_SWAP','SCALE'):check_literal_family(e,m);phasechecks+=1
            hist=Counter(e['rank_per_f']for e in E if e['kind']=='NATIVE')
            need(sum(r*c for r,c in hist.items())==n*m+8,'fully charged rank bill')
            Pi=qc.replay(inverse_events(P,m),n,m);C=product(G,Pi[1][3])
            need(not product(G,Pi[1][1]),'changed t current U coefficient vanishes')
            need(len(C)==1 and qc.rank(next(iter(C)).polar())==2*q+2,'changed tV tariff uses current prefix')
            mutants=[]
            def reject(label,wrong):
                need(wrong!=E,'mutation changes the actual event word')
                need(qc.replay(wrong,n,m)!=target,label);mutants.append(label)
            old=next(x for x in original['fixtures']if x['q']==q and x['name']=='folded-dual')
            at=next(i for i,e in enumerate(E)if e['label']=='fusion stage2 uniform fresh on former source')
            wrong=list(E);wrong[at]=next(e for e in old['prefix_events']if e['label']=='query2 source J')
            reject('stale source J after deleting its B2 inverse',wrong)
            at=next(i for i,e in enumerate(E)if e['label']=='fusion replace shared initial J by minus identity')
            wrong=list(E);wrong[at]=next(e for e in old['prefix_events']if e['label']=='shared initial J exposure')
            reject('stale initial exposure after deleting target t J',wrong)
            at=next(i for i,e in enumerate(E)if e['label']=='dual Q1 recovery')
            wrong=E[:at]+[next(e for e in old['tail_events']if e['label']=='dual B2 recovery')]+E[at:]
            reject('stale downstream cleanup patch reinstates B2 inverse',wrong)
            inv=inverse_events(E,m);at=next(i for i,e in enumerate(inv)if e['kind']=='NATIVE');wronginv=inv[:at]+inv[at+1:]
            need(mm(A,qc.replay(wronginv,n,m))!=eye(n,m),'omitted actual inverse gate is detected')
            mutants.append('omitted actual reverse-inverse native gate')
            bad=dict(f,prefix_D=old['prefix_D'])
            try:validate_scientific_metadata(bad)
            except ValueError:mutants.append('stale inherited prefix margin metadata')
            else:raise ValueError('stale prefix metadata mutant was accepted')
            bad=dict(f,original_t_current_V_arity_per_f=old['original_t_current_V_arity_per_f'])
            try:validate_scientific_metadata(bad)
            except ValueError:mutants.append('stale inherited tV arity metadata')
            else:raise ValueError('stale tV metadata mutant was accepted')
            wrong=canonical(E);at=next(i for i,e in enumerate(wrong)if e['label']=='fusion stage2 uniform fresh on former source')
            stale=next(e for e in old['prefix_events']if e['label']=='query2 source J')
            wrong[at]['native_recipe_id']=stale['native_recipe_id'];wrong[at]['recipe_embedding']=stale['recipe_embedding']
            try:verify_event_metadata(wrong+inverse_events(wrong,m),f['native_recipe_pool'],m)
            except ValueError as error:
                need('embedded native definition'in str(error),'stale recipe control reaches actual operator mismatch')
                mutants.append('stale source J recipe pointer on replaced fresh operator')
            else:raise ValueError('stale native recipe pointer mutant was accepted')
            out.append({'artifact':name,'sha256':hashlib.sha256(raw).hexdigest(),'q':q,'all_original_columns':n,'all_positive_f':'exact tensor family and four Gaussian phase residues',
                        'forward_and_inverse_unary_phase_checks':phasechecks,'inverse_orders':2,'negative_controls':mutants,
                        'complete_histogram':dict(hist),'mass':n*m+8,'stock':n*m,'required_current_tV_arity_per_f':2*q+2,'required_current_tV_coefficient':serial(C),
                        'current_prefix_margin':f['prefix_D'],'event_kind_counts':dict(Counter(e['kind']for e in E))})
    return{'status':'PASS_FOLDED_CROSS_CUT_FUSIONS_ALL_COLUMNS_PHASES_INVERSES_CURRENT_METADATA_CONTROLS',
           'validation_mode':'normal'if __debug__ else'optimized','producer_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
           'schema_sha256':hashlib.sha256((HERE/'fixture_schema.py').read_bytes()).hexdigest(),'cases':out,'no_new_kappa':True}


if __name__=='__main__':
    out=run();name='VERIFICATION.json'if __debug__ else'VERIFICATION-OPTIMIZED.json'
    (HERE/name).write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(out['status'],out['validation_mode'])
