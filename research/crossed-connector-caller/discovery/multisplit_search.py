"""Test three or more native calls per shared stage.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
import itertools
import json
from pathlib import Path
import time
import free_algebra as F
Z=F.ZERO;I=F.ONE
SPLITS=3

def orders(m):
    def rec(word,counts,max_seen):
        if len(word)==3*m:yield [(j,word[:i].count(j)) for i,j in enumerate(word)];return
        for j in range(min(2,max_seen+1)+1):
            if counts[j]<m:
                counts[j]+=1;yield from rec(word+[j],counts,max(max_seen,j));counts[j]-=1
    yield from rec([], [0,0,0],-1)

def equations(g,order):
    m=SPLITS;n=g+1;names=[];eq=[];good=[]
    for j in range(g):
        aa=[];bb=[];alast=I;blast=Z
        for h in range(m-1):
            a=F.var(len(names));b=F.var(len(names)+1);names.extend((f'A{j}_{h}',f'B{j}_{h}'));aa.append(a);bb.append(b);alast^=a;blast^=b
        aa.append(alast);bb.append(blast)
        for h,k in itertools.product(range(m),repeat=2):
            e=F.prod(aa[h],aa[k])^(aa[h] if h==k else Z)
            f=F.prod(aa[h],bb[k])^F.prod(bb[h],aa[k])^(bb[h] if h==k else Z)
            if e:eq.append((f'A{j}_{h} A{j}_{k}',e))
            if f:eq.append((f'B{j}_{h} B{j}_{k}',f))
        group=[]
        for a,b in zip(aa,bb):
            p=[[Z]*n for _ in range(n)];r=[[Z]*n for _ in range(n)]
            for row,col in itertools.product((0,j+1),repeat=2):p[row][col]=a^b if row==col else b;r[row][col]=a
            group.append((p,r))
        good.append(group)
    tails=[]
    for i in range(m*g):
        s=len(names);k=[[F.var(s+2*r+c) for c in range(2)] for r in range(2)]
        names.extend(f'X{i}_{r}{c}' for r in range(2) for c in range(2))
        tails.append([[k[int(r>0)][int(c>0)] for c in range(n)] for r in range(n)])
    tail=[[Z]*n for _ in range(n)];out=[[[Z]*n for _ in range(n)] for _ in range(g)]
    for i,(j,k) in reversed(list(enumerate(order))):
        p,r=good[j][k];total=F.add(tail,tails[i]);out[j]=F.add(out[j],F.add(F.mul(p,total),F.mul(total,p)));tail=F.add(tail,r)
    for j,mat in enumerate(out):
        for row,values in enumerate(mat):
            for col,poly in enumerate(values):
                if row in (0,j+1) and col in (0,j+1):continue
                if poly:eq.append((f'chronology {j}:{row},{col}',poly))
    return names,eq

def main():
    global SPLITS
    ap=argparse.ArgumentParser();ap.add_argument('--splits',type=int,default=3);ap.add_argument('--degree',type=int,default=2);ap.add_argument('--limit',type=int,default=280);args=ap.parse_args();SPLITS=args.splits
    F.equations=equations;start=time.monotonic();hit=0;miss=[]
    for i,o in enumerate(orders(SPLITS)):
        if i>=args.limit:break
        r=F.certificate(3,o,args.degree)
        if 'one' in r['certificates']:hit+=1
        else:miss.append(o)
        if (i+1)%20==0:print(i+1,hit,len(miss),round(time.monotonic()-start,2),flush=True)
    Path(__file__).with_name(f'MULTISPLIT-M{SPLITS}-D{args.degree}.json').write_text(json.dumps({'orders':hit+len(miss),'certificates':hit,'unresolved':miss},indent=2)+'\n')
    print('FINAL',hit,len(miss),flush=True)
if __name__=='__main__':main()
