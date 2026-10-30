#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Literal P104 recipient join, conditional on native covariance/B9 invariance.

Hiroki Kumazaki with substantial OpenAI Codex assistance. No predecessor imports.
"""
import argparse
from collections import Counter
from copy import deepcopy
from fractions import Fraction
import gzip
import hashlib
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WORD = 'research/p104-rounded-collector/inputs/WORD.json'
NATIVE = 'research/p104-rounded-collector/inputs/NATIVE.json.gz'
ROLES = set(['Y'+str(i) for i in (*range(22,33),*range(63,104))] +
            ['D'+str(i) for i in range(27,32)] + ['G'+str(i) for i in range(27,32)] + ['Q7'])


def need(ok, message):
    if not ok:
        raise ValueError(message)


def unique(pairs):
    d = dict(pairs)
    need(len(d) == len(pairs), 'duplicate JSON key')
    return d


def read(p):
    b = p.read_bytes()
    return json.loads(gzip.decompress(b) if p.suffix == '.gz' else b, object_pairs_hook=unique)


def canonical(x):
    return json.dumps(x,sort_keys=True,separators=(',',':')).encode()


def digest(x):
    return hashlib.sha256(canonical(x)).hexdigest()


def add(a,b,c):
    out = dict(a)
    for k,v in b.items():
        out[k] = out.get(k,Fraction())+c*v
        if not out[k]:
            del out[k]
    return out


def row_json(r):
    return {k:str(v) for k,v in sorted(r.items())}


def dyadic_bits(q):
    d = q.denominator
    need(d & (d-1) == 0, 'non-dyadic coefficient')
    return d.bit_length()-1


def build(word, native):
    """Build state-version DAG while propagating exact normalized scalar rows."""
    frames={k:tuple(v) for k,v in word['initial_frames'].items()}
    initial=sorted(frames)
    node={k:-i-1 for i,k in enumerate(initial)}
    rows={node[k]:{k:Fraction(1)} for k in initial}
    deps={node[k]:() for k in initial}
    owners={node[k]:k for k in initial}
    records={}
    lifetime={}
    pairs={}
    occurrences={}
    for rec in native['transports']:
        for i in rec['events']:
            need(i not in occurrences,'duplicate native occurrence')
            occurrences[i]=rec
    need(word['chart']==native['chart'],'native chart binding')
    for i,op in enumerate(word['program']):
        kind,dst=op[:2]
        if kind=='zero':
            need(dst not in node,'private allocation aliases live bank')
            node[dst]=i; frames[dst]=tuple(op[2]); rows[i]={};deps[i]=()
            lifetime[dst]=i
        else:
            need(dst in node,'unknown target')
            before=node[dst]
            if kind=='transport':
                need(frames[dst]==tuple(op[2]),'old frame mismatch')
                rec=occurrences[i]
                need(rec['old']==op[2] and rec['new']==op[3] and rec['recipe']['rank']==op[4], 'native occurrence binding')
                frames[dst]=tuple(op[3]);deps[i]=(before,);rows[i]=dict(rows[before])
            elif kind=='sign':
                need(frames[dst]==tuple(op[3]) and Fraction(op[2])==-1,'sign frame/coefficient')
                deps[i]=(before,);rows[i]={k:-v for k,v in rows[before].items()}
            elif kind=='add':
                src=op[2];need(src in node,'unknown source')
                need(frames[dst]==frames[src]==tuple(op[4]),'unequal ADD frames')
                c=Fraction(op[3]);need(c!=0,'zero ADD')
                deps[i]=(before,node[src]);rows[i]=add(rows[before],rows[node[src]],c)
                records[i]={'event':i,'target':dst,'source':src,'coefficient':str(c),'frame':op[4],
                            'before':before,'source_version':node[src]}
            elif kind=='erase':
                need(dst in lifetime and frames[dst]==tuple(op[2]),'private erasure lifetime/frame')
                need(not rows[before],'nonzero private erasure')
                deps[i]=(before,);rows[i]={};pairs[lifetime.pop(dst)]=i
                del node[dst];del frames[dst]
            else:
                raise ValueError('unknown opcode')
            if kind!='erase':node[dst]=i
        owners[i]=dst
    need(not lifetime,'unclosed private lifetime')
    need(frames=={k:tuple(v) for k,v in word['final_frames'].items()},'terminal frames')
    need(set(occurrences)=={i for i,o in enumerate(word['program']) if o[0]=='transport'},'complete native occurrence set')
    return {'deps':deps,'rows':rows,'owners':owners,'records':records,'pairs':pairs,'final':node,'initial':initial}


def ancestors(dag,seeds):
    seen=set(); stack=list(seeds)
    while stack:
        i=stack.pop()
        if i in seen:continue
        need(i in dag['deps'],'unknown state version')
        seen.add(i);stack.extend(dag['deps'][i])
    return seen


def close(dag,seeds):
    result=ancestors(dag,seeds)
    while True:
        erases={end for start,end in dag['pairs'].items() if start in result}
        new=ancestors(dag,result|erases)
        if new==result:return result
        result=new


def require_closed(dag,selected,seeds):
    need(set(seeds)<=selected,'missing observation')
    for i in selected:need(set(dag['deps'][i])<=selected,'missing actual dependency')
    for start,end in dag['pairs'].items():
        if start in selected:need(end in selected,'missing private cleanup')


def evaluate_slice(word, dag, selected, values):
    """One independent scalar fixture through the projected literal program."""
    state={k:Fraction(values[k]) for i,k in enumerate(dag['initial']) if -i-1 in selected}
    for i,o in enumerate(word['program']):
        if i not in selected:continue
        kind,dst=o[:2]
        if kind=='zero':state[dst]=Fraction()
        elif kind=='add':state[dst]+=Fraction(o[3])*state[o[2]]
        elif kind=='sign':state[dst]=-state[dst]
        elif kind=='erase':need(state.pop(dst)==0,'fixture private dirt')
        elif kind!='transport':raise ValueError('fixture opcode')
    return state


def profile(word,dag,selected):
    initials=sorted(dag['owners'][i] for i in selected if i<0)
    bits={k:0 for k in initials}; witness={}
    maximum=(Fraction(-1),-1)
    for i in sorted(selected):
        row=dag['rows'][i]
        norm=sum(map(abs,row.values()),Fraction())
        if norm>maximum[0]:maximum=(norm,i)
        for k,v in row.items():
            b=dyadic_bits(v)
            if b>bits[k]:bits[k]=b;witness[k]={'event':i,'coefficient':str(v)}
    return {'initial_inputs':initials,'initial_scale_bits':bits,'scale_witnesses':witness,
            'events':sorted(i for i in selected if i>=0),
            'op_counts':dict(sorted(Counter(word['program'][i][0] for i in selected if i>=0).items())),
            'max_row_l1':str(maximum[0]),'max_row_event':maximum[1],
            'component_bound_factor':str(32*maximum[0])}


def rational_rank(matrix):
    pivots={}
    for row in matrix:
        row=list(row)
        for i in range(len(row)):
            value=row[i]
            if not value:continue
            if i in pivots:row=[a-value*b for a,b in zip(row,pivots[i])]
            else:
                pivots[i]=[a/value for a in row];break
    return len(pivots)


def rank_witness(terminal_rows):
    names=['X1','X100','X103','X13','X14','X18','X19','X20','X22']
    columns=[1,2,14,3,7,4,5,33,22]
    basis=[[Fraction(terminal_rows[k].get('Y'+str(j),'0')) for j in range(104)] for k in names]
    square=[[row[j] for j in columns] for row in basis]
    aug=[row+[Fraction(i==j) for j in range(9)] for i,row in enumerate(square)]
    determinant=Fraction(1)
    for col in range(9):
        pivot=next((i for i in range(col,9) if aug[i][col]),None)
        need(pivot is not None,'singular rank witness')
        if pivot!=col:aug[pivot],aug[col]=aug[col],aug[pivot];determinant=-determinant
        value=aug[col][col];determinant*=value
        aug[col]=[v/value for v in aug[col]]
        for i in range(9):
            if i==col:continue
            value=aug[i][col]
            aug[i]=[a-value*b for a,b in zip(aug[i],aug[col])]
    inverse=[row[9:] for row in aug]
    need(determinant==Fraction(-1,128),'rank witness determinant')
    coefficients={}
    for name,row in terminal_rows.items():
        if not name.startswith('X'):continue
        target=[Fraction(row.get('Y'+str(j),'0')) for j in range(104)]
        coef=[sum((target[columns[k]]*inverse[k][j] for k in range(9)),Fraction()) for j in range(9)]
        need(all(sum((coef[k]*basis[k][j] for k in range(9)),Fraction())==target[j] for j in range(104)),
             'rank-nine full matrix factorization')
        coefficients[name]=[str(c) for c in coef]
    return {'basis_rows':names,'minor_Y_columns':columns,'minor_determinant':str(determinant),
            'coefficients':coefficients,'identity':'Every terminal X-to-Y row equals its nine coefficients times the nine named full Y rows.'}


def check_terminal(dag,terminal):
    for k in terminal:
        row=dag['rows'][dag['final'][k]]
        if k.startswith('X'):
            need(row.get(k)==1 and all(src==k or src.startswith('Y') for src in row),
                 'terminal dirty-input cancellation')
        else:need(row=={k:Fraction(1)},'terminal normalized restoration')


def audit(word,native):
    dag=build(word,native)
    ports=[i for i,o in enumerate(word['program']) if i<=4516 and o[0]=='add' and o[2] in ROLES and o[1] not in ROLES and o[1]!='C']
    need(len(ports)==675,'675 actual outgoing ports')
    need(digest(ports)=='04b3a0bc022c336c9b177eeed49036f1257ab81ea9d0459b8170075b002a24a4', 'PR3423 published port-index binding')
    targets={word['program'][i][1] for i in ports}
    terminal=sorted(targets|ROLES)
    port_set=close(dag,ports)
    end_seeds=[dag['final'][k] for k in terminal]
    end_set=close(dag,end_seeds)
    # Joining both sets is necessary: final cancellation must not drop port observations.
    joined=close(dag,ports+end_seeds)
    for s,seeds in ((port_set,ports),(end_set,end_seeds),(joined,ports+end_seeds)):
        require_closed(dag,s,seeds)
    p=profile(word,dag,joined)
    all_inputs=p['initial_inputs']
    returned=close(dag,ports+[dag['final'][k] for k in all_inputs])
    need({dag['owners'][i] for i in returned if i<0}==set(all_inputs),
         'terminal-history closure introduces new inputs')
    require_closed(dag,returned,ports+[dag['final'][k] for k in all_inputs])
    returned_profile=profile(word,dag,returned)
    need(returned_profile['initial_scale_bits']==p['initial_scale_bits'],'returned entrance contract changed')
    check_terminal(dag,all_inputs)
    terminal_rows={k:row_json(dag['rows'][dag['final'][k]]) for k in terminal}
    check_terminal(dag,terminal)
    scales=p['initial_scale_bits']
    for i in joined:
        for name,c in dag['rows'][i].items():
            need((c*2**scales[name]).denominator==1,'product entrance insufficient')
    # Each smaller independent dyadic factor has a reachable nonintegral coefficient.
    lower_controls=[]
    for name,b in scales.items():
        if not b:continue
        witness=p['scale_witnesses'][name]
        need((Fraction(witness['coefficient'])*2**(b-1)).denominator>1,
             'one-bit-lower admission was not rejected')
        lower_controls.append(name)
    matrix=[[Fraction(terminal_rows[k].get('Y'+str(j),'0')) for j in range(104)]
            for k in terminal if k.startswith('X')]
    matrix_rank=rational_rank(matrix)
    need(matrix_rank==9,'complete terminal Y-map rank')
    need(rational_rank([[Fraction(1),Fraction(1)],[Fraction(1),Fraction(1)]])==1,
         'duplicate-row rank control')
    need(rational_rank([[Fraction(x) for x in row] for row in [[1,2,3],[2,4,6],[0,1,1]]])==2,
         'dependent-row rank control')
    port_rows=[]
    for i in ports:
        rec=dag['records'][i]; before=dag['rows'][rec['before']]; after=dag['rows'][i]
        inc={k:Fraction(rec['coefficient'])*v for k,v in dag['rows'][rec['source_version']].items()}
        port_rows.append({k:v for k,v in rec.items() if k not in ('before','source_version')}|
                         {'before_row':row_json(before),'increment_row':row_json(inc),'after_row':row_json(after),
                          'before_l1':str(sum(map(abs,before.values()),Fraction())),
                          'after_l1':str(sum(map(abs,after.values()),Fraction()))})
    # Independent integer fixture execution checks actual slice/full joins; no native claim.
    all_nodes=set(dag['deps'])
    for seed in (0,17,73):
        values={k:((j*37+seed*11)%43-21)*(2**p['initial_scale_bits'].get(k,2)) for j,k in enumerate(dag['initial'])}
        sliced=evaluate_slice(word,dag,returned,values)
        full=evaluate_slice(word,dag,all_nodes,values)
        for k in all_inputs:
            expected=sum((v*values[src] for src,v in dag['rows'][dag['final'][k]].items()),Fraction())
            need(sliced[k]==full[k]==expected,'slice/full terminal fixture')
    result={'schema_version':1,'scope':'Conditional chart-normalized recipient closure; native covariance and B9 automorphisms inherited.',
            'ports':port_rows,'recipients':sorted(targets),'terminal_targets':terminal,
            'port_cut':profile(word,dag,port_set),'terminal_cut':profile(word,dag,end_set),'joined':p,
            'history_complete':returned_profile,
            'history_terminal_rows':{k:row_json(dag['rows'][dag['final'][k]]) for k in all_inputs},
            'history_terminal_frames':{k:word['final_frames'][k] for k in all_inputs},
            'terminal_rows':terminal_rows,'terminal_Y_matrix_rank':matrix_rank,'terminal_Y_rank_witness':rank_witness(terminal_rows),
            'one_bit_lower_admission_controls':lower_controls,'terminal_frames':{k:word['final_frames'][k] for k in terminal},
            'initial_frames':{k:word['initial_frames'][k] for k in p['initial_inputs']},
            'private_lifetimes':[[a,b] for a,b in dag['pairs'].items() if a in joined]}
    return result,dag,returned,ports,[dag['final'][k] for k in all_inputs]


def controls(word,native,dag,joined,ports,end_seeds):
    rejected=[]
    def fail(label,fn):
        try:fn()
        except (ValueError,KeyError):rejected.append(label)
        else:raise ValueError('accepted control '+label)
    fail('omit_actual_incoming_half_read',lambda:require_closed(dag,joined-{312},ports+end_seeds))
    start,end=next((a,b) for a,b in dag['pairs'].items() if a in joined)
    fail('omit_private_erasure',lambda:require_closed(dag,joined-{end},ports+end_seeds))
    wrong=deepcopy(word);wrong['program'][312][4]=[1]
    fail('wrong_recipient_frame',lambda:build(wrong,native))
    wrong=deepcopy(word);wrong['program'][2038][3]='1'
    fail('dirty_private_erase',lambda:build(wrong,native))
    wrong=deepcopy(word);wrong['program'][312][3]='1/4'
    fail('wrong_half_read_leaves_dirty_N100',lambda:check_terminal(build(wrong,native),['X100']))
    wrong=deepcopy(native);wrong['transports'][0]['recipe']['rank']+=1
    fail('native_rank_binding',lambda:build(word,wrong))
    need(word['program'][312]==['add','X100','N100','1/2',[]],'half-read witness source')
    derived=profile(word,dag,joined)['initial_scale_bits']
    weak=dict(derived);weak['N100']=0
    def validate_entrance(scales):
        for i in sorted(joined):
            for name,c in dag['rows'][i].items():
                need((c*2**scales[name]).denominator==1, 'admission failure at event '+str(i))
    validate_entrance(derived)
    fail('weak_N100_B9_in_actual_prefix',lambda:validate_entrance(weak))
    need(Fraction(1,2)*2==1,'strengthened half-read positive control')
    # Endpoint-correct omission is detected by retaining the observations themselves.
    fail('omit_observed_port',lambda:require_closed(dag,joined-{ports[0]},ports+end_seeds))
    return rejected


def summarize(result):
    payload=(json.dumps(result,sort_keys=True,indent=2)+'\n').encode()
    out={'status':'PASS_P104_EXTERNAL_PORT_CLOSURE',
         'certificate_payload_sha256':hashlib.sha256(payload).hexdigest(),
         'ports':len(result['ports']),'recipients':len(result['recipients'])}
    for tag in ('port_cut','terminal_cut','history_complete'):
        p=result[tag]
        out[tag]={'events':len(p['events']),'inputs':len(p['initial_inputs']),
                  'op_counts':p['op_counts'],'event_ids_sha256':digest(p['events']),
                  'max_row_l1':p['max_row_l1'],'max_row_event':p['max_row_event'],
                  'component_bound_factor':p['component_bound_factor']}
    out['initial_scale_bits']=result['history_complete']['initial_scale_bits']
    out['actual_recipient_counterexample']=result['independent_closure']['N100_exact_half_control']
    out['rejection_controls']=result['rejected_controls']
    out['one_bit_lower_controls']=len(result['one_bit_lower_admission_controls'])
    out['terminal_Y_rank']=result['terminal_Y_matrix_rank']
    out['terminal_Y_minor_determinant']=result['terminal_Y_rank_witness']['minor_determinant']
    omitted=result['omitted_outgoing_adds']
    out['omitted_outgoing_adds']={k:v for k,v in omitted.items() if k!='events'}
    out['omitted_outgoing_adds']['event_indices']=[a['event'] for a in omitted['events']]
    out['omitted_outgoing_adds']['first_two']=omitted['events'][:2]
    out['scope']='Literal endpoint projection and conditional normalized algebra/module admission. Native operator semantics, physical admission, omitted-bank effects and full supplier costs remain outside this check.'
    return out


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--emit',action='store_true');ap.add_argument('--summary',action='store_true');args=ap.parse_args()
    for ent in read(HERE/'SOURCES.json')['files']:
        if ent['usage']=='input':need(hashlib.sha256((ROOT/ent['path']).read_bytes()).hexdigest()==ent['sha256'],'source pin '+ent['path'])
    word,native=read(ROOT/WORD),read(ROOT/NATIVE)
    result,dag,joined,ports,end_seeds=audit(word,native)
    result['rejected_controls']=controls(word,native,dag,joined,ports,end_seeds)
    independent=json.loads(subprocess.check_output([sys.executable,'-I','-B',str(HERE/'oracle.py'),'--full'],text=True))
    for a,b in (('port_cut','port_cuts'),('terminal_cut','final_endpoints'),('history_complete','history_complete')):
        need(result[a]['events']==independent[b]['lifecycle_closed']['event_ids'],'SSA/reverse-liveness event sets')
        need(result[a]['initial_inputs']==independent[b]['initial_roles'],'SSA/reverse-liveness initial roles')
    result['independent_closure']={k:independent[k] for k in ('outgoing_ports_sha256','N100_exact_half_control')}
    result['independent_closure']['event_sets_and_initial_inputs_agree']=True
    inputs=set(result['history_complete']['initial_inputs'])
    omitted=[{'event':i,'operation':o} for i,o in enumerate(word['program'])
             if i not in joined and o[0]=='add' and o[2] in inputs and o[1] not in inputs]
    need(omitted==independent['history_complete']['omitted_outgoing_adds']['events'],
         'omitted outgoing effects agree')
    result['omitted_outgoing_adds']=independent['history_complete']['omitted_outgoing_adds']
    if args.summary:print(json.dumps(summarize(result),sort_keys=True,indent=2))
    elif args.emit:print(json.dumps(result,sort_keys=True,indent=2))
    else:
        need(result==read(HERE/'CERTIFICATE.json.gz'),'retained certificate mismatch')
        need(summarize(result)==read(HERE/'SUMMARY.json'),'retained summary mismatch')
        print('PASS_P104_EXTERNAL_PORT_CLOSURE',digest(result))


if __name__=='__main__':main()
