#!/usr/bin/env python3
"""Protected response resynthesis with globally movable scalar frames.

For each deleted A injection, recompute the entire chronological frame DAG.
Its least and greatest assignments bound a new common-frame receiver gate;
the complete changed graph is solved and the complete dirty law is checked.
This removes the fixed neighboring-frame restriction in the earlier search.
"""
from argparse import ArgumentParser
from collections import Counter
from copy import deepcopy
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
from time import monotonic
import gzip,json,sys
from network_search import ROOT,HERE,FROZEN,F,O,FULL,OLD,trace,canonical,add,repair,encode_sections,future_caps,normalized
from response_routes import backward
sys.path.insert(0,str(FROZEN.parent))
from complex_projection_screen import combination


def ranges(word,cut):
    sec,nodes,frames,edges,lo,hi,comps=O.graph(word)
    low=deepcopy(sec);high=deepcopy(sec)
    for j,(name,index) in enumerate(nodes):
        low[name][index][-1]=list(lo[j]);high[name][index][-1]=list(hi[j])
    live=set(range(704))-set(word['removed'])
    current={r:F.basis((word['ports'][r],)) if r<112 else F.basis(tuple(word['start_extra'].get(str(r),()))) for r in live}
    for e in low['A'][:cut]:
        if e[0]=='warp':current[e[1]]=F.basis(tuple(e[4]))
        else:
            for r in F.regs(e):current[r]=F.basis(tuple(e[-1]))
    caps=future_caps(word,high)['A'][cut]
    return current,caps


def main():
    ap=ArgumentParser(description=__doc__);ap.add_argument('--output',type=Path,required=True)
    ap.add_argument('--word',type=Path);ap.add_argument('--target-only',action='store_true')
    ap.add_argument('--max-optimize',type=int,default=0);ap.add_argument('--spans',action='store_true')
    args=ap.parse_args();args.output.mkdir(parents=True,exist_ok=True)
    source=args.word or OLD/'candidate/BORROW-WORD-43base.json.gz';word=F.read(source);sec=F.expand(word)
    live=set(range(704))-set(word['removed']);outputs=set(range(112,224))|(set() if args.target_only else set(map(int,word['helper_final'])))
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
    original_caps=future_caps(word,sec)['A'];base=Counter({int(r):c for r,c in word['report']['local_profile'].items()})
    census=Counter();found=[];cases=[];started=monotonic();seen_graphs=set()
    for index in reversed(range(len(sec['A']))):
        event=sec['A'][index]
        if index>=word['prelude_events'] and event[0]=='add' and event[1]>=224:
            d,s=event[1:3];oldframe=F.basis(tuple(event[-1]));cur=starts[index];cap=original_caps[index+1]
            removed_cost=F.phi(len(oldframe)-len(cur[d]))+F.phi(len(cap[d])-len(oldframe))-F.phi(len(cap[d])-len(cur[d]))
            if removed_cost>1e-10:
                census['injection_queries']+=1
                es=deepcopy(sec);del es['A'][index];deleted=encode_sections(word,es)
                low,high=ranges(deleted,index);coefficient=Q(event[3],event[4]);wanted={k:coefficient*v for k,v in cols[d].items()}
                target_key,target_factor=normalized(wanted);solutions=[]
                if not wanted:solutions.append(((),{}))
                options={low[s],high[s],oldframe}
                for q in sorted(live):
                    if q==d or not cols[q]:continue
                    frame=F.basis(low[s]+low[q])
                    if not F.contains(frame,high[s]) or not F.contains(frame,high[q]):continue
                    options.add(frame)
                    k,f=normalized(cols[q])
                    if k==target_key:
                        value=target_factor/f
                        if not value.denominator&(value.denominator-1):solutions.append((frame,{q:value}));census['single_column_solutions']+=1
                if args.spans:
                    for frame in sorted(options,key=lambda f:(len(f),f)):
                        if not F.contains(low[s],frame) or not F.contains(frame,high[s]):continue
                        available=[q for q in sorted(live) if q!=d and cols[q] and F.contains(low[q],frame) and F.contains(frame,high[q])]
                        # Preference changes only the witness chosen by exact
                        # elimination; no numerical coefficient is admitted.
                        available.sort(key=lambda q:(not (F.contains(cur[q],frame) and F.contains(frame,cap[q])),
                                                     0 if cur[q]==frame or cap[q]==frame else 1,len(cols[q]),q))
                        for subset in (available,list(reversed(available))):
                            census['exact_span_queries']+=1
                            answer=combination(wanted,subset,cols)
                            if answer is not None:solutions.append((frame,answer));census['span_solutions']+=1
                seen=set()
                for frame,support in solutions:
                    signature=tuple(sorted(support.items()))
                    # Scalar graph optimization discards placeholder frames;
                    # equivalent supports therefore need only one solve.
                    if signature in seen:continue
                    seen.add(signature)
                    new=[['add',q,s,a.numerator,a.denominator,list(frame)] for q,a in sorted(support.items()) if q!=s and a]
                    if s in support:
                        factor=1+support[s]
                        if not factor or abs(factor.numerator)&(abs(factor.numerator)-1):continue
                        new.append(['scale',s,factor.numerator,factor.denominator,list(frame)])
                    graph_key=(index,tuple(tuple(e[:-1]) for e in new))
                    if graph_key in seen_graphs:continue
                    seen_graphs.add(graph_key)
                    es2=deepcopy(sec);es2['A'][index:index+1]=new;candidate=encode_sections(word,es2)
                    try:O.graph(candidate)
                    except (ValueError,AssertionError) as exc:census['global_graph_rejected']+=1;continue
                    census['global_graph_feasible']+=1
                    if args.max_optimize and census['joint_optimized']>=args.max_optimize:census['optimization_budget_skipped']+=1;continue
                    try:candidate,opt=O.optimize(candidate)
                    except (ValueError,AssertionError) as exc:census['optimizer_capacity_or_reject']+=1;continue
                    census['joint_optimized']+=1;profile,_=trace(candidate);delta=profile.copy();delta.subtract(base)
                    saving=-sum(c*F.phi(r) for r,c in delta.items())
                    if saving<=1e-10:continue
                    info={'old_A_index':index,'old':event,'new':new,'delta':{r:c for r,c in delta.items() if c},
                          'saving':saving,'optimization':opt,'protected_outputs':len(outputs)}
                    try:info['repair']=repair(candidate)
                    except (AssertionError,ValueError) as exc:census['full_dirty_rejected']+=1;info['rejected']=str(exc)
                    else:
                        payload=canonical(candidate);name=f'WORD-A{index}-{len(found)}.json.gz';(args.output/name).write_bytes(gzip.compress(payload,mtime=0))
                        info.update(word=name,word_content_sha256=sha256(payload).hexdigest(),local_profile=dict(profile),native_admission=False)
                        found.append(info);census['positive_exact']+=1;print('POSITIVE',json.dumps(info,sort_keys=True),flush=True)
                    cases.append(info)
        backward(cols,event)
        if index%250==0:print('PROGRESS',index,dict(census),monotonic()-started,flush=True)
    paths=[Path(__file__),HERE/'response_routes.py',HERE/'network_search.py',source,FROZEN/'exact_rows.py',FROZEN.parent/'complex_projection_screen.py',OLD/'opt_frames.py']
    result={'status':'COMPLEX_PROTECTED_RESPONSE_GLOBAL_FRAME_SEARCH','protected_outputs':len(outputs),'target_only':args.target_only,
            'census':dict(census),'positives':found,'cases':cases,'seconds':monotonic()-started,
            'source_sha256':{str(p.relative_to(ROOT)):sha256(p.read_bytes()).hexdigest() for p in paths},
            'scope':'Every paid-stop A injection into a helper, replacing its response by one or arbitrary many same-input receivers at one cut. Global least/greatest native frame assignments are recomputed after deletion. Exact weighted basis witnesses are heuristic; all feasible dyadic networks are not enumerated. Exact complete dirty repair and independent native admission remain separate gates.'}
    (args.output/'RESULT.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n');print('DONE',dict(census),flush=True)


if __name__=='__main__':main()
