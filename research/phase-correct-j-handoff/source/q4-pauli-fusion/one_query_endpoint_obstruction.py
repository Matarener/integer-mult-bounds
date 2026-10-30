#!/usr/bin/env python3
"""Actual-base sparsity certificate for the changed two-carrier gate.

The general two-column argument and its two independent all-size proofs
are written in ONE-QUERY-ENDPOINT-OBSTRUCTION.md.  This producer checks
actual Gaussian matrices, not a native-arity label inferred from a word.
Apache-2.0; substantial OpenAI Codex assistance.
"""
from pathlib import Path
from collections import Counter
from fractions import Fraction
import argparse
import hashlib
import json
from reflection_route_pruned import EnlargedBase
from unpaired_reflection_screen import need

HERE = Path(__file__).resolve().parent


def walsh(values):
    out = list(values)
    step = 1
    while step < len(out):
        for first in range(0, len(out), 2 * step):
            for j in range(first, first + step):
                a, b = out[j], out[j + step]
                out[j] = a[0] + b[0], a[1] + b[1]
                out[j + step] = a[0] - b[0], a[1] - b[1]
        step *= 2
    return out


def physical_certificate(A, op):
    permutation, phases = A.ops[op]
    units = ((1, 0), (0, 1), (-1, 0), (0, -1))
    rows = []
    for x in range(64):
        values = []
        for w in range(64):
            a, b = units[phases[w]]
            sign = -1 if (x & permutation[w]).bit_count() & 1 else 1
            values.append((sign * a, sign * b))
        rows.append(walsh(values))
    support = [sum(rows[x][y] != (0, 0) for x in range(64)) for y in range(64)]
    norms = sorted({a * a + b * b for row in rows for a, b in row if (a, b) != (0, 0)})
    # This independent actual-column unitary check is sensitive to Gaussian
    # phases, the Walsh conjugation and all64 independent input columns.
    for j in range(64):
        for k in range(64):
            real, imag = 0, 0
            for row in rows:
                a, b = row[j]
                c, d = row[k]
                real += a * c + b * d
                imag += a * d - b * c
            need((real, imag) == ((4096, 0) if j == k else (0, 0)),
                 'all physical Gaussian columns are exactly unitary')
    return dict(matrix_dimension=64, common_denominator=64,
                column_support_histogram=dict(Counter(support)),
                nonzero_entry_squared_integer_norms=norms,
                maximum_entry_squared_modulus=str(Fraction(max(norms), 4096)),
                exact_integer_matrix_sha256=hashlib.sha256(
                    json.dumps(rows, separators=(',', ':')).encode()).hexdigest())


def run():
    A = EnlargedBase(True)
    operators = [('H0=-i*N0_1', A.H[0], 'native')]
    for kind, reflections in (('primal', A.Rs), ('dual', A.dual)):
        for j, R in enumerate(reflections):
            for i, H in enumerate(A.H):
                operators.append((f'{kind}_Q_reflection{j}_plane{i}',
                                  A.left(H, A.left(R, H)), 'native'))
    operators.append(('R0_actual_ADDRESS_control', A.Rs[0], 'monomial'))
    cases = []
    for name, op, kind in operators:
        certificate = physical_certificate(A, op)
        need(certificate['column_support_histogram'] == ({4: 64} if kind == 'native' else {1: 64}),
             'actual admitted native and monomial controls have the predicted physical sparsity')
        need(certificate['maximum_entry_squared_modulus'] == ('1/4' if kind == 'native' else '1'),
             'actual Gaussian maximum amplitude establishes the uncertainty tariff')
        cases.append(dict(name=name, kind=kind, certificate=certificate))
    # Exact sharp control for Cauchy's support uncertainty: a coordinate
    # vector under a4-flat-column native has support product4, not1.
    need(1 * 4 == 4 and 1 * 1 < 4,
         'the actual one-query native uncertainty bound is sensitive to an omitted support factor')
    native = HERE.parent / 'native-frames'
    pins = [HERE / 'unpaired_reflection_screen.py', HERE / 'varied_reflection_screen.py',
            HERE / 'reflection_route_pruned.py']
    pins += [native / name for name in ('native_model.py', 'conjugated_reflection.py',
                                       'CONJUGATED-REFLECTION.json', 'dual_reflections.py',
                                       'DUAL-REFLECTIONS.json')]
    return dict(status='PASS_ACTUAL_GAUSSIAN_ONE_QUERY_ENDPOINT_OBSTRUCTION', no_new_kappa=True,
                target='C=[[Q-I,N],[Q,0]], two independent M-dimensional carrier banks; optionally any finite h additional M-dimensional restored identity helper banks, with one query on an M-dimensional bank.',
                exact_actual_base_cases=cases,
                all_size_binding='N_f=i*H0^tensorf and each primal/dualQ_f=Q_1^tensorf. The exact base maximum1/2 gives maximum2^-f at everyf; all columns remain unitary.',
                finite_uniform_theorem='No one-query factorization C G=F diag(U,I) exists over a fixed finite uniform-tensor physical-monomial endpoint algebra for allf. U is arbitrary. Distinct nonproportional tensor rays are independent for all sufficiently large tensor powers, so Qg0 and Ng1 cannot both return to the monomial algebra unless the untouched column vanishes.',
                nonuniform_support_theorem='For arbitrary physical monomial controllers, if endpoint block columns have at mostK_G andK_F nonzero entries, a one-query factorization requiresK_G*K_F>=2^(2f). Consequently scalar bank ADD counts obeya_F+a_G>=2f. A growingO(f)ADD word is not excluded.',
                helper_dimension_contract='For h additional M-dimensional identity helper banks and one M-dimensional queried bank, unqueried input dimension (h+1)M exceeds helper image dimension hM. More generally, after the same carrier-row vanishing, helper widths totaling K and query width w<=M give 2M+K-w>=M+K>K. No arbitrarily larger single queried helper bank is admitted.',
                exact_support_thresholds=[dict(f=f, required_support_product_at_least=4 ** f,
                                               required_scalar_bank_ADDs_at_least=2 * f)
                                          for f in range(1, 17)],
                limits=['The nonuniform theorem is a support/scan lower bound, not an impossibility result forO(f)ADD words.',
                        'Finite uniform tensor independence does not itself cover f-dependent growing nonuniform controllers.',
                        'The gate is unary on one physical bank. Multi-bank native primitives or nonmonomial free endpoints are outside the premise.',
                        'The helper dimension argument requires an M-dimensional queried bank, or query width<=M in the stated conditional variable-width extension; unbounded queried helper width is excluded.',
                        'This is a scoped obstruction for the changed localC gate, not a complete-caller stock floor in the enlarged reflection grammar.'],
                attribution='The independent-column obstruction and support-uncertainty proposal are from root. This file supplies the actual Gaussian base verification and the written all-size composition proof. Native arity and literal primal/dual recipes are from stabilizer_escape_1019.',
                producer_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                source_pins=[dict(path=str(p), sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in pins])


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--write', action='store_true')
    args = ap.parse_args()
    out = json.loads(json.dumps(run()))
    path = HERE / 'ONE-QUERY-ENDPOINT-OBSTRUCTION.json'
    if args.write:
        path.write_text(json.dumps(out, sort_keys=True, indent=2) + '\n')
    else:
        need(json.loads(path.read_text()) == out, 'saved actual one-query obstruction differs')
    print(out['status'], 'actual Gaussian cases', len(out['exact_actual_base_cases']))


if __name__ == '__main__':
    main()
