"""Search all order types of three leaves and four fixed connectors.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
import itertools
import json
from pathlib import Path
import time
import free_algebra as N

_original=N.equations

def pair_equations(g,order):
    names,eq=_original(g,order);out=[]
    for label,p in eq:
        if not label.startswith('chronology'):
            out.append((label,p));continue
        head,rc=label.split(':');c=int(head.split()[1]);r,col=map(int,rc.split(','))
        if c>=g:continue
        if r in (0,c+1) and col in (0,c+1):continue
        out.append((label,p))
    return names,out


def orders():
    good_words=sorted(set(itertools.permutations((0,0,1,1,2,2))))
    good_words=[w for w in good_words if w.index(0)<w.index(1)<w.index(2)]
    for good in good_words:
        for slots in itertools.combinations(range(10),6):
            slots=set(slots)
            for connectors in itertools.permutations(((3,0),(3,1),(4,0),(4,1))):
                giter=iter(good);biter=iter(connectors);seen=set();out=[]
                for i in range(10):
                    if i in slots:
                        c=next(giter);out.append((c,int(c in seen)));seen.add(c)
                    else:out.append(next(biter))
                yield out


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--limit',type=int,default=75600);ap.add_argument('--degree',type=int,default=2);args=ap.parse_args()
    N.equations=pair_equations;start=time.monotonic();hits=0;misses=[];examples=[]
    for i,order in enumerate(orders()):
        if i>=args.limit:break
        r=N.certificate(3,order,args.degree)
        if 'one' in r['certificates']:
            hits+=1
            if len(examples)<3:examples.append(r)
        else:misses.append(order)
        if (i+1)%1000==0:print(json.dumps({'orders':i+1,'certificates':hits,'unresolved':len(misses),'seconds':round(time.monotonic()-start,2)}),flush=True)
    report={'scope':'All order types of three good pairs and the four fixed connectors; no matrix size bound','degree':args.degree,'orders':hits+len(misses),'certificates':hits,'unresolved':misses,'examples':examples}
    Path(__file__).with_name(f'ORDER-SEARCH-D{args.degree}.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:report[k] for k in ('scope','degree','orders','certificates')}|{'unresolved':len(misses)}),flush=True)

if __name__=='__main__':main()
