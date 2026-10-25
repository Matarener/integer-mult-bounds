#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Data-only reverse-liveness oracle for PR3423's external-port interface.

Imports no predecessor code. This computes least literal read/write ancestor
closures, not cancellation-minimized semantic dependencies. C erasure obligations
are closed to a fixed point, including all restoration predecessors.
"""
import argparse
from collections import Counter
from fractions import Fraction
import hashlib
import json
from pathlib import Path

DEFAULT=Path(__file__).resolve().parents[2]/'research/p104-rounded-collector/inputs/WORD.json'
WORD_SHA='cec1fb3fbd0067b500ad5119a62ba60685be718e769374d7ec8abdd2beaa7e50'
Y={f'Y{i}' for i in [*range(22,33),*range(63,104)]}
INTERNAL=Y|{f'{c}{i}' for c in ('D','G') for i in range(27,32)}|{'Q7'}

def must(ok,label):
    if not ok:raise ValueError(label)

def digest(obj):
    return hashlib.sha256(json.dumps(obj,sort_keys=True,separators=(',',':')).encode()).hexdigest()

def hist(names):
    return dict(sorted(Counter(n.rstrip('0123456789') for n in names).items()))

def newton(values):
    values=[(Fraction(a),Fraction(b)) for a,b in values]
    for j in range(9):
        for x in range(512):
            if x & (1<<j):
                a,b=values[x];c,d=values[x^(1<<j)];values[x]=(a-c,b-d)
    for x,(a,b) in enumerate(values):
        for _ in range(x.bit_count()):a,b=(a+b)/2,(b-a)/2
        values[x]=(a,b)
    return values

def run(path):
    raw=path.read_bytes();must(hashlib.sha256(raw).hexdigest()==WORD_SHA,'source pin')
    word=json.loads(raw);program=word['program']
    frames={r:tuple(f) for r,f in word['initial_frames'].items()};fh={};live={};lifetimes=[];ports=[]
    for i,e in enumerate(program):
        op,dst=e[:2]
        if op=='zero':
            must(dst not in frames,'fresh private lifetime')
            before=None;frames[dst]=tuple(e[2]);live[dst]=i
        elif op=='erase':
            must(dst in live and frames[dst]==tuple(e[2]),'private erase frame')
            before=frames.pop(dst);lifetimes.append((live.pop(dst),i,dst))
        else:
            must(dst in frames,'bound target');before=frames[dst]
            if op=='transport':
                must(before==tuple(e[2]),'transport preframe');frames[dst]=tuple(e[3])
            elif op=='sign':must(before==tuple(e[3]),'sign frame')
            elif op=='add':must(before==frames[e[2]]==tuple(e[4]),'ADD frame')
            else:raise ValueError('unsupported opcode')
        fh[i]={'event':i,'before':None if before is None else list(before),'after':None if dst not in frames else list(frames[dst])}
        if i<=4516 and op=='add' and e[2] in INTERNAL and dst not in INTERNAL and dst!='C':
            ports.append({'event':i,'target':dst,'source':e[2],'coefficient':str(e[3]),'frame':e[4]})
    must(not live,'open private lifetime');must(frames=={r:tuple(f) for r,f in word['final_frames'].items()},'final frames')
    must(len(ports)==675,'port census');recipients={p['target'] for p in ports}

    def backward(final,goals,forced_erases):
        needed=set(final);events=set()
        for i in range(len(program)-1,-1,-1):
            e=program[i];op,dst=e[:2]
            if i in goals:needed.add(goals[i])
            if i in forced_erases:needed.add(dst)
            if dst not in needed:continue
            if op=='erase':
                must(i in forced_erases,'value dependency crosses a dead lifetime')
                events.add(i)
                continue
            events.add(i)
            if op=='add':needed.add(e[2])
            if op=='zero':needed.remove(dst)
        return sorted(needed),sorted(events)

    def report(final,goals):
        initial,rawids=backward(final,goals,set());forced=set();last=None;steps=0
        # Force every touched private lifetime's erasure and all its value ancestors.
        ids=rawids
        while last!=forced:
            last=set(forced)
            for start,end,role in lifetimes:
                if any(start<=i<=end and (program[i][1]==role or
                    (program[i][0]=='add' and program[i][2]==role)) for i in ids):
                    forced.add(end)
            initial2,ids=backward(final,goals,forced);steps+=1
        names=sorted(initial2);extra=sorted(set(names)-INTERNAL)
        selected_lifetimes=[{'zero':a,'erase':b,'role':r} for a,b,r in lifetimes if b in forced]
        def block(events):
            return {'count':len(events),'opcodes':dict(sorted(Counter(program[i][0] for i in events).items())),
                    'event_ids':events,'event_ids_sha256':digest(events),
                    'frame_history_sha256':digest([fh[i] for i in events])}
        return {'value_only':block(rawids),'lifecycle_closed':block(ids),
                'value_initial_roles':initial,'value_initial_count':len(initial),
                'initial_roles':names,'initial_count':len(names),'initial_by_role':hist(names),
                'initial_roles_sha256':digest(names),'additional_initial_roles':extra,
                'additional_initial_count':len(extra),'additional_initial_by_role':hist(extra),
                'private_lifetimes':selected_lifetimes,'lifecycle_added_event_ids':sorted(set(ids)-set(rawids)),
                'fixed_point_scans':steps}
    cut=report(set(),{p['event']:p['target'] for p in ports})
    end=report(recipients|INTERNAL,{})
    # Every borrowed initial bank acquires its original terminal-history
    # obligation. This is a projection onto those endpoints, not an assertion
    # that the projected program preserves updates to excluded banks.
    terminal=recipients|INTERNAL;history_rounds=[]
    while True:
        history=report(terminal,{})
        added=set(history['initial_roles'])-terminal
        history_rounds.append({
            'terminal_count':len(terminal),'terminal_roles':sorted(terminal),
            'initial_count':history['initial_count'],
            'value_only_events':history['value_only']['count'],
            'lifecycle_closed_events':history['lifecycle_closed']['count'],
            'additional_terminal_roles':sorted(added),
            'event_ids_sha256':history['lifecycle_closed']['event_ids_sha256']})
        if not added:break
        terminal.update(added)
    history['terminal_roles']=sorted(terminal)
    history['terminal_count']=len(terminal)
    history['history_rounds']=history_rounds
    excluded=sorted(set(word['initial_frames'])-terminal)
    history['excluded_initial_roles']=excluded
    history['excluded_initial_count']=len(excluded)
    history['excluded_initial_by_role']=hist(excluded)
    retained=set(history['lifecycle_closed']['event_ids'])
    omitted_outgoing=[{'event':i,'operation':e} for i,e in enumerate(program)
                      if i not in retained and e[0]=='add' and e[2] in terminal
                      and e[1] not in terminal]
    outgoing_targets=sorted({x['operation'][1] for x in omitted_outgoing})
    history['omitted_outgoing_adds']={
        'count':len(omitted_outgoing),'events':omitted_outgoing,
        'events_sha256':digest(omitted_outgoing),
        'source_by_role':hist([x['operation'][2] for x in omitted_outgoing]),
        'target_by_role':hist([x['operation'][1] for x in omitted_outgoing]),
        'target_roles':outgoing_targets,'target_count':len(outgoing_targets),
        'target_bank_by_role':hist(outgoing_targets)}
    earliest=[{'event':i,'operation':program[i]} for i in cut['value_only']['event_ids']
              if program[i][0]=='add' and program[i][1] in recipients and program[i][2] not in INTERNAL]
    # Reachable exact-half counterexample: every other initial bank is zero.
    must(word['initial_frames']['N100']==[],'N100 entry frame')
    contacts=[i for i,e in enumerate(program) if e[1]=='N100' or (e[0]=='add' and e[2]=='N100')]
    must(contacts[0]==312 and program[312]==['add','X100','N100','1/2',[]],'N100 first contact')
    witness=[]
    for amplitude in (2,4):
        src=[(amplitude*(x&1),0) for x in range(512)]
        out=[(a//2,b//2) for a,b in src]
        sc=newton(src);oc=newton(out)
        must(all(z.denominator==1 for pair in sc for z in pair),'source Newton membership')
        failure=[i for i,pair in enumerate(oc) if any(z.denominator!=1 for z in pair)]
        must(bool(failure)==(amplitude==2),'counterexample/positive control')
        witness.append({'amplitude':amplitude,'source_newton_coefficient_1':[str(z) for z in sc[1]],
                        'output_newton_coefficient_1':[str(z) for z in oc[1]],'output_bad_indices':failure,
                        'half_arithmetic_exact':all(a%2==b%2==0 for a,b in src)})
    return {'status':'PASS_INDEPENDENT_REVERSE_PORT_DEPENDENCY_CLOSURE','word_sha256':WORD_SHA,
            'word_events':len(program),'initial_word_banks':len(word['initial_frames']),
            'internal_banks':len(INTERNAL),'outgoing_ports':len(ports),'outgoing_ports_sha256':digest(ports),
            'recipient_banks':len(recipients),'recipient_by_role':hist(recipients),'recipients':sorted(recipients),
            'port_cuts':cut,'final_endpoints':end,'history_complete':history,
            'first_added_incoming_events':earliest[:12],
            'N100_exact_half_control':witness,
            'scope':'Least literal read/write dependency closures, including private lifetime restoration and a fixed point of original endpoint-history obligations. These are projections; omitted outgoing side effects are not preserved. Not a minimum modulo cancellation, native semantic replay, width invoice, or supplier admission.'}

def main():
    p=argparse.ArgumentParser();p.add_argument('--word',type=Path,default=DEFAULT);p.add_argument('--full',action='store_true');a=p.parse_args();d=run(a.word)
    if not a.full:
        for label in ('port_cuts','final_endpoints','history_complete'):
            for part in ('value_only','lifecycle_closed'):del d[label][part]['event_ids']
    print(json.dumps(d,sort_keys=True,indent=2))
if __name__=='__main__':main()
