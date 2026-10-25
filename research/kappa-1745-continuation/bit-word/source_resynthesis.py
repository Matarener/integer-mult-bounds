#!/usr/bin/env python3
"""Rewrite SOURCE increments, freeing all intermediate dirty responses.

Every A/B destination keeps its original SOURCE value after each consecutive
same-frame destination block. Donors can change, and the actual resulting raw
dirty matrix regenerates D. C is the literal inverse. No clean ancilla is
assumed. Candidates are independently checked on all arbitrary columns.
Apache-2.0; substantial OpenAI assistance under the user's direction.
"""
from bisect import bisect_right
from collections import Counter, defaultdict
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import argparse, gzip, json, random, time

from search_networks import ROOT, HERE, OLD, SOURCE, CHECKER, EXPECTED, read, canonical, cleanup, scalar, load_checker, actual_profile, Optimizer
from source_quotient import regenerate_D


def blocks(word):
    out=[]
    for section in ('A','B'):
        for gi,(f,d,ss) in enumerate(word[section]):
            if out and out[-1][0]==section and out[-1][2:4]==[f,d]:
                out[-1][4].extend(ss);out[-1][1].append(gi)
            else:out.append([section,[gi],f,d,list(ss)])
        if section=='A':out.append(['capture',[],None,None,None])
    return out


def synthesize(word, dimensions, capture_frames, seed=0, max_terms=2, section_filter='both'):
    n=2*word['v']+word['R'];v=word['v'];events=blocks(word)
    masks=[sum(1<<r for r in f) for f in word['frames']]
    nested=lambda a,b:not (masks[a]&~masks[b])
    price=[r**(1-.001745) if r else 0.0 for r in range(9)]
    contacts=defaultdict(list)
    for i,(section,groups,f,d,ss) in enumerate(events):
        if section=='capture':
            for r,cf in capture_frames.items():contacts[r].append((i,cf))
        else:
            for r in {d,*ss}:contacts[r].append((i,f))
    for r,f in enumerate(word['final']):contacts[r].append((len(events),f))
    keys={r:[i for i,f in contacts[r]] for r in range(n)}
    cur=list(word['start']);values=[1<<r if r<v else 0 for r in range(n)]
    out=deepcopy(word);out['A']=[];out['B']=[];notes=[];stats=Counter();rng=random.Random(seed)
    # Random priorities are only tie breakers. All actual tariff comparisons
    # use the same local moment at the requested endpoint.
    tie=[rng.random() if seed else float(r) for r in range(n)]
    def climb(r,f):
        assert nested(cur[r],f),(r,cur[r],f)
        cur[r]=f
    for i,(section,groups,f,d,ss) in enumerate(events):
        if section=='capture':
            assert all(cur[r]==cf for r,cf in capture_frames.items())
            continue
        wanted=0
        for s in ss:wanted^=values[s]
        original=sorted(r for r,count in Counter(ss).items() if count%2)
        if section_filter!='both' and section_filter!=section:
            support=original;bestcost=None;oldcost=None;donor_count=0
        else:
            rows={};costs={};donor_count=0
            for r in range(n):
                if r==d or v<=r<2*v or not values[r] or not nested(cur[r],f):continue
                upper=contacts[r][bisect_right(keys[r],i)][1]
                if not nested(f,upper):continue
                cost=price[dimensions[f]-dimensions[cur[r]]]+price[dimensions[upper]-dimensions[f]]-price[dimensions[upper]-dimensions[cur[r]]]
                costs[r]=cost;donor_count+=1
                rank=(cost,cur[r]!=f,tie[r])
                row=values[r]
                if row not in rows or rank<rows[row][0]:rows[row]=(rank,r)
            oldcost=sum(costs.get(r,0.0) for r in original)
            choices=[(oldcost,len(original),sum(cur[r]!=f for r in original),sum(tie[r] for r in original),original)]
            if not wanted:choices.append((0.0,0,0,0.0,[]))
            if wanted in rows:
                r=rows[wanted][1];choices.append((costs[r],1,int(cur[r]!=f),tie[r],[r]))
            if max_terms>=2:
                for row,(rank,r) in rows.items():
                    other=rows.get(row^wanted)
                    if other is None:continue
                    s=other[1]
                    if r>=s:continue
                    choices.append((costs[r]+costs[s],2,int(cur[r]!=f)+int(cur[s]!=f),tie[r]+tie[s],[r,s]))
            if max_terms>=3:
                rs=list(rows.items())
                for j,(row,(_,r)) in enumerate(rs):
                    for row2,(_,s) in rs[j+1:]:
                        third=rows.get(row^row2^wanted)
                        if third is None:continue
                        t=third[1]
                        if t in (r,s) or t<max(r,s):continue
                        support3=[r,s,t]
                        choices.append((sum(costs[q] for q in support3),3,sum(cur[q]!=f for q in support3),sum(tie[q] for q in support3),support3))
            # Round away sub-ulp arithmetic differences in equal tariff sums.
            chosen=min(choices,key=lambda x:(round(x[0],12),x[1],x[2],x[3]))
            bestcost=chosen[0];support=chosen[-1]
        reconstructed=0
        for r in support:reconstructed^=values[r]
        assert reconstructed==wanted
        if support:
            climb(d,f)
            for r in support:climb(r,f)
            out[section].append([f,d,support])
        values[d]^=wanted
        stats['blocks']+=1
        if support!=original:
            stats['changed_blocks']+=1;stats['old_ADDs_changed']+=len(original);stats['new_ADDs_changed']+=len(support)
            notes.append({'section':section,'groups':groups,'event':i,'frame':f,'destination':d,
                          'SOURCE_increment':hex(wanted),'old_sources':original,'new_sources':support,
                          'old_contact_penalty':oldcost,'new_contact_penalty':bestcost,'donor_count':donor_count})
    regenerate_D(out);scalar(out)
    return out,{'seed':seed,'max_terms':max_terms,'section_filter':section_filter,'stats':dict(stats),'edits':notes,
                'old_D_ADD_count':sum(len(g[2]) for g in word['D']),
                'D_ADD_count':sum(len(g[2]) for g in out['D'])}


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--word',type=Path,default=SOURCE)
    ap.add_argument('--expected-sha',default=EXPECTED)
    ap.add_argument('--seeds',type=int,default=4)
    ap.add_argument('--max-terms',type=int,choices=(1,2,3),default=2)
    ap.add_argument('--passes',type=int,default=3)
    ap.add_argument('--section',choices=('A','B','both'),default='both')
    ap.add_argument('--optimize',action='store_true')
    args=ap.parse_args();args.out.mkdir(parents=True,exist_ok=True)
    raw=gzip.decompress(args.word.read_bytes());assert sha256(raw).hexdigest()==args.expected_sha
    word=json.loads(raw);word['frames']=read(OLD/'enriched-frames/CATALOGUE-WORD.json.gz')['frames']
    module=load_checker(CHECKER);checker=module.Word(word);checker.full()
    optimizer=Optimizer(word,checker,.001745);base=actual_profile(word,checker)
    price=optimizer.price;best=deepcopy(word);bestvalue=sum(price[r]*c for r,c in base.items())
    pins=[args.word,CHECKER,OLD/'enriched-frames/CATALOGUE-WORD.json.gz',OLD/'bit_pair_search.py',OLD/'bit_joint_frames.py',HERE/'search_networks.py',HERE/'source_quotient.py',Path(__file__)]
    sources={str(p.relative_to(ROOT)):sha256(p.read_bytes()).hexdigest() for p in pins}
    results=[];t0=time.monotonic()
    for trial in range(args.passes):
        startword=best
        for seed in range(args.seeds):
            out,identity=synthesize(startword,checker.fdim,optimizer.captures,seed,args.max_terms,args.section)
            exact=module.Word(out);columns=exact.full();hypotheses,conclusion,_=exact.interface()
            assert all(hypotheses.values()) and all(conclusion.values())
            profile=actual_profile(out,exact);value=sum(price[r]*c for r,c in profile.items())
            frame_result=None
            if args.optimize and identity['stats'].get('changed_blocks',0):
                try:
                    optimized,info=optimizer.optimize(out)
                    exact2=module.Word(optimized);exact2.full()
                    profile2=actual_profile(optimized,exact2)
                    assert dict(profile2)==info['local_profile']
                    value2=sum(price[r]*c for r,c in profile2.items())
                    if value2<value-1e-10:out,profile,value,frame_result=optimized,profile2,value2,info
                except ValueError as exc:frame_result={'rejected':str(exc)}
            delta=profile.copy();delta.subtract(base)
            row={'pass':trial,'seed':seed,'identity':identity,'profile':dict(profile),
                 'delta':{r:c for r,c in delta.items() if c},'saving':sum(price[r]*c for r,c in base.items())-value,
                 'independent_columns':columns,'hypotheses':hypotheses,'conclusion':conclusion,
                 'frame_optimization':frame_result,'A_ADD_count':sum(len(g[2]) for g in out['A']),
                 'B_ADD_count':sum(len(g[2]) for g in out['B']),'C_ADD_count':sum(len(g[2]) for g in out['C']),
                 'D_ADD_count':sum(len(g[2]) for g in out['D'])}
            if value<bestvalue-1e-10:
                payload=canonical(out);name=f'PASS{trial}-SEED{seed}.json.gz'
                (args.out/name).write_bytes(gzip.compress(payload,mtime=0))
                row['word']=name;row['content_sha256']=sha256(payload).hexdigest();best=out;bestvalue=value
            results.append(row)
            print('RESULT',trial,seed,'changes',identity['stats'].get('changed_blocks',0),'saving',row['saving'],'delta',row['delta'],'D',row['D_ADD_count'],flush=True)
        if best==startword:break
    result={'status':'FINITE_SOURCE_PROJECTION_WHOLE_WORD_RESYNTHESIS','source_word_content_sha256':args.expected_sha,
            'source_sha256':sources,'results':results,'seconds':time.monotonic()-t0,
            'scope':'Every retained SOURCE projection after each consecutive same-frame destination block is preserved; intermediate dirty responses may change. D is regenerated from actual raw columns, C is literal inverse. One/two/three-donor choices use current frames and next retained original contact upper bounds. This is a finite greedy search, not a general graph impossibility claim. Hosted/native/whole-word/coefficient invoices remain separate.'}
    (args.out/'RESULT.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
    print('DONE',time.monotonic()-t0,flush=True)


if __name__=='__main__':main()
