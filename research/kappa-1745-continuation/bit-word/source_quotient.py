#!/usr/bin/env python3
"""Source-projection helper deletion with regenerated arbitrary-dirty D/C.

Intermediate dirty responses are deliberately free to change. Each eliminated
helper observation is realized from a span of compatible surviving registers;
SOURCE projections are exact at every unchanged logical observation. The
actual resulting raw dirty matrix supplies D, and literal inverse supplies C.
This is distinct from fixed original dirty-response or zero-input quotients.
Apache-2.0; substantial OpenAI assistance under the user's direction.
"""
from bisect import bisect_right
from collections import Counter,defaultdict
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import argparse,gzip,json,time
from search_networks import ROOT,HERE,OLD,SOURCE,CHECKER,EXPECTED,read,canonical,cleanup,scalar,compact,load_checker,actual_profile,Optimizer


def regenerate_D(word):
    n=2*word['v']+word['R'];v=word['v'];values=[1<<r for r in range(n)]
    for section in ('A','scatter','B'):
        if section=='scatter':
            captures=[values[r] for r in word['ret']]
            for t,indices in enumerate(word['scatter']):
                for k in indices:values[v+t]^=captures[k]
        else:
            for f,d,ss in word[section]:
                for s in ss:values[d]^=values[s]
    smask=(1<<v)-1;ymask=smask<<v
    assert all(values[v+t]&smask==1<<t and values[v+t]&ymask==1<<(v+t) for t in range(v))
    word['D']=[]
    for t in range(v):
        support=[r for r in range(2*v,n) if values[v+t]>>r&1]
        if support:word['D'].append([0,v+t,support])
    cleanup(word)


def span_representation(rows,wanted,order):
    if not wanted:return []
    direct=[row for row in rows if row[1]==wanted]
    if direct:return [min(direct,key=lambda r:r[2])[0]]
    if order=='sparse':rows=sorted(rows,key=lambda r:(r[2],r[1].bit_count(),r[0]))
    elif order=='source_first':rows=sorted(rows,key=lambda r:(r[2],r[0]>=111,r[0]))
    else:rows=sorted(rows,key=lambda r:(r[2],r[0]<222,r[0]))
    basis={}
    for role,row,cost in rows:
        support=1<<role
        while row:
            pivot=row.bit_length()-1
            if pivot not in basis:
                basis[pivot]=(row,support);break
            old,combination=basis[pivot];row^=old;support^=combination
    remainder=wanted;support=0
    while remainder:
        pivot=remainder.bit_length()-1
        if pivot not in basis:raise ValueError(('source_span_obstruction',hex(wanted),hex(remainder),len(rows),len(basis)))
        row,combination=basis[pivot];remainder^=row;support^=combination
    return [r for r in range(659) if support>>r&1]


def build(word,removed,dimensions,original_captures,order):
    n=2*word['v']+word['R'];v=word['v']
    masks=[sum(1<<i for i in frame) for frame in word['frames']]
    nested=lambda a,b:not(masks[a]&~masks[b])
    price=[r**(1-.001745) if r else 0.0 for r in range(9)]
    events=[]
    for section in ('A','B'):
        for gi,(f,d,ss) in enumerate(word[section]):
            for s in ss:events.append((section,gi,f,d,s))
        if section=='A':
            for role,f in original_captures.items():events.append(('capture',-1,f,role,None))
    contacts=defaultdict(list)
    for i,(section,gi,f,d,s) in enumerate(events):
        if d==removed:continue
        for role in (d,) if s is None or s==removed else (d,s):contacts[role].append((i,f))
    for r,f in enumerate(word['final']):contacts[r].append((len(events),0 if r==removed else f))
    keys={r:[i for i,f in values] for r,values in contacts.items()}
    values=[(1<<r) if r<v else 0 for r in range(n)]
    cur=list(word['start']);out=deepcopy(word);out['A']=[];out['B']=[];notes=[];captures=[]
    def climb(role,f):
        if not nested(cur[role],f):raise ValueError(('nonmonotone_surviving_contact',role,cur[role],f))
        cur[role]=f
    for i,(section,gi,f,d,s) in enumerate(events):
        if section=='capture':
            if cur[d]!=f:raise ValueError(('capture_frame_not_emitted',d,cur[d],f))
            captures.append({'role':d,'frame':f,'SOURCE_row':hex(values[d])});continue
        if d==removed:
            values[d]^=values[s];continue
        if s!=removed:
            climb(d,f);climb(s,f);out[section].append([f,d,[s]])
        else:
            rows=[]
            for role in range(n):
                if role in (removed,d) or v<=role<2*v:continue
                if not values[role] or not nested(cur[role],f):continue
                next_i=bisect_right(keys[role],i)
                upper=contacts[role][next_i][1]
                if not nested(f,upper):continue
                cost=price[dimensions[f]-dimensions[cur[role]]]+price[dimensions[upper]-dimensions[f]]-price[dimensions[upper]-dimensions[cur[role]]]
                rows.append((role,values[role],cost))
            try:support=span_representation(rows,values[s],order)
            except ValueError as exc:
                raise ValueError(('source_span_obstruction',section,gi,i,d,f,hex(values[s]),exc.args[0],
                                  [[role,hex(row)] for role,row,cost in rows]))
            assert all(role!=d for role in support)
            reconstructed=0
            for role in support:reconstructed^=values[role]
            assert reconstructed==values[s]
            if support:
                climb(d,f)
                for role in support:climb(role,f)
                out[section].append([f,d,support])
            notes.append({'section':section,'group':gi,'event':i,'destination':d,'frame':f,'replaced_helper':s,
                          'SOURCE_row':hex(values[s]),'support':support,'compatible_donors':len(rows)})
        values[d]^=values[s]
    out['final'][removed]=0
    regenerate_D(out);scalar(out)
    return out,{'removed_helper':removed,'basis_order':order,'substitutions':notes,'captures':captures,
                'D_ADD_count':sum(len(g[2]) for g in out['D']),
                'old_D_ADD_count':sum(len(g[2]) for g in word['D'])}


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--order',choices=('sparse','source_first','helper_first'),default='sparse')
    args=ap.parse_args();args.out.mkdir(parents=True,exist_ok=True)
    raw=gzip.decompress(SOURCE.read_bytes());assert sha256(raw).hexdigest()==EXPECTED
    word=json.loads(raw);word['frames']=read(OLD/'enriched-frames/CATALOGUE-WORD.json.gz')['frames']
    module=load_checker(CHECKER);checker=module.Word(word);checker.full()
    optimizer=Optimizer(word,checker,.001745);caps=optimizer.captures.copy()
    pins=[SOURCE,CHECKER,OLD/'enriched-frames/CATALOGUE-WORD.json.gz',OLD/'bit_pair_search.py',OLD/'bit_joint_frames.py',HERE/'search_networks.py',Path(__file__)]
    sources={str(p.relative_to(ROOT)):sha256(p.read_bytes()).hexdigest() for p in pins}
    stats=Counter();candidates=[];rejects=[];t0=time.monotonic()
    for helper in range(2*word['v'],2*word['v']+word['R']):
        if helper in word['ret'] or helper==469:continue
        stats['attempted']+=1
        try:
            candidate,identity=build(word,helper,checker.fdim,caps,args.order)
            stats['fixed_frame_SOURCE_quotient_pass']+=1
            candidate,result=optimizer.optimize(candidate)
            # The optimizer changes A/B frames but keeps their scalar graph;
            # it also regenerates literal C. The actual D is retained.
            compacted=compact(candidate,helper)
            native=module.Word(compacted);columns=native.full()
            hypotheses,conclusion,_=native.interface();assert all(hypotheses.values()) and all(conclusion.values())
            assert dict(actual_profile(compacted,native))==result['local_profile']
        except ValueError as exc:
            reason=exc.args[0];label=str(reason[0]) if isinstance(reason,tuple) else str(reason)
            stats[label]+=1;rejects.append({'helper':helper,'reason':reason});continue
        payload=canonical(compacted)
        name=f'R436-SOURCE-{helper}'
        row={'id':name,'helper':helper,'identity':identity,'optimization':result,'columns':columns,
             'hypotheses':hypotheses,'conclusion':conclusion,'word':name+'.json.gz','content_sha256':sha256(payload).hexdigest(),
             'scope':'New arbitrary-dirty D/C and complete finite R436 word. Full hosted inventory, native export and coefficient/global invoices remain mandatory.'}
        (args.out/row['word']).write_bytes(gzip.compress(payload,mtime=0))
        (args.out/(name+'.json')).write_text(json.dumps(row,sort_keys=True,indent=2)+'\n')
        candidates.append(row)
        print('FOUND',helper,'delta',result['delta'],'saving',result['saving'],'D',identity['D_ADD_count'],flush=True)
    result={'status':'FINITE_SOURCE_PROJECTION_QUOTIENT_SEARCH','source_word_content_sha256':EXPECTED,
            'source_sha256':sources,'basis_order':args.order,'stats':dict(stats),'candidates':candidates,'rejections':rejects,
            'seconds':time.monotonic()-t0,
            'scope':'Every helper except nine COPY centers and already-public fixed-boundary469. The greedy donor basis uses the current frame and next unchanged-contact upper frame; failures are not exclusions of retimed or changed-observation graphs. Intermediate dirty responses may change; actual D and literal C are regenerated and all remaining columns are checked on every candidate.'}
    (args.out/'RESULT.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
    print('DONE',dict(stats),'positive',len(candidates),'seconds',time.monotonic()-t0,flush=True)


if __name__=='__main__':main()
