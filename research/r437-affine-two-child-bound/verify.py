#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Chris R / Clear1nsight, substantial OpenAI Codex assistance.
"""Exact finite controls for a new serial affine two-child flag theorem."""
from fractions import Fraction
from itertools import product
from pathlib import Path
import hashlib,json,gzip,random,math,sys
HERE=Path(__file__).resolve().parent

def need(ok,message):
    if not ok: raise ValueError(message)
def canon(x):return json.dumps(x,sort_keys=True,separators=(',',':')).encode()
def eye(n):return [[int(i==j) for j in range(n)] for i in range(n)]
def lower(n,entries,mod):
    m=eye(n);it=iter(entries)
    for i in range(n):
        for j in range(i):m[i][j]=next(it)%mod
    return m

def permutation(n,k):
    p=list(range(n))
    for i in range(k):p[i],p[n-1-i]=p[n-1-i],p[i]
    return p

def double(m,a,b):
    pa,pb=permutation(len(m),a),permutation(len(m),b)
    return [[m[pa[i]][pb[j]] for j in range(len(m))] for i in range(len(m))]
def zero_ne(m,k):return all(m[i][j]==0 for i in range(k) for j in range(k,len(m)))
def rank(m,q):
    if not m:return 0
    a=[r[:] for r in m];k=0
    for j in range(len(a[0])):
        p=next((i for i in range(k,len(a)) if a[i][j]%q),None)
        if p is None:continue
        a[k],a[p]=a[p],a[k];v=pow(a[k][j],-1,q);a[k]=[v*x%q for x in a[k]]
        for i in range(len(a)):
            if i!=k:
                v=a[i][j];a[i]=[(x-v*y)%q for x,y in zip(a[i],a[k])]
        k+=1
        if k==len(a):break
    return k

def ne_table(m,q):
    n=len(m)
    return tuple(rank([row[j:] for row in m[:i]],q) for i in range(1,n+1) for j in range(n))
def target(n,r=1,weight=1,mod=3):
    t=eye(2*n)
    for i in range(n-r,n):
        j=2*n-1-i;t[i]=[0]*(2*n);t[j]=[0]*(2*n)
        t[i][j]=weight;t[j][i]=pow(weight,-1,mod)
    return t

def auth():
    s=json.loads((HERE/'SOURCES.json').read_text())
    for row in s['retained']:
        p=HERE/row['path'];need(p.is_file() and not p.is_symlink(),'missing or linked source')
        b=p.read_bytes();need(hashlib.sha256(b).hexdigest()==row['sha256'],'source SHA256')
        need(hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()==row['git_blob'],'source Git blob')
    word=json.loads(gzip.decompress((HERE/'inputs/r437-word.json.gz').read_bytes()))
    need(word['ret']==list(range(470,479)),'actual nine capture identifiers')
    cur=word['start'][:]
    for sec in ['D','A']:
        for frame,to,src in word[sec]:
            for r in [to]+src:cur[r]=frame
    dims=[]
    for r in word['ret']:
        rows=[word['lines'][i] for i in word['frames'][cur[r]]]
        dims.append(rank(rows,101))
    need(dims==[7]*9,'finite source capture ranks')
    return {'captures':word['ret'],'ranks_mod_101':dims,'all_class_split_premise':'inherited PR4014, not inferred from finite ranks'}

def exhaustive():
    receipts=[]
    for d,q,N in [(4,3,1),(6,2,2)]:
        count=0;candidates={f'{a}+{b}':0 for a in range(1,N+1) for b in range(1,N+1)}
        fullmatches=0;T=target(d//2,mod=q);tt=ne_table(T,q)
        for entries in product(range(q),repeat=d*(d-1)//2):
            m=lower(d,entries,q);count+=1
            for a in range(1,N+1):
                for b in range(1,N+1):
                    x=double(m,a,b);p=max(a,b)
                    if a!=b:
                        need(not zero_ne(x,p),'unequal widths have nonzero NE')
                    elif zero_ne(x,a) and zero_ne(x,d-a):
                        candidates[f'{a}+{b}']+=1
                        mid=[row[a:d-a] for row in x[a:d-a]]
                        need(all(mid[i][j]==0 for i in range(len(mid)) for j in range(i+1,len(mid))),'middle lower after outer restoration')
                    # Target has both endpoint zeros; membership requires them.
                    # Compute whole NE rank table independently on remaining candidates.
                    if zero_ne(x,N) and zero_ne(x,d-N):
                        if ne_table(x,q)==tt:fullmatches+=1
        need(fullmatches==0,'exhaustive target double-coset exclusion')
        receipts.append(dict(d=d,modulus=q,all_middle_factors=count,width_pairs=N*N,outer_zero_candidates=candidates,target_rank_table_matches=fullmatches,scope='q=2 is algebra control outside odd-prime supplier admission' if q==2 else 'finite field control'))
    return receipts

def local_ring_controls():
    rng=random.Random(4374014);count=0;zero_count=0;minor_count=0
    for mod in [9,25,27]:
        units=[i for i in range(mod) if math.gcd(i,mod)==1]
        for d in [6,8,12]:
            N=d//2-1
            for _ in range(80):
                m=lower(d,[rng.randrange(mod) for _ in range(d*(d-1)//2)],mod)
                for i in range(d):m[i][i]=rng.choice(units)
                for a in range(1,N+1):
                    for b in range(1,N+1):
                        x=double(m,a,b);p=max(a,b);count+=1
                        if a!=b:
                            indices=list(range(d-a,d-b)) if a>b else list(range(a,b))
                            pa,pb=permutation(d,a),permutation(d,b)
                            rr=[pa.index(i) for i in indices];cc=[pb.index(i) for i in indices]
                            need(all(i<p for i in rr) and all(j>=p for j in cc),'unit minor lies in NE')
                            minor=[[x[i][j] for j in cc] for i in rr]
                            need(all(minor[i][j]==0 for i in range(len(minor)) for j in range(i+1,len(minor))),'identified original-order triangular minor')
                            need(all(math.gcd(minor[i][i],mod)==1 for i in range(len(minor))),'minor determinant unit');minor_count+=1
                        else:
                            # Force admissible endpoint zeros to exercise non-vacuous equal-width branch.
                            t=a
                            for i in range(t,d-t):
                                for j in range(t):m[i][j]=0
                            for i in range(d-t,d):
                                for j in range(d-t):m[i][j]=0
                            z=double(m,t,t)
                            need(zero_ne(z,t) and zero_ne(z,d-t),'forced endpoint zeros')
                            mid=[r[t:d-t] for r in z[t:d-t]]
                            need(all(mid[i][j]==0 for i in range(len(mid)) for j in range(i+1,len(mid))),'local ring central lower');zero_count+=1
    # Premise control: ordinary middle exchange realizes the target immediately.
    t=target(3,weight=2,mod=9)
    need(not all(t[i][j]==0 for i in range(6) for j in range(i+1,6)),'target violates forward alphabet')
    return dict(word_cases=count,unit_minors=minor_count,equal_width_restoration_cases=zero_count,moduli=[9,25,27])

def target_rank_cuts():
    rows=[]
    for n,r,mod,h in [(4,2,3,2),(8,3,5,2),(64,7,3,2),(128,14,3,2)]:
        t=target(n,r,h,mod);N=n-r
        measured=[]
        for p in range(1,n):
            got=rank([row[p:] for row in t[:p]],mod)
            need(got==max(0,p-N),'actual weighted target NE rank profile')
            measured.append(got)
        survivors=[]
        for a in range(1,n):
            for b in range(1,n):
                p=max(a,b)
                if p>N and abs(a-b)<=measured[p-1]:
                    need(min(a,b)>=N and a+b>=2*N+1,'strengthened mixed-width sum bound')
                    survivors.append((a,b))
        need(min(sum(x) for x in survivors)==2*N+1,'necessary width boundary arithmetic')
        quotient=[(a,b) for a,b in survivors if (a-N)+(b-N)>=r]
        need(min(a+b for a,b in quotient)==2*N+r,'quotient rank lower bound arithmetic')
        rows.append(dict(n=n,r=r,modulus=mod,outer_cut_minimum=2*N+1,quotient_minimum=2*N+r,necessary_pairs=len(quotient),realizability=False))
    return rows

def matvec(a,x,mod):return tuple(sum(u*v for u,v in zip(row,x))%mod for row in a)
def translation_escape():
    out=[]
    for n,mod,h in [(2,3,2),(2,9,2)]:
        d=2*n;xs=list(product(range(mod),repeat=d));index={x:i for i,x in enumerate(xs)};t=target(n,weight=h,mod=mod)
        displacement={x:tuple((y-z)%mod for y,z in zip(matvec(t,x,mod),x)) for x in xs}
        ds=sorted(set(displacement.values()));need(len(ds)==mod,'rank-one displacement cardinality')
        source=[int((i*37+19)%101<47) for i in range(len(xs))];saved=source[:]
        dirty=[int((i*13+7)%23<11) for i in range(len(xs))];before=dirty[:];dest=[0]*len(xs)
        for delta in ds:
            tmp=[source[index[tuple((v+w)%mod for v,w in zip(x,delta))]] for x in xs]
            for i,x in enumerate(xs):dest[i]^=int(displacement[x]==delta)&tmp[i]
            tmp=[0]*len(xs);need(not any(tmp),'temporary erased')
        expected=[source[index[matvec(t,x,mod)]] for x in xs]
        need(dest==expected and source==saved and dirty==before,'masked translation exact arbitrary-source semantics and restoration')
        # Every source basis is covered by a combinatorial incidence check, not just this sample payload.
        need(all(tuple((a+b)%mod for a,b in zip(x,displacement[x]))==matvec(t,x,mod) for x in xs),'all source delta functions')
        missing=ds[-1];witness=next(x for x in xs if displacement[x]==missing)
        need(matvec(t,witness,mod)!=witness or missing==tuple([0]*d),'missing mask witness exists')
        need(sum(displacement[x]==missing for x in xs)>0,'each translation necessary')
        y=matvec(t,witness,mod)
        wrong=sum(int(displacement[witness]==delta) * int(tuple((a+b)%mod for a,b in zip(witness,delta))==y) for delta in ds if delta!=missing)%2
        need(wrong==0 and int(y==matvec(t,witness,mod))==1,'deleted mask fails source delta witness')
        unweighted=target(n,weight=1,mod=mod)
        need(any(matvec(t,x,mod)!=matvec(unweighted,x,mod) for x in xs),'ancestor weight mutation detected')
        out.append(dict(modulus=mod,addresses=len(xs),branches=len(ds),mask_source_positions=len(ds)*len(xs),temporary_erases=len(ds)*len(xs),payload_inventory_cells=3*len(xs),head_and_metadata_cost='additional unresolved',every_delta_source_checked=True))
    return out

def budget():
    old=json.loads((HERE/'inputs/r437-EXPECTED.json').read_text());new=json.loads((HERE/'inputs/pr4010-RESULT.json').read_text());cat=json.loads((HERE/'inputs/pr3967-CATALOGUE.json').read_text())
    profile={int(k):v for k,v in new['profile'].items()};W=old['live'];copies=new['request_kinds']['COPY']
    need(copies==cat['literal_opcode_counts']['2']==2592,'COPY census agreement')
    mass=sum(k*v for k,v in profile.items());need(mass==new['rank_mass']==old['rank_mass']==1808352,'pooled rank mass')
    need(profile.get(26,0)==0 and profile[14]==1,'pooled profile not relabelled unpooled')
    replacement=dict(profile);replacement[7]-=copies;replacement[58]=copies;replacement[63]=copies
    need(all(x>=0 for x in replacement.values()),'valid replacement profile')
    newmass=sum(k*v for k,v in replacement.items());need(newmass-mass==114*copies,'minimum integer-rank increment')
    moment=Fraction(newmass,64*W);need(moment>1,'optimistic fixed schedule fails')
    theta=Fraction(64*W-mass,copies*114);need(theta==Fraction(107,3078),'adaptive zero-exponent necessary condition')
    return dict(pooled_profile={str(k):v for k,v in sorted(profile.items())},W=W,COPY_calls=copies,old_mass=mass,minimum_integer_rank_pair=[58,63],minimum_replacement_mass=newmass,extra_mass=newmass-mass,deficit=64*W-mass,excess=newmass-64*W,moment_zero=str(moment),adaptive_fraction_zero_necessary=str(theta),realizability=False,physical_costs='additional nonnegative and unresolved')

def evaluate():return dict(source=auth(),exhaustive=exhaustive(),local_rings=local_ring_controls(),target_rank_cuts=target_rank_cuts(),translation_escape=translation_escape(),budget=budget(),new_kappa=False)
if __name__=='__main__':
    result=evaluate()
    if '--write' in sys.argv:(HERE/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
    else:need(result==json.loads((HERE/'RESULT.json').read_text()),'committed receipt equality')
    print('PASS_AFFINE_TWO_CHILD_SCOPED_BOUND '+hashlib.sha256(canon(result)).hexdigest())
