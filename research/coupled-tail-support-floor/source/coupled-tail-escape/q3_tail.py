#!/usr/bin/env python3
"""Exact q3 suffix and the same isolated entry support boundary.
Apache-2.0. Substantial OpenAI Codex assistance. No all-q caller claim.
"""
from pathlib import Path
import argparse,copy,hashlib,json,sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import local_block as base
from joint_algebra import *
from validate_recipe_links import compile_literal,compile_recipe,embedding_circuit


def produce():
    R=base.RUNDIR
    a=next(f for f in json.loads((R/'two-site-continuation/ADMITTED-TWO-SITE-FUSIONS.json').read_text())['fixtures']if f['q']==3)
    b=next(f for f in json.loads((R/'folded-fusion/SIMPLIFIED-FUSIONS.json').read_text())['fixtures']if f['q']==3)
    cut=next(i for i,e in enumerate(a['events'])if e['label']=='final independent a J query')
    E=copy.deepcopy(a['events'][cut:]);Ei=copy.deepcopy(a['inverse_events'][:len(E)]);n,m=8,16;pool={}
    for events in(E,Ei):
        for e in events:
            if e['kind']in('ADD','SCALE','BANK_SWAP'):continue
            old=b['events'][e['source_event_ordinal']];g=qc.decode(old,m)
            op=compile_literal(old['one_coordinate_literal_circuit'],m)
            ep=tuple(old['phase_exponent']*(1-r)%4 for r in range(4))
            if e['source_operator_is_adjoint']:g=g.inv();op=op.adjoint();ep=tuple(-x%4 for x in ep)
            e['x_monomial']=g.data();actual=compile_literal(e['one_coordinate_literal_circuit'],m)
            same(actual,op,'q3 actual source unary signed operator and Gaussian phase')
            need(base.extra(e)==ep,'q3 all-f source phase')
            if e['kind']=='NATIVE':
                rec=a['native_recipe_pool'][e['native_recipe_id']];d=len(rec['one_coordinate_tableau'])//2
                selected=compile_recipe(rec['selected_native_recipe'],d)
                full=compile_literal(embedding_circuit(selected.circuit,e['recipe_embedding'],m),m)
                same(full,actual,'q3 current forward/inverse selected recipe')
                need(tuple(rec['extra_global_phase_exponent_by_f_mod4'])==ep,'q3 selected recipe all-f phase')
                pool[e['native_recipe_id']]=rec
    M=qc.replay(E,n,m);Mi=qc.replay(Ei,n,m)
    need(mm(M,Mi)==mm(Mi,M)==eye(n,m),'q3 serialized entire local inverse bothorders')
    reverse=[e for e in E if e['label'].startswith('w reverse')and e['kind']!='ADD' or e['label']=='final extraction D_final inverse sign']
    W=next(e for e in E if e['label']=='dual Q1 recovery');Rop=qc.identity(m)
    C=ce.ident(m);phase=[0]*4
    for e in reverse+[W]:
        C=C.then(compile_literal(e['one_coordinate_literal_circuit'],m));phase=[(x+y)%4 for x,y in zip(phase,base.extra(e))]
    for e in reverse:Rop=qc.decode(e,m)@Rop
    need(M[1][3]==mono(qc.decode(W,m)@Rop),'q3 exact single WR incoming3/output1 coefficient')
    need(len(M[1][3])==1 and ce.rank(x for x,z,p in C.tab[m:])==8,'q3 native arity8 entry')
    rec,compiled=ce.lower_child(C);same(compiled,C,'q3 support witness exact Gaussian lowering');same(compile_recipe(rec,m),C,'q3 support recipe recompilation')
    need(rec['rank']==8,'q3 support witness Fourier rank')
    local=sum(e['rank_per_f']for e in E if e['kind']=='NATIVE');before=a['native_mass']-local
    need((cut,local,before,a['stock'])==(119,12,120,128),'q3 exact local/full invoice')
    return dict(status='PASS_Q3_COUPLED_SUFFIX_SUPPORT_GATE',no_new_kappa=True,producer_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                q=3,banks=n,ambient_arity=m,cut_event_ordinal=cut,unchanged_prefix_native_mass=before,local_native_mass=local,whole_native_mass=132,stock=128,
                events=E,inverse_events=Ei,native_recipe_pool=pool,complete_local_matrix=sm(M),complete_local_inverse=sm(Mi),
                unavoidable_entry=dict(row=1,column=3,operator=serial(M[1][3]),native_arity_per_f=8,one_coordinate_tableau=C.tab,
                                      one_coordinate_literal_circuit=C.circuit,extra_global_phase_exponent_by_f_mod4=phase,support_witness_recipe=rec),
                support_inequality='R_f+S_f>=8f; fixed120f prefix prevents total<128f for bounded-in-f ADD scans.',
                source_pins=[dict(path=str(R/p),sha256=h)for p,h in base.PINS.items()],base_producer_sha256=hashlib.sha256(Path(base.__file__).read_bytes()).hexdigest(),
                scope='Exact q3 local suffix on all8 arbitrary incoming banks and both serialized inverse orders; conditional all-q tail lemma is separate, not an all-q complete caller.')


def main():
    p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');a=p.parse_args();out=json.loads(json.dumps(produce()));target=HERE/'Q3-LOCAL-BLOCK.json'
    if a.write:target.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    else:need(json.loads(target.read_text())==out,'saved q3 local suffix')
    print(out['status'],'prefix120/local12/entry8/stock128')


if __name__=='__main__':main()
