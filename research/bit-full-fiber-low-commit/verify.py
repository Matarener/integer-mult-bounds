#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Closed-source full-fiber consumer checks with independent local execution."""
from fractions import Fraction
from pathlib import Path
import gzip
import hashlib
import json
import sys

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from loader import load
from controller import compile_commit,compile_cache
from type_compiler import compile_types,right_action,inverse


def need(ok,message):
    if not ok: raise ValueError(message)


def execute(program,initial,limit):
    # Independent literal machine: the program observes no address or counter.
    cells=[dict(c) for c,h in initial]
    heads=[h for c,h in initial]
    low=list(heads);high=list(heads)
    pc=program.entry;steps=0
    while True:
        row=program.instructions[pc];op=row[0];steps+=1
        need(steps<=limit,'transition envelope')
        if op=='halt': break
        if op=='reject': raise ValueError(row[1])
        if op=='goto': pc=row[1];continue
        tape=row[1]
        if op=='branch': pc=dict(row[2]).get(cells[tape].get(heads[tape],0),row[3]);continue
        if op=='move': heads[tape]+=row[2]
        elif op=='write':
            if row[2]: cells[tape][heads[tape]]=row[2]
            else: cells[tape].pop(heads[tape],None)
        else: raise ValueError('nonlocal instruction')
        low[tape]=min(low[tape],heads[tape]);high[tape]=max(high[tape],heads[tape]);pc+=1
    return list(zip(cells,heads)),steps,sum(b-a+1 for a,b in zip(low,high))


def marked(symbols,origin=0):
    symbols=list(symbols)
    return ({origin:1,**{origin+i+1:v for i,v in enumerate(symbols)},origin+len(symbols)+1:2},origin+1)


def binary(value,origin):
    return marked([4 if value>>i&1 else 3 for i in range(value.bit_length())],origin)


def fixture(program,payload,Q,Z,cache,translated):
    origins=[(i*7-41 if translated else 0) for i in range(program.tapes)]
    bank=[({},o) for o in origins]
    bank[0]=marked((4 if b else 3 for b in payload),origins[0])
    bank[2]=binary(Q,origins[2]);bank[3]=binary(Z,origins[3])
    bank[4]=marked((4 if b else 3 for b in cache),origins[4])
    return bank


def check(program,permutation,D,cache,Q,Z,payload,modules,translated=False,primary=False):
    H=Q**D*Z;V=len(permutation)*H;K=len(cache)
    need(len(payload)==V,'complete payload')
    bank=fixture(program,payload,Q,Z,cache,translated)
    empty=[(dict(cells),head) for cells,head in bank]
    empty[4]=({},bank[4][1]-1)
    prep=compile_cache(modules['machine'],cache,program.tapes)
    prepared,prepare_steps,_=execute(prep,empty,5*len(cache)+16)
    need(prepared==bank,'literal full old-cache preparation')
    bound=128*(len(permutation)+D+1)*V+16*K+16+128*D
    output,steps,space=execute(program,bank,bound)
    expected=[0]*V
    for src,dst in enumerate(permutation):
        expected[dst*H:(dst+1)*H]=payload[src*H:(src+1)*H]
    need(output[0]==marked((4 if b else 3 for b in expected),bank[0][1]-1),'literal low-type push and installation')
    for i in (2,3): need(output[i]==bank[i],'descriptor or head changed')
    for i in (1,4,*range(5,program.tapes)):
        origin=bank[i][1]-(1 if i==4 else 0)
        need(output[i]==({},origin),'owned storage or head not erased: '+str(i))
    need(space<=(D+8)*V+2*K+64*(D+1),'visited-space envelope')
    if primary:
        m=modules['machine']
        machine=m.Machine(program,[m.Tape(c,h) for c,h in bank]).run(bound)
        need([(t.cells,t.head) for t in machine.tapes]==output and machine.steps==steps,'independent interpreter disagreement')
    return dict(types=len(permutation),dimensions=D,Q=Q,Z=Z,volume=V,steps=steps,visited=space,
                instructions=len(program.instructions),cache_prepare_steps=prepare_steps,endpoint_sha256=hashlib.sha256(bytes(expected)).hexdigest())


def main():
    raw,modules=load();m,c=modules['machine'],modules['counters']
    records=[]
    # Every low type in GL2(F3), not a chosen subset; both direction tables.
    matrix=[[1,1],[0,1]]
    for inverse_direction in (False,True):
        types,perm,cache=compile_types(3,matrix,inverse_direction)
        need(len(types)==48,'complete GL2 type count')
        program=compile_commit(m,c,perm,4,cache)
        for Q,Z in ((1,1),(3,1),(3,2)):
            V=len(perm)*Q**4*Z
            payload=[((i*i+3*i+7)^(i>>2))&1 for i in range(V)]
            records.append(check(program,perm,4,cache,Q,Z,payload,modules,True,primary=Q==1))
    # Exhaustive arbitrary-bit inputs for a nontrivial three-block permutation.
    perm=[2,0,1];cache=[0,1,1,0];program=compile_commit(m,c,perm,1,cache)
    for value in range(8):
        records.append(check(program,perm,1,cache,1,1,[(value>>i)&1 for i in range(3)],modules,primary=True))
    # The generic cache length is independent of V. This rejects the old 8K
    # invoice even at the exact requested K=1000, T=D=V=1 boundary.
    long_cache=[i%2 for i in range(1000)]
    long_program=compile_commit(m,c,[0],1,long_cache)
    long_record=check(long_program,[0],1,long_cache,1,1,[1],modules,True)
    need(long_record['steps']>128*3+8*1000+128,'long-cache undercharge control')
    records.append(long_record)
    # Read actual S8 and bind both modular directions to the actual source ABI.
    source=json.loads(gzip.decompress(raw['research/bit-row-route-generator/PROGRAM.json.gz']))
    S=[[Fraction(v) for v in row] for row in source['matcher']]
    source_checks=[]
    for q in (3,5,7):
        mod=[[v.numerator*pow(v.denominator,-1,q)%q for v in row] for row in S]
        inv=inverse(mod,q)
        old=tuple(int(i==j) for i in range(8) for j in range(8))
        extra=list(old);extra[5]=q-2;extra=tuple(extra)
        for g in (old,extra):
            mapped=right_action(g,mod,q)
            need(right_action(mapped,inv,q)==g,'actual source forward/inverse type')
            for w in (2,4):
                Q=q**(w-1);M=q*Q
                lift=[[v.numerator*pow(v.denominator,-1,M)%M for v in row] for row in S]
                for i in range(64):
                    r,col=divmod(i,8)
                    total=sum(g[r*8+j]*lift[j][col] for j in range(8))
                    need(total%q==mapped[i],'old-low source map')
                    source_checks.append((q,w,i,total//q%Q))
    # Boundary and actual-byte mutation controls.
    controls=[]
    for label,per,D,bits in [('duplicate_type',[0,0],1,[]),('zero_dimension',[0],0,[]),('bad_cache',[0],1,[2])]:
        try: compile_commit(m,c,per,D,bits)
        except ValueError: controls.append(label)
        else: raise ValueError('accepted '+label)
    bank=fixture(program,[0,1,0],1,1,cache,False)
    for label,tape,position,symbol in [('stale_cache',4,1,4),('short_payload',0,2,2),('zero_extent',2,1,3)]:
        mutant=[(dict(cells),head) for cells,head in bank]
        mutant[tape][0][position]=symbol
        try: execute(program,mutant,100000)
        except ValueError: controls.append(label)
        else: raise ValueError('accepted '+label)
    result=dict(schema_version=1,physical=records,source_cases=len(source_checks),controls=controls,
                scope='complete low-type block consumer; high/carry suppliers remain explicit inherited contracts')
    result['code_hashes']={name:hashlib.sha256((HERE/name).read_bytes()).hexdigest() for name in ('controller.py','type_compiler.py','loader.py','verify.py','PROOF.md')}
    canonical=json.dumps(result,indent=2,sort_keys=True)+'\n'
    if sys.argv[1:]==['--write-result']:(HERE/'RESULT.json').write_text(canonical)
    else:
        need(not sys.argv[1:],'arguments')
        need((HERE/'RESULT.json').read_text()==canonical,'receipt mismatch')
    print('PASS_FULL_FIBER_LOW_COMMIT complete_GL2_48 literal_payload cache_retired')


if __name__=='__main__':main()
