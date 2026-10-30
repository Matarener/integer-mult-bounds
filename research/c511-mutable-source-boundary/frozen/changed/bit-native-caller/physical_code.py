#!/usr/bin/env python3
"""Actual repaired R429 source code, routed conjugacy and native-cut tests.

The exact native intertwiner is constructive; its simplest use loses fresh
coverage. The finite orbit tests reject finite-order shortcuts, not all callers.
Apache-2.0. Prepared with substantial OpenAI Codex assistance.
"""
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import argparse
import gzip
import json

HERE=Path(__file__).resolve().parent
BASE=Path('/Users/ross/git/math')
RAW=BASE/'integer-mult-bounds/research/bit-r438-transport-rehost/words/r438-t154.json.gz'
FULL=BASE/'integer-mult-bounds/research/e8-bit-carrier-skeleton/data/bit/bitE8-r865.json.gz'
GEOMETRY=FULL.parents[2]/'code/nine/geometry.py'
OLD=BASE/'.research-automation/runs/kappa-major-20261018T1330Z'
COMP=OLD/'bit-endpoint/BIT-FULL-COMPENSATION.json'
CODE=BASE/'.research-automation/runs/kappa-3605-successor-20261018T0940Z/major-frontier/root-pruned-code/BIT-PRUNED-WORD.json.gz'

def need(b,m):
    if not b:raise ValueError(m)
def eye(n):return [[Q(i==j)for j in range(n)]for i in range(n)]
def tr(a):return list(map(list,zip(*a)))
def mm(a,b):return [[sum(x*y for x,y in zip(r,c))for c in zip(*b)]for r in a]
def serial(a):return [[str(x)for x in r]for r in a]
def bits(x):
    while x:
        z=x&-x;yield z.bit_length()-1;x^=z
def bxor(xs):
    z=0
    for x in xs:z^=x
    return z
def mul2(a,b):return [bxor(b[j]for j in bits(x))for x in a]
def rank2(rows):
    b={}
    for x in rows:
        while x:
            j=x.bit_length()-1
            if j in b:x^=b[j]
            else:b[j]=x;break
    return len(b)

def actual_routes(w):
    full=json.loads(gzip.decompress(FULL.read_bytes()))
    roots=full['lines'];I=eye(8);gs={0:I};todo=[0]
    while todo:
        more=[]
        for p in todo:
            for q in range(120):
                ip=sum(x*y for x,y in zip(roots[p],roots[q]))//2
                if q in gs or abs(ip)!=1:continue
                d=[Q(x-y if ip==1 else x+y)for x,y in zip(roots[p],roots[q])]
                norm=sum(x*x for x in d)
                ref=[[Q(i==j)-2*d[i]*d[j]/norm for j in range(8)]for i in range(8)]
                gs[q]=mm(ref,gs[p]);more.append(q)
        todo=more
    need(len(gs)==120,'actual upstream Weyl route graph')
    rhos=[];projectors=[]
    for p,label in enumerate(w['ports_geom']):
        g=gs[label];A=[r[1:]for r in g];q=w['lines'][p]
        P=[[Q(x*y,4)for y in q]for x in q]
        K=[[I[i][j]-P[i][j]for j in range(8)]for i in range(8)]
        need(mm(A,tr(A))==K and mm(tr(A),A)==eye(7),'actual cap isometry')
        rho=[P[i]+A[i]for i in range(8)]+[r+[Q(0)]*7 for r in tr(A)]
        need(tr(rho)==rho and mm(rho,rho)==eye(15),'actual rho involution')
        rhos.append(rho);projectors.append(P)
    return rhos,projectors,full

def embed(rho,stage):
    # common8, old fresh7, new fresh7; stage0/1 chooses the fresh block.
    axes=list(range(8))+list(range(8+7*stage,15+7*stage))
    out=eye(22)
    for i,a in enumerate(axes):
        for j,b in enumerate(axes):out[a][b]=rho[i][j]
    return out

def commutant_rank(rhos,edges,prime=101):
    basis={};n=15;progress=[]
    for p,q in edges:
        M=mm(rhos[p],rhos[q])
        M=[[x.numerator*pow(x.denominator,-1,prime)%prime for x in row]for row in M]
        for i in range(n):
            for j in range(n):
                v=[0]*(n*n)
                for k in range(n):
                    v[i*n+k]=(v[i*n+k]+M[k][j])%prime
                    v[k*n+j]=(v[k*n+j]-M[i][k])%prime
                for k,old in sorted(basis.items()):
                    f=v[k]
                    if f:v=[(x-f*y)%prime for x,y in zip(v,old)]
                k=next((k for k,x in enumerate(v)if x),None)
                if k is not None:
                    f=pow(v[k],-1,prime);basis[k]=[(x*f)%prime for x in v]
        progress.append(len(basis))
    return len(basis),progress

def orbit_screen(A,w,full):
    roots=[tuple(sign*x for x in q)for q in full['lines']for sign in(1,-1)]
    indices={q:i for i,q in enumerate(roots)};perms=[]
    for q in w['lines']:
        perm=[]
        for r in roots:
            dot=sum(x*y for x,y in zip(q,r));need(not dot%2,'root integral pairing')
            rr=tuple(x-(dot//2)*y for x,y in zip(r,q))
            need(rr in indices,'signed root orbit reflection closure')
            perm.append(indices[rr])
        need(all(perm[perm[i]]==i for i in range(240)),'actual native N involution')
        perms.append(perm)
    def N(v):
        return [bxor(1<<p[i]for i in bits(x))for x,p in zip(v,perms)]
    def code(v):return [bxor(v[j]for j in bits(row))for row in A]
    # F swaps head/tail. At plus-coordinate0 this negates the minus root.
    neg=[indices[tuple(-x for x in r)]for r in roots]
    def F(v):return [bxor(1<<neg[i]for i in bits(x))for x in v]
    def plus(a,b):return [x^y for x,y in zip(a,b)]
    x=[1]+[0]*110;y=[0,1<<2]+[0]*109
    need(F(code(x))==code(F(x)) and F(N(x))==N(F(x)),'actual F commutation')
    G=lambda v:F(N(v))
    a=lambda v:N(code(N(v)))
    physical_source=F(code(N(x)))
    physical_target=plus(G(y),G(code(N(x))))
    factored_source=G(a(x))
    factored_target=G(plus(y,N(a(x))))
    need((physical_source,physical_target)==(factored_source,factored_target),'actual local G F_N diag(NAN,I) factor')
    need(G(code(x))!=physical_source,'wrong source precode A rather thanNAN rejected')
    start=x[:];z=start;records=[];returns=[]
    for k in range(1,225):
        z=code(N(z))
        if z==start:returns.append(k)
        if k in(2,4,7,14,28,56,112,224):
            packed=json.dumps([hex(v)for v in z],separators=(',',':')).encode()
            records.append({'power':k,'VALUE_weight':sum(v.bit_count()for v in z),
                'output_sha256':sha256(packed).hexdigest(),'returns_input':z==start})
    need(not returns,'no AN orbit period at most224 on explicit input')
    return {'domain':'240 signed E8 root minus-addresses, plus-address0; exact dyadic addresses (head=root/2,tail=-root/2), also valid modulo101.',
        'input':'VALUE delta at physical port0 and first positive full E8 root.',
        'all111_reflection_orbit_columns_checked':111*240,
        'AN_periods_at_most224':returns,'saved_powers':records,
        'actual_local_factor_and_wrong_precode_control':True}

def receipt():
    need(sha256(RAW.read_bytes()).hexdigest()=='a353999bceac4ac957f540adfd3e5f8768297138b27132eeb83332e2ea4b1022','raw pin')
    need(sha256(CODE.read_bytes()).hexdigest()=='1a6841fccba51fa922993c77b4b296e659c2c538252e5e06113d0438c5edb870','coded word pin')
    w=json.loads(gzip.decompress(RAW.read_bytes()));c=json.loads(COMP.read_bytes())
    R,K=c['R'],c['K'];W=K[:];W[:3]=[0]*3
    I=[1<<p for p in range(111)]
    J=[i^r for i,r in zip(I,mul2(K,R))]
    A=[i^r for i,r in zip(I,mul2(W,R))]
    need(rank2(J)==108 and rank2(A)==111,'singular bulk J versus repaired invertibleA')
    prog=json.loads(gzip.decompress(CODE.read_bytes()));literal=I[:];count=0
    for op,d,s,coef,frame,phase in prog['records']:
        if op==1 and phase in(21,22,23,24):
            need(d<111 and s<111 and frame==1,'actual FULL source-code primitive')
            if coef&1:literal[d]^=literal[s]
            count+=1
    need(literal==A and count==1499,'actual source code matches I+WR')
    powers=[];P=I
    for k in range(1,29):
        P=mul2(A,P)
        if k<28:need(P!=I and any(row&~(1<<p)for p,row in enumerate(P)),'no nontrivial diagonal scalar power')
        if k in(1,2,4,7,14,28):
            powers.append({'power':k,'rank_Apower_minus_I':rank2([x^y for x,y in zip(P,I)]),
                'offdiagonal_rows':sum(bool(row&~(1<<p))for p,row in enumerate(P))})
    need(P==I,'exact repaired code order28')
    rhos,projectors,full=actual_routes(w)
    edges=[(3,q)for q in(0,1,2,4,5)]
    need(all(A[p]>>q&1 for p,q in edges),'actual source-code commutant edges')
    cr,cp=commutant_rank(rhos,edges)
    need(cr==224,'mod101 rank224 gives rational commutant dimension1')
    # The identity is in the rational commutant, so its dimension is exactly1,
    # not merely at most1. A common native projector commuting these couplings
    # is therefore scalar, and idempotence leaves onlyZERO/FULL.
    identity_coeff=[int(i==j)for i in range(15)for j in range(15)]
    need(sum(identity_coeff)==15,'nonzero exact identity commutant control')
    Hhash=[];coverage=[]
    for p,rho in enumerate(rhos):
        rs,rt=embed(rho,0),embed(rho,1);H=mm(rt,rs)
        # H maps every old fresh basis column into the new fresh subspace.
        need(all(H[i][j]==int(i==j+7)for i in range(22)for j in range(8,15)),
            'actual H sends completed old fresh exactly to future fresh')
        P0=[[projectors[p][i][j]if i<8 and j<8 else Q(0)for j in range(22)]for i in range(22)]
        need(mm(H,P0)==mm(P0,H),'actual H commutes common N_p projector')
        Hhash.append(sha256(json.dumps(serial(H),separators=(',',':')).encode()).hexdigest())
    for p,q in edges:
        rs_p,rs_q=embed(rhos[p],0),embed(rhos[q],0)
        rt_p,rt_q=embed(rhos[p],1),embed(rhos[q],1)
        hp,hq=mm(rt_p,rs_p),mm(rt_q,rs_q)
        need(mm(hp,mm(rs_p,rs_q))==mm(mm(rt_p,rt_q),hq),
            'actual all-input ADDRESS intertwiner coefficient identity')
    M=mm(rhos[3],rhos[0])
    witness=next((i,j,M[i][j])for i in range(8,15)for j in range(8)if M[i][j])
    return {'status':'PASS_PHYSICAL_REPAIRED_A_INTERTWINER_AND_EXPLICIT_COVERAGE_DEBT',
        'scientific_pin':'20ecf2891d80b5acf18d980b2164fb44ea7faa90','no_new_kappa':True,
        'sources':{str(p):sha256(p.read_bytes()).hexdigest()for p in(RAW,FULL,GEOMETRY,COMP,CODE)},
        'R':R,'K':K,'W':W,'A':A,'J_rank':108,'A_rank':111,'literal_source_code_ADDs':1499,
        'A_order':28,'power_diagnostics':powers,
        'native_factor':'Let F be actual local FULL, N=diag(D_Pp), G=F N, a=N A N. Since F commutes scalar A and N, repaired local Fphys=diag(G,G) F_N diag(a,I). It has source A G and cross G A N. This statement uses the same actual rho conjugacy on all factors at later stages.',
        'routed_source_code':'A_s[p,q]=A[p,q] times VALUE push(rho_s,p rho_s,q). These exact rho_s,p are reconstructed from upstream geometry.py Weyl BFS, not chosen fresh gauges.',
        'all111_actual_rho15':[[[str(x)for x in row]for row in rho]for rho in rhos],
        'intertwiner':'H_p=rho_t,p rho_s,p: H A_s H^-1=A_t, H commutes N_p, and H(E_s)=E_t. H is an orthogonal ADDRESS transform; all its access and head movement remain paid.',
        'all111_intertwiner_H_sha256':Hhash,
        'coverage_debt':'H^-1 D_Et H D_Es=I on arbitrary VALUE functions, while the desired D_(Es+Et) has native rank14. The naive alignment/query/unwind word cancels its two rank7 fresh advances. This prices that word only.',
        'uniform_source_frame_commutant':{'active_dimension':15,'matrix_unknowns':225,
            'field_for_rank_lower_certificate':101,'actual_A_edges':edges,
            'modular_constraint_rank':224,'rank_progress':cp,'rational_commutant_dimension':1,
            'consequence':'A common orthogonal projector Q commuting the actual source-code coupling maps is scalar, hence Q=0 orI15. The routed source code cannot be treated as a code preserving an unchanged intermediate common native frame.'},
        'actual_future_fiber_witness':{'output_port':3,'input_port':0,'row':witness[0],
            'column':witness[1],'coefficient':str(witness[2])},
        'AN_native_orbit_screen':orbit_screen(A,w,full),
        'exact_commutator_fact':'For a scalar port code T, [T,N]_(p,q)=T_pq(D_Pq-D_Pp). Distinct actual E8 lines give distinct native permutations. Every A^k,1<=k<28, has an offdiagonal entry, so none commutes N. Low rank(A^14-I)=2 does not make its routed native coefficient a rank2 query.',
        'open_next_question':'Construct a caller using genuinely changing/port-dependent native frames or shared operator-valued readers so H coverage loss is compensated inside the actual word. No such positive complete word is supplied here.',
        'limits':['No general obstruction for arbitrary operator-valued or nonlinear callers.',
            'No chronological helper owners, rounded errors, source/tape bill, full recurrence or new conditional exponent.',
            'The AN test is a finite exact counterexample to periods<=224, not a proof of infinite order or a universal word lower bound.']}

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--write',action='store_true');args=ap.parse_args()
    out=json.loads(json.dumps(receipt()));path=HERE/'PHYSICAL-CODE.json'
    if args.write:path.write_text(json.dumps(out,sort_keys=True,indent=2)+'\n')
    else:need(json.loads(path.read_bytes())==out,'stored physical code receipt differs')
    print(out['status']);print('literal A order28; actual rho intertwiner; native coverage debt14; commutant dimension1; AN periods<=224 rejected')
if __name__=='__main__':main()
