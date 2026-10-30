#!/usr/bin/env python3
"""Move exact signed TARGET queries to later legal observation frames.

The queried row is held fixed modulo the explicitly compensatable unwrapped
dirty inputs, and rebuilt from the actual rows at the new chronological cut.
All full dirty inputs and free warp words are checked after compensation.
"""
from argparse import ArgumentParser
from collections import Counter,defaultdict
from copy import deepcopy
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
from time import monotonic
import gzip,json,sys
from network_search import ROOT,HERE,FROZEN,F,O,FULL,OLD,trace,canonical,quotient_rows,normalized,execute,add,repair,encode_sections,future_caps
sys.path.insert(0,str(FROZEN.parent))
from complex_projection_screen import combination


def main():
    ap=ArgumentParser(description=__doc__);ap.add_argument('--output',type=Path,required=True)
    ap.add_argument('--variant',choices=('base','extra'),default='base');ap.add_argument('--combinations',action='store_true')
    ap.add_argument('--max-query-index',type=int,default=150);ap.add_argument('--query',type=int)
    args=ap.parse_args();args.output.mkdir(parents=True,exist_ok=True)
    source=OLD/f'candidate/BORROW-WORD-43{args.variant}.json.gz';word=F.read(source);sections=F.expand(word)
    base=Counter({int(r):c for r,c in word['report']['local_profile'].items()});caps=future_caps(word,sections)
    rows=quotient_rows(word);live=set(rows)
    current={r:F.basis((word['ports'][r],)) if r<112 else F.basis(tuple(word['start_extra'].get(str(r),()))) for r in live}
    def advance(e):
        if e[0]=='warp':current[e[1]]=F.basis(tuple(e[4]))
        else:
            for r in F.regs(e):current[r]=F.basis(tuple(e[-1]))
        execute(rows,e)
    for e in sections['A']:advance(e)
    for r,f in zip(word['centers'],word['center_frames']):current[r]=F.basis(tuple(f))
    for t in range(112):current[112+t]=F.basis(tuple(word['target_levels'].get(str(t),[])))
    for e in word['cut']:execute(rows,e)
    queries=[];census=Counter();found=[];started=monotonic()
    for name in ('B','restore'):
        for index,e in enumerate(sections[name]):
            # A TARGET-to-TARGET read is an observation barrier. This bounded
            # search does not propagate one omitted query into several rows.
            if e[0]=='add' and 112<=e[2]<224:
                assert 112<=e[1]<224
                before=len(queries);queries=[q for q in queries if q['target']!=e[2]]
                census['target_observation_barriers']+=before-len(queries)
            if 112<=e[1]<224:
                d=e[1];frame=F.basis(tuple(e[-1]));eligible=[q for q in queries if q['target']==d]
                if eligible:
                    available=[r for r in sorted(live) if not 112<=r<224 and rows[r] and
                               F.contains(current[r],frame) and F.contains(frame,caps[name][index][r])]
                    available.sort(key=lambda r:(F.phi(len(frame)-len(current[r]))+F.phi(len(caps[name][index][r])-len(frame))-
                                                 F.phi(len(caps[name][index][r])-len(current[r])),len(rows[r]),r))
                    groups=defaultdict(list)
                    for r in available:
                        key,factor=normalized(rows[r]);groups[key].append((r,factor))
                    for query in eligible:
                        census['later_target_contacts']+=1
                        target=query['row'];key,factor=normalized(target)
                        solutions=[{r:factor/f} for r,f in groups.get(key,()) if not (factor/f).denominator&((factor/f).denominator-1)]
                        if args.combinations:
                            census['linear_span_queries']+=1
                            answer=combination(target,available,rows)
                            if answer:solutions.append(answer)
                        for answer in solutions:
                            census['algebraic_solutions']+=1
                            new=[['add',d,r,q.numerator,q.denominator,list(frame)] for r,q in sorted(answer.items()) if q]
                            sec=deepcopy(sections);where=query['index']
                            if name=='B':sec['B']=sec['B'][:where]+sec['B'][where+1:index]+new+sec['B'][index:]
                            else:
                                del sec['B'][where];sec[name][index:index]=new
                            candidate=encode_sections(word,sec)
                            try:profile,_=trace(candidate)
                            except (AssertionError,ValueError):census['frame_rejected']+=1;continue
                            delta=profile.copy();delta.subtract(base)
                            saving=-sum(c*F.phi(r) for r,c in delta.items())
                            if saving<=1e-10:continue
                            candidate['report']['local_profile']={str(r):c for r,c in sorted(profile.items())}
                            candidate,optimization=O.optimize(candidate)
                            profile,_=trace(candidate);delta=profile.copy();delta.subtract(base)
                            info={'query_B_index':where,'old':query['event'],'replacement_section':name,'replacement_index':index,
                                  'new':new,'delta':{r:c for r,c in delta.items() if c},'local_profile':dict(profile),
                                  'saving':-sum(c*F.phi(r) for r,c in delta.items()),'optimization':optimization}
                            try:info['repair']=repair(candidate)
                            except (AssertionError,ValueError) as exc:
                                census['full_dirty_rejected']+=1;info['rejected']=str(exc)
                            else:
                                census['positive_exact_word']+=1
                                payload=canonical(candidate);filename=f'WORD-{where}-{name}-{index}-{len(found)}.json.gz'
                                (args.output/filename).write_bytes(gzip.compress(payload,mtime=0))
                                info.update(word=filename,word_content_sha256=sha256(payload).hexdigest(),native_admission=False)
                                found.append(info);print('POSITIVE',json.dumps(info,sort_keys=True),flush=True)
                if name=='B' and index<args.max_query_index and e[0]=='add' and (args.query is None or index==args.query):
                    r=e[2];coefficient=Q(e[3],e[4]);row={k:coefficient*v for k,v in rows[r].items()}
                    if row:queries.append({'index':index,'target':d,'row':row,'event':e});census['query_births']+=1
            # TARGETs are not sources in this construction. Only their own
            # scalar multipliers propagate the pending lost observation.
            if e[0]=='scale' and 112<=e[1]<224:
                for q in queries:
                    if q['target']==e[1]:q['row']={k:Q(e[2],e[3])*v for k,v in q['row'].items()}
            if e[0]=='warp':assert not 112<=e[1]<224
            advance(e)
        print('SECTION',name,dict(census),monotonic()-started,flush=True)
    paths=[Path(__file__),HERE/'network_search.py',source,FROZEN/'exact_rows.py',FROZEN.parent/'complex_projection_screen.py',OLD/'opt_frames.py']
    result={'status':'EXACT_DELAYED_COMPLEX_TARGET_QUERY_SEARCH','census':dict(census),'positives':found,'seconds':monotonic()-started,
            'combinations':args.combinations,'source_sha256':{str(p.relative_to(ROOT)):sha256(p.read_bytes()).hexdigest() for p in paths},
            'scope':'Individual early B TARGET observations moved to later existing TARGET contacts, exact protected-module rows and literal full-dirty compensation. Native admission and whole invoice remain required for positives.'}
    (args.output/'RESULT.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n');print('DONE',dict(census),flush=True)


if __name__=='__main__':main()
