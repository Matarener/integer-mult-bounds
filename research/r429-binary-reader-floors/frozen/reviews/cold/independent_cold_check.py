#!/usr/bin/env python3
"""Independent finite checks for B08, excluding the separately replayed 2.5m census.

Standard library only. Substantial OpenAI Codex assistance; Apache-2.0.
"""
from collections import Counter
from fractions import Fraction
from hashlib import sha256
from itertools import combinations, combinations_with_replacement
from pathlib import Path
import gzip
import json

ROOT = Path('/Users/ross/git/math')
OLD = ROOT/'.research-automation/runs/kappa-changed-endpoints-20261019T0153Z'
HERE = Path(__file__).resolve().parent

def need(ok, message):
    if not ok:
        raise ValueError(message)

def dot(a,b):
    return sum(x*y for x,y in zip(a,b))

def bits(n):
    return [i for i in range(n.bit_length()) if n>>i&1]

def xor(values):
    out=0
    for v in values:
        out ^= v
    return out

def rank(rows, prime=None):
    a=[list(row) if prime else list(map(Fraction,row)) for row in rows]
    if not a:
        return 0
    h=0
    for j in range(len(a[0])):
        if prime:
            for i in range(h,len(a)):
                a[i][j] %= prime
        p=next((i for i in range(h,len(a)) if a[i][j]),None)
        if p is None:
            continue
        a[h],a[p]=a[p],a[h]
        q=pow(a[h][j],-1,prime) if prime else 1/a[h][j]
        a[h]=[(x*q)%prime if prime else x*q for x in a[h]]
        for i in range(h+1,len(a)):
            q=a[i][j]
            if q:
                a[i]=[(x-q*y)%prime if prime else x-q*y for x,y in zip(a[i],a[h])]
        h+=1
        if h==len(a[0]):
            break
    return h

def inverse(a, binary=False):
    n=len(a)
    a=[[int(x) if binary else Fraction(x) for x in row]+[int(i==j) for j in range(n)] for i,row in enumerate(a)]
    for j in range(n):
        p=next(i for i in range(j,n) if a[i][j])
        a[j],a[p]=a[p],a[j]
        if not binary:
            q=a[j][j]
            a[j]=[x/q for x in a[j]]
        for i in range(n):
            if i!=j and a[i][j]:
                q=a[i][j]
                a[i]=[(x-q*y)%2 if binary else x-q*y for x,y in zip(a[i],a[j])]
    return [row[n:] for row in a]

def brank(rows):
    return rank([[v>>i&1 for i in range(111)] for v in rows],2)

def main():
    paths={
        'source':OLD/'bit-native-caller/READOUT-FLOOR.json',
        'cosets':OLD/'bit-native-caller/COLD-COSETS.json',
        'nine':OLD/'cold-reader/NINE-TERM-FLOOR.json',
        'ten':OLD/'bit-native-caller/TEN-FACTOR-FLOOR56.json',
        'unit':OLD/'bit-native-caller/UNIT-COLD-EXTENSION.json',
        'eleven':OLD/'bit-native-caller/ELEVEN-FACTOR-FLOOR56.json',
        'prior_word':ROOT/'integer-mult-bounds/research/e8-bit-p111/data/bitE8mut-p111.json.gz',
        'other_prior_word':ROOT/'integer-mult-bounds/research/e8-punctured111-star/data/bitE8mut-v111-r489.json.gz',
        'prior_verifier':ROOT/'integer-mult-bounds/research/p111-copy-rank-certificate/verify.py',
    }
    data={k:json.loads(p.read_text()) for k,p in paths.items() if k not in ('prior_word','other_prior_word','prior_verifier')}
    src,cos=data['source'],data['cosets']
    roots=src['root_lines']; full=cos['full_E8_root_lines']; R=src['R']; K=src['K']
    need(roots==cos['live_roots'] and R==cos['R'] and K==cos['K'],'cross-receipt physical data')
    oldword=json.loads(gzip.decompress(paths['prior_word'].read_bytes()))
    otherword=json.loads(gzip.decompress(paths['other_prior_word'].read_bytes()))
    need(roots==oldword['lines'],'exact earlier P111 live root order')
    need(set(map(tuple,roots))!=set(map(tuple,otherword['lines'])),'different PR545/761 fixture')
    deleted=oldword['punctured']; live=[i for i in range(120) if i not in deleted]
    need(roots==[full[i] for i in live],'exact full root order and puncture')
    need(len(set(map(tuple,full)))==120 and all(dot(r,r)==4 for r in full),'120 norm-four lines')
    signed=set(map(tuple,full))|{tuple(-x for x in r) for r in full}
    need(len(signed)==240,'240 signed roots')
    # Establish this is the whole simply-laced root system, not a partial list.
    for a in signed:
        for b in signed:
            need(dot(a,b)%2==0,'integral reflection coefficient')
            need(tuple(x-dot(a,b)//2*y for x,y in zip(a,b)) in signed,'root reflection closure')
    positive={r for r in signed if next(x for x in r if x)>0}
    simple=sorted(r for r in positive if not any(tuple(x-y for x,y in zip(r,s)) in positive for s in positive))
    need(len(simple)==8 and rank(simple)==8,'eight independent simple roots')
    inv=inverse(simple)
    coeff=[[sum(r[i]*inv[i][j] for i in range(8)) for j in range(8)] for r in full]
    need(all(all(x.denominator==1 for x in row) and (all(x>=0 for x in row) or all(x<=0 for x in row)) for row in coeff),'all roots have one-sign integral simple coordinates')
    gram=[[dot(a,b)//2 for b in simple] for a in simple]
    need(all(gram[i][j] in (-1,0) for i in range(8) for j in range(8) if i!=j),'simply-laced Cartan')
    edges=[[i,j] for i in range(8) for j in range(i) if gram[i][j]==-1]
    need(len(edges)==7 and sorted(sum(i in e for e in edges) for i in range(8))==[1,1,1,2,2,2,2,3],'E8 simple tree degrees')
    joint=next(i for i in range(8) if sum(i in e for e in edges)==3)
    arms=[]
    for start in [next(v for v in e if v!=joint) for e in edges if joint in e]:
        prev,cur=joint,start;length=1
        while True:
            nxt=[next(v for v in e if v!=cur) for e in edges if cur in e and prev not in e]
            if not nxt:break
            need(len(nxt)==1,'simple Dynkin arm');prev,cur=cur,nxt[0];length+=1
        arms.append(length)
    need(sorted(arms)==[1,2,4],'E8 Dynkin arm lengths')
    caps=[0]*9; large=[]; non_e7=0; subsets=[]
    for mask in range(256):
        sub=[r for r,c in zip(full,coeff) if all(not x or mask>>j&1 for j,x in enumerate(c))]
        d=mask.bit_count();caps[d]=max(caps[d],len(sub))
        if d==7 and len(sub)!=63:non_e7=max(non_e7,len(sub))
        if d<=6 and len(sub)>21:
            normals=[r for r in full if all(dot(r,simple[j])==0 for j in bits(mask))]
            need(d==6 and len(sub) in (30,36),'only D6/E6 exceed21')
            need(rank(normals)==2 and len(normals)==(2 if len(sub)==30 else 3),'complement A1^2/A2 root plane')
            need(set(map(tuple,sub))=={tuple(r) for r in full if all(dot(r,n)==0 for n in normals)},'exact double orthogonal complement')
            large.append({'subset':mask,'root_lines':len(sub),'complement_lines':len(normals)})
        subsets.append({'subset':mask,'rank':d,'root_lines':len(sub)})
    need(caps==[0,1,3,6,12,20,36,63,120] and non_e7==42,'all parabolic capacities')
    families={'E6':set(),'D6':set()}
    for i,j in combinations(range(120),2):
        v=abs(dot(full[i],full[j])); typ='E6' if v==2 else 'D6' if v==0 else None
        if typ:
            families[typ].add(sum((dot(r,full[i])==dot(r,full[j])==0)<<p for p,r in enumerate(roots)))
    need({k:len(v) for k,v in families.items()}=={'E6':1120,'D6':3780},'complete normal-plane flat counts')
    print('PASS independent parabolic reduction and exact prior root order',flush=True)
    code=[0]
    for r in R:code += [x^r for x in code]
    need(len(set(code))==512 and min(x.bit_count() for x in code[1:])==48,'dimension and distance')
    lookup={d:i for i,d in enumerate(code)}
    M=[xor(R[j] for j in bits(k)) for k in K]
    affine=[sum(((1+dot(q,r)//2)%2)<<j for j,r in enumerate(roots)) for q in roots]
    need(M==affine and brank(M)==9,'R429 equals prior exact affine P111 matrix')
    oldspecial=[sum((dot(q,full[p])==0)<<j for j,q in enumerate(roots)) for p in deleted]
    need(set(oldspecial)==set(R),'same physical nine special label directions as prior')
    rankhist=Counter();special={}
    for label,word in enumerate(code[1:],1):
        rr=rank([roots[p] for p in bits(word)]);rankhist[rr]+=1
        if rr==7:
            ns=[q for q in full if all(dot(q,roots[p])==0 for p in bits(word))]
            need(len(ns)==1,'unique hyperplane root normal');special[label]=ns[0]
    need(rankhist=={7:9,8:502} and set(special)=={1<<j for j in range(9)},'independent exact rational code census')
    normals=[special[1<<j] for j in range(9)]
    Hcols=[lookup[sum((k>>j&1)<<p for p,k in enumerate(K))] for j in range(9)]
    H=[[Hcols[j]>>i&1 for j in range(9)] for i in range(9)]
    dual=inverse(H,True)
    need(all(dual[i][i]==1 for i in range(9)),'same-label binary dual pairing one')
    support_bases=[]
    for r in R:
        b=[]
        for p in bits(r):
            if rank(b+[roots[p]])>len(b):b.append(roots[p])
        need(len(b)==7,'rational hyperplane basis')
        support_bases.append(b)
    pairings=[]
    for i in range(9):
        for j in range(9):
            actual=rank([[dot(a,b) for b in support_bases[j]] for a in support_bases[i]])
            need(actual==(6 if dot(normals[i],normals[j])==0 else 7),'all81 independent rational hyperplane pairings')
            if dual[i][j]:need(actual==(7 if i==j else 6),'dual-matched distinct specials have orthogonal normals')
            pairings.append([i,j,dual[i][j],actual])
    # M = sum_i B_i C_i^T, with B_i equal to the physical special codewords R_i.
    C=[]
    for j in range(9):
        C.append(sum((lookup[row]>>j&1)<<p for p,row in enumerate(M)))
    need([xor(C[j] for j in range(9) if R[j]>>p&1) for p in range(111)]==M,'independent special-basis dual identity')
    projected=[[[4*x-dot(n,q)*y for x,y in zip(q,n)] for q in roots] for n in normals]
    need(all(rank([p[k] for k in bits(c)])==7 for c,p in zip(C,projected)),'attaining nine-term pairing bill63')
    tenhist=Counter()
    for a in range(111):
        costs=[rank([p[k] for k in bits(c^(1<<a))]) for c,p in zip(C,projected)]
        best=min(1+sum(costs[i] if lam>>i&1 else 7 for i in range(9)) for lam in range(512) if lam.bit_count()>=2)
        tenhist[best]+=1
    need(tenhist=={63:1,64:110},'111 exact rational unit projection checks with502 target choices each')
    print('PASS independent rational code and ten-term equality witnesses',flush=True)
    # Use a different small prime from the producer; each rank-seven support
    # also has an exact integral null witness, so no modular upper inference.
    unit_hist=Counter();bases=[]
    for a in range(111):
        for u,d in enumerate(code[1:],1):
            w=d^(1<<a);rr=rank([roots[p] for p in bits(w)],3)
            unit_hist[rr]+=1
            predicted=(u in special and dot(special[u],roots[a])==0) or d==M[a]
            need(rr in (7,8) and (rr==7)==predicted,'independent mod3 unit rank classification')
            if rr==7:
                n=roots[a] if d==M[a] else special[u]
                need(all(dot(n,roots[p])==0 for p in bits(w)),'exact rank-seven upper witness')
        labels=[1<<j for j in range(9)]+[lookup[M[a]]]
        for omitted in range(10):
            U=labels[:omitted]+labels[omitted+1:]
            if brank(U)!=9:continue
            ui=inverse([[u>>j&1 for j in range(9)] for u in U],True)
            V=[sum((sum((K[p]>>j&1)*ui[j][i] for j in range(9))%2)<<p for p in range(111)) for i in range(9)]
            need(len(set(V))==9 and all(v in lookup and v not in R for v in V),'nine generic target duals')
            source=[code[u] for u in U]
            need([xor(source[i] for i in range(9) if V[i]>>p&1) for p in range(111)]==M,'all638 exact dual reconstruction identities')
            bases.append([a,omitted,U,[lookup[v] for v in V]])
    need(len(bases)==638,'complete independent638 bases')
    need(unit_hist==Counter({int(k):v for k,v in data['unit']['combined_toggled_rank_histogram'].items()}),'unit census matches frozen result')
    frozen_bases=[[r['source_unit'],r['omitted_code_label'],r['source_code_basis'],r['all_nine_generic_dual_code_masks']] for r in data['unit']['source_hyperplane_code_bases']]
    need(bases==frozen_bases,'all638 exact basis records agree')
    near=Counter();other=111
    for q in full:
        cap=sum((dot(q,r)==0)<<j for j,r in enumerate(roots))
        a=roots.index(q) if q in roots else None
        expected=cap if a is None else M[a]
        for d in code[1:]:
            outside=d&~cap;w=outside.bit_count()
            if d!=expected:other=min(other,w)
            if w<=3:
                near[w]+=1;need(d==expected and outside==(0 if a is None else 1<<a),'complete near-cap classification')
    need(near=={0:9,1:111} and other==18,'61320 near-cap cases')
    profiles=[p for p in combinations_with_replacement(range(1,7),3) if sum(caps[d] for d in p)>=48]
    need(min(map(sum,profiles))==11,'three-low support-capacity minimum')
    # Every allowed integer rank pair is explicitly listed, including transposes.
    pairs=[[a,b] for a in range(9,12) for b in range(9,12) if a+b-11<=9]
    need(pairs==[[9,9],[9,10],[9,11],[10,9],[10,10],[11,9]],'Sylvester rank cases')
    out={'status':'PASS_INDEPENDENT_B08_COLD_MATHEMATICS','scientific_pin':src['scientific_pin'],
         'sources':{str(p):sha256(p.read_bytes()).hexdigest() for p in paths.values()},
         'PR757_PR555_live_order_identical':True,'PR757_PR555_matrix_identical':True,
         'PR545_PR761_live_root_set_different':True,
         'prior_PR555_punctures':deleted,'other_PR545_punctures':otherword['punctured'],
         'simple_roots':simple,'simple_Cartan':gram,
         'all256_parabolic_line_counts':subsets,'large_rank6_parabolics':large,
         'rank_line_capacities':caps,'non_E7_rank7_maximum':non_e7,
         'normal_plane_flats':{k:len(v) for k,v in families.items()},
         'exact_rational_code_rank_histogram':dict(rankhist),'unit_target_bill_histogram':dict(tenhist),
         'all81_exact_rational_special_pairings':pairings,
         'mod3_plus_exact_normal_unit_rank_histogram':dict(unit_hist),'independently_reconstructed_dual_bases':len(bases),
         'near_cap_small_outside_histogram':dict(near),'other_outside_minimum':other,
         'minimum_three_low_dimension_sum':11,'Sylvester_rank_pairs':pairs,
         'not_repeated':'The2503900 coset outside-flat ranks are delegated to the parent frozen replay; this review checks their finite-domain reduction and arithmetic implementation.',
         'limits':['Finite arithmetic and written proof audit, not a formal-kernel proof.','No native circuit, arbitrary-dirt restoration, outer multiplication or new kappa claim.']}
    (HERE/'RESULT.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    print(out['status'])

if __name__=='__main__':main()
