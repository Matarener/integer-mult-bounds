"""Exact free-algebra tests for the coupled star frame.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
import itertools
import json
from pathlib import Path
import time

ZERO=frozenset();ONE=frozenset(((),))

def var(x): return frozenset(((x,),))

def prod(a,b):
    out=set()
    for x in a:
        for y in b:
            z=x+y
            if z in out:out.remove(z)
            else:out.add(z)
    return frozenset(out)

def add(a,b):return [[x^y for x,y in zip(ar,br)] for ar,br in zip(a,b)]

def mul(a,b):
    n=len(a);out=[[ZERO]*n for _ in range(n)]
    for i in range(n):
        for k in range(n):
            for j in range(n):
                if a[i][k] and b[k][j]:out[i][j]^=prod(a[i][k],b[k][j])
    return out

def equations(g,order):
    n=g+1;c=var(2*g);gates=[];eq=[]
    names=[name+str(i) for i in range(g) for name in ('A','B')]+['C']
    for j in range(g):
        a=var(2*j);b=var(2*j+1)
        p=[[ZERO]*n for _ in range(n)];r=[[ZERO]*n for _ in range(n)];e=[[ZERO]*n for _ in range(n)];rg=[[ZERO]*n for _ in range(n)]
        for i,k in ((0,0),(0,j+1),(j+1,0),(j+1,j+1)):
            p[i][k]=(a^b) if i==k else b
            r[i][k]=a;rg[i][k]=ONE
        e[0][0]=e[j+1][j+1]=ONE
        gates.append(((p,r),(add(p,e),add(r,rg))))
        eq.append((f'A{j} idempotent',prod(a,a)^a))
        eq.append((f'B{j} centralizer',prod(a,b)^prod(b,a)^b))
    eq.append(('C idempotent',prod(c,c)^c))
    bad=[]
    for h in (c,ONE^c):
        p=[[ZERO]*n for _ in range(n)];a=[[ZERO]*n for _ in range(n)];b=[[ZERO]*n for _ in range(n)]
        p[0][0]=h
        for j in range(1,n):
            a[0][j]=h;b[j][0]=h
            for k in range(1,n):p[j][k]=h
        bad.extend(((p,a),(p,b)))
    out=[[[ZERO]*n for _ in range(n)] for _ in range(g+2)]
    tail=[[ZERO]*n for _ in range(n)]
    for j,k in reversed(order):
        p,r=gates[j][k] if j<g else bad[2*(j-g)+k]
        out[j]=add(out[j],add(mul(p,tail),mul(tail,p)));tail=add(tail,r)
    for j,mat in enumerate(out):
        for row,values in enumerate(mat):
            for col,p in enumerate(values):
                if p:eq.append((f'chronology {j}:{row},{col}',p))
    return names,eq


def certificate(g,order,degree=3):
    names,eq=equations(g,order);alphabet=range(len(names))
    words=[()]
    for d in range(1,degree+1):words.extend(itertools.product(alphabet,repeat=d))
    index={w:i for i,w in enumerate(words)};basis={};generators=[];tested={}
    def encode(p):return sum(1<<index[w] for w in p)
    for ei,(_,p) in enumerate(eq):
        deg=max(map(len,p),default=0)
        for length in range(degree-deg+1):
            for leftsize in range(length+1):
                for word in itertools.product(alphabet,repeat=length):
                    left=word[:leftsize];right=word[leftsize:]
                    shifted=frozenset(left+w+right for w in p)
                    value=encode(shifted);rep=1<<len(generators)
                    generators.append((ei,left,right))
                    while value:
                        pivot=value.bit_length()-1
                        if pivot not in basis:
                            basis[pivot]=(value,rep);break
                        row,combo=basis[pivot];value^=row;rep^=combo
    for label,p in [('one',ONE),('C',var(2*g)),('one_plus_C',ONE^var(2*g))]:
        value=encode(p);rep=0
        while value:
            pivot=value.bit_length()-1
            if pivot not in basis:break
            row,combo=basis[pivot];value^=row;rep^=combo
        if value==0:
            terms=[generators[i] for i in range(len(generators)) if rep>>i&1]
            # Independent literal expansion of the relation.
            check=ZERO
            for ei,left,right in terms:check^=frozenset(tuple(left)+w+tuple(right) for w in eq[ei][1])
            if check!=p:raise ValueError('Bad ideal certificate')
            tested[label]=terms
    return {'g':g,'order':order,'degree':degree,'names':names,'equations':[(label,[list(w) for w in sorted(p)]) for label,p in eq],'monomials':len(words),'rows':len(generators),'rank':len(basis),'certificates':tested}


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--degree',type=int,default=3);ap.add_argument('--limit',type=int,default=1);args=ap.parse_args()
    g=3;records=[];start=time.monotonic()
    for second in itertools.permutations(range(g)):
        for bad in itertools.permutations(((3,0),(3,1),(4,0),(4,1))):
            order=[(j,0) for j in range(g)]+list(bad)+[(j,1) for j in second]
            r=certificate(g,order,args.degree);records.append(r)
            print(json.dumps({k:r[k] for k in ('order','rows','rank','monomials')}|{'certificates':{k:len(v) for k,v in r['certificates'].items()},'seconds':round(time.monotonic()-start,2)}),flush=True)
            if len(records)>=args.limit:break
        if len(records)>=args.limit:break
    Path(__file__).with_name(f'NC-STAR-D{args.degree}.json').write_text(json.dumps(records,indent=2)+'\n')

if __name__=='__main__':main()
