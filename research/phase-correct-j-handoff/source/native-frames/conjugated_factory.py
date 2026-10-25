#!/usr/bin/env python3
"""A one-child lowering for the genuinely two-sided R P2 R factory.
Apache-2.0; substantial OpenAI Codex assistance. No free source substitution.
"""
from pathlib import Path
import argparse
import hashlib
import json
from native_model import *
from orthogonal_source_normalizer import reflection
from conjugated_reflection import tensor_monomial

HERE = Path(__file__).resolve().parent


def run():
    z1 = Model(1, 3)
    R1, _ = reflection(z1, 3, (0, 1, 2, 4))
    M1 = mul(R1, z1.P[1], R1)
    B1 = mul(z1.N, M1, z1.N.adjoint())
    recipe, compiled = ce.lower_child(B1)
    need(recipe['rank'] == 2, 'two-sided factory conjugate native2')
    same(B1, compiled, 'literal one-bit factory lowering phase')
    checks = []
    for f in (1, 2, 3):
        z = Model(f, 3)
        R, _ = reflection(z, 3, (0, 1, 2, 4))
        M = mul(R, z.P[1], R)
        B = mul(z.N, M, z.N.adjoint())
        literal = mul(tensor_monomial(recipe['left'], f),
                      ce.fourier(z.n, range(2 * f)), tensor_monomial(recipe['right'], f))
        same(B, literal, 'two-sided factory all-f tensor recipe phase')
        same(mul(B, B), z.I, 'two-sided factory literal involution')
        ranks = [b.native_rank(mul(z.N, X, z.N.adjoint()))
                 for X in (z.P[1], mul(R, z.P[1]), mul(z.P[1], R), M)]
        need(ranks == [4 * f, 4 * f, 4 * f, 2 * f], 'both R sides are required for this saving')
        checks.append({'f': f, 'ranks_P2_RP2_P2R_RP2R': ranks,
                       'actual_native_recipe_phase': True, 'inverse': 'same operator'})
    return {'status': 'PASS_ALL_F_TWO_SIDED_REFLECTION_FACTORY_SINGLE_CHILD',
            'scientific_pin': PIN,
            'producer_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'source_pins': [{'path': str(HERE/name), 'sha256': hashlib.sha256((HERE/name).read_bytes()).hexdigest()}
                            for name in ('native_model.py', 'orthogonal_source_normalizer.py', 'conjugated_reflection.py')],
            'exact_operator': 'B=N0 R P2 R N0^-1, P2=SWAP(plane0,plane2), R=ADDRESS(I+vv^T), v=(p0,q0,p1,p2).',
            'all_f_proof': 'P2_f and R_f are bitwise tensors. Global N_f phases cancel in conjugation, so B_f=B_1^tensor f. The explicit actual one-bit equality B_1=L C_2 R_adapter tensor-lifts with fixed bitwise ADDRESS/quadratic-phase controllers to one selected native2f query. B_1 has B-rank2, so B_f has exact B-rank2f, including all f-dependent adapter phase powers.',
            'one_bit_selected_native_recipe': recipe,
            'complete_unary_invoice': {'native_H2': 1, 'native_rank_mass': 2,
                                       'monomial_adapters': 2, 'ADDRESS_scans_at_most': 2,
                                       'Gaussian_quadratic_phase_scans_at_most': 2,
                                       'ordinary_helpers': 0, 'private_fields': 0},
            'actual_checks': checks,
            'caller_obligation': 'This bill applies only to the literal B shown. An outgoing source P2 is not replaced for free. R uses the stage2-future plane2, so supplying both R sides at a legal caller cut with all source/target columns and fresh coverage is a separate obligation. A global chart change also transports N and cannot be used to claim this saving while holding N fixed.',
            'COPY_precision_tape_obligations': 'Native lowering is a Fourier/supplier query with arbitrary input. Any source COPY to a fanout, all bank reads, the two monomial ADDRESS/phase adapters, their reversible scans, precision/rounding propagation, source-bound block norms, and physical tape return remain paid caller obligations. No endpoint, all-size recursion, stock or exponent follows from this unary identity.',
            'evidence_domain': 'Written exact all-f tensor proof, actual Gaussian recipe and phase checks f1/f2/f3, and one-sided negative controls. No finite-f extrapolation and no formal-kernel claim.',
            'no_new_kappa': True}


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--write', action='store_true')
    args = p.parse_args()
    out = json.loads(json.dumps(run()))
    path = HERE/'CONJUGATED-FACTORY.json'
    if args.write:
        path.write_text(json.dumps(out, indent=2, sort_keys=True)+'\n')
    else:
        need(json.loads(path.read_text()) == out, 'saved conjugated factory differs')
    print(out['status'])
    print(out['complete_unary_invoice'])
