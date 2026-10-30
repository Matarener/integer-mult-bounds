"""Sharp fixed-cut capacity enlargement; exact finite corroboration. Apache-2.0."""
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


def rank_mod(a,p):
    a=[[int(x)%p for x in row] for row in a]
    m=len(a);n=len(a[0]) if m else 0;i=0
    for j in range(n):
        k=next((k for k in range(i,m) if a[k][j]),None)
        if k is None:continue
        a[i],a[k]=a[k],a[i];u=pow(a[i][j],-1,p)
        a[i]=[x*u%p for x in a[i]]
        for k in range(m):
            if k!=i:
                u=a[k][j];a[k]=[(x-u*y)%p for x,y in zip(a[k],a[i])]
        i+=1
        if i==m:break
    return i


def full_word(d):
    n=3*d;a=eye(n);events=[]
    for block in range(d):
        x,y,z=range(3*block,3*block+3)
        events.extend([(x,z,1),(y,z,1),(y,z,1),(z,x,1),(z,y,1),(z,y,1)])
    for dst,src,c in events:a[dst]=[x+c*y for x,y in zip(a[dst],a[src])]
    b=eye(n)
    for dst,src,c in reversed(events):b[dst]=[x-c*y for x,y in zip(b[dst],b[src])]
    need(mm(a,b)==mm(b,a)==eye(n),'full arbitrary-dirty restoration')
    need(2*len(events)==12*d,'full signed ADD bill')
    return a,b


def pairing(a,b,f,g,kernel):
    out=[j for j in range(len(a)) if j not in g]
    l=tr(kernel([[a[i][j] for i in f] for j in out],len(f)))
    r=kernel([[b[j][i] for i in f] for j in out],len(f))
    return mm(l,r),l,r


def rejected(fn):
    try:fn()
    except ValueError:return
    raise ValueError('negative control accepted')


def main():
    pins=json.loads((HERE/'SOURCES.json').read_text())
    for row in pins['files']:
        if row['usage']=='input':
            need(hashlib.sha256((ROOT/row['path']).read_bytes()).hexdigest()==row['sha256'],'source bytes')
    path=ROOT/'research/dyadic-helper-channel-capacity/capacity.py'
    spec=importlib.util.spec_from_file_location('retained_capacity',path)
    old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)
    subsets=0
    for d in range(1,7):
        a,b=full_word(d);g=[j for j in range(3*d) if j%3!=2]
        k,l,r=pairing(a,b,g,g,old.kernel)
        need(k==[[5*int(i==j) for j in range(d)] for i in range(d)],'old full pairing')
        need(rank_mod(k,5)==old.capacity(k)['capacity']==0,'zero old capacity')
        for bits in words((0,1),repeat=d):
            added=[3*i+2 for i,x in enumerate(bits) if x]
            f=sorted(g+added);s=sum(bits)
            k,l,r=pairing(a,b,f,g,old.kernel);c=old.capacity(k)
            need(c['capacity']==2*s,'exact partial enlargement')
            need(c['rational_rank']==d+s,'full kernel dimensions')
            need(rank_mod(k,5)==2*s,'modular upper bound')
            if s:need(mm(mm(c['left'],k),c['right'])==eye(2*s),'literal unit block')
            subsets+=1
    # Independent field-rank census of every 2x2 bordering of a 1x1 block.
    bordered=0
    for p in (3,5):
        for entries in words(range(p),repeat=4):
            a=[[entries[0],entries[1]],[entries[2],entries[3]]]
            need(0<=rank_mod(a,p)-int(entries[0]!=0)<=2,'bordered rank bound')
            bordered+=1
    a,b=full_word(1)
    need(a==[[1,0,1],[0,1,2],[1,2,6]],'source literal prefix')
    need(b==[[2,2,-1],[2,5,-2],[-1,-2,1]],'source literal suffix')
    l=[b[0],b[1]];r=[[a[i][0],a[i][1]] for i in range(3)]
    need(mm(l,r)==eye(2),'full-cut source witness')
    u=[[-2,1],[1,0]]
    need(mm(mm(u,mm(l,r)),u)==[[5,-2],[-2,1]],'compatible bordered bases')
    need(old.capacity([[5,-2],[-2,1]])['capacity']==2,'sharp bordered unit')
    need(old.capacity([[Q(5,8)]])['capacity']==0,'dyadic scaling cannot invert five')
    need(old.capacity([[1,0],[0,5]])['capacity']==1,'mixed unit/nonunit control')
    rejected(lambda:need(2<=1,'false one-channel-per-coordinate bound'))
    rejected(lambda:need(old.capacity([[15]])['capacity']==1,'odd scaling false unit'))
    rejected(lambda:old.capacity([[Q(1,3)]]))
    bad=[row[:] for row in a];bad[0][0]+=1
    rejected(lambda:need(mm(bad,b)==eye(3),'changed prefix'))
    rejected(lambda:need(mm([[3*x for x in row] for row in l],r)==eye(2),'nonsaturated basis'))
    print(json.dumps(dict(status='PASS_DYADIC_CUT_ENLARGEMENT',support_enlargements=subsets,
                         bordered_matrices=bordered,sharp_gain_per_coordinate=2,
                         scope='fixed-prefix module theorem and scalar calibration; no new kappa'),sort_keys=True))


if __name__=='__main__':main()
