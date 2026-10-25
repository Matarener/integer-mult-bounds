#!/usr/bin/env python3
"""Independent phase/contact audit for the actual p2 whole-job interface.

Apache-2.0, substantial OpenAI assistance. Uses direct Fourier symbols and
serialized maps, never the producer's polynomial/contact/coordinate functions.
The established native local word is authenticated, not silently re-proved.
"""
from collections import Counter
from hashlib import sha256
from itertools import combinations
from pathlib import Path
import gzip
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
COMPLEX = HERE.parent/'complex'
INPUT = HERE.parent/'controller/GLOBAL-IDENTITY-COVER.json.gz'
AXES = tuple(1 << i for i in range(73))


def need(test, message):
    if not test:
        raise AssertionError(message)


def digest(path):
    return sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    raw = Path(path).read_bytes()
    return json.loads(gzip.decompress(raw) if str(path).endswith('.gz') else raw)


def act(columns, vector):
    answer = 0
    while vector:
        low = vector & -vector
        answer ^= columns[low.bit_length()-1]
        vector ^= low
    return answer


def normalized(terms):
    weights = Counter()
    for axis, value in terms:
        weights[axis] += value
    return tuple(sorted((axis, value % 4) for axis, value in weights.items() if axis and value % 4))


def value(terms, address):
    return sum(weight*((axis & address).bit_count() & 1) for axis, weight in terms) % 4


def discrepancy(old, new, columns, shift):
    return normalized([(act(columns, axis), weight) for axis, weight in old]+
                      [(shift, 2)]+[(axis, -weight) for axis, weight in new])


def main():
    receipt = read(INPUT)
    producer = HERE.parent/'controller/global_identity_cover.py'
    need(digest(producer) == receipt['generator_sha256'], 'Actual global generator pin')
    for path, expected in receipt['sources'].items():
        need(digest(ROOT/path) == expected, 'Actual native source pin '+path)
    phase_path = ROOT/'research/kappa-next-regime/direct-decoder/sources/DATA-PHASES.json'
    need(digest(phase_path) == receipt['immutable_phase_sources']['DATA-PHASES.json'], 'Exact external port reference')
    phases = read(phase_path)
    points = (0,)+AXES[:41]+tuple(a ^ b for a, b in combinations(AXES[:41], 2))
    cache = set()
    count = 0
    changed_phase_rejected = False
    for row in receipt['main_contacts']:
        stage, port = row['stage'], row['port']
        q = phases['recipes'][port]['q']
        sign = 1 if row['direction'] == 'forward' else -1
        spectator = tuple((axis, 1) for axis in AXES[9:9+8*stage])
        previous = tuple((axis, 1) for axis in AXES[:9+8*(stage-1)]) if stage else ()
        completed = tuple((axis, 1) for axis in AXES[:9+8*stage])
        input_x = ((q, 1),) if stage == 0 else previous
        input_y = () if stage == 0 else previous+((q, -1),)
        local_x0 = spectator+((q, sign),)
        local_y0 = spectator
        local_x1 = spectator+tuple((axis, sign) for axis in AXES[:9])
        local_y1 = local_x1+((q, -sign),)
        pairs = {'entry_X':(input_x, local_x0), 'entry_Y':(input_y, local_y0),
                 'exit_X':(local_x1, completed), 'exit_Y':(local_y1, completed+((q, -1),))}
        need(normalized(row['common_spectator_frame']) == normalized(spectator), 'Declared common spectator frame')
        for kind, (old, new) in pairs.items():
            recipe = row['maps'][kind]
            columns, inverse = recipe['owner_columns'], recipe['inverse_owner_columns']
            need(len(columns) == len(inverse) == 73, 'Explicit full route and inverse')
            need(columns[41:] == inverse[41:] == list(AXES[41:]), 'All unselected high axes are spectators')
            need(all(x < (1 << 41) for x in columns[:41]+inverse[:41]), 'Only ambient41 coordinates mixed')
            need(all(act(columns, inverse[i]) == act(inverse, columns[i]) == AXES[i] for i in range(73)),
                 'Exact serialized inverse coordinate map')
            need(recipe['inverse_physical_shift'] == act(inverse, recipe['physical_shift']), 'Exact inverse shift')
            for before, after, matrix, shift in ((old, new, columns, recipe['physical_shift']),
                                                 (new, old, inverse, recipe['inverse_physical_shift'])):
                delta = discrepancy(before, after, matrix, shift)
                if delta not in cache:
                    need(all(value(delta, address) == 0 for address in points), 'Degree-two exact Fourier phase')
                    cache.add(delta)
            need(recipe['global_phase_Z4'] == 0, 'Absolute global phase is included')
            if not changed_phase_rejected and stage:
                bad = discrepancy(old, new, columns, recipe['physical_shift'] ^ 1)
                changed_phase_rejected = any(value(bad, address) for address in points)
            count += 1
    need(count == 2240 and changed_phase_rejected, 'All native forward/backward contacts and mutation control')
    case = receipt['all_three']
    map_count = 0
    for recipe in case['owner_coordinate_maps'].values():
        columns, rows = recipe['columns'], recipe['inverse_rows']
        need(len(columns) == len(rows) == 41, 'Complete helper coordinate extension')
        for j, column in enumerate(columns):
            decoded = sum(((row & column).bit_count() & 1) << i for i, row in enumerate(rows))
            need(decoded == AXES[j], 'Helper inverse matrix is exact')
        map_count += 1
    by_stage = {}
    for row in case['helper_bindings']:
        key = row['coordinate_map']
        matrix = case['owner_coordinate_maps'][key]
        need(matrix['columns'][:row['width']] == row['axes'], 'Actual target axes match helper map')
        by_stage.setdefault(row['stage'], []).append(row)
    for stage, rows in by_stage.items():
        need(len(rows) == 408 and {row['role'] for row in rows} == set(range(224, 632)), 'Every helper bound once')
        need(len({row['owner'] for row in rows}) == 408, 'Independent helper owners at invocation')
    base = read(COMPLEX/'full-identity-certificates/THREE-base-FULL-IDENTITY-CANONICAL.json.gz')
    extra = read(COMPLEX/'full-identity-certificates/THREE-extra-FULL-IDENTITY-CANONICAL.json.gz')
    changed_keys = sorted(key for key in base if base[key] != extra[key])
    need(changed_keys == ['frames', 'warps'], 'Provider variant differences are isolated')
    need(all(base['frames'][base[endpoint][i]] == extra['frames'][extra[endpoint][i]]
             for endpoint in ('start', 'final') for i in range(632)), 'All632 endpoint references coincide')
    need(base['ports'] == extra['ports'], 'Original external port references coincide')
    result = {'schema':'independent-p2-native-whole-job-boundary-audit/1',
              'status':'PASS_2240_PHASE_CONTACTS_HELPER_MAPS_AND_FIXED_PROVIDER_INTERFACE',
              'source_sha256':digest(__file__), 'input_sha256':digest(INPUT),
              'contact_count':count, 'inverse_contacts_also_checked':count,
              'degree_two_determining_points':len(points), 'unique_discrepancy_patterns':len(cache),
              'helper_bindings':sum(map(len, by_stage.values())), 'helper_coordinate_maps':map_count,
              'all632_base_extra_endpoints_identical':True,
              'base_extra_changed_internal_keys':changed_keys,
              'changed_phase_negative_control_rejected':changed_phase_rejected,
              'tensor_lift':'Proved structurally in AUDIT.md; fixed binary-affine maps and Z4 quadratic phases lift columnwise, with absolute phase multiplied by f.',
              'scope':'Independent finite interface/phase audit, conditional on the authenticated complete local native operator. Not a rounded multiplication theorem.'}
    (HERE/'NATIVE-BOUNDARY-AUDIT.json').write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    print(json.dumps(result, sort_keys=True))


if __name__ == '__main__':
    main()
