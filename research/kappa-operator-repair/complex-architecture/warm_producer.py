#!/usr/bin/env python3
"""Rebuild warm B-helper production after its early dirty observations.

SOURCE and all protected dirty rows are matched exactly. Only zero-entrance,
full-exit unwrapped helper columns may enter the separately checked TARGET
correction. This changes a later producer/observation boundary, not the
already-screened first A birth. Apache-2.0; substantial OpenAI assistance.
"""
from argparse import ArgumentParser
from collections import Counter
from copy import deepcopy
from fractions import Fraction as Q
from hashlib import sha256
import gzip
import json
from pathlib import Path
import sys
from time import monotonic
from matched_basis import ROOT,HERE,OLD,PREVIOUS,F,O,canonical,replay,expected
from exact_rows import execute,add,repair
from commute_birth import trace,FULL
sys.path.insert(0,str(PREVIOUS.parent))
from complex_projection_screen import combination


def setup(word):
    live=set(range(704))-set(word['removed'])
    allowed=set(range(224,704))-set(word['removed'])-set(map(int,word['start_extra']))-set(map(int,word['helper_final']))
    rows={r:{(r,()):Q(1)} if r not in allowed else {} for r in live}
    current={r:F.basis((word['ports'][r],)) if r<112 else F.basis(tuple(word['start_extra'].get(str(r),[]))) for r in live}
    for term in word['initial_corrections']:
        if term['source'] not in allowed:
            add(rows[term['target']],{(term['source'],tuple(term['operator_word'])):Q(1)},Q(term['coefficient']))
    for event in word['precondition']+word['compensation']:
        execute(rows,event)
    for event in word['A']:
        execute(rows,event)
        if event[0]=='warp':current[event[1]]=F.basis(tuple(event[4]))
        else:
            for r in F.regs(event):current[r]=F.basis(tuple(event[-1]))
    for r,frame in zip(word['centers'],word['center_frames']):current[r]=F.basis(tuple(frame))
    for t in range(112):current[112+t]=F.basis(tuple(word['target_levels'].get(str(t),[])))
    for event in word['cut']:execute(rows,event)
    return rows,current,allowed


def candidate(word, helper, position='last_write'):
    events=F.expand(word)['B']
    writes=[];observer=None
    for index,event in enumerate(events):
        if event[0]=='warp' and event[1]==helper:raise ValueError('wrapped_B_helper')
        if writes and event[0]=='add' and event[2]==helper:
            observer=index;break
        if event[1]==helper:
            writes.append(index)
    if len(writes)<2:raise ValueError('short_producer')
    if observer is None:raise ValueError('no_postproduction_observer')
    first=writes[0];end=writes[-1] if position=='last_write' else observer
    stop=end+1 if position=='last_write' else end
    frame=F.basis(tuple(events[end][-1]))
    rows,current,allowed=setup(word)
    retained=None;deleted=set(writes)
    for index,event in enumerate(events[:stop]):
        if index==first:retained=dict(rows[helper])
        execute(rows,event)
        if index in deleted:continue
        if event[0]=='warp':current[event[1]]=F.basis(tuple(event[4]))
        else:
            for r in F.regs(event):current[r]=F.basis(tuple(event[-1]))
    wanted=dict(rows[helper]);add(wanted,retained,Q(-1))
    if not wanted:raise ValueError('zero_protected_increment')
    caps={r:None for r in rows}
    for event in events[stop:]+word['restore']:
        for r in F.regs(event):
            if caps[r] is None:caps[r]=F.basis(tuple(event[3] if event[0]=='warp' else event[-1]))
    for r in caps:
        if caps[r] is None:
            caps[r]=F.basis(tuple(word['helper_final'].get(str(r),FULL)))
    available=[r for r in rows if r!=helper and not 112<=r<224 and rows[r]
               and F.contains(current[r],frame) and F.contains(frame,caps[r])]
    def cost(r):
        return F.phi(len(frame)-len(current[r]))+F.phi(len(caps[r])-len(frame))-F.phi(len(caps[r])-len(current[r]))
    available.sort(key=lambda r:(cost(r),len(rows[r]),r))
    support=combination(wanted,available,rows)
    if not support:raise ValueError('no_dyadic_protected_span')
    new=[['add',helper,r,q.numerator,q.denominator,list(frame)] for r,q in sorted(support.items()) if q]
    changed=[]
    for index,event in enumerate(events):
        if index==end:changed.extend(new)
        if index not in deleted:changed.append(event)
    out=deepcopy(word);out['B']=[]
    for event in changed:
        if event[0]=='warp':out['warps'][event[2]-1][0]=len(out['B'])
        else:out['B'].append(event)
    F.derive_cleanup(out)
    return out,{'helper':helper,'position':position,'deleted_expanded_B':writes,
                'first_observer':observer,'new_production':new,'compatible_donors':len(available),
                'protected_increment_support':len(wanted),'matched_protected_input_count':len(rows)-len(allowed),
                'early_dirty_reads_retained':True}


def main():
    p=ArgumentParser(description=__doc__)
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--variant',choices=('base','extra'),default='base')
    p.add_argument('--position',choices=('last_write','first_observer'),default='last_write')
    p.add_argument('--helpers',nargs='+',type=int)
    args=p.parse_args();source=OLD/f'candidate/BORROW-WORD-43{args.variant}.json.gz'
    word=F.read(source);assert replay(word)[0]==expected(word)
    helpers=sorted(set(map(int,word['start_extra']))-set(map(int,word['helper_final'])))
    helpers=[r for r in helpers if r>=224 and r not in word['removed']]
    if args.helpers:helpers=args.helpers
    args.output.mkdir(parents=True,exist_ok=True);stats=Counter();cases=[];positives=[];started=monotonic()
    for helper in helpers:
        stats['warm_helpers_considered']+=1
        try:out,identity=candidate(word,helper,args.position)
        except (ValueError,AssertionError) as exc:
            reason=str(exc.args[0]);stats[reason]+=1;continue
        stats['protected_producer_rebuilt']+=1
        case={'helper':helper,'identity':identity}
        try:out,optimization=O.optimize(out)
        except (ValueError,AssertionError) as exc:
            stats['frame_rejected']+=1;case['frame_rejection']=str(exc)
        else:
            stats['joint_frames_solved']+=1;case['optimization']=optimization
            if optimization['saving']>1e-10:
                try:correction=repair(out)
                except (ValueError,AssertionError) as exc:
                    case['dirty_rejection']=str(exc);stats['dirty_rejected']+=1
                else:
                    assert trace(out)[0]==Counter({int(r):c for r,c in out['report']['local_profile'].items()})
                    payload=canonical(out);name=f'WORD-helper{helper}.json.gz'
                    (args.output/name).write_bytes(gzip.compress(payload,mtime=0))
                    case.update(correction=correction,word=name,payload_sha256=sha256(payload).hexdigest(),native_admission=False)
                    stats['positive_exact_word']+=1;positives.append(case)
                    print('POSITIVE',helper,optimization,correction,flush=True)
        cases.append(case)
        if len(cases)%10==0:print('PROGRESS',dict(stats),'seconds',monotonic()-started,flush=True)
    paths=[source,Path(__file__),HERE/'matched_basis.py',OLD/'fanout_search.py',OLD/'opt_frames.py',
           PREVIOUS/'exact_rows.py',PREVIOUS/'commute_birth.py',PREVIOUS.parent/'complex_projection_screen.py']
    result={'status':'WARM_COMPLEX_B_PRODUCER_PROTECTED_ROW_SCREEN','variant':args.variant,'position':args.position,
            'helpers':helpers,'stats':dict(stats),'cases':cases,'positives':positives,'new_kappa':False,
            'seconds':monotonic()-started,
            'source_sha256':{str(x.relative_to(ROOT)):sha256(x.read_bytes()).hexdigest() for x in paths},
            'scope':'Later production after unchanged early dirty observations; SOURCE, TARGET, and every nonzero-entry/wrapped dirty '
                    'input are retained. Changed zero-entry/full-exit helper residuals require exact dirty TARGET repair. '
                    'Positive profile nomination is not native or outer admission.'}
    (args.output/'RESULT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print('DONE',dict(stats),'seconds',monotonic()-started,flush=True)


if __name__=='__main__':main()
