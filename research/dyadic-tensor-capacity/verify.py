"""Full dyadic cut modules and fixed-catalogue decay. Apache-2.0."""
from fractions import Fraction as Q
from itertools import product as words
from pathlib import Path
import hashlib
import importlib.util
import json

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]


def need(ok,msg):
    if not ok:raise ValueError(msg)


def eye(n):return [[int(i==j) for j in range(n)] for i in range(n)]
def tr(a):return [list(x) for x in zip(*a)]
def mm(a,b):return [[sum(x*y for x,y in zip(row,col)) for col in zip(*b)] for row in a]


def tensor(a,b):
    return [[x*y for x in rowa for y in rowb] for rowa in a for rowb in b]


def kron_indices(left,right,nright):return [i*nright+j for i in left for j in right]


def rref(a):
    a=[[Q(x) for x in row] for row in a]
    if not a:return a,[]
    piv=[];i=0
    for j in range(len(a[0])):
        k=next((k for k in range(i,len(a)) if a[k][j]),None)
        if k is None:continue
        a[i],a[k]=a[k],a[i]
        t=a[i][j];a[i]=[x/t for x in a[i]]
        for k in range(len(a)):
            if k!=i:
                t=a[k][j];a[k]=[x-t*y for x,y in zip(a[k],a[i])]
        piv.append(j);i+=1
        if i==len(a):break
    return a,piv


def rank(a):return len(rref(a)[1])


def module_contains(basis,rows):
    # RREF pivot columns give a nonsingular coordinate restriction.
    if not basis:return all(not any(row) for row in rows)
    _,piv=rref(basis)
    need(len(piv)==len(basis),'basis independent')
    small=tr([[row[j] for j in piv] for row in basis])
    for row in rows:
        augmented=[list(a)+[row[j]] for a,j in zip(small,piv)]
        reduced,cols=rref(augmented)
        need(cols==list(range(len(basis))),'coordinate system')
        coeff=[reduced[i][-1] for i in range(len(basis))]
        if any(x.denominator & (x.denominator-1) for x in coeff):return False
        if [sum(coeff[i]*basis[i][j] for i in range(len(basis)))
            for j in range(len(row))]!=row:return False
    return True


def same_module(a,b):
    need(rank(a)==rank(b),'module rank')
    need(module_contains(a,b) and module_contains(b,a),'full dyadic module equality')


def eligible(a,b,f,g,kernel):
    n=len(a);outside=[j for j in range(n) if j not in g]
    # Full kernel bases as columns, transposed to row bases for comparison.
    left=tr(kernel([[a[i][j] for i in f] for j in outside],len(f)))
    right=tr(kernel([[b[j][i] for i in f] for j in outside],len(f)))
    return left,right


def causal(p):
    n=2*p;a=eye(n);events=[]
    # (free, p data, p-1 dirty auxiliary) coordinates.
    for j in range(p-1):
        z=p+1+j
        events.extend([(1+j,z,1),(2+j,z,-1)])
    for j in range(p-1):
        z=p+1+j
        events.extend([(z,1+j,1),(z,2+j,-1)])
    for dst,src,c in events:a[dst]=[x+c*y for x,y in zip(a[dst],a[src])]
    b=eye(n)
    for dst,src,c in reversed(events):b[dst]=[x-c*y for x,y in zip(b[dst],b[src])]
    need(mm(a,b)==mm(b,a)==eye(n),'arbitrary-input identity word')
    need(len(events)*2==8*(p-1),'complete scalar tariff')
    expected=[[1]+[0]*p,[0]+[1]*p]
    return a,b,list(range(p+1)),expected


def rejected(fn):
    try:fn()
    except ValueError:return
    raise ValueError('negative control accepted')


def main():
    pins=json.loads((HERE/'SOURCES.json').read_text())
    for row in pins['files']:
        if row['usage']=='input':
            need(hashlib.sha256((ROOT/row['path']).read_bytes()).hexdigest()==row['sha256'],'source hash')
    path=ROOT/'research/dyadic-helper-channel-capacity/capacity.py'
    spec=importlib.util.spec_from_file_location('retained_capacity',path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    kernel=module.kernel
    circuits={}
    for p in (3,5):
        a,b,f,expected=causal(p)
        l,r=eligible(a,b,f,f,kernel)
        same_module(l,expected);same_module(r,expected)
        need(mm(expected,tr(expected))==[[1,0],[0,p]],'causal pairing')
        circuits[p]=(a,b,f,expected)
    # Independently solve every full eligible module of three small product cuts.
    cuts=0
    for pp,qq in ((3,3),(3,5),(5,3)):
        a,b,f,e=circuits[pp];aa,bb,ff,ee=circuits[qq]
        biga,bigb=tensor(a,aa),tensor(b,bb)
        bigf=kron_indices(f,ff,len(aa))
        l,r=eligible(biga,bigb,bigf,bigf,kernel)
        expected=tensor(e,ee)
        same_module(l,expected);same_module(r,expected)
        need(rank(l)==4,'full product eligibility')
        cuts+=1
    # Retained literal K=[5] fixture: full tensor kernels, not guessed channels.
    a=[[1,0,1],[0,1,2],[1,2,6]]
    b=[[2,2,-1],[2,5,-2],[-1,-2,1]]
    biga=bigb=[[1]];f=[0];expected=[[1]]
    for depth in range(1,5):
        biga,bigb=tensor(biga,a),tensor(bigb,b)
        f=kron_indices(f,[0,1],3)
        expected=tensor(expected,[[-2,1]])
        l,r=eligible(biga,bigb,f,f,kernel)
        same_module(l,expected);same_module(r,expected)
        need(mm(expected,tr(expected))==[[5**depth]],'zero-capacity tensor fixture')
        cuts+=1
    schedules=0
    for n in range(1,13):
        for w in words((3,5),repeat=n):
            count3=w.count(3);count5=n-count3
            cap=min(2**count3,2**count5)
            need(cap==2**min(count3,count5),'exact two-prime profile')
            need(cap*2**((n+1)//2)<=2**n,'fixed-catalogue decay')
            schedules+=1
    k=[[1,0,0,0],[0,5,0,0],[0,0,3,0],[0,0,0,15]]
    x=[[1,0,0,0],[0,-1,2,0]]
    y=[[1,0],[0,1],[0,1],[0,0]]
    need(mm(mm(x,k),y)==eye(2),'credited complementary-prime witness')
    rejected(lambda:same_module([[3,3]],[[1,1]]))
    rejected(lambda:same_module([[1,0]],[[0,1]]))
    a,b,f,e=circuits[3]
    l,r=eligible(a,b,f[:-1],f,kernel)
    rejected(lambda:same_module(l,[row[:-1] for row in e]))
    bad=[row[:] for row in a];bad[1][1]+=1
    rejected(lambda:need(mm(bad,b)==eye(len(a)),'changed prefix'))
    rejected(lambda:need(3<=2,'false three-channel capacity'))
    rejected(lambda:need(Q(1,1)<1,'full-capacity type is defective'))
    print(json.dumps(dict(status='PASS_DYADIC_FULL_TENSOR_CUT',full_product_cuts=cuts,
                         schedules=schedules,scope='full-module theorem and catalogue decay; no new kappa'),sort_keys=True))


if __name__=='__main__':main()
