#!/usr/bin/env python3
"""Rebuild any unobserved signed helper write interval, beyond first births."""
from argparse import ArgumentParser
from collections import Counter,defaultdict
from copy import deepcopy
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
from time import monotonic
import gzip,json,sys
from network_search import ROOT,HERE,FROZEN,F,O,FULL,OLD,trace,canonical,quotient_rows,normalized,execute,add,repair,encode_sections,future_caps,allowed_helpers
sys.path.insert(0,str(FROZEN.parent))
from complex_projection_screen import combination


def main():
    ap=ArgumentParser(description=__doc__);ap.add_argument('--output',type=Path,required=True)
    ap.add_argument('--variant',choices=('base','extra'),default='base');ap.add_argument('--source-only',action='store_true')
    ap.add_argument('--optimize-ties',action='store_true');ap.add_argument('--multi-frame-only',action='store_true')
    args=ap.parse_args();args.output.mkdir(parents=True,exist_ok=True)
    source=OLD/f'candidate/BORROW-WORD-43{args.variant}.json.gz';word=F.read(source);sec=F.expand(word)
    rows=quotient_rows(word,args.source_only);allowed=allowed_helpers(word);live=set(rows)
    current={r:F.basis((word['ports'][r],)) if r<112 else F.basis(tuple(word['start_extra'].get(str(r),()))) for r in live}
    history={r:[(-1,current[r])] for r in live};caps=future_caps(word,sec);pending={};initial={}
    base=Counter({int(r):c for r,c in word['report']['local_profile'].items()});census=Counter();found=[];cases=[];started=monotonic()
    def test(helper,index,observer_frame):
        writes=pending.pop(helper,[])
        before=initial.pop(helper,None)
        if len(writes)<2:return
        census['unobserved_intervals']+=1
        if args.multi_frame_only and len({tuple(word['A'][i][-1]) for i in writes})<2:return
        wanted=dict(rows[helper]);add(wanted,before,Q(-1))
        frame=F.basis(tuple(observer_frame));deleted=set(writes)
        affected={r for i in writes for r in F.regs(word['A'][i])}
        cur=dict(current)
        for r in affected:
            cur[r]=next(f for k,f in reversed(history[r]) if k not in deleted)
        if not F.contains(cur[helper],frame):return
        available=[r for r in sorted(live) if r!=helper and not 112<=r<224 and rows[r] and
                   F.contains(cur[r],frame) and F.contains(frame,caps['A'][index][r])]
        available.sort(key=lambda r:(F.phi(len(frame)-len(cur[r]))+F.phi(len(caps['A'][index][r])-len(frame))-
                                     F.phi(len(caps['A'][index][r])-len(cur[r])),len(rows[r]),r))
        solution={} if not wanted else combination(wanted,available,rows)
        if solution is None:census['no_exact_dyadic_span']+=1;return
        census['exact_span']+=1
        new=[['add',helper,r,q.numerator,q.denominator,list(frame)] for r,q in sorted(solution.items()) if q]
        es=deepcopy(sec);es['A']=[e for k,e in enumerate(sec['A'][:index]) if k not in deleted]+new+sec['A'][index:]
        candidate=encode_sections(word,es)
        try:profile,_=trace(candidate)
        except (AssertionError,ValueError) as exc:census['frame_rejected']+=1;return
        delta=profile.copy();delta.subtract(base);saving=-sum(c*F.phi(r) for r,c in delta.items())
        if saving < -1e-10 or saving<=1e-10 and not args.optimize_ties:return
        candidate['report']['local_profile']={str(r):c for r,c in sorted(profile.items())}
        candidate,optimization=O.optimize(candidate);profile,_=trace(candidate)
        delta=profile.copy();delta.subtract(base);saving=-sum(c*F.phi(r) for r,c in delta.items())
        census['joint_optimized']+=1
        info={'helper':helper,'old_A_writes':writes,'replacement_before_A':index,'new':new,
              'delta':{r:c for r,c in delta.items() if c},'saving':saving,'optimization':optimization}
        if saving>1e-10:
            try:info['repair']=repair(candidate)
            except (AssertionError,ValueError) as exc:census['dirty_rejected']+=1;info['rejected']=str(exc)
            else:
                payload=canonical(candidate);name=f'WORD-helper{helper}-before{index}.json.gz';(args.output/name).write_bytes(gzip.compress(payload,mtime=0))
                info.update(word=name,word_content_sha256=sha256(payload).hexdigest(),local_profile=dict(profile),native_admission=False)
                found.append(info);census['positive_exact']+=1;print('POSITIVE',json.dumps(info,sort_keys=True),flush=True)
        cases.append(info)
    for index,event in enumerate(sec['A']):
        if event[0]=='add' and event[2] in allowed:test(event[2],index,event[-1])
        d=event[1]
        if index>=word['prelude_events'] and d in allowed:
            if d not in pending:pending[d]=[];initial[d]=dict(rows[d])
            pending[d].append(index)
        execute(rows,event)
        if event[0]=='warp':current[d]=F.basis(tuple(event[4]));history[d].append((index,current[d]))
        else:
            for r in F.regs(event):current[r]=F.basis(tuple(event[-1]));history[r].append((index,current[r]))
        if index%500==0:print('PROGRESS',index,dict(census),monotonic()-started,flush=True)
    # Helpers not subsequently read by A may first be observed by COPY/B.
    for helper in sorted(set(pending)):
        frame=word['center_frames'][word['centers'].index(helper)] if helper in word['centers'] else caps['A'][-1][helper]
        test(helper,len(sec['A']),frame)
    paths=[Path(__file__),HERE/'network_search.py',source,FROZEN/'exact_rows.py',FROZEN.parent/'complex_projection_screen.py',OLD/'opt_frames.py']
    result={'status':'SIGNED_COMPLEX_ALL_UNOBSERVED_WRITE_INTERVAL_SCREEN','source_only':args.source_only,
            'census':dict(census),'cases':cases,'positives':found,'seconds':monotonic()-started,
            'source_sha256':{str(p.relative_to(ROOT)):sha256(p.read_bytes()).hexdigest() for p in paths},
            'scope':'Every at-least-two-write interval between A donor observations on the213 unwrapped zero-entrance/full-exit helpers; one exact greedy weighted rational donor basis at the next observation frame. This includes later write intervals, not just first births.'}
    (args.output/'RESULT.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n');print('DONE',dict(census),flush=True)


if __name__=='__main__':main()
