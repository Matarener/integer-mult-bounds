#!/usr/bin/env python3
"""Literal simultaneous prefix/tail edits, exact full-column replay.
Apache-2.0. Substantial OpenAI Codex assistance. No new kappa.
"""
from pathlib import Path
from collections import Counter
import json, sys, hashlib
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE/'inputs'))
from joint_algebra import *
from joint_prefix import check_literal_family
from one_site_absorption import screen, inverse
from literal_events import inverse_events
from fixture_schema import assemble_fixture


def event_from_op(bank,g,op,exponent,label,key):
    rank=qc.rank(g.polar())
    e={'kind':'NATIVE'if rank else'ADDRESS_OR_UNIT','bank':bank,'x_monomial':g.data(),'rank_per_f':rank,
       'label':label,'native_family':{'kind':'folded-fusion','inverse':False}if rank else None,
       'phase_exponent':exponent,'one_coordinate_literal_circuit':op.circuit,'one_coordinate_tableau':[list(t)for t in op.tab]}
    if rank:e.update(native_recipe_id=key,recipe_embedding=list(range(len(g.rows))))
    check_literal_family(e,len(g.rows));return e


def combine(f,lower=True):
    q,n,m=f['q'],f['banks'],f['ambient_arity'];k=2*q+1;z=Model(1,k)
    I=qc.identity(m);minus=qc.Mono(I.rows,0,(0,)*m,(0,)*m,0,2)
    minusop=ce.Op(m,ce.identity(m),[('phase',2)])
    newG=plane_swap(m,0,2)@n_pair(m,2);newop=mul(z.P[1],z.T[1])
    P=[];T=[];changes=[];pool=dict(f.get('native_recipe_pool',{}))
    for i,e in enumerate(f['prefix_events']):
        if e['label']=='shared initial J exposure':
            e=event_from_op(1,minus,minusop,2,'fusion replace shared initial J by minus identity','fusion-initial')
            changes.append({'section':'prefix','old_site':i,'kind':'replace','rank_delta':-2,'identity':'J*J=-I'})
        elif e['label']=='query2 source J':
            e=event_from_op(1,newG,newop,1,'fusion query2 native fresh ADDRESS completion','fusion-source2')
            changes.append({'section':'prefix','old_site':i,'kind':'replace','rank_delta':0,'identity':'P2 N2; retarded source code becomes I'})
        P.append(e)
    for i,e in enumerate(f['tail_events']):
        if e['label']in('dual B2 recovery','dual original t full FJ'):
            changes.append({'section':'tail','old_site':i,'kind':'delete','label':e['label'],'rank_delta':-e['rank_per_f']})
        else:T.append(e)
    if lower:
        for inv in(False,True):
            op=newop.adjoint()if inv else newop;name='fusion-source2'+('inv'if inv else'')
            rec,compiled=ce.lower_child(op);same(compiled,op,'new source2 full signed tableau and Gaussian phase')
            need(rec['rank']==2,'new source2 native rank2')
            pool[name]={'selected_native_recipe':rec,'native_rank':2,'phase_exponent':-1 if inv else 1,
                        'one_coordinate_definition_circuit':op.circuit,'one_coordinate_tableau':[list(t)for t in op.tab]}
    E=P+T;actual=qc.replay(E,n,m);target=mono(prefix(m,k)@j_operator(m));expected=[[target if i==j else{}for j in range(n)]for i in range(n)];inve=inverse_events(E,m);actuali=qc.replay(inve,n,m)
    for e in inve:
        if e['kind']not in('ADD','BANK_SWAP','SCALE'):check_literal_family(e,m)
    need(actual==expected,'simultaneous fusion all original columns, exact all-f family')
    need(mm(actual,actuali)==mm(actuali,actual)==eye(n,m),'simultaneous complete literal inverse both orders')
    H=Counter(e['rank_per_f']for e in E if e['kind']=='NATIVE');mass=sum(r*c for r,c in H.items())
    need(mass==f['native_mass']-8,'all changed native charges included')
    source_reference={'artifact':'inputs/DUAL-CORE.json','sha256':hashlib.sha256((HERE/'inputs/DUAL-CORE.json').read_bytes()).hexdigest(),
                      'fixture_q':q,'fixture_name':f['name'],'role':'immutable predecessor only; its derived fields are not current fixture metadata'}
    return assemble_fixture(q,'folded-dual-two-fusions',P,T,pool,source_reference,
                            {'simultaneous_edits':changes,'new_source2_selected_lowering':lower})


def simplify_stage2(f,lower=True):
    """Regenerate from current two-fusion word; cancel the literal star."""
    q,n,m=f['q'],f['banks'],f['ambient_arity'];z=Model(1,2*q+1)
    P=f['prefix_events'];new=[];removed=[];pool=dict(f['native_recipe_pool'])
    skip_labels={'changed core2 scalar entrance','changed core2 scalar exit','changed core2 J-valued pre-delivery','query2 delivery','query2 source swap'}
    for i,e in enumerate(P):
        if e['label']in skip_labels:removed.append({'site':i,'event':e});continue
        if e['label']=='fusion query2 native fresh ADDRESS completion':
            e=event_from_op(1,n_pair(m,2),z.T[1],1,'fusion stage2 uniform fresh on former source','fusion-source2-uniform')
        new.append(e)
    need(len(removed)==2*q+3,'exact stage2 star and cancelled delivery sites')
    E=new+f['tail_events'];need(qc.replay(E,n,m)==qc.replay(f['events'],n,m),'current-word stage2 star cancellation all input columns')
    if lower:
        for inv in(False,True):
            op=z.T[1].adjoint()if inv else z.T[1];key='fusion-source2-uniform'+('inv'if inv else'')
            rec,compiled=ce.lower_child(op);same(compiled,op,'uniform source fresh selected native phase')
            pool[key]={'selected_native_recipe':rec,'native_rank':2,'phase_exponent':-1 if inv else 1,
                       'one_coordinate_definition_circuit':op.circuit,'one_coordinate_tableau':[list(t)for t in op.tab]}
    inve=inverse_events(E,m);A=qc.replay(E,n,m);Ai=qc.replay(inve,n,m)
    need(mm(A,Ai)==mm(Ai,A)==eye(n,m),'simplified complete reverse inverse both orders')
    return assemble_fixture(q,'folded-dual-two-fusions-uniform-stage2',new,f['tail_events'],pool,f['source_reference'],
                            {'simultaneous_edits':f['construction_notes']['simultaneous_edits'],
                             'simplified_stage2_removed_sites':removed,'new_source2_selected_lowering':lower})


def fuse_u(f):
    q,n,m=f['q'],f['banks'],f['ambient_arity'];P=list(f['prefix_events']);T=list(f['tail_events'])
    at=next(i for i,e in enumerate(P)if e['label']==f'query{2*q+1} idle fresh'and e.get('bank')==1)
    tailat=next(i for i,e in enumerate(T)if e['label']=='joint U coordinate recovery')
    def touched(e):
        if e['kind']=='ADD':return{e['src'],e['dst']}
        if e['kind']=='BANK_SWAP':return set(e['banks'])
        return{e['bank']}
    need(all(1 not in touched(e)for e in P[at+1:]+T[:tailat]),'U fusion literal disjoint intervening supports')
    a,b=P[at],T[tailat];ga,gb=qc.decode(a,m),qc.decode(b,m)
    opa=ce.Op(m,tuple(tuple(t)for t in a['one_coordinate_tableau']),a['one_coordinate_literal_circuit'])
    opb=ce.Op(m,tuple(tuple(t)for t in b['one_coordinate_tableau']),b['one_coordinate_literal_circuit'])
    op=mul(opb,opa);g=gb@ga;need(qc.rank(g.polar())==8,'U plus disjoint final fresh arity8')
    P[at]=event_from_op(1,g,op,a['phase_exponent']+b['phase_exponent'],'fusion U inverse with final charged fresh','fusion-U-final-fresh')
    del T[tailat];pool=dict(f['native_recipe_pool'])
    for inv in(False,True):
        actual=op.adjoint()if inv else op;key='fusion-U-final-fresh'+('inv'if inv else'')
        rec,compiled=ce.lower_child(actual);same(compiled,actual,'fused U actual selected native rank8 phase')
        need(rec['rank']==8,'fused U selected native rank8')
        pool[key]={'selected_native_recipe':rec,'native_rank':8,'phase_exponent':0,'one_coordinate_definition_circuit':actual.circuit,
                   'one_coordinate_tableau':[list(t)for t in actual.tab]}
    E=P+T;need(qc.replay(E,n,m)==qc.replay(f['events'],n,m),'fused U original columns unchanged')
    inve=inverse_events(E,m);A=qc.replay(E,n,m);Ai=qc.replay(inve,n,m)
    need(mm(A,Ai)==mm(Ai,A)==eye(n,m),'fused U complete reverse inverse both orders')
    hist=Counter(e['rank_per_f']for e in E if e['kind']=='NATIVE')
    need(sum(r*c for r,c in hist.items())==f['native_mass'],'U fusion mass neutrality')
    return assemble_fixture(q,'folded-dual-three-fusions',P,T,pool,f['source_reference'],
                            {'simultaneous_edits':f['construction_notes']['simultaneous_edits'],
                             'simplified_stage2_removed_sites':f['construction_notes']['simplified_stage2_removed_sites'],
                             'extra_fusion':{'prefix_site':at,'removed_tail_site':tailat,'delta':'H8-H6-H2','mass_delta':0}})


def main():
    source=HERE/'inputs/DUAL-CORE.json';raw=source.read_bytes()
    fs=[f for f in json.loads(raw)['fixtures']if f['name']=='folded-dual']
    results=[combine(f)for f in fs]
    out={'schema':'folded-fusion-current-word-v2','status':'PASS_TWO_SIMULTANEOUS_FUSIONS_ALL_COLUMNS_ALL_F',
         'producer_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
         'source_sha256':hashlib.sha256(raw).hexdigest(),'fixtures':results,'no_new_kappa':True}
    (HERE/'COMBINED-FUSIONS.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    simplified=[simplify_stage2(f)for f in results]
    (HERE/'SIMPLIFIED-FUSIONS.json').write_text(json.dumps(dict(out,status='PASS_SIMPLIFIED_TWO_FUSIONS_ALL_COLUMNS_ALL_F',fixtures=simplified),indent=2,sort_keys=True)+'\n')
    three=[fuse_u(f)for f in simplified]
    (HERE/'THREE-FUSIONS.json').write_text(json.dumps(dict(out,status='PASS_THREE_SIMULTANEOUS_FUSIONS_ALL_COLUMNS_ALL_F',fixtures=three),indent=2,sort_keys=True)+'\n')
    screens=[]
    for f in results:
        screens.append(screen(f));r=screens[-1]
        (HERE/'AFTER-TWO-SCREEN.json').write_text(json.dumps({'results':screens,'no_new_kappa':True},indent=2,sort_keys=True)+'\n')
        print('q',r['q'],'combined',r['frozen_complete_mass'],'remaining one-site best',r['best_complete_mass'],'stock',r['stock'],flush=True)
    all_unary=[screen(f,include_zero=True)for f in simplified]
    (HERE/'ALL-UNARY-AFTER-TWO-SCREEN.json').write_text(json.dumps({'results':all_unary,'no_new_kappa':True},indent=2,sort_keys=True)+'\n')


if __name__=='__main__':main()
