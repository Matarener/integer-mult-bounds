#!/usr/bin/env python3
"""Dense exact replay of the frozen R429 FULL-target word, without producer imports.

All integer coefficients are Python arbitrary-precision integers. Standard
library only. Substantial OpenAI Codex assistance; Apache-2.0.
"""
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import argparse
import gzip
import json

ROOT=Path('/Users/ross/git/math')
RUN=ROOT/'.research-automation/runs/kappa-major-20261018T1330Z/bit-endpoint'
OLD=ROOT/'.research-automation/runs/kappa-3605-successor-20261018T0940Z/major-frontier'
HERE=Path(__file__).resolve().parent
N=651
V=111

def need(ok,message):
    if not ok:raise ValueError(message)

def canonical(value):
    return json.dumps(value,sort_keys=True,separators=(',',':')).encode()

def digest(rows):
    h=sha256()
    for row in rows:h.update((','.join(map(str,row))+'\n').encode())
    return h.hexdigest()

def ident(n):
    return [[int(i==j) for j in range(n)] for i in range(n)]

def bits(n):
    return [i for i in range(n.bit_length()) if n>>i&1]

def qrank(rows):
    a=[list(map(Q,row)) for row in rows]
    if not a:return 0
    p=0
    for col in range(len(a[0])):
        k=next((k for k in range(p,len(a)) if a[k][col]),None)
        if k is None:continue
        a[p],a[k]=a[k],a[p];v=a[p][col]
        a[p]=[x/v for x in a[p]]
        for k in range(p+1,len(a)):
            v=a[k][col]
            if v:a[k]=[x-v*y for x,y in zip(a[k],a[p])]
        p+=1
        if p==len(a[0]):break
    return p

def multiply(a,b):
    return [[sum(x*y for x,y in zip(row,col)) for col in zip(*b)] for row in a]

def exchange(p):
    # ADDRESS map (u,v) -> ((I-P)u+Pv, Pu+(I-P)v).
    c=[[Q(i==j)-p[i][j] for j in range(8)] for i in range(8)]
    return [c[i]+p[i] for i in range(8)]+[p[i]+c[i] for i in range(8)]

def dyadic_hash(a):
    return sha256(canonical([[[Q(x).numerator,Q(x).denominator] for x in row] for row in a])).hexdigest()

def replay(records,backward=False,initial=None):
    a=ident(N) if initial is None else [row[:] for row in initial]
    maximum=max(sum(map(abs,row)) for row in a);first=None
    counts=Counter()
    ordered=list(enumerate(records))
    if backward:ordered.reverse()
    for index,(op,d,s,c,f,phase) in ordered:
        counts[op]+=1
        need(op in (0,1),'no COPY/ERASE/private opcode')
        if op!=1:continue
        need(0<=d<N and 0<=s<N and d!=s and c in (-1,1),'signed ADD schema')
        c=-c if backward else c
        a[d]=[x+c*y for x,y in zip(a[d],a[s])]
        norm=sum(map(abs,a[d]))
        if norm>maximum:maximum=norm;first={'record':index,'destination':d,'phase':phase}
    return a,maximum,first,counts

def parity(rows):
    return [sum((x%2)<<j for j,x in enumerate(row)) for row in rows]

def validate_signed_endpoint(rows):
    for p in list(range(V))+list(range(2*V,N)):
        need(rows[p]==[int(p==j) for j in range(N)],'source/helper exact integer identity')
    for p in range(V,2*V):
        need(rows[p][V:2*V]==[int(p==j) for j in range(V,2*V)],'old target block is exact identity')
        need(all(x%2==0 for x in rows[p][2*V:]),'all integer helper leakage even')
    want=[1<<i for i in range(N)]
    for p in range(V):want[V+p]^=1<<p
    need(parity(rows)==want,'all651 binary shear columns')

def native_frames(records,program,geometry,dims,backward=False):
    current=(program['final'] if backward else program['start'])[:]
    masks=[set(f) for f in geometry['frames']]
    hist=Counter();adds=Counter();moves=[]
    rows=list(enumerate(records))
    if backward:rows.reverse()
    for index,(op,d,s,c,f,phase) in rows:
        need(0<=d<N,'native destination role')
        if op==0:
            old,new=(c,s) if backward else (s,c)
            lower,upper=(new,old) if backward else (old,new)
            need(current[d]==old,'MOVE current frame')
            need(masks[lower]<=masks[upper],'MOVE literal nested support')
            need(dims[upper]-dims[lower]==f and f>0,'MOVE exact rational dimension increment')
            current[d]=new;hist[f]+=1;moves.append([index,d,old,new,f])
        elif op==1:
            need(0<=s<N and d!=s and current[d]==current[s]==f,'ADD actual common frame')
            adds[f]+=1
        else:raise ValueError('private opcode not permitted')
    need(current==(program['start'] if backward else program['final']),'complete frame endpoint')
    return hist,adds,sha256(canonical(moves)).hexdigest()

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--write',action='store_true');args=parser.parse_args()
    files={
        'word':RUN/'BIT-FULL-COMPENSATION-WORD.json.gz',
        'receipt':RUN/'BIT-FULL-COMPENSATION.json',
        'pruned':OLD/'root-pruned-code/BIT-PRUNED-WORD.json.gz',
        'raw':ROOT/'integer-mult-bounds/research/bit-r438-transport-rehost/words/r438-t154.json.gz',
        'producer':RUN/'bit_full_compensation.py',
        'replay_utility':RUN/'bit_full_targets.py',
        'old_cap_utility':OLD/'recursive/bit_cap_copy_local.py',
        'old_scalar_utility':OLD/'recursive/bit_signed_audit.py',
    }
    pins={k:sha256(p.read_bytes()).hexdigest() for k,p in files.items()}
    need(pins['word']=='0f461dbc7e82a02faedb4a5129103963507c9f063a0a3679ba5d20ad94df160e','frozen final word gzip pin')
    need(pins['raw']=='a353999bceac4ac957f540adfd3e5f8768297138b27132eeb83332e2ea4b1022','raw R438 geometry pin')
    need(pins['pruned']=='1a6841fccba51fa922993c77b4b296e659c2c538252e5e06113d0438c5edb870','frozen R429 predecessor gzip pin')
    body=gzip.decompress(files['word'].read_bytes());program=json.loads(body)
    prior_body=gzip.decompress(files['pruned'].read_bytes());base=json.loads(prior_body)
    need(sha256(body).hexdigest()=='895a359e33a7a9a9cb2c4a68acc9fcf624596d334a52381264ae498e0e55c847','canonical final word')
    need(sha256(prior_body).hexdigest()=='ebc33ee086f610c1fd540fa56bb99b2b96a768e4aed4a18defcb0e1f507fca89','published predecessor canonical word')
    geometry=json.loads(gzip.decompress(files['raw'].read_bytes()))
    receipt=json.loads(files['receipt'].read_text());records=program['records'];roots=geometry['lines']
    need(program['public_registers']==N and program['private_register'] is None,'651 ordinary roles and no private field')
    keep=[i for i in range(660) if i not in program['deleted_public_families']]
    need(program['start']==[geometry['start'][i] for i in keep],'inherited source/helper entrance frames')
    need(len(program['start'])==N and program['final']==[1]*N,'all651 final frames FULL')
    need(program['start'][V:]==[0]*(N-V),'targets and429 helpers enter ZERO')
    # Decode the raw reader map without importing any producer or proof utility.
    raw_rows=ident(660)
    for phase in ('D','A'):
        for frame,d,sources in geometry[phase]:
            for s in sources:raw_rows[d]=[x^y for x,y in zip(raw_rows[d],raw_rows[s])]
    R=[sum(x<<p for p,x in enumerate(raw_rows[h][:V])) for h in geometry['ret']]
    K=[sum(1<<j for j in sources) for sources in geometry['scatter']]
    need(R==receipt['R'] and K==receipt['K'],'all raw R/K coordinates')
    # Verify the exact final literal construction, then replay its signed map.
    bulk=[r for r in base['records'] if r[0] not in (2,3) and r[5] not in (21,22,23,24,31,32,33)]
    lifts=[[0,d,base['final'][d],1,1,42] for d in range(V,2*V)]
    correction=[]
    for j,r in enumerate(R):
        support=bits(r);pivot=support[0];other=support[1:]
        correction += [[1,pivot,p,1,1,51] for p in other]
        correction += [[1,V+p,pivot,1,1,52] for p,k in enumerate(K) if k>>j&1]
        correction += [[1,pivot,p,-1,1,53] for p in reversed(other)]
    need(records==bulk+lifts+correction,'complete literal bulk/lifts/nine-total word equality')
    need(len(correction)==1555 and len(lifts)==111,'new literal code counts')
    forward,pf,wf,counts=replay(records)
    backward,pb,wb,back_counts=replay(records,True)
    validate_signed_endpoint(forward);validate_signed_endpoint(backward)
    need(counts==back_counts==Counter({0:2984,1:12932}),'complete word opcode counts')
    need(pf==pb==874,'exact forward and inverse signed row-L1 prefix874')
    # The endpoint is a single signed shear, hence its complete integer inverse
    # negates every off-diagonal coefficient, including all even residuals.
    need(backward==[[2*int(i==j)-x for j,x in enumerate(row)] for i,row in enumerate(forward)],'full signed inverse matrix, not merely parity')
    roundtrip,_,_,_=replay(records,True,forward)
    need(roundtrip==ident(N),'literal inverse roundtrip on all651 integer columns')
    bulk_matrix,_,_,_=replay(bulk)
    need(all(bulk_matrix[p]==forward[p] for p in list(range(V))+list(range(2*V,N))),'bulk restores all source/helper integer rows')
    for p in range(V):
        target=bulk_matrix[V+p][:]
        for j,k in enumerate(K[p]>>j&1 for j in range(9)):
            if k:
                for q in bits(R[j]):target[q]+=1
        need(target==forward[V+p],'complete signed target matrix equals bulk plus positive nine-total correction')
    A=[row[:V] for row in forward[V:2*V]]
    E=[row[2*V:] for row in forward[V:2*V]]
    B=[row[:V] for row in bulk_matrix[V:2*V]]
    need(any(x!=int(i==j) for i,row in enumerate(A) for j,x in enumerate(row)),'signed target update is not asserted equal to x overZ')
    need(any(x for row in E for x in row),'nonzero even dirt witness retained')
    print('PASS independent dense651-column signed endpoint, inverse, bulk identity and prefix874',flush=True)
    dims=[qrank([roots[i] for i in f]) for f in geometry['frames']]
    need(dims[0]==0 and dims[1]==8,'ZERO/FULL frame dimensions')
    hist,add_frames,fh=native_frames(records,program,geometry,dims)
    rhist,radd_frames,bh=native_frames(records,program,geometry,dims,True)
    expected=Counter({1:1406,2:1342,3:79,4:44,5:93,6:11,7:9})
    need(hist==rhist==expected and add_frames==radd_frames,'complete forward/inverse frame invoice')
    need(sum(k*v for k,v in hist.items())==5097==sum(dims[f] for f in program['final'])-sum(dims[f] for f in program['start']),'rank mass equals chronological frame progress')
    need(add_frames[0]==5758 and add_frames[1]==4147 and sum(v for f,v in add_frames.items() if f not in (0,1))==3027,'correct old intermediate-frame ADD scope')
    need(all(r[4]==1 for r in correction),'all new compensation atFULL')
    ident8=ident(8);ident16=ident(16);DI=exchange(ident8)
    projectors=[];lift_hashes=[];native_rows=[]
    for p,q in enumerate(roots):
        need(sum(x*x for x in q)==4,'actual root norm4')
        P=[[Q(x*y,4) for y in q] for x in q]
        C=[[Q(i==j)-P[i][j] for j in range(8)] for i in range(8)]
        start=geometry['frames'][program['start'][p]]
        cap=geometry['frames'][base['final'][V+p]]
        need(qrank([roots[i] for i in start])==1 and all(multiply(P,[[x] for x in roots[i]])==[[Q(x)] for x in roots[i]] for i in start),'actual source entrance line projector')
        need(qrank([roots[i] for i in cap])==7 and all(sum(x*y for x,y in zip(q,roots[i]))==0 for i in cap),'actual target cap projector')
        need(multiply(P,P)==P and qrank(P)==1 and qrank(C)==7,'dyadic complementary projectors')
        DP,DC=exchange(P),exchange(C)
        need(multiply(DI,DP)==DC and multiply(DP,DP)==ident16,'inherited cap ADDRESS identities')
        need(multiply(DI,DC)==DP,'new rank1 cap-to-FULL ADDRESS identity')
        projectors.append(dyadic_hash(P));lift_hashes.append(dyadic_hash(DP))
        # q has coordinates 0,+/-1,+/-2 and norm4, so P is nonzero rank1
        # in every odd characteristic. The factor q/4 times q^T has trace1.
        need(all(abs(x)<=2 for x in q) and any(x for x in q),'odd-characteristic rank1 factor')
        native_rows.append({'port':p,'source_rank':7,'target_rank':8,'lift_rank':1})
    need(projectors==receipt['actual_address_projectors'] and lift_hashes==receipt['new_target_lift_ADDRESS_sha256'],'all111 projector and1776 new ADDRESS-column hashes')
    need(V*(7+8)+429*8==5097,'complete local native progress; zero excess')
    print('PASS independent exact frame chronology and5328 dyadic ADDRESS columns',flush=True)
    # Semantic controls: mutate the executed word, then check actual consequences.
    scatter=next(i for i,r in enumerate(records) if r[5]==52)
    bad_scatter,_,_,_=replay(records[:scatter]+records[scatter+1:])
    need(parity(bad_scatter)!=parity(forward),'omitted scatter changes binary endpoint')
    unprepare=next(i for i,r in enumerate(records) if r[5]==53)
    bad=[r[:] for r in records];bad[unprepare][3]*=-1
    wrong_sign,_,_,_=replay(bad)
    need(wrong_sign[:V]!=forward[:V] and parity(wrong_sign)==parity(forward),'wrong unprepare breaks signed source restoration despite identical parity')
    lift=next(i for i,r in enumerate(records) if r[0]==0 and r[1]==V and r[5]==42)
    try:native_frames(records[:lift]+records[lift+1:],program,geometry,dims)
    except ValueError as error:lift_rejection=str(error)
    else:raise ValueError('missing target lift escaped')
    need(lift_rejection=='ADD actual common frame','missing lift fails at a real native ADD')
    # Postcompose y <- y-x. Over F2 this diagonalizes the physical block;
    # overZ it intentionally retains the even residual rather than hiding it.
    diagonalized=[row[:] for row in forward]
    for p in range(V):diagonalized[V+p]=[x-y for x,y in zip(diagonalized[V+p],diagonalized[p])]
    need(parity(diagonalized)==[1<<i for i in range(N)],'111 paid FULL ADDs diagonalize binary endpoint')
    need(diagonalized!=ident(N),'paid binary diagonalization is not an integer identity claim')
    residue_samples={'target_source':next([i,j,x-int(i==j)] for i,row in enumerate(A) for j,x in enumerate(row) if x!=int(i==j)),
                     'target_helper':next([i,j+2*V,x] for i,row in enumerate(E) for j,x in enumerate(row) if x)}
    out={'status':'PASS_INDEPENDENT_R429_FULL_TARGET_WORD','scientific_pin':'20ecf2891d80b5acf18d980b2164fb44ea7faa90',
         'sources':{str(files[k]):h for k,h in pins.items()},'word_canonical_sha256':sha256(body).hexdigest(),
         'predecessor_canonical_sha256':sha256(prior_body).hexdigest(),'arbitrary_integer_columns':N,
         'forward_dense_integer_sha256':digest(forward),'literal_inverse_dense_integer_sha256':digest(backward),
         'target_source_integer_A_sha256':digest(A),'target_helper_integer_E_sha256':digest(E),'bulk_target_source_integer_B_sha256':digest(B),
         'integer_endpoint':'(x,y,h) -> (x,y+A*x+E*h,h), A=I mod2, E=0 mod2; A and E are fully computed, nontrivial signed integer matrices.',
         'even_residual_samples':residue_samples,'source_restored_over_Z':111,'helpers_restored_in_logical_coordinates_over_Z':429,
         'literal_inverse_all_integer_columns':True,'exact_signed_prefix_row_L1':[pf,pb],'first_maximum_witnesses':[wf,wb],
         'ADD_count':12932,'MOVE_count':2984,'new_compensation_ADDs':1555,'new_target_lifts':111,
         'profile':dict(hist),'rank_mass':5097,'frame_chronology_sha256':[fh,bh],
         'ADD_frame_counts':{'ZERO':5758,'FULL':4147,'other':3027,'distinct_frames':len(add_frames)},
         'new_compensation_frame':'FULL','private_fields':0,'COPY_ERASE_records':0,
         'old_projector_ADDRESS_columns':3552,'new_lift_ADDRESS_columns':1776,'all111_exact_projector_hashes':projectors,'all111_lift_hashes':lift_hashes,
         'controls':{'omitted_scatter_binary_failure':True,'wrong_unprepare_integer_failure_parity_unchanged':True,'omitted_lift':lift_rejection},
         'physical_boundary':'Under inherited native MOVE/frame realization over binary VALUES, source S=F8*D_P, target T=F8, data block [[S,0],[S,T]], helpers F8*d. Logical integer helper identity is not physical identity.',
         'paid_diagonalization_ADDs':111,'paid_diagonalized_total_ADDs':13043,'diagonalized_binary_endpoint':True,'integer_identity_after_diagonalization':False,
         'native_progress':V*15+429*8,'no_new_kappa':True,
         'scope':['The frozen final word is consumed directly; no producer or producer utility is imported.',
                  'Old internal native MOVE implementations and compiler guards remain inherited premises; their all-modulus implementation is not independently replayed.',
                  'Dyadic ADDRESS equalities hold in every odd field; VALUE additions and integer scalar normalization are distinct layers.',
                  'Prefix874 is a signed scalar bound, not a rounded precision or child-defect theorem.',
                  'No global caller, owner chronology, physical source access, tape realization or stronger multiplication theorem is admitted.'],
         'historical_receipt_correction':'Its allsize_lift sentence saying every scalar ADD is atZERO/FULL is false. Every ADD is at its actual common frame; only all newly added nine-total compensation ADDs are atFULL.'}
    out=json.loads(json.dumps(out))
    path=HERE/'RESULT.json'
    if args.write:path.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    else:need(json.loads(path.read_text())==out,'independent complete receipt differs')
    print(out['status'])

if __name__=='__main__':main()
