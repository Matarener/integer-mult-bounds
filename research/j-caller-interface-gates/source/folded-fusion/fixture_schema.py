#!/usr/bin/env python3
"""Explicit current-word fixture schema; no inherited scientific fields.
Apache-2.0. Substantial OpenAI Codex assistance.
"""
from pathlib import Path
from collections import Counter
from functools import lru_cache
import hashlib, json, sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(HERE/'inputs'))
from joint_algebra import *
from joint_prefix import check_literal_family
from literal_events import inverse_events

SCHEMA='folded-fusion-current-word-v2'
REMOVED_SOURCE_FIELDS=('retarded_H','retarded_L','core_Knew','P2tilde','physical_prefix_matrix',
                       'physical_prefix_inverse','source_choice','reader_identity','selected_native_lowerings')
CURRENT_FIXTURE_FIELDS=set('''schema q name banks width ambient_arity prefix_events tail_events events full_events native_recipe_pool
source_reference construction_notes all_original_columns literal_inverse_orders new_native_lowerings recipe_reference_validation
removed_inherited_scientific_fields limits inverse_events histogram native_mass stock D prefix_histogram prefix_native_mass prefix_D
tail_histogram tail_native_mass original_t_current_V_correction original_t_current_V_arity_per_f original_t_current_U_correction
current_original_owner_inverse_coefficients event_kind_counts'''.split())


@lru_cache(None)
def compile_literal(encoded,n):
    out=ce.ident(n)
    for e in json.loads(encoded):
        if e[0]=='P':op=ce.perm(n,e[1])
        elif e[0]=='D':op=ce.diag(n,e[1],e[2])
        elif e[0]=='C':op=ce.cgate(n,e[1],e[2])
        elif e[0]=='X':op=ce.xgate(n,e[1])
        else:
            need(e[0]=='phase','covered literal circuit primitive')
            op=ce.Op(n,ce.identity(n),[('phase',e[1])])
        out=out.then(op)
    return out


def embed(circuit,index,n):
    d=len(index);need(len(set(index))==d and all(0<=j<n for j in index),'injective current native embedding')
    def bits(x):return sum(((x>>i)&1)<<index[i]for i in range(d))
    out=[]
    for e in circuit:
        if e[0]=='P':
            rows=[1<<i for i in range(n)]
            for i,j in enumerate(index):rows[j]=bits(e[1][i])
            out.append(('P',rows))
        elif e[0]=='D':
            rows=[0]*n;alpha=[0]*n
            for i,j in enumerate(index):rows[j]=bits(e[1][i]);alpha[j]=e[2][i]
            out.append(('D',rows,alpha))
        elif e[0]in('C','X'):out.append((e[0],bits(e[1]),*e[2:]))
        else:
            need(e[0]=='phase','covered embedding primitive');out.append(e)
    return out


def verify_event_metadata(events,pool,m):
    """Bind every retained family, definition, rank, phase and recipe pointer."""
    links=0;used=set();I=qc.identity(m)
    for e in events:
        if e['kind']in('ADD','BANK_SWAP','SCALE'):continue
        g=qc.decode(e,m);r=qc.rank(g.polar())
        need(r==e['rank_per_f'],'event rank from actual operator')
        need((e['kind']=='NATIVE')==(r>0),'native kind from actual operator')
        actual=compile_literal(json.dumps(e['one_coordinate_literal_circuit']),m)
        need(actual.tab==tuple(tuple(t)for t in e['one_coordinate_tableau']),'event tableau from actual literal circuit')
        check_literal_family(e,m)
        fam=e.get('native_family')
        if e['kind']!='NATIVE':
            need(not fam and 'native_recipe_id'not in e,'rank-zero event has no native family or recipe pointer')
            continue
        need(fam and isinstance(fam.get('inverse'),bool),'native family has an explicit direction')
        key=e['native_recipe_id'];need(key in pool,'current native recipe pointer exists')
        need(fam['inverse']==key.endswith('inv'),'current native family and recipe direction agree')
        if fam['kind']=='N':
            expected=n_pair(m,fam['plane'])
        elif fam['kind']=='J':
            F0=prefix(m,fam['completed']);expected=F0@j_operator(m)@F0.inv()
        else:
            need(fam['kind']in('tail','dual-tail','folded-fusion'),'covered native family')
            expected=None
        if expected is not None:
            if fam['inverse']:expected=expected.inv()
            need(g==expected,'retained N/J family names the actual operator')
        p=pool[key];pn=len(p['one_coordinate_tableau'])//2
        need(len(e['recipe_embedding'])==pn,'current recipe embedding has definition width')
        definition=compile_literal(json.dumps(p['one_coordinate_definition_circuit']),pn)
        need(definition.tab==tuple(tuple(t)for t in p['one_coordinate_tableau']),'pool tableau from actual definition')
        nr=ce.rank(x for x,z,ph in definition.tab[pn:])
        need(nr==r==p['selected_native_recipe']['rank'],'event/pool/selected native ranks agree')
        if 'native_rank'in p:need(p['native_rank']==nr,'pool explicit native rank agrees')
        need(e['phase_exponent']==p['phase_exponent'],'event/pool exact tensor phase exponent')
        embedded=embed(p['one_coordinate_definition_circuit'],e['recipe_embedding'],m)
        compiled=compile_literal(json.dumps(embedded),m)
        need(compiled.tab==actual.tab,'embedded native definition signed tableau equals actual event')
        check_literal_family(dict(e,one_coordinate_literal_circuit=embedded),m)
        used.add(key);links+=1
    return {'used_recipe_keys':sorted(used),'forward_inverse_native_links':links}


def current_statistics(q,P,T):
    n,m=2*q+2,4*q+4;E=P+T;Pinv=inverse_events(P,m);Einv=inverse_events(E,m)
    PM,Pi=qc.replay(P,n,m),qc.replay(Pinv,n,m)
    need(mm(PM,Pi)==mm(Pi,PM)==eye(n,m),'current prefix inverse both orders')
    G=mono(prefix(m,2*q+1)@j_operator(m));target=[[G if i==j else{}for j in range(n)]for i in range(n)]
    A,Ai=qc.replay(E,n,m),qc.replay(Einv,n,m)
    need(A==target,'current complete exact physical FJ target')
    need(mm(A,Ai)==mm(Ai,A)==eye(n,m),'current complete inverse both orders')
    ph=Counter(e['rank_per_f']for e in P if e['kind']=='NATIVE')
    th=Counter(e['rank_per_f']for e in T if e['kind']=='NATIVE')
    h=ph+th;mass=sum(r*c for r,c in h.items());pmass=sum(r*c for r,c in ph.items())
    owner={str(i):{str(j):serial(product(G,Pi[i][j]))for j in(1,3)}for i in(1,3)}
    C=product(G,Pi[1][3]);need(len(C)==1,'current tV coefficient is one native operator')
    return {'inverse_events':Einv,'histogram':dict(h),'native_mass':mass,'stock':n*m,'D':n*m-mass,
            'prefix_histogram':dict(ph),'prefix_native_mass':pmass,'prefix_D':n*m-pmass,'tail_histogram':dict(th),
            'tail_native_mass':mass-pmass,'original_t_current_V_correction':serial(C),
            'original_t_current_V_arity_per_f':qc.rank(next(iter(C)).polar()),'original_t_current_U_correction':serial(product(G,Pi[1][1])),
            'current_original_owner_inverse_coefficients':owner,'event_kind_counts':dict(Counter(e['kind']for e in E))}


def assemble_fixture(q,name,P,T,pool,source_reference,construction_notes):
    """Construct from an allowlist, never copy an old fixture dictionary."""
    n,m=2*q+2,4*q+4;stats=current_statistics(q,P,T);E=P+T
    used={e['native_recipe_id']for e in E+stats['inverse_events']if e['kind']=='NATIVE'}
    selected={key:pool[key]for key in sorted(used)}
    links=verify_event_metadata(E+stats['inverse_events'],selected,m)
    result={'schema':SCHEMA,'q':q,'name':name,'banks':n,'width':n,'ambient_arity':m,
            'prefix_events':P,'tail_events':T,'events':E,'full_events':E,'native_recipe_pool':selected,
            'source_reference':source_reference,'construction_notes':construction_notes,
            'all_original_columns':n,'literal_inverse_orders':2,'new_native_lowerings':'actual signed tableau and Gaussian phase checked',
            'recipe_reference_validation':links,'removed_inherited_scientific_fields':list(REMOVED_SOURCE_FIELDS),
            'limits':['Finite physical serialization q as listed, every positive f by exact tensor family.',
                      'Written all-q local identities retain the source folded-reader interface.',
                      'No precision, physical tape, chronological owner allocation, useful supplier or new kappa.']}
    result.update(stats)
    need(set(result)==CURRENT_FIXTURE_FIELDS,'explicit current-word field allowlist')
    need(all(k not in result for k in REMOVED_SOURCE_FIELDS),'no inherited scientific fixture fields')
    return result
