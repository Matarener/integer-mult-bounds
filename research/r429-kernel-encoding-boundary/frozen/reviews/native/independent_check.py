#!/usr/bin/env python3
"""Independent dense F2 replay and rational native-boundary witnesses.

No producer mathematics imported. Standard library only; Apache-2.0.
Substantial OpenAI Codex assistance.
"""
from collections import Counter, deque
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import argparse, gzip, json

ROOT=Path('/Users/ross/git/math')
HERE=Path(__file__).resolve().parent
RUN=ROOT/'.research-automation/runs/kappa-changed-endpoints-20261019T0153Z'
OLD=ROOT/'.research-automation/runs/kappa-3605-successor-20261018T0940Z/major-frontier'
MAJOR=ROOT/'.research-automation/runs/kappa-major-20261018T1330Z'

def need(ok,message):
    if not ok:raise ValueError(message)
def ident(n):return [[Q(i==j) for j in range(n)] for i in range(n)]
def transpose(a):return list(map(list,zip(*a)))
def mm(a,b):return [[sum(x*y for x,y in zip(r,c)) for c in zip(*b)] for r in a]
def sub(a,b):return [[x-y for x,y in zip(r,s)] for r,s in zip(a,b)]
def scaled(a,k):return [[k*x for x in r] for r in a]
def canonical(x):return json.dumps(x,sort_keys=True,separators=(',',':')).encode()
def ser(a):return [[str(x) for x in r] for r in a]
def bits(x):return [j for j in range(x.bit_length()) if x>>j&1]
def packed(row):return sum(int(x)<<j for j,x in enumerate(row))
def rank(a,mod=None):
    if not a:return 0
    a=[list(r) if mod else list(map(Q,r)) for r in a];k=0
    for j in range(len(a[0])):
        p=next((p for p in range(k,len(a)) if a[p][j]%mod),None) if mod else next((p for p in range(k,len(a)) if a[p][j]),None)
        if p is None:continue
        a[k],a[p]=a[p],a[k]
        v=pow(int(a[k][j]),-1,mod) if mod else 1/a[k][j]
        a[k]=[(x*v)%mod if mod else x*v for x in a[k]]
        for p in range(k+1,len(a)):
            v=a[p][j]
            if v:a[p]=[(x-v*y)%mod if mod else x-v*y for x,y in zip(a[p],a[k])]
        k+=1
        if k==len(a[0]):break
    return k
def inverse_det(a):
    n=len(a);m=[list(map(Q,r))+s for r,s in zip(a,ident(n))];det=Q(1)
    for j in range(n):
        p=next(p for p in range(j,n) if m[p][j])
        if p!=j:m[p],m[j]=m[j],m[p];det=-det
        v=m[j][j];det*=v;m[j]=[x/v for x in m[j]]
        for p in range(n):
            if p!=j:
                v=m[p][j]
                if v:m[p]=[x-v*y for x,y in zip(m[p],m[j])]
    return [r[n:] for r in m],det
def prime_factors(n):
    out=[];n=abs(n);p=2
    while p*p<=n:
        if n%p==0:
            out.append(p)
            while n%p==0:n//=p
        p+=1
    if n>1:out.append(n)
    return out
def modq(x,q=1009):
    x=Q(x);return x.numerator*pow(x.denominator,-1,q)%q
def matvec(a,v,q=None):
    out=[sum(x*y for x,y in zip(r,v)) for r in a]
    return [modq(x,q) for x in out] if q else out
def cross(u,v):return sub(sub(u,scaled(v,-1)),scaled(mm(u,v),2))
def embed(a):return [[a[i][j] if i<8 and j<8 else Q(0) for j in range(15)] for i in range(15)]

def routes(raw,full):
    roots=full['lines'];parents={0:None};queue=deque([0])
    while queue:
        p=queue.popleft()
        for q in range(120):
            twice=sum(x*y for x,y in zip(roots[p],roots[q]))
            if q not in parents and abs(twice)==2:
                parents[q]=(p,twice//2);queue.append(q)
    need(len(parents)==120,'complete deterministic Weyl BFS')
    gs=[]
    for q in range(120):
        path=[];at=q
        while parents[at] is not None:
            p,sgn=parents[at];path.append((p,at,sgn));at=p
        g=ident(8)
        for p,t,sgn in reversed(path):
            v=[x-sgn*y for x,y in zip(roots[p],roots[t])];den=sum(x*x for x in v)
            reflection=[[Q(i==j)-Q(2*v[i]*v[j],den) for j in range(8)] for i in range(8)]
            g=mm(reflection,g)
        need(mm(transpose(g),g)==ident(8),'actual Weyl orthogonal chart')
        gs.append(g)
    rhos=[];lines=[];hashes=[]
    for p,q in enumerate(raw['lines']):
        g=gs[raw['ports_geom'][p]];A=[row[1:] for row in g]
        P=[[Q(x*y,4) for y in q] for x in q]
        need(mm(A,transpose(A))==sub(ident(8),P) and mm(transpose(A),A)==ident(7),'actual cap isometry')
        rho=[P[i]+A[i] for i in range(8)]+[row+[Q(0)]*7 for row in transpose(A)]
        need(all(x.denominator & (x.denominator-1)==0 for row in rho for x in row),'actual rho matrices have only dyadic denominators')
        need(rho==transpose(rho) and mm(rho,rho)==ident(15),'actual rho involution')
        need(mm(mm(rho,embed(P)),rho)==embed(P),'rho fixes native entrance')
        hashes.append(sha256(json.dumps(ser(rho),separators=(',',':')).encode()).hexdigest())
        rhos.append(rho);lines.append(P)
    return rhos,lines,hashes

def binary_rows(n,m):return [bytearray(int(i==j) for j in range(m)) for i in range(n)]
def add(row,other):return bytearray(x^y for x,y in zip(row,other))
def scalar_replay(P,F,E,bulk,omit=False):
    state=[bytearray(633) for _ in range(651)]
    for j,p in enumerate(F):state[p][j]=1;state[111+p][102+j]=1
    for h in range(429):state[222+h][204+h]=1
    entrance=[r[:] for r in state];gates=[]
    def gate(d,s):
        state[d]=add(state[d],state[s]);gates.append((d,s))
    omitted=None
    for offset in (0,111):
        for p in P:
            for j in bits(E[p]):
                if omit and omitted is None:omitted=[offset+p,F[j]];continue
                gate(offset+p,offset+F[j])
    # All preparations commute: their targets are dependent cells and their
    # sources are public cells. Check the reversed ordering as a positive control.
    reverse_preparation=[r[:] for r in entrance]
    for d,s in reversed(gates):reverse_preparation[d]=add(reverse_preparation[d],reverse_preparation[s])
    need(reverse_preparation==state,'equivalent reversed preparation order')
    for op,d,s,c,f,phase in bulk:
        if op==1 and c%2:gate(d,s)
    for offset in (0,111):
        for p in P:
            for j in bits(E[p]):gate(offset+p,offset+F[j])
    expected=[bytearray(633) for _ in range(651)]
    for j,p in enumerate(F):expected[p][j]=1;expected[111+p][j]=expected[111+p][102+j]=1
    for h in range(429):expected[222+h][204+h]=1
    differences=[[i,j] for i,(r,s) in enumerate(zip(state,expected)) for j,(x,y) in enumerate(zip(r,s)) if x!=y]
    if omit:need(differences,'omitted preparation gate must break exact endpoint')
    else:need(not differences,'complete633-column binary endpoint including18 zero parities')
    digest=sha256(b''.join(state)).hexdigest()
    for d,s in reversed(gates):state[d]=add(state[d],state[s])
    need(state==entrance,'literal inverse returns all633 entrance columns and18 parity zeros')
    return {'all_entries_compared':651*633,'matrix_sha256':digest,'literal_binary_inverse':True,
            'equivalent_preparation_order':True,
            'different_entries':len(differences),'first_difference':differences[0] if differences else None,
            'omitted_gate':omitted}

def systematic(raw,bulk):
    rows=binary_rows(660,111)
    for phase in ('D','A'):
        for frame,d,ss in raw[phase]:
            for s in ss:rows[d]=add(rows[d],rows[s])
    R=[rows[h] for h in raw['ret']]
    need(rank(R,2)==9,'actual R has binary rank9')
    cols=transpose(R);weights=Counter(r[1]%111 for r in bulk if r[0]==0 and r[1]<222)
    P=[];chosen=[]
    for p in sorted(range(111),key=lambda p:(weights[p],p)):
        if rank(chosen+[cols[p]],2)>len(chosen):P.append(p);chosen.append(cols[p])
        if len(P)==9:break
    rr=[r[:] for r in R]
    for j,p in enumerate(P):
        k=next(k for k in range(j,9) if rr[k][p]);rr[k],rr[j]=rr[j],rr[k]
        for i in range(9):
            if i!=j and rr[i][p]:rr[i]=add(rr[i],rr[j])
    F=[p for p in range(111) if p not in P];E=[0]*111
    for j,p in enumerate(F):E[p]=1<<j
    for i,p in enumerate(P):E[p]=sum(rr[i][f]<<j for j,f in enumerate(F))
    denseE=[[int(e>>j&1) for j in range(102)] for e in E]
    need(rank(denseE,2)==102 and all(x%2==0 for row in mm(R,denseE) for x in row),'systematic full rank102 and RE0')
    need(all(any(c) for c in cols),'every R column nonzero')
    return R,P,F,E,rr,weights

def native_checks(raw,pruned,bulk,R,P,F,E,rhos,Ps,saved):
    # Integer root bases and their Gram determinants certify specialization.
    cache={};basis_evidence={};bad_primes={2}
    def projection(ports):
        key=tuple(sorted(set(ports)))
        if key in cache:return cache[key]
        selected=[];basis=[]
        for p in key:
            row=raw['lines'][p]
            if rank(basis+[row])>len(basis):basis.append(row);selected.append(p)
        if basis:
            gram=mm(basis,transpose(basis));inv,det=inverse_det(gram)
            need(det.denominator==1 and det>0,'positive integral Gram determinant')
            answer=mm(mm(transpose(basis),inv),basis)
        else:det=Q(1);answer=[[Q(0)]*8 for _ in range(8)]
        need(mm(answer,answer)==answer and answer==transpose(answer),'rational orthogonal frame projector')
        bad_primes.update(prime_factors(det.numerator))
        basis_evidence[','.join(map(str,key))]={'basis_ports':selected,'dimension':len(basis),'Gram_determinant':int(det)}
        cache[key]=(answer,len(basis));return cache[key]
    q=1009;need(all(q%d for d in range(2,32)),'1009 is prime by complete trial division')
    x=[1<<i for i in range(8)];images=[]
    for matrix in Ps:
        y=matvec(matrix,x);image=[modq(Q(a)-b) for a,b in zip(x,y)]+[modq(v) for v in y]
        need(any(image[8:]),'each actual native line image nonzero');images.append(image)
    need(len({tuple(v) for v in images})==111,'all111 source entrance impulse images distinct')
    source_witnesses=[]
    for j in range(102):
        support=[p for p,e in enumerate(E) if e>>j&1];p=support[0];reader=next(i for i,r in enumerate(R) if r[p])
        need(sum(R[reader][s] for s in support if images[s]==images[p])%2==1,'actual source code column rejected')
        source_witnesses.append({'column':j,'port':p,'reader':reader,'output_ADDRESS':images[p]})
    need(source_witnesses==saved['source_entrance_failure']['witnesses'],'all102 historical source witnesses independently matched')
    frames=pruned['start'][111:222][:]
    lasts={p:max(i for i,r in enumerate(bulk) if r[0]==0 and r[1]==111+p) for p in P}
    all_pairs=[];witnesses=[];cuts={};completed=[];rank_hist=Counter()
    for at,r in enumerate(bulk):
        op,d,s,c,tariff,phase=r
        if op==0 and 111<=d<222:
            need(frames[d-111]==s,'actual target frame chronology');frames[d-111]=c
        if op!=0 or d-111 not in P or at!=lasts.get(d-111):continue
        p=d-111;U,du=projection(raw['frames'][c]);Uold,do=projection(raw['frames'][s])
        need(du==7 and du-do==tariff>0 and set(raw['frames'][s])<=set(raw['frames'][c]),'strict actual last target climb')
        need(U==sub(ident(8),Ps[p]),'actual last target reaches exact cap')
        rank_rows=[]
        for j in bits(E[p]):
            f=F[j];V,dv=projection(raw['frames'][frames[f]])
            _,joint=projection(raw['frames'][c]+raw['frames'][frames[f]])
            Bnew=cross(U,V);Bold=cross(Uold,V);delta=sub(Bnew,Bold)
            need(Bnew==mm(sub(ident(8),scaled(U,2)),sub(V,U)),'crossblock factorization')
            need(delta==mm(sub(U,Uold),sub(ident(8),scaled(V,2))),'retained-old increment crossblock difference')
            actual_rank=rank(Bnew);difference_rank=rank(delta)
            need(actual_rank==2*joint-du-dv>0 and difference_rank==du-do>0,'all required rational ranks and strict update ranks')
            need(rank([[modq(v) for v in row] for row in Bnew],q)==actual_rank,'actual F1009 cross rank')
            need(rank([[modq(v) for v in row] for row in delta],q)==difference_rank,'actual F1009 update rank')
            rank_hist[actual_rank]+=1
            rank_rows.append({'public_port':f,'public_frame':frames[f],'required_coefficient_native_rank':actual_rank})
            if dv==7:need(joint==8,'equal-dimension actual caps remain distinct under every permitted specialization')
            all_pairs.append({'dependent':p,'public':f,'frame':frames[f],'dimension_new':du,'dimension_old':do,
                              'dimension_public':dv,'dimension_joint':joint,'rank_new':actual_rank,
                              'rank_increment_difference':difference_rank})
            if j!=bits(E[p])[0]:continue
            C=mm(mm(rhos[p],embed(Bnew)),rhos[f]);C0=mm(mm(rhos[p],embed(Bold)),rhos[f]);D=sub(C,C0)
            need(rank(C)==actual_rank and rank(D)==difference_rank,'actual rho conjugates preserve both ranks')
            units=[[int(i==k) for i in range(15)] for k in range(15)]
            u=next(w for w in units if any(matvec(C,w,q)))
            if not any(matvec(D,u,q)):
                v=next(w for w in units if any(matvec(D,w,q)))
                u=v if any(matvec(C,v,q)) else [a+b for a,b in zip(u,v)]
            newtail=matvec(C,u,q);oldtail=matvec(C0,u,q);base=matvec(mm(rhos[p],rhos[f]),u,q)
            new=[(a-b)%q for a,b in zip(base,newtail)]+newtail
            old=[(a-b)%q for a,b in zip(base,oldtail)]+oldtail
            need(any(newtail) and new!=old,'retained-old update produces uncancelled delta outside zero-tail fiber')
            witnesses.append({'dependent_port':p,'public_port':f,'bulk_record_index':at,'public_frame':frames[f],
                              'MOVE_record':r,'rank_new':actual_rank,'rank_difference':difference_rank,
                              'input_ADDRESS':u+[0]*15,'new_ADDRESS':new,'old_ADDRESS':old,
                              'new_rho_crossblock':ser(C),'old_rho_crossblock':ser(C0)})
        entry={'bulk_record_index':at,'MOVE_record':r,'target_cap':c,'parity_support_size':len(rank_rows),
               'all_required_coefficients_positive_native_rank':True,'public_support':rank_rows}
        need(entry==saved['target_native_reconstruction']['last_MOVE_cuts'][str(p)],'complete historical last cut support independently matched')
        cuts[str(p)]=entry
    need(len(all_pairs)==470 and len(witnesses)==9 and len(cuts)==9,'complete target coverage')
    for p in P:
        f=F[bits(E[p])[0]];B=cross(sub(ident(8),Ps[p]),sub(ident(8),Ps[f]));C=mm(mm(rhos[p],embed(B)),rhos[f])
        need(rank(B)==rank(C)==2,'all nine completed-cap crossblocks have exact rank2')
        base=mm(rhos[p],rhos[f]);a=next(a for a in range(15) if any(C[i][a] for i in range(15)))
        bottom=[C[i][a] for i in range(15)];top=[base[i][a]-bottom[i] for i in range(15)]
        completed.append({'dependent_port':p,'public_port':f,'native_cross_rank':2,'ADDRESS_input_axis':a,
                          'actual_rho_crossblock':ser(C),'ADDRESS_output':list(map(str,top+bottom)),
                          'ADDRESS_output_mod1009':[modq(v) for v in top+bottom]})
    need(completed==saved['target_native_reconstruction']['rho_completed_cap_witnesses'],'complete historical completed-cap witnesses independently matched')
    actual_by_port={w['dependent_port']:w for w in witnesses}
    need(all(w['actual_rho_crossblock']==actual_by_port[w['dependent_port']]['new_rho_crossblock'] for w in completed),
         'all nine selected completed-cap crossblocks also equal the actual last-cut crossblocks')
    need(1009 not in bad_primes,'F1009 avoids every required Gram denominator and rank guard')
    # Controls change the mathematical premises, not just receipt metadata.
    need(cross(Ps[0],Ps[0])==[[0]*8 for _ in range(8)],'equal-frame control has no native crossblock')
    need(sub(cross(Ps[0],Ps[1]),cross(Ps[0],Ps[1]))==[[0]*8 for _ in range(8)],'no-change MOVE control has zero update')
    no_entrance=[tuple(x+[0]*8)]*111
    need(len(set(no_entrance))==1 and all(sum(R[a][p]*(E[p]>>j&1) for p in range(111))%2==0 for a in range(9) for j in range(102)),
         'omitting actual entrances restores every scalar source cancellation')
    return {'source_prime':q,'source_input_ADDRESS':x+[0]*8,'source_images':images,'source_witnesses':source_witnesses,
            'last_cuts':cuts,'all470_pair_ranks':all_pairs,'rank_histogram':dict(rank_hist),
            'actual_last_cut_update_witnesses':witnesses,'completed_cap_witnesses':completed,
            'Gram_certificates':basis_evidence,'excluded_target_characteristics':sorted(bad_primes),
            'source_scope':'All nonzero scalar F2 columns fail on the explicit F1009 ADDRESS fixture; not a claim separately for every odd field.',
            'target_scope':'Rational and any field whose characteristic avoids the listed Gram primes; binary VALUE coefficients, unchanged word and native0 alphabet.',
            'controls':{'equal_frame_crossblock_zero':True,'no_change_update_zero':True,'no_native_entrance_restores_scalar_kernel':True}}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--write',action='store_true');args=ap.parse_args()
    paths={'raw':ROOT/'integer-mult-bounds/research/bit-r438-transport-rehost/words/r438-t154.json.gz',
           'pruned':OLD/'root-pruned-code/BIT-PRUNED-WORD.json.gz',
           'full':ROOT/'integer-mult-bounds/research/e8-bit-carrier-skeleton/data/bit/bitE8-r865.json.gz',
           'comp':MAJOR/'bit-endpoint/BIT-FULL-COMPENSATION.json',
           'native':RUN/'bit-native-caller/NATIVE-SEED-BINDING.json',
           'receipt':RUN/'coded-bit-boundary/KER-CODE-NATIVE-REJECTION.json',
           'producer':RUN/'coded-bit-boundary/ker_code_probe.py',
           'readme':RUN/'coded-bit-boundary/README.md'}
    expected={'raw':'a353999bceac4ac957f540adfd3e5f8768297138b27132eeb83332e2ea4b1022',
              'pruned':'1a6841fccba51fa922993c77b4b296e659c2c538252e5e06113d0438c5edb870',
              'full':'1fb726ea3818fe0837cceb0dd22a71a0814f064e5e781628104610d6468e0e55',
              'comp':'1ee06005d3b82ff592640d9aa4be2021b6de0a0b27fba5723aa06c36a6adbd20',
              'native':'786632fa57320e4c3a0966b74745af38a45c0312fed5036c0b9d80e004430d1c',
              'receipt':'f01694055292f9897ca9e109fd026c8c9b26c8c5bb3723b51ef192be9c7411c1',
              'producer':'69614d027eb67030d9a9f93fe2dff68700b54ce8a5d3088b07da922ab3d6aa6e',
              'readme':'d09c3b5451080f5bc3bfa348513c034e3aee11edc769cb552679607cd5bf11b7'}
    pins={k:sha256(p.read_bytes()).hexdigest() for k,p in paths.items()};need(pins==expected,'all frozen source pins')
    raw=json.loads(gzip.decompress(paths['raw'].read_bytes()));pruned=json.loads(gzip.decompress(paths['pruned'].read_bytes()))
    full=json.loads(gzip.decompress(paths['full'].read_bytes()));saved=json.loads(paths['receipt'].read_bytes())
    comp=json.loads(paths['comp'].read_bytes());native=json.loads(paths['native'].read_bytes())
    bulk=[r for r in pruned['records'] if r[0] not in (2,3) and r[5] not in (21,22,23,24,31,32,33)]
    need(all(r[0] in (0,1) for r in bulk) and all(not 111<=r[2]<222 for r in bulk if r[0]==1),'target-never-read fixed bulk')
    H=Counter(r[4] for r in bulk if r[0]==0)
    need(H==Counter({1:1295,2:1342,3:79,4:44,5:93,6:11,7:9}) and sum(k*v for k,v in H.items())==4986,'complete cheap bulk tariff')
    R,P,F,E,rr,weights=systematic(raw,bulk)
    need(P==saved['dependent_ports'] and F==saved['public_ports'] and E==saved['encoder_rows_102'] and [packed(r) for r in rr]==saved['systematic_paritycheck_rows_111'],'all fixed code rows')
    need([packed(r) for r in R]==comp['R'],'actual R agrees with frozen dependency')
    K=[sum(1<<j for j in ss) for ss in raw['scatter']];need(K==comp['K'],'actual K dependency')
    denseE=[[int(e>>j&1) for j in range(102)] for e in E];I=[[int(i==j) for j in range(111)] for i in range(111)]
    for repair in (False,True):
        rows=[]
        for p,k in enumerate(K):
            row=bytearray(I[p])
            if not repair or p not in (0,1,2):
                for j in bits(k):row=add(row,R[j])
            rows.append(row)
        need([[v%2 for v in row] for row in mm(rows,denseE)]==denseE,'both J E and A E equal E')
    scalar=scalar_replay(P,F,E,bulk);omitted=scalar_replay(P,F,E,bulk,True)
    mass=sum(r[4] for r in bulk if r[0]==0 and r[1]<222 and r[1]%111 in P)
    need(mass==126 and sum(E[p].bit_count() for p in P)==470,'complete selected parity cost and preparation gates')
    rhos,Ps,hashes=routes(raw,full);need(hashes==native['all111_actual_rho15_hashes'],'all actual rho route hashes')
    nat=native_checks(raw,pruned,bulk,R,P,F,E,rhos,Ps,saved)
    # A changed graph reads one old target: its independent coefficient enters x.
    target_columns=[bytearray(102) for _ in range(651)]
    for j,p in enumerate(F):target_columns[111+p][j]=1
    for p in P:target_columns[111+p]=bytearray(int(E[p]>>j&1) for j in range(102))
    target_columns[0]=add(target_columns[0],target_columns[111+F[0]])
    need(target_columns[0][0]==1,'target-reading control violates old-target independence')
    out={'status':'PASS_B13_SCALAR_CODE_AND_FIXED_NATIVE_REJECTION','no_new_kappa':True,'source_sha256':pins,
         'dependent_ports':P,'public_ports':F,'encoder_rows_102':E,'R_rows':list(map(packed,R)),
         'greedy_basis_weights':[weights[p] for p in P],'scalar':scalar,'omitted_preparation_control':omitted,
         'bulk_histogram':dict(H),'bulk_mass':4986,'selected_parity_mass':mass,'preparation_ADDs_per_bank':470,
         'all111_rho_hashes':hashes,'native':nat,'target_reading_control_nonzero_old_y_in_source':True,
         'scope':'F2 scalar certificate; rational/guarded odd-field fixed native0 obstruction. No integer cleanup, operator-code impossibility, owner, rounding, tape or new kappa admission.'}
    out=json.loads(json.dumps(out));target=HERE/'RESULT.json'
    if args.write:target.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    else:need(json.loads(target.read_text())==out,'whole independent receipt matches')
    print(out['status']);print('633 columns; 470 actual cut coefficients; 9 actual rho/update witnesses; bad target characteristics',nat['excluded_target_characteristics'])

if __name__=='__main__':main()
