"""Allow an arbitrary aggregate matrix in every gap of the good word.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
"""
import itertools
import json
from pathlib import Path
import free_algebra as F
Z=F.ZERO;I=F.ONE

def orders():
    for good in sorted(set(itertools.permutations((0,0,1,1,2,2)))):
        if good.index(0)<good.index(1)<good.index(2):
            seen=set();out=[]
            for j in good:out.append((j,int(j in seen)));seen.add(j)
            yield out

def equations(g,order):
    n=g+1;names=[x+str(j) for j in range(g) for x in ('A','B')];eq=[];good=[]
    for j in range(g):
        a=F.var(2*j);b=F.var(2*j+1)
        p=[[Z]*n for _ in range(n)];r=[[Z]*n for _ in range(n)];e=[[Z]*n for _ in range(n)];t=[[Z]*n for _ in range(n)]
        for row,col in itertools.product((0,j+1),repeat=2):
            p[row][col]=a^b if row==col else b;r[row][col]=a;t[row][col]=I
        e[0][0]=e[j+1][j+1]=I
        good.append(((p,r),(F.add(p,e),F.add(r,t))))
        eq.extend(((f'A{j} idempotent',F.prod(a,a)^a),(f'B{j} relation',F.prod(a,b)^F.prod(b,a)^b)))
    # The tail after each good call is an independent connector total.
    # The first gap can supply the required remaining sum.
    tails=[]
    for i in range(2*g):
        s=len(names);k=[[F.var(s+2*r+c) for c in range(2)] for r in range(2)]
        names.extend(f'X{i}_{r}{c}' for r in range(2) for c in range(2))
        tails.append([[k[int(r>0)][int(c>0)] for c in range(n)] for r in range(n)])
    tail=[[Z]*n for _ in range(n)];out=[[[Z]*n for _ in range(n)] for _ in range(g)]
    for i,(j,k) in reversed(list(enumerate(order))):
        p,r=good[j][k];total=F.add(tail,tails[i])
        out[j]=F.add(out[j],F.add(F.mul(p,total),F.mul(total,p)));tail=F.add(tail,r)
    for j,m in enumerate(out):
        for r,row in enumerate(m):
            for c,poly in enumerate(row):
                if r in (0,j+1) and c in (0,j+1):continue
                if poly:eq.append((f'chronology {j}:{r},{c}',poly))
    return names,eq

def main():
    F.equations=equations;records=[]
    for o in orders():
        r=F.certificate(3,o,3);records.append(r)
        print(o,{k:len(v) for k,v in r['certificates'].items()},flush=True)
    Path(__file__).with_name('GAP-SEARCH.json').write_text(json.dumps(records,indent=2)+'\n')
if __name__=='__main__':main()
