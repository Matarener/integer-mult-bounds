"""Literal first-pair and routed ordinary-output audit.

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


def decoder_replay(word):
    """Actual PR4015 WORD at the same common-cover constant specialization."""
    rows = {side+str(p): {p+(112 if side == 'Y' else 0):F(1)}
            for side in ('X','Y') for p in range(112)}
    borrowed = {name: row.copy() for name,row in rows.items()}
    for event in word:
        if event[0] == 'clear':
            need(event[1] not in borrowed, 'decoder cannot clear borrowed data')
            rows[event[1]] = {}
        elif event[0] == 'add':
            _, target, source, coefficient = event
            need(target not in borrowed and target in rows and source in rows,
                 'decoder ownership and defined reads')
            rows[target] = add(rows[target], rows[source], F(coefficient))
        else:
            need(event[0] in ('begin','end','line','map','checkpoint'), 'known decoder event')
    need(all(rows[name] == value for name,value in borrowed.items()), 'all decoder current inputs unchanged')
    return [rows[side+str(p)] for side in ('Z','W') for p in range(112)]


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


def source_routes(phases):
    result = []
    need(phases['m'] == 73 and len(phases['recipes']) == 112, 'actual native phase dimensions')
    for p, record in enumerate(phases['recipes']):
        need(record['port'] == p, 'source port order')
        local = tuple(record['idle_children'][0]['orthogonal_axes'][:8])
        need(len(local) == 8, 'eight actual local directions')
        # Swap these eight local axes with the first external stage block.
        swaps = tuple(v ^ I73[9+i] for i,v in enumerate(local))
        matrix = tuple(v ^ act(swaps, sum(((v & w).bit_count()%2)<<i
                                         for i,w in enumerate(swaps))) for v in I73)
        need(orthogonal(matrix) and product(matrix,matrix) == I73, 'actual stage1 orthogonal involution')
        need(act(matrix,record['q']) == record['q'], 'port normal fixed')
        result.append(matrix)
    return result


def owner_replay_y(packet, qf):
    """Literal B1 prefix on input X0(d)=delta_I(d), payload constant.

    A row maps actual right-owner matrices to exact coefficients. A cover map
    g sends f(d h) to f(d g h); payload shifts fix the constant payload.
    The final backward core preserves every source Y, audited separately.
    """
    rows = [{I73:row[0]} if row.get(0) else {} for row in qf]
    rows.extend({} for _ in range(488))
    core_seen = 0
    map_count = 0
    def consume(event):
        nonlocal map_count
        if event[0] == 'scalar':
            scalar_step(rows,event[1])
        elif event[0] == 'cover_map':
            _, token, label, _, _ = event
            at = register(token)
            matrix = tuple(packet['map_registry'][label]['owner_right_matrix_columns'])
            need(orthogonal(matrix), 'literal map owner belongs to actual orthogonal cover')
            out = {}
            for h, coefficient in rows[at].items():
                key = product(matrix,h)
                out[key] = out.get(key,F(0))+coefficient
                if not out[key]: del out[key]
            rows[at] = out
            map_count += 1
        else:
            need(event[0] == 'native_line', 'known B1 prefix event')
    for event in packet['programs']['B_1_2']:
        if event[0] == 'retained_core':
            need(event[1:3] == ['backward',1], 'actual final B1 core')
            core_seen += 1
            continue
        need(not core_seen, 'retained backward core is last')
        if event[0] in ('cover_sweep','private_sweep'):
            for nested in event[2]: consume(nested)
        else: consume(event)
    need(core_seen == 1 and map_count == 528, 'complete literal B1 prefix owner maps')
    need(rows[704:] == [{} for _ in range(8)], 'owner-prefix private return')
    return rows[112:224]


def load_sources():
    raw = {}
    for path, expected in SOURCE_PINS.items():
        raw[path] = (ROOT/path).read_bytes()
        need(digest(raw[path]) == expected, 'primary canonical source pin: '+path)
    names = {
        'template':'t16/global/hosted/GLOBAL-TEMPLATE.json.gz',
        'programs':'t16/global/base/providers/gauge44/LOCAL-PROGRAMS.json.gz',
        'canonical':'t16/global/base/providers/gauge44/CANONICAL-WORD.json.gz',
        'phases':'t16/global/base/work/complex-nine-native/DATA-PHASES.json',
    }
    data = {}
    hashes = {}
    with tarfile.open(fileobj=io.BytesIO(raw[ARCHIVE]),mode='r:gz') as archive:
        for label,name in names.items():
            members = [m for m in archive.getmembers() if m.name == name]
            need(len(members) == 1 and members[0].isfile(), 'unique regular source member')
            value = archive.extractfile(members[0]).read()
            hashes[name] = digest(value)
            data[label] = json.loads(gzip.decompress(value) if name.endswith('.gz') else value)
    data['packet'] = json.loads(gzip.decompress(raw[PACKET]))
    word = (PKG/'vendor/PR4015-WORD.json').read_bytes()
    need(digest(word) == '272d8c1bd172c29044eb227ec6d67a882501250978234685e035158f4479aa58', 'exact PR4015 word')
    data['decoder_word'] = json.loads(word)
    return data, hashes


def compute():
    data, member_hashes = load_sources()
    template, source, packet = (data[k] for k in ('template','programs','packet'))
    need(template['cover'] == 'all matrices d in O(73,2), in lexicographic row order', 'actual full orthogonal cover')
    f_index = next(i for i,c in enumerate(template['calls']) if c['replica']==0 and c['stage']==0)
    b_index = next(i for i,c in enumerate(template['calls']) if c['replica']==0 and c['stage']==1)
    need((f_index,b_index) == (0,4), 'actual serialized call indices')
    wrong_second = template['calls'][1]
    need(wrong_second['replica'] == 8 and wrong_second['stage'] == 0 and
         wrong_second['orientation'] == 'forward' and
         (wrong_second['replica'],wrong_second['stage']) != (0,1),
         'negative caller control: calls[1] is not the same-replica backward call')
    calls = [template['calls'][i] for i in (f_index,b_index)]
    for stage,call in enumerate(calls):
        need(call['provider_id']=='gauge44' and call['pair']==0 and
             call['orientation']==('forward' if stage==0 else 'backward'), 'actual selected provider orientation')
        need(call['owners'][:224] == [[p,[1,stage,p%112]] for p in range(224)], 'same-port X/Y co-owner routes')
        need(len(call['owners'])==704 and len({x[0]for x in call['owners']})==704, 'distinct local persistent physical owners')
        need(digest(canonical(source[call['orientation']])) == call['local_program_sha256'], 'actual called word hash')
    need(template['local_providers']['gauge44']['local_programs'] == source, 'embedded actual selected programs')
    events = template['execution_schedule']
    chosen = [events[i] for i in (0,4,5,6)]
    need([(e['kind'],e['replica'],e['source_event'])for e in chosen] ==
         [('local_cover_sweep',0,0),('local_cover_sweep',0,1),('idle_cover_sweep',0,2),('bridge',0,3)], 'actual first pair and continuation events')
    need(chosen[2]['pair']==1 and chosen[3]['src']==1 and chosen[3]['dst']==0 and chosen[3]['coefficient']==1, 'actual zero-pair preparation and signed bridge')
    intervening = []
    pair0_data = {owner[0] for owner in calls[0]['owners'][:224]}
    pair1_data = set(range(224,448))
    for index,replica in ((1,8),(2,1),(3,9)):
        event,call = events[index],template['calls'][index]
        need(event['kind']=='local_cover_sweep' and event['replica']==replica and
             event['source_event']==0 and call['replica']==replica and
             call['stage']==0 and call['pair']==0 and
             call['orientation']=='forward' and call['provider_id']=='gauge44',
             'actual intervening events are other-replica forward calls')
        need(digest(canonical(source['forward'])) == call['local_program_sha256'],
             'intervening call uses audited helper-returning forward word')
        data_owners = {owner[0] for owner in call['owners'][:224]}
        helper_owners = {owner[0] for owner in call['owners'][224:]}
        need(not data_owners & (pair0_data|pair1_data), 'intervening data writes disjoint from replica0 pair0 and pair1')
        intervening.append({'hosted_event':index,'replica':replica,
            'pair0_data_borrowed_as_helpers':len(helper_owners & pair0_data),
            'pair1_data_borrowed_as_helpers':len(helper_owners & pair1_data)})
    gf,gb = (scalar_replay(source[name]) for name in ('forward','backward'))
    qf,qb = (scalar_replay(flatten(packet,name)) for name in ('F_0','B_1_2'))
    identity = [{i:F(1)}for i in range(224)]
    need(gf == identity[:112]+[add(identity[112+p],identity[p])for p in range(112)], 'selected local forward shear')
    need(gb == [add(identity[p],identity[112+p],-1)for p in range(112)]+identity[112:], 'selected local backward shear')
    core_b = scalar_replay(packet['core_words']['backward'])
    need(core_b[112:] == identity[112:], 'literal backward core preserves every Y source')
    gpair,qpair = multiply(gb,gf),multiply(qb,qf)
    d = decoder_replay(data['decoder_word'])
    dq = multiply(d,qpair)
    need(dq==identity and multiply(qpair,d)==identity, 'both decoder inverse orders on224 data only')
    need(all(rank(x)==224 for x in (gf,gb,qf,qb,gpair,qpair,d)), 'data maps invertible')
    A,T,U = (packet[k+'_ports'] for k in ('A','T','U'))
    S = sorted(A+T)
    changed_x = [p for p in range(112)if qpair[p]!=gpair[p]]
    changed_y = [p for p in range(112)if qpair[112+p]!=gpair[112+p]]
    need(changed_x==changed_y==S, 'constant pair residual precisely selected output rows')
    delta_rank = rank(difference(qpair,gpair))
    need(delta_rank==32 and rank(difference(qpair[:112],gpair[:112]))==16 and
         rank(difference(qpair[112:],gpair[112:]))==16, 'pair difference exact ranks')
    dg = multiply(d,gpair)
    need(rank(difference(dg,identity))==32, 'actual decoder on selected source is wrong')
    endpoint = multiply(gpair,d)
    need(rank(difference(endpoint,identity))==32, 'coordinated correction rank on224 data')
    # Actual literal owner replay, independent of the following short formula.
    owner_y = owner_replay_y(packet,qf)
    routes = source_routes(data['phases'])
    R = [{int(j):F(v)for j,v in row.items()}for row in packet['R_rows']]
    K = [{int(j):F(v)for j,v in row.items()}for row in packet['K_rows']]
    known_maps = {tuple(m['owner_right_matrix_columns'])for m in packet['map_registry'].values()}
    need(all(r in known_maps for r in routes), 'all source-derived stage1 routes present in packet')
    # Independent formula: Y_U = y_U+x_U+(K1_U ell1_T P0-K0_U)R0 x.
    formula = {}
    for u in U:
        row = {I73:qf[112+u][0]} if qf[112+u].get(0) else {}
        for t in T:
            coefficient = sum(K[u].get(j,0)*R[j].get(t,0)for j in range(8))
            coefficient *= qf[t].get(0,0)
            if coefficient:
                key = product(routes[u],routes[t])
                row[key] = row.get(key,F(0))+coefficient
                if not row[key]:del row[key]
        formula[u] = row
        need(owner_y[u]==row, 'literal owner prefix equals independently derived ordinary Y formula')
        need(sum(row.values())==gpair[112+u].get(0,0), 'common-cover collapse recovers constant pair cancellation')
    need(all(formula[u] for u in U), 'all96 ordinary Y operators nonzero on this original X0 field')
    h76,h81 = (product(routes[1],routes[t])for t in (76,81))
    expected = {I73:F(-1,2),h76:F(1,4),h81:F(1,4)}
    need(len(expected)==3 and formula[1]==expected, 'three-term exact ordinary witness')
    need(h76!=I73 and h81!=I73 and orthogonal(h76) and orthogonal(h81), 'distinct legal nonidentity owner products')
    need((h76[0],h81[0])==(448,460), 'short nonidentity witnesses')
    need(gpair[113].get(0,0)==0 and formula[1][I73]==F(-1,2), 'delta_I current Y1 discrepancy')
    helpers = [{owner[0]for owner in call['owners'][224:]}for call in calls]
    need(len(helpers[0]&helpers[1])==40 and len(helpers[0]|helpers[1])==920, 'physical helper union differs from a local704 role space')
    witness_constant = {
        'input':'pair0 X_0=1 on every cover, all other fields zero',
        'source_pair_port0':[str(gpair[0].get(0,0)),str(gpair[112].get(0,0))],
        'QQ16_pair_port0':[str(qpair[0].get(0,0)),str(qpair[112].get(0,0))],
        'source_bridge_pair1_Y0':str(-chosen[3]['coefficient']*gpair[112].get(0,0)),
        'QQ16_bridge_pair1_Y0':str(-chosen[3]['coefficient']*qpair[112].get(0,0)),
    }
    need(witness_constant['QQ16_pair_port0']==['13','-12'], 'full bridge constant selected witness')
    decoder_control = {
        'input':'X_1=1, all others0',
        'G_current_Y1':str(gpair[113].get(1,0)),
        'Q_current_Y1':str(qpair[113].get(1,0)),
        'D_Q_recovered_Y1':str(dq[113].get(1,0)),
        'actual_bridge_Y1':str(-chosen[3]['coefficient']*gpair[113].get(1,0)),
        'naive_recovered_bridge_Y1':str(-chosen[3]['coefficient']*dq[113].get(1,0)),
    }
    need(decoder_control['G_current_Y1']==decoder_control['Q_current_Y1']=='1' and
         decoder_control['actual_bridge_Y1']=='-1' and
         decoder_control['D_Q_recovered_Y1']==decoder_control['naive_recovered_bridge_Y1']=='0',
         'computed negative control: recovered old Y is not current bridge Y')
    return {
        'status':'PASS_LITERAL_PAIR_AND_ROUTED_ORDINARY_OBSTRUCTION',
        'source_archive_members':member_hashes,
        'boundary_binding':{
            'serialized_call_indices':[0,4], 'hosted_event_indices':[0,4,5,6],
            'source_event_indices':[0,1,2,3], 'events':chosen,
            'intervening_other_replica_events':intervening,
            'intervening_preservation':'Other-replica data writes are disjoint; borrowed replica0 fields are returned by the audited local source word on the payload-constant domain.',
            'program_sha256':[c['local_program_sha256']for c in calls],
            'owner_list_sha256':[digest(canonical(c['owners']))for c in calls],
            'local_persistent_roles_per_call':704,'borrowed_helpers_per_call':480,
            'physical_helper_intersection':40,'physical_helper_union':920,
            'inverse_domain':'224 data coordinates only; each704 local interface has480 independently returned helper roles; no inversion of712 private-clearing fields',
            'physical_pair_union_if_other_events_held_fixed':1144,
        },
        'constant_pair':{
            'source_map':'(x,y) -> (-y,x+y)',
            'data_map_rank':224,'pair_difference_rank':delta_rank,
            'X_difference_rank':16,'Y_difference_rank':16,
            'changed_X_ports':changed_x,'changed_Y_ports':changed_y,
            'ordinary_rows_equal':192,
            'individual_F_difference_rank':rank(difference(qf,gf)),
            'individual_B_difference_rank':rank(difference(qb,gb)),
            'coordinated_post_adapter_rank_minus_I':32,
            'rank_invoice_scope':'Algebraic update-rank obligation only, not a native-child lower bound or paid construction.',
            'full_bridge_witness':witness_constant,
        },
        'decoder_boundary':{
            'actual_PR4015_events':len(data['decoder_word']),
            'D_Q_pair':'identity224, checked in both orders',
            'D_G_pair_minus_I_rank':32,
            'current_inputs':'all224 borrowed unchanged',
            'outputs':'pre-pair original data inF17 by inherited native contract, not actual current source-provider pair',
            'naive_recovered_Y_as_bridge_source_control':decoder_control,
        },
        'routed_ordinary_witness':{
            'input':'pair0 X_0(d,z)=delta[d=I73] for every payload address z; all other data/helpers/private and pair1 zero',
            'cover':template['cover'],'payload_character':0,'output_owner':'I73',
            'operator':'Y_Q,1-Y_G,1 = (D_(rho1 rho76)+D_(rho1 rho81))/4 - I/2 applied to original X_0',
            'ordinary_port':1,
            'source_current_Y1':str(gpair[113].get(0,0)),
            'QQ16_current_Y1':str(formula[1][I73]),
            'source_bridge_pair1_Y1':str(-chosen[3]['coefficient']*gpair[113].get(0,0)),
            'QQ16_bridge_pair1_Y1':str(-chosen[3]['coefficient']*formula[1][I73]),
            'source_route_columns':{'rho1':list(routes[1]),'rho76':list(routes[76]),'rho81':list(routes[81])},
            'product_columns':{'rho1_rho76':list(h76),'rho1_rho81':list(h81)},
            'product_column0':[448,460], 'product_coefficients':['1/4','1/4'],
            'identity_coefficient':'-1/2','all96_ordinary_Y_operator_rows_nonzero':True,
            'literal_owner_prefix_vs_formula':'PASS for all96 ordinary Y rows on originalX0 input column',
            'native_scope':'Every individual payload is constant; native line/translation/frame factors fix it exactly, while actual full-cover owner pullbacks remain nonconstant.',
        },
        'excluded_mapping_class':'Post-pair adapters followed by the unchanged named full bridge, with persistent writes confined to pair0 X/Y at A union T. All nonselected pair0 fields, pair1 bridge inputs, and other persistent bridge inputs remain unchanged; only private work and those named selected pair0 fields may change. The class must work on every state permitted by the declared module interface.',
        'not_excluded':['Earlier changes to selected registers','Paid repairs that write ordinary U or other bridge inputs','Factored query repairs outside the declared write class','Different global endpoint or terminal consumer','Repairs on a separately proved smaller reachable subspace','Other representations or input domains with separate interface proofs'],
        'controls':[
            'Wrong serialized calls[1] is replica8 F0, not actual B1; source binding requires calls[4].',
            'Collapsing all owner routes makes the three-term witness zero and misses the actual caller obstruction.',
            'Actual decoder D composed with selected G fails identity at rank32.',
            'Replacing actual current bridge source with D recovered pre-pair source changes -1 to0 on X1 witness.',
            'Full712 private-clearing map is never passed to any inverse; both inverse orders are tested only on224 data.',
        ],
        'scientific_scope':'Exact actual source pair and bridge obstruction on a concrete cover-varying, payload-constant input permitted by the declared independent-cover module interface. Reachability from an outer multiplication entrance is unestablished; no paid replacement or supplier improvement certified.',
    }
