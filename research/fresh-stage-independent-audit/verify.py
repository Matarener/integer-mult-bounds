#!/usr/bin/env python3
"""Independent source/operator and inverse-scope audit; Python 3.12 stdlib.

Hiroki KUMAZAKI, with substantial OpenAI Codex assistance. Apache-2.0.
No predecessor verifier is imported or executed. See REVIEW.md for the proof.
"""
from collections import Counter
from fractions import Fraction as F
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = ROOT / 'research/fresh-stage-code-separation'


def require(condition, message):
    if not condition:
        raise ValueError(message)


def authenticate():
    manifest = json.loads((HERE / 'SOURCES.json').read_text())
    count = 0
    for entry in manifest['files']:
        if entry['usage'] == 'input':
            raw = (ROOT / entry['path']).read_bytes()
            require(hashlib.sha256(raw).hexdigest() == entry['sha256'],
                    'Source byte mismatch: ' + entry['path'])
            count += 1
    return count


def apply_rows(rows, x):
    return sum(((row & x).bit_count() % 2) << j for j, row in enumerate(rows))


def monomials():
    ports = json.loads((SOURCE / 'inputs/NORMALIZERS.json').read_text())['ports']
    require(len(ports) == 112, '112 source normalizers')
    tables = []
    for i, port in enumerate(ports):
        rows, z = port['G_rows'], port['Z_mask']
        require(port['port'] == i and len(rows) == 9, 'Ordered nine-axis ports')
        require(all(type(r) is int and 0 <= r < 512 for r in rows), 'Binary rows')
        require(type(z) is int and 0 <= z < 512, 'Binary sign mask')
        require(all((rows[r] & rows[s]).bit_count() % 2 == (r == s)
                    for r in range(9) for s in range(9)), 'Orthogonal row Gram matrix')
        require(apply_rows(rows, 1) == port['q'], 'Central image binding')
        require(port['K_word'] == [['P', rows], ['D', [0]*9, [2*((z >> j) & 1) for j in range(9)]]],
                'Literal signed P then D normalizer')
        table = []
        for x in range(512):
            # Evaluate the literal word with a Z/4 phase accumulator.
            y, phase = x, 0
            for instruction in port['K_word']:
                if instruction[0] == 'P':
                    y = apply_rows(instruction[1], y)
                else:
                    require(instruction[1] == [0]*9, 'No quadratic phase in K')
                    phase += sum(c*((y >> j) & 1) for j, c in enumerate(instruction[2]))
            require(phase % 2 == 0, 'Real signed normalizer')
            sign = (1, -1)[(phase // 2) % 2]
            require(sign == (-1)**((z & y).bit_count() % 2), 'Exact output phase')
            table.append((y, sign))
        require(len({y for y, _ in table}) == 512, 'Bijection')
        tables.append(table)
    require(len({p['q'] for p in ports}) == 112, 'Distinct central images')
    return tables


def inverse(table):
    out = [None]*len(table)
    for x, (y, sign) in enumerate(table):
        out[y] = (x, sign)
    require(all(v is not None for v in out), 'Monomial inverse domain')
    return out


def gadd(a, b):
    return a[0]+b[0], a[1]+b[1]


def gmul(a, b):
    return a[0]*b[0]-a[1]*b[1], a[0]*b[1]+a[1]*b[0]


def put(out, y, value):
    out[y] = gadd(out.get(y, (F(0), F(0))), value)
    if out[y] == (0, 0):
        del out[y]


def q_column(vector, backwards=False):
    sign = -1 if backwards else 1
    out = {}
    for x, c in vector.items():
        put(out, x, gmul(c, (F(1, 2), F(sign, 2))))
        put(out, x ^ 1, gmul(c, (F(1, 2), F(-sign, 2))))
    return out


def m_column(table, vector):
    out = {}
    for x, c in vector.items():
        y, sign = table[x]
        put(out, y, (sign*c[0], sign*c[1]))
    return out


def geometry(tables):
    inv = inverse(tables[1])
    path = []
    for y, s in tables[0]:
        z, t = inv[y]
        path.append((z, s*t))
    require(path[1][0] != 1, 'Alternating first transition moves e')
    rows = Counter()
    for x in range(512):
        basis = {x: (F(1), F(0))}
        n = q_column(m_column(path, q_column(basis)), backwards=True)
        require(len(n) == 4, 'Conjugated column has four entries')
        for y, c in n.items():
            require(c[0]**2 + c[1]**2 == F(1, 4), 'Four exact magnitudes 1/2')
            rows[y] += 1
        # Independent sparse multiplication of Q (Q^-1 M Q) Q^-1.
        recovered = q_column(q_column(m_column(path,
                    q_column(q_column(basis, backwards=True))), backwards=True))
        require(recovered == m_column(path, basis), 'Marker conjugation orientation')
        fixed = q_column(q_column(basis), backwards=True)
        require(fixed == basis, 'Ge=e identity control has one entry, not four')
    require(set(rows.values()) == {4} and len(rows) == 512, 'Four entries in every row')
    basis = {0: (F(1), F(0))}
    wrong = q_column(q_column(m_column(path,
                q_column(q_column(basis, backwards=True))), backwards=True), backwards=True)
    require(wrong != m_column(path, basis), 'Wrong outer Q orientation is detected')
    return {'literal_normalizer_entries': 112*512,
            'conjugated_columns_and_rows': 512,
            'four_entry_magnitude_squared': '1/4',
            'marker_orientation_columns': 512,
            'fixed_central_vector_control_support': 1,
            'wrong_outer_Q_orientation_rejected': True}


def inverse_counterexample():
    raw = json.loads((SOURCE / 'inputs/CODE.json').read_text())['A']
    a = [[F(x) for x in row] for row in raw]
    n = len(a)
    require(n == 112 and all(len(row) == n for row in a), '112 square code')
    require(all(a[i][i] == 0 for i in range(n)), 'Zero diagonal')
    require(a[0][1] == a[1][0] == F(-1, 2), 'Alternating edge coefficient')
    require(all((2*x).denominator == 1 for row in a for x in row), 'Integral doubled code')
    b = [[int(2*x) for x in row] for row in a]
    # B=2A: B^2+24B=52I checks A(A+12I)/13=I exactly.
    for i in range(n):
        for j in range(n):
            square = sum(b[i][t]*b[t][j] for t in range(n))
            require(square+24*b[i][j] == 52*(i == j), 'Exact inverse polynomial')
    ainv = [[F(b[i][j]+24*(i == j), 26) for j in range(n)] for i in range(n)]
    # Compile and symbolically execute scalar owner mixing in normalized coordinates.
    # A first nonzero term uses COPY+SCALE; each additional term uses one ADD.
    adds, row_terms = 0, []
    for row in ainv:
        terms = [(j, c) for j, c in enumerate(row) if c]
        require(bool(terms), 'Nonempty inverse row')
        state = {terms[0][0]: terms[0][1]}
        for j, c in terms[1:]:
            state[j] = state.get(j, F(0))+c
            adds += 1
        require([state.get(j, F(0)) for j in range(n)] == row, 'Exact symbolic ADD program')
        row_terms.append(len(terms))
    require(set(row_terms) == {53} and adds == 5824, 'Source sparse inverse bill')
    width = (adds+24)//2+1
    alleged = 2*width-24
    require(width == 2925 and alleged == 5826 and alleged > adds, 'Literal inverse contradiction')
    # Removing the diagonal term does not invert A: inspect the (0,1) product.
    wrong_entry = sum(a[0][t]*a[t][1]/13 for t in range(n))
    require(wrong_entry != 0, 'Omitted 12I inverse term is detected')
    c = ainv[0][1]
    require(c == F(-1, 26) and c != c*c, 'Owner scalar must not be tensor powered')
    return {'scope': 'Unconjugated B_f^-1 at k=1, a_1=1',
            'matrix_polynomial_entries': n*n,
            'inverse_formula': 'A^-1=(A+12I)/13',
            'inverse_nonzero_terms_per_owner': 53,
            'add_count_for_every_positive_tensor_width': adds,
            'witness_tensor_width': width,
            'incorrect_literal_lower_bound': alleged,
            'omitted_diagonal_product_entry_0_1': str(wrong_entry),
            'once_applied_owner_coefficient': str(c),
            'incorrect_tensor_squared_coefficient': str(c*c),
            'large_tensor_materialized': False}


def run():
    pins = authenticate()
    tables = monomials()
    spec = importlib.util.spec_from_file_location('independent_markers', HERE / 'markers.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return {'status': 'PASS_INDEPENDENT_FRESH_STAGE_AUDIT_WITH_INVERSE_SCOPE_FINDING',
            'authenticated_inputs': pins,
            'inverse_scope_counterexample': inverse_counterexample(),
            'normalizers_and_conjugation': geometry(tables),
            'marker_audit': module.run(SOURCE),
            'proof_review': 'REVIEW.md; written argument, not formal-kernel acceptance',
            'complete_producer_replayed': False,
            'selected_frontier_changed': False}


def main():
    require(sys.argv[1:] in ([], ['--write']), 'Use no arguments or --write')
    result = run()
    encoded = json.dumps(result, sort_keys=True, indent=2)+'\n'
    target = HERE / 'RESULT.json'
    if sys.argv[1:]:
        require(not target.exists(), 'Refuse to overwrite receipt')
        target.write_text(encoded)
    else:
        require(target.read_text() == encoded, 'Deterministic receipt differs')
    print(result['status'])
    print(json.dumps(result['inverse_scope_counterexample'], sort_keys=True))


if __name__ == '__main__':
    main()
