#!/usr/bin/env python3
"""Independent exact p3 Laurent replay, native contacts, and output phases.

Apache-2.0; substantial OpenAI assistance. This reads the proposed event and
adapter word, not its polynomial generator. Native local words are separately
authenticated. Helper placement and complete recursive tariffs are caller
obligations, not inferred from the main output factorization.
"""
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from itertools import combinations
from pathlib import Path
import gzip
import importlib.util
import json
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
INPUT = HERE.parent/'bit/COMPLEX-CONTROLLER-FACTOR.json'
NATIVE_COMMON = ROOT/'research/kappa-next-regime/direct-decoder/native_common.py'
LOCAL_RECEIPT = HERE.parent/'complex/full-identity-certificates/RESULT.json'
AXES = tuple(1 << i for i in range(73))


def need(test, message):
    if not test:
        raise AssertionError(message)


def digest(path):
    return sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    data = Path(path).read_bytes()
    return json.loads(gzip.decompress(data) if str(path).endswith('.gz') else data)


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def add(a, b, coefficient=1):
    out = a.copy()
    for word, value in b.items():
        out[word] = out.get(word, Q(0))+coefficient*value
        if not out[word]:
            del out[word]
    return out


def shift(polynomial, delta, coefficient=1):
    return {tuple(a+b for a, b in zip(word, delta)):coefficient*value
            for word, value in polynomial.items()}


def replay(case):
    count = 2*case['pairs']
    variables = len(case['coefficient_variables'])
    zero = (0,)*variables
    matrix = [[{zero:Q(i == j)} if i == j else {} for j in range(count)] for i in range(count)]
    # Right boundary is the first physical operation.
    for event in case['right_program']+case['physical_events']+case['left_program']:
        kind = event[0]
        if kind == 'ADD':
            _, destination, source, coefficient = event
            matrix[destination] = [add(a, b, Q(coefficient))
                                   for a, b in zip(matrix[destination], matrix[source])]
        elif kind == 'SCALE':
            _, role, coefficient = event
            matrix[role] = [{word:Q(coefficient)*value for word, value in row.items()} for row in matrix[role]]
        elif kind == 'SWAP':
            _, a, b = event
            matrix[a], matrix[b] = matrix[b], matrix[a]
        elif kind == 'SIGNED_SWAP':
            _, a, b = event
            matrix[a], matrix[b] = matrix[b], [{word:-value for word, value in row.items()} for row in matrix[a]]
        elif kind == 'IDLE':
            _, pair, stages = event
            delta = (0,)+tuple(int(s in stages) for s in range(variables-1))
            for role in (2*pair, 2*pair+1):
                matrix[role] = [shift(row, delta) for row in matrix[role]]
        elif kind == 'LOCAL':
            _, stage, pair, backward = event
            x, y = 2*pair, 2*pair+1
            q_delta = (1 if backward else -1,)+(0,)*(variables-1)
            destination, source, coefficient = (x, y, -1) if backward else (y, x, 1)
            matrix[destination] = [add(a, shift(b, q_delta), coefficient)
                                   for a, b in zip(matrix[destination], matrix[source])]
            d_delta = tuple(int(i == stage+1) for i in range(variables))
            for role in (x, y):
                matrix[role] = [shift(row, d_delta) for row in matrix[role]]
        else:
            raise AssertionError('Unknown actual event '+kind)
    wanted = [[{tuple(case['exact_diagonal_monomials'][i]):Q(1)} if i == j else {}
               for j in range(count)] for i in range(count)]
    need(matrix == wanted, 'Every Laurent coefficient of the literal boundary/controller word')
    return matrix


def act(columns, vector):
    out = 0
    while vector:
        low = vector & -vector
        out ^= columns[low.bit_length()-1]
        vector ^= low
    return out


def normalize(terms):
    result = Counter()
    for axis, coefficient in terms:
        result[axis] += coefficient
    return tuple(sorted((axis, value % 4) for axis, value in result.items() if axis and value % 4))


def evaluate(terms, address):
    return sum(coefficient*((axis & address).bit_count() & 1) for axis, coefficient in terms) % 4


def affine_contact(old, new, columns, points, cache):
    moved = tuple((act(columns, axis), coefficient) for axis, coefficient in old)
    delta = [(evaluate(new, axis)-evaluate(moved, axis)) % 4 for axis in AXES[:57]]
    need(all(value % 2 == 0 for value in delta), 'Native contact has no missing Fourier rank')
    translation = sum((value//2) << i for i, value in enumerate(delta))
    error = normalize(list(moved)+[(translation, 2)]+[(axis, -coefficient) for axis, coefficient in new])
    if error not in cache:
        need(all(evaluate(error, point) == 0 for point in points), 'Complete native quadratic phase')
        cache.add(error)
    inverse = tuple(sum(((columns[j] >> i) & 1) << j for j in range(73)) for i in range(73))
    need(all(act(columns, inverse[i]) == act(inverse, columns[i]) == AXES[i] for i in range(73)),
         'Actual route is orthogonal and explicitly inverted')
    inverse_translation = act(inverse, translation)
    inverse_error = normalize([(act(inverse, axis), coefficient) for axis, coefficient in new]+
                              [(inverse_translation, 2)]+[(axis, -coefficient) for axis, coefficient in old])
    if inverse_error not in cache:
        need(all(evaluate(inverse_error, point) == 0 for point in points), 'Inverse contact absolute phase')
        cache.add(inverse_error)
    return {'owner_columns':list(columns), 'inverse_owner_columns':list(inverse),
            'physical_shift':translation, 'inverse_physical_shift':inverse_translation,
            'global_phase_Z4':0}


def extend(axes, dimension=57):
    basis = {}
    columns = []

    def insert(vector):
        value = vector
        for pivot in sorted(basis, reverse=True):
            if value >> pivot & 1:
                value ^= basis[pivot]
        if not value:
            return False
        basis[value.bit_length()-1] = value
        columns.append(vector)
        return True

    need(all(insert(axis) for axis in axes), 'Independent actual target axes')
    for axis in AXES[:dimension]:
        insert(axis)
    need(len(columns) == dimension, 'Invertible endpoint coordinate extension')
    return columns


def main():
    receipt = read(INPUT)
    for name, expected in receipt['source_sha256'].items():
        need(digest(INPUT.parent/name) == expected, 'Actual proposed Laurent-source pin')
    case = receipt['selected_p3_keep43']
    need(case['pairs'] == 3 and case['keep_idle_mask'] == 43, 'Selected actual controller')
    replay(case)
    native = read(LOCAL_RECEIPT)
    provider = native['providers']['THREE-base']
    for name, expected in provider['artifacts'].items():
        need(digest(LOCAL_RECEIPT.parent/name) == expected, 'Authenticated actual native word')
    need(provider['all_632_persistent_inputs_arbitrary'] and provider['all_408_helpers_autonomous'],
         'Native unit accepts arbitrary independent raw fields')
    common = load(NATIVE_COMMON, 'p3_audit_native_source')
    packet, phases = common.load_sources()
    points = (0,)+AXES[:57]+tuple(a ^ b for a, b in combinations(AXES[:57], 2))
    phase_cache = set()
    contacts = []
    stages = [(event[1], event[2], event[3]) for event in case['physical_events'] if event[0] == 'LOCAL']
    need([s for s, pair, backward in stages] == list(range(7)), 'All seven chronological native stages')
    for stage, pair, backward in stages:
        sign = -1 if backward else 1
        spectator = tuple((axis, 1) for axis in AXES[9:9+8*stage])
        previous = tuple((axis, 1) for axis in AXES[:9+8*(stage-1)]) if stage else ()
        completed = tuple((axis, 1) for axis in AXES[:9+8*stage])
        for port, data in enumerate(phases['recipes']):
            q = data['q']
            route = tuple(common.source_route(phases, stage, port))
            need(route[57:] == AXES[57:] and all(x < 1 << 57 for x in route[:57]), 'Fixed ambient57 route')
            need(all(act(route, route[i]) == AXES[i] for i in range(73)), 'Port route cancels on an identity shear')
            raw_x0 = ((q, 1),) if stage == 0 else previous
            raw_y0 = () if stage == 0 else previous+((q, -1),)
            local_x0 = spectator+((q, sign),)
            local_y0 = spectator
            local_x1 = spectator+tuple((axis, sign) for axis in AXES[:9])
            local_y1 = local_x1+((q, -sign),)
            old_new = {'entry_X':(raw_x0, local_x0), 'entry_Y':(raw_y0, local_y0),
                       'exit_X':(local_x1, completed), 'exit_Y':(local_y1, completed+((q, -1),))}
            maps = {name:affine_contact(old, new, route, points, phase_cache)
                    for name, (old, new) in old_new.items()}
            contacts.append({'stage':stage, 'pair':pair, 'port':port,
                             'direction':'backward' if backward else 'forward', 'maps':maps})
    endpoints = []
    ranks = Counter()
    omitted_translation_rejected = 0
    for port, data in enumerate(phases['recipes']):
        q = data['q']
        for output, term in enumerate(case['exact_diagonal_monomials']):
            q_power, stages = term[0], term[1:]
            terms = [(q, q_power)]
            if stages[0]:
                terms += [(axis, 1) for axis in AXES[:9]]+[(q, -1)]
            for stage in range(1, 7):
                if stages[stage]:
                    terms += [(axis, 1) for axis in AXES[9+8*(stage-1):9+8*stage]]
            axes = list(AXES[:9]) if stages[0] else [q]
            for stage in range(1, 7):
                if stages[stage]:
                    axes += list(AXES[9+8*(stage-1):9+8*stage])
            translation = q if q_power == -1 else 0
            need(q_power in (-1, 1), 'Only exact free Q-square repair is used')
            wanted = tuple((axis, 1) for axis in axes)
            error = normalize(terms+[(translation, 2)]+[(axis, -1) for axis in axes])
            need(all(evaluate(error, point) == 0 for point in points), 'Full exact endpoint including phase')
            if translation:
                wrong = normalize(terms+[(axis, -1) for axis in axes])
                need(any(evaluate(wrong, point) for point in points), 'Missing Q-square repair changes the operator')
                omitted_translation_rejected += 1
            columns = extend(axes)
            endpoints.append({'port':port, 'output_role':output, 'rank':len(axes),
                              'physical_translation_after':translation,
                              'target_axes':axes, 'canonical_to_target_columns':columns,
                              'exact_absolute_phase':True})
            ranks[len(axes)] += 1
    need(ranks == Counter({25:448,57:224}), 'Actual positive canonical main target inventory')
    boundary_counts = Counter(event[0] for event in case['left_program']+case['right_program'])
    need(boundary_counts == Counter({'ADD':4,'SWAP':6,'SCALE':2}), 'Literal scalar boundary inventory')
    need(all(Q(event[-1]) in (1,-1) for event in case['left_program']+case['right_program']
             if event[0] in ('ADD','SCALE')), 'Boundary scalars are dyadic units')
    output = {'schema':'independent-p3-native-Laurent-boundary-binding/1',
              'status':'PASS_LITERAL_LAURENT_NATIVE_CONTACTS_AND_ALL672_MAIN_OUTPUT_PHASES',
              'source_sha256':digest(__file__), 'proposed_factor_sha256':digest(INPUT),
              'native_local_receipt_sha256':digest(LOCAL_RECEIPT),
              'native_route_source_sha256':digest(NATIVE_COMMON),
              'immutable_phase_sources':common.PINS,
              'literal_Laurent_coefficient_replay':True,
              'native_local_contract':{'forward':'D_s * [[1,0],[Q^-1,1]]',
                                       'backward':'D_s * [[1,-Q],[0,1]]',
                                       'D0':'F9 * Q^-1', 'Ds_for_s_positive':'C on fresh eight axes',
                                       'arbitrary_raw_inputs':True,
                                       'derivation':'Native exact reference conjugation; equal involutive port routes cancel on the identity-response shear.'},
              'contacts':contacts, 'contact_count':len(contacts)*4,
              'inverse_contacts_checked':len(contacts)*4,
              'phase_determining_addresses':len(points), 'unique_phase_patterns':len(phase_cache),
              'canonical_main_targets':dict(sorted(ranks.items())), 'endpoint_normalizers':endpoints,
              'missing_endpoint_translation_controls_rejected':omitted_translation_rejected,
              'boundary_scalar_inventory':dict(boundary_counts),
              'arithmetic_only_boundary_allowance_per_port':{'unit_ADD':22,'negate':8,
                                                            'real_scalar_primitives':22*8+8*2},
              'alternative_boundary_implementation':'Six whole-role permutations, four unit ADD, two negations, with fixed movement charged separately.',
              'limits':['Independent native local binding and main endpoint closure only.',
                        'Helper owner windows, complete paid tariffs and outer precision are separate obligations.',
                        'No new kappa is claimed.']}
    destination = HERE/'P3-NATIVE-AUDIT.json.gz'
    destination.write_bytes(gzip.compress(json.dumps(output, sort_keys=True, separators=(',',':')).encode(), mtime=0))
    print(json.dumps({'status':output['status'],'contacts':output['contact_count'],
                      'targets':output['canonical_main_targets'],'endpoint_phase_controls':omitted_translation_rejected,
                      'sha256':digest(destination)}))


if __name__ == '__main__':
    main()
