#!/usr/bin/env python3
"""Source-bound symplectic progress audit; unsigned ranks, not phase admission."""
import argparse
import hashlib
import importlib.util
import itertools
import json
import sys
from pathlib import Path
P=Path(__file__).resolve().parent
ROOT=P.parents[1]


def need(ok,message):
    if not ok:raise ValueError(message)


def read_json(path):
    def pairs(items):
        out={}
        for key,value in items:
            need(key not in out,'duplicate JSON key: '+key);out[key]=value
        return out
    return json.loads(path.read_text(),object_pairs_hook=pairs)


def rank(values):
    pivots={}
    for value in values:
        while value:
            bit=value.bit_length()-1
            if bit in pivots:value^=pivots[bit]
            else:pivots[bit]=value;break
    return len(pivots)


def apply(cols,value):
    out=0
    while value:
        bit=(value&-value).bit_length()-1;out^=cols[bit];value^=1<<bit
    return out


def mul(a,b):return tuple(apply(a,x) for x in b)
def ident(n):return tuple(1<<i for i in range(2*n))
def phi(a):
    n=len(a)//2
    return rank(x&((1<<n)-1) for x in a[n:])
def defect(a):return rank(x^(1<<i) for i,x in enumerate(a))
def pairing(x,y,n):
    mask=(1<<n)-1
    return (((x&mask)&(y>>n)).bit_count()+((y&mask)&(x>>n)).bit_count())&1

def symplectic(a):
    n=len(a)//2
    need(all(pairing(x,y,n)==(int(i%n==j%n and i//n!=j//n)) for i,x in enumerate(a) for j,y in enumerate(a)),'symplectic matrix')

def inverse(a):
    d=len(a);rows=[sum(((a[j]>>i)&1)<<j for j in range(d))|(1<<(d+i)) for i in range(d)]
    for j in range(d):
        k=next((i for i in range(j,d) if rows[i]>>j&1),None);need(k is not None,'invertible matrix')
        rows[j],rows[k]=rows[k],rows[j]
        for i in range(d):
            if i!=j and rows[i]>>j&1:rows[i]^=rows[j]
    return tuple(sum(((rows[i]>>(d+j))&1)<<i for i in range(d)) for j in range(d))

def upper(n,columns):return tuple([1<<i for i in range(n)]+[(1<<(n+i))|columns[i] for i in range(n)])
def rotation(n,q):return upper(n,[q if q>>i&1 else 0 for i in range(n)])
def full(n):return upper(n,[1<<i for i in range(n)])
def hadamard(n,axis):
    a=list(ident(n));a[axis],a[n+axis]=a[n+axis],a[axis];return tuple(a)

def binding():
    for row in read_json(P/'SOURCES.json')['files']:
        if row['usage']=='input':need(hashlib.sha256((ROOT/row['path']).read_bytes()).hexdigest()==row['sha256'],'source hash: '+row['path'])

def physical_labels():
    roots=[]
    for i,j in itertools.combinations(range(8),2):
        for s in (-1,1):
            v=[0]*8;v[i]=2;v[j]=2*s;roots.append(tuple(v))
    for signs in itertools.product((-1,1),repeat=7):
        if signs.count(-1)%2==0:roots.append((1,*signs))
    roots.sort();dot=lambda x,y:sum(a*b for a,b in zip(x,y))//4
    gram=[sum(((dot(x,y)+1)&1)<<j for j,y in enumerate(roots)) for x in roots]
    selected=[];rows=[]
    for i,row in enumerate(gram):
        if rank(rows+[row])>len(rows):selected.append(i);rows.append(row)
    need(len(selected)==9,'root pairing dimension')
    compressed=[sum(((row>>j)&1)<<k for k,j in enumerate(selected)) for row in gram]
    g=[compressed[i] for i in selected]
    # inverse() accepts a square column matrix, regardless of even dimension.
    invg=inverse(tuple(g))
    bil=lambda x,y:(x&apply(invg,y)).bit_count()&1
    def extend(vs):
        if len(vs)==9:return vs
        choices=[v for v in range(1,512) if bil(v,v) and all(not bil(v,u) for u in vs)]
        for v in choices:
            if len(vs)<8 and not any(not bil(v,u) for u in choices):continue
            out=extend(vs+[v])
            if out is not None:return out
        return None
    orth=extend([]);need(orth is not None,'physical isometry')
    transform=lambda x:sum(bil(x,v)<<i for i,v in enumerate(orth))
    physical=[transform(x) for x in compressed]
    need(all(((physical[i]&physical[j]).bit_count()&1)==((gram[i]>>j)&1) for i in range(120) for j in range(120)),'14400 physical pairings')
    fixture=read_json(ROOT/'research/p104-native-channel/inputs/P104-FIXTURE.json')['section4_explicit_P104']
    removed={tuple(x) for x in fixture['F0']+fixture['C']}
    ports=[q for root,q in zip(roots,physical) if root not in removed]
    need(len(ports)==104 and ports[0]==386,'P104 physical ports')
    return ports,transform


def canonical(values):
    p={}
    for v in values:
        while v:
            j=v.bit_length()-1
            if j in p:v^=p[j]
            else:p[j]=v;break
    for j in sorted(p):
        for k in p:
            if k>j and p[k]>>j&1:p[k]^=p[j]
    return tuple(p[j] for j in sorted(p,reverse=True))


def verify():
    binding();ports,transform=physical_labels();n=9;F=full(n);I=ident(n)
    intrinsic=[]
    for q in ports:
        need(q.bit_count()%2==1,'odd physical source')
        C=rotation(n,q);K=mul(F,inverse(C));symplectic(K)
        need(phi(C)==1 and phi(F)==9 and phi(K)==defect(K)==8,'intrinsic width8')
        intrinsic.append({'q':q,'source_progress':phi(F)-phi(C),'target_progress':phi(K),'cocycle_defect':defect(K)})
    need(2*sum(x['cocycle_defect'] for x in intrinsic)+72*defect(F)==2312,'intrinsic bound2312')
    # Bind the actual canonical frame convention without importing its generator.
    path=ROOT/'research/p104-native-channel/vendor/clifford_exact.py'
    spec=importlib.util.spec_from_file_location('p104_progress_native',path);ce=importlib.util.module_from_spec(spec);sys.modules[spec.name]=ce;spec.loader.exec_module(ce)
    tocols=lambda op:tuple(x|(z<<9) for x,z,_ in op.tab)
    word=read_json(ROOT/'research/p104-native-channel/inputs/LOWRANK-WITNESS.json')
    frame=lambda f:canonical(transform(x) for x in f)
    cache={}
    def chart(f):
        f=tuple(f)
        if f not in cache:cache[f]=tocols(ce.canonical_frame(9,f));symplectic(cache[f])
        return cache[f]
    endpoint_counts={};canonical_pairs={}
    for name in word['initial_frames']:
        gi=chart(frame(word['initial_frames'][name]));go=chart(frame(word['final_frames'][name]));k=mul(go,inverse(gi))
        key=f'{name[0]}:B{phi(k)}:defect{defect(k)}';endpoint_counts[key]=endpoint_counts.get(key,0)+1
        canonical_pairs[name]=(gi,go)
    need(endpoint_counts=={'X:B8:defect10':102,'X:B8:defect8':2,'Y:B8:defect8':104,'Q:B9:defect9':8,'G:B9:defect9':32,'D:B9:defect9':32},'canonical endpoint census')
    G=canonical_pairs['X0'][0];H=hadamard(9,1);K=mul(F,inverse(G));translated=mul(mul(H,K),H)
    adapter=mul(G,inverse(rotation(n,386)));adapt_trans=mul(mul(H,adapter),H)
    intrinsic_trans=mul(mul(H,mul(F,inverse(rotation(n,386)))),H)
    need((phi(K),defect(K),phi(translated),phi(adapter),phi(adapt_trans),phi(intrinsic_trans))==(8,10,9,0,2,8),'actual adapter-placement counterexample')
    # This whole canonical-word control is a changed schedule, not an admitted supplier.
    R=mul(inverse(G),H);actual_progress=0
    for gi,go in canonical_pairs.values():actual_progress+=phi(mul(mul(H,go),R))-phi(mul(mul(H,gi),R))
    histogram={};original_mass=0
    for e in word['program']:
        if e[0]=='transport':
            rel=mul(chart(frame(e[3])),inverse(chart(frame(e[2]))));need(phi(rel)==e[4],'original native width binding');original_mass+=phi(rel);p=phi(mul(mul(H,rel),H));histogram[p]=histogram.get(p,0)+1
    mass=sum(k*v for k,v in histogram.items())
    need(actual_progress==2066 and mass==2248 and original_mass==2368,'changed canonical control bill')
    # An alternating nondegenerate plane in ordinary F2^3: neither basis vector is odd.
    v,w=3,6
    proj=[(v if (w>>i)&1 else 0)^(w if (v>>i)&1 else 0) for i in range(3)]
    alt=upper(3,proj);symplectic(alt)
    need(rank(proj)==phi(alt)==defect(alt)==2,'alternating residual width')
    return {'schema_version':1,'claim':'matched intrinsic role-local Clifford translations preserve the2312 progress upper bound',
            'intrinsic_ports':intrinsic,'intrinsic_total_bound':2312,'changed_full_Y_endpoint_bound':104*8+104*9+72*9,'canonical_endpoint_census':endpoint_counts,
            'counterexample':{'register':'X0','q':386,'H_axis':1,'canonical_B_rank':8,'canonical_defect':10,'translated_B_rank':9,'entry_adapter_B_rank':0,'translated_entry_adapter_B_rank':2,'intrinsic_translated_B_rank':8,'canonical_source_columns':list(G),'relative_columns':list(K),'translated_relative_columns':list(translated)},
            'whole_canonical_control':{'progress':actual_progress,'native_mass':mass,'native_excess':mass-actual_progress,'histogram':{str(k):v for k,v in sorted(histogram.items())},'scope':'conjugated transports only; intrinsic endpoint adapters and side correction must be separately repriced'},
            'alternating_plane':{'ambient_dimension':3,'basis':[v,w],'projector_columns':proj,'rank':2},'selected_frontier_changed':False}


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--write-result',action='store_true');args=ap.parse_args();out=verify()
    if args.write_result:(P/'RESULT.json').write_text(json.dumps(out,indent=2)+'\n')
    else:need(json.dumps(out,sort_keys=True,separators=(',',':'))==json.dumps(read_json(P/'RESULT.json'),sort_keys=True,separators=(',',':')),'typed result equality')
    print('PASS_P104_TRANSLATED_PROGRESS: intrinsic2312; adapter-sensitive canonical counterexample')
if __name__=='__main__':main()
