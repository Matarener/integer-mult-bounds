"""Actual serialized coefficient path and independent native-ring oracle."""
from pathlib import Path
from types import SimpleNamespace as NS
from fractions import Fraction
from hashlib import sha256
import importlib.util, sys, json
import cse
HERE=Path(__file__).resolve().parent; ROOT=HERE.parents[1]
V=ROOT/'research/selected-bit-physical-caller/inputs/pr2753/predecessor/vendor'
def need(ok,msg):
    if not ok: raise ValueError(msg)
def load(name):
    p=V/(name+'.py');s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);sys.modules[name]=m;exec(compile(p.read_bytes(),str(p),'exec'),m.__dict__);return m

def setup(adapted):
    w=load('words');r=load('records');load('matrices');c=load('controller');ch=load('children');p=load('plan')
    class MeteredTape(r.Tape):
        created=[]
        def __init__(self):
            super().__init__();self.created.append(self)
    r.Tape=MeteredTape
    if adapted: ch.Callback=cse.install(c.Callback,V/'controller.py',vars(c))
    return w,r,c,ch,p

def eye(n): return [[int(i==j) for j in range(n)] for i in range(n)]
def mm(a,b,M):return [[sum(x*y for x,y in zip(row,col))%M for col in zip(*b)] for row in a]
def inv(a,M):
    from math import gcd
    n=len(a);rows=[list(row)+e for row,e in zip(a,eye(n))]
    for j in range(n):
        k=next(k for k in range(j,n) if gcd(rows[k][j],M)==1);rows[j],rows[k]=rows[k],rows[j]
        z=pow(rows[j][j],-1,M);rows[j]=[z*x%M for x in rows[j]]
        for i in range(n):
            if i!=j:
                z=rows[i][j];rows[i]=[(x-z*y)%M for x,y in zip(rows[i],rows[j])]
    return [row[n:] for row in rows]
def projector(low,high,M,q=3):
    a=[[(x+q*y)%M for x,y in zip(l,h)] for l,h in zip(low,high)]
    return mm([row[:7] for row in a],inv(a,M)[:7],M)
def fallback(p,M):
    from math import gcd
    rows=[[0]*128 for _ in range(128)]
    for i in range(64):
        for j in range(64):
            rows[i][j]=rows[127-i][127-j]=(int(i==j)-p[i][j])%M
            rows[i][127-j]=rows[127-i][j]=p[i][j]
    pi=list(range(128))
    for j in range(128):
        k=next(k for k in range(j,128) if gcd(rows[k][j],M)==1);rows[j],rows[k]=rows[k],rows[j];pi[j],pi[k]=pi[k],pi[j]
        v=pow(rows[j][j],-1,M)
        for i in range(128):
            if i!=j:
                z=rows[i][j]*v%M
                if z:rows[i]=[(x-z*y)%M for x,y in zip(rows[i],rows[j])]
    return [rows[i][i] for i in range(128)],pi

def case(h=1,kind='pair',field=0,half=False,adapted=False,seed=0,mutation=None,negative=False,history_kinds=None):
    w,r,c,ch,p=setup(adapted);root=64**(h+2);I=root.bit_length()+1;L=5;M=9
    ia=w.Arena(I,131072);ra=w.Arena(L,131072);mod=ra.input(M);ring=w.Ring(mod)
    low0=eye(64)
    for i in range(7):low0[i],low0[57+i]=low0[57+i],low0[i]
    specs={i:NS(code=i,good=bool(i),low=(eye(64) if i else low0),template=NS(q=3,rank=7,preparation=[[Fraction(x) for x in row] for row in eye(64)])) for i in (0,1)}
    history_kinds=['pair']*h if history_kinds is None else history_kinds
    need(len(history_kinds)==h,'history length')
    history=[({'good':0,'pair':1,'unit':2}[k],int(k=='good'),7,0,False,k=='unit') for k in history_kinds]
    program=r.Program.fixture(ia,ra,root,2,history,2)
    high=[]
    for k in range(h+1):
        a=[[0]*64 for _ in range(64)];a[(k+seed)%64][(k+seed)%64]=(seed+1)%3
        # Nonzero high lift which changes prepared entries but retains invertibility.
        a[(k+3)%64][(k+9)%64]=seed%3
        high.append(a)
    code=int(kind=='good');fields=r.Fields.fixture(ia,ra,[(int(k=='good'),a) for k,a in zip(history_kinds,high[:-1])]+[(code,high[-1])],2)
    if mutation=='high':fields.tape.cells[4]=w.ONE;fields.tape.cells[5]=w.ONE # first high digit 3 exceeds cap
    if mutation=='root':program.tape.cells[I+3]=w.ZERO;program.tape.cells[I+4]=w.ZERO
    saved=bytes(program.tape.cells),bytes(fields.tape.cells);live=set(ia.live),set(ra.live)
    ix=ia.input(0);live=(set(ia.live),set(ra.live))
    calls=[];old=ch.Callback.prepare
    def observe(self,slot,code,scope):calls.append(slot.inspect());return old(self,slot,code,scope)
    ch.Callback.prepare=observe
    ia.meter=w.Meter();ra.meter=w.Meter()
    for tape in r.Tape.created:tape.meter=w.Meter()
    original_inspect=w.Word.inspect
    w.Word.inspect=lambda self: (_ for _ in ()).throw(ValueError('runtime decode forbidden'))
    # Inspector used only in checker instrumentation, never by runtime.
    def observe(self,slot,code,scope):calls.append(original_inspect(slot));return old(self,slot,code,scope)
    ch.Callback.prepare=observe
    request=p.Request('child',ix,child_kind=kind,field=field,reverse=field>=64,half=half,negative_inverse=negative)
    result=None;error=None
    try:result=ch.coefficient(ring,ia,program,fields,specs,code,request)
    except ValueError as e:error=str(e)
    finally:w.Word.inspect=original_inspect
    observed=None if result is None else result.inspect()
    if result is not None:ra.free(result)
    need(saved==(bytes(program.tape.cells),bytes(fields.tape.cells)),'borrowed bytes')
    need(live==(set(ia.live),set(ra.live)),'numerical ownership')
    need(program.tape.head==fields.tape.head==1,'public heads')
    meter=lambda x:{k:getattr(x,k) for k in ('reads','writes','moves')}
    receipt=dict(history_kinds=history_kinds,h=h,kind=kind,field=field,half=half,seed=seed,adapted=adapted,result=observed,error=error,preparations=len(calls),slots=calls,index=meter(ia.meter),residue=meter(ra.meter),program=meter(program.tape.meter),fields=meter(fields.tape.meter),negative=negative,record_total={k:sum(getattr(t.meter,k) for t in r.Tape.created) for k in ('reads','writes','moves')},record_tapes=len(r.Tape.created),index_backing=len(ia.words),residue_backing=len(ra.words))
    if mutation is None:
        need(error is None,'actual coefficient succeeds: '+str(error))
        descriptors=history+[(dict(good=0,pair=1,unit=2)[kind],code,7,field,field>=64,half)]
        prepared=[];sizes=[root]
        for desc,hi in zip(descriptors,high):
            k,co,rank,fi,rev,ha=desc;f=sizes[-1]//64
            sizes.append(rank*f if k==0 else f//2 if ha else f)
            if k==2:prepared.append(None)
            else:
                proj=projector(specs[co].low,hi,M)
                if k==1:prepared.append(fallback(proj,M))
                else:
                    rows=[row[:] for row in proj];piv=[]
                    for j in range(rank):
                        pivot=rows[j][j];piv.append(pivot);iv=pow(pivot,-1,M)
                        for i in range(j+1,64):
                            z=rows[i][j]*iv%M
                            if z:rows[i]=[(x-z*y)%M for x,y in zip(rows[i],rows[j])]
                    prepared.append(piv)
        def oracle(depth,coordinate):
            if depth==0:return 2
            k,co,rank,fi,rev,ha=descriptors[depth-1];f=sizes[depth-1]//64
            if k==2:return 1
            if k==0:return prepared[depth-1][coordinate//f]*oracle(depth-1,coordinate)%M
            diagonal,pi=prepared[depth-1];column=f-1-coordinate if rev else coordinate
            def bank(row):return oracle(depth-1,row*f+column) if row<64 else 1
            return diagonal[fi]*bank(pi[fi])*pow(bank(fi),-1,M)%M
        expected=oracle(h+1,0)
        if negative:expected=-pow(expected,-1,M)%M
        need(observed==expected,'independent local-ring result')
    else:need(error is not None,'malformed fixture rejected')
    ia.free(ix);program.tape.clear();fields.tape.clear();ring.close();ra.free(mod)
    return receipt

if __name__=='__main__':
    print(json.dumps(case(h=0,adapted=True),indent=2))
