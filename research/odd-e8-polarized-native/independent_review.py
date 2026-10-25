"""Read-only independent review of the emitted one-direction H_ab word.

Does not import module.py or frame_tools.py, and never regenerates source data.
The pinned primitive Pauli compiler is reused, with a fresh sparse amplitude
evaluator and explicit analytic phase proof for the four full conjugations.
"""
from pathlib import Path
from fractions import Fraction as F
from collections import Counter, defaultdict
from hashlib import sha256
import argparse, gzip, importlib.util, json, sys

HERE=Path(__file__).resolve().parent
sys.dont_write_bytecode=True

def require(value, why):
    if not value: raise ValueError(why)

def read(path): return json.loads(path.read_bytes())

def gbasis(rows):
    piv={}
    for value in rows:
        for pivot in sorted(piv, reverse=True):
            if value>>pivot&1: value^=piv[pivot]
        if value: piv[value.bit_length()-1]=value
    for pivot in sorted(piv):
        for other in piv:
            if other!=pivot and piv[other]>>pivot&1: piv[other]^=piv[pivot]
    return tuple(piv[p] for p in sorted(piv,reverse=True))

def parity(value): return value.bit_count()&1
def dot(a,b): return parity(a&b)
def contains(b,v): return len(gbasis(list(b)+[v]))==len(b)

def sparse(circuit,n=25):
    # Literal Gaussian-integer arithmetic, independent of author's evaluator.
    values={0:(1,0)}; denominator=0
    for gate in circuit:
        kind=gate[0]
        if kind=='P':
            rows=gate[1]
            values={sum(dot(row,x)<<i for i,row in enumerate(rows)):a
                    for x,a in values.items()}
        elif kind=='X': values={x^gate[1]:a for x,a in values.items()}
        elif kind in ('D','phase'):
            dest={}
            for x,(a,b) in values.items():
                if kind=='phase': phase=gate[1]
                else:
                    Q,alpha=gate[1:]
                    phase=sum(alpha[i] for i in range(n) if x>>i&1)
                    phase+=2*sum(dot(Q[i]>>(i+1),x>>(i+1))
                                  for i in range(n) if x>>i&1)
                dest[x]=[(a,b),(-b,a),(-a,-b),(b,-a)][phase%4]
            values=dest
        elif kind=='C':
            q,sign=gate[1:];dest={}
            for x in values.keys()|{x^q for x in values}:
                a,b=values.get(x,(0,0));c,d=values.get(x^q,(0,0))
                # ((1+sign*i) I +(1-sign*i) X_q)/2
                out=(a-sign*b+c+sign*d,b+sign*a+d-sign*c)
                if out!=(0,0):dest[x]=out
            values=dest;denominator+=1
        else: raise ValueError('unknown gate '+str(kind))
        require(len(values)<=65536,'independent sparse support bound')
        while denominator and all(not(a&1) and not(b&1) for a,b in values.values()):
            denominator-=1;values={x:(a//2,b//2) for x,(a,b) in values.items()}
    return values,denominator

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--package',type=Path,default=HERE,help='Module package; default is this script directory')
    parser.add_argument('--receipt',type=Path,default=None,help='Review receipt; default PACKAGE/INDEPENDENT-REVIEW.json')
    parser.add_argument('--write',action='store_true',help='Explicitly author the review receipt')
    args=parser.parse_args();ROOT=args.package.resolve()
    receipt_path=args.receipt.resolve()if args.receipt else ROOT/'INDEPENDENT-REVIEW.json'
    raw=(ROOT/'PROGRAM.json.gz').read_bytes();program=json.loads(gzip.decompress(raw))
    canonical_payload=(json.dumps(program,sort_keys=True,separators=(',',':'))+'\n').encode()
    receipt=read(ROOT/'MODULE.json');n=program['axis_dimension'];require(n==25,'dimension25')
    pins={p:sha256((ROOT/'inputs'/p).read_bytes()).hexdigest() for p in receipt['source_pins']}
    require(pins==receipt['source_pins'],'all source pins')
    require(sha256(canonical_payload).hexdigest()==receipt['program_payload_sha256']==receipt['proof_relevant_digest'],'emitted canonical scientific word pin')
    spec=importlib.util.spec_from_file_location('review_primitive_clifford',ROOT/'inputs/clifford_exact.py')
    ce=importlib.util.module_from_spec(spec);sys.modules[spec.name]=ce;spec.loader.exec_module(ce)
    def literal(word):
        value=ce.ident(n)
        for gate in word:
            kind=gate[0]
            if kind=='P':part=ce.perm(n,gate[1])
            elif kind=='X':part=ce.xgate(n,gate[1])
            elif kind=='D':part=ce.diag(n,gate[1],gate[2])
            elif kind=='phase':part=ce.Op(n,ce.identity(n),[tuple(gate)])
            else:
                require(kind=='C','known literal primitive');part=ce.cgate(n,gate[1],gate[2])
            value=value.then(part)
        return value
    def exact(a,b,label):
        require(a.tab==b.tab,'signed tableau '+label)
        require(sparse(a.circuit)==sparse(b.circuit),'absolute phase '+label)
    definitions=program['monomial_and_frame_definitions']
    for key,word in definitions.items():
        require(sha256(json.dumps(word,separators=(',',':')).encode()).hexdigest()==key,'literal definition hash')
    def mono(word):require(all(g[0]in ('P','D','X','phase') for g in word),'no Fourier hidden in wrapper')
    def native(cols):
        G=ce.transpose(cols,n);inverse=ce.inv(G,n);columns=ce.transpose(inverse,n)
        Q=tuple((1<<i)^sum(dot(a,b)<<j for j,b in enumerate(columns)) for i,a in enumerate(columns))
        return ce.perm(n,G).then(ce.diag(n,Q))
    def frame(cols,rank):
        K=native(cols)
        return K.adjoint().then(ce.fourier(n,range(rank))).then(K)
    normal=read(ROOT/'inputs/NORMALIZERS.json');labels=[p['q']for p in normal['ports']]
    orth=program['orthonormal_basis_in_raw27']
    require(len(orth)==25 and all(dot(a,b)==int(i==j) for i,a in enumerate(orth) for j,b in enumerate(orth)),'explicit physical I25 basis')
    def qlabel(p):
        a,b,c=p//112**2,p//112%112,p%112
        value=labels[a]|(labels[b]<<9)|(labels[c]<<18)
        q=sum(dot(value,b)<<j for j,b in enumerate(orth))
        inverse=0
        for j,b in enumerate(orth):
            if q>>j&1:inverse^=b
        require(inverse==value and dot(q,q)==1,'actual norm-one port isometry')
        return q
    channels=json.loads(gzip.decompress((ROOT/'inputs/POLARIZED-CHANNELS.json.gz').read_bytes()))['channels']
    source_groups={};reader_groups={};group_by_key=defaultdict(list)
    expected=defaultdict(dict)
    for j,ch in enumerate(channels):
        S=gbasis(qlabel(p) for p,a,b in ch['source']);R=gbasis(qlabel(p) for p,a,b in ch['reader'])
        require(len(S)==len(R)==8 and all(not dot(a,b)for a in S for b in R),'orthogonal8space pair')
        key=(S,R);group_by_key[key].append(j)
        for name,lookup in [('source',source_groups),('reader',reader_groups)]:
            require(len(ch[name])==68,'68-port polarized channel support')
            for p,a,b in ch[name]:
                require(p not in lookup or lookup[p]==key,'one common frame per literal port');lookup[p]=key
        for p,a,b in ch['reader']:
            row=expected[p]
            for q,c,d in ch['source']:
                row[q]=row.get(q,F(0))+F(a,b)*F(c,d)
                if not row[q]:del row[q]
    require(len(channels)==64 and len(group_by_key)==4 and all(len(v)==16 for v in group_by_key.values()),'64channels only4pairs16each')
    require(len(source_groups)==len(reader_groups)==512 and not(set(source_groups)&set(reader_groups)),'1024 independent source/reader roles')
    require(program['field_roles']=={str(p):['X'if p in source_groups else'Y',p]for p in set(source_groups)|set(reader_groups)},'literal X/Y role namespace')
    Rfull=ce.fourier(n);source_paths=0;reader_paths=0;path_ops={};chart_ops={}
    full_anchors=[]
    for group in program['groups']:
        gi=str(group['group']);S=group['S8_basis25'];R=group['R8_basis25'];key=(gbasis(S),gbasis(R))
        require(key in group_by_key and group['channels']==group_by_key[key],'emitted group channels')
        require(set(group['source_ports'])=={p for p,k in source_groups.items()if k==key},'source group partition')
        require(set(group['reader_ports'])=={p for p,k in reader_groups.items()if k==key},'reader group partition')
        require(len(group['source_ports'])==len(group['reader_ports'])==128,'128-port blocks')
        common=program['common_paths'][gi];Phi=literal(definitions[common['S8_frame']]);cols=ce.basis_extend(S,n);K=native(cols)
        exact(Phi,frame(cols,8),'S8 defining frame')
        chart_ops['S8:'+gi]=Phi
        entry=common['reader_ground_to_S8'];post=definitions[entry['after_monomial']];pre=definitions[entry['before_monomial']]
        mono(pre);mono(post)
        require(pre==json.loads(json.dumps(K.adjoint().circuit)) and post==json.loads(json.dumps(K.circuit)),'reader entry literal factors')
        require(entry['child_axes']==list(range(8)) and entry['rank']==8,'reader8 child')
        exit=common['source_S8_to_full25'];pre=definitions[exit['before_monomial']];post=definitions[exit['after_monomial']]
        mono(pre);mono(post)
        require(pre==json.loads(json.dumps(K.adjoint().circuit)),'full exit literal K inverse')
        require(exit['child_axes']==list(range(8,25)) and exit['rank']==17,'full exit17child')
        T=literal(post);expected_T=Rfull.adjoint().then(K).then(Rfull)
        require(T.tab==expected_T.tab,'native full conjugation signed tableau')
        inversecols=ce.transpose(ce.inv(ce.transpose(cols,n),n),n)
        d=sum(((x.bit_count()//2)&1)<<j for j,x in enumerate(inversecols));phase=(-d.bit_count())%4
        require(sparse(T.circuit)==({d:[(1,0),(0,1),(-1,0),(0,-1)][phase]},0),'native anchor exact monomial zero column')
        full_anchors.append({'offset':d,'phase':phase})
        for p in group['source_ports']:
            q=qlabel(p);qframe=ce.canonical_frame(n,[q]);flag=[q]
            source_frame=program['source_entry_frames'][str(p)]
            require(source_frame['q25']==q,'source actual q entrance')
            exact(literal(definitions[source_frame['literal_frame_word']]),qframe,'source entrance literal frame')
            for v in S:
                if not contains(gbasis(flag),v):flag.append(v)
            require(len(flag)==8,'q contained in source S8')
            cols_q=ce.basis_extend(flag,n);Kq=native(cols_q);small=frame(cols_q,1);wide=frame(cols_q,8)
            path=program['source_entry_paths'][str(p)];pre=definitions[path['before_monomial']];post=definitions[path['after_monomial']]
            mono(pre);mono(post);require(pre[-2:]==json.loads(json.dumps(Kq.adjoint().circuit)) and post[:2]==json.loads(json.dumps(Kq.circuit)),'source nested flag inverse factors')
            exact(literal(pre[:-2]),qframe.adjoint().then(small),'source before gauge')
            exact(literal(post[2:]),wide.adjoint().then(Phi),'source after gauge')
            require(path['child_axes']==list(range(1,8)) and path['rank']==7,'source7child')
            chart_ops['line:'+str(q)]=qframe;source_paths+=1
        for p in group['reader_ports']:
            q=qlabel(p);endpoint=program['reader_endpoint_frames'][str(p)];V=endpoint['qperp24_basis25']
            require(endpoint['q25']==q and len(gbasis(V))==24 and all(not dot(q,v)for v in V),'reader actual qperp24 endpoint')
            require(all(contains(gbasis(V),v)for v in S),'source S8 in reader cap')
            cols_v=ce.basis_extend(V,n);Kv=native(cols_v);low=frame(cols_v,8);target=frame(cols_v,24)
            require(V[:8]==S,'reader flag preserves common S8 prefix')
            require(literal(definitions[endpoint['literal_frame_word']]).circuit==target.circuit,'reader endpoint literal target frame')
            path=program['reader_exit_paths'][str(p)];pre=definitions[path['before_monomial']];post=definitions[path['after_monomial']]
            mono(pre);mono(post)
            require(pre[-2:]==json.loads(json.dumps(Kv.adjoint().circuit)) and post==json.loads(json.dumps(Kv.circuit)),'reader nested flag inverse factors')
            exact(literal(pre[:-2]),Phi.adjoint().then(low),'reader before gauge')
            require(path['child_axes']==list(range(8,24)) and path['rank']==16,'reader16child')
            chart_ops['qperp24:'+str(p)]=target;reader_paths+=1
    require(full_anchors==[{k:a[k]for k in ['offset','phase']}for a in program['native_full_conjugate_anchors']],'all4emitted native anchors')
    first=program['groups'][0];first_s=chart_ops['S8:'+str(first['group'])]
    wrong_frame=ce.canonical_frame(n,first['R8_basis25'])
    transport=first_s.adjoint().then(wrong_frame)
    wrong_frame_rank=ce.rank([x for x,z,p in transport.tab[n:]])
    require(wrong_frame_rank==4,'actual wrong S8/R8 chart needs rank4 transport')
    first_path=program['source_entry_paths'][str(first['source_ports'][0])]
    phase_word=literal(definitions[first_path['before_monomial']]).then(ce.fourier(n,first_path['child_axes'])).then(literal(definitions[first_path['after_monomial']]))
    phase_mutant=phase_word.then(ce.Op(n,ce.identity(n),[('phase',1)]))
    require(phase_word.tab==phase_mutant.tab and sparse(phase_word.circuit)!=sparse(phase_mutant.circuit),'actual phase mutation rejected independently')
    first_add=next(i for i,e in enumerate(program['program'])if e[0]=='ADD')
    first_channel=program['program'][first_add:first_add+204]
    require(all(e[0]=='ADD'for e in first_channel),'one204ADDchannel literal slice')
    def local_replay(seq):
        values={p:{p:F(1)}for p in set(source_groups)|set(reader_groups)};values['C0']={}
        for _,dst,src,a,b,chart in seq:
            for p,c in values[src].items():
                v=values[dst].get(p,F(0))+F(a,b)*c
                if v:values[dst][p]=v
                else:values[dst].pop(p,None)
        return values
    require(not local_replay(first_channel)['C0']and bool(local_replay(first_channel[:-1])['C0']),'actual missing uncompute rejected independently')
    roles=set(source_groups)|set(reader_groups);rows={p:{p:F(1)}for p in roles};rows['C0']={}
    charts={p:'line:'+str(qlabel(p))if p in source_groups else'ground'for p in roles};charts['C0']='ground'
    paid=Counter();ordinary=Counter();seen_adds=0
    growth={k:{'peak_coefficient_l1':F(0),'max_dyadic_denominator_exponent':0,
               'peak_l1_event':None,'max_denominator_event':None}for k in ['source','reader','owned_C0']}
    def measure(p,event_index):
        family='owned_C0'if p=='C0'else('source'if p in source_groups else'reader')
        row=rows[p];l1=sum(map(abs,row.values()),F(0));den=0
        for value in row.values():
            denominator=value.denominator
            require(denominator&(denominator-1)==0,'dyadic row coefficients')
            den=max(den,denominator.bit_length()-1)
        record=growth[family]
        if l1>record['peak_coefficient_l1']:record['peak_coefficient_l1']=l1;record['peak_l1_event']=event_index
        if den>record['max_dyadic_denominator_exponent']:record['max_dyadic_denominator_exponent']=den;record['max_denominator_event']=event_index
    for p in rows:measure(p,-1)
    for event_index,event in enumerate(program['program']):
        kind=event[0]
        if kind=='PAID_PATH':
            _,p,old,new,path=event
            require(charts[p]==old,'paid edge actual entrance chart')
            paid[path['rank']]+=1
            for name in ['before_monomial','after_monomial']:
                word=definitions[path[name]];mono(word);ordinary.update(g[0]for g in word)
            if old.startswith('line:'):require(path==program['source_entry_paths'][str(p)],'exact source path reference')
            elif new=='full25':require(path==program['common_paths'][old.split(':')[1]]['source_S8_to_full25'],'exact full path reference')
            elif old=='ground':require(path==program['common_paths'][new.split(':')[1]]['reader_ground_to_S8'],'exact reader entry reference')
            else:require(path==program['reader_exit_paths'][str(p)],'exact reader exit reference')
            charts[p]=new
        elif kind=='ADD':
            _,dst,src,a,b,chart=event
            require(charts[dst]==charts[src]==chart,'literal ADD common physical frame')
            for p,c in rows[src].items():
                value=rows[dst].get(p,F(0))+F(a,b)*c
                if value:rows[dst][p]=value
                else:rows[dst].pop(p,None)
            measure(dst,event_index)
            ordinary[kind]+=1;seen_adds+=1
        elif kind=='ZERO_RETAG':
            _,p,old,new=event
            require(p=='C0'and not rows[p]and charts[p]==old,'owned zero retag true precondition')
            charts[p]=new;ordinary[kind]+=1
        elif kind=='CLEAR_ZERO':
            _,p,chart=event
            require(p=='C0'and charts[p]==chart and not rows[p],'CLEAR only on already exact zero owned scratch')
            ordinary[kind]+=1
        else: raise ValueError('unknown typed event')
    require(paid==Counter({7:512,8:512,16:512,17:512}),'independent full Gaussian bill')
    require({str(k):v for k,v in paid.items()}==receipt['paid_profile'],'published Gaussian bill')
    require(dict(ordinary)==receipt['ordinary_literal_gate_histogram'],'complete literal ordinary counts')
    for p in source_groups:require(rows[p]=={p:F(1)} and charts[p]=='full25','source arbitrary independent original retained')
    for p in reader_groups:
        goal={p:F(1),**expected[p]}
        require(rows[p]==goal and charts[p]=='qperp24:'+str(p),'reader exact arbitrary independent H_ab endpoint')
    require(not rows['C0']and charts['C0']=='ground','owned scratch zero ground returned')
    require(program['logical_endpoint_rows']=={'source_identity_fields':sorted(source_groups),
        'reader_rows':{str(p):[[s,q.numerator,q.denominator]for s,q in sorted(rows[p].items())]for p in sorted(reader_groups)},
        'owned_C0':[]},'literal published endpoint rows')
    result={'status':'PASS_INDEPENDENT_LOCAL_HAB_TYPED_WORD_REVIEW','source_pins':pins,
        'proof_relevant_program_payload_sha256':sha256(canonical_payload).hexdigest(),
        'environment_metadata':{'program_container_sha256':sha256(raw).hexdigest(),'program_container_bytes':len(raw)},
        'module_py_sha256':sha256((ROOT/'module.py').read_bytes()).hexdigest(),
        'frame_tools_py_sha256':sha256((ROOT/'frame_tools.py').read_bytes()).hexdigest(),
        'polarized_channels':64,'orthogonal8space_pairs':4,'channels_per_pair':16,
        'unique_group_source_fields':512,'unique_group_reader_fields':512,'source_entry_gauges_exact':source_paths,
        'reader_exit_gauges_exact':reader_paths,'native_full_anchors':full_anchors,
        'literal_program_events':len(program['program']),'ordinary':dict(ordinary),'paid':dict(paid),
        'exact_logical_coefficient_growth':{family:{**record,'peak_coefficient_l1':str(record['peak_coefficient_l1'])}for family,record in growth.items()},
        'growth_scope':'At every literal module event, each physical row is its unitary chart times the logical row. If each original entrance norm is at most M, row norm is at most reported peak l1 times M. This does not by itself bound accumulated rounding errors or complete-caller precision.',
        'all1024original_logical_endpoints':True,'zero_scratch_lifecycle':True,
        'independent_mutation_controls':{'same_tableau_phase_i_rejected_by_absolute_column':True,'S8_to_R8_requires_rank':wrong_frame_rank,'omitting_actual_uncompute_leaves_nonzero_owned_C0':True},
        'universal_native_anchor_proof':'Written in REVIEW.md; exact signed tableau and analytic phase, not finite-width extrapolation.',
        'independence':'Does not call module.py, frame_tools.py or check.py calculation; primitive pinned Pauli compiler reused. Fresh sparse Gaussian-integer column evaluator.',
        'scope':'One-direction 25D H_ab local ABI only; source Phi_line entrances are supplied; coupled reader endpoints carry no autonomous Gaussian-job credit; no 20D-to25D free connection; no K-core or full caller/precision/compiler/kappa/upstream acceptance claim.'}
    encoded=json.dumps(result,indent=2,sort_keys=True)+'\n'
    if args.write:receipt_path.write_text(encoded)
    else:
        old=read(receipt_path);old.pop('environment_metadata',None)
        new=json.loads(encoded);new.pop('environment_metadata',None)
        require(old==new,'frozen scientific independent result; gzip container is environmental')
    print(json.dumps({k:result[k]for k in ['status','orthogonal8space_pairs','source_entry_gauges_exact','reader_exit_gauges_exact','ordinary','paid']},sort_keys=True))

if __name__=='__main__':main()
