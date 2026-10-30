"""Search arbitrary connectors on the core and the leaf sum.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
import itertools
import json
from pathlib import Path
import time
import free_algebra as F
Z=F.ZERO; I=F.ONE

def orders():
    for good in sorted(set(itertools.permutations((0,0,1,1,2,2)))):
        if not good.index(0)<good.index(1)<good.index(2):continue
        for slots in itertools.combinations(range(10),6):
            slots=set(slots);it=iter(good);seen=set();out=[];k=0
            for pos in range(10):
                if pos in slots:
                    j=next(it);out.append((j,int(j in seen)));seen.add(j)
                else:out.append((3,k));k+=1
            yield out

def equations(g,order):
    n=g+1;eq=[];names=[x+str(j) for j in range(g) for x in ('A','B')];good=[]
    for j in range(g):
        a=F.var(2*j);b=F.var(2*j+1)
        p=[[Z]*n for _ in range(n)];r=[[Z]*n for _ in range(n)];e=[[Z]*n for _ in range(n)];t=[[Z]*n for _ in range(n)]
        for row,col in itertools.product((0,j+1),repeat=2):
            p[row][col]=a^b if row==col else b;r[row][col]=a;t[row][col]=I
        e[0][0]=e[j+1][j+1]=I
        good.append(((p,r),(F.add(p,e),F.add(r,t))))
        eq.extend(((f'A{j} idempotent',F.prod(a,a)^a),(f'B{j} relation',F.prod(a,b)^F.prod(b,a)^b)))
    ks=[];last=[[Z,I],[I,Z]]
    for k in range(3):
        mat=[[F.var(len(names)+2*r+c) for c in range(2)] for r in range(2)]
        names.extend(f'K{k}_{r}{c}' for r in range(2) for c in range(2))
        ks.append(mat);last=F.add(last,mat)
    ks.append(last)
    for i,k in enumerate(ks):
        for r,row in enumerate(F.mul(k,k)):
            for c,poly in enumerate(row):
                if poly:eq.append((f'K{i} square {r},{c}',poly))
    for i,left in enumerate(ks):
        swapped=[[row[1],row[0]] for row in left]
        for j,right in enumerate(ks):
            product=F.mul(swapped,right)
            if i==j:product=F.add(product,left)
            for r,row in enumerate(product):
                for c,poly in enumerate(row):
                    if poly:eq.append((f'K{i} resolution K{j} {r},{c}',poly))
    bad=[[[k[int(r>0)][int(c>0)] for c in range(n)] for r in range(n)] for k in ks]
    tail=[[Z]*n for _ in range(n)];out=[[[Z]*n for _ in range(n)] for _ in range(g)]
    for j,k in reversed(order):
        if j<g:
            p,r=good[j][k]
            out[j]=F.add(out[j],F.add(F.mul(p,tail),F.mul(tail,p)))
        else:r=bad[k]
        tail=F.add(tail,r)
    for j,m in enumerate(out):
        for r,row in enumerate(m):
            for c,poly in enumerate(row):
                if r in (0,j+1) and c in (0,j+1):continue
                if poly:eq.append((f'chronology {j}:{r},{c}',poly))
    return names,eq

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--degree',type=int,default=2);ap.add_argument('--limit',type=int,default=3150);args=ap.parse_args()
    F.equations=equations;start=time.monotonic();miss=[];hits=0;first=[]
    for i,o in enumerate(orders()):
        if i>=args.limit:break
        r=F.certificate(3,o,args.degree)
        if 'one' in r['certificates']:
            hits+=1
            if len(first)<3:first.append(r)
        else:miss.append(o)
        if (i+1)%100==0:print(i+1,hits,len(miss),round(time.monotonic()-start,2),flush=True)
    report={'degree':args.degree,'orders':hits+len(miss),'certificates':hits,'unresolved':miss,'examples':first}
    Path(__file__).with_name(f'AGGREGATE-D{args.degree}.json').write_text(json.dumps(report,indent=2)+'\n')
    print('FINAL',hits,len(miss),flush=True)
if __name__=='__main__':main()
