"""Replay the complete binary word with independent stage variables.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
"""
import json
from pathlib import Path

def eye(n):return tuple(1<<i for i in range(n))
def add(a,b):return tuple(x^y for x,y in zip(a,b))
def mul(a,b):
    result=[]
    for row in a:
        v=0
        while row:
            bit=row&-row;v^=b[bit.bit_length()-1];row^=bit
        result.append(v)
    return tuple(result)

def product(a,b):
    n=len(next(iter(a.values())));zero=(0,)*n;out={}
    for x,ax in a.items():
        for y,by in b.items():
            if x[0]+y[0]>1:continue
            key=tuple(a+b for a,b in zip(x,y));out[key]=add(out.get(key,zero),mul(ax,by))
    return {k:v for k,v in out.items() if any(v)}

def replay(calls,order):
    n=len(calls[0]['p']);g=max(c['stage'] for c in calls);base=(0,)*(g+1);ebit=(1,)+(0,)*g
    word={base:eye(n)};expected={base:eye(n),ebit:eye(n)};targets=[(0,)*n for _ in range(g)]
    for c in calls:
        if c['stage']<g:targets[c['stage']]=add(targets[c['stage']],tuple(c['p']))
    for s,e in enumerate(targets):
        d=list(base);d[s+1]=1;expected=product({base:eye(n),tuple(d):e},expected)
    for i in order:
        c=calls[i];p=tuple(c['p']);r=tuple(c['r']);gate={base:eye(n),ebit:r}
        if c['stage']<g:
            d=list(base);d[c['stage']+1]=1;ed=d.copy();ed[0]=1
            gate[tuple(d)]=p;gate[tuple(ed)]=r
        word=product(gate,word)
    defects={k:add(word.get(k,(0,)*n),expected.get(k,(0,)*n)) for k in word.keys()|expected.keys()}
    defects={k:v for k,v in defects.items() if any(v)}
    return {'passed':not defects,'coefficients':len(word),'expected_coefficients':len(expected),'defect_coefficients':len(defects),'first_defect':next(iter(defects.items()),None)}

if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('--file',type=Path,default=Path(__file__).with_name('ESCAPE-WORD.json'));args=parser.parse_args()
    data=json.loads(args.file.read_text());records=data if isinstance(data,list) else [data]
    for record in records:
        if 'calls' in record:print(json.dumps({'case':record.get('case'),**replay(record['calls'],record['order'])}),flush=True)
