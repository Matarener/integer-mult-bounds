"""Check the declared finite domains and compare the saved receipt.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
"""
from itertools import product
from pathlib import Path
from math import gcd
import importlib.util
import json
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import pencils as P
spec = importlib.util.spec_from_file_location('literal_equations', ROOT/'source/oracle.py')
O = importlib.util.module_from_spec(spec); spec.loader.exec_module(O)


def full_line(q, length=1):
    return [['F', [a, 1], length, 1] for a in range(q)]+[['I', length, 1]]


DOMAINS = [
    ('binary_full_line', 2, full_line(2), True),
    ('ternary_full_line', 3, full_line(3), True),
    ('quartic_full_line', 4, full_line(4), False),
    ('binary_thick_line', 2, full_line(2, 2), True),
    ('ternary_thick_line', 3, full_line(3, 2), False),
    ('ternary_jordan', 3, [['F', [0, 1], 2, 1]], True),
    ('ternary_nonsplit', 3, [['F', [1, 0, 1], 1, 1]], True),
    ('ternary_nonsplit_thick', 3, [['F', [1, 0, 1], 2, 1]], True),
    ('binary_nonsplit_thick', 2, [['F', [1, 1, 1], 2, 1]], True),
    ('binary_cubic', 2, [['F', [1, 1, 0, 1], 1, 1]], True),
    ('finite_infinity_lengths', 3, [['F', [0, 1], 2, 1], ['I', 1, 1]], True),
    ('mixed_right_jordan', 3, [['R', 1, 1], ['F', [0, 1], 2, 1]], True),
    ('mixed_zero_jordan', 3, [['R', 0, 1], ['F', [0, 1], 2, 1]], True),
    ('mixed_both_nonsplit', 2, [['R', 1, 1], ['L', 1, 1], ['F', [1, 1, 1], 1, 1]], True),
    ('mixed_zero_both', 2, [['R', 0, 1], ['L', 0, 1], ['F', [0, 1], 1, 1]], True),
    ('repeated_regular', 3, [['F', [0, 1], 1, 2]], True),
]
EXTRA = [
    ('quinary_full_line', 5, full_line(5)),
    ('quinary_thick_line', 5, full_line(5, 2)),
    ('quartic_third_order_line', 4, full_line(4, 3)),
    ('regular_colours', 3, [['F', [0, 1], 1, 2], ['F', [1, 1], 1, 1], ['I', 1, 1]]),
    ('two_points_odd', 5, [['F', [0, 1], 1, 1], ['I', 1, 1]]),
    ('two_points_even', 5, [['F', [0, 1], 2, 1], ['I', 2, 1]]),
    ('mixed_coprime_lengths', 5, [['R', 1, 1], ['L', 1, 1], ['F', [0, 1], 2, 1]]),
    ('mixed_equal_index_gcd', 3, [['R', 1, 1], ['R', 3, 1], ['F', [0, 1], 2, 1]]),
    ('mixed_left_nonsplit', 3, [['L', 2, 1], ['F', [1, 0, 1], 2, 1]]),
    ('mixed_regular_lengths', 4, [['R', 0, 1], ['F', [0, 1], 3, 1], ['I', 2, 1]]),
    ('pure_singular_control', 5, [['R', 1, 1], ['L', 2, 1]]),
]


def reference_fixed(model, f):
    vectors = []
    for block in model:
        if block[0] == 'R': vectors.append((block[1], -block[1]-1))
        elif block[0] == 'L': vectors.append((-block[1]-1, block[1]))
        else:
            length = block[-2]; vectors.append((length, -length))
    subgroup = {(1, 1)}
    for a, b in vectors:
        subgroup = {P.pair_mul(pair, (f.power(u, a), f.power(u, b)), f)
                    for pair in subgroup for u in range(1, f.q)}
    return subgroup


def action_subset(f, complete):
    if complete: return list(P.old.general_linear_two(f))
    out = [[[z, 0], [0, 1]] for z in range(1, f.q)]
    for x in ([[0, 1], [1, 0]], [[1, 1], [0, 1]]):
        if x not in out: out.append(x)
    return out


def oracle_check(compiled, complete):
    f = compiled['field']; a, b = compiled['slices']; m, n = compiled['dimensions']
    lifts = {tuple(sum(lift[2], [])): char for char, lift in compiled['lifts']}
    image = set(); tested = accepted = 0; dimensions = []
    for action in action_subset(f, complete):
        space = O.stabilizer_space(a, b, action, f)
        pairs, count = O.enumerate_space(space, m, n, f)
        tested += f.q**len(space); accepted += count; dimensions.append(len(space))
        char = lifts.get(tuple(sum(action, [])))
        expected = set() if char is None else {P.pair_mul(char[:2], key, f) for key in compiled['fixed']}
        P.need(pairs == expected, 'Separate full coefficient-space image for one slice action')
        z = O.determinant(action, f); image.update(pair+(z,) for pair in pairs)
    if complete: P.need(image == set(compiled['image']), 'Complete literal determinant image')
    return dict(all_slice_actions=complete, slice_actions=len(dimensions), equation_dimensions=sorted(set(dimensions)),
                linear_solutions=tested, invertible_stabilizers=accepted, determinant_triples_seen=len(image))


def witnesses(compiled):
    f = compiled['field']; yes = no = prescribed = 0; m, n = compiled['dimensions']
    for triple in product(range(1, f.q), repeat=3):
        if triple in compiled['image']:
            P.witness(compiled, triple); yes += 1
            maps = [P.old.identity(m), P.old.identity(n), P.old.identity(2)]
            for matrix, value in zip(maps, triple):
                matrix[0][0] = value
                if len(matrix) > 1: matrix[0][1] = 1
            P.correct_map(compiled, maps)
        else:
            try: P.witness(compiled, triple)
            except ValueError: no += 1
            else: raise ValueError('Excluded determinant triple accepted')
    for char, lift in compiled['lifts']:
        for pair in compiled['fixed']:
            triple = P.pair_mul(char, pair+(1,), f)
            P.witness(compiled, triple, lift[2]); prescribed += 1
    return dict(accepted_triples=yes, excluded_triples=no, supplied_map_SL_corrections=yes,
                prescribed_slice_witnesses=prescribed, SL_orbits=len(set(P.orbit_labels(compiled).values())))


def singular_pair(side, e):
    m, n = e+(side == 'L'), e+(side == 'R')
    a = [[0]*n for _ in range(m)]; b = [[0]*n for _ in range(m)]
    for i in range(e):
        a[i][i] = 1
        if side == 'R': b[i][i+1] = 1
        else: b[i+1][i] = 1
    return (a, b), (m, n)


def hom_checks():
    report = []
    for q in (2, 3, 4, 5):
        f = P.Field(q); regular = []
        for length in (1, 2):
            for block in (['F', [0, 1], length, 1], ['I', length, 1]):
                parts, m, n = P.normalized([block], f)
                regular.append((P.slices(parts, m, n, f), (m, n), block))
        count = 0; total = 0
        for reg, dims, block in regular:
            for side in ('R', 'L'):
                for e in range(4):
                    sing, sd = singular_pair(side, e)
                    for source, target, ds, dt, expected in (
                        (reg, sing, dims, sd, dims[0] if side == 'R' else 0),
                        (sing, reg, sd, dims, dims[0] if side == 'L' else 0)):
                        rows, columns = O.equations(source, target, ds, dt, f)
                        dimension = len(O.nullspace(rows, columns, f))
                        P.need(dimension == expected, 'Regular/singular Hom dimension')
                        count += 1; total += dimension
        for a, da, ta in regular:
            for b, db, tb in regular:
                rows, columns = O.equations(a, b, da, db, f)
                expected = min(ta[-2], tb[-2]) if ta[0] == tb[0] else 0
                P.need(len(O.nullspace(rows, columns, f)) == expected, 'Finite/infinity regular Hom dimension')
                count += 1
        report.append(dict(field=q, ordered_Hom_cases=count, mixed_Hom_dimension_sum=total))
    return report


def controls(compiled):
    f = P.Field(3); names = []
    jordan = compiled['ternary_jordan']; exact = set(jordan['image'])
    P.need(exact == {(1, 1, 1), (2, 2, 2)}, 'The source Jordan sign example survives')
    names += ['similarity_determinant', 'length_power_subgroup']
    for name, q in [('ternary_full_line', 3), ('quartic_full_line', 4)]:
        c = compiled[name]; field = c['field']; a, b = c['slices']
        P.need(all(P.old.determinant(P.matrix_sum(a, b, x, y, field), field) == 0
                   for x, y in product(range(q), repeat=2) if x or y), 'No invertible rational slice')
    names.append('global_invertible_slice_is_unnecessary')
    P.need(len(compiled['regular_colours']['lifts']) < 48, 'Coloured support restricts the slice group')
    names.append('unrestricted_slice_group')
    P.need(set(compiled['mixed_right_jordan']['fixed']) != set(product((1, 2), repeat=2)), 'Regular length still restricts a singular mixture')
    names.append('mixed_length_gcd')
    P.need(len(compiled['mixed_coprime_lengths']['image']) == 64, 'Coprime mixed vectors remove the row/column restriction')
    names.append('mixed_coprime_characters')
    for name in ('ternary_nonsplit', 'ternary_nonsplit_thick'):
        P.need(set(compiled[name]['fixed']) == reference_fixed(compiled[name]['model'], f), 'Nonsplit norms use the block length')
    names.append('residue_degree_is_not_block_length')
    for name in ('ternary_jordan', 'mixed_right_jordan', 'ternary_full_line'):
        c = compiled[name]; field = c['field']; maps = P.witness(c, next(iter(c['image'])))
        bad = [x[:] for x in maps[0]]; bad[0][0] = field.add(bad[0][0], 1)
        P.need(not P.old.fixes(*c['slices'], (bad, maps[1], maps[2]), field), 'Corrupt literal lift rejects')
    names.append('literal_row_map_corruption')
    for name in ('quinary_full_line', 'quinary_thick_line', 'quartic_third_order_line'):
        c = compiled[name]; field = c['field']; length = c['model'][0][-2]
        powers = {field.power(u, length) for u in range(1, field.q)}
        predicted = {t for t in product(range(1, field.q), repeat=3)
                     if t[0] in powers and field.mul(field.mul(t[0], t[1]), field.power(t[2], length)) == 1}
        P.need(set(c['image']) == predicted and len(set(P.orbit_labels(c).values())) == (field.q-1)*gcd(field.q-1, length),
               'Full projective line with nonsemisimple length character')
    names.append('uniform_projective_line_length_character')
    bad_models = [[], [['X', 1, 1]], [['R', -1, 1]], [['F', [0, 0, 1], 1, 1]], [['F', [0, 1], 0, 1]],
                  [['F', [0, 1], 1, 0]], [['R', 0, 1]], [['I', 1, 1], ['I', 1, 1]], [['F', [0, 3], 1, 1]]]
    for model in bad_models:
        try: P.compile_model(model, f)
        except ValueError: pass
        else: raise ValueError('Malformed model accepted')
    return dict(mathematical_controls=names, malformed_models=len(bad_models))


def run():
    hom = hom_checks(); reports = []; compiled = {}
    for name, q, model in [(n, q, m) for n, q, m, _ in DOMAINS]+EXTRA:
        c = P.compile_model(model, P.Field(q)); compiled[name] = c
        P.need(set(c['fixed']) == reference_fixed(model, c['field']), 'Independent exponent-generated fixed image')
        P.need(all(P.pair_mul(x, y, c['field']) in c['image'] for x in c['image'] for y in c['image']), 'Complete determinant image is closed')
        item = dict(name=name, field=q, model=model, dimensions=c['dimensions'],
                    admissible_slice_actions=len(c['lifts']), total_slice_actions=c['slice_actions'],
                    fixed_image=sorted(c['fixed']), determinant_image=sorted(c['image']), **witnesses(c))
        entry = next((x for x in DOMAINS if x[0] == name), None)
        if entry: item['literal_oracle'] = oracle_check(c, entry[3])
        reports.append(item); print('PASS_PENCIL_DOMAIN', name, flush=True)
    return dict(status='PASS_COMPLETE_SUPPLIED_FINITE_FIELD_PENCIL_CHARACTERS', hom_domains=hom,
                models=reports, controls=controls(compiled),
                scope='All-dimension finite-field proof for supplied complete block models. Bounded literal evidence; no arbitrary extraction or physical caller.')


if __name__ == '__main__':
    result = json.loads(json.dumps(run()))
    if sys.argv[1:] == ['--write']:
        (ROOT/'RESULT.json').write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    else:
        P.need(not sys.argv[1:], 'No unknown verifier arguments')
        P.need(result == json.loads((ROOT/'RESULT.json').read_text()), 'Saved exact receipt differs')
    print(result['status'])
