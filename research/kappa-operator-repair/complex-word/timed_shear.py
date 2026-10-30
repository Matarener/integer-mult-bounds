#!/usr/bin/env python3
"""Paid later-cut helper-basis changes, including warm full-exit A helpers."""
from argparse import ArgumentParser
from collections import Counter,defaultdict
from fractions import Fraction as Q
from hashlib import sha256
from itertools import combinations
from pathlib import Path
from time import monotonic
import gzip,json
from network_search import ROOT,HERE,FROZEN,F,O,OLD,trace,canonical,repair,encode_sections
from permanent_shear import gate,translate,simplify,check_conjugation


def construct(word,p,q,t,cut):
    sec=F.expand(word);out={}
    for name in ('A','B','restore'):
        start=cut if name=='A' else 0
        translated=[]
        for e in sec[name][start:]:translated.extend(translate(e,p,q,t))
        out[name]=sec[name][:start]+([gate(q,p,t,())] if name=='A' else [])+simplify(translated)
    return encode_sections(word,out)


def main():
    ap=ArgumentParser(description=__doc__);ap.add_argument('--output',type=Path,required=True);ap.add_argument('--word',type=Path)
    ap.add_argument('--min-common',type=int,default=4);ap.add_argument('--max-pairs',type=int,default=0)
    ap.add_argument('--max-optimize',type=int,default=0);ap.add_argument('--limit',type=int,default=0)
    args=ap.parse_args();args.output.mkdir(parents=True,exist_ok=True);translator_checks=check_conjugation()
    source=args.word or OLD/'candidate/BORROW-WORD-43base.json.gz';word=F.read(source);sec=F.expand(word)
    allowed=set(range(224,704))-set(word['removed'])-set(map(int,word['helper_final']))-set(word['centers'])
    allowed-={e[1] for name in ('A','B','restore') for e in sec[name] if e[0]=='warp'}
    used=defaultdict(set);coefficients=defaultdict(list);positions=defaultdict(list)
    for i,e in enumerate(word['A']):
        if i>=word['prelude_events'] and e[0]=='add' and e[1] in allowed:
            used[e[1]].add(e[2]);coefficients[e[1],e[2]].append(Q(e[3],e[4]));positions[e[1],e[2]].append(i)
    pairs=[(p,q,len(used[p]&used[q])) for p,q in combinations(sorted(allowed),2) if len(used[p]&used[q])>=args.min_common]
    pairs.sort(key=lambda x:(-x[2],x[0],x[1]));selected=pairs[:args.max_pairs] if args.max_pairs else pairs
    base=Counter({int(r):c for r,c in word['report']['local_profile'].items()})
    census=Counter(eligible_helpers=len(allowed),pairs=len(pairs),selected_pairs=len(selected));found=[];cases=[];hist=Counter();started=monotonic()
    for pair_index,(a,b,common) in enumerate(selected):
        ps=sorted({i for s in used[a]&used[b] for r in (a,b) for i in positions[r,s]})
        cuts=sorted({ps[0],ps[len(ps)//2],ps[-1]})
        for p,q in ((a,b),(b,a)):
            values={Q(1),Q(-1)}
            for s in used[p]&used[q]:
                for c in coefficients[p,s]:
                    for d in coefficients[q,s]:
                        t=-d/c
                        if t and not t.denominator&(t.denominator-1) and abs(t)<=4:values.add(t)
            for cut in cuts:
                for t in sorted(values):
                    if args.limit and census['constructed']>=args.limit:break
                    census['constructed']+=1;candidate=construct(word,p,q,t,cut)
                    try:O.graph(candidate)
                    except (ValueError,AssertionError) as exc:census['global_frame_infeasible']+=1;hist[str(exc)[:120]]+=1;continue
                    census['global_frame_feasible']+=1
                    if args.max_optimize and census['joint_optimized']>=args.max_optimize:census['optimization_budget_skipped']+=1;continue
                    try:candidate,opt=O.optimize(candidate)
                    except (ValueError,AssertionError) as exc:census['optimizer_capacity_or_reject']+=1;continue
                    census['joint_optimized']+=1;profile,_=trace(candidate);delta=profile.copy();delta.subtract(base)
                    saving=-sum(c*F.phi(r) for r,c in delta.items())
                    if saving<=1e-10:continue
                    info={'p':p,'q':q,'t':str(t),'insertion_before_A':cut,'common_producers':common,'local_profile':dict(profile),
                          'delta':{r:c for r,c in delta.items() if c},'saving':saving,'optimization':opt,
                          'warm_helpers':[r for r in (p,q) if str(r) in word['start_extra']]}
                    try:info['repair']=repair(candidate)
                    except (ValueError,AssertionError) as exc:census['full_dirty_rejected']+=1;info['rejected']=str(exc)
                    else:
                        payload=canonical(candidate);name=f'WORD-{p}-{q}-cut{cut}-t{t.numerator}over{t.denominator}.json.gz';(args.output/name).write_bytes(gzip.compress(payload,mtime=0))
                        info.update(word=name,word_content_sha256=sha256(payload).hexdigest(),native_admission=False)
                        found.append(info);census['positive_exact']+=1;print('POSITIVE',json.dumps(info,sort_keys=True),flush=True)
                    cases.append(info)
                if args.limit and census['constructed']>=args.limit:break
            if args.limit and census['constructed']>=args.limit:break
        if pair_index%5==0:print('PROGRESS',pair_index,dict(census),monotonic()-started,flush=True)
        if args.limit and census['constructed']>=args.limit:break
    paths=[Path(__file__),HERE/'permanent_shear.py',HERE/'network_search.py',source,FROZEN/'exact_rows.py',OLD/'opt_frames.py',OLD/'fanout_search.py']
    result={'status':'TIMED_FULL_EXIT_HELPER_BASIS_SEARCH','census':dict(census),'positives':found,'cases':cases,'seconds':monotonic()-started,
            'infeasibility_histogram':dict(hist),'min_common':args.min_common,'max_pairs':args.max_pairs,
            'exact_translator_basis_checks':translator_checks,
            'source_sha256':{str(p.relative_to(ROOT)):sha256(p.read_bytes()).hexdigest() for p in paths},
            'scope':'All declared common-producer pairs of full-exit helpers without warp/COPY; warm entrances retained. Single shears at first/middle/last common producer cut, every later gate conjugated. Native scalar frames vary globally, including the new paid shear. Exact dyadic cancellation ratios and ±1 are searched; arbitrary GL or all cuts are not exhausted.'}
    (args.output/'RESULT.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n');print('DONE',dict(census),flush=True)


if __name__=='__main__':main()
