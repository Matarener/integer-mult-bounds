"""Source-bound stochastic compute/accumulate/uncompute on an integer grid."""
from fractions import Fraction as Q
from itertools import product
from pathlib import Path
from random import Random
import gzip
import hashlib
import json

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
WORD='research/p104-helper-subspace-splits/WORD.json.gz'


def need(ok,msg):
    if not ok:raise ValueError(msg)


def sr(n,d,u):
    need(d>0 and d&(d-1)==0 and 0<=u<d,'dyadic coin domain')
    k,r=divmod(n,d)
    return k+int(u<r)


def source():
    pins=json.loads((HERE/'SOURCES.json').read_text())
    for row in pins['files']:
        if row['usage']=='input':
            raw=(ROOT/row['path']).read_bytes()
            need(hashlib.sha256(raw).hexdigest()==row['sha256'],'source bytes')
    raw=(ROOT/WORD).read_bytes();need(len(raw)<=1<<20,'compressed bound')
    with gzip.open(ROOT/WORD,'rb') as f:raw=f.read((1<<22)+1)
    need(len(raw)<=1<<22,'unpacked bound')
    w=json.loads(raw);need(w['public']==748 and w['frames'][3]==[],'source boundary')
    cut=next(i for i,e in enumerate(w['program']) if e[0]=='MOVE')
    need(cut==9589,'source scalar prefix')
    es=[]
    for e in w['program'][:cut]:
        op=e[0];need(op in ('ADD','SCALE') and e[-1]==3,'scalar opcode/chart')
        a=Q(e[-2]);n,d=a.numerator,a.denominator
        dst=e[1];src=e[2] if op=='ADD' else None
        need(0<=dst<748 and d in (1,2,4) and abs(a)<=16,'coefficient/role')
        if op=='ADD':need(0<=src<748 and src!=dst,'shear source')
        else:need(a in (Q(-1),Q(2),Q(1,2),Q(-1,2)),'supported SCALE')
        es.append((op,dst,src,n,d))
    return es


def forward(initial,events,tape):
    need(len(events)==len(tape),'tape length')
    x=list(initial);logs=[]
    for (op,dst,src,n,d),u in zip(events,tape):
        if op=='ADD':x[dst]+=sr(n*x[src],d,u)
        else:
            if d==2:logs.append((n*x[dst])%2)
            x[dst]=sr(n*x[dst],d,u)
        need(abs(x[dst]).bit_length()<=256,'finite fixture magnitude')
    return x,logs


def backward(current,events,tape,logs):
    x=list(current);logs=list(logs);j=len(logs)
    for (op,dst,src,n,d),u in reversed(list(zip(events,tape))):
        if op=='ADD':x[dst]+=sr(-n*x[src],d,d-1-u)
        elif d==2:
            need(n in (-1,1),'half sign');j-=1;r=logs[j]
            x[dst]=n*(2*x[dst]-2*int(u<r)+r)
            logs[j]^=(n*x[dst])%2
            need(logs[j]==0,'recomputed residue clears log')
        elif n==-1:x[dst]=-x[dst]
        elif n==2:
            need(x[dst]%2==0,'exact inverse on reached doubled image')
            x[dst]//=2
        else:raise ValueError('unsupported inverse SCALE')
    need(j==0 and not any(logs),'all owned residue bits restored')
    return x,logs


def protocol(initial,out,events,tape):
    need(isinstance(tape,tuple),'read-only coin tape')
    saved_tape=tuple(tape)
    result,logs=forward(initial,events,tape)
    target=[y+z for y,z in zip(out,result)]
    back,cleared=backward(result,events,tape,logs)
    need(back==list(initial),'arbitrary dirty data restored')
    need(tuple(tape)==saved_tape and not any(cleared),'tape/log boundary')
    return target,max((abs(v).bit_length() for v in result),default=0)


def rejected(fn):
    try:fn()
    except ValueError:return
    raise ValueError('negative control accepted')


def main():
    identities=0
    for d in (1,2,4,8,16):
        for n in range(-16,17):
            need(sum(sr(n,d,u) for u in range(d))==n,'exact unbiased marginal')
            for u in range(d):
                need(sr(-n,d,d-1-u)==-sr(n,d,u),'antithetic identity')
                for y in range(-4,5):
                    need(sr(d*y+n,d,u)==y+sr(n,d,u),'grid translation')
                identities+=1
    halves=0
    for x,sign,u in product(range(-64,65),(-1,1),(0,1)):
        es=[('SCALE',0,None,sign,2)]
        y,logs=forward([x],es,(u,));back,log=backward(y,es,(u,),logs)
        need(back==[x] and log==[0],'signed half recovery')
        halves+=1
    tiny=[('ADD',0,1,1,4),('SCALE',1,None,-1,2),('ADD',1,0,-1,2),
          ('SCALE',0,None,2,1),('SCALE',1,None,-1,1)]
    tiny_cases=0
    for a,b in product(range(-3,4),repeat=2):
        total=[0,0];exact=[Q(a),Q(b)]
        for op,dst,src,n,d in tiny:
            exact[dst]=exact[dst]+Q(n,d)*exact[src] if op=='ADD' else Q(n,d)*exact[dst]
        for u,v,w in product(range(4),range(2),range(2)):
            protocol([a,b],[5,-7],tiny,(u,v,w,0,0));tiny_cases+=1
            values,_=forward([a,b],tiny,(u,v,w,0,0))
            total=[x+y for x,y in zip(total,values)]
        need([Q(x,16) for x in total]==exact,'full tiny-word unbiased forward law')
    events=source()
    ops={op:sum(e[0]==op for e in events) for op in ('ADD','SCALE')}
    bits=sum(d.bit_length()-1 for _,_,_,_,d in events)
    h=sum(op=='SCALE' and d==2 for op,_,_,_,d in events)
    rounded=sum(d>1 for _,_,_,_,d in events)
    need(ops=={'ADD':9358,'SCALE':231} and bits==11713 and h==84 and rounded==7421,'source ledger')
    rng=Random(6026)
    fixtures=[[0]*748,[((i*73)%251)-125 for i in range(748)],
              [(-1 if i%2 else 1)*((1<<30)+104729*i) for i in range(748)],
              [rng.randrange(-10**6,10**6) for _ in range(748)]]
    full=peak=0
    for initial in fixtures:
        target=[i*17-12345 for i in range(748)]
        for mode in range(4):
            tape=tuple(0 if mode==0 else d-1 if mode==1 else i%d if mode==2
                       else hashlib.sha256(str(i).encode()).digest()[0]%d
                       for i,(_,_,_,_,d) in enumerate(events))
            _,size=protocol(initial,target,events,tape);peak=max(peak,size);full+=1
    # Same uncomplemented coin is an actual failing inverse, not a guarantee.
    y=sr(1,2,0);bad=y+sr(-1,2,0)
    need(bad!=0,'uncomplemented-coin counterexample')
    reused=sum(sr(sr(1,2,u),2,u) for u in (0,1))
    fresh=sum(sr(sr(1,2,u),2,v) for u,v in product((0,1),repeat=2))
    need(Q(reused,2)==Q(1,2) and Q(fresh,4)==Q(1,4),
         'restored tape is not fresh for an adaptive second shear')
    need(sr(0,2,1)==sr(1,2,1),'one side bit necessary for local halving')
    rejected(lambda:need(2*sr(1,2,0)==1,'discarded half residue'))
    es=[('SCALE',0,None,1,2)];y,log=forward([1],es,(0,));log[0]=0
    rejected(lambda:need(backward(y,es,(0,),log)[0]==[1],'corrupt residue'))
    rejected(lambda:sr(1,3,0))
    rejected(lambda:sr(1,2,2))
    rejected(lambda:forward([1],[],(0,)))
    print(json.dumps(dict(status='PASS_REVERSIBLE_STOCHASTIC_PREFIX',local_coin_identities=identities,
                         signed_halves=halves,tiny_protocols=tiny_cases,full_prefix_protocols=full,
                         events=9589,random_bits=bits,clean_residue_bits=h,
                         forward_reverse_and_copy_macros=2*len(events)+748,
                         peak_fixture_value_bits=peak,
                         scope='logical scalar-grid ABI; physical sampler/native costs open; no new kappa'),sort_keys=True))


if __name__=='__main__':main()
