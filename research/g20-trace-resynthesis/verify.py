"""Resynthesize the complete G20 dependency trace without changing queries.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
Source and exact synthesis credits remain in inputs/NOTICE and vendor files.
"""
import argparse
from copy import deepcopy
from hashlib import sha256
import gzip
import importlib.util
import json
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent


def need(ok,why):
    if not ok:raise ValueError(why)


def canonical(x):
    return json.dumps(x,sort_keys=True,separators=(',',':')).encode()


def touched(e):
    return set(e[1:3]) if e[0]=='ADD' else {e[1]}


def validate_projection(records,first,last,indices,new,parent,tables):
    selected=[records[k] for k in indices]
    roles=set().union(*(touched(e) for e in selected))
    need(2<=len(roles)<=4 and indices==sorted(set(indices)) and indices[0]==first
         and indices[-1]==last,'complete projected interval')
    for k in range(first,last+1):
        if k not in indices:
            need(not touched(records[k])&roles,'crossed dependent operation')
    parent.same_endpoint(selected,new)
    need(len(new)==parent.shortest(selected,tables)[1]<len(selected),'exact improving projected minimum')


def candidate(records,i,parent,tables):
    frame=records[i][3];roles=set(records[i][1:3]);best=None
    for j in range(i+1,len(records)):
        e=records[j]
        if e[0]!='ADD':
            if e[1] in roles:break
            continue
        if not roles.intersection(e[1:3]):continue
        roles.update(e[1:3])
        while len(roles)<=4:
            old=set(roles);valid=True
            for q in records[i:j+1]:
                if q[0]!='ADD':
                    if q[1] in roles:valid=False;break
                elif roles.intersection(q[1:3]):
                    if q[3]!=frame:valid=False;break
                    roles.update(q[1:3])
            if not valid or roles==old:break
        if len(roles)>4 or not valid:break
        indices=[k for k in range(i,j+1) if records[k][0]=='ADD' and roles.intersection(records[k][1:3])]
        selected=[records[k] for k in indices];new,cost=parent.shortest(selected,tables)
        gain=len(selected)-cost
        if gain>0 and (best is None or gain>best[0]):best=(gain,j,indices,new)
    return best


def commute_pass(records,parent):
    records=deepcopy(records);edits=[];i=0
    while i<len(records):
        a=records[i]
        if a[0]!='ADD':i+=1;continue
        d,s=a[1:3];conflict=None;found=None
        for j in range(i-1,-1,-1):
            b=records[j]
            if b[0]!='ADD':
                if b[1] in (d,s):break
                continue
            if b==a:found=j;break
            if b[1]!=s and b[2]!=d:continue
            if conflict is not None or (b[1]==s and b[2]==d) or b[3]!=a[3]:break
            conflict=j
        if found is None:i+=1;continue
        new=[];replacement=[]
        if conflict is not None:
            b=records[conflict]
            replacement=[b,['ADD',d,b[2],a[3]] if b[1]==s else ['ADD',b[1],s,a[3]]]
            parent.same_endpoint([a,b,a],replacement)
        else:
            parent.same_endpoint([a,a],[])
        for j in range(found+1,i):
            new.extend(replacement if j==conflict else [records[j]])
        edits.append({'kind':'commutation','first':found,'last':i,'conflict':conflict,
                      'gate':a,'replacement':replacement})
        records[found:i+1]=new;i=max(found-1,0)
    return records,edits


def projection_pass(records,parent,tables):
    records=deepcopy(records);edits=[];i=0
    while i<len(records):
        if records[i][0]!='ADD':i+=1;continue
        choice=candidate(records,i,parent,tables)
        if choice:
            gain,end,indices,new=choice
            validate_projection(records,i,end,indices,new,parent,tables)
            chosen=set(indices)
            edits.append({'kind':'projection','first':i,'last':end,'indices':indices,
                          'before':[records[k] for k in indices],'after':new})
            records[i:end+1]=new+[records[k] for k in range(i,end+1) if k not in chosen]
            i+=len(new)
        else:i+=1
    return records,edits


def observations(word):
    rows=[1<<i for i in range(len(word['start']))];out=[]
    for e in word['records']:
        if e[0]=='ADD':rows[e[1]]^=rows[e[2]]
        else:
            out.append([e,hex(rows[e[1]])])
            if e[0] in ('ERASE','INIT'):rows[e[1]]=0
    return out


def run(emit):
    for pin in json.loads((HERE/'SOURCES.json').read_text())['vendored_inputs']:
        need(sha256((HERE/pin['path']).read_bytes()).hexdigest()==pin['sha256'],'frozen source '+pin['path'])
    old_path=list(sys.path);sys.path.insert(0,str(HERE/'vendor'))
    try:
        spec=importlib.util.spec_from_file_location('trace_parent',HERE/'inputs/parent.py')
        parent=importlib.util.module_from_spec(spec);spec.loader.exec_module(parent)
    finally:sys.path[:]=old_path
    source=json.loads(gzip.decompress((HERE/'inputs/WORD.json.gz').read_bytes()))
    tables=parent.tables();word=deepcopy(source);rounds=[]
    while True:
        records,a=commute_pass(word['records'],parent)
        records,b=projection_pass(records,parent,tables)
        if not a and not b:break
        need(len(records)<len(word['records']),'strict descent')
        rounds.append(a+b);word['records']=records
    before,after=parent.replay(source),parent.replay(word)
    observed=observations(word)
    need(observed==observations(source),'every exact native and owned boundary input')
    need(before['paid']==after['paid'],'complete paid profile')
    need(after['peak_owned']<=before['peak_owned'],'no extra owned reserve')
    need(int(after['positive_majorant'])<=int(before['positive_majorant']),'positive scalar majorant')
    saved=before['counts']['ADD']-after['counts']['ADD'];need(saved>2,'substantive construction beyond the two-ADD screen')
    prior=json.loads((HERE/'inputs/RESULT.json').read_text())
    need(canonical(before)==canonical(prior['constructed']),'published source replay')
    controls=[]
    bad=deepcopy(word);i=next(i for i,e in enumerate(bad['records']) if e[0]=='Q')
    bad['records'][i][1]=(bad['records'][i][1]+1)%len(word['start'])
    need(observations(bad)!=observed,'wrong query control discriminates')
    controls.append('wrong query owner changes its exact observation')
    r=[['ADD',0,1,0],['Q',0,0,1,1],['ADD',0,1,0]]
    try:validate_projection(r,0,2,[0,2],[],parent,tables)
    except ValueError as error:controls.append(str(error))
    else:raise ValueError('dependent query crossing accepted')
    result={'schema':'g20-trace-resynthesis/1','before':before,'after':after,
            'rounds':len(rounds),'replacements':sum(map(len,rounds)),
            'saved_local_adds':saved,'saved_18_call_adds':18*saved,
            'source_primitive_count':prior['substitution_primitive_count'],
            'substitution_primitive_count':prior['substitution_primitive_count']-36*saved,
            'queried_boundary_sha256':sha256(canonical(observed)).hexdigest(),
            'word_sha256':sha256(canonical(word)).hexdigest(),'controls':controls,
            'fixed_point_scope':'All candidates generated by the stated dependency-closure projection and one-conflict commutation scans.'}
    payload={'RESULT.json':json.dumps(result,indent=2).encode()+b'\n',
             'EDITS.json':json.dumps(rounds,indent=1).encode()+b'\n',
             'WORD.json.gz':gzip.compress(canonical(word),mtime=0)}
    if emit:
        for name,data in payload.items():(emit/name).write_bytes(data)
    else:
        for name,data in payload.items():
            kept=(HERE/name).read_bytes()
            need((gzip.decompress(kept)==gzip.decompress(data)) if name.endswith('.gz') else kept==data,'complete retained '+name)
    print('PASS_G20_TRACE_RESYNTHESIS',saved,result['rounds'],result['replacements'])


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--emit',type=Path)
    run(p.parse_args().emit)
