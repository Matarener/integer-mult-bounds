"""Emit two SOURCE snapshots and fuse their native helper returns.

Dugongue PR5639 gives two windows. The helper444 extension is handed to Discussion5638. Zero-centre reuse
and complete native pricing are supplied here. Credit ai-nanachi PR5512 and Ali Romman PR5421/5641.
Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
"""
from collections import Counter
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
import json
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
import baseline as B
import native
R,S,need,load,read,put,source = B.R,B.S,B.need,B.load,B.read,B.put,B.source
SOURCE=B.SOURCE
PARTIAL=B.PARTIAL


@lru_cache(maxsize=1)
def baseline():
    return B.construct()


def discover():
    word, owned, _, _ = baseline()
    base, frames, _ = source()
    geom = SOURCE.Geometry(frames)
    access = {h: [] for h in range(658) if h not in owned}
    rows=[1<<i for i in range(660)];source_rows={}
    for ix,e in enumerate(word):
        op,d=e[:2]
        if d in access:access[d].append(ix)
        if op=='ADD':
            if e[2] in access:access[e[2]].append(ix)
            source_rows[ix]=rows[e[2]];rows[d]^=rows[e[2]]
        elif op=='ERASE':rows[d]=0
    candidates=[]
    for h,ids in access.items():
        for position,a in enumerate(ids):
            first=word[a]
            if first[0]!='Q':continue
            target=0;queries=[a];adds=[]
            for b in ids[position+1:]:
                e=word[b]
                if e[0]=='ADD' and e[1]==h:
                    target^=source_rows[b];adds.append(b)
                elif e[0]=='Q' and e[1]==h:
                    queries.append(b)
                    ranks=[word[i][4] for i in queries]
                    try:geom.nested(first[2],e[3],sum(ranks))
                    except ValueError:continue
                    candidates.append({'helper':h,'indices':sorted(queries+adds),
                                       'queries':queries[:],'adds':adds[:],
                                       'frames':[first[2],e[3]],'ranks':ranks,'target_row':target})
                else:break
    requests={}
    for c in candidates:requests.setdefault(c['queries'][0],[]).append(c)
    bases={};observations=[];last_direct={}
    def observe(cut,d):
        if st[d] is None or not rows[d]:return
        last_direct[(d,st[d],rows[d])]=cut
        row=rows[d];combo=0;b=bases.setdefault(st[d],{})
        while row:
            pivot=row.bit_length()-1
            if pivot not in b:
                j=len(observations)
                observations.append({'cut':cut,'owner':d,'frame':st[d],'row':hex(rows[d])})
                b[pivot]=(row,combo^(1<<j));return
            v,k=b[pivot];row^=v;combo^=k
    rows=[1<<i for i in range(660)];st=base['final']+[None,None]
    for d in range(660):observe(0,d)
    hits=[]
    for ix,e in enumerate(word):
        for c in requests.get(ix,[]):
            row=c['target_row'];combo=0
            for pivot,(v,k) in sorted(bases.get(c['frames'][0],{}).items(),reverse=True):
                if row>>pivot&1:row^=v;combo^=k
            c['residual']=hex(row)
            if not row:
                c['span_witness']=[observations[j] for j in range(len(observations)) if combo>>j&1]
                need(len(c['adds'])==1,'Each admitted window has one direct SOURCE snapshot')
                src=word[c['adds'][0]][2];c['source']=src
                key=(src,c['frames'][0],c['target_row'])
                if (src,st[src],rows[src])==key:c['capture']=ix
                else:
                    need(key in last_direct,'A literal SOURCE version exists')
                    c['capture']=last_direct[key]
                hits.append(c)
        op,d=e[:2]
        if st[d] is not None and rows[d]:last_direct[(d,st[d],rows[d])]=ix
        if op=='ADD':rows[d]^=rows[e[2]]
        elif op=='ERASE':rows[d]=0;st[d]=e[2]
        elif op=='INIT':st[d]=e[2]
        else:st[d]=e[3]
        observe(ix+1,d)
    need(len(candidates)==667 and {c['helper'] for c in hits}=={444,465,467},'Complete declared block census')
    return candidates, sorted(hits,key=lambda c:c['capture'])


def construct(stale=False):
    word,owned,_,_=baseline();base,_,_=source();candidates,eligible=discover();hits=[c for c in eligible if c['helper'] in {465,467}]
    # Use the old centre for helper465. Its complete old payload is zero.
    banks={465:658,467:660}
    rows=[1<<i for i in range(660)]
    cleared=False;omitted=[]
    for ix,e in enumerate(word):
        op,d=e[:2]
        if d==658 or(op=='ADD' and e[2]==658):
            need((op=='ERASE' and not cleared) or rows[658]==0,'Only obsolete whole-zero centre accesses are removed')
            omitted.append(ix)
            if op=='ERASE':cleared=True
        if op=='ADD':rows[d]^=rows[e[2]]
        elif op=='ERASE':rows[d]=0
    captures={c['capture']:c for c in hits};starts={c['indices'][0]:c for c in hits}
    skip=set(omitted)|{i for c in hits for i in c['indices']}
    out=[]
    for ix,e in enumerate(word):
        if ix in captures:
            c=captures[ix];s=c['source'];d=banks[c['helper']];u=c['frames'][0]
            out.extend([['ERASE',d,u],['ADD',d,s,u]])
        if ix in starts:
            c=starts[ix];h=c['helper'];d=banks[h];u,ground=c['frames']
            out.extend([['ADD',h,d,u],['Q',h,u,ground,sum(c['ranks'])],['ERASE',d,None]])
        if ix not in skip:out.append(e)
    if stale:
        # Capturing SOURCE38 after its U-frame exit is not a valid substitute.
        ix=next(i for i,e in enumerate(out) if e[:3]==['ADD',660,38])
        delayed=out.pop(ix)
        j=next(i for i,e in enumerate(out) if i>=ix and e[0]=='Q' and e[1]==38)
        out.insert(j+1,delayed)
    return out,owned|{660},candidates,hits,omitted


def run():
    base,frames,_=source();word,owned,candidates,hits,omitted=construct()
    stats=native.replay(base,frames,word,owned)
    for modulus in [101,101**2]:native.replay(base,frames,word,owned,modulus)
    need(stats['paid']=={1:1303,2:1342,3:71,4:42,5:102,6:10,7:9},'Actual two-fusion invoice')
    controls=[]
    bad,_,_,_,_=construct(stale=True)
    missing=[e[:] for e in word]
    missing.pop(next(i for i,e in enumerate(missing) if e==['ERASE',660,None]))
    for name,mutant in [('stale_source_snapshot',bad),('missing_snapshot_teardown',missing)]:
        try:native.replay(base,frames,mutant,owned)
        except ValueError:controls.append(name)
        else:raise ValueError('Accepted '+name)
    put('WORD.json.gz',{'records':word,'owned':sorted(owned),'start':base['final']+[None]*3,'final':base['start']+[None]*3})
    put('WINDOWS.json',{'candidates':candidates,'eligible':discover()[1],'selected':hits,'scope_handoff':'Helper444 is handed to Discussion5638; no third fusion is emitted here.','obsolete_centre_records':omitted,
                        'scope':'All nested runs of at least two queries, with any number of destination ADDs and no source observer, on every retained field. All earlier same-frame field observations are available in arbitrary F2 combinations.'})
    result={'status':'PASS_TWO_NATIVE_G20_SOURCE_SNAPSHOT_FUSIONS','stats':stats,'native_moduli':[101,10201],
            'owned_banks':{465:658,467:660},'candidate_windows':len(candidates),
            'rejected_controls':controls,'canonical_word_sha256':sha256(json.dumps(word,separators=(',',':')).encode()).hexdigest()}
    put('LOCAL-RESULT.json',result);print(json.dumps(result,indent=2));return result


if __name__=='__main__':run()
