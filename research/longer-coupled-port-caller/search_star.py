"""Search the coupled split of the constant-loss star frame.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
This is a binary necessary-condition search, not a native caller.
"""
import importlib.util
import itertools
import json
from pathlib import Path
import time

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('predecessor', ROOT/'research/productive-controller-basis-search/algebra.py')
old = importlib.util.module_from_spec(spec)
spec.loader.exec_module(old)

def mul(a, b):
    out = []
    for row in a:
        value = 0
        while row:
            bit = row & -row
            value ^= b[bit.bit_length()-1]
            row ^= bit
        out.append(value)
    return tuple(out)

def add(a, b):
    return tuple(x^y for x,y in zip(a,b))

def comm(a, b):
    return add(mul(a,b),mul(b,a))

def packed(a):
    n=len(a)
    return sum(x << (n*i) for i,x in enumerate(a))

def outer(a,b,n):
    return tuple(b if a>>i&1 else 0 for i in range(n))

def embed(a, indices, n):
    out=[0]*n
    for i,row in enumerate(a):
        out[indices[i]]=sum((1<<indices[j]) for j in range(len(indices)) if row>>j&1)
    return tuple(out)


def frame(g):
    if g<3 or g%2!=1:
        raise ValueError('Use an odd leaf count at least three.')
    n=2*(g+1)
    # Two core coordinates, then two coordinates for each leaf.
    local=(5,10,5,10)
    identity=(1,2,4,8)
    ps=sorted(set(p for p,_ in old.FULL))
    options=[]
    for p in ps:
        if mul(p,local)!=mul(local,p): continue
        r=mul(p,local)
        if old.rank(r)!=1: continue
        other=add(identity,p)
        options.append(((p,r),(other,add(local,r))))
    good=[]
    for j in range(g):
        indices=(0,1,2+2*j,3+2*j)
        good.append([tuple((embed(p,indices,n),embed(r,indices,n)) for p,r in pair) for pair in options])
    bad=[]
    for k in range(2):
        c=1<<k
        w=sum(1<<(2+2*j+k) for j in range(g))
        p=add(outer(c,c,n),outer(w,w,n))
        bad.extend([(p,outer(c,w,n)),(p,outer(w,c,n))])
    total=(0,)*n
    for choices in good: total=add(total,add(choices[0][0][1],choices[0][1][1]))
    for _,r in bad: total=add(total,r)
    if total!=tuple(1<<i for i in range(n)): raise ValueError('Bad query frame')
    return good,bad


def defects(good,bad,order,choice):
    n=len(bad[0][0]); g=len(good)
    out=[(0,)*n for _ in range(g+2)]
    tail=(0,)*n
    for c,k in reversed(order):
        p,r=good[c][choice[c]][k] if c<g else bad[2*(c-g)+k]
        out[c]=add(out[c],comm(p,tail))
        tail=add(tail,r)
    return tuple(packed(x) for x in out)


def tables(good,bad,order):
    g=len(good); z=[0]*g
    base=defects(good,bad,order,z)
    singles=[]
    for c in range(g):
        table=[]
        for x in range(len(good[c])):
            ch=z.copy();ch[c]=x
            table.append(tuple(a^b for a,b in zip(defects(good,bad,order,ch),base)))
        singles.append(table)
    pairs={}
    for c,d in itertools.combinations(range(g),2):
        tab=[]
        for x in range(len(good[c])):
            row=[]
            for y in range(len(good[d])):
                ch=z.copy();ch[c]=x;ch[d]=y
                val=defects(good,bad,order,ch)
                row.append(tuple(a^b^u^v for a,b,u,v in zip(val,base,singles[c][x],singles[d][y])))
            tab.append(row)
        pairs[c,d]=tab
    return base,singles,pairs


def search_order(good,bad,order):
    base,singles,pairs=tables(good,bad,order)
    g=len(good)
    # Concatenate all stage defects. Every bit must be zero.
    n=len(bad[0][0]); stride=n*n
    join=lambda x:sum(v<<(stride*j) for j,v in enumerate(x))
    b=join(base)
    s=[[join(x) for x in tab] for tab in singles]
    p={cd:[[join(x) for x in row] for row in tab] for cd,tab in pairs.items()}
    survivors=[]
    if g==3:
        for x in range(len(s[0])):
            for y in range(len(s[1])):
                val=b^s[0][x]^s[1][y]^p[0,1][x][y]
                for z in range(len(s[2])):
                    if val^s[2][z]^p[0,2][x][z]^p[1,2][y][z]==0:
                        survivors.append((x,y,z))
        return survivors
    raise ValueError('This exhaustive entry point uses three leaves.')


def main():
    good,bad=frame(3);g=3; start=time.monotonic()
    print(json.dumps({'options_per_stage':len(good[0]),'frame_fields':8,'calls':10}),flush=True)
    records=[]
    first=[(j,0) for j in range(g)]
    bad_calls=[(3,0),(3,1),(4,0),(4,1)]
    # First occurrences are in canonical order. Test all second sweeps and all
    # connector orders between the sweeps. This does not cover every order.
    for second in itertools.permutations(range(g)):
        for connectors in itertools.permutations(bad_calls):
            order=first+list(connectors)+[(j,1) for j in second]
            survivors=search_order(good,bad,order)
            rec={'order':order,'chronology_survivors':len(survivors),'examples':survivors[:4]}
            records.append(rec)
            if survivors: print(json.dumps(rec),flush=True)
        print(json.dumps({'second_sweep':second,'orders_done':len(records),'elapsed_seconds':round(time.monotonic()-start,2)}),flush=True)
    report={'scope':'All coupled centralizer splits of the fixed star query frame, three leaves, two sweeps with four fixed connectors in between','options_per_stage':len(good[0]),'orders':len(records),'assignments_per_order':len(good[0])**3,'survivors':sum(r['chronology_survivors'] for r in records),'records':records}
    Path(__file__).with_name('STAR-SEARCH.json').write_text(json.dumps(report,indent=2)+'\n')

if __name__=='__main__': main()
