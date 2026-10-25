"""Join the actual coupled native word to the retained balanced-J boundary.

This uses the retained normalized native-row convention and Clifford lift.
It does not flatten the physical child adapters into a new machine compiler.
"""
from collections import Counter
from fractions import Fraction as F
from functools import lru_cache
from pathlib import Path
from hashlib import sha256
import argparse
import copy
import gzip
import importlib.util
import json
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
NATIVE = 'research/native-rank8-helper-provider/'
PACKET = 'research/global120-optimistic-budget/science/inputs/10-BALANCED-J-NATIVE-v1.json'
SOURCE = 'research/kappa-round3-warp-20261022/ACTUAL-WORD.json.gz'
CLIFFORD = 'research/coded-native-caller/clifford_exact.py'
NORMAL = 'research/coded-native-caller/NORMALIZERS.json'
ce = None


def authenticate():
    payloads = {}
    for record in json.loads((HERE/'SOURCES.json').read_text())['files']:
        if record['usage'] == 'input':
            raw = (ROOT/record['path']).read_bytes()
            need(sha256(raw).hexdigest() == record['sha256'],
                 'Changed live input: '+record['path'])
            payloads[record['path']] = raw
    return payloads


def freeze(value):
    return tuple(freeze(x) for x in value) if isinstance(value,(list,tuple)) else value


def load_clifford(payloads):
    global ce
    spec = importlib.util.spec_from_file_location('joined_clifford',ROOT/CLIFFORD)
    ce = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = ce
    exec(compile(payloads[CLIFFORD],str(ROOT/CLIFFORD),'exec',optimize=0),ce.__dict__)


def need(ok, message):
    if not ok:
        raise ValueError(message)


def add(dst, src, factor=1):
    for key, value in src.items():
        value = dst.get(key, F()) + factor*value
        if value:
            dst[key] = value
        else:
            dst.pop(key, None)


def literal(word):
    return cached_literal(freeze(word))


@lru_cache(None)
def cached_literal(word):
    op = ce.ident(9)
    for e in word:
        kind = e[0]
        if kind == 'P': part = ce.perm(9, tuple(e[1]))
        elif kind == 'D': part = ce.diag(9, tuple(e[1]), tuple(e[2]))
        elif kind == 'X': part = ce.xgate(9, e[1])
        elif kind == 'C': part = ce.cgate(9, e[1], e[2])
        elif kind == 'phase': part = ce.Op(9, ce.identity(9), [('phase', e[1])])
        else: raise ValueError('Unknown Clifford word')
        op = op.then(part)
    return op


class Operators:
    """Exact Clifford keys include an absolute phase, up to a real sign."""
    def __init__(self):
        self.ops, self.keys, self.products, self.by_circuit = [], {}, {}, {}
        self.parity = 1
        need(self.insert(ce.ident(9)) == (0, 1), 'Identity key')

    def insert(self, op):
        literal_key = (op.tab, freeze(op.circuit))
        if literal_key in self.by_circuit:
            return self.by_circuit[literal_key]
        state, den = op.zero_state()
        at = next(j for j, z in enumerate(state) if z != (0,0))
        a, b = state[at]
        sign = -1 if a < 0 or (a == 0 and b < 0) else 1
        key = (op.tab, at, F(sign*a,1<<den), F(sign*b,1<<den))
        if key not in self.keys:
            if sign < 0:
                op = ce.Op(9, op.tab, op.circuit + [('phase',2)])
            self.keys[key] = len(self.ops)
            self.ops.append(op)
        result = self.keys[key], sign
        self.by_circuit[literal_key] = result
        return result

    def product(self, left, right):
        pair = (left, right)
        if pair not in self.products:
            self.products[pair] = self.insert(self.ops[right].then(self.ops[left]))
        return self.products[pair]

    def apply(self, row, op):
        key, sign = self.insert(op)
        out = {}
        for (owner, right), coefficient in row.items():
            result, phase = self.product(key, right)
            add(out, {(owner,result):coefficient*(sign*phase)**self.parity})
        return out


def span(vectors):
    values = {0}
    for vector in vectors:
        values |= {value ^ vector for value in tuple(values)}
    return values


def apply_columns(columns, value):
    result = 0
    for j in range(9):
        if value >> j & 1:
            result ^= columns[j]
    return result


def warp_maps(c):
    maps = {}
    for item in c['warps']:
        columns = item['G_columns']
        need(len(columns) == 9 and len(span(columns)) == 512,'Invertible native map')
        inverse = [next(x for x in range(512) if apply_columns(columns,x) == 1<<j)
                   for j in range(9)]
        need(all(apply_columns(inverse,apply_columns(columns,x)) == x for x in range(512)),
             'Native map inverse on all addresses')
        maps[item['op']], maps[-item['op']] = columns,inverse
    need(len(maps) == 144,'All72 native maps and their inverses')
    return maps


def raw_transfer(word, c, maps):
    rows = [{(j,()):F(1)} for j in range(641)]
    charts = c['start'][:] + [None]*9
    paid, scalar = Counter(), Counter()
    zero_checks = 0
    def address(ref):
        need(ref[0] in ('L','C'), 'Native field kind')
        return ref[1]+(632 if ref[0]=='C' else 0)
    for e in word:
        if e[0] == 'scalar':
            gate, chart = e[1:]
            dst = address(gate[1]); kind = gate[0]; scalar[kind] += 1
            if kind == 'clear':
                need(dst >= 632, 'No persistent erasure')
                rows[dst], charts[dst] = {}, chart
            else:
                need(charts[dst] == chart, 'Native destination chart')
                if kind in ('add','copy'):
                    src = address(gate[2])
                    need(charts[src] == chart and src != dst, 'Native source chart and alias')
                    if kind == 'copy':
                        need(dst >= 632 and not rows[dst], 'Native COPY uses owned zero')
                        rows[dst] = dict(rows[src])
                    else:
                        add(rows[dst],rows[src],F(gate[3],gate[4]))
                else:
                    need(kind == 'scale' and gate[2] != 0, 'Native nonzero SCALE')
                    rows[dst] = {key:F(gate[2],gate[3])*a for key,a in rows[dst].items()}
        elif e[0] == 'warp':
            _, ref, symbol, before, after = e
            dst = address(ref)
            need(charts[dst] == before, 'Native warp chart')
            need(symbol in maps and span(apply_columns(maps[symbol],x) for x in c['frames'][before])
                 == span(c['frames'][after]),'Native warp frame image')
            out = {}
            for (owner, tail), a in rows[dst].items():
                tail = tail[1:] if tail and tail[0] == -symbol else (symbol,)+tail
                add(out,{(owner,tail):a})
            rows[dst], charts[dst] = out, after
        elif e[0] == 'climb':
            _, _, dst, before, after, rank = e
            need(charts[dst] == before, 'Native child input chart')
            need(rank == len(c['frames'][after])-len(c['frames'][before]) > 0, 'Native paid rank')
            charts[dst] = after; paid[rank] += 1
        elif e[0] == 'zero_retag':
            _, dst, before, after = e
            need(charts[dst] == before and not rows[dst], 'Native zero-retag guard')
            charts[dst] = after; zero_checks += 1
        else:
            need(e[0] in ('phase','adapter','residual_adapter'), 'Inherited physical annotation')
    need(charts[:632] == c['final'], 'Every persistent native exit chart')
    need(all(not tail and owner < 632 for row in rows for owner,tail in row), 'Every free native word cancels; arbitrary owned input is absent')
    return [{owner:a for (owner,_),a in row.items()} for row in rows], charts, paid, scalar, zero_checks


def lift(word, active):
    def mask(value):return sum(1<<active[j] for j in range(9) if value>>j&1)
    out=[]
    for e in word:
        if e[0]=='P':
            cols=[1<<j for j in range(25)]
            for j,v in enumerate(e[1]):cols[active[j]]=mask(v)
            out.append(['P',cols])
        elif e[0]=='D':
            quadratic,linear=[0]*25,[0]*25
            for j,v in enumerate(e[1]):quadratic[active[j]]=mask(v)
            for j,v in enumerate(e[2]):linear[active[j]]=v
            out.append(['D',quadratic,linear])
        elif e[0]=='X':out.append(['X',mask(e[1])])
        else:
            need(e[0]=='phase','Only monomial stage gates')
            out.append(e)
    return out


def check_origin(source, native, witness):
    """Check the exact eight-site replacement recipe from the source provider."""
    centers = {row['event']:j for j,row in enumerate(witness)}
    late = {row['zero_event']:j for j,row in enumerate(witness)}
    caches = {row['cached_event']:j for j,row in enumerate(witness)}
    need(len(centers)==len(late)==len(caches)==8 and max(caches)<min(centers),'Eight ordered native sites')
    expected=[]
    for index,event in enumerate(source['programs']['backward']):
        if index in centers:
            j=centers[index];frame=witness[j]['frame']
            need(event==['center',0,0,frame,8],'Actual source centre event')
            expected += [['scalar',['clear',['C',0]],frame],
                         ['scalar',['copy',['C',0],['C',j+1]],frame]]
        elif index in late:
            row=witness[late[index]]
            need(event==['climb','warp_retimed',row['zero_role'],row['frame'],1,1],'Actual source late child')
            expected.append(['zero_retag',row['zero_role'],row['frame'],1])
        else:
            expected.append(event)
        if index in caches:
            j=caches[index];row=witness[j]
            expected += [['scalar',['clear',['C',j+1]],row['frame']],
                         ['scalar',['copy',['C',j+1],['L',row['cached_role']]],row['frame']]]
    need(native==expected,'Every emitted native record binds to actual source')


def run(payloads, pool, parity):
    source_payload = gzip.decompress(payloads[SOURCE])
    source = json.loads(source_payload)
    c = source['canonical']
    native_payload = gzip.decompress(payloads[NATIVE+'WORD.json.gz'])
    native = json.loads(native_payload)['word']
    provider = json.loads(payloads[NATIVE+'PROVIDER.json'])
    normal = json.loads(payloads[NORMAL])
    packet = json.loads(payloads[PACKET])
    witness = json.loads(payloads[NATIVE+'WITNESS.json'])
    need(sha256(source_payload).hexdigest() == provider['source_payload_sha256'], 'Decoded original source pin')
    need(sha256(native_payload).hexdigest() == provider['word_payload_sha256'], 'Decoded coupled word pin')
    need(sha256(payloads[NATIVE+'WITNESS.json']).hexdigest() == provider['candidate_witness_sha256'], 'Eight retained source sites')
    check_origin(source, native, witness)
    maps = warp_maps(c)
    raw,charts,paid,scalar,guards=raw_transfer(native,c,maps)
    need(paid == Counter({1:2193,2:412,3:510,4:127,5:40}), 'Native full paid profile')
    pool.parity=parity
    rows=[{(j,0):F(1)} for j in range(641)]
    mode=packet['coupled_h_owners']; promoted=packet['promoted_old_H8_owners']
    need(mode==provider['mode_owners'] and len(set(mode+promoted))==16,'Actual mode owners')
    names={**{f'x{j}':j for j in range(112)},**{f'y{j}':112+j for j in range(112)},
           **{f'h{j}':owner for j,owner in enumerate(mode)},**{f'k{j}':owner for j,owner in enumerate(promoted)},
           **{f'owner{j}':j for j in range(632)},**{f'c{j}':632+j for j in range(9)}}
    tags={name:('entry',slot) for name,slot in names.items()}
    cleared=None
    @lru_cache(None)
    def frame(j):
        op=ce.canonical_frame(9,c['frames'][j]); word=[]
        for e in op.circuit:
            if e[0]=='D':word.append(('D',e[1],tuple(-a%4 for a in e[2])))
            elif e[0]=='C':word.append(('C',e[1],-e[2]))
            elif e[0]=='phase':word.append(('phase',-e[1]%4))
            else:word.append(e)
        return ce.Op(9,tuple((x,z,-p%4) for x,z,p in op.tab),word)
    boundary=Counter()
    def physical(slot,op):rows[slot]=pool.apply(rows[slot],op)
    def scale(slot,a):
        boundary['SCALE']+=1
        rows[slot]={key:a*x for key,x in rows[slot].items() if a*x}
    def basis(program):
        for e in program:
            if e[0]=='add':
                add(rows[e[1]],rows[e[2]],F(e[3]))
                boundary['ADD']+=1
            else:
                need(e[0]=='scale','Native basis alphabet')
                scale(e[1],F(e[2]))
    def provider_call():
        nonlocal rows
        for j,port in enumerate(normal['ports']):
            wrappers=port['compiled_wrappers']
            physical(j,literal(wrappers['backward_input_X']['word']))
            physical(112+j,literal(wrappers['backward_input_Y']['word']))
            boundary['MONOMIAL']+=2
        for record in provider['mode_boundaries']:
            physical(record['owner'],literal(record['input_K']['literal_word']))
            boundary['MONOMIAL']+=1
            scale(record['owner'],F(2))
        basis(provider['input_basis_program'])
        for j in range(632):physical(j,frame(c['start'][j]).adjoint())
        entered=rows
        rows=[]
        for coefficients in raw:
            row={}
            for owner,a in coefficients.items():add(row,entered[owner],a)
            rows.append(row)
        for j,chart in enumerate(charts):
            if rows[j]:physical(j,frame(chart))
        basis(provider['output_basis_program'])
        for record in provider['mode_boundaries']:
            cache,owner=record['cache_slot'],record['owner']
            scale(cache,F(record['cache_scalar']))
            physical(cache,literal(record['output_N']['literal_word']))
            boundary['MONOMIAL']+=1
            need(not rows[owner], 'Whole native mode swap has zero destination')
            rows[cache],rows[owner]=rows[owner],rows[cache]
            boundary['SWAP']+=1
            need(not rows[cache],'Normalized owned cache is zero after whole-field swap')
            rows[cache]={}
            boundary['CLEAR']+=1
        for j,port in enumerate(normal['ports']):
            wrappers=port['compiled_wrappers']
            physical(j,literal(wrappers['backward_output_X']['word']))
            physical(112+j,literal(wrappers['backward_output_Y']['word']))
            boundary['MONOMIAL']+=2
        need(all(not row for row in rows[632:]),'All9 provider owned returns zero')
    external=Counter()
    before_last_half = None
    for seg in packet['forward_segments']:
        if seg['label'] == 'output_h_half2':
            before_last_half = [dict(row) for row in rows]
        for event in seg['operations']:
            op=event['op'];external[op]+=1
            if op=='MONOMIAL':
                need(event['word']==lift(event['source_word9'],packet['stage_geometry']['source9_to_stage_axes']),'Exact25-axis source lift')
                physical(names[event['field']],literal(event['source_word9']))
            elif op=='CLEAR':
                slot=names[event['field']];need(slot>=632,'Boundary erases only owned')
                rows[slot]={};tags[event['field']]=None;cleared=event['field']
            elif op=='ZERO_RETAG':
                field=event['field'];need(field==cleared and not rows[names[field]],'Retag immediately cleared owned field')
                chart=event['chart']
                tags[field]=tags[chart.removeprefix('exact current frame of ')] if chart!='ground' else 'ground'
                cleared=None
            elif op=='COPY':
                dst,src=names[event['dst']],names[event['src']]
                need(dst>=632 and not rows[dst] and tags[event['dst']]==tags[event['src']],'Boundary COPY actual owned zero/chart')
                rows[dst]=dict(rows[src])
            elif op=='ADD':
                dst,src=names[event['dst']],names[event['src']]
                need(dst!=src and F(event['coefficient']) in (1,-1,F(1,2),F(-1,2)),'Literal ADD coefficient')
                add(rows[dst],rows[src],F(event['coefficient']))
            elif op=='SWAP':
                a,b=event['fields'];need(event['includes_chart'] is True,'Whole-field/chart swap')
                x,y=names[a],names[b];rows[x],rows[y]=rows[y],rows[x];tags[a],tags[b]=tags[b],tags[a]
            elif op=='GAUSSIAN_Q':
                need(event['axis']==0 and event['rank']==1 and event['sign']==1 and event['paid'] is True,'Actual paid common Q')
                physical(names[event['field']],ce.cgate(9,1))
            elif op=='PROVIDER_5402':provider_call()
            else:raise ValueError('Unknown boundary primitive '+op)
    need(dict(external)==packet['forward_counts'],'All literal boundary counts')
    need(all(not row for row in rows[632:]),'All9 final owned fields zero')
    original=[{(j,0):F(1)} for j in range(641)]
    R,D=ce.fourier(9),ce.fourier(9,range(1,9))
    Kp=[literal(port['K_word']) for port in normal['ports']]
    Km=[literal(record['input_K']['literal_word']) for record in provider['mode_boundaries']]
    M=normal['mode_columns']
    def Z(bank):
        out=[{} for _ in range(8)]
        for k in range(8):
            for j in range(112):
                if M[k][j]:add(out[k],pool.apply(bank[j],Kp[j].then(Km[k].adjoint())),F(M[k][j],2))
        return out
    def W(bank):
        out=[{} for _ in range(112)]
        for k in range(8):
            for j in range(112):
                if M[k][j]:add(out[j],pool.apply(bank[k],Km[k].then(Kp[j].adjoint())),F(M[k][j],2))
        return out
    y=[dict(original[112+j]) for j in range(112)];h=[dict(original[j]) for j in mode]
    zy=Z(y);wzy=W(zy);wh=W(h)
    expected=[{} for _ in range(641)]
    for j in range(112):
        expected[j]=pool.apply(original[j],D);add(expected[j],pool.apply(original[112+j],R),-1)
        jy=dict(y[j]);add(jy,wzy[j],-1);add(jy,wh[j],-4)
        expected[112+j]=pool.apply(jy,D)
    for k,owner in enumerate(promoted):
        expected[owner]=pool.apply(original[owner],D);add(expected[owner],pool.apply(h[k],R),-1)
        jh={};add(jh,zy[k],3);add(jh,h[k],13)
        expected[mode[k]]=pool.apply(jh,D)
    for j in range(224,632):
        if j not in mode+promoted:
            rank=len(c['frames'][c['final'][j]])-len(c['frames'][c['start'][j]])
            expected[j]=pool.apply(original[j],ce.fourier(9,range(rank)))
    need(rows == expected, 'Complete632-original/9-owned endpoint in digit-column parity '+str(parity))
    controls = []
    def reject(label, action, messages):
        try:
            action()
        except ValueError as error:
            need(str(error) in messages,'Wrong rejection for '+label+': '+str(error))
            controls.append({'mutation':label,'rejection':str(error)})
        else:
            raise ValueError('Mutation admitted: '+label)
    bad = copy.deepcopy(native)
    next(e for e in bad if e[0] == 'climb')[-1] += 1
    reject('native_paid_rank',lambda:raw_transfer(bad,c,maps),{'Native paid rank'})
    first_clear = next(i for i,e in enumerate(native) if e[0]=='scalar' and e[1][0]=='clear')
    bad = native[:first_clear]+native[first_clear+1:]
    reject('native_owned_entry_CLEAR',lambda:raw_transfer(bad,c,maps),
           {'Native destination chart','Native source chart and alias','Native COPY uses owned zero'})
    bad = copy.deepcopy(native)
    event = next(e for e in bad if e[0]=='warp' and c['frames'][e[3]] and e[3]!=e[4])
    event[2] *= -1
    reject('native_warp_orientation',lambda:raw_transfer(bad,c,maps),{'Native warp frame image'})
    need(before_last_half is not None and before_last_half != expected,'Missing second output half must fail')
    controls.append({'mutation':'missing_second_output_half','rejection':'Complete endpoint differs'})
    post = next(seg for seg in packet['forward_segments'] if seg['label']=='forward_alias_post')
    post_k = next(e for e in post['operations'] if e['field']=='k0')
    need(post_k['source_owner']==promoted[0],'Phase control is on actual promoted owner')
    phase = ce.Op(9,ce.identity(9),[('phase',1)])
    need(phase.tab == ce.identity(9),'Phase-only control has unchanged signed tableau')
    need(pool.apply(rows[promoted[0]],phase) != expected[promoted[0]],'Wrong absolute phase must fail')
    controls.append({'mutation':'phase_i_after_actual_k0_post_alias','rejection':'Same tableau; wrong absolute phase'})
    bad_lift = copy.deepcopy(post_k)
    bad_lift['word'].append(['X',2])
    need(bad_lift['word'] != lift(bad_lift['source_word9'],packet['stage_geometry']['source9_to_stage_axes']),
         'Spectator mutation must fail exact lift')
    controls.append({'mutation':'unbound_spectator_translation','rejection':'Exact25-axis source lift differs'})
    need(guards==8 and len(native)==21473 and dict(scalar)==provider['source_changed_scalar_counts'],
         'Full native event, zero-guard and scalar census')
    need(len({j for j in mode+promoted})==16 and len(expected)==641,'Independent original ownership')
    helper_profile=Counter(len(c['frames'][c['final'][j]])-len(c['frames'][c['start'][j]])
                           for j in range(224,632) if j not in mode+promoted)
    need(helper_profile==Counter({4:28,7:7,8:39,9:318}),'Every remaining productive helper')
    need(boundary==Counter({'ADD':1644,'SCALE':40,'MONOMIAL':464,'SWAP':8,'CLEAR':8}),'Loop-derived provider boundary census')
    complete_paid=paid+Counter({1:external['GAUSSIAN_Q']})
    return {'status':'PASS_BALANCED_J_ACTUAL_NATIVE_WORD_JOIN',
            'source_payload_sha256':sha256(source_payload).hexdigest(),
            'native_payload_sha256':sha256(native_payload).hexdigest(),
            'packet_sha256':sha256(payloads[PACKET]).hexdigest(),
            'native_events':len(native),'native_warp_events':sum(e[0]=='warp' for e in native),
            'native_maps':72,'native_zero_guards':guards,'original_columns':632,
            'main_original_columns':240,'autonomous_helper_columns':392,'arbitrary_owned_columns':9,
            'owned_zero_returns':9,'paid_native':dict(sorted(paid.items())),
            'paid_complete_component':dict(sorted(complete_paid.items())),
            'native_scalar':dict(sorted(scalar.items())),
            'provider_boundary_ordinary':dict(sorted(boundary.items())),
            'external':dict(sorted(external.items())),
            'remaining_helper_profile':dict(sorted(helper_profile.items())),
            'endpoint':'T_s(u,v)=(D_s u-R_s v,D_s J_s v); all392 other original fields are positive normalized H_r jobs',
            'J':'[[I-WZ,-4W],[3Z,13I]]','all_lifted_boundary_maps':1040,
            'absolute_phase_method':'Signed Clifford tableau plus one nonzero entry of the exact zero column; real signs remain in rational coefficients',
            'controls':controls,'digit_column_parity':parity,'new_construction':False,'new_kappa':False,
            'scope':'Forward actual-word and literal balanced-J boundary join under retained normalized-row and physical-adapter premises. No inverse, new all-width compiler or global caller.'}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--emit',action='store_true',help='Write the mathematical receipt for package authors.')
    args=parser.parse_args()
    payloads=authenticate()
    load_clifford(payloads)
    pool=Operators()
    odd=run(payloads,pool,1)
    even=run(payloads,pool,2)
    need({k:v for k,v in odd.items() if k!='digit_column_parity'} ==
         {k:v for k,v in even.items() if k!='digit_column_parity'},'Identical scientific census in both parity classes')
    result={k:v for k,v in odd.items() if k!='digit_column_parity'}
    result['digit_column_parities_checked']=[1,0]
    result['phase_lift_rule']='An extracted real Clifford sign is raised to the digit-column count; exterior rational coefficients are not raised.'
    result['physical_implementation']='Inherited source adapter and prescribed columnwise lift; no new all-width machine compiler.'
    text=json.dumps(result,sort_keys=True,indent=2)+'\n'
    target=HERE/'RESULT.json'
    if args.emit:
        target.write_text(text)
    else:
        saved=json.loads(target.read_text())
        need(text==json.dumps(saved,sort_keys=True,indent=2)+'\n','Saved typed result differs')
    print(result['status'],json.dumps({'native_events':result['native_events'],
          'original_columns':result['original_columns'],'owned_zero_returns':result['owned_zero_returns'],
          'controls':len(result['controls'])},sort_keys=True))


if __name__=='__main__':
    main()
