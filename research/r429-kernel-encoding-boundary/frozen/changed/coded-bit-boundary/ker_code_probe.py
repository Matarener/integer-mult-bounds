#!/usr/bin/env python3
"""Paid102-to111 kerR code: complete optimistic bill and native cut tests.

Only frozen predecessor inputs are read. Apache-2.0; substantial OpenAI Codex
assistance. This is a scoped rejection, not a positive BIT supplier.
"""
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from math import isqrt
from pathlib import Path
import argparse
import gzip
import json
import sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
BASE=Path('/Users/ross/git/math')
OLD=BASE/'.research-automation/runs/kappa-major-20261018T1330Z'
RAW=BASE/'integer-mult-bounds/research/bit-r438-transport-rehost/words/r438-t154.json.gz'
PRUNED=BASE/'.research-automation/runs/kappa-3605-successor-20261018T0940Z/major-frontier/root-pruned-code/BIT-PRUNED-WORD.json.gz'
COMP=OLD/'bit-endpoint/BIT-FULL-COMPENSATION.json'
NATIVE=HERE.parent/'bit-native-caller/NATIVE-SEED-BINDING.json'
FULL=BASE/'integer-mult-bounds/research/e8-bit-carrier-skeleton/data/bit/bitE8-r865.json.gz'
GEOMETRY=BASE/'integer-mult-bounds/research/e8-bit-carrier-skeleton/code/nine/geometry.py'
PIN='20ecf2891d80b5acf18d980b2164fb44ea7faa90'

def need(b,m):
    if not b:raise ValueError(m)
def bits(x):
    while x:
        a=x&-x;yield a.bit_length()-1;x^=a
def xor(vs):
    x=0
    for v in vs:x^=v
    return x
def rank2(rows):
    b={}
    for r in rows:
        while r:
            k=r.bit_length()-1
            if k in b:r^=b[k]
            else:b[k]=r;break
    return len(b)
def qb(rows):
    b={}
    for r in rows:
        r=list(map(Q,r))
        for k,v in sorted(b.items()):
            c=r[k];r=[x-c*y for x,y in zip(r,v)]
        k=next((i for i,x in enumerate(r) if x),None)
        if k is not None:b[k]=[x/r[k] for x in r]
    return list(b.values())
def mm(a,b):return [[sum(x*y for x,y in zip(r,c)) for c in zip(*b)] for r in a]
def tr(a):return list(map(list,zip(*a)))
def eye(n):return [[Q(i==j) for j in range(n)] for i in range(n)]
def minus(a,b):return [[x-y for x,y in zip(r,s)] for r,s in zip(a,b)]
def ser(a):return [[str(x) for x in r] for r in a]
def fmod(x,q):return x.numerator*pow(x.denominator,-1,q)%q

def load():
    need(sha256(RAW.read_bytes()).hexdigest()=='a353999bceac4ac957f540adfd3e5f8768297138b27132eeb83332e2ea4b1022','raw pin')
    need(sha256(PRUNED.read_bytes()).hexdigest()=='1a6841fccba51fa922993c77b4b296e659c2c538252e5e06113d0438c5edb870','pruned pin')
    raw=json.loads(gzip.decompress(RAW.read_bytes()))
    pruned=json.loads(gzip.decompress(PRUNED.read_bytes()))
    comp=json.loads(COMP.read_bytes())
    r=[1<<i for i in range(660)]
    for phase in ('D','A'):
        for _,d,ss in raw[phase]:
            for s in ss:r[d]^=r[s]
    R=[r[h]&((1<<111)-1) for h in raw['ret']]
    K=[sum(1<<j for j in ss) for ss in raw['scatter']]
    need(R==comp['R'] and K==comp['K'] and rank2(R)==9,'actual independent R and K reconstruction')
    bulk=[r for r in pruned['records'] if r[0] not in (2,3) and r[-1] not in (21,22,23,24,31,32,33)]
    H=Counter(r[4] for r in bulk if r[0]==0)
    need(H==Counter({1:1295,2:1342,3:79,4:44,5:93,6:11,7:9}),'complete cheap bulk histogram')
    need(sum(k*v for k,v in H.items())==4986,'cheap bulk mass')
    need(all(not (111<=r[2]<222) for r in bulk if r[0]==1),
         'no ADD reads any target; all arbitrary old-target columns remain separate')
    return raw,pruned,R,K,bulk,H

def systematic(R,bulk):
    calls=Counter(r[1]%111 for r in bulk if r[0]==0 and r[1]<222)
    cols=[sum(((r>>p)&1)<<j for j,r in enumerate(R)) for p in range(111)]
    P=[];chosen=[];prefix=[]
    # Greedy minimum-weight basis of the binary column matroid. Weight is
    # actual source+target MOVE event count, with port ID as tie breaker.
    for p in sorted(range(111),key=lambda p:(calls[p],p)):
        if rank2(chosen+[cols[p]])>len(chosen):
            P.append(p);chosen.append(cols[p]);prefix.append({'port':p,'weight':calls[p],'rank':len(chosen)})
            if len(P)==9:break
    need(len(P)==9,'full rank strategic dependent9 set')
    rr=R[:]
    for j,p in enumerate(P):
        k=next(k for k in range(j,9) if rr[k]>>p&1)
        rr[j],rr[k]=rr[k],rr[j]
        for i in range(9):
            if i!=j and rr[i]>>p&1:rr[i]^=rr[j]
    F=[p for p in range(111) if p not in P]
    at={p:j for j,p in enumerate(F)}
    E=[0]*111
    for p in F:E[p]=1<<at[p]
    for j,p in enumerate(P):E[p]=sum(((rr[j]>>f)&1)<<at[f] for f in F)
    need(all(xor(E[p] for p in bits(row))==0 for row in R),'all102 encoded columns satisfy R E=0')
    need(rank2(E)==102,'injective arbitrary102 inputs')
    need(xor(0 for _ in ())==0,'empty XOR convention')
    # Every independent free target variable occurs in a parity cell; no
    # source column of R is zero.
    need(all(any(E[p]>>j&1 for p in P) for j in range(102)),'all102 free columns occur in parity coordinates')
    return P,F,E,rr,prefix

def replay2(rows,bulk):
    rows=rows[:]
    for op,d,s,c,f,phase in bulk:
        if op==1 and c&1:rows[d]^=rows[s]
    return rows

def scalar_certificate(P,F,E,R,K,bulk):
    J=[(1<<p)^xor(R[j] for j in bits(mask)) for p,mask in enumerate(K)]
    W=K[:]
    for p in (0,1,2):W[p]=0
    A=[(1<<p)^xor(R[j] for j in bits(mask)) for p,mask in enumerate(W)]
    need(all(xor(E[q] for q in bits(J[p]))==E[p] for p in range(111)),'J E=E')
    need(all(xor(E[q] for q in bits(A[p]))==E[p] for p in range(111)),'A E=E')
    initial=E[:]+[r<<102 for r in E]+[1<<(204+h) for h in range(429)]
    z=replay2(initial,bulk)
    for offset in (0,111):
        for p in P:z[offset+p]^=xor(z[offset+F[j]] for j in bits(E[p]))
    want=[0]*651
    for j,p in enumerate(F):
        want[p]=1<<j;want[111+p]=(1<<j)|(1<<(102+j))
    for h in range(429):want[222+h]=1<<(204+h)
    need(z==want,'all633 independent scalar encoded columns,429 arbitrary dirty helpers,18 parity cells return0 overF2')
    # A real changed gate/control: remove one parity preparation input.
    badE=E[:];p=P[0];f=next(bits(E[p]));badE[p]^=1<<f
    need(badE!=E and any(xor(badE[p] for p in bits(r)) for r in R),'omitted actual parity ADD breaks kerR')
    return {'J_rows':J,'A_rows':A,'independent_scalar_columns':633,
            'arbitrary_dirty_helpers':429,'source_target_private_cells':18,
            'parity_preparation_ADDs_per_bank':sum(E[p].bit_count() for p in P),
            'scalar_identity':'At scalar frames, J E=E and A E=E; encoding both banks, cheap bulk and inverse encoding gives204 arbitrary data columns plus429 dirty identity columns, overF2.',
            'control':'Omitting one actual parity preparation ADD changes R E from0.'}

def projectors_and_routes(raw):
    I=eye(8);PP=[];rho=[];hashes=[]
    full=json.loads(gzip.decompress(FULL.read_bytes()))
    roots=full['lines'];gs={0:I};todo=[0]
    # Reconstruct the source geometry's exact Weyl BFS, rather than choose a
    # fresh Householder gauge. The frozen native lane hashes must agree.
    while todo:
        more=[]
        for p in todo:
            for q in range(120):
                ip=sum(x*y for x,y in zip(roots[p],roots[q]))//2
                if q in gs or abs(ip)!=1:continue
                v=[Q(x-y if ip==1 else x+y) for x,y in zip(roots[p],roots[q])]
                norm=sum(x*x for x in v)
                ref=[[Q(i==j)-2*v[i]*v[j]/norm for j in range(8)] for i in range(8)]
                gs[q]=mm(ref,gs[p]);more.append(q)
        todo=more
    need(len(gs)==120,'all120 source Weyl charts')
    for p,label in enumerate(raw['ports_geom']):
        root=raw['lines'][p]
        P=[[Q(x*y,4) for y in root] for x in root]
        G=gs[label]
        A=[r[1:] for r in G]
        need(mm(A,tr(A))==minus(I,P) and mm(tr(A),A)==eye(7),'actual source cap isometry')
        rr=[P[i]+A[i] for i in range(8)]+[r+[Q(0)]*7 for r in tr(A)]
        need(mm(rr,rr)==eye(15),'actual rho15 involution')
        ph=[P[i]+[Q(0)]*7 for i in range(8)]+[[Q(0)]*15 for _ in range(7)]
        need(mm(mm(rr,ph),rr)==ph,'actual rho fixes source entrance P')
        body=json.dumps([[str(x) for x in r] for r in rr],separators=(',',':')).encode()
        hashes.append(sha256(body).hexdigest());PP.append(P);rho.append(rr)
    ref=json.loads(NATIVE.read_bytes())
    need(hashes==ref['all111_actual_rho15_hashes'],'all111 exact rho hashes match native binding')
    return PP,rho,hashes

def entrance_failure(E,R,PP,rhohash):
    q=1009;x=[1<<i for i in range(8)]
    images=[]
    for P in PP:
        y=[sum(r[j]*x[j] for j in range(8)) for r in P]
        image=tuple(fmod(Q(x[i])-y[i],q) for i in range(8))+tuple(fmod(v,q) for v in y)
        need(any(image[8:]),'every actual Pp x nonzero')
        images.append(image)
    need(len(set(images))==111,'all111 source entrance delta images distinct')
    witnesses=[]
    for j in range(102):
        support=[p for p in range(111) if E[p]>>j&1]
        p=support[0];reader=next(a for a,r in enumerate(R) if r>>p&1)
        # At this unique address the coefficient is1, independent of all
        # other source ports. This is an operator witness, not augmentation.
        need(sum(bool(R[reader]>>s&1) and images[s]==images[p] for s in support)%2==1,
             'actual native entrance rejects scalar kerR code column')
        witnesses.append({'column':j,'port':p,'reader':reader,'output_ADDRESS':images[p]})
    return {'address_prime':q,'input_ADDRESS':x+[0]*8,
      'all111_projected_delta_images_distinct':True,'all102_scalar_code_columns_fail_native_RN':True,
      'witnesses':witnesses,
      'all_parameter_scope':'The separated-impulse argument excludes every nonzero scalar code column at commonZERO followed by the actual portwise source entrances Np=D_Pp, because every R column is nonzero. All rho_s,p fix Pp; adding only these port charts does not erase that native entrance.',
      'remaining_contract':'An operator-valued encoder such as diag(Np)^-1 E, with the required input/right gauges, must be implemented and charged. R E=0 alone is insufficient.'}

def target_reconstruction(P,F,E,raw,pruned,bulk,PP,rho):
    dims=[len(qb(raw['lines'][p] for p in frame)) for frame in raw['frames']]
    target_frames=pruned['start'][111:222][:]
    last={p:max(i for i,r in enumerate(bulk) if r[0]==0 and r[1]==111+p) for p in P}
    cuts={};I=eye(8)
    for i,r in enumerate(bulk):
        if r[0]==0 and 111<=r[1]<222:target_frames[r[1]-111]=r[3]
        for p in P:
            if i!=last[p]:continue
            U=raw['frames'][target_frames[p]]
            Uold=raw['frames'][r[2]]
            need(set(Uold)<=set(U) and 7-dims[r[2]]==r[4]>0,'actual last target MOVE is a strict nested native climb')
            need(dims[target_frames[p]]==7 and all(sum(x*y for x,y in zip(raw['lines'][q],raw['lines'][p]))==0 for q in U),
                 'dependent target final MOVE reaches its actual cap Kp')
            pairranks=[]
            for j in bits(E[p]):
                f=F[j];V=raw['frames'][target_frames[f]]
                joint=len(qb(raw['lines'][q] for q in set(U)|set(V)))
                d=2*joint-7-dims[target_frames[f]]
                need(d>0,'no surviving public target can supply dependent final cap at native0')
                pairranks.append({'public_port':f,'public_frame':target_frames[f],
                                  'required_coefficient_native_rank':d})
            cuts[p]={'bulk_record_index':i,'MOVE_record':r,'target_cap':target_frames[p],
                     'parity_support_size':len(pairranks),'all_required_coefficients_positive_native_rank':True,
                     'public_support':pairranks}
    # Exact rho-dependent ADDRESS matrix witnesses at the completed cap cut.
    witnesses=[]
    for p in P:
        f=F[next(bits(E[p]))]
        U=minus(I,PP[p]);V=minus(I,PP[f]);UV=mm(U,V)
        B=[[U[i][j]+V[i][j]-2*UV[i][j] for j in range(8)] for i in range(8)]
        need(len(qb(B))==2,'actual completed target coefficient native rank2')
        B15=[r+[Q(0)]*7 for r in B]+[[Q(0)]*15 for _ in range(7)]
        C=mm(mm(rho[p],B15),rho[f])
        need(len(qb(C))==2,'actual rho pullback retains positive native rank2')
        base=mm(rho[p],rho[f])
        a=next(a for a in range(15) if any(C[j][a] for j in range(15)))
        bottom=[C[j][a] for j in range(15)]
        top=[base[j][a]-bottom[j] for j in range(15)]
        need(any(fmod(x,1009) for x in bottom),'actual odd-field output escapes zero-second-half fiber')
        witnesses.append({'dependent_port':p,'public_port':f,'native_cross_rank':2,
             'ADDRESS_input_axis':a,'actual_rho_crossblock':ser(C),
             'ADDRESS_output':list(map(str,top+bottom)),
             'ADDRESS_output_mod1009':[fmod(x,1009) for x in top+bottom]})
    return {'last_MOVE_cuts':cuts,'rho_completed_cap_witnesses':witnesses,
      'operator_coefficient':'For the rho-adapted systematic kerR input code, each independent old target y_f would require M_pf=rho_p^-1 D_(Kp) D_(Kf)^-1 rho_f at the completed cap cut. Its cross block is rho_p^-1 (U+V-2UV) rho_f, U=Kp,V=Kf, and has rank2.',
      'general_identity':'For actual orthogonal projectors U,V, U+V-2UV=(I-2U)(V-U). Hence rank of the ADDRESS crossblock equals rank(V-U), and is zero iff U=V.',
      'fiber_proof':'Every allowed native0 rho ADDRESS adapter acts block-diagonally on the two ADDRESS halves, so it preserves the zero-second-half fiber. Any finite binary linear combination of such permutations preserves that fiber. The exact M_pf witness sends one delta outside it and cannot be such a combination.',
      'in_place_MOVE_proof':'Retaining the previous virtual value does not give a native0 update. For old/new projectors Uold<Unew=Kp and current public V, the required increment is (D_Unew+D_Uold)D_V. Its two permutation crossblocks satisfy Bnew!=0 and Bnew-Bold=(Unew-Uold)(I-2V)!=0. Choose a rational first-half input x outside the two proper kernels. The new delta is outside the zero-second-half fiber and differs from the old delta, so it does not cancel. No finite binary sum of native0 rho adapters can equal this increment. The same statement holds over sufficiently large odd ADDRESS fields avoiding the finitely many rational denominators/numerators.',
      'old_target_independence':'Bulk never reads a target. Sources and all429 dirty helpers therefore have zero coefficients on every arbitrary original target input. They cannot supply the missing old-target columns at this cut.',
      'conclusion':'The strategically selected dependent9 target arrays cannot have their final native MOVE operations replaced solely by same-frame ADDs or any finite native0 rho-addressed combinations of the surviving public target arrays in the unchanged bulk chronology.',
      'scope_limit':'Does not exclude a newly operator-valued input code with paid native factors, a changed target-reading word, new intermediate queries, query sharing with a different chronology, or a different public/private contract.'}

def partition(n,cap):
    out=[]
    while n:
        r=min(cap,n);out.append(r);n-=r
    return out
def invoice(H,L):
    B=(L-1)//2;m=1+7*L;V=102
    stock=Q((L-1)*V);hist=Counter({r:Q(L*c) for r,c in H.items()})
    slots=[14*(B-1)] if B>1 else []
    for j in range(1,B):
        slots.extend([14*j,7])
        if B-j-1:slots.append(14*(B-j-1))
    cap=isqrt((m*m-1)//2)
    for s in slots:
        for r in partition(s,cap):hist[r]+=2*V
    q=m//8;pad=m-8*q;helperstock=Q(429*L,q);stock+=helperstock
    for r in partition(pad,cap):hist[r]+=helperstock
    mass=sum(r*c for r,c in hist.items());D=m*stock-mass
    need(D==102*(L-1)-126*L==-24*L-102,'complete optimistic coded invoice')
    return {'L':L,'m':m,'public_fields':102*(L-1),'public_parity_cells_per_active_call':18,
            'helper_stock_relaxation':str(helperstock),'W':str(stock),'H':{r:str(c) for r,c in sorted(hist.items())},
            'rank_mass':str(mass),'D':str(D),'private_parity_native_mass_per_call':126,
            'zero_exponent_verdict':'FAIL_ALREADY_EXCEEDS_STOCK',
            'targets':{'0.002':'FAIL_ALL_POSITIVE_EXPONENTS','0.003':'FAIL_ALL_POSITIVE_EXPONENTS','0.005':'FAIL_ALL_POSITIVE_EXPONENTS'}}

def receipt():
    raw,pruned,R,K,bulk,H=load()
    P,F,E,rr,prefix=systematic(R,bulk)
    scalar=scalar_certificate(P,F,E,R,K,bulk)
    PP,rho,rhash=projectors_and_routes(raw)
    moved=sum(r[4] for r in bulk if r[0]==0 and (r[1] in P or 111<=r[1]<222 and r[1]-111 in P))
    need(moved==126,'all selected nine source and nine target MOVE paths cost126')
    return {'status':'PASS_KERR102_SCALAR_CODE_NATIVE_RECONSTRUCTION_REJECTION',
      'scientific_pin':PIN,'no_new_kappa':True,
      'sources':{str(p):sha256(p.read_bytes()).hexdigest() for p in (RAW,PRUNED,COMP,NATIVE,FULL,GEOMETRY)},
      'dependent_ports':P,'public_ports':F,'encoder_rows_102':E,'systematic_paritycheck_rows_111':rr,
      'pivot_strategy':'Minimum-weight column-matroid basis for actual source+target MOVE event count; every such basis has native mass126 for its9 source and9 target ports.',
      'greedy_basis_certificate':prefix,'selected_parity_port_MOVE_mass':moved,
      'scalar_code':scalar,'source_entrance_failure':entrance_failure(E,R,PP,rhash),
      'target_native_reconstruction':target_reconstruction(P,F,E,raw,pruned,bulk,PP,rho),
      'optimistic_complete_invoices':[invoice(H,L) for L in (3,5,7,9,11,13,17)],
      'complete_mass_proof':'m=1+7L, W_public=102(L-1). Cheap R429 bulk has mass4986=2*111*7+429*8. Its18 parity fields cost126/call beyond2*102 useful public progress. Exact fractional helper banks and pads cancel in mass-versus-stock. Therefore D=102(L-1)-126L=-24L-102<0 before encoder/decoder, zero preparation/cleanup, rho/native entrance or primitive costs. Every contracting positive-beta child moment strictly exceeds its zero-beta mass, so all positive supplier exponents fail for this invoice.',
      'unresolved':['No operator-valued code/cleanup compiler eliminating the126/call cost is constructed.',
        'The full encoded scalar gate calculation is overF2; no exact integer-zero private cleanup is claimed.',
        'Rounded precision, whole-helper integral owners and physical tape contracts are not supplied; the favorable invoice already fails without them.'],
      'attribution':'Frozen R429 and full compensation sources/root native BIT lane supply the original circuit, actual R/K and rho charts. This lane constructs the systematic102-to111 code, its complete optimistic invoice and actual native source/target reconstruction witnesses.'}

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--write',action='store_true');args=ap.parse_args()
    out=json.loads(json.dumps(receipt()))
    p=HERE/'KER-CODE-NATIVE-REJECTION.json'
    if args.write:p.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    else:need(json.loads(p.read_bytes())==out,'saved coded boundary receipt differs')
    print(out['status'])
    print('dependent9',out['dependent_ports'],'parity ADDs/bank',out['scalar_code']['parity_preparation_ADDs_per_bank'])
    print('633 scalar columns;102 actual source-entrance failures;9 final target MOVE/rho witnesses; D=-24L-102.')

if __name__=='__main__':main()
