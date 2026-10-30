"""Dense direct implementation; imports no primary or predecessor checker."""
from hashlib import sha256
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def need(ok, message):
    if not ok:raise ValueError(message)


def rank(a, p):
    a = [[x%p for x in row] for row in a]
    r = 0
    for j in range(len(a[0]) if a else 0):
        pivot = next((i for i in range(r,len(a)) if a[i][j]),None)
        if pivot is None:continue
        a[r],a[pivot] = a[pivot],a[r]
        inv = pow(a[r][j],-1,p)
        a[r] = [x*inv%p for x in a[r]]
        for i in range(r+1,len(a)):
            factor=a[i][j]
            a[i]=[(x-factor*y)%p for x,y in zip(a[i],a[r])]
        r+=1
    return r


def run():
    meta=json.loads((HERE/'SOURCES.json').read_text())
    row=next(r for r in meta['files'] if r['usage']=='input')
    raw=(ROOT/row['path']).read_bytes()
    need(sha256(raw).hexdigest()==row['sha256'],'independent source hash')
    obj=json.loads(raw)
    q={r['port']:[(r['q']>>i)&1 for i in range(9)] for r in obj['recipes']}
    cert=json.loads((HERE/'CERTIFICATE.json').read_text());groups=cert['orthonormal_groups']
    need(sorted(x for g in groups for x in g)==list(range(112)),'independent partition')
    pairs=[];factors=[];tariffs=[]
    for group in groups:
        local_pairs=[group[i:i+2] for i in range(0,len(group),2)]
        pairs+=local_pairs
        for parity in range(2):
            factor=[0]*112
            for pair in local_pairs:factor[pair[parity]]=1
            factors.append(factor)
            gram=[[sum(a*b for a,b in zip(q[i],q[j]))%2 for j in group] for i in group]
            need(gram==[[int(i==j) for j in range(len(group))] for i in range(len(group))],
                 'independent full-plane Gram identity')
            tariffs.append(rank(gram,2))
    a=[[sum(v[i]*v[j] for v in factors) for j in range(112)] for i in range(112)]
    plane={p:i for i,pair in enumerate(pairs) for p in pair}
    # Enumerate all four vectors, including zero, in every physical plane.
    spaces=[[[u*x^v*y for x,y in zip(q[i],q[j])] for u in (0,1) for v in (0,1)] for i,j in pairs]
    orth=[[all(sum(x*y for x,y in zip(u,v))%2==0 for u in s for v in t)
           for t in spaces] for s in spaces]
    forced=0
    for i in range(112):
        for j in range(112):
            if i==j or not orth[plane[i]][plane[j]]:
                need(a[i][j]==int(i==j),'independent complete ordered fitting mask');forced+=1
    minor=[p for i in cert['clique_planes'] for p in pairs[i]]
    need(len(minor)==len(set(minor))==32,'independent minor size')
    need(all(not orth[plane[i]][plane[j]] for i in minor for j in minor),
         'independent forced I32')
    ranks={str(p):rank(a,p) for p in (2,3,1000003)}
    need(set(ranks.values())=={32},'independent dense ranks')
    # Literal algebraic sum/add/uncompute on every source and dirty-target column.
    # This is an ordinary field program, not an emitted native copy word.
    supports=[[i for i,x in enumerate(v) if x] for v in factors]
    for column in range(224):
        x=[int(column==i) for i in range(112)]
        y=[int(column==112+i) for i in range(112)]
        original_x=x[:];original_y=y[:]
        for support in supports:
            temporary=0
            for i in support:temporary+=x[i]
            for i in support:y[i]+=temporary
            for i in support:temporary-=x[i]
            need(temporary==0,'literal query cleanup')
        expected=[original_y[i]+sum(a[i][j]*original_x[j] for j in range(112)) for i in range(112)]
        need(x==original_x and y==expected,'complete source/dirty-target field program')
    return dict(dense_ranks=ranks,forced_entries=forced,vector_pair_geometry_tests=56*56*16,
                full_port_copy_rank=sum(tariffs),source_columns=112,dirty_target_columns=112,
                matrix_sha256=sha256(bytes(x for row in a for x in row)).hexdigest())
