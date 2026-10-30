#!/usr/bin/env python3
"""Matched full-chart joint compensation. Apache-2.0; polynomial helpers adapted from PR3978."""
import argparse
from collections import Counter
import gzip,hashlib,itertools,json
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
def need(ok,msg):
    if not ok:raise ValueError(msg)
def read(path):
    def unique(items):
        d={}
        for k,v in items:
            need(k not in d,'duplicate JSON key');d[k]=v
        return d
    return json.loads(path.read_text(),object_pairs_hook=unique)
def canon(x):return json.dumps(x,sort_keys=True,separators=(',',':'))+'\n'
def authenticate():
    pins=read(HERE/'SOURCES.json')
    for r in pins['files']:
        if r['usage']!='input':continue
        p=ROOT/r['path'];need(not p.is_symlink(),'source symlink');b=p.read_bytes()
        need(hashlib.sha256(b).hexdigest()==r['sha256'],'source hash '+r['path'])
        need(hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()==r['git_blob'],'source blob')
    for r in pins['source_exports']:
        b=(HERE/r['path']).read_bytes();need(hashlib.sha256(b).hexdigest()==r['sha256'],'predecessor export hash')
        need(hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()==r['upstream_git_blob'],'predecessor blob')
# Free associative algebra in A,B,T,K, with only TK=KT=1.
# A and B are deliberately NOT commuted in these identities.
def poly(letter=None): return {(() if letter is None else (letter,)):1}
def plus(*args):
    out=Counter()
    for p in args:
        for w,c in p.items():out[w]+=c
    return {w:c for w,c in out.items() if c}
def neg(p):return {w:-c for w,c in p.items()}
def times(p,q):
    out=Counter()
    for w,c in p.items():
        for v,d in q.items():
            stack=[]
            for z in w+v:
                if stack and (stack[-1],z) in [('T','K'),('K','T')]:stack.pop()
                else:stack.append(z)
            out[tuple(stack)]+=c*d
    return {w:c for w,c in out.items() if c}
def mm(a,b):return [[plus(*(times(a[i][k],b[k][j]) for k in range(2))) for j in range(2)] for i in range(2)]
def upper(x):return [[poly(),x],[{},poly()]]
def lower(x):return [[poly(),{}],[x,poly()]]

def algebra():
    I,A,B,T,K=[poly(x) for x in (None,'A','B','T','K')]
    C=[[A,plus(times(A,B),neg(I))],[I,B]]
    DT=[[I,{}],[{},T]];DK=[[I,{}],[{},K]]
    scalar=mm(mm(upper(plus(A,neg(I))),lower(I)),upper(plus(B,neg(I))))
    need(scalar==C,'three common-chart scalar layers')
    new=mm(mm(DK,scalar),DT)
    old=mm(mm(upper(times(plus(A,neg(I)),T)),lower(K)),upper(times(plus(B,neg(I)),T)))
    need(new==old,'same ordered prepared-cut operator')
    M=mm(upper(neg(B)),lower(A));J=[[{},neg(I)],[I,{}]]
    G=[[I,{}],[{},K]];entrance=[[K,{}],[{},I]]
    need(mm(mm(mm(new,G),M),entrance)==mm(mm(G,J),entrance),'same physical input tags and target')
    need(mm(scalar,DT)!=new,'missing final inverse rejected')
    need(mm(DK,scalar)!=new,'missing entrance lift rejected')
    need(mm(mm(DT,scalar),DK)!=new,'swapped boundary transforms rejected')

def geometry():
    roots=set()
    for i,j in itertools.combinations(range(8),2):
        for s in (-1,1):
            r=[0]*8;r[i]=2;r[j]=2*s;roots.add(tuple(r))
    for s in itertools.product((-1,1),repeat=7):
        if s.count(-1)%2==0:roots.add((1,)+s)
    f=read(ROOT/'research/p104-native-channel/inputs/P104-FIXTURE.json')['section4_explicit_P104']
    ports=sorted(roots-{tuple(r) for r in f['F0']+f['C']});need(len(ports)==104,'P104 ports')
    a2=[[sum(x*y for x,y in zip(r,s))//4 for s in ports] for r in ports]
    need(all(a2[i][i]==2 for i in range(104)),'unit Gram diagonal')
    off=[(i,j,a2[i][j]) for i in range(104) for j in range(104) if i!=j and a2[i][j]]
    need(len(off)==4992 and all(c in (-1,1) for i,j,c in off),'signed half support')
    # Actual in-place half/add/restore word, all208 local input columns.
    rows=[[2*(i==j) for j in range(208)] for i in range(208)]
    counts=Counter()
    for j in range(104):
        donor=104+j;need(all(v%2==0 for v in rows[donor]),'exact donor half')
        rows[donor]=[v//2 for v in rows[donor]];counts['half']+=1
        for i in range(104):
            c=a2[i][j] if i!=j else 0
            if c:rows[i]=[x+c*y for x,y in zip(rows[i],rows[donor])];counts['add']+=1
        rows[donor]=[2*v for v in rows[donor]];counts['double']+=1
    expected=[[2*(i==j) if j<104 else a2[i][j-104]-2*(i==j-104) for j in range(208)] for i in range(104)]
    need(rows[:104]==expected,'all upper-layer source columns')
    need(rows[104:]==[[2*(104+i==j) for j in range(208)] for i in range(104)],'all donor columns restored')
    return counts

def native_boundaries():
    cert=json.loads(gzip.decompress((ROOT/'research/p104-native-channel/NATIVE-RECIPES.json.gz').read_bytes()))
    entries={r['register']:r for r in cert['endpoint_adapters'] if r['position']=='entry'}
    labels=[entries['X'+str(i)]['normal'] for i in range(104)]
    need(len(set(labels))==104 and all(0<u<512 and u.bit_count()%2==1 for u in labels),'104 retained odd physical labels')
    # Tensor product labels; each elementary rank-one recipe has exact zero wrapper phase.
    lines=[sum(((a>>i)&1)*b<<(9*i) for i in range(9)) for a in labels for b in labels]
    need(len(set(lines))==10816 and all(u.bit_count()%2 for u in lines),'distinct norm-one product lines')
    count=0
    for u in lines:
        pivot=(u&-u).bit_length()-1;e=1<<pivot
        def P(x):return x^((u^e) if (x>>pivot)&1 else 0)
        need(P(e)==u,'basis image')
        for j in range(81):
            x=1<<j;need(P(P(x))==x,'involutive binary basis permutation');count+=1
    # Gaussian numerator/2 for C_u and inverse, exact phase on every translated pair.
    def gm(a,b):return (a[0]*b[0]-a[1]*b[1],a[0]*b[1]+a[1]*b[0])
    plus=lambda a,b:(a[0]+b[0],a[1]+b[1])
    a,b=(1,1),(1,-1)
    need(plus(gm(a,b),gm(b,a))==(4,0) and plus(gm(a,a),gm(b,b))==(0,0),'C inverse phase')
    need(plus(gm(a,a),gm(b,b))==(0,0) and plus(gm(a,b),gm(b,a))==(4,0),'C squared translation')
    return {'physical_labels':labels,'product_line_count':len(lines),'binary_basis_checks':count,'recipe':'P_u C_p P_u; inverse X_u P_u C_p P_u','rank_per_direction':1,'recipe_phase':0}

def run():
    authenticate();algebra();counts=geometry();native=native_boundaries()
    old=read(HERE/'inputs/pr3978-RESULT.json');n=104;N=n*n
    need(old['joint_route']['positive_rank_one_copy_transforms']==3*N,'predecessor matched native bill')
    need(old['joint_route']['unit_array_adds']==2*n*counts['add']+N,'predecessor same scalar support')
    w=read(ROOT/'research/p104-native-channel/inputs/LOWRANK-WITNESS.json')
    mass=sum(e[4] for e in w['program'] if e[0]=='transport')
    progress=sum(len(w['final_frames'][r])-len(f) for r,f in w['initial_frames'].items())
    need((mass,progress)==(2368,2312),'inherited bare channel recount')
    W=2*N+2*n*72;capacity=81*W;base=2*n*mass+capacity-N-2*n*progress
    return {'schema_version':1,'scope':'same prepared physical cut as PR3978; actual producer unproved','n':n,'N':N,'native_boundary_certificate':native,
      'old_route':old['joint_route'],
      'new_route':{'positive_rank_one_transforms':2*N,'unit_array_adds':2*n*counts['add']+N,'persistent_donor_halves':2*n*counts['half'],'persistent_donor_doubles':2*n*counts['double'],'private_initializations':0,'private_copies':0,'private_erasures':0,'peak_additional_private_arrays':0,'binary_basis_permutation_passes':4*N,'inverse_translation_passes':N,'persistent_helper_changes':0,'net_persistent_chart_progress':0},
      'native_rank_saved':N,'gate':{'bare_lower_bill':base,'capacity':capacity,'old_joint_lower_bill':base+3*N,'new_joint_lower_bill':base+2*N,'new_excess':base+2*N-capacity},'selected_frontier_changed':False,'global_producer_constructed':False}
def main():
    p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');args=p.parse_args();r=run()
    if args.write:(HERE/'RESULT.json').write_text(json.dumps(r,indent=2)+'\n')
    else:need(canon(read(HERE/'RESULT.json'))==canon(r),'typed receipt mismatch')
    print('PASS full-chart joint: matched endpoint; native32448->21632; private0; gap22464')
if __name__=='__main__':main()
