#!/usr/bin/env python3
"""Independent finite matrix checks for product Frobenius characters.

Apache-2.0. Prepared by apoursh with substantial OpenAI Codex assistance.
All oracle arithmetic below is independent of model.py's implementations.
Full GL exhaustion is limited to the explicitly reported dimensions <= 3.
"""
import argparse
import copy
import hashlib
import importlib.util
import itertools
import json
from pathlib import Path


def require(condition, message):
    if not condition:
        raise ValueError(message)


def authenticate_sources():
    package = Path(__file__).resolve().parent
    root = package.parents[1]
    manifest = json.loads((package / 'SOURCES.json').read_text())
    rows = [row for row in manifest['files'] if row.get('usage') == 'input']
    expected = {'research/frobenius-tensor-characters/README.md',
                'research/frobenius-algebra-recognition/PROOF.md',
                'research/etale-tensor-determinant-image/README.md'}
    require({row['path'] for row in rows} == expected and len(rows) == 3,
            'live proof source set differs from the declared three inputs')
    for row in rows:
        actual = hashlib.sha256((root / row['path']).read_bytes()).hexdigest()
        require(actual == row['sha256'], 'source hash mismatch: ' + row['path'])
    return len(rows)


def load_model():
    path = Path(__file__).with_name('model.py')
    spec = importlib.util.spec_from_file_location('product_model_target', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def eye(n):
    return [[int(i == j) for j in range(n)] for i in range(n)]


def determinant(matrix, p):
    a = [list(row) for row in matrix]
    result = 1
    for j in range(len(a)):
        pivot = next((i for i in range(j, len(a)) if a[i][j] % p), None)
        if pivot is None:
            return 0
        if pivot != j:
            a[j], a[pivot] = a[pivot], a[j]
            result = -result
        value = a[j][j] % p
        result = result * value % p
        reciprocal = pow(value, p-2, p)
        for i in range(j+1, len(a)):
            factor = a[i][j] * reciprocal % p
            for k in range(j, len(a)):
                a[i][k] = (a[i][k] - factor*a[j][k]) % p
    return result % p


def inverse(matrix, p):
    n = len(matrix)
    a = [list(row) + unit for row, unit in zip(matrix, eye(n))]
    for j in range(n):
        pivot = next((i for i in range(j, n) if a[i][j] % p), None)
        require(pivot is not None, 'oracle matrix is singular')
        a[j], a[pivot] = a[pivot], a[j]
        reciprocal = pow(a[j][j] % p, p-2, p)
        a[j] = [(x*reciprocal) % p for x in a[j]]
        for i in range(n):
            if i != j:
                factor = a[i][j]
                a[i] = [(x-factor*y) % p for x, y in zip(a[i], a[j])]
    return [row[n:] for row in a]


def apply(matrix, vector, p):
    return [sum(x*y for x, y in zip(row, vector)) % p for row in matrix]


def matmul(left, right, p):
    return [[sum(left[i][k]*right[k][j] for k in range(len(right))) % p
             for j in range(len(right[0]))] for i in range(len(left))]


def columns(matrix):
    return [list(column) for column in zip(*matrix)]


def multiply(table, left, right, p):
    n = len(table)
    out = [0]*n
    for i, a in enumerate(left):
        if a:
            for j, b in enumerate(right):
                if b:
                    for k, c in enumerate(table[i][j]):
                        if c:
                            out[k] = (out[k] + a*b*c) % p
    return out


def oracle_model(p, components):
    factors = [list(itertools.product(*(range(p**e) for e in heights)))
               for heights in components]
    n = sum(map(len, factors))
    table = [[[0]*n for _ in range(n)] for _ in range(n)]
    unit, offset = [0]*n, 0
    for heights, exponents in zip(components, factors):
        unit[offset] = 1
        positions = {powers: i for i, powers in enumerate(exponents)}
        for i, a in enumerate(exponents):
            for j, b in enumerate(exponents):
                powers = tuple(x+y for x, y in zip(a, b))
                if all(x < p**e for x, e in zip(powers, heights)):
                    table[offset+i][offset+j][offset+positions[powers]] = 1
        offset += len(exponents)
    return table, unit


def multiplication_matrix(table, value, p):
    return columns([multiply(table, value, vector, p) for vector in eye(len(table))])


def preserves_product(table, matrix, unit, p):
    if apply(matrix, unit, p) != unit:
        return False
    basis_images = columns(matrix)
    for i, left in enumerate(basis_images):
        for j, right in enumerate(basis_images):
            if multiply(table, left, right, p) != apply(matrix, table[i][j], p):
                return False
    return True


def endpoint(table, U, V, W, source, p):
    uc, vc = columns(U), columns(V)
    return all(multiply(table, uc[i], vc[j], p) == apply(W, source[i][j], p)
               for i in range(len(table)) for j in range(len(table)))


def transformed_table(table, U, V, W, p):
    ui, vi = columns(inverse(U, p)), columns(inverse(V, p))
    return [[apply(W, multiply(table, x, y, p), p) for y in vi] for x in ui]


def rejected(action, label):
    try:
        action()
    except (ValueError, TypeError):
        return 1
    raise ValueError('invalid case accepted: ' + label)


def enumerate_automorphisms(p, components):
    table, unit = oracle_model(p, components)
    n, invertible, automorphisms = len(table), 0, []
    for entries in itertools.product(range(p), repeat=n*n):
        matrix = [list(entries[i*n:(i+1)*n]) for i in range(n)]
        det = determinant(matrix, p)
        if det:
            invertible += 1
            if preserves_product(table, matrix, unit, p):
                automorphisms.append(matrix)
    return table, unit, invertible, automorphisms


def check_constructed_character(api, p, components, expected):
    table, unit = oracle_model(p, components)
    actual = set()
    for value in range(1, p):
        if value in expected:
            result = api.automorphism(p, components, value)
            matrix = result['matrix']
            require(determinant(matrix, p) == value, 'wrong constructed automorphism determinant')
            require(preserves_product(table, matrix, unit, p), 'constructed map is not an automorphism')
            actual.add(value)
        else:
            rejected(lambda value=value: api.automorphism(p, components, value),
                     'unattainable automorphism determinant')
    require(actual == expected, 'character image differs from independent matrix oracle')
    return sorted(actual)


def tiny_exhaustions(api):
    domains = [(2, [[], []], 2), (3, [[], []], 2),
               (2, [[1], []], 1), (2, [[], [], []], 6),
               (3, [[1]], 6), (3, [[], [], []], 6)]
    reports = []
    for p, components, expected_count in domains:
        table, unit, gl_count, autos = enumerate_automorphisms(p, components)
        n = len(table)
        require(len(autos) == expected_count, 'tiny automorphism count changed')
        model = api.make_model(p, components)
        require(model['table'] == table and model['unit'] == unit, 'model differs from independent table')
        image = {determinant(phi, p) for phi in autos}
        check_constructed_character(api, p, components, image)
        units = []
        for value in itertools.product(range(p), repeat=n):
            matrix = multiplication_matrix(table, value, p)
            if determinant(matrix, p):
                units.append((list(value), matrix))
        triples, normalized_count = set(), 0
        for phi in autos:
            for u, mu in units:
                for v, mv in units:
                    U, V = matmul(mu, phi, p), matmul(mv, phi, p)
                    W = matmul(multiplication_matrix(table, multiply(table, u, v, p), p), phi, p)
                    require(endpoint(table, U, V, W, table, p), 'normalized autotopism endpoint failed')
                    triples.add(tuple(determinant(matrix, p) for matrix in (U, V, W)))
                    normalized_count += 1
        for wanted in itertools.product(range(1, p), repeat=3):
            if wanted in triples:
                got = api.autotopism(p, components, *wanted)
                matrices = [got[key] for key in ('U', 'V', 'W')]
                require(tuple(determinant(matrix, p) for matrix in matrices) == wanted,
                        'wrong constructed autotopism determinants')
                require(endpoint(table, *matrices, table, p), 'constructed autotopism endpoint failed')
            else:
                rejected(lambda wanted=wanted: api.autotopism(p, components, *wanted),
                         'unattainable autotopism determinant triple')
        reports.append({'p': p, 'components': components, 'n': n,
                        'all_matrices': p**(n*n), 'invertible_matrices': gl_count,
                        'automorphisms': len(autos), 'automorphism_determinants': sorted(image),
                        'units': len(units), 'normalized_autotopisms': normalized_count,
                        'determinant_triples': [list(triple) for triple in sorted(triples)]})
    return reports


def polynomial_product(left, right, p):
    n, result = len(left), [0]*len(left)
    for i, x in enumerate(left):
        if x:
            for j in range(n-i):
                if right[j]:
                    result[i+j] = (result[i+j] + x*right[j]) % p
    return result


def cyclic_substitutions(p, height):
    n, count, image = p**height, 0, set()
    for linear in range(1, p):
        for tail in itertools.product(range(p), repeat=n-2):
            generator = [0, linear, *tail]
            powers, current = [], [1]+[0]*(n-1)
            for _ in range(n):
                powers.append(current)
                current = polynomial_product(current, generator, p)
            require(not any(current), 'cyclic substitution violates truncation')
            matrix = columns(powers)
            value = determinant(matrix, p)
            require(value != 0, 'nonzero-linear cyclic substitution was singular')
            image.add(value)
            count += 1
    return count, image


def representative_triples(api, p, components, phis, unit_values):
    """Enumerate determinant triples from actual matrices representing each image."""
    table, unit = oracle_model(p, components)
    triples = set()
    for phi in phis:
        require(preserves_product(table, phi, unit, p), 'bad oracle automorphism representative')
        for u in unit_values:
            for v in unit_values:
                U = matmul(multiplication_matrix(table, u, p), phi, p)
                V = matmul(multiplication_matrix(table, v, p), phi, p)
                W = matmul(multiplication_matrix(table, multiply(table, u, v, p), p), phi, p)
                require(endpoint(table, U, V, W, table, p), 'moderate representative endpoint failed')
                triples.add(tuple(determinant(matrix, p) for matrix in (U, V, W)))
    accepted, refused = 0, 0
    for wanted in itertools.product(range(1, p), repeat=3):
        if wanted in triples:
            got = api.autotopism(p, components, *wanted)
            matrices = [got[key] for key in ('U', 'V', 'W')]
            require(tuple(determinant(matrix, p) for matrix in matrices) == wanted,
                    'moderate constructed determinant triple failed')
            require(endpoint(table, *matrices, table, p), 'moderate constructed endpoint failed')
            accepted += 1
        else:
            refused += rejected(lambda wanted=wanted: api.autotopism(p, components, *wanted),
                                'moderate determinant triple outside subgroup')
    return {'p': p, 'components': components, 'accepted_triples': accepted,
            'rejected_triples': refused,
            'scope': 'All determinant triples; matrices use unit/automorphism image representatives.'}


def moderate_oracles(api):
    count9, image9 = cyclic_substitutions(3, 2)
    require(count9 == 4374 and image9 == {1}, 'F3[x]/x9 local oracle changed')
    check_constructed_character(api, 3, [[2]], image9)
    table18, unit18 = oracle_model(3, [[2], [2]])
    swap = [[int(j == (i+9) % 18) for j in range(18)] for i in range(18)]
    require(preserves_product(table18, swap, unit18, 3) and determinant(swap, 3) == 2,
            'repeated odd-dimensional block swap failed')
    check_constructed_character(api, 3, [[2], [2]], {1, 2})
    count5, image5 = cyclic_substitutions(5, 1)
    require(count5 == 500 and image5 == {1, 4}, 'F5[x]/x5 local oracle changed')
    check_constructed_character(api, 5, [[], [1]], image5)
    wrong_total_dimension_image = {pow(a, 6*(5-1)//2, 5) for a in range(1, 5)}
    require(wrong_total_dimension_image == {1} and wrong_total_dimension_image != image5,
            'wrong-total-dimension control does not discriminate')
    table2, _ = oracle_model(3, [[], []])
    require(determinant(multiplication_matrix(table2, [1, 2], 3), 3) == 2,
            'componentwise unit determinant lost')
    require({determinant(multiplication_matrix(table2, [a, a], 3), 3)
             for a in (1, 2)} == {1}, 'global-scalar-unit control changed')
    mixed, mixed_unit = oracle_model(2, [[2], [1, 1]])
    bad_swap = [[int(j == (i+4) % 8) for j in range(8)] for i in range(8)]
    require(determinant(bad_swap, 2) == 1 and not preserves_product(mixed, bad_swap, mixed_unit, 2),
            'equal-dimensional nonisomorphic factor swap unexpectedly preserved product')
    rejected(lambda: api.validate_certificate(2, [[2], [1, 1]], mixed,
                                               bad_swap, bad_swap, bad_swap), 'nonisotype internal swap')
    scaling5 = eye(6)
    for exponent in range(5):
        scaling5[1+exponent][1+exponent] = pow(2, exponent, 5)
    triple_reports = [
        representative_triples(api, 3, [[2]], [eye(9)],
                               [[a]+[0]*8 for a in (1, 2)]),
        representative_triples(api, 3, [[2], [2]], [eye(18), swap],
                               [[a]+[0]*8+[1]+[0]*8 for a in (1, 2)]),
        representative_triples(api, 5, [[], [1]], [eye(6), scaling5],
                               [[a, 1]+[0]*4 for a in range(1, 5)]),
    ]
    return {'cyclic_f3_height2_substitutions': count9, 'cyclic_f3_height2_determinants': sorted(image9),
            'two_copies_swap_determinant': 2, 'cyclic_f5_height1_substitutions': count5,
            'cyclic_f5_height1_determinants': sorted(image5),
            'wrong_total_dimension_image': sorted(wrong_total_dimension_image),
            'component_unit_determinant': 2, 'global_scalar_unit_determinants': [1],
            'nonisotype_swap_rejected': True,
            'determinant_triple_checks': triple_reports,
            'scope': 'Local substitutions exhausted; repeated-product full automorphism group not enumerated.'}


def covariant_coefficient_action(table, A, B, C, p):
    """Literal (A tensor B tensor C) action on every coefficient index."""
    n = len(table)
    support = [(r, s, t, table[r][s][t]) for r, s, t in itertools.product(range(n), repeat=3)
               if table[r][s][t]]
    for i, j, k in itertools.product(range(n), repeat=3):
        actual = sum(A[i][r]*B[j][s]*C[k][t]*value for r, s, t, value in support) % p
        if actual != table[i][j][k]:
            return False
    return True


def covariant_controls(api):
    reports = []
    for p in (5, 7):
        table, _ = oracle_model(p, [[1]])
        # Independent diagonal substitution matrices determine these character
        # generators; completeness of the character image uses the written proof.
        scaling_dets = set()
        for a in range(1, p):
            matrix = [[int(i == j)*pow(a, i, p) for j in range(p)] for i in range(p)]
            scaling_dets.add(determinant(matrix, p))
        accepted, refused = 0, 0
        for wanted in itertools.product(range(1, p), repeat=3):
            if wanted[0]*wanted[1]*wanted[2] % p in scaling_dets:
                got = api.covariant_stabilizer(p, [[1]], *wanted)
                matrices = [got[key] for key in ('A', 'B', 'C')]
                require(tuple(determinant(matrix, p) for matrix in matrices) == wanted,
                        'wrong covariant determinants')
                require(covariant_coefficient_action(table, *matrices, p),
                        'literal covariant coefficient-index action failed')
                accepted += 1
            else:
                refused += rejected(lambda wanted=wanted: api.covariant_stabilizer(p, [[1]], *wanted),
                                    'covariant triple outside character subgroup')
        # This explicit nonlinear substitution makes transpose errors visible;
        # the constructive API's selected scaling matrices may be diagonal.
        generator = [0, 1, 1]+[0]*(p-3)
        powers, current = [], [1]+[0]*(p-1)
        for _ in range(p):
            powers.append(current)
            current = polynomial_product(current, generator, p)
        phi = columns(powers)
        inv_phi = inverse(phi, p)
        inverse_transpose = columns(inv_phi)
        require(covariant_coefficient_action(table, inverse_transpose, inverse_transpose, phi, p),
                'nonlinear inverse-transpose coefficient control failed')
        require(not covariant_coefficient_action(table, inv_phi, inv_phi, phi, p),
                'missing-transpose mutation escaped coefficient control')
        reports.append({'p': p, 'n': p, 'accepted_covariant_triples': accepted,
                        'rejected_covariant_triples': refused,
                        'nonlinear_missing_transpose_mutation_rejected': True})
    return reports


def shear(n, p, shift):
    result = eye(n)
    for i in range(n):
        j = (i+1+shift) % n
        if i != j:
            result[i] = [(x+y) % p for x, y in zip(result[i], result[j])]
    return result


def certificate_controls(api):
    p, components = 3, [[2]]
    table, _ = oracle_model(p, components)
    n = len(table)
    U, V, W = shear(n, p, 0), shear(n, p, 2), shear(n, p, 4)
    U[0] = [(2*x) % p for x in U[0]]
    V[0] = [(2*x) % p for x in V[0]]
    target = transformed_table(table, U, V, W, p)
    require(endpoint(target, U, V, W, table, p), 'independent three-factor fixture is invalid')
    got = api.validate_certificate(p, components, target, U, V, W)
    require(got['label'] == 1, 'equal-class independent-basis certificate mislabeled')
    mutations = 0
    for key in ('U', 'V', 'W'):
        changed = {'U': copy.deepcopy(U), 'V': copy.deepcopy(V), 'W': copy.deepcopy(W)}
        changed[key][0][0] = (changed[key][0][0]+1) % p
        mutations += rejected(lambda changed=changed: api.validate_certificate(
            p, components, target, changed['U'], changed['V'], changed['W']), 'changed factor map '+key)
    broken = copy.deepcopy(target)
    broken[0][0][0] = (broken[0][0][0]+1) % p
    mutations += rejected(lambda: api.validate_certificate(p, components, broken, U, V, W), 'changed tensor')
    mutations += rejected(lambda: api.validate_certificate(p, components, target, U[:-1], V, W), 'wrong map shape')
    mutations += rejected(lambda: api.validate_certificate(p, components, target, [[0]*n for _ in range(n)], V, W),
                          'singular map')
    for invalid in (-1, p):
        changed_map = copy.deepcopy(U)
        changed_map[0][0] = invalid
        mutations += rejected(lambda changed_map=changed_map: api.validate_certificate(
            p, components, target, changed_map, V, W), 'noncanonical map entry')
        changed_table = copy.deepcopy(target)
        changed_table[0][0][0] = invalid
        mutations += rejected(lambda changed_table=changed_table: api.validate_certificate(
            p, components, changed_table, U, V, W), 'noncanonical tensor entry')
    # The same ambient tensor has a certificate in either supplied factor order.
    canonical, _ = oracle_model(3, [[], [2]])
    R = api.model_isomorphism(3, [[2], []], [[], [2]])
    require(determinant(R, 3) == 2, 'factor-order permutation lost odd block sign')
    order_a = api.validate_certificate(3, [[], [2]], canonical, eye(10), eye(10), eye(10))
    order_b = api.validate_certificate(3, [[2], []], canonical, R, R, R)
    require(order_a['label'] == order_b['label'] == 1, 'label depends on supplied component order')
    require(order_a['d'] == order_b['d'] == 1 and order_a['raw_d'] != order_b['raw_d'],
            'factor-order determinant normalization not exercised')
    mutations += rejected(lambda: api.model_isomorphism(2, [[2]], [[1, 1]]), 'same-size different type')
    left = {'U': eye(n), 'V': eye(n), 'W': eye(n)}
    right = {'U': U, 'V': V, 'W': W}
    transfer = api.sl_transporter(p, components, table, left, components, target, right)
    matrices = [transfer[key] for key in ('A', 'B', 'C')]
    require(all(determinant(matrix, p) == 1 for matrix in matrices), 'SL transporter determinant failed')
    require(endpoint(target, *matrices, table, p), 'SL transporter endpoint failed')
    bad_U = eye(n)
    bad_U[0][0] = 2
    different = transformed_table(table, bad_U, eye(n), eye(n), p)
    other = {'U': bad_U, 'V': eye(n), 'W': eye(n)}
    different_label = api.validate_certificate(p, components, different, **other)
    require(different_label['label'] == 2, 'different SL class mislabeled')
    mutations += rejected(lambda: api.sl_transporter(p, components, table, left,
                                                     components, different, other), 'unequal SL labels')
    return {'independent_factor_basis_dimension': n, 'permuted_factor_order_dimension': 10,
            'same_label_sl_transporter_checked': True, 'different_label_sl_transporter_rejected': True,
            'malformed_or_changed_certificates_rejected': mutations}


def run():
    source_count = authenticate_sources()
    api = load_model()
    return {'status': 'PASS_FROBENIUS_PRODUCT_CHARACTERS', 'authenticated_source_files': source_count,
            'tiny_full_GL_exhaustions': tiny_exhaustions(api),
            'moderate_substitution_oracles': moderate_oracles(api),
            'covariant_coefficient_controls': covariant_controls(api),
            'certificate_controls': certificate_controls(api),
            'scope': 'Finite exact matrix checks support the separate proof; no exhaustive large-product orbit search or new kappa.'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--json', action='store_true')
    args = parser.parse_args()
    report = run()
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(report['status'])
        print(json.dumps({key: value for key, value in report.items() if key != 'status'}, sort_keys=True))
