#!/usr/bin/env python3
"""Bounded PR6228-to-PR4205 compensated-child comparison; Apache-2.0.

AAAmirinu with substantial OpenAI Codex assistance. Near-unit producer: Nick
Petalas. Retained exact producer/compiler: Jose Manuel / jmbarrancoml, with
Vlado's macro and Chafik's phase oracle. Frozen loading and sources are unchanged.
"""
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import sys
import types

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BASE = 'research/rational-unitary-fft/'
MODULES = ('exact', 'engine', 'triangular', 'generator')
EXTRA = ('research/capped-phase-fusion/evidence/inplace_algebra_ultra/check_circuits.py',
         'research/cubic-cyclic-inverse/vendor/interval_kernel.py',
         BASE + 'vendor/stein_rational.py', BASE + 'vendor/STEIN-PROVENANCE.json')


def require(ok, message):
    if not ok:
        raise ValueError(message)


def authenticate_bytes(raw, row):
    require(hashlib.sha256(raw).hexdigest() == row['sha256'], 'source SHA256 mismatch')
    blob = b'blob ' + str(len(raw)).encode('ascii') + b'\0' + raw
    require(hashlib.sha1(blob).hexdigest() == row['git_blob'], 'source Git blob mismatch')


def authenticate():
    rows = [r for r in json.loads((HERE / 'SOURCES.json').read_bytes())['files']
            if r['usage'] == 'input']
    expected = {BASE + name + '.py' for name in MODULES} | set(EXTRA)
    require(len(rows) == 8 and {r['path'] for r in rows} == expected, 'live source inventory')
    raw = {}
    for row in rows:
        path = ROOT / row['path']
        require(not path.is_symlink(), 'live source symlink')
        raw[row['path']] = path.read_bytes()
        authenticate_bytes(raw[row['path']], row)
    vendors = json.loads((HERE / 'PREDECESSORS.json').read_bytes())['files']
    require(len(vendors) == 1 and vendors[0]['path'] == 'vendor/pr6228/verify.py'
            and vendors[0]['source_path'] == 'research/near-unit-stein-normalization/verify.py'
            and vendors[0]['head'] == 'd85df7f7524e41799a6db2d6c082f6cadbd5cc84',
            'normalizer predecessor identity')
    row = vendors[0]
    path = HERE / row['path']
    require(not path.is_symlink(), 'vendor source symlink')
    vendor = path.read_bytes()
    authenticate_bytes(vendor, row)
    return raw, vendor, rows, row


def loaded(name, raw):
    module = types.ModuleType(name)
    sys.modules[name] = module
    exec(compile(raw, '<pinned ' + name + '>', 'exec', optimize=0), module.__dict__)
    return module


def plain(value):
    if isinstance(value, F):
        return str(value)
    if isinstance(value, dict):
        return {key: plain(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [plain(item) for item in value]
    return value


def main():
    raw, vendor, source_rows, vendor_row = authenticate()
    for name in MODULES:
        loaded(name, raw[BASE + name + '.py'])
    ex, gen = sys.modules['exact'], sys.modules['generator']
    old_producer = gen.load_producer(raw)  # The frozen producer loader is unchanged.
    normalizer = loaded('pinned_near_unit_normalizer', vendor)
    records = lambda vector: [x.record() for x in vector]
    matrix_records = lambda matrix: [records(row) for row in matrix]
    matrix = ex.Mat([[int(0 <= i - j < 3) for j in range(4)] for i in range(4)])
    old_items, displacement, bound_e, old_heights = gen.prepare(matrix, old_producer)
    require(bound_e == 3 and len(old_items) == 1, 'frozen rank-one fixture')
    terms = normalizer.produce(tuple(tuple((x.re, x.im) for x in row)
                                    for row in displacement), 3)
    require(len(terms) == 1, 'near-unit rank-one term')
    g, row, residual, c = terms[0]
    new_g, new_row = ex.Vec(ex.C(*x) for x in g), ex.Vec(ex.C(*x) for x in row)

    def gamma_for(row):
        gamma = F(1)
        while gamma < max(F(1), 2 * ex.component_l1(row)):
            gamma *= 2
        return gamma

    new_items = [dict(g=new_g, row=new_row, gamma=gamma_for(new_row))]
    require(c == F(7, 4) and new_g == ex.Vec([F(4, 7)] * 3 + [0])
            and new_row == ex.Vec([F(7, 4), 0, 0, 0])
            and ex.Vec(ex.C(*x) for x in residual) == ex.Vec([1, 1, 1, 0])
            and ex.norm2(new_g) == F(48, 49), 'exact p3 normalizer witness')
    require(old_items[0]['g'] == ex.Vec([F(1, 2)] * 3 + [0])
            and old_items[0]['row'] == ex.Vec([2, 0, 0, 0]), 'old producer witness')

    def admit(items, target=matrix):
        require(len(items) == 1 and all(len(t['g']) == len(t['row']) == 4 for t in items),
                'rank-one adapter dimensions')
        require(max(max(ex.component_l1(row) for row in displacement),
                    max(ex.component_l1(col) for col in zip(*displacement))) == bound_e,
                'displacement source bound')
        require(all(ex.norm2(t['g']) <= 1 and ex.norm2(t['row']) < 4 * bound_e ** 2
                    and 2 * ex.component_l1(t['row']) <= t['gamma']
                    and t['gamma'] == gamma_for(t['row']) for t in items),
                'generator norm and gamma admission')
        rebuilt = ex.Mat([[sum((t['g'][i] * t['row'][j] for t in items), ex.C())
                           for j in range(4)] for i in range(4)])
        require(rebuilt == displacement, 'entrywise generator reconstruction')
        # Coefficient rows already carry the producer's adjoints: no extra conjugation.
        rebuilt_t = ex.Mat([[sum((t['g'][i-k] * t['row'][j-k]
                                 for t in items for k in range(min(i, j) + 1)), ex.C())
                             for j in range(4)] for i in range(4)])
        require(rebuilt_t == target, 'Toeplitz reconstruction')

    admit(old_items)
    admit(new_items)
    incoming = 1  # The predeclared mixed input contains exact half components.
    bound, triangle_bound = gen.allocation(4, 1, bound_e, F(2), 12, incoming)
    bit_keys = ('child_target_bits', 'phase_bits', 'multiplier_bits', 'leaf_bits', 'data_bits')
    require(tuple(bound[k] for k in bit_keys) == (25, 77, 71, 69, 49), 'frozen allocation bits')
    require(bound['incoming_bits'] == incoming, 'common incoming width')
    # The complete corpus is fixed before constructing either child; no adaptive samples.
    inputs = [('real-' + str(k), ex.Vec(int(j == k) for j in range(8))) for k in range(8)]
    inputs += [('imag-' + str(k), ex.Vec(ex.C(0, int(j == k)) for j in range(8))) for k in range(8)]
    signs = ((1, 1), (-1, 1), (1, -1), (-1, -1), (-1, -1), (1, -1), (-1, 1), (1, 1))
    inputs.append(('dirty-mixed-radius-two', ex.Vec(ex.C(F(a, 2), F(b, 2)) for a, b in signs)))
    require(len(inputs) == 17 and ex.norm2(inputs[-1][1]) == 4, 'fixed observation corpus')

    def admit_input(vector, incoming_bits):
        require(all((part * (1 << incoming_bits)).denominator == 1
                    for value in vector for part in (value.re, value.im)),
                'input incoming-grid admission')
        require(ex.norm2(vector) <= bound['radius'] ** 2, 'input radius admission')

    for _, vector in inputs[:8]:
        admit_input(vector, 0)  # The original eight-real-basis scout was admissible.
    cases = []
    for label, items, p_scalar, g_scalar, envelope in (
        ('old_PR4198', old_items, F(3, 2), F(2), F(6)),
        ('new_PR6228_p3', new_items, F(23, 16), F(16, 7), F(48, 7)),
    ):
        program = gen.Program(bound, triangle_bound, raw)
        plan = program.plan(items)
        require(len(plan) == 98 and sum(map(len, plan)) == 264, 'frozen actual layer/gate count')
        stages = program.stages
        p = gen.lower(stages[0]['symbol'])
        scaled_g = stages[1]['matrix']
        require(p == p_scalar * ex.eye(4) and scaled_g == g_scalar * matrix
                and stages[3]['matrix'] == -1 * scaled_g
                and stages[1]['envelope'] == stages[3]['envelope'] == envelope,
                'actual compensated scaling and envelopes')
        observations = []
        for input_label, vector in inputs:
            admit_input(vector, incoming)
            unrounded, _ = ex.apply(plan, vector)
            rounded, stats = ex.apply(plan, vector, bound['data_bits'])
            wanted = ex.Vec(vector[:4] + [vector[4+i] + sum(
                (matrix[i][j] * vector[j] for j in range(4)), ex.C()) for i in range(4)])
            errors = dict(coefficient_squared=ex.norm2(unrounded - wanted),
                          arithmetic_squared=ex.norm2(rounded - unrounded),
                          total_squared=ex.norm2(rounded - wanted),
                          source_squared=ex.norm2(ex.Vec(rounded[:4]) - ex.Vec(vector[:4])))
            require(unrounded[:4] == vector[:4], 'unrounded source restoration')
            require(errors['coefficient_squared'] <= (bound['coefficient_error'] * bound['radius']) ** 2
                    and errors['arithmetic_squared'] <= bound['rounding_error'] ** 2
                    and errors['total_squared'] <= bound['total_error'] ** 2
                    and errors['source_squared'] <= bound['rounding_error'] ** 2,
                    'finite coefficient/rounding/total/source bounds')
            require(stats['max_observed_height'] <= bound['temporary_bits']
                    and stats['max_grid_numerator_bits'] <= bound['data_bits'] + bound['integer_bits']
                    and stats['max_reduced_fractional_bits'] <= bound['data_bits'],
                    'finite temporary/grid height bounds')
            observations.append(dict(input=input_label, output=records(rounded), **errors,
                                     unrounded_source_exact=True, statistics=stats))
        leaf = program.triangles[0].leaves[0]
        require(leaf['stored'] == p_scalar and leaf['reciprocal'] == 1 / p_scalar,
                'same stored triangular leaf and reciprocal')
        cases.append(dict(label=label, g=records(items[0]['g']), row=records(items[0]['row']),
                          gamma=items[0]['gamma'], g_norm_squared=ex.norm2(items[0]['g']),
                          row_norm_squared=ex.norm2(items[0]['row']), layers=len(plan), gates=264,
                          P=matrix_records(p), scaled_G=matrix_records(scaled_g), envelope=envelope,
                          stored_leaf=leaf['stored'].record(), reciprocal=leaf['reciprocal'].record(),
                          observations=observations, maximum_statistics={key: max(
                              o['statistics'][key] for o in observations) for key in observations[0]['statistics']}))

    controls = []
    def reject(label, action, expected):
        try:
            action()
        except ValueError as error:
            require(str(error) == expected, 'unexpected control rejection: ' + label)
            controls.append(dict(control=label, rejected=str(error)))
        else:
            raise ValueError('control accepted: ' + label)
    bad_row = new_row.copy()
    bad_row[0] += ex.C(F(1, 4))
    reject('unpadded_size_three', lambda: gen.allocation(3, 1, F(3), F(2), 12, 0), 'dyadic macro size')
    reject('underpriced_gamma_two', lambda: gen.Program(bound, triangle_bound, raw).plan(
        [dict(new_items[0], gamma=F(2))]), 'component-l1 near-identity admission')
    reject('changed_coefficient_row', lambda: admit([dict(new_items[0], row=bad_row)]),
           'entrywise generator reconstruction')
    reject('changed_generator_factor', lambda: admit([dict(new_items[0], g=new_g * F(7, 8))]),
           'entrywise generator reconstruction')
    reject('changed_vendor_bytes', lambda: authenticate_bytes(vendor + b'\n', vendor_row),
           'source SHA256 mismatch')
    reject('mixed_input_on_zero_bit_grid', lambda: admit_input(inputs[-1][1], 0),
           'input incoming-grid admission')
    authenticate()
    receipt = dict(status='PASS_NEAR_UNIT_ROUNDED_CHILD', input_sources=source_rows,
                   normalizer_source=vendor_row, scientific_source_optimize=0,
                   matrix=matrix_records(matrix), displacement=matrix_records(displacement),
                   normalizer=dict(precision=3, c=c, residual=records(ex.Vec(ex.C(*x) for x in residual))),
                   parameter_admission=dict(m=4, rank=1, B_E=bound_e, radius=2, target_bits=12,
                                            incoming_bits=incoming, both_generator_reconstructions=True),
                   allocation_correction=dict(original_scout_incoming_bits=0,
                                              registered_incoming_bits=incoming,
                                              reason='Predeclared mixed input has half-valued real and imaginary components.',
                                              original_eight_real_basis_inputs_admitted_at_zero=True,
                                              corpus_radius_target_unchanged=True,
                                              allocated_precision_bits_unchanged=True),
                   allocation=bound, old_producer_heights=old_heights,
                   fixed_inputs=[dict(label=label, vector=records(vector)) for label, vector in inputs],
                   observations_per_child=17, observation_count=34, cases=cases, controls=controls,
                   limitations=['Finite observations are not a universal rounded-error proof.',
                                'Unrounded sources restore exactly; rounded sources have only the checked error bound.',
                                'The unchanged allocation does not consume the smaller coefficient-row norm.',
                                'No full Gaussian/caller, physical delivery, tape, complete cost or savings claim.'])
    print(json.dumps(plain(receipt), sort_keys=True, separators=(',', ':')))
    print('PASS_NEAR_UNIT_ROUNDED_CHILD')


if __name__ == '__main__':
    main()
