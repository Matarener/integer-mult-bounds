"""Independent paid-query-factor invoice checks.

Chris R / Clear1nsight with OpenAI Codex assistance. Apache-2.0.
The package driver authenticates inputs before calling compute().
No primary or predecessor executable is imported.
"""
from collections import Counter
from fractions import Fraction as F
from functools import lru_cache
import gzip
import hashlib
import json
from pathlib import Path
import tarfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def need(ok, message):
    if not ok:
        raise ValueError(message)


def expand(events, packet):
    result = []
    for event in events:
        if event[0] == 'retained_core':
            result.extend(packet['core_words'][event[1]])
        elif event[0] in ('cover_sweep','private_sweep'):
            result.extend(expand(event[2],packet))
        else:
            result.append(event)
    return result


def scalar_price(gate):
    if gate[0] in ('copy','clear'):
        return 2
    coefficient = F(gate[3],gate[4]) if gate[0] == 'add' else F(gate[2],gate[3])
    num,den = abs(coefficient.numerator),coefficient.denominator
    need(num and not den&(den-1), 'nonzero dyadic coefficient')
    if gate[0] == 'add':
        return 2*(2+num.bit_length()+num.bit_count()+den.bit_length()-1)
    need(gate[0] == 'scale' and not num&(num-1), 'signed binary scale')
    return 2*(abs(num.bit_length()-den.bit_length())+(coefficient<0))


def invoice(events, packet):
    native = Counter()
    wrappers = 0
    for event in events:
        if event[0] == 'climb': native[event[5]] += 1
        elif event[0] == 'center': native[event[4]] += 1
        elif event[0] == 'native_line':
            recipe = packet['native_line_recipes'][event[2]]
            native[recipe['rank']] += 1
            need('left' in recipe['recipe'] and 'right' in recipe['recipe'], 'both native line wrappers')
            wrappers += 2
    scalar = [e[1] for e in events if e[0]=='scalar']
    return {'native_rank_profile':dict(sorted((str(k),v) for k,v in native.items())),
            'native_calls':sum(native.values()),'native_rank_sum':sum(k*v for k,v in native.items()),
            'scalar_macros':len(scalar),'scalar_real_primitive_allowance':sum(map(scalar_price,scalar)),
            'scalar_clears':sum(g[0]=='clear' for g in scalar),
            'explicit_owner_maps':sum(e[0]=='cover_map' for e in events),
            'native_line_wrapper_maps':wrappers}


IDENTITY=tuple(1<<i for i in range(73))


def xor_action(columns,vector):
    out=0
    while vector:
        bit=vector&-vector;out^=columns[bit.bit_length()-1];vector^=bit
    return out


@lru_cache(None)
def compose_owner(left,right):
    return tuple(xor_action(left,v) for v in right)


def plus(left,right,coefficient=F(1)):
    out=left.copy()
    for h,v in right.items():
        out[h]=out.get(h,F(0))+coefficient*v
        if not out[h]:del out[h]
    return out


def moved(row,g):
    return {compose_owner(g,h):v for h,v in row.items()}


def current_query_check(packet,phases,word):
    # Independent one-input full-owner replay; no primary implementation imported.
    rows=[{} for _ in range(712)];rows[0]={IDENTITY:F(1)}
    events=expand(packet['programs']['F_0'],packet)
    backward=packet['programs']['B_1_2']
    need(backward[-1][0:3]==['retained_core','backward',1], 'B core final source-Y identity endpoint')
    events+=expand(backward[:-1],packet)
    register=lambda token:token[1]+704*(token[0]=='C')
    for event in events:
        kind=event[0]
        if kind=='scalar':
            gate=event[1];op=gate[0];target=register(gate[1])
            if op=='clear':rows[target]={}
            elif op=='scale':rows[target]={h:v*F(gate[2],gate[3]) for h,v in rows[target].items()}
            elif op=='copy':rows[target]=rows[register(gate[2])].copy()
            else:
                need(op=='add', 'scalar opcode')
                rows[target]=plus(rows[target],rows[register(gate[2])],F(gate[3],gate[4]))
        elif kind=='cover_map':
            at=register(event[1]);rows[at]=moved(rows[at],tuple(packet['map_registry'][event[2]]['owner_right_matrix_columns']))
        else:need(kind in ('climb','phase','adapter','residual_adapter','native_line'), 'constant-payload native opcode')
    rho=[]
    for p,recipe in enumerate(phases['recipes']):
        swaps=[v^(1<<(9+i)) for i,v in enumerate(recipe['idle_children'][0]['orthogonal_axes'][:8])]
        columns=[]
        for v in IDENTITY:
            columns.append(v^xor_action(swaps,sum(((v&w).bit_count()%2)<<i for i,w in enumerate(swaps))))
        rho.append(tuple(columns))
        need(tuple(word['routes']['r1_'+str(p)])==rho[p], 'candidate stage1 route from source phase recipe')
    R=[{int(p):F(v) for p,v in row.items()} for row in packet['R_rows']]
    K=[{int(j):F(v) for j,v in row.items()} for row in packet['K_rows']]
    a=[]
    for row in R:
        total={}
        for p,v in row.items():total=plus(total,moved(rows[112+p],rho[p]),v)
        a.append(total)
    f=[]
    for row in R:
        total={}
        for p in packet['T_ports']:
            for j,v in K[p].items():total=plus(total,moved(a[j],rho[p]),row.get(p,0)*v)
        f.append(total)
    expected=[{IDENTITY:row[0]} if row.get(0) else {} for row in R]
    need(f==expected, 'original f recovered from current a via literal T-section owner paths')
    need(a!=expected, 'current a is not the original f')
    return {'input':'X0 arbitrary in cover owner, constant payload; all other initial data zero',
            'literal_current_Y_endpoint':'F0 and B1 prefix replay; backward core source Y identity inherited',
            'source_routes_checked':len(rho),'identity':'f=ell0,T P1,T (R1 Y_current)',
            'full_owner_operator_identity_for_this_input':True,
            'substitute_current_a_for_original_f':'REJECTED',
            'scope':'independent critical query-availability check, not all224-column factor proof or native acquisition certificate'}


def candidate_audit(packet,phases):
    raw = (HERE/'CANDIDATE-WORD.json').read_bytes()
    word = json.loads(raw)
    events,owned,routes = word['events'],word['owned_fields'],word['routes']
    need(owned==['q'+str(i) for i in range(33)], '33 declared owned fields')
    data = {side+str(p) for side in ('X','Y') for p in range(112)}
    allowed = data|set(owned)
    initialized = set()
    known_zero = set()
    coefficient_counts = Counter()
    writes = Counter()
    used_routes = Counter()
    scalar_total = 0
    for index,event in enumerate(events):
        op,target = event[:2]
        need(target in allowed, 'declared target namespace')
        writes[target] += 1
        if op=='clear':
            need(len(event)==2 and target in owned, 'clear only owned field')
            initialized.add(target);known_zero.add(target)
            scalar_total += 2
        else:
            need(op=='add_view' and len(event)==5, 'routed scalar ADD schema')
            source,coefficient,label = event[2:]
            need(source in allowed and source!=target and label in routes, 'declared routed ADD read')
            need((target not in owned or target in initialized) and (source not in owned or source in initialized), 'owned scratch initialized before use')
            coefficient=F(coefficient)
            need(coefficient, 'nonzero routed ADD')
            coefficient_counts[str(coefficient)] += 1
            used_routes[label] += 1
            scalar_total += scalar_price(['add',target,source,coefficient.numerator,coefficient.denominator])
            known_zero.discard(target)
    need(set(owned)<=known_zero, 'every owned field zero at terminal boundary')
    need(not any('X'+str(p) in writes for p in packet['U_ports']), 'ordinary current X never overwritten')
    I=tuple(1<<i for i in range(73))
    need(tuple(routes['I'])==I, 'identity owner route')
    for label in used_routes:
        columns=routes[label]
        need(len(columns)==73 and all(type(v)is int and 0<v<1<<73 for v in columns), 'full owner matrix')
        need(all(((columns[i]&columns[j]).bit_count()%2)==(i==j) for i in range(73) for j in range(i,73)), 'orthogonal owner route')
    counts=Counter(e[0] for e in events)
    need((len(events),counts['add_view'],counts['clear'],scalar_total)==(6216,6112,104,66832), 'literal candidate arithmetic invoice')
    nonidentity=sum(count for label,count in used_routes.items() if tuple(routes[label])!=I)
    query_check=current_query_check(packet,phases,word)
    return {'independent_current_query_check':query_check,'word_sha256':hashlib.sha256(raw).hexdigest(),'events':len(events),'operations':dict(sorted(counts.items())),
            'add_coefficients':dict(sorted(coefficient_counts.items())),'scalar_real_primitive_allowance':scalar_total,
            'logical_routed_ADD_reads':nonidentity,'identity_owner_ADD_reads':counts['add_view']-nonidentity,
            'distinct_used_owner_matrices':len({tuple(routes[label]) for label in used_routes}),
            'owned_fields':len(owned),'owned_initialization_before_each_use':True,'owned_terminal_zero':True,
            'pair1_or_helper_accesses':0,'ordinary_current_X_writes':0,
            'physical_storage_allocation':'not supplied; 33 declared independent owned cover fields are an ABI requirement',
            'native_legality':'not supplied by add_view; frame conversion, source preservation and payload translation need a native lowering',
            'movement_and_precision':'unknown; routed reads are not priced physical maps, tape moves or bit operations',
            'scope':'independent literal arithmetic and owned lifetime audit, not a native supplier certificate'}


def compute():
    packet = json.loads(gzip.decompress((ROOT/'research/joint-query/certificate.json.gz').read_bytes()))
    with tarfile.open(ROOT/'research/community-frontier1042-audit/selected-replay.tar.gz') as archive:
        template = json.loads(gzip.decompress(archive.extractfile('t16/global/hosted/GLOBAL-TEMPLATE.json.gz').read()))
        word_raw = archive.extractfile('t16/global/base/providers/gauge44/CANONICAL-WORD.json.gz').read()
        recipes_raw = archive.extractfile('t16/global/base/providers/gauge44/CLIFFORD-RECIPES.json').read()
        source_word = json.loads(gzip.decompress(word_raw))
        source_recipes = json.loads(recipes_raw)
        phases=json.load(archive.extractfile('t16/global/base/work/complex-nine-native/DATA-PHASES.json'))
    source = template['local_providers']['gauge44']['local_programs']
    selected = invoice(source['forward']+source['backward'],packet)
    candidate = invoice(expand(packet['programs']['F_0']+packet['programs']['B_1_2'],packet),packet)
    delta = {key:candidate[key]-selected[key] for key in selected if key!='native_rank_profile'}
    need((selected['native_rank_profile']['8'],candidate['native_rank_profile'].get('8',0))==(16,0), 'sixteen incumbent H8 children')
    need(candidate['native_rank_profile']['1']-selected['native_rank_profile']['1']==32, 'thirty-two new H1 children')
    need((delta['scalar_real_primitive_allowance'],delta['explicit_owner_maps'],delta['native_line_wrapper_maps'])==(28616,528,64), 'literal pair baseline')
    previous = json.loads((HERE/'vendor/PR4105-RESULT.json').read_text())['independent_cost_and_owner_audit']
    need(previous['qq_minus_selected']['scalar_real_primitive_bound']==delta['scalar_real_primitive_allowance'], 'retained baseline agreement')
    centres = [e for events in source.values() for e in events if e[0]=='center']
    need(len(centres)==16 and all(e[4]==8 and sorted([len(source_word['frames'][e[2]]),len(source_word['frames'][e[3]])])==[0,8] for e in centres), 'actual eight-axis centre frames')
    need(all(any((r['old'],r['new'],r['rank'])==(e[2],e[3],e[4]) for r in source_recipes['children']) for e in centres), 'actual centre Clifford children')
    normalizations = len(packet['A_ports']+packet['T_ports']+packet['U_ports'])
    introduced = candidate['native_rank_profile']['1']-selected['native_rank_profile']['1']
    old_linear_rank_credit = sum(e[4] for e in centres)
    optimistic_cap = old_linear_rank_credit-introduced
    need((normalizations,optimistic_cap,introduced+normalizations-old_linear_rank_credit,introduced+2*normalizations-old_linear_rank_credit)==(112,96,16,128), 'generic normalization arithmetic')
    screen = {'class':'normalize all112 Y holes to common F17 on ingress; optional matching egress restoration',
              'tariff_premise':'The compared actual normalized phase children share C_r(lambda)=K(lambda)*(r*lambda)^(1-a), K(lambda)>0, 0<=a<=1, with equal tariffs for the compared positive and inverse normalized signs.',
              'lift_correspondence':'prescribed native-moment model; production recursive compiler correspondence not supplied here',
              'inequality':'16*C8 <= 128*C1; QQ adds32*C1, leaving at most96*C1 for all repair native calls',
              'optimistic_repair_H1_allowance':optimistic_cap,
              'ingress_H1':normalizations,'ingress_native_excess_at_least_H1':introduced+normalizations-old_linear_rank_credit,
              'ingress_and_egress_H1':2*normalizations,'ingress_and_egress_excess_at_least_H1':introduced+2*normalizations-old_linear_rank_credit,
              'incidence_scope':'pointwise per replaced pair at every lambda; any positive incidence preserves this conditional native excess',
              'scope':'rejection of this generic normalization route under the stated tariff, not a lower bound for all paid repairs or physical costs',
              'source_member_sha256':{'canonical_word':hashlib.sha256(word_raw).hexdigest(),'clifford_recipes':hashlib.sha256(recipes_raw).hexdigest()}}
    repair=candidate_audit(packet,phases)
    return {'candidate_arithmetic_and_ownership':repair,'generic_native_screen':screen,'selected_pair':selected,'unrepaired_qq16_pair':candidate,'qq_minus_selected':delta,
            'removed_children':{'rank':8,'count':16},'introduced_children_before_repair':{'rank':1,'count':32},
            'known_scalar_increment_with_candidate':delta['scalar_real_primitive_allowance']+repair['scalar_real_primitive_allowance'],
            'conditional_screen':'16*C8 > 32*C1 + 95448*S + all remaining native repair, frame conversion, retention, restoration, allocation, movement, precision and control tariffs',
            'screen_premises':['same required current X/Y endpoint and unchanged pair1 inputs','comparable native and scalar tariffs','native wrappers counted exactly once','explicit owner maps priced separately unless tariff includes them','actual recursive replacement incidence established'],
            'query_retention':'Earlier queries are not free at the pair boundary; private streams clear and borrowed helpers restore.',
            'recursive_usage':'unknown; no fixed incumbent incidence or PR3976 proposed allowance applied',
            'scope_4030':'fixed 104 M21 owner routes, fixed F16 output, separate branch normalization and prescribed phase-normalizer tariff; not automatically the new pair factor',
            'repair_invoice_status':'logical add_view word counted and owned lifetime checked; native lowering and complete cost remain unestablished'}
