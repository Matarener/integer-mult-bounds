"""Independent literal cost and owner-only bridge residual audit.

Apache-2.0. Chris R / Clear1nsight with OpenAI Codex assistance.
Reads pinned evidence only; does not import the main pair verifier.
"""
import ast
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
IDENTITY = tuple(1 << i for i in range(73))


def need(value, reason):
    if not value:
        raise ValueError(reason)


def canon(x):
    return json.dumps(x, sort_keys=True, separators=(',', ':')).encode()


def reg(token):
    return token[1] + (704 if token[0] == 'C' else 0)


def flatten(events, packet):
    out = []
    for e in events:
        if e[0] == 'retained_core':
            out.extend(packet['core_words'][e[1]])
        elif e[0] in ('cover_sweep', 'private_sweep'):
            out.extend(flatten(e[2], packet))
        else:
            out.append(e)
    return out


def scalar_cost(gate):
    op = gate[0]
    if op in ('clear', 'copy'):
        return 2
    c = F(gate[3], gate[4]) if op == 'add' else F(gate[2], gate[3])
    a, b = abs(c.numerator), c.denominator
    need(a and not b & (b-1), 'nonzero dyadic gate')
    if op == 'add':
        return 2*(2+a.bit_length()+a.bit_count()+b.bit_length()-1)
    need(op == 'scale' and not a & (a-1), 'signed binary scale')
    return 2*(abs(a.bit_length()-b.bit_length())+(c < 0))


def bill(events):
    profile = Counter(e[5] for e in events if e[0] == 'climb')
    profile.update(e[4] for e in events if e[0] == 'center')
    profile[1] += sum(e[0] == 'native_line' for e in events)
    gates = [e[1] for e in events if e[0] == 'scalar']
    return {'events': len(events), 'event_kinds': dict(sorted(Counter(e[0] for e in events).items())),
            'native_profile': {str(k): v for k, v in sorted(profile.items()) if v},
            'native_calls': sum(profile.values()), 'native_rank_mass': sum(k*v for k,v in profile.items()),
            'scalar_macro_count': len(gates), 'scalar_operations': dict(sorted(Counter(g[0] for g in gates).items())),
            'scalar_real_primitive_bound': sum(map(scalar_cost, gates))}


def act(columns, x):
    out = 0
    while x:
        low = x & -x
        out ^= columns[low.bit_length()-1]
        x ^= low
    return out


@lru_cache(None)
def product(left, right):
    return tuple(act(left, v) for v in right)


def combine(a, b, c=F(1)):
    out = a.copy()
    for k,v in b.items():
        out[k] = out.get(k,F(0))+c*v
        if not out[k]:
            del out[k]
    return out


def scalar_rows(events):
    rows = [{i:F(1)} for i in range(712)]
    for e in events:
        if e[0] != 'scalar':
            need(e[0] in ('climb','center','phase','adapter','residual_adapter'), 'local native kind')
            continue
        gate = e[1]; op, at = gate[0], reg(gate[1])
        if op == 'clear': rows[at] = {}
        elif op == 'scale': rows[at] = {j:v*F(gate[2],gate[3]) for j,v in rows[at].items()}
        elif op == 'copy': rows[at] = rows[reg(gate[2])].copy()
        else:
            need(op == 'add', 'local scalar opcode')
            rows[at] = combine(rows[at],rows[reg(gate[2])],F(gate[3],gate[4]))
    return rows


def owner_replay(packet, source=0, collapse_routes=False):
    """One input X_source(d), constant payload; track owner d explicitly.

    Each dictionary key h denotes evaluation of that input at d*h.
    F0 starts at the identity chart. Stop B1 immediately before its core:
    the backward core preserves its Y source at payload character zero.
    No claim is made here about its X target or its full native lift.
    """
    rows = [{} for _ in range(712)]
    rows[source] = {IDENTITY: F(1)}
    events = flatten(packet['programs']['F_0'], packet)
    backward = packet['programs']['B_1_2']
    for index, e in enumerate(backward):
        if e[0] == 'retained_core':
            need(e[1:3] == ['backward',1] and index == len(backward)-1, 'backward core is final endpoint event')
            break
        events.extend(flatten([e], packet))
    else:
        raise ValueError('missing backward core')
    for e in events:
        kind = e[0]
        if kind == 'cover_map':
            at = reg(e[1])
            g = IDENTITY if collapse_routes else tuple(packet['map_registry'][e[2]]['owner_right_matrix_columns'])
            rows[at] = {product(g,h): v for h,v in rows[at].items()}
        elif kind == 'scalar':
            gate = e[1]; op, at = gate[0], reg(gate[1])
            if op == 'clear': rows[at] = {}
            elif op == 'scale': rows[at] = {h:v*F(gate[2],gate[3]) for h,v in rows[at].items()}
            elif op == 'copy': rows[at] = rows[reg(gate[2])].copy()
            else:
                need(op == 'add', 'scalar opcode')
                rows[at] = combine(rows[at], rows[reg(gate[2])], F(gate[3],gate[4]))
        else:
            need(kind in ('climb','phase','adapter','residual_adapter','native_line'), 'owner replay opcode')
            # All native kernels preserve the constant-payload character.
    return rows[112:224]


def bridge_binding(template):
    path = 'research/e8-bit-p111-tuned/vendor/pr510/e8-r480-nine-stage/vendor/e8-r715-eleven-stage-whole/code/global_k.py'
    raw = (ROOT/path).read_bytes()
    need(hashlib.sha256(raw).hexdigest() == '6368196a393ac25bb2918880e4c4bd31ed733b762c27b6873ab391cbc0c5c3c8', 'signed controller bytes')
    tree = ast.parse(raw)
    recipe = next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name == 'recipe')
    # Execute only this pure recipe constructor, never module setup or main.
    for n in ast.walk(recipe):
        if isinstance(n,ast.Call):
            need((isinstance(n.func,ast.Name) and n.func.id in ('dict','range','reversed')) or
                 (isinstance(n.func,ast.Attribute) and isinstance(n.func.value,ast.Name) and n.func.value.id == 'out' and n.func.attr == 'append'), 'pure recipe constructor calls')
    namespace = {'__builtins__':{'dict':dict,'range':range,'reversed':reversed}}
    exec(compile(ast.Module(body=[recipe],type_ignores=[]),path,'exec'),namespace)
    generated = namespace['recipe'](4)
    need(len(generated) == len(template['recipe']) == 19 and generated[:18] == template['recipe'][:18], 'all 18 preterminal signed controller events')
    need(generated[-1] == {'kind':'exchange'} and template['recipe'][-1] == {'kind':'terminal','pairs':4}, 'explicit distinct terminal conventions')
    small = next(n for n in ast.walk(tree) if isinstance(n,ast.FunctionDef) and n.name == 'small')
    shape = lambda n: ast.dump(n,include_attributes=False)
    expected_test = shape(ast.parse("e['kind']=='bridge'",mode='eval').body)
    branches = [n for n in ast.walk(small) if isinstance(n,ast.If) and shape(n.test) == expected_test]
    need(len(branches) == 1, 'unique signed bridge branch')
    branch = branches[0]
    expected_assign = ast.parse("d,s,c=e['dst'],e['src'],e['coefficient']").body[0]
    expected_loop = ast.parse("for x,y,sgn in [(2*d,2*s,c),(2*s+1,2*d+1,-c)]:\n if count!=skip: add(x,y,sgn)\n count+=1").body[0]
    need([shape(n) for n in branch.body] == [shape(expected_assign),shape(expected_loop)], 'exact two signed bank additions')
    add = next(n for n in small.body if isinstance(n,ast.FunctionDef) and n.name == 'add')
    expected_add = ast.parse('def add(d,s,c): z[d]=[x+c*y for x,y in zip(z[d],z[s])]').body[0]
    need(shape(add) == shape(expected_add), 'signed row addition semantics')
    execution_index, event = next((i,e) for i,e in enumerate(template['execution_schedule']) if e['kind']=='bridge' and e.get('replica')==0)
    recipe_index, specification = next((i,e) for i,e in enumerate(template['recipe']) if e['kind']=='bridge')
    need({k:event[k] for k in ('kind','src','dst','coefficient')} == specification, 'hosted bridge matches inherited signed controller')
    need((execution_index,event['source_event'],recipe_index) == (6,3,2), 'first pair bridge placement')
    ports = len(template['port_restriction']['new_to_old'])
    return {'source_path':path,'source_sha256':hashlib.sha256(raw).hexdigest(),
            'matched_preterminal_recipe_events':18,'terminal_conventions':{'source':generated[-1],'selected':template['recipe'][-1]},
            'recipe_index':recipe_index,'execution_index':execution_index,'source_event':event['source_event'],
            'hosted_event':event,'ports':ports,'complex_additions':2*ports,'real_component_additions':4*ports,
            'typed_ADD_compiler_real_primitive_bound':16*ports,'equations':['X0 += X1','Y1 -= Y0'],
            'scope':'inherited signed bank-controller semantics; no execution of the physical complex bridge'}


def compute():
    packet = json.loads(gzip.decompress((ROOT/'research/joint-query/certificate.json.gz').read_bytes()))
    with tarfile.open(ROOT/'research/community-frontier1042-audit/selected-replay.tar.gz') as ar:
        template = json.loads(gzip.decompress(ar.extractfile('t16/global/hosted/GLOBAL-TEMPLATE.json.gz').read()))
    provider = template['local_providers']['gauge44']
    words = provider['local_programs']
    selected_f = scalar_rows(words['forward'])
    selected_b = scalar_rows(words['backward'])
    qq_b = scalar_rows(packet['core_words']['backward'])
    need(selected_f[:112] == [{i:F(1)} for i in range(112)], 'selected F preserves X at payload zero')
    need(selected_f[112:224] == [{i:F(1),112+i:F(1)} for i in range(112)], 'selected F same-port Y shear')
    need(selected_b[112:224] == qq_b[112:224] == [{112+i:F(1)} for i in range(112)], 'both B source Y endpoints are identity for all 712 local inputs')
    selected = {side: bill(words[side]) for side in ('forward','backward')}
    qq_words = {side:flatten(packet['programs'][name],packet) for side,name in [('forward','F_0'),('backward','B_1_2')]}
    qq = {side:bill(events) for side,events in qq_words.items()}
    removed = [{'orientation':side,'source_event_index':i,'rank':e[4],'event_sha256':hashlib.sha256(canon(e)).hexdigest()} for side,events in words.items() for i,e in enumerate(events) if e[0]=='center']
    added = [{'orientation':side,'flattened_event_index':i,'rank':packet['native_line_recipes'][e[2]]['rank'],'event_sha256':hashlib.sha256(canon(e)).hexdigest()} for side,events in qq_words.items() for i,e in enumerate(events) if e[0]=='native_line']
    need(len(removed)==16 and all(e['rank']==8 for e in removed), 'sixteen named incumbent centre children')
    need(len(added)==32 and all(e['rank']==1 for e in added), 'thirty-two named candidate line children')
    owner_maps = sum(e[0]=='cover_map' for events in qq_words.values() for e in events)
    wrapper_maps = sum(sum(side in packet['native_line_recipes'][e[2]]['recipe'] for side in ('left','right')) for events in qq_words.values() for e in events if e[0]=='native_line')
    need((owner_maps,wrapper_maps)==(528,64), 'literal candidate map counts')
    need([selected[s]['scalar_real_primitive_bound'] for s in ('forward','backward')] == [198766,198814], 'selected scalar bills')
    need([qq[s]['scalar_real_primitive_bound'] for s in ('forward','backward')] == [211210,214986], 'QQ scalar bills')
    delta = {field: sum(qq[s][field]-selected[s][field] for s in selected)
             for field in ('native_calls','native_rank_mass','scalar_macro_count','scalar_real_primitive_bound')}
    decoder = json.loads((HERE/'vendor/PR4015-WORD.json').read_text())
    dbill = dict(sorted(Counter(e[0] for e in decoder).items()))
    dscalar = 2*dbill['clear'] + sum(8 if F(e[3]) in (1,-1) else 12 for e in decoder if e[0] == 'add')
    need(all(F(e[3]) in (1,-1,F(1,4),F(-1,4)) for e in decoder if e[0] == 'add'), 'decoder dyadic set')
    need((dbill['line'],dbill['map'],dbill['clear'],dscalar) == (224,352,416,26944), 'literal decoder invoice')
    dbill.update(native_wrappers=2*dbill['line'], scalar_allowance=dscalar, owned_output_fields=224, additional_owned_query_fields=0)
    result = {'decoder4015': dbill, 'selected': selected, 'qq16': qq, 'qq_minus_selected': delta,
              'bridge': bridge_binding(template),
              'candidate_operation_ledger': {'status':'candidate unintegrated; no accepted deletions','removed_centres':removed,'added_rank_one_lines':added},
              'explicit_added_owner_maps':owner_maps,'native_added_line_wrapper_maps':wrapper_maps,
              'status':'literal local invoice, not a funded replacement budget'}
    rows = owner_replay(packet)
    collapsed = owner_replay(packet, collapse_routes=True)
    ordinary = packet['U_ports']
    failures = [p for p in ordinary if rows[p]]
    need(all(not collapsed[p] for p in ordinary), 'owner-collapsed ordinary cancellation control')
    for p in failures:
        for h in rows[p]:
            need(all(((h[i]&h[j]).bit_count()%2) == (i == j) for i in range(73) for j in range(i,73)), 'owner witness remains in O(73,2)')
    result['owner_only_test'] = {'input':'X_0 is constant in payload and arbitrary in owner',
         'nonzero_ordinary_Y_ports':failures, 'input_at_identity_owner_bridge_Y1_port1':str(-rows[1].get(IDENTITY,0)), 'owner_collapsed_ordinary_Y_zero':True,
         'domain':'declared independent-cover module inputs; delta_I reachability from a particular outer multiplication input is not established',
         'repair_class':'postpair correction confined to A union T, preserving ordinary fields and pair-1 bridge target inputs',
         'scope':'B1 source Y only; both selected and QQ backward cores have exact same-port identity Y endpoints on all 712 local inputs at payload character zero',
         'lift_argument':'At each provider owner d, port p enters/exits at d*rho_p; a same-port identity endpoint cancels that route. Native phases and translations act identically on the constant-payload character.',
         'all_input_local_source_Y_columns_checked':712}
    need(failures == ordinary, 'all 96 ordinary Y outputs expose the owner residual')
    need(rows[1].get(IDENTITY) == F(-1,2), 'literal identity-owner witness')
    if failures:
        p = failures[0]; h,v = next(iter(sorted(rows[p].items())))
        result['owner_only_test'].update({'witness_output_port':p,'witness_input_owner_columns':list(h),
          'coefficient_at_identity_output_owner':str(v),'row_terms':len(rows[p]),
          'row_sha256':hashlib.sha256(canon([[list(h),str(v)] for h,v in sorted(rows[p].items())])).hexdigest()})
    return result


if __name__ == '__main__':
    # Standalone byte checks supplement the main verifier's source-history checks.
    for entry in json.loads((HERE/'SOURCES.json').read_text())['files']:
        need(hashlib.sha256((ROOT/entry['path']).read_bytes()).hexdigest() == entry['sha256'], 'standalone source bytes: '+entry['path'])
    for entry in json.loads((HERE/'PREDECESSORS.json').read_text())['files']:
        need(hashlib.sha256((HERE/entry['local']).read_bytes()).hexdigest() == entry['sha256'], 'standalone retained bytes: '+entry['local'])
    print(json.dumps(compute(),indent=2,sort_keys=True))
