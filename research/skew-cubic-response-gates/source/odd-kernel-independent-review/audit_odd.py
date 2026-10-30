#!/usr/bin/env python3
"""Independent finite odd-kernel crossed-strand/source/phase audit.
Apache-2.0; substantial OpenAI Codex assistance. No search or supplier claim.
"""
from pathlib import Path
import argparse,hashlib,json,sys,types
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;R=HERE.parent;SOURCE=R/'odd-kernel-frame-escape'
p=R/'completed-gates-review/audit_gates.py';a=types.ModuleType('pinned_exact_review');a.__file__=str(p)
exec(compile(p.read_bytes(),str(p),'exec',dont_inherit=True,optimize=0),a.__dict__)
def direct(events,n,m,crosses,omit_swap=None):
    labels=list(range(n));ops=[a.ce.ident(m)for _ in range(n)];ph=[(0,)*4 for _ in range(n)]
    for t,e in enumerate(events):
        if (e['kind']=='BANK_SWAP'and t!=omit_swap) or(e['kind']=='ADD'and t in crosses):
            i,j=e['banks']if e['kind']=='BANK_SWAP'else(e['dst'],e['src'])
            for v in(labels,ops,ph):v[i],v[j]=v[j],v[i]
        elif e['kind']not in('ADD','SCALE','BANK_SWAP'):
            b=e['bank'];g=a.independent.op_of(json.dumps(e['one_coordinate_literal_circuit']),m);ops[b]=ops[b].then(g)
            ex=e.get('extra_global_phase_exponent_by_f_mod4',[(e.get('phase_exponent',0)*(1-r))%4 for r in range(4)]);ph[b]=tuple((x+y)%4 for x,y in zip(ph[b],ex))
    return [(labels.index(i),ops[labels.index(i)],ph[labels.index(i)])for i in range(n)]
def partition(edges,paths):
    a.need(sorted(i for p in paths for i in p)==list(range(len(edges))),'every edge exactly once')
    for path in paths:
        previous=0
        for i in path:a.need(edges[i]['u']==previous,'partition path incidence');previous=edges[i]['v']
        a.need(previous==0,'partition endpoint boundary')
def check(f,source):
    q=f['q'];raw=source['isolated'];E=raw['events'];m,n=f['ambient_arity'],f['banks'];mask=int(f['mask_decimal']);adds=[t for t,e in enumerate(E)if e['kind']=='ADD'];crosses={t for bit,t in enumerate(adds)if mask>>bit&1}
    a.need(mask>=0 and mask<1<<len(adds) and adds==f['ADD_event_ordinals'] and sorted(crosses)==f['crossing_ADD_event_ordinals'],'exact chronological pairing bits')
    a.need(f['chronological_pairing_bitstring']==''.join('1'if mask>>bit&1 else'0'for bit in range(len(adds))),'redundant chronological bitstring agrees')
    a.need(hashlib.sha256(a.stable(E).encode()).hexdigest()==f['source_events_sha256'],'exact actual isolated source event array')
    edges=[];paths=[[]for _ in range(n)];at=[0]*n;owner=list(range(n));pend=[a.ce.ident(m)for _ in range(n)];phase=[(0,)*4 for _ in range(n)];ords=[[]for _ in range(n)];node=1
    def emit(b,v):
        i=len(edges);edges.append(dict(id=i,u=at[b],v=v,bank=b,one_coordinate_tableau=pend[b].tab,one_coordinate_literal_circuit=pend[b].circuit,extra_global_phase_exponent_by_f_mod4=phase[b],source_event_ordinals=ords[b],rank_per_f=a.rank(x for x,z,p in pend[b].tab[m:])))
        paths[owner[b]].append(i);at[b]=v;pend[b]=a.ce.ident(m);phase[b]=(0,)*4;ords[b]=[]
    for t,e in enumerate(E):
        if e['kind']=='ADD':
            i,j=e['dst'],e['src'];emit(i,node);emit(j,node);node+=1
            if t in crosses:owner[i],owner[j]=owner[j],owner[i]
        elif e['kind']=='BANK_SWAP':
            i,j=e['banks']
            for v in(at,owner,pend,phase,ords):v[i],v[j]=v[j],v[i]
        elif e['kind']!='SCALE':
            op=a.independent.op_of(json.dumps(e['one_coordinate_literal_circuit']),m)
            a.need(op.tab==tuple(tuple(t)for t in e['one_coordinate_tableau']),'actual unary signed tableau')
            rank=a.rank(x for x,z,p in op.tab[m:]);a.need(rank==e['rank_per_f'] and (e['kind']=='NATIVE')==bool(rank),'actual native rank and event kind')
            b=e['bank'];pend[b]=pend[b].then(op);ords[b]=ords[b]+[t];ex=e.get('extra_global_phase_exponent_by_f_mod4',[(e.get('phase_exponent',0)*(1-r))%4 for r in range(4)]);phase[b]=tuple((x+y)%4 for x,y in zip(phase[b],ex))
    for b in range(n):emit(b,0)
    a.need(a.stable(edges)==a.stable(f['edges']),'entire independently rebuilt fixed source graph')
    a.need(node==f['graph_nodes'],'actual graph node count')
    partition(edges,paths)
    physical=direct(E,n,m,crosses);ranks=[];primitives={}
    for label,(path,saved)in enumerate(zip(paths,f['trajectories'])):
        a.need(saved['initial_bank']==label and saved['edges']==path,'saved path binds actual crossing choices')
        vertex=0;op=a.ce.ident(m);ph=(0,)*4;source_ords=[]
        for i in path:
            edge=edges[i];a.need(edge['u']==vertex,'path vertex incidence');vertex=edge['v'];op=op.then(a.independent.op_of(json.dumps(edge['one_coordinate_literal_circuit']),m));ph=tuple((x+y)%4 for x,y in zip(ph,edge['extra_global_phase_exponent_by_f_mod4']));source_ords+=edge['source_event_ordinals']
        a.need(vertex==0,'path physical Z boundary');bank,expected,ep=physical[label]
        a.need(op.tab==expected.tab and a.stable(op.circuit)==a.stable(expected.circuit)and ph==ep and saved['final_bank']==bank,'independent direct crossed-strand literal/phase/endpoint replay')
        a.need(a.stable(op.circuit)==a.stable(saved['one_coordinate_literal_circuit'])and a.stable(op.tab)==a.stable(saved['one_coordinate_tableau'])and list(ph)==saved['extra_global_phase_exponent_by_f_mod4']and source_ords==saved['source_unary_event_ordinals'],'all saved holonomy metadata bound')
        a.need(a.stable(op.adjoint().circuit)==a.stable(saved['literal_inverse_circuit'])and saved['inverse_extra_global_phase_exponent_by_f_mod4']==[(-x)%4 for x in ph],'actual literal inverse and tensor phase')
        rank=a.rank(x for x,z,p in op.tab[m:]);a.need(rank==saved['native_arity_per_f'],'actual holonomy rank');ranks.append(rank)
        for gate in op.circuit:primitives[a.stable(gate)]=gate
    for gate in primitives.values():
        g=a.independent.op_of(json.dumps([gate]),m)
        for pair in(g.then(g.adjoint()),g.adjoint().then(g)):
            a.need(pair.tab==a.ce.identity(m),'primitive inverse signed tableau');col,den=a.independent.b.sparse_column(pair);a.need(col=={0:(1,0)}and den==0,'primitive inverse exact Gaussian phase')
    a.need(len(primitives)==f['primitive_exact_Gaussian_inverse_checks'],'actual primitive coverage count')
    J=a.embed(source['J_four_axes'],m);a.need(a.eq(J@J,a.scalar(m,2))and a.native(J)==1,'odd kernel whole-field skew phase/rank')
    a.need(a.eq(J,a.qc.decode({'x_monomial':f['J']},m))and f['kernel_native_arity_per_f']==1,'saved embedded kernel metadata')
    parent=a.native(a.F(m,2*q+1)@J);a.need(parent==m-1==f['parent_arity_per_f']==raw['parent_arity'],'actual changed parent versus ambient')
    parent_op,_=a.independent.to_op(a.oldexpr(a.F(m,2*q+1)@J));a.need(a.rank(x for x,z,p in parent_op.tab[m:])==parent,'literal physical target B-rank versus ambient')
    mass=sum(e['rank_per_f']for e in E if e['kind']=='NATIVE');a.need(ranks==f['path_ranks_per_f']and sum(ranks)==mass==n*parent==f['stock']==f['admitted_floor_per_f'],'sharp fixed-graph stock floor')
    a.need(mass==raw['mass']==raw['optimistic_stock']==f['source_native_mass'],'source invoice metadata matches actual native ranks')
    straight=sum(a.rank(x for x,z,p in op.tab[m:])for bank,op,ph in direct(E,n,m,set()));a.need(straight==f['negative_controls']['straight_floor_below_stock']and straight<mass,'all-straight control below required floor')
    bad=a.ce.Op(m,a.ce.identity(m),[('phase',1)]);col,den=a.independent.b.sparse_column(bad);a.need(bad.tab==a.ce.identity(m)and(col!={0:(1,0)}or den!=0),'global-i mutant rejected beyond tableau')
    wrong=[list(p)for p in paths];wrong[0]=wrong[0][1:]
    try:partition(edges,wrong)
    except ValueError as ex:a.need('every edge exactly once'==str(ex),'specific omitted-edge control rejection')
    else:raise ValueError('omitted path edge accepted')
    swap_at=f['negative_controls']['wrong_actual_SWAP_rejected'];a.need(E[swap_at]['kind']=='BANK_SWAP','actual swap defect control bound')
    altered=direct(E,n,m,crosses,omit_swap=swap_at)
    a.need(any(x[0]!=y[0]or a.stable(x[1].circuit)!=a.stable(y[1].circuit)or x[1].tab!=y[1].tab or x[2]!=y[2]for x,y in zip(physical,altered)),'omitted actual SWAP changes independent literal trajectory')
    a.need(not a.eq(a.scalar(m,1)@J@a.scalar(m,1)@J,a.scalar(m,2)),'incorrect whole-field kernel normalization rejected')
    return dict(q=q,banks=n,ambient=m,parent=parent,kernel_arity=1,mask=str(mask),path_ranks=ranks,floor=sum(ranks),source_mass=mass,stock=n*parent,straight_floor=straight,edges=len(edges),primitive_inverse_pairs=len(primitives),all_f_phases_bound=True,exact_partition=True)
def run():
    a.need(a.sha(SOURCE/'MANIFEST.json')=='0104ff73b8108a520e17269fb4219d930083e09024bfec0569fc8da6e54db705','assigned frozen odd manifest')
    for x in json.loads((SOURCE/'MANIFEST.json').read_text())['files']:a.need(a.sha(SOURCE/x['path'])==x['sha256'],'frozen odd source '+x['path'])
    raw=json.loads((R/'general-clifford-retiming/kernel-search/EXACT-FIXTURES.json').read_text())['fixtures'];cert=json.loads((SOURCE/'ODD-FRAME-CERTIFICATES.json').read_text());out=[]
    for f in cert['fixtures']:out.append(check(f,next(x for x in raw if x['kernel']=='odd_rankone_involution'and x['isolated']['q']==f['q'])))
    return dict(status='PASS_INDEPENDENT_ODD_KERNEL_SHARP_TRAJECTORY_REVIEW',fixtures=out,no_new_kappa=True,scope='Two finite q words, all f, fixed unary/common-frame graph and Z boundaries; general Clifford gauges may mix tensor coordinates. Native rank tariff, not selected-native or owner/volume admission.')
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');args=p.parse_args();out=json.loads(json.dumps(run()));dest=HERE/'AUDIT.json'
    if args.write:dest.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    else:a.need(json.loads(dest.read_text())==out,'saved odd-kernel independent audit')
    print(out['status']);print([(f['q'],f['parent'],f['floor'],f['path_ranks'])for f in out['fixtures']])
