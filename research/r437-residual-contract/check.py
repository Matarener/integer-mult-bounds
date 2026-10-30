"""Actual encoded coefficient controls and independent vector-address algebra.

The oracle uses native integers solely as an independent finite checker.
The production path keeps Word.inspect disabled; runtime sources are unchanged.
"""
from collections import Counter
from contextlib import contextmanager
from hashlib import sha256
import json
from math import gcd
from pathlib import Path
import adapter

HERE=Path(__file__).resolve().parent

def need(ok,message):
    if not ok:raise ValueError(message)

def eye(n):return [[int(i==j) for j in range(n)] for i in range(n)]
def mul(a,b,M):
    out=[[0]*len(b[0]) for _ in a]
    for i,row in enumerate(a):
        for k,v in enumerate(row):
            if v:
                for j,w in enumerate(b[k]):
                    if w:out[i][j]=(out[i][j]+v*w)%M
    return out

def inv(a,M):
    n=len(a);rows=[list(r)+e for r,e in zip(a,eye(n))]
    for j in range(n):
        k=next(k for k in range(j,n) if gcd(rows[k][j],M)==1)
        rows[j],rows[k]=rows[k],rows[j]
        z=pow(rows[j][j],-1,M);rows[j]=[z*x%M for x in rows[j]]
        for i in range(n):
            if i!=j:
                z=rows[i][j]
                if z:rows[i]=[(x-z*y)%M for x,y in zip(rows[i],rows[j])]
    return [r[n:] for r in rows]

def rational(a,M):return [[x.numerator*pow(x.denominator,-1,M)%M for x in r] for r in a]

def prepare(spec,high,M):
    raw=[[(a+spec.template.q*b)%M for a,b in zip(x,y)] for x,y in zip(spec.low,high)]
    h=mul(raw,rational(spec.template.preparation,M),M);r=spec.template.rank
    return mul([x[:r] for x in h],inv(h,M)[:r],M)

def pivots(p,r,M):
    rows=[x[:] for x in p];out=[]
    for k in range(r):
        a=rows[k][k];out.append(a);z=pow(a,-1,M)
        for i in range(k+1,len(rows)):
            c=rows[i][k]*z%M
            if c:rows[i]=[(x-c*y)%M for x,y in zip(rows[i],rows[k])]
    need(all(x==0 for row in rows[r:] for x in row[r:]),'independent zero Schur complement')
    return out

def fallback(p,M):
    n=len(p);rows=[[0]*(2*n) for _ in range(2*n)]
    for i in range(n):
        for j in range(n):
            rows[i][j]=rows[2*n-1-i][2*n-1-j]=(int(i==j)-p[i][j])%M
            rows[i][2*n-1-j]=rows[2*n-1-i][j]=p[i][j]
    pi=list(range(2*n))
    for j in range(2*n):
        k=next(k for k in range(j,2*n) if gcd(rows[k][j],M)==1)
        rows[j],rows[k]=rows[k],rows[j];pi[j],pi[k]=pi[k],pi[j]
        z=pow(rows[j][j],-1,M)
        for i in range(2*n):
            if i!=j:
                c=rows[i][j]*z%M
                if c:rows[i]=[(x-c*y)%M for x,y in zip(rows[i],rows[j])]
    need(all(x==0 for i,row in enumerate(rows) for j,x in enumerate(row) if i!=j),'independent diagonal endpoint')
    return [row[i] for i,row in enumerate(rows)],pi

def vector(weights,kind,rank,field,reverse,half,p,M):
    f=len(weights)//64
    if kind=='unit':return [1]*(f//2 if half else f)
    if kind=='good':
        d=pivots(p,rank,M)
        return [weights[i]*d[i//f]%M for i in range(rank*f)]
    d,pi=fallback(p,M)
    def bank(row,j):return weights[row*f+j] if row<64 else 1
    return [d[field]*bank(pi[field],f-1-i if reverse else i)*pow(bank(field,f-1-i if reverse else i),-1,M)%M for i in range(f)]

def setup():
    catalogue,_=adapter.load()
    from catalogue import Specifications
    from macro_binding import SelectedBinding
    specs=Specifications(catalogue);binding=SelectedBinding(specs);defs={}
    for label,ident,common,good in [('ancestor',27776,False,True),('good',1603,True,True),('bad',1603,True,False)]:
        t=catalogue.template_for(ident,common);h=eye(64);r=t.rank
        if good:h[0][0]=1;h[0][r]=1;h[r][0]=1;h[r][r]=2
        else:
            for i in range(r):h[i],h[64-r+i]=h[64-r+i],h[i]
        low=tuple(map(tuple,mul(h,inv(rational(t.preparation,3),3),3)))
        d=binding.residual(ident,common,low,0)
        need(d.plan.good==good,'actual low branch')
        defs[label]=d
    need(defs['ancestor'].plan.rank==26 and defs['good'].plan.rank==7,'current OQ4 source ranks')
    return catalogue,specs,defs

@contextmanager
def observed_prepare():
    from controller import Callback
    from check_support import inspect_count
    old=Callback.prepare;calls=[]
    def wrapped(self,slot,code,scope):
        calls.append((inspect_count(slot),code));return old(self,slot,code,scope)
    Callback.prepare=wrapped
    try:yield calls
    finally:Callback.prepare=old

def encoded(catalogue,specs,defs,kind,field=0,reverse=False,half=False,coordinate=0,negative=False,high_seed=0,check_value=True):
    from check_support import no_decode,inspect_count,audit,bits
    from records import Program,Fields
    from words import Arena,Ring
    from children import coefficient
    from plan import Request
    res,idx=Arena(5,131072),Arena(13);mod=res.input(9);ring=Ring(mod)
    current=defs['good' if kind=='good' else 'bad'];ancestor=defs['ancestor']
    high=[]
    for level in range(2):
        matrix=[[0]*64 for _ in range(64)]
        for k in range(3):matrix[(7*k+level)%64][(11*k+high_seed+1)%64]=(k+1+high_seed)%3
        high.append(matrix)
    program=Program.fixture(idx,res,2048,2,[(0,ancestor.code,26,0,0,0)],catalogue.codes.bits)
    fields=Fields.fixture(idx,res,[(ancestor.code,high[0]),(current.code,high[1])],catalogue.codes.bits)
    saved=bits(program.tape),bits(fields.tape)
    p0=prepare(specs[ancestor.code],high[0],9);p1=prepare(specs[current.code],high[1],9)
    a=vector([2]*2048,'good',26,0,False,False,p0,9)
    expected=vector(a,kind,7,field,reverse,half,p1,9)[coordinate]
    index=idx.input(coordinate)
    with observed_prepare() as calls:
        with no_decode():value=coefficient(ring,idx,program,fields,specs,current.code,Request('child',index,child_kind=kind,field=field,reverse=reverse,half=half,negative_inverse=negative))
    observed=inspect_count(value)
    if negative:expected=-pow(expected,-1,9)%9
    if check_value:need(observed==expected,'actual encoded child coefficient equals independent vector contract')
    need(saved==(bits(program.tape),bits(fields.tape)),'borrowed program and complete raw fields unchanged')
    need(program.tape.head==fields.tape.head==1,'borrowed heads restored')
    # A unit descriptor stops immediately; good descends once; pair uses both
    # head operands even when the native permutation fixes the field.
    if kind=='unit':expected_preparations=0
    elif kind=='good':expected_preparations=2
    else:
        _,pi=fallback(p1,9);expected_preparations=1+int(field<64)+int(pi[field]<64)
    need(len(calls)==expected_preparations,'exact actual preparation tree count')
    record=dict(kind=kind,field=field,reverse=reverse,half=half,coordinate=coordinate,negative=negative,high_seed=high_seed,value=observed,preparations=len(calls),slots=[x[0] for x in calls])
    res.free(value);idx.free(index);program.tape.clear();fields.tape.clear();ring.close();res.free(mod);audit(res);audit(idx)
    return record

def leaf_controls():
    """Literal source trace; independent complete address action, no payload sampling."""
    from numeric import Geometry
    from trace import leaf
    from words import Arena
    from check_support import no_decode,inspect_count,audit
    from types import SimpleNamespace
    digest=sha256();cases=0;controls=set()
    # These finite address checks complement, not prove, the universal matrix identity.
    for width in (1,2,7,26,63):
        idx=Arena(10);columns,depth=idx.input(1),idx.input(0)
        page=Geometry(SimpleNamespace(dimension=64),idx,columns,depth,17,object())
        first,second,c=idx.input(0),idx.input(width),idx.input(width)
        ops=[]
        with no_decode():
            for e in leaf(page,first,second,c,'good'):
                ops.append((e.kind,inspect_count(e.first),None if e.second is None else inspect_count(e.second),None if e.request is None else inspect_count(e.request.coordinate),False if e.request is None else e.request.negative_inverse))
        need(len(ops)==8*width+2,'literal eight-stage count')
        need(Counter(x[0] for x in ops)==Counter({'enter':1,'return':1,'atom_swap':4*width,'add':3*width,'sign':width}),'complete primitive invoice')
        for M in (3,9,25):
            weights=[next(a for a in range(2+(i%3),M+2) if gcd(a,M)==1)%M for i in range(width)]
            for x in range(M):
                for y in range(M):
                    original=[(x+3*i)%M for i in range(width)]+[(y+2*i)%M for i in range(width)];state=original[:]
                    for kind,a,b,i,negative in ops:
                        if kind=='atom_swap':state[a],state[b]=state[b],state[a]
                        elif kind=='add':state[a]=(state[a]+(-pow(weights[i],-1,M) if negative else weights[i])*state[b])%M
                        elif kind=='sign':state[a]=-state[a]%M
                    target=[weights[i]*original[2*width-1-i]%M for i in range(width)]+[pow(weights[width-1-i],-1,M)*original[width-1-i]%M for i in range(width)]
                    need(state==target,'literal trace complete coordinate permutation');cases+=1;digest.update(bytes(state))
            # Deleting final sign or reversing middle reciprocal must fail.
            a=2 if M%2 else 3
            if gcd(a,M)==1:
                for mutant in ('omit_sign','wrong_inverse'):
                    state=[1,2%M]
                    for stage in range(8):
                        if stage%2==0:state.reverse()
                        elif stage==7:
                            if mutant!='omit_sign':state[1]=-state[1]%M
                        else:state[1]=(state[1]+((-pow(a,-1,M) if mutant!='wrong_inverse' else pow(a,-1,M)) if stage==3 else a)*state[0])%M
                    need(state!=[2*a%M,pow(a,-1,M)],'semantic leaf mutant rejection');controls.add(mutant)
        page.close();idx.free_many(columns,depth,first,second,c);audit(idx)
    return dict(address_cases=cases,widths=[1,2,7,26,63],digest=digest.hexdigest(),mutants=sorted(controls))

def pair_mutant(catalogue,specs,defs):
    # Compile one semantic mutation of the authenticated actual method. It still
    # executes real words/stacks/matrices; cleanup runs before comparison.
    import ast
    import controller
    path=Path(controller.__file__);tree=ast.parse(path.read_text())
    method=next(x for x in next(x for x in tree.body if isinstance(x,ast.ClassDef) and x.name=='Callback').body if isinstance(x,ast.FunctionDef) and x.name=='weight')
    changed=0
    for node in ast.walk(method):
        if isinstance(node,ast.Call) and isinstance(node.func,ast.Attribute) and node.func.attr=='multiply' and len(node.args)==2 and all(isinstance(x,ast.Name) for x in node.args) and [x.id for x in node.args]==['coefficient','numerator']:
            node.args[1].id='denominator';changed+=1
    need(changed==1,'one exact pair numerator mutation')
    namespace=dict(controller.__dict__);exec(compile(ast.fix_missing_locations(ast.Module([method],type_ignores=[])),str(path),'exec'),namespace)
    original=controller.Callback.weight;controller.Callback.weight=namespace['weight']
    try:record=encoded(catalogue,specs,defs,'pair',57,False,False,0,False,1,check_value=False)
    finally:controller.Callback.weight=original
    need(record['value']!=5,'wrong PAIR numerator accepted')
    return {'mutation':'replace_pair_numerator_with_denominator','correct':5,'mutant':record['value']}

def stream_controls():
    from stream import add_pass
    from records import Tape
    from cardinal_counts import Count
    from words import Arena,Ring
    from check_support import bits,no_decode,audit
    receipts=[]
    for M in (3,9):
        arena=Arena(M.bit_length()+1);mod=arena.input(M);ring=Ring(mod)
        counts=[Count.literal(x) for x in (2,3,2)];extents=[x.marginal() for x in counts]
        original=bytes(((i*7)^(i//5)^(i//13))&1 for i in range(12*M*M))
        source=Tape()
        for bit in original:source.append(bit)
        source.rewind();calls=[]
        for coefficient in (2,-pow(2,-1,M)%M,2):
            def prepare():
                calls.append(coefficient);return arena.literal(coefficient)
            with no_decode():out,_=add_pass(source,ring,*extents,prepare)
            expected=bytearray(len(original))
            def offset(b,x,g,y,s):return ((((b*M+x)*3+g)*M+y)*2+s)
            for b in range(2):
                for x in range(M):
                    for g in range(3):
                        for y in range(M):
                            for suffix in range(2):
                                expected[offset(b,x,g,(y+coefficient*x)%M,suffix)]=original[offset(b,x,g,y,suffix)]
            need(bits(out)==bytes(expected),'actual ADD complete dirty fibre permutation')
            need(bits(source)==original and source.head==1,'ADD borrowed source retained and reset')
            out.clear()
        need(calls==[2,2,-pow(2,-1,M)%M,-pow(2,-1,M)%M,2,2],'six physical preparations for three leaf ADD requests')
        source.clear()
        for extent in extents+counts:extent.close()
        ring.close();arena.free(mod);audit(arena)
        receipts.append({'modulus':M,'payload_bits':len(original),'preparations':calls})
    return receipts

def run(quick=False):
    catalogue,specs,defs=setup()
    if quick:return {'leaf':leaf_controls(),'add_pass':stream_controls(),'scope':'literal leaf trace finite address controls; encoded coefficient suite omitted'}
    cases=[('good',0,False,False,0,False,0),('good',0,False,False,90,True,1),('pair',0,False,False,12,False,0),('pair',57,False,False,0,False,1),('pair',70,True,False,12,True,2),('unit',0,False,True,5,False,2)]
    records=[encoded(catalogue,specs,defs,*args) for args in cases]
    return {'source':{'ancestor':27776,'copy':1603,'ranks':[26,7],'q':3,'modulus':9,'widths':[2048,832],'current_request_digest':adapter.REQUEST_DIGEST},'encoded':records,'pair_mutant':pair_mutant(catalogue,specs,defs),'leaf':leaf_controls(),'add_pass':stream_controls(),'scope':'actual word-tape coefficients at finite source-bound controls; literal leaf coordinate algebra, not a complete GL64 packet'}

if __name__=='__main__':print(json.dumps(run(),indent=2,sort_keys=True))
