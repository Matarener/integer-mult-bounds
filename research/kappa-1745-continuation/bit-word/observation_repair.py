#!/usr/bin/env python3
"""Delete upstream updates; repair only COPY and productive observations.

Intermediate SOURCE and dirty rows may change. The exact nine COPY SOURCE
rows and each productive B increment are reconstructed from current compatible
register rows. The resulting raw dirty operator regenerates D; C is literal
inverse. No zero-filled dirty ancilla is assumed.
Apache-2.0; substantial OpenAI assistance under the user's direction.
"""
from bisect import bisect_right
from collections import Counter,defaultdict
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import argparse,gzip,json,random,time
from search_networks import ROOT,HERE,OLD,SOURCE,CHECKER,EXPECTED,read,canonical,cleanup,scalar,load_checker,actual_profile,Optimizer
from source_quotient import regenerate_D
from source_resynthesis import blocks


def representation(rows,wanted,seed=0):
    if not wanted:return []
    # One cheapest role per current SOURCE row. Basis elimination retains
    # exact support identities, including arbitrary combinations.
    distinct={}
    for r,row,cost,tie in rows:
        if row not in distinct or (cost,tie)<distinct[row][0]:distinct[row]=((cost,tie),r)
    ordered=sorted(((r,row,rank[0],rank[1]) for row,(rank,r) in distinct.items()),key=lambda x:(round(x[2],12),x[3]))
    costs={r:c for r,row,c,tie in ordered};choices=[]
    if wanted in distinct:
        r=distinct[wanted][1];choices.append([r])
    for row,(rank,r) in distinct.items():
        other=distinct.get(row^wanted)
        if other and r<other[1]:choices.append([r,other[1]])
    basis={}
    for r,row,cost,tie in ordered:
        support=1<<r
        while row:
            p=row.bit_length()-1
            if p not in basis:basis[p]=(row,support);break
            x,s=basis[p];row^=x;support^=s
    row=wanted;support=0
    while row:
        p=row.bit_length()-1
        if p not in basis:break
        x,s=basis[p];row^=x;support^=s
    if not row:choices.append([r for r in costs if support>>r&1])
    if not choices:raise ValueError(('observation_span',hex(wanted),hex(row),len(rows),len(basis)))
    return min(choices,key=lambda ss:(round(sum(costs[r] for r in ss),12),len(ss),ss))


class Builder:
    def __init__(self,word,checker,relaxed=False,seed=0):
        self.word=word;self.v=word['v'];self.n=2*self.v+word['R'];self.events=blocks(word)
        self.dim=checker.fdim;self.masks=[sum(1<<i for i in f) for f in word['frames']]
        self.price=[r**(1-.001745) if r else 0.0 for r in range(9)]
        self.relaxed=relaxed;self.seed=seed
        self.original_caps=Optimizer(word,checker,.001745).captures
        self.ref_before=[];values=[1<<r if r<self.v else 0 for r in range(self.n)]
        for section,groups,f,d,ss in self.events:
            if section=='capture':self.capture_rows={r:values[r] for r in word['ret']};self.ref_before.append(None)
            else:
                wanted=0
                for s in ss:wanted^=values[s]
                self.ref_before.append(wanted);values[d]^=wanted

    def nested(self,a,b):return not(self.masks[a]&~self.masks[b])

    def build(self,drop):
        word=self.word;v=self.v;n=self.n
        # Drop uses original section/group identifiers, preserving grouped
        # source order when only one scalar update is removed.
        events=[]
        for section in ('A','B'):
            for gi,(f,d,ss) in enumerate(word[section]):
                if (section,gi) not in drop:events.append((section,gi,f,d,list(ss)))
            if section=='A':events.append(('capture',-1,None,None,None))
        # The reference stream is evaluated separately so deleted writes do
        # not silently alter any desired COPY or productive SOURCE query.
        desired={};ref=[1<<r if r<v else 0 for r in range(n)]
        for section in ('A','B'):
            for gi,(f,d,ss) in enumerate(word[section]):
                inc=0
                for s in ss:inc^=ref[s]
                desired[section,gi]=inc;ref[d]^=inc
        contacts=defaultdict(list)
        for i,(section,gi,f,d,ss) in enumerate(events):
            if section=='capture':
                for r,cf in self.original_caps.items():contacts[r].append((i,cf))
            else:
                roles={d} if self.relaxed and v<=d<2*v else {d,*ss}
                for r in roles:contacts[r].append((i,f))
        for r,f in enumerate(word['final']):contacts[r].append((len(events),f))
        keys={r:[i for i,f in contacts[r]] for r in range(n)}
        values=[1<<r if r<v else 0 for r in range(n)];cur=list(word['start'])
        out=deepcopy(word);out['A']=[];out['B']=[];notes=[];rng=random.Random(self.seed)
        tie=[rng.random() if self.seed else float(r) for r in range(n)]
        def emit(section,f,d,ss):
            if not ss:return
            for r in [d]+ss:
                if not self.nested(cur[r],f):raise ValueError(('nonmonotone',section,r,cur[r],f))
                cur[r]=f
            out[section].append([f,d,ss])
            for s in ss:values[d]^=values[s]
        def donors(i,f,d,wanted):
            rows=[]
            for r in range(n):
                if r==d or v<=r<2*v or not values[r] or not self.nested(cur[r],f):continue
                upper=contacts[r][bisect_right(keys[r],i)][1]
                if not self.nested(f,upper):continue
                cost=self.price[self.dim[f]-self.dim[cur[r]]]+self.price[self.dim[upper]-self.dim[f]]-self.price[self.dim[upper]-self.dim[cur[r]]]
                rows.append((r,values[r],cost,tie[r]))
            try:return representation(rows,wanted,self.seed)
            except ValueError as exc:raise ValueError(('observation_span',i,d,f,exc.args[0]))
        for i,(section,gi,f,d,ss) in enumerate(events):
            if section=='capture':
                for r in word['ret']:
                    f=self.original_caps[r];wanted=self.capture_rows[r]^values[r]
                    if wanted:
                        support=donors(i,f,r,wanted);emit('A',f,r,support)
                        notes.append({'kind':'COPY_repair','role':r,'frame':f,'sources':support,'SOURCE_increment':hex(wanted)})
                    if cur[r]!=f:raise ValueError(('capture_frame_not_emitted',r,cur[r],f))
                    assert values[r]==self.capture_rows[r]
                continue
            if v<=d<2*v:
                wanted=desired[section,gi]
                actual=0
                for s in ss:actual^=values[s]
                if actual==wanted and all(self.nested(cur[s],f) for s in ss):emit(section,f,d,ss)
                else:
                    support=donors(i,f,d,wanted);emit(section,f,d,support)
                    notes.append({'kind':'productive_query','section':section,'group':gi,'role':d,'frame':f,
                                  'old_sources':ss,'sources':support,'SOURCE_increment':hex(wanted)})
            else:emit(section,f,d,ss)
        cleanup(out)
        # Price before full raw-column work. D is frame0, so its eventual
        # support cannot create a positive paid rank jump.
        profile=Counter();cur=list(word['start'])
        for section in ('A','B','C'):
            for f,d,ss in out[section]:
                for r in [d]+ss:
                    assert self.nested(cur[r],f)
                    jump=self.dim[f]-self.dim[cur[r]]
                    if jump:profile[jump]+=1
                    cur[r]=f
            if section=='A':profile.update(self.dim[cur[r]] for r in word['ret'])
        for r,f in enumerate(word['final']):
            assert self.nested(cur[r],f)
            jump=self.dim[f]-self.dim[cur[r]]
            if jump:profile[jump]+=1
        return out,{'deleted_original_groups':sorted(drop),'repairs':notes,'profile':dict(profile)}


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--word',type=Path,default=SOURCE);ap.add_argument('--expected-sha',default=EXPECTED)
    ap.add_argument('--out',type=Path,required=True);ap.add_argument('--relaxed-queries',action='store_true')
    ap.add_argument('--seed',type=int,default=0);ap.add_argument('--mode',choices=('birth','any_A','source_loads'),default='birth')
    ap.add_argument('--limit',type=int,default=100000);ap.add_argument('--start',type=int,default=0)
    ap.add_argument('--greedy',action='store_true');args=ap.parse_args();args.out.mkdir(parents=True,exist_ok=True)
    raw=gzip.decompress(args.word.read_bytes());assert sha256(raw).hexdigest()==args.expected_sha
    word=json.loads(raw);word['frames']=read(OLD/'enriched-frames/CATALOGUE-WORD.json.gz')['frames']
    module=load_checker(CHECKER);checker=module.Word(word);checker.full();baseline=actual_profile(word,checker)
    builder=Builder(word,checker,args.relaxed_queries,args.seed)
    targets=[];seen=set()
    for gi,(f,d,ss) in enumerate(word['A']):
        if d==469:continue
        if args.mode=='any_A' or args.mode=='source_loads' and all(s<word['v'] for s in ss) or args.mode=='birth' and d not in seen:targets.append(('A',gi))
        seen.add(d)
    stats=Counter();results=[];rejects=[];best=0.0;t0=time.monotonic();accepted=set()
    for index,target in enumerate(targets):
        if not args.start<=index<args.start+args.limit:continue
        stats['attempted']+=1;drop=accepted|{target} if args.greedy else {target}
        try:out,identity=builder.build(drop)
        except ValueError as exc:
            stats[str(exc.args[0][0])]+=1;rejects.append({'index':index,'delete':target,'reason':exc.args[0]});continue
        stats['SOURCE_observations_repaired']+=1
        delta=Counter({int(r):c for r,c in identity['profile'].items()});delta.subtract(baseline)
        saving=-sum(builder.price[r]*c for r,c in delta.items())
        if saving<=best+1e-9:stats['not_better']+=1;continue
        regenerate_D(out);scalar(out);native=module.Word(out);columns=native.full();hs,cs,_=native.interface()
        assert all(hs.values()) and all(cs.values());assert dict(actual_profile(out,native))==identity['profile']
        payload=canonical(out);name=f'{args.mode}-{index}.json.gz';(args.out/name).write_bytes(gzip.compress(payload,mtime=0))
        row={'index':index,'word':name,'content_sha256':sha256(payload).hexdigest(),'identity':identity,
             'saving':saving,'delta':{r:c for r,c in delta.items() if c},'columns':columns,'hypotheses':hs,'conclusion':cs,
             'counts':{sec:sum(len(g[2]) for g in out[sec]) for sec in ('D','A','B','C')}}
        results.append(row);stats['positive']+=1
        if args.greedy:accepted=drop;best=saving
        print('FOUND',index,'saving',saving,'delta',row['delta'],'counts',row['counts'],flush=True)
        if stats['attempted']%100==0:print('PROGRESS',dict(stats),'seconds',time.monotonic()-t0,flush=True)
    pins=[args.word,CHECKER,OLD/'enriched-frames/CATALOGUE-WORD.json.gz',OLD/'bit_pair_search.py',OLD/'bit_joint_frames.py',HERE/'search_networks.py',HERE/'source_quotient.py',HERE/'source_resynthesis.py',Path(__file__)]
    result={'status':'FINITE_OBSERVATION_ONLY_SOURCE_REPAIR','source_word_content_sha256':args.expected_sha,
            'source_sha256':{str(p.relative_to(ROOT)):sha256(p.read_bytes()).hexdigest() for p in pins},
            'mode':args.mode,'relaxed_queries':args.relaxed_queries,'seed':args.seed,'greedy':args.greedy,
            'stats':dict(stats),'results':results,'rejections':rejects,'seconds':time.monotonic()-t0,
            'scope':'COPY SOURCE rows and all productive B increments are fixed. Intermediate SOURCE/dirty responses are free. Source representation is a finite greedy exact compatible span query. No helper is removed from the physical inventory. Full native, coefficient, owner and global moment invoices remain separate.'}
    (args.out/'RESULT.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
    print('DONE',dict(stats),'seconds',time.monotonic()-t0,flush=True)


if __name__=='__main__':main()
