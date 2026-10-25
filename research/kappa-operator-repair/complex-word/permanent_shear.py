#!/usr/bin/env python3
"""Permanent early helper-basis shears with all producer/consumer gates changed.

P=I+t E_(q,p) is inserted at frame zero after the protected prelude. Every
later scalar gate M is conjugated to P M P^-1. The pair has no warp or COPY
anchor and both helpers have zero entrance and full exit. All other output
rows are algebraically preserved; literal cleanup and the dirty gate still
check the construction, and every changed native path is repriced.
"""
from argparse import ArgumentParser
from collections import Counter,defaultdict
from copy import deepcopy
from fractions import Fraction as Q
from hashlib import sha256
from itertools import combinations
from pathlib import Path
from time import monotonic
import gzip,json
from network_search import ROOT,HERE,FROZEN,F,O,OLD,trace,canonical,repair,encode_sections,allowed_helpers


def gate(d,s,c,frame):return ['add',d,s,c.numerator,c.denominator,list(frame)]


def commute(a,b):
    return a[0]=='add' and b[0]=='add' and a[1]!=b[2] and a[2]!=b[1]


def simplify(events):
    out=[]
    for e in events:
        if e[0]=='add':
            merged=False
            for i in range(len(out)-1,max(-1,len(out)-65),-1):
                a=out[i]
                if a[-1]!=e[-1]:break
                if a[0]=='add' and a[1:3]==e[1:3]:
                    c=Q(a[3],a[4])+Q(e[3],e[4])
                    if c:out[i]=gate(e[1],e[2],c,e[-1])
                    else:del out[i]
                    merged=True;break
                if not commute(a,e):break
            if not merged:out.append(e)
        else:out.append(e)
    return out


def translate(e,p,q,t):
    kind,d=e[:2];frame=e[-1]
    if kind=='warp':assert d not in (p,q);return [e]
    if kind=='scale':
        if d not in (p,q):return [e]
        # P M P^-1 is a scale plus one exactly dyadic shear.
        c=Q(e[2],e[3])
        if d==p:return [e,gate(q,p,t*(c-1)/c,frame)] if c!=1 else []
        return [e,gate(q,p,t*(1-c),frame)] if c!=1 else []
    assert kind=='add';s=e[2];c=Q(e[3],e[4])
    if d not in (p,q) and s not in (p,q):return [e]
    if d==q and s==p:return [e]  # the same shear subgroup commutes
    if d==p and s==q:
        # The three-gate word is always exactly dyadic and avoids divisions
        # by a potentially odd pivot in a Gaussian factorization.
        return [gate(q,p,-t,frame),e,gate(q,p,t,frame)]
    if d==p:return [e,gate(q,s,t*c,frame)]
    if d==q:return [e]
    if s==q:return [e,gate(d,p,-t*c,frame)]
    assert s==p;return [e]


def construct(word,p,q,t):
    sec=F.expand(word);out={};cut=word['prelude_events']
    for name in ('A','B','restore'):
        prefix=sec[name][:cut] if name=='A' else []
        translated=[]
        for e in sec[name][cut if name=='A' else 0:]:translated.extend(translate(e,p,q,t))
        out[name]=prefix+([gate(q,p,t,())] if name=='A' else [])+simplify(translated)
    return encode_sections(word,out)


def check_conjugation():
    """Check each translator branch on a complete rational scalar basis."""
    from exact_rows import execute
    tests=0
    for t in (Q(-2),Q(-1),Q(-1,2),Q(1,2),Q(1),Q(2)):
        for coefficient in (Q(-2),Q(-1),Q(-1,2),Q(1,2),Q(1),Q(2)):
            events=[gate(d,s,coefficient,()) for d in range(3) for s in range(3) if d!=s]
            events += [['scale',d,coefficient.numerator,coefficient.denominator,[]] for d in range(3)]
            for event in events:
                left={r:{(r,()):Q(1)} for r in range(3)};right=deepcopy(left)
                execute(left,gate(1,0,t,()))
                for e in translate(event,0,1,t):execute(left,e)
                execute(right,event);execute(right,gate(1,0,t,()))
                assert left==right,(t,event,translate(event,0,1,t));tests+=1
    return tests


def main():
    ap=ArgumentParser(description=__doc__);ap.add_argument('--output',type=Path,required=True);ap.add_argument('--word',type=Path)
    ap.add_argument('--min-common',type=int,default=4);ap.add_argument('--max-common',type=int,default=10000)
    ap.add_argument('--max-optimize',type=int,default=0);ap.add_argument('--limit',type=int,default=0)
    args=ap.parse_args();args.output.mkdir(parents=True,exist_ok=True)
    translator_checks=check_conjugation()
    source=args.word or OLD/'candidate/BORROW-WORD-43base.json.gz';word=F.read(source);sec=F.expand(word)
    allowed=allowed_helpers(word)-set(word['centers'])
    allowed-={e[1] for name in ('A','B','restore') for e in sec[name] if e[0]=='warp'}
    used=defaultdict(set);coefficients=defaultdict(list)
    for e in word['A'][word['prelude_events']:]:
        if e[0]=='add' and e[1] in allowed:used[e[1]].add(e[2]);coefficients[e[1],e[2]].append(Q(e[3],e[4]))
    pairs=[(p,q,len(used[p]&used[q])) for p,q in combinations(sorted(allowed),2)
           if args.min_common<=len(used[p]&used[q])<=args.max_common]
    pairs.sort(key=lambda x:(-x[2],x[0],x[1]))
    base=Counter({int(r):c for r,c in word['report']['local_profile'].items()});census=Counter(eligible_helpers=len(allowed),pairs=len(pairs))
    started=monotonic();found=[];cases=[];hist=Counter();seen=set()
    for pair_index,(a,b,common) in enumerate(pairs):
        for p,q in ((a,b),(b,a)):
            values={Q(1),Q(-1)}
            for s in used[p]&used[q]:
                for c in coefficients[p,s]:
                    for d in coefficients[q,s]:
                        t=-d/c
                        if t and not t.denominator&(t.denominator-1) and abs(t)<=4:values.add(t)
            for t in sorted(values):
                if args.limit and census['constructed']>=args.limit:break
                census['constructed']+=1;candidate=construct(word,p,q,t)
                try:graph=O.graph(candidate)
                except (ValueError,AssertionError) as exc:census['global_frame_infeasible']+=1;hist[str(exc)[:120]]+=1;continue
                census['global_frame_feasible']+=1
                if args.max_optimize and census['joint_optimized']>=args.max_optimize:census['optimization_budget_skipped']+=1;continue
                try:candidate,opt=O.optimize(candidate)
                except (ValueError,AssertionError) as exc:census['optimizer_capacity_or_reject']+=1;continue
                census['joint_optimized']+=1;profile,_=trace(candidate);delta=profile.copy();delta.subtract(base)
                saving=-sum(c*F.phi(r) for r,c in delta.items())
                if saving<=1e-10:continue
                info={'p':p,'q':q,'t':str(t),'common_producers':common,'local_profile':dict(profile),
                      'delta':{r:c for r,c in delta.items() if c},'saving':saving,'optimization':opt}
                try:info['repair']=repair(candidate)
                except (ValueError,AssertionError) as exc:census['full_dirty_rejected']+=1;info['rejected']=str(exc)
                else:
                    payload=canonical(candidate);name=f'WORD-{p}-{q}-t{t.numerator}over{t.denominator}.json.gz';(args.output/name).write_bytes(gzip.compress(payload,mtime=0))
                    info.update(word=name,word_content_sha256=sha256(payload).hexdigest(),native_admission=False)
                    found.append(info);census['positive_exact']+=1;print('POSITIVE',json.dumps(info,sort_keys=True),flush=True)
                cases.append(info)
            if args.limit and census['constructed']>=args.limit:break
        if pair_index%10==0:print('PROGRESS',pair_index,dict(census),monotonic()-started,flush=True)
        if args.limit and census['constructed']>=args.limit:break
    paths=[Path(__file__),HERE/'network_search.py',source,FROZEN/'exact_rows.py',OLD/'opt_frames.py',OLD/'fanout_search.py']
    result={'status':'PERMANENT_ZERO_ENTRANCE_FULL_EXIT_HELPER_BASIS_SEARCH','census':dict(census),'positives':found,'cases':cases,
            'seconds':monotonic()-started,'infeasibility_histogram':dict(hist),'min_common':args.min_common,'max_common':args.max_common,
            'exact_translator_basis_checks':translator_checks,
            'source_sha256':{str(p.relative_to(ROOT)):sha256(p.read_bytes()).hexdigest() for p in paths},
            'scope':'Literal permanent single shears P=I+t E_(q,p) after protected prelude, paired helpers zero entrance/full exit and no warp or COPY. Every later producer/consumer gate conjugated. t=±1 or an exact dyadic producer-cancellation ratio of absolute value≤4. Global scalar frames vary; only the declared finite producer-overlap catalogue is searched.'}
    (args.output/'RESULT.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n');print('DONE',dict(census),flush=True)


if __name__=='__main__':main()
