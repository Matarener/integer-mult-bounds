"""Raw finite-field pencil SL labels and maps. Apache-2.0.

Ali Romman with substantial OpenAI Codex assistance. The retained raw
extractor and complete fixed-slice character theorem keep their credit.
"""
import hashlib
from itertools import product
import json
from pathlib import Path
import random
import sys

ROOT=Path(__file__).resolve().parent


def need(ok,message):
    if not ok:raise ValueError(message)


def authenticate():
    rows=json.loads((ROOT/'SOURCES.json').read_text())['files'];count=0
    for row in rows:
        if row['usage']!='input':continue
        path=ROOT/Path(row['path']).relative_to('research/raw-pencil-sl-transport')
        raw=path.read_bytes()
        need(hashlib.sha256(raw).hexdigest()==row['sha256'],'source hash: '+str(path))
        need(hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==row['git_blob'],'source blob')
        count+=1
    return count


authenticate()
sys.path.insert(0,str(ROOT/'vendor/raw'))
import decompose as d
Field=d.a.Field


def multiply(A,B,f):return d.mm(A,B,len(B[0]) if B else 0,f)

def transpose(A,n):return d.tr(A,n)

def pair_product(x,y,f):return tuple(f.mul[a][b] for a,b in zip(x,y))


def action(slices,maps,f):
    A,B=slices;P,Q,S=maps;qt=transpose(Q,len(Q))
    return tuple(multiply(multiply(P,[[f.add[f.mul[x][a]][f.mul[y][b]] for a,b in zip(r,s)]
                                     for r,s in zip(A,B)],f),qt,f) for x,y in S)


def compose(left,right,f):return tuple(multiply(a,b,f) for a,b in zip(left,right))


def inverse(maps,f):return tuple(d.a.inverse(a,f) for a in maps)


def special_linear_two(f):
    for a,b,c,e in product(range(f.q),repeat=4):
        if f.add[f.mul[a][e]][f.neg[f.mul[b][c]]]==1:yield [[a,b],[c,e]]


def validate(slices,m,n,f):
    need(isinstance(f,Field),'explicit common finite field')
    need(type(m) is int and type(n) is int and m>0 and n>0,'positive factor dimensions')
    need(isinstance(slices,(tuple,list)) and len(slices)==2,'two coefficient matrices')
    for A in slices:
        need(isinstance(A,(tuple,list)) and len(A)==m,'matrix row count')
        for row in A:
            need(isinstance(row,(tuple,list)) and len(row)==n and
                 all(type(x) is int and 0<=x<f.q for x in row),'canonical matrix row')


def dimensions(block):
    side,p,e=block
    if side=='right':return e,e+1
    if side=='left':return e+1,e
    size=e*(len(p)-1) if side=='finite' else e
    return size,size


def strict(slices,m,n,f):
    blocks,R,Q=d.decompose(*slices,m,n,f)
    starts=[];r=c=0
    for block in blocks:
        h,w=dimensions(block);starts.append((r,c,h,w));r+=h;c+=w
    indices=sorted(range(len(blocks)),key=lambda i:blocks[i])
    rows=[];cols=[]
    for i in indices:
        r,c,h,w=starts[i];rows+=list(range(r,r+h));cols+=list(range(c,c+w))
    E=[[int(j==old) for j in range(m)] for old in rows]
    F=[[int(j==old) for j in range(n)] for old in cols]
    maps=(multiply(E,d.a.inverse(R,f),f),multiply(F,transpose(Q,n),f),d.a.identity(2))
    ordered=tuple(blocks[i] for i in indices);A,B,_,_=d.model(ordered,f)
    need(action(slices,maps,f)==(A,B),'strict canonical coefficient equations')
    return ordered,(A,B),maps


def character(block,u,f):
    side,p,e=block;v=f.inv[u]
    if side=='right':return f.power(u,e),f.power(v,e+1)
    if side=='left':return f.power(v,e+1),f.power(u,e)
    return f.power(u,e),f.power(v,e)


def subgroup(blocks,f):
    generators={}
    for i,block in enumerate(blocks):
        for u in range(1,f.q):generators.setdefault(character(block,u,f),(i,u))
    paths={(1,1):()};queue=[(1,1)]
    for current in queue:
        for char,step in generators.items():
            target=pair_product(current,char,f)
            if target not in paths:
                paths[target]=paths[current]+(step,);queue.append(target)
    return paths


def diagonal(size,first):
    out=d.a.identity(size);out[0][0]=first;return out


def analyze(slices,m,n,f):
    """Return the deterministic complete label and its fixed representative."""
    validate(slices,m,n,f);best=None;groups={};actions=0;strict_results={}
    identities=(d.a.identity(m),d.a.identity(n))
    for S in special_linear_two(f):
        changed=action(slices,identities+(S,),f)
        raw_key=tuple(tuple(tuple(row) for row in A) for A in changed)
        if raw_key not in strict_results:strict_results[raw_key]=strict(changed,m,n,f)
        blocks,model,maps=strict_results[raw_key]
        if blocks not in groups:groups[blocks]=subgroup(blocks,f)
        H=groups[blocks];det=tuple(d.a.determinant(M,f) for M in maps[:2])
        label=min(pair_product(det,h,f) for h in H)
        key=(m,n,blocks,label);actions+=1
        if best is None or key<best['key']:
            needed=pair_product(label,tuple(f.inv[x] for x in det),f)
            scale=(diagonal(m,f.inv[label[0]]),diagonal(n,f.inv[label[1]]),d.a.identity(2))
            best=dict(key=key,representative=action(model,scale,f),model=model,blocks=blocks,
                      to_strict=maps[:2]+(S,),scale=scale,correction_path=H[needed],
                      fixed_character_size=len(H))
    best['slice_actions']=actions
    return best


def norm_unit(poly,target,f,rng):
    """Find an exact residue unit. Uniform sampling has at most q mean trials."""
    need(type(target) is int and 0<target<f.q,'nonzero norm target')
    need(len(poly)>=2 and poly[-1]==1 and d.factor(poly,f)==[tuple(poly)],'irreducible norm polynomial')
    degree=len(poly)-1;exponent=(f.q**degree-1)//(f.q-1);trials=0
    while True:
        value=[rng.randrange(f.q) for _ in range(degree)];trials+=1
        if not any(value):continue
        norm=d.ppow(value,exponent,f,poly)
        need(len(norm)==1,'norm belongs to the base field')
        if norm[0]==target:return value,trials


def put(A,B,r,c):
    for i,row in enumerate(B):A[r+i][c:c+len(row)]=row


def fixed_witness(blocks,path,m,n,f,rng):
    P,Q=d.a.identity(m),d.a.identity(n);trials=0
    starts=[];r=c=0
    for block in blocks:
        h,w=dimensions(block);starts.append((r,c));r+=h;c+=w
    for index,u in path:
        block=blocks[index];side,poly,e=block;h,w=dimensions(block);v=f.inv[u]
        if side=='right':
            bp=[[u if i==j else 0 for j in range(h)] for i in range(h)]
            bq=[[v if i==j else 0 for j in range(w)] for i in range(w)]
        elif side=='left':
            bp=[[v if i==j else 0 for j in range(h)] for i in range(h)]
            bq=[[u if i==j else 0 for j in range(w)] for i in range(w)]
        else:
            if side=='finite':coefficients,used=norm_unit(poly,u,f,rng);trials+=used
            else:coefficients=[u]
            J=d.companion(d.ppow(poly if side=='finite' else (0,1),e,f),f)
            bp=d.peval(coefficients,J,f);bq=transpose(d.a.inverse(bp,f),w)
        need((d.a.determinant(bp,f),d.a.determinant(bq,f))==character(block,u,f),'literal block character')
        gp,gq=d.a.identity(m),d.a.identity(n);r,c=starts[index]
        put(gp,bp,r,r);put(gq,bq,c,c)
        P,Q=multiply(gp,P,f),multiply(gq,Q,f)
    model=d.model(blocks,f)[:2]
    need(action(model,(P,Q,d.a.identity(2)),f)==model,'complete fixed-slice stabilizer')
    return (P,Q,d.a.identity(2)),trials


def canonicalize(slices,m,n,f,rng=None):
    """Return a complete label, representative and literal SL map to it."""
    result=analyze(slices,m,n,f)
    correction,trials=fixed_witness(result['blocks'],result['correction_path'],m,n,f,
                                    random.SystemRandom() if rng is None else rng)
    maps=compose(result['scale'],compose(correction,result['to_strict'],f),f)
    need(all(d.a.determinant(M,f)==1 for M in maps),'three determinant-one maps')
    need(action(slices,maps,f)==result['representative'],'complete canonical SL endpoint')
    return dict(key=result['key'],representative=result['representative'],maps=maps,
                slice_actions=result['slice_actions'],norm_trials=trials)


def transporter(first,second,m,n,f,rng=None):
    a=canonicalize(first,m,n,f,rng);b=canonicalize(second,m,n,f,rng)
    if a['key']!=b['key']:return None
    maps=compose(inverse(b['maps'],f),a['maps'],f)
    need(all(d.a.determinant(M,f)==1 for M in maps),'transporter determinants')
    need(action(first,maps,f)==tuple(second),'raw-to-raw SL endpoint')
    return maps
