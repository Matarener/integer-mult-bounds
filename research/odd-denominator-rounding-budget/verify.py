"""Exact fair-bit budget tradeoffs for rational stochastic rounding. Apache-2.0."""
from fractions import Fraction as Q
from itertools import product
from math import gcd
from pathlib import Path
import hashlib
import json

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]


def need(ok,msg):
    if not ok:raise ValueError(msg)


def bounds(a,b,r):
    need(type(a) is int and type(b) is int and 0<a<b and b%2==1 and gcd(a,b)==1,'reduced odd-denominator interior probability')
    need(type(r) is int and 0<=r<=16,'finite verification budget')
    n=1<<r;res=(a*n)%b
    return Q(min(res,b-res),b*n),Q(n%b,n)


def tree(a,b,depth):
    # Enumerate every fair-bit prefix, retaining all unresolved strings.
    # Uniform binary comparison to a/b; exact integer residue recursion.
    unresolved={():a};ones=zeros=0
    for t in range(1,depth+1):
        nxt={};ones*=2;zeros*=2
        for prefix,rem in unresolved.items():
            bit,newrem=divmod(2*rem,b)
            need(newrem!=0,'nondyadic comparison remainder')
            for coin in (0,1):
                if coin<bit:ones+=1
                elif coin>bit:zeros+=1
                else:nxt[prefix+(coin,)]=newrem
        unresolved=nxt
        need(len(unresolved)==1,'exact one unresolved fair prefix')
        need(ones+zeros+1==1<<t,'full stopping-tree mass')
        need(Q(ones,1<<t)<Q(a,b)<Q(ones+1,1<<t),'exact unfinished success interval')
    return ones,zeros,len(unresolved)


def sample(a,b,bits):
    rem=a
    for i,coin in enumerate(bits):
        need(coin in (0,1),'fair-bit value')
        digit,rem=divmod(2*rem,b)
        if coin<digit:return 1,i+1
        if coin>digit:return 0,i+1
    return None,len(bits)


def rejected(fn):
    try:fn()
    except ValueError:return
    raise ValueError('negative control accepted')


def main():
    pins=json.loads((HERE/'SOURCES.json').read_text())
    for row in pins['files']:
        if row['usage']=='input':
            need(hashlib.sha256((ROOT/row['path']).read_bytes()).hexdigest()==row['sha256'],'source bytes')
    lattice=0
    for b in range(3,32,2):
        for a in range(1,b):
            if gcd(a,b)!=1:continue
            for r in range(0,11):
                n=1<<r;bias,abort=bounds(a,b,r)
                # Independent exhaustive integer output-count oracle.
                best=min(abs(k*b-a*n) for k in range(n+1))
                need(bias==Q(best,b*n) and bias>0,'sharp bounded sampler bias')
                need(abort==Q(n-b*(n//b),n) and abort>0,'sharp exact conditional abort')
                lattice+=1
    triples=0
    for b in (3,5,7,9,11,13,15):
        for a in range(1,b):
            if gcd(a,b)!=1:continue
            for r in range(0,6):
                n=1<<r;accepted=0
                for one in range(n+1):
                    for zero in range(n-one+1):
                        total=one+zero
                        if total and b*one==a*total:
                            need(total%b==0,'exact conditional count divisor')
                            accepted=max(accepted,total)
                        triples+=1
                need(accepted==b*(n//b),'optimal accepted fair strings')
    trees=0;literal=0
    for b in range(3,20,2):
        for a in range(1,b):
            if gcd(a,b)!=1:continue
            tree(a,b,16);trees+=1
            one=zero=unresolved=0
            for bits in product((0,1),repeat=8):
                out,used=sample(a,b,bits)
                if out==1:one+=1
                elif out==0:zero+=1
                else:unresolved+=1
                need(1<=used<=8,'stopping length');literal+=1
            want=tree(a,b,8)
            need((one,zero,unresolved)==want,'literal full binary-tape oracle')
    # Capping and retrying preserves the law only at the correct congruence.
    for b in range(3,20,2):
        for a in range(1,b):
            if gcd(a,b)!=1:continue
            for r in range(1,11):
                one,zero,left=tree(a,b,r)
                need((Q(one,one+zero)==Q(a,b))==(((1<<r)-1)%b==0),
                     'exact capped-retry congruence')
    one,zero,left=tree(1,13,4)
    need((one,zero,left)==(1,14,1) and Q(one,one+zero)==Q(1,15),
         'four-bit retry changes 1/13 to 1/15')
    # Geometric stopping: E min(T,k)=2-2^(1-k), P(T>k)=2^-k.
    for k in range(1,65):
        need(sum((Q(1,1<<j) for j in range(k)),Q(0))==2-Q(1,1<<(k-1)),'exact truncated mean')
    table={}
    for r in (4,8,12,16):
        bias,abort=bounds(1,13,r)
        table[r]={'bias':str(bias),'abort':str(abort)}
    need(table[4]=={'bias':'3/208','abort':'3/16'},'denominator-13 four-bit fixture')
    need(table[12]=={'bias':'1/53248','abort':'1/4096'},'denominator-13 twelve-bit fixture')
    for r in range(0,17):
        worst=max(bounds(a,13,r)[0] for a in range(1,13))
        need(worst==Q(6,13*(1<<r)),'uniform residue worst bias')
    rejected(lambda:need(bounds(1,13,12)[0]==0,'false bounded exact sampler'))
    rejected(lambda:need(bounds(1,13,4)[1]<Q(3,16),'understated abort'))
    rejected(lambda:bounds(2,6,4))
    rejected(lambda:bounds(0,13,4))
    rejected(lambda:bounds(1,13,17))
    # A finite expected count cannot be used as a hard completion guarantee.
    need(tree(1,13,16)[2]==1,'positive mass remains at every fixed depth')
    print(json.dumps(dict(status='PASS_ODD_DENOMINATOR_ROUNDING_BUDGET',lattice_cases=lattice,
                         conditional_count_triples=triples,comparison_trees=trees,literal_tapes=literal,
                         denominator13=table,scope='sharp standalone sampler and capped-retry tradeoff; no inverse implementation or new kappa'),sort_keys=True))


if __name__=='__main__':main()
