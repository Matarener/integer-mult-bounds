"""Independent finite audit: no imports from cycle.py, check.py or source.py.

Exact edge-capacity enumeration and complete directed GF(2) fitting matrices.
"""
from collections import Counter
from functools import lru_cache
from hashlib import sha256
from io import BytesIO
from itertools import product
import json
from pathlib import Path
import tarfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def require(ok, message):
    if not ok:raise ValueError(message)


@lru_cache(None)
def maximum_edges(index, capacities):
    if index == 5:return 0
    i,j = index,(index+1)%5
    best = 0
    for copies in range(min(capacities[i],capacities[j])+1):
        remaining=list(capacities)
        remaining[i]-=copies;remaining[j]-=copies
        best=max(best,copies+maximum_edges(index+1,tuple(remaining)))
    return best


def bit_rank(rows):
    basis={}
    for row in rows:
        while row:
            lead=row.bit_length()-1
            if lead not in basis:
                basis[lead]=row;break
            row^=basis[lead]
    return len(basis)


def full_completions(sizes):
    owner=[v for v,size in enumerate(sizes) for _ in range(size)]
    n=len(owner)
    free=[(i,j) for i in range(n) for j in range(n) if (owner[i]-owner[j])%5 in (1,4)]
    rows=[1<<i for i in range(n)]
    histogram=Counter({bit_rank(rows):1})
    previous=0
    # Reflected Gray enumeration changes one genuinely free matrix entry.
    for number in range(1,1<<len(free)):
        gray=number^(number>>1)
        delta=gray^previous;bit=delta.bit_length()-1
        i,j=free[bit];rows[i]^=1<<j
        histogram[bit_rank(rows)]+=1;previous=gray
    expected=max([sum(sizes)//2+sum(sizes)%2]+[sizes[i]+sizes[(i+2)%5] for i in range(5)])
    require(min(histogram)==expected,'minimum over all directed binary completions')
    return dict(sizes=list(sizes),free_bits=len(free),matrices=1<<len(free),
                minimum=min(histogram),histogram={str(k):v for k,v in sorted(histogram.items())})


def source_check():
    raw={}
    for row in json.loads((HERE/'SOURCES.json').read_text())['files']:
        if row['usage']=='input':
            data=(ROOT/row['path']).read_bytes()
            require(sha256(data).hexdigest()==row['sha256'],'independent input hash')
            raw[row['path']]=data
    with tarfile.open(fileobj=BytesIO(raw['research/community-frontier1094-audit/selected-replay.tar.gz'])) as archive:
        obj=json.load(archive.extractfile('candidate/strict/global/base/work/complex-nine-native/DATA-PHASES.json'))
    lookup={row['port']:[(row['q']>>bit)&1 for bit in range(9)] for row in obj['recipes']}
    pairs=json.loads(raw['research/paired-plane-scalar-mask-obstruction/PR1825-CERTIFICATE.json'])['matching']
    cert=json.loads(raw['research/paired-plane-minrank-bracket-audit/CERTIFICATE.json'])
    # Enumerate every vector of each plane, not just the four basis products.
    planes=[]
    for i,j in pairs:
        a,b=lookup[i],lookup[j]
        planes.append([[x*u^y*v for u,v in zip(a,b)] for x,y in product((0,1),repeat=2)])
    orthogonal=lambda i,j:all(sum(x*y for x,y in zip(a,b))%2==0 for a in planes[i] for b in planes[j])
    core,clique=cert['c5_core'],cert['clique22']
    require(all(orthogonal(i,j)==((a-b)%5 in (1,4)) for a,i in enumerate(core) for b,j in enumerate(core)),
            'independent actual cycle geometry')
    require(all(not orthogonal(i,j) for i in clique for j in clique+core),
            'independent actual separated geometry')
    return dict(planes=len(planes),core=core,clique=len(clique),core_vector_pair_tests=25*16,
                separated_vector_pair_tests=22*27*16)


def run():
    digest=sha256()
    for sizes in product(range(4),repeat=5):
        rank=sum(sizes)-maximum_edges(0,sizes)
        closed=max([sum(sizes)//2+sum(sizes)%2]+[sizes[i]+sizes[(i+2)%5] for i in range(5)])
        require(rank==closed,'independent capacity optimization')
        digest.update(bytes(sizes)+bytes([rank]))
    cases=[full_completions(sizes) for sizes in product((0,1),repeat=5)]
    cases.append(full_completions((2,1,1,1,1)))
    return dict(edge_capacity_cases=4**5,edge_capacity_sha256=digest.hexdigest(),
                binary_completion_cases=cases,total_binary_matrices=sum(x['matrices'] for x in cases),
                source=source_check())
