#!/usr/bin/env python3
"""Independent exact audit of three fixed changed-helper-boundary words.

Dense signed rows; semantic binary dirt; integer Gram projectors; direct
ADDRESS-column tests. No producer mathematics imported. Standard library only.
Apache-2.0; substantial OpenAI Codex assistance.
"""
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import argparse, gzip, json

HERE=Path(__file__).resolve().parent
FROZEN=HERE.parent/'b10-staging/frozen'
LANE='changed/bit-native-caller/'
RAW='upstream/research/bit-r438-transport-rehost/words/r438-t154.json.gz'
BASE='major/bit-endpoint/BIT-FULL-COMPENSATION-WORD.json.gz'
# The exact input hash map is appended below before main() is called.

class Rejection(ValueError):
    def __init__(self,kind,detail):self.kind=kind;super().__init__(kind+': '+detail)
def need(ok,message):
    if not ok:raise ValueError(message)
def typed(ok,kind,detail):
    if not ok:raise Rejection(kind,detail)
def canonical(x):return json.dumps(x,sort_keys=True,separators=(',',':')).encode()
def ident(n):return [[int(i==j) for j in range(n)] for i in range(n)]
def mm(a,b):return [[sum(x*y for x,y in zip(r,c)) for c in zip(*b)] for r in a]
def tr(a):return list(map(list,zip(*a)))
def sub(a,b):return [[x-y for x,y in zip(r,s)] for r,s in zip(a,b)]
def parse(a):return [list(map(Q,r)) for r in a]
def ser(a):return [[str(x) for x in r] for r in a]
def matvec(a,v):return [sum(x*y for x,y in zip(r,v)) for r in a]
def bits(x):return [j for j in range(x.bit_length()) if x>>j&1]
def rank2(rows):
    rows=[r[:] for r in rows];k=0
    if not rows:return 0
    for j in range(len(rows[0])):
        p=next((p for p in range(k,len(rows)) if rows[p][j]&1),None)
        if p is None:continue
        rows[k],rows[p]=rows[p],rows[k]
        for p in range(k+1,len(rows)):
            if rows[p][j]&1:rows[p]=[x^y for x,y in zip(rows[p],rows[k])]
        k+=1
        if k==len(rows):break
    return k
def rref(a):
    a=[list(map(Q,r)) for r in a];k=0
    if not a:return []
    for j in range(len(a[0])):
        p=next((p for p in range(k,len(a)) if a[p][j]),None)
        if p is None:continue
        a[k],a[p]=a[p],a[k];v=a[k][j];a[k]=[x/v for x in a[k]]
        for p in range(len(a)):
            if p!=k:
                v=a[p][j]
                if v:a[p]=[x-v*y for x,y in zip(a[p],a[k])]
        k+=1
        if k==len(a[0]):break
    return a[:k]
def inverse_det(a):
    n=len(a);z=[list(map(Q,r))+s for r,s in zip(a,ident(n))];det=Q(1)
    for j in range(n):
        p=next(p for p in range(j,n) if z[p][j])
        if p!=j:z[p],z[j]=z[j],z[p];det=-det
        v=z[j][j];det*=v;z[j]=[x/v for x in z[j]]
        for p in range(n):
            if p!=j:
                v=z[p][j]
                if v:z[p]=[x-v*y for x,y in zip(z[p],z[j])]
    return [r[n:] for r in z],det
def primes(n):
    n=abs(n);out=set();p=2
    while p*p<=n:
        if n%p==0:
            out.add(p)
            while n%p==0:n//=p
        p+=1
    if n>1:out.add(n)
    return out
def dense_hash(rows):
    h=sha256()
    for r in rows:h.update((','.join(map(str,r))+'\n').encode())
    return h.hexdigest()
def load(name):
    data=(FROZEN/name).read_bytes()
    return json.loads(gzip.decompress(data) if name.endswith('.gz') else data)

class Geometry:
    def __init__(self,raw):
        self.raw=raw;self.bases=[];self.originals=[];self.frame_basis_ports=[];self.projections={};self.nested_cache={}
        for frame in raw['frames']:
            echelon={};original=[];labels=[]
            for p in frame:
                v=list(map(Q,raw['lines'][p]))
                for j,row in sorted(echelon.items()):
                    c=v[j]
                    if c:v=[x-c*y for x,y in zip(v,row)]
                j=next((j for j,x in enumerate(v) if x),None)
                if j is not None:
                    c=v[j];echelon[j]=[x/c for x in v];original.append(raw['lines'][p]);labels.append(p)
            self.bases.append(rref(original));self.originals.append(original);self.frame_basis_ports.append(labels)
        self.dims=list(map(len,self.bases))
    def nested(self,a,b):
        key=(a,b)
        if key not in self.nested_cache:
            self.nested_cache[key]=len(rref(self.bases[a]+self.bases[b]))==self.dims[b]
        return self.nested_cache[key]
    def projector(self,f):
        if f not in self.projections:
            B=self.originals[f]
            if B:
                inv,det=inverse_det(mm(B,tr(B)));P=mm(mm(tr(B),inv),B)
            else:det=Q(1);P=[[Q(0)]*8 for _ in range(8)]
            need(P==tr(P) and mm(P,P)==P,'independent rational orthogonal projector')
            need(det.denominator==1 and det>0,'integer-basis Gram determinant')
            self.projections[f]=(P,det)
        return self.projections[f][0]

def replay(program,geom,back=False,initial=None,omit_comp=False,track_peak=True):
    n=len(program['start']);has_private=any(r[0] in (2,3) for r in program['records'])
    width=n if initial is None else len(initial[0])
    state=ident(n)+([[0]*n] if has_private else []) if initial is None else [r[:] for r in initial]
    frames=(program['final'] if back else program['start'])[:]+([None] if has_private else [])
    hist=Counter();adds=0;copies=[];opened=None;peak=max(sum(map(abs,r)) for r in state)
    records=list(enumerate(program['records']))
    if back:records.reverse()
    for at,(op,d,s,c,f,phase) in records:
        detail=f'record {at}'
        typed(0<=d<n,'register',detail)
        if op==0:
            a,b=(c,s) if back else (s,c);lo,hi=(b,a) if back else (a,b)
            typed(frames[d]==a and geom.nested(lo,hi) and geom.dims[hi]-geom.dims[lo]==f>0,'frame',detail)
            frames[d]=b;hist[f]+=1
        elif op==1:
            typed(d!=opened,'snapshot',detail)
            typed(0<=s<len(state) and d!=s and frames[d]==frames[s]==f,'frame',detail)
            if not(omit_comp and phase==10):
                sign=-c if back else c
                state[d]=[x+sign*y for x,y in zip(state[d],state[s])]
                if track_peak:peak=max(peak,sum(map(abs,state[d])))
            adds+=1
        elif op==(3 if back else 2):
            typed(has_private and s==n and opened is None and frames[n] is None and not any(state[n]),'snapshot',detail)
            typed(frames[d]==c and geom.nested(f,c) and geom.dims[c]>geom.dims[f],'frame',detail)
            cost=geom.dims[c]-geom.dims[f];hist[cost]+=1
            copies.append({'source_helper':d,'source_frame':c,'private_frame':f,'query_rank':cost})
            state[n]=state[d][:];frames[n]=f;opened=d
        else:
            typed(op==(2 if back else 3) and opened==d and s==n and state[n]==state[d],'snapshot',detail)
            typed(frames[d]==c and frames[n]==f,'frame',detail)
            state[n]=[0]*width;frames[n]=None;opened=None
    typed(frames==(program['start'] if back else program['final'])+([None] if has_private else []),'frame','endpoint')
    typed(opened is None and (not has_private or not any(state[n])),'snapshot','endpoint')
    rec={'H':dict(sorted(hist.items())),'mass':sum(k*v for k,v in hist.items()),'ADDs':adds,'prefix_row_L1':peak}
    if has_private:rec.update(COPYs=len(copies),private_fields=1,COPY_records=copies)
    return state,rec

def original_clean(raw,geom):
    frames=raw['start'][:];records=[]
    def move(d,f):
        if frames[d]!=f:
            records.append([0,d,frames[d],f,geom.dims[f]-geom.dims[frames[d]],0]);frames[d]=f
    for name,phase,sign in [('D',10,1),('A',2,1),('B',4,1),('C',5,-1)]:
        if name=='B':
            for j,h in enumerate(raw['ret']):
                records.append([2,h,660,frames[h],0,3])
                records += [[1,111+p,660,1,0,3] for p,ss in enumerate(raw['scatter']) if j in ss]
                records.append([3,h,660,frames[h],0,3])
        for f,d,ss in raw[name]:
            for r in [d]+ss:move(r,f)
            records += [[1,d,s,sign,f,phase] for s in ss]
    for d,f in enumerate(raw['final']):move(d,f)
    return {'start':raw['start'],'final':raw['final'],'records':records}

def semantic_dirty(base,geom):
    n=len(base['start']);h=n-222;has_private=n==660
    initial=[[int(222+j==i) for j in range(h)] for i in range(n)]+([[0]*h] if has_private else [])
    rows,cost= replay(base,geom,initial=initial,omit_comp=True,track_peak=False)
    need(rows[:111]==[[0]*h for _ in range(111)] and rows[222:n]==ident(h),'semantic dirt replay restores every source/helper integer row')
    D=[[v%2 for v in row] for row in rows[111:222]]
    literal=[[0]*h for _ in range(111)]
    for op,d,s,c,f,phase in base['records']:
        if op==1 and phase==10:
            need(111<=d<222 and 222<=s<n and f==0,'initial compensation domain')
            literal[d-111][s-222]^=c%2
    need(D==literal and rank2(D)==111,'complete semantic dirty matrix equals literal compensation and has rank111')
    cost.pop('prefix_row_L1')
    return D,cost

def join_contract(base,program,oldgeom,geom,E=None,selected=None):
    if E is None:
        original=[r for r in base['records'] if r[0]==1 and r[-1]!=10]
        actual=[r for r in program['records'] if r[0]==1 and r[-1] not in (10,71,72)]
        need(original==actual,'all ten-local inherited scalar operations unchanged')
        before=Counter(tuple(r[:5]) for r in base['records'] if r[0]==0)
        after=Counter(tuple(r[:5]) for r in program['records'] if r[0]==0)
        for h in selected:
            first=next(r for r in base['records'] if r[0]==0 and r[1]==h)
            need(first[2]==0 and first[3]==program['start'][h] and first[4]==1,'actual selected first rank-one MOVE')
            before[tuple(first[:5])]-=1
        need(+before==after and program['start'][:222]==base['start'][:222] and program['final']==base['final'],'exact ten removed H1 queries and unchanged public cuts')
        return
    original=[r for r in base['records'] if r[0]!=0 and r[-1]!=10]
    actual=[r for r in program['records'] if r[0]!=0 and r[-1] not in (10,81,82)]
    joins={}
    def joined(f):
        if f not in joins:joins[f]=rref(oldgeom.bases[f]+geom.bases[E])
        return joins[f]
    need(len(original)==len(actual),'same complete scalar and COPY/ERASE word after common-E change')
    for old,new in zip(original,actual):
        op,d,s,c,f,phase=old
        need(new[:3]==old[:3] and new[-1]==phase,'inherited operation chronology and roles')
        if op==1:
            need(new[3]==c and geom.bases[new[4]]==joined(f),'each old ADD is at its exact joined frame')
        else:
            need(geom.bases[new[3]]==joined(c) and geom.bases[new[4]]==joined(f),'each old COPY/ERASE uses exact joined source and private frames')
    need(program['start'][:222]==base['start'][:222],'source and target entrance cuts preserved')
    need(all(geom.bases[f]==joined(base['final'][r]) for r,f in enumerate(program['final'])),'every declared exit is the actual old exit joined with E')

def factor_columns(D):
    # Low-pivot dense elimination, recording expansions in original columns.
    # The producer uses high-bit sparse elimination; the solutions are unique.
    B={};piv=[];deps=[];expansion={}
    for h,col in enumerate(tr(D),222):
        v=col[:];coeff=set()
        for j in sorted(B):
            if v[j]:
                row,support=B[j];v=[x^y for x,y in zip(v,row)];coeff^=support
        j=next((j for j,x in enumerate(v) if x),None)
        if j is None:deps.append(h);expansion[h]=sorted(coeff)
        else:piv.append(h);B[j]=(v,coeff^{h})
    need(len(piv)==111,'independent dirty pivot columns')
    return piv,deps,expansion

def basis_check(program,D,saved,ten=False):
    n=len(program['start']);forward_tag,backward_tag=(71,72) if ten else (81,82)
    forward=[r for r in program['records'] if r[-1]==forward_tag]
    backward=[r for r in program['records'] if r[-1]==backward_tag]
    need(all(r[0]==1 and r[3]==1 for r in forward),'integer shear basis gates')
    pairs=[(r[1],r[2]) for r in forward];dest={d for d,s in pairs};source={s for d,s in pairs}
    need(not dest&source and len(pairs)==len(set(pairs)),'N squared zero over integers, no repeated coefficient')
    expected=[[1,d,s,-1,1,backward_tag] for d,s in reversed(pairs)]
    if ten:
        need(sorted(backward)==sorted(expected),'literal inverse for the three disjoint local bases')
        selected=[w['selected_helper'] for w in saved['compensation_kernel_witnesses']]
        need(len(selected)==10 and set(source)<=set(selected),'ten selected entrance directions')
        groups={w['selected_helper']:w for w in saved['compensation_kernel_witnesses']}
        for h in selected:
            support=[h]+[d for d,s in pairs if s==h]
            need(sorted(support)==sorted(groups[h]['kernel_helpers']),'actual ten-group kernel support')
    else:
        need(backward==expected,'literal reverse signed basis inverse')
        piv,selected,expansions=factor_columns(D)
        need(piv==saved['pivot_helpers'] and selected==saved.get('selected_kernel_helpers',saved.get('selected_helpers')),'independently reconstructed greedy pivots and kernel coordinates')
        need(pairs==[(k,h) for h in selected for k in expansions[h]],'every emitted basis shear equals semantic unique solution')
        source=set(selected)
    Ds=[r[:] for r in D]
    for d,s in pairs:
        for p in range(111):Ds[p][s-222]^=D[p][d-222]
    need(all(Ds[p][h-222]==0 for p in range(111) for h in selected),'all selected columns of D S vanish')
    compensation=[[0]*(n-222) for _ in range(111)]
    for op,d,s,c,f,phase in program['records']:
        if op==1 and phase==10:
            need(f==0 and program['start'][s]==0,'new compensation only reads actual ZERO entrances')
            compensation[d-111][s-222]^=c%2
    need(compensation==Ds,'complete new compensation is D S overF2')
    need(len(forward)+len(backward)==saved.get('new_basis_ADDs',saved.get('new_basis_scalar_ADDs')),'full basis ADD count')
    return selected,pairs,{'basis_ADDs':2*len(pairs),'N_squared_zero_over_Z':True,'dirty_rank':111,
                           'semantic_dirty_rows':[sum(x<<j for j,x in enumerate(r)) for r in D],
                           'selected_helpers':selected,'basis_pairs':[list(p) for p in pairs]}

def signed_contract(program,geom,saved):
    n=len(program['start']);private=n==660
    fw,profile=replay(program,geom)
    need(json.loads(json.dumps(profile))==saved['profile'],'complete independently recomputed profile including prefix')
    inverse_expected=ident(n)+([[0]*n] if private else [])
    max_coeff=0;even_nonzero=0
    for i,row in enumerate(fw):
        expected=[int(i==j) for j in range(n)]
        if 111<=i<222:
            need(row[111:222]==[int(i==111+j) for j in range(111)],'all old-y coefficients form exact identity')
            expected[i-111]=1
            need([x%2 for x in row]==expected,'all binary target source/helper columns')
            inverse_expected[i]=[-x+(2 if j==i else 0) for j,x in enumerate(row)]
            even_nonzero+=sum(bool(x) for x in row[222:])
        else:need(row==expected,'all signed source/helper rows and zero private return')
        max_coeff=max(max_coeff,max(map(abs,row),default=0))
    bw,back_profile=replay(program,geom,back=True)
    need(bw==inverse_expected,'complete literal signed inverse matrix, both compositions follow from shear block')
    need(back_profile['H']==profile['H'] and back_profile['ADDs']==profile['ADDs'],'inverse pays complete same histogram')
    need(all(program['final'][h]==1 for h in range(222,n)),'all helpers end FULL')
    inventory=Counter(8-geom.dims[f] for f in program['start'][222:])
    need(json.loads(json.dumps(dict(sorted(inventory.items()))))==saved['helper_inventory_by_residual_width'],'paired helper residual inventory')
    return {'forward_sha256':dense_hash(fw),'inverse_sha256':dense_hash(bw),
            'compared_entries_per_orientation':len(fw)*n,'forward_profile':profile,'inverse_from_identity_profile':back_profile,
            'maximum_endpoint_coefficient':max_coeff,'nonzero_even_helper_coefficients_in_targets':even_nonzero,
            'residual_width_inventory':dict(inventory)}

def controls(program,geom,selected,pairs,ten=False):
    n=len(program['start']);private=n==660;h=pairs[0][1];d=pairs[0][0]
    initial=[[int(i==h)] for i in range(n)]+([[0]] if private else [])
    front,back=(71,72) if ten else (81,82)
    bad=dict(program);bad['records']=[r for r in program['records'] if r[-1]!=back]
    rows,_=replay(bad,geom,initial=initial,track_peak=False)
    changed=[i for i in range(222,n) if rows[i]!=initial[i]]
    need(changed,'omitted integer inverse basis fails helper restoration on actual dirty column')
    bad=dict(program);bad['records']=[r for r in program['records'] if not(r[-1] in (front,back) and r[1]==d and r[2]==h)]
    rows,_=replay(bad,geom,initial=initial,track_peak=False)
    leaked=[i-111 for i in range(111,222) if rows[i][0]%2]
    need(leaked,'actual perturbed kernel exposes target dirty parity')
    bad=dict(program);bad['start']=program['start'][:];bad['start'][selected[0]]=0
    try:replay(bad,geom,initial=initial,track_peak=False)
    except Rejection as ex:need(ex.kind=='frame','frame control must fail intended rule');frame_error=str(ex)
    else:raise ValueError('old ZERO entrance mutation accepted')
    out={'input_dirty_helper':h,'removed_basis_pair':[d,h],'omitted_inverse_changed_helpers':changed,
         'perturbed_kernel_leaking_targets':leaked,'old_ZERO_entrance_rejection':frame_error}
    if private:
        first=next(i for i,r in enumerate(program['records']) if r[0]==3)
        bad=dict(program);bad['records']=program['records'][:first]+program['records'][first+1:]
        try:replay(bad,geom,initial=initial,track_peak=False)
        except Rejection as ex:need(ex.kind=='snapshot','ERASE control must fail lifecycle');out['omitted_ERASE_rejection']=str(ex)
        else:raise ValueError('omitted ERASE accepted')
    return out

def d_apply(P,v):
    head,tail=v[:8],v[8:];delta=matvec(P,[b-a for a,b in zip(head,tail)])
    return [a+c for a,c in zip(head,delta)]+[b-c for b,c in zip(tail,delta)]
def native_audit(items,geom):
    frames={};charts={};coverage={};bad={2};odd=[]
    for name,word,saved in items:
        fs=saved.get('native_rational_ADDRESS_frames',saved.get('ADDRESS_frames'))
        cs=saved.get('native_rational_ADDRESS_MOVE_charts',saved.get('ADDRESS_MOVE_and_COPY_charts'))
        used={f for r in word['records'] for f in ([r[2],r[3]] if r[0]==0 else [r[4]] if r[0]==1 else [r[3],r[4]])}
        pairs={(r[2],r[3]) for r in word['records'] if r[0]==0}|{(r[4],r[3]) for r in word['records'] if r[0]==2}
        need(set(f['frame'] for f in fs)==used and {(c['old_frame'],c['new_frame']) for c in cs}==pairs,'complete actual MOVE/COPY chart and frame coverage')
        coverage[name]={'frames':len(fs),'query_pairs':len(cs)}
        for f in fs:
            k=f['frame']
            if k in frames:need(frames[k]==f,'common frame certificate consistency')
            frames[k]=f
        for c in cs:
            k=(c['old_frame'],c['new_frame'])
            if k in charts:need(charts[k]==c,'common query certificate consistency')
            charts[k]=c
    frame_evidence=[]
    for f,c in sorted(frames.items()):
        P=geom.projector(f);B=geom.bases[f];_,g=inverse_det(mm(B,tr(B))) if B else ([],Q(1))
        need(parse(c['root_basis_rref'])==B and parse(c['projector'])==P and Q(c['gram_det'])==g and c['rank']==len(B),'every stored rational frame basis/projector/Gram determinant')
        for v in [g]+[x for r in P for x in r]:bad.update(primes(v.denominator))
        bad.update(primes(g.numerator))
        bad.update(primes(geom.projections[f][1].numerator))
        if any(x.denominator&(x.denominator-1) for r in P for x in r):odd.append(f)
        frame_evidence.append({'frame':f,'integer_basis_ports':geom.frame_basis_ports[f],
                               'integer_Gram_det':str(geom.projections[f][1]),'rank':len(B),'projector_sha256':sha256(canonical(ser(P))).hexdigest()})
    chart_evidence=[];I=ident(8)
    for (a,b),c in sorted(charts.items()):
        P,R=geom.projector(a),geom.projector(b);W=sub(R,P);r=geom.dims[b]-geom.dims[a]
        need(geom.nested(a,b) and mm(P,R)==mm(R,P)==P,'actual nested projectors')
        need(mm(W,W)==W and W==tr(W) and len(rref(W))==r>0,'actual native residual projector and rank')
        C,Ci=parse(c['ADDRESS_C']),parse(c['ADDRESS_C_inverse'])
        need(mm(C,Ci)==mm(Ci,C)==I and c['query_rank']==r and parse(c['residual_projector'])==W,'stored GL inverse and full residual')
        coordinate=[[int(i==j and i<r) for j in range(8)] for i in range(8)]
        need(mm(mm(C,coordinate),Ci)==W,'GL diagonalization of actual residual')
        for col in range(16):
            v=[int(i==col) for i in range(16)]
            z=matvec(Ci,v[:8])+matvec(Ci,v[8:]);z=d_apply(coordinate,z)
            z=matvec(C,z[:8])+matvec(C,z[8:])
            need(z==d_apply(W,v)==d_apply(R,d_apply(P,v)),'every actual 16-dimensional ADDRESS column')
        for row in C+Ci:
            for v in row:bad.update(primes(v.denominator))
        chart_evidence.append({'old':a,'new':b,'rank':r,'complete16_ADDRESS_columns':True})
    need(sorted(bad)==[2,3,5],'exact rational chart excluded-prime set')
    for name,word,saved in items:
        need(saved['finite_bad_prime_factors']==sorted(bad) and saved['joined_frames_with_odd_projector_denominators']==odd,'finite prime and odd-projector lists')
    E=[[int(i==j and i<2) for j in range(8)] for i in range(8)];Ec=sub(I,E)
    route=I[2:]+I[:2]
    need(mm(mm(route,Ec),tr(route))==[[int(i==j and i<6) for j in range(8)] for i in range(8)],'literal coordinate permutation routes the width6 residual')
    global_saved=next(saved for name,word,saved in items if name=='GLOBAL-KERNEL-E2')
    need(parse(global_saved['paired_owner_residual_coordinate_permutation'])==route,'stored paired residual route matches actual coordinate permutation')
    for col in range(16):
        v=[int(i==col) for i in range(16)];need(d_apply(I,d_apply(E,v))==d_apply(Ec,v),'coordinate paired E2/FULL residual all ADDRESS columns')
    # A one-entry residual perturbation must fail the exact native identity.
    first=next(iter(sorted(charts)));a,b=first;W=sub(geom.projector(b),geom.projector(a));wrong=[row[:] for row in W];wrong[0][0]+=1
    witness=next(col for col in range(16) if d_apply(wrong,[int(i==col) for i in range(16)])!=d_apply(geom.projector(b),d_apply(geom.projector(a),[int(i==col) for i in range(16)])))
    return {'coverage':coverage,'distinct_frames':len(frames),'distinct_query_pairs':len(charts),'frame_certificates':frame_evidence,
            'query_pairs':chart_evidence,'finite_excluded_primes':sorted(bad),'odd_projector_frames':odd,
            'coordinate_complement_route':route,
            'wrong_residual_projector_control':{'pair':list(first),'ADDRESS_column':witness},
            'scope':'Exact rational GL ADDRESS identities away from2,3,5; no orthogonal/dyadic or all-size compiler admission.'}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--write',action='store_true');args=ap.parse_args()
    pins={name:sha256((FROZEN/name).read_bytes()).hexdigest() for name in PINS}
    need(pins==PINS,'all exact frozen source bytes')
    raw=load(RAW);base=load(BASE);oldgeom=Geometry(raw)
    old=original_clean(raw,oldgeom)
    print('independent semantic dirty matrices',flush=True)
    Dfull,full_cost=semantic_dirty(base,oldgeom);Dold,old_cost=semantic_dirty(old,oldgeom)
    need(full_cost['mass']==5097 and old_cost['mass']==5121,'complete fixed baseline masses')
    need(old_cost['COPYs']==9 and sum(c['query_rank'] for c in old_cost['COPY_records'])==63,'all original nine COPY tariffs sum63')
    joined=load(LANE+'GLOBAL-KERNEL-E2-GEOMETRY.json.gz')
    need(joined==load(LANE+'OLD-KERNEL-E2-GEOMETRY.json.gz'),'exact common emitted geometry')
    geom=Geometry(joined);results={};native_items=[]
    for name,ten,D,g in [('KERNEL-ENTRANCES',True,Dfull,oldgeom),('GLOBAL-KERNEL-E2',False,Dfull,geom),('OLD-KERNEL-E2',False,Dold,geom)]:
        print('independent dense signed replay',name,flush=True)
        word=load(LANE+name+'-WORD.json.gz');saved=load(LANE+name+'.json')
        need(sha256(canonical(word)).hexdigest()==saved['word_canonical_sha256'],'frozen canonical word hash')
        if not ten:need(sha256(canonical(joined)).hexdigest()==saved['geometry_canonical_sha256'],'frozen canonical joined geometry')
        selected,pairs,basis=basis_check(word,D,saved,ten)
        join_contract(base if len(word['start'])==651 else old,word,oldgeom,g,None if ten else saved['E_frame'],selected)
        signed=signed_contract(word,g,saved);faults=controls(word,g,selected,pairs,ten)
        if ten:
            wraps=[]
            for h in sorted(selected):
                E=g.projector(word['start'][h]);need(g.dims[word['start'][h]]==1,'actual rank-one entrance')
                for col in range(16):
                    v=[int(i==col) for i in range(16)];need(d_apply(ident(8),d_apply(E,v))==d_apply(sub(ident(8),E),v),'ten actual rank7 paired residuals all ADDRESS columns')
                wraps.append({'helper':h,'entrance':word['start'][h],'residual_rank':7})
            basis['ten_paired_residuals']=wraps
        else:
            E=saved['E_frame'];need(geom.bases[E]==[[Q(i==j) for j in range(8)] for i in range(2)],'literal coordinate E2 plane')
            need(all(word['start'][h]==E for h in selected),'all dependent helpers actually enter E2')
            native_items.append((name,word,saved))
            lifts=[p for p in range(111) if word['final'][111+p]!=raw['final'][111+p]]
            if name.startswith('OLD'):
                need(lifts==saved['old_cap_targets_enlarged_toFULL'] and len(lifts)==83,'exact83 changed old target caps')
                need(sum(r['query_rank'] for r in signed['forward_profile']['COPY_records'])==52,'all nine paid copied totals sum52')
                basis['target_lift_ports']=lifts
                paths=[]
                for r in range(222):
                    path=[word['start'][r]]+[z[3] for z in word['records'] if z[0]==0 and z[1]==r]
                    paths.append({'role':r,'path':path,'ranks':[geom.dims[f] for f in path]})
                need(paths==saved['all_public_role_paths'],'all222 changed public paths and every rank')
        results[name]={'basis':basis,'signed':signed,'controls':faults}
    tenH=Counter({int(k):v for k,v in results['KERNEL-ENTRANCES']['signed']['forward_profile']['H'].items()})
    need(tenH==Counter(full_cost['H'])-Counter({1:10}),'exact ten H1 reduction from fixed baseline')
    need(results['GLOBAL-KERNEL-E2']['signed']['forward_profile']['mass']==5097-318*2==4461,'global complete coverage mass')
    need(results['OLD-KERNEL-E2']['signed']['forward_profile']['mass']==5121-327*2+83+52-63==4539,'old complete coverage and nine-COPY mass')
    print('independent rational ADDRESS chart columns',flush=True)
    native=native_audit(native_items,geom)
    out={'status':'PASS_B10_THREE_FIXED_WORDS_AND_PAIRED_NATIVE_RESIDUALS','no_new_kappa':True,'source_sha256':pins,
         'words':results,'native':native,'baseline_costs':{'R429_FULL':full_cost,'R438_CLEAN':old_cost},
         'limits':['Integer source/helper restoration; target clean shear only overF2.','Physical helper residual keyed by both entrance and exit.',
                   'No chronological owner, full caller, all-size compiler, rounded or tape admission.','Hybrid coordinate census and bank lower bound reviewed separately.']}
    out=json.loads(json.dumps(out));path=HERE/'RESULT.json'
    if args.write:path.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    else:need(json.loads(path.read_text())==out,'complete independent receipt matches')
    print(out['status'])

PINS={'changed/bit-native-caller/GLOBAL-KERNEL-BOOST.md': 'f8f8c6db53a7884660eb51860d85710e4a73960c0174393a80c42b420c6e63e7', 'changed/bit-native-caller/GLOBAL-KERNEL-E2-GEOMETRY.json.gz': '5b4fb65d4a42e0127133ba57b44d5c9f7ceb586577beae1855e43601bccbb8ea', 'changed/bit-native-caller/GLOBAL-KERNEL-E2-WORD.json.gz': 'd08f04739685c9645afd2f60e89c50d2fc353cef869da0fc77cf3f33c8e1a677', 'changed/bit-native-caller/GLOBAL-KERNEL-E2.json': '472975e220fb0705899b0cc139df8c2c37f807af87dab027d61a125bd6b07aa8', 'changed/bit-native-caller/KERNEL-ENTRANCES-WORD.json.gz': '9425c0e80cb256b389663ddecf33a08f174387096e6563c45fb38fc663acff12', 'changed/bit-native-caller/KERNEL-ENTRANCES.json': '09fe24030f394ca05818dc0436bb143e4920084a15eb18a4d4ce9fc817541ee4', 'changed/bit-native-caller/KERNEL-ENTRANCES.md': 'c2903a019ae00678d1bb98e6b97dce41298e0dfc80317d6760bc5c3331840abd', 'changed/bit-native-caller/OLD-KERNEL-E2-GEOMETRY.json.gz': '5b4fb65d4a42e0127133ba57b44d5c9f7ceb586577beae1855e43601bccbb8ea', 'changed/bit-native-caller/OLD-KERNEL-E2-WORD.json.gz': '839b246ff3dd12105b90b7c45984d3c2e98c3249b1d947493d4f94b28539a1ea', 'changed/bit-native-caller/OLD-KERNEL-E2.json': 'a3d153cc873a636531573a72412bb6d177dec8c9427318d78d7a9c3a386b2537', 'changed/bit-native-caller/global_kernel_boost.py': '22773bd9f955130ca3c1fe2fa2c047ee7d831759df08567e2a6c987349b18272', 'changed/bit-native-caller/kernel_entrances.py': '921f18dc02df3a799a4fae60aa861b1f7e908957b01b81dd395f5cd8dac222cc', 'changed/bit-native-caller/old_kernel_boost.py': '71070cceb72b089d745f080e642dce26c1404508411288265b6bf3f4a004ea20', 'major/bit-endpoint/BIT-FULL-COMPENSATION-WORD.json.gz': '0f461dbc7e82a02faedb4a5129103963507c9f063a0a3679ba5d20ad94df160e', 'upstream/research/bit-r438-transport-rehost/words/r438-t154.json.gz': 'a353999bceac4ac957f540adfd3e5f8768297138b27132eeb83332e2ea4b1022'}

if __name__=='__main__':main()
