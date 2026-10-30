#!/usr/bin/env python3
"""Exact bounded checks of the nonsplit presentation bridge and SL transport.

Independent polynomial arithmetic, elimination and literal tensor coefficients
are used as oracles. Retained recognition and character code are targets, not
oracles for their own acceptance. apoursh with OpenAI Codex; Apache-2.0.
"""
import argparse
import copy
import hashlib
import itertools
import json
from pathlib import Path
from types import ModuleType


def require(condition, message):
    if not condition:
        raise ValueError(message)


def authenticate_sources():
    package = Path(__file__).resolve().parent
    root = package.parents[1]
    manifest = json.loads((package / 'SOURCES.json').read_text())
    rows = [r for r in manifest['files'] if r.get('usage') == 'input']
    names = {'character_model.py', 'vendor/local.py', 'vendor/split.py',
             'vendor/recognize.py', 'vendor/character-proof.md',
             'vendor/character-readme.md', 'vendor/recognition-proof.md',
             'vendor/recognition-readme.md', 'vendor/split-recognition-proof.md',
             'vendor/ORIGINS.json'}
    expected = {'research/nonsplit-sl-transport/' + p for p in names}
    require(len(rows) == len(expected) and {r['path'] for r in rows} == expected,
            'live source inventory differs from ten retained inputs')
    for row in rows:
        actual = hashlib.sha256((root / row['path']).read_bytes()).hexdigest()
        require(actual == row['sha256'], 'source hash mismatch: ' + row['path'])
    return len(rows)


def load_api():
    path = Path(__file__).with_name('bridge.py')
    module = ModuleType('bridge_target')
    module.__file__ = str(path)
    exec(compile(path.read_bytes(), str(path), 'exec'), module.__dict__)
    return module


class Arithmetic:
    """Independent base field from ordinary polynomial remainder arithmetic."""
    def __init__(self, p, modulus):
        self.p, self.modulus, self.degree = p, tuple(modulus), len(modulus)-1
        self.q = p**self.degree
        digits = [[(a//p**i) % p for i in range(self.degree)] for a in range(self.q)]
        self.add = [[sum(((x+y) % p)*p**i for i, (x, y) in enumerate(zip(a, b)))
                     for b in digits] for a in digits]
        self.neg = [sum((-x % p)*p**i for i, x in enumerate(a)) for a in digits]
        self.mul = [[self._product(a, b) for b in digits] for a in digits]
        self.inv = [0] + [next(b for b in range(1, self.q) if self.mul[a][b] == 1)
                          for a in range(1, self.q)]

    def _product(self, a, b):
        values = [0]*(2*self.degree-1)
        for i, x in enumerate(a):
            for j, y in enumerate(b):
                values[i+j] = (values[i+j]+x*y) % self.p
        for k in range(len(values)-1, self.degree-1, -1):
            c = values[k]
            for j, m in enumerate(self.modulus[:-1]):
                values[k-self.degree+j] = (values[k-self.degree+j]-c*m) % self.p
        return sum(values[i]*self.p**i for i in range(self.degree))

    def total(self, values):
        out = 0
        for value in values:
            out = self.add[out][value]
        return out

    def power(self, a, n):
        out = 1
        while n:
            if n & 1:
                out = self.mul[out][a]
            a = self.mul[a][a]
            n //= 2
        return out


def identity(n):
    return [[int(i == j) for j in range(n)] for i in range(n)]


def transpose(matrix):
    return [list(col) for col in zip(*matrix)]


def determinant(matrix, f):
    rows = copy.deepcopy(matrix)
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
        rows[j] = [f.mul[f.inv[rows[j][j]]][x] for x in rows[j]]
        for i in range(n):
            if i != j:
                scale = f.neg[rows[i][j]]
                rows[i] = [f.add[x][f.mul[scale][y]] for x, y in zip(rows[i], rows[j])]
    return [row[n:] for row in rows]


def mv(matrix, vector, f):
    return [f.total(f.mul[x][y] for x, y in zip(row, vector)) for row in matrix]


def mm(left, right, f):
    return transpose([mv(left, col, f) for col in transpose(right)])


def multiply(table, a, b, f):
    out = [0]*len(table)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            if x and y:
                xy = f.mul[x][y]
                for k, z in enumerate(table[i][j]):
                    out[k] = f.add[out[k]][f.mul[xy][z]]
    return out


def field_table(modulus, f):
    d = len(modulus)-1
    result = [[[0]*d for _ in range(d)] for _ in range(d)]
    for i, j in itertools.product(range(d), repeat=2):
        value = [0]*(2*d-1)
        value[i+j] = 1
        for k in range(2*d-2, d-1, -1):
            for r, c in enumerate(modulus[:-1]):
                correction = f.neg[f.mul[value[k]][c]]
                value[k-d+r] = f.add[value[k-d+r]][correction]
        result[i][j] = value[:d]
    return result


def product_model(components, f):
    blocks = []
    for component in components:
        field, hs = component['field'], component['heights']
        d = len(field)
        exponents = list(itertools.product(*(range(f.p**h) for h in hs)))
        positions = {a: i for i, a in enumerate(exponents)}
        n = d*len(exponents)
        table = [[[0]*n for _ in range(n)] for _ in range(n)]
        for i, a in enumerate(exponents):
            for j, b in enumerate(exponents):
                c = tuple(x+y for x, y in zip(a, b))
                if all(x < f.p**h for x, h in zip(c, hs)):
                    offset = d*positions[c]
                    for u, v in itertools.product(range(d), repeat=2):
                        table[d*i+u][d*j+v][offset:offset+d] = field[u][v]
        blocks.append(table)
    n = sum(map(len, blocks))
    table = [[[0]*n for _ in range(n)] for _ in range(n)]
    offset = 0
    for block in blocks:
        size = len(block)
        for i, j in itertools.product(range(size), repeat=2):
            table[offset+i][offset+j][offset:offset+size] = block[i][j]
        offset += size
    return table


def endpoint(target, P, Q, R, source, f):
    left, right = transpose(P), transpose(Q)
    return all(multiply(target, left[i], right[j], f) == mv(R, source[i][j], f)
               for i, j in itertools.product(range(len(source)), repeat=2))


def transform(table, U, V, W, f):
    u, v = transpose(inverse(U, f)), transpose(inverse(V, f))
    return [[mv(W, multiply(table, x, y, f), f) for y in v] for x in u]


def coefficient_action(source, A, B, C, target, f):
    n = len(source)
    support = [(r, s, t, source[r][s][t]) for r, s, t in itertools.product(range(n), repeat=3)
               if source[r][s][t]]
    for i, j, k in itertools.product(range(n), repeat=3):
        value = f.total(f.mul[f.mul[A[i][r]][B[j][s]]][f.mul[C[k][t]][v]]
                        for r, s, t, v in support)
        if value != target[i][j][k]:
            return False
    return True


def refused(action, label):
    try:
        action()
    except (ValueError, TypeError):
        return 1
    raise ValueError('invalid input accepted: '+label)


def check_normalized(cert, target, canonical, f):
    require(endpoint(target, cert['U'], cert['V'], cert['W'], canonical, f),
            'normalized certificate literal product mismatch')
    ds = [determinant(cert[k], f) for k in ('U', 'V', 'W')]
    delta = f.mul[ds[2]][f.inv[f.mul[ds[0]][ds[1]]]]
    require(cert['determinants'] == ds and cert['d'] == delta,
            'normalized determinant accounting mismatch')
    require(cert['label'] == f.power(delta, (f.q-1)//cert['index']), 'label arithmetic mismatch')


def check_transport(result, first, second, f):
    require(result is not None, 'expected transporter rejected')
    mats = [result[k] for k in ('P', 'Q', 'R')]
    require([determinant(m, f) for m in mats] == [1, 1, 1], 'transport is not special linear')
    require(endpoint(second, *mats, first, f), 'literal transported multiplication failed')
    require(result['A'] == transpose(inverse(mats[0], f))
            and result['B'] == transpose(inverse(mats[1], f)) and result['C'] == mats[2],
            'covariant transport convention mismatch')
    require(coefficient_action(first, result['A'], result['B'], result['C'], second, f),
            'literal covariant coefficient transport failed')


def basis_changes(d, f):
    for entries in itertools.product(range(f.q), repeat=d*(d-1)):
        matrix = [[int(i == 0)]+list(entries[i*(d-1):(i+1)*(d-1)]) for i in range(d)]
        if determinant(matrix, f):
            yield matrix


def field_presentations(api):
    fixtures = [(2, [0, 1], [1, 1, 1]), (3, [0, 1], [1, 0, 1]),
                (2, [1, 1, 1], [2, 1, 1]), (2, [0, 1], [1, 1, 0, 1])]
    reports = []
    for p, base_modulus, modulus in fixtures:
        f = Arithmetic(p, base_modulus)
        base = api.Field(p, base_modulus)
        d, canonical = len(modulus)-1, field_table(modulus, f)
        residue = api.Extension(base, modulus)
        cases, isomorphisms, distinct = 0, 0, set()
        for S in basis_changes(d, f):
            table = transform(canonical, inverse(S, f), inverse(S, f), inverse(S, f), f)
            cert = dict(components=[dict(degree=d, heights=[], field=table)], U=S, V=S, W=S)
            maps = []
            for choice in range(d):
                phi = api.field_isomorphism(table, canonical, base, component_choice=choice)
                require(determinant(phi, f) != 0 and mv(phi, identity(d)[0], f) == identity(d)[0],
                        'field identification fails invertibility/unit')
                require(endpoint(canonical, phi, phi, phi, table, f), 'field identification fails products')
                normalized = api.normalize_certificate(canonical, cert, base, {d: residue},
                                                       field_choices=[choice])
                check_normalized(normalized, canonical, canonical, f)
                require(normalized['label'] == 1, 'field identification choice changes normalized orbit')
                maps.append(tuple(sum(phi, [])))
                isomorphisms += 1
            require(len(set(maps)) == d, 'primitive choices do not give all field identifications')
            distinct.add(json.dumps(table))
            cases += 1
        reports.append(dict(base_size=f.q, residue_degree=d, unit_first_bases=cases,
                            distinct_tables=len(distinct), all_primitive_choices=isomorphisms))
    require([r['unit_first_bases'] for r in reports] == [2, 6, 12, 24], 'complete basis domain changed')
    return reports


def shear(n, shift, f):
    matrix = identity(n)
    for i in range(n):
        j = (i+shift+1) % n
        if i != j:
            matrix[i] = [f.add[x][y] for x, y in zip(matrix[i], matrix[j])]
    return matrix


def fixtures_and_recognition(api):
    fixtures = [(2, [0, 1], [(1, []), (2, [1])], {1: [0, 1], 2: [1, 1, 1]}),
                (2, [0, 1], [(2, []), (2, []), (3, [])], {2: [1, 1, 1], 3: [1, 1, 0, 1]}),
                (3, [0, 1], [(3, [])], {3: [2, 2, 0, 1]}),
                (3, [0, 1], [(3, []), (3, [])], {3: [2, 2, 0, 1]}),
                (2, [1, 1, 1], [(2, [1])], {2: [2, 1, 1]}),
                (3, [1, 0, 1], [(2, [])], {2: [8, 0, 1]})]
    reports, transpose_rejections = [], 0
    for p, base_modulus, types, moduli in fixtures:
        f, base = Arithmetic(p, base_modulus), api.Field(p, base_modulus)
        components = [dict(degree=d, heights=hs, field=field_table(moduli[d], f)) for d, hs in types]
        canonical = product_model(components, f)
        n = len(canonical)
        residues = {d: api.Extension(base, moduli[d]) for d in moduli}
        matrices = [shear(n, shift, f) for shift in (0, 1, 2)]
        target = transform(canonical, *matrices, f)
        raw, reason = api.recognition.recognize(target, base)
        require(raw is not None and reason is None, 'retained recognizer failed a specified valid tensor')
        require(endpoint(target, raw['U'], raw['V'], raw['W'], product_model(raw['components'], f), f),
                'retained output fails independent basis products')
        cert = api.normalize_certificate(target, raw, base, residues)
        check_normalized(cert, target, canonical, f)
        require(cert['label'] == 1, 'independent determinant-one bases change orbit label')
        bridge, why = api.sl_transport(canonical, target, base, residues)
        require(why is None, 'valid recognition transport returned a reason')
        check_transport(bridge, canonical, target, f)
        if not coefficient_action(canonical, inverse(bridge['P'], f), inverse(bridge['Q'], f),
                                  bridge['R'], target, f):
            transpose_rejections += 1
        reports.append(dict(base_size=f.q, types=types, dimension=n, checked_basis_products=n*n))
    require(transpose_rejections > 0, 'missing inverse-transpose mutant escaped every fixture')
    return dict(presentations=reports, missing_transpose_controls=transpose_rejections)


def determinant_domains(api):
    f, base = Arithmetic(3, [1, 0, 1]), api.Field(3, [1, 0, 1])
    modulus, d = [8, 0, 1], 2
    canonical = field_table(modulus, f)
    residues = {d: api.Extension(base, modulus)}
    accepted, rejected, labels = 0, 0, set()
    # All determinant triples, not every matrix in the GL orbit.
    for a, b, c in itertools.product(range(1, f.q), repeat=3):
        mats = [[[value, 0], [0, 1]] for value in (a, b, c)]
        target = transform(canonical, *mats, f)
        delta = f.mul[c][f.inv[f.mul[a][b]]]
        expected = delta in (1, f.neg[1])
        result, reason = api.sl_transport(canonical, target, base, residues)
        if expected:
            require(reason is None, 'allowed determinant triple rejected')
            check_transport(result, canonical, target, f)
            accepted += 1
        else:
            require(result is None and reason is not None, 'different SL cosets connected')
            rejected += 1
        got, why = api.recognize(target, base, residues)
        require(why is None and got is not None, 'GL-equivalent tensor not recognized')
        check_normalized(got, target, canonical, f)
        require(got['label'] == f.power(delta, 2) and got['index'] == 4,
                'F81-over-F9 four-coset classification differs')
        labels.add(got['label'])
    require((accepted, rejected, len(labels)) == (128, 384, 4), 'complete determinant census changed')
    S = [[1, 0], [0, 4]]
    discovered = transform(canonical, inverse(S, f), inverse(S, f), inverse(S, f), f)
    raw = dict(components=[dict(degree=2, heights=[], field=discovered)], U=S, V=S, W=S)
    raw_label = f.power(f.inv[determinant(S, f)], 2)
    normalized = api.normalize_certificate(canonical, raw, base, residues)
    require(raw_label != 1 and normalized['label'] == 1, 'omitted bridge determinant mutant escaped')
    # Odd degree has no Frobenius sign; a unit-first basis of determinant -1 flips the raw label.
    f3, b3 = Arithmetic(3, [0, 1]), api.Field(3, [0, 1])
    cubic = field_table([2, 2, 0, 1], f3)
    S3 = [[1, 0, 0], [0, 2, 0], [0, 0, 1]]
    changed = transform(cubic, inverse(S3, f3), inverse(S3, f3), inverse(S3, f3), f3)
    raw3 = dict(components=[dict(degree=3, heights=[], field=changed)], U=S3, V=S3, W=S3)
    cubic_labels = [api.normalize_certificate(cubic, raw3, b3, {3: api.Extension(b3, [2, 2, 0, 1])},
                                             field_choices=[i])['label'] for i in range(3)]
    require(cubic_labels == [1]*3, 'cubic presentation sign not normalized')
    return dict(base_size=9, residue_degree=2, determinant_triples=512, accepted=accepted,
                rejected=rejected, labels=sorted(labels), unnormalized_basis_label=raw_label,
                normalized_basis_label=normalized['label'], cubic_raw_label=2,
                cubic_normalized_labels=cubic_labels)


def presentation_matching(api):
    f, base = Arithmetic(3, [0, 1]), api.Field(3, [0, 1])
    moduli = {1: [0, 1], 3: [2, 2, 0, 1]}
    residues = {d: api.Extension(base, poly) for d, poly in moduli.items()}
    one = dict(degree=1, heights=[], field=field_table(moduli[1], f))
    three = dict(degree=3, heights=[], field=field_table(moduli[3], f))
    canonical = product_model([one, three], f)
    permutation = transpose([identity(4)[i] for i in (1, 2, 3, 0)])
    raw = dict(components=[three, one], U=permutation, V=permutation, W=permutation)
    require(determinant(permutation, f) == 2, 'odd block-order determinant fixture changed')
    cert = api.normalize_certificate(canonical, raw, base, residues)
    check_normalized(cert, canonical, canonical, f)
    require(cert['label'] == 1 and cert['index'] == 2, 'component order sign not normalized')
    # Every ordering of three labeled factors, with repeated odd-degree types,
    # and every independent coefficient-field identification for those factors.
    components = [one, three, three]
    canonical = product_model(components, f)
    ranges, offset = [], 0
    for c in components:
        ranges.append(list(range(offset, offset+c['degree'])))
        offset += c['degree']
    cases = 0
    for order in itertools.permutations(range(3)):
        indices = [i for c in order for i in ranges[c]]
        permutation = transpose([identity(7)[i] for i in indices])
        raw = dict(components=[components[i] for i in order],
                   U=permutation, V=permutation, W=permutation)
        for first, second in itertools.product(range(3), repeat=2):
            cert = api.normalize_certificate(canonical, raw, base, residues,
                                             field_choices=[0, first, second])
            check_normalized(cert, canonical, canonical, f)
            require(cert['label'] == 1 and cert['index'] == 1,
                    'equal-type matching changes the SL orbit label')
            cases += 1
    # Changing the common reference can shift every label by the same factor;
    # relative equivalence remains invariant. Let v=beta*u in F81 over F9.
    f9, b9 = Arithmetic(3, [1, 0, 1]), api.Field(3, [1, 0, 1])
    beta = 4
    original = field_table([8, 0, 1], f9)
    original_residue = {2: api.Extension(b9, [8, 0, 1])}
    alternate_poly = [f9.neg[f9.power(beta, 3)], 0, 1]
    alternate_residue = {2: api.Extension(b9, alternate_poly)}
    reference_shift = f9.power(f9.inv[beta], 2)
    shifts = []
    for scalar in range(1, f9.q):
        target = transform(original, [[scalar, 0], [0, 1]], identity(2), identity(2), f9)
        old, why = api.recognize(target, b9, original_residue)
        new, why_new = api.recognize(target, b9, alternate_residue)
        require(why is None and why_new is None, 'alternate supplied reference rejected')
        require(new['label'] == f9.mul[old['label']][reference_shift],
                'reference-label conversion lacks the determinant factor')
        shifts.append([old['label'], new['label']])
    require(reference_shift != 1, 'reference change must genuinely relabel the four cosets')
    return dict(odd_component_order_raw_label=2, odd_component_order_normalized_label=1,
                repeated_component_order_and_field_choices=cases,
                alternate_reference_pairs=shifts, reference_shift=reference_shift)


def input_controls(api):
    f, base = Arithmetic(2, [1, 1, 1]), api.Field(2, [1, 1, 1])
    table = field_table([2, 1, 1], f)
    residues = {2: api.Extension(base, [2, 1, 1])}
    cert = dict(components=[dict(degree=2, heights=[], field=table)],
                U=identity(2), V=identity(2), W=identity(2))
    count = 0
    for bad in (-1, 4, True, 0.5):
        altered = copy.deepcopy(table); altered[1][1][0] = bad
        count += refused(lambda altered=altered: api.field_isomorphism(altered, table, base),
                         'noncanonical coefficient field entry')
        altered_cert = copy.deepcopy(cert); altered_cert['U'][0][0] = bad
        count += refused(lambda altered_cert=altered_cert: api.normalize_certificate(table, altered_cert, base, residues),
                         'noncanonical factor-map entry')
    for choice in (-1, 2, True, 0.5):
        count += refused(lambda choice=choice: api.field_isomorphism(table, table, base, choice),
                         'invalid primitive-idempotent choice')
    badfield = [[[1, 0], [0, 1]], [[0, 1], [0, 0]]]
    count += refused(lambda: api.field_isomorphism(badfield, table, base), 'nonreduced coefficient algebra')
    splitfield = [[[1, 0], [0, 1]], [[0, 1], [0, 1]]]
    count += refused(lambda: api.field_isomorphism(splitfield, table, base), 'split coefficient algebra')
    count += refused(lambda: api.field_isomorphism(table, [[[1]]], base), 'unequal residue degrees')
    for key in ('U', 'V', 'W'):
        altered = copy.deepcopy(cert); altered[key][0][1] = 1
        count += refused(lambda altered=altered: api.normalize_certificate(table, altered, base, residues),
                         'changed three-factor map')
    altered = copy.deepcopy(cert); altered['components'][0]['degree'] = True
    count += refused(lambda: api.normalize_certificate(table, altered, base, residues), 'boolean residue degree')
    altered = copy.deepcopy(cert); altered['components'][0]['heights'] = [True]
    count += refused(lambda: api.normalize_certificate(table, altered, base, residues), 'boolean height')
    count += refused(lambda: api.normalize_certificate(table, cert, base, {}), 'missing reference residue')
    count += refused(lambda: api.normalize_certificate(table, cert, base, {2: api.Extension(base, [0, 1])}),
                     'wrong reference degree')
    # Absolute p-Frobenius is not base-linear when q > p: extending its basis images linearly fails.
    unit, beta = identity(2)
    p_power = multiply(table, beta, beta, f)
    fake = transpose([unit, p_power])
    require(not endpoint(table, fake, fake, fake, table, f), 'p-versus-q Frobenius control is nondiscriminating')
    actual = [api.field_isomorphism(table, table, base, i) for i in range(2)]
    require(all(phi != fake for phi in actual), 'non-base-linear absolute Frobenius accepted')
    semilinear = dict(components=copy.deepcopy(cert['components']), U=fake, V=fake, W=fake)
    count += refused(lambda: api.normalize_certificate(table, semilinear, base, residues),
                     'absolute p-Frobenius basis images extended incorrectly over K')
    # Same ground dimension does not determine residue degree or height type.
    f2, b2 = Arithmetic(2, [0, 1]), api.Field(2, [0, 1])
    fields = {1: field_table([0, 1], f2), 2: field_table([1, 1, 1], f2)}
    models = [product_model([dict(degree=d, heights=hs, field=fields[d])], f2)
              for d, hs in ((1, [2]), (1, [1, 1]), (2, [1]))]
    for other in models[1:]:
        result, reason = api.sl_transport(models[0], other, b2,
                                          {1: api.Extension(b2, [0, 1]), 2: api.Extension(b2, [1, 1, 1])})
        require(result is None and reason is not None, 'different complete types treated as equivalent')
    return dict(malformed_rejections=count, wrong_type_rejections=2,
                absolute_frobenius_mutant_rejected=True)


def run():
    sources = authenticate_sources()
    api = load_api()
    return dict(status='PASS_NONSPLIT_SL_TRANSPORT', authenticated_source_files=sources,
                field_presentations=field_presentations(api),
                actual_recognition=fixtures_and_recognition(api),
                determinant_domains=determinant_domains(api),
                presentation_matching=presentation_matching(api),
                input_controls=input_controls(api),
                scope='Complete listed field-basis and determinant-triple domains; no exhaustive arbitrary-tensor census or physical cost claim.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--json', action='store_true')
    args = parser.parse_args()
    report = run()
    if args.json:
        print(json.dumps(report, sort_keys=True, indent=2))
    else:
        print(report['status'])
        print(json.dumps({k: v for k, v in report.items() if k != 'status'}, sort_keys=True))
