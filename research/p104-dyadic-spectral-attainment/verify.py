#!/usr/bin/env python3
"""Exact dyadic endpoint-rank certificates; standard library, Apache-2.0.

AAAmirinu with substantial OpenAI Codex assistance. The obstruction and lift
question are Nick Petalas's. The triangular congruence and P104 port convention
are Chris R / Clear1nsight's p104-tensor-code work; source_matrix there guided
the independent reconstruction below. The pinned fixture retains its authors.
No native implementation, cost, scratch, or selected-frontier claim is checked.
"""
from fractions import Fraction as F
import hashlib
import itertools
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PIVOTS = (0, 1, 3, 6, 22, 31, 93, 103)
FIXTURE = 'research/p104-native-channel/inputs/P104-FIXTURE.json'
EXPECTED_INPUTS = {
    FIXTURE,
    'research/p104-joint-spectral-obstruction/PROOF.md',
    'research/p104-tensor-code/PROOF.md',
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read_json(raw):
    def unique(items):
        result = {}
        for key, value in items:
            require(key not in result, 'duplicate JSON key')
            result[key] = value
        return result
    return json.loads(raw, object_pairs_hook=unique)


def verify_source(raw, row):
    require(hashlib.sha256(raw).hexdigest() == row['sha256'], 'source SHA256 mismatch')
    blob = b'blob ' + str(len(raw)).encode('ascii') + b'\0' + raw
    require(hashlib.sha1(blob).hexdigest() == row['git_blob'], 'source Git blob mismatch')


def authenticate():
    rows = [row for row in read_json((HERE / 'SOURCES.json').read_bytes())['files']
            if row['usage'] == 'input']
    require(len(rows) == len(EXPECTED_INPUTS) and
            {row['path'] for row in rows} == EXPECTED_INPUTS, 'source inventory mismatch')
    inputs = {}
    for row in rows:
        path = ROOT / row['path']
        require(not path.is_symlink(), 'source symlink')
        raw = path.read_bytes()
        verify_source(raw, row)
        inputs[row['path']] = (raw, row)
    return inputs


def zero(rows, cols=None):
    return [[F(0) for _ in range(rows if cols is None else cols)] for _ in range(rows)]


def eye(size):
    result = zero(size)
    for i in range(size):
        result[i][i] = F(1)
    return result


def transpose(a):
    return [list(row) for row in zip(*a)]


def multiply(a, b):
    require(len(a[0]) == len(b), 'matrix shape mismatch')
    result = zero(len(a), len(b[0]))
    sparse_b = [[(j, value) for j, value in enumerate(row) if value] for row in b]
    for i, row in enumerate(a):
        for k, value in enumerate(row):
            if value:
                for j, other in sparse_b[k]:
                    result[i][j] += value * other
    return result


def scale(value, a):
    return [[value * cell for cell in row] for row in a]


def add(a, b):
    require(len(a) == len(b) and len(a[0]) == len(b[0]), 'matrix shape mismatch')
    return [[x + y for x, y in zip(ar, br)] for ar, br in zip(a, b)]


def subtract(a, b):
    return add(a, scale(-1, b))


def blocks(a, b, c, d):
    return [ar + br for ar, br in zip(a, b)] + [cr + dr for cr, dr in zip(c, d)]


def diagonal(a, b):
    return blocks(a, zero(len(a), len(b)), zero(len(b), len(a)), b)


def tensor(a, b):
    # Large P104 two-axis matrices must remain factored, including controls.
    require(len(a) * len(b) <= 32 and len(a[0]) * len(b[0]) <= 32,
            'literal tensor exceeds small-fixture bound')
    return [[x * y for x in ar for y in br] for ar in a for br in b]


def upper_minus(c):
    n = len(c)
    return blocks(eye(n), scale(-1, c), zero(n), eye(n))


def lower(b):
    n = len(b)
    return blocks(eye(n), zero(n), b, eye(n))


def rank_exact(a):
    work = [[F(x) for x in row] for row in a]
    rank = 0
    for col in range(len(work[0])):
        pivot = next((i for i in range(rank, len(work)) if work[i][col]), None)
        if pivot is None:
            continue
        work[rank], work[pivot] = work[pivot], work[rank]
        value = work[rank][col]
        work[rank] = [x / value for x in work[rank]]
        for i in range(rank + 1, len(work)):
            value = work[i][col]
            if value:
                work[i] = [x - value * y for x, y in zip(work[i], work[rank])]
        rank += 1
        if rank == len(work):
            break
    return rank


def determinant_exact(a):
    require(len(a) == len(a[0]), 'determinant needs square matrix')
    work = [[F(x) for x in row] for row in a]
    result = F(1)
    for col in range(len(work)):
        pivot = next((i for i in range(col, len(work)) if work[i][col]), None)
        if pivot is None:
            return F(0)
        if pivot != col:
            work[col], work[pivot] = work[pivot], work[col]
            result = -result
        value = work[col][col]
        result *= value
        for i in range(col + 1, len(work)):
            ratio = work[i][col] / value
            if ratio:
                work[i] = [x - ratio * y for x, y in zip(work[i], work[col])]
    return result


def residue(value, prime=13):
    value = F(value)
    require(value.denominator % prime != 0, 'non-reducible denominator')
    return value.numerator * pow(value.denominator, -1, prime) % prime


def modular_elimination(a, prime=13):
    work = [[residue(x, prime) for x in row] for row in a]
    rank, determinant, columns = 0, 1, []
    for col in range(len(work[0])):
        pivot = next((i for i in range(rank, len(work)) if work[i][col]), None)
        if pivot is None:
            continue
        if pivot != rank:
            work[rank], work[pivot] = work[pivot], work[rank]
            determinant = -determinant
        value = work[rank][col]
        determinant = determinant * value % prime
        inv = pow(value, -1, prime)
        work[rank] = [x * inv % prime for x in work[rank]]
        for i in range(rank + 1, len(work)):
            value = work[i][col]
            if value:
                work[i] = [(x - value * y) % prime for x, y in zip(work[i], work[rank])]
        columns.append(col)
        rank += 1
        if rank == len(work):
            break
    square = len(a) == len(a[0])
    return rank, determinant % prime if square and rank == len(a) else None, columns


def matrix_hash(a):
    raw = json.dumps([[str(F(x)) for x in row] for row in a],
                     separators=(',', ':')).encode('ascii')
    return hashlib.sha256(raw).hexdigest()


def dyadic(a):
    return all(F(x).denominator & (F(x).denominator - 1) == 0 for row in a for x in row)


def axis_data(b, expected_norm):
    b = [[F(x) for x in row] for row in b]
    r, m = len(b), len(b[0])
    require(all(len(row) == m for row in b), 'ragged coupling matrix')
    n = r + m
    require(multiply(b, transpose(b)) == scale(expected_norm, eye(r)), 'coupling Gram mismatch')
    u, inverse, p = eye(n), eye(n), zero(n)
    for i in range(r):
        p[i][i] = F(1)
        for j in range(m):
            u[i][r + j] = b[i][j]
            inverse[i][r + j] = -b[i][j]
    # Unit upper triangular form explicitly certifies det(U)=det(U^-1)=1.
    require(all(u[i][j] == 0 for i in range(n) for j in range(i)) and
            all(u[i][i] == 1 for i in range(n)), 'unit triangular code mismatch')
    require(multiply(u, inverse) == eye(n) and multiply(inverse, u) == eye(n),
            'explicit inverse mismatch')
    ut, uit = transpose(u), transpose(inverse)
    a = multiply(multiply(ut, p), u)
    matrix_m = multiply(u, ut)
    inverse_m = multiply(uit, inverse)
    require(multiply(matrix_m, inverse_m) == eye(n), 'M inverse mismatch')
    # These one-axis identities prove the large tensor conjugations by factoring.
    require(multiply(multiply(uit, a), inverse) == p, 'congruence mismatch')
    require(multiply(multiply(uit, a), ut) == multiply(p, matrix_m), 'lower factor mismatch')
    require(multiply(uit, ut) == eye(n), 'upper factor mismatch')
    require(all(dyadic(x) for x in (b, u, inverse, p, a, matrix_m, inverse_m)),
            'non-dyadic code or inverse')
    return {'n': n, 'r': r, 'b': b, 'u': u, 'inverse': inverse,
            'p': p, 'a': a, 'm': matrix_m}


def reconstruct_ports(raw):
    # Enumerate positive doubled E8 root representatives, not a stored Gram.
    roots = set()
    for i, j in itertools.combinations(range(8), 2):
        for last in (-2, 2):
            root = [0] * 8
            root[i], root[j] = 2, last
            roots.add(tuple(root))
    for tail in itertools.product((-1, 1), repeat=7):
        if sum(x < 0 for x in tail) % 2 == 0:
            roots.add((1,) + tail)
    fixture = read_json(raw)['section4_explicit_P104']
    removed_rows = fixture['F0'] + fixture['C']
    removed = {tuple(row) for row in removed_rows}
    require(len(roots) == 120 and len(removed_rows) == len(removed) == 16 and
            removed <= roots, 'root or removed-frame inventory mismatch')
    ports = sorted(roots - removed)
    require(len(ports) == 104, 'P104 port inventory mismatch')
    order = list(PIVOTS) + [i for i in range(104) if i not in PIVOTS]
    require(sorted(order) == list(range(104)), 'port permutation mismatch')
    ports = [ports[i] for i in order]
    # Coordinates are doubled roots: A=Gram/2 before doubling is dot/8 here.
    a = [[F(sum(x * y for x, y in zip(v, w)), 8) for w in ports] for v in ports]
    require([row[:8] for row in a[:8]] == eye(8), 'pivot Gram mismatch')
    b = [row[8:] for row in a[:8]]
    require(all(x in (F(-1, 2), F(0), F(1, 2)) for row in b for x in row),
            'P104 signed-half coupling mismatch')
    require(sum(bool(x) for row in b for x in row) == 384, 'P104 coupling count mismatch')
    axis = axis_data(b, F(12))
    require(axis['a'] == a, 'independent Gram/congruence mismatch')
    v = [row[:] for row in axis['u'][:8]]
    require(multiply(v, transpose(v)) == scale(13, eye(8)), 'Gram spectral factor mismatch')
    require(multiply(transpose(v), v) == a, 'Gram reconstruction factor mismatch')
    # V V^t=13I and A=V^t V imply A^2=13A without a dense pair matrix.
    return ports, axis


def check_coefficients(alpha, beta):
    require(alpha * beta == 169, 'spectral coefficient product mismatch')


def check_transformed_pair(original, q, q_inverse, pc, lower_coefficient):
    size = len(pc)
    require(multiply(q, q_inverse) == eye(2 * size) and
            multiply(q_inverse, q) == eye(2 * size), 'pair code inverse mismatch')
    actual = multiply(multiply(q, original), q_inverse)
    expected = blocks(subtract(eye(size), multiply(pc, lower_coefficient)), scale(-1, pc),
                      lower_coefficient, eye(size))
    require(actual == expected, 'ordered conjugated pair mismatch')
    return actual


def check_correction(transformed, pc, pr, lower_coefficient, alpha, beta, expected_rank):
    check_coefficients(alpha, beta)
    target = multiply(upper_minus(scale(alpha, pc)), lower(scale(beta, pr)))
    actual = subtract(transformed, target)
    predicted = blocks(scale(-1, multiply(pc, subtract(lower_coefficient, scale(169, pr)))),
                       scale(alpha - 1, pc), subtract(lower_coefficient, scale(beta, pr)),
                       zero(len(pc)))
    require(actual == predicted, 'correction block formula mismatch')
    require(rank_exact(actual) == expected_rank, 'literal correction rank mismatch')
    require(modular_elimination(actual)[0] == expected_rank, 'literal modular rank mismatch')
    return {'alpha': alpha, 'beta': beta, 'rank_Q': expected_rank,
            'rank_F13': expected_rank, 'correction_sha256': matrix_hash(actual)}


def toy_case():
    a = [[F(13), F(1)], [F(0), F(0)]]
    h = [[F(13), F(1)], [F(1), F(0)]]
    h_inverse = [[F(0), F(1)], [F(1), F(-13)]]
    p = [[F(1), F(0)], [F(0), F(0)]]
    pc, pr = tensor(eye(2), p), tensor(p, eye(2))
    q = diagonal(eye(4), tensor(eye(2), h))
    q_inverse = diagonal(eye(4), tensor(eye(2), h_inverse))
    upper, bottom = upper_minus(tensor(eye(2), a)), lower(tensor(a, eye(2)))
    original = multiply(upper, bottom)
    lower_coefficient = tensor(a, h)
    transformed = check_transformed_pair(original, q, q_inverse, pc, lower_coefficient)
    require(multiply(a, a) == scale(13, a) and modular_elimination(a)[0] == 1,
            'toy spectral premise mismatch')
    require(determinant_exact(q) == 1 and dyadic(q_inverse), 'toy ring inverse mismatch')
    cases = [check_correction(transformed, pc, pr, lower_coefficient, 1, 169, 2),
             check_correction(transformed, pc, pr, lower_coefficient, 13, 13, 4)]
    return {'name': 'integral-handoff-toy', 'dimension': 8, 'cases': cases}, (
        multiply(bottom, upper), q, q_inverse, pc, lower_coefficient)


def dense_congruence_case(name, b, norm):
    data = axis_data(b, norm)
    n, r, a, p = data['n'], data['r'], data['a'], data['p']
    u, inverse = data['u'], data['inverse']
    ut, uit = transpose(u), transpose(inverse)
    pc, pr = tensor(eye(n), p), tensor(p, eye(n))
    q = diagonal(tensor(uit, uit), tensor(uit, u))
    q_inverse = diagonal(tensor(ut, ut), tensor(ut, inverse))
    upper, bottom = upper_minus(tensor(eye(n), a)), lower(tensor(a, eye(n)))
    original = multiply(upper, bottom)
    lower_coefficient = tensor(multiply(p, data['m']), data['m'])
    transformed = check_transformed_pair(original, q, q_inverse, pc, lower_coefficient)
    cases = [check_correction(transformed, pc, pr, lower_coefficient, 1, 169, n * r),
             check_correction(transformed, pc, pr, lower_coefficient, 13, 13, 2 * n * r)]
    wrong_q = diagonal(tensor(inverse, inverse), tensor(inverse, u))
    wrong_inverse = diagonal(tensor(u, u), tensor(u, inverse))
    return {'name': name, 'dimension': 2 * n * n, 'coupling_gram_scalar': str(norm),
            'spectral_13_premise': norm == 12, 'cases': cases}, (
        original, wrong_q, wrong_inverse, pc, lower_coefficient)


def factored_p104_certificate(data):
    n, r = data['n'], data['r']
    b_rank, _, columns = modular_elimination(data['b'])
    require(b_rank == r, 'coupling modular rank mismatch')
    b_minor = [[row[j] for j in columns] for row in data['b']]
    b_determinant = determinant_exact(b_minor)
    require(b_determinant != 0, 'coupling rational minor vanished')
    m_rank, m_det, _ = modular_elimination(data['m'])
    require(m_rank == n and m_det == 1, 'M modular invertibility mismatch')
    require(modular_elimination(data['a'])[0] == r, 'P104 Gram modular rank mismatch')
    pm = multiply(data['p'], data['m'])
    require(all(not any(row) for row in pm[r:]) and
            [row[r:] for row in pm[:r]] == data['b'], 'lower image/minor mismatch')
    # In D_beta=PM tensor M-beta(P tensor I), select first-factor columns
    # r+columns and rows 0..r-1, with ALL second-factor coordinates. The beta
    # term is zero there, leaving B_minor tensor M, of order n*r, for both
    # beta=169 and beta=13. Its determinant is det(B_minor)^n det(M)^r.
    lower_minor_mod13 = pow(residue(b_determinant), n, 13) * pow(m_det, r, 13) % 13
    require(lower_minor_mod13 != 0, 'factored lower minor vanished')
    require(n == 104 and r == 8, 'P104 certificate dimensions mismatch')
    # E_1,169=[-Pc;I] D_169 has rank(D_169)=nr and image in an nr-space.
    # E_13,13 has upper image Pc, lower image Pr. Its upper-right block is
    # 12Pc: choose those nr columns plus the lower minor's nr left columns.
    # Reorder columns as right/left: the selected 2nr minor is block triangular
    # with diagonal 12I and B_minor tensor M. No large pair is materialized.
    balanced_minor_mod13 = pow(12, n * r, 13) * lower_minor_mod13 % 13
    require(balanced_minor_mod13 != 0, 'factored balanced minor vanished')
    return {'n': n, 'r': r, 'endpoint_dimension': 2 * n * n,
            'scratch_dimension': 0, 'rank_alpha1_beta169': n * r,
            'rank_alpha13_beta13': 2 * n * r,
            'rank_A_mod13': r, 'rank_M_mod13': m_rank,
            'B_minor_columns_within_nonpivots': columns,
            'B_minor_determinant_Q': str(b_determinant),
            'M_determinant_Q': '1 (unit triangular U and transpose)',
            'lower_tensor_minor_determinant_mod13': lower_minor_mod13,
            'balanced_minor_determinant_mod13': balanced_minor_mod13,
            'U_sha256': matrix_hash(data['u']), 'A_sha256': matrix_hash(data['a']),
            'M_sha256': matrix_hash(data['m']), 'B_sha256': matrix_hash(data['b'])}


def main():
    inputs = authenticate()
    controls = []

    def reject(name, action, expected):
        try:
            action()
        except ValueError as exc:
            require(str(exc) == expected, 'wrong negative-control rejection: ' + name)
        else:
            raise ValueError('negative control accepted: ' + name)
        controls.append(name)

    ports, actual = reconstruct_ports(inputs[FIXTURE][0])
    actual_certificate = factored_p104_certificate(actual)
    toy, reversed_toy = toy_case()
    integral, wrong_integral = dense_congruence_case('integral-Gram12', [[2, 2, 2]], F(12))
    dyadic_case, wrong_dyadic = dense_congruence_case(
        'dyadic-congruence-only', [[F(1, 2), F(-3, 2), F(1)]], F(7, 2))
    reject('reversed-shear-order', lambda: check_transformed_pair(*reversed_toy),
           'ordered conjugated pair mismatch')
    reject('missing-transpose-integral', lambda: check_transformed_pair(*wrong_integral),
           'ordered conjugated pair mismatch')
    reject('missing-transpose-dyadic', lambda: check_transformed_pair(*wrong_dyadic),
           'ordered conjugated pair mismatch')
    reject('wrong-target-product', lambda: check_coefficients(1, 168),
           'spectral coefficient product mismatch')
    changed = [row[:] for row in actual['b']]
    changed[0][0] += F(1, 2)
    reject('corrupted-P104-coupling', lambda: axis_data(changed, F(12)),
           'coupling Gram mismatch')
    raw, row = inputs[FIXTURE]
    reject('corrupted-source-bytes', lambda: verify_source(raw + b'\n', row),
           'source SHA256 mismatch')
    reject('forbidden-denominator13', lambda: residue(F(1, 13)),
           'non-reducible denominator')
    reject('large-literal-tensor', lambda: tensor(eye(33), eye(1)),
           'literal tensor exceeds small-fixture bound')
    authenticate()
    receipt = {
        'status': 'PASS_P104_DYADIC_SPECTRAL_ATTAINMENT',
        'arithmetic': 'exact rational; all code/inverse entries Gaussian-dyadic; modulo13 reduction',
        'source_sha256': {path: row['sha256'] for path, (_, row) in sorted(inputs.items())},
        'port_coordinates_sha256': matrix_hash(ports),
        'p104_factored_certificate': actual_certificate,
        'literal_fixtures': [toy, integral, dyadic_case],
        'literal_endpoint_cases': 6,
        'factored_endpoint_cases': 2,
        'negative_control_count': len(controls),
        'negative_controls': controls,
        'maximum_literal_endpoint_dimension': 32,
        'maximum_one_axis_dimension': 104,
        'scope': 'Exact common-code endpoint correction rank; no native recipe, paid cost or cold replay',
    }
    print(json.dumps(receipt, sort_keys=True, separators=(',', ':')))
    print('PASS_P104_DYADIC_SPECTRAL_ATTAINMENT')


if __name__ == '__main__':
    main()
