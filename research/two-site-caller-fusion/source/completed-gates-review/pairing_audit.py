#!/usr/bin/env python3
"""Independent crossed-strand admission of four finite ADD-pairing witnesses.
Apache-2.0; substantial OpenAI Codex assistance. No search is performed.
"""
from pathlib import Path
import argparse,copy,json,sys,types
sys.dont_write_bytecode=True
_source=Path(__file__).resolve().parent/'audit_gates.py';a=types.ModuleType('audit_gates');a.__file__=str(_source);sys.modules['audit_gates']=a
exec(compile(_source.read_bytes(),str(_source),'exec',dont_inherit=True,optimize=0),a.__dict__)
HERE=Path(__file__).resolve().parent;SOURCE=a.R/'trajectory-pairing-search'
def check(name,q):
    proposal_path=SOURCE/f'{name}-Q{q}-PROPOSAL.json';p=json.loads(proposal_path.read_text())
    for path,h in p['source_pins'].items():a.need(a.sha(path)==h,'pairing proposal source pin')
    relative='inputs/REPAIRED-SIMPLIFIED.json' if name=='REPAIRED' else 'inputs/ADMITTED-TWO-SITE.json'
    fixture=next(x for x in json.loads((a.T/relative).read_text())['fixtures'] if x['q']==q)
    E=fixture.get('full_events',fixture['events']);n,m=fixture['banks'],fixture['ambient_arity']
    actual_adds=[i for i,e in enumerate(E) if e['kind']=='ADD'];a.need(actual_adds==p['ADD_event_ordinals'],'all actual ADD ordinals bound')
    mask=int(p['mask']);a.need(mask>=0 and mask<(1<<len(actual_adds)),'pairing mask range')
    crosses={i for bit,i in enumerate(actual_adds)if mask>>bit&1}
    a.need(sorted(crosses)==p['crossing_ADD_event_ordinals'],'mask and explicit crossing list agree')
    at=[0]*n;owner=list(range(n));pending=[a.ce.ident(m)for _ in range(n)];extra=[(0,)*4 for _ in range(n)];ordinals=[[]for _ in range(n)]
    paths=[[]for _ in range(n)];edges=[];node=1
    # Separate direct traversal has no graph nodes/edges.
    direct_labels=list(range(n));direct_ops=[a.ce.ident(m)for _ in range(n)];direct_phase=[(0,)*4 for _ in range(n)]
    def emit(b,dst):
        i=len(edges);edges.append(dict(id=i,u=at[b],v=dst,bank=b,source_event_ordinals=ordinals[b],one_coordinate_literal_circuit=pending[b].circuit,one_coordinate_tableau=pending[b].tab,extra_global_phase_exponent_by_f_mod4=extra[b],rank_per_f=a.rank(x for x,z,p in pending[b].tab[m:])))
        paths[owner[b]].append(i);at[b]=dst;pending[b]=a.ce.ident(m);extra[b]=(0,)*4;ordinals[b]=[]
    def swap_lists(i,j,lists):
        for x in lists:x[i],x[j]=x[j],x[i]
    for ordinal,e in enumerate(E):
        if e['kind']=='ADD':
            i,j=e['dst'],e['src'];emit(i,node);emit(j,node);node+=1
            if ordinal in crosses:
                owner[i],owner[j]=owner[j],owner[i]
                swap_lists(i,j,[direct_labels,direct_ops,direct_phase])
        elif e['kind']=='BANK_SWAP':
            i,j=e['banks'];swap_lists(i,j,[at,owner,pending,extra,ordinals,direct_labels,direct_ops,direct_phase])
        elif e['kind']=='SCALE':pass
        else:
            b=e['bank'];op=a.independent.op_of(json.dumps(e['one_coordinate_literal_circuit']),m)
            a.need(op.tab==tuple(tuple(x)for x in e['one_coordinate_tableau']),'pairing actual unary tableau')
            a.need(a.rank(x for x,z,p in op.tab[m:])==e['rank_per_f'],'pairing actual unary B rank')
            ex=e.get('extra_global_phase_exponent_by_f_mod4',[(e.get('phase_exponent',0)*(1-r))%4 for r in range(4)])
            pending[b]=pending[b].then(op);extra[b]=tuple((x+y)%4 for x,y in zip(extra[b],ex));ordinals[b]=ordinals[b]+[ordinal]
            direct_ops[b]=direct_ops[b].then(op);direct_phase[b]=tuple((x+y)%4 for x,y in zip(direct_phase[b],ex))
    for b in range(n):emit(b,0)
    old_family='REPAIRED-SIMPLIFIED'if name=='REPAIRED'else'ADMITTED-TWO-SITE'
    old=next(x for x in json.loads((a.T/'TRAJECTORY-CERTIFICATES.json').read_text())['fixtures']if x['family']==old_family and x['q']==q)
    a.need(a.stable(edges)==a.stable(old['edges']),'crossing leaves the exact source unary graph unchanged')
    a.need(sorted(i for path in paths for i in path)==list(range(len(edges))),'crossed paths edge-disjoint and exhaustive')
    holonomies=[]
    for label,path in enumerate(paths):
        vertex=0;op=a.ce.ident(m);ex=(0,)*4
        for i in path:
            edge=edges[i];a.need(edge['u']==vertex,'crossed path consecutive vertices');vertex=edge['v']
            op=op.then(a.independent.op_of(json.dumps(edge['one_coordinate_literal_circuit']),m));ex=tuple((x+y)%4 for x,y in zip(ex,edge['extra_global_phase_exponent_by_f_mod4']))
        a.need(vertex==0,'crossed path fixed boundary')
        bank=direct_labels.index(label)
        a.need(a.stable(op.circuit)==a.stable(direct_ops[bank].circuit) and op.tab==direct_ops[bank].tab and ex==direct_phase[bank],'independent crossed strand operator and all-f phase traversal')
        r=a.rank(x for x,z,p in op.tab[m:]);a.need(r==m,'each finite crossed holonomy has full ambient rank')
        holonomies.append(dict(initial_label=label,final_bank=bank,path=path,rank_per_f=r,one_coordinate_tableau=op.tab,one_coordinate_literal_circuit=op.circuit,extra_global_phase_exponent_by_f_mod4=ex))
    floor=sum(h['rank_per_f']for h in holonomies);stock=n*fixture.get('parent_arity',m)
    a.need(floor==stock==p['best_floor']==p['goal'],'new exact stock floor')
    admitted_path=SOURCE/'FULL-STOCK-CERTIFICATES.json';admitted=json.loads(admitted_path.read_text())
    auth=next(x for x in admitted['fixtures']if x['family']==name and x['q']==q)
    a.need(auth['pairing_mask_decimal']==str(mask) and a.stable(auth['edges'])==a.stable(edges),'author admitted witness equals independently rebuilt graph/mask')
    a.need(auth['source_sha256']==a.sha(a.T/relative) and auth['source_events_sha256']==__import__('hashlib').sha256(a.stable(E).encode()).hexdigest(),'author admitted source/event pins')
    for h,ah in zip(holonomies,auth['trajectories']):
        for key,akey in [('initial_label','initial_bank'),('final_bank','final_bank'),('path','edges'),('rank_per_f','native_holonomy_arity_per_f'),('one_coordinate_tableau','one_coordinate_tableau'),('one_coordinate_literal_circuit','one_coordinate_literal_circuit'),('extra_global_phase_exponent_by_f_mod4','extra_global_phase_exponent_by_f_mod4')]:
            a.need(a.stable(h[key])==a.stable(ah[akey]),'author admitted literal crossed holonomy field '+key)
        op=a.independent.op_of(json.dumps(h['one_coordinate_literal_circuit']),m)
        a.need(a.stable(op.adjoint().circuit)==a.stable(ah['literal_inverse_circuit']) and ah['inverse_extra_global_phase_exponent_by_f_mod4']==[(-x)%4 for x in h['extra_global_phase_exponent_by_f_mod4']],'author admitted literal inverse and all-f phase')
        a.need(ah['source_unary_event_ordinals']==[ordinal for eid in h['path']for ordinal in edges[eid]['source_event_ordinals']],'ordered source unary chronology on each path')
    # A changed pairing is a different proposed witness. It must not be accepted
    # against the saved paths/circuits merely because a rank score might tie.
    bad_crosses=crosses^{actual_adds[0]};bl=list(range(n));bo=[a.ce.ident(m)for _ in range(n)];bp=[(0,)*4 for _ in range(n)]
    for ordinal,e in enumerate(E):
        if e['kind']=='BANK_SWAP':swap_lists(*e['banks'],[bl,bo,bp])
        elif e['kind']=='ADD' and ordinal in bad_crosses:swap_lists(e['dst'],e['src'],[bl,bo,bp])
        elif e['kind'] not in ('ADD','SCALE'):
            b=e['bank'];op=a.independent.op_of(json.dumps(e['one_coordinate_literal_circuit']),m);bo[b]=bo[b].then(op)
            ex=e.get('extra_global_phase_exponent_by_f_mod4',[(e.get('phase_exponent',0)*(1-r))%4 for r in range(4)])
            bp[b]=tuple((x+y)%4 for x,y in zip(bp[b],ex))
    a.need(any(bl.index(h['initial_label'])!=h['final_bank'] or a.stable(bo[bl.index(h['initial_label'])].circuit)!=a.stable(h['one_coordinate_literal_circuit']) or list(bp[bl.index(h['initial_label'])])!=list(h['extra_global_phase_exponent_by_f_mod4'])for h in holonomies),'one-bit wrong routing rejected by actual saved holonomy witness')
    return dict(family=name,q=q,banks=n,ambient_arity=m,stock=stock,floor=floor,source_mass=fixture.get('mass',fixture.get('native_mass')),mask=str(mask),crossing_ADD_event_ordinals=sorted(crosses),edges=edges,holonomies=holonomies,proposal_sha256=a.sha(proposal_path),admitted_certificate_sha256=a.sha(admitted_path),source_sha256=a.sha(a.T/relative),every_edge_once=True,exact_circuits_and_all_f_phases=True,wrong_routing_control=True,no_all_q_extrapolation=True)
def main():
    p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');args=p.parse_args()
    out=dict(status='PASS_INDEPENDENT_CROSSED_PAIRING_ADMISSION',fixtures=[check(name,q)for name in('REPAIRED','TWO-SITE')for q in(2,3)],no_new_kappa=True,model='Fixed source unary graph, every ADD common-frame node, fixed physical Z boundaries, all positive f and arbitrary Clifford frame gauges.',scope='Exact finite witnesses; source masses80/136 and76/132 not proved optimal. No search or same-function-word/global obstruction.')
    out=json.loads(json.dumps(out));dest=HERE/'PAIRING-AUDIT.json'
    if args.write:dest.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    else:a.need(json.loads(dest.read_text())==out,'saved independent pairing audit')
    print(out['status']);print([(x['family'],x['q'],x['floor'])for x in out['fixtures']])
if __name__=='__main__':main()
