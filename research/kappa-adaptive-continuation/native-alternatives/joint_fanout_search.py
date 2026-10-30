#!/usr/bin/env python3
"""Exact covector graph edits followed by constructive joint frame search.

The shared-source identity is exact over arbitrary inputs. Floating min-sum
prices nominate candidates; each emitted candidate still needs independent
native replay and exact whole-allocation pricing. Source mechanism credits
are given in fanout_search.py and opt_frames.py. Apache-2.0.
"""
import argparse,gzip,json,time
from pathlib import Path
from collections import Counter
from copy import deepcopy
from hashlib import sha256
from fanout_search import read,expand,trace,pair_catalog,clusters,mutation,basis,meet
from opt_frames import optimize

def transposed(es):
    out=deepcopy(es)[::-1]
    for e in out:
        if e[0]=='add':e[1],e[2]=e[2],e[1]
    return out

def transpose_mutation(w,name,ces,chosen,lo,hi,ar,br,q):
    drop={p['drop'] for p in chosen};result=[]
    first=['add',ar,br,q.numerator,q.denominator,[]]
    last=['add',ar,br,-q.numerator,q.denominator,[]]
    for i in range(len(ces)+1):
        if i==lo:result.append(first)
        if i==hi:result.append(last)
        if i<len(ces) and i not in drop:result.append(ces[i])
    original=transposed(result);out=deepcopy(w)
    if name=='B':
        out['B']=[]
        for e in original:
            if e[0]=='warp':out['warps'][e[2]-1][0]=len(out['B'])
            else:out['B'].append(e)
    else:out[name]=original
    return out,first,last

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--word',type=Path,required=True)
    ap.add_argument('--section',choices=('A','B','restore'),required=True)
    ap.add_argument('--out',type=Path,required=True);ap.add_argument('--max-gap',type=int,default=150)
    ap.add_argument('--permanent-tail',action='store_true');ap.add_argument('--start',type=int,default=0);ap.add_argument('--limit',type=int,default=100000)
    ap.add_argument('--transpose',action='store_true',help='Use the transpose identity to share target updates.')
    a=ap.parse_args();w=read(a.word);es=expand(w);_,_,_,snaps,nexts,_=trace(w,es)
    assert not (a.transpose and a.permanent_tail)
    ces=transposed(es[a.section]) if a.transpose else es[a.section]
    groups,reads,writes=pair_catalog(ces,a.max_gap);a.out.mkdir(parents=True,exist_ok=True)
    indexed=[]
    for (ar,br,q,ae,be),pairs in groups.items():
        for chosen,lo,hi in clusters(pairs,ar,br,reads,writes):
            if a.section=='A' and (len(ces)-hi if a.transpose else lo)<w['prelude_events']:continue
            if a.permanent_tail:
                if 112<=ar<224 or str(ar) in w['helper_final']:continue
                keeps={p['keep'] for p in chosen}
                if any(i>=lo and i not in keeps for i in reads[ar]):continue
                later=('A','B','restore')[('A','B','restore').index(a.section)+1:]
                if any(e[0]=='add' and e[2]==ar for n in later for e in es[n]):continue
            indexed.append((ar,br,q,chosen,lo,hi))
    stats=Counter();found=[];t=time.monotonic()
    for index,(ar,br,q,chosen,lo,hi) in enumerate(indexed):
        if not a.start<=index<a.start+a.limit:continue
        if a.transpose:nw,first,last=transpose_mutation(w,a.section,ces,chosen,lo,hi,ar,br,q)
        else:
            G=basis(snaps[a.section][lo][ar]+snaps[a.section][lo][br]);H=None if a.permanent_tail else meet(nexts[a.section][hi][ar],nexts[a.section][hi][br])
            nw,first,last=mutation(w,es,a.section,chosen,lo,hi,ar,br,q,G,H)
        stats['attempted']+=1
        try: nw,result=optimize(nw)
        except (ValueError,AssertionError) as exc:
            stats[str(exc.args[0][0] if exc.args and isinstance(exc.args[0],tuple) else exc.args[0])]+=1
            continue
        stats['feasible']+=1
        if result['saving']>1e-9:
            ident=f'{a.section}-{index}-{ar}-{br}-{lo}-{hi}'
            payload=json.dumps(nw,sort_keys=True,separators=(',',':')).encode();p=a.out/f'WORD-{ident}.json.gz';p.write_bytes(gzip.compress(payload,mtime=0))
            rec=dict(id=ident,index=index,ar=ar,br=br,coefficient=str(q),section=a.section,lo=lo,hi=hi,chosen=chosen,permanent_tail=a.permanent_tail,transpose=a.transpose,
                before_events={str(i):ces[i] for p_ in chosen for i in (p_['keep'],p_['drop'])},
                aggregate_before_frames=first,undo_before_frames=last,optimization=result,word=p.name,word_payload_sha256=sha256(payload).hexdigest())
            found.append(rec);(a.out/f'{ident}.json').write_text(json.dumps(rec,sort_keys=True,indent=2)+'\n');print('FOUND',json.dumps(rec,sort_keys=True),flush=True)
        if stats['attempted']%50==0:print('PROGRESS',index,dict(stats),'seconds',round(time.monotonic()-t,1),flush=True)
    receipt=dict(status='BOUNDED_CHANGED_COVECTOR_GRAPH_SEARCH',source_sha256=sha256(a.word.read_bytes()).hexdigest(),source_name=a.word.name,section=a.section,
        permanent_tail=a.permanent_tail,transpose=a.transpose,start=a.start,limit=a.limit,total_indexed=len(indexed),stats=dict(stats),candidates=found)
    (a.out/'RESULT.json').write_text(json.dumps(receipt,sort_keys=True,indent=2)+'\n');print('DONE',dict(stats),'found',len(found),'total',len(indexed),flush=True)

if __name__=='__main__':main()
