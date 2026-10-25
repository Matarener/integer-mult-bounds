#!/usr/bin/env python3
"""Arbitrary monomial source posts cannot change the fixed-core support gap.

The telescope is checked in a free noncommutative operator algebra. No
source ADDRESS is assumed to commute a past or future Fourier frame.
Apache-2.0; substantial OpenAI Codex assistance.
"""
from pathlib import Path
import argparse
import hashlib
import json
from joint_coefficient_gate import f, PIN

HERE = Path(__file__).resolve().parent


def prove(q):
    k = 2 * q + 1
    J, Ji = f.N, f.inv(f.N)
    S = {s: f.mono((s,)) for s in range(1, k + 1)}
    # N_s are independent invertible generators here. Telescoping needs
    # no mutual commutation or relation N_s^2=-I.
    native_offset = 10 * k
    N = {s: f.mono((native_offset + s,)) for s in range(1, k + 1)}
    F = {0: f.I}
    for s in range(1, k + 1):
        F[s] = f.prod(N[s], F[s - 1])
    B = {s: f.prod(f.inv(F[s]), S[s], F[s - 1], J) for s in range(1, k + 1)}
    D = {s: f.prod(B[s], J) for s in range(1, k + 1)}
    for s in D:
        f.need(D[s] == f.neg(f.prod(f.inv(F[s]), S[s], F[s - 1])),
               'exact changed source B_s J with mandatory minus sign')
    Q1 = f.prod(Ji, B[1], J)
    base = f.prod(f.inv(B[1]), J, f.inv(B[2]))
    collapsed_base = f.prod(Ji, f.inv(S[1]), f.inv(S[2]), F[2])
    f.need(base == collapsed_base, 'fully noncommutative original base collapse')
    wrong = f.prod(Ji, f.inv(S[1]), N[1], f.inv(S[2]), N[2])
    f.need(base != wrong, 'commuting N1 across arbitrary S2 is rejected')
    Dv = f.I
    for r in range(2, q):
        Dv = f.prod(f.neg(D[2 * r + 1]), Dv)
    Dv = f.prod(D[k], Dv)
    G = f.prod(f.inv(S[1]), f.inv(S[2]), F[2], f.inv(Dv))
    C = f.prod(F[k], Ji, G, f.inv(F[k]))
    R = f.neg(f.prod(F[k], f.inv(G)))
    T = f.prod(F[k], J)
    telescope = f.I
    for s in range(k, 4, -2):
        telescope = f.prod(telescope, S[s], N[s - 1])
    telescope = f.prod(telescope, N[3], S[2], S[1])
    f.need(R == telescope, 'all-q exact plus-sign native/monomial telescope')
    f.need(f.prod(C, R) == T, 'general-source universal joint coefficient identity')
    f.need(f.prod(C, f.neg(R)) != T, 'wrong overall telescope sign rejected')
    # A literal implementation of this R uses exactly q native N_s calls
    # and q+1 physical source monomial posts. It is an upper bound on
    # its support, irrespective of cancellation between those factors.
    (_, letters), = ((coefficient, word) for word, coefficient in R.items())
    native_letters = [s - native_offset for s in letters if abs(s) > native_offset]
    source_letters = [s for s in letters if 0 < abs(s) <= k]
    f.need(len(native_letters) == q and len(source_letters) == q + 1,
           'literal complement query and source-post census')
    return {'q': q, 'k': k, 'native_N_s_factors': native_letters,
            'source_post_factors': source_letters, 'R': f.serial(R),
            'R_native_mass_upper_per_f': 2 * q,
            'C_required_support_exponent_per_f': 2 * q + 4,
            'native_prefix_margin_per_f': 2 * q,
            'global_sign': '+1'}


def run():
    checks = [prove(q) for q in range(2, 26)]
    return {'status': 'PASS_ARBITRARY_MONOMIAL_SOURCE_POST_JOINT_GATE',
            'scientific_pin': PIN,
            'producer_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'source_pins': [{'path': str(HERE / p), 'sha256': hashlib.sha256((HERE / p).read_bytes()).hexdigest()}
                            for p in ('joint_coefficient_gate.py', 'UNIVERSAL-KERNEL-GATE.json', 'LITERAL-INVERSE-BINDING.json')],
            'general_stage': 'K_s=F_(s-1) J F_(s-1)^-1 on source; scalar delivery; physical source post S_s; fresh N_s on every other bank. Retarded B_s=F_s^-1 S_s F_(s-1) J.',
            'D_s': 'B_s J=-F_s^-1 S_s F_(s-1). No S_s/frame commutation is assumed.',
            'generic_base_collapse': 'B1^-1 J B2^-1=J^-1 S1^-1 S2^-1 F2.',
            'Dv': 'D_(2q+1) (-D_(2q-1))...(-D5).',
            'universal_factorization': 'G=S1^-1 S2^-1 F2 Dv^-1; C=F_k J^-1 G F_k^-1; T=F_k J; R=-F_k G^-1; C R=T exactly.',
            'exact_telescope': 'R=S_(2q+1) N_(2q) S_(2q-1) N_(2q-2)...S5 N4 N3 S2 S1, with PLUS overall sign for every q.',
            'monomial_domain': 'Each actual physical S_s may be any invertible monomial on the full address set, including f-dependent/nonlinear ADDRESS and value phases. Causality is not needed for this support theorem. Any separate caller admission restriction remains additional.',
            'support_result': 'There are q actual rank-2f N_s factors in R and q+1 monomial S factors. Thus max_row_support(R)<=2^(2qf). Full target F_k J has2^(mf) nonzeros in every row, so C has at least2^((2q+4)f) nonzeros in every row. All complete joint cleanups satisfy total_native_arity+binary_ADD_count>=(2q+4)f.',
            'prefix_count_scope': 'The same fixed scalar/retraction architecture has separately exposed source queries K_s; full target forces each such Clifford K_s to have arity>=2f, independently of S_s. Thus its native prefix mass is at least stock-2q; growing full-bank ADDs and proper child moments need the parent transfer gate.',
            'negative_controls': ['An N1 commuted through noncommuting S2 does not equal the exact base product.',
                                  'A wrong overall minus sign gives -T, not T.'],
            'free_word_checks': checks,
            'limits': ['This is a fixed scalar/core/diagonal-continuation architecture gate, not a global supplier lower bound.',
                       'Cross-cut fusion, a new scalar core or continuation, changed delivery map or terminal coupled-owner/input/target contract changes the required equation and is not covered.',
                       'Partial/local scan work and a different transfer theorem must be priced separately; no unconditional exclusion of O(f) algorithms is made.',
                       'The all-q free algebra applies when the caller original-column H/L interface is established; physical prefix fixtures are separately pinned at q2/q3.',
                       'No stronger kappa, all-size supplier, owner, precision or fixed-tape result is claimed.'],
            'no_new_kappa': True}


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--write', action='store_true')
    args = ap.parse_args()
    out = json.loads(json.dumps(run()))
    path = HERE / 'GENERAL-SOURCE-GATE.json'
    if args.write:
        path.write_text(json.dumps(out, indent=2, sort_keys=True) + '\n')
    else:
        f.need(json.loads(path.read_text()) == out, 'saved arbitrary-source gate differs')
    print(out['status'])
