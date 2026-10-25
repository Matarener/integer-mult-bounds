# SPDX-License-Identifier: Apache-2.0
"""Whole-array coordinate oracle and independent literal table execution."""
from pathlib import Path
import sys,json,gzip,hashlib
from fractions import Fraction
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from loader import authenticate,load_macros,need
from kernel import build,initialize_actual_T,LOW,CACHE


def invert(a):
    n=len(a);r=[list(row)+[Fraction(i==j) for j in range(n)] for i,row in enumerate(a)]
    for c in range(n):
        pivot=next(i for i in range(c,n) if r[i][c]);r[c],r[pivot]=r[pivot],r[c]
        v=r[c][c];r[c]=[x/v for x in r[c]]
        for i in range(n):
            if i!=c:
                v=r[i][c];r[i]=[x-v*y for x,y in zip(r[i],r[c])]
    return [row[n:] for row in r]


def dense(program,initial,limit):
    """Independent expanding-array interpreter; producer Machine is unused."""
    tapes=[];heads=[];visited=[]
    for cells,head in initial:
        n=max(cells,default=0)+2;t=[0]*n
        for k,v in cells.items():t[k]=v
        tapes.append(t);heads.append(head);visited.append(set())
    pc=program.entry;steps=0
    while steps<limit:
        row=program.instructions[pc];op=row[0];steps+=1
        if op=='halt':break
        if op=='reject':raise ValueError(row[1])
        if op=='goto':pc=row[1];continue
        i=row[1];h=heads[i];need(h>=0,'no negative fixture head')
        while len(tapes[i])<=h:tapes[i].append(0)
        visited[i].add(h)
        if op=='branch':pc=dict(row[2]).get(tapes[i][h],row[3]);continue
        if op=='write':tapes[i][h]=row[2]
        elif op=='move':heads[i]+=row[2];visited[i].add(heads[i])
        else:raise ValueError('unknown instruction')
        pc+=1
    else:raise ValueError('dense external step cap')
    return [(dict((k,v) for k,v in enumerate(t) if v),h) for t,h in zip(tapes,heads)],steps,sum(map(len,visited))


def fixture(mod, q,f,Q,Z,depth,values,seed,basis=None):
    m=mod['machine'];n=8*f;D=n*n;b=(q-1).bit_length();T=len(values);H=Q**depth*Z
    cache=[]
    for v in values:
        row=[int(i==j) for i in range(n) for j in range(n)]
        row[5*f]=v;row[4*f]=(v+1)%q
        cache.extend(row)
    payload=[((i*i+seed+3*i)^(i>>1))&1 for i in range(T*H)]
    if basis is not None:payload=[int(i==basis) for i in range(T*H)]
    return cache,payload


def run_case(mod,q,f,Q,Z,depth,values,inverse=False,seed=1,basis=None,dual=True,mutate=None,dirty=False,trailing=False):
    m=mod['machine'];D=(8*f)**2;b=(q-1).bit_length();T=len(values);H=Q**depth*Z;V=T*H
    cache,payload=fixture(mod,q,f,Q,Z,depth,values,seed,basis)
    program=build(mod,q,f,inverse,depth)
    if mutate:program=mutate(program)
    bank=[m.Tape() for _ in range(program.tapes)]
    bank[0]=m.marked(m.ONE if x else m.ZERO for x in payload)
    bank[4]=m.binary(T);bank[5]=m.binary(Q);bank[7]=m.binary(Z)
    bank[CACHE]=m.marked(m.ONE if (x>>k)&1 else m.ZERO for x in cache for k in range(b))
    if dirty:bank[17]=m.marked([m.ONE])
    if trailing:
        last=max(bank[CACHE].cells);bank[CACHE].cells[last]=m.ZERO;bank[CACHE].cells[last+1]=m.RIGHT
    initial=[(dict(t.cells),t.head) for t in bank]
    bound=2048*(depth+1)*V+32*T*D*b+256*(depth+1)
    space=(depth+20)*V+2*T*D*b+128*(depth+1)
    machine=m.Machine(program,bank).run(bound)
    result=[(dict(t.cells),t.head) for t in bank]
    if dual:
        other,steps,visited=dense(program,initial,bound)
        need(other==result and steps==machine.steps and visited==sum(map(len,machine.visits)),'independent interpreters agree')
    S=Q**(depth-1)*Z;wanted=[0]*V;lows=[]
    for t in range(T):
        v=cache[t*D+(4 if inverse else 5)*f]
        carry=0 if inverse else (2*v)//q;lows.append(v if inverse else 2*v%q)
        for x in range(Q):
            for z in range(S):wanted[t*H+((x+carry)%Q)*S+z]=payload[t*H+x*S+z]
    expected=m.marked(m.ONE if x else m.ZERO for x in wanted)
    need(result[0]==(expected.cells,1),'whole T output installed at original owner')
    lowout=m.marked(m.ONE if (x>>k)&1 else m.ZERO for x in lows for k in range(b))
    need(result[LOW]==(lowout.cells,1),'actual low0 result retained')
    for t in (4,5,7,CACHE):need(result[t]==initial[t],'preserved input/cache/head')
    for t in set(range(program.tapes))-{0,4,5,7,CACHE,LOW}:
        need(result[t]==({},0),'private erase and origin')
    need(machine.steps<=bound and sum(map(len,machine.visits))<=space,'complete tariff envelopes')
    return {'q':q,'f':f,'Q':Q,'Z':Z,'depth':depth,'T':T,'inverse':inverse,'bits':V,'steps':machine.steps,'visited':sum(map(len,machine.visits)),'instructions':len(program.instructions)}


def main():
    contents=authenticate();mod=load_macros(contents)
    source=json.loads(gzip.decompress(contents['research/bit-row-route-generator/PROGRAM.json.gz']))
    S=[[Fraction(v) for v in row] for row in source['matcher']];A=invert(S)
    need([row[0] for row in S]==[Fraction(2*(j==5)) for j in range(8)],'actual forward column0')
    need([row[0] for row in A]==[Fraction(j==4) for j in range(8)],'actual inverse column0')
    tables=json.loads(gzip.decompress((HERE/'TABLE.json.gz').read_bytes()))
    expected_tables={str(inverse):json.loads(json.dumps({'tapes':p.tapes,'entry':p.entry,'instructions':p.instructions}))
                     for inverse in (False,True) for p in [build(mod,5,1,inverse)]}
    need(tables==expected_tables,'actual depth64 finite tables match compiler')
    initializers=[]
    for q,f in [(3,1),(5,2),(7,1)]:
        m=mod['machine'];p=initialize_actual_T(mod,q,f);run=m.Machine(p).run()
        n=8*f;T=1
        for i in range(n):T*=q**n-q**i
        expected=m.binary(T)
        need(run.tapes[0].cells==expected.cells and run.tapes[0].head==1,'actual T initializer')
        need(run.steps==4*T.bit_length()+6,'initializer exact cost')
        other,steps,visited=dense(p,[({},0)],run.steps+1)
        need(other==[(expected.cells,1)] and steps==run.steps,'independent T initialization')
        initializers.append({'q':q,'f':f,'steps':steps,'bits':T.bit_length()})
    large=build(mod,3,4)
    need(large.tapes==1041,'default f4/D1024 compiler has no recursion limit')
    cases=[]
    for q in (3,5,7):
        for inverse in (False,True):
            for Q,Z,depth in [(3,1,1),(3,2,2),(5,1,3)]:
                cases.append(run_case(mod,q,1,Q,Z,depth,list(range(q)),inverse))
    for i in range(18):cases.append(run_case(mod,3,1,3,2,1,[0,2,1],basis=i))
    cases.append(run_case(mod,5,1,125,2,1,[3,0,4],False))
    cases.append(run_case(mod,5,2,3,1,2,[3,0,4],False))
    # Actual D compiler depths, Q1 only: structural microcode controls, not actual odd-q payload runs.
    for f in (1,2):cases.append(run_case(mod,5,f,1,2,(8*f)**2,[3,0],False))
    controls=0
    raw=contents['research/high-carry-streams/rotation.py']
    try:authenticate({'research/high-carry-streams/rotation.py':raw+b'\n# corruption\n'})
    except ValueError:controls+=1
    else:raise ValueError('source mutation escaped')
    for q,f in [(2,1),(5,0)]:
        try:build(mod,q,f)
        except ValueError:controls+=1
        else:raise ValueError('invalid compiler parameter escaped')
    def wrong_payload(program):
        code=list(program.instructions)
        pos=next(i for i,row in enumerate(code) if row==('write',0,mod['machine'].ZERO))
        code[pos]=('write',0,mod['machine'].ONE)
        return mod['machine'].Program(tuple(code),program.tapes,program.entry)
    for options in ({'mutate':wrong_payload},{'mutate':lambda p:build(mod,5,1,True,1)}, {'dirty':True},{'trailing':True}):
        try:run_case(mod,5,1,5,2,1,[3,0,4],**options)
        except ValueError:controls+=1
        else:raise ValueError('semantic mutation escaped')
    receipt={'status':'PASS_ACTUAL_CELLZERO_WHOLE_T_JOIN','cases':len(cases),'total_steps':sum(c['steps'] for c in cases),'max_steps':max(c['steps'] for c in cases),'dual_interpreter_cases':len(cases),'source_columns':'2e5 and e4; tensor lane proven','rejecting_controls':controls,'full_GL8_materialized':False,'new_kappa':False,'cases_detail':cases,'actual_T_initializers':initializers,'large_depth_compile':{'f':4,'depth':1024,'instructions':len(large.instructions)}}
    if (HERE/'RESULT.json').exists():need(receipt==json.loads((HERE/'RESULT.json').read_text()),'committed receipt')
    print(json.dumps(receipt,sort_keys=True,indent=2))

if __name__=='__main__':main()
