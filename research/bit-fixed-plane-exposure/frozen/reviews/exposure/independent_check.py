#!/usr/bin/env python3
"""Independent complete fixed-E exposure certificates; no producer imports.

Reverse adjoints reconstruct semantic dirty columns. Forward seed-bitset
propagation reconstructs every causal mask. All saved partition fields are
checked; no optimizer or bounded search supplies the all-subset theorem.
Apache-2.0; substantial OpenAI Codex assistance.
"""
from copy import deepcopy
from fractions import Fraction as Q
from hashlib import sha256
from math import gcd, lcm
from pathlib import Path
import argparse
import gzip
import json

BASE = Path('/Users/ross/git/math')
LANE = BASE / '.research-automation/runs/kappa-changed-endpoints-20261019T0153Z/bit-native-caller'
RAW = BASE / 'integer-mult-bounds/research/bit-r438-transport-rehost/words/r438-t154.json.gz'
FULL = BASE / 'integer-mult-bounds/research/e8-bit-carrier-skeleton/data/bit/bitE8-r865.json.gz'
ROOTS = LANE / 'SELECTIVE-UNION-ROOTS-L8.json'
FRAMES = LANE / 'SELECTIVE-UNION-FRAMES-L8.json'
PINS = {RAW: 'a353999bceac4ac957f540adfd3e5f8768297138b27132eeb83332e2ea4b1022',
        FULL: '1fb726ea3818fe0837cceb0dd22a71a0814f064e5e781628104610d6468e0e55',
        ROOTS: '5c530085e98efef7b3757aec59d31b6b5ac23b4991e658aaf2a9ad68167b6e16',
        FRAMES: 'bd78a68e1667a8313c019a69cb23a8648e760123b33c2c66ac6da77e733ff6d7'}
PRODUCER_PINS = {
    LANE / 'selective_boost_screen.py': 'a95fb44bb7937066ae8d2f7a6b76c4a04c6c4370b284e52340a675f83b3dc504',
    LANE / 'selective_union_partition.py': '5715814bcb33703b59ecfc3114af868090961db75a3ea391b335f921c02969e5',
}
BATCH_KEYS = {'attribution', 'exact_scope', 'limits', 'mode', 'no_new_kappa', 'physical_scope',
              'planes_tested', 'positive_cut_planes', 'resource_weight', 'scientific_pin',
              'source', 'status', 'helper_order', 'semantic_dirty_columns', 'runs'}


def require(value, message):
    if not value:
        raise ValueError(message)


def digest(value):
    return sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def rref(rows):
    a = [list(map(Q, row)) for row in rows]
    rank = 0
    for col in range(8):
        pivot = next((i for i in range(rank, len(a)) if a[i][col]), None)
        if pivot is None:
            continue
        a[rank], a[pivot] = a[pivot], a[rank]
        scale = a[rank][col]
        a[rank] = [x / scale for x in a[rank]]
        for i in range(len(a)):
            if i != rank and a[i][col]:
                c = a[i][col]
                a[i] = [x - c * y for x, y in zip(a[i], a[rank])]
        rank += 1
        if rank == len(a):
            break
    return a[:rank]


def integral(row):
    denominator = 1
    for x in row:
        denominator = lcm(denominator, x.denominator)
    out = [int(x * denominator) for x in row]
    content = 0
    for x in out:
        content = gcd(content, x)
    return [x // content for x in out] if content else out


def normals(basis):
    pivots = [next(i for i, x in enumerate(row) if x) for row in basis]
    result = []
    for free in set(range(8)) - set(pivots):
        row = [Q(0)] * 8
        row[free] = 1
        for pivot, b in zip(pivots, basis):
            row[pivot] = -b[free]
        result.append(integral(row))
    return result


def contained(vectors, annihilator):
    return all(not sum(x * y for x, y in zip(v, row)) for v in vectors for row in annihilator)


def rank_binary(columns):
    # Least-significant pivot, distinct from the historical highest-pivot code.
    pivots = {}
    for value in columns:
        while value:
            bit = value & -value
            if bit in pivots:
                value ^= pivots[bit]
            else:
                pivots[bit] = value
                break
    return len(pivots)


def events_from_raw(raw, bases, orthogonals):
    require(len(bases[0]) == 0 and len(bases[1]) == 8, 'actual ZERO and FULL frames')
    require(len(raw['ret']) == 9 and len(set(raw['ret'])) == 9 and
            all(222 <= h < 660 for h in raw['ret']), 'nine distinct physical copied helpers')
    require(all(not 111 <= register < 222 for _, destination, sources in raw['A']
                for register in [destination, *sources]), 'A has no target incidence')
    current = raw['start'][:]
    events = []
    def move(register, frame, phase):
        old = current[register]
        if old != frame:
            require(contained([integral(v) for v in bases[old]], orthogonals[frame]), 'actual nested MOVE')
            require(len(bases[old]) < len(bases[frame]), 'strict actual MOVE')
            events.append(('move', register, old, frame, phase))
            current[register] = frame
    def phase(name):
        for frame, destination, sources in raw[name]:
            for register in [destination, *sources]:
                move(register, frame, name)
            for source in sources:
                require(source != destination, 'ADD has distinct actors')
                events.append(('add', destination, source, frame, name))
    phase('D')
    phase('A')
    for ordinal, source in enumerate(raw['ret']):
        frame = current[source]
        require(len(bases[frame]) == 7, 'every original COPY source is a hyperplane')
        events.append(('copy', source, 660, frame, ordinal))
        for port, totals in enumerate(raw['scatter']):
            if ordinal in totals:
                require(current[111 + port] == 0, 'private ZERO scatter')
                events.append(('add', 111 + port, 660, 0, 'scatter'))
        events.append(('erase', source, 660, frame, ordinal))
    phase('B')
    phase('C')
    for register, frame in enumerate(raw['final']):
        move(register, frame, 'endpoint')
    require(current == raw['final'], 'complete raw endpoints')
    require(all(len(bases[raw['final'][p]]) == 8 for p in range(111)), 'all source exits FULL')
    require(all(len(bases[raw['final'][111 + p]]) == 7 for p in range(111)), 'all original target caps have rank seven')
    return events


def semantic_dirty(raw, events):
    # Adjoint columns for all 111 final target coordinates at once. The
    # original initial compensation is excluded, exactly defining D.
    adjoint = [0] * 661
    for port in range(111):
        adjoint[111 + port] = 1 << port
    for op, dst, src, _, phase in reversed(events):
        if op == 'add' and phase != 'D':
            adjoint[src] ^= adjoint[dst]
        elif op == 'copy':
            adjoint[dst] ^= adjoint[src]
            adjoint[src] = 0
        elif op == 'erase':
            adjoint[src] = 0
    columns = adjoint[222:660]
    require(adjoint[111:222] == [1 << i for i in range(111)], 'old-target identity columns')
    direct = [0] * 438
    for frame, dst, sources in raw['D']:
        require(frame == 0 and 111 <= dst < 222, 'literal initial compensation at ZERO')
        for source in sources:
            require(222 <= source < 660, 'literal compensation helper binding')
            direct[source - 222] ^= 1 << (dst - 111)
    require(columns == direct, 'reverse semantic map equals every literal compensation column')
    require(rank_binary(columns) == 111, 'full dirty rank111 and nullity327')
    return columns


def causal_masks(events, raw, upper, keep_zero=True, absorb=True, bidirectional=True, include_initial_D=False):
    # Each bit names one of 438 possible entrance seeds. All sources and
    # targets initially have no promotion. Private snapshots remain ZERO.
    tags = [0] * 661
    for h in range(438):
        tags[222 + h] = 1 << h
    resources = [0] * 120
    for op, dst, src, frame, phase in events:
        if op == 'move':
            if absorb and upper[frame]:
                tags[dst] = 0
        elif op == 'add' and (phase != 'D' or include_initial_D):
            if src == 660 and keep_zero:
                continue
            if absorb and upper[frame]:
                tags[dst] = tags[src] = 0
            else:
                union = tags[dst] | tags[src]
                tags[dst] = union
                if bidirectional:
                    tags[src] = union
        elif op == 'copy':
            if not upper[frame]:
                resources[111 + phase] |= tags[dst]
            if not keep_zero:
                tags[src] = tags[dst]
        elif op == 'erase':
            tags[src] = 0
    for port in range(111):
        if not upper[raw['final'][111 + port]]:
            resources[port] |= tags[111 + port]
    masks = [0] * 438
    for resource, seeds in enumerate(resources):
        while seeds:
            bit = seeds & -seeds
            masks[bit.bit_length() - 1] |= 1 << resource
            seeds ^= bit
    return masks


RUN_KEYS = {'COPY_exposure', 'D_rank', 'E_basis', 'assigned_color_copies', 'dual_reachable_color_copies',
            'entrance_rank', 'exposure_mask', 'exposure_masks', 'ground_color_copies', 'kernel_dimension',
            'optimum_auxiliary_profit', 'partition_D_colors', 'partition_resource_slots', 'plane',
            'resource_weight', 'selected_helper_count', 'selected_helper_indices', 'selected_physical_helpers',
            'target_exposure', 'unassigned_color_copies'}


def check_partition(run, columns, masks):
    require(set(run) == RUN_KEYS, 'complete typed run field coverage')
    n, r, cap = len(columns), run['entrance_rank'], run['resource_weight']
    require(type(r) is int and r in (1, 2) and type(cap) is int and cap == 8, 'fixed dimensions and resource cap')
    require(type(run['ground_color_copies']) is int and run['ground_color_copies'] == r * n, 'complete colored groundset')
    seen = set()
    def claim(nodes):
        require(all(type(x) is int and 0 <= x < r * n for x in nodes), 'integer colored node range')
        require(len(set(nodes)) == len(nodes) and not seen.intersection(nodes), 'unique ownership of every colored node')
        seen.update(nodes)
    require(len(run['partition_D_colors']) == r, 'all independent colors present')
    for color, nodes in enumerate(run['partition_D_colors']):
        claim(nodes)
        require(all(x // n == color for x in nodes), 'physical helper/color binding')
        require(rank_binary([columns[x % n] for x in nodes]) == len(nodes), 'D class independent')
    for key, nodes in run['partition_resource_slots'].items():
        resource = int(key)
        require(str(resource) == key and 0 <= resource < 120, 'canonical actual resource ID')
        claim(nodes)
        require(len(nodes) <= cap and all(masks[x % n] >> resource & 1 for x in nodes), 'actual resource incidence and capacity')
    complement = sorted(set(range(r * n)) - seen)
    require(complement == run['unassigned_color_copies'] == [], 'true complete partition coverage')
    require(type(run['assigned_color_copies']) is int and run['assigned_color_copies'] == len(seen), 'assigned count')
    # With no unassigned sources, the retained residual reachability/cut is
    # empty. Check every field, rather than relying on optimum=0 alone.
    require(run['dual_reachable_color_copies'] == [], 'empty residual-reachability witness')
    require(run['selected_helper_indices'] == run['selected_physical_helpers'] == [], 'actual matching empty cut')
    integer_zero = ['D_rank', 'kernel_dimension', 'optimum_auxiliary_profit', 'selected_helper_count', 'target_exposure', 'COPY_exposure']
    require(all(type(run[k]) is int and run[k] == 0 for k in integer_zero), 'all matching cut counts/rank/profit')
    require(run['exposure_mask'] == '0', 'matching cut exposure')
    require(run['exposure_masks'] == [str(x) for x in masks], 'all438 actual causal masks')


def must_reject(action, name):
    try:
        action()
    except (ValueError, IndexError, KeyError):
        return True
    raise ValueError('control did not reject: ' + name)


def controls(run, columns, masks, events, raw, upper):
    outcomes = {}
    bad = deepcopy(run)
    c = next(i for i, nodes in enumerate(bad['partition_D_colors']) if nodes)
    bad['partition_D_colors'][c].append(bad['partition_D_colors'][c][0])
    outcomes['duplicated_actual_owner'] = must_reject(lambda: check_partition(bad, columns, masks), 'duplicate')
    bad = deepcopy(run)
    bad['partition_D_colors'][c].pop()
    outcomes['deleted_actual_owner'] = must_reject(lambda: check_partition(bad, columns, masks), 'coverage omission')
    color = run['partition_D_colors'][c]
    require(len(color) >= 2, 'rank mutation needs two independent columns')
    changed_D = columns[:]
    changed_D[color[1] % 438] = changed_D[color[0] % 438]
    outcomes['rank_collapsed_two_actual_columns'] = must_reject(lambda: check_partition(run, changed_D, masks), 'rank collapse')
    resource, nodes = next(iter(run['partition_resource_slots'].items()))
    changed_masks = masks[:]
    changed_masks[nodes[0] % 438] &= ~(1 << int(resource))
    outcomes['removed_used_resource_incidence'] = must_reject(lambda: check_partition(run, columns, changed_masks), 'incidence')
    bad = deepcopy(run)
    bad['ground_color_copies'] = True
    outcomes['boolean_replaces_integer_count'] = must_reject(lambda: check_partition(bad, columns, masks), 'type')
    no_stop = causal_masks(events, raw, upper, absorb=False)
    copied_tags = causal_masks(events, raw, upper, keep_zero=False)
    directed = causal_masks(events, raw, upper, bidirectional=False)
    initial_D = causal_masks(events, raw, upper, include_initial_D=True)
    outcomes['disable_frame_absorption_changed_helpers'] = sum(x != y for x, y in zip(no_stop, masks))
    outcomes['propagate_into_PRIVATEZERO_changed_helpers'] = sum(x != y for x, y in zip(copied_tags, masks))
    outcomes['wrong_directed_ADD_changed_helpers'] = sum(x != y for x, y in zip(directed, masks))
    outcomes['wrong_initial_D_inclusion_changed_helpers'] = sum(x != y for x, y in zip(initial_D, masks))
    # Absorption alone may be observationally redundant because all later
    # frames are monotone and resource guards exclude containing frames.
    # Report its actual response; do not promote it to a detected control.
    require(outcomes['wrong_directed_ADD_changed_helpers'] > 0, 'actual common-frame ADD control')
    require(outcomes['wrong_initial_D_inclusion_changed_helpers'] > 0, 'actual initial-compensation boundary control')
    require(outcomes['propagate_into_PRIVATEZERO_changed_helpers'] > 0, 'actual PRIVATEZERO control')
    outcomes['causal_mutations'] = {}
    for name, changed in [('PRIVATEZERO_transport', copied_tags), ('directed_ADD', directed), ('initial_D_included', initial_D)]:
        require(changed != masks, 'actual changed causal result: ' + name)
        outcomes['causal_mutations'][name] = {
            'changed_masks_sha256': digest(changed),
            'rejected_by_full_mask_and_partition_check': must_reject(lambda: check_partition(run, columns, changed), name),
        }
    outcomes['absorption_control_status'] = 'Insensitive here; retained as an observation, not a detected negative control.'
    return outcomes


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    for path, expected in PINS.items():
        require(sha256(path.read_bytes()).hexdigest() == expected, 'frozen input ' + str(path))
    raw = json.loads(gzip.decompress(RAW.read_bytes()))
    full = json.loads(gzip.decompress(FULL.read_bytes()))
    bases = [rref([raw['lines'][i] for i in frame]) for frame in raw['frames']]
    orthogonals = [normals(B) for B in bases]
    events = events_from_raw(raw, bases, orthogonals)
    columns = semantic_dirty(raw, events)
    todo = [(f'root{i}', rref([line])) for i, line in enumerate(full['lines'])]
    require(len(todo) == 120 and len({tuple(map(tuple, E)) for _, E in todo}) == 120, 'exact120 distinct root lines')
    frame_todo = [(f'frame{i}', B) for i, B in enumerate(bases) if len(B) == 2]
    require(len(frame_todo) == 153 and len({tuple(map(tuple, E)) for _, E in frame_todo}) == 153, 'exact153 distinct actual rank2 frames')
    by_name = dict(todo + frame_todo)
    all_runs, control_result, sharpness = [], None, None
    for path, mode, expected in ((ROOTS, 'roots', todo), (FRAMES, 'frames', frame_todo)):
        data = json.loads(path.read_bytes())
        require(set(data) == BATCH_KEYS, 'complete batch field coverage')
        require(data['mode'] == mode and type(data['resource_weight']) is int and data['resource_weight'] == 8, 'batch mode/cap')
        require(data['status'] == 'PASS_FINITE_NATIVE_PLANES_ALL_UNION_PARTITION_CERTIFICATES' and data['no_new_kappa'] is True, 'retained status/scope')
        require(data['scientific_pin'] == '20ecf2891d80b5acf18d980b2164fb44ea7faa90', 'scientific identity')
        require(data['helper_order'] == list(range(222, 660)), 'physical helper order')
        require(data['semantic_dirty_columns'] == columns, 'complete independent semantic D')
        require(data['positive_cut_planes'] == [] and data['planes_tested'] == len(expected), 'exact recorded family size')
        require([run['plane'] for run in data['runs']] == [name for name, _ in expected], 'all planes in exact source order')
        expected_sources = {str(p): h for p, h in {RAW: PINS[RAW], FULL: PINS[FULL], **PRODUCER_PINS}.items()}
        require(data['source'] == expected_sources, 'complete declared historical sources')
        for source, expected_hash in data['source'].items():
            require(sha256(Path(source).read_bytes()).hexdigest() == expected_hash, 'declared historical source authentication')
        for run in data['runs']:
            name = run['plane']
            E = by_name[name]
            serialized = [[str(x) for x in row] for row in E]
            require(run['E_basis'] == serialized and run['entrance_rank'] == len(E), 'exact actual E basis/rank')
            vectors = [integral(row) for row in E]
            upper = [contained(vectors, annihilator) for annihilator in orthogonals]
            masks = causal_masks(events, raw, upper)
            check_partition(run, columns, masks)
            all_runs.append(deepcopy(run))
            if name == 'frame116':
                union = 0
                for mask in masks:
                    union |= mask
                nullity = 438 - rank_binary(columns)
                require(len(E) == 2 and nullity == 327 and union.bit_count() == 90, 'full-helper sharpness witness')
                require((union & ((1 << 111) - 1)).bit_count() == 86 and (union >> 111).bit_count() == 4, 'all sharpness exposure resources')
                sharpness = {'plane': name, 'E_basis': serialized, 'helpers': list(range(222, 660)),
                             'D_rank': 111, 'nullity': nullity, 'exposure_mask': str(union), 'target_exposure': 86,
                             'COPY_exposure': 4, 'lambda7_profit': 2 * nullity - 7 * union.bit_count(),
                             'real_ratio_lower_bound': str(Q(2 * nullity, union.bit_count())),
                             'claim': '8 is the least integer common coefficient for this fixed273-plane family, not the optimal real coefficient.'}
                require(sharpness['lambda7_profit'] == 24, 'integer-seven counterexample')
                control_result = controls(run, columns, masks, events, raw, upper)
        print('verified', mode, len(data['runs']), 'complete planes', flush=True)
    require(len(all_runs) == 273 and control_result and sharpness, 'entire declared result')
    result = {'status': 'PASS_INDEPENDENT_ALL273_FIXED_E_EXPOSURE_PARTITIONS', 'no_new_kappa': True,
              'source_sha256': {str(p): h for p, h in PINS.items()},
              'historical_producer_sha256': {str(p): h for p, h in PRODUCER_PINS.items()},
              'semantic_dirty_columns': columns, 'semantic_D_sha256': digest(columns),
              'chronological_event_count': len(events), 'chronological_events_sha256': digest(events),
              'exact_plane_count': 273, 'complete_verified_runs': all_runs,
              'sharp_integer_coefficient_witness': sharpness, 'controls': control_result,
              'written_proof': 'PROOF-EXPOSURE.md: partition counting proves every helper subset for each certified fixed E.',
              'scope': 'F2 full semantic D; unchanged causal common-E joins; PRIVATEZERO; no cold-target quotient, mixed-E, all-E, literal selective supplier or rate obstruction.'}
    encoded = json.dumps(result, indent=2, sort_keys=True) + '\n'
    if args.output:
        args.output.write_text(encoded)
    else:
        print(encoded, end='')


if __name__ == '__main__':
    main()
