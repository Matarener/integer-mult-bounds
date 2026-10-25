"""Exact independent finite corroboration of RANK57-GAUGE.md; no external imports."""
from collections import Counter
from fractions import Fraction as F
from hashlib import sha256
from pathlib import Path
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]

def require(ok, message):
    if not ok:
        raise ValueError(message)

def eye(n):
    return [[F(i==j) for j in range(n)] for i in range(n)]

def mm(a,b):
    return [[sum((x*y for x,y in zip(row,col)),F(0)) for col in zip(*b)] for row in a]

def transpose(a):
    return [list(x) for x in zip(*a)]

def inv(a):
    n=len(a); rows=[list(row)+ident for row,ident in zip(a,eye(n))]
    for col in range(n):
        pivot=next((j for j in range(col,n) if rows[j][col]),None)
        require(pivot is not None,'invertible rational matrix')
        rows[col],rows[pivot]=rows[pivot],rows[col]
        v=rows[col][col]; rows[col]=[x/v for x in rows[col]]
        for j in range(n):
            if j!=col and rows[j][col]:
                v=rows[j][col]; rows[j]=[x-v*y for x,y in zip(rows[j],rows[col])]
    return [row[n:] for row in rows]

def dense(seed):
    l=[[F(1),F(0),F(0)],[F(seed+1,2),F(1),F(0)],
       [F(seed+2,3),F(seed+3,2),F(1)]]
    d=[[F(2,3),F(0),F(0)],[F(0),F(seed+2,5),F(0)],
       [F(0),F(0),F(seed+3,7)]]
    u=[[F(1),F(seed+1,3),F(seed+2,2)],
       [F(0),F(1),F(seed+3,5)],[F(0),F(0),F(1)]]
    return mm(mm(l,d),u)

def rank2(rows):
    basis={}
    for x in rows:
        while x:
            p=x.bit_length()-1
            if p not in basis:
                basis[p]=x; break
            x^=basis[p]
    return len(basis)

def charge(u,v,groups,labels):
    left=[p for g in groups if any(u[p] for p in g) for p in g]
    right=[p for g in groups if any(v[p] for p in g) for p in g]
    return rank2(sum(((labels[p]&labels[q]).bit_count()%2)<<j
                     for j,q in enumerate(right)) for p in left)

def apply(blocks, groups, vector):
    out=[F(0)]*112
    for block,g in zip(blocks,groups):
        for i,p in enumerate(g):
            out[p]=sum((block[i][j]*vector[q] for j,q in enumerate(g)),F(0))
    return out

def supports(vector,groups):
    return [i for i,g in enumerate(groups) if any(vector[p] for p in g)]

def kernel_basis(b,a,axis):
    pivot=next(i for i,x in enumerate(b) if x)
    columns=[]
    for j in range(3):
        if j!=pivot:
            col=[F(k==j) for k in range(3)]; col[pivot]-=b[j]/b[pivot]
            columns.append(col)
    columns.insert(axis,list(a))
    return transpose(columns)

def label_data():
    source=ROOT/'research/adaptive-kernel-demotion/inputs/DATA-PHASES.json'
    candidate=ROOT/'research/p112-rational-decoder-gate/CANDIDATE.json'
    require(sha256(source.read_bytes()).hexdigest()=='c5916ff312678f12aba403847643fbbc29f643acec60bdf836fa56cd3e8251fa','label pin')
    require(sha256(candidate.read_bytes()).hexdigest()=='dc5fbe51f9cd3a14361256ac136736bffb18971d0247b891accf0d2ee060d06b','candidate pin')
    data=json.loads(candidate.read_bytes())
    labels=[r['q'] for r in sorted(json.loads(source.read_bytes())['recipes'],key=lambda r:r['port'])]
    return labels,data

def geometry(labels,data):
    groups=data['groups']; odd=list(range(1,38,2)); rem=[0]+list(range(2,37,2))
    orth=[[all((labels[p]&labels[q]).bit_count()%2==0 for p in g for q in h)
           for h in groups] for g in groups]
    require(all(not orth[i][j] for i in odd for j in odd),'forced I57')
    neighbors={i:[j for j in odd if orth[i][j]] for i in rem}
    for i in range(2,37,2):
        require(neighbors[i]==([3,23] if i==24 else [i-1]),'exact even odd-neighbors')
    require(neighbors[0]==[15,27],'residual odd-neighbors')
    require(not orth[4][24] and not orth[0][28],'forbidden cross-blocks')
    require(orth[0][15] and orth[0][16],'residual canonical legal')
    require(data['factor_supports'][21]==[9,39,55],'literal residual convention')
    return orth,neighbors

def canonical(groups,axis):
    rows=[[F(0)]*57 for _ in range(112)]
    for i in range(18):
        for g in (2*i+1,2*i+2):
            for j,p in enumerate(groups[g]):rows[p][3*i+j]=F(1)
    for j,p in enumerate(groups[37]):rows[p][54+j]=F(1)
    rows[groups[0][0]][21+axis]=F(1)
    return rows

def product_rows(left,right):
    sparse=[[(k,x) for k,x in enumerate(row) if x] for row in left]
    return [[sum((x*row[k] for k,x in items),F(0)) for row in right] for items in sparse]

def fixture(axis,labels,groups,orth):
    aa=[dense(i+2+axis) for i in range(18)]; bb=[inv(a) for a in aa]
    precursor=dense(31+axis); precinv=inv(precursor)
    a=[row[axis] for row in precursor]; b=precinv[axis]
    require(sum(x*y for x,y in zip(a,b))==1,'ba=1')
    left=[[F(0)]*57 for _ in range(112)]; right=[[F(0)]*57 for _ in range(112)]
    for i in range(18):
        for j,p in enumerate(groups[2*i+1]):left[p][3*i+j]=right[p][3*i+j]=F(1)
        for j,p in enumerate(groups[2*i+2]):
            left[p][3*i:3*i+3]=bb[i][j]
            right[p][3*i:3*i+3]=transpose(aa[i])[j]
    for j,p in enumerate(groups[37]):left[p][54+j]=right[p][54+j]=F(1)
    left[groups[0][0]][21:24]=b; right[groups[0][0]][21:24]=a
    raw=product_rows(left,right)
    owner={p:g for g,ports in enumerate(groups) for p in ports}
    for p in range(112):
        for q in range(112):
            if p==q or not orth[owner[p]][owner[q]]:
                require(raw[p][q]==F(p==q),'raw strict mask')
    t=kernel_basis(b,a,axis); pmat=inv(t)
    blocks=[eye(len(g)) for g in groups]
    for i in range(18):blocks[2*i+2]=aa[i]
    blocks[15]=pmat; blocks[16]=mm(pmat,aa[7])
    transformed_left=transpose([apply(blocks,groups,col) for col in transpose(left)])
    invt=[transpose(inv(block)) for block in blocks]
    transformed_right=transpose([apply(invt,groups,col) for col in transpose(right)])
    rr=canonical(groups,axis); target=product_rows(rr,rr)
    transformed=product_rows(transformed_left,transformed_right)
    require(transformed==target,'all12544 conjugacy entries')
    wrong_right=transpose([apply(blocks,groups,col) for col in transpose(right)])
    require(product_rows(transformed_left,wrong_right)!=target,
            'control: congruence must not replace conjugacy')
    wrong_axis=canonical(groups,1-axis)
    require(transformed!=product_rows(wrong_axis,wrong_axis),
            'control: unswapped residual axis mismatch')
    # The original latent basis need not itself be the gauge-adapted canonical basis.
    # Pull back R's columns to get that distinguished basis, then add cancellations.
    inverse_blocks=[inv(block) for block in blocks]
    transpose_blocks=[transpose(block) for block in blocks]
    us=[apply(inverse_blocks,groups,col) for col in transpose(rr)]
    vs=[apply(transpose_blocks,groups,col) for col in transpose(rr)]
    exterior_u=[F((7*k)%13-6,3) for k in range(112)]
    exterior_v=[F((5*k)%11-5,2) for k in range(112)]
    us.extend([exterior_u,exterior_u]); vs.extend([exterior_v,[-x for x in exterior_v]])
    newu=[apply(blocks,groups,col) for col in us]
    newv=[apply(invt,groups,col) for col in vs]
    oldcost=[]; newcost=[]
    for u,v,uu,vv in zip(us,vs,newu,newv):
        require(supports(u,groups)==supports(uu,groups),'source group support')
        require(supports(v,groups)==supports(vv,groups),'reader group support')
        oldcost.append(charge(u,v,groups,labels));newcost.append(charge(uu,vv,groups,labels))
    require(oldcost==newcost,'every actual tariff invariant')
    require(sum(oldcost[:57])==334,'baseline334')
    require(product_rows(transpose(us),transpose(vs))==raw,'all12544 exterior operator entries')
    require(product_rows(transpose(newu),transpose(newv))==target,'all12544 transformed exterior entries')
    return {'axis':axis,'terms':len(us),'operator_entries_checked':3*112*112,
            'source_and_reader_support_pairs_checked':len(us),
            'baseline_tariff':sum(oldcost[:57]),'all_term_tariff':sum(oldcost),
            'tariff_histogram':dict(sorted(Counter(oldcost).items())),
            'dense_nonsymmetric_fit':raw!=transpose(raw),
            'controls':['congruence rejected','unswapped residual axis rejected']}

def run():
    labels,data=label_data();groups=data['groups'];orth,neighbors=geometry(labels,data)
    results=[fixture(axis,labels,groups,orth) for axis in (0,1)]
    first=canonical(groups,0);second=canonical(groups,1)
    swap=[eye(len(g)) for g in groups]
    for g in (15,16):swap[g]=[[F(0),F(1),F(0)],[F(1),F(0),F(0)],[F(0),F(0),F(1)]]
    swapped=transpose([apply(swap,groups,col) for col in transpose(first)])
    require(product_rows(swapped,swapped)==product_rows(second,second),'axis swap all12544 entries')
    result={'scope':'Finite corroboration of exact written gauge theorem, no higher rank fit claim',
            'odd_neighbor_geometry':neighbors,'fixtures':results,
            'axis0_residual_support':[9,39,55],'axis1_residual_support':[23,62,55],
            'axis_swap_entries_checked':112*112,'status':'PASS'}
    print(json.dumps(result,indent=2))

if __name__=='__main__':run()
