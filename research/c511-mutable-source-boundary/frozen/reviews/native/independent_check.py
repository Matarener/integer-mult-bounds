#!/usr/bin/env python3
"""Independent dense C511 local replay, exact chart construction and operator proof.

No producer mathematics is imported. Standard library only. Substantial
OpenAI Codex assistance; Apache-2.0.
"""
from collections import Counter,deque
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import argparse,gzip,json

ROOT=Path('/Users/ross/git/math')
HERE=Path(__file__).resolve().parent
OLD=ROOT/'.research-automation/runs/kappa-3605-successor-20261018T0940Z/major-frontier/recursive'
RUN=ROOT/'.research-automation/runs/kappa-changed-endpoints-20261019T0153Z/bit-native-caller'
N,V=660,111

def need(ok,m):
    if not ok:raise ValueError(m)

def canonical(x):return json.dumps(x,sort_keys=True,separators=(',',':')).encode()
def ident(n):return [[int(i==j) for j in range(n)] for i in range(n)]
def mm(a,b):return [[sum(x*y for x,y in zip(r,c)) for c in zip(*b)] for r in a]
def transpose(a):return list(map(list,zip(*a)))
def bits(n):return [i for i in range(n.bit_length()) if n>>i&1]
def xor(xs):
    out=0
    for x in xs:out^=x
    return out
def rankq(rows):
    a=[list(map(Q,r)) for r in rows];k=0
    if not a:return 0
    for j in range(len(a[0])):
        p=next((p for p in range(k,len(a)) if a[p][j]),None)
        if p is None:continue
        a[k],a[p]=a[p],a[k];v=a[k][j];a[k]=[x/v for x in a[k]]
        for p in range(k+1,len(a)):
            v=a[p][j]
            if v:a[p]=[x-v*y for x,y in zip(a[p],a[k])]
        k+=1
        if k==len(a[0]):break
    return k
def rank2(rows):
    b={}
    for x in rows:
        while x:
            p=x.bit_length()-1
            if p in b:x^=b[p]
            else:b[p]=x;break
    return len(b)
def binary(rows):return [sum((x%2)<<j for j,x in enumerate(r)) for r in rows]
def bprod(a,b):return [xor(b[j] for j in bits(x)) for x in a]
def bpow(a,n):
    out=[1<<i for i in range(len(a))]
    while n:
        if n&1:out=bprod(out,a)
        a=bprod(a,a);n//=2
    return out
def dense_hash(rows):
    h=sha256()
    for row in rows:h.update((','.join(map(str,row))+'\n').encode())
    return h.hexdigest()

def replay(program,raw,dims,back=False,initial=None):
    state=ident(N)+[[0]*N] if initial is None else [r[:] for r in initial]
    frames=(program['final'] if back else program['start'])[:]+[None]
    masks=[set(f) for f in raw['frames']]
    records=list(enumerate(program['records']))
    if back:records.reverse()
    live=None;hist=Counter();adds=0;copies=[];peak=max(sum(map(abs,r)) for r in state)
    for at,(op,d,s,c,f,ph) in records:
        need(0<=d<N,'ordinary destination')
        if op==0:
            before,after=(c,s) if back else (s,c)
            lo,hi=(after,before) if back else (before,after)
            need(frames[d]==before and masks[lo]<=masks[hi] and dims[hi]-dims[lo]==f>0,'typed nested MOVE')
            frames[d]=after;hist[f]+=1
        elif op==1:
            need(0<=s<=N and s!=d and frames[d]==frames[s]==f,'typed common-frame ADD')
            need(d!=live,'immutable original snapshot source')
            v=-c if back else c
            state[d]=[x+v*y for x,y in zip(state[d],state[s])]
            peak=max(peak,sum(map(abs,state[d])));adds+=1
        elif op==(3 if back else 2):
            need(live is None and s==N and state[N]==[0]*N and frames[N] is None and frames[d]==c,'fresh zero private COPY')
            need(masks[f]<=masks[c] and dims[c]>dims[f],'positive nested COPY tariff')
            cost=dims[c]-dims[f];hist[cost]+=1
            copies.append([d,c,f,cost]);state[N]=state[d][:];frames[N]=f;live=d
        else:
            need(op==(2 if back else 3) and live==d and s==N and frames[d]==c and frames[N]==f and state[N]==state[d],'literal ERASE original exact snapshot')
            state[N]=[0]*N;frames[N]=None;live=None
    need(frames==(program['start'] if back else program['final'])+[None] and live is None and state[N]==[0]*N,'all typed endpoints and zero private return')
    return state,{'histogram':dict(hist),'mass':sum(k*v for k,v in hist.items()),'ADDs':adds,'COPYs':copies,'prefix':peak}

def clean_program(raw,dims):
    frames=raw['start'][:];records=[]
    def move(d,f):
        if frames[d]!=f:
            records.append([0,d,frames[d],f,dims[f]-dims[frames[d]],0]);frames[d]=f
    for phase,tag,sign in [('D',10,1),('A',2,1)]:
        for f,d,ss in raw[phase]:
            for r in [d]+ss:move(r,f)
            records += [[1,d,s,sign,f,tag] for s in ss]
    for j,h in enumerate(raw['ret']):
        records.append([2,h,N,frames[h],0,3])
        records += [[1,V+p,N,1,0,3] for p,ss in enumerate(raw['scatter']) if j in ss]
        records.append([3,h,N,frames[h],0,3])
    for phase,tag,sign in [('B',4,1),('C',5,-1)]:
        for f,d,ss in raw[phase]:
            for r in [d]+ss:move(r,f)
            records += [[1,d,s,sign,f,tag] for s in ss]
    for d,f in enumerate(raw['final']):move(d,f)
    return {'start':raw['start'],'final':raw['final'],'records':records}

def routes(raw,full):
    # First choose the deterministic BFS tree on root labels, then reconstruct
    # every chart from its path. This does not call physical_code.actual_routes.
    roots=full['lines'];parent={0:None};queue=deque([0])
    while queue:
        p=queue.popleft()
        for q in range(120):
            ip=sum(x*y for x,y in zip(roots[p],roots[q]))//2
            if q not in parent and abs(ip)==1:
                parent[q]=(p,ip);queue.append(q)
    need(len(parent)==120,'complete120-line Weyl BFS')
    gs=[]
    for q in range(120):
        path=[];at=q
        while parent[at] is not None:
            p,sgn=parent[at];path.append((p,at,sgn));at=p
        g=ident(8)
        for p,t,sgn in reversed(path):
            v=[a-sgn*b for a,b in zip(roots[p],roots[t])];den=sum(x*x for x in v)
            ref=[[Q(i==j)-Q(2*v[i]*v[j],den) for j in range(8)] for i in range(8)]
            g=mm(ref,g)
        need(mm(transpose(g),g)==ident(8),'orthogonal exact Weyl chart')
        gs.append(g)
    rh=[];Ps=[];hashes=[]
    H=[[Q(i==j and i<8) for j in range(15)] for i in range(15)]
    E=[[Q(i==j and i>=8) for j in range(15)] for i in range(15)]
    for p,q in enumerate(raw['lines']):
        g=gs[raw['ports_geom'][p]];A=[row[1:] for row in g]
        P=[[Q(x*y,4) for y in q] for x in q]
        K=[[Q(i==j)-P[i][j] for j in range(8)] for i in range(8)]
        need(mm(A,transpose(A))==K and mm(transpose(A),A)==ident(7),'actual cap isometry')
        rho=[P[i]+A[i] for i in range(8)]+[row+[Q(0)]*7 for row in transpose(A)]
        need(rho==transpose(rho) and mm(rho,rho)==ident(15),'exact rho involution')
        oldcap=[[K[i][j] if i<8 and j<8 else Q(0) for j in range(15)] for i in range(15)]
        line=[[P[i][j] if i<8 and j<8 else Q(0) for j in range(15)] for i in range(15)]
        localfull=[[line[i][j]+E[i][j] for j in range(15)] for i in range(15)]
        need(mm(mm(rho,oldcap),rho)==E and mm(mm(rho,localfull),rho)==H,'actual old-cap and localFULL intertwiners')
        need(mm(mm(rho,line),rho)==line,'same native line under rho')
        hashes.append(sha256(json.dumps([[str(x) for x in row] for row in rho],separators=(',',':')).encode()).hexdigest())
        rh.append(rho);Ps.append(line)
    return rh,Ps,hashes

# Operator monomials form C2(F) x (C2(N) * Z(C)); F commutes both N,C.
# A normal word is (F parity, alternating N marker0 and nonzero C exponents).
def normal(f,word):
    out=[]
    for x in word:
        if out and x==out[-1]==0:out.pop()
        elif out and x!=0 and out[-1]!=0:
            value=out.pop()+x
            if value:out.append(value)
        else:out.append(x)
    return (f%2,tuple(out))
def poly(f=0,word=()):return {normal(f,word)}
def add(a,b):return a^b
def product(a,b):
    out=set()
    for (f,u) in a:
        for (g,v) in b:
            w=normal(f+g,u+v)
            if w in out:out.remove(w)
            else:out.add(w)
    return out
def matmul(a,b):return [[add(product(a[i][0],b[0][j]),product(a[i][1],b[1][j])) for j in range(2)] for i in range(2)]
def formal():
    O=set();I=poly();F=poly(1);Nn=poly(0,(0,));C=poly(0,(1,));Ci=poly(0,(-1,));G=product(F,Nn)
    identity=[[I,O],[O,I]]
    physical=[[product(F,product(C,Nn)),O],[product(G,product(C,Nn)),G]]
    inverse=[[product(G,Ci),O],[F,G]]
    need(matmul(physical,inverse)==matmul(inverse,physical)==identity,'universal physical inverse both orders')
    # Independently execute the normalized bank updates on the two input columns.
    x,y=[I,O],[O,I]
    def plus_left(a,k,b):return [add(u,product(k,v)) for u,v in zip(a,b)]
    y=plus_left(y,Nn,x);x=plus_left(x,Nn,y);y=plus_left(y,Nn,x);x,y=y,x
    need([x,y]==[[Nn,O],[O,Nn]],'three CLEAN calls and paid swap')
    old=x;x=[product(product(Nn,product(C,Nn)),v) for v in old]
    y=plus_left(y,product(C,Nn),old);y=plus_left(y,Nn,x)
    need([x,y]==[[product(Nn,C),O],[O,Nn]],'five-call universal normal form')
    Qc=[[product(Nn,product(C,Nn)),O],[product(C,Nn),I]]
    Cf=[[I,O],[Nn,I]];Cb=[[I,Nn],[O,I]]
    first=matmul(Cf,matmul(Cb,Qc))
    need(first==[[O,Nn],[product(C,Nn),O]] and first!=[[O,Nn],[product(Nn,C),O]],'wrong-side first-coded control')
    consuming=matmul([[I,O],[O,Ci]],matmul(inverse,[[C,O],[O,I]]))
    need(consuming==[[G,O],[F,product(Ci,G)]],'source-consuming map with arbitrary oldy retained')
    return {'physical_inverse_verified_both_orders':True,'five_call_normalized':'diag(N*C,N)',
            'first_coded_replacement':'[[0,N],[C*N,0]] != [[0,N],[N*C,0]]',
            'source_consuming_with_arbitrary_y':'(G*x,F*x+C^-1*G*y)',
            'relations':'F central involution; N involution; C invertible; no N/C commutation or finite order used.'}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--write',action='store_true');a=ap.parse_args()
    paths={'word':OLD/'BIT-THREE-COPY-INPUT-WORD.json.gz',
           'raw':ROOT/'integer-mult-bounds/research/bit-r438-transport-rehost/words/r438-t154.json.gz',
           'full':ROOT/'integer-mult-bounds/research/e8-bit-carrier-skeleton/data/bit/bitE8-r865.json.gz',
           'receipt':RUN/'MUTABLE-SOURCE-FIVE.json'}
    pins={k:sha256(p.read_bytes()).hexdigest() for k,p in paths.items()}
    need(pins['word']=='ac8a6dcd5957f49eefd6fc945332b1c31afa26c48fc301d37bfb1338beea6847' and pins['raw']=='a353999bceac4ac957f540adfd3e5f8768297138b27132eeb83332e2ea4b1022','exact frozen source pins')
    word=json.loads(gzip.decompress(paths['word'].read_bytes()));raw=json.loads(gzip.decompress(paths['raw'].read_bytes()));full=json.loads(gzip.decompress(paths['full'].read_bytes()));saved=json.loads(paths['receipt'].read_text())
    need(word['public_registers']==660 and word['private_register']==660,'660 arbitrary roles and one zero private')
    need(word['start']==raw['start'] and word['final']==raw['final'],'exact inherited endpoint frames')
    dims=[rankq([raw['lines'][p] for p in f]) for f in raw['frames']]
    forward,fw=replay(word,raw,dims);backward,bw=replay(word,raw,dims,True)
    I=ident(N)+[[0]*N]
    for state in (forward,backward):
        need(state[2*V:N]==I[2*V:N] and state[N]==[0]*N,'all438 logical integer helpers and zero private restored')
        need(all(not any(row[V:]) for row in state[:V]),'source is uncontaminated overZ')
        need(all(row[V:2*V]==[int(i==j) for j in range(V)] for i,row in enumerate(state[V:2*V])),'old target exact identity block')
        need(all(x%2==0 for row in state[V:2*V] for x in row[2*V:]),'integer helper leakage even')
    literal=[r for r in word['records'] if r[0]==1 and r[5] in (21,22,23,24)]
    need(len(literal)==1487 and all(d<V and s<V and f==1 for op,d,s,c,f,ph in literal),'1487 actual FULL source code ADDs')
    Cz=ident(V)
    for op,d,s,c,f,ph in literal:Cz[d]=[x+c*y for x,y in zip(Cz[d],Cz[s])]
    need([row[:V] for row in forward[:V]]==Cz,'complete exact source-code integer matrix')
    C=binary(Cz);Cinv=binary([row[:V] for row in backward[:V]])
    need(C==saved['C_binary_rows'] and rank2(C)==111 and rank2([r^(1<<i) for i,r in enumerate(C)])==9,'source-bound C rank and defect')
    need(bprod(C,Cinv)==bprod(Cinv,C)==[1<<i for i in range(V)],'binary inverse code')
    expected=[1<<i for i in range(N)]+[0];expected[:V]=C
    for p in range(V):expected[V+p]^=C[p]
    need(binary(forward)==expected,'all660 arbitrary binary columns and zero private row')
    expected[:V]=Cinv
    for p in range(V):expected[V+p]=(1<<(V+p))^(1<<p)
    need(binary(backward)==expected,'raw inverse cross independent ofC on all columns')
    closed,_=replay(word,raw,dims,True,forward);need(closed==I,'complete literal integer inverse roundtrip')
    for op,d,s,c,f,ph in reversed(literal):Cz[d]=[x-c*y for x,y in zip(Cz[d],Cz[s])]
    need(Cz==ident(V),'literal integer source decoder')
    need(bpow(C,511)==[1<<i for i in range(V)] and bpow(C,73)!=[1<<i for i in range(V)] and bpow(C,7)!=[1<<i for i in range(V)],'exact order511 via its two prime divisors')
    need(fw['histogram']==bw['histogram']=={1:1325,2:1342,3:79,4:44,5:102,6:11,7:9} and fw['mass']==5061 and len(fw['COPYs'])==3,'complete coded invoice')
    clean=clean_program(raw,dims);cleanrows,cl=replay(clean,raw,dims)
    want=[1<<i for i in range(N)]+[0]
    for p in range(V):want[V+p]^=1<<p
    need(binary(cleanrows)==want and all(cleanrows[p]==I[p] for p in list(range(V))+list(range(2*V,N))),'clean all-column source/helper contract')
    need(cl['histogram']=={1:1322,2:1342,3:79,4:44,5:102,6:11,7:18} and cl['ADDs']==24248 and len(cl['COPYs'])==9,'complete clean invoice')
    print('PASS independent dense660-input C511 word, exact lifecycle and CLEAN invoice',flush=True)
    rh,Ps,rho_hashes=routes(raw,full)
    need(rho_hashes==[r['rho_sha256'] for r in saved['actual_native_geometry']['ports']],'all111 exact chosen Weyl-BFS gauges')
    edge_count=sum(x.bit_count() for x in C);witness=None
    for p,row in enumerate(C):
        for q in bits(row):
            if p==q:continue
            edge=mm(rh[p],rh[q]);left,right=mm(Ps[p],edge),mm(edge,Ps[q])
            if left!=right:
                i,j=next((i,j) for i in range(15) for j in range(15) if left[i][j]!=right[i][j])
                witness={'edge':[p,q],'ADDRESS_entry':[i,j],'left':str(left[i][j]),'right':str(right[i][j])};break
        if witness:break
    need(witness==saved['actual_native_geometry']['commonN_noncommutation_control'],'actual routed noncommutation witness')
    relations=formal()
    hist=Counter({k:4*v for k,v in cl['histogram'].items()});hist.update(fw['histogram'])
    need(dict(hist)=={1:6613,2:6710,3:395,4:220,5:510,6:55,7:81},'complete five-call histogram')
    mass=sum(k*v for k,v in hist.items());public=2*111*36;helpers=5*438*8;private=4*63+3
    adds=4*cl['ADDs']+fw['ADDs']+1487+333
    need((mass,public,helpers,private,public+helpers-mass,adds)==(25545,7992,17520,255,-33,112095),'full five-call failed invoice')
    need(111*8+438*8-5061==-669,'source-consuming independent-output invoice')
    # Mutations are executed against the actual typed/signed word.
    bad=dict(word);bad['records']=[r for i,r in enumerate(word['records']) if i!=next(j for j,r in enumerate(word['records']) if r[0]==3)]
    try:replay(bad,raw,dims)
    except ValueError as e:erase_control=str(e)
    else:raise ValueError('omitted ERASE escaped')
    need(erase_control=='immutable original snapshot source','omitted ERASE rejects actual source change before next COPY')
    bad=dict(word);bad['records']=[r[:] for r in word['records']]
    which=next(i for i,r in enumerate(bad['records']) if r[0]==1 and r[5] in (21,22,23,24))
    bad['records'][which][3]*=-1
    changed,_=replay(bad,raw,dims)
    need(changed[:V]!=forward[:V] and binary(changed)==binary(forward),'wrong source-code sign changesZ but notF2')
    out={'status':'PASS_INDEPENDENT_C511_NATIVE_INTERFACE_AND_NEGATIVE_BUDGET',
         'scientific_pin':'20ecf2891d80b5acf18d980b2164fb44ea7faa90','sources':{str(paths[k]):v for k,v in pins.items()},
         'ordinary_arbitrary_input_columns':660,'ordinary_helper_rows':438,'required_zero_private_rows':1,
         'private_arbitrary_input_not_claimed':True,'forward_dense_integer_sha256':dense_hash(forward),'literal_inverse_dense_integer_sha256':dense_hash(backward),
         'forward_local':fw,'inverse_local':bw,'clean_local':cl,
         'C_rank':111,'C_defect_rank':9,'C_order':511,'order_divisor_checks':[7,73,511],'source_CODE_ADDs':1487,
         'all111_Weyl_BFS_rho_sha256':rho_hashes,'nonzero_C_coefficients_covered_by_port_intertwiners':edge_count,'actual_C_N_noncommutation':witness,
         'universal_operator_algebra':relations,'complete_five_call_histogram':dict(hist),
         'native_rank_mass':mass,'public_progress':public,'ordinary_helper_progress':helpers,'private_COPY_rank':private,
         'complete_scalar_ADDs':adds,'uncovered_deficit':-33,'source_consuming_deficit_uncredited_remnant':-669,
         'source_consuming_zero_target_fields':111,'source_consuming_linked_source_remnants':111,
         'source_consuming_scalar_ADDs':fw['ADDs']+2*1487,
         'executed_controls':{'omitted_ERASE':erase_control,'wrong_integer_source_code_sign_parity_unchanged':True,'wrong_side_C_N':True},
         'no_new_kappa':True,'limits':['Local signed and binary columns plus exact typed lifecycle; private register is required zero, not arbitrary dirt.',
             'The universal operator-ring identity is over binary VALUES; integer scalar residuals are separately retained.',
             'Helpers have logical identity and physical residual frame progress; reverse owner admission is separate.',
             'Old native internal MOVE/COPY realizations, all chronological owners, rounded children, access and tape costs remain inherited or unresolved.',
             'Historical million-pair searches and rolling obstructions are not replayed or included in this theorem.']}
    out=json.loads(json.dumps(out));path=HERE/'RESULT.json'
    if a.write:path.write_text(json.dumps(out,sort_keys=True,indent=2)+'\n')
    else:need(json.loads(path.read_text())==out,'complete independent receipt differs')
    print(out['status'])

if __name__=='__main__':main()
