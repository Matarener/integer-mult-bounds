#!/usr/bin/env python3
"""Delay the complete helper birth until its first actual A read or COPY.

The destination's initial dirty value remains arbitrary. All writes before
its first read/COPY are replaced by an exact compatible SOURCE span immediately
before that observer, at its frame. Actual changed dirty columns determine D, with literal
C inverse. Apache-2.0; OpenAI assistance under user direction.
"""
from bisect import bisect_right
from collections import Counter,defaultdict
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import argparse,gzip,json,random,time
from search_networks import ROOT,HERE,OLD,SOURCE,CHECKER,EXPECTED,read,canonical,cleanup,scalar,load_checker,actual_profile,Optimizer
from source_quotient import regenerate_D
from observation_repair import representation


def build(word,helper,dimensions,capture_frames,seed=0):
    n=2*word['v']+word['R'];v=word['v'];masks=[sum(1<<r for r in f) for f in word['frames']]
    nested=lambda a,b:not(masks[a]&~masks[b])
    price=[r**(1-.001745) if r else 0.0 for r in range(9)]
    prefix=[];cut=None;f=None
    for gi,(f,d,ss) in enumerate(word['A']):
        if helper in ss:cut=gi;break
        if d==helper:prefix.append(gi)
    if not prefix:raise ValueError(('empty_prefix',0))
    if cut is None:
        if helper not in capture_frames:raise ValueError(('no_A_or_COPY_observer',helper))
        cut=len(word['A']);f=capture_frames[helper]
    deleted=set(prefix)
    if all(word['A'][i][0]==f for i in prefix):raise ValueError(('single_frame_prefix',f))
    cur=list(word['start']);values=[1<<r if r<v else 0 for r in range(n)];want=0
    for gi,(gf,d,ss) in enumerate(word['A'][:cut]):
        if gi not in deleted:
            for r in [d]+ss:cur[r]=gf
        for s in ss:values[d]^=values[s]
    wanted=values[helper];assert cur[helper]==word['start'][helper]==0
    contacts=defaultdict(list)
    for gi,(gf,d,ss) in enumerate(word['A']):
        if gi<cut:continue
        for r in {d,*ss}:contacts[r].append(gf)
    for r,cf in capture_frames.items():contacts[r].append(cf)
    for gf,d,ss in word['B']:
        for r in {d,*ss}:contacts[r].append(gf)
    for r,gf in enumerate(word['final']):contacts[r].append(gf)
    rng=random.Random(seed);tie=[rng.random() if seed else float(r) for r in range(n)]
    rows=[]
    for r in range(n):
        if r==helper or v<=r<2*v or not values[r] or not nested(cur[r],f):continue
        upper=contacts[r][0]
        if not nested(f,upper):continue
        cost=price[dimensions[f]-dimensions[cur[r]]]+price[dimensions[upper]-dimensions[f]]-price[dimensions[upper]-dimensions[cur[r]]]
        rows.append((r,values[r],cost,tie[r]))
    try:support=representation(rows,wanted,seed)
    except ValueError as exc:raise ValueError(('late_prefix_SOURCE_span',helper,prefix,cut,f,hex(wanted),exc.args[0]))
    if not support:raise ValueError(('zero_SOURCE_prefix',helper))
    restored=0
    for r in support:restored^=values[r]
    assert restored==wanted
    out=deepcopy(word);out['A']=[]
    for gi,g in enumerate(word['A']):
        if gi==cut:out['A'].append([f,helper,support])
        if gi not in deleted:out['A'].append(g)
    if cut==len(word['A']):out['A'].append([f,helper,support])
    cleanup(out)
    profile=Counter();cur=list(word['start'])
    for section in ('A','B','C'):
        for gf,d,ss in out[section]:
            for r in [d]+ss:
                if not nested(cur[r],gf):raise ValueError(('candidate_nonmonotone',section,r,cur[r],gf))
                jump=dimensions[gf]-dimensions[cur[r]]
                if jump:profile[jump]+=1
                cur[r]=gf
        if section=='A':
            assert all(cur[r]==cf for r,cf in capture_frames.items())
            profile.update(dimensions[cur[r]] for r in word['ret'])
    for r,gf in enumerate(word['final']):
        assert nested(cur[r],gf)
        jump=dimensions[gf]-dimensions[cur[r]]
        if jump:profile[jump]+=1
    identity={'helper':helper,'observer_A_group':cut,'deleted_A_groups':prefix,'old_prefix':[word['A'][i] for i in prefix],
              'new_birth':[f,helper,support],'SOURCE_row':hex(wanted),'compatible_donors':len(rows),
              'profile':dict(profile),'seed':seed}
    return out,identity


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--word',type=Path,default=SOURCE);ap.add_argument('--expected-sha',default=EXPECTED)
    ap.add_argument('--out',type=Path,required=True);ap.add_argument('--seed',type=int,default=0)
    ap.add_argument('--passes',type=int,default=2);ap.add_argument('--independent',action='store_true')
    args=ap.parse_args();args.word=args.word.resolve();args.out.mkdir(parents=True,exist_ok=True)
    raw=gzip.decompress(args.word.read_bytes());assert sha256(raw).hexdigest()==args.expected_sha
    source=json.loads(raw);source['frames']=read(OLD/'enriched-frames/CATALOGUE-WORD.json.gz')['frames']
    module=load_checker(CHECKER);checker=module.Word(source);checker.full();optimizer=Optimizer(source,checker,.001745)
    baseline=actual_profile(source,checker);word=source;price=optimizer.price
    best=sum(price[r]*c for r,c in baseline.items());stats=Counter();positives=[];rejects=[];t0=time.monotonic()
    for trial in range(args.passes):
        entered=best
        for helper in range(2*word['v'],2*word['v']+word['R']):
            if helper==469:continue
            stats['attempted']+=1
            try:out,identity=build(source if args.independent else word,helper,checker.fdim,optimizer.captures,args.seed)
            except ValueError as exc:
                stats[str(exc.args[0][0])]+=1;rejects.append({'pass':trial,'helper':helper,'reason':exc.args[0]});continue
            stats['SOURCE_prefix_rebuilt']+=1
            profile=Counter({int(r):c for r,c in identity['profile'].items()});value=sum(price[r]*c for r,c in profile.items())
            threshold=sum(price[r]*c for r,c in baseline.items()) if args.independent else best
            if value>=threshold-1e-9:stats['not_better']+=1;continue
            regenerate_D(out);scalar(out);native=module.Word(out);columns=native.full();hs,cs,_=native.interface()
            assert all(hs.values()) and all(cs.values());assert dict(actual_profile(out,native))==identity['profile']
            payload=canonical(out);name=f'PASS{trial}-HELPER{helper}.json.gz';(args.out/name).write_bytes(gzip.compress(payload,mtime=0))
            delta=profile.copy();delta.subtract(baseline)
            row={'pass':trial,'helper':helper,'word':name,'content_sha256':sha256(payload).hexdigest(),'identity':identity,
                 'profile':dict(profile),'delta':{r:c for r,c in delta.items() if c},
                 'saving':sum(price[r]*c for r,c in baseline.items())-value,'columns':columns,'hypotheses':hs,'conclusion':cs,
                 'counts':{s:sum(len(g[2]) for g in out[s]) for s in ('D','A','B','C')}}
            positives.append(row);stats['positive']+=1
            if not args.independent:word=out;best=value
            print('FOUND',trial,helper,'saving',row['saving'],'delta',row['delta'],'D',row['counts']['D'],flush=True)
        if best==entered:break
    pins=[args.word,CHECKER,OLD/'enriched-frames/CATALOGUE-WORD.json.gz',OLD/'bit_pair_search.py',OLD/'bit_joint_frames.py',HERE/'search_networks.py',HERE/'source_quotient.py',HERE/'source_resynthesis.py',HERE/'observation_repair.py',Path(__file__)]
    result={'status':'FINITE_FIRST_OBSERVER_BIRTH_PREFIX_SOURCE_RESYNTHESIS','source_content_sha256':args.expected_sha,
            'source_sha256':{str(p.relative_to(ROOT)):sha256(p.read_bytes()).hexdigest() for p in pins},
            'stats':dict(stats),'positives':positives,'rejections':rejects,'seconds':time.monotonic()-t0,
            'scope':'Only writes before the first SOURCE read/COPY of a helper are replaced; its exact SOURCE row is reconstructed immediately before its first observer. Arbitrary initial dirt persists and actual D/C are regenerated. Greedy compatible donor basis with fixed original later contacts; no general impossibility is claimed.'}
    (args.out/'RESULT.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
    print('DONE',dict(stats),'seconds',time.monotonic()-t0,flush=True)


if __name__=='__main__':main()
