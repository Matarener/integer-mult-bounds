#!/usr/bin/env python3
"""Literal global-E helper-kernel entrances with actual rational ADDRESS cuts.

Arbitrary physical dirt is interpreted in each entrance frame. New MOVE charts are rational
GL charts; the retained orthogonal-query compiler is not silently assumed.
Apache-2.0. Prepared with substantial OpenAI Codex assistance.
"""
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import argparse
import gzip
import json
from cold_cosets import bits,need
from helper_tail_retime import WORD,RAW,replay,rankQ
from kernel_entrances import parity

HERE=Path(__file__).resolve().parent

def basis(rows):
    out={}
    for row in rows:
        row=list(map(Q,row))
        for j,v in sorted(out.items()):
            c=row[j]
            if c:row=[x-c*y for x,y in zip(row,v)]
        j=next((j for j,x in enumerate(row)if x),None)
        if j is not None:
            c=row[j];row=[x/c for x in row]
            for k,v in list(out.items()):
                c=v[j]
                if c:out[k]=[x-c*y for x,y in zip(v,row)]
            out[j]=row
    return [out[k]for k in sorted(out)]

def contains(B,v):
    v=list(map(Q,v))
    for b in B:
        j=next(j for j,x in enumerate(b)if x)
        c=v[j]
        if c:v=[x-c*y for x,y in zip(v,b)]
    return not any(v)

def inv(A):
    n=len(A);Z=[list(map(Q,row))+[Q(i==j)for j in range(n)]for i,row in enumerate(A)]
    for j in range(n):
        k=next(i for i in range(j,n)if Z[i][j]);Z[j],Z[k]=Z[k],Z[j]
        c=Z[j][j];Z[j]=[x/c for x in Z[j]]
        for i in range(n):
            if i!=j:
                c=Z[i][j]
                if c:Z[i]=[x-c*y for x,y in zip(Z[i],Z[j])]
    return [r[n:]for r in Z]

def mm(A,B):return [[sum(x*y for x,y in zip(r,c))for c in zip(*B)]for r in A]
def tr(A):return list(map(list,zip(*A)))
def matkey(A):return [[str(x)for x in r]for r in A]
def eye(n):return [[Q(i==j)for j in range(n)]for i in range(n)]

def projector(B):
    if not B:return [[Q(0)]*8 for _ in range(8)]
    return mm(mm(tr(B),inv(mm(B,tr(B)))),B)

def det(A):
    A=[r[:]for r in A];v=Q(1)
    for j in range(len(A)):
        k=next(i for i in range(j,len(A))if A[i][j])
        if k!=j:A[j],A[k]=A[k],A[j];v=-v
        c=A[j][j];v*=c
        for i in range(j+1,len(A)):
            a=A[i][j]/c
            for k in range(j+1,len(A)):A[i][k]-=a*A[j][k]
    return v

def primefactors(v):
    v=abs(v);out=[];p=2
    while p*p<=v:
        if v%p==0:
            out.append(p)
            while v%p==0:v//=p
        p+=1 if p==2 else 2
    if v>1:out.append(v)
    return out

def frames(raw,d):
    roots=raw['lines'];old=raw['frames'];base=[basis(roots[j]for j in f)for f in old]
    E=basis(roots[j]for j in range(d))
    need(E==[eye(8)[i]for i in range(d)],'selected common E is literal coordinate plane')
    new=dict(raw);new['frames']=[f[:]for f in old]
    table={tuple(tuple(r)for r in B):i for i,B in enumerate(base)}
    def get(B):
        k=tuple(tuple(r)for r in B)
        if k not in table:
            table[k]=len(base);base.append(B)
            new['frames'].append([p for p,q in enumerate(roots)if contains(B,q)])
        return table[k]
    ef=get(E);joins=[]
    for f in range(len(old)):joins.append(get(basis(base[f]+E)))
    return new,ef,joins,base

def factor_dirty(records):
    cols={h:0 for h in range(222,651)}
    for op,t,h,c,f,ph in records:
        if op==1 and ph==10:
            need(c==1 and f==0 and 111<=t<222,'literal compensation atZERO')
            cols[h]^=1<<(t-111)
    B={};pivots=[];dependent=[];setup=[];witness=[]
    for h,v in cols.items():
        z=v;c=0
        while z:
            j=z.bit_length()-1
            if j not in B:
                B[j]=(z,c^(1<<len(pivots)));pivots.append(h);break
            w,a=B[j];z^=w;c^=a
        if not z:
            used=[pivots[i]for i in bits(c)];w=cols[h]
            for k in used:w^=cols[k]
            need(w==0,'every dependent column is exact pivot-column XOR')
            dependent.append(h);setup.extend((k,h)for k in used)
            witness.append({'helper':h,'pivot_helpers':used,'old_dirty_weight':v.bit_count()})
    need(len(pivots)==111 and len(dependent)==318,'literal compensation has rank111 and kernel318')
    need(not set(pivots)&set(dependent),'disjoint pivot/dependent coordinates gives N^2=0 overZ')
    return cols,pivots,dependent,setup,witness

def build(base,raw,d):
    geom,E,joins,B=frames(raw,d)
    cols,pivots,dependent,setup,witness=factor_dirty(base['records'])
    dependent=set(dependent);records=[];start=base['start'][:]
    for h in dependent:start[h]=E
    current=start[:]
    def move(r,f,ph):
        old=current[r]
        if old==f:return
        need(all(contains(B[f],q)for q in B[old]),'new frame climb is genuinely nested')
        delta=len(B[f])-len(B[old]);need(delta>0,'strict join climb')
        records.append([0,r,old,f,delta,ph]);current[r]=f
    # D*S overF2 has the original pivot columns and zero dependent columns.
    records.extend(r[:]for r in base['records']if r[-1]==10 and r[2]not in dependent)
    for r,f in enumerate(base['start']):move(r,joins[f],80)
    need(all(current[h]==E for h in range(222,651)),'all helpers at the actual common E setup cut')
    records.extend([1,k,h,1,E,81]for k,h in setup)
    for op,r,s,c,f,ph in base['records']:
        if ph==10:continue
        if op==0:move(r,joins[c],ph)
        else:
            need(current[r]==current[s]==joins[f],'old ADD becomes a true joined common-frame ADD')
            records.append([1,r,s,c,joins[f],ph])
    need(all(current[h]==1 for h in range(222,651)),'all helpersFULL before inverse setup')
    records.extend([1,k,h,-1,1,82]for k,h in reversed(setup))
    new=dict(base);new.update(start=start,records=records,format='R429-global-coordinate-E-kernel-entrances-v1')
    return new,geom,E,joins,B,pivots,sorted(dependent),setup,witness

def native_charts(new,geom,B):
    I=eye(8);used={f for r in new['records']for f in([r[2],r[3]]if r[0]==0 else[r[4]])}
    Ps={f:projector(B[f])for f in used};frame_rows=[];bad={2};odd=[]
    for f in sorted(used):
        P=Ps[f];need(mm(P,P)==P and tr(P)==P,'actual rational orthogonal frame projector')
        gram=mm(B[f],tr(B[f]));g=det(gram)if gram else Q(1)
        need(g>0,'all used rational frames nondegenerate')
        for v in [g]+[x for r in P for x in r]:
            bad.update(primefactors(v.denominator))
        bad.update(primefactors(g.numerator))
        if any(x.denominator&(x.denominator-1)for r in P for x in r):odd.append(f)
        frame_rows.append({'frame':f,'rank':len(B[f]),'root_basis_rref':matkey(B[f]),'projector':matkey(P),'gram_det':str(g)})
    pairs=sorted({(r[2],r[3])for r in new['records']if r[0]==0});charts=[]
    for a,b in pairs:
        P,Qp=Ps[a],Ps[b]
        need(mm(P,Qp)==P==mm(Qp,P),'actual ADDRESS nested-projector compatibility')
        W=[[Qp[i][j]-P[i][j]for j in range(8)]for i in range(8)]
        need(mm(W,W)==W and tr(W)==W,'actual residual is an orthogonal projector')
        rank=len(B[b])-len(B[a]);K=basis(W);Kperp=basis([[I[i][j]-W[i][j]for j in range(8)]for i in range(8)])
        need(len(K)==rank and len(K)+len(Kperp)==8,'actual native residual rank')
        C=tr(K+Kperp);Ci=inv(C)
        expected=[[C[i][j]if j<rank else Q(0)for j in range(8)]for i in range(8)]
        need(mm(W,C)==expected and mm(C,Ci)==I,'literal GL ADDRESS adapter: C diag(I_r,0) C^-1=W')
        # This 8x8 identity proves the full16x16 interchange conjugation:
        # diag(C,C) D_coord(r) diag(C^-1,C^-1)=D_W.
        # D_b D_a=D_(b-a) follows by expanding the nested projectors above.
        for v in [x for r in C+Ci for x in r]:bad.update(primefactors(v.denominator))
        charts.append({'old_frame':a,'new_frame':b,'query_rank':rank,'residual_projector':matkey(W),
                       'ADDRESS_C':matkey(C),'ADDRESS_C_inverse':matkey(Ci),
                       'interchange_identity':'diag(C,C) D_coord(rank) diag(C^-1,C^-1) = D_(Pnew-Pold) = D_new D_old'})
    return frame_rows,charts,sorted(bad),odd

def receipt(d,write=False):
    need(sha256(WORD.read_bytes()).hexdigest()=='0f461dbc7e82a02faedb4a5129103963507c9f063a0a3679ba5d20ad94df160e','frozen FULL word')
    need(sha256(RAW.read_bytes()).hexdigest()=='a353999bceac4ac957f540adfd3e5f8768297138b27132eeb83332e2ea4b1022','frozen root geometry')
    base=json.loads(gzip.decompress(WORD.read_bytes()));raw=json.loads(gzip.decompress(RAW.read_bytes()))
    new,geom,E,joins,B,pivots,deps,setup,witness=build(base,raw,d)
    rows,rec=replay(new,geom)
    need(all(rows[h]=={h:1}for h in list(range(111))+list(range(222,651))),'all111 source and429 helper rows exactly restored overZ')
    expected=[1<<j for j in range(651)]
    for p in range(111):expected[111+p]^=1<<p
    need(parity(rows)==expected,'all651 binary columns: exact clean FULL shear')
    closed,invrec=replay(new,geom,rows,True)
    need(closed==[{j:1}for j in range(651)],'literal inverse every arbitrary integer column')
    need(rec['mass']==5097-318*d,'complete mass equals declared source/target and paired helper progress')
    fs,charts,bad,odd=native_charts(new,geom,B)
    # Root-plane E has a coordinate owner route, independent of the new joins.
    need(B[E]==[eye(8)[i]for i in range(d)],'coordinate helper residual owner route')
    wrapper=eye(8)[d:]+eye(8)[:d]
    need(mm(wrapper,tr(wrapper))==eye(8),'whole helper residual route is a literal coordinate permutation')
    enlarged=[p for p in range(111)if joins[raw['final'][111+p]]!=raw['final'][111+p]]
    need(all(len(B[joins[raw['final'][111+p]]])==8 for p in enlarged),'each changed old cap becomesFULL')
    badword=dict(new);badword['records']=[r[:]for r in new['records']if r[-1]!=82]
    br,_=replay(badword,geom)
    need(any(br[h]!={h:1}for h in range(222,651)),'missing inverse basis leaks arbitrary dirty helper')
    h=next(h for h in deps if witness[deps.index(h)]['pivot_helpers'])
    k=next(k for k,j in setup if j==h)
    badword=dict(new);badword['records']=[r[:]for r in new['records']if not(r[-1]in(81,82)and r[1]==k and r[2]==h)]
    br,_=replay(badword,geom)
    need(parity(br)!=expected,'perturbed kernel basis exposes actual target dirty column')
    canonical=json.dumps(new,sort_keys=True,separators=(',',':')).encode()
    geometry=json.dumps(geom,sort_keys=True,separators=(',',':')).encode()
    out={'status':'PASS_LITERAL_GLOBAL_COORDINATE_E_HELPER_KERNEL_FULL_BOX',
         'scientific_pin':'20ecf2891d80b5acf18d980b2164fb44ea7faa90','no_new_kappa':True,
         'sources':{str(p):sha256(p.read_bytes()).hexdigest()for p in(WORD,RAW)},
         'E_rank':d,'E_frame':E,'E_axes':list(range(d)),'ordinary_helpers':429,'private_fields':0,
         'dirty_compensation_rank':111,'selected_kernel_helpers':deps,'pivot_helpers':pivots,
         'compensation_kernel_witnesses':witness,'new_basis_ADDs':2*len(setup),
         'all651_signed_restored_source_helper_rows':True,'all651_clean_F2_columns':True,'literal_inverse':invrec,
         'profile':rec,'helper_inventory_by_residual_width':{8-d:318,8:111},
         'paired_owner_residual_coordinate_permutation':matkey(wrapper),
         'old_cap_targets_enlarged_toFULL':enlarged,'old_cap_target_lift_count':len(enlarged),
         'native_rational_ADDRESS_frames':fs,'native_rational_ADDRESS_MOVE_charts':charts,
         'finite_bad_prime_factors':bad,'joined_frames_with_odd_projector_denominators':odd,
         'word_canonical_sha256':sha256(canonical).hexdigest(),'geometry_canonical_sha256':sha256(geometry).hexdigest(),
         'construction':'Choose111 original independent dirty columns; for each of318 dependent columns j, write it as XOR of pivots I_j. At a common actual E perform helper_i += helper_j for i in I_j. These integer shears commute because their destinations are pivots and sources are dependent, hence S=I+N with N^2=0 overZ. D*S mod2 has unchanged pivot columns and zero dependent columns, so initialZERO compensation never reads the318 nonzero-entrance helpers. Replace each subsequent native frame f by span(f,E), execute the old scalar word, then apply S^-1 atFULL.',
         'contract':'318 explicitly selected arbitrary dirty helpers enter at coordinate E and leaveFULL;111 pivot helpers enterZERO and leaveFULL. All429 are restored exactly overZ. Source entrancesPp and all source/targetFULL exits are unchanged from the FULL box; target entrances remainZERO. Physical helper residual D_FULL D_E^-1 is coordinate-width8-d.',
         'complete_price':'All public forced early climbs, all joined internal queries, all helper setup/restoration ADDs and changed initial compensation are in the literal word/profile. Public native coverage remains111*(7+8); helper coverage111*8+318*(8-d) equals the entire query mass. No private COPY or additional recursive adapter query is omitted. ADDRESS charts are rational GL maps with explicit finite prime exclusions; their scalar lowering/source/tape invoice and the retained self-recursive admission premise require review.',
         'owner_gate':'The physical owner residual is D_FULL D_E^-1 and all public dependence on arbitrary helper dirt cancels. An arbitrary physical helper u can be interpreted as h=D_E^-1u with no executed E query merely for this interpretation. An explicit E lift is needed only if retaining the old ZERO logical-dirt identification. Coordinate residual routes alone do not prove chronological whole-owner availability.',
         'old_cap_gate':'Applying this boost to the old cap-exit CLEAN box enlarges exactly the listed old target caps toFULL. Their native per-port operator changes and all target lifts must be charged; no old paired caller is imported for that changed hybrid.',
         'controls':{'omitted_inverse_basis_fails_Z_helpers':True,'perturbed_kernel_leaks_F2_dirt':True},
         'limits':['No admitted chronological owner/caller for these entrances.','No complete outer moment or all-size tape/rounding theorem.','Rational GL ADDRESS charts are explicit algebra; they do not by themselves certify compatibility with a narrower orthogonal/dyadic recursive query alphabet.'],
         'attribution':'Frozen R429 word and E8 root supplier ancestry retain their original authorship. This lane supplies the global compensation-kernel basis, exact common-E boost, full-column checks, rational ADDRESS adapters and paired coordinate residuals.'}
    out=json.loads(json.dumps(out));prefix=f'GLOBAL-KERNEL-E{d}'
    paths=[HERE/(prefix+'-WORD.json.gz'),HERE/(prefix+'-GEOMETRY.json.gz')]
    for p,data in zip(paths,[canonical,geometry]):
        if write:p.write_bytes(gzip.compress(data,mtime=0))
        else:need(gzip.decompress(p.read_bytes())==data,'saved global kernel artifact differs')
    p=HERE/(prefix+'.json')
    if write:p.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    else:need(json.loads(p.read_bytes())==out,'saved global kernel receipt differs')
    return out

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--rank',type=int,choices=range(1,8),default=2);ap.add_argument('--write',action='store_true');args=ap.parse_args()
    out=receipt(args.rank,args.write)
    print(out['status']);print('E',args.rank,'H',out['profile']['H'],'mass',out['profile']['mass'],'helpers',out['helper_inventory_by_residual_width'],'badprimes',out['finite_bad_prime_factors'],'old cap lifts',out['old_cap_target_lift_count'])

if __name__=='__main__':main()
