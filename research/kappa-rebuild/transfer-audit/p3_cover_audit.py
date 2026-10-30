#!/usr/bin/env python3
"""Adversarial replay of p3 physical ownership, normalizer order and invoice.

Apache-2.0; substantial OpenAI assistance. Separate from the cover producer.
"""
from collections import Counter, defaultdict
from fractions import Fraction
from hashlib import sha256
from pathlib import Path
import gzip
import json

from finite_dag_audit import Rule, Compiler

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
INPUT = HERE.parent/'controller/P3-NATIVE-COVER.json.gz'


def need(test, message):
    if not test:
        raise AssertionError(message)


def digest(path):
    return sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    raw = Path(path).read_bytes()
    return json.loads(gzip.decompress(raw) if str(path).endswith('.gz') else raw)


def main():
    receipt = read(INPUT)
    need(digest(HERE.parent/'controller/p3_native_cover.py') == receipt['generator_sha256'], 'Exact cover generator')
    for path, expected in receipt['sources'].items():
        need(digest(ROOT/path) == expected, 'Pinned source '+path)
    independent = read(HERE/'P3-NATIVE-AUDIT.json.gz')
    formal = read(HERE.parent/'bit/COMPLEX-CONTROLLER-FACTOR.json')['selected_p3_keep43']
    ours = {(row['stage'],row['port']):row for row in independent['contacts']}
    for row in receipt['main_contacts']:
        other = ours[row['stage'],row['port']]
        need(all(row[key] == other[key] for key in ('maps','pair','direction')), 'Independent actual contact recipes agree')
    ours_ends = {(row['output_role'],row['port']):row for row in independent['endpoint_normalizers']}
    main_ranks = {}
    for row in receipt['main_endpoint_normalizers']:
        key = row['original_input_role'],row['port']
        other = ours_ends[key]
        need(row['target_rank'] == other['rank'] and row['positive_axes'] == other['target_axes'], 'Independent target axes')
        need(row['output_translation_before_inverse_map'] == other['physical_translation_after'], 'Translation precedes output inverse')
        columns, inverse_rows = row['input_coordinate_columns'],row['output_coordinate_inverse_rows']
        need(columns[:row['target_rank']] == row['positive_axes'], 'Input conjugation has exact required columns')
        for j, column in enumerate(columns):
            decoded = sum(((r & column).bit_count() & 1) << i for i,r in enumerate(inverse_rows))
            need(decoded == 1 << j, 'Output map is inverse of actual input map')
        role,port = key
        main_ranks[f'{"Y" if role%2 else "X"}{role//2}:{port}'] = row['target_rank']
    need(receipt['physical_order'] == 'Endpoint input coordinate maps; R; literal serialized controller with whole-call helper adapters; L; endpoint translations; endpoint inverse coordinate maps.',
         'The emitted order realizes G^-1 X L M R G')
    cover = receipt['cover']
    helpers_path = HERE.parent/'complex/fresh-certificates/THREE-base-HELPER-BOUNDARIES.json.gz'
    helper_width = {row['role']:row['width'] for row in read(helpers_path)['recipes']}
    stage_table = {event[1]:(event[2], 'backward' if event[3] else 'forward')
                   for event in formal['physical_events'] if event[0]=='LOCAL'}
    by_stage = defaultdict(list)
    by_window = defaultdict(list)
    for row in cover['helper_bindings']:
        stage = row['stage']
        need(helper_width[row['role']] == row['width'] == len(row['axes']), 'Actual native helper width, not a rank-only substitute')
        contract = row['whole_helper_boundary']
        need(contract['direction'] == stage_table[stage][1] and contract['role'] == row['role'] and
             contract['provider'] == 'THREE-base', 'Exact oriented helper normalizer')
        by_stage[stage].append(row)
        if row['kind'] == 'original_idle':
            by_window[row['window_index'],row['owner']].append(row)
        matrix = cover['owner_coordinate_maps'][row['coordinate_map']]
        need(matrix['columns'][:row['width']] == row['axes'], 'Helper conjugation reaches actual idle axes')
        for j,column in enumerate(matrix['columns']):
            decoded = sum(((r & column).bit_count() & 1) << i for i,r in enumerate(matrix['inverse_rows']))
            need(decoded == 1 << j, 'Helper route inverse')
    for stage, rows in by_stage.items():
        need({row['role'] for row in rows} == set(range(224,632)) and len(rows)==408, 'All local helper roles used exactly once')
        need(len({row['owner'] for row in rows}) == 408, 'Helper physical owners injective')
        active_pair = stage_table[stage][0]
        active = {f'{side}{active_pair}:{port}' for side in ('X','Y') for port in range(112)}
        need(not active & {row['owner'] for row in rows}, 'No helper borrows a live main register')
    events = formal['physical_events']
    paid_by_owner = defaultdict(list)
    for row in cover['paid_residuals']:
        need(row['rank'] == len(row['axes']) and 1 <= row['rank'] <= 5, 'Actual completion width')
        paid_by_owner[row['owner'],row['after_stage'],row['kind']].append(row)
    for window in cover['windows']:
        stages, pair = window['stages'],window['pair']
        idle_index = next(i for i,event in enumerate(events) if event == ['IDLE',pair,stages])
        first_index = next(i for i,event in enumerate(events) if event[0]=='LOCAL' and event[1]==min(stages))
        for event in events[first_index:idle_index]:
            if event[0] == 'LOCAL':
                need(event[2] != pair, 'Owned idle field is never an active local input in the window')
            elif event[0] == 'ADD':
                need(event[1]//2 != pair and event[2]//2 != pair, 'No interleaved bridge reads or writes a partially completed idle')
            elif event[0] == 'SIGNED_SWAP':
                need(event[1]//2 != pair, 'No swap before idle completion')
        assigned = sorted(by_window[window['index'],window['owner']], key=lambda row:row['stage'])
        need([(row['stage'],row['width']) for row in assigned] ==
             [(s,w) for s,w in zip(stages,window['widths']) if w], 'Actual window slice assignment')
        pieces = [axis for row in assigned for axis in row['axes']]
        rests = paid_by_owner[window['owner'],max(stages),'idle_remnant']
        pieces += [axis for row in rests for axis in row['axes']]
        need(pieces == window['axes'], 'Every idle axis is funded once in chronological order')
    fresh = {row['owner']:row for row in cover['fresh_outputs']}
    fresh_binding = {row['owner']:row for row in cover['helper_bindings'] if row['kind']=='fresh'}
    need(len(fresh)==len(fresh_binding)==1570 and set(fresh)==set(fresh_binding), 'Every fresh field is an independent actual helper')
    for name, row in fresh.items():
        pieces = list(fresh_binding[name]['axes'])
        pieces += [axis for extra in paid_by_owner[name,row['stage'],'fresh_topup'] for axis in extra['axes']]
        need(pieces == [1 << i for i in range(row['target_rank'])], 'Every fresh full target includes paid topup axes')
    local_receipt = read(HERE.parent/'complex/full-identity-certificates/RESULT.json')
    native = read(HERE.parent/'complex/full-identity-certificates/THREE-base-FULL-IDENTITY-NATIVE.json.gz')
    rounds = []
    native_scalar = 0
    for stage in range(7):
        pair,direction = stage_table[stage]
        native_scalar += local_receipt['providers']['THREE-base']['split_replays'][direction]['independent_native_replay']['conservative_real_scalar_primitive_allowance']
        owner = {row['role']:row['owner'] for row in by_stage[stage]}
        for event in native[direction]:
            if event[0]=='climb':
                role=event[2]
                name = f'X{pair}:{role}' if role<112 else f'Y{pair}:{role-112}' if role<224 else owner[role]
                rounds.append((event[-1],name))
            elif event[0]=='center':
                rounds.append((event[-1],'owned-C0'))
        rounds += [(row['rank'],row['owner']) for row in cover['paid_residuals'] if row['after_stage']==stage]
    roles = tuple(sorted(main_ranks.items()))+tuple((name,row['target_rank']) for name,row in sorted(fresh.items()))
    rule = Rule(roles,tuple(rounds))
    need(rule.targets == Counter({int(k):v for k,v in cover['targets'].items()}), 'All productive ranks independently counted')
    need(Counter(rank for rank,name in rounds) == Counter({int(k):v for k,v in cover['paid'].items()}), 'Every paid child independently counted on its actual owner')
    scalar = native_scalar+112*((22+12+9)*8+8*2)
    need(scalar == receipt['scalar_invoice']['conservative_real_scalar_primitive_allowance'] == 1147304,
         'Complete arithmetic invoice includes all six swap negations')
    compiler = Compiler(rule)
    compiled = compiler.compile(57)
    need(compiled['width']==2242 and compiled['leaves']==127570 and compiled['units']==1, 'Full rank57 completion including all partial-source complements')
    result = {'schema':'independent-p3-owner-order-and-complete-tariff-audit/1',
              'status':'PASS_ALL2856_HELPERS_CAUSAL_WINDOWS_MAIN_NORMALIZER_ORDER_AND_COMPLETE_BILL',
              'source_sha256':digest(__file__),'input_sha256':digest(INPUT),
              'main_phase_audit_sha256':digest(HERE/'P3-NATIVE-AUDIT.json.gz'),
              'native_local_source_bound':True,'helper_bindings':2856,'independent_productive_fields':2242,
              'targets':dict(sorted(rule.targets.items())), 'paid':dict(sorted(Counter(r for r,n in rounds).items())),
              'owned_center_uncredited':1,'arithmetic_allowance':scalar,
              'uniform_rank57':{key:str(value) if isinstance(value,Fraction) else value
                                for key,value in compiled.items() if key!='ordered_requirements'},
              'uniform_rank57_event_graph':compiler.trees[57].summary(),
              'limits':['Ideal native finite unit and finite integer compilation audit.',
                        'The rank57 depth-zero supplier is not asserted to attain the mixed exponent.',
                        'Large fixed-template existence, updated precision/stock and outer transfer are separate documented steps.']}
    (HERE/'P3-COVER-AUDIT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'status':result['status'],'targets':result['targets'],'paid':result['paid'],
                      'scalar':scalar,'uniform_full57_paid1':compiled['leaves']}))


if __name__=='__main__':
    main()
