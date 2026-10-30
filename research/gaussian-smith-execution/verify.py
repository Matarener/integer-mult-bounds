#!/usr/bin/env python3
"""Check arbitrary-input execution, exact invoice and precision witnesses."""
from pathlib import Path
import argparse
import hashlib
import itertools
import json
import random
import sys
from math import comb
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
import engine as E


def dense(x,n):
    out=[]
    for r in range(1<<n):
        y=E.ZERO
        for s,z in enumerate(x):
            y=E.add(y,E.phase(z,n-(r^s).bit_count()))
        out.append(y)
    return out


def residue_oracle(x,q):
    # Repeated parity digits use a different reduction algorithm.
    a,b=x
    result=E.ZERO
    for k in range(q):
        digit=(a+b)%2
        result=E.add(result,E.mul((digit,0),E.pi_power(k)))
        a-=digit
        a,b=(a+b)//2,(b-a)//2
    return E.residue(result,q)


def lower_precision_witness(n,P,k,r):
    Q=P-2*(r&((1<<k)-1)).bit_count()
    if Q<=0:
        return False
    cut=[E.ZERO]*(1<<n)
    cut[r]=E.pi_power(Q-1)
    x=list(cut)
    for axis in reversed(range(k)):
        bit=1<<axis
        for s in range(1<<n):
            if not s&bit:
                x[s]=E.add(x[s],E.phase(x[s+bit],1))
    output=E.raw_tensor(x,n)
    E.need(any(E.residue(z,P)!=E.ZERO for z in output),'One fewer T digit loses an output')
    E.need(E.residue(cut[r],Q-1)==E.ZERO,'Inputs collide after underprecision')
    return True


def run():
    origins=json.loads((ROOT/'ORIGINS.json').read_text())
    for o in origins:
        b=(ROOT/o['local']).read_bytes()
        for data,expect in ((b,True),(b+b'!',False)):
            good=hashlib.sha256(data).hexdigest()==o['sha256'] and hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==o['git_blob']
            E.need(good==expect,'Frozen source authentication')
    residue_checks=0
    for q in range(13):
        for a in range(-19,20):
            for b in range(-19,20):
                z=(a,b);v=E.residue(z,q)
                E.need(v==residue_oracle(z,q),'Independent parity-digit residue')
                E.need(E.exact_divide(E.add(z,E.neg(v)),q) is not None,'Residue ideal difference')
                residue_checks+=1
    rng=random.Random(5815)
    examples=[];checks=0;basis=0
    for n in range(0,11):
        N=1<<n
        inputs=[[tuple(rng.randrange(-257,258) for _ in range(2)) for _ in range(N)] for _ in range(3)]
        if n<=5:
            inputs += [[E.ONE if i==j else E.ZERO for i in range(N)] for j in range(N)]
            basis+=N
        for x in inputs:
            raw=E.raw_tensor(x,n)
            if n<=6:
                E.need(raw==dense(x,n),'Independent dense tensor oracle')
            for P in sorted({0,1,2,n,n+1,n+2,2*n,2*n+5}):
                y,invoice=E.execute(x,n,P)
                E.need(y==[E.residue(z,P) for z in raw],'Complete modular endpoint')
                f=E.formula(n,P)
                E.need(invoice['precision_mass']['ADD']==f['add_mass'],'Full addition precision mass')
                E.need([s[2] for s in invoice['stages'][:n]]==f['T'],'Every T stage cost')
                E.need([s[2] for s in invoice['stages'][n:]]==f['S'],'Every S stage cost')
                E.need(invoice['diagonal_bits']==f['diagonal_bits'],'Diagonal storage')
                checks+=1
        if n:
            x=inputs[0]
            y,receipt=E.install(x,n,header=3)
            E.need(y==E.raw_tensor(x,n),'Exact forward/swap/inverse installation')
            examples.append(dict(n=n,p=n,invoice=E.execute(x,n,2*n)[1],installation=receipt))
    sharp=0
    for n in range(1,6):
        for P in range(1,2*n+3):
            for k in range(n+1):
                for r in range(1<<n):
                    sharp+=lower_precision_witness(n,P,k,r)
    cardinalities=[]
    for n,P in ((1,1),(1,2),(1,3),(1,4),(2,1),(2,2),(2,3)):
        ring=sorted({E.residue((a,b),P) for a in range(1<<P) for b in range(1<<((P+1)//2))})
        E.need(len(ring)==2**P,'Canonical ring cardinality')
        images=set()
        for x in itertools.product(ring,repeat=1<<n):
            images.add(tuple(E.residue(z,P) for z in dense(x,n)))
        bits=E.formula(n,P)['diagonal_bits']
        E.need(len(images)==2**bits,'Exact all-input image information')
        cardinalities.append(dict(n=n,P=P,inputs=len(ring)**(1<<n),images=len(images),bits=bits))
    invoice_checks=0
    for n in range(1,129):
        for p in (0,1,2,n//3,n,n+1):
            P=p+n;bill=E.formula(n,P)['add_mass'];N=1<<n
            floor=N*(n*p+n*(n+1)//2)
            E.need(floor<=bill<=floor+N*n,'Whole-pass uniform invoice bounds')
            if p>=n-2:
                E.need(bill==floor,'Exact high-precision invoice')
            if p==n:
                E.need(4*n*bill==(3*n+1)*n*N*P,'Exact p=n ratio')
            invoice_checks+=1
    # A zero normalized precision still has a nonzero raw response.
    y,_=E.execute([E.ONE,E.ZERO,E.ZERO,E.ZERO],2,2)
    E.need(any(z!=E.ZERO for z in y),'Normalized precision zero is not a zero raw modulus')
    # Rectangular truncation at an odd precision loses a parity bit.
    E.need(E.residue((1,0),1)!=E.ZERO,'Odd-precision parity control')
    # Rounded forward installation does not permit exact inverse cleanup.
    x=[E.ONE,E.ZERO];y,_=E.exact(x,1);y[0]=E.add(y[0],E.pi_power(2))
    back,_=E.exact(y,1,inverse=True)
    E.need([E.exact_divide(z,2) for z in back]!=x,'Rounded result cannot clear old value')
    return dict(schema_version=1,source_head='f0fcda576df410dc15cd5b8183d4f74d284eba2b',
        residue_checks=residue_checks,endpoint_cases=checks,basis_axes=basis,
        minimal_T_precision_witnesses=sharp,image_cardinalities=cardinalities,
        invoice_cases=invoice_checks,examples=examples,source_corruptions=len(origins),
        controls=['zero normalized precision retains response','odd Gaussian precision retains parity',
                  'one fewer T digit loses output','rounded inverse cleanup fails'],
        scope='Exact indexed ordinary circuit and precision invoice; no physical tape cost or kappa claim.')


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--write-receipt',action='store_true');args=p.parse_args()
    result=run();path=ROOT/'RESULT.json'
    if args.write_receipt:
        with path.open('x') as f:json.dump(result,f,indent=2,sort_keys=True);f.write('\n')
    else:
        E.need(json.dumps(json.loads(path.read_text()),sort_keys=True)==json.dumps(result,sort_keys=True),'Exact typed stored receipt')
    print('PASS_GAUSSIAN_SMITH_EXECUTION',json.dumps({k:v for k,v in result.items() if k not in ('examples','image_cardinalities')},sort_keys=True))
