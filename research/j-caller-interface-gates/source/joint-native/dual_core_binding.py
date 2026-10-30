#!/usr/bin/env python3
"""Independent literal inverse-row binding for paid and folded dual cores.

No caller operator algebra is imported. Native/source definition circuits
are compiled gate by gate with exact all-f Gaussian phases. Apache-2.0;
substantial OpenAI Codex assistance. No improved supplier claim.
"""
from pathlib import Path
from fractions import Fraction
import argparse
import hashlib
import json
from joint_coefficient_gate import Model, kernels, mul, phase, ce, b, need, PIN
from literal_inverse_binding import from_circuit, circuit_op, product, sumexpr, scale, serial

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / 'caller-joint'
PINS = {
    'dual_core_caller.py': 'e4517853efdb408bd619275f215dd9928f3492df9647da9de4d0ae4ec7e3fcd1',
    'base_core_retraction.py': '5073cf0d988c4d74460a108a490dde76bb2dd3a2b1fcbfa8a29700587d8658d5',
    'DUAL-CORE-RANK-ONLY.json': '7b4828681a86da9477328a7b04f85adf535abc834ff0aee935f91a65a1ee2783',
}


def independent_expected(q, folded):
    z = Model(1, 2 * q + 1)
    _, J = kernels(z)
    A = mul(z.N.adjoint(), J)
    B = [mul(p, A) for p in z.P]
    P = B[1] if folded else mul(J, B[1])
    ep = 0 if folded else 1
    Q = mul(J.adjoint(), B[0], J)
    Du = mul(B[2], J)
    for r in range(2, q + 1):
        Du = mul(B[2 * r - 1], Du)
    Dv = z.I
    for r in range(2, q + 1):
        Dv = mul(z.P[2 * r], z.N, Dv)
    Dv = mul(phase(z.n, 2 * (q - 2)), Dv)
    F = z.prefix(2 * q + 1)
    target = from_circuit(mul(F, J), 2 * q + 2)
    def entry(prefix, ending, exponent):
        op = mul(F, J, prefix, ending.adjoint(), F.adjoint())
        return from_circuit(op, exponent), op
    tv, tvop = entry(Q.adjoint(), Dv, 6 - 3 * q)
    ku, kuop = entry(P.adjoint(), Du, -ep)
    kvp, _ = entry(P.adjoint(), Dv, 6 - 3 * q - ep)
    kv = sumexpr(tv, scale(kvp, -1))
    return z, target, {(1, 1): {}, (1, 3): tv, (3, 1): ku, (3, 3): kv}, tvop, kuop


def inverse_rows(fixture):
    q, n, m = fixture['q'], fixture['banks'], fixture['ambient_arity']
    folded = fixture['name'] == 'folded-dual'
    identity = from_circuit(ce.ident(m), 0)
    rows = {i: [dict(identity) if i == j else {} for j in range(n)] for i in (1, 3)}
    hist, add_count = {}, 0
    for event in fixture['prefix_events']:
        kind = event['kind']
        if kind == 'ADD':
            d, s = event['dst'], event['src']
            for row in rows.values():
                row[s] = sumexpr(row[s], scale(row[d], -Fraction(event['coefficient'])))
            add_count += 1
        elif kind == 'BANK_SWAP':
            i, j = event['banks']
            for row in rows.values():
                row[i], row[j] = row[j], row[i]
        elif kind == 'SCALE':
            for row in rows.values():
                row[event['bank']] = scale(row[event['bank']], 1 / Fraction(event['coefficient']))
        else:
            op = circuit_op(event['one_coordinate_literal_circuit'], m)
            need(op.tab == tuple(tuple(x) for x in event['one_coordinate_tableau']),
                 'changed prefix literal signed tableau')
            rank = b.native_rank(op)
            if kind == 'NATIVE':
                need(rank == event['rank_per_f'] == 2, 'changed prefix actual native rank2')
                hist[rank] = hist.get(rank, 0) + 1
            else:
                need(rank == 0, 'changed prefix free physical operator monomial')
            value = from_circuit(op.adjoint(), -event['phase_exponent'])
            for row in rows.values():
                row[event['bank']] = product(row[event['bank']], value)

    z, target, expected, tvop, kuop = independent_expected(q, folded)
    corrections = {}
    for key, predicted in expected.items():
        i, j = key
        actual = product(target, rows[i][j])
        need(actual == predicted, 'literal paid/folded original-column inverse entry with every f phase')
        corrections[f'input{i}_from_current{j}'] = serial(actual)
    base = n * (2 * q + 1) + q + 2
    need(hist == {2: base + int(not folded)}, 'paid/folded prefix native tariff')
    need(b.native_rank(tvop) == 2 * q, 'literal required tV native arity2qf')
    # The corrected full inverse is not merely a selected-entry identity:
    # the two original owner rows retain every public coefficient here.
    return {
        'q': q, 'name': fixture['name'], 'all_f_mod4_residues': 'PASS',
        'inverse_original_rows': [1, 3], 'current_pivot_columns': [1, 3],
        'prefix_native_histogram': hist, 'literal_prefix_ADD_count': add_count,
        'prefix_mass': 2 * hist[2], 'stock': n * m,
        'prefix_margin': n * m - 2 * hist[2],
        'original_t_from_U_zero': True,
        'original_t_from_V_native_arity_per_f': b.native_rank(tvop),
        'original_k_from_U_native_arity_per_f': b.native_rank(kuop),
        'full_owner_inverse_rows': {str(i): [serial(x) for x in row] for i, row in rows.items()},
        'physical_joint_correction_pivot_block': corrections,
        'separate_site_mass_gap_lower': 0 if folded else 2,
    }


def run():
    for name, digest in PINS.items():
        need(hashlib.sha256((SOURCE / name).read_bytes()).hexdigest() == digest,
             'dual caller source pin ' + name)
    source = json.loads((SOURCE / 'DUAL-CORE-RANK-ONLY.json').read_text())
    fixtures = [inverse_rows(x) for x in source['fixtures']]
    return {
        'status': 'PASS_INDEPENDENT_PAID_AND_FOLDED_DUAL_CORE_LITERAL_BINDING',
        'scientific_pin': PIN,
        'producer_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'source_pins': [{'path': str(SOURCE / name), 'sha256': digest} for name, digest in PINS.items()]
                       + [{'path': str(HERE / p), 'sha256': hashlib.sha256((HERE / p).read_bytes()).hexdigest()}
                          for p in ('dual_core_gate.py', 'DUAL-CORE-GATE.json', 'literal_inverse_binding.py')],
        'fixtures': fixtures,
        'method': 'Recompile every prefix unary definition circuit; independently derive its physical X-character action and Gaussian tensor phase, and right-multiply both original-owner inverse rows by every forward primitive inverse. The caller joint_algebra, quadratic_charts and formula functions are not imported.',
        'native_admission_scope': 'Every forward prefix operator has actual rank2 and exact all-f phase. The named rank-only source includes definition circuits and selected-native identifiers; selected tail lowering is a separate caller receipt, not inferred from this binding.',
        'paid_domain': 'Paid dual uses P2tilde=JB2 and one extra source J. Conditional all-q complement/support proof gives mass at least stock+2 under equal-volume/fixed-site/full-scan hypotheses.',
        'folded_domain': 'Folded dual uses P2tilde=B2. Its lone J-valued stage2 postfanout is moved through the next paid source query, with the intervening t-=c1 bridge delayed. This is outside the separate-site continuation fee in DUAL-CORE-PROOF.md. Its unchanged prefix margin2q equals the required tV support exponent2q, giving mass at least stock, not stock+2.',
        'all_q_scope': 'Actual original-column/literal-phase binding here is q2/q3. The caller states the exact all-q H/L and local folding identity. The algebraic support proof applies at any q with that physical interface; finite fixtures alone are not an all-q physical serialization.',
        'cost_scope': 'No positive native deficit is possible from the folded fixed-cut support allowance under equal-volume full-bank normalization and the parent full-scan transfer. Unequal child volumes, cross-cut query fusion, owner retirement, another core or a changed target require separate proofs.',
        'no_new_kappa': True,
    }


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--write', action='store_true')
    args = ap.parse_args()
    out = json.loads(json.dumps(run()))
    path = HERE / 'DUAL-CORE-BINDING.json'
    if args.write:
        path.write_text(json.dumps(out, indent=2, sort_keys=True) + '\n')
    else:
        need(json.loads(path.read_text()) == out, 'saved independent dual binding differs')
    print(out['status'])
