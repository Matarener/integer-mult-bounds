#!/usr/bin/env python3
"""Width-preserving exact dirty-source covector rewrites on retained words.

Mechanism credit: Nick Petalas / rank7-shared-restore-fanin, Jeremy Kothe's
declared native rewrites, and the retained PR2979/PR3133/PR3734 word lineage.
New bounded source-contact search with substantial OpenAI assistance.
Apache-2.0. A candidate requires independent full native replay before use.
"""
from __future__ import annotations
import argparse
from collections import Counter,defaultdict
from copy import deepcopy
from fractions import Fraction as Q
from functools import lru_cache
from hashlib import sha256
import gzip,json
from pathlib import Path


def read(p):
    p=Path(p);raw=p.read_bytes()
    return json.loads(gzip.decompress(raw) if p.suffix=='.gz' else raw)


@lru_cache(None)
def basis(vs):
    piv={}
    for x in vs:
        for k in sorted(piv,reverse=True):
            if x>>k&1:x^=piv[k]
        if x:
            k=x.bit_length()-1
            for j in piv:
                if piv[j]>>k&1:piv[j]^=x
            piv[k]=x
    return tuple(piv[k] for k in sorted(piv,reverse=True))


@lru_cache(None)
def span(vs):
    s={0}
    for x in vs:s|={q^x for q in s}
    return frozenset(s)


def contains(a,b):return basis(a+b)==b
def meet(a,b):return basis(tuple(sorted(span(a)&span(b))))
def regs(e):return e[1:3] if e[0]=='add' else [e[1]]
def coefficient(e):return Q(e[3],e[4])
def phi(r):return r**(1-0.0017305784372662468) if r else 0.0


def expand(w):
    by=defaultdict(list)
    for op,(p,r,G,f,t) in enumerate(w['warps'],1):
        by[p].append(['warp',r,op,f,t])
    B=[]
    for p in range(len(w['B'])+1):
        B+=by[p]
        if p<len(w['B']):B.append(w['B'][p])
    return {'A':w['A'],'B':B,'restore':w['restore']}


def trace(w,sections):
    full=basis(tuple(1<<i for i in range(9)))
    kept=[r for r in range(704) if r not in set(w['removed'])]
    start={r:basis((w['ports'][r],)) if r<112 else basis(tuple(w['start_extra'].get(str(r),[]))) for r in kept}
    final={r:full if r<112 or r>=224 else basis(tuple(x for x in range(512) if not ((x&w['ports'][r-112]).bit_count()%2))) for r in kept}
    for r,f in w['helper_final'].items():final[int(r)]=basis(tuple(f))
    contacts={r:[] for r in kept};cur=start.copy();snaps={};nxts={}
    for si,name in enumerate(('A','B','restore')):
        snaps[name]=[]
        for i,e in enumerate(sections[name]):
            snaps[name].append(cur.copy())
            if e[0]=='warp':
                r=e[1];f=basis(tuple(e[3]));t=basis(tuple(e[4]))
                assert cur[r]==f,(name,i,r,'warp')
                contacts[r].append(((si,i,1),'warp',f,t));cur[r]=t
            else:
                f=basis(tuple(e[-1]))
                for r in regs(e):
                    assert contains(cur[r],f),(name,i,r,cur[r],f)
                    contacts[r].append(((si,i,1),'frame',f));cur[r]=f
        snaps[name].append(cur.copy())
        if name=='A':
            for r,f in zip(w['centers'],w['center_frames']):
                assert cur[r]==basis(tuple(f)),('center',r)
    for r in kept:contacts[r].append(((3,0,1),'frame',final[r]))
    baseline={r:path_profile(start[r],contacts[r]) for r in kept}
    for si,name in enumerate(('A','B','restore')):
        out=[]
        for i in range(len(sections[name])+1):
            boundary=(si,i,0)
            out.append({r:next((x[2] for x in contacts[r] if x[0]>=boundary),final[r]) for r in kept})
        nxts[name]=out
    return start,final,contacts,snaps,nxts,baseline


def path_profile(start,contacts):
    out=Counter();cur=start
    for _,tag,*fs in sorted(contacts):
        if tag=='warp':
            if cur!=fs[0]:raise ValueError(('warp',cur,fs[0]))
            cur=fs[1]
        else:
            f=fs[0]
            if not contains(cur,f):raise ValueError(('nonmonotone',cur,f))
            if f!=cur:out[len(f)-len(cur)]+=1;cur=f
    return out


def pair_catalog(es,max_gap):
    writes=[[] for _ in range(704)];reads=[[] for _ in range(704)]
    targets=defaultdict(list)
    epoch=[0]*704;epochs=[]
    for i,e in enumerate(es):
        epochs.append(epoch.copy())
        if e[0]=='add':
            reads[e[2]].append(i);writes[e[1]].append(i);epoch[e[1]]+=1
            targets[e[1]].append(i)
        else:
            writes[e[1]].append(i);epoch[e[1]]+=1
    groups=defaultdict(dict)
    for t,positions in targets.items():
        for ii,i in enumerate(positions):
            e=es[i]
            for j in positions[ii+1:]:
                if j-i>max_gap:break
                f=es[j];a,b=e[2],f[2]
                if a==b or not coefficient(e) or not coefficient(f):continue
                # The two target updates commute across this interval only if
                # their target has no observer or non-additive transformation.
                if any(i<k<j for k in reads[t]):continue
                if any(es[k][0]!='add' for k in writes[t] if i<k<j):continue
                if any(i<k<j for k in writes[a]+writes[b]):continue
                for aa,bb,ka,kb in ((a,b,i,j),(b,a,j,i)):
                    ratio=coefficient(es[kb])/coefficient(es[ka])
                    if ratio.denominator&(ratio.denominator-1):continue
                    key=(aa,bb,ratio,epochs[i][aa],epochs[i][bb])
                    p=dict(keep=ka,drop=kb,target=t,lo=i,hi=j)
                    previous=groups[key].get(ka)
                    if previous is None or j-i<previous['hi']-previous['lo']:
                        groups[key][ka]=p
    return groups,reads,writes


def clusters(pairs,a,b,reads,writes):
    ps=sorted(pairs.values(),key=lambda p:p['keep'])
    for l in range(len(ps)):
        for u in range(l+1,min(len(ps),l+8)+1):
            chosen=ps[l:u];lo=min(p['lo'] for p in chosen);hi=max(p['hi'] for p in chosen)
            keeps={p['keep'] for p in chosen};drops={p['drop'] for p in chosen}
            if len(drops)!=len(chosen):continue
            if any(lo<=i<=hi and i not in keeps for i in reads[a]):continue
            if any(lo<=i<=hi for i in writes[a]+writes[b]):continue
            yield chosen,lo,hi+1


def mutation(w,sections,name,chosen,lo,hi,a,b,q,G,H):
    new=deepcopy(w);es=deepcopy(sections[name]);drop={p['drop'] for p in chosen}
    first=['add',a,b,q.numerator,q.denominator,list(G)]
    last=None if H is None else ['add',a,b,-q.numerator,q.denominator,list(H)]
    out=[]
    for i in range(len(es)+1):
        if i==lo:out.append(first)
        if i==hi and last is not None:out.append(last)
        if i<len(es) and i not in drop:out.append(es[i])
    if name=='B':
        new['B']=[]
        for e in out:
            if e[0]=='warp':new['warps'][e[2]-1][0]=len(new['B'])
            else:new['B'].append(e)
    else:new[name]=out
    return new,first,last


def derive_cleanup(w):
    """Literal inverse of all non-target events, with owned HPE buffers."""
    n=704;full=list(basis(tuple(1<<i for i in range(9))))
    restored=set(map(int,w['helper_final']))
    buf=lambda r:r+n if r in restored else r
    es=expand(w)
    events=es['A'][w['prelude_events']:]+es['B']+es['restore']
    cleanup=[]
    for e in reversed(events):
        if 112<=e[1]<224 and e[0]!='warp':continue
        if e[0]=='warp':cleanup.append(['warp',buf(e[1]),-e[2],full])
        elif e[0]=='add':cleanup.append(['add',buf(e[1]),buf(e[2]),-e[3],e[4],full])
        else:cleanup.append(['scale',buf(e[1]),e[3],e[2],full])
    w['cleanup']=cleanup


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--word',type=Path,required=True)
    ap.add_argument('--out',type=Path,default=Path(__file__).resolve().parent/'fanout')
    ap.add_argument('--section',choices=('A','B','restore','all'),default='all')
    ap.add_argument('--max-gap',type=int,default=24)
    ap.add_argument('--permanent-tail',action='store_true',help='Use existing FULL inverse cleanup to erase an unobserved carrier aggregate.')
    a=ap.parse_args();w=read(a.word);sections=expand(w)
    start,final,contacts,snaps,nexts,base=trace(w,sections)
    a.out.mkdir(parents=True,exist_ok=True);found=[];tried=0
    for si,name in enumerate(('A','B','restore')):
        if a.section!='all' and a.section!=name:continue
        groups,reads,writes=pair_catalog(sections[name],a.max_gap)
        print('SECTION',name,'groups',len(groups),flush=True)
        for (ar,br,q,ae,be),pairs in groups.items():
            for chosen,lo,hi in clusters(pairs,ar,br,reads,writes):
                if name=='A' and lo<w['prelude_events']:continue
                G=basis(snaps[name][lo][ar]+snaps[name][lo][br])
                H=meet(nexts[name][hi][ar],nexts[name][hi][br])
                if a.permanent_tail:
                    if 112<=ar<224 or str(ar) in w['helper_final']:continue
                    keeps={p['keep'] for p in chosen}
                    if any(i>=lo and i not in keeps for i in reads[ar]):continue
                    later=('A','B','restore')[si+1:]
                    if any(e[0]=='add' and e[2]==ar for ns in later for e in sections[ns]):continue
                    H=None
                affected={ar,br}|{p['target'] for p in chosen}
                drop={(si,p['drop'],1) for p in chosen}
                delta=Counter();tried+=1
                try:
                    for r in affected:
                        cs=[x for x in contacts[r] if x[0] not in drop]
                        if r in (ar,br):
                            cs.append(((si,lo,0),'frame',G))
                            if H is not None:cs.append(((si,hi,0),'frame',H))
                        pp=path_profile(start[r],cs)
                        delta.update(pp);delta.subtract(base[r])
                except ValueError:continue
                delta={r:n for r,n in delta.items() if n}
                saving=-sum(n*phi(r) for r,n in delta.items())
                if saving<=1e-10:continue
                new,first,last=mutation(w,sections,name,chosen,lo,hi,ar,br,q,G,H)
                derive_cleanup(new)
                # Full chronology, including the centre boundary assertions.
                try:
                    ns=expand(new);_,_,_,_,_,nb=trace(new,ns)
                except (ValueError,AssertionError):continue
                actual=Counter()
                for r in nb:actual.update(nb[r]);actual.subtract(base[r])
                assert {r:n for r,n in actual.items() if n}==delta
                profile=Counter({int(r):n for r,n in w['report']['local_profile'].items()});profile.update(delta)
                new['report']['local_profile']={r:n for r,n in sorted(profile.items()) if n}
                ident=f'{name}-{ar}-{br}-{lo}-{hi}-{len(found)}'
                path=a.out/f'WORD-{ident}.json.gz'
                payload=json.dumps(new,sort_keys=True,separators=(',',':')).encode()
                path.write_bytes(gzip.compress(payload,mtime=0))
                info=dict(id=ident,section=name,source_a=ar,source_b=br,ratio=str(q),lo=lo,hi=hi,
                    chosen_pairs=chosen,aggregate_gate=first,restore_gate=last,native_delta=delta,
                    native_profile=new['report']['local_profile'],approx_local_saving=saving,
                    word=path.name,word_payload_sha256=sha256(payload).hexdigest(),
                    status='CANDIDATE_EXACT_COVECTOR_IDENTITY_REQUIRES_FULL_NATIVE_REPLAY')
                found.append(info);(a.out/f'{ident}.json').write_text(json.dumps(info,indent=2,sort_keys=True)+'\n')
                print('FOUND',json.dumps(info,sort_keys=True),flush=True)
        print('END_SECTION',name,'tried',tried,'found',len(found),flush=True)
    result=dict(status='PASS_BOUNDED_LITERAL_COVECTOR_SEARCH',source_word_sha256=sha256(a.word.read_bytes()).hexdigest(),
        source_word_name=a.word.name,section=a.section,max_gap=a.max_gap,permanent_tail=a.permanent_tail,tried=tried,candidates=found,
        scope='Local exact covector rewrite and full native frame price only; each candidate needs full arbitrary-column/native replay and whole invoice.')
    (a.out/'RESULT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')


if __name__=='__main__':main()
