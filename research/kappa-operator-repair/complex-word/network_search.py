#!/usr/bin/env python3
"""Signed observed-module resynthesis with explicit free-operator repair.

The quotient kills only the 213 zero-entrance/full-exit unwrapped helpers.
All SOURCE, TARGET and wrapped-helper columns remain independent. A changed
word is a candidate until exact all-input and native phase/frame admission.
Apache-2.0; substantial OpenAI assistance. Retained supplier authors and the
frame optimizer are credited through the pinned predecessor source files.
"""
from argparse import ArgumentParser
from collections import Counter, defaultdict
from copy import deepcopy
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
from time import monotonic
import gzip, json, random, sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
FROZEN = ROOT/'research/kappa-1745-continuation/complex-birth'
sys.path.insert(0, str(FROZEN))
from commute_birth import F, O, trace, canonical, FULL, OLD
from exact_rows import add, execute, replay, expected, repair


def allowed_helpers(word):
    return set(range(224,704))-set(word['removed'])-set(map(int,word['start_extra']))-set(map(int,word['helper_final']))


def quotient_rows(word, source_only=False):
    allowed = allowed_helpers(word)
    live = set(range(704))-set(word['removed'])
    rows = {r: {} if (r in allowed or source_only and r>=112) else {(r,()):Q(1)} for r in live}
    for term in word['initial_corrections']:
        if term['source'] not in allowed:
            raise ValueError('retained initial correction uses protected input')
    for event in word['precondition']+word['compensation']:
        execute(rows,event)
    return rows


def normalized(row):
    if not row:
        return (),Q(1)
    first=min(row);factor=row[first]
    return tuple((key,value/factor) for key,value in sorted(row.items())),factor


def blocks(events, start=0):
    index=0
    while index<len(events):
        end=index+1
        event=events[index]
        if index>=start and event[0]=='add':
            while end<len(events) and events[end][0]=='add' and events[end][1]==event[1] and events[end][-1]==event[-1]:
                end+=1
        yield index,end,events[index:end]
        index=end


def future_caps(word, sections):
    live=set(range(704))-set(word['removed'])
    upper=[None]*704
    for r in live:
        upper[r]=F.basis(tuple(word['helper_final'].get(str(r),FULL)))
        if 112<=r<224:
            upper[r]=F.basis(tuple(x for x in range(512) if not ((x&word['ports'][r-112]).bit_count()&1)))
    future={}
    for name in ('restore','B','A'):
        out=[None]*(len(sections[name])+1);out[-1]=tuple(upper)
        for index in reversed(range(len(sections[name]))):
            e=sections[name][index]
            if e[0]=='warp':upper[e[1]]=F.basis(tuple(e[3]))
            else:
                frame=F.basis(tuple(e[-1]))
                for r in F.regs(e):upper[r]=frame
            out[index]=tuple(upper)
        future[name]=out
        if name=='B':
            for r,f in zip(word['centers'],word['center_frames']):upper[r]=F.basis(tuple(f))
            for t in range(112):upper[112+t]=F.basis(tuple(word['target_levels'].get(str(t),[])))
    return future


def encode_sections(word, sections):
    out=deepcopy(word);out['A']=sections['A'];out['restore']=sections['restore'];out['B']=[]
    for event in sections['B']:
        if event[0]=='warp':out['warps'][event[2]-1][0]=len(out['B'])
        else:out['B'].append(event)
    F.derive_cleanup(out)
    return out


def local_change(current, cap, old, new, frame):
    old_regs={r for e in old for r in F.regs(e)}
    new_regs={r for e in new for r in F.regs(e)}
    oldframe=F.basis(tuple(old[0][-1]));delta=Counter()
    for r in old_regs|new_regs:
        before=current[r];after=cap[r]
        for active, middle, sign in ((r in old_regs,oldframe,-1),(r in new_regs,frame,1)):
            path=(before,middle,after) if active else (before,after)
            for a,b in zip(path,path[1:]):
                if not F.contains(a,b):return None
                if len(a)!=len(b):delta[len(b)-len(a)]+=sign
    return {r:c for r,c in delta.items() if c}


def synthesize(word, seed=0, pairs=False, source_only=False, optimize_ties=False, limit=0):
    rows=quotient_rows(word,source_only);live=set(rows)
    groups=defaultdict(set);keys={};factors={}
    def refresh(r):
        if r in keys:groups[keys[r]].discard(r)
        keys[r],factors[r]=normalized(rows[r]);groups[keys[r]].add(r)
    for r in live:refresh(r)
    current={r:F.basis((word['ports'][r],)) if r<112 else F.basis(tuple(word['start_extra'].get(str(r),()))) for r in live}
    sections=F.expand(word);caps=future_caps(word,sections)
    changes=[];census=Counter();out={};rng=random.Random(seed)
    for name in ('A','B','restore'):
        out[name]=[]
        for lo,hi,old in blocks(sections[name],word['prelude_events'] if name=='A' else 0):
            selected=old
            if old[0][0]=='add' and (name!='A' or lo>=word['prelude_events']) and (not limit or len(changes)<limit):
                d=old[0][1];wanted={}
                for e in old:add(wanted,rows[e[2]],Q(e[3],e[4]))
                key,factor=normalized(wanted);census['blocks']+=1
                hypotheses=[]
                if not key:hypotheses.append({})
                else:
                    for donor in sorted(groups.get(key,())):
                        if donor==d or 112<=donor<224:continue
                        q=factor/factors[donor]
                        if not q.denominator&(q.denominator-1):hypotheses.append({donor:q})
                if pairs and key:
                    oldframe=F.basis(tuple(old[0][-1]));compatible=[]
                    for donor in sorted(live):
                        if donor==d or 112<=donor<224 or not rows[donor]:continue
                        if F.contains(current[donor],oldframe) and F.contains(oldframe,caps[name][hi][donor]):compatible.append(donor)
                    rng.shuffle(compatible)
                    for a in compatible:
                        # Coefficient candidates are exact dyadics; row differences
                        # and the second donor are verified over the full quotient.
                        qs={Q(1),Q(-1),Q(2),Q(-2),Q(1,2),Q(-1,2)}
                        if min(rows[a]) in wanted:qs.add(wanted[min(rows[a])]/rows[a][min(rows[a])])
                        for qa in sorted(qs):
                            if qa.denominator&(qa.denominator-1):continue
                            remainder=dict(wanted);add(remainder,rows[a],-qa)
                            k,f=normalized(remainder)
                            if not k:continue
                            for b in groups.get(k,()):
                                if b==d or b==a or 112<=b<224:continue
                                qb=f/factors[b]
                                if not qb.denominator&(qb.denominator-1):hypotheses.append({a:qa,b:qb})
                best=(0.0,0,());best_info=None
                for support in hypotheses:
                    frame=F.basis(tuple(v for r in [d]+list(support) for v in current[r]))
                    new=[['add',d,r,q.numerator,q.denominator,list(frame)] for r,q in sorted(support.items())]
                    delta=local_change(current,caps[name][hi],old,new,frame)
                    if delta is None:census['fixed_frames_reject']+=1;continue
                    census['fixed_frames_feasible']+=1
                    saving=-sum(c*F.phi(r) for r,c in delta.items())
                    score=(round(saving,12),len(old)-len(new),tuple(-r for r in support))
                    acceptable=saving>1e-10 or optimize_ties and abs(saving)<1e-10 and len(new)<len(old)
                    if acceptable and score>best:
                        selected=new;best=score;best_info=(delta,support,frame,saving)
                if best_info:
                    delta,support,frame,saving=best_info
                    changed={'section':name,'old_slice':[lo,hi],'old':old,'new':selected,'delta':delta,'saving':saving,
                             'projected_terms':len(wanted),'projected_sources':sorted(set(var for var,op in wanted))}
                    changes.append(changed);census['changes']+=1
                    print('CHANGE',name,lo,hi,delta,saving,flush=True)
            for event in selected:
                if event[0]=='warp':
                    assert F.contains(current[event[1]],F.basis(tuple(event[3])))
                    current[event[1]]=F.basis(tuple(event[4]))
                else:
                    frame=F.basis(tuple(event[-1]))
                    for r in F.regs(event):
                        assert F.contains(current[r],frame),(name,lo,r,current[r],frame)
                        current[r]=frame
                execute(rows,event);refresh(event[1])
            out[name].extend(selected)
        if name=='A':
            for r,f in zip(word['centers'],word['center_frames']):current[r]=F.basis(tuple(f))
            for t in range(112):current[112+t]=F.basis(tuple(word['target_levels'].get(str(t),[])))
            for event in word['cut']:execute(rows,event);refresh(event[1])
    return encode_sections(word,out),changes,dict(census)


def main():
    ap=ArgumentParser(description=__doc__);ap.add_argument('--output',type=Path,required=True)
    ap.add_argument('--word',type=Path);ap.add_argument('--variant',choices=('base','extra'),default='base')
    ap.add_argument('--pairs',action='store_true');ap.add_argument('--source-only',action='store_true')
    ap.add_argument('--ties',action='store_true');ap.add_argument('--seed',type=int,default=0)
    ap.add_argument('--limit',type=int,default=0)
    args=ap.parse_args();args.output.mkdir(parents=True,exist_ok=True)
    source=args.word or OLD/f'candidate/BORROW-WORD-43{args.variant}.json.gz';word=F.read(source)
    started=monotonic();base=Counter({int(r):c for r,c in word['report']['local_profile'].items()})
    candidate,changes,census=synthesize(word,args.seed,args.pairs,args.source_only,args.ties,args.limit)
    print('SYNTHESIZED',len(changes),census,monotonic()-started,flush=True)
    profile,_=trace(candidate);delta=profile.copy();delta.subtract(base)
    candidate['report']['local_profile']={str(r):c for r,c in sorted(profile.items())}
    candidate,optimization=O.optimize(candidate)
    profile,_=trace(candidate);delta=profile.copy();delta.subtract(base)
    result={'status':'SIGNED_QUOTIENT_NETWORK_SCREEN','changes':changes,'census':census,
            'source_only':args.source_only,'pairs':args.pairs,'ties':args.ties,'optimization':optimization,
            'local_profile':dict(profile),'delta':{r:c for r,c in delta.items() if c},
            'saving':-sum(c*F.phi(r) for r,c in delta.items()),'native_admission':False}
    try:result['repair']=repair(candidate)
    except (ValueError,AssertionError) as exc:result['rejected']=str(exc)
    else:
        payload=canonical(candidate);path=args.output/'WORD.json.gz';path.write_bytes(gzip.compress(payload,mtime=0))
        result.update(word='WORD.json.gz',word_content_sha256=sha256(payload).hexdigest(),word_sha256=sha256(path.read_bytes()).hexdigest())
    result['seconds']=monotonic()-started
    paths=[Path(__file__),source,FROZEN/'commute_birth.py',FROZEN/'exact_rows.py',OLD/'fanout_search.py',OLD/'opt_frames.py']
    result['source_sha256']={str(p.relative_to(ROOT)):sha256(p.read_bytes()).hexdigest() for p in paths}
    (args.output/'RESULT.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
    print('DONE',{k:v for k,v in result.items() if k not in ('changes','source_sha256')},flush=True)


if __name__=='__main__':main()
