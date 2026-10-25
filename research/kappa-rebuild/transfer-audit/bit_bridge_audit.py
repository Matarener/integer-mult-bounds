#!/usr/bin/env python3
"""Independent native/flow/lift audit for the delayed whole-cover BIT bridge.

No matrix or projector routines are imported from the BIT producer. The
shared finite-DAG audit supplies only its separately implemented integer
job scheduler. Apache-2.0; substantial OpenAI assistance.
"""
from collections import Counter
from fractions import Fraction as F
from hashlib import sha256
from itertools import product
from pathlib import Path
import gzip
import json
import struct

from finite_dag_audit import Rule,Compiler

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
BIT=HERE.parent/'bit'


def need(condition,message):
    if not condition:
        raise AssertionError(message)


def digest(path):
    return sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    path=Path(path); raw=path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix=='.gz' else raw)


def eye(n):
    return [[F(i==j) for j in range(n)] for i in range(n)]


def diag(values):
    return [[F(x) if i==j else F(0) for j in range(len(values))] for i,x in enumerate(values)]


def transpose(a):
    return list(map(list,zip(*a)))


def mul(a,b):
    result=[[F(0)]*len(b[0]) for _ in a]
    for i,row in enumerate(a):
        for k,value in enumerate(row):
            if value:
                for j,other in enumerate(b[k]):
                    if other:
                        result[i][j]+=value*other
    return result


def sub(a,b):
    return [[x-y for x,y in zip(row,other)] for row,other in zip(a,b)]


def inverse(a):
    n=len(a)
    rows=[[F(x) for x in row]+[F(i==j) for j in range(n)] for i,row in enumerate(a)]
    for j in range(n):
        pivot=next(i for i in range(j,n) if rows[i][j])
        rows[j],rows[pivot]=rows[pivot],rows[j]
        scale=rows[j][j];rows[j]=[x/scale for x in rows[j]]
        for i in range(n):
            if i!=j and rows[i][j]:
                scale=rows[i][j];rows[i]=[x-scale*y for x,y in zip(rows[i],rows[j])]
    result=[row[n:] for row in rows]
    need(mul(a,result)==eye(n),'Independent exact matrix inverse')
    return result


def conjugate(a,b):
    return mul(mul(a,b),inverse(a))


def kron(a,b):
    return [[x*y for x in row_a for y in row_b] for row_a in a for row_b in b]


def reversal(n):
    return [[F(i+j==n-1) for j in range(n)] for i in range(n)]


def block_diag(a,b):
    return [row+[F(0)]*len(b) for row in a]+[[F(0)]*len(a)+row for row in b]


def D(p):
    n=len(p); c=reversal(n)
    pc,cp=mul(p,c),mul(c,p)
    q=sub(eye(n),p);r=sub(eye(n),mul(cp,c))
    return [q[i]+pc[i] for i in range(n)]+[cp[i]+r[i] for i in range(n)]


def reduce_mod(a,modulus):
    return [[x.numerator*pow(x.denominator,-1,modulus)%modulus for x in map(F,row)] for row in a]


def rational_lift_checks():
    # Neither matcher nor its image projector is constrained to be orthogonal.
    s=[[F(1),F(1,2),F(0)],[F(0),F(1),F(1,3)],[F(1),F(0),F(1)]]
    g=[[F(1),F(1),F(0)],[F(0),F(1),F(1)],[F(1),F(0),F(2)]]
    records=[];wrong_tail=0
    for rank in (1,2):
        q=diag([1]*rank+[0]*(3-rank));p=conjugate(s,q)
        need(p!=transpose(p),'Nonorthogonal projector is exercised')
        need(mul(p,p)==p,'Actual rational split projector')
        for f in (1,2,3,4):
            n=3*f
            pf,qf=kron(p,eye(f)),kron(q,eye(f))
            gf,sf=kron(g,eye(f)),kron(s,eye(f))
            twist=block_diag(eye(n),kron(eye(3),reversal(f)))
            need(mul(mul(twist,kron(D(p),eye(f))),twist)==D(pf),
                 'Every-column lifting retains reversed within-column tail pairing')
            if f>1:
                need(kron(D(p),eye(f))!=D(pf),'Dropping the column reversal is a genuine negative control')
                wrong_tail+=1
            a=[F(2+i%8) for i in range(n)]
            gauge=diag(a+[F(1)]*n)
            parent=conjugate(gf,pf)
            child=conjugate(mul(gf,sf),qf)
            need(parent==child,'Whole ambient rank is preserved under matcher embedding')
            first=conjugate(gauge,D(parent))
            second=conjugate(gauge,D(sub(eye(n),parent)))
            full=conjugate(gauge,D(eye(n)))
            need(mul(first,second)==full and mul(second,first)==full,
                 'Source and complementary jobs give the full weighted endpoint on every spectator coordinate')
            need(first==conjugate(gauge,D(child)),'One arbitrary common diagonal A survives role-specific matching')
            need(reduce_mod(mul(first,second),121)==reduce_mod(full,121),
                 'The exact identity specializes to a genuine non-field local ring')
            records.append({'rank':rank,'column_count':f,'full_ambient_atoms':n})
    # The inherited ordinary wrapper uses two reversed calls and three paid
    # lower-bank additions. This verifies it with an actual nontrivial C_n.
    n=5;c=reversal(n);I=eye(n);Z=[[F(0)]*n for _ in range(n)]
    lower_minus=[I[i]+Z[i] for i in range(n)]+[[-x for x in I[i]]+I[i] for i in range(n)]
    lower_plus=[I[i]+Z[i] for i in range(n)]+[I[i]+I[i] for i in range(n)]
    final=[I[i]+Z[i] for i in range(n)]+[I[i]+[-x for x in I[i]] for i in range(n)]
    swap=[Z[i]+I[i] for i in range(n)]+[I[i]+Z[i] for i in range(n)]
    need(mul(final,mul(D(I),mul(lower_plus,mul(D(I),lower_minus))))==swap,
         'Exact two-call ordinary wrapper, including its paid address additions')
    return {'nonorthogonal_cases':records,'missing_column_reversal_controls':wrong_tail,
            'common_A_varies_across_coarse_axes_and_columns':True,
            'ordinary_wrapper_completed_reversed_calls':2,'ordinary_wrapper_paid_lower_bank_additions':3}


def nonintegral_cover_checks():
    modulus,prime=9,3
    def mm(a,b,mod=modulus):
        return [[sum(x*y for x,y in zip(row,column))%mod for column in zip(*b)] for row in a]
    def ii(a):
        det=(a[0][0]*a[1][1]-a[0][1]*a[1][0])%modulus
        d=pow(det,-1,modulus)
        return [[d*a[1][1]%modulus,-d*a[0][1]%modulus],[-d*a[1][0]%modulus,d*a[0][0]%modulus]]
    cover=[]
    for v in product(range(modulus),repeat=4):
        if (v[0]*v[3]-v[1]*v[2])%prime:
            cover.append([list(v[:2]),list(v[2:])])
    need(len(cover)==3888,'Complete independent GL2(Z/9Z) enumeration')
    matchers=[[[F(1),F(1,2)],[F(1),F(1)]],[[F(1),F(0)],[F(1,2),F(1)]]]
    bad_carry=None;total=0
    for rational in matchers:
        s=reduce_mod(rational,modulus);sinv=ii(s);images=set()
        for g in cover:
            h=mm(g,s);images.add(tuple(sum(h,[])))
            need(mm(h,sinv)==g,'Whole cover route has exact inverse for rational matcher')
            g0=[[x%prime for x in row] for row in g]
            h0=[[x%prime for x in row] for row in h]
            G=[[(x-y)//prime for x,y in zip(row,low)] for row,low in zip(g,g0)]
            raw=[[sum(x*y for x,y in zip(row,column)) for column in zip(*s)] for row in g0]
            carry=[[(x-y)//prime for x,y in zip(row,low)] for row,low in zip(raw,h0)]
            predicted=[[(x+y)%prime for x,y in zip(row,cr)] for row,cr in zip(mm(G,s,prime),carry)]
            actual=[[(x-y)//prime for x,y in zip(row,low)] for row,low in zip(h,h0)]
            need(actual==predicted,'Nonintegral matcher uses the actual q-adic carry')
            low_s=[[x%prime for x in row] for row in s]
            wrong_raw=[[sum(x*y for x,y in zip(row,column)) for column in zip(*low_s)] for row in g0]
            wrong_carry=[[(x-y)//prime for x,y in zip(row,low)] for row,low in zip(wrong_raw,h0)]
            wrong=[[(x+y)%prime for x,y in zip(row,cr)] for row,cr in zip(mm(G,s,prime),wrong_carry)]
            if actual!=wrong and bad_carry is None:
                bad_carry={'g':g,'matcher_mod9':s,'actual_high':actual,'incorrect_low_only_high':wrong}
            total+=1
        need(len(images)==len(cover),'Every arbitrary input row occurs exactly once after routing')
    need(bad_carry is not None,'Discarding higher digits of a rational matcher must fail')
    return {'ring_modulus':modulus,'rows':len(cover),'nonintegral_matchers':2,
            'exact_inverse_and_affine_carry_checks':total,'low_only_carry_counterexample':bad_carry}


def polynomial_controller(case):
    M=[[{0} if i==j else set() for j in range(6)] for i in range(6)]
    def add(i,j):
        M[i]=[a^b for a,b in zip(M[i],M[j])]
    def shift(i,term):
        M[i]=[{v^term for v in entry} for entry in M[i]]
    def scalar(program):
        for kind,i,j in program:
            if kind=='ADD':add(i,j)
            else:
                need(kind=='SWAP','Literal scalar adapter grammar');M[i],M[j]=M[j],M[i]
    scalar(case['factorization']['right_program'])
    for event in case['physical_events']:
        kind=event[0]
        if kind=='LOCAL':
            _,stage,pair,reverse=event;i,j=2*pair,2*pair+1
            if reverse:i,j=j,i
            M[j]=[a^{v^1 for v in b} for a,b in zip(M[j],M[i])]
            shift(i,1<<(stage+1));shift(j,1<<(stage+1))
        elif kind=='IDLE':
            _,pair,term=event;shift(2*pair,term);shift(2*pair+1,term)
        elif kind=='ADD':add(event[1],event[2])
        else:
            need(kind=='SWAP','Literal controller event');i,j=event[1:];M[i],M[j]=M[j],M[i]
    scalar(case['factorization']['left_program'])
    terms=case['factorization']['diagonal_monomials']
    need(all(M[i][j]==({terms[i]} if i==j else set()) for i in range(6) for j in range(6)),
         'Independent serialized R/body/L replay on every group-algebra coefficient')


def native_binding():
    binding=read(BIT/'BIT-P3-NATIVE-BINDING.json')
    for path,expected in binding['source_sha256'].items():
        need(digest(ROOT/path)==expected,'Pinned BIT native source '+path)
    data=read(BIT/'MIXED-PRODUCTIVE-BIT.json')
    case=next(c for c in data['candidates'] if c['pairs']==3 and c['keep_idle_mask']==43)
    polynomial_controller(case)
    folder=BIT/'sources/pr589-regenerated'
    word=read(folder/'WORD.json.gz')
    frames=read(folder/'records/frames.json')['frames']
    records=list(struct.iter_unpack('<6i',(folder/'records/249-records.bin').read_bytes()))
    projectors={}
    for key,frame in frames.items():
        basis=[[F(x) for x in row] for row in frame['B']]
        if basis:
            bt=transpose(basis);p=mul(mul(bt,inverse(mul(basis,bt))),basis)
        else:p=[[F(0)]*8 for _ in range(8)]
        need(mul(p,p)==p and sum(p[i][i] for i in range(8))==frame['dim'],
             'Independently reconstructed exact frame projector')
        projectors[int(key)]=p
    dims={int(key):frame['dim'] for key,frame in frames.items()}
    all_move_pairs={(y,c,f) for op,x,y,c,f,z in records if op==0}
    for low,high,rank in all_move_pairs:
        a,b=projectors[low],projectors[high]
        need(mul(a,b)==a and mul(b,a)==a,'Every actual transition has nested rational projectors')
        need(dims[high]-dims[low]==rank,'Every native residual has exactly the paid rank')
    endpoints=0
    for row in binding['ports']:
        port=row['port'];q=list(map(F,word['lines'][port]));p=[[x*y/4 for y in q] for x in q]
        a=[[F(x) for x in r] for r in row['complement_columns']]
        rho=[[F(x) for x in r] for r in row['chart_15']]
        need(row['root']==[str(x) for x in q],'Native port vector, not an arbitrary rank representative')
        need(mul(transpose(a),a)==eye(7) and mul(a,transpose(a))==sub(eye(8),p),
             'Actual rational complement basis')
        need(mul(rho,rho)==eye(15),'Each actual port chart is involutive')
        A8=diag([1]*8+[0]*7)
        target=block_diag(p,eye(7))
        need(mul(mul(rho,A8),rho)==target,'Exact embedded helper-active projector')
        need(mul(mul(rho,block_diag(p,[[F(0)]*7 for _ in range(7)])),rho)==
             block_diag(p,[[F(0)]*7 for _ in range(7)]),'Every port route fixes its true common line')
        for stage in row['lifted_routes']:
            s=stage['stage'];axes=stage['axes']
            need(axes==list(range(8))+list(range(8+7*(s-1),8+7*s)) and len(set(axes))==15 and max(axes)<50,
                 'Every one of the666 route embeddings has complete disjoint spectator coordinates')
            endpoints+=1
        need(projectors[word['start'][port]]==p and dims[word['start'][111+port]]==0,
             'Native main entrance')
        need(projectors[word['final'][port]]==eye(8) and
             projectors[word['final'][111+port]]==sub(eye(8),p),'Native main return')
    for role in range(222,661):
        need(dims[word['start'][role]]==0 and projectors[word['final'][role]]==eye(8),
             'Each helper is an autonomous full local8 job')
    # Independently replay native decoded scalar/COPY semantics and retain
    # literal ordered paid owner names for the generic integer compiler.
    streams={}
    for reverse in (False,True):
        values=[1<<i for i in range(661)]+[0]
        current=list(word['final'] if reverse else word['start'])+[-1]
        owned=None;stream=[];copies=0
        for op,x,y,c,f,z in (reversed(records) if reverse else records):
            if op==0:
                old,new=(c,y) if reverse else (y,c)
                need(current[x]==old,'Native paid transition reads its actual current frame')
                current[x]=new
                if f:stream.append((f,x))
            elif op==1:
                need(c==1 and current[x]==current[y]==f and x!=y,'Every ADD is pointwise at its actual common frame')
                need(owned is None or x!=owned,'Copied source stays immutable')
                values[x]^=values[y]
            elif op==(3 if reverse else 2):
                need(owned is None and y==661 and values[661]==0 and current[x]==c,'Actual private COPY entry')
                owned=x;values[661]=values[x];current[661]=f
                low,high=(c,f) if dims[c]<dims[f] else (f,c)
                need(mul(projectors[low],projectors[high])==projectors[low], 'COPY transition is a split projector request')
                rank=abs(dims[c]-dims[f]);need(rank==7,'Actual center paid rank')
                stream.append((rank,661));copies+=1
            else:
                need(op==(2 if reverse else 3) and owned==x and y==661 and values[y]==values[x],
                     'Owned COPY returns its exact payload before erasure')
                values[661]=0;current[661]=-1;owned=None
        need(owned is None and copies==9,'Nine complete owned episodes per native call')
        expected=[(1<<i)^((1<<(i-111)) if 111<=i<222 else 0) for i in range(661)]+[0]
        need(values==expected,'All arbitrary native input columns, including every helper')
        need(current[:661]==(word['start'] if reverse else word['final']),'All declared native physical endpoint frames')
        streams[reverse]=stream
    rounds=[]
    for event in case['physical_events']:
        if event[0]=='LOCAL':
            _,stage,pair,reverse=event
            for rank,role in streams[reverse]:
                if role==661:name='owned-C0'
                elif role<222:
                    side,port=divmod(role,111)
                    if reverse:side=1-side
                    name=f'main:{2*pair+side}:{port}'
                else:name=f'helper:{stage}:{role-222}'
                rounds.append((rank,name))
        elif event[0]=='IDLE':
            _,pair,term=event
            for stage in range(7):
                if term>>(stage+1)&1:
                    rounds += [(7,f'main:{side}:{port}') for side in (2*pair,2*pair+1) for port in range(111)]
    roles=[]
    for i,term in enumerate(case['factorization']['diagonal_monomials']):
        rank=(term&1)+7*(term>>1).bit_count()
        roles.extend((f'main:{i}:{port}',rank) for port in range(111))
    roles.extend((f'helper:{stage}:{port}',8) for stage in range(7) for port in range(439))
    rule=Rule(tuple(roles),tuple(rounds))
    need(rule.targets==Counter({int(k):v for k,v in case['targets'].items()}),'Source-bound BIT productive targets')
    need(Counter(r for r,n in rounds)==Counter({int(k):v for k,v in case['paid'].items()}),'Actual chronologically owned BIT paid rounds')
    need(sum(n=='owned-C0' for r,n in rounds)==63,'All63 copied-center requests are billed on owned fields')
    compiler=Compiler(rule);example=compiler.compile(50)
    need((example['width'],example['leaves'],example['units'])==(3739,186725,1),
         'Every source complement paid in fullrank50 completion')
    return {'native_frames':len(frames),'nested_native_move_pairs':len(all_move_pairs),
            'actual_ports':111,'embedded_nonidentity_port_routes':endpoints,
            'arbitrary_native_columns_per_direction':661,'global_productive_fields':3739,
            'independent_original_helpers':3073,'owned_COPY_paid_calls':63,
            'targets':dict(sorted(rule.targets.items())),
            'paid':dict(sorted(Counter(r for r,n in rounds).items())),
            'uniform_rank50':{k:str(v) if isinstance(v,F) else v for k,v in example.items() if k!='ordered_requirements'},
            'uniform_rank50_event_graph':compiler.trees[50].summary()}


def parameters():
    before,after,delta,old=F(69,25000),F(11,4000),F(3,1000),F(384599,10**10)
    gap=before-after
    need(gap==F(1,100000),'Actual strict cover gap')
    q_coefficient=256/gap
    need(q_coefficient==25600000,'Complete fallback prime coefficient')
    full_moment=(1+gap/4)/(1+gap/2)
    need(full_moment==F(400001,400002)<1,'Every bad-class fallback call fits, without subtracting good calls')
    saving=(1-delta)*after+delta*old
    need(saving==F(27418653797,10**13),'Changed atom exponent exact ordinary saving')
    need(delta>saving>F(27,10000) and delta<1-saving,'Linear adapters and complete borrowed stock are lower order')
    return {'precompile_saving':str(before),'covered_saving':str(after),'atom_power':str(delta),
            'prime_coefficient_for_N_power5':int(q_coefficient),'complete_fallback_moment_upper':str(full_moment),
            'ordinary_saving':str(saving),'ordinary_saving_admitted':'27/10000',
            'linear_adapter_gap':str(delta-saving),'borrowed_stock_log_gap':str(1-saving-delta)}


def main():
    native=native_binding();lift=rational_lift_checks();cover=nonintegral_cover_checks();params=parameters()
    paths=[BIT/'BIT-P3-NATIVE-BINDING.json',BIT/'MIXED-PRODUCTIVE-BIT.json',
           BIT/'DELAYED-COVER-BRIDGE.md',BIT/'BIT-ALLSIZE-PARAMETERS.json',
           ROOT/'notes/three-stage-cover-bit.tex',ROOT/'notes/three-stage-cover-rows.tex',
           ROOT/'notes/batched-bit-rows.tex']
    result={'schema':'independent-bit-delayed-cover-native-transfer-audit/1',
            'status':'PASS_NATIVE_ROLES_COMPLETE_DAG_ALL_COLUMN_PAIRING_COMMON_WEIGHT_AND_PAID_COVER',
            'source_sha256':digest(__file__),'sources':{str(p.relative_to(ROOT)):digest(p) for p in paths},
            'native_and_flow_binding':native,'tensor_and_weight_checks':lift,
            'nonintegral_local_ring_routes':cover,'allsize_parameters':params,
            'proof_scope':'Independent exact native binding and adversarial instances of the written universal cover proof; the sample uniformrank50 is not the limiting winner.',
            'remaining_inherited_hypotheses':['Permitted ordered-affine and fixed-rational cover routing implementations.',
              'The retained old ordinary leaf supplier and fixed-tape/analytic outer interfaces.']}
    (HERE/'BIT-BRIDGE-AUDIT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'status':result['status'],'native_productive_fields':3739,'paid_COPY_calls':63,
                      'uniform50_paid1':native['uniform_rank50']['leaves'],
                      'nonintegral_cover_checks':cover['exact_inverse_and_affine_carry_checks'],
                      'ordinary_saving':params['ordinary_saving']}))


if __name__=='__main__':
    main()
