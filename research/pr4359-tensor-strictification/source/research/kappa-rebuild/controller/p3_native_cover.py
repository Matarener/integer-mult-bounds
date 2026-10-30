#!/usr/bin/env python3
"""Complete native ownership and phase binding for p3/keep43.

This binds the exact Laurent controller to all 2,856 original helper roles,
whole-call adapters, arbitrary productive inputs, and the full recursive
invoice.  Apache-2.0; substantial OpenAI assistance.  Native source credits
and immutable hashes are inherited from the reconstruction receipts.
"""
from collections import Counter, defaultdict, deque
from hashlib import sha256
from pathlib import Path
import argparse
import gzip
import json
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
import global_identity_cover as G

STAGES = ((0,'forward'),(0,'backward'),(0,'forward'),(1,'backward'),
          (1,'forward'),(2,'backward'),(2,'forward'))
FORMAL = HERE.parent/'bit/COMPLEX-CONTROLLER-FACTOR.json'
TARIFF = HERE.parent/'architecture/P3-CONTROLLER-TARIFF-CERTIFICATE.json'
AUDIT = HERE.parent/'transfer-audit/P3-NATIVE-AUDIT.json.gz'
TARGETS = {6:192,7:56,8:93,9:1229,25:448,57:224}
PAID = {1:17623,2:5065,3:1738,4:714,5:254}


def need(condition, message):
    if not condition:
        raise AssertionError(message)


def stage_frame(n, stage, q):
    if stage == 0:
        return n.frame([(a,1) for a in n.AXES[:9]]+[(q,-1)])
    return n.frame((a,1) for a in n.AXES[9+8*(stage-1):9+8*stage])


def contacts(n, F, phases):
    result = []
    for stage,(pair,direction) in enumerate(STAGES):
        sign = 1 if direction == 'forward' else -1
        spectator = n.frame((a,1) for a in n.AXES[9:9+8*stage])
        for port,recipe in enumerate(phases['recipes']):
            q = recipe['q']; route = n.source_route(phases,stage,port)
            need(all(route[i] == 1 << i for i in range(57,73)), 'No route touches outside ambient57')
            need(all(axis < 1 << 57 for axis in route[:57]), 'All native views lie in ambient57')
            input_x = n.frame([(q,1)]) if not stage else n.completed(stage-1)
            input_y = () if not stage else n.frame(list(input_x)+[(q,-1)])
            local_x = n.frame(list(spectator)+[(q,sign)])
            local_y = spectator
            end_x = n.frame(list(spectator)+[(a,sign) for a in n.AXES[:9]])
            end_y = n.frame(list(end_x)+[(q,-sign)])
            output_x = n.completed(stage)
            output_y = n.frame(list(output_x)+[(q,-1)])
            maps = {'entry_X':F.between(n,input_x,route,local_x),
                    'entry_Y':F.between(n,input_y,route,local_y),
                    'exit_X':F.between(n,end_x,route,output_x),
                    'exit_Y':F.between(n,end_y,route,output_y)}
            delta = stage_frame(n,stage,q)
            # References cancel as operators on arbitrary raw inputs. No
            # historical assumption about which idles have run is needed.
            need(n.polynomial(n.frame(list(output_x)+[(a,-c) for a,c in input_x]))
                 == n.polynomial(delta), 'Exact diagonal physical D_s on X')
            need(n.polynomial(n.frame(list(output_y)+[(a,-c) for a,c in input_y]))
                 == n.polynomial(delta), 'Exact diagonal physical D_s on Y')
            cross = n.frame(list(output_y if sign == 1 else output_x)+
                            [(a,-c) for a,c in (input_x if sign == 1 else input_y)])
            wanted = n.frame(list(delta)+[(q,-1 if sign == 1 else 1)])
            need(n.polynomial(cross) == n.polynomial(wanted), 'Physical cross operator D_s Q^+-1')
            result.append({'stage':stage,'pair':pair,'port':port,'direction':direction,
                           'common_spectator_frame':list(spectator),'maps':maps})
    return result


def make_windows(n, phases, formal):
    output = []
    for number,window in enumerate(formal['retained_idle_windows']):
        stages = window['stages']
        patterns = [list(spec[1:]) for spec in (G.PAIRS if len(stages) == 2 else G.MIDDLE)
                    for _ in range(spec[0])]
        need(len(patterns) == 224, 'Every retained window has224 distinct possible owners')
        for index,widths in enumerate(patterns):
            side,port = ('X' if index < 112 else 'Y'),index % 112
            recipe = phases['recipes'][port]
            if 0 in stages:
                need(stages == [0,1], 'The retained initial window is D0D1')
                axes = recipe['idle_children'][0]['orthogonal_axes']
                shift = recipe['idle_children'][0]['translation_after']
            else:
                axes = [axis for stage in stages for axis in n.AXES[9+8*(stage-1):9+8*stage]]
                shift = 0
            desired = n.frame([term for stage in stages for term in stage_frame(n,stage,recipe['q'])])
            actual = n.frame([(axis,1) for axis in axes]+[(shift,2)])
            need(n.polynomial(actual) == n.polynomial(desired), 'Literal whole idle operator including phase')
            need(len(axes) == window['rank'] and sum(widths) <= len(axes), 'Every hosted helper fits')
            output.append({'family':number,'index':window['index'],'kind':window['kind'],
                           'pair':window['pair'],'stages':stages,'side':side,'port':port,
                           'owner':f"{side}{window['pair']}:{port}", 'widths':widths,
                           'axes':axes,'translation_after':shift})
    return output


def helper_assignment(n, phases, formal, local, helper_recipes):
    windows = make_windows(n,phases,formal)
    pools = []
    for stage in range(7):
        pool = defaultdict(deque)
        for recipe in helper_recipes['THREE-base']['recipes']:
            pool[recipe['width']].append(recipe['role'])
        pools.append(pool)
    bindings,residuals,fresh = [],[],[]
    paid = Counter(); targets = Counter({25:448,57:224})
    for window in windows:
        cursor = 0
        for stage,width in zip(window['stages'],window['widths']):
            if not width:
                continue
            need(pools[stage][width], 'A real local helper of this width exists')
            role = pools[stage][width].popleft()
            axes = window['axes'][cursor:cursor+width]; cursor += width
            bindings.append({'stage':stage,'role':role,'width':width,'owner':window['owner'],
                             'axes':axes,'kind':'original_idle','window_index':window['index']})
        for axes in G.split_axes(window['axes'][cursor:]):
            residuals.append({'owner':window['owner'],'after_stage':max(window['stages']),
                              'axes':axes,'rank':len(axes),'kind':'idle_remnant'})
            paid[len(axes)] += 1
    for stage,pool in enumerate(pools):
        for width,roles in sorted(pool.items()):
            for role in roles:
                owner = f'G{stage}:{role}'; target = max(6,width)
                bindings.append({'stage':stage,'role':role,'width':width,'owner':owner,
                                 'axes':list(n.AXES[:width]),'kind':'fresh'})
                fresh.append({'owner':owner,'stage':stage,'native_width':width,'target_rank':target})
                targets[target] += 1
                for axes in G.split_axes(list(n.AXES[width:target])):
                    residuals.append({'owner':owner,'after_stage':stage,'axes':axes,
                                      'rank':len(axes),'kind':'fresh_topup'})
                    paid[len(axes)] += 1
    coordinate_maps = {}
    for stage,(pair,direction) in enumerate(STAGES):
        native = local['providers']['THREE-base']['split_replays'][direction]['independent_native_replay']
        paid.update({int(rank):count for rank,count in native['paid_profile'].items()})
        selected = [row for row in bindings if row['stage'] == stage]
        need(len(selected) == 408 and {row['role'] for row in selected} == set(range(224,632)),
             'All408 actual native helper roles are assigned exactly once')
        need(len({row['owner'] for row in selected}) == 408, 'Every local helper has a distinct physical owner')
        active = {f'{side}{pair}:{port}' for side in ('X','Y') for port in range(112)}
        need(not active.intersection(row['owner'] for row in selected), 'No live main role is borrowed')
        for row in selected:
            key = ','.join(map(str,row['axes']))
            if key not in coordinate_maps:
                coordinate_maps[key] = G.coordinate_map(row['axes'],57)
            row['coordinate_map'] = key
            row['whole_helper_boundary'] = {'provider':'THREE-base','direction':direction,'role':row['role'],
                  'selector':'certificate.directions.direction.existing_native_boundary_normal_form'}
    need(dict(sorted(paid.items())) == PAID, 'Full actual paid histogram')
    need(dict(sorted(targets.items())) == TARGETS, 'All and only productive target fields')
    need(len(fresh) == 1570 and len(bindings) == 2856, 'Complete field and helper census')
    need(sum(k*v for k,v in targets.items())-sum(k*v for k,v in paid.items()) == 224, 'Rank-unit margin')
    need(max(paid) < min(targets), 'Strict recursive separation')
    return {'windows':windows,'helper_bindings':bindings,'owner_coordinate_maps':coordinate_maps,
            'paid_residuals':residuals,'fresh_outputs':fresh,'paid':PAID,'targets':TARGETS,
            'rank_margin':224,'productive_fields':2242,'owned_center_fields':1,'external_cleanup_fields':0}


def endpoint_normalizers(n, phases, formal):
    output = []; histogram = Counter()
    for role,term in enumerate(formal['exact_diagonal_monomials']):
        q_power,selected = term[0],term[1:]
        need(q_power in (-1,1) and set(selected) <= {0,1}, 'Exact Laurent endpoint alphabet')
        for port,recipe in enumerate(phases['recipes']):
            q = recipe['q']
            physical = n.frame([(q,q_power)]+[entry for stage,yes in enumerate(selected) if yes
                                                  for entry in stage_frame(n,stage,q)])
            axes = list(n.AXES[:9]) if selected[0] else [q]
            axes += [axis for stage in range(1,7) if selected[stage]
                     for axis in n.AXES[9+8*(stage-1):9+8*stage]]
            translation = q if q_power == -1 else 0
            repaired = n.frame(list(physical)+[(translation,2)])
            canonical_on_axes = n.frame((a,1) for a in axes)
            need(n.polynomial(repaired) == n.polynomial(canonical_on_axes), 'Exact endpoint phase including constant')
            if translation:
                need(n.polynomial(physical) != n.polynomial(canonical_on_axes), 'Missing phase repair really fails')
            rank = len(axes)
            need(rank == 1+8*sum(selected), 'Earned endpoint rank')
            matrix = G.coordinate_map(axes,57)
            need(matrix['columns'][:rank] == axes, 'Literal target-rank conjugation')
            output.append({'original_input_role':role,'port':port,'target_rank':rank,
                           'input_coordinate_columns':matrix['columns'],
                           'output_coordinate_inverse_rows':matrix['inverse_rows'],
                           'output_translation_before_inverse_map':translation,
                           'physical_frame':list(physical),'positive_axes':axes})
            histogram[rank] += 1
    need(histogram == Counter({25:448,57:224}), 'Main endpoint distribution')
    return output


def scalar_invoice(local, formal):
    native = sum(local['providers']['THREE-base']['split_replays'][direction]['independent_native_replay']
                 ['conservative_real_scalar_primitive_allowance'] for pair,direction in STAGES)
    adapters = formal['right_program']+formal['left_program']
    counts = Counter(row[0] for row in adapters)
    need(counts == Counter({'ADD':4,'SWAP':6,'SCALE':2}), 'Literal boundary scalar word')
    need(all(str(row[-1]) in ('1','-1') for row in adapters if row[0] in ('ADD','SCALE')),
         'Only unit scalar boundary coefficients')
    # Ordinary swap: three additions followed by one negation. Signed swap
    # needs three additions. No free whole-role movement is assumed here.
    adapter_adds = 4+6*3; adapter_negs = 2+6
    bridges = sum(row[0] == 'ADD' for row in formal['physical_events'])
    signed_swaps = sum(row[0] == 'SIGNED_SWAP' for row in formal['physical_events'])
    need(bridges == 12 and signed_swaps == 3, 'Literal global bridge and swap census')
    total = native+112*((adapter_adds+bridges+3*signed_swaps)*8+adapter_negs*2)
    return {'native_real_scalar_allowance':native,'boundary_unit_ADD_per_port':adapter_adds,
            'boundary_negations_per_port':adapter_negs,'bridge_unit_ADD_per_port':bridges,
            'terminal_signed_swap_unit_ADD_per_port':3*signed_swaps,
            'conservative_real_scalar_primitive_allowance':total,
            'coordinate_and_phase_moves':'Explicit separate fixed movement operations; not scalar ADDs and not paid recursive calls.'}


def run():
    F = G.load(HERE/'frame_exchange.py','p3_contacts')
    n = G.load(F.NATIVE,'p3_native_common')
    packet,phases = n.load_sources()
    local,pins,helpers = G.local_bindings()
    formal_source = G.read(FORMAL); formal = formal_source['selected_p3_keep43']
    tariff = G.read(TARIFF); audit = G.read(AUDIT)
    need(tariff['controller'] == formal, 'The native cover binds the exact priced controller')
    for path,wanted in tariff['source_sha256'].items():
        need(G.digest(ROOT/path) == wanted, 'Pinned actual tariff source '+path)
    for name,wanted in formal_source['source_sha256'].items():
        need(G.digest(FORMAL.parent/name) == wanted, 'Pinned formal word source '+name)
    main_contacts = contacts(n,F,phases)
    cover = helper_assignment(n,phases,formal,local,helpers)
    endings = endpoint_normalizers(n,phases,formal)
    scalar = scalar_invoice(local,formal)
    need({int(k):int(v) for k,v in tariff['invoice']['paid'].items()} == cover['paid'], 'Independent complete paid invoice agrees')
    need({int(k):int(v) for k,v in tariff['invoice']['targets'].items()} == cover['targets'], 'Independent productive credit agrees')
    for path in (FORMAL,TARIFF,AUDIT,HERE/'global_identity_cover.py',HERE/'frame_exchange.py',F.NATIVE):
        pins[str(path.relative_to(ROOT))] = G.digest(path)
    return {'schema':'complete-native-p3-keep43-owner-phase-cover/1',
            'status':'PASS_COMPLETE_FINITE_NATIVE_CONTROLLER_OWNER_PHASE_INVOICE',
            'generator_sha256':G.digest(__file__),'sources':pins,'immutable_phase_sources':n.PINS,
            'main_contacts':main_contacts,'contact_count':3136,'main_endpoint_normalizers':endings,
            'cover':cover,'scalar_invoice':scalar,'root_bracket':tariff['invoice']['root_bracket'],
            'physical_order':'Endpoint input coordinate maps; R; literal serialized controller with whole-call helper adapters; L; endpoint translations; endpoint inverse coordinate maps.',
            'native_local_contract':{'forward':'D_s [[1,0],[Q^-1,1]]','backward':'D_s [[1,-Q],[0,1]]',
                'meaning':'Exact raw-input operators, valid for arbitrary prior histories and after every boundary scalar basis change.'},
            'arbitrary_productive_input_fields':2242,'all_2856_original_helper_roles_assigned':True,
            'one_owned_center_reused_sequentially':True,'owned_center_arbitrary_at_entry_zero_at_return':True,
            'helpers_normalized_only_around_whole_native_invocations':True,
            'new_kappa':False,
            'remaining_transfer_obligations':['Finite mixed-to-uniform precompilation and ordinary supplier instantiation.',
                'Replacement precision, stock, scalar and movement constants for the resulting finite template.',
                'A compatible BIT supplier and the inherited outer analytic transfer.']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out',type=Path,default=HERE/'P3-NATIVE-COVER.json.gz')
    args = parser.parse_args()
    receipt = run()
    args.out.write_bytes(gzip.compress(json.dumps(receipt,sort_keys=True,separators=(',',':')).encode(),mtime=0))
    print(json.dumps({'status':receipt['status'],'targets':receipt['cover']['targets'],
                      'paid':receipt['cover']['paid'],'scalar':receipt['scalar_invoice'],
                      'root_bracket':receipt['root_bracket'],'sha256':G.digest(args.out)},sort_keys=True))


if __name__ == '__main__':
    main()
