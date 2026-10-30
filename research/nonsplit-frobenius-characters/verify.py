#!/usr/bin/env python3
"""Bounded independent ground-field checks of nonsplit determinant characters.

Apache-2.0. Prepared by apoursh with substantial OpenAI Codex assistance.
Only the retained Field primitive is shared; extension arithmetic, elimination,
model products and tensor coefficient checks below are independent oracles.
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
    here = Path(__file__).resolve()
    root, package = here.parents[2], here.parent
    manifest = json.loads((package / 'SOURCES.json').read_text())
    rows = [row for row in manifest['files'] if row.get('usage') == 'input']
    expected = {'research/etale-tensor-determinant-image/README.md',
                'research/frobenius-tensor-characters/README.md',
                'research/nonsplit-frobenius-characters/vendor/local.py',
                'research/nonsplit-frobenius-characters/vendor/split-proof.md',
                'research/nonsplit-frobenius-characters/vendor/ORIGINS.json'}
    require(len(rows) == 5 and {row['path'] for row in rows} == expected,
            'declared live source set differs from five pinned inputs')
    for row in rows:
        actual = hashlib.sha256((root / row['path']).read_bytes()).hexdigest()
        require(actual == row['sha256'], 'source hash mismatch: '+row['path'])
    return len(rows)


def load_api():
    path = Path(__file__).with_name('model.py')
    spec = importlib.util.spec_from_file_location('nonsplit_model_target', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def identity(n):
    return [[int(i == j) for j in range(n)] for i in range(n)]


def transpose(matrix):
    return [list(column) for column in zip(*matrix)]


def determinant(matrix, f):
    rows = [list(row) for row in matrix]
    out = 1
    for j in range(len(rows)):
        pivot = next((i for i in range(j, len(rows)) if rows[i][j]), None)
        if pivot is None:
            return 0
        if pivot != j:
            rows[j], rows[pivot] = rows[pivot], rows[j]
            out = f.neg[out]
        value = rows[j][j]
        out = f.mul[out][value]
        for i in range(j+1, len(rows)):
            scale = f.neg[f.mul[rows[i][j]][f.inv[value]]]
            for k in range(j, len(rows)):
                rows[i][k] = f.add[rows[i][k]][f.mul[scale][rows[j][k]]]
    return out


def inverse(matrix, f):
    n = len(matrix)
    rows = [list(row)+unit for row, unit in zip(matrix, identity(n))]
    for j in range(n):
        pivot = next((i for i in range(j, n) if rows[i][j]), None)
        require(pivot is not None, 'oracle matrix singular')
        rows[j], rows[pivot] = rows[pivot], rows[j]
        scale = f.inv[rows[j][j]]
        rows[j] = [f.mul[scale][x] for x in rows[j]]
        for i in range(n):
            if i != j:
                scale = f.neg[rows[i][j]]
                rows[i] = [f.add[x][f.mul[scale][y]] for x, y in zip(rows[i], rows[j])]
    return [row[n:] for row in rows]


def mv(matrix, vector, f):
    return [f.total(f.mul[x][y] for x, y in zip(row, vector)) for row in matrix]


def mm(left, right, f):
    return transpose([mv(left, column, f) for column in transpose(right)])


def multiply(table, left, right, f):
    out = [0]*len(table)
    for i, x in enumerate(left):
        if x:
            for j, y in enumerate(right):
                if y:
                    scale = f.mul[x][y]
                    for k, z in enumerate(table[i][j]):
                        if z:
                            out[k] = f.add[out[k]][f.mul[scale][z]]
    return out


class OracleExtension:
    """Polynomial remainder arithmetic without the implementation's tables."""
    def __init__(self, base, modulus):
        self.base, self.modulus = base, list(modulus)
        self.degree, self.q = len(modulus)-1, base.q**(len(modulus)-1)

    def digits(self, value):
        return [(value//self.base.q**r) % self.base.q for r in range(self.degree)]

    def encode(self, values):
        return sum(value*self.base.q**r for r, value in enumerate(values))

    def add(self, a, b):
        return self.encode([self.base.add[x][y] for x, y in zip(self.digits(a), self.digits(b))])

    def multiply(self, a, b):
        f, d = self.base, self.degree
        product = [0]*(2*d-1)
        for i, x in enumerate(self.digits(a)):
            for j, y in enumerate(self.digits(b)):
                product[i+j] = f.add[product[i+j]][f.mul[x][y]]
        for k in range(2*d-2, d-1, -1):
            coefficient = product[k]
            for j in range(d):
                correction = f.neg[f.mul[coefficient][self.modulus[j]]]
                product[k-d+j] = f.add[product[k-d+j]][correction]
        return self.encode(product[:d])

    def power(self, a, exponent):
        out = 1
        for _ in range(exponent):
            out = self.multiply(out, a)
        return out


def oracle_model(base, components, moduli):
    factors = []
    for d, heights in components:
        extension = OracleExtension(base, moduli[d])
        exponents = list(itertools.product(*(range(base.p**h) for h in heights)))
        factors.append((extension, exponents, heights))
    n = sum(extension.degree*len(exponents) for extension, exponents, _ in factors)
    table, unit, offset = [[[0]*n for _ in range(n)] for _ in range(n)], [0]*n, 0
    for extension, exponents, heights in factors:
        d = extension.degree
        unit[offset] = 1
        positions = {powers: i for i, powers in enumerate(exponents)}
        for i, a in enumerate(exponents):
            for j, b in enumerate(exponents):
                powers = tuple(x+y for x, y in zip(a, b))
                if all(x < base.p**h for x, h in zip(powers, heights)):
                    output = offset + d*positions[powers]
                    for r in range(d):
                        for s in range(d):
                            value = extension.multiply(base.q**r, base.q**s)
                            for t, coefficient in enumerate(extension.digits(value)):
                                table[offset+i*d+r][offset+j*d+s][output+t] = coefficient
        offset += d*len(exponents)
    return table, unit


def multiplier(table, value, f):
    return transpose([multiply(table, value, unit, f) for unit in identity(len(table))])


def endpoint(target, U, V, W, source, f):
    uc, vc = transpose(U), transpose(V)
    return all(multiply(target, uc[i], vc[j], f) == mv(W, source[i][j], f)
               for i in range(len(source)) for j in range(len(source)))


def is_automorphism(table, unit, matrix, f):
    return mv(matrix, unit, f) == unit and endpoint(table, matrix, matrix, matrix, table, f)


def transform(table, U, V, W, f):
    uc, vc = transpose(inverse(U, f)), transpose(inverse(V, f))
    return [[mv(W, multiply(table, x, y, f), f) for y in vc] for x in uc]


def refused(action, message):
    try:
        action()
    except (ValueError, TypeError):
        return 1
    raise ValueError('invalid input accepted: '+message)


def instantiate(api, base, components, moduli):
    residues = {d: api.Extension(base, modulus) for d, modulus in moduli.items()}
    model = api.make_model(base, components, residues)
    table, unit = oracle_model(base, components, moduli)
    require(model['table'] == table and model['unit'] == unit, 'ground-field multiplication table mismatch')
    return model, table, unit


def compare_character(api, model, table, unit, image):
    f = model['base']
    for value in range(1, f.q):
        if value in image:
            got = api.automorphism(model, value)
            matrix = got['matrix']
            require(determinant(matrix, f) == value and is_automorphism(table, unit, matrix, f),
                    'constructed automorphism failed independent matrix check')
        else:
            refused(lambda value=value: api.automorphism(model, value), 'outside automorphism determinant image')


def tiny_exhaustions(api):
    domains = [(2, [(2, [])], {2: [1, 1, 1]}, 2),
               (3, [(2, [])], {2: [1, 0, 1]}, 2),
               (2, [(3, [])], {3: [1, 1, 0, 1]}, 3),
               (3, [(3, [])], {3: [2, 2, 0, 1]}, 3),
               (2, [(1, []), (2, [])], {1: [0, 1], 2: [1, 1, 1]}, 2),
               (3, [(1, []), (2, [])], {1: [0, 1], 2: [1, 0, 1]}, 2)]
    reports = []
    for p, components, moduli, expected in domains:
        f = api.Field(p, [0, 1])
        model, table, unit = instantiate(api, f, components, moduli)
        n, gl_count, autos = len(table), 0, []
        for entries in itertools.product(range(f.q), repeat=n*n):
            matrix = [list(entries[i*n:(i+1)*n]) for i in range(n)]
            if determinant(matrix, f):
                gl_count += 1
                if is_automorphism(table, unit, matrix, f):
                    autos.append(matrix)
        require(len(autos) == expected, 'tiny nonsplit automorphism count changed')
        image = {determinant(matrix, f) for matrix in autos}
        compare_character(api, model, table, unit, image)
        units = [(list(value), multiplier(table, value, f))
                 for value in itertools.product(range(f.q), repeat=n)]
        units = [(value, matrix) for value, matrix in units if determinant(matrix, f)]
        triples, count = set(), 0
        for phi in autos:
            for u, mu in units:
                for v, nu in units:
                    U, V = mm(mu, phi, f), mm(nu, phi, f)
                    W = mm(multiplier(table, multiply(table, u, v, f), f), phi, f)
                    require(endpoint(table, U, V, W, table, f), 'tiny normalized autotopism failed')
                    triples.add(tuple(determinant(matrix, f) for matrix in (U, V, W)))
                    count += 1
        for wanted in itertools.product(range(1, f.q), repeat=3):
            if wanted in triples:
                got = api.autotopism(model, *wanted)
                matrices = [got[key] for key in ('U', 'V', 'W')]
                require(tuple(determinant(matrix, f) for matrix in matrices) == wanted,
                        'tiny constructed autotopism determinant mismatch')
                require(endpoint(table, *matrices, table, f), 'tiny constructed autotopism endpoint mismatch')
            else:
                refused(lambda wanted=wanted: api.autotopism(model, *wanted), 'tiny outside determinant triple')
        reports.append({'p': p, 'components': components, 'dimension': n,
                        'all_matrices': f.q**(n*n), 'invertible_matrices': gl_count,
                        'automorphisms': len(autos), 'determinant_image': sorted(image),
                        'units': len(units), 'normalized_autotopisms': count,
                        'determinant_triples': [list(t) for t in sorted(triples)]})
    return reports


def polynomial_product(a, b, extension):
    out = [0]*len(a)
    for i, x in enumerate(a):
        for j in range(len(a)-i):
            if x and b[j]:
                out[i+j] = extension.add(out[i+j], extension.multiply(x, b[j]))
    return out


def substitution(extension, length, coefficients, frobenius_power=0):
    f, d = extension.base, extension.degree
    powers, current = [], [1]+[0]*(length-1)
    for _ in range(length):
        powers.append(current)
        current = polynomial_product(current, coefficients, extension)
    require(not any(current), 'substitution violates nilpotent relation')
    images = []
    for power in powers:
        for r in range(d):
            coefficient = extension.power(f.q**r, f.q**frobenius_power)
            images.append([c for value in power
                           for c in extension.digits(extension.multiply(coefficient, value))])
    return transpose(images)


def nilpotent_exhaustions(api):
    reports = []
    for p, modulus, expected in [(2, [1, 1, 1], 6), (3, [1, 0, 1], 144)]:
        f = api.Field(p, [0, 1])
        model, table, unit = instantiate(api, f, [(2, [1])], {2: modulus})
        extension = OracleExtension(f, modulus)
        count, image = 0, set()
        for frobenius in range(2):
            for linear in range(1, extension.q):
                for tail in itertools.product(range(extension.q), repeat=p-2):
                    matrix = substitution(extension, p, [0, linear, *tail], frobenius)
                    require(is_automorphism(table, unit, matrix, f), 'nilpotent substitution endpoint failed')
                    value = determinant(matrix, f)
                    require(value != 0, 'nilpotent substitution singular')
                    image.add(value)
                    count += 1
        require(count == expected, 'nilpotent complete substitution count changed')
        compare_character(api, model, table, unit, image)
        reports.append({'p': p, 'residue_degree': 2, 'height': 1, 'dimension': len(table),
                        'complete_automorphism_substitutions': count, 'determinant_image': sorted(image)})
    return reports


def strong_controls(api):
    f = api.Field(3, [1, 0, 1])
    beta = 4  # 1+t, encoded in base 3; t^2=-1.
    require(f.power(beta, 4) == f.neg[1] and f.power(beta, 8) == 1,
            'specified F9 primitive element changed')
    modulus = [f.neg[beta], 0, 1]
    extension = OracleExtension(f, modulus)
    actual_extension = api.Extension(f, modulus)
    multiplication_checks = 0
    for a, b in itertools.product(range(extension.q), repeat=2):
        require(extension.multiply(a, b) == actual_extension.mul[a][b], 'extension multiplication differs')
        multiplication_checks += 1
    for a in range(1, extension.q):
        matrix = transpose([extension.digits(extension.multiply(a, f.q**r)) for r in range(2)])
        require(determinant(matrix, f) == actual_extension.norm(a), 'norm differs from ground-field determinant')
    model, table, unit = instantiate(api, f, [(2, [1])], {2: modulus})
    u = f.q
    scaling = substitution(extension, 3, [0, u, 0])
    expected = f.power(beta, 7)
    require(determinant(scaling, f) == expected and is_automorphism(table, unit, scaling, f),
            'F81 nilpotent scaling determinant is not beta^7')
    require(len({f.power(expected, k) for k in range(8)}) == 8, 'strong determinant does not have order eight')
    image, direct_cases = set(), 0
    for a in range(1, extension.q):
        matrix = substitution(extension, 3, [0, a, 0])
        require(is_automorphism(table, unit, matrix, f), 'F81 linear substitution endpoint failed')
        image.add(determinant(matrix, f)); direct_cases += 1
    for tail in (1, beta, u, extension.add(1, u)):
        for frobenius in range(2):
            matrix = substitution(extension, 3, [0, u, tail], frobenius)
            require(is_automorphism(table, unit, matrix, f), 'F81 nonlinear substitution endpoint failed')
            direct_cases += 1
    require(image == set(range(1, f.q)), 'linear substitution determinants fail to fill F9 multiplicative group')
    compare_character(api, model, table, unit, image)
    wrong_extra_degree = {f.mul[value][value] for value in image}
    require(len(wrong_extra_degree) == 4 and expected not in wrong_extra_degree,
            'extra residue-degree exponent control failed')
    # Ground F3, coefficient field F9, local nilpotent length nine.
    ground = api.Field(3, [0, 1])
    residue = OracleExtension(ground, [1, 0, 1])
    model18, table18, unit18 = instantiate(api, ground, [(2, [2])], {2: [1, 0, 1]})
    local_scaling_dets = set()
    for a in range(1, residue.q):
        matrix = substitution(residue, 9, [0, a]+[0]*7)
        require(is_automorphism(table18, unit18, matrix, ground), 'length-nine coefficient scaling failed')
        local_scaling_dets.add(determinant(matrix, ground))
    frobenius = substitution(residue, 9, [0, 1]+[0]*7, 1)
    require(local_scaling_dets == {1} and determinant(frobenius, ground) == 2,
            'coefficient Frobenius sign correction missing')
    require(is_automorphism(table18, unit18, frobenius, ground), 'coefficient Frobenius endpoint failed')
    compare_character(api, model18, table18, unit18, {1, 2})
    odd_pair, odd_table, odd_unit = instantiate(api, ground, [(3, []), (3, [])],
                                               {3: [2, 2, 0, 1]})
    swap = [[int(j == (i+3) % 6) for j in range(6)] for i in range(6)]
    require(determinant(swap, ground) == 2 and is_automorphism(odd_table, odd_unit, swap, ground),
            'repeated odd residue-degree block swap failed')
    require(api.component_swap(odd_pair, 0, 1) == swap, 'constructed component swap differs')
    compare_character(api, odd_pair, odd_table, odd_unit, {1, 2})
    return {'base_field_size': 9, 'residue_field_size': 81, 'beta': beta,
            'scaling_x_to_u_x_determinant': expected, 'determinant_order': 8,
            'independent_extension_products': multiplication_checks, 'independent_norm_checks': 80,
            'checked_F81_substitutions': direct_cases, 'F81_linear_scaling_image': sorted(image),
            'wrong_extra_degree_image': sorted(wrong_extra_degree),
            'F9_x9_over_F3_scaling_determinants': sorted(local_scaling_dets),
            'F9_x9_over_F3_coefficient_frobenius_determinant': 2,
            'F27_pair_over_F3_component_swap_determinant': 2,
            'scope': '80 linear and 8 nonlinear F81 substitutions checked, not all12960 automorphisms.'}


def coefficient_action(table, A, B, C, f):
    n = len(table)
    support = [(r, s, t, table[r][s][t]) for r, s, t in itertools.product(range(n), repeat=3)
               if table[r][s][t]]
    for i, j, k in itertools.product(range(n), repeat=3):
        value = 0
        for r, s, t, coefficient in support:
            scale = f.mul[f.mul[A[i][r]][B[j][s]]][f.mul[C[k][t]][coefficient]]
            value = f.add[value][scale]
        if value != table[i][j][k]:
            return False
    return True


def covariant_controls(api):
    f = api.Field(3, [1, 0, 1])
    model, table, _ = instantiate(api, f, [(1, [2])], {1: [0, 1]})
    residue = OracleExtension(f, [0, 1])
    image = {determinant(substitution(residue, 9, [0, a]+[0]*7), f) for a in range(1, f.q)}
    require(image == {1, f.neg[1]}, 'proper-subgroup scaling fixture changed')
    accepted, rejected = 0, 0
    # Exhaust determinant triples, not all maps in their stabilizer fibres.
    for wanted in itertools.product(range(1, f.q), repeat=3):
        if f.mul[f.mul[wanted[0]][wanted[1]]][wanted[2]] in image:
            got = api.covariant_stabilizer(model, *wanted)
            matrices = [got[key] for key in ('A', 'B', 'C')]
            require(tuple(determinant(matrix, f) for matrix in matrices) == wanted,
                    'covariant determinant mismatch')
            require(coefficient_action(table, *matrices, f), 'literal covariant coefficient action failed')
            accepted += 1
        else:
            rejected += refused(lambda wanted=wanted: api.covariant_stabilizer(model, *wanted),
                                'outside proper covariant subgroup')
    phi = substitution(residue, 9, [0, 1, 1]+[0]*6)
    inv_phi = inverse(phi, f)
    require(coefficient_action(table, transpose(inv_phi), transpose(inv_phi), phi, f),
            'nonlinear inverse-transpose check failed')
    require(not coefficient_action(table, inv_phi, inv_phi, phi, f),
            'missing transpose mutation escaped')
    return {'base_field_size': 9, 'dimension': 9, 'accepted_covariant_triples': accepted,
            'rejected_covariant_triples': rejected, 'nonlinear_missing_transpose_rejected': True}


def shear(n, f, shift):
    matrix = identity(n)
    for i in range(n):
        j = (i+1+shift) % n
        if i != j:
            matrix[i] = [f.add[x][y] for x, y in zip(matrix[i], matrix[j])]
    return matrix


def certificate_controls(api):
    f = api.Field(3, [1, 0, 1])
    model, table, _ = instantiate(api, f, [(1, [2])], {1: [0, 1]})
    n = len(table)
    U, V, W = shear(n, f, 0), shear(n, f, 2), shear(n, f, 4)
    U[0] = [f.mul[4][x] for x in U[0]]
    V[0] = [f.mul[f.inv[4]][x] for x in V[0]]
    target = transform(table, U, V, W, f)
    got = api.validate_certificate(model, target, U, V, W)
    require(got['label'] == 1 and endpoint(target, U, V, W, table, f),
            'independent factor-basis certificate failed')
    count = 0
    for key in ('U', 'V', 'W'):
        maps = {'U': copy.deepcopy(U), 'V': copy.deepcopy(V), 'W': copy.deepcopy(W)}
        maps[key][0][0] = f.add[maps[key][0][0]][1]
        count += refused(lambda maps=maps: api.validate_certificate(model, target, **maps), 'changed factor map')
    changed = copy.deepcopy(target); changed[0][0][0] = f.add[changed[0][0][0]][1]
    count += refused(lambda: api.validate_certificate(model, changed, U, V, W), 'changed tensor')
    count += refused(lambda: api.validate_certificate(model, target, U[:-1], V, W), 'wrong matrix shape')
    count += refused(lambda: api.validate_certificate(model, target, [[0]*n for _ in range(n)], V, W), 'singular matrix')
    for invalid in (-1, f.q, True, 0.5):
        changed = copy.deepcopy(U); changed[0][0] = invalid
        count += refused(lambda changed=changed: api.validate_certificate(model, target, changed, V, W),
                         'noncanonical matrix entry')
        changed = copy.deepcopy(target); changed[0][0][0] = invalid
        count += refused(lambda changed=changed: api.validate_certificate(model, changed, U, V, W),
                         'noncanonical tensor entry')
    other_U = identity(n); other_U[0][0] = 4
    other_table = transform(table, other_U, identity(n), identity(n), f)
    other = api.validate_certificate(model, other_table, other_U, identity(n), identity(n))
    require(other['label'] != got['label'], 'distinct determinant cosets have equal labels')
    return {'dimension': n, 'changed_or_malformed_certificates_rejected': count,
            'independent_three_factor_bases_checked': True, 'different_coset_labels_distinguished': True}


def presentation_controls(api):
    f2, f3 = api.Field(2, [0, 1]), api.Field(3, [0, 1])
    f9, alt9 = api.Field(3, [1, 0, 1]), api.Field(3, [2, 1, 1])
    count = 0
    count += refused(lambda: api.Extension(f3, [0, 0, 1]), 'reducible residue polynomial')
    alt_primitive = next(a for a in range(1, alt9.q)
                         if len({alt9.power(a, k) for k in range(8)}) == 8)
    valid_over_alternate_base = api.Extension(alt9, [alt9.neg[alt_primitive], 0, 1])
    count += refused(lambda: api.make_model(f9, [(2, [])], {2: valid_over_alternate_base}),
                     'different ground field presentation')
    count += refused(lambda: api.make_model(f3, [(3, [])], {3: api.Extension(f3, [1, 0, 1])}),
                     'declared residue degree mismatch')
    count += refused(lambda: api.make_model(f3, [(2, []), (1, [])],
                                            {1: api.Extension(f3, [0, 1]), 2: api.Extension(f3, [1, 0, 1])}),
                     'noncanonical component order')
    first = api.make_model(f3, [(2, [])], {2: api.Extension(f3, [1, 0, 1])})
    second = api.make_model(f3, [(2, [])], {2: api.Extension(f3, [2, 1, 1])})
    count += refused(lambda: api.model_isomorphism(first, second), 'alternate residue presentation')
    cyclic = api.make_model(f2, [(1, [2])])
    nonsplit = api.make_model(f2, [(2, [1])], {2: api.Extension(f2, [1, 1, 1])})
    require(cyclic['n'] == nonsplit['n'] == 4, 'same-dimension type control changed')
    count += refused(lambda: api.model_isomorphism(cyclic, nonsplit), 'same dimension different residue type')
    count += refused(lambda: api.validate_certificate(cyclic, nonsplit['table'],
                                                       identity(4), identity(4), identity(4)),
                     'same-dimensional different-type multiplication table')
    square = api.make_model(f2, [(1, [1, 1])])
    count += refused(lambda: api.model_isomorphism(cyclic, square), 'same dimension different height type')
    require(api.model_isomorphism(first, first) == identity(2), 'identity model isomorphism failed')
    return {'presentation_or_type_rejections': count, 'same_dimension_different_types_checked': True}


def run():
    sources = authenticate_sources()
    api = load_api()
    return {'status': 'PASS_NONSPLIT_FROBENIUS_CHARACTERS',
            'authenticated_source_files': sources,
            'tiny_full_GL_exhaustions': tiny_exhaustions(api),
            'nilpotent_substitution_exhaustions': nilpotent_exhaustions(api),
            'strong_norm_and_frobenius_controls': strong_controls(api),
            'covariant_controls': covariant_controls(api),
            'certificate_controls': certificate_controls(api),
            'presentation_controls': presentation_controls(api),
            'scope': 'Finite exact matrices support the separate theorem; large automorphism groups and tensor recognition are not exhausted.'}


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
