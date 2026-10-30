# SPDX-License-Identifier: Apache-2.0
"""Independent characteristic-polynomial, label and literal group-ring checks."""
from itertools import product,permutations
from pathlib import Path
from collections import Counter
import json,gzip,hashlib,random,argparse
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]


def need(x,s):
    if not x:raise ValueError(s)


def lin(a,x):
    y=0
    while x:
        t=x&-x;y^=a[t.bit_length()-1];x^=t
    return y


def rank(a):
    piv={}
    for v in a:
        while v:
            k=v.bit_length()-1
            if k not in piv:piv[k]=v;break
            v^=piv[k]
    return len(piv)


def zpower(a):
    b=a
    for _ in range(len(a)-1):b=tuple(lin(a,x) for x in b)
    return len(a)-rank(b)


def pmul(a,b):
    x=0
    while b:
        if b&1:x^=a
        a<<=1;b>>=1
    return x


def characteristic(a):
    n=len(a);poly=0
    for p in permutations(range(n)):
        term=1
        for r,c in enumerate(p):term=pmul(term,((a[c]>>r)&1)^(2 if r==c else 0))
        poly^=term
    need(poly>>n==1,'monic characteristic')
    return poly


def zchar(a):
    p=characteristic(a);return (p&-p).bit_length()-1


def memberships(supports):
    fields=sorted(set().union(*map(set,supports)))
    return {a:tuple(i for i,s in enumerate(supports) if a in s) for a in fields}


def labels(supports,order):
    history={a:0 for a in memberships(supports)};out={}
    for i in order:
        out[i]=history.copy()
        for a in supports[i]:history[a]^=1<<i
    return out


def check_blocks(supports,order):
    owner=memberships(supports);history=labels(supports,order);position={i:k for k,i in enumerate(order)}
    pairs=0
    for i,fields in enumerate(supports):
        def block(a):
            others=[j for j in owner[a] if j!=i]
            if not others:return (2,a)
            j=others[0]
            return (0,position[j]) if position[j]>position[i] else (1,position[j])
        for a,b in product(fields,repeat=2):
            if a==b:continue
            contributions=owner[b]
            possible=len(contributions)==2 and len({history[j][a]^history[j][b] for j in contributions})==1
            if possible:need(block(a)>=block(b),'lower block ordering from exact labels')
            if len(owner[b])==1:need(not possible,'private offdiagonal forbidden')
            pairs+=1
    return pairs


def gmul(a,b):
    out=set()
    for m,p in a:
        for n,q in b:
            if p+q>1:continue
            x=(m^n,p+q)
            if x in out:out.remove(x)
            else:out.add(x)
    return out


def matrix_product(a,b):
    n=len(a);out=[[set() for _ in range(n)] for _ in range(n)]
    for i,j,k in product(range(n),repeat=3):out[i][j]^=gmul(a[i][k],b[k][j])
    return out


def exact_word(supports,matrices,flags,order):
    n=len(flags);out=[[{(0,0)} if i==j else set() for j in range(n)] for i in range(n)]
    for call in order:
        s=set(supports[call]);R=matrices[call]
        stage=[[set() for _ in range(n)] for _ in range(n)]
        for r,c in product(range(n),repeat=2):
            mask=(1<<call) if r in s else 0
            if r==c:stage[r][c].add((mask,0))
            if R[c]>>r&1:stage[r][c].add((mask,1))
        out=matrix_product(stage,out)
    for a,b in product(range(n),repeat=2):
        mask=sum(1<<i for i,s in enumerate(supports) if a in s)
        expected={(mask,0)}|({(mask,1)} if flags[a] else set()) if a==b else set()
        need(out[a][b]==expected,'literal complete group-ring endpoint')


def native_chains(supports,matrices):
    chains=[]
    for support,a in zip(supports,matrices):
        vectors=[sum(((x>>i)&1)<<v for i,v in enumerate(support)) for x in range(1<<4)]
        pair=next(((u,w) for u,w in product(vectors,vectors) if u and lin(a,u)==0 and lin(a,w)==u),None)
        need(pair is not None,'actual native Jordan chain')
        chains.append(pair)
    return chains


def authenticate():
    data={}
    for r in json.loads((HERE/'SOURCES.json').read_text())['files']:
        if r['usage']=='input':
            b=(ROOT/r['path']).read_bytes();need(hashlib.sha256(b).hexdigest()==r['sha256'],'source SHA256')
            data[r['path']]=b
    return data


def typed_match(expected, observed):
    need(json.dumps(expected,sort_keys=True,separators=(",",":"))==json.dumps(observed,sort_keys=True,separators=(",",":")),'typed exact receipt')


def main(emit=False):
    data=authenticate();local=exception=0
    for n in (1,2,3):
        for a in product(range(1<<n),repeat=n):
            za=zpower(a);need(za==zchar(a),'independent zero multiplicities')
            for mask in range(1<<n):
                b=tuple(v^((1<<j) if mask>>j&1 else 0) for j,v in enumerate(a))
                zb=zpower(b);need(zb==zchar(b),'independent shifted multiplicities')
                k=mask.bit_count();ex=n==3 and k==2 and za+zb>4
                if ex:need(za==zb==3,'only exceptional nilpotent triple');exception+=1
                else:need(za+zb<=2*n-k,'local mixed-flag spectral bound')
                local+=1
    need(zpower((2,7,5))==zpower((3,5,5))==3,'genuine mixed exception')
    graphs=[[[0,1,4,5],[0,1,2,3],[2,3,6,7]], [[0,1,4,5],[0,1,2,3],[2,3,4,5]], [[0,1,2,3],[0,1,2,3]]]
    rng=random.Random(5501)
    for _ in range(100):
        c=rng.randrange(2,7);support=[[] for _ in range(c)];field=0
        pairs=list((i,j) for i in range(c) for j in range(i+1,c));rng.shuffle(pairs)
        for i,j in pairs:
            for _ in range(rng.randrange(min(4-len(support[i]),4-len(support[j]))+1)):
                support[i].append(field);support[j].append(field);field+=1
        for s in support:
            while len(s)<4:s.append(field);field+=1
        graphs.append(support)
    blockpairs=orders=0
    for support in graphs:
        samples=list(permutations(range(len(support)))) if len(support)<=3 else [tuple(rng.sample(range(len(support)),len(support))) for _ in range(8)]
        for order in samples:blockpairs+=check_blocks(support,order);orders+=1
    # Constructed complement pair: independent from predecessor's saved matrix.
    support=[[0,1,2,3]]*2
    A=(0,1,4,12);B=tuple(v^(1<<j) for j,v in enumerate(A))
    native_chains(support,[A,B]);exact_word(support,[A,B],[1]*4,[0,1])
    # Mixed triple with private Q targets: exception compensation is attained.
    support2=[[0,1,2,3],[0,1,2,4]]
    A3=(2,7,5);B3=(3,5,5)
    mats=[tuple(A3)+(8,0),tuple(B3)+(0,16)]
    native_chains(support2,mats)
    for order in ((0,1),(1,0)):exact_word(support2,mats,[1,1,0,1,1],order)
    word=json.loads(gzip.decompress(data['research/kappa-rebuild/bit/sources/pr589-regenerated/WORD.json.gz']))
    departures={};port={}
    for section in ('D','A','B','C'):
        for frame,d,ss in word[section]:
            for r in [d]+ss:
                if r>=2*word['v'] and r not in departures and frame!=0:
                    departures[r]=frame
                    if len(word['frames'][frame])==1:port.setdefault(word['frames'][frame][0],[]).append(r)
            need(d<2*word['v'] or d in departures,'no helper write before first departure')
    selected=[r for group in port.values() for r in group[:2]]
    need(len(departures)==439 and len(port)==111 and min(map(len,port.values()))>=2,'actual first-departure coverage')
    need(len(selected)==len(set(selected))==222,'distinct original helper owners across ports')
    receipt=json.loads(data['research/kappa-rebuild/bit/PR589-STATE-SHARING-PROBE.json'])['baseline']
    paid={int(k):v for k,v in receipt['paid'].items()};need(word['v']==111 and word['R']==439,'actual source inventory')
    need(receipt['dirty_helpers']==word['R'] and receipt['owned_COPY_episodes']==9,'all helper/owned costs retained')
    paidrank=sum(k*v for k,v in paid.items());untouched=word['R']-2*word['v']
    need(paidrank==5129 and untouched==217,'complete native invoice')
    targets=untouched*8+111*(28+2);need(targets-paidrank==-63,'uniform signed deficit')
    controls=0
    for check in (lambda:need(3+3<=2*3-2,'false uncorrected local bound'),
                  lambda:need(111*8-285*3<=0,'unfunded path wrong classification'),
                  lambda:exact_word(support,[A,B],[1,1,0,1],[0,1]),
                  lambda:native_chains([[0,1,2,3]],[(1,2,4,8)])):
        try:check()
        except ValueError:controls+=1
        else:raise ValueError('control failed to reject')
    result={'status':'PASS_MULTIGRAPH_FUNDING_OBSTRUCTION','local_spectral_cases':local,'exceptional_cases':exception,'graph_fixtures':len(graphs),'chronologies':orders,'restricted_entry_checks':blockpairs,'literal_positive_words':3,'paid_rank_per_FULL':paidrank,'untouched_helpers_per_FULL':untouched,'distinct_selected_helper_owners':len(selected),'rank_deficit_per_FULL':63,'rejecting_controls':controls,'solver_run':False,'all_flags_covered':True,'new_kappa':False}
    forged=dict(result);forged['new_kappa']=0
    try:typed_match(result,forged)
    except ValueError:pass
    else:raise ValueError('bool/integer receipt control escaped')
    if not emit:
        need((HERE/'RESULT.json').is_file(),'required receipt missing')
        typed_match(result,json.loads((HERE/'RESULT.json').read_text()))
    print(json.dumps(result,sort_keys=True,indent=2))

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--emit',action='store_true');args=parser.parse_args();main(args.emit)
