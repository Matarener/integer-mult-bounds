#!/usr/bin/env python3
"""Jointly reroute all plain-helper injections of one unchanged A donor.

All TARGET and HPE output responses are constrained in the exact free warp
algebra. Several removed injections share the same unchanged donor value.
This is a receiver-network change, with actual paths repriced and full native
operator admission required after the all-input free-word gate.
"""
from argparse import ArgumentParser
from collections import Counter,defaultdict
from copy import deepcopy
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
from time import monotonic
import gzip,json,sys
from network_search import ROOT,HERE,FROZEN,F,O,FULL,OLD,trace,canonical,add,repair,encode_sections,future_caps,allowed_helpers
from response_routes import backward
sys.path.insert(0,str(FROZEN.parent))
from complex_projection_screen import combination


def main():
    ap=ArgumentParser(description=__doc__);ap.add_argument('--output',type=Path,required=True)
    ap.add_argument('--word',type=Path);ap.add_argument('--target-only',action='store_true')
    ap.add_argument('--all-cuts',action='store_true');ap.add_argument('--optimize-ties',action='store_true')
    args=ap.parse_args();args.output.mkdir(parents=True,exist_ok=True)
    source=args.word or OLD/'candidate/BORROW-WORD-43base.json.gz';word=F.read(source);sec=F.expand(word);events=sec['A']
    live=set(range(704))-set(word['removed']);allowed=allowed_helpers(word);caps=future_caps(word,sec)['A']
    current={r:F.basis((word['ports'][r],)) if r<112 else F.basis(tuple(word['start_extra'].get(str(r),()))) for r in live}
    starts=[];history={r:[(-1,current[r])] for r in live};groups=defaultdict(list);epoch=Counter();epochs=[]
    for index,e in enumerate(events):
        starts.append(dict(current));epochs.append(epoch.copy())
        if e[0]=='add' and e[1]>=224 and index>=word['prelude_events']:groups[e[2],epoch[e[2]]].append(index)
        if e[0]=='warp':current[e[1]]=F.basis(tuple(e[4]));history[e[1]].append((index,current[e[1]]))
        else:
            for r in F.regs(e):current[r]=F.basis(tuple(e[-1]));history[r].append((index,current[r]))
        epoch[e[1]]+=1
    selected={}
    for key,positions in groups.items():
        if len(positions)<2:continue
        if not any(len(starts[i][events[i][1]])<len(F.basis(tuple(events[i][-1])))<len(caps[i+1][events[i][1]]) for i in positions):continue
        selected[key]={'source':key[0],'positions':positions,'wanted':{},'contributions':{}}
    byposition={i:key for key,q in selected.items() for i in q['positions']}
    outputs=set(range(112,224)) | (set() if args.target_only else set(map(int,word['helper_final'])))
    def initial_columns():
        cols={r:{(r,()):Q(1)} if r in outputs else {} for r in live}
        for e in reversed(sec['restore']):backward(cols,e)
        for e in reversed(sec['B']):backward(cols,e)
        for e in reversed(word['cut']):backward(cols,e)
        return cols
    cols=initial_columns()
    for index in reversed(range(len(events))):
        e=events[index]
        if index in byposition:
            query=selected[byposition[index]];contribution={k:Q(e[3],e[4])*v for k,v in cols[e[1]].items()}
            query['contributions'][index]=contribution;add(query['wanted'],contribution,Q(1))
        backward(cols,e)
    cut_queries=defaultdict(list)
    for key,q in selected.items():
        ps=q['positions']
        cuts=ps if args.all_cuts else sorted({ps[0],ps[-1],ps[len(ps)//2]})
        for cut in cuts:cut_queries[cut].append(key)
    base=Counter({int(r):c for r,c in word['report']['local_profile'].items()});cols=initial_columns()
    census=Counter(groups=len(selected),cuts=sum(map(len,cut_queries.values())));found=[];cases=[];started=monotonic()
    for index in reversed(range(len(events))):
        backward(cols,events[index])
        for key in cut_queries.get(index,()):
            query=selected[key];s=query['source'];deleted=set(query['positions']);cur=dict(starts[index]);cap=list(caps[index])
            affected={r for i in deleted for r in F.regs(events[i])}
            for r in affected:
                cur[r]=next(f for j,f in reversed(history[r]) if j<index and j not in deleted)
                future=next((e for j,e in enumerate(events[index:],index) if j not in deleted and r in F.regs(e)),None)
                cap[r]=F.basis(tuple(future[3] if future and future[0]=='warp' else future[-1])) if future else caps[-1][r]
            # Every donor write is an epoch boundary. The same literal input
            # value therefore appears in every removed gate and at this cut.
            assert all(epochs[i][s]==key[1] for i in deleted)
            # The donor's own response changes when its future fanout is
            # deleted. Other columns cannot feed it in this unchanged epoch.
            effective=dict(cols);effective[s]=dict(cols[s])
            for old_index,contribution in query['contributions'].items():
                if old_index>=index:add(effective[s],contribution,Q(-1))
            old_frames={F.basis(tuple(events[i][-1])) for i in deleted}
            options={cur[s],F.basis(tuple(events[index][-1])),cap[s]}|old_frames
            seen=set()
            for frame in sorted(options,key=lambda f:(len(f),f)):
                if not F.contains(cur[s],frame) or not F.contains(frame,cap[s]):continue
                census['native_frame_queries']+=1
                available=[q for q in sorted(live) if effective[q] and F.contains(cur[q],frame) and F.contains(frame,cap[q])]
                def extra(q):return F.phi(len(frame)-len(cur[q]))+F.phi(len(cap[q])-len(frame))-F.phi(len(cap[q])-len(cur[q]))
                available.sort(key=lambda q:(round(extra(q),12),len(effective[q]),q))
                for subset in ([q for q in available if extra(q)<1e-10],available):
                    census['exact_span_queries']+=1
                    answer=combination(query['wanted'],subset,effective) if query['wanted'] else {}
                    if answer is None:continue
                    support=tuple(sorted(answer.items()));identity=(frame,support)
                    if identity in seen:continue
                    seen.add(identity);census['algebraic_solutions']+=1
                    new=[['add',q,s,a.numerator,a.denominator,list(frame)] for q,a in support if q!=s and a]
                    if s in answer:
                        factor=1+answer[s]
                        if not factor or abs(factor.numerator)&(abs(factor.numerator)-1):continue
                        new.append(['scale',s,factor.numerator,factor.denominator,list(frame)])
                    es=deepcopy(sec);es['A']=[]
                    for j,e in enumerate(events):
                        if j==index:es['A'].extend(new)
                        if j not in deleted:es['A'].append(e)
                    candidate=encode_sections(word,es)
                    try:profile,_=trace(candidate)
                    except (ValueError,AssertionError):census['fixed_frame_reject']+=1;continue
                    delta=profile.copy();delta.subtract(base);saving=-sum(c*F.phi(r) for r,c in delta.items())
                    if saving < -1e-10 or saving<=1e-10 and not args.optimize_ties:continue
                    candidate['report']['local_profile']={str(r):c for r,c in sorted(profile.items())}
                    candidate,opt=O.optimize(candidate);profile,_=trace(candidate);delta=profile.copy();delta.subtract(base)
                    census['joint_optimized']+=1;saving=-sum(c*F.phi(r) for r,c in delta.items())
                    if saving<=1e-10:continue
                    info={'source':s,'donor_epoch':key[1],'old_A_indices':query['positions'],'replacement_before_A':index,'new':new,
                          'delta':{r:c for r,c in delta.items() if c},'saving':saving,'optimization':opt,'protected_outputs':len(outputs)}
                    try:info['repair']=repair(candidate)
                    except (AssertionError,ValueError) as exc:census['full_dirty_rejected']+=1;info['rejected']=str(exc)
                    else:
                        name=f'WORD-source{s}-epoch{key[1]}-cut{index}-{len(found)}.json.gz';payload=canonical(candidate)
                        (args.output/name).write_bytes(gzip.compress(payload,mtime=0));info.update(word=name,word_content_sha256=sha256(payload).hexdigest(),local_profile=dict(profile),native_admission=False)
                        census['positive_exact']+=1;found.append(info);print('POSITIVE',json.dumps(info,sort_keys=True),flush=True)
                    cases.append(info)
        if index%500==0:print('PROGRESS',index,dict(census),monotonic()-started,flush=True)
    paths=[Path(__file__),HERE/'response_routes.py',HERE/'network_search.py',source,FROZEN/'exact_rows.py',FROZEN.parent/'complex_projection_screen.py',OLD/'opt_frames.py']
    result={'status':'EXACT_COMPLEX_MULTIHELPER_RESPONSE_ROUTING','census':dict(census),'positives':found,'cases':cases,'seconds':monotonic()-started,
            'target_only':args.target_only,'source_sha256':{str(p.relative_to(ROOT)):sha256(p.read_bytes()).hexdigest() for p in paths},
            'scope':'All helper A reads of one constant donor epoch replaced together, at first/middle/last original cut (or all cuts if requested), using a greedy exact weighted basis of203 protected output-response columns. Literal full-dirty repair and native admission are distinct gates.'}
    (args.output/'RESULT.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n');print('DONE',dict(census),flush=True)


if __name__=='__main__':main()
