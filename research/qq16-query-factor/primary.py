"""Current-output query-factor candidate audit.

Sparse arithmetic and source-route helpers adapted from the retained PR4105
primary verifier; no predecessor module is imported or executed.

Read only. The package driver authenticates all inputs before importing this
module. New work: Chris R / Clear1nsight with OpenAI Codex assistance,
Apache-2.0. No predecessor executable is imported.
"""
from collections import Counter
from fractions import Fraction as F
from functools import lru_cache
import gzip
import hashlib
import io
import json
from pathlib import Path
import tarfile

PKG = Path(__file__).resolve().parent
ROOT = PKG.parents[1]
ARCHIVE = 'research/community-frontier1042-audit/selected-replay.tar.gz'
PACKET = 'research/joint-query/certificate.json.gz'
I73 = tuple(1 << i for i in range(73))
SOURCE_PINS = {
    ARCHIVE: '22c3f4dce4b897a1d423d1388801933e288b6a6b1906cb15e1b16a5eb68db754',
    PACKET: 'a5ed85fac5ebf3c091482a113ab0d351eb5a7892fe2841a35e16017ec1ff49f7',
}


def need(ok, message):
    if not ok:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()


def digest(value):
    return hashlib.sha256(value).hexdigest()


def add(left, right, coefficient=F(1)):
    out = left.copy()
    for j, value in right.items():
        out[j] = out.get(j, F(0)) + coefficient*value
        if not out[j]:
            del out[j]
    return out


def multiply(left, right):
    result = []
    for row in left:
        out = {}
        for j, value in row.items():
            out = add(out, right[j], value)
        result.append(out)
    return result


def difference(left, right):
    return [add(a, b, -1) for a, b in zip(left, right)]


def rank(rows):
    pivots = {}
    for initial in rows:
        row = initial.copy()
        while row:
            pivot = min(row)
            if pivot not in pivots:
                coefficient = row[pivot]
                pivots[pivot] = {j: value/coefficient for j, value in row.items()}
                break
            row = add(row, pivots[pivot], -row[pivot])
    return len(pivots)


def register(token):
    kind, index = token
    need(kind in ('L', 'C') and type(index) is int and
         0 <= index < (704 if kind == 'L' else 8), 'local register namespace')
    return index + (704 if kind == 'C' else 0)


def scalar_step(rows, gate):
    op, target = gate[:2]
    at = register(target)
    if op == 'clear':
        need(at >= 704, 'only owned private values may be cleared')
        rows[at] = {}
    elif op == 'copy':
        rows[at] = rows[register(gate[2])].copy()
    elif op == 'scale':
        value = F(gate[2], gate[3])
        need(value, 'nonzero scalar scale')
        rows[at] = {j: v*value for j, v in rows[at].items()}
    else:
        need(op == 'add' and at != register(gate[2]), 'known non-self scalar add')
        rows[at] = add(rows[at], rows[register(gate[2])], F(gate[3], gate[4]))


def flatten(packet, name):
    events = []
    for event in packet['programs'][name]:
        if event[0] == 'retained_core':
            events.extend(packet['core_words'][event[1]])
        elif event[0] in ('cover_sweep', 'private_sweep'):
            events.extend(event[2])
        else:
            need(event[0] in ('cover_map', 'native_line'), 'known outer event')
            events.append(event)
    return events


def scalar_replay(events):
    """Audit 712 columns, then return only the invertible data block.

    Private columns are used to check erasure, never inverted.
    """
    rows = [{i: F(1)} for i in range(712)]
    for event in events:
        if event[0] == 'scalar':
            scalar_step(rows, event[1])
        else:
            need(event[0] in ('phase', 'climb', 'center', 'adapter',
                 'residual_adapter', 'cover_map', 'native_line'), 'known native event')
    need(rows[224:704] == [{i:F(1)} for i in range(224,704)], '480 arbitrary local helpers returned')
    need(rows[704:] == [{} for _ in range(8)], 'eight private outputs cleared')
    need(all(j < 224 for row in rows[:224] for j in row), 'data independent of helpers and private inputs')
    return rows[:224]


def act(matrix, vector):
    out = 0
    while vector:
        bit = vector & -vector
        out ^= matrix[bit.bit_length()-1]
        vector ^= bit
    return out


@lru_cache(None)
def product(left, right):
    return tuple(act(left, v) for v in right)


def orthogonal(matrix):
    return len(matrix) == 73 and all(
        ((matrix[i] & matrix[j]).bit_count() % 2) == (i == j)
        for i in range(73) for j in range(73))


def source_routes(phases, stage=1):
    result = []
    need(phases['m'] == 73 and len(phases['recipes']) == 112, 'actual native phase dimensions')
    for p, record in enumerate(phases['recipes']):
        need(record['port'] == p, 'source port order')
        local = tuple(record['idle_children'][0]['orthogonal_axes'][:8])
        need(len(local) == 8, 'eight actual local directions')
        # Swap these eight local axes with the requested external stage block.
        swaps = tuple(v ^ I73[9+8*(stage-1)+i] for i,v in enumerate(local))
        matrix = tuple(v ^ act(swaps, sum(((v & w).bit_count()%2)<<i
                                         for i,w in enumerate(swaps))) for v in I73)
        need(orthogonal(matrix) and product(matrix,matrix) == I73, 'actual stage orthogonal involution')
        need(act(matrix,record['q']) == record['q'], 'port normal fixed')
        result.append(matrix)
    return result


def load_sources():
    raw = {}
    for path, expected in SOURCE_PINS.items():
        raw[path] = (ROOT/path).read_bytes()
        need(digest(raw[path]) == expected, 'canonical source pin: '+path)
    names = {
        'template':'t16/global/hosted/GLOBAL-TEMPLATE.json.gz',
        'programs':'t16/global/base/providers/gauge44/LOCAL-PROGRAMS.json.gz',
        'phases':'t16/global/base/work/complex-nine-native/DATA-PHASES.json',
    }
    data, hashes = {}, {}
    with tarfile.open(fileobj=io.BytesIO(raw[ARCHIVE]),mode='r:gz') as archive:
        for label,name in names.items():
            members = [m for m in archive.getmembers() if m.name == name]
            need(len(members) == 1 and members[0].isfile(), 'unique regular source member')
            value = archive.extractfile(members[0]).read()
            hashes[name] = digest(value)
            data[label] = json.loads(gzip.decompress(value) if name.endswith('.gz') else value)
    data['packet'] = json.loads(gzip.decompress(raw[PACKET]))
    return data, hashes


def route(row, matrix):
    return {(j,product(matrix,h)):v for (j,h),v in row.items()}


def mix(rows, coefficients):
    out = {}
    for j,c in coefficients.items():
        out = add(out,rows[j],c)
    return out


def queries(rows, R, ports, routes):
    routed=[route(row,routes[p]) for p,row in enumerate(rows)]
    return [mix(routed,{p:c for p,c in rr.items() if p in ports}) for rr in R]


def scatter(query, K, ports, routes):
    return {p:route(mix(query,K[p]),routes[p]) for p in ports}


def prefix_replay(packet, rows):
    rows = [r.copy() for r in rows]+[{}for _ in range(488)]
    maps, core = 0, 0
    for event in packet['programs']['B_1_2']:
        if event[0]=='retained_core':
            need(event[1:3]==['backward',1], 'exact final lifted core')
            core += 1
            continue
        need(not core,'core last')
        block = event[2] if event[0] in ('cover_sweep','private_sweep') else [event]
        for item in block:
            if item[0]=='scalar':
                gate=item[1]
                touched=[gate[1]]+([gate[2]]if gate[0] in ('add','copy')else [])
                need(all(not 224<=register(token)<704 for token in touched),
                     'prefix never reads or writes arbitrary borrowed helpers')
                scalar_step(rows,gate)
            elif item[0]=='cover_map':
                _,token,label,_,_ = item
                need(not 224<=register(token)<704,'prefix map avoids borrowed helpers')
                matrix=tuple(packet['map_registry'][label]['owner_right_matrix_columns'])
                need(orthogonal(matrix),'literal owner map orthogonal')
                at=register(token);rows[at]=route(rows[at],matrix);maps+=1
            else:
                need(item[0]=='native_line','prefix native event')
                need(not 224<=register(item[1])<704,'prefix native line avoids borrowed helpers')
    need(core==1 and maps==528,'all literal prefix maps')
    need(all(not r for r in rows[224:]),'zero initial helpers/private returned in literal prefix')
    return rows[:224]


def candidate_word(packet, rho, rho2):
    A,T,U=(packet[k+'_ports'] for k in ('A','T','U'))
    R=[{int(j):F(v)for j,v in row.items()}for row in packet['R_rows']]
    K=[{int(j):F(v)for j,v in row.items()}for row in packet['K_rows']]
    registry={'I':list(I73)}
    for p in range(112):
        registry['r1_'+str(p)]=list(rho[p])
        registry['r2_'+str(p)]=list(rho2[p])
        registry['r21_'+str(p)]=list(product(rho2[p],rho[p]))
    names={name:['q'+str(base+j)for j in range(8)]
           for name,base in [('a',0),('f',8),('n',16),('t',24),('c',16)]}
    events=[]
    def clear(q):events.append(['clear',q])
    def emit(target,source,value,g='I'):
        if value:events.append(['add_view',target,source,str(value),g])
    for i in range(32):clear('q'+str(i))
    # a=R1 Y.
    for j,row in enumerate(R):
        for p,v in row.items():emit(names['a'][j],'Y'+str(p),v,'r1_'+str(p))
    # f=ell0,T P1,T a.
    for j,row in enumerate(R):
        for p in T:
            for k,v in K[p].items():emit(names['f'][j],names['a'][k],row.get(p,0)*v,'r1_'+str(p))
    # n=(R2-ell2,A)u, expanded without a materialized u bank.
    for j,row in enumerate(R):
        for p in T+U:
            emit(names['n'][j],'Y'+str(p),row.get(p,0),'r2_'+str(p))
            if p in T:emit(names['n'][j],'X'+str(p),row.get(p,0),'r2_'+str(p))
            for k,v in K[p].items():emit(names['n'][j],names['a'][k],-row.get(p,0)*v,'r21_'+str(p))
    # t=ell0,A(X_A+P2,A n).
    for j,row in enumerate(R):
        for p in A:
            emit(names['t'][j],'X'+str(p),row.get(p,0))
            for k,v in K[p].items():emit(names['t'][j],names['n'][k],row.get(p,0)*v,'r2_'+str(p))
    # n has had its last read; c uses the same eight owned physical fields.
    for field in names['n']:clear(field)
    for j,row in enumerate(R):
        for p in U:
            emit(names['c'][j],'X'+str(p),row.get(p,0))
            emit(names['c'][j],'Y'+str(p),row.get(p,0))
            for k,v in K[p].items():emit(names['c'][j],names['a'][k],-row.get(p,0)*v,'r1_'+str(p))
    for p in U:
        for k,v in K[p].items():
            emit('Y'+str(p),names['a'][k],-v,'r1_'+str(p))
            emit('Y'+str(p),names['f'][k],v)
    for p in sorted(A+T):emit('Y'+str(p),'X'+str(p),F(1))
    for p in sorted(A+T):
        clear('q32')
        for k,v in K[p].items():
            if p in T:emit('q32',names['t'][k],v)
            else:
                emit('q32',names['c'][k],-v)
                emit('q32',names['f'][k],-11*v)
                emit('q32',names['t'][k],-v)
        emit('q32','Y'+str(p),F(-1));emit('q32','X'+str(p),F(-1))
        emit('X'+str(p),'q32',F(1));clear('q32')
    for i in range(32):clear('q'+str(i))
    return {'schema':'qq16-current-query-factor-logical-word-v1',
      'interpretation':'add_view(t,s,c,g) means t(d)+=c*s(d*g) on logical coefficients; native realization must lift source and target frames.',
      'current_data_frames':{'X':'F17(d)','Y':'F17(d) C_(d q_p)^-1'},
      'owned_frame_choice':'F17(d) for all q0..q32',
      'owned_fields':['q'+str(i)for i in range(33)],'query_aliases':names,
      'owned_lifetime':'n and c alias q16..q23 after explicit clear; q32 is one selected-output delta temporary, cleared before and after each use. All owned fields end zero.',
      'preservation':'No pair1 field or borrowed helper is read or written. Current pair0 X_U is unchanged; other current pair0 data are intended outputs.',
      'routes':registry,'events':events}


def replay_candidate(word, input_rows):
    rows={side+str(p):input_rows[p+(112 if side=='Y' else 0)].copy()
          for side in ('X','Y')for p in range(112)}
    # Independent arbitrary dirty columns demonstrate every owned field is
    # explicitly erased before use and contributes nothing to final data.
    for i,field in enumerate(word['owned_fields']):rows[field]={(224+i,I73):F(1)}
    routes={name:tuple(matrix)for name,matrix in word['routes'].items()}
    for event in word['events']:
        if event[0]=='clear':
            need(event[1] in word['owned_fields'],'clear owns target');rows[event[1]]={}
        else:
            _,target,source,coefficient,g=event
            need(target!=source,'no self add-view')
            rows[target]=add(rows[target],route(rows[source],routes[g]),F(coefficient))
    need(all(not rows[field]for field in word['owned_fields']),'all33 owned fields return zero')
    return [rows[side+str(p)]for side in ('X','Y')for p in range(112)]


def current_inverse_check(word, R, K, A, T, U, rho, rho2):
    """Ordered contract inverse on224 FREE CURRENT fields, separately checked.

    Verify the forward contracts on the recovered intermediate/original data
    before comparing the literal repair. This does not use a scalar224 inverse
    or a predecessor decoder word.
    """
    ports=list(range(112));zero=[I73]*112
    current=[{(j,I73):F(1)}for j in range(224)]
    X,Y=current[:112],current[112:]
    a=queries(Y,R,ports,rho)
    ka=scatter(a,K,U,rho)
    ellx=queries(X,R,T,rho)
    pt=scatter([add(ellx[j],a[j],-1)for j in range(8)],K,T,rho)
    u=[add(Y[p],ka[p],-1) if p in U else
       add(Y[p],pt[p]) if p in T else Y[p] for p in ports]
    n=queries(u,R,U+T,rho2);pn=scatter(n,K,A,rho2)
    yf=[add(u[p],pn[p],-1) if p in A else u[p]for p in ports]
    pat=scatter(a,K,T,rho)
    xf=[add(X[p],yf[p]) if p in U else
        add(add(X[p],u[p]),yf[p],-1) if p in A else pat[p]for p in ports]
    # Reapply the actual B contract to recovered xF,yF.
    future=queries(yf,R,U+T,rho2);pf=scatter(future,K,A,rho2)
    eu=[add(yf[p],pf[p]) if p in A else yf[p]for p in ports]
    ar=queries(xf,R,T,rho);b=queries(eu,R,ports,rho)
    ku=scatter(ar,K,U,rho)
    t11=scatter([add(b[j],ar[j],11)for j in range(8)],K,T,rho)
    t12=scatter([add(b[j],ar[j],12)for j in range(8)],K,T,rho)
    yr=[eu[p] if p in A else add(yf[p],ku[p]) if p in U else
        add(eu[p],t11[p],-1) for p in ports]
    xr=[add(xf[p],yf[p],-1) if p in U else
        add(add(xf[p],yf[p]),eu[p],-1) if p in A else t12[p] for p in ports]
    need(xr+yr==current,'ordered B inverse right-composition on224 free current fields')
    f=queries(xf,R,T,zero);t=queries(xf,R,A,zero);c=queries(xf,R,U,zero)
    kf=scatter(f,K,U,zero);xt=scatter(t,K,T,zero)
    xa=scatter([add(add({},f[j],-11),add(c[j],t[j]),-1)for j in range(8)],K,A,zero)
    oldx=[add(xf[p],kf[p]) if p in U else xt[p] if p in T else xa[p]for p in ports]
    oldy=[add(yf[p],xf[p],-1) if p in U else add(add(yf[p],xf[p]),oldx[p],-1)for p in ports]
    # Reapply the actual F contract to the recovered original data.
    fr=queries(oldx,R,ports,zero);kfr=scatter(fr,K,U,zero)
    selected_t=queries(oldx,R,T,zero)
    far=scatter(selected_t,K,A,zero);ftr=scatter(fr,K,T,zero)
    xfr=[add(oldx[p],kfr[p],-1) if p in U else far[p] if p in A else ftr[p]for p in ports]
    yfr=[add(oldy[p],xfr[p]) if p in U else add(add(oldx[p],oldy[p]),xfr[p],-1)for p in ports]
    need(xfr+yfr==xf+yf,'ordered F inverse right-composition on224 free current fields')
    selected=[add({},row,-1)for row in oldy]+[add(x,y)for x,y in zip(oldx,oldy)]
    need(replay_candidate(word,current)==selected,
         'literal H equals G Q inverse on224 FREE CURRENT fields')
    return {'B_inverse_then_B':'identity on224 free current fields',
            'F_inverse_then_F':'identity on recovered224 intermediate fields',
            'literal_H_on_free_current':'G Q_inverse, exact ordered owner algebra',
            'inverse_domain':'persistent data fields only; no private-clearing map inverted'}


def compute():
    data,member_hashes=load_sources()
    template=data['template']
    calls=[template['calls'][i]for i in (0,4)]
    need([(c['replica'],c['pair'],c['stage'],c['orientation'])for c in calls]==
         [(0,0,0,'forward'),(0,0,1,'backward')],'same actual first source pair')
    for stage,call in enumerate(calls):
        need(call['provider_id']=='gauge44' and
             digest(canonical(data['programs'][call['orientation']]))==call['local_program_sha256'],
             'actual selected provider and local word')
        need(call['owners'][:224]==[[p,[1,stage,p%112]]for p in range(224)],
             'actual paired data owner paths')
    bridge=template['execution_schedule'][6]
    need(bridge['kind']=='bridge' and bridge['replica']==0 and bridge['source_event']==3 and
         bridge['src']==1 and bridge['dst']==0 and bridge['coefficient']==1,
         'same actual next full bridge')
    packet=data['packet'];A,T,U=(packet[k+'_ports']for k in ('A','T','U'))
    S=sorted(A+T);ports=list(range(112))
    R=[{int(j):F(v)for j,v in row.items()}for row in packet['R_rows']]
    K=[{int(j):F(v)for j,v in row.items()}for row in packet['K_rows']]
    for subset,scale in ((A,1),(T,1),(U,12)):
        need([[sum(R[i].get(p,0)*K[p].get(j,0)for p in subset)
               for j in range(8)]for i in range(8)]==
             [[F(scale*(i==j))for j in range(8)]for i in range(8)],'query right inverse and complement constants')
    rho=source_routes(data['phases']);rho2=source_routes(data['phases'],2);zero_routes=[I73]*112
    known_maps={tuple(record['owner_right_matrix_columns'])for record in packet['map_registry'].values()}
    need(all(matrix in known_maps for matrix in rho+rho2),
         'both independently derived stage routes occur in the actual packet')
    qf=scalar_replay(flatten(packet,'F_0'))
    gf,gb=(scalar_replay(data['programs'][name])for name in ('forward','backward'))
    gpair=multiply(gb,gf)
    core=scalar_replay(packet['core_words']['backward'])
    ident=[{i:F(1)}for i in range(224)]
    for p in ports:
        expected=add(ident[p],ident[112+p],-1)
        for j,v in K[p].items():
            expected=add(expected,{112+t:c for t,c in R[j].items()},v)
        need(core[p]==expected and core[112+p]==ident[112+p],'literal scalar backward core I-KR factor')
    qfrows=[{(j,I73):v for j,v in row.items()}for row in qf]
    pre=prefix_replay(packet,qfrows)
    bquery=queries(pre[112:],R,ports,rho)
    bscatter=scatter(bquery,K,ports,rho)
    Q=[add(add(pre[p],pre[112+p],-1),bscatter[p])for p in ports]+pre[112:]
    X,Y=Q[:112],Q[112:]
    # All queries here are derived from current Q outputs, not retained old data.
    a=queries(Y,R,ports,rho)
    xft=scatter(a,K,T,rho)
    f=queries([xft.get(p,{})for p in ports],R,T,zero_routes)
    ka=scatter(a,K,U,rho)
    u=[add(Y[p],ka[p],-1) if p in U else
       Y[p] if p in A else add(add(Y[p],X[p]),xft[p],-1)for p in ports]
    n=queries(u,R,T+U,rho2)
    en=scatter(n,K,A,rho2)
    xf=[add(add(X[p],Y[p]),ka[p],-1) if p in U else
        add(X[p],en[p]) if p in A else xft[p] for p in ports]
    t=queries(xf,R,A,zero_routes)
    c=queries(xf,R,U,zero_routes)
    xoT=scatter(t,K,T,zero_routes)
    xoA=scatter([add(add({},f[j],-11),add(c[j],t[j]),-1)for j in range(8)],K,A,zero_routes)
    kf=scatter(f,K,U,zero_routes)
    outY=[add(add(Y[p],ka[p],-1),kf[p]) if p in U else
          add(X[p],Y[p]) for p in ports]
    outX=[X[p] if p in U else add((xoA if p in A else xoT)[p],outY[p],-1)for p in ports]
    G=[{(j,I73):v for j,v in row.items()}for row in gpair]
    need(outX+outY==G,'full-cover all224 free-input pair identity')
    word=candidate_word(packet,rho,rho2)
    need(json.loads((PKG/'CANDIDATE-WORD.json').read_text())==word,'committed literal factor word matches constructor')
    need(replay_candidate(word,Q)==G,'literal current-output factor word repairs all224 columns and erases all33 dirty owned fields')
    current_check=current_inverse_check(word,R,K,A,T,U,rho,rho2)
    need(len(a)==len(f)==len(n)==len(c)==len(t)==8,'five eight-field query families')
    need(any(h!=I73 for row in Q for j,h in row),'nonconstant owner paths retained')
    return {'status':'PASS_FULL_COVER_PAYLOAD_CONSTANT_FACTOR',
       'source_archive_members':member_hashes,
       'query_basis':['a=R1 Y_current','f=ell0,T P1,T a',
          'n=(R2-ell2,A)(Y-K1,U a+P1,T(ell1,T X-a))',
          't=ell0,A(X_current,A+P2,A n)',
          'c=R0,U(X_current,U+Y_current,U-K1,U a)'],
       'query_families':5,'query_records':40,'owned_physical_fields':33,'free_input_fields':224,
       'literal_word_events':dict(Counter(e[0]for e in word['events'])),
       'candidate_word_sha256':digest(canonical(word)),
       'free_current_inverse_check':current_check,
       'checked_endpoint':'all112 X and all112 Y, full actual owner ring, payload character0',
       'retained_literal_prefix_maps':528,
       'total_Q_operator_terms':sum(map(len,Q)),
       'native_status':'UNESTABLISHED: the logical ADD-view word needs an exact paid native phase and owner lift. Its commonF17 query-frame declaration is not a native implementation.',
       'source_binding':{'serialized_calls':[0,4],'hosted_bridge_event':6,
          'bridge':bridge,'program_sha256':[c['local_program_sha256']for c in calls]},
       'reuse':'Sparse exact arithmetic, local scalar-replay, and source-route helpers adapted from retained PR4105-primary.py; no predecessor executable is imported or run.',
       'ordinary_X_unchanged':all(outX[p]==X[p]for p in U),
       'query_operator_terms':[sum(map(len,q))for q in (a,f,n,c,t)],
       'comparison_scope':'Source pair current data, before unchanged full bridge; pair1 inputs and all borrowed helpers must remain unchanged in a paid implementation.',
       'not_a_paid_supplier':True}

if __name__=='__main__':
    print(json.dumps(compute(),sort_keys=True,indent=2))
