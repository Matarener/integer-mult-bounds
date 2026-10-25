#!/usr/bin/env python3
"""Route one A input into a signed network with identical protected outputs.

Backward free-operator columns retain every TARGET and every non-FULL helper
output. Replacing d += c*s by q_j += a_j*s is exact on these outputs when
sum a_j response(q_j) = c response(d). Literal inverse cleanup is regenerated;
the complete all-input free-warp law and native frame pricing remain gates.
"""
from argparse import ArgumentParser
from collections import Counter,defaultdict
from copy import deepcopy
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
from time import monotonic
import gzip,json,sys
from network_search import ROOT,HERE,FROZEN,F,O,FULL,OLD,trace,canonical,execute,add,repair,encode_sections,future_caps,allowed_helpers,normalized,local_change
sys.path.insert(0,str(FROZEN.parent))
from complex_projection_screen import combination


def backward(columns,event):
    kind,d=event[:2]
    if kind=='add':add(columns[event[2]],columns[d],Q(event[3],event[4]))
    elif kind=='scale':columns[d]={k:Q(event[2],event[3])*v for k,v in columns[d].items()}
    elif kind=='warp':
        op=event[2]
        columns[d]={(var,word[:-1] if word and word[-1]==-op else word+(op,)):v for (var,word),v in columns[d].items()}
    else:raise ValueError(kind)


def main():
    ap=ArgumentParser(description=__doc__);ap.add_argument('--output',type=Path,required=True)
    ap.add_argument('--variant',choices=('base','extra'),default='base');ap.add_argument('--word',type=Path)
    ap.add_argument('--target-only',action='store_true');ap.add_argument('--singles',action='store_true')
    ap.add_argument('--limit',type=int,default=0);args=ap.parse_args();args.output.mkdir(parents=True,exist_ok=True)
    source=args.word or OLD/f'candidate/BORROW-WORD-43{args.variant}.json.gz';word=F.read(source);sec=F.expand(word)
    live=set(range(704))-set(word['removed']);allowed=allowed_helpers(word)
    outputs=set(range(112,224)) | (set() if args.target_only else set(map(int,word['helper_final'])))
    cols={r:{(r,()):Q(1)} if r in outputs else {} for r in live}
    for e in reversed(sec['restore']):backward(cols,e)
    for e in reversed(sec['B']):backward(cols,e)
    for e in reversed(word['cut']):backward(cols,e)
    current={r:F.basis((word['ports'][r],)) if r<112 else F.basis(tuple(word['start_extra'].get(str(r),()))) for r in live}
    starts=[]
    for e in sec['A']:
        starts.append(dict(current))
        if e[0]=='warp':current[e[1]]=F.basis(tuple(e[4]))
        else:
            for r in F.regs(e):current[r]=F.basis(tuple(e[-1]))
    caps=future_caps(word,sec)['A'];base=Counter({int(r):c for r,c in word['report']['local_profile'].items()})
    census=Counter();found=[];cases=[];started=monotonic()
    for index in reversed(range(len(sec['A']))):
        event=sec['A'][index]
        if index>=word['prelude_events'] and event[0]=='add' and event[1] >= 224:
            d,s=event[1:3];frame=F.basis(tuple(event[-1]));cur=starts[index];cap=caps[index+1]
            # A movable paid destination contact is the initial useful scale.
            removed_cost=F.phi(len(frame)-len(cur[d]))+F.phi(len(cap[d])-len(frame))-F.phi(len(cap[d])-len(cur[d]))
            if removed_cost>1e-10 and (not args.limit or census['queries']<args.limit):
                census['queries']+=1;coefficient=Q(event[3],event[4]);wanted={k:coefficient*v for k,v in cols[d].items()}
                def extra(q):return F.phi(len(frame)-len(cur[q]))+F.phi(len(cap[q])-len(frame))-F.phi(len(cap[q])-len(cur[q]))
                available=[q for q in sorted(live) if q!=d and cols[q] and F.contains(cur[q],frame) and F.contains(frame,cap[q])]
                available.sort(key=lambda q:(round(extra(q),12),len(cols[q]),q))
                solutions=[];key,factor=normalized(wanted)
                if not wanted:solutions.append({})
                else:
                    for q in available:
                        k,f=normalized(cols[q])
                        if k==key and not (factor/f).denominator&((factor/f).denominator-1):solutions.append({q:factor/f})
                    if not args.singles:
                        for subset in ([q for q in available if extra(q)<1e-10],available):
                            census['rational_span_queries']+=1
                            answer=combination(wanted,subset,cols)
                            if answer is not None:solutions.append(answer)
                seen=set()
                for support in solutions:
                    key=tuple(sorted(support.items()))
                    if key in seen:continue
                    seen.add(key);census['exact_column_solutions']+=1
                    new=[['add',q,s,a.numerator,a.denominator,list(frame)] for q,a in sorted(support.items()) if q!=s and a]
                    if s in support:
                        factor=1+support[s]
                        if not factor or factor.numerator and abs(factor.numerator)&(abs(factor.numerator)-1):continue
                        new.append(['scale',s,factor.numerator,factor.denominator,list(frame)])
                    delta=local_change(cur,cap,[event],new,frame)
                    if delta is None:census['fixed_frames_rejected']+=1;continue
                    saving=-sum(c*F.phi(r) for r,c in delta.items())
                    if saving<=1e-10:continue
                    census['positive_fixed_profile']+=1
                    sections=deepcopy(sec);sections['A'][index:index+1]=new;candidate=encode_sections(word,sections)
                    profile,_=trace(candidate);actual=profile.copy();actual.subtract(base)
                    assert {r:c for r,c in actual.items() if c}==delta
                    candidate['report']['local_profile']={str(r):c for r,c in sorted(profile.items())}
                    candidate,opt=O.optimize(candidate);profile,_=trace(candidate);actual=profile.copy();actual.subtract(base)
                    info={'old_A_index':index,'old':event,'new':new,'delta':{r:c for r,c in actual.items() if c},
                          'saving':-sum(c*F.phi(r) for r,c in actual.items()),'optimization':opt,'protected_outputs':len(outputs)}
                    try:info['repair']=repair(candidate)
                    except (AssertionError,ValueError) as exc:census['full_dirty_rejected']+=1;info['rejected']=str(exc)
                    else:
                        payload=canonical(candidate);name=f'WORD-A{index}-{len(found)}.json.gz';(args.output/name).write_bytes(gzip.compress(payload,mtime=0))
                        info.update(word=name,word_content_sha256=sha256(payload).hexdigest(),local_profile=dict(profile),native_admission=False)
                        found.append(info);census['positive_exact']+=1;print('POSITIVE',json.dumps(info,sort_keys=True),flush=True)
                    cases.append(info)
        backward(cols,event)
        if index%250==0:print('PROGRESS',index,dict(census),monotonic()-started,flush=True)
    paths=[Path(__file__),HERE/'network_search.py',source,FROZEN/'exact_rows.py',FROZEN.parent/'complex_projection_screen.py',OLD/'opt_frames.py']
    result={'status':'EXACT_COMPLEX_BACKWARD_RESPONSE_INPUT_ROUTING','protected_outputs':len(outputs),'target_only':args.target_only,
            'census':dict(census),'positives':found,'cases':cases,'seconds':monotonic()-started,
            'source_sha256':{str(p.relative_to(ROOT)):sha256(p.read_bytes()).hexdigest() for p in paths},
            'scope':'A injections into all live helpers with a removable paid stop; same-cut same-input signed receiver network with exact free-operator response columns, then complete all-input repair. No native or global admission is asserted by this search.'}
    (args.output/'RESULT.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n');print('DONE',dict(census),flush=True)


if __name__=='__main__':main()
