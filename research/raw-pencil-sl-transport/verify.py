#!/usr/bin/env python3
"""Independent finite SL orbits, exact maps and unbounded-interface fixtures."""
import argparse
from concurrent.futures import ProcessPoolExecutor
import hashlib
import importlib.util
from itertools import permutations,product
import json
from pathlib import Path
import random
import sys

ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
import sl


def authenticate():return sl.authenticate()

def need(ok,message):
    if not ok:raise ValueError(message)


def matrices(values,m,n):
    return tuple([list(values[k*m*n+i*n:k*m*n+(i+1)*n]) for i in range(m)] for k in (0,1))


def determinant(A,f):
    total=0
    for p in permutations(range(len(A))):
        v=1
        for i,j in enumerate(p):v=f.mul[v][A[i][j]]
        if sum(p[i]>p[j] for i in range(len(p)) for j in range(i+1,len(p)))%2:v=f.neg[v]
        total=f.add[total][v]
    return total


def literal(first,second,maps,f,small=True):
    P,Q,S=maps;m,n=len(P),len(Q)
    det=determinant if small else sl.d.a.determinant
    if any(det(M,f)!=1 for M in maps):return False
    for k,i,j in product(range(2),range(m),range(n)):
        total=0
        for t,a,b in product(range(2),range(m),range(n)):
            total=f.add[total][f.mul[f.mul[f.mul[S[k][t]][P[i][a]]][Q[j][b]]][first[t][a][b]]]
        if total!=second[k][i][j]:return False
    return True


def digits(code,q,width):
    out=[]
    for _ in range(width):out.append(code%q);code//=q
    return out


def neighbors(code,m,n,f):
    width=2*m*n;v=digits(code,f.q,width);powers=[f.q**i for i in range(width)]
    for axis,size in ((0,m),(1,n),(2,2)):
        for i in range(size):
            for j in range(size):
                if i==j:continue
                for c in range(1,f.q):
                    target=code
                    for k,r,s in product(range(2),range(m),range(n)):
                        if (r,s,k)[axis]!=i:continue
                        t,a,b=(j,r,s) if axis==2 else (k,j,s) if axis==0 else (k,r,j)
                        dest=k*m*n+r*n+s;source=t*m*n+a*n+b
                        value=f.add[v[dest]][f.mul[c][v[source]]]
                        target+=(value-v[dest])*powers[dest]
                    yield target


def orbit_ids(m,n,f):
    count=f.q**(2*m*n);ids=[-1]*count;components=0
    for start in range(count):
        if ids[start]>=0:continue
        ids[start]=components;queue=[start]
        for current in queue:
            for following in neighbors(current,m,n,f):
                if ids[following]<0:ids[following]=components;queue.append(following)
        components+=1
    return ids,components


def batch(args):
    p,modulus,m,n,lo,hi=args;f=sl.Field(p,modulus);out=[];trials=0
    for code in range(lo,hi):
        first=matrices(digits(code,f.q,2*m*n),m,n)
        cert=sl.canonicalize(first,m,n,f,random.Random(code+817))
        need(literal(first,cert['representative'],cert['maps'],f),'independent literal SL map')
        out.append(cert['key']);trials+=cert['norm_trials']
    return lo,out,trials


def exhaustive(p,modulus,m,n,workers):
    f=sl.Field(p,modulus);ids,components=orbit_ids(m,n,f);count=len(ids)
    tasks=[(p,modulus,m,n,i,min(i+128,count)) for i in range(0,count,128)]
    labels=[None]*count;trials=0
    if workers==1:answers=map(batch,tasks);pool=None
    else:pool=ProcessPoolExecutor(max_workers=workers);answers=pool.map(batch,tasks,chunksize=1)
    try:
        for start,keys,used in answers:labels[start:start+len(keys)]=keys;trials+=used
    finally:
        if pool is not None:pool.shutdown()
    by_orbit={};by_label={}
    for code,key in enumerate(labels):
        component=ids[code]
        need(by_orbit.setdefault(component,key)==key,'label constant on independent SL orbit')
        need(by_label.setdefault(key,component)==component,'distinct independent SL orbits separated')
    need(len(by_label)==components,'complete finite orbit partition')
    digest=hashlib.sha256(repr(labels).encode()).hexdigest()
    return dict(q=f.q,shape=[m,n],pencils=count,sl_orbits=components,norm_trials=trials,sha256=digest)


def first_irreducible(degree,f):
    constants=range(1,f.q) if degree>1 else range(f.q)
    for constant in constants:
        for tail in product(range(f.q),repeat=degree-1):
            p=(constant,)+tuple(tail)+(1,)
            if sl.d.factor(p,f)==[p]:return p
    raise ValueError('no irreducible polynomial')


def random_sl(n,f,rng):
    M=sl.d.a.identity(n)
    if n==1:return M
    for _ in range(3*n+2):
        i,j=rng.sample(range(n),2);c=rng.randrange(1,f.q)
        M[i]=[f.add[x][f.mul[c][y]] for x,y in zip(M[i],M[j])]
    return M


def fixtures():
    rng=random.Random(92841);records=[];transports=controls=no_slice=0
    for p,modulus in ((2,(0,1)),(3,(0,1)),(2,(1,1,1)),(3,(1,0,1))):
        f=sl.Field(p,modulus)
        specs=[(('finite',first_irreducible(4,f),1),),
               (('finite',(0,1),4),),
               (('right',(),6),('left',(),0)),
               (('right',(),1),)*4,
               (('left',(),0),('right',(),0),('finite',(1,1),2))]
        if f.q<=4:specs.append(tuple(('finite',(f.neg[a],1),1) for a in range(f.q))+(('infinity',(),1),))
        for blocks in specs:
            A,B,m,n=sl.d.model(blocks,f);raw=(A,B)
            maps=(random_sl(m,f,rng),random_sl(n,f,rng),random_sl(2,f,rng))
            changed=sl.action(raw,maps,f)
            first=sl.canonicalize(raw,m,n,f,rng);second=sl.canonicalize(changed,m,n,f,rng)
            need(first['key']==second['key'],'larger arbitrary-basis SL invariance')
            need(literal(raw,first['representative'],first['maps'],f,False),'larger first literal map')
            need(literal(changed,second['representative'],second['maps'],f,False),'larger second literal map')
            transport=sl.compose(sl.inverse(second['maps'],f),first['maps'],f)
            need(literal(raw,changed,transport,f,False),'larger raw-to-raw map');transports+=1
            if m==n:
                invertible=any(sl.d.a.determinant([[f.add[f.mul[x][u]][f.mul[y][v]] for u,v in zip(r,s)] for r,s in zip(A,B)],f)
                               for x,y in product(range(f.q),repeat=2) if x or y)
                no_slice+=int(not invertible)
            bad=tuple([row[:] for row in M] for M in first['maps']);bad[0][0]=[0]*m
            need(not literal(raw,first['representative'],bad,f,False),'singular map mutant rejected');controls+=1
            records.append(dict(q=f.q,shape=[m,n],blocks=blocks,slice_actions=first['slice_actions']))
    f=sl.Field(2,(0,1));raw=([[0] for _ in range(17)],[[0] for _ in range(17)])
    cert=sl.canonicalize(raw,17,1,f,rng)
    need(literal(raw,cert['representative'],cert['maps'],f,False),'dimension above source bounded interface')
    f=sl.Field(3,(0,1));x=([[1,0]],[[0,1]]);y=([[2,0]],[[0,1]])
    need(determinant(x[0]+x[1],f)==1 and determinant(y[0]+y[1],f)==2,'independent stacked determinant separation')
    need(sl.transporter(x,y,1,2,f,rng) is None,'inequivalent raw pencils rejected');controls+=1
    good=sl.transporter(x,x,1,2,f,rng);need(literal(x,x,good,f),'public transporter identity')
    native=([[1,0],[0,1]],[[0,1],[0,0]])
    changed=sl.action(native,([[1,1],[0,1]],sl.d.a.identity(2),sl.d.a.identity(2)),f)
    public=sl.transporter(native,changed,2,2,f,rng)
    need(native!=changed and literal(native,changed,public,f),'public nontrivial raw-to-raw transporter')
    invalid=[(([],[]),1,1),(([[0]],[[0]]),0,1),(([[3]],[[0]]),1,1),(([[True]],[[0]]),1,1),(([[0,0]],[[0]]),1,1)]
    for raw,m,n in invalid:
        try:sl.analyze(raw,m,n,f)
        except ValueError:controls+=1
        else:raise ValueError('invalid raw tensor accepted')
    return dict(fixtures=len(records)+1,larger_transports=transports,no_invertible_slice_cases=no_slice,
                controls=controls,records=records)


def norms():
    rng=random.Random(72619);checks=trials=0;degrees=[]
    for p,modulus in ((2,(0,1)),(3,(0,1)),(2,(1,1,1)),(3,(1,0,1))):
        f=sl.Field(p,modulus)
        for degree in range(1,9):
            poly=first_irreducible(degree,f);J=sl.d.companion(poly,f)
            for target in range(1,f.q):
                value,used=sl.norm_unit(poly,target,f,rng);trials+=used
                need(sl.d.a.determinant(sl.d.peval(value,J,f),f)==target,'independent multiplication determinant norm')
                for length in (1,2,4):
                    C=sl.d.companion(sl.d.ppow(poly,length,f),f)
                    need(sl.d.a.determinant(sl.d.peval(value,C,f),f)==f.power(target,length),'all-length lifted norm determinant')
                checks+=1
            degrees.append([f.q,degree])
    controls=0;f=sl.Field(3,(0,1))
    for poly,target in (((0,0,1),1),((1,1),0),((1,),1)):
        try:sl.norm_unit(poly,target,f,rng)
        except ValueError:controls+=1
        else:raise ValueError('invalid norm problem accepted')
    return dict(norm_targets=checks,sampled_candidates=trials,lifted_determinants=3*checks,field_degree_pairs=degrees,controls=controls)


def characters():
    path=ROOT/'vendor/characters/pencils.py';spec=importlib.util.spec_from_file_location('retained_characters',path)
    old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)
    rng=random.Random(717);records=[];triples=0
    specs=[(('R',1,1),),(('R',0,1),('L',0,1)),(('F',(0,1),2,1),),
           (('F',(0,1),1,1),('I',1,1)),(('R',1,1),('F',(1,1),1,1))]
    for q,p,modulus in ((2,2,(0,1)),(3,3,(0,1)),(4,2,(1,1,1))):
        f=sl.Field(p,modulus);g=old.Field(q)
        need(all(f.add[a][b]==g.add(a,b) and f.mul[a][b]==g.mul(a,b) for a,b in product(range(q),repeat=2)),'common field encoding')
        for model in specs:
            compiled=old.compile_model(model,g);m,n=compiled['dimensions'];raw=compiled['slices'];prior=old.orbit_labels(compiled)
            our_to_prior={};prior_to_our={}
            for triple in product(range(1,q),repeat=3):
                maps=(sl.diagonal(m,triple[0]),sl.diagonal(n,triple[1]),sl.diagonal(2,triple[2]))
                changed=sl.action(raw,maps,f);cert=sl.canonicalize(changed,m,n,f,rng)
                need(literal(changed,cert['representative'],cert['maps'],f,False),'character comparison literal map')
                label=prior[triple];key=cert['key']
                need(our_to_prior.setdefault(key,label)==label and prior_to_our.setdefault(label,key)==key,'complete supplied/raw SL quotient agreement')
                triples+=1
            records.append(dict(q=q,model=model,sl_orbits=len(our_to_prior)))
    return dict(models=len(records),determinant_triples=triples,records=records)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--phase',choices=('small','extension','fixtures','norms','characters'),required=True)
    parser.add_argument('--workers',type=int,default=4);args=parser.parse_args();need(1<=args.workers<=4,'bounded worker count')
    inputs=authenticate()
    if args.phase=='small':
        result={'domains':[exhaustive(p,mod,m,n,args.workers) for p,mod,m,n in ((2,(0,1),2,2),(2,(0,1),2,3),(2,(0,1),3,2),(3,(0,1),2,2),(3,(0,1),1,1),(3,(0,1),1,2),(3,(0,1),2,1))]}
    elif args.phase=='extension':result={'domains':[exhaustive(2,(1,1,1),m,n,args.workers) for m,n in ((2,2),(1,1),(1,2),(2,1))]}
    else:result=globals()[args.phase]()
    print(json.dumps(dict(status='PASS_RAW_PENCIL_SL_'+args.phase.upper(),source_inputs=inputs,**result),sort_keys=True,indent=2),flush=True)


if __name__=='__main__':main()
