#!/usr/bin/env python3
"""Lower every actual unary in a complete retimed word to selected primitives.

Apache-2.0. Substantial OpenAI Codex assistance. This does not admit owners,
precision, storage or a compatible BIT supplier.
"""
import sys
sys.dont_write_bytecode = True
import argparse
import copy
import hashlib
import json
from collections import Counter
from pathlib import Path
from math import isqrt

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'caller-joint'))
from joint_algebra import qc,ce,need,same,eye,mono,prefix,j_operator
from joint_prefix import check_literal_family,inverse_transpose
from validate_recipe_links import compile_literal,compile_recipe,check_artifact
from literal_events import inverse_events

def literal(g):
    """Physical circuit for i^global times coordinate X-character quadratic."""
    m=len(g.rows); circuit=[]
    for i,a in enumerate(g.alpha):
        if a%4==1:circuit.append(('C',1<<i,1))
        elif a%4==2:circuit.extend([('C',1<<i,1)]*2)
        elif a%4==3:circuit.append(('C',1<<i,-1))
    for i,row in enumerate(g.quad):
        for j in range(i+1,m):
            if row>>j&1:
                circuit.extend([('C',1<<i,1),('C',1<<j,1),('C',(1<<i)|(1<<j),-1)])
    circuit.append(('P',inverse_transpose(g.rows)))
    circuit.append(('D',(0,)*m,tuple(2*((g.offset>>i)&1) for i in range(m))))
    circuit.append(('phase',(g.constant+g.global_phase)%4))
    return compile_literal(circuit,m)

def produce(source):
    data=json.loads(source.read_bytes()); events=copy.deepcopy(data['events'])
    m,n=data['ambient_arity'],data['width']; q=(n-2)//2
    need(n==2*q+2 and m==4*q+4,'caller dimensions')
    pool={}; cap=isqrt((m*m-1)//2); count=0
    for index,e in enumerate(events):
        if e['kind'] in ('ADD','BANK_SWAP'):continue
        g=qc.decode(e,m); op=literal(g); rank=qc.rank(g.polar())
        need(rank==e['rank_per_f'],'unchanged event rank')
        e['one_coordinate_literal_circuit']=op.circuit
        e['one_coordinate_tableau']=[list(t) for t in op.tab]
        e['phase_exponent']=g.global_phase
        check_literal_family(e,m)
        need(ce.rank(x for x,y,p in op.tab[m:])==rank,'physical native arity equals exact polar rank')
        if rank:
            need(rank<=cap,'proper selected child contraction')
            key=f'retimed-q{q}-site{index}'
            e['native_recipe_id']=key;e['recipe_embedding']=list(range(m))
            e['native_family']={'kind':'explicit-retimed-quadratic','inverse':False}
            for inv in (False,True):
                a=op.adjoint() if inv else op; rec,compiled=ce.lower_child(a)
                same(compiled,a,'selected lowering exact tableau and Gaussian zero column')
                same(compile_recipe(rec,m),a,'independent recompilation exact Gaussian operator')
                need(rec['rank']==rank,'selected lowering rank')
                pool[key+('inv' if inv else '')]={
                    'one_coordinate_tableau':[list(t) for t in a.tab],
                    'one_coordinate_definition_circuit':a.circuit,
                    'selected_native_recipe':rec,
                    'phase_exponent':-g.global_phase if inv else g.global_phase,
                    'all_f_phase':'i^(phase_exponent*(1-f)) times the coordinate tensor power'}
            count+=1
    target=mono(prefix(m,2*q+1)@j_operator(m))
    expected=[[target if i==j else {} for j in range(n)] for i in range(n)]
    need(qc.replay(events,n,m)==expected,'actual full FJ on every arbitrary original input')
    inverse=inverse_events(events,m)
    for e in inverse:
        if e['kind'] not in ('ADD','BANK_SWAP'):check_literal_family(e,m)
    need(qc.replay(events+inverse,n,m)==eye(n,m),'complete literal inverse appended')
    need(qc.replay(inverse+events,n,m)==eye(n,m),'complete literal inverse prepended')
    hist=Counter(e['rank_per_f'] for e in events if e['kind']=='NATIVE')
    result=dict(status='PASS_FULL_RETIMED_NATIVE_CALLER',no_new_kappa=True,
        fixtures=[dict(q=q,width=n,banks=n,ambient_arity=m,events=events,inverse_events=inverse,
                       native_recipe_pool=pool,histogram=dict(sorted(hist.items())),
                       native_rank_mass=sum(r*c for r,c in hist.items()),stock=n*m,
                       proper_child_cap=cap,all_input_domain='All original banks arbitrary; every positive f by exact tensor phase polynomials.')],
        source_pins={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in
                     [source,Path(__file__),Path(ce.__file__),Path(qc.__file__),
                      HERE.parent/'caller-joint/joint_algebra.py',
                      HERE.parent/'caller-joint/joint_prefix.py',
                      HERE.parent/'caller-joint/validate_recipe_links.py',
                      HERE.parent/'caller-joint/literal_events.py']},
        limits=['Finite q fixture with all positive f exact operator proof; no all-q construction claim.',
                'Complete rank mass still above stock in the saved q2 witness.',
                'No owner allocation, rounding, source-access, tape, storage, BIT or conditional kappa admission.'])
    return json.loads(json.dumps(result))

def main():
    p=argparse.ArgumentParser();p.add_argument('--source',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True);p.add_argument('--write',action='store_true');a=p.parse_args()
    result=produce(a.source.resolve())
    if a.write:a.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    else:need(json.loads(a.output.read_bytes())==result,'saved native retiming artifact')
    links=check_artifact(a.output)
    print(result['status'],result['fixtures'][0]['native_rank_mass'],links['fixtures'],flush=True)

if __name__=='__main__':main()
