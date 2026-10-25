#!/usr/bin/env python3
"""Exact recognition, coordinate-change and witness controls. Apache-2.0.

Prepared by apoursh with substantial OpenAI Codex assistance.
The fixture builder does not import the recognizer's arithmetic helpers.
"""
import argparse
import copy
import importlib.util
import itertools
import json
from pathlib import Path


def require(ok, message):
    if not ok:
        raise ValueError(message)


def load_recognizer():
    path = Path(__file__).with_name('recognize.py')
    spec = importlib.util.spec_from_file_location('recognize_local', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def identity(n):
    return [[int(i == j) for j in range(n)] for i in range(n)]


def inverse(matrix, p):
    n = len(matrix)
    rows = [list(row) + eye for row, eye in zip(matrix, identity(n))]
    for col in range(n):
        pivot = next((i for i in range(col, n) if rows[i][col] % p), None)
        require(pivot is not None, 'singular fixture change of basis')
        rows[col], rows[pivot] = rows[pivot], rows[col]
        scale = pow(rows[col][col], -1, p)
        rows[col] = [(x * scale) % p for x in rows[col]]
        for i in range(n):
            if i != col:
                scale = rows[i][col]
                rows[i] = [(x - scale*y) % p for x, y in zip(rows[i], rows[col])]
    return [row[n:] for row in rows]


def product(table, x, y, p):
    n = len(table)
    result = [0] * n
    for i, a in enumerate(x):
        if a:
            for j, b in enumerate(y):
                if b:
                    for k, c in enumerate(table[i][j]):
                        result[k] = (result[k] + a*b*c) % p
    return result


def model(p, heights):
    bounds = [p**e for e in heights]
    exponents = list(itertools.product(*(range(b) for b in bounds)))
    lookup = {a: i for i, a in enumerate(exponents)}
    n = len(exponents)
    table = [[[0]*n for _ in range(n)] for _ in range(n)]
    for i, a in enumerate(exponents):
        for j, b in enumerate(exponents):
            c = tuple(x+y for x, y in zip(a, b))
            if all(x < bound for x, bound in zip(c, bounds)):
                table[i][j][lookup[c]] = 1
    return table


def rebase(table, matrix, p):
    """Columns of matrix are the new basis in the old coordinates."""
    n = len(table)
    inv = inverse(matrix, p)
    columns = list(map(list, zip(*matrix)))
    result = []
    for x in columns:
        row = []
        for y in columns:
            z = product(table, x, y, p)
            row.append([sum(a*b for a, b in zip(r, z)) % p for r in inv])
        result.append(row)
    return result


def scrambled_basis(n, p, variant):
    rows = identity(n)
    if n == 1:
        rows[0][0] = p-1
        return rows
    # Elementary invertible changes mix the unit, tangent and higher terms.
    for k in range(3*n):
        i = (k + variant) % n
        j = (i + 1 + (k % (n-1))) % n
        if i == j:
            j = (j+1) % n
        c = 1 + (k % (p-1))
        rows[i] = [(a+c*b) % p for a, b in zip(rows[i], rows[j])]
    rows = rows[variant % n:] + rows[:variant % n]
    return rows


def square_zero(p, radical_dimension):
    n = radical_dimension + 1
    table = [[[0]*n for _ in range(n)] for _ in range(n)]
    for i in range(n):
        table[0][i][i] = table[i][0][i] = 1
    return table


def check_transporter_independently(p, table, witness):
    columns = witness['transporter']
    n = len(table)
    matrix = list(map(list, zip(*columns)))
    require(inverse(matrix, p) == witness['inverse'], 'wrong inverse certificate')
    target = model(p, witness['heights'])
    require(len(target) == n, 'wrong model dimension')
    for i in range(n):
        for j in range(n):
            left = product(table, columns[i], columns[j], p)
            right = [sum(target[i][j][a]*columns[a][k] for a in range(n)) % p
                     for k in range(n)]
            require(left == right, 'independent transporter endpoint mismatch')
    return n*n


def rejection_controls(api):
    fixtures = []
    fixtures.append(('square_zero_dimension', 2, square_zero(2, 3)))
    twisted = square_zero(2, 3)
    twisted[1][1][3] = twisted[2][2][3] = 1
    fixtures.append(('quadratic_identification', 2, twisted))
    # F2[x,y,z]/(x^2+yz,y^2,z^2): eight square-free monomials remain,
    # but x has height two while y,z have height one. The model therefore
    # predicts sixteen monomials; the extra mixed relation must be detected.
    exponents = list(itertools.product(range(2), repeat=3))
    lookup = {a: i for i, a in enumerate(exponents)}
    mixed_relation = [[[0]*8 for _ in range(8)] for _ in range(8)]
    for i, a in enumerate(exponents):
        for j, b in enumerate(exponents):
            x, y, z = (u+v for u, v in zip(a, b))
            if x == 2:
                x, y, z = 0, y+1, z+1
            if y < 2 and z < 2:
                mixed_relation[i][j][lookup[(x, y, z)]] = 1
    fixtures.append(('twisted_complete_intersection', 2, mixed_relation))
    field4 = square_zero(2, 1)
    field4[1][1] = [1, 1]
    fixtures.append(('nonsplit_residue_field', 2, field4))
    split = square_zero(2, 1)
    split[1][1] = [0, 1]
    fixtures.append(('product_of_fields', 2, split))
    # F2[t]/t^3 is local but its truncation is not a characteristic power.
    cube = square_zero(2, 2)
    cube[1][1][2] = 1
    fixtures.append(('non_power_truncation', 2, cube))
    noncomm = square_zero(2, 2)
    noncomm[1][2][1] = 1
    fixtures.append(('noncommutative', 2, noncomm))
    nonassoc = square_zero(2, 2)
    nonassoc[1][1][2] = nonassoc[2][2][1] = 1
    fixtures.append(('nonassociative', 2, nonassoc))
    fixtures.append(('no_unit', 2, [[[0, 0] for _ in range(2)] for _ in range(2)]))
    results = []
    for name, p, table in fixtures:
        got = api.recognize(p, table)
        require(got['status'] == 'rejected', 'accepted nonmember '+name)
        result = {'case': name, 'reason': got['reason']}
        if name == 'twisted_complete_intersection':
            require(got.get('radical_dimension') == 7, 'wrong twisted radical dimension')
            require(got.get('heights') == [1, 1, 2], 'wrong twisted Frobenius heights')
            require(got.get('predicted_dimension') == 16, 'wrong twisted model dimension')
            result.update({'heights': got['heights'],
                           'predicted_dimension': got['predicted_dimension']})
        results.append(result)
    return results


def malformed_controls(api):
    cases = [(4, model(2, [1])), (True, model(2, [1])), (2, []),
             (2, [[[0]] , [[0]]]), (2, [[[True]]]),
             (2, [[[0.0]]])]
    count = 0
    for p, table in cases:
        try:
            api.recognize(p, table)
        except ValueError:
            count += 1
        else:
            raise ValueError('malformed input was accepted')
    return count


def normalization_controls(api):
    canonical = api.recognize(3, [[[2]]])
    require(canonical['status'] == 'accepted', 'normalization baseline rejected')
    for coefficient in (5, -1):
        got = api.recognize(3, [[[coefficient]]])
        require(got == canonical, 'integer coefficient normalization changed recognition')
        require(api.validate_witness(3, [[[coefficient]]], got),
                'normalized witness did not verify')
    return 2


def witness_controls(api):
    table = model(2, [1, 2])
    original = api.recognize(2, table)
    require(original['status'] == 'accepted', 'witness control lacks positive baseline')
    mutations = []
    x = copy.deepcopy(original); x['unit'] = [0]*8; mutations.append(('unit', x))
    x = copy.deepcopy(original); x['inverse'][0][0] ^= 1; mutations.append(('inverse', x))
    x = copy.deepcopy(original); x['generators'][0] = [0]*8; mutations.append(('generator', x))
    x = copy.deepcopy(original); x['heights'][0] += 1; mutations.append(('height', x))
    x = copy.deepcopy(original); x['transporter'][1][0] ^= 1; mutations.append(('column', x))
    x = copy.deepcopy(original); x['transporter'].pop(); mutations.append(('missing_column', x))
    x = copy.deepcopy(original); x['monomial_exponents'][0] = [1, 0]; mutations.append(('exponent_order', x))
    count = 0
    for name, witness in mutations:
        try:
            api.validate_witness(2, table, witness)
        except ValueError:
            count += 1
        else:
            raise ValueError('accepted witness mutation '+name)
    return count


def run():
    api = load_recognizer()
    domains = [(2, []), (2, [1]), (2, [2]), (2, [3]), (2, [1, 1]),
               (2, [1, 2]), (2, [2, 2]), (2, [1, 1, 1]), (2, [1, 3]),
               (3, []), (3, [1]), (3, [2]), (3, [1, 1]), (5, [1]), (7, [1])]
    cases, product_checks = [], 0
    for p, heights in domains:
        table = model(p, heights)
        for variant in range(3):
            actual = table if variant == 0 else rebase(table, scrambled_basis(len(table), p, variant), p)
            got = api.recognize(p, actual)
            require(got['status'] == 'accepted', 'target rejected '+str((p, heights, variant)))
            require(got['heights'] == heights, 'incorrect recovered heights')
            product_checks += check_transporter_independently(p, actual, got)
            cases.append({'p': p, 'heights': heights, 'n': len(table), 'chart': variant})
    # In this chart the short variable is hidden as x+y^2, not a coordinate axis.
    table = model(2, [1, 3])
    chart = identity(16)
    chart[2][8] = 1
    hidden = api.recognize(2, rebase(table, chart, 2))
    require(hidden['status'] == 'accepted' and hidden['heights'] == [1, 3], 'nonlinear lift lost')
    product_checks += check_transporter_independently(2, rebase(table, chart, 2), hidden)
    cases.append({'p': 2, 'heights': [1, 3], 'n': 16, 'chart': 'hidden_short_generator'})
    trap = api.recognize(2, model(2, [2]))
    require(trap['heights'] == [2], 'tangent Frobenius trap')
    return {'status': 'PASS_FROBENIUS_ALGEBRA_RECOGNITION',
            'positive_presentations': len(cases), 'positive_cases': cases,
            'independent_basis_product_checks': product_checks,
            'nonmember_controls': rejection_controls(api),
            'malformed_controls': malformed_controls(api),
            'normalization_controls': normalization_controls(api),
            'witness_mutations_rejected': witness_controls(api),
            'scope': 'Supplied common-basis prime-field algebra tables; no arbitrary tensor recognition or new kappa.'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--json', action='store_true')
    args = parser.parse_args()
    result = run()
    if args.json:
        print(json.dumps(result, sort_keys=True, indent=2))
    else:
        print(result['status'], json.dumps({k: v for k, v in result.items()
              if k not in ('status', 'positive_cases')}, sort_keys=True))
